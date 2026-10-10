"""Walls inferred from labelled room outlines and sheet frame blocks (wenart/ingest/generic/outlines.py, frame.py;
CLAUDE.md evidence and inference rules: open outer walls -> infer first, mark ``inferred``).

Hand-made DXFs (centimetres): three rooms drawn only as closed outlines with a name and a printed area inside, 15 cm
apart, a door symbol in the wall between two of them, and a sheet frame block (frame + title block rows that pass
the outline-wall rule) around the plan. Without drawn walls the walls are inferred along the outlines; with drawn
walls (a wall hatch) nothing is inferred. real03 (the user's D Blok ground floor: the flats are empty external
references, only the core's room outlines are drawn) runs end to end when LibreDWG is installed.
"""
from __future__ import annotations

import math
from pathlib import Path

import ezdxf
import pytest
from shapely.geometry import Polygon

from conftest import PROJECTS
from wenart.ingest import dwg
from wenart.ingest import dxf_generic as DG
from wenart.ingest.generic import core
from wenart.ingest.generic import frame as FR
from wenart.ingest.generic import topology as TP

# Rooms in cm: (name, printed area, outline). The corridor runs along the top of both rooms, 15 cm apart from them;
# the two rooms are 15 cm apart from each other.
ROOMS = [
    ("SALON", "12,00 m²", [(0, 0), (400, 0), (400, 300), (0, 300)]),
    ("YATAK ODASI", "9,00 m²", [(415, 0), (715, 0), (715, 300), (415, 300)]),
    ("KORIDOR", "14,30 m²", [(0, 315), (715, 315), (715, 515), (0, 515)]),
]
OUTER = 25.0                                   # cm: the wall hatch's outer ring


def _plan(walls: bool = False, frame: bool = True):
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 5                  # cm
    msp = doc.modelspace()
    doc.layers.add("ALAN-NET")
    for name, area, pts in ROOMS:
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "ALAN-NET"})
        cx = sum(p[0] for p in pts) / 4.0
        cy = sum(p[1] for p in pts) / 4.0
        msp.add_text(name, height=12, dxfattribs={"layer": "TEXT"}).set_placement((cx, cy + 4),
                                                                                  align=ezdxf.enums.TextEntityAlignment.BOTTOM_CENTER)
        msp.add_text(area, height=10, dxfattribs={"layer": "TEXT"}).set_placement((cx, cy - 12),
                                                                                  align=ezdxf.enums.TextEntityAlignment.BOTTOM_CENTER)
    # A 90 cm door from SALON into the corridor: hinge on SALON's top face, leaf open into SALON, quarter arc.
    msp.add_line((100, 300), (100, 210), dxfattribs={"layer": "KAPI"})
    msp.add_arc((100, 300), 90, 270, 360, dxfattribs={"layer": "KAPI"})
    if walls:
        hatch = msp.add_hatch(color=7, dxfattribs={"layer": "DUVAR"})
        hatch.paths.add_polyline_path([(-OUTER, -OUTER), (715 + OUTER, -OUTER), (715 + OUTER, 515 + OUTER),
                                       (-OUTER, 515 + OUTER)], is_closed=True, flags=1)
        for _, _, pts in ROOMS:
            hatch.paths.add_polyline_path(pts, is_closed=True)
    if frame:
        # The sheet frame and its title block as one block (real03's legend block): the title rows are thin
        # closed rectangles (5 x 50 cm at the drawing unit) that pass the outline-wall rule on their own.
        blk = doc.blocks.new("LEGEND")
        blk.add_lwpolyline([(-300, -300), (1300, -300), (1300, 900), (-300, 900)], close=True)
        blk.add_lwpolyline([(-290, -290), (1290, -290), (1290, 890), (-290, 890)], close=True)
        for k in range(4):
            y = -280 + k * 40
            blk.add_lwpolyline([(1100, y), (1280, y), (1280, y + 25), (1100, y + 25)], close=True)
        blk.add_line((1100, 800), (1280, 800))
        msp.add_blockref("LEGEND", (0, 0), dxfattribs={"layer": "LEJAND"})
        msp.add_text("ZEMIN KAT PLANI", height=20, dxfattribs={"layer": "TEXT"}).set_placement((1110, -100))
    return doc


def _extract(tmp_path: Path, **kw):
    path = tmp_path / "plan.dxf"
    _plan(**kw).saveas(path)
    page = DG.read_page(path, "plan.dxf")
    return page, core.extract(page, "L0", "plan.dxf", no_ai=True)


def _room_faces(ex) -> list[Polygon]:
    return TP.faces(ex.walls, [o for o in ex.openings if not o.virtual], ex.separators)


def test_frame_block_found_and_kept_out(tmp_path):
    page, ex = _extract(tmp_path, walls=True)
    frames = FR.frame_blocks(page)
    assert len(frames) == 1 and frames[0]["block"] == "LEGEND"
    assert any("sheet frame block" in n for n in ex.notes)
    # No wall lies in the title block column (x >= 11 m page metres).
    for w in ex.walls:
        assert w.evidence.get("entity", "").find(frames[0]["entity"]) < 0


def test_a_plan_block_is_no_frame_block(tmp_path):
    """A block whose strokes fill the middle of its outer rectangle is a drawing, not a frame block."""
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 5
    blk = doc.blocks.new("PLAN")
    blk.add_lwpolyline([(0, 0), (1000, 0), (1000, 800), (0, 800)], close=True)
    blk.add_lwpolyline([(400, 300), (600, 300), (600, 500), (400, 500)], close=True)
    doc.modelspace().add_blockref("PLAN", (0, 0))
    doc.modelspace().add_line((450, 350), (550, 450))
    path = tmp_path / "p.dxf"
    doc.saveas(path)
    assert FR.frame_blocks(DG.read_page(path, "p.dxf")) == []


def test_room_outlines_without_walls_give_inferred_walls(tmp_path):
    _, ex = _extract(tmp_path, walls=False)
    assert not ex.review, ex.review
    assert ex.walls and all(w.inferred for w in ex.walls)
    for w in ex.walls:
        ev = w.evidence
        assert ev["method"] == "inferred" and ev["rule"] == "room_outlines"
        assert w.status == "unverified"
        assert ev["entity"].startswith("LWPOLYLINE:")
        assert "inferred from the labelled room outlines" in ev["note"]
    assert TP.outer_loop_problem(ex.walls, ex.openings) is None
    # The faces are the drawn outlines: the areas match the printed ones.
    faces = sorted(round(f.area, 2) for f in _room_faces(ex))
    assert faces == [9.0, 12.0, 14.3]
    # Inner walls are the 15 cm gaps, outer walls 0.25 m (assumed default).
    thick = sorted({round(w.thickness, 3) for w in ex.walls if math.dist(w.start, w.end) > 1.0})
    assert thick == [0.15, 0.25]
    # The drawn door is read on the inferred wall; nothing is invented for the bedroom.
    doors = [o for o in ex.openings if o.kind == "door"]
    assert len(doors) == 1 and abs(doors[0].width - 0.9) < 0.01 and doors[0].evidence["method"] == "vector"
    assert any("walls inferred from room outlines" in w for w in ex.warnings)
    assert any("'YATAK ODASI'" in w and "no door" in w for w in ex.warnings)
    assert not any("'SALON'" in w and "no door" in w for w in ex.warnings)
    # The title block rows of the frame block are no walls.
    assert all(w.start[0] < 8.0 and w.end[0] < 8.0 for w in ex.walls)


def test_drawn_walls_stay_and_nothing_is_inferred(tmp_path):
    _, ex = _extract(tmp_path, walls=True)
    assert not ex.review, ex.review
    assert ex.walls and not any(w.inferred for w in ex.walls)
    assert all(w.evidence["method"] in ("vector", "derived") for w in ex.walls)
    assert "walls_from_outlines" not in ex.report
    assert not any("walls inferred" in w for w in ex.warnings)


def test_no_outlines_still_needs_review(tmp_path):
    """Nothing usable (labels without outlines, no walls): the review stop stands."""
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 5
    msp = doc.modelspace()
    msp.add_text("SALON", height=12).set_placement((100, 100))
    msp.add_text("12,00 m²", height=10).set_placement((100, 84))
    msp.add_line((0, 0), (400, 0))
    path = tmp_path / "n.dxf"
    doc.saveas(path)
    ex = core.extract(DG.read_page(path, "n.dxf"), "L0", "n.dxf", no_ai=True)
    assert ex.review
    assert not any(getattr(w, "inferred", False) for w in ex.walls)


def test_outline_area_must_match_its_label(tmp_path):
    """An outline whose area is off its printed area by more than 8 % is no room outline."""
    from wenart.ingest.generic import labels as LB
    from wenart.ingest.generic import outlines as OL

    path = tmp_path / "plan.dxf"
    _plan(frame=False).saveas(path)
    page = DG.read_page(path, "plan.dxf")
    strokes, texts = core.to_metres(page, 0.01)
    blocks = LB.merge_label_blocks(texts, "plan.dxf", None)
    assert len(OL.labelled_outlines(strokes, blocks)) == 3
    for b in blocks:
        if b.name == "SALON":
            b.area_m2 = 13.5                             # 12.00 drawn: 11 % off
    names = sorted(o.block.name for o in OL.labelled_outlines(strokes, blocks))
    assert names == ["KORIDOR", "YATAK ODASI"]


# --------------------------------------------------------------------------
# real03 end to end
# --------------------------------------------------------------------------

REAL03_LABELS = {"YANGIN MERDİVENİ": 14.17, "KAT MERDİVENİ": 14.17, "GÜVENLİK HOLÜ": 3.38, "KAT HOLÜ": 46.94,
                 "RÜZGARLIK": 9.64}


@pytest.fixture(scope="module")
def real03(tmp_path_factory):
    if not dwg.available_converters():
        pytest.skip("LibreDWG dwg2dxf not installed")
    from wenart.ingest import pipeline as P

    out = tmp_path_factory.mktemp("real03")
    b, _ = P.run_project(PROJECTS / "real03", out, no_ai=True)
    return b, out


def test_real03_builds_from_room_outlines(real03):
    b, out = real03
    assert b["status"] != "needs_review", b["warnings"]
    rooms = {r["label_raw"]: r for r in b["rooms"]}
    assert set(rooms) == set(REAL03_LABELS)
    for name, area in REAL03_LABELS.items():
        assert rooms[name]["area_label"] == pytest.approx(area)
        assert rooms[name]["area_computed"] == pytest.approx(area, rel=0.01)
    inferred = [w for w in b["walls"] if w.get("inferred")]
    assert len(inferred) >= 20 and len(inferred) == len(b["walls"])
    assert all(w["evidence"][0]["method"] == "inferred" and w["status"] == "unverified" for w in inferred)
    # The title block (legend block) gives no walls: every wall lies around the core (26.5 x 15 m).
    for w in b["walls"]:
        for x, y in (w["start"], w["end"]):
            assert -0.5 <= x <= 27.0 and -0.5 <= y <= 15.5
    doors = [o for o in b["openings"] if o["type"] == "door"]
    assert len(doors) == 4
    assert any("walls inferred from room outlines" in w for w in b["warnings"])
    assert "Walls inferred from room outlines" in (out / "report.md").read_text(encoding="utf-8")
