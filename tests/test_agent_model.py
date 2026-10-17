"""The agent model client and MockModel (docs/milestone11.md §2 "Model client", §11 "Serving", §10).

Request bodies (temperature 0, seed 0, tools strict with tool_choice auto, the critic's JSON-schema response
format without tools and with thinking off, images as data URLs, at most 4), retries, the validation of critic
answers and the call log (model id, revision, call id, tokens, seconds)."""
from __future__ import annotations

import json

import pytest
from PIL import Image

from wenart.agent import model as M
from wenart.recognition import vlm_client as VC

SCHEMA = {"type": "object", "required": ["findings"], "additionalProperties": False,
          "properties": {"findings": {"type": "array", "items": {"type": "string"}}}}


def _png(tmp_path, name="a.png"):
    path = tmp_path / name
    Image.new("RGB", (64, 32), (200, 100, 50)).save(path)
    return path


def ok_answer(content="", tool_calls=None, usage=None):
    msg = {"role": "assistant", "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    return {"choices": [{"message": msg, "finish_reason": "stop"}],
            "usage": usage or {"prompt_tokens": 11, "completion_tokens": 7}}


def test_chat_body_tools_strict_auto_temperature_zero():
    tool = M.tool_spec("rotate_piece", "turn", {"$schema": "x", "type": "object", "properties": {}})
    assert tool == {"type": "function", "function": {"name": "rotate_piece", "description": "turn",
                                                     "parameters": {"type": "object", "properties": {}},
                                                     "strict": True}}
    body = M.chat_body("m", [{"role": "user", "content": "hi"}], [tool])
    assert body["temperature"] == 0.0 and body["seed"] == 0 and body["tool_choice"] == "auto"
    assert body["tools"] == [tool] and body["chat_template_kwargs"] == {"enable_thinking": False}
    assert "response_format" not in body
    assert "tools" not in M.chat_body("m", [], None)


def test_critic_body_json_schema_no_tools_thinking_off():
    body = M.critic_body("m", [], dict(SCHEMA, **{"$schema": "https://json-schema.org/draft/2020-12/schema"}))
    assert body["response_format"]["type"] == "json_schema"
    js = body["response_format"]["json_schema"]
    assert js["strict"] is True and js["name"] == "findings" and "$schema" not in js["schema"]
    assert "tools" not in body and "tool_choice" not in body
    assert body["chat_template_kwargs"] == {"enable_thinking": False} and body["temperature"] == 0.0


def test_images_are_data_urls_and_at_most_four(tmp_path):
    img = _png(tmp_path)
    msg = M.user_message("look", [img, img], ["Image 1", None])
    parts = msg["content"]
    assert parts[0] == {"type": "text", "text": "Image 1"}
    assert parts[1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert parts[2]["type"] == "image_url" and parts[-1] == {"type": "text", "text": "look"}
    assert M.count_images([msg]) == 2
    mock = M.MockModel()
    with pytest.raises(ValueError, match="at most 4"):
        mock.chat([M.user_message("x", [img] * 5)], call_id="c1")
    assert mock.requests == []                                   # refused before it was sent


def test_chat_parses_tool_calls_and_logs_every_call():
    logged = []
    mock = M.MockModel(chat=[{"tool_calls": [{"name": "room", "arguments": {"room_id": "r1"}},
                                             {"name": "finish", "arguments": "{not json"}]}],
                       on_call=logged.append)
    reply = mock.chat([{"role": "user", "content": "go"}], [M.tool_spec("room", "", {"type": "object"})],
                      call_id="r1-p1")
    assert [tc.name for tc in reply.tool_calls] == ["room", "finish"]
    assert reply.tool_calls[0].parsed == {"room_id": "r1"} and reply.tool_calls[0].error is None
    assert reply.tool_calls[1].parsed is None and "not valid JSON" in reply.tool_calls[1].error
    msg = reply.assistant_message()
    assert msg["tool_calls"][0]["function"]["name"] == "room"
    entry = logged[0]
    assert entry["call_id"] == "r1-p1" and entry["model"] == "mock/agent" and entry["revision"] == "mock-rev"
    assert entry["prompt_tokens"] == 100 and entry["completion_tokens"] == 20 and entry["seconds"] is not None
    assert entry["kind"] == "chat" and entry["tool_calls"] == 2
    assert mock.chat_requests()[0]["tools"][0]["function"]["strict"] is True
    # an exhausted script: no tool call
    assert mock.chat([], call_id="r1-p2").tool_calls == []


def test_critic_validates_and_retries_once():
    mock = M.MockModel(critic=[{"__raw__": "no json"}, {"findings": ["a"]}, {"findings": [1]}, {"findings": [2]}])
    good = mock.critic([], SCHEMA, call_id="v1")
    assert good.data == {"findings": ["a"]} and good.attempts == 2
    bad = mock.critic([], SCHEMA, call_id="v2")
    assert bad.data is None and bad.errors and bad.attempts == 2
    assert mock.calls[-1]["error"] and mock.calls[-1]["kind"] == "critic"
    assert all("response_format" in r for r in mock.critic_requests())


def test_transport_retries_then_model_error():
    attempts = []

    def post(url, body, timeout):
        attempts.append(url)
        if len(attempts) < 3:
            raise VC.VLMError("HTTP 503")
        return ok_answer("fine")

    model = M.AgentModel("http://x:8001/v1", "Qwen/Qwen3.8-27B-FP8", "017b", post=post, sleep=lambda s: None,
                         retries=2)
    reply = model.chat([], call_id="c")
    assert reply.content == "fine" and reply.attempts == 3 and attempts[0] == "http://x:8001/v1/chat/completions"
    assert model.calls[0]["revision"] == "017b" and model.calls[0]["model"] == "Qwen/Qwen3.8-27B-FP8"

    def down(url, body, timeout):
        raise VC.VLMError("cannot reach")

    model = M.AgentModel("http://x/v1", "m", "r", post=down, sleep=lambda s: None, retries=1)
    with pytest.raises(M.ModelError):
        model.critic([], SCHEMA, call_id="v")
    assert model.calls[0]["error"] and model.calls[0]["attempts"] == 2


def test_from_check_yaml_uses_the_agent_entry():
    model = M.from_check_yaml("http://127.0.0.1:8001/v1")
    assert model.model == "Qwen/Qwen3.8-27B-FP8" and model.revision == "017b9c7af6b5689d5dd426a76e0bc077eb5ca20a"
    fast = M.from_check_yaml("http://127.0.0.1:8001/v1", "agent_fast")
    assert fast.model == "Qwen/Qwen3.6-35B-A3B-FP8"
    assert json.dumps(M.chat_body(model.model, [], None))      # serialisable


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026): 4xx not retried, a full context, the planner's budget, the repetition stop
# --------------------------------------------------------------------------

# vLLM's answer to r4-p5 of P3 (runs/20261016-172855-full/results/agent/real04/log.json), as post_json raises it
P3_CONTEXT_400 = ('HTTP 400 from http://127.0.0.1:8001/v1/chat/completions: {"error":{"message":"This model\'s '
                  'maximum context length is 32768 tokens. However, you requested 4096 output tokens and your prompt '
                  'contains at least 28673 input tokens, for a total of at least 32769 tokens. Please reduce the '
                  'length of the input prompt or the number of requested output tokens. (parameter=input_tokens, '
                  'value=28673)","type":"BadRequestError","param":"input_tokens","code":400}}')


def test_a_context_full_400_is_sent_once_and_raised_as_its_own_error():
    """Fails on the old code: ``_send`` retried every VLMError, so the deterministic 400 went out 3 times, the call
    log said 3 attempts and the loop could not tell a full context from a dead server (P3 r4-p5)."""
    posts = []

    def full(url, body, timeout):
        posts.append(body)
        raise VC.VLMError(P3_CONTEXT_400)

    model = M.AgentModel("http://x/v1", "m", "r", post=full, sleep=lambda s: None, retries=2)
    with pytest.raises(M.ContextFullError) as info:
        model.chat([{"role": "user", "content": "go"}], call_id="r4-p5")
    assert len(posts) == 1 and info.value.attempts == 1 and info.value.status == 400
    assert info.value.prompt_tokens == 28673 and isinstance(info.value, M.ModelError)
    assert model.calls[-1]["attempts"] == 1 and model.calls[-1]["finish_reason"] == "context_full"
    assert model.calls[-1]["max_tokens"] == M.PLANNER_MAX_TOKENS
    # another 4xx: one POST, a plain ModelError; 408 / 429 and 5xx are retried
    for status, sent in ((404, 1), (422, 1), (429, 3), (408, 3), (503, 3)):
        n = []

        def answer(url, body, timeout, status=status, n=n):
            n.append(1)
            raise VC.VLMError(f"HTTP {status} from {url}: no")

        bad = M.AgentModel("http://x/v1", "m", "r", post=answer, sleep=lambda s: None, retries=2)
        with pytest.raises(M.ModelError) as err:
            bad.critic([], SCHEMA, call_id="v")
        assert len(n) == sent and not isinstance(err.value, M.ContextFullError), status
        assert bad.calls[-1]["attempts"] == sent
    assert M.http_status(VC.VLMError("cannot reach http://x")) is None


def test_the_planner_answer_budget_and_the_served_context():
    """Fails on the old code: every planner call asked for 4096 tokens (P3: p99 609, the largest valid answer 1,086;
    a runaway answer of 4,096 filled a session's context) and the client did not know the server's context."""
    mock = M.MockModel()
    mock.chat([{"role": "user", "content": "go"}], call_id="c1")
    assert mock.max_tokens == M.PLANNER_MAX_TOKENS == 1536 and mock.chat_requests()[0]["max_tokens"] == 1536
    assert M.AgentModel("http://x/v1", "m", planner_thinking=True).max_tokens == M.DEFAULT_MAX_TOKENS
    assert M.AgentModel("http://x/v1", "m", max_tokens=700).max_tokens == 700
    mock.chat([{"role": "user", "content": "go"}], call_id="c2", max_tokens=1100)
    assert mock.chat_requests()[1]["max_tokens"] == 1100
    # the context: --max-model-len of the served key's server_flags (default 32768)
    assert M.max_model_len_of({"server_flags": "--reasoning-parser qwen3 --max-model-len 16384 --max-num-seqs 4"}) \
        == 16384
    assert M.max_model_len_of({"server_flags": "--max-model-len=8192"}) == 8192
    assert M.max_model_len_of({"server_flags": "--max-num-seqs 4"}) == M.DEFAULT_MAX_MODEL_LEN == 32768
    # vLLM 0.30.0 human_readable_int_or_auto: k = 1000, K = 1024; auto / -1 = the model's own length (unknown here)
    assert M.max_model_len_of({"server_flags": "--max-model-len 32k"}) == 32000
    assert M.max_model_len_of({"server_flags": "--max-model-len 16K"}) == 16384
    assert M.max_model_len_of({"server_flags": "--max-model-len 25.6k"}) == 25600
    assert M.max_model_len_of({"server_flags": "--max-model-len auto"}) == 32768 == M.max_model_len_of(None)
    assert M.max_model_len_of({"server_flags": "--max-model-len 1.5K"}) == 32768
    assert M.from_check_yaml("http://127.0.0.1:8001/v1").max_model_len == 32768
    assert M.from_check_yaml("http://127.0.0.1:8001/v1", max_model_len=4000).max_model_len == 4000


def test_every_request_sends_the_repetition_stop_and_the_log_keeps_the_finish_reason(tmp_path):
    """Fails on the old code: the agent's chat and JSON calls had no repetition stop (the recognition client's
    ``REPETITION_DETECTION`` stopped P3's whitespace runs), and the call log dropped ``finish_reason``."""
    from wenart.agent import log as LG
    log = LG.AgentLog(tmp_path, "p")
    mock = M.MockModel(chat=[{"content": "x" * 10, "finish_reason": "repetition"}], on_call=log.call)
    reply = mock.chat([{"role": "user", "content": "go"}], call_id="c1")
    mock.critic([{"role": "user", "content": "look"}], SCHEMA, call_id="v1")
    assert reply.finish_reason == "repetition"
    for body in mock.requests:
        assert body["repetition_detection"] == VC.REPETITION_DETECTION == {"max_pattern_size": 4,
                                                                           "min_pattern_size": 1, "min_count": 16}
    assert [(c["call_id"], c["finish_reason"], c["max_tokens"]) for c in log.calls] == [
        ("c1", "repetition", 1536), ("v1", "stop", M.CRITIC_MAX_TOKENS)]
    assert "repetition_detection" not in M.chat_body("m", [], None)          # only when given
    off = M.AgentModel("http://x/v1", "m", repetition_detection=None, post=lambda u, b, t: ok_answer("y"))
    assert off.repetition_detection is None


def test_a_json_answer_stopped_for_repetition_is_asked_once_more_on_one_line():
    """Fails on the old code: the retry of an invalid JSON answer sent the same request again, which at temperature
    0 gives the same whitespace run; now the retry after a ``repetition`` stop carries the one-line note (the
    recognition client's compact retry)."""
    mock = M.MockModel(critic=[{"__raw__": '{"findings": [\n' + " " * 60, "__finish__": "repetition"},
                               {"findings": ["a"]}])
    good = mock.critic([{"role": "user", "content": [{"type": "text", "text": "look"}]}], SCHEMA, call_id="v1")
    first, second = mock.critic_requests()
    assert good.data == {"findings": ["a"]} and good.attempts == 2
    assert M.COMPACT_RETRY_NOTE == VC.COMPACT_RETRY_NOTE
    assert M.COMPACT_RETRY_NOTE not in json.dumps(first["messages"])
    assert second["messages"][-1]["content"][-1] == {"type": "text", "text": M.COMPACT_RETRY_NOTE}
    # an invalid answer that was not stopped for repetition is asked again as it was (M11 rule)
    plain = M.MockModel(critic=[{"__raw__": "no json"}, {"findings": []}])
    plain.critic([{"role": "user", "content": "look"}], SCHEMA, call_id="v2")
    assert plain.critic_requests()[0]["messages"] == plain.critic_requests()[1]["messages"]
