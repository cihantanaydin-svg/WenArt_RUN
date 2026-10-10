"""The agent model client (docs/milestone11.md §2 "Model client", §11 "Serving").

What: ``AgentModel`` talks to the OpenAI-compatible vLLM server of ``check.yaml models.agent``
(``Qwen/Qwen3.8-27B-FP8``) in two ways:

- ``chat(messages, tools)``: the planner. ``tools`` in the OpenAI ``tools`` format with ``strict: true``,
  ``tool_choice: "auto"``; the answer is text and/or tool calls;
- ``critic(messages, schema)``: the critic. ``response_format`` = ``{"type": "json_schema", "json_schema":
  {"name", "schema", "strict": true}}``, no tools, thinking off (``chat_template_kwargs.enable_thinking:
  false``); the answer is parsed and validated against the schema again in our code (one retry when it does not
  validate).

Why both: in vLLM 0.30.0 a forced tool call (``tool_choice: "required"``) and a JSON-schema ``response_format``
cannot be combined in one request (§11), so the planner uses ``auto`` tool calls and the critic structured output.

How: temperature 0 and seed 0 on every call (CLAUDE.md, AI calls); images as base64 PNG data URLs
(``wenart.recognition.vlm_client.encode_image``), at most ``MAX_IMAGES`` = 4 per call (the server's
``--limit-mm-per-prompt '{"image":4}'``): a request with more is refused before it is sent; transport errors and
HTTP 5xx are retried ``retries`` times; every call is logged (``calls`` and the ``on_call`` callback) with the
model id, revision, call id, tokens, seconds and attempts (§9). ``MockModel`` replays scripted answers through the
same parsing, validation and logging (the CPU tests, §10) and records every request.
"""
from __future__ import annotations

import copy
import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

from wenart.recognition import vlm_client as VC

MAX_IMAGES = 4                   # --limit-mm-per-prompt '{"image":4}' of the agent server (§11)
DEFAULT_MAX_TOKENS = 4096
CRITIC_MAX_TOKENS = 2048
THINKING_MAX_TOKENS = 8192       # a structured answer with thinking on: room for the reasoning before the JSON
DEFAULT_TIMEOUT_S = 600.0
DEFAULT_RETRIES = 2
IMAGE_MAX_SIDE = 1280            # a 960x540 preview is sent as it is; a 1920x1080 render is scaled down


class ModelError(RuntimeError):
    """The server did not give a usable answer after the retries."""


@dataclass
class ToolCall:
    """One tool call of the model. ``arguments`` is the raw JSON text; ``parsed`` the dict (None when the text is
    not a JSON object: the loop answers the model with the parse error)."""
    id: str
    name: str
    arguments: str
    parsed: Optional[dict] = None
    error: Optional[str] = None

    def to_message(self) -> dict:
        return {"id": self.id, "type": "function", "function": {"name": self.name, "arguments": self.arguments}}


@dataclass
class ModelReply:
    call_id: str
    content: str
    tool_calls: list = field(default_factory=list)
    usage: dict = field(default_factory=dict)
    seconds: float = 0.0
    attempts: int = 1
    finish_reason: Optional[str] = None

    def assistant_message(self) -> dict:
        msg: dict = {"role": "assistant", "content": self.content or ""}
        if self.tool_calls:
            msg["tool_calls"] = [tc.to_message() for tc in self.tool_calls]
        return msg


@dataclass
class CriticReply:
    call_id: str
    data: Optional[dict]
    errors: list = field(default_factory=list)
    raw: str = ""
    usage: dict = field(default_factory=dict)
    seconds: float = 0.0
    attempts: int = 1


# --------------------------------------------------------------------------
# Pure helpers: messages and request bodies
# --------------------------------------------------------------------------

def image_part(image, max_side: int = IMAGE_MAX_SIDE) -> dict:
    """An ``image_url`` content part (PNG data URL) of a path or PIL image."""
    url, _sent, _orig = VC.encode_image(image, max_side)
    return {"type": "image_url", "image_url": {"url": url}}


def user_message(text: str, images: Sequence = (), labels: Optional[Sequence[Optional[str]]] = None,
                 max_side: int = IMAGE_MAX_SIDE) -> dict:
    """A user message: each image (path, PIL image or a ready ``image_url`` part) after its optional label, then
    the text."""
    labels = list(labels) if labels is not None else [None] * len(images)
    if len(labels) != len(images):
        raise ValueError(f"{len(labels)} labels for {len(images)} images")
    content: list = []
    for label, img in zip(labels, images):
        if label:
            content.append({"type": "text", "text": label})
        content.append(img if isinstance(img, dict) and img.get("type") == "image_url" else image_part(img, max_side))
    content.append({"type": "text", "text": text})
    return {"role": "user", "content": content}


def count_images(messages: Sequence[dict]) -> int:
    n = 0
    for m in messages:
        content = m.get("content")
        if isinstance(content, list):
            n += sum(1 for part in content if isinstance(part, dict) and part.get("type") == "image_url")
    return n


def tool_spec(name: str, description: str, parameters: dict) -> dict:
    """One tool in the OpenAI ``tools`` format, ``strict: true`` (vLLM 0.30.0 accepts it with ``tool_choice:
    "auto"``; the arguments are validated again by ``tools.Registry``)."""
    params = {k: v for k, v in parameters.items() if k != "$schema"}
    return {"type": "function", "function": {"name": name, "description": description, "parameters": params,
                                             "strict": True}}


def template_kwargs(thinking: bool, extra: Optional[dict] = None) -> dict:
    """``chat_template_kwargs``: ``enable_thinking`` (Qwen3.x templates) plus the model's own keys from check.yaml
    (e.g. Muse Glimmer's ``reasoning_strength``, read from its chat template); a template ignores unknown keys."""
    out = {"enable_thinking": bool(thinking)}
    out.update(dict(extra or {}))
    return out


def chat_body(model: str, messages: list, tools: Optional[list], *, max_tokens: int = DEFAULT_MAX_TOKENS,
              thinking: bool = False, seed: int = 0, extra_template: Optional[dict] = None) -> dict:
    body = {"model": model, "messages": messages, "temperature": 0.0, "seed": seed, "max_tokens": max_tokens,
            "chat_template_kwargs": template_kwargs(thinking, extra_template)}
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    return body


def critic_body(model: str, messages: list, schema: dict, *, name: str = "findings",
                max_tokens: int = CRITIC_MAX_TOKENS, seed: int = 0, thinking: bool = False,
                extra_template: Optional[dict] = None) -> dict:
    return {"model": model, "messages": messages, "temperature": 0.0, "seed": seed, "max_tokens": max_tokens,
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": name, "schema": VC.grammar_of(schema), "strict": True}},
            "chat_template_kwargs": template_kwargs(thinking, extra_template)}


def parse_tool_calls(raw_calls: Any) -> list:
    out = []
    for i, tc in enumerate(raw_calls or []):
        fn = (tc or {}).get("function") or {}
        args = fn.get("arguments")
        text = args if isinstance(args, str) else json.dumps(args if args is not None else {})
        call = ToolCall(id=str(tc.get("id") or f"call_{i}"), name=str(fn.get("name") or ""), arguments=text)
        try:
            parsed = json.loads(text) if text.strip() else {}
            if isinstance(parsed, dict):
                call.parsed = parsed
            else:
                call.error = "the arguments are not a JSON object"
        except ValueError as exc:
            call.error = f"the arguments are not valid JSON ({exc})"
        out.append(call)
    return out


# --------------------------------------------------------------------------
# The client
# --------------------------------------------------------------------------

class AgentModel:
    """The vLLM client of the agent model (module docstring)."""

    def __init__(self, base_url: str, model: str, revision: str = "", *, timeout_s: float = DEFAULT_TIMEOUT_S,
                 retries: int = DEFAULT_RETRIES, max_tokens: int = DEFAULT_MAX_TOKENS, planner_thinking: bool = False,
                 post: Optional[Callable[[str, dict, float], dict]] = None, clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], None] = time.sleep, on_call: Optional[Callable[[dict], None]] = None,
                 critic_thinking: bool = False, extra_template: Optional[dict] = None,
                 thinking_max_tokens: int = 0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.revision = revision
        self.timeout_s = float(timeout_s)
        self.retries = int(retries)
        self.max_tokens = int(max_tokens)
        self.planner_thinking = bool(planner_thinking)
        # Milestone 12 (bake-off, docs/milestone12.md §5.1): the critic with thinking on, and the model's own chat
        # template keys from check.yaml.
        self.critic_thinking = bool(critic_thinking)
        self.extra_template = dict(extra_template or {})
        self.thinking_max_tokens = int(thinking_max_tokens or THINKING_MAX_TOKENS)
        self._post = post or VC.post_json
        self.clock = clock
        self.sleep = sleep
        self.on_call = on_call
        self.calls: list[dict] = []

    # ----- transport ------------------------------------------------------------

    def _send(self, body: dict) -> tuple[dict, int, float]:
        """POST with retries; ``(response, attempts, seconds)``; ModelError after the last attempt."""
        t0 = self.clock()
        last = None
        for attempt in range(1, self.retries + 2):
            try:
                resp = self.post(body)
                return resp, attempt, self.clock() - t0
            except VC.VLMError as exc:
                last = exc
                if attempt <= self.retries:
                    self.sleep(min(30.0, 2.0 * attempt))
        raise ModelError(f"{self.model}: {last}")

    def post(self, body: dict) -> dict:
        return self._post(f"{self.base_url}/chat/completions", body, self.timeout_s)

    def _log(self, entry: dict) -> None:
        entry = dict(entry, model=self.model, revision=self.revision)
        self.calls.append(entry)
        if self.on_call is not None:
            self.on_call(entry)

    @staticmethod
    def _check_images(messages: list) -> int:
        n = count_images(messages)
        if n > MAX_IMAGES:
            raise ValueError(f"{n} images in one call: the agent server takes at most {MAX_IMAGES}")
        return n

    @staticmethod
    def _message(resp: dict) -> tuple[dict, Optional[str], dict]:
        choices = resp.get("choices") or []
        if not choices:
            raise ModelError(f"no choices in the answer: {json.dumps(resp)[:300]}")
        return choices[0].get("message") or {}, choices[0].get("finish_reason"), dict(resp.get("usage") or {})

    # ----- the two kinds of calls ------------------------------------------------

    def chat(self, messages: list, tools: Optional[list] = None, *, call_id: str,
             max_tokens: Optional[int] = None) -> ModelReply:
        """The planner's call: tools offered, ``tool_choice: auto`` (thinking as ``planner_thinking``)."""
        images = self._check_images(messages)
        body = chat_body(self.model, messages, tools, max_tokens=max_tokens or self.max_tokens,
                         thinking=self.planner_thinking, extra_template=self.extra_template)
        try:
            resp, attempts, seconds = self._send(body)
            msg, finish, usage = self._message(resp)
        except ModelError as exc:
            self._log({"call_id": call_id, "kind": "chat", "images": images, "error": str(exc), "seconds": None,
                       "attempts": self.retries + 1, "prompt_tokens": None, "completion_tokens": None})
            raise
        reply = ModelReply(call_id=call_id, content=str(msg.get("content") or ""),
                           tool_calls=parse_tool_calls(msg.get("tool_calls")), usage=usage,
                           seconds=round(seconds, 3), attempts=attempts, finish_reason=finish)
        self._log({"call_id": call_id, "kind": "chat", "images": images, "error": None,
                   "seconds": reply.seconds, "attempts": attempts, "tool_calls": len(reply.tool_calls),
                   "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens")})
        return reply

    def critic(self, messages: list, schema: dict, *, call_id: str, name: str = "findings") -> CriticReply:
        """The critic's call: a JSON-schema answer, validated here; one more try when it does not validate. Thinking
        as ``critic_thinking`` (off in M11; the M12 bake-off measures both)."""
        return self.structured(messages, schema, call_id=call_id, name=name, kind="critic",
                               thinking=self.critic_thinking)

    def structured(self, messages: list, schema: dict, *, call_id: str, name: str = "answer", kind: str = "critic",
                   thinking: bool = False, max_tokens: Optional[int] = None) -> CriticReply:
        """A JSON-schema answer (the critic, the M12 room plan, the bake-off tasks): validated here, one more try
        when it does not validate; ``kind`` names the call in the log (critic | plan | task)."""
        images = self._check_images(messages)
        limit = max_tokens or (self.thinking_max_tokens if thinking else CRITIC_MAX_TOKENS)
        body = critic_body(self.model, messages, schema, name=name, max_tokens=limit, thinking=thinking,
                           extra_template=self.extra_template)
        attempts_total, seconds_total, usage = 0, 0.0, {}
        errors: list = []
        raw = ""
        data = None
        for _try in range(2):
            try:
                resp, attempts, seconds = self._send(body)
                msg, _finish, usage = self._message(resp)
            except ModelError as exc:
                self._log({"call_id": call_id, "kind": kind, "images": images, "error": str(exc),
                           "seconds": None, "attempts": attempts_total + self.retries + 1, "prompt_tokens": None,
                           "completion_tokens": None})
                raise
            attempts_total += attempts
            seconds_total += seconds
            raw = str(msg.get("content") or "")
            try:
                data = VC.parse_answer(raw)
                errors = VC.schema_errors(schema, data)
            except ValueError as exc:
                data, errors = None, [f"not JSON: {exc}"]
            if not errors:
                break
            data = None
        self._log({"call_id": call_id, "kind": kind, "images": images, "error": "; ".join(errors[:3]) or None,
                   "seconds": round(seconds_total, 3), "attempts": attempts_total,
                   "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens")})
        return CriticReply(call_id=call_id, data=data, errors=errors, raw=raw, usage=usage,
                           seconds=round(seconds_total, 3), attempts=attempts_total)


class MockModel(AgentModel):
    """Scripted answers for the CPU tests (§10). ``chat``: a list of planner answers, each ``{"tool_calls":
    [{"name", "arguments": dict | str}], "content": str}`` or a callable ``(body) -> answer``; ``critic``: a list
    of critic answers (the JSON data; ``{"__raw__": "text"}`` for a raw text answer) or callables; ``plan`` (M12): the
    room plans (JSON-schema calls named ``plan``), the same way. An exhausted script answers with no tool call
    (planner), ``{"findings": []}`` (critic) or an empty, invalid plan (the loop then uses the brief's default
    checklist). Every request body is kept in ``requests`` (images included). Thread-safe (parallel sessions)."""

    def __init__(self, chat: Sequence = (), critic: Sequence = (), *, plan: Sequence = (), model: str = "mock/agent",
                 revision: str = "mock-rev", on_call: Optional[Callable[[dict], None]] = None):
        super().__init__("http://mock/v1", model, revision, on_call=on_call, clock=self._tick, sleep=lambda s: None)
        self.chat_script = list(chat)
        self.critic_script = list(critic)
        self.plan_script = list(plan)
        self.requests: list[dict] = []
        self._t = 0.0
        self._n = 0
        self._lock = threading.RLock()

    def _tick(self) -> float:
        with self._lock:
            self._t += 0.5
            return self._t

    @staticmethod
    def schema_name(body: dict) -> Optional[str]:
        return ((body.get("response_format") or {}).get("json_schema") or {}).get("name")

    def post(self, body: dict) -> dict:
        with self._lock:
            self.requests.append(copy.deepcopy(body))
            self._n += 1
            n = self._n
            usage = {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120}
            if "response_format" in body:
                if self.schema_name(body) == "plan":
                    item = self.plan_script.pop(0) if self.plan_script else {"__raw__": "{}"}
                else:
                    item = self.critic_script.pop(0) if self.critic_script else {"findings": []}
            else:
                item = self.chat_script.pop(0) if self.chat_script else {"content": "done"}
        item = item(body) if callable(item) else item
        if "response_format" in body:
            text = item["__raw__"] if isinstance(item, dict) and "__raw__" in item else json.dumps(item)
            return {"choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}],
                    "usage": usage}
        calls = []
        for i, tc in enumerate(item.get("tool_calls") or []):
            args = tc.get("arguments", {})
            calls.append({"id": tc.get("id") or f"call_{n}_{i}", "type": "function",
                          "function": {"name": tc["name"],
                                       "arguments": args if isinstance(args, str) else json.dumps(args)}})
        msg = {"role": "assistant", "content": item.get("content") or ""}
        if calls:
            msg["tool_calls"] = calls
        return {"choices": [{"message": msg, "finish_reason": "tool_calls" if calls else "stop"}], "usage": usage}

    def chat_requests(self) -> list:
        return [r for r in self.requests if "response_format" not in r]

    def critic_requests(self) -> list:
        return [r for r in self.requests if "response_format" in r and self.schema_name(r) != "plan"]

    def plan_requests(self) -> list:
        return [r for r in self.requests if self.schema_name(r) == "plan"]


def from_check_yaml(base_url: str, key: str = "agent", check_yaml: Optional[Path] = None, **kwargs) -> AgentModel:
    """The client of ``check.yaml models.<key>`` (id, revision) at ``base_url``."""
    from wenart.run import servers as SV
    models = SV.check_models(check_yaml) if check_yaml else SV.check_models()
    m = models[key]
    return AgentModel(base_url, str(m["id"]), str(m.get("revision") or ""), **kwargs)
