"""RL try 2 (23 Nov 2026): training questions from the dataset bench (wenart/reading_check/rl_bench.py) and its job."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.reading_check import rl_bench as RB

ROOT = Path(__file__).resolve().parents[1]


def _w(a, b, t=0.2):
    return {"start": list(a), "end": list(b), "thickness": t}


def _r(poly, label="ODA", typ="bedroom"):
    return {"polygon": [list(p) for p in poly], "label": label, "room_type": typ}


TRUTH = {"walls": [_w((0, 0), (6, 0)), _w((0, 0), (0, 5)), _w((6, 0), (6, 5)), _w((0, 5), (6, 5)),
                   _w((2, 0), (2, 5), 0.1)],
         "doors": [{"center": [1.5, 5], "width": 0.9}],
         "windows": [{"center": [4.5, 0], "width": 1.2}, {"center": [6, 2.5], "width": 1.2}],
         "rooms": [_r([(0, 0), (2, 0), (2, 5), (0, 5)]), _r([(2, 0), (6, 0), (6, 5), (2, 5)])], "stairs": []}
READ = {"walls": [_w((0, 0), (6, 0)), _w((0, 0), (0, 5)), _w((6, 0), (6, 5)), _w((0, 5), (6, 5)),
                  _w((0.8, 1.5), (0.8, 3.5), 0.1)],
        "doors": [{"center": [1.5, 5], "width": 0.9}, {"center": [4.5, 0], "width": 1.2}], "windows": [],
        "openings": [], "rooms": [_r([(0, 0), (6, 0), (6, 5), (0, 5)])], "stairs": []}


def test_level_items_answer_from_the_truth():
    got = {(q["kind"], tuple(q["at"])): (q["answer"], q["error"]) for q in RB.level_items("p", "L0", TRUTH, READ,
                                                                                          READ, None)}
    assert got[("wall_right", (0.8, 2.5))] == ("no", True)              # a wall on no drawn line
    assert got[("wall_right", (3.0, 0.0))] == ("yes", False)
    assert got[("wall_missing", (2.0, 2.5))] == ("yes", True)           # the drawn wall the reading lacks
    assert got[("opening_right", (4.5, 0))] == ("window", True)         # a window read as a door
    assert got[("opening_right", (1.5, 5))] == ("door", False)
    assert got[("opening_missing", (6.0, 2.5))] == ("yes", True)
    assert ("opening_missing", (4.5, 0.0)) not in got                   # read as another type: no "missing" item
    assert got[("room_missing", (1.0, 2.5))] == ("yes", True)           # merged into its neighbour
    assert ("wall_right", (6.0, 2.5)) not in got                        # a ring on a window is no wall question


def test_level_items_put_truth_places_in_the_readings_frame():
    raw = copy.deepcopy(READ)
    for items in raw.values():
        for e in items:
            for k in ("start", "end", "center"):
                if k in e:
                    e[k] = [e[k][0] + 0.5, e[k][1]]
            if "polygon" in e:
                e["polygon"] = [[p[0] + 0.5, p[1]] for p in e["polygon"]]
    items = RB.level_items("p", "L0", TRUTH, raw, READ, {"shift_m": [0.5, 0.0], "rot_deg": 0.0})
    at = {(q["kind"], tuple(q["at"])) for q in items}
    assert ("wall_missing", (2.5, 2.5)) in at and ("opening_missing", (6.5, 2.5)) in at
    assert ("wall_right", (1.3, 2.5)) in at                             # the reading's own place


def test_split_is_by_building_and_deterministic():
    names = [f"swiss-b{i}" for i in range(11)]
    a, b = RB.split(names), RB.split(list(reversed(names)))
    assert a == b
    assert sum(v == "train" for v in a.values()) == 6 and sum(v == "held" for v in a.values()) == 5


def test_select_balances_right_and_wrong_and_caps_buildings():
    items = []
    for p in range(6):
        for k in range(5):
            items.append({"id": f"b{p}|r{k}", "project": f"b{p}", "kind": "room_right", "answer": "yes", "error": False})
        items.append({"id": f"b{p}|w", "project": f"b{p}", "kind": "room_right", "answer": "no", "error": True})
    got = RB.select(items, cap_class=40, cap_building=3)
    assert sum(q["error"] for q in got) == 6 and sum(not q["error"] for q in got) == 6
    per = {}
    for q in got:
        per[(q["project"], q["answer"])] = per.get((q["project"], q["answer"]), 0) + 1
    assert max(per.values()) <= 3


def test_says_error_and_verify():
    q = {"kind": "opening_right", "model_has": "door", "answer": "window"}
    assert RB.says_error(q, "window") is True and RB.says_error(q, "door") is False
    assert RB.verify(q, '{"answer": "window"}') is True and RB.verify(q, "no json") is None
    assert RB.says_error({"kind": "wall_right"}, "no") is True
    assert RB.says_error({"kind": "room_missing"}, "yes") is True
    assert RB.says_error({"kind": "room_missing"}, "no") is False


def test_sft_rows_keep_mixed_questions_balanced_with_their_images():
    qs = {}
    samples = []
    for i in range(10):
        cls = ("room_right", "yes", False) if i % 2 else ("room_right", "no", True)
        q = {"id": f"q{i}", "project": "b", "kind": cls[0], "answer": cls[1], "error": cls[2], "held_out": False,
             "images": ["crops/a_d.jpg", "crops/a_m.jpg"]}
        qs[q["id"]] = q
        ver = [True, False] if i < 8 else ([True, True] if i == 8 else [False, False])
        samples.append({"id": q["id"], "verified": ver})
    rows, rep = RB.sft_rows(qs, samples, rows_max=4)
    assert rep["kept"] == 8 and rep["all_right"] == 1 and rep["all_wrong"] == 1 and rep["rows"] == 4
    assert rep["by_class"] == {"room_right:no": 2, "room_right:yes": 2}
    r = rows[0]
    n_img = sum(1 for m in r["prompt"] for c in m["content"] if c.get("type") == "image")
    assert n_img == len(r["images"]) == 2
    assert json.loads(r["completion"][0]["content"][0]["text"])["answer"] == qs[r["id"]]["answer"]


def test_held_score_counts_errors_flagged_and_false_alarms(tmp_path):
    qs = [{"id": "a", "kind": "wall_right", "answer": "no", "error": True, "held_out": True},
          {"id": "b", "kind": "wall_right", "answer": "yes", "error": False, "held_out": True}]
    (tmp_path / "questions.jsonl").write_text("".join(json.dumps(q) + "\n" for q in qs))
    (tmp_path / "x.jsonl").write_text(json.dumps({"id": "a", "answers": ['{"answer": "no"}']}) + "\n"
                                      + json.dumps({"id": "b", "answers": ['{"answer": "no"}']}) + "\n")
    st = RB.held_score(tmp_path, {"x": tmp_path / "x.jsonl"})["x"]
    assert (st["right"], st["errors_flagged"], st["false_alarms"], st["accuracy"]) == (1, 1, 1, 0.5)


def test_the_committed_set_is_whole_and_split_by_building():
    d = RB.SET_DIR
    if not (d / "questions.jsonl").is_file():
        pytest.skip("no committed set")
    m = json.loads((d / "manifest.json").read_text())
    qs = list(RB.load_questions(d / "questions.jsonl").values())
    assert not set(m["projects_train"]) & set(m["projects_held"])
    for q in qs:
        assert len(q["images"]) == 2 and all((d / p).is_file() for p in q["images"])
        assert q["project"] in (m["projects_held"] if q["held_out"] else m["projects_train"])
        assert q["kind"] in RB.KINDS
    assert m["train"] == sum(not q["held_out"] for q in qs) and m["held_out"] == sum(q["held_out"] for q in qs)


def test_phase_exam_asks_both_arms_with_the_drawing_text(tmp_path, monkeypatch):
    import contextlib

    from wenart.reading_check import rl_pilot as RP
    from wenart.run import servers as SV

    calls, flags = [], []

    @contextlib.contextmanager
    def fake_server(key, deadline, extra_flags=""):
        flags.append(extra_flags)
        yield "http://127.0.0.1:1/v1"

    def fake_exam(url, key, out, served=None, fewshot=None, deadline=None, workers=8, arms=None):
        calls.append((key, served, fewshot, arms))
        return {"asked": 1}

    monkeypatch.setattr(SV, "server", fake_server)
    monkeypatch.setattr(SV, "model_entry", lambda models, key: {"id": "Qwen/base"})
    monkeypatch.setattr(SV, "check_models", lambda: {})
    monkeypatch.setattr(RP, "_exam", fake_exam)
    monkeypatch.setattr(RB, "sample", lambda *a, **k: {"questions": 0})
    rep = RB.phase_exam(tmp_path, tmp_path / "adapter", tmp_path / "out", log=lambda *_: None)
    assert sorted(calls, key=str) == sorted([("bakeoff.bf16", RP.LORA_NAME, None, ("1",)),
                                             ("bakeoff.bf16", None, None, ("1",))], key=str)
    assert "--enable-lora --max-lora-rank 16 --lora-modules" in flags[0]
    assert set(rep) >= {"held_lora", "held_bf16", "exam_lora", "exam_bf16"}


FAKE_PY = r'''#!/usr/bin/env python3
import sys, pathlib
a = sys.argv[1:]
if "-c" in a:
    print("Qwen/x" if '["id"]' in a[a.index("-c") + 1] else "rev0")
    sys.exit(0)
def arg(k):
    return a[a.index(k) + 1] if k in a else None
mod = "rl_bench" if "rl_bench" in a else "rl_pilot"
cmd = a[a.index(mod) + 1] if mod in a else ""
if cmd == "phase-sample":
    d = pathlib.Path(arg("--out")); d.mkdir(parents=True, exist_ok=True)
    (d / "samples.jsonl").write_text('{"id": "q"}\n')
elif cmd == "filter":
    (pathlib.Path(arg("--train")) / "sft.jsonl").write_text("{}\n")
elif cmd == "train":
    assert arg("--max-minutes") is not None
    d = pathlib.Path(arg("--out")); d.mkdir(parents=True, exist_ok=True)
    (d / "adapter_config.json").write_text("{}")
print("fake", mod, cmd)
'''


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_the_rl_bench_job_reaches_its_end_with_fakes(tmp_path):
    import os
    import subprocess

    ws, fast = tmp_path / "ws", tmp_path / "fast"
    repo = ws / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "pod_setup_polish.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    st = repo / "results" / "rl_bench" / "set" / "crops"
    st.mkdir(parents=True)
    (st / "a_d.jpg").write_text("x")
    (st.parent / "questions.jsonl").write_text('{"id": "q"}\n')
    py = tmp_path / "bin" / "python"
    py.parent.mkdir()
    py.write_text(FAKE_PY)
    py.chmod(0o755)
    vtrain = fast / "venv-train" / "bin"
    vtrain.mkdir(parents=True)
    (fast / "venv-train" / ".rl-pilot-1").write_text("")
    (vtrain / "python").write_text(FAKE_PY)
    (vtrain / "python").chmod(0o755)
    env = dict(os.environ, WENART_WS=str(ws), WENART_FAST=str(fast), WENART_PY=str(py), JOB_ID="rlbflow",
               WENART_RESULTS=str(tmp_path / "results"), WENART_JOB_DIR=str(tmp_path / "job"))
    env.pop("WENART_DEADLINE", None)
    res = subprocess.run(["bash", str(ROOT / "scripts" / "jobs" / "rl_bench.sh")], env=env, cwd=str(tmp_path),
                         capture_output=True, text=True, timeout=120)
    out = res.stdout + res.stderr
    assert res.returncode == 0, out[-3000:]
    for step in ("step start: setup", "step start: set", "step start: phase-a", "step start: filter",
                 "step start: train", "step start: phase-c", "all steps ok"):
        assert step in out, f"missing {step!r}:\n{out[-3000:]}"


def test_the_job_skips_training_when_phase_c_would_lose_its_time(tmp_path):
    import os
    import subprocess
    import time

    ws, fast = tmp_path / "ws", tmp_path / "fast"
    repo = ws / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "pod_setup_polish.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    st = repo / "results" / "rl_bench" / "set" / "crops"
    st.mkdir(parents=True)
    (st.parent / "questions.jsonl").write_text('{"id": "q"}\n')
    py = tmp_path / "bin" / "python"
    py.parent.mkdir()
    py.write_text(FAKE_PY)
    py.chmod(0o755)
    (fast / "venv-train").mkdir(parents=True)
    (fast / "venv-train" / ".rl-pilot-1").write_text("")
    env = dict(os.environ, WENART_WS=str(ws), WENART_FAST=str(fast), WENART_PY=str(py), JOB_ID="rlbskip",
               WENART_RESULTS=str(tmp_path / "results"), WENART_JOB_DIR=str(tmp_path / "job"),
               WENART_DEADLINE=str(int(time.time()) + 2000))
    res = subprocess.run(["bash", str(ROOT / "scripts" / "jobs" / "rl_bench.sh")], env=env, cwd=str(tmp_path),
                         capture_output=True, text=True, timeout=120)
    out = res.stdout + res.stderr
    assert res.returncode == 1 and "skipping the training" in out and "step start: phase-c" not in out, out[-2000:]
