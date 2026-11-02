"""2 Nov 2026 (user on real10: "There are too many mistakes in the structure", "go ahead with 1, 2 and 3", "Shaft is the
good place to align the floors", "align according to shaft"): the levels of a multi-plan sheet are placed by their
lift shaft (the core's walls on the reference core's), checked by the shared axis grid; the grid alone when a plan has
no lift; the outline fit keeps the sheet's orientation unless another rotation fits clearly better. CPU only."""
from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

from wenart.sheets import register as RG


def test_an_axis_turned_by_a_right_angle():
    assert RG._turn_axis("v", 3.0, 0) == ("v", 3.0) and RG._turn_axis("v", 3.0, 90) == ("h", 3.0)
    assert RG._turn_axis("v", 3.0, 180) == ("v", -3.0) and RG._turn_axis("v", 3.0, 270) == ("h", -3.0)
    assert RG._turn_axis("h", 2.0, 90) == ("v", -2.0) and RG._turn_axis("h", 2.0, 270) == ("v", 2.0)


def _grid(dx=0.0, dy=0.0, turn=0.0):
    axes = {str(k + 1): ("v", 1.0 + 3.5 * k) for k in range(5)}
    axes.update({c: ("h", 2.0 + 4.0 * k) for k, c in enumerate("ABCD")})
    out = {}
    for label, (o, c) in axes.items():
        o2, c2 = RG._turn_axis(o, c, turn)
        out[label] = (o2, c2 + (dx if o2 == "v" else dy))
    return out


def test_the_grid_gives_the_rotation_and_the_shift_by_label():
    """real10: the basements carry the normal floor's grid 28.87 m to the left on the sheet; the outline fit had turned
    them 90 degrees."""
    ref = _grid()
    moved = {k: (o, c - 28.87 if o == "v" else c) for k, (o, c) in ref.items()}
    fit = RG.grid_fit(ref, moved)
    assert fit["rotation_deg"] == 0.0 and fit["shift"] == [28.87, 0.0] and fit["residual_m"] == 0.0
    assert fit["axes"] == {"v": 5, "h": 4}
    # a plan drawn turned by 180 degrees: its axis 1 at the right end
    turned = {}
    for k, (o, c) in ref.items():
        o2, c2 = RG._turn_axis(o, c, 180.0)     # p' = R(180) p: the plan as drawn is the reference turned back
        turned[k] = (o2, c2)
    fit = RG.grid_fit(ref, turned)
    assert fit["rotation_deg"] == 180.0 and fit["residual_m"] == 0.0
    assert RG.grid_fit(ref, {"1": ("v", 0.0), "A": ("h", 0.0)}) is None        # too few shared axes


def _region(texts, ents, box=(0, 0, 100, 100)):
    return SimpleNamespace(texts=texts, ents=ents, geometry_box=box)


def _txt(text, x, y):
    return SimpleNamespace(text=text, point=(x, y))


def _circle(x, y, r):
    return SimpleNamespace(kind="CIRCLE", box=(x - r, y - r, x + r, y + r), strokes=[], rect=None,
                           centre=(x, y), id=f"CIRCLE:{x}:{y}", dim=None)


def test_grid_axes_are_the_labels_in_bubbles_at_both_ends():
    # units of 1 m (mpu 1); bubbles 0.6 m wide at the top and bottom of axes 1 and 2, left and right of A and B
    texts = [_txt("1", 5, 0), _txt("1", 5, 30), _txt("2", 9, 0), _txt("2", 9, 30), _txt("A", 0, 8), _txt("A", 40, 8),
             _txt("B", 0, 12), _txt("B", 40, 12), _txt("A", 20, 3),        # a section marker A: no bubble there
             _txt("3", 13, 15)]                                            # a lone label: no axis
    ents = [_circle(x, y, 0.3) for x, y in ((5, 0), (5, 30), (9, 0), (9, 30), (0, 8), (40, 8), (0, 12), (40, 12),
                                            (13, 15))]
    axes = RG.grid_axes(_region(texts, ents), 1.0)
    assert axes == {"1": ("v", 5.0), "2": ("v", 9.0), "A": ("h", 8.0), "B": ("h", 12.0)}


def test_the_lift_shaft_places_the_level():
    """The core's walls (a shaft box and a stair wall) drawn 30 m to the right and 1.3 m lower land on the
    reference's: the shift, a tiny RMS."""
    ref_segs = [((10, 10), (12, 10)), ((12, 10), (12, 12)), ((12, 12), (10, 12)), ((10, 12), (10, 10)),
                ((13, 9), (13, 14)), ((9, 14), (13, 14))]
    segs = [((a[0] + 30, a[1] - 1.3), (b[0] + 30, b[1] - 1.3)) for a, b in ref_segs]
    fit = RG.core_fit(ref_segs, (11.0, 11.0), segs, (41.4, 9.9), 0.0)   # the labels are 0.4 m apart in the shafts
    assert fit["shift"] == pytest.approx([-30.0, 1.3], abs=0.02) and fit["rms_m"] < 0.02
    assert RG.core_fit([], (0, 0), segs, (0, 0), 0.0) is None
    reg = _region([_txt("ASANSÖR", 11, 11), _txt("salon", 50, 50)], [])
    assert RG.lift_anchor(reg) == (11, 11)
    assert RG.lift_anchor(_region([_txt("asansör mahali", 3, 4)], [])) == (3, 4)     # the machine room above it
    assert RG.lift_anchor(_region([_txt("salon", 1, 1)], [])) is None


# ------------------------------------------------------------------ axis lines are never walls
def test_axis_lines_by_layer_linetype_or_the_bubble_at_their_end():
    """2 Nov 2026 (user: "the red lines should have been dotted lines, those are for coordinates, you can understand
    this from the numbers at the end"): real10's grid, layer aks, linetype ACAD_ISO04W100."""
    from wenart.ingest.generic import axes as AX
    from wenart.ingest.generic.model import Stroke, TextRun
    assert AX.is_axis_style("aks", None) and AX.is_axis_style("S-GRID", None) and AX.is_axis_style("0", "CENTER2")
    assert AX.is_axis_style("0", "ACAD_ISO04W100") and not AX.is_axis_style("AKSESUAR", None)
    assert not AX.is_axis_style("DUVAR", "DASHED") and not AX.is_axis_style("WALL", "Continuous")
    strokes = [
        Stroke(id="a1", kind="line", pts=[(0, 0), (0, 30)], layer="aks"),                       # by layer
        Stroke(id="a2", kind="line", pts=[(5, 0), (5, 30)], layer="0", linetype="ACAD_ISO04W100"),   # by linetype
        Stroke(id="a3", kind="line", pts=[(10, 0.8), (10, 30)], layer="0"),                     # ends in bubble 3
        Stroke(id="w1", kind="line", pts=[(0, 5), (20, 5)], layer="DUVAR"),                     # a wall
        Stroke(id="w2", kind="line", pts=[(11, 0.5), (25, 0.5)], layer="DUVAR"),                # passes by, no aim
        Stroke(id="b3", kind="circle", pts=[(10, 0)], closed=True, layer="0",
               arc={"center": (10, 0), "radius": 0.5, "start_deg": 0, "end_deg": 360}),
    ]
    texts = [TextRun(id="t3", text="3", box=(9.85, -0.2, 10.15, 0.2), height=0.4),
             TextRun(id="t4", text="salon", box=(3, 3, 6, 4), height=0.4)]
    assert AX.axis_line_ids(strokes, texts) == {"a1", "a2", "a3"}


def test_a_thinly_labelled_plan_adds_its_own_best_wall_layer_to_the_documents():
    """2 Nov 2026 (real10's 2nd basement, user: "2nd basement is fully underground and fully walled around"): its
    concrete outer walls on the column layer ranked first on its own evidence, yet only the document's plaster and
    masonry layers were taken and the outer ring stayed open."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from test_generic_walls import _face_plan

    from wenart.ingest.generic import walls as W
    from wenart.ingest.generic.model import TextRun
    page, _, _ = _face_plan()
    page.texts.append(TextRun(id="t3", text="DEPO", box=(8.6, 6.0, 9.4, 6.2), height=0.2))   # a label nothing closes
    page.document_wall_layers = ("MOB",)                      # the document's layer: here only a bed's outline
    prims, choice = W.face_pair_walls(page, 1.0, [])
    # ... and the corner column's layer A-BA (BA: betonarme, reinforced concrete) joins by its name
    assert choice["used"] and choice["layer"] == "W1" and choice["also"] == ["MOB", "A-BA"]
    assert choice["reason"] == "the document's other plans"


def test_the_cores_stair_places_the_top_floor_whose_machine_room_differs():
    """2 Nov 2026 (user: "Shaft on the terras, top flow is different than the rest"): real10's terrace floor has a
    lift machine room larger than the shaft below; its walls pulled the fit 0.60 / 1.26 m off. The spiral stair's
    eye (the same concentric arcs on every floor) places it exactly."""
    arcs = lambda cx, cy, radii: SimpleNamespace(strokes=[SimpleNamespace(arc={"center": (cx, cy), "radius": r})
                                                          for r in radii], kind="ARC")
    ref = SimpleNamespace(ents=[arcs(14.266, 11.37, (0.12, 0.17, 0.2, 0.8)), arcs(10.3, 11.7, (0.165, 0.19))])
    top = SimpleNamespace(ents=[arcs(44.864, 12.627, (0.12, 0.17, 0.2, 0.8))])
    eyes_ref = RG.stair_eyes(ref, 1.0, (12.0, 11.0))
    eyes_top = RG.stair_eyes(top, 1.0, (42.0, 12.0))
    fit = RG.stair_fit(eyes_ref, eyes_top, 0.0)
    assert fit["common"] == 4 and fit["shift"] == pytest.approx([-30.598, -1.257], abs=1e-6)
    assert RG.stair_fit(eyes_ref, RG.stair_eyes(SimpleNamespace(ents=[arcs(42, 12, (0.165, 0.19))]), 1.0,
                                                (42.0, 12.0)), 0.0) is None          # only 2 radii in common


def test_a_level_with_soil_all_round_is_closed_and_has_no_opening_to_the_soil():
    """2 Nov 2026 (real10's 2nd basement, user: "2n basement is fully underground and fully walled around", "first
    from the stairs and than from the door"): soil labels outside on 3+ sides: the outer gap closed (inferred), the
    openings on the outer ring removed; an inner door stays."""
    from wenart.ingest.generic import underground as UG
    from wenart.ingest.model import OpeningItem, TextItem, WallItem
    ev = {"method": "vector"}
    W = lambda a, b, t=0.3: WallItem(start=a, end=b, thickness=t, box=[0, 0, 1, 1], entity="w", evidence=ev)
    walls = [W((0, 0), (10, 0)), W((10, 0), (10, 4)), W((10, 6.2), (10, 8)), W((10, 8), (0, 8)), W((0, 8), (0, 0)),
             W((5, 0), (5, 8), 0.15)]
    O = lambda kind, c, w=0.9: OpeningItem(kind=kind, width=w, center=c, rotation_deg=0.0, box=[0, 0, 1, 1],
                                           entity="o", evidence=ev)
    opens = [O("window", (2.5, 8.0)), O("door", (5.0, 3.0))]
    T = lambda s, x, y: TextItem(text=s, start=(x, y), box=[x, y, x + 1, y + 0.2], rotation_deg=0.0, entity="t",
                                 height=0.2)
    texts = [T("SIKIŞTIRILMIŞ TOPRAK", -2, 4), T("SIKIŞTIRILMIŞ TOPRAK", 5, -1.5), T("SIKIŞTIRILMIŞ TOPRAK", 5, 9.5)]
    ex = SimpleNamespace(walls=list(walls), openings=list(opens), texts=texts, labels=[])
    note = UG.close_underground(ex, lambda p: p)
    assert note and "1 gap(s)" in note and "2.20 m" in note and "1 opening(s)" in note
    new = [w for w in ex.walls if w.inferred]
    assert len(new) == 1 and new[0].evidence["method"] == "inferred" and {new[0].start, new[0].end} == {(10, 4), (10, 6.2)}
    assert [o.kind for o in ex.openings] == ["door"]                    # the window to the soil is gone, the door stays
    ex2 = SimpleNamespace(walls=list(walls), openings=list(opens), texts=texts[:2], labels=[])
    assert UG.close_underground(ex2, lambda p: p) is None               # soil on 2 sides only: not underground
