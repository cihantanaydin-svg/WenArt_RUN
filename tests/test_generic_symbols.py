"""Furniture clusters, composites, rules and site decor of the generic plan core (docs/milestone7.md §2.8, §11 G2).

Synthetic rooms (metres) check the segment-wise outline removal, the containment exception (a sink in a counter
stays its own piece; a bed's inner outline and pillows do not), the composite split (table and chairs, bed and
nightstands; sofa cushions stay one sofa), the unsplittable composite, the stair rule (dedupe, divider split,
flights), the kitchen counter rule (chaining, wall faces incl. openings), the front candidates, block names and the
site decor. real01 checks every reference piece: 2 beds, 4 nightstands, 1 table, 6 chairs, 2 sofas, the coffee table,
the round piece, the 2 counter legs and the stair, no cluster over 4.5 m, and 9 plants plus the entrance step.
"""
import math

import pytest
from shapely.geometry import box as sbox

import _real01_page as R
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.model import OpeningItem

FT = 0.3048
TABLE = SY.FALLBACK_SIZE_TABLE


def _room(x0=0.0, y0=0.0, x1=6.0, y1=5.0, t=0.2):
    return [R.wall((x0, y0), (x1, y0), t), R.wall((x1, y0), (x1, y1), t), R.wall((x1, y1), (x0, y1), t),
            R.wall((x0, y1), (x0, y0), t)]


def _furn(strokes, walls=None, openings=(), faces=(), texts=(), dims=(), site_walls=(), notes=None):
    walls = walls or _room()
    outline = TP.building_outline(walls, list(openings))
    return SY.furniture(strokes, set(), walls, list(openings), list(texts), list(dims), outline, list(faces),
                        site_walls=list(site_walls), level_id="L0", file_rel="t.pdf", page_no=1,
                        size_table=TABLE, notes=notes)


def _all(pieces, cands):
    return list(pieces) + [c["item"] for c in cands]


def _rect_strokes(x0, y0, x1, y1, **kw):
    return [R.stroke(seg, **kw) for seg in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)),
                                            ((x0, y1), (x0, y0)))]


# --------------------------------------------------------------------------
# Strokes considered and clusters
# --------------------------------------------------------------------------

def test_wall_outline_segments_of_a_polyline_are_dropped_segment_by_segment():
    # One polyline: along the north wall face (outline), then down and back: a counter front 0.6 m from the wall.
    poly = R.stroke([(0.1, 4.9), (2.5, 4.9), (2.5, 4.3), (0.1, 4.3)])
    table = _rect_strokes(2.5, 1.5, 3.7, 2.3)
    notes = []
    pieces, cands, decor = _furn([poly] + table, notes=notes)
    found = _all(pieces, cands)
    assert any("dropped as wall outline" in n for n in notes)
    # The table is one candidate; the polyline's wall-face segment is in no piece.
    assert any(c["fits"] and "table_dining" in c["fits"] for c in cands)
    for c in cands:
        for pts in c["strokes"]:
            assert not (abs(pts[0][1] - 4.9) < 1e-6 and abs(pts[-1][1] - 4.9) < 1e-6)
    assert all(max(p.size) <= SY.MAX_SIDE_M for p in found)


def test_glyph_and_dimension_strokes_are_ignored():
    glyph = R.stroke([(1.0, 1.0), (1.2, 1.3)])
    dim = R.stroke([(0.5, 3.0), (5.5, 3.0)])
    text = type("T", (), {"box": (0.95, 0.95, 1.25, 1.35)})()
    dims = [R.DimStub({dim.id})]
    pieces, cands, _ = _furn([glyph, dim], texts=[text], dims=dims)
    assert pieces == [] and cands == []


def test_contained_sink_stays_its_own_piece_but_a_bed_outline_and_pillows_do_not():
    counter = [R.stroke([(0.1, 4.3), (2.5, 4.3)]), R.stroke([(2.5, 4.3), (2.5, 4.9)]),
               R.stroke([(0.1, 4.9), (2.5, 4.9)]), R.stroke([(0.1, 4.3), (0.1, 4.9)])]
    sink = _rect_strokes(0.8, 4.35, 1.6, 4.85)                       # 0.8 x 0.5 inside the 0.6 m deep counter
    bed = _rect_strokes(3.5, 0.5, 5.1, 2.5)                          # 1.6 x 2.0
    inner = _rect_strokes(3.55, 0.55, 5.05, 2.45)                    # the double outline, 25 mm inside
    pillows = _rect_strokes(3.7, 2.0, 4.25, 2.35) + _rect_strokes(4.35, 2.0, 4.9, 2.35)
    pieces, cands, _ = _furn(counter + sink + bed + inner + pillows)
    items = _all(pieces, cands)
    sizes = sorted(tuple(round(v, 2) for v in sorted(p.size)) for p in items)
    assert (0.5, 0.8) in sizes                                       # the sink
    assert (1.6, 2.0) in sizes                                       # the bed, with its outline and pillows
    assert not [s for s in sizes if s in ((0.35, 0.55), (1.5, 1.9))]


def test_composite_split_table_and_chairs_and_sofa_cushions_stay_together():
    table = _rect_strokes(2.0, 1.5, 3.6, 2.4)                        # 1.6 x 0.9
    chairs = (_rect_strokes(2.3, 1.05, 2.75, 1.5) + _rect_strokes(2.85, 1.05, 3.3, 1.5)      # touch the table edge
              + _rect_strokes(2.3, 2.4, 2.75, 2.85) + _rect_strokes(2.85, 2.4, 3.3, 2.85))
    sofa = (_rect_strokes(1.0, 3.8, 1.6, 4.4) + _rect_strokes(1.6, 3.8, 2.2, 4.4) + _rect_strokes(2.2, 3.8, 2.8, 4.4)
            + [R.stroke([(0.9, 4.45), (2.9, 4.45)]), R.stroke([(0.9, 3.75), (0.9, 4.45)]),
               R.stroke([(2.9, 3.75), (2.9, 4.45)])])
    pieces, cands, _ = _furn(table + chairs + sofa)
    sizes = sorted(tuple(round(v, 2) for v in sorted(c["footprint"]["size"])) for c in cands)
    assert sizes.count((0.45, 0.45)) == 4
    assert (0.9, 1.6) in sizes
    sofas = [s for s in sizes if s[1] >= 1.9]
    assert sofas == [(0.7, 2.0)]                                       # one sofa, not three cushions
    assert not pieces


def test_unsplittable_group_stays_one_unknown_composite():
    lines = [R.stroke([(1.0 + 0.4 * k, 0.5), (1.2 + 0.4 * k, 3.9)]) for k in range(9)]   # 3.4 m x 3.4 m of hatching
    lines += [R.stroke([(1.0, 0.5 + 0.4 * k), (4.4, 0.7 + 0.4 * k)]) for k in range(9)]
    notes = []
    pieces, cands, _ = _furn(lines, notes=notes)
    assert not cands
    assert len(pieces) == 1
    p = pieces[0]
    assert p.type == "unknown" and p.status == "unverified" and p.type_method == "none"
    assert "fits no size-table type" in p.evidence["note"] or "possible group" in p.evidence["note"]


def test_details_and_oversize_clusters():
    speck = _rect_strokes(2.0, 3.0, 2.1, 3.1)
    big = _rect_strokes(0.5, 0.5, 5.5, 1.0) + [R.stroke([(1.0, 0.6), (5.0, 0.9)])]
    notes = []
    pieces, cands, _ = _furn(speck + big, notes=notes)
    assert [p.details.get("oversize") for p in pieces] == [True]
    assert any("details smaller than" in n for n in notes)


# --------------------------------------------------------------------------
# Rules: stair, counter, block names, fronts
# --------------------------------------------------------------------------

def _stair_strokes(x0=1.0, y0=1.0, width=1.5, step=0.25, n=8, divider=True, duplicates=True):
    out = [R.stroke([(x0, y0 + k * step), (x0 + width, y0 + k * step)]) for k in range(n)]
    if duplicates:
        out += [R.stroke([(x0, y0 + k * step), (x0 + width / 2, y0 + k * step)]) for k in range(n)]
    if divider:
        out.append(R.stroke([(x0 + width / 2, y0), (x0 + width / 2, y0 + (n - 1) * step + 0.66)]))
    return out


def test_stair_rule_two_flights_split_at_the_divider():
    pieces, cands, _ = _furn(_stair_strokes())
    stairs = [p for p in pieces if p.type == "stair"]
    assert len(stairs) == 1 and not cands
    s = stairs[0]
    assert s.type_method == "rule" and s.status == "verified"
    st = s.details["stair"]
    assert len(st["flights"]) == 2
    assert all(f["lines"] == 8 and f["width"] == pytest.approx(0.75) and f["spacing"] == pytest.approx(0.25)
               for f in st["flights"])
    assert st["landing"]["depth"] == pytest.approx(0.66)
    assert st["direction_assumed"] and st["turn_assumed"] and st["turn"] == "U"
    assert sorted(s.size) == pytest.approx([1.5, 1.75 + 0.66])


def test_stair_rule_single_flight_and_uneven_lines():
    stringers = [R.stroke([(1.0, 1.0), (1.0, 2.75)]), R.stroke([(2.5, 1.0), (2.5, 2.75)])]   # side lines
    pieces, _, _ = _furn(_stair_strokes(divider=False, duplicates=False) + stringers)
    st = [p for p in pieces if p.type == "stair"][0].details["stair"]
    assert len(st["flights"]) == 1 and st["flights"][0]["lines"] == 8 and st["turn"] == "straight"
    uneven = [R.stroke([(1.0, 1.0 + y), (2.5, 1.0 + y)]) for y in (0, 0.25, 0.5, 0.9, 1.0, 1.5, 1.55)]
    pieces2, _, _ = _furn(uneven + [R.stroke([(1.0, 1.0), (1.0, 2.55)]), R.stroke([(2.5, 1.0), (2.5, 2.55)])])
    assert not [p for p in pieces2 if p.type == "stair"]


def test_kitchen_counter_rule_l_shape_with_a_window_behind():
    walls = _room(0, 0, 4, 4)
    window = OpeningItem(kind="window", width=1.2, center=(2.0, 4.0), rotation_deg=0.0, box=[], entity="w",
                         evidence={})
    chain = [R.stroke([(0.8, 3.9), (0.8, 3.3)]), R.stroke([(0.8, 3.3), (3.3, 3.3)]),
             R.stroke([(3.3, 3.3), (3.3, 2.0)]), R.stroke([(3.3, 2.0), (3.9, 2.0)])]
    faces = [{"polygon": sbox(0.1, 0.1, 3.9, 3.9), "room_type": "kitchen", "label": "Kitchen"}]
    pieces, cands, _ = _furn(chain, walls=walls, openings=[window], faces=faces)
    counters = sorted((p for p in pieces if p.type == "kitchen_counter"), key=lambda p: -p.size[0])
    assert len(counters) == 2 and not cands
    north, east = counters
    assert north.size == pytest.approx((3.1, 0.6))                 # 0.8 -> 3.9: the corner square goes to it
    assert north.front_deg == 270.0 and north.rotation_deg == 0.0
    assert east.size == pytest.approx((1.3, 0.6))
    assert east.front_deg == 180.0 and east.rotation_deg == 270.0
    assert all(p.status == "verified" and p.type_method == "rule" for p in counters)
    assert north.details["counter_run"]["strokes"]


def test_counter_outside_a_kitchen_is_unverified():
    walls = _room(0, 0, 4, 4)
    chain = [R.stroke([(0.8, 3.9), (0.8, 3.3)]), R.stroke([(0.8, 3.3), (3.3, 3.3)]), R.stroke([(3.3, 3.3), (3.3, 3.9)])]
    faces = [{"polygon": sbox(0.1, 0.1, 3.9, 3.9), "room_type": "bedroom", "label": "Bed Room"}]
    notes = []
    pieces, _, _ = _furn(chain, walls=walls, faces=faces, notes=notes)
    assert [p.status for p in pieces if p.type == "kitchen_counter"] == ["unverified"]
    assert any("not in a kitchen" in n for n in notes)


def test_block_names_type_dxf_pieces():
    bed = _rect_strokes(1.0, 1.0, 2.6, 3.0, block="PLAN/BED-DOUBLE")
    wc = _rect_strokes(3.5, 1.0, 5.5, 3.0, block="WC")                # 2 x 2 m: not a toilet
    pieces, cands, _ = _furn(bed + wc)
    by_type = {p.type: p for p in pieces}
    assert by_type["bed_double"].type_method == "block_name" and by_type["bed_double"].status == "verified"
    assert by_type["bed_double"].type_raw == "PLAN/BED-DOUBLE"
    assert by_type["toilet"].status == "unverified" and "does not fit" in by_type["toilet"].evidence["note"]
    assert not cands


def test_front_candidates():
    # A sofa with its back 0.1 m from the south wall faces north.
    sofa = _rect_strokes(2.0, 0.2, 4.0, 1.1)
    # A bed with two pillows at its west end: the head is west, so it faces east.
    bed = _rect_strokes(0.2, 2.5, 2.2, 4.1) + _rect_strokes(0.3, 2.7, 0.65, 3.25) + _rect_strokes(0.3, 3.35, 0.65, 3.9)
    pieces, cands, _ = _furn(sofa + bed)
    by_size = {tuple(sorted(round(v, 1) for v in c["footprint"]["size"])): c for c in cands}
    sofa_c = by_size[(0.9, 2.0)]
    assert {f["front_deg"] for f in sofa_c["front_candidates"]} == {90.0}
    bed_c = by_size[(1.6, 2.0)]
    assert [f["front_deg"] for f in bed_c["front_candidates"]] == [0.0]      # wall rule and pillows agree
    assert "head = side with >= 2 small closed shapes" in bed_c["front_candidates"][0]["rule"]
    assert all(c["item"].front_deg is None for c in cands)          # fronts wait for the AI agreement (§3.3)


def test_chairs_face_the_table():
    table = _rect_strokes(2.0, 2.0, 3.6, 2.9)
    chairs = _rect_strokes(2.3, 1.4, 2.75, 1.85) + _rect_strokes(2.3, 3.05, 2.75, 3.5)
    pieces, cands, _ = _furn(table + chairs)
    chair_c = [c for c in cands if max(c["footprint"]["size"]) < 0.5]
    fronts = sorted(f["front_deg"] for c in chair_c for f in c["front_candidates"] if f["rule"].startswith("chair"))
    assert fronts == [90.0, 270.0]


# --------------------------------------------------------------------------
# Site decor
# --------------------------------------------------------------------------

def test_site_decor_plants_other_and_lines():
    plant = [R.stroke([(8.0, 1.0), (8.4, 1.0), (8.4, 1.4), (8.0, 1.4)], closed=True, fill=(0.07, 0.30, 0.0))
             for _ in range(3)]
    step = _rect_strokes(6.3, 1.0, 6.8, 2.5)
    boundary = [R.stroke([(10.0, -2.0), (10.0, 8.0)])]
    pieces, cands, decor = _furn(plant + step + boundary)
    kinds = sorted(d["kind"] for d in decor)
    assert kinds == ["other", "plant"]
    assert all(d["id"].startswith("sd_L0_") for d in decor)
    assert not pieces and not cands


# --------------------------------------------------------------------------
# real01
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def chain():
    return R.g2_chain()


def _ft(p):
    return R.to_ref(p)


def test_real01_no_cluster_over_4_5_m(chain):
    items = _all(chain["pieces"], chain["candidates"])
    assert all(max(p.size) <= 4.5 for p in items)
    assert not [p for p in items if p.details.get("oversize")]
    outline_poly = "curve:9590"                                      # the 94.7 m wall outline polyline
    assert all(outline_poly not in p.evidence.get("entity", "") for p in items)


def test_real01_every_reference_piece_is_found(chain):
    ref = R.reference()
    items = _all(chain["pieces"], chain["candidates"])
    assert len(items) == ref["counts"]["furniture_total"]            # 20
    used = set()
    for r in ref["furniture"]:
        if r.get("not_a_piece"):
            continue
        tol = r["tol"]
        best = None
        for k, p in enumerate(items):
            if k in used:
                continue
            d = math.dist(_ft(p.center), r["centre_ft"])
            want = sorted(r["size_wd_ft"])
            got = sorted(v / FT for v in p.size)
            if d <= tol["centre"] and all(abs(a - b) <= tol["size"] for a, b in zip(got, want)):
                if best is None or d < best[0]:
                    best = (d, k)
        assert best is not None, r["id"]
        used.add(best[1])
        p = items[best[1]]
        if r.get("type_method_expected") == "rule":
            assert p.type == r["type"] and p.type_method == "rule", r["id"]
        else:
            # AI-typed pieces wait for the answers (§2.10: type_accept, or unknown + unverified + candidates).
            assert p.type == "unknown" and p.status == "unverified" and p.type_method == "none", r["id"]


def test_real01_stair(chain):
    stair = [p for p in chain["pieces"] if p.type == "stair"][0]
    assert stair.status == "verified"                                  # in the unlabelled hall face
    st = stair.details["stair"]
    assert len(st["flights"]) == 2
    for f in st["flights"]:
        assert f["width"] == pytest.approx(0.762, abs=0.01)
        assert f["lines"] == 8
        assert f["spacing"] == pytest.approx(0.253, abs=0.005)
    xs = sorted(round(_ft(f["start"])[0], 1) for f in st["flights"])
    assert xs == pytest.approx([12.5, 15.0], abs=0.1)                  # x 11.25-13.75 and 13.75-16.26 ft
    assert st["landing"]["depth"] == pytest.approx(0.66, abs=0.02)
    assert st["direction_assumed"] is True and st["turn_assumed"] is True


def test_real01_kitchen_counter_legs(chain):
    legs = sorted((p for p in chain["pieces"] if p.type == "kitchen_counter"), key=lambda p: -p.size[0])
    assert len(legs) == 2
    assert legs[0].size == pytest.approx((2.568, 0.612), abs=0.01)
    assert legs[1].size == pytest.approx((0.991, 0.609), abs=0.01)
    assert [p.status for p in legs] == ["verified", "verified"]       # in the kitchen
    assert [p.front_deg for p in legs] == [270.0, 180.0]


def test_real01_composites_are_split(chain):
    """The two bed groups and the dining group come out as separate pieces (no unknown composite left)."""
    assert not [p for p in chain["pieces"] if p.details.get("composite")]
    cands = chain["candidates"]
    chairs = [c for c in cands if max(c["footprint"]["size"]) < 0.5 and c["room_hint"] == "Dining"]
    assert len(chairs) == 6
    beds = [c for c in cands if "bed_double" in c["fits"]]
    assert len(beds) == 2
    assert all(c["key"].startswith("sym_L0_") for c in cands)
    assert len({c["key"] for c in cands}) == len(cands)
    bed_fronts = [f["front_deg"] for c in beds for f in c["front_candidates"]]
    assert sorted(set(bed_fronts)) == [90.0, 270.0]                    # heads against the north and south walls


def test_real01_site_decor(chain):
    decor = chain["decor"]
    plants = [d for d in decor if d["kind"] == "plant"]
    assert len(plants) == R.reference()["counts"]["site_plants"]       # 9
    want = R.reference()["site"]["decor"]["plants"]["centres_ft"]
    for c in want:
        assert min(math.dist(_ft(d["center"]), c) for d in plants) <= 0.49
    other = [d for d in decor if d["kind"] == "other"]
    step = R.reference()["site"]["decor"]["entrance_step"]
    assert len(other) == 1
    assert math.dist(_ft(other[0]["center"]), step["centre_ft"]) <= step["tol"]["centre"]
    assert sorted(v / FT for v in other[0]["size"]) == pytest.approx(sorted(step["size_xy_ft"]), abs=0.49)


def test_apply_room_checks_marks_a_stair_in_a_bedroom_unverified():
    pieces, _, _ = _furn(_stair_strokes())
    faces = [{"polygon": sbox(0.1, 0.1, 5.9, 4.9), "room_type": "bedroom", "label": "Bed Room"}]
    notes = []
    SY.apply_room_checks(pieces, [], faces, notes)
    assert [p.status for p in pieces if p.type == "stair"] == ["unverified"]
    assert any("stair drawn in the labelled room" in n for n in notes)


def test_id_ranges():
    assert SY.id_ranges(["line:3", "line:4", "line:5", "curve:9", "line:7#2"]) == "curve:9,line:3-5,line:7"
