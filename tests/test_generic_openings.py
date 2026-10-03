"""Openings of the generic plan core (docs/milestone7.md §2.6, §11 G2).

Synthetic walls (metres) check the three gap kinds (run gap, end gap from a free end, run gap split by a
perpendicular wall end), the classes (door with/without leaf, double door, window, doorless, unclassified, closed),
the exterior empty gap, the owned strokes, the merged/extended walls and the continuous-wall symbols of the synthetic
convention. real01 checks 5/5 doors (two on the split run gap at x 11.0 ft, the bath and store doors on extended
walls), 9 windows and the 3 doorless openings O1, O3, O5 against tests/fixtures/real01_reference.yaml.
"""
import math

import pytest

import _real01_page as R
from wenart.ingest.generic import openings as O

FT = 0.3048


def _door(hinge, radius, closed_deg, open_deg, leaf=True):
    """Swing arc from the closed to the open position plus a 30 mm leaf along the open radius."""
    strokes = [R.arc(hinge, radius, closed_deg, open_deg)]
    if leaf:
        t = math.radians(open_deg)
        d = (math.cos(t), math.sin(t))
        n = (-d[1], d[0])
        p0 = (hinge[0] + d[0] * 0.03, hinge[1] + d[1] * 0.03)
        p1 = (hinge[0] + d[0] * 0.95 * radius, hinge[1] + d[1] * 0.95 * radius)
        strokes.append(R.stroke([p0, p1, (p1[0] + n[0] * 0.03, p1[1] + n[1] * 0.03),
                                 (p0[0] + n[0] * 0.03, p0[1] + n[1] * 0.03)], closed=True))
    return strokes


def _run(walls, strokes):
    return O.gaps_and_openings(walls, strokes, "test.pdf", 1)


# --------------------------------------------------------------------------
# Run gaps
# --------------------------------------------------------------------------

def test_run_gap_with_a_door_closes_the_run():
    walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, 0), (5, 0))]
    door = _door((2.88, 0.08), 0.88, 180, 90)
    out_walls, openings, log, owned = _run(walls, door)
    assert len(out_walls) == 1
    w = out_walls[0]
    assert (w.start, w.end) == ((0.0, 0.0), (5.0, 0.0))
    assert "run of 2 pieces" in w.evidence["note"]
    assert len(openings) == 1
    d = openings[0]
    assert d.kind == "door" and d.width == pytest.approx(0.9)
    assert d.center == pytest.approx((2.45, 0.0))
    assert d.evidence["confidence"] == 0.95                       # with a leaf
    assert d.rotation_deg == 0.0                                  # swings to the left of +x (north)
    assert d.swing_point[1] > 0.2
    assert d.height == 2.10 and d.assumed == ["height"]
    assert {s.id for s in door} <= owned
    gap = [e for e in log if e["kind"] == "run"][0]
    assert gap["class"] == "door" and gap["leaf"] is True and gap["radius"] == pytest.approx(0.88)


def test_door_without_leaf_has_lower_confidence_and_south_swing():
    walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, 0), (5, 0))]
    door = _door((2.0, -0.05), 0.9, 0, -90, leaf=False)          # hinged at the west jamb, swings south
    _, openings, _, _ = _run(walls, door)
    assert [o.kind for o in openings] == ["door"]
    assert openings[0].evidence["confidence"] == 0.85
    assert openings[0].rotation_deg == 180.0
    assert "without a drawn leaf" in openings[0].evidence["note"]


def test_double_door_has_two_arcs_of_half_the_gap():
    walls = [R.wall((0, 0), (2, 0)), R.wall((3.6, 0), (6, 0))]
    strokes = _door((2.02, 0.08), 0.79, 0, 90) + _door((3.58, 0.08), 0.79, 180, 90)
    _, openings, _, _ = _run(walls, strokes)
    assert [o.kind for o in openings] == ["door"]
    assert openings[0].width == pytest.approx(1.6)


def test_window_needs_two_parallel_band_lines():
    walls = [R.wall((0, 0), (2, 0)), R.wall((3.2, 0), (5, 0))]
    lines = [R.stroke([(2.0, -0.03), (3.2, -0.03)]), R.stroke([(2.0, 0.03), (3.2, 0.03)])]
    _, openings, log, owned = _run(walls, lines)
    assert [o.kind for o in openings] == ["window"]
    win = openings[0]
    assert win.width == pytest.approx(1.2) and win.sill == 0.90 and win.height == 1.20
    assert win.assumed == ["height", "sill_height"]
    assert win.evidence["confidence"] == 0.9
    assert {s.id for s in lines} <= owned
    # A band line running far past the gap (a wall face line, a bed edge) is not owned.
    face = R.stroke([(-1.0, 0.09), (6.0, 0.09)])
    _, openings2, _, owned2 = _run(walls, lines + [face])
    assert [o.kind for o in openings2] == ["window"] and face.id not in owned2


def _room_with_partition(gap_lo, gap_hi):
    """A 6 x 4 m box with a partition at x 3 that has a gap from y gap_lo to gap_hi."""
    outer = [R.wall((0, 0), (6, 0)), R.wall((6, 0), (6, 4)), R.wall((6, 4), (0, 4)), R.wall((0, 4), (0, 0))]
    part = [R.wall((3, 0), (3, gap_lo), 0.15), R.wall((3, gap_hi), (3, 4), 0.15)]
    return outer + part


def test_doorless_interior_gap_is_a_verified_opening():
    _, openings, log, _ = _run(_room_with_partition(1.5, 2.5), [])
    assert [o.kind for o in openings] == ["opening"]
    o = openings[0]
    assert o.status == "verified" and o.width == pytest.approx(1.0)
    assert o.height == 2.10 and o.assumed == ["height"]
    assert o.evidence["method"] == "derived" and o.evidence["confidence"] == 0.8


def test_empty_gap_in_an_exterior_wall_is_unverified():
    walls = [R.wall((0, 0), (2, 0)), R.wall((3, 0), (6, 0)), R.wall((6, 0), (6, 4)), R.wall((6, 4), (0, 4)),
             R.wall((0, 4), (0, 0))]
    _, openings, _, _ = _run(walls, [])
    assert [o.kind for o in openings] == ["opening"]
    assert openings[0].status == "unverified"
    assert "possible undrawn door or window" in openings[0].evidence["note"]


def test_unclassified_gap_content_is_listed():
    walls = _room_with_partition(1.5, 2.5)
    junk = R.stroke([(2.95, 1.8), (3.05, 2.2)])                    # a diagonal stroke in the band
    _, openings, log, _ = _run(walls, [junk])
    assert openings[0].kind == "opening" and openings[0].status == "unverified"
    assert openings[0].type_raw == "unclassified gap content"
    entry = [e for e in log if e.get("class") == "unclassified"][0]
    assert entry["strokes"] == [junk.id]


def test_gap_below_25_cm_is_closed_with_a_warning():
    walls = [R.wall((0, 0), (2, 0)), R.wall((2.1, 0), (5, 0))]
    out_walls, openings, log, _ = _run(walls, [])
    assert len(out_walls) == 1 and not openings
    entry = [e for e in log if e["kind"] == "run"][0]
    assert entry["class"] == "closed" and "closed" in entry["warning"]


def test_gap_over_3_m_stays_open_and_splits_the_run():
    walls = [R.wall((0, 0), (2, 0)), R.wall((5.5, 0), (8, 0))]
    out_walls, openings, log, _ = _run(walls, [])
    assert len(out_walls) == 2 and not openings
    assert [e["class"] for e in log if e["kind"] == "run"] == ["open"]


# --------------------------------------------------------------------------
# End gaps and split gaps
# --------------------------------------------------------------------------

def test_end_gap_with_a_door_extends_the_free_end_wall():
    walls = [R.wall((3, -2), (3, 2), 0.2, entity="perp"), R.wall((0, 0), (2, 0), 0.15, entity="free")]
    door = _door((2.88, 0.06), 0.88, 180, 90)
    out_walls, openings, log, owned = _run(walls, door)
    ext = [w for w in out_walls if w.entity.startswith("free")][0]
    assert ext.end == pytest.approx((2.9, 0.0)) or ext.start == pytest.approx((2.9, 0.0))
    assert ext.evidence["method"] == "derived"
    assert "extended to host the drawn door" in ext.evidence["note"]
    assert {s.id for s in door[:1]} <= set(ext.entity.split(","))
    assert [o.kind for o in openings] == ["door"]
    assert openings[0].center == pytest.approx((2.45, 0.0)) and openings[0].width == pytest.approx(0.9)
    entry = [e for e in log if e["kind"] == "end"][0]
    assert entry["class"] == "door" and entry["free_end"] == "end"
    # The other end of the free wall hits nothing within 3 m.
    assert any(e["kind"] == "free_end" and e["gap_class"] == "none" for e in log)


def test_empty_end_gap_is_only_a_separator_candidate():
    walls = [R.wall((3, -2), (3, 2), 0.2), R.wall((0, 0), (1.8, 0), 0.15)]
    out_walls, openings, log, _ = _run(walls, [])
    assert not openings
    assert [math.dist(w.start, w.end) for w in out_walls if w.thickness == 0.15] == [pytest.approx(1.8)]
    entry = [e for e in log if e["kind"] == "end"][0]
    assert entry["class"] == "empty" and entry["width"] == pytest.approx(1.1)
    assert entry["line"] == [[1.8, 0.0], [2.9, 0.0]]
    free = [e for e in log if e["kind"] == "free_end" and e["gap_class"] == "empty"]
    assert len(free) == 1 and free[0]["direction"] == [1.0, 0.0]


def test_run_gap_split_by_a_perpendicular_wall_end_gives_two_doors():
    run = [R.wall((0, 0), (0, 2), 0.15), R.wall((0, 3.2), (0, 5), 0.15)]
    perp = R.wall((-3, 2.6), (0.075, 2.6), 0.15)                  # ends at the far face of the run band
    strokes = _door((-0.06, 2.02), 0.51, 90, 180) + _door((-0.06, 3.18), 0.51, 270, 180)
    out_walls, openings, log, _ = _run(run + [perp], strokes)
    doors = sorted((o for o in openings if o.kind == "door"), key=lambda o: o.center[1])
    assert len(doors) == 2
    assert doors[0].center == pytest.approx((0.0, 2.2625)) and doors[0].width == pytest.approx(0.525)
    assert doors[1].center == pytest.approx((0.0, 2.9375)) and doors[1].width == pytest.approx(0.525)
    assert [e["kind"] for e in log if e["kind"] in ("run", "split")] == ["split", "split"]
    merged = [w for w in out_walls if w.thickness == 0.15 and abs(w.start[0]) < 1e-9 and abs(w.end[0]) < 1e-9]
    assert len(merged) == 1 and math.dist(merged[0].start, merged[0].end) == pytest.approx(5.0)
    # The perpendicular wall ends at the face of the through-wall.
    perp_out = [w for w in out_walls if w.start[1] == 2.6][0]
    assert max(perp_out.start[0], perp_out.end[0]) == pytest.approx(-0.075)


def test_door_beside_a_perpendicular_wall_in_an_open_run_gap_is_an_end_gap():
    """A run gap over 3 m stays open, but a free end facing a perpendicular wall inside it still hosts a door."""
    run = [R.wall((0, 0), (2, 0), 0.15), R.wall((7, 0), (9, 0), 0.15)]
    perp = R.wall((3.0, -3), (3.0, 0.075), 0.2)                    # sub-gaps 0.9 m and 3.9 m: the run gap is open
    door = _door((2.88, 0.06), 0.87, 180, 90)                    # in the 0.9 m end gap from x 2.0 to the wall face
    out_walls, openings, log, _ = _run(run + [perp], door)
    assert [o.kind for o in openings] == ["door"]
    assert openings[0].center == pytest.approx((2.45, 0.0))
    assert [e["class"] for e in log if e["kind"] == "split"] == ["open", "open"]
    assert [e["class"] for e in log if e["kind"] == "end"] == ["door"]
    assert len([w for w in out_walls if w.thickness == 0.15]) == 2  # the open gap keeps the pieces apart


# --------------------------------------------------------------------------
# Continuous-wall symbols (synthetic convention)
# --------------------------------------------------------------------------

def test_continuous_wall_door_and_window_of_the_synthetic_convention():
    w = R.wall((0, 0), (6, 0), 0.2)
    # Door as wenart.synthetic.pdf_writer._draw_door draws it: hinge on the centre line, leaf to the tip, 90 deg arc.
    hinge, tip = (1.55, 0.0), (1.55, 0.9)
    door = [R.stroke([hinge, tip]), R.arc(hinge, 0.9, 0, 90)]
    # Window as _draw_window: a 0.1 m deep rectangle of four lines on the wall centre line.
    win = [R.stroke([(3.9, -0.05), (5.1, -0.05)]), R.stroke([(3.9, 0.05), (5.1, 0.05)]),
           R.stroke([(3.9, -0.05), (3.9, 0.05)]), R.stroke([(5.1, -0.05), (5.1, 0.05)])]
    out_walls, openings, log, owned = _run([w], door + win + R.wall_faces(w))
    kinds = sorted(o.kind for o in openings)
    assert kinds == ["door", "window"]
    d = [o for o in openings if o.kind == "door"][0]
    assert d.center == pytest.approx((2.0, 0.0)) and d.width == pytest.approx(0.9)
    assert d.rotation_deg == 0.0 and d.swing_point[1] > 0
    wi = [o for o in openings if o.kind == "window"][0]
    assert wi.center == pytest.approx((4.5, 0.0), abs=1e-6) and wi.width == pytest.approx(1.2)
    assert {door[0].id, door[1].id} <= owned
    assert len([e for e in log if e["kind"] == "continuous"]) == 2


def test_solid_wall_faces_alone_are_not_a_window():
    w = R.wall((0, 0), (6, 0), 0.2)
    faces = R.wall_faces(w) + R.wall_faces(w)                    # duplicated face lines (an outline polyline)
    _, openings, _, _ = _run([w], faces)
    assert openings == []


# --------------------------------------------------------------------------
# real01
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def chain():
    return R.g2_chain()


def _ref_ft(p):
    return R.to_ref(p)


def _match(found, ref_items, centre_tol, width_tol):
    """Greedy one-to-one matching by centre; returns (matched pairs, unmatched refs, unmatched found)."""
    pairs, used = [], set()
    for r in ref_items:
        best = None
        for k, o in enumerate(found):
            if k in used:
                continue
            c = _ref_ft(o.center)
            d = math.dist(c, r["centre_ft"])
            if d <= centre_tol and abs(o.width / FT - r["width_ft"]) <= width_tol and (best is None or d < best[0]):
                best = (d, k)
        if best is not None:
            used.add(best[1])
            pairs.append((r, found[best[1]]))
    missing = [r for r in ref_items if r not in [p[0] for p in pairs]]
    extra = [o for k, o in enumerate(found) if k not in used]
    return pairs, missing, extra


def test_real01_doors(chain):
    ref = R.reference()
    doors = [o for o in chain["openings"] if o.kind == "door"]
    tol = ref["tolerances_default"]["door"]
    pairs, missing, extra = _match(doors, ref["doors"], tol["centre"], tol["width"])
    assert not missing and not extra, (missing, extra)
    for r, o in pairs:
        assert o.evidence["confidence"] == 0.95, r["id"]             # every real01 door has its leaf drawn
        # The swing point lies in the room the door opens into.
        swing_ft = _ref_ft(o.swing_point)
        hinge_side = math.dist(swing_ft, r["swing_point_ft"]) < math.dist(_ref_ft(o.center), r["swing_point_ft"])
        assert hinge_side, r["id"]
    log = chain["gap_log"]
    radii = [e["radius"] for e in log if e.get("class") == "door"]
    assert len(radii) == 5 and all(0.72 <= r <= 1.02 for r in radii)
    # D1 and D2 share the run gap at x 11.0 ft that the bedroom wall's end splits in two.
    split = [e for e in log if e["kind"] == "split" and e["class"] == "door"]
    assert len(split) == 2
    assert all(abs(_ref_ft(e["p0"])[0] - 11.006) <= 0.05 for e in split)
    # The bath and store doors sit on walls extended over an end gap; the entrance is a run gap.
    ends = [e for e in log if e["kind"] == "end" and e["class"] == "door"]
    assert sorted(round(_ref_ft(((e["p0"][0] + e["p1"][0]) / 2, 0))[0]) for e in ends) == [15, 40]
    extended = [w for w in chain["walls"] if "extended to host the drawn door" in w.evidence.get("note", "")]
    assert len(extended) == 2 and all(w.evidence["method"] == "derived" for w in extended)
    run_doors = [e for e in log if e["kind"] == "run" and e["class"] == "door"]
    assert len(run_doors) == 1
    assert abs(_ref_ft(run_doors[0]["p0"])[0] - 31.131) <= 0.05


def test_real01_windows(chain):
    ref = R.reference()
    windows = [o for o in chain["openings"] if o.kind == "window"]
    tol = ref["tolerances_default"]["window"]
    pairs, missing, extra = _match(windows, ref["windows"], tol["centre"], tol["width"])
    assert not missing and not extra, (missing, extra)
    assert all(w.assumed == ["height", "sill_height"] for w in windows)


def test_real01_doorless_openings(chain):
    ref = R.reference()
    doorless = [o for o in chain["openings"] if o.kind == "opening"]
    want = [o for o in ref["openings"] if o["kind"] == "wall_gap"]          # O1, O3, O5
    tol = ref["tolerances_default"]["opening"]
    pairs, missing, extra = _match(doorless, want, tol["centre"], tol["width"])
    assert not missing and not extra, (missing, extra)
    assert all(o.status == "verified" for o in doorless)                     # interior gaps
    # O2 is an empty end gap from the dining wall's free end to the kitchen pier: a separator candidate.
    o2 = [o for o in ref["openings"] if o["id"] == "O2"][0]
    empty = [e for e in chain["gap_log"] if e["kind"] == "end" and e["class"] == "empty"]
    assert len(empty) == 1
    assert empty[0]["width"] / FT == pytest.approx(o2["width_ft"], abs=0.1)


def test_real01_owned_strokes(chain):
    owned = chain["owned"]
    for arc_id in ("curve:4", "curve:10", "curve:15", "curve:20", "curve:1281"):    # the five swing arcs
        assert arc_id in owned
    assert {"curve:13", "line:11559", "curve:14"} <= owned                        # D1's leaf and hinge pin
    assert "line:15499" not in owned                                              # the bed edge in W1's band
    assert "curve:1392" not in owned                                              # the bed corner by W4


def test_real01_merged_walls(chain):
    walls = chain["walls"]
    assert len(walls) == 17                                       # 13 house walls + 4 plot walls
    runs = [w for w in walls if "run of" in w.evidence.get("note", "")]
    assert len(runs) >= 8
    x31 = [w for w in walls if abs(_ref_ft(w.start)[0] - 31.131) < 0.05 and abs(_ref_ft(w.end)[0] - 31.131) < 0.05]
    assert len(x31) == 1                                          # W_ENT + P_1 + P_2: one run with D5, O5, O1
