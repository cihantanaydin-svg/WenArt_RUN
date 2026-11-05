"""5 Nov 2026 (Milestone 14 track R8; user: "I want structure recognition to be cumulatively better with the feedbacks
I am giving"): the stability test of the reader. Pure tests of the DXF variants on a small generated drawing, the
mapping back of a reading, and one end-to-end run on projects/synthetic-06 (CPU, about 30 s)."""
from __future__ import annotations

import copy

import ezdxf
import pytest

from wenart.reading_check import score as SC
from wenart.reading_check import stability as ST


def small_dxf(path):
    """Two rooms, a door block, two windows, a dimension text, a level mark, a label, a circle."""
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 5                                     # cm
    for name in ("WALL", "DOOR", "WINDOW", "TEXT", "OLCU"):
        doc.layers.add(name)
    blk = doc.blocks.new("DOORSYM")
    blk.add_line((0, 0), (90, 0), dxfattribs={"layer": "DOOR"})
    msp = doc.modelspace()
    for rect in (((0, 0), (400, 0), (400, 300), (0, 300)), ((400, 0), (800, 0), (800, 300), (400, 300))):
        msp.add_lwpolyline(list(rect), close=True, dxfattribs={"layer": "WALL"})
    msp.add_blockref("DOORSYM", (400, 100), dxfattribs={"layer": "DOOR"})
    msp.add_line((100, 0), (200, 0), dxfattribs={"layer": "WINDOW"})
    msp.add_line((500, 300), (600, 300), dxfattribs={"layer": "WINDOW"})
    msp.add_circle((200, 150), 20, dxfattribs={"layer": "WALL"})
    msp.add_text("315", dxfattribs={"layer": "TEXT", "insert": (200, -30), "height": 10})
    msp.add_text("+3.00", dxfattribs={"layer": "TEXT", "insert": (0, 330), "height": 10})
    msp.add_text("Kitchen", dxfattribs={"layer": "TEXT", "insert": (100, 100), "height": 15})
    msp.add_text("90/210", dxfattribs={"layer": "TEXT", "insert": (400, 120), "height": 10})
    msp.add_text("Bedroom", dxfattribs={"layer": "OLCU", "insert": (600, 100), "height": 15})
    doc.saveas(str(path))
    return path


def points(doc):
    out = []
    for e in doc.modelspace():
        t = e.dxftype()
        if t == "LINE":
            out += [tuple(e.dxf.start)[:2], tuple(e.dxf.end)[:2]]
        elif t == "LWPOLYLINE":
            out += [tuple(v)[:2] for v in e.vertices_in_wcs()]      # a mirror may flip the extrusion (OCS)
        elif t == "CIRCLE":
            out.append(tuple(e.ocs().to_wcs(e.dxf.center))[:2])
        elif t == "INSERT":
            out.append(tuple(e.ocs().to_wcs(e.dxf.insert))[:2])
    return out


@pytest.fixture()
def drawing(tmp_path):
    return small_dxf(tmp_path / "small.dxf")


@pytest.mark.parametrize("kind,times", [("mirror", 2), ("rotate90", 4)])
def test_geometric_variants_return_to_the_start(drawing, kind, times):
    doc = ezdxf.readfile(str(drawing))
    before = points(doc)
    for _ in range(times):
        assert not ST.apply_geometry(doc, kind)["failed"]
    after = points(doc)
    assert len(before) == len(after)
    assert max(abs(a - b) for p, q in zip(before, after) for a, b in zip(p, q)) < 1e-6


def test_mirror_really_flips_x_and_keeps_y(drawing):
    doc = ezdxf.readfile(str(drawing))
    before = points(doc)
    ST.apply_geometry(doc, "mirror")
    after = points(doc)
    sums = {round(a[0] + b[0], 6) for a, b in zip(after, before)}
    assert len(sums) == 1                                                     # one mirror axis for every point
    assert all(a[1] == pytest.approx(b[1], abs=1e-6) for a, b in zip(after, before))
    assert after[0][0] != before[0][0]


def test_mm_scales_by_the_header_unit_and_skips_mm(drawing):
    doc = ezdxf.readfile(str(drawing))
    res = ST.apply_mm(doc)
    assert res["factor"] == pytest.approx(10.0) and doc.header["$INSUNITS"] == 4
    assert max(abs(c) for p in points(doc) for c in p) == pytest.approx(8000.0, abs=1e-6)
    assert ST.apply_mm(doc).get("skipped") == "already mm"


def test_layer_renaming_keeps_the_count_and_renames_block_entities(drawing):
    doc = ezdxf.readfile(str(drawing))
    n = len(list(doc.layers))
    ST.apply_layers(doc)
    names = [lay.dxf.name for lay in doc.layers]
    assert len(names) == n and len({x.lower() for x in names}) == n
    assert not {"WALL", "DOOR", "WINDOW", "TEXT", "OLCU"} & set(names)
    used = {e.dxf.layer for e in doc.modelspace()} | {e.dxf.layer for e in doc.blocks.get("DOORSYM")}
    assert used <= set(names)
    assert next(iter(doc.blocks.get("DOORSYM"))).dxf.layer.startswith("L")


def test_nodims_removes_dimensions_and_keeps_labels_and_size_tags(drawing):
    doc = ezdxf.readfile(str(drawing))
    res = ST.apply_nodims(doc)
    left = sorted(e.dxf.text for e in doc.modelspace() if e.dxftype() == "TEXT")
    assert res["removed"] == 3                       # "315", "+3.00" and the label on the dimension layer OLCU
    assert left == ["90/210", "Kitchen"]


@pytest.mark.parametrize("text,layer,expected", [("315", "A", True), ("3.15", "A", True), ("±0.00", "A", True),
                                                 ("+3.00", "A", True), ("KOT +3.00", "A", True),
                                                 ("90/210", "OLCU", False), ("Kitchen", "A-ANNO", False),
                                                 ("Kitchen", "dim_text", True), ("Living 12 m2", "A", False)])
def test_dimension_text_rule(text, layer, expected):
    assert ST.is_dimension_text(text, layer) is expected


# --- the mapping back ---------------------------------------------------------------------------------------------

def reading_of(project):
    """A truth-shaped reading of one level built by hand (rooms, doors, windows, walls, a stair)."""
    walls = [{"id": f"w{i}", "start": s, "end": e, "thickness": 0.2} for i, (s, e) in enumerate(
        [([0, 0], [8, 0]), ([8, 0], [8, 6]), ([8, 6], [0, 6]), ([0, 6], [0, 0]), ([4, 0], [4, 6])])]
    return {"project": project, "status": "accepted", "levels": [{"id": "L0", "elevation": 0.0, "order": 0}],
            "per_level": {"L0": {"rooms": [{"id": "a", "label": "Kitchen", "centroid": [2, 3],
                                            "polygon": [[0, 0], [4, 0], [4, 6], [0, 6]]},
                                           {"id": "b", "label": "Bedroom", "centroid": [6, 3],
                                            "polygon": [[4, 0], [8, 0], [8, 6], [4, 6]]}],
                                "doors": [{"id": "d", "center": [4, 2], "width": 0.9}],
                                "windows": [{"id": "x", "center": [2, 0], "width": 1.2},
                                            {"id": "y", "center": [6, 6], "width": 1.2}],
                                "openings": [], "walls": walls,
                                "stairs": [{"id": "s", "center": [6, 4], "flights": [{"start": [5, 4], "end": [7, 4]}]}]}}}


@pytest.mark.parametrize("kind", ["mirror", "rotate90"])
def test_mapping_back_of_the_forward_reading_scores_100(kind):
    orig = reading_of("p")
    var = ST.forward(orig, kind)
    back = ST.map_back(orig, var, kind)
    assert SC.match(orig, back)["total"] == 100.0
    assert not ST.findings(orig, back, kind)


def test_levels_are_mapped_by_elevation():
    orig = reading_of("p")
    var = copy.deepcopy(orig)
    var["levels"] = [{"id": "Z9", "elevation": 0.02, "order": 5}]
    var["per_level"] = {"Z9": var["per_level"]["L0"]}
    back = ST.relabel_levels(var, ST.level_id_map(orig, var))
    assert back["levels"][0]["id"] == "L0" and "L0" in back["per_level"]
    assert SC.match(orig, back)["total"] == 100.0


def test_findings_name_what_was_lost_and_added():
    orig = reading_of("p")
    var = copy.deepcopy(orig)
    var["per_level"]["L0"]["windows"].pop()
    var["per_level"]["L0"]["doors"].append({"id": "n", "center": [1, 5], "width": 0.9})
    f = ST.findings(orig, var, "layers")
    assert {(x["change"], x["kind"]) for x in f} == {("lost", "windows"), ("added", "doors")}
    grouped = ST.group_fragile(f + [dict(f[0], variant="mm")])
    assert grouped["L0"][0]["variants"] == ["layers", "mm"]


# --- the real thing -----------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def synthetic06(tmp_path_factory):
    work = tmp_path_factory.mktemp("stability")
    return ST.stability_project("synthetic-06", work, ("mirror", "layers"))


def test_synthetic06_mirror_end_to_end(synthetic06):
    e = synthetic06["variants"]["mirror"]
    assert e["row"]["levels_read"] == e["row"]["levels_truth"] == 1
    assert e["row"]["total"] == pytest.approx(100.0, abs=2.0)
    assert "mirror" in ST.table([synthetic06])


@pytest.mark.xfail(strict=True, reason="found 5 Nov 2026: with every layer renamed the reader of synthetic-06 loses "
                   "the room labels (A-ANNO) and most walls, doors and windows (it keys on drafter layer names); "
                   "the places are in work/stability/synthetic-06.json")
def test_synthetic06_layer_renaming_is_stable(synthetic06):
    assert synthetic06["variants"]["layers"]["row"]["total"] == pytest.approx(100.0, abs=2.0)
