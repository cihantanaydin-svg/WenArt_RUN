"""CAD-PDF adapter (wenart/ingest/cad_pdf.py, docs/milestone7.md §2.2, §11 G3).

- a hand-made page (reportlab): y up, colours in gray/RGB/CMYK, fills only on paths with an area, closed paths,
  a Bézier quarter circle flattened from the path (not from its two vertices) with ``arc``, a zero-length dot,
  rotated text;
- the flattening itself: chord error <= 0.25 pt, ``h`` and a repeated first point close a path, ``v``/``y`` forms;
- stroke ids follow ``pdf_extract``'s path numbering (synthetic-01's PDF);
- real01: the 5 door swings come out as arcs of radius 0.72-1.02 m at the reference scale with their hinges where
  the reference puts them; the dimension lines are red; texts are merged runs.
"""
import math

import pdfplumber
import pytest
from reportlab.pdfgen import canvas as rl_canvas

import _real01_page as RP
from wenart.ingest import cad_pdf
from wenart.ingest.pdf_extract import read_page_objects

from conftest import PROJECTS

FT = 0.3048


@pytest.fixture(scope="module")
def handmade(tmp_path_factory):
    path = tmp_path_factory.mktemp("cadpdf") / "page.pdf"
    c = rl_canvas.Canvas(str(path), pagesize=(600, 400))
    c.setLineWidth(0.72)
    c.setStrokeColorRGB(1, 0, 0)
    c.line(100, 50, 300, 50)                                    # path 0: red, y up
    c.setStrokeColorCMYK(0, 1, 1, 0)
    c.line(100, 60, 300, 60)                                    # path 1: CMYK red
    c.setStrokeGray(0.5)
    c.line(100, 70, 300, 70)                                    # path 2: gray
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0.1, 0.5, 0.1)
    p = c.beginPath()                                           # path 3: filled, closed triangle
    p.moveTo(400, 300)
    p.lineTo(440, 300)
    p.lineTo(420, 340)
    p.close()
    c.drawPath(p, stroke=1, fill=1)
    p = c.beginPath()                                           # path 4: a quarter circle, r 50, centre (150, 200)
    p.moveTo(200, 200)
    k = 0.5522847498 * 50
    p.curveTo(200, 200 + k, 150 + k, 250, 150, 250)
    c.drawPath(p, stroke=1, fill=0)
    c.line(500, 100, 500, 100)                                  # path 5: a dot
    c.rect(50, 300, 40, 20, stroke=1, fill=0)                   # path 6: rectangle
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 12)
    c.drawString(300, 200, "Bed Room")
    c.saveState()
    c.translate(80, 150)
    c.rotate(90)
    c.drawString(0, 0, "30'")
    c.restoreState()
    c.showPage()
    c.save()
    return cad_pdf.read_page(path, 1, "page.pdf")


def by_id(page, sid):
    return next(s for s in page.strokes if s.id == sid)


def test_y_up_colours_and_kinds(handmade):
    page = handmade
    assert page.size == (600.0, 400.0) and page.units == "pt" and page.source_kind == "cad_pdf"
    assert page.units_to_m is None and page.file == "page.pdf" and page.page == 1
    red = by_id(page, "path:0")
    assert red.kind == "line" and red.pts == [(100.0, 50.0), (300.0, 50.0)] and red.colour == (1.0, 0.0, 0.0)
    assert red.width == pytest.approx(0.72) and red.fill is None and not red.closed
    assert by_id(page, "path:1").colour == pytest.approx((1.0, 0.0, 0.0))
    assert by_id(page, "path:2").colour == pytest.approx((0.5, 0.5, 0.5))
    tri = by_id(page, "path:3")
    assert tri.closed and tri.fill == pytest.approx((0.1, 0.5, 0.1)) and len(tri.pts) == 3
    assert sorted(tri.pts) == [(400.0, 300.0), (420.0, 340.0), (440.0, 300.0)]
    rect = by_id(page, "path:6")
    assert rect.closed and rect.kind == "polyline" and rect.fill is None
    assert sorted(rect.pts) == [(50.0, 300.0), (50.0, 320.0), (90.0, 300.0), (90.0, 320.0)]


def test_bezier_is_flattened_from_the_path_and_gets_an_arc(handmade):
    arc = by_id(handmade, "path:4")
    assert arc.kind == "curve" and len(arc.pts) > 4                   # not just the two path vertices
    assert arc.pts[0] == (200.0, 200.0) and arc.pts[-1] == pytest.approx((150.0, 250.0))
    for p in arc.pts:                                                 # chord points on the circle
        assert math.dist(p, (150.0, 200.0)) == pytest.approx(50.0, abs=0.05)
    for a, b in zip(arc.pts, arc.pts[1:]):                            # chord error <= 0.25 pt
        mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        assert 50.0 - math.dist(mid, (150.0, 200.0)) <= cad_pdf.CHORD_PT
    assert arc.arc["center"] == pytest.approx((150.0, 200.0), abs=0.05)
    assert arc.arc["radius"] == pytest.approx(50.0, rel=0.002)
    assert arc.arc["start_deg"] == pytest.approx(0.0, abs=0.1) and arc.arc["end_deg"] == pytest.approx(90.0, abs=0.1)
    # Straight paths never get an arc.
    assert all(s.arc is None for s in handmade.strokes if s.kind != "curve")


def test_dots_are_kept(handmade):
    dot = by_id(handmade, "path:5")
    assert dot.pts == [(500.0, 100.0), (500.0, 100.0)] and dot.colour == (0.0, 0.0, 0.0)


def test_texts_are_merged_runs_with_rotation(handmade):
    texts = {t.text: t for t in handmade.texts}
    assert set(texts) == {"Bed Room", "30'"}
    bed = texts["Bed Room"]
    assert bed.rotation_deg == 0.0 and bed.id.startswith("char:")
    x0, y0, x1, y1 = bed.box
    assert x0 == pytest.approx(300.0, abs=0.5) and y0 < 202 < y1 and x1 > 350          # y up
    upright = texts["30'"]
    assert upright.rotation_deg == pytest.approx(90.0)
    x0, y0, x1, y1 = upright.box
    assert y1 - y0 > x1 - x0 and y0 == pytest.approx(150.0, abs=0.5)


def test_flatten_path_closing_and_short_bezier_forms():
    pts, closed, bezier, _ = cad_pdf.flatten_path([("m", (0, 0)), ("l", (10, 0)), ("l", (10, 10)), ("h",)])
    assert pts == [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)] and closed and not bezier
    pts, closed, _, _ = cad_pdf.flatten_path([("m", 0, 0), ("l", 10, 0), ("l", 10, 10), ("l", 0, 0)])
    assert closed and len(pts) == 3                                   # a repeated first point closes too
    # "v": the first control point is the current point; "y": the second one is the end point.
    for op in (("v", (50, 30), (50, 50)), ("y", (20, 0), (50, 50))):
        pts, closed, bezier, dense = cad_pdf.flatten_path([("m", (0, 0)), op])
        assert bezier and not closed and pts[-1] == pytest.approx((50.0, 50.0)) and len(pts) >= 3 and len(dense) >= 5


def test_colour_normalisation():
    assert cad_pdf.colour_rgb(None) is None
    assert cad_pdf.colour_rgb(0.25) == (0.25, 0.25, 0.25)
    assert cad_pdf.colour_rgb((0.25,)) == (0.25, 0.25, 0.25)
    assert cad_pdf.colour_rgb((0.1, 0.2, 0.3)) == (0.1, 0.2, 0.3)
    assert cad_pdf.colour_rgb((0.0, 0.0, 0.0, 1.0)) == (0.0, 0.0, 0.0)
    assert cad_pdf.colour_rgb((0.0, 1.0, 1.0, 0.0)) == (1.0, 0.0, 0.0)
    assert cad_pdf.colour_rgb("P1") is None                           # a pattern has no RGB value


def test_stroke_ids_follow_pdf_extract_numbering():
    path = PROJECTS / "synthetic-01" / "1_kat.pdf"
    page = cad_pdf.read_page(path, 1, "1_kat.pdf")
    with pdfplumber.open(str(path)) as pdf:
        objects = read_page_objects(pdf.pages[0])
    strokes = {s.id: s for s in page.strokes}
    assert len(strokes) == len(objects.paths)
    for obj in objects.paths:
        st = strokes[obj.entity]
        assert st.pts[0] == pytest.approx(obj.pts[0], abs=1e-6)
    assert [t.text for t in page.texts] == [t.text for t in objects.texts]


@pytest.fixture(scope="module")
def real01():
    return cad_pdf.read_page(PROJECTS / "real01" / "real01.pdf", 1, "real01.pdf")


def _sweep(arc) -> float:
    return abs((arc["end_deg"] - arc["start_deg"] + 180.0) % 360.0 - 180.0)


def test_real01_door_arcs_from_the_bezier_paths(real01):
    m_per_pt = RP.M_PER_PT
    # Swing-sized arcs (the two 0.65 m, 67 deg arcs are the folded blankets on the beds).
    doors = [s for s in real01.strokes if s.arc and not s.closed and 0.70 <= s.arc["radius"] * m_per_pt <= 1.05
             and 60.0 <= _sweep(s.arc) <= 100.0]
    assert len(doors) == 5
    radii = sorted(s.arc["radius"] * m_per_pt for s in doors)
    assert 0.72 <= radii[0] and radii[-1] <= 1.02
    ref = RP.reference()["doors"]
    for d in ref:
        hinge_pt = RP.ref_point(*d["hinge_ft"])
        hinge_pt = (hinge_pt[0] / m_per_pt, hinge_pt[1] / m_per_pt)
        hits = [s for s in doors if math.dist(s.arc["center"], hinge_pt) * m_per_pt <= d["tol"]["hinge"] * FT]
        assert len(hits) == 1, d["id"]
        radius_ft = hits[0].arc["radius"] * m_per_pt / FT
        assert radius_ft == pytest.approx(d["swing_radius_ft"], abs=d["tol"]["swing_radius"])
        assert len(hits[0].pts) > 2 and hits[0].kind == "curve"


def test_real01_colours_texts_and_counts(real01):
    assert len(real01.strokes) == 27259 + 9592 + 26
    red = [s for s in real01.strokes if s.colour == (1.0, 0.0, 0.0)]
    assert len(red) >= 4                                              # the two dimension lines and their marks
    green_fills = [s for s in real01.strokes if s.fill and s.fill[1] > s.fill[0] + 0.05]
    assert len(green_fills) > 1000                                    # the plants
    texts = [t.text for t in real01.texts]
    assert "Bath+" in texts and "Toilet" in texts and "50'" in texts and "11' x 10'" in texts
    assert texts.count("Bed Room") == 2
    assert all(t.box[1] < t.box[3] for t in real01.texts)
