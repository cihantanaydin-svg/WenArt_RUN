"""``python -m wenart.run plan``: the time rule, the pod split and the golden plan of the committed projects
(docs/milestone6.md §2.1, §4.1, §8.1; docs/milestone7.md §9.3: GPU_SPEED, ``--gpu``, recognition calls, the
pending status, the §6.2 view rule, the window pull)."""
from __future__ import annotations

import json

import pytest

from wenart.run import plan as P
from wenart.run.__main__ import main as run_main
from wenart.run.projects import REPO_ROOT, project_folder

# synthetic-02 is a raster project since M7 (area S): its plan status is not pinned here.
GOLDEN = ["synthetic-01", "synthetic-03", "synthetic-04", "synthetic-05", "synthetic-06", "real01", "review-01"]
PRESENT = [p for p in GOLDEN if project_folder(p, REPO_ROOT).is_dir()]
GPU = "RTX PRO 6000"


def square(side, **kw):
    return dict({"polygon": [[0, 0], [side, 0], [side, side], [0, side]]}, **kw)


def test_views_per_room_by_area():
    assert [P.views_for_area(a) for a in (2.99, 3.0, 5.99, 6.0, 40.0, 0)] == [1, 2, 2, 3, 3, 1]
    # The polygon area decides (camsearch.room_view_count), not the label's area_computed; rooms the layout
    # furnishes and rooms with furniture by area, a room that stays empty 1 view, none below 2.5 m² (M7 §6.2).
    rooms = [square(20 ** 0.5, id="a"), square(4.96 ** 0.5, id="b"), square(2.8 ** 0.5, id="c"),
             square(2.0 ** 0.5, id="d"), square(1.0, id="e", area_computed=20.0)]
    furniture = [{"id": "f1", "room_id": "b", "type": "sofa"}, {"id": "f2", "room_id": "c", "type": "chair"},
                 {"id": "f3", "room_id": "d", "type": "chair", "build": False},
                 {"id": "f4", "room_id": "e", "type": "potted_plant", "kind": "decor"}]
    building = {"rooms": rooms, "furniture": furniture}
    assert P.building_views(building, ai_rooms=[rooms[0]]) == 3 + 2 + 1 + 0 + 0
    assert P.building_views(building) == 1 + 2 + 1 + 0 + 0
    assert P.building_views({"rooms": [square(1.0, id="x", area_computed=20.0)]}, [{"id": "x"}]) == 1


def test_time_rule_and_server_starts():
    assert P.project_minutes(29, 7) == pytest.approx(4 + (0.63 + 1 / 60) * 29 + 7 / 6, abs=0.01)
    assert P.project_minutes(29, 7, recognition=1.5, speed=2.0) == pytest.approx(
        (4 + (0.63 + 1 / 60) * 29 + 7 / 6 + 1.5) / 2, abs=0.01)
    assert P.project_minutes(None, 0) == 4.0                          # views unknown (a raster page before answers)
    assert P.recognition_minutes({"qwen": 17, "glm": 17}, {"qwen": 8, "glm": 2}) == pytest.approx(
        (17 * 4.4 / 8 + 17 * 4.4 / 2) / 60)
    assert P.server_starts(True, True) == 4 and P.server_starts(False, True) == 3 and P.server_starts(False, False) == 2
    assert P.server_starts(False, False, questions=True) == 4 and P.server_starts(False, True, True) == 4
    assert {n: P.fixed_minutes(n) for n in (2, 3, 4)} == {2: 14.5, 3: 19.0, 4: 21.3}
    assert {n: P.limit_minutes(n) for n in (2, 3, 4)} == {2: 77.5, 3: 73.0, 4: 70.7}   # §2.1: <= 73 / <= 71


def test_gpu_speed_table_and_default_gpu(tmp_path, monkeypatch):
    assert P.GPU_SPEED["RTX PRO 4500"] == 1.0 and P.GPU_SPEED["RTX 4090"] == 1.1
    assert P.default_gpu() == "RTX PRO 6000"                         # GPU_PRIORITY[0] of scripts/gpu_run.py
    fake = tmp_path / "gpu_run.py"
    fake.write_text("import urllib.request\nGPU_PRIORITY = ['RTX 4090', 'L40S']\nraise SystemExit(1)\n")
    assert P.default_gpu(fake) == "RTX 4090"                          # read with ast, never run
    assert P.default_gpu(tmp_path / "missing.py") == "RTX PRO 4500"
    assert P.gpu_speed("RTX PRO 6000") == {"name": "RTX PRO 6000", "speed": 1.0, "matched": None}
    monkeypatch.setitem(P.GPU_SPEED, "RTX PRO 6000", 1.9)
    assert P.gpu_speed("NVIDIA RTX PRO 6000 Blackwell Server Edition")["speed"] == 1.9
    assert P.gpu_speed("rtx pro 6000 wk")["matched"] == "RTX PRO 6000"
    plan = P.gpu_plan("RTX PRO 6000", {"qwen": {"max_seqs": 8}, "glm": {"max_seqs": 4}})
    assert plan["memory_mib"] == 96 * 1024 and plan["seqs"] == {"qwen": 8, "glm": 4} and plan["speed"] == 1.9
    assert P.gpu_plan("RTX PRO 4500", {"qwen": {}})["seqs"] == {"qwen": 2}
    assert P.gpu_plan("H100 SXM", {"qwen": {}})["seqs"] == {"qwen": 2}  # no VRAM in the table: the safe size


def test_first_fit_split():
    def p(name, minutes, starts=3, status="ok", verified=True):
        return {"project": name, "minutes": minutes, "server_starts": starts, "status": status, "verified": verified}

    pods = P.split([p("a", 40), p("b", 30), p("x", 0, 0, "needs_review"), p("c", 20), p("d", 3)])
    assert [pod["projects"] for pod in pods] == [["a", "b", "d"], ["c"]]
    assert pods[0]["project_minutes"] == 73 and pods[0]["fits"] and pods[0]["job_minutes"] == 92.0
    assert all(pod["verified"] for pod in pods)
    # A project with uncached photos turns its pod into a 4-start pod with a lower limit.
    pods = P.split([p("a", 50), p("ph", 21, 4)])
    assert [pod["projects"] for pod in pods] == [["a"], ["ph"]] and pods[1]["server_starts"] == 4
    pods = P.split([p("a", 50), p("ph", 20, 4)])
    assert [pod["projects"] for pod in pods] == [["a", "ph"]] and pods[0]["limit_minutes"] == 70.7
    # A project larger than one pod gets a pod of its own that does not fit (deadline cut, resume).
    pods = P.split([p("big", 90)])
    assert pods[0]["fits"] is False
    # A pending project (questions, pre-answer building) gets pod time; its pod is not verified.
    pods = P.split([p("a", 30), p("q", 20, 4, "pending", False)])
    assert [pod["projects"] for pod in pods] == [["a", "q"]] and pods[0]["verified"] is False


@pytest.fixture(scope="module")
def golden(tmp_path_factory):
    out = tmp_path_factory.mktemp("plan_outputs")
    plan = P.make_plan(PRESENT, outputs=out, gpu=GPU)
    return out, plan


def test_golden_plan_of_the_committed_projects(golden):
    out, plan = golden
    by = {e["project"]: e for e in plan["projects"]}
    assert plan["gpu"]["name"] == GPU and plan["gpu"]["memory_mib"] == 96 * 1024
    s1, s3 = by["synthetic-01"], by["synthetic-03"]
    assert (s1["status"], s1["levels"], s1["rooms"], s1["empty_rooms"], s1["views"]) == ("ok", 2, 10, 7, 29)
    assert s1["minutes"] == P.project_minutes(29, 7) == 23.92 and s1["server_starts"] == 3 and s1["photos"] == 0
    # §6.2: rooms that stay without furniture (a bath, a hall) get one view before the layout too.
    assert (s3["status"], s3["levels"], s3["rooms"], s3["empty_rooms"], s3["views"]) == ("ok", 3, 19, 11, 44)
    assert s3["minutes"] == P.project_minutes(44, 11) and s3["server_starts"] == 3
    if "synthetic-04" in by:
        s4 = by["synthetic-04"]
        assert (s4["status"], s4["views"], s4["empty_rooms"]) == ("ok", 14, 2)
        assert s4["minutes"] == P.project_minutes(14, 2) and s4["server_starts"] == 3
    if "synthetic-05" in by:
        s5 = by["synthetic-05"]
        assert (s5["status"], s5["views"], s5["empty_rooms"], s5["photos"]) == ("ok", 25, 3, 1)
        assert s5["server_starts"] == 4 and s5["photos_cached"] is False
    if "synthetic-06" in by:                                          # the DWG project (read through its DXF here
        s6 = by["synthetic-06"]                                       # only when LibreDWG is installed)
        assert s6["status"] in ("ok", "needs_review")
        if s6["status"] == "ok":
            assert (s6["levels"], s6["rooms"], s6["empty_rooms"], s6["views"]) == (1, 6, 2, 17)
            assert s6["server_starts"] == 3 and s6["questions"] is None
    r1 = by["real01"]
    # real01 writes 17 recognition questions (exit 4): pod time from the pre-answer building, both passes to ask.
    assert (r1["status"], r1["stage_status"], r1["levels"], r1["rooms"]) == ("pending", "pending", 1, 9)
    assert (r1["questions"], r1["recognition_calls"], r1["server_starts"], r1["verified"]) == (17, 34, 4, False)
    calls = P.recognition_minutes({"qwen": 17, "glm": 17}, plan["gpu"]["seqs"])
    assert r1["minutes"] == P.project_minutes(r1["views"], r1["empty_rooms"], calls)
    assert r1["views"] == 20 and r1["pod"] is not None
    rv = by["review-01"]
    assert rv["status"] == "needs_review" and rv["views"] is None and rv["minutes"] == 0.0 and rv["pod"] is None
    assert rv["report"].endswith("review-01/report.md") and (out / "review-01" / "report.md").is_file()
    assert "cannot order untitled plan pages" in (out / "review-01" / "report.md").read_text()
    pod_of_real01 = next(pod for pod in plan["pods"] if "real01" in pod["projects"])
    assert pod_of_real01["verified"] is False and pod_of_real01["server_starts"] == 4
    assert all(pod["fits"] for pod in plan["pods"])
    if PRESENT == GOLDEN and by["synthetic-06"]["status"] == "ok":
        assert [pod["projects"] for pod in plan["pods"]] == [["synthetic-01", "synthetic-03", "synthetic-04"],
                                                             ["synthetic-05", "synthetic-06", "real01"]]


def test_plan_reuses_stage_1_and_writes_records(golden):
    out, _plan = golden
    rec = json.loads((out / "synthetic-01" / "run" / "pipeline.json").read_text())
    assert rec["stage"] == "pipeline" and rec["status"] in ("ok", "reused") and rec["fingerprint"]
    again = P.make_plan(["synthetic-01", "real01"], outputs=out, gpu=GPU)
    assert json.loads((out / "synthetic-01" / "run" / "pipeline.json").read_text())["status"] == "reused"
    assert again["projects"][0]["views"] == 29
    # A reused pending pipeline stays pending (its questions still need the answers).
    assert json.loads((out / "real01" / "run" / "pipeline.json").read_text())["status"] == "pending"
    assert again["projects"][1]["status"] == "pending" and again["projects"][1]["questions"] == 17


def test_gpu_speed_and_sequences_change_the_minutes(golden, monkeypatch):
    out, plan = golden
    slow = P.make_plan(["synthetic-01", "real01"], outputs=out, gpu="RTX PRO 4500")
    assert slow["gpu"]["seqs"] == {"qwen": 2, "glm": 2}
    r_fast = next(e for e in plan["projects"] if e["project"] == "real01")
    r_slow = slow["projects"][1]
    assert r_slow["minutes"] > r_fast["minutes"]                     # 34 calls at 2 instead of 8 at once
    monkeypatch.setitem(P.GPU_SPEED, "RTX PRO 6000", 2.0)
    fast = P.make_plan(["synthetic-01"], outputs=out, gpu=GPU)
    assert fast["projects"][0]["minutes"] == round(P.project_minutes(29, 7, speed=2.0), 2) == 11.96
    assert "speed 2" in P.plan_text(fast)


def test_synthetic_02_is_planned_whatever_its_raster_status(tmp_path):
    """synthetic-02 became a raster project in M7 (area S): ok, pending (room-label questions) or needs_review; the
    plan's fields follow its status."""
    plan = P.make_plan(["synthetic-02"], outputs=tmp_path, gpu=GPU)
    e = plan["projects"][0]
    assert e["status"] in ("ok", "pending", "needs_review")
    if e["status"] == "needs_review":
        assert e["minutes"] == 0.0 and e["pod"] is None and e["report"]
    else:
        assert e["minutes"] >= P.MIN_PER_PROJECT and e["pod"] == 1


def test_plan_cli(golden, tmp_path, capsys):
    out, _plan = golden
    rc = run_main(["plan", "--projects", "synthetic-01,review-01", "--outputs", str(out), "--gpu", GPU, "--out",
                   str(tmp_path / "run_plan.json")])
    assert rc == 0
    text = capsys.readouterr().out
    assert "| synthetic-01 | ok | 2 | 10 | 7 | 29 | - | - | 23.92 | 3 | 1 |" in text
    assert "- review-01: needs_review, no pod time" in text
    assert any(line.startswith("GPU: RTX PRO 6000 (speed 1 (not measured") for line in text.splitlines())
    data = json.loads((tmp_path / "run_plan.json").read_text())
    assert data["kind"] == "run_plan" and data["schema_version"] == "0.1" and data["gpu"]["name"] == GPU
    assert run_main(["plan", "--projects", "../etc"]) == 2
