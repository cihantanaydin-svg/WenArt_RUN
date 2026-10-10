"""Milestone 12 P1, the agent model bake-off (docs/milestone12.md §5.1, §13.3; ``wenart.agent.bakeoff``), on the CPU.

- the models of ``check.yaml models.bakeoff`` are the contract's ids and revisions; 2-GPU ones say so; the
  variants become client options (``model.from_check_yaml``); the setup downloads dotted keys;
- the task set: 40 / 30 / 20 / 20 / 20 items, hand labels with reasons, every image there;
- the code checks of the planted problems on a toy room (bed turned, nightstand at the foot, TV away, chair away)
  and a door blocked in a committed building; a plant adds exactly its problem;
- scoring per task, the T1-T4 score, the decision rule (a 2-GPU model only >= 10 points better);
- a variant run with a scripted model: requests at temperature 0 with strict schemas, at most 4 images, the T5
  plan + tool calls judged (valid, allowed, in the plan), the time cap;
- the summary files and the job script.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from wenart.agent import bakeoff as BO
from wenart.agent import model as M
from wenart.run import servers as SV

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "scripts" / "jobs" / "bakeoff_m12.sh"


@pytest.fixture(scope="module")
def items():
    return BO.load_items()


# --------------------------------------------------------------------------
# Models
# --------------------------------------------------------------------------

def test_the_bakeoff_models_are_the_contract_ones():
    text = (ROOT / "docs" / "milestone12.md").read_text(encoding="utf-8")
    part = text[text.index("- Bake-off (A):"):text.index("- Runner (lead):")]
    want = set(re.findall(r"`([\w.-]+/[\w.-]+)`\s*@([0-9a-f]{40})", part))
    table = SV.check_models()["bakeoff"]
    have = {(m["id"], m["revision"]) for m in table.values()}
    assert len(want) == 5 and have == want
    assert {k for k, m in table.items() if int(m.get("gpus") or 1) == 2} == {"flash_next", "step_flash"}
    for m in table.values():
        assert m["variants"] and m["max_seqs"] == 8 and m["limit_mm"] == 4
        assert "--max-model-len 32768" in m["server_flags"] and "--tool-call-parser" in m["server_flags"]
    lines = BO.models_lines()
    assert [ln.split()[1] for ln in lines] == [f"bakeoff.{k}" for k in table]


def test_a_variant_is_a_client_setting():
    fp8_on = M.from_check_yaml("http://x/v1", "bakeoff.fp8", variant="on")
    assert fp8_on.critic_thinking and fp8_on.planner_thinking and fp8_on.model == "Qwen/Qwen3.8-27B-FP8"
    assert not M.from_check_yaml("http://x/v1", "bakeoff.fp8", variant="off").critic_thinking
    muse = M.from_check_yaml("http://x/v1", "bakeoff.muse", variant="low")
    assert muse.extra_template == {"reasoning_strength": "low"} and not muse.critic_thinking
    body = M.critic_body(muse.model, [], {"type": "object"}, thinking=False, extra_template=muse.extra_template)
    assert body["chat_template_kwargs"]["reasoning_strength"] == "low" and body["temperature"] == 0.0
    with pytest.raises(KeyError):
        M.from_check_yaml("http://x/v1", "bakeoff.nope")


def test_the_setup_downloads_dotted_keys(tmp_path):
    env = dict(os.environ, WENART_WS=str(tmp_path / "ws"), WENART_FAST=str(tmp_path / "fast"),
               WENART_PY=sys.executable, POLISH_SETUP_PLAN_ONLY="1", POLISH_PHASES="check",
               AGENT_MODELS="bakeoff.fp8 bakeoff.flash_next")
    env.pop("CHECK_MODELS", None)
    proc = subprocess.run(["bash", str(ROOT / "scripts" / "pod_setup_polish.sh")], capture_output=True, text=True,
                          env=env, timeout=60)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    line = next(ln for ln in proc.stdout.splitlines() if ln.startswith("PLAN BAKEOFF_MODELS="))
    table = SV.check_models()["bakeoff"]
    for k in ("fp8", "flash_next"):
        assert f"{table[k]['id']}@{table[k]['revision']}" in line


# --------------------------------------------------------------------------
# The task set
# --------------------------------------------------------------------------

def test_the_task_set(items):
    its, folder = items
    counts = {t: sum(1 for i in its if i["task"] == t) for t in BO.TASKS}
    assert counts == {"T1": 40, "T2": 30, "T3": 20, "T4": 20, "T5": 20}
    choices = set(BO.t1_choices())
    for it in its:
        for ref in it["images"]:
            assert BO.image_path(ref, folder).is_file(), ref
        if it["task"] == "T1":
            assert set(it["truth"]) <= choices and len(it["why"]) > 8 and len(it["images"]) == 1
        if it["task"] == "T2":
            assert all(p[0] in BO.PROBLEMS for p in it["truth"]) and set(map(tuple, it["planted"])) <= \
                set(map(tuple, it["truth"]))
        if it["task"] == "T3":
            assert len(it["images"]) == 3 and it["truth"] in (1, 2, 3)
            assert it["layouts"][it["truth"] - 1]["planted"] == []
            assert all(lay["planted"] for k, lay in enumerate(it["layouts"], 1) if k != it["truth"])
        if it["task"] == "T4":
            assert set(it["truth"]) == {"floating_or_sunk_decor", "wrong_object"}
            assert any(v is not None for v in it["truth"].values()) and it["why"]
        if it["task"] == "T5":
            assert it["brief"]["findings"]["fixable"] and it["offered"] and it["default_checklist"]
    t2 = [i for i in its if i["task"] == "T2"]
    planted = {p[0] for i in t2 for p in i["planted"]}
    assert planted == set(BO.PROBLEMS)                              # every problem kind is planted somewhere
    assert any(not i["truth"] for i in t2)                          # and some rooms have none
    t4 = [i for i in its if i["task"] == "T4"]
    for key in ("floating_or_sunk_decor", "wrong_object"):
        values = [i["truth"][key] for i in t4]
        assert True in values and False in values


# --------------------------------------------------------------------------
# The code checks of the planted problems
# --------------------------------------------------------------------------

def _p(pid, ptype, center, size, rot, room="r1"):
    return {"id": pid, "type": ptype, "room_id": room, "level_id": "L0", "source": "from_documents",
            "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot}}


def toy() -> dict:
    """Three 4 x 4 m rooms: a bedroom (bed head on the top wall, two nightstands), a living room (sofa and TV unit
    facing each other) and a study (a desk on the top wall, its chair facing it). Front = rotation - 90."""
    rooms = [{"id": rid, "level_id": "L0", "label": rid, "room_type": "bedroom",
              "polygon": [[x0, 0], [x0 + 4, 0], [x0 + 4, 4], [x0, 4]]} for rid, x0 in (("r1", 0), ("r2", 5),
                                                                                       ("r3", 10))]
    furniture = [_p("bed", "bed_double", (2, 3), (1.6, 2.0), 0), _p("n1", "nightstand", (0.9, 3.75), (0.4, 0.4), 0),
                 _p("n2", "nightstand", (3.1, 3.75), (0.4, 0.4), 0),
                 _p("sofa", "sofa", (7, 0.5), (2.0, 0.9), 180, "r2"),
                 _p("tv", "tv_unit", (7, 3.8), (1.6, 0.4), 0, "r2"),
                 _p("desk", "desk", (11, 3.7), (1.2, 0.6), 0, "r3"),
                 _p("ch", "chair", (11, 3.0), (0.5, 0.5), 180, "r3")]
    return {"levels": [{"id": "L0", "elevation": 0.0}], "rooms": rooms, "walls": [], "openings": [],
            "furniture": furniture}


def test_the_code_checks_of_the_planted_problems():
    b = toy()
    assert [BO.problems_of(b, r) for r in ("r1", "r2", "r3")] == [[], [], []]
    bed = next(f for f in b["furniture"] if f["id"] == "bed")
    turned = BO.with_piece(b, BO.turned(bed))
    # A reversed bed is the error, not its nightstands (they stay at the wall end).
    assert BO.problems_of(turned, "r1") == [("bed_reversed", "bed")]
    n1 = next(f for f in b["furniture"] if f["id"] == "n1")
    t = BO.along(bed, BO.center(n1))
    assert t < 0
    at_foot = BO.with_piece(b, BO.moved(n1, (0.9, 3.75 + 2 * t)))
    assert BO.problems_of(at_foot, "r1") == [("nightstand_at_foot", "n1")]
    tv = next(f for f in b["furniture"] if f["id"] == "tv")
    assert BO.problems_of(BO.with_piece(b, BO.turned(tv)), "r2") == [("tv_away", "tv")]
    ch = next(f for f in b["furniture"] if f["id"] == "ch")
    assert BO.problems_of(BO.with_piece(b, BO.turned(ch)), "r3") == [("chair_away", "ch")]
    opts = {(p, pid) for p, pid, _piece in BO.plant_options(b, "r1")}
    assert ("bed_reversed", "bed") in opts and ("nightstand_at_foot", "n1") in opts


def test_a_plant_adds_exactly_its_problem_in_a_committed_building():
    b = BO.building_of("synthetic-04")
    kinds = set()
    for room in b["rooms"]:
        base = set(BO.problems_of(b, room["id"]))
        for problem, pid, piece in BO.plant_options(b, room["id"]):
            after = set(BO.problems_of(BO.with_piece(b, piece), room["id"]))
            assert after - base == {(problem, pid)} and base <= after
            kinds.add(problem)
    assert "door_blocked" in kinds and "chair_away" in kinds


def test_rooms_are_picked_in_a_seeded_order():
    pool = [("p1", f"r{i}") for i in range(10)] + [("p2", f"r{i}") for i in range(3)]
    a = BO.pick_rooms(pool, 6, 12, per_project=4)
    assert a == BO.pick_rooms(pool, 6, 12, per_project=4) and len(a) == 6
    assert sum(1 for p, _r in a if p == "p1") <= 4
    avoid = tuple(a)
    b = BO.pick_rooms(pool, 3, 12, per_project=10, avoid=avoid)
    assert not set(b) & set(avoid)


# --------------------------------------------------------------------------
# Scoring and the decision rule
# --------------------------------------------------------------------------

def test_scoring_per_task():
    t1 = {"task": "T1", "truth": ["chair", "office_chair"]}
    assert BO.score_item(t1, {"type": "office_chair"})["score"] == 1.0
    assert BO.score_item(t1, None)["score"] == 0.0
    t2 = {"task": "T2", "truth": [["bed_reversed", "f1"], ["door_blocked", "f2"]]}
    s = BO.score_item(t2, {"errors": [{"problem": "bed_reversed", "piece_id": "f1"},
                                      {"problem": "tv_away", "piece_id": "f3"}]})
    assert (s["hit"], s["missed"], s["false"], s["score"]) == (1, 1, 1, round(1 / 3, 4))
    assert BO.score_item({"task": "T2", "truth": []}, {"errors": []})["score"] == 1.0
    assert BO.score_item({"task": "T2", "truth": []}, None)["score"] == 0.0
    assert BO.score_item({"task": "T3", "truth": 2}, {"best": 2})["score"] == 1.0
    t4 = {"task": "T4", "truth": {"floating_or_sunk_decor": True, "wrong_object": None}}
    s = BO.score_item(t4, {"floating_or_sunk_decor": True, "wrong_object": True})
    assert (s["score"], s["scored"], s["false"]) == (1.0, 1, 0)
    t4b = {"task": "T4", "truth": {"floating_or_sunk_decor": False, "wrong_object": False}}
    assert BO.score_item(t4b, {"floating_or_sunk_decor": True, "wrong_object": False})["false"] == 1
    calls = [{"valid": True, "allowed": True, "edit": True, "in_plan": True},
             {"valid": True, "allowed": True, "edit": False, "in_plan": False},
             {"valid": True, "allowed": False, "edit": True, "in_plan": True},
             {"valid": False, "allowed": False, "edit": False, "in_plan": False}]
    s = BO.score_item({"task": "T5"}, {"calls": calls, "plan_ok": True})
    assert (s["score"], s["valid"], s["allowed"], s["edits"], s["in_plan"]) == (0.5, 3, 2, 2, 2)


def row(name, variant, gpus, combined, valid=1.0, answered=1.0, s=2.0):
    return {"name": name, "variant": variant, "model": f"m/{name}", "gpus": gpus, "combined": combined,
            "T5_valid": valid, "answered": answered, "s_per_call": s}


def test_the_decision_rule():
    rows = [row("fp8", "off", 1, 70.0), row("muse", "high", 1, 72.0, s=9.0), row("flash", "on", 2, 81.9)]
    d = BO.decide(rows)
    assert d["pick"]["name"] == "muse" and "less than 10 points" in d["why"]
    rows[-1]["combined"] = 82.0
    assert BO.decide(rows)["pick"]["name"] == "flash"
    # within 1 point: the faster one; a model with bad tool calls or too few answers never wins
    rows = [row("fp8", "off", 1, 71.5, s=2.0), row("muse", "high", 1, 72.0, s=9.0),
            row("bf16", "on", 1, 90.0, valid=0.5), row("x", "on", 1, 95.0, answered=0.8)]
    d = BO.decide(rows)
    assert d["pick"]["name"] == "fp8" and set(d["not_eligible"]) == {"bf16 on", "x on"}
    assert BO.decide([row("flash", "on", 2, 60.0)])["pick"]["name"] == "flash"
    assert BO.decide([])["pick"] is None


# --------------------------------------------------------------------------
# A variant with a scripted model
# --------------------------------------------------------------------------

def _first(items, task):
    return next(i for i in items[0] if i["task"] == task)


def _t5_call(item):
    step = item["default_checklist"][0]
    if step["tool"] == "set_front":
        args = {"piece_id": step["target"], "front_deg": 90, "reason": "turn it to face its group"}
    else:
        args = {"piece_id": step["target"], "center": [1.0, 1.0], "reason": "move it out of the way"}
    return {"name": step["tool"], "arguments": args}


def test_every_task_through_a_scripted_model(items):
    its, folder = items
    one = {t: _first(items, t) for t in BO.TASKS}
    t2_truth = [{"problem": p, "piece_id": pid} for p, pid in one["T2"]["truth"]]
    model = M.MockModel(
        critic=[lambda body: {"type": one["T1"]["truth"][0], "why": "a seat at the desk"}],
        plan=[{"room_id": one["T5"]["room_id"], "program": {"keep": True, "choices": []},
               "steps": [dict(one["T5"]["default_checklist"][0])], "skip": []}],
        chat=[{"tool_calls": [_t5_call(one["T5"]), {"name": "no_such_tool", "arguments": {}}]}])
    from wenart.agent import tools as TL
    registry = TL.build_registry()
    r5 = BO.answer_item(model, one["T5"], folder, registry)
    assert r5["error"] is None and r5["answer"]["plan_ok"], r5["answer"]
    first, bad = r5["answer"]["calls"]
    assert first["valid"] and first["edit"] and first["in_plan"] and first["allowed"], first
    assert not bad["valid"] and r5["score"]["score"] == 0.5
    r1 = BO.answer_item(model, one["T1"], folder, registry)
    assert r1["score"]["correct"] and r1["call_seconds"]
    for task, answer in (("T2", {"errors": t2_truth}), ("T3", {"best": one["T3"]["truth"], "why": "fewest"}),
                         ("T4", {"floating_or_sunk_decor": bool(one["T4"]["truth"]["floating_or_sunk_decor"]),
                                 "wrong_object": bool(one["T4"]["truth"]["wrong_object"]), "notes": "seen"})):
        model.critic_script.append(answer)
        res = BO.answer_item(model, one[task], folder, registry)
        assert res["error"] is None and res["score"]["score"] == 1.0, (task, res)
    for body in model.requests:
        assert body["temperature"] == 0.0
        if "response_format" in body:
            assert body["response_format"]["json_schema"]["strict"] is True
        n = sum(1 for m in body["messages"] if isinstance(m.get("content"), list)
                for part in m["content"] if part.get("type") == "image_url")
        assert n <= M.MAX_IMAGES
    t3 = next(b for b in model.requests if (b.get("response_format") or {}).get("json_schema", {}).get("name") == "t3")
    assert sum(1 for part in t3["messages"][1]["content"] if part.get("type") == "image_url") == 3


def test_a_variant_respects_its_time_cap(items):
    its, folder = items
    sub = [_first(items, t) for t in ("T1", "T2", "T3", "T4")]
    ticks = iter([0.0, 0.0, 1.0, 2000.0, 2000.0, 2000.0, 2000.0, 2000.0])
    model = M.MockModel(critic=[{"type": "chair", "why": "x"}])
    res = BO.run_variant(model, sub, folder, workers=1, cap_s=100.0, clock=lambda: next(ticks))
    statuses = [res["results"][i["id"]].get("status") for i in sub]
    assert statuses[0] is None and statuses[1:] == ["skipped"] * 3
    assert res["metrics"]["T2"]["run"] == 0 and res["metrics"]["combined"] is not None
    assert [i["task"] for i in BO.run_order(its)[:22]] == ["T5"] * 20 + ["T1", "T2"]


def test_the_summary_and_its_files(tmp_path):
    def record(name, variant, gpus, acc):
        metrics = {t: {"items": 10, "run": 10, "answered": 10, "accuracy": acc} for t in BO.SCORED}
        metrics["T5"] = {"items": 10, "run": 10, "answered": 10, "accuracy": 0.9, "valid_rate": 0.95,
                         "allowed_rate": 0.9, "in_plan_rate": 0.8, "plans_ok": 9, "calls": 20}
        metrics.update(combined=round(acc * 100, 1), s_per_call=3.0, completion_tokens_per_call=200.0)
        return {"key": f"bakeoff.{name}", "name": name, "variant": variant, "model": f"m/{name}", "gpus": gpus,
                "wall_s": 100.0, "metrics": metrics, "vram_peak": {"0": 70000}, "cycles": {"render_rc": 0},
                "results": {}}
    BO.write_json(tmp_path / "fp8-off.json", record("fp8", "off", 1, 0.70))
    BO.write_json(tmp_path / "flash_next-on.json", record("flash_next", "on", 2, 0.75))
    BO.write_json(tmp_path / "flash_next.json", {"key": "bakeoff.flash_next", "name": "flash_next",
                                                  "variants": {"on": {"wall_s": 100.0}}, "server": {"ok": True}})
    BO.write_json(tmp_path / "step_flash.json", {"key": "bakeoff.step_flash", "name": "step_flash", "variants": {},
                                                  "server": {"error": "early exit", "reason": "early_exit"}})
    data = BO.summary(tmp_path)
    assert data["decision"]["pick"]["name"] == "fp8"
    md = (tmp_path / "summary.md").read_text()
    assert "| fp8 | off | 1 |" in md and "step_flash: server failed" in md and "Pick: fp8 off" in md
    assert BO.started(tmp_path, "flash_next") and not BO.started(tmp_path, "step_flash")
    assert not BO.started(tmp_path, "bf16")


def test_the_t1_crop_outlines_the_piece(tmp_path):
    from PIL import Image
    b = BO.building_of("real02")
    out = BO.t1_crop(b, "real02", "f_L-1_008", "r_L-1_mutfak", tmp_path / "c.jpg")
    im = Image.open(out).convert("RGB")
    assert max(im.size) == 512
    import numpy as np
    a = np.asarray(im).astype(int)
    blue = int(((a[..., 2] > 200) & (a[..., 0] < 60) & (a[..., 1] < 140)).sum())
    assert blue > 200


# --------------------------------------------------------------------------
# The job
# --------------------------------------------------------------------------

def test_the_job_script():
    text = JOB.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash") and "set -Eeuo pipefail" in text
    assert "trap 'on_error $LINENO" in text and "trap 'on_exit' EXIT" in text
    assert "--gpu-count 2" in text and "--over-5-ok" in text and "--max-minutes 100" in text
    assert subprocess.run(["bash", "-n", str(JOB)]).returncode == 0
    order = [text.index(s) for s in ('pair fp8 muse', 'bakeoff bf16 0 8001', 'two_gpu flash_next',
                                     'two_gpu step_flash', 'run_step summary')]
    assert order == sorted(order)
    assert '--key "bakeoff.$name"' in text and "--gpu-tests" in text and "started --out" in text
    assert text.count("copy_results") >= 3 and "kill_vllm" in text and "HF_HUB_OFFLINE=1" in text
    assert 'hf" download "$id" --revision "$rev"' in text


def test_a_partial_rebuild_keeps_the_other_tasks(tmp_path, items):
    import shutil
    its, folder = items
    shutil.copyfile(folder / BO.ITEMS_NAME, tmp_path / BO.ITEMS_NAME)
    res = BO.build(BO.SPEC_PATH, tmp_path, tasks=("T4",))
    assert res["counts"] == {"T1": 40, "T2": 30, "T3": 20, "T4": 20, "T5": 20}
    rebuilt = BO.read_json(tmp_path / BO.ITEMS_NAME)["items"]
    assert [i["id"] for i in rebuilt] == [i["id"] for i in its]
    assert [i for i in rebuilt if i["task"] == "T4"] == [i for i in its if i["task"] == "T4"]


def test_run_model_writes_the_server_facts_and_every_variant(tmp_path, items, monkeypatch):
    """``run_model`` on a server someone else started (``--url``), the model client scripted: ``<name>.json`` and
    ``<name>-<variant>.json`` per variant, ``started``; no T5 run: the summary picks nobody (T5 calls < 80 %)."""
    its, folder = items
    sub = []
    for t in ("T1", "T2", "T3", "T4"):
        it = dict(_first(items, t))
        it["images"] = [r if r.startswith("repo:") else f"repo:{(folder / r).relative_to(ROOT)}" for r in it["images"]]
        sub.append(it)
    BO.write_json(tmp_path / "items" / BO.ITEMS_NAME, {"version": 1, "items": sub})
    answers = {"t1": {"type": "chair", "why": "x"}, "t2": {"errors": []}, "t3": {"best": 1, "why": "x"},
               "t4": {"floating_or_sunk_decor": False, "wrong_object": False, "notes": "x"}}
    made = []

    def fake_client(url, key, check_yaml=None, *, variant=None, **kw):
        model = M.MockModel(critic=[lambda body: answers[M.MockModel.schema_name(body)]] * 4)
        model.critic_thinking = variant == "on"
        made.append((url, key, variant))
        return model

    monkeypatch.setattr(M, "from_check_yaml", fake_client)
    monkeypatch.setenv("WENART_JOB_DIR", str(tmp_path / "job"))
    facts = BO.run_model("bakeoff.fp8", tmp_path / "out", url="http://127.0.0.1:9/v1",
                         items_path=tmp_path / "items" / BO.ITEMS_NAME, workers=2, tasks=("T1", "T2", "T3", "T4"))
    assert [v for _u, _k, v in made] == ["off", "on"] and facts["server"]["external"]
    for v in ("off", "on"):
        rec = BO.read_json(tmp_path / "out" / f"fp8-{v}.json")
        assert rec["variant"] == v and set(rec["results"]) == {i["id"] for i in sub}
        assert rec["metrics"]["combined"] is not None and rec["cycles"]
    assert BO.started(tmp_path / "out", "fp8")
    assert not (tmp_path / "out" / "render-fp8").exists()
    data = BO.summary(tmp_path / "out")
    assert len(data["rows"]) == 2 and data["decision"]["pick"] is None
    assert set(data["decision"]["not_eligible"]) == {"fp8 off", "fp8 on"}
