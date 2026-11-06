"""6 Nov 2026 (real21; user: "all floors needs to be done"; lesson UL331): the storeys and windows a drawing leaves out,
read end to end through the CPU pipeline on two generated projects (no project data, nothing committed).

What: the synthetic ground floor plan (``failure_projects.base_house``, titled ZEMİN KAT PLANI) with a text listing the
floors on the sheet ('Z+2': the ground floor and two above) and an 'bitişik' text beside its east wall. Without its
windows (none drawn) the reading builds three storeys (the drawn plan repeated, inferred from the title rung) and
infers the windows, none on the attached east wall; with its windows drawn (layer PENCERE) it builds the same storeys
and infers no window.
Why: the rules must fire on a drawing that needs them and stay silent where the drawing draws what they would add.
"""
from __future__ import annotations

import pytest

from wenart.synthetic import failure_classes as FC
from wenart.synthetic.failure_projects import BRIEF, base_house


def _project(name: str, windows: bool) -> FC.FailureProject:
    plan = base_house()
    if not windows:
        plan.openings = [o for o in plan.openings if o.kind != "window"]
    ox, oy = plan.origin
    notes = [FC.Prim("text", FC.L_TEXT, pts=[(ox + 12.0 + 1.2, oy + 4.5)], text="bitişik", height=0.3),
             FC.Prim("text", FC.L_TEXT, pts=[(ox + 6.0, oy - 4.0)], text="Z+2", height=0.4)]
    levels = [FC.TruthLevel("L0", "Zemin Kat", 0.0, 0, "p0")]
    return FC.FailureProject(name, "completion", "UL331", "a ground plan, a floor list and an attached side", [plan],
                             levels, BRIEF, sheet_prims=notes)


@pytest.fixture(scope="module")
def readings(tmp_path_factory):
    from wenart.ingest import pipeline as PL

    root = tmp_path_factory.mktemp("completion")
    out = {}
    for name, windows in (("synthetic-completion-nowin", False), ("synthetic-completion-win", True)):
        FC.generate_failure_project(_project(name, windows), root)
        building, _build = PL.run_project(root / name, root / f"{name}-out", no_ai=True)
        out[windows] = building
    return out


def test_a_floor_list_on_the_sheet_builds_the_storeys_the_drawing_does_not_draw(readings):
    for b in readings.values():
        assert [lv["id"] for lv in b["levels"]] == ["L0", "L1", "L2"]
        st = b["level_inference"]["storeys"]
        assert st["rule"] == "title" and st["count"] == 3 and st["guess"] is False
        assert [lv.get("storey_inference", {}).get("rule") for lv in b["levels"]] == [None, "title", "title"]
        assert b["roof"] is not None and b["roof"]["over_level_id"] == "L2"


def test_a_plan_without_windows_gets_inferred_windows_but_none_on_the_attached_side(readings):
    b = readings[False]
    wins = [o for o in b["openings"] if o["type"] == "window"]
    assert wins and all(o.get("inferred") for o in wins)
    assert {o["level_id"] for o in wins} == {"L0", "L1", "L2"}
    party = {w["id"] for w in b["walls"] if w.get("party_wall")}
    assert party, "the 'bitişik' text names the east wall as a party wall"
    assert not [o for o in b["openings"] if o["wall_id"] in party]
    rec = b["level_inference"]["windows"]["levels"]["L0"]
    assert rec["drawing"]["draws_windows"] is False and rec["inferred"]


def test_a_plan_that_draws_windows_gets_no_inferred_window(readings):
    b = readings[True]
    wins = [o for o in b["openings"] if o["type"] == "window"]
    assert wins and not [o for o in b["openings"] if o.get("inferred")]
    assert b["level_inference"]["windows"]["levels"]["L0"]["drawing"]["draws_windows"] is True
