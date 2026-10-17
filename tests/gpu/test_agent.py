"""Milestone 11 GPU tests of the agent (docs/milestone11.md §10 "GPU", §12 pod G1).

Run on the pod (``scripts/jobs/agent_check.sh``, or ``pytest -m gpu tests/gpu/test_agent.py``). The agent server is
``$WENART_AGENT_URL`` when set (a server that is already up), else one ``vllm serve`` of ``check.yaml models.<key>``
(``$AGENT_TEST_MODEL``, default ``agent``) started for this module by ``wenart.run.servers`` exactly as the
orchestrator starts it.

- the model serves: one planner call with the real tool list gives a tool call whose arguments validate, and one
  critic call gives an answer that validates against the room schema;
- the critic flags a planted error: the committed real02 building with a double bed turned by 180 deg (its top-down
  image and the room's committed previews): a kept finding names that bed;
- the loop on synthetic-01 (the committed building and previews, re-runs replaced by ``apply`` on the CPU): it ends
  by a stop rule, its log validates, every accepted edit passed the code checks, and a last critique finds no
  critical problem;
- Milestone 12 (pod P1, ``scripts/jobs/bakeoff_m12.sh`` runs this module against the live server of
  ``bakeoff.fp8``): one item of every bake-off task (``wenart.agent.bakeoff``) gets a valid answer: T1-T4 JSON that
  passes its schema, T5 a plan or tool calls on the room brief;
- fix round after P3 (16-17 Oct 2026): every agent request carries the repetition stop and the call log its
  ``finish_reason`` and ``max_tokens`` (1536 for the planner without thinking); a prompt past the served context is
  sent once and raised as ``ContextFullError`` with the prompt size; the client's ``max_model_len`` is the served one.
"""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

import pytest

from wenart.agent import log as LG
from wenart.agent import loop as LP
from wenart.agent import model as M
from wenart.agent import overrides as OV
from wenart.agent import podcheck as PC
from wenart.agent import topdown as TD

pytestmark = pytest.mark.gpu
ROOT = Path(__file__).resolve().parents[2]
KEY = os.environ.get("AGENT_TEST_MODEL", "agent")


@pytest.fixture(scope="module")
def agent_url():
    url = os.environ.get("WENART_AGENT_URL", "").strip()
    if url:
        yield url
        return
    from wenart.run import servers as SV
    mem = None
    try:
        import subprocess
        _name, mem = SV.gpu_from_text(subprocess.run(SV.NVIDIA_SMI_QUERY, capture_output=True, text=True,
                                                     timeout=20).stdout)
    except OSError:
        pass
    with SV.server(KEY, None, seqs=4, mem_mib=mem or None,
                   logs_dir=Path(os.environ.get("WENART_LOGS", "/workspace/logs"))) as served:
        yield served


@pytest.fixture
def model(agent_url):
    return M.from_check_yaml(agent_url, KEY, timeout_s=900.0)


def test_the_model_serves_a_tool_call_and_a_json_schema_answer(model, tmp_path):
    tool = PC.tool_call_check(model)
    assert tool["ok"], tool
    building = json.loads((ROOT / "results" / "furniture" / "synthetic-01" / "building_final.json").read_text())
    room = "r_L0_salon"
    image = TD.draw_room(building, room, tmp_path / "salon.png")
    structured = PC.structured_check(model, building, room, image)
    assert structured["ok"], structured
    assert all(c["revision"] == model.revision and c["seconds"] is not None for c in model.calls)


def test_the_critic_flags_a_planted_bed(model, tmp_path):
    res = PC.planted_critic(model, "real02", tmp_path)
    assert "skipped" not in res, res
    bed = next(r for r in res["planted"] if r["what"].startswith("bed"))
    assert bed["error"] is None and bed["flagged"], bed


def _synthetic_01(tmp_path: Path) -> Path:
    out = tmp_path / "synthetic-01"
    b = ROOT / "results" / "furniture" / "synthetic-01" / "building_final.json"
    for name in ("building_decor.json", "building_final.json", "building.json"):
        (out / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(b, out / name)
    renders = ROOT / "results" / "renders" / "synthetic-01"
    (out / "scene").mkdir()
    shutil.copyfile(renders / "scene_manifest.json", out / "scene" / "scene_manifest.json")
    prev = out / "agent" / "previews"
    prev.mkdir(parents=True)
    for p in renders.glob("*_preview.jpg"):
        shutil.copyfile(p, prev / p.name)
    (prev / "render_manifest.json").write_text(json.dumps({"renders": [
        {"camera": p.name[:-len("_preview.jpg")]} for p in renders.glob("*_preview.jpg")]}))
    (out / "style.json").write_text("{}")
    return out


def test_the_loop_on_synthetic_01(model, tmp_path):
    out = _synthetic_01(tmp_path)

    def rerun(stage, views, round_no, final):
        # On the CPU: the accepted edits replayed (apply) and taken as the rendered building; no new previews.
        OV.apply(out)
        shutil.copyfile(out / OV.AGENT_BUILDING, out / "building_final.json")
        return {"status": "ok", "views": [], "note": "apply only (GPU test)"}

    loop = LP.AgentLoop(out, model, rerun=rerun, max_rounds=3)
    summary = loop.run()
    assert summary["stop"]["reason"] in ("no_finding", "no_edit", "max_rounds"), summary
    data = json.loads((out / "orchestrator" / "log.json").read_text())
    assert LG.validate_log(data) == []
    for e in data["events"]:
        if e["kind"] == "edit":
            assert e["validation"]["accepted"] and not e["validation"]["failed_checks"] and e["reason"]
    ctx = loop.context(99)
    code = loop.run_code_critic(ctx, loop.preview_dir)
    vision = loop.run_vision_critic(ctx, code, 99)
    # This test re-renders nothing (no Blender run), so the vision critic sees the old previews again: only the code
    # findings can show what the loop fixed (pod G1: the vision critic kept its F9 findings on the stale previews).
    critical = [f for f in code["findings"] if f["severity"] == "critical"]
    assert not critical, critical
    ids = {r["id"] for r in json.loads((out / "building_final.json").read_text())["rooms"]}
    assert all(f.get("target") for f in vision["kept"]) and vision["kept"] is not None and ids


def test_every_bakeoff_task_answers_on_this_model(model):
    from wenart.agent import bakeoff as BO
    from wenart.agent import tools as TL
    items, folder = BO.load_items()
    registry = TL.build_registry()
    for task in BO.TASKS:
        item = next(i for i in items if i["task"] == task)
        res = BO.answer_item(model, item, folder, registry)
        assert res["error"] is None, (task, res["error"])
        assert res["call_seconds"] and all(s is not None for s in res["call_seconds"]), res
        if task == "T5":
            assert res["answer"]["plan"] is not None or res["answer"]["calls"], res["answer"]
        else:
            assert res["answer"] is not None, (task, res)


# ----- fix round after P3 (16-17 Oct 2026; the agent track's ask): the client against the served agent key --------

def _counting(model):
    """Wrap the model's POST so the test sees every request body it sends."""
    sent = []
    post = model._post

    def counted(url, body, timeout_s):
        sent.append(body)
        return post(url, body, timeout_s)

    model._post = counted
    return sent


def test_the_planner_call_sends_the_repetition_stop_and_logs_its_finish_and_budget(model):
    # P3: no repetition guard on the agent calls and no finish_reason in the call log
    sent = _counting(model)
    tool = PC.tool_call_check(model)
    assert tool["ok"], tool
    assert sent and all(b.get("repetition_detection") == model.repetition_detection for b in sent)
    call = model.calls[-1]
    assert call["finish_reason"] in ("stop", "tool_calls") and call["max_tokens"] == model.max_tokens
    if not model.planner_thinking:
        assert model.max_tokens == M.PLANNER_MAX_TOKENS == 1536


def test_a_prompt_past_the_served_context_is_refused_once_and_raised_as_context_full(model):
    # P3 r4-p5: HTTP 400 'maximum context length' (28,673 prompt + 4,096 answer > 32,768), retried and logged as
    # 'the agent model did not answer'. A prompt of about max_model_len - 800 tokens plus the 1536-token answer
    # budget passes the context; the prompt alone fits, so vLLM names its size ("at least N input tokens").
    sent = _counting(model)
    words = " ".join(["word"] * (model.max_model_len - 800))
    with pytest.raises(M.ContextFullError) as info:
        model.chat([{"role": "user", "content": words}], None, call_id="context-full", max_tokens=1536)
    assert len(sent) == 1 and info.value.attempts == 1 and info.value.status == 400
    assert info.value.prompt_tokens is not None and info.value.prompt_tokens + 1536 > model.max_model_len
    assert model.calls[-1]["finish_reason"] == "context_full" and model.calls[-1]["attempts"] == 1


def test_the_client_knows_the_served_context_of_the_key(agent_url):
    import urllib.request

    model = M.from_check_yaml(agent_url, KEY)
    if KEY == "agent":
        assert model.max_model_len == 32768
    with urllib.request.urlopen(f"{agent_url.rstrip('/')}/models", timeout=30) as resp:
        card = json.loads(resp.read().decode("utf-8"))
    served = [m.get("max_model_len") for m in card.get("data") or [] if m.get("max_model_len")]
    assert served, card                                       # vLLM's /v1/models names max_model_len
    assert model.max_model_len == served[0]
