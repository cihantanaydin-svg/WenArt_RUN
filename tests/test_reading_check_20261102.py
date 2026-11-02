"""2 Nov 2026 (user: "We need to improve this initial project reading part currently it is requiring a lot of fixing",
"go ahead with all 4", "can we keep improving this regression set?"): the reading self-check (floors that do not
stack, areas against the drawing's own area texts, drawn walls not built, walls on no drawn line), its conventions
record and the reading regression set's comparison. CPU only, pure parts."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import wenart.reading_check as RC
from wenart.reading_check import regress as RG


def test_floors_that_do_not_stack_are_critical_by_their_axes_and_arc_sets():
    ref = {"axes": {"1": ("v", 1.75), "2": ("v", 2.15), "A": ("h", 1.75)}, "stairs": [((14.27, 11.37), {0.12, 0.17, 0.2})]}
    off = {"axes": {"1": ("v", 0.20), "2": ("v", 0.60), "A": ("h", 0.00)}, "stairs": [((12.7, 9.6), {0.12, 0.17, 0.2})]}
    same = {"axes": dict(ref["axes"]), "stairs": list(ref["stairs"])}
    out = RC.stacking({"L0": ref, "L-1": off, "L1": same}, "L0")
    assert [f["level_id"] for f in out] == ["L-1"] and out[0]["severity"] == "critical"
    assert out[0]["offset_m"] == pytest.approx(1.75, abs=0.01) and "median of 4" in out[0]["message"]   # 1.55 x, 1.75 y


def test_an_area_text_against_the_room_it_stands_in():
    page = SimpleNamespace(texts=[SimpleNamespace(text="220.60 m2", box=(5, 5, 6, 5.2)),
                                  SimpleNamespace(text="h:2.70 m", box=(5, 4, 6, 4.2))])
    tf = [1, 0, 0, 0, 1, 0]
    room = {"id": "r1", "label": "Sığınak", "polygon": [[0, 0], [20, 0], [20, 10], [0, 10]], "area_computed": 180.0}
    out = RC.area_findings(page, tf, [room], "L-2")
    assert len(out) == 1 and out[0]["drawn_m2"] == 220.6 and out[0]["model_m2"] == 180.0
    room["area_computed"] = 211.1                                           # within 5 %: no finding
    assert RC.area_findings(page, tf, [room], "L-2") == []


def test_only_paired_drawn_lines_are_wall_faces():
    face = [((0, 0), (5, 0)), ((0, 0.2), (5, 0.2))]                     # a 20 cm wall: two faces
    tread = [((10, 0), (11, 1))]                                         # a lone line: a spiral tread
    assert RC.paired(face + tread) == face


def test_missing_drawn_walls_and_walls_on_no_drawn_line():
    segs = [((0, 0), (6, 0)), ((0, 0.2), (6, 0.2)),                    # wall 1, built
            ((0, 5), (6, 5)), ((0, 5.2), (6, 5.2))]                    # wall 2, not built
    walls = [{"id": "w1", "start": [0, 0.1], "end": [6, 0.1], "thickness": 0.2},
             {"id": "w9", "start": [10, 0], "end": [10, 4], "thickness": 0.2}]   # on no drawn line
    out = RC.wall_findings(segs, walls, "L0")
    rc4 = [f for f in out if f["check"] == "RC4"]
    rc5 = [f for f in out if f["check"] == "RC5"]
    assert rc4 and rc4[0]["missing_m"] == pytest.approx(12.0, abs=0.1)
    assert [f["wall_id"] for f in rc5] == ["w9"]


def test_the_regression_compare_flags_regressions_and_lets_improvements_pass():
    base = {"status": "ok", "levels": ["L0", "L1"], "levels_left_out": ["L-2"],
            "per_level": {"L0": {"rooms": 20, "walls": 100, "doors": 10, "windows": 8, "openings": 2, "room_area": 200.0}},
            "check": {"verdict": "ready", "counts": {"critical": 0}, "stacking": {}}}
    better = dict(base, levels=["L-2", "L0", "L1"], levels_left_out=[])
    assert RG.compare(base, better) == []
    worse = dict(base, status="needs_review",
                 per_level={"L0": dict(base["per_level"]["L0"], rooms=12, room_area=150.0)},
                 check={"verdict": "fix before a pod run", "counts": {"critical": 1}, "stacking": {"L1": 1.2}})
    diffs = RG.compare(base, worse)
    assert any("status" in d for d in diffs) and any("rooms: 20 -> 12" in d for d in diffs)
    assert any("room area" in d for d in diffs) and any("verdict" in d for d in diffs)
    assert any("stacking offset" in d for d in diffs) and any("critical findings" in d for d in diffs)
