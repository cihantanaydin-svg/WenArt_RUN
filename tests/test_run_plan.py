"""``python -m wenart.run plan``: the time rule, the pod split and the golden plan of the synthetic projects
(docs/milestone6.md §2.1, §4.1, §8.1)."""
from __future__ import annotations

import json

import pytest

from wenart.run import plan as P
from wenart.run.__main__ import main as run_main
from wenart.run.projects import REPO_ROOT

ALL = ["synthetic-01", "synthetic-02", "synthetic-03", "synthetic-04", "synthetic-05"]
PRESENT = [p for p in ALL if (REPO_ROOT / "projects" / p).is_dir()]


def test_views_per_room_by_area():
    assert [P.views_for_area(a) for a in (2.99, 3.0, 5.99, 6.0, 40.0, 0)] == [1, 2, 2, 3, 3, 1]
    square = lambda s: {"polygon": [[0, 0], [s, 0], [s, s], [0, s]]}  # noqa: E731
    # The polygon area decides (camsearch.room_view_count), not the label's area_computed.
    rooms = [square(20 ** 0.5), square(4.96 ** 0.5), square(2.8 ** 0.5)]
    assert P.building_views({"rooms": rooms}) == 6
    assert P.building_views({"rooms": [dict(square(1.0), area_computed=20.0)]}) == 1


def test_time_rule_and_server_starts():
    assert P.project_minutes(29, 7) == pytest.approx(4 + 0.63 * 29 + 7 / 6, abs=0.01)
    assert P.server_starts(True, True) == 4 and P.server_starts(False, True) == 3 and P.server_starts(False, False) == 2
    assert {n: P.fixed_minutes(n) for n in (2, 3, 4)} == {2: 14.5, 3: 19.0, 4: 21.3}
    assert {n: P.limit_minutes(n) for n in (2, 3, 4)} == {2: 77.5, 3: 73.0, 4: 70.7}   # §2.1: <= 73 / <= 71


def test_first_fit_split():
    def p(name, minutes, starts=3, status="ok"):
        return {"project": name, "minutes": minutes, "server_starts": starts, "status": status}

    pods = P.split([p("a", 40), p("b", 30), p("x", 0, 0, "needs_review"), p("c", 20), p("d", 3)])
    assert [pod["projects"] for pod in pods] == [["a", "b", "d"], ["c"]]
    assert pods[0]["project_minutes"] == 73 and pods[0]["fits"] and pods[0]["job_minutes"] == 92.0
    # A project with uncached photos turns its pod into a 4-start pod with a lower limit.
    pods = P.split([p("a", 50), p("ph", 21, 4)])
    assert [pod["projects"] for pod in pods] == [["a"], ["ph"]] and pods[1]["server_starts"] == 4
    pods = P.split([p("a", 50), p("ph", 20, 4)])
    assert [pod["projects"] for pod in pods] == [["a", "ph"]] and pods[0]["limit_minutes"] == 70.7
    # A project larger than one pod gets a pod of its own that does not fit (deadline cut, resume).
    pods = P.split([p("big", 90)])
    assert pods[0]["fits"] is False


@pytest.fixture(scope="module")
def golden(tmp_path_factory):
    out = tmp_path_factory.mktemp("plan_outputs")
    plan = P.make_plan(PRESENT, outputs=out)
    return out, plan


def test_golden_plan_of_the_synthetic_projects(golden):
    out, plan = golden
    by = {e["project"]: e for e in plan["projects"]}
    s1, s2, s3 = by["synthetic-01"], by["synthetic-02"], by["synthetic-03"]
    assert (s1["status"], s1["levels"], s1["rooms"], s1["empty_rooms"], s1["views"]) == ("ok", 2, 10, 7, 29)
    assert s1["minutes"] == 23.44 and s1["server_starts"] == 3 and s1["photos"] == 0
    assert (s3["status"], s3["levels"], s3["rooms"], s3["empty_rooms"], s3["views"]) == ("ok", 3, 19, 11, 50)
    assert s3["minutes"] == 37.33 and s3["server_starts"] == 3
    assert s2["status"] == "needs_review" and s2["views"] is None and s2["minutes"] == 0.0 and s2["pod"] is None
    assert s2["report"].endswith("synthetic-02/report.md") and (out / "synthetic-02" / "report.md").is_file()
    assert by["synthetic-01"]["pod"] == by["synthetic-03"]["pod"] == 1
    pod1 = plan["pods"][0]
    assert pod1["projects"][:2] == ["synthetic-01", "synthetic-03"] and pod1["project_minutes"] >= 60.77
    if "synthetic-04" in by:
        s4 = by["synthetic-04"]
        assert (s4["status"], s4["views"], s4["empty_rooms"]) == ("ok", 14, 2)
        assert s4["minutes"] == P.project_minutes(14, 2) and s4["server_starts"] == 3
    if "synthetic-05" in by:
        s5 = by["synthetic-05"]
        assert (s5["status"], s5["views"], s5["empty_rooms"], s5["photos"]) == ("ok", 25, 3, 1)
        assert s5["server_starts"] == 4 and s5["photos_cached"] is False
    if PRESENT == ALL:
        assert [pod["projects"] for pod in plan["pods"]] == [["synthetic-01", "synthetic-03"],
                                                             ["synthetic-04", "synthetic-05"]]
        assert plan["pods"][1]["server_starts"] == 4 and all(pod["fits"] for pod in plan["pods"])


def test_plan_reuses_stage_1_and_writes_records(golden):
    out, _plan = golden
    rec = json.loads((out / "synthetic-01" / "run" / "pipeline.json").read_text())
    assert rec["stage"] == "pipeline" and rec["status"] in ("ok", "reused") and rec["fingerprint"]
    again = P.make_plan(["synthetic-01"], outputs=out)
    assert json.loads((out / "synthetic-01" / "run" / "pipeline.json").read_text())["status"] == "reused"
    assert again["projects"][0]["views"] == 29


def test_plan_cli(golden, tmp_path, capsys):
    out, _plan = golden
    rc = run_main(["plan", "--projects", "synthetic-01,synthetic-02", "--outputs", str(out), "--out",
                   str(tmp_path / "run_plan.json")])
    assert rc == 0
    text = capsys.readouterr().out
    assert "| synthetic-01 | ok | 2 | 10 | 7 | 29 | - | 23.44 | 3 | 1 |" in text
    assert "- synthetic-02: needs_review, no pod time" in text
    data = json.loads((tmp_path / "run_plan.json").read_text())
    assert data["kind"] == "run_plan" and data["schema_version"] == "0.1"
    assert run_main(["plan", "--projects", "../etc"]) == 2
