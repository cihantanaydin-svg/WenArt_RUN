"""Walls of the generic plan core (docs/milestone7.md §2.4, §11 G2).

Synthetic pages (in metres) check each rule: hatch groups (spacing, angle, colour), the dark-fill chroma rule,
outline walls, the mask decomposition of L, T and + junctions (IoU >= 0.97), face snapping and the angled-wall
warning. real01 checks the result on a real CAD PDF: the two thickness classes 0.150 / 0.230 m, the house and plot
walls of the reference, and that the coffee table's solid frame (a 0/90 deg line fill) is not a wall.
"""
import math

import numpy as np
import pytest
from shapely.geometry import LineString, box as sbox
from shapely.ops import unary_union

import _real01_page as R
from wenart.ingest.generic import walls as W
from wenart.ingest.generic.model import MaskLayer


def _walls_of(strokes, outline=None):
    page = R.synthetic_page(strokes)
    prims = W.wall_primitives(page, 1.0)
    mask = W.wall_mask(page, prims, 1.0)
    ids = {i for p in prims for i in p.stroke_ids}
    outline = [s for s in strokes if s.id not in ids] if outline is None else outline
    walls, info = W.walls_from_mask(mask, outline, "test.pdf", 1)
    return prims, mask, walls, info


def _union(walls):
    return unary_union([LineString([w.start, w.end]).buffer(w.thickness / 2, cap_style=2, join_style=2)
                        for w in walls])


# --------------------------------------------------------------------------
# Primitives
# --------------------------------------------------------------------------

def test_hatch_group_needs_a_regular_comb_of_one_colour_and_direction():
    dense = R.hatch(R.rect(0, 0, 3, 0.2), step=0.003, angle_deg=45)            # a wall: 3 mm comb
    sparse = R.hatch(R.rect(0, 1, 3, 1.2), step=0.06, angle_deg=45)            # 60 mm apart: not a hatch
    red = R.hatch(R.rect(0, 2, 3, 2.2), step=0.003, angle_deg=45, colour=(1.0, 0.0, 0.0))
    page = R.synthetic_page(dense + sparse + red)
    prims = W.wall_primitives(page, 1.0)
    hatches = [p for p in prims if p.kind == "hatch"]
    assert len(hatches) == 2                                  # black and red are separate groups
    by_size = sorted(hatches, key=lambda p: len(p.lines))
    assert all(abs(p.direction_deg - 45.0) <= 1.0 for p in hatches)
    assert all(p.step_m <= 0.025 for p in hatches)
    assert {s.id for s in dense} <= set(by_size[0].stroke_ids) | set(by_size[1].stroke_ids)
    assert not ({s.id for s in sparse} & {i for p in hatches for i in p.stroke_ids})
    assert all(p.method == "vector" and p.confidence == 0.95 and p.entity.startswith("hatch:") for p in hatches)


def test_hatch_direction_is_one_degree_and_long_lines_are_not_hatch():
    lines45 = R.hatch(R.rect(0, 0, 3, 0.2), step=0.003, angle_deg=45)
    lines48 = R.hatch(R.rect(0, 1, 3, 1.2), step=0.003, angle_deg=48)
    long = R.hatch(R.rect(0, 2, 3, 3.0), step=0.003, angle_deg=0)             # 3 m lines: longer than 0.8 m
    prims = W.wall_primitives(R.synthetic_page(lines45 + lines48 + long), 1.0)
    dirs = sorted(round(p.direction_deg) for p in prims if p.kind == "hatch")
    assert dirs == [45, 48]


def test_dark_fill_chroma_rule():
    black = R.stroke(R.rect(0, 0, 3, 0.2), closed=True, fill=(0.1, 0.1, 0.1))
    green = R.stroke(R.rect(0, 1, 3, 1.2), closed=True, fill=(0.0745, 0.298, 0.0))   # real01's plant green
    red = R.stroke(R.rect(0, 2, 3, 2.2), closed=True, fill=(1.0, 0.0, 0.0))
    grey = R.stroke(R.rect(0, 3, 3, 3.2), closed=True, fill=(0.6, 0.6, 0.6))         # too light
    prims = W.wall_primitives(R.synthetic_page([black, green, red, grey]), 1.0)
    fills = [p for p in prims if p.kind == "fill"]
    assert [p.entity for p in fills] == [black.id]
    assert fills[0].confidence == 0.9


def test_outline_wall_is_an_empty_thin_closed_polygon():
    wall = R.stroke(R.rect(0, 0, 3, 0.15), closed=True)
    table = R.stroke(R.rect(0, 1, 1.0, 1.5), closed=True)                # too wide (0.5 m is fine) ...
    marker = R.stroke([(0.2, 1.1), (0.8, 1.1)])                         # ... but it holds a marker line
    thin = R.stroke(R.rect(0, 2, 3, 2.03), closed=True)                  # 30 mm: a door leaf, not a wall
    short = R.stroke(R.rect(0, 3, 0.3, 3.15), closed=True)               # 0.3 m long
    prims = W.wall_primitives(R.synthetic_page([wall, table, marker, thin, short]), 1.0)
    outlines = [p for p in prims if p.kind == "outline"]
    assert [p.entity for p in outlines] == [wall.id]
    assert outlines[0].confidence == 0.8


def test_dxf_hatch_on_a_wall_layer_is_filled_even_odd():
    outer = R.stroke(R.rect(0, 0, 4, 3), closed=True, fill=(0.0, 0.0, 0.0))
    hole = R.stroke(R.rect(0.2, 0.2, 3.8, 2.8), closed=True, fill=(0.0, 0.0, 0.0))
    outer.id, hole.id = "ent:1A#0", "ent:1A#1"
    outer.layer = hole.layer = "A-WALL"
    page = R.synthetic_page([outer, hole], wall_hint_layers=("A-WALL",))
    prims = W.wall_primitives(page, 1.0)
    assert [p.kind for p in prims] == ["dxf_hatch"] and prims[0].confidence == 0.95
    mask = W.wall_mask(page, prims, 1.0)
    area = mask.mask.sum() * mask.px ** 2
    assert area == pytest.approx(4 * 3 - 3.6 * 2.6, rel=0.05)          # the room island stays empty


def test_raster_mask_primitive_keeps_its_pixels():
    m = np.zeros((100, 300), bool)
    m[40:60, 10:290] = True                                              # 2.8 m x 0.2 m at 1 cm/px
    page = R.synthetic_page([])
    page.wall_mask = MaskLayer(mask=m, origin=(0.0, 100.0), px=1.0)     # page units: cm, top-left corner
    prims = W.wall_primitives(page, 0.01)
    assert prims[0].kind == "raster" and prims[0].method == "raster" and prims[0].confidence == 0.85
    mask = W.wall_mask(page, prims, 0.01)
    walls, info = W.walls_from_mask(mask, [], "scan.png", 1, units_to_m=0.01)
    assert len(walls) == 1
    w = walls[0]
    assert w.evidence["method"] == "raster"
    assert math.dist(w.start, w.end) == pytest.approx(2.8, abs=0.03)
    assert w.thickness == pytest.approx(0.2, abs=0.015)
    assert w.box == pytest.approx([10, 40, 290, 60], abs=2)             # page units (pixels)


# --------------------------------------------------------------------------
# Mask, decomposition, faces
# --------------------------------------------------------------------------

SHAPES = {
    "L": [sbox(0, 0, 5, 0.2), sbox(0, 0, 0.2, 4)],
    "T": [sbox(0, 3.8, 6, 4.0), sbox(2.9, 0, 3.1, 4.0)],
    "+": [sbox(0, 1.9, 6, 2.1), sbox(2.9, 0, 3.1, 4.0)],
}


@pytest.mark.parametrize("name", sorted(SHAPES))
def test_decomposition_of_l_t_plus_reproduces_the_mask(name):
    shape = unary_union(SHAPES[name])
    strokes = R.hatch(shape, step=0.003) + R.edges(list(shape.exterior.coords)[:-1])
    prims, mask, walls, info = _walls_of(strokes)
    assert info["iou"] >= 0.97, info
    assert not info["warnings"]
    u = _union(walls)
    assert u.symmetric_difference(shape).area <= 0.03 * shape.area
    assert all(w.thickness == pytest.approx(0.2, abs=0.005) for w in walls)
    assert all(abs(w.start[0] - w.end[0]) < 1e-6 or abs(w.start[1] - w.end[1]) < 1e-6 for w in walls)


def test_l_junction_square_goes_to_the_longer_wall():
    shape = unary_union(SHAPES["L"])
    _, _, walls, _ = _walls_of(R.hatch(shape, step=0.003) + R.edges(list(shape.exterior.coords)[:-1]))
    longest = max(walls, key=lambda w: math.dist(w.start, w.end))
    assert math.dist(longest.start, longest.end) == pytest.approx(5.0, abs=0.01)   # the 5 m wall keeps the corner
    assert len(walls) == 2


def test_faces_snap_to_outline_strokes_and_round_to_5_mm():
    # A 0.1524 m (6 in) wall: the hatch mask is jagged at 10 mm/px; the outline strokes give the faces.
    poly = R.rect(0, 0, 4, 0.1524)
    hatch = R.hatch(poly, step=0.003)
    prims, mask, walls, info = _walls_of(hatch + R.edges(poly))
    assert len(walls) == 1
    w = walls[0]
    assert w.thickness == pytest.approx(0.150, abs=1e-9)                   # 152.4 mm rounded to 5 mm
    assert w.start[1] == pytest.approx(0.0762, abs=0.003)
    assert math.dist(w.start, w.end) == pytest.approx(4.0, abs=0.003)     # end faces snapped too
    assert info["faces_snapped"] == 4
    # Without outline strokes the eroded mask decides (within a pixel or so).
    _, _, walls2, info2 = _walls_of(hatch, outline=[])
    assert info2["faces_snapped"] == 0
    assert walls2[0].thickness == pytest.approx(0.15, abs=0.02)


def test_small_and_non_elongated_components_are_dropped():
    wall = R.stroke(R.rect(0, 0, 4, 0.2), closed=True, fill=(0, 0, 0))
    speck = R.stroke(R.rect(2, 2, 2.1, 2.1), closed=True, fill=(0, 0, 0))     # 0.01 m²
    block = R.stroke(R.rect(5, 5, 5.5, 5.5), closed=True, fill=(0, 0, 0))     # 0.25 m², not elongated
    pillar = R.stroke(R.rect(3.8, 0.2, 4.0, 0.5), closed=True, fill=(0, 0, 0))  # touches the wall: kept
    _, mask, walls, info = _walls_of([wall, speck, block, pillar])
    centres = [((w.start[0] + w.end[0]) / 2, (w.start[1] + w.end[1]) / 2) for w in walls]
    assert not any(c[0] > 4.5 for c in centres)                               # the block is gone
    assert any("without an elongated" in n for n in info["notes"])
    assert any("< 0.02 m²" in n for n in mask.notes)
    assert block.id in info["dropped_strokes"]                                # given back to §2.8
    assert _union(walls).contains(sbox(3.85, 0.25, 3.95, 0.45))              # the pillar stays


def test_angled_wall_gives_a_warning():
    axis = sbox(0, 0, 6, 0.2)
    angled = LineString([(1, 1), (4, 3)]).buffer(0.1, cap_style=2)          # about 34 deg
    strokes = [R.stroke(list(axis.exterior.coords)[:-1], closed=True, fill=(0, 0, 0)),
               R.stroke(list(angled.exterior.coords)[:-1], closed=True, fill=(0, 0, 0))]
    _, _, walls, info = _walls_of(strokes)
    assert any("angled wall not modelled" in w for w in info["warnings"])


def test_rotated_plan_is_decomposed_in_its_own_orientation():
    t = math.radians(20.0)

    def rot(p):
        return (p[0] * math.cos(t) - p[1] * math.sin(t), p[0] * math.sin(t) + p[1] * math.cos(t))

    pieces = [R.rect(0, 0, 5, 0.2), R.rect(0, 0, 0.2, 4)]
    strokes = [R.stroke([rot(p) for p in poly], closed=True, fill=(0, 0, 0)) for poly in pieces]
    for poly in pieces:
        strokes += R.edges([rot(p) for p in poly])
    _, _, walls, info = _walls_of(strokes)
    assert info["dominant_deg"] == pytest.approx(20.0, abs=0.5)
    assert len(walls) == 2
    longest = max(walls, key=lambda w: math.dist(w.start, w.end))
    ang = math.degrees(math.atan2(longest.end[1] - longest.start[1], longest.end[0] - longest.start[0])) % 180
    assert ang == pytest.approx(20.0, abs=0.5)
    assert math.dist(longest.start, longest.end) == pytest.approx(5.0, abs=0.03)
    assert all(w.thickness == pytest.approx(0.2, abs=0.005) for w in walls)


def test_thickness_classes_cluster_within_15_mm():
    walls = [R.wall((0, 0), (4, 0), 0.150), R.wall((0, 1), (4, 1), 0.155), R.wall((0, 2), (2, 2), 0.230),
             R.wall((0, 3), (2, 3), 0.225)]
    classes = W.thickness_classes(walls)
    assert len(classes) == 2
    assert sorted(c["thickness"] for c in classes) == pytest.approx([0.1525, 0.2275], abs=0.001)


# --------------------------------------------------------------------------
# real01
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def chain():
    return R.g2_chain()


def test_real01_hatch_is_the_wall_material(chain):
    hatches = [p for p in chain["prims"] if p.kind == "hatch"]
    main = [p for p in hatches if abs(p.direction_deg - 135.0) <= 1.0]
    assert sum(len(p.lines) for p in main) >= 21000                          # 21,316 hatch lines
    assert all(p.step_m <= 0.025 for p in main)
    assert sorted(p.step_m for p in main)[len(main) // 2] <= 0.0035              # the 3 mm comb
    assert not [p for p in chain["prims"] if p.kind == "fill"]                 # the green plants are no walls
    info = chain["wall_info"]
    assert info["iou"] >= 0.97
    assert info["dominant_deg"] == pytest.approx(0.0, abs=0.1)


def test_real01_thickness_classes(chain):
    classes = chain["wall_info"]["thickness_classes"]
    assert len(classes) == 2
    thick = sorted(c["thickness"] for c in classes)
    assert thick[0] == pytest.approx(0.150, abs=0.005)
    assert thick[1] == pytest.approx(0.230, abs=0.005)
    for w in chain["walls_raw"]:
        assert min(abs(w.thickness - 0.150), abs(w.thickness - 0.230)) <= 0.0051, w


def test_real01_wall_rectangles_match_the_reference_faces(chain):
    """Every reference wall rectangle (windows and run gaps included, so after the runs are merged) is covered by
    the wall rectangles with faces within 0.15 ft."""
    ref = R.reference()["walls"]
    u = _union(chain["walls"])
    tol = 0.15 * 0.3048
    for group in ref.values():
        if not isinstance(group, list):
            continue
        for w in group:
            box = sbox(*R.ref_box(w["rect"]))
            assert u.intersection(box.buffer(-tol, join_style=2)).area >= 0.99 * box.buffer(-tol, join_style=2).area, w
    # The plot wall: four rectangles of 6 in around the house.
    for seg in R.reference()["site"]["plot_wall"]["segments"]:
        box = sbox(*R.ref_box(seg["rect"]))
        assert u.intersection(box.buffer(-tol, join_style=2)).area >= 0.99 * box.buffer(-tol, join_style=2).area


def test_real01_coffee_table_frame_is_not_a_wall(chain):
    coffee = sbox(*R.ref_box([19.580, 6.195, 23.276, 9.882]))
    round_piece = sbox(*R.ref_box([25.553, 2.567, 26.972, 3.985]))
    u = _union(chain["walls_raw"])
    assert u.intersection(coffee).area == 0
    assert u.intersection(round_piece).area == 0
    assert any("main-style" in n for n in chain["wall_info"]["notes"])
    # Their line fills go back to the furniture strokes.
    assert chain["wall_info"]["dropped_strokes"]
