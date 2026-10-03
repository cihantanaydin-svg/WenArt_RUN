"""The generic DXF adapter (wenart/ingest/dxf_generic.py, docs/milestone7.md §5.2) on hand-made DXFs and on the
synthetic-06 source: nested inserts and their block chains, ATTRIBs, units, even-odd hatches with islands, colours,
dimensions measured from geometry (incl. a rotated one without its angle), texts, curves, hidden layers."""
import math
from pathlib import Path

import ezdxf
import pytest
from ezdxf import recover
from shapely.geometry import Polygon
from shapely.ops import unary_union

from wenart.ingest import dxf_generic as DG
from wenart.ingest.dxf_extract import has_synthetic_layers, read_dxf
from wenart.synthetic import blocks
from wenart.synthetic.projects import plan_06

from conftest import PROJECTS

SOURCE_06 = PROJECTS / "synthetic-06" / "source" / "synthetic-06.dxf"


def new_doc(insunits: int = 1):
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = insunits
    return doc


def save(doc, tmp_path: Path, name: str = "plan.dxf") -> Path:
    path = tmp_path / name
    doc.saveas(path)
    return path


def by_id(items):
    return {item.id: item for item in items}


def patch_entity(path: Path, handle: str, code: int, value=None) -> None:
    """Rewrite group code ``code`` of the entity ``handle`` in a DXF text file (``value`` None: remove the pair).
    ezdxf itself never writes a rotated dimension without code 50 or an MTEXT of height 0, while files converted
    from a DWG by LibreDWG do."""
    lines = path.read_text(encoding="utf-8").split("\n")
    start = next(i for i in range(0, len(lines) - 1) if lines[i].strip() == "5" and lines[i + 1].strip() == handle)
    end = start + 2
    while end < len(lines) - 1 and lines[end].strip() != "0":
        end += 2
    hits = [k for k in range(start, end, 2) if lines[k].strip() == str(code)]
    assert hits, f"no group code {code} in entity {handle}"
    for k in reversed(hits):
        if value is None:
            del lines[k:k + 2]
        else:
            lines[k + 1] = str(value)
    path.write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------------------
# Units, layers, dispatch
# --------------------------------------------------------------------------

@pytest.mark.parametrize("code, metres", [(1, 0.0254), (2, 0.3048), (4, 0.001), (5, 0.01), (6, 1.0)])
def test_units_from_insunits(tmp_path, code, metres):
    doc = new_doc(code)
    doc.modelspace().add_line((0, 0), (1, 0))
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    assert page.units_to_m == metres and DG.units_to_m(code) == metres
    assert page.source_kind == "dxf" and page.units == "dxf" and page.page == 1
    assert not any("$INSUNITS" in w for w in page.warnings)


@pytest.mark.parametrize("code", [0, 3, 14])
def test_unitless_or_unusual_insunits_leave_the_scale_to_the_dimensions(tmp_path, code):
    doc = new_doc(code)
    doc.modelspace().add_line((0, 0), (1, 0))
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    assert page.units_to_m is None
    assert any(f"$INSUNITS={code}" in w and "dimension" in w for w in page.warnings)


def test_wall_hint_layers():
    for name in ("A-WALL", "WALLS", "a-wall-ext", "DUVAR", "MUR_EXT", "Pared"):
        assert DG.is_wall_hint_layer(name), name
    for name in ("A-DOOR", "FURN", "0", None, ""):
        assert not DG.is_wall_hint_layer(name), name


def test_dispatch_by_synthetic_layers():
    assert has_synthetic_layers(read_dxf(PROJECTS / "synthetic-01" / "zemin_kat.dxf")[0])
    assert not has_synthetic_layers(read_dxf(SOURCE_06)[0])
    doc = new_doc()
    doc.layers.add("MOBILYA")                       # a layer nobody draws on does not count
    doc.modelspace().add_line((0, 0), (1, 0), dxfattribs={"layer": "A-WALL"})
    assert not has_synthetic_layers(doc)
    doc.modelspace().add_line((0, 0), (1, 0), dxfattribs={"layer": "duvar"})
    assert has_synthetic_layers(doc)


# --------------------------------------------------------------------------
# Blocks: nested inserts, block chain, layer 0 and BYBLOCK, ATTRIBs
# --------------------------------------------------------------------------

def _nested_doc():
    doc = new_doc()
    doc.layers.add("A-FURN", color=3)
    chair = doc.blocks.new("CHAIR")
    chair.add_lwpolyline([(-9, -9), (9, -9), (9, 9), (-9, 9)], close=True)           # layer 0, BYLAYER
    chair.add_line((-9, 6), (9, 6), dxfattribs={"color": 0})                        # BYBLOCK
    chair.add_attdef("NO", (0, 0), dxfattribs={"height": 3})
    table = doc.blocks.new("DINING-6")
    table.add_lwpolyline([(-36, -18), (36, -18), (36, 18), (-36, 18)], close=True)
    inner = table.add_blockref("CHAIR", (0, 29), dxfattribs={"color": 0})         # BYBLOCK: passes the colour on
    inner.add_attrib("NO", "C1", (0, 29), dxfattribs={"height": 3})
    tag = doc.blocks.new("ROOMTAG")
    tag.add_attdef("NAME", (0, 0), dxfattribs={"height": 9})
    msp = doc.modelspace()
    ins = msp.add_blockref("DINING-6", (100, 200), dxfattribs={"layer": "A-FURN", "rotation": 90, "color": 1})
    roomtag = msp.add_blockref("ROOMTAG", (10, 20), dxfattribs={"layer": "A-ANNO"})
    roomtag.add_auto_attribs({"NAME": "KITCHEN"})
    hidden = msp.add_blockref("ROOMTAG", (50, 20), dxfattribs={"layer": "A-ANNO"})
    hidden.add_auto_attribs({"NAME": "SECRET"})
    hidden.attribs[0].dxf.flags = 1                                                   # invisible attribute
    return doc, ins, roomtag


def test_nested_inserts_keep_the_block_chain_and_take_the_insert_layer_and_colour(tmp_path):
    doc, ins, _ = _nested_doc()
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    strokes = by_id(page.strokes)
    h = ins.dxf.handle
    table = strokes[f"INSERT:{h}/0"]
    assert table.block == "DINING-6" and table.layer == "A-FURN" and table.closed
    # Rotated 90 degrees about (100, 200): the 72 x 36 table stands upright.
    x0, y0, x1, y1 = table.bbox()
    assert (x0, y0, x1, y1) == pytest.approx((82, 164, 118, 236))
    chair = strokes[f"INSERT:{h}/1/0"]
    assert chair.block == "DINING-6/CHAIR" and chair.layer == "A-FURN"
    assert chair.colour == (0.0, 1.0, 0.0)          # BYLAYER on layer 0 -> the INSERT's layer (A-FURN, ACI 3 green)
    back = strokes[f"INSERT:{h}/1/1"]
    assert back.colour == (1.0, 0.0, 0.0)           # BYBLOCK in BYBLOCK -> the outer INSERT's colour (ACI 1 red)
    cx, cy = ((chair.bbox()[0] + chair.bbox()[2]) / 2, (chair.bbox()[1] + chair.bbox()[3]) / 2)
    assert (cx, cy) == pytest.approx((100 - 29, 200))
    assert not any("ATTDEF" in w for w in page.warnings)


def test_attribs_of_every_insert_are_texts_nested_included(tmp_path):
    doc, ins, roomtag = _nested_doc()
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    texts = {t.text: t for t in page.texts}
    assert set(texts) == {"KITCHEN", "C1"}          # the invisible attribute and the ATTDEF templates are not read
    kitchen = texts["KITCHEN"]
    assert kitchen.id == f"ATTRIB:{roomtag.attribs[0].dxf.handle}" and kitchen.height == 9
    assert kitchen.box[0] == pytest.approx(10) and kitchen.box[1] < 20 < kitchen.box[3]
    assert kitchen.evidence[0]["layer"] == "A-ANNO" and kitchen.evidence[0]["block"] == "ROOMTAG"
    nested = texts["C1"]
    assert nested.id.startswith(f"INSERT:{ins.dxf.handle}/1/attrib")
    # The attribute moved and turned with the rotated DINING-6 insert: (0, 29) -> (100 - 29, 200), upright.
    assert nested.rotation_deg == 90 and nested.box[0] < 100 - 29 < nested.box[2]
    assert nested.box[1] == pytest.approx(200)
    assert nested.evidence[0]["block"] == "DINING-6/CHAIR"


def test_collect_texts_has_block_texts_and_attribs(tmp_path):
    doc, _, _ = _nested_doc()
    blk = doc.blocks.new("NOTE")
    blk.add_text("BED ROOM", height=9)
    msp = doc.modelspace()
    msp.add_blockref("NOTE", (0, 100))
    msp.add_text("LIVING ROOM", height=9).set_placement((0, 0))
    msp.add_mtext("DINING\\PSTORE", dxfattribs={"char_height": 6, "insert": (0, 50)})
    texts = DG.collect_texts(recover.readfile(str(save(doc, tmp_path)))[0])
    assert sorted(t.text for t in texts) == ["BED ROOM", "C1", "DINING", "KITCHEN", "LIVING ROOM", "STORE"]
    assert all(t.evidence == [] for t in texts)
    with_ev = DG.collect_texts(doc, "plan.dxf")
    assert all(t.evidence and t.evidence[0]["file"] == "plan.dxf" for t in with_ev)
    assert not any(t.text for t in texts if t.text == "SECRET")


def test_minsert_copies_get_their_own_ids(tmp_path):
    doc = new_doc()
    blk = doc.blocks.new("POST")
    blk.add_circle((0, 0), 2)
    ins = doc.modelspace().add_blockref("POST", (0, 0))
    ins.grid(size=(1, 3), spacing=(0, 10))
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    ids = sorted(s.id for s in page.strokes)
    h = ins.dxf.handle
    assert ids == [f"INSERT:{h}[0]/0", f"INSERT:{h}[1]/0", f"INSERT:{h}[2]/0"]
    assert sorted(s.arc["center"][0] for s in page.strokes) == [0.0, 10.0, 20.0]


# --------------------------------------------------------------------------
# Hatches, fills, colours
# --------------------------------------------------------------------------

def _hatch_doc(layer="A-WALL", solid=True, style=0, colour=7):
    doc = new_doc()
    doc.layers.add(layer, color=5)
    hatch = doc.modelspace().add_hatch(color=colour, dxfattribs={"layer": layer, "hatch_style": style})
    if not solid:
        hatch.set_pattern_fill("ANSI31", scale=1.0)
    hatch.paths.add_polyline_path([(0, 0), (100, 0), (100, 60), (0, 60)], is_closed=True, flags=1)
    hatch.paths.add_polyline_path([(10, 10), (40, 10), (40, 50), (10, 50)], is_closed=True, flags=16)
    hatch.paths.add_polyline_path([(50, 10), (90, 10), (90, 50), (50, 50)], is_closed=True, flags=16)
    hatch.paths.add_polyline_path([(60, 20), (70, 20), (70, 30), (60, 30)], is_closed=True, flags=0)  # island in island
    return doc, hatch


def _even_odd_area(strokes) -> float:
    shape = Polygon()
    for st in strokes:
        shape = shape.symmetric_difference(Polygon(st.pts))
    return shape.area


def test_hatch_is_one_even_odd_shape_over_all_its_paths(tmp_path):
    doc, hatch = _hatch_doc()
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    paths = [s for s in page.strokes if s.id.startswith(f"HATCH:{hatch.dxf.handle}#")]
    assert [s.id.split("#")[1] for s in paths] == ["0", "1", "2", "3"]
    assert all(s.closed and s.fill == (0.0, 0.0, 0.0) and s.colour == (0.0, 0.0, 0.0) for s in paths)   # ACI 7
    assert all(s.layer == "A-WALL" and len(s.pts) == 4 for s in paths)
    # Even-odd: outer 6000 - islands 1200 and 1600 + the island inside an island 100.
    assert _even_odd_area(paths) == pytest.approx(6000 - 1200 - 1600 + 100)
    assert page.wall_hint_layers == ("A-WALL",)


@pytest.mark.parametrize("style, kept", [(1, ["0", "1", "2"]), (2, ["0"])])
def test_hatch_style_outer_and_ignore(tmp_path, style, kept):
    doc, hatch = _hatch_doc(style=style)
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    assert [s.id.split("#")[1] for s in page.strokes] == kept


def test_pattern_hatch_is_filled_only_on_wall_layers(tmp_path):
    doc, _ = _hatch_doc(layer="A-WALL", solid=False)
    assert all(s.fill is not None for s in DG.read_page(save(doc, tmp_path, "a.dxf"), "a.dxf").strokes)
    doc, _ = _hatch_doc(layer="A-FLOR-PATT", solid=False)
    page = DG.read_page(save(doc, tmp_path, "b.dxf"), "b.dxf")
    assert page.strokes and all(s.fill is None and s.closed for s in page.strokes)
    assert page.wall_hint_layers == ()


def test_colours_aci7_white_bylayer_and_true_colour(tmp_path):
    doc = new_doc()
    doc.layers.add("RED", color=1)
    white = doc.layers.add("WHITE-TC")
    white.rgb = (255, 255, 255)
    msp = doc.modelspace()
    a = msp.add_line((0, 0), (1, 0), dxfattribs={"color": 7})
    b = msp.add_line((0, 1), (1, 1), dxfattribs={"layer": "RED"})
    c = msp.add_line((0, 2), (1, 2), dxfattribs={"true_color": ezdxf.rgb2int((255, 255, 255))})
    d = msp.add_line((0, 3), (1, 3), dxfattribs={"true_color": ezdxf.rgb2int((0, 128, 255))})
    e = msp.add_line((0, 4), (1, 4), dxfattribs={"layer": "WHITE-TC"})
    f = msp.add_line((0, 5), (1, 5), dxfattribs={"color": 0})                     # BYBLOCK at the top level
    s = by_id(DG.read_page(save(doc, tmp_path), "plan.dxf").strokes)
    assert s[f"LINE:{a.dxf.handle}"].colour == (0.0, 0.0, 0.0)
    assert s[f"LINE:{b.dxf.handle}"].colour == (1.0, 0.0, 0.0)
    assert s[f"LINE:{c.dxf.handle}"].colour == (0.0, 0.0, 0.0)
    assert s[f"LINE:{d.dxf.handle}"].colour == pytest.approx((0.0, 128 / 255, 1.0), abs=1e-6)
    assert s[f"LINE:{e.dxf.handle}"].colour == (0.0, 0.0, 0.0)
    assert s[f"LINE:{f.dxf.handle}"].colour == (0.0, 0.0, 0.0)


def test_solid_is_a_filled_quadrilateral(tmp_path):
    doc = new_doc()
    solid = doc.modelspace().add_solid([(0, 0), (10, 0), (0, 5), (10, 5)], dxfattribs={"color": 7})
    st = by_id(DG.read_page(save(doc, tmp_path), "plan.dxf").strokes)[f"SOLID:{solid.dxf.handle}"]
    assert st.closed and st.fill == (0.0, 0.0, 0.0)
    assert Polygon(st.pts).area == pytest.approx(50.0)          # vertex order 0, 1, 3, 2: no bow tie


# --------------------------------------------------------------------------
# Curves
# --------------------------------------------------------------------------

def test_lines_polylines_bulges_arcs_circles(tmp_path):
    doc = new_doc(4)                                             # millimetres: flattening to 5 mm
    msp = doc.modelspace()
    pl = msp.add_lwpolyline([(0, 0, 0), (1000, 0, 1.0), (1000, 1000, 0), (2000, 1000, 0)], format="xyb")
    round_table = msp.add_lwpolyline([(0, 5000, 1.0), (1200, 5000, 1.0)], format="xyb", close=True)
    plain = msp.add_lwpolyline([(0, 0), (10, 0), (10, 10)], close=True)
    arc = msp.add_arc((500, 500), 900, 0, 90)
    mirrored = msp.add_arc((0, 0), 800, 0, 90, dxfattribs={"extrusion": (0, 0, -1)})
    circle = msp.add_circle((3000, 3000), 450)
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    s = by_id(page.strokes)
    h = pl.dxf.handle
    # Open polyline with a bulge: straight run, one arc (semicircle of the 1000 mm chord), straight run.
    assert [s[f"LWPOLYLINE:{h}:{k}"].kind for k in range(3)] == ["line", "arc", "line"]
    semi = s[f"LWPOLYLINE:{h}:1"]
    assert semi.arc["radius"] == pytest.approx(500) and semi.arc["center"] == pytest.approx((1000, 500))
    assert semi.pts[0] == (1000.0, 0.0) and semi.pts[-1] == (1000.0, 1000.0)
    sag = max(abs(math.hypot(x - 1000, y - 500) - 500) for (x, y) in
              [((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(semi.pts, semi.pts[1:])])
    assert sag <= 5.0 + 1e-6                                     # chord error <= 5 mm
    table = s[f"LWPOLYLINE:{round_table.dxf.handle}"]
    assert table.closed and table.arc and table.arc["radius"] == pytest.approx(600, rel=1e-3)
    assert table.arc["start_deg"] == 0 and table.arc["end_deg"] == 360
    box = s[f"LWPOLYLINE:{plain.dxf.handle}"]
    assert box.kind == "polyline" and box.closed and box.arc is None and len(box.pts) == 3
    a = s[f"ARC:{arc.dxf.handle}"]
    assert a.kind == "arc" and a.arc == {"center": (500.0, 500.0), "radius": 900.0, "start_deg": 0.0, "end_deg": 90.0}
    m = s[f"ARC:{mirrored.dxf.handle}"]
    # Extrusion -Z mirrors the arc: OCS 0..90 deg is WCS 90..180 deg (still counter-clockwise start -> end).
    assert m.arc["start_deg"] == pytest.approx(90.0) and m.arc["end_deg"] == pytest.approx(180.0)
    assert all(x <= 1e-6 and y >= -1e-6 for x, y in m.pts)
    c = s[f"CIRCLE:{circle.dxf.handle}"]
    assert c.kind == "circle" and c.closed and c.arc["radius"] == 450 and c.pts[0] != c.pts[-1]


def test_ellipse_and_spline_are_flattened_and_circles_found(tmp_path):
    doc = new_doc(4)
    msp = doc.modelspace()
    ellipse = msp.add_ellipse((0, 0), major_axis=(1000, 0), ratio=0.5)
    round_ellipse = msp.add_ellipse((5000, 0), major_axis=(300, 0), ratio=1.0)
    spline = msp.add_spline([(0, 0), (500, 400), (1000, 0), (1500, -400), (2000, 0)])
    point = msp.add_point((7, 7))
    msp.add_point((8, 8), dxfattribs={"layer": "Defpoints"})
    s = by_id(DG.read_page(save(doc, tmp_path), "plan.dxf").strokes)
    e = s[f"ELLIPSE:{ellipse.dxf.handle}"]
    assert e.kind == "curve" and e.closed and e.arc is None
    assert max(x for x, _ in e.pts) == pytest.approx(1000, abs=5) and max(y for _, y in e.pts) == pytest.approx(500, abs=5)
    assert s[f"ELLIPSE:{round_ellipse.dxf.handle}"].arc["radius"] == pytest.approx(300, rel=1e-3)
    sp = s[f"SPLINE:{spline.dxf.handle}"]
    assert sp.kind == "curve" and not sp.closed and len(sp.pts) > 10
    assert sp.pts[0] == (0.0, 0.0) and sp.pts[-1] == (2000.0, 0.0)
    dot = s[f"POINT:{point.dxf.handle}"]
    assert dot.pts == [(7.0, 7.0), (7.0, 7.0)]
    assert not any(st.pts[0] == (8.0, 8.0) for st in s.values())            # DEFPOINTS never plots


def test_hidden_layers_and_unsupported_types_are_reported(tmp_path):
    doc = new_doc()
    off = doc.layers.add("OFF")
    off.off()
    frozen = doc.layers.add("FROZEN")
    frozen.freeze()
    msp = doc.modelspace()
    msp.add_line((0, 0), (1, 0), dxfattribs={"layer": "OFF"})
    msp.add_text("HIDDEN", dxfattribs={"layer": "FROZEN"})
    msp.add_line((0, 1), (1, 1))
    msp.add_leader([(0, 0), (5, 5)])
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    assert len(page.strokes) == 1 and page.texts == []
    assert any("2 entities on layers that are off or frozen" in w for w in page.warnings)
    assert any("not read: LEADER x1" in w for w in page.warnings)


# --------------------------------------------------------------------------
# Texts
# --------------------------------------------------------------------------

def test_mtext_paragraphs_inline_heights_and_attachment(tmp_path):
    doc = new_doc()
    msp = doc.modelspace()
    m = msp.add_mtext("\\H9;LIVING ROOM\\P{\\H0.5x;14'-0\" X 12'-0\"}",
                      dxfattribs={"char_height": 0.0, "insert": (100, 200), "attachment_point": 1})
    c = msp.add_mtext("WC", dxfattribs={"char_height": 6, "insert": (0, 0), "attachment_point": 5})
    page = DG.read_page(save(doc, tmp_path), "plan.dxf")
    t = by_id(page.texts)
    name, size = t[f"MTEXT:{m.dxf.handle}:0"], t[f"MTEXT:{m.dxf.handle}:1"]
    assert (name.text, name.height) == ("LIVING ROOM", 9) and (size.text, size.height) == ("14'-0\" X 12'-0\"", 4.5)
    assert name.box[0] == 100 and name.box[3] == 200                          # top left at the insert point
    assert size.box[3] < name.box[1]                                          # the size line is below the name
    wc = t[f"MTEXT:{c.dxf.handle}"]                                           # one paragraph: no :k suffix
    assert (wc.box[0] + wc.box[2]) / 2 == pytest.approx(0) and wc.box[1] < 0 < wc.box[3]
    assert not page.warnings


def test_mtext_without_any_height_uses_textsize_with_a_warning(tmp_path):
    doc = new_doc()
    doc.header["$TEXTSIZE"] = 7.0
    m = doc.modelspace().add_mtext("KITCHEN", dxfattribs={"insert": (0, 0)})
    path = save(doc, tmp_path)
    patch_entity(path, m.dxf.handle, 40, "0.0")                  # what LibreDWG's dxf2dwg makes of MTEXT heights
    page = DG.read_page(path, "plan.dxf")
    assert page.texts[0].height == 7.0
    assert any(f"MTEXT:{m.dxf.handle} has no text height" in w for w in page.warnings)


def test_text_alignment_and_rotation(tmp_path):
    doc = new_doc()
    msp = doc.modelspace()
    left = msp.add_text("BATH", height=10)
    left.set_placement((0, 0))
    centred = msp.add_text("HALL", height=10)
    centred.set_placement((100, 0), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    upright = msp.add_text("30'", height=10, rotation=90)
    upright.set_placement((200, 0))
    t = by_id(DG.read_page(save(doc, tmp_path), "plan.dxf").texts)
    assert t[f"TEXT:{left.dxf.handle}"].box == pytest.approx((0, -2.5, 32, 10))
    hall = t[f"TEXT:{centred.dxf.handle}"]
    assert ((hall.box[0] + hall.box[2]) / 2, (hall.box[1] + hall.box[3]) / 2) == pytest.approx((100, -1.25))
    up = t[f"TEXT:{upright.dxf.handle}"]
    assert up.rotation_deg == 90 and up.box == pytest.approx((190, 0, 202.5, 24))


# --------------------------------------------------------------------------
# Dimensions
# --------------------------------------------------------------------------

def test_dimensions_are_measured_from_geometry(tmp_path):
    doc = new_doc()
    msp = doc.modelspace()
    aligned = msp.add_aligned_dim(p1=(0, 0), p2=(30, 40), distance=10, text="4'-2\"")
    aligned.render()
    aligned.dimension.dxf.dimtype = (aligned.dimension.dxf.dimtype & ~7) | 1
    aligned.dimension.dxf.discard("angle")
    rotated = msp.add_linear_dim(base=(-20, 0), p1=(0, 0), p2=(30, 40), angle=90)   # vertical part only
    rotated.render()
    lost = msp.add_linear_dim(base=(-50, 0), p1=(0, 0), p2=(0, 120), angle=90, text="10'-0\"")
    lost.render()
    lost.dimension.dxf.actual_measurement = 7.0                 # code 42 is never read
    zero = msp.add_linear_dim(base=(0, -10), p1=(5, 5), p2=(5, 5), angle=0)
    zero.render()
    path = save(doc, tmp_path)
    patch_entity(path, lost.dimension.dxf.handle, 50)          # no angle: what LibreDWG's dxf2dwg leaves of it
    page = DG.read_page(path, "plan.dxf")
    d = by_id(page.dimensions)
    a = d[f"DIMENSION:{aligned.dimension.dxf.handle}"]
    assert a.measured_units == 50.0 and a.text == "4'-2\"" and (a.p1, a.p2) == ((0.0, 0.0), (30.0, 40.0))
    r = d[f"DIMENSION:{rotated.dimension.dxf.handle}"]
    assert r.measured_units == 40.0 and r.text is None and r.p1[0] == r.p2[0] == -20.0
    rec = d[f"DIMENSION:{lost.dimension.dxf.handle}"]
    assert rec.measured_units == 120.0 and rec.p1 == (-50.0, 0.0) and rec.p2 == (-50.0, 120.0)
    assert f"DIMENSION:{zero.dimension.dxf.handle}" not in d
    assert any(f"DIMENSION:{zero.dimension.dxf.handle} measures" in w and "dropped" in w for w in page.warnings)
    # The dimension block's lines and text are not strokes or texts of the page.
    assert page.strokes == [] and page.texts == []


def test_dimension_angle_from_block_needs_a_dimension_line(tmp_path):
    doc = new_doc()
    dim = doc.modelspace().add_linear_dim(base=(0, 50), p1=(0, 0), p2=(80, 0), angle=0)
    dim.render()
    ent = dim.dimension
    assert DG.dimension_angle_from_block(ent) == 0.0
    vertical = doc.modelspace().add_linear_dim(base=(30, 0), p1=(0, 0), p2=(0, 80), angle=90)
    vertical.render()
    assert DG.dimension_angle_from_block(vertical.dimension) == 90.0
    for e in list(doc.blocks.get(ent.dxf.geometry)):
        if e.dxftype() == "LINE":
            doc.blocks.get(ent.dxf.geometry).delete_entity(e)
    assert DG.dimension_angle_from_block(ent) is None
    path = save(doc, tmp_path)
    patch_entity(path, ent.dxf.handle, 50)
    page = DG.read_page(path, "plan.dxf")
    assert [d.id for d in page.dimensions] == [f"DIMENSION:{vertical.dimension.dxf.handle}"]
    assert any("states no angle and its block draws no dimension line" in w for w in page.warnings)


# --------------------------------------------------------------------------
# synthetic-06 source
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def page06():
    return DG.read_page(SOURCE_06, "synthetic-06.dwg")


def test_synthetic_06_page(page06):
    plan = plan_06()
    p = page06
    assert p.units_to_m == 0.0254 and p.wall_hint_layers == (blocks.CAD_LAYER_WALLS,) and p.warnings == []
    hatch = [s for s in p.strokes if s.id.startswith("HATCH:")]
    assert len({s.id.split("#")[0] for s in hatch}) == 1 and len(hatch) == 6     # outer loop + 5 room islands
    assert all(s.fill == (0.0, 0.0, 0.0) for s in hatch)
    wall_area = unary_union([Polygon(w.rectangle()) for w in plan.walls]).area
    assert _even_odd_area(hatch) == pytest.approx(wall_area, rel=1e-9)        # the hatch is the wall union
    doors = [s for s in p.strokes if s.layer == blocks.CAD_LAYER_DOORS and s.kind == "arc"]
    assert sorted(s.arc["radius"] for s in doors) == sorted(d.width for d in plan.doors)
    assert sum(1 for s in p.strokes if s.layer == blocks.CAD_LAYER_GLAZING) == 5 * len(plan.windows)
    chains = {s.block for s in p.strokes if s.block}
    assert chains == {"SOFA-3", "DINING-6", "DINING-6/CHAIR", "BED-DOUBLE", "WC", "BASIN"}
    assert sum(1 for s in p.strokes if s.block == "DINING-6/CHAIR" and s.closed) == 6
    texts = {t.text: t for t in p.texts}
    assert set(texts) == {"LIVING ROOM", "14'-0\" X 12'-0\"", "KITCHEN", "LOBBY", "BATH", "BED ROOM",
                          "MASTER BED ROOM"}
    assert texts["KITCHEN"].id.startswith("ATTRIB:") and texts["LIVING ROOM"].id.endswith(":0")
    assert texts["LIVING ROOM"].height == 9.0                                   # also with the DWG's height 0


def test_synthetic_06_dimensions_measure_the_drawing(page06):
    plan = plan_06()
    dims = page06.dimensions
    assert len(dims) == len(plan.dimensions)
    for prim, dim in zip(dims, plan.dimensions):
        assert prim.measured_units == pytest.approx(math.dist(dim.p1, dim.p2)), prim
        assert prim.text == dim.text
    rotated_vertical = [d for d, spec in zip(dims, plan.dimensions) if spec.kind == "rotated" and spec.p1[0] == spec.p2[0]]
    assert len(rotated_vertical) == 1 and rotated_vertical[0].measured_units == 366.0
