"""4 Nov 2026, Milestone 14 R2 (the plan's words: "never leave a level out; carry confidence instead"; the user's
request behind it: "I want structure recognition to be cumulatively better with the feedbacks I am giving"): the
outline closure (the last closure pass of ``generic.core``), the ``failed_levels: build_marked`` policy of the
pipeline, the schema's low-confidence level fields and the reading check's RC7 low-confidence places. CPU only, pure
parts on hand-made walls and pages."""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from wenart import building as B
from wenart.ingest.generic import core as C
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke, TextRun
from wenart.ingest.generic import labels as LB
from wenart.ingest.model import LevelExtraction, OpeningItem, WallItem
import wenart.reading_check as RC


def _walls(xy, t=0.2):
    return [WallItem(start=a, end=b, thickness=t, box=[0, 0, 1, 1], entity=f"LINE:{k}",
                     evidence=B.evidence("x.dxf", "vector", 0.95, page=1, entity=f"LINE:{k}"))
            for k, (a, b) in enumerate(xy)]


def _blocks(labels):
    runs = [TextRun(id=f"T{k}", text=name, box=(x - 0.4, y - 0.1, x + 0.4, y + 0.1), height=0.2)
            for k, (name, x, y) in enumerate(labels)]
    return LB.merge_label_blocks(runs, "x.dxf", 1)


def _frames(segments, layer="PENCERE"):
    """Drawn frame lines (a glazed facade) along the given segments."""
    return [Stroke(id=f"F{k}", kind="line", pts=[a, b], layer=layer) for k, (a, b) in enumerate(segments)]


def _state(walls, openings, blocks):
    bw, site, sw = TP.split_plot(walls, openings, blocks, level_id="L0")
    idx = {o["index"] for o in site["openings"]}
    b_open = [o for j, o in enumerate(openings) if j not in idx]
    return bw, sw, b_open, TP.outer_loop_problem(bw, b_open)


def _close(walls, openings, blocks, strokes):
    ex = SimpleNamespace(notes=[], warnings=[], report={})
    bw, sw, b_open, prob = _state(walls, openings, blocks)
    got = C._outline_closure(ex, "x", walls, openings, blocks, "L0", sw, prob, bw, b_open, strokes, set(), "x.dxf", 1)
    return ex, got


# ------------------------------------------------------------------------------------------------- the closure pass
def test_a_glazed_corner_between_two_free_ends_is_closed_along_the_outline_at_confidence_0_3():
    """real09's living rooms: both facade walls stop short of the corner, frames run on to it."""
    walls = _walls([((2.0, 0.0), (5.0, 0.0)), ((5.0, 0.0), (5.0, 4.0)), ((5.0, 4.0), (0.0, 4.0)),
                    ((0.0, 4.0), (0.0, 1.5))])
    blocks = _blocks([("SALON", 2.5, 2.0)])
    strokes = _frames([((2.0, -0.05), (0.0, -0.05)), ((2.0, 0.05), (0.0, 0.05)),
                       ((-0.05, 1.5), (-0.05, 0.0)), ((0.05, 1.5), (0.05, 0.0))])
    assert _state(walls, [], blocks)[3] == "building walls enclose no face"
    ex, got = _close(walls, [], blocks, strokes)
    assert got is not None
    new_walls, _openings, bw, _site, sw, _b_open, prob = got
    assert prob is None and C._unclosed(sw) == 0
    added = [w for w in new_walls if w.evidence.get("rule") == C.OUTLINE_CLOSURE_RULE]
    assert len(added) == 2 and all(w.inferred and w.status == "unverified" for w in added)
    ends = sorted(tuple(sorted((w.start, w.end))) for w in added)
    assert ends == [(((0.0, 0.0)), (0.0, 1.5)), ((0.0, 0.0), (2.0, 0.0))]
    for w in added:
        assert w.evidence["method"] == "inferred" and w.evidence["confidence"] == C.CLOSURE_CONFIDENCE == 0.3
        assert "LINE:0 start at (2.00, 0.00)" in w.evidence["note"] and "LINE:3 end at (0.00, 1.50)" in w.evidence["note"]
        assert "3.50 m gap" in w.evidence["note"] and w.thickness == pytest.approx(0.2)
    rep = ex.report["outline_closure"]
    assert len(rep["kept"]) == 1 and rep["kept"][0]["kind"] == "corner" and rep["unclosed_after"] == 0
    assert any("outline closure (corner, confidence 0.3)" in n for n in ex.notes)
    assert any(C.OUTLINE_CLOSURE_RULE in w and "RC7" in w for w in ex.warnings)


def test_a_straight_gap_between_two_free_ends_is_bridged_with_the_median_outer_thickness():
    walls = _walls([((0.0, 0.0), (1.0, 0.0)), ((4.0, 0.0), (5.0, 0.0)), ((5.0, 0.0), (5.0, 4.0)),
                    ((5.0, 4.0), (0.0, 4.0)), ((0.0, 4.0), (0.0, 0.0))], t=0.3)
    walls[0].thickness = 0.3
    blocks = _blocks([("MUTFAK", 2.5, 2.0)])
    strokes = _frames([((1.0, 0.0), (4.0, 0.0))])
    ex, got = _close(walls, [], blocks, strokes)
    assert got is not None and got[6] is None
    added = [w for w in got[0] if w.evidence.get("rule") == C.OUTLINE_CLOSURE_RULE]
    assert len(added) == 1 and added[0].thickness == pytest.approx(0.3)
    xs = sorted((added[0].start[0], added[0].end[0]))          # from either free end, 1 cm into the wall it meets
    assert xs[0] == pytest.approx(1.0, abs=0.02) and xs[1] == pytest.approx(4.0, abs=0.02)
    assert added[0].start[1] == added[0].end[1] == 0.0
    assert ex.report["outline_closure"]["thickness"]["how"].startswith("median of")


def test_a_gap_across_a_drawn_door_is_never_bridged():
    """The door read in the gap stays a door (the openings reader's work): no wall across it."""
    walls = _walls([((0.0, 0.0), (1.9, 0.0)), ((3.1, 0.0), (5.0, 0.0)), ((5.0, 0.0), (5.0, 4.0)),
                    ((5.0, 4.0), (0.0, 4.0)), ((0.0, 4.0), (0.0, 0.0))])
    blocks = _blocks([("SALON", 2.5, 2.0)])
    door = OpeningItem(kind="door", width=0.9, center=(2.5, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1], entity="D1",
                       evidence=B.evidence("x.dxf", "vector", 0.9, page=1, entity="D1"))
    ex, got = _close(walls, [door], blocks, _frames([((1.9, 0.0), (3.1, 0.0))]))
    assert got is None
    rep = ex.report["outline_closure"]
    assert rep["kept"] == [] and any("drawn door or window" in r["why"] for r in rep["refused"])
    assert any("no bridge" in n for n in ex.notes)


def test_the_two_pieces_of_a_wall_split_on_purpose_are_never_closed_again():
    """An open recess (``_open_recesses`` splits the wall, same entity): its gap is open air, not a bridge."""
    walls = _walls([((0.0, 0.0), (1.9, 0.0)), ((3.1, 0.0), (5.0, 0.0)), ((5.0, 0.0), (5.0, 4.0)),
                    ((5.0, 4.0), (0.0, 4.0)), ((0.0, 4.0), (0.0, 0.0))])
    walls[1].entity = walls[0].entity                     # one drawn wall, split in two
    blocks = _blocks([("SALON", 2.5, 2.0)])
    cands = C.closure_candidates(walls, walls, [], _frames([((1.9, 0.0), (3.1, 0.0))]), 0.2)
    assert not any(c["kind"] == "straight" and c["length"] == pytest.approx(1.2, abs=0.02) for c in cands)


def test_a_corner_end_runs_on_only_along_drawn_lines_near_the_outline():
    """real11's kitchen: the facade runs from one wall's corner to another's; nothing is free. A bridge from a corner
    needs drawn lines along it (the frames) and it must lie near the drawn outline (not a counter line inside)."""
    # the kitchen (0..4 x 0..3): its bottom wall turns up into a shaft wall at x=4, the salon wall at x=7 comes down
    # to y=3 and turns east; the facade from (4, 0) to (7, 0) and up to (7, 3) is frames only
    walls = _walls([((0.0, 0.0), (4.0, 0.0)), ((4.0, 0.0), (4.0, -1.5)), ((0.0, 0.0), (0.0, 5.0)),
                    ((0.0, 5.0), (7.0, 5.0)), ((7.0, 5.0), (7.0, 3.0)), ((7.0, 3.0), (9.0, 3.0))])
    blocks = _blocks([("MUTFAK", 2.0, 2.5)])
    frames = _frames([((4.0, 0.0), (7.0, 0.0)), ((7.0, 0.0), (7.0, 3.0))])
    ends = C.ring_ends(walls, walls, [])
    assert any(not free and p == (4.0, 0.0) for _k, _w, p, _d, _h, free in ends)     # a corner end
    cands = C.closure_candidates(walls, walls, [], frames, 0.2)
    corner = [c for c in cands if c["kind"] == "corner" and not c["free"]]
    assert corner and corner[0]["support"] >= C.CLOSURE_SUPPORT_MIN
    ex, got = _close(walls, [], blocks, frames)
    assert got is not None and C._unclosed(got[4]) == 0
    assert all(c["kind"] == "corner" for c in ex.report["outline_closure"]["kept"])
    # the same corner with nothing drawn along it: refused (a free end is an evident gap; a corner is not)
    ex2, got2 = _close(walls, [], blocks, [])
    assert got2 is None and any("drawn lines along" in r["why"] for r in ex2.report["outline_closure"]["refused"])


def test_no_bridge_closes_a_balcony_label_into_a_room():
    walls = _walls([((2.0, 0.0), (5.0, 0.0)), ((5.0, 0.0), (5.0, 4.0)), ((5.0, 4.0), (0.0, 4.0)),
                    ((0.0, 4.0), (0.0, 1.5))])
    blocks = _blocks([("SALON", 3.5, 2.5), ("BALKON", 0.6, 0.5)])
    ex, got = _close(walls, [], blocks, _frames([((2.0, 0.0), (0.0, 0.0)), ((0.0, 1.5), (0.0, 0.0))]))
    assert got is None and any("balcony or terrace" in r["why"] for r in ex.report["outline_closure"]["refused"])


def test_the_closure_pass_stays_silent_when_the_ring_closes():
    walls = _walls([((0.0, 0.0), (5.0, 0.0)), ((5.0, 0.0), (5.0, 4.0)), ((5.0, 4.0), (0.0, 4.0)),
                    ((0.0, 4.0), (0.0, 0.0))])
    blocks = _blocks([("SALON", 2.5, 2.0)])
    bw, sw, b_open, prob = _state(walls, [], blocks)
    assert prob is None and C._unclosed(sw) == 0
    assert C.closure_candidates(walls, bw, b_open, [], 0.2) == []


def test_canopy_and_exit_words_name_no_room():
    """real11: 'GİRİŞ SAÇAK' (the entrance canopy) and 'SIĞINAK KAÇIŞI' (the shelter's escape) left every level out."""
    from wenart.ingest import pipeline as PL
    from wenart.levels import outdoor as OD

    assert OD.space_kind("GİRİŞ SAÇAK")["kind"] == "porch" and OD.space_kind("Canopy")["kind"] == "porch"
    assert OD.space_kind("SAÇAK ALTI")["kind"] == "porch" and OD.space_kind("SALON") is None
    assert TP._outdoor_label(_blocks([("GİRİŞ SAÇAK", 1.0, 1.0)])[0])
    for t in ("SIĞINAK KAÇIŞI", "ACİL ÇIKIŞ", "FIRE EXIT"):
        assert PL.ENTRANCE_WORD_RE.search(" ".join(B.fold_ascii(t).upper().split())), t
    assert not PL.ENTRANCE_WORD_RE.search("KACIS YOLU ODASI")


# ------------------------------------------------------------------------------------------- failed_levels: build_marked
def _build_and_record(policy="build_marked"):
    from wenart.ingest import pipeline as PL
    from wenart.ingest.classify import PageRecord

    build = PL.ProjectBuild(B.empty_building("p", "projects/p", "test"))
    build.failed_levels = policy
    build.sheets = {"multi_region": True}
    record = PageRecord(file="x.dwg", page=1, format="dwg", kind="vector", page_class="floor_plan", level_id="L0",
                        level_label="Zemin Kat", level_order=0, region_id="r1")
    return PL, build, record


def _extraction(walls=1, review=("x.dwg r1: outer walls do not close (building walls form 2 separate parts)",)):
    ex = LevelExtraction(file="x.dwg", page=1, level_id="L0", units="mm", source_kind="dxf")
    ex.scale = {"metres_per_unit": 0.01, "method": "unit_check", "confidence": 1.0}
    ex.transform_to_building = [0.01, 0, 0, 0, 0.01, 0]
    ex.walls = _walls([((0.0, 0.0), (5.0, 0.0))])[:walls]
    ex.review = list(review)
    return ex


def test_build_marked_builds_a_region_with_review_reasons_and_marks_its_level():
    PL, build, record = _build_and_record()
    ex = _extraction()
    assert PL.FAILED_LEVELS_DEFAULT == "build_marked" and PL._build_marked(build, record, ex)
    assert ex.review == [] and len(ex.reading_review) == 1 and build.marked_levels == {"L0"}
    assert any("outer walls do not close" in w and PL.BUILT_MARKED_NOTE in w for w in build.building["warnings"])
    assert not build.review_reasons
    level = {"id": "L0", "label": "Zemin Kat"}
    PL._level_review(build, "L0", ex, "L0: room labels outside every enclosed room ('MUTFAK')", True,
                     places=[{"kind": "unplaced_label", "text": "MUTFAK", "at": [1.0, 2.0]}])
    PL._mark_level(level, ex)
    assert level["reading_confidence"] == PL.READING_CONFIDENCE_LOW == "low" and len(level["reading_review"]) == 2
    assert level["reading_places"] == [{"kind": "unplaced_label", "text": "MUTFAK", "at": [1.0, 2.0]}]
    assert not build.review_reasons                        # the project status stays ok


def test_a_region_nothing_can_be_placed_in_is_still_left_out():
    PL, build, record = _build_and_record()
    for ex in (_extraction(walls=0), _extraction()):
        if ex.walls:
            ex.scale = None
        assert not PL._build_marked(build, record, ex) and ex.review and not ex.reading_review
    assert not build.marked_levels and not build.building["warnings"]


def test_leave_out_and_stop_keep_their_meaning():
    PL, build, record = _build_and_record("leave_out")
    ex = _extraction()
    assert not PL._build_marked(build, record, ex) and ex.review
    PL._level_review(build, "L0", ex, "L0: outer walls do not form a closed loop", False)
    assert build.review_reasons == ["L0: outer walls do not form a closed loop"]
    from wenart import brief as BR
    values = BR.merge_brief({})["values"]
    assert values["failed_levels"] == "build_marked"
    assert BR.merge_brief({"failed_levels": "stop"})["values"]["failed_levels"] == "stop"
    assert BR.merge_brief({"failed_levels": "leave_out"})["values"]["failed_levels"] == "leave_out"
    bad = BR.merge_brief({"failed_levels": "ignore"})
    assert bad["values"]["failed_levels"] == "build_marked" and bad["warnings"]


def test_a_level_without_reasons_is_not_marked():
    PL, build, record = _build_and_record()
    ex = _extraction(review=())
    assert PL._build_marked(build, record, ex) and not build.marked_levels
    level = {"id": "L0"}
    PL._mark_level(level, ex)
    assert "reading_confidence" not in level


# ------------------------------------------------------------------------------------------------------- the schema
def test_the_schema_accepts_the_low_confidence_level_fields():
    b = B.empty_building("p", "projects/p", "test")
    b["levels"].append({"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0, "ceiling_height": 2.7,
                        "ceiling_height_source": "assumed_default", "reading_confidence": "low",
                        "reading_review": ["r1 (L0): outer walls do not close"],
                        "reading_places": [{"kind": "unplaced_label", "text": "MUTFAK", "at": [1.0, 2.0],
                                            "note": "in no closed face"}]})
    assert B.validation_errors(b) == []
    b["levels"][0]["reading_confidence"] = "high"
    assert B.validation_errors(b)


# ----------------------------------------------------------------------------------------------------------- RC7
def _building_rc7():
    ev = B.evidence("x.dwg", "inferred", 0.3, page=1, entity="closure:LINE:1+LINE:2", rule=C.OUTLINE_CLOSURE_RULE)
    ev["note"] = "a 2.00 m gap from LINE:1 end to LINE:2 start bridged along the outline"
    return {"project": {"id": "p"},
            "levels": [{"id": "L0", "label": "Zemin Kat", "reading_confidence": "low",
                        "reading_review": ["r1 (L0): outer walls do not close (2 parts)"],
                        "reading_places": [{"kind": "unplaced_label", "text": "MUTFAK", "at": [1.0, 2.0]}]},
                       {"id": "L1", "label": "1. Kat"}],
            "walls": [{"id": "w_L0_001", "level_id": "L0", "start": [0, 0], "end": [2, 0], "thickness": 0.2,
                       "status": "unverified", "inferred": True, "evidence": [ev]},
                      {"id": "w_L0_002", "level_id": "L0", "start": [0, 0], "end": [0, 2], "thickness": 0.2,
                       "status": "verified", "evidence": [B.evidence("x.dwg", "vector", 1.0, page=1)]}],
            "warnings": ["x.dwg r1 (L0): r1 (L0): outer walls do not close (2 parts) (built, reading confidence low)"]}


def test_rc7_lists_the_level_its_closure_walls_and_its_unplaced_labels_numbered():
    assert RC.CLOSURE_RULE == C.OUTLINE_CLOSURE_RULE and RC.CHECKS["RC7"] == "low-confidence places"
    b = _building_rc7()
    out = RC.low_confidence_findings(b)
    assert [(f["severity"], f.get("place")) for f in out] == [("major", None), ("minor", 1), ("minor", 2)]
    assert out[0]["level_id"] == "L0" and "outer walls do not close" in out[0]["message"]
    assert out[1]["wall_id"] == "w_L0_001" and out[1]["at"] == [1.0, 0.0] and "place 1" in out[1]["message"]
    assert out[2]["text"] == "MUTFAK" and out[2]["at"] == [1.0, 2.0] and "place 2" in out[2]["message"]
    assert RC.is_closure_wall(b["walls"][0]) and not RC.is_closure_wall(b["walls"][1])


def test_rc7_comes_first_in_the_markdown_and_never_changes_the_verdict(tmp_path):
    (tmp_path / "building.json").write_text(json.dumps(_building_rc7()), encoding="utf-8")
    res = RC.check(tmp_path)
    checks = [f["check"] for f in res["findings"]]
    assert checks[:3] == ["RC7", "RC7", "RC7"] and res["verdict"] == "ready"
    assert "RC6" not in checks                              # the reason the level carries is RC7's, not RC6's too
    res["findings"].append(RC._finding("RC1", "critical", "order 2", "level 2. Kat left out of the model: x"))
    RC.write(tmp_path, res)
    md = (tmp_path / "reading_check" / "reading_check.md").read_text(encoding="utf-8")
    rows = [ln for ln in md.splitlines() if ln.startswith("| RC")]
    assert rows[0].startswith("| RC7") and rows[3].startswith("| RC1")


def test_the_sheets_draw_closure_walls_dashed_and_number_the_places():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from wenart.reading_check import sheets as SH

    b = _building_rc7()
    fig, ax = plt.subplots()
    SH._draw_model(ax, b, "L0", [1, 0, 0, 0, 1, 0], [-1, -1, 3, 3])
    styles = {ln.get_linestyle() for ln in ax.lines if ln.get_color() == SH.INFERRED_COLOUR}
    assert styles and all(s != "-" for s in styles)
    fig2, ax2 = plt.subplots()
    SH._mark_findings(ax2, RC.low_confidence_findings(b), b, "L0", [1, 0, 0, 0, 1, 0])
    assert sorted(t.get_text() for t in ax2.texts) == ["place 1", "place 2"]
    plt.close(fig)
    plt.close(fig2)


def test_every_conflict_kind_the_sheets_write_is_in_the_building_schema():
    """real11, once its levels were built: the registration's shaft_grid_mismatch conflict failed the building schema
    and the project went needs_review for that alone (the kind was in the sheets schema only)."""
    import json
    from pathlib import Path

    root = Path(B.__file__).resolve().parent / "schema"
    sheets = json.loads((root / "sheets.schema.json").read_text(encoding="utf-8"))
    building = json.loads((root / "building.schema.json").read_text(encoding="utf-8"))
    sheet_kinds = set(sheets["$defs"]["conflict"]["properties"]["kind"]["enum"])
    building_kinds = set(building["$defs"]["conflict"]["properties"]["kind"]["enum"])
    assert sheet_kinds <= building_kinds, sheet_kinds - building_kinds
