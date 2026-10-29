"""29 Oct 2026 (user on real06 run 20261028-154514-full: "If there is a window here it needs to alight with the
stairs"; lesson UL104): the windows behind a stair's winders are set to the stair (architect W6, Argus U28; CPU)."""
import json
from pathlib import Path

import pytest

from wenart.audit import lessons as L
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as AR

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_stair_windows_20261029.json"   # run 154514, trimmed


@pytest.fixture(scope="module")
def real06():
    return json.loads(REAL06.read_text(encoding="utf-8"))


def test_the_windows_behind_the_winders_and_over_the_stair_opening(real06):
    found = {f["window"]: f for f in AR.stair_window_findings(AA.Plan(real06))}
    cut = [f for f in found.values() if f["kind"] == "cut"]
    high = [f for f in found.values() if f["kind"] == "high"]
    assert cut and all(f["sill"] is None and f["upper"] for f in cut)        # no room to rise: closed, lit from above
    assert high and all(f["sill"] == pytest.approx(AR.STAIR_WINDOW["low_sill_m"]) for f in high)
    w6 = AR.stair_windows_rule(AA.Plan(real06))[0]
    defaults = {a["element"]: a.get("default") for a in w6["answers"] if a.get("open")}
    assert {defaults[f["window"]] for f in cut} == {"close_stair_window"}
    assert {defaults[f["window"]].split(":")[0] for f in high} == {"stair_window"}
    assert {f["target"] for f in L.stair_windows(real06)} == set(found)


def test_the_actions_set_a_window_to_the_stair(real06):
    plan = AA.Plan(json.loads(json.dumps(real06)))
    f = next(f for f in AR.stair_window_findings(plan) if f["kind"] == "high")
    ok, text = AA.act_stair_window(plan, f"W6:{f['window']}", {"by": "architect"}, f["window"], f["sill"],
                                   f["height"], f["why"])
    o = plan.openings[f["window"]]
    assert ok and o["sill_height"] == pytest.approx(f["sill"]) and "sill 0.90 -> 0.30 m" in text
    assert o["adjusted_by_ai"]["answer_key"] == f"W6:{f['window']}"
    assert not AA.act_stair_window(plan, "k", {}, f["window"], 2.5, 1.2)[0]            # over its head limit
    c = next(f for f in AR.stair_window_findings(plan) if f["kind"] == "cut")
    ok, _ = AA.act_close_stair_window(plan, f"W6:{c['window']}", {"by": "architect"}, c["window"], c["why"])
    assert ok and c["window"] not in plan.openings
    assert any(x["id"] == c["window"] for x in plan.b["openings_closed"])
