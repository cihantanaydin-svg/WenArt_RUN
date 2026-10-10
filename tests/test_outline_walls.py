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

@pytest.fixture(scope="module")
def real03(tmp_path_factory):
    if not dwg.available_converters():
        pytest.skip("LibreDWG dwg2dxf not installed")
    from wenart.ingest import pipeline as P

    out = tmp_path_factory.mktemp("real03")
    b, _ = P.run_project(PROJECTS / "real03", out, no_ai=True)
    return b, out


def test_real03_reads_the_whole_ground_floor(real03):
    """real03 follow-up (10 Oct 2026, docs/milestone11.md §19.8): with the patched LibreDWG the flats are in the DXF;
    their clipped blocks, ring walls and the concrete core give the whole floor from vector geometry, so the
    room-outline fallback of the core-only reading is no longer needed."""
    b, out = real03
    assert b["status"] == "ok", b["warnings"]
    types = [r["room_type"] for r in b["rooms"]]
    assert types.count("living") == 8 and types.count("bathroom") == 8 and types.count("stair") == 2
    assert types.count("bedroom") >= 9
    labels = {r["label_raw"] for r in b["rooms"]}
    assert {"KAT HOLÜ", "RÜZGARLIK", "KAT MERDİVENİ", "YANGIN MERDİVENİ"} <= labels
    assert "SUBSTATİON" not in labels                    # a services-layer text, no room name
    assert not [w for w in b["walls"] if w.get("inferred")]
    assert any("ring:" in str(w["evidence"][0].get("entity")) for w in b["walls"])
    # The title block (legend block) gives no walls: every wall lies in the building (33.2 x 14.6 m).
    for w in b["walls"]:
        for x, y in (w["start"], w["end"]):
            assert -0.5 <= x <= 34.0 and -0.5 <= y <= 15.5
    # Oversized furniture clusters are recorded, never built as boxes.
    assert all(f.get("build") is False for f in b["furniture"]
               if f["type"] == "unknown" and max(f["footprint"]["size"]) > 4.5)


def test_real03_furniture_is_read_completely(real03):
    """Milestone 12 track R (docs/milestone12.md §4.1 D7), without AI answers: no untyped box is built, every unbuilt
    piece says why; the room-number circles, door swings and trace / area / text-frame strokes are symbols; the
    counter runs, sinks, fridges and corner sofas of the eight flats are read from the drawing (before: 43 built
    unknown boxes, 7 oversized clusters, no counter, sink or fridge); the toilets have their real size (the axis line
    through the klozet block is left out: 0.36 x 0.53 m, before 1.145 x 0.356 m); each living room's open kitchen is
    a zone. The candidates the AI is asked about stay unknown (not built, listed for review) until answered."""
    from collections import Counter

    from wenart.furniture import sizes

    b, out = real03
    built = [f for f in b["furniture"] if f.get("build") is not False]
    assert not [f for f in built if f["type"] == "unknown"]
    assert all(f.get("not_built_reason") or f.get("inferred_reason") for f in b["furniture"] if f.get("build") is False)
    kinds = Counter(s["kind"] for s in b["symbols"])
    assert kinds["room_number"] == 8 and kinds["door_arc"] >= 15 and kinds["text_frame"] >= 4 and kinds["other"] >= 20
    types = Counter(f["type"] for f in built)
    assert types["kitchen_counter"] >= 8 and types["sofa_corner"] >= 6 and types["toilet"] == 8
    assert types["sink_kitchen"] >= 6 and types["fridge"] >= 6 and types["table_dining"] >= 2
    assert all(sizes.fits("toilet", f["footprint"]["size"]) for f in built if f["type"] == "toilet")
    assert sorted(r["room_type"] for r in b["rooms"] if r.get("zones")) == ["living"] * 8
    review = {n["id"] for n in b["needs_review"]}
    assert all(f.get("build") is False for f in b["furniture"] if f["id"] in review)
    assert "## Reading (Milestone 12)" in (out / "report.md").read_text(encoding="utf-8")
