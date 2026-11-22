"""22 Nov 2026 (the user's C0089 on real10 L-1, "it is not a real room and there is no doors to outside"; "yes start
C0089"; lesson UL365): a grille is no door.

The cause on the drawing: real10 L-1's light slot between two flats (1.8 m wide, under the normal floors' open facade
recess, the two bathrooms' 50/50 windows opening onto it) is closed at the facade line by a grille on the furniture
layer TEFRİŞ: 32 equal bars 0.64 m long, in pairs 2 cm apart at a 0.10 m pitch, from the outer face inward. The open-leaf
rule (doors drawn open at 90 degrees with no swing arc) took two of the bars for a double door's leaves (d_L-1_006) and
the slot for a room with a door to the outside. The slot's sides are real walls (shear walls on kolon/DUVAR), so the
'room' is no outline of non-wall lines; the door is the error.

- ``openings._grille_bars``: equal bars across a gap at a pitch finer than any stair's going, filling it, standing out
  of the wall's band on one side only, none running on past the jambs, not on a wall, hatch, finish, stair or notation
  layer: a fixed grille (a window, operation fixed), checked before the open leaves.
- ``openings.blocked_passage``: a doorway's passage is clear; leaves opened at 90 degrees with bars of their own length
  between them are no leaves (``Gap.blocked``, never silent; the ranker may then not type the gap a door).
- RC14 ``unnamed_exit`` (not calibrated, info): an outer door with no swing, door block or door-high size tag drawn, the
  only door of a face no label names.
- Must not fire: balcony and terrace doors, French windows over a railing, basement doors onto a light well or an
  outside stair, garage doors on a ramp, real unlabelled rooms bounded by walls, doors whose outside step or stair is
  drawn on another layer, a wall's hatch, a floor drawn on through a doorway, a stair's treads.
- synthetic-35-grille-slot read end to end through the CPU pipeline (generated into a temporary folder).
"""
from __future__ import annotations

import copy
import math

import pytest

from wenart.ingest.generic import decisions as DEC
from wenart.ingest.generic import openings as O
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke
from wenart.reading_check import ranker as RK
from wenart.reading_check import score as SC
from wenart.reading_check import sense as SN
from wenart.synthetic import failure_classes as FC
from wenart.synthetic import weak_projects as WP


# --- helpers: a wall along x on y = 0 (band -t/2 .. t/2); the inside of the building is y < 0 -------------------------

def _gap(a=0.0, b=1.8, t=0.27):
    return O.Gap("run", "h", 0.0, t, a, b, [])


def _line(sid, p, q, layer="0"):
    return Stroke(sid, "line", [p, q], layer=layer)


def _arc(sid, c, r, a0, a1, layer="KAPI"):
    pts = [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / 16)),
            c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / 16))) for k in range(17)]
    return Stroke(sid, "arc", pts, layer=layer, arc={"center": c, "radius": r, "start_deg": a0, "end_deg": a1})


def _index(*strokes):
    return O.StrokeIndex(list(strokes), 0.0)


def _classify(g, *strokes):
    O._classify_gap_rules(g, _index(*strokes), set())
    return g


def _c0089_grille(t=0.27, a=0.0, b=1.8, layer="TEFRİŞ"):
    """real10 L-1's grille: bars in pairs 2 cm apart at a 0.10 m pitch, 0.64 m long from the outer face (y = +t/2)
    inward, the first 0.14 m from a jamb."""
    out, k, x = [], 0, a + 0.14
    while x <= b - 0.14 + 1e-9:
        for dx in (0.0, 0.02):
            out.append(_line(f"b{k}", (x + dx, t / 2), (x + dx, t / 2 - 0.64), layer))
            k += 1
        x += 0.10
    return out


def _leaf(x, y0, y1, sid="l", layer="KAPI", width=0.04):
    """A door leaf drawn as two lines ``width`` apart standing across the wall (open at 90 degrees)."""
    return [_line(f"{sid}1", (x, y0), (x, y1), layer), _line(f"{sid}2", (x + width, y0), (x + width, y1), layer)]


# --- the C0089 case ----------------------------------------------------------------------------------------------------

def test_the_c0089_grille_is_a_fixed_grille_never_a_double_door():
    bars = _c0089_grille()
    found = O._grille_bars(_gap(), _index(*bars), set())
    assert found is not None and found["count"] == 32 and found["length"] == 0.64 and found["layers"] == ["TEFRİŞ"]
    g = _classify(_gap(), *bars)
    assert g.cls == "window" and g.found["grille"]["count"] == 32
    assert O.gap_rule(g, {})[0] == "window_grille"
    assert DEC.RULE_CONFIDENCE["window_grille"] >= RK.RULE_TRUST       # the ranker never re-types it


def test_open_leaves_with_bars_of_their_length_between_them_are_no_door():
    g = _gap()
    zone = _index(*_c0089_grille()).query(g.rect(grow_face=O.ZONE_M))
    assert O._open_leaves(g, zone) is None and g.blocked >= O.PASSAGE_BARS_MIN
    # the same two 'leaves' alone: HEAD's double door
    g2 = _gap()
    two = [s for s in _c0089_grille() if any(abs(s.pts[0][0] - x) < 1e-6 for x in (0.14, 0.16, 1.44, 1.46))]
    assert O._open_leaves(g2, _index(*two).query(g2.rect(grow_face=O.ZONE_M))) is not None and not g2.blocked


def test_the_ranker_may_not_type_a_blocked_gap_a_door():
    rec = {"kind": RK.KIND_GAP, "gap": "run", "rule_answer": "opening", "features": {"width": 1.8, "run_length": 9.0}}
    assert "door" in RK.allowed_answers(rec)
    assert "door" not in RK.allowed_answers(dict(rec, leaves_blocked=12))


# --- what keeps its door or opening ------------------------------------------------------------------------------------

def test_a_door_drawn_open_at_90_degrees_keeps_its_door_single_and_double():
    g = _classify(_gap(0.0, 0.9, 0.2), *_leaf(0.02, -0.1, -0.95))
    assert g.cls == "door" and g.found["open_leaf"] and not g.blocked
    g = _classify(_gap(0.0, 1.6, 0.2), *_leaf(0.02, -0.1, -0.85, "a"), *_leaf(1.54, -0.1, -0.85, "b"))
    assert g.cls == "door" and g.found["double"] and not g.blocked


def test_balcony_and_french_window_doors_keep_their_door():
    # a balcony door with its swing, a balustrade's bars drawn across the band onto the balcony (a grille's shape)
    t = 0.25
    balusters = [_line(f"k{k}", (0.1 + 0.12 * k, t / 2), (0.1 + 0.12 * k, -t / 2 - 0.2), "KORKULUK") for k in range(7)]
    swing = [_arc("a1", (0.0, -t / 2), 0.9, 270.0, 360.0), _line("lf", (0.0, -t / 2), (0.0, -t / 2 - 0.9), "KAPI")]
    assert O._grille_bars(_gap(0.0, 0.9, t), _index(*balusters), set()) is not None
    g = _classify(_gap(0.0, 0.9, t), *swing, *balusters)
    assert g.cls == "door" and g.found["arcs"]                          # the swing comes first
    # a French window: a door over a railing (one line along the outer face, short baluster ticks on it)
    rail = [_line("r", (0.0, t / 2 + 0.05), (0.9, t / 2 + 0.05), "KORKULUK")] + \
        [_line(f"t{k}", (0.06 + 0.12 * k, t / 2 + 0.03), (0.06 + 0.12 * k, t / 2 + 0.07), "KORKULUK") for k in range(7)]
    assert O._grille_bars(_gap(0.0, 0.9, t), _index(*rail), set()) is None
    g = _classify(_gap(0.0, 0.9, t), *swing, *rail)
    assert g.cls == "door"


def test_basement_and_outside_stair_doors_and_steps_on_another_layer_keep_their_door():
    t = 0.25
    leaf = _leaf(0.02, -t / 2, -t / 2 - 0.85)
    # an outside stair down into a light well: treads along the wall, and a flight along the facade whose treads stand
    # across it from the outer face (0.28 m going), on MERDIVEN; a step's outline beside the door
    along = [_line(f"s{k}", (-0.2, t / 2 + 0.3 + 0.28 * k), (1.1, t / 2 + 0.3 + 0.28 * k), "MERDIVEN") for k in range(5)]
    across = [_line(f"c{k}", (0.05 + 0.28 * k, t / 2), (0.05 + 0.28 * k, t / 2 + 1.0), "MERDIVEN") for k in range(4)]
    step = [_line("p1", (-0.1, t / 2), (-0.1, t / 2 + 0.3), "MERDIVEN"), _line("p2", (1.0, t / 2), (1.0, t / 2 + 0.3), "0"),
            _line("p3", (-0.1, t / 2 + 0.3), (1.0, t / 2 + 0.3), "0")]
    for extra in (along, across, step):
        g = _classify(_gap(0.0, 0.9, t), *leaf, *extra)
        assert g.cls == "door" and g.found.get("open_leaf") and not g.blocked
        assert O._grille_bars(_gap(0.0, 0.9, t), _index(*extra), set()) is None


def test_a_garage_door_on_a_ramp_is_no_grille():
    t = 0.25
    grooves = [_line(f"g{k}", (0.0, t / 2 + 0.2 + 0.15 * k), (2.5, t / 2 + 0.2 + 0.15 * k), "RAMPA") for k in range(12)]
    sides = [_line("s1", (0.0, t / 2), (0.0, t / 2 + 4.0), "RAMPA"), _line("s2", (2.5, t / 2), (2.5, t / 2 + 4.0), "RAMPA")]
    arrows = [_line(f"a{k}", (0.4 + 0.1 * k, t / 2 + 0.3), (0.4 + 0.1 * k, t / 2 + 2.0), "RAMPA") for k in range(18)]
    assert O._grille_bars(_gap(0.0, 2.5, t), _index(*grooves, *sides, *arrows), set()) is None


def test_hatch_floors_and_treads_are_no_grille():
    g = _gap()
    hatch = [_line(f"h{k}", (0.05 + 0.1 * k, -0.135), (0.05 + 0.1 * k, 0.135)) for k in range(17)]     # face to face
    through = [_line(f"f{k}", (0.1 + 0.1 * k, -0.6), (0.1 + 0.1 * k, 0.6), "ZEMIN") for k in range(17)]  # both sides
    runs_on = [_line(f"r{k}", (-1.0 + 0.1 * k, 0.135), (-1.0 + 0.1 * k, -0.5), "ZEMIN") for k in range(40)]
    treads = [_line(f"t{k}", (0.1 + 0.28 * k, 0.135), (0.1 + 0.28 * k, -1.0)) for k in range(6)]
    tiles = _c0089_grille(layer="KARO")                                  # a finish layer: tiles, never a grille
    for strokes in (hatch, through, runs_on, treads, tiles):
        assert O._grille_bars(g, _index(*strokes), set()) is None


def test_real_unlabelled_rooms_bounded_by_walls_keep_their_type():
    # a closet behind a door: storage; a shaft no door reaches and no window opens onto: unknown, as before
    walls = [_wall_item((0.0, 0.0), (2.0, 0.0)), _wall_item((2.0, 0.0), (2.0, 1.2)), _wall_item((2.0, 1.2), (0.0, 1.2)),
             _wall_item((0.0, 1.2), (0.0, 0.0))]
    face = [(0.1, 0.1), (1.9, 0.1), (1.9, 1.1), (0.1, 1.1)]
    door = _door_item(1.0, 0.0, 0.8)
    kind, why = TP.unlabelled_face_type(face, walls, [door])
    assert kind == "storage", why
    kind, why = TP.unlabelled_face_type(face, walls, [])
    assert kind == "unknown", why


def _wall_item(a, b, t=0.2):
    from wenart.ingest.model import WallItem

    return WallItem(a, b, t, [0, 0, 0, 0], "LWPOLYLINE:W", {})


def _door_item(x, y, w):
    from wenart.ingest.model import OpeningItem

    return OpeningItem(kind="door", width=w, center=(x, y), rotation_deg=0.0, box=[0, 0, 0, 0], entity="ARC:1",
                       evidence={"method": "vector"})


# --- RC14 unnamed_exit ---------------------------------------------------------------------------------------------------

def _building(label_raw=None, entity="LINE:1,LINE:2", block=None, other_door=False, tag=None):
    rooms = [{"id": "r_slot", "level_id": "L-1", "label": "Oda", "label_raw": label_raw, "room_type": "unknown",
              "polygon": [[0.0, 0.0], [1.8, 0.0], [1.8, 3.6], [0.0, 3.6]]},
             {"id": "r_bath", "level_id": "L-1", "label": "Banyo", "label_raw": "banyo", "room_type": "bathroom",
              "polygon": [[0.0, -3.0], [1.8, -3.0], [1.8, -0.2], [0.0, -0.2]]}]
    walls = [{"id": "w_out", "level_id": "L-1", "start": [-2.0, 3.735], "end": [4.0, 3.735], "thickness": 0.27,
              "exterior": True},
             {"id": "w_in", "level_id": "L-1", "start": [-2.0, -0.1], "end": [4.0, -0.1], "thickness": 0.2,
              "exterior": False}]
    ev = {"method": "vector", "entity": entity}
    if block:
        ev["block"] = block
    if tag:
        ev.update(text=tag, rule="size_tag")
    ops = [{"id": "d_1", "type": "door", "level_id": "L-1", "wall_id": "w_out", "center": [0.9, 3.735], "width": 1.8,
            "evidence": [ev]}]
    if other_door:
        ops.append({"id": "d_2", "type": "door", "level_id": "L-1", "wall_id": "w_in", "center": [0.9, -0.1],
                    "width": 0.8, "evidence": [{"method": "vector", "entity": "ARC:9"}]})
    return {"levels": [{"id": "L-1", "elevation": -3.0}], "rooms": rooms, "walls": walls, "openings": ops}


def test_rc14_unnamed_exit_names_an_unnamed_faces_only_door_drawn_without_a_swing():
    found = SN.unnamed_exit(_building())
    assert [f["element_ids"] for f in found] == [["d_1", "r_slot"]] and found[0]["severity"] == "major"
    assert SN.apply_trust(found, SN.load_trust())[0]["severity"] == "info"          # not calibrated: info only
    # a label, a swing arc, a door block, a door-high size tag (swiss-b1479's '105/210') or a second door: no finding
    for kw in ({"label_raw": "depo"}, {"entity": "ARC:5,LINE:6"}, {"block": "KAPI_90"}, {"other_door": True},
               {"tag": "105/210"}):
        assert SN.unnamed_exit(_building(**kw)) == [], kw


def test_the_rule_is_registered_and_the_check_is_uncalibrated():
    assert "unnamed_exit" in SN.RULES
    trust = SN.load_trust()["rules"]["unnamed_exit"]
    assert trust["precision"] is None and trust["trusted"] is False
    assert "window_grille" in DEC.RULE_CONFIDENCE


# --- synthetic-35-grille-slot end to end -----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def reading(tmp_path_factory):
    from wenart.ingest import pipeline as PL

    root = tmp_path_factory.mktemp("rules_c0089")
    project = WP.project_35()
    FC.generate_failure_project(project, root)
    building, _build = PL.run_project(root / project.name, root / f"{project.name}-out", no_ai=True)
    return project, root, building


def _at(building, x, y, kind=None):
    return [o for o in building["openings"] if (kind is None or o["type"] == kind)
            and math.dist(o["center"][:2], (x, y)) <= 0.3]


def test_synthetic_35_reads_the_grille_and_keeps_the_others(reading):
    _project, _root, b = reading
    grille = _at(b, 7.2, 8.875)
    assert len(grille) == 1 and grille[0]["type"] == "window" and grille[0]["operation"] == "fixed"
    assert "grille" in grille[0]["evidence"][0]["note"]
    slot = [r for r in b["rooms"] if r["polygon"] and 6.3 <= sum(p[0] for p in r["polygon"]) / len(r["polygon"]) <= 8.1
            and sum(p[1] for p in r["polygon"]) / len(r["polygon"]) > 6.0]
    assert len(slot) == 1 and slot[0]["room_type"] == "shaft"                # a light well, never furnished
    assert [o["type"] for o in _at(b, 0.125, 5.1)] == ["door"]               # the entrance, open leaf, step outside
    assert [o["type"] for o in _at(b, 11.875, 2.2)] == ["door"]              # the French window over the balustrade
    assert [o["type"] for o in _at(b, 1.8, 5.8)] == ["opening"]              # the kitchen's way in, boards through it
    assert [f for f in SN.run(copy.deepcopy(b), apply=False) if f["rule"] == "unnamed_exit"] == []


def test_synthetic_35_scores_100(reading):
    from wenart.reading_check import truth as TR

    project, root, b = reading
    truth = TR.synthetic_truth(project.name, root / project.name / FC.TRUTH_FILE)
    assert SC.match(truth, SC.reading_for(truth, b, project.name), b)["total"] == 100.0
