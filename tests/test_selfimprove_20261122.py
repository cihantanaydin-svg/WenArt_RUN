"""The self-improvement round of 22 Nov 2026 (Milestone 14, user-approved queue item): the threshold search (``tune``),
the weak-spot hunter (``weak_spots`` and the synthetic projects 24-26 with the three reader rules they exposed), read
twice (``twice`` and the question picker's extra uncertainty) and the RL pilot's CPU side (``rl_pilot``).

Every rule here is general (UL338): the synthetic projects are its tests, the user's records the cases that showed it.
"""
from __future__ import annotations

import importlib
import inspect
import json
import re
from pathlib import Path

import pytest

from wenart.ingest.generic import openings as OP
from wenart.ingest.generic import walls as W
from wenart.ingest.generic.model import Stroke
from wenart.reading_check import rl_pilot as RL
from wenart.reading_check import tune as TU
from wenart.reading_check import twice as TW
from wenart.reading_check import weak_spots as WS

ROOT = Path(__file__).resolve().parents[1]


# --- tune ----------------------------------------------------------------------------------------------------------

def test_tunable_thresholds_are_module_globals_read_at_call_time():
    """Setting a module attribute must change the reading: no tunable constant is a default argument or imported by
    value anywhere in the reader."""
    src = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT / "wenart").rglob("*.py"))
    for prm in TU.PARAMS:
        mod = importlib.import_module(prm.module)
        assert isinstance(getattr(mod, prm.name), (int, float)), prm.key
        assert not re.search(rf"def \w+\([^)]*=\s*{prm.name}\b", inspect.getsource(mod)), prm.key
        assert not re.search(rf"from {re.escape(prm.module)} import [^\n]*\b{prm.name}\b", src), prm.key
        assert all(c > 0 for c in prm.candidates) and prm.current() not in prm.candidates, prm.key


def test_apply_settings_sets_and_names_unknown():
    was = OP.ZONE_M
    try:
        TU.apply_settings({"openings.ZONE_M": 0.41})
        assert OP.ZONE_M == 0.41
        with pytest.raises(AttributeError):
            TU.apply_settings({"wenart.ingest.generic.openings.NO_SUCH_M": 1.0})
    finally:
        OP.ZONE_M = was


def _res(total, entries=None):
    r = {"total": total}
    if entries is not None:
        r.update(sparse=True, entries=entries, assertions=[])
    return r


def test_split_is_stratified_and_holds_records_by_hash():
    base = {f"synthetic-{k:02d}": _res(100.0 - k) for k in range(9)}
    sp = TU.split(base)
    assert len(sp["held"]) == 3 and set(sp["held"]).isdisjoint(sp["tune"])
    assert "synthetic-07" in sp["held"]          # sorted by total: the weak ones are held out too
    assert TU.held_record("C0001") == TU.held_record("C0001")
    held = [r for r in (f"C{k:04d}" for k in range(1, 61)) if TU.held_record(r)]
    assert 10 <= len(held) <= 30


def test_decide_keeps_only_a_held_out_rise_without_a_fall():
    sp = {"tune": ["a"], "held": ["b", "c"]}
    base = {"a": _res(90.0), "b": _res(90.0), "c": _res(100.0)}
    better = {"a": _res(95.0), "b": _res(95.0), "c": _res(100.0)}
    worse = {"a": _res(99.0), "b": _res(99.0), "c": _res(98.0)}
    flat = {"a": _res(99.0), "b": _res(90.0), "c": _res(100.0)}
    assert TU.decide(base, better, sp)["keep"]
    d = TU.decide(base, worse, sp)
    assert not d["keep"] and any("c:" in f for f in d["held_falls"])
    assert not TU.decide(base, flat, sp)["keep"]


def test_held_record_falls_count():
    rid = next(r for r in (f"C{k:04d}" for k in range(1, 99)) if TU.held_record(r))
    e_ok = [{"id": "u1", "type": "doors", "records": [rid], "satisfied": True}]
    e_no = [{"id": "u1", "type": "doors", "records": [rid], "satisfied": False}]
    sp = {"tune": [], "held": []}
    falls = TU.held_falls({"real": _res(100.0, e_ok)}, {"real": _res(0.0, e_no)}, sp)
    assert falls and rid in falls[0]


# --- the weak-spot hunter ------------------------------------------------------------------------------------------

def test_rank_by_shares_not_by_source_size():
    rows = WS.rank({"big": {"x": 1000, "y": 1000}, "small": {"y": 3}})
    assert rows[0]["kind"] == "y" and rows[0]["score"] == pytest.approx(1.5)


def test_bench_and_known_sources_parse():
    assert WS.bench_counts().get("wall_invented", 0) > 0
    known = WS.known_counts()
    assert known.get("opening_type", 0) > 0 and known.get("door_invented", 0) > 0


@pytest.fixture(scope="module")
def weak_readings(tmp_path_factory):
    return {r["project"]: r for r in WS.hunt(tmp_path_factory.mktemp("weak"))}


@pytest.mark.parametrize("name", ["synthetic-24-sliding-windows", "synthetic-25-stair-edge",
                                  "synthetic-26-corner-shower"])
def test_weak_spot_projects_read_exactly(weak_readings, name):
    """The three reader rules of 22 Nov 2026 on their synthetic projects: sliding sashes on a window layer are a
    window (UL346), a flight's open side is no wall (C0053), a fixture's curve is no door swing."""
    r = weak_readings[name]
    assert r["total"] == 100.0, r["faults"]


def test_sliding_sashes_by_layer():
    loose = [Stroke("a", "polyline", [(0, 0), (1, 0)], layer="PENCERE"),
             Stroke("b", "polyline", [(0, 0.1), (1, 0.1)], layer="PENCERE")]
    assert OP.sliding_sashes(loose)
    assert not OP.sliding_sashes(loose + [Stroke("c", "line", [(0, 0), (1, 0)], layer="KAPI")])
    assert not OP.sliding_sashes([Stroke("d", "line", [(0, 0), (1, 0)], layer="PENCERE", block="BALKON_1")])
    assert OP.sliding_sashes([Stroke("e", "line", [(0, 0), (1, 0)], layer="0", block="PENCERE_SURME")])
    assert not OP.sliding_sashes([])


def test_no_door_swing_on_fixture_layers():
    arc = {"center": (0, 0), "radius": 0.8, "start_deg": 180, "end_deg": 270}
    assert not OP.swing_layer_ok(Stroke("s", "arc", [(0, 0), (1, 1)], layer="VITRIFIYE", arc=arc))
    assert not OP.swing_layer_ok(Stroke("t", "arc", [(0, 0), (1, 1)], layer="KARO", arc=arc))
    # a furniture layer may hold a door (real03's typical-floor door block on the xref layer 'SAA_TEFRİS')
    assert OP.swing_layer_ok(Stroke("f", "arc", [(0, 0), (1, 1)], layer="xref_2+1_A3_PLAN$0$SAA_TEFRİS", arc=arc))
    assert OP.swing_layer_ok(Stroke("k", "arc", [(0, 0), (1, 1)], layer="KAPI", arc=arc))
    assert OP.swing_layer_ok(Stroke("b", "arc", [(0, 0), (1, 1)], layer="VITRIFIYE", block="KAPI_90", arc=arc))
    assert OP.swing_layer_ok(Stroke("o", "arc", [(0, 0), (1, 1)], layer="0", arc=arc))


def test_stair_edge_must_stand_free():
    edge = _pair(0.0, 3.0)
    meets = W._Pair("DUVAR", (0.0, 1.0), (-1.0, 0.0), -1.0, 0.05, (W._Line(-3.0, -1.0, 0.05, ["c"]),
                                                                 W._Line(-3.1, -1.0, 0.05, ["d"])))
    assert W.free_standing([edge], [edge]) == [edge]
    assert W.free_standing([edge], [edge, meets]) == []      # a wall meets its end at x = 3.0: a wall piece


def _pair(lo, hi, o0=0.0, o1=0.05):
    return W._Pair("DUVAR", (1.0, 0.0), (0.0, 1.0), lo, hi, (W._Line(o0, lo, hi, ["a"]), W._Line(o1, lo, hi, ["b"])))


def test_stair_edge_pair_dropped_only_at_a_flight_side():
    treads_above = [((0.25 * k, 0.05), (0.25 * k, 1.05)) for k in range(13)]          # end at the upper face
    treads_below = [((0.25 * k, -1.0), (0.25 * k, 0.0)) for k in range(13)]           # end at the lower face
    keep, drop = W._drop_stair_edge_pairs([_pair(0.0, 3.0)], treads_above)
    assert drop and not keep
    keep, drop = W._drop_stair_edge_pairs([_pair(0.0, 3.0)], treads_above + treads_below)
    assert keep and not drop                                  # a U stair's well: treads at both faces stay a wall
    keep, drop = W._drop_stair_edge_pairs([_pair(-2.0, 6.0)], treads_above)
    assert keep and not drop                                  # a wall running on past the flight
    keep, drop = W._drop_stair_edge_pairs([_pair(0.0, 3.0, 0.0, 0.25)], treads_above)
    assert keep and not drop                                  # a thick wall is never a balustrade
    assert "stair_edge" in __import__("wenart.ingest.generic.decisions", fromlist=["x"]).RULE_CONFIDENCE


# --- read twice ----------------------------------------------------------------------------------------------------

STAB = {"fragile": {"L0": [
    {"change": "lost", "kind": "doors", "place": {"id": "d_L0_001", "at": [1.0, 1.0]}, "variants": ["layers"]},
    {"change": "added", "kind": "windows", "place": {"id": "x", "at": [5.0, 5.0]}, "variants": ["mirror", "layers"]}]}}


def test_low_places_and_marking():
    low = TW.low_places(STAB)
    assert [x["change"] for x in low] == ["lost", "added"]
    assert low[0]["id"] == "d_L0_001" and low[1]["id"] is None
    assert "layers, mirror" in low[1]["reason"]
    b = {"openings": [{"id": "d_L0_001"}, {"id": "d_L0_002"}], "rooms": [], "walls": [], "stairs": []}
    assert TW.mark(b, low) == 1
    assert b["openings"][0]["reading_confidence"] == "low" and b["openings"][0]["reading_review"]
    assert "reading_confidence" not in b["openings"][1]


def test_value_counts_corrections_on_low_places_against_chance():
    truth = {"source": "user_corrections", "per_level": {"L0": {
        "doors": [{"center": [1.2, 1.0], "corrections": ["C1"]}],
        "windows": [{"center": [9.0, 9.0], "corrections": ["C2"]}]}}}
    read = {"per_level": {"L0": {"doors": [{"id": "d1", "center": [1.0, 1.0]}, {"id": "d2", "center": [20, 20]}],
                                 "windows": [{"id": "w1", "center": [9.0, 9.0]}]}}}
    truth["per_level"]["L0"]["doors"][0]["id"] = "u1"
    v = TW.value({"p": truth}, {"p": TW.low_places(STAB)}, {"p": read}, unsatisfied={"p": {"u1"}})
    assert v["entries"] == 2 and v["on_low_any"] == 1 and v["records_on_low"] == ["C1"]
    assert v["projects"]["p"]["chance"] == pytest.approx(0.333)   # one of three reading elements lies at a low place
    assert v["expected"] == pytest.approx(0.7) and v["lift"] == pytest.approx(1.5)
    assert v["wrong"] == 1 and v["wrong_on_low"] == 1


def test_question_picker_adds_instability():
    from wenart.reading_check import bandit as BA

    rec = {"project": "p", "level_id": "L0", "place": [1.0, 1.0], "final_answer": "door", "margin": 0.8,
           "scores": {"door": 0.9}, "kind": "gap_kind", "id": "g1"}
    labels = {"disagreements": [{"rec": rec, "ai": {"drawing": "window", "entry": "e"}}], "unstable": {}}
    base = BA.question_list(labels, include_findings=False, excluded={})[0]["score"]
    labels["unstable"] = {"p": TW.low_places(STAB)}
    q = BA.question_list(labels, include_findings=False, excluded={})[0]
    assert q["score"] > base and q["unstable"].startswith("read twice")


# --- the RL pilot --------------------------------------------------------------------------------------------------

def test_rl_answers_are_verified_against_the_truth():
    q = {"answer": "window"}
    assert RL.verify(q, '{"answer": "window"}') is True
    assert RL.verify(q, '```json\n{"answer": "door"}\n```') is False
    assert RL.verify(q, "a window") is None
    assert RL.verify({"answer": False}, '<think></think>{"answer": false}') is True
    assert RL.keep_question([True, False, False]) and not RL.keep_question([True] * 8)
    assert not RL.keep_question([False] * 8)


def test_rl_rejection_sampling_rows():
    qs = {"q1": {"id": "q1", "project": "synthetic-08-spaced-labels", "kind": "opening_kind", "crop": "crops/a.jpg",
                 "answer": "door"},
          "q2": {"id": "q2", "project": "synthetic-08-spaced-labels", "kind": "opening_kind", "crop": "crops/b.jpg",
                 "answer": "wall"}}
    assert not RL.held_project("synthetic-08-spaced-labels")
    samples = [{"id": "q1", "answers": ['{"answer": "door"}', '{"answer": "window"}', '{"answer":"door"}'],
                "verified": [True, False, True]},
               {"id": "q2", "answers": ['{"answer": "wall"}'] * 2, "verified": [True, True]}]
    rows, rep = RL.sft_rows(qs, samples)
    assert rep["all_right"] == 1 and rep["kept"] == 1 and len(rows) == 1      # one distinct right answer
    assert rows[0]["completion"][0]["content"][0]["text"] == '{"answer": "door"}'
    assert rows[0]["images"] == ["crops/a.jpg"] and rows[0]["prompt"][0]["content"][0] == {"type": "image"}


def test_rl_fewshot_folds_never_examine_their_examples():
    marks = {f"m{k}": {"right": k % 2 == 0} for k in range(25)}
    folds = RL.fewshot_folds(marks)
    for f in folds.values():
        assert set(f["examples"]).isdisjoint(f["exam"])
    assert sorted(m for f in folds.values() for m in f["exam"]) == sorted(marks)


def test_rl_level_questions_from_a_truth():
    tl = {"rooms": [{"id": "r1", "label": "MUTFAK", "room_type": "kitchen", "centroid": [2.0, 2.0],
                     "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}],
          "windows": [{"id": "w1", "center": [2.0, 0.0], "width": 1.2}],
          "doors": [{"id": "d1", "center": [4.0, 2.0], "width": 0.9}],
          "walls": [{"id": "w", "start": [0, 4], "end": [4, 4]}], "stairs": []}
    qs = RL.level_questions("synthetic-x", "L0", tl)
    kinds = {(q["kind"], json.dumps(q["answer"])) for q in qs}
    assert ("opening_kind", '"window"') in kinds and ("opening_kind", '"door"') in kinds
    assert ("opening_kind", '"wall"') in kinds and ("room_window", "true") in kinds
    assert ("stair_here", "false") in kinds and ("room_here", "false") in kinds


def test_rl_fewshot_block_reaches_the_checks_prompt(tmp_path):
    from wenart.reading_check import critic as CR

    ex = [{"id": "m", "kind": "door_into_air", "description": "d_L1_001: a door into the air", "right": False}]
    f = tmp_path / "fold.json"
    f.write_text(json.dumps({"text": RL.fewshot_text(ex)}), encoding="utf-8")
    assert CR.fewshot_block({}) == ""
    block = CR.fewshot_block({"CRITIC_FEWSHOT": str(f)})
    assert "door_into_air" in block and "not an error" in block


# --- the RL pilot's pod job (control flow with fakes: no GPU, no network) ------------------------------------------

FAKE_RL_PY = r'''#!/usr/bin/env python3
import sys, pathlib
a = sys.argv[1:]
if "-c" in a:
    print("Qwen/x" if '["id"]' in a[a.index("-c") + 1] else "rev0")
    sys.exit(0)
def arg(k):
    return a[a.index(k) + 1] if k in a else None
cmd = a[a.index("rl_pilot") + 1] if "rl_pilot" in a else ""
if cmd in ("build", "fewshot"):
    d = pathlib.Path(arg("--out")); d.mkdir(parents=True, exist_ok=True)
    (d / ("manifest.json" if cmd == "build" else "fewshot_fold0.json")).write_text("{}")
elif cmd == "phase-sample":
    d = pathlib.Path(arg("--out")); d.mkdir(parents=True, exist_ok=True)
    (d / "samples.jsonl").write_text('{"id": "q"}\n')
elif cmd == "train":
    d = pathlib.Path(arg("--out")); d.mkdir(parents=True, exist_ok=True)
    (d / "adapter_config.json").write_text("{}")
print("fake", cmd)
'''


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_the_rl_pilot_job_reaches_its_end_with_fakes(tmp_path):
    import os
    import subprocess

    ws, fast = tmp_path / "ws", tmp_path / "fast"
    repo = ws / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "pod_setup_polish.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    py = tmp_path / "bin" / "python"
    py.parent.mkdir()
    py.write_text(FAKE_RL_PY)
    py.chmod(0o755)
    vtrain = fast / "venv-train" / "bin"
    vtrain.mkdir(parents=True)
    (fast / "venv-train" / ".rl-pilot-1").write_text("")
    (vtrain / "python").write_text(FAKE_RL_PY)
    (vtrain / "python").chmod(0o755)
    env = dict(os.environ, WENART_WS=str(ws), WENART_FAST=str(fast), WENART_PY=str(py), JOB_ID="rlflow",
               WENART_RESULTS=str(tmp_path / "results"), WENART_JOB_DIR=str(tmp_path / "job"))
    env.pop("WENART_DEADLINE", None)
    res = subprocess.run(["bash", str(ROOT / "scripts" / "jobs" / "rl_pilot.sh")], env=env, cwd=str(tmp_path),
                         capture_output=True, text=True, timeout=120)
    out = res.stdout + res.stderr
    assert res.returncode == 0, out[-3000:]
    for step in ("step start: setup", "step start: build", "step start: phase-a", "step start: filter",
                 "step start: train", "step start: phase-c", "all steps ok"):
        assert step in out, f"missing {step!r}:\n{out[-3000:]}"
