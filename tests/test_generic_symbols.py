"""Furniture clusters, composites, rules and site decor of the generic plan core (docs/milestone7.md §2.8, §11 G2).

Synthetic rooms (metres) check the segment-wise outline removal, the containment exception (a sink in a counter
stays its own piece; a bed's inner outline and pillows do not), the composite split (table and chairs, bed and
nightstands; sofa cushions stay one sofa), the unsplittable composite, the stair rule (dedupe, divider split,
flights), the kitchen counter rule (chaining, wall faces incl. openings), the front candidates, block names and the
site decor. real01 checks every reference piece: 2 beds, 4 nightstands, 1 table, 6 chairs, 2 sofas, the coffee table,
the round piece, the 2 counter legs and the stair, no cluster over 4.5 m, and 9 plants plus the entrance step.

Milestone 10 (real02): the Turkish and English block-name words of the new types (whole words for short ones, M7 words
first, KOLTUK resolved by size), L outlines as corner-sofa candidates (chaise side, depths, the open corner as the
front), one named piece per block instance (a WC's flush plate joins it, a footstool or nightstands are asked),
stairs drawn with nosing strips and no divider line, a room label over a piece that does not cut its outline, and an
armchair with open arm lines that keeps its own piece inside a large cluster's box.
"""
import math

import pytest
from shapely.geometry import box as sbox

import _real01_page as R
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke
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


def test_a_label_over_a_piece_does_not_cut_its_outline():
    # Milestone 10 (real02): BANYO written over the front of a WC bowl. One closed polyline, its pointed top under
    # the text box: a vector stroke is a glyph only when all of it lies in the box, so the outline stays whole; a
    # short stroke inside the box is still a glyph.
    bowl = R.stroke([(2.0, 1.0), (2.5, 1.0), (2.5, 1.5), (2.25, 1.75), (2.0, 1.5)], closed=True)
    glyph = R.stroke([(2.1, 1.55), (2.15, 1.6)])
    text = type("T", (), {"box": (1.95, 1.45, 2.55, 1.8)})()
    notes = []
    pieces, cands, _ = _furn([bowl, glyph], texts=[text], notes=notes)
    sizes = [tuple(round(v, 2) for v in sorted(p.size)) for p in _all(pieces, cands)]
    assert sizes == [(0.5, 0.75)]
    assert "1 glyph strokes inside text boxes ignored" in notes


def test_an_armchair_with_open_arm_lines_keeps_its_own_piece_in_a_large_cluster_box():
    # Milestone 10 (real02, the Açık mutfak Salon): an armchair drawn with loose lines, its arms open three-line
    # boxes ending on the body's sides, stands inside the box of a 5.1 m TV unit + column cluster. Its body alone
    # covers 79.95 % of its box (under the 80 % own-outline share); noded at the T-junctions it closes, so it stays
    # its own piece (the mirrored copy, 0.01 % over the share, always did).
    tv = _rect_strokes(7.0, 1.9, 7.38, 7.0)
    column = _rect_strokes(4.62, 7.04, 5.02, 7.44)
    shelf = [R.stroke([(5.02, 7.04), (7.19, 7.04)]), R.stroke([(7.19, 7.04), (7.19, 7.0)])]
    x0, x1, xa, xb, y0, y1 = 5.585, 6.239, 5.503, 6.321, 2.205, 2.996
    body = _rect_strokes(x0, y0, x1, y1) + [R.stroke([(x0, 2.314), (x1, 2.314)]), R.stroke([(x0, 2.477), (x1, 2.477)])]
    arms = [R.stroke([(xa, 2.232), (xa, 2.941)]), R.stroke([(xa, 2.232), (x0, 2.232)]), R.stroke([(xa, 2.941), (x0, 2.941)]),
            R.stroke([(xb, 2.232), (xb, 2.941)]), R.stroke([(x1, 2.232), (xb, 2.232)]), R.stroke([(x1, 2.941), (xb, 2.941)])]
    pieces, cands, _ = _furn(tv + column + shelf + body + arms, walls=_room(0.0, 0.0, 9.0, 9.0))
    sizes = [tuple(round(v, 2) for v in sorted(p.size)) for p in _all(pieces, cands)]
    assert sorted(sizes) == [(0.79, 0.82), (2.76, 5.54)]             # the TV unit cluster does not take it


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


def test_single_lines_are_line_details_not_zero_depth_furniture():
    """review2 ingest-4: a lone straight stroke (one side >= 0.2 m, the other ~0) fits no type; it is a drawn line
    detail (counted and reported), never an 'unknown' piece of depth 0 that Blender would build as a sliver."""
    lone = R.stroke([(1.0, 2.5), (2.0, 2.5)])                                 # 1.0 x 0.0 m
    slanted = R.stroke([(3.0, 1.0), (3.8, 1.6)])                               # 1.0 m at 37 deg
    table = _rect_strokes(2.5, 3.0, 3.7, 3.8)
    notes = []
    pieces, cands, _ = _furn([lone, slanted] + table, notes=notes)
    found = _all(pieces, cands)
    assert len(found) == 1 and min(found[0].size) == pytest.approx(0.8)      # only the table
    assert all(min(p.size) >= SY.LINE_DETAIL_M for p in found)
    line_note = [n for n in notes if "line details" in n]
    assert len(line_note) == 1 and line_note[0].startswith("2 line details")
    assert line_note[0].endswith(SY.id_ranges([lone.id, slanted.id]))           # the strokes are named


def test_isolated_treads_between_walls_become_a_stair():
    """review2 ingest-4: treads drawn from wall face to wall face (no stringer, no walk line) are separate clusters;
    they are grouped into one stair candidate that the stair rule types, not 8 zero-depth unknown pieces."""
    walls = _room(0.0, 0.0, 1.7, 4.0)                                          # faces x 0.1-1.6, y 0.1-3.9
    treads = [R.stroke([(0.1, 1.0 + 0.25 * k), (1.6, 1.0 + 0.25 * k)]) for k in range(8)]
    notes = []
    pieces, cands, _ = _furn(treads, walls=walls, notes=notes)
    assert not cands
    assert [(p.type, p.type_method, p.status) for p in pieces] == [("stair", "rule", "verified")]
    st = pieces[0].details["stair"]
    assert len(st["flights"]) == 1 and st["flights"][0]["lines"] == 8
    assert st["flights"][0]["width"] == pytest.approx(1.5) and st["flights"][0]["spacing"] == pytest.approx(0.25)
    assert sorted(pieces[0].size) == pytest.approx([1.5, 1.75])
    assert any("8 isolated, evenly spaced tread lines" in n for n in notes)
    # Lines on both sides of a wall are no flight: 3 + 3 evenly spaced lines with a wall (faces y 1.575-1.675)
    # between them stay line details.
    walls2 = _room(0.0, 0.0, 1.7, 4.0) + [R.wall((0.0, 1.625), (1.7, 1.625), 0.1)]
    split = [R.stroke([(0.1, y), (1.6, y)]) for y in (1.0, 1.25, 1.5, 1.75, 2.0, 2.25)]
    notes2 = []
    pieces2, cands2, _ = _furn(split, walls=walls2, notes=notes2)
    assert not [p for p in pieces2 if p.type == "stair"] and not cands2 and not pieces2
    assert any("line details" in n for n in notes2)


def test_rotated_plan_containment_merge_uses_the_aligned_frame():
    """review2 ingest-5: on a plan drawn at 30 deg the page-axis box of the stair covers a chair across the wall;
    the containment merge works in the plan's frame, so the stair keeps its own strokes and size."""
    a = math.radians(30.0)

    def rot(p):
        return (p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a))

    def rotated(strokes):
        return [R.stroke([rot(p) for p in s.pts]) for s in strokes]

    def scene(turn):
        f = rot if turn else (lambda p: p)
        walls = [R.wall(f(s), f(e), t) for s, e, t in (((0, 0.1), (6, 0.1), 0.2), ((5.9, 0), (5.9, 5), 0.2),
                                                      ((6, 4.9), (0, 4.9), 0.2), ((0.1, 5), (0.1, 0), 0.2),
                                                      ((2.1, 0.2), (2.1, 4.8), 0.2))]
        stair = _stair_strokes(x0=0.4, y0=0.5, width=1.5)                       # x 0.4-1.9, y 0.5-2.91
        stair += [R.stroke([(0.4, 0.5), (0.4, 2.91)]), R.stroke([(1.9, 0.5), (1.9, 2.91)])]   # side lines
        # An open chair outline (three sides) in the next room, 0.1 m from the wall face: turned by 30 deg, 98 % of
        # its page-axis box lies inside the stair's page-axis box.
        chair = [R.stroke([(2.3, 1.95), (2.3, 2.4)]), R.stroke([(2.3, 2.4), (2.75, 2.4)]),
                 R.stroke([(2.75, 2.4), (2.75, 1.95)])]
        strokes = rotated(stair + chair) if turn else stair + chair
        return _furn(strokes, walls=walls)

    for turn in (False, True):
        pieces, cands, _ = scene(turn)
        stairs = [p for p in pieces if p.type == "stair"]
        assert len(stairs) == 1, turn
        assert sorted(stairs[0].size) == pytest.approx([1.5, 1.75 + 0.66], abs=1e-3), turn
        # The chair is its own candidate (merged into the stair, the stair would grow and the chair vanish).
        assert len(cands) == 1 and sorted(cands[0]["item"].size) == pytest.approx([0.45, 0.45], abs=1e-3), turn


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


def _insert(handle, chain, rect, start=0):
    """The four lines of a rectangle drawn by a DXF INSERT as dxf_generic ids them (``INSERT:<h>/<k>``)."""
    x0, y0, x1, y1 = rect
    segs = (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0)))
    return [Stroke(id=f"{handle}/{start + k}", kind="line", pts=[tuple(map(float, p)) for p in seg], block=chain)
            for k, seg in enumerate(segs)]


def test_dxf_clusters_split_by_insert_instance():
    """One piece per INSERT of a furniture-named block (G3's synthetic-06 finding): a WC's tank and bowl stay one
    toilet although they are two closed contours; DINING-6 gives its table and each nested CHAIR; a PILLOW block
    nested in a BED block stays part of the bed."""
    tank = _insert("INSERT:A1", "WC", (0.6, 0.5, 1.05, 0.72))
    bowl_pts = [(0.825 + 0.2 * math.cos(2 * math.pi * k / 32), 0.96 + 0.24 * math.sin(2 * math.pi * k / 32))
                for k in range(32)]
    bowl = [Stroke(id="INSERT:A1/4", kind="curve", pts=bowl_pts, closed=True, block="WC")]
    table = _insert("INSERT:B2", "DINING-6", (2.5, 2.0, 4.1, 2.9))
    chairs = (_insert("INSERT:B2/4", "DINING-6/CHAIR", (2.8, 1.5, 3.25, 1.99))
              + _insert("INSERT:B2/5", "DINING-6/CHAIR", (3.4, 2.91, 3.85, 3.4)))
    bed = _insert("INSERT:C3", "BED-DOUBLE", (0.6, 2.0, 2.2, 4.0))
    pillows = (_insert("INSERT:C3/4", "BED-DOUBLE/PILLOW", (0.7, 3.5, 1.3, 3.9))
               + _insert("INSERT:C3/5", "BED-DOUBLE/PILLOW", (1.5, 3.5, 2.1, 3.9)))
    pieces, cands, _ = _furn(tank + bowl + table + chairs + bed + pillows)
    assert not cands
    got = sorted((p.type, p.type_method, p.status) for p in pieces)
    assert got == [("bed_double", "block_name", "verified"), ("chair", "block_name", "verified"),
                   ("chair", "block_name", "verified"), ("table_dining", "block_name", "verified"),
                   ("toilet", "block_name", "verified")]
    toilet = [p for p in pieces if p.type == "toilet"][0]
    assert sorted(toilet.size) == [pytest.approx(0.45), pytest.approx(0.7)]
    assert toilet.evidence["entity"] == "INSERT:A1/0,INSERT:A1/1,INSERT:A1/2,INSERT:A1/3,INSERT:A1/4"
    # A block whose chain names no furniture is split by the geometry as before.
    sofa = _insert("INSERT:D4", "LIVING-GROUP", (1.0, 2.6, 3.0, 3.5))
    coffee = _insert("INSERT:D4", "LIVING-GROUP", (1.5, 1.9, 2.5, 2.59), start=4)
    pieces2, cands2, _ = _furn(sofa + coffee)
    assert not pieces2 and len(cands2) == 2


# --------------------------------------------------------------------------
# Milestone 10 (real02): block-name words, L outlines, named instances, nosing-strip stairs
# --------------------------------------------------------------------------

def test_m10_block_name_words():
    assert SY.keyword_type("KÖŞE KOLTUK") == "sofa_corner" and SY.keyword_type("corner-sofa_01") == "sofa_corner"
    assert SY.keyword_type("puf") == "ottoman" and SY.keyword_type("BANK") == "bench"
    assert SY.keyword_type("BANKO") is None                         # a counter, not a bench (whole words only)
    assert SY.keyword_type("BAR TABURESİ") == "bar_stool" and SY.keyword_type("ofis koltuğu") == "office_chair"
    assert SY.keyword_type("KONSOL") == "console_table" and SY.keyword_type("beşik") == "crib"
    assert SY.keyword_type("RANZA") == "bunk_bed" and SY.keyword_type("ayakkabı dolabı") == "shoe_cabinet"
    assert SY.keyword_type("eb_banyo_ustdolap") == "wall_cabinet" and SY.keyword_type("VITRIN") == "display_cabinet"
    assert SY.keyword_type("merdiven") is None and SY.keyword_type("derr") is None   # unknown names stay unknown
    assert SY.keyword_type("duşş") == "shower" and SY.keyword_type("KOMİDİN") == "nightstand"   # folded M7 words
    assert SY.block_type(["YATAK_TEK"], (1.2, 2.0), TABLE) == "bed_single"           # the M7 word says more
    assert SY.block_type(["YATAK"], (1.6, 2.0), TABLE) == "bed_double"
    assert SY.block_type(["YATAK"], (0.9, 2.0), TABLE) == "bed_single"
    assert SY.block_type(["masa"], (1.6, 0.9), TABLE) == "table_dining"
    assert SY.block_type(["koltuk"], (0.9, 0.85), TABLE) == "armchair"               # M7: KOLTUK = armchair ...
    assert SY.block_type(["koltuk011"], (2.2, 0.9), TABLE) == "sofa"                 # ... or a sofa by its size
    assert SY.block_type(["koltuk"], (2.6, 1.6), TABLE, "L") == "sofa_corner"
    assert "sofa_corner" not in SY.fitting_types(TABLE, (2.6, 1.6))
    assert "sofa_corner" in SY.fitting_types(TABLE, (2.6, 1.6), "L")


def test_a_tv_console_block_is_a_tv_unit():
    # Review #15: KONSOL (console table) must not shadow the M7 TV word in a TV console's name.
    for name in ("TV_KONSOL", "TV KONSOLU", "tv-konsol", "TV_CONSOLE", "TVKONSOL"):
        assert SY.keyword_type(name) == "tv_unit", name
    assert SY.block_type(["TV KONSOLU"], (1.8, 0.45), TABLE) == "tv_unit"
    assert SY.keyword_type("KONSOL") == "console_table"


def _l_sofa(notch="bottom-left"):
    """An L outline in the box x 1.0-3.6, y 2.4-4.0: the main seat 0.9 m deep along y 4.0, the chaise 0.9 m wide."""
    if notch == "bottom-left":
        pts = [(1.0, 3.1), (2.7, 3.1), (2.7, 2.4), (3.6, 2.4), (3.6, 4.0), (1.0, 4.0)]
    else:
        pts = [(1.0, 2.4), (1.9, 2.4), (1.9, 3.1), (3.6, 3.1), (3.6, 4.0), (1.0, 4.0)]
    cushions = [R.stroke(R.rect(1.1 + 0.8 * k, 3.2, 1.8 + 0.8 * k, 3.9), closed=True) for k in range(2)]
    return [R.stroke(pts, closed=True)] + cushions


def test_an_l_outline_is_a_corner_sofa_candidate():
    pieces, cands, _ = _furn(_l_sofa())
    assert not pieces and len(cands) == 1
    c = cands[0]
    assert c["footprint"]["shape"] == "L" and "sofa_corner" in c["fits"]
    assert sorted(c["footprint"]["size"]) == pytest.approx([1.6, 2.6])
    assert c["front_candidates"] == [{"front_deg": 270.0, "rule": "L outline: the open inner corner is the front"}]
    d = c["item"].details
    assert "shape" not in d                                          # shape L only once the type is sofa_corner
    assert d["l_outline"]["chaise_side"] == "right"                  # the contract example: chaise on local +X
    lo = d["l_outline"]
    assert (lo["chaise_depth"], lo["seat_depth"], lo["chaise_width"]) == pytest.approx((1.6, 0.9, 0.9))
    assert c["item"].evidence["note"].startswith("L outline 2.60 x 1.60 m: main seat 0.90 m deep")
    _, cands2, _ = _furn(_l_sofa("bottom-right"))
    assert cands2[0]["item"].details["l_outline"]["chaise_side"] == "left"       # the mirrored twin


def test_a_corner_sofa_block_takes_its_l_front():
    sofa = [Stroke(id=f"INSERT:S1/{k}", kind=s.kind, pts=s.pts, closed=s.closed, block="KÖŞE KOLTUK")
            for k, s in enumerate(_l_sofa())]
    pieces, cands, _ = _furn(sofa)
    assert not cands and [p.type for p in pieces] == ["sofa_corner"]
    p = pieces[0]
    assert p.type_method == "block_name" and p.status == "verified" and p.front_deg == 270.0
    assert p.size == pytest.approx((2.6, 1.6)) and p.rotation_deg == 0.0     # front_deg = (270 + rotation) mod 360
    assert p.details["l_outline"]["chaise_side"] == "right"


def test_an_l_shaped_stair_outline_stays_a_stair():
    # Review #11: a quarter-turn stair drawn as a closed L outline with its treads inside (20 mm short of the outline)
    # is read by the stair rule before the L-outline (corner sofa) path.
    def p(x, y):
        return (x + 1.0, y + 1.0)
    outline = R.stroke([p(0, 1.6), p(2, 1.6), p(2, 0), p(3, 0), p(3, 2.6), p(0, 2.6)], closed=True)
    treads = [R.stroke([p(0.28 * k + 0.2, 1.62), p(0.28 * k + 0.2, 2.58)]) for k in range(6)] + \
        [R.stroke([p(2.02, 0.28 * k + 0.2), p(2.98, 0.28 * k + 0.2)]) for k in range(5)]
    pieces, cands, _ = _furn([outline] + treads)
    assert [(x.type, x.type_method) for x in pieces] == [("stair", "rule")] and cands == []


def test_rectangles_and_u_shapes_are_no_l():
    cl = SY.Cluster(SY._segments([R.stroke(R.rect(1, 1, 3.6, 2.0), closed=True)], set()))
    assert SY.l_shape(cl, 0.0) is None
    u = R.stroke([(1, 1), (4, 1), (4, 3), (3.1, 3), (3.1, 1.9), (1.9, 1.9), (1.9, 3), (1, 3)], closed=True)
    assert SY.l_shape(SY.Cluster(SY._segments([u], set())), 0.0) is None


def test_one_named_piece_per_block_instance():
    # A WC: bowl and a thin flush plate 5 cm behind it, split by the 20 mm clustering: one toilet.
    bowl = _insert("INSERT:W1", "klozet", (1.0, 1.0, 1.4, 1.6))
    plate = _insert("INSERT:W1", "klozet", (0.95, 1.65, 1.45, 1.72), start=4)
    # An armchair block that also draws its footstool: the armchair takes the name, the footstool is asked.
    chair = _insert("INSERT:K1", "koltuk", (3.0, 1.0, 3.9, 1.85))
    stool = _insert("INSERT:K1", "koltuk", (3.1, 2.0, 3.7, 2.45), start=4)
    # A bed block drawn with its two nightstands (touching): the bed takes the name, the nightstands are asked.
    bed = _insert("INSERT:Y1", "YATAK", (2.0, 3.0, 3.6, 4.9))
    stands = _insert("INSERT:Y1", "YATAK", (1.5, 4.5, 1.99, 4.9), start=4) + \
        _insert("INSERT:Y1", "YATAK", (3.61, 4.5, 4.1, 4.9), start=8)
    notes = []
    pieces, cands, _ = _furn(bowl + plate + chair + stool + bed + stands, notes=notes)
    got = sorted((p.type, p.type_method, p.status) for p in pieces)
    assert got == [("armchair", "block_name", "verified"), ("bed_double", "block_name", "verified"),
                   ("toilet", "block_name", "verified")]
    assert len(cands) == 3 and all("next to its named piece" in c["item"].evidence["note"] for c in cands)
    assert any("2 drawn parts of one block instance are one piece" in n for n in notes)
    bed_piece = [p for p in pieces if p.type == "bed_double"][0]
    assert sorted(bed_piece.size) == pytest.approx([1.6, 1.9]) and "takes the name" in bed_piece.evidence["note"]


def test_stair_with_nosing_strips_and_no_divider():
    """real02: every tread drawn as two lines 50 mm apart, the two flights side by side without one divider line,
    the treads next to the break line shorter: the loose rule finds both flights (the strict one finds none)."""
    strokes = []
    for side, (y0, y1) in enumerate(((1.0, 1.95), (2.15, 3.1))):
        for k in range(6):
            x = 1.0 + 0.28 * k
            top = y1 - (0.2 if (side, k) == (1, 3) else 0.0)            # a tread cut short by the break line
            strokes += [R.stroke([(x, y0), (x, top)]), R.stroke([(x + 0.05, y0), (x + 0.05, top)])]
    strokes.append(R.stroke(R.rect(0.9, 1.95, 2.7, 2.15), closed=True))  # the handrail band between the flights
    pieces, cands, _ = _furn(strokes)
    stairs = [p for p in pieces if p.type == "stair"]
    assert len(stairs) == 1 and not cands
    st = stairs[0].details["stair"]
    assert len(st["flights"]) == 2 and st["turn"] == "U"
    assert all(f["lines"] == 6 and f["spacing"] == pytest.approx(0.28) for f in st["flights"])


def test_id_ranges_keep_non_numeric_ids_sorted():
    assert SY.id_ranges(["INSERT:FF/3/1", "INSERT:FF/0", "LINE:2F", "INSERT:FF/3/0"]) == \
        "INSERT:FF/0,INSERT:FF/3/0,INSERT:FF/3/1,LINE:2F"


def test_stroke_id_order_does_not_depend_on_the_input_order():
    # DXF ids are not numeric: they sort by the id itself, not by set iteration (real02's counter_run strokes
    # changed order from run to run).
    ids = ["INSERT:2DE26/3", "INSERT:2DE26/12", "INSERT:2DE26/1", "path:12", "path:3"]
    expected = ["INSERT:2DE26/1", "INSERT:2DE26/12", "INSERT:2DE26/3", "path:3", "path:12"]
    assert sorted(ids, key=SY._id_key) == sorted(reversed(ids), key=SY._id_key) == expected


_COUNTER_SCRIPT = """
import _real01_page as R
import test_generic_symbols as T
from shapely.geometry import box as sbox
from wenart.ingest.model import OpeningItem
chain = [R.stroke([(0.8, 3.9), (0.8, 3.3)]), R.stroke([(0.8, 3.3), (3.3, 3.3)]),
         R.stroke([(3.3, 3.3), (3.3, 2.0)]), R.stroke([(3.3, 2.0), (3.9, 2.0)])]
for st, k in zip(chain, (3, 12, 1, 2)):
    st.id = f"INSERT:2DE26/{k}"
window = OpeningItem(kind="window", width=1.2, center=(2.0, 4.0), rotation_deg=0.0, box=[], entity="w", evidence={})
faces = [{"polygon": sbox(0.1, 0.1, 3.9, 3.9), "room_type": "kitchen", "label": "Kitchen"}]
pieces, _, _ = T._furn(chain, walls=T._room(0, 0, 4, 4), openings=[window], faces=faces)
print(sorted([p.entity] + p.details["counter_run"]["strokes"] for p in pieces if p.type == "kitchen_counter"))
"""


def test_counter_run_strokes_do_not_depend_on_the_hash_seed():
    # Lead item (track A1 found it on real02): the counter_run strokes of DXF ids followed Python's string hashing.
    import os
    import subprocess
    import sys
    from pathlib import Path

    tests = Path(__file__).resolve().parent
    env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(tests.parent), str(tests)]))
    outs = set()
    for seed in ("1", "2", "3", "4"):
        run = subprocess.run([sys.executable, "-c", _COUNTER_SCRIPT], cwd=tests.parent, capture_output=True,
                             text=True, env=dict(env, PYTHONHASHSEED=seed), timeout=120)
        assert run.returncode == 0, run.stderr
        outs.add(run.stdout.strip())
    assert len(outs) == 1, outs
    import ast
    rows = ast.literal_eval(outs.pop())
    assert len(rows) == 2 and all(row[1:] == sorted(row[1:]) and row[0] == row[1] for row in rows)  # by id


def test_round_pieces_record_their_shape():
    """§6.4: a side table is round when a circle fits >= 90 % of its outline; a square one is not (its 4 corners
    lie on a circle, its outline does not)."""
    circle = R.arc((2.0, 2.0), 0.22, 0, 360, n=48)
    square = R.stroke(R.rect(4.0, 2.0, 4.45, 2.45), closed=True)
    pieces, cands, _ = _furn([circle, square])
    by_x = sorted((c["item"] for c in cands), key=lambda p: p.center[0])
    assert len(by_x) == 2
    assert by_x[0].details["shape"] == "round"
    assert by_x[0].details["circle_fit"]["share"] >= 0.9
    assert by_x[0].details["circle_fit"]["radius"] == pytest.approx(0.22, abs=0.005)
    assert "shape" not in by_x[1].details and "circle_fit" not in by_x[1].details
    assert all("shape" not in c for c in cands)                     # the question and its hash are unchanged


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
