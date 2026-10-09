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
