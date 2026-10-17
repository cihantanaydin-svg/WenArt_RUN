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

Fix round after P3 (16-17 Oct 2026; docs/milestone13.md §14.8 "Attempt 2"):

- What: an HTTP 4xx answer is not retried (only 408 and 429 are); vLLM's "maximum context length" 400 raises
  ``ContextFullError`` (a ``ModelError``) with the prompt size the server names; every error carries the real
  number of POSTs (``attempts``), which the call log records. ``AgentModel.max_model_len`` is the served model's
  ``--max-model-len`` (``max_model_len_of``: the key's ``server_flags`` in check.yaml, default 32768), read by the
  loop's context budget. The planner's chat answer is capped at ``PLANNER_MAX_TOKENS`` = 1536 tokens (thinking
  off; P3: p50 109, p99 609, the largest valid answer 1,086). Every chat and JSON-schema call sends vLLM 0.30.0's
  ``repetition_detection`` (``vlm_client.REPETITION_DETECTION``, as the recognition client does), the call log keeps
  ``finish_reason`` and ``max_tokens``, and a JSON answer stopped for repetition is asked again once with a one-line
  note (the same request at temperature 0 gives the same run).
- Why: in P3 the building session's 5th planner call got HTTP 400 "maximum context length is 32768 tokens"; the
  client sent the same 400 twice more, logged 3 attempts as if the server were down, and the round stopped with
  "the agent model did not answer" although the model had answered 4 times. One planner answer ran to its 4,096
  tokens (r3-s18-p3, 91 s) and filled the session's context.
- How: ``_send`` reads the status from the ``VLMError`` text (``vlm_client.post_json``: "HTTP <code> from ...").
"""
from __future__ import annotations

import copy
import json
import re
import shlex
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional, Sequence

from wenart.recognition import vlm_client as VC

MAX_IMAGES = 4                   # --limit-mm-per-prompt '{"image":4}' of the agent server (§11)
DEFAULT_MAX_TOKENS = 4096
# Fix round after P3: the planner's chat answer with thinking off (P3 real04: 1,068 answers, p50 109, p99 609, the
# largest valid one 1,086 tokens; one runaway answer of 4,096 tokens filled a session's context). With thinking on
# the reasoning counts too, so the planner keeps DEFAULT_MAX_TOKENS.
PLANNER_MAX_TOKENS = 1536
CRITIC_MAX_TOKENS = 2048
THINKING_MAX_TOKENS = 8192       # a structured answer with thinking on: room for the reasoning before the JSON
DEFAULT_TIMEOUT_S = 600.0
DEFAULT_RETRIES = 2
IMAGE_MAX_SIDE = 1280            # a 960x540 preview is sent as it is; a 1920x1080 render is scaled down
# Fix round after P3: the server's context (``--max-model-len`` of check.yaml models.agent and agent_fast) when the
# served key's flags do not name it.
DEFAULT_MAX_MODEL_LEN = 32768
# HTTP 4xx answers that may pass on a retry (request timeout, too many requests); every other 4xx is the request's
# own fault and is the same on every retry.
RETRY_4XX = (408, 429)
# vLLM's 400 when the prompt plus max_tokens pass --max-model-len (P3: "This model's maximum context length is
# 32768 tokens. However, you requested 4096 output tokens and your prompt contains at least 28673 input tokens").
CONTEXT_FULL_TEXTS = ("maximum context length", "maximum model length")
_PROMPT_AT_LEAST = re.compile(r"prompt contains at least (\d+) input tokens")
# The note of the one retry after a JSON answer stopped for repetition (= vlm_client.COMPACT_RETRY_NOTE).
COMPACT_RETRY_NOTE = VC.COMPACT_RETRY_NOTE


class ModelError(RuntimeError):
    """The server did not give a usable answer after the retries. ``attempts``: the POSTs sent (fix round after P3:
    the call log records this number, not the retry setting); ``status``: the HTTP status of the last answer (None
    for a transport error)."""

    def __init__(self, message: str, *, attempts: int = 0, status: Optional[int] = None):
        super().__init__(message)
        self.attempts = int(attempts)
        self.status = status


class ContextFullError(ModelError):
    """Fix round after P3: the server refused the request because the prompt plus ``max_tokens`` pass its context
    (``--max-model-len``). Never retried as it is; ``prompt_tokens``: the prompt size the server names ("at least
    N input tokens"; None when it names none)."""

    def __init__(self, message: str, *, attempts: int = 0, status: Optional[int] = None,
                 prompt_tokens: Optional[int] = None):
        super().__init__(message, attempts=attempts, status=status)
        self.prompt_tokens = prompt_tokens


def http_status(exc) -> Optional[int]:
    """The HTTP status of a ``VLMError`` ("HTTP 400 from <url>: ..."), None for a transport error."""
    m = re.match(r"\s*HTTP (\d{3})\b", str(exc))
    return int(m.group(1)) if m else None


def is_context_full(text: str) -> bool:
    """vLLM's answer to a prompt that does not fit the context (``CONTEXT_FULL_TEXTS``)."""
    low = str(text).lower()
    return any(t in low for t in CONTEXT_FULL_TEXTS)


def prompt_tokens_floor(text: str) -> Optional[int]:
    """The prompt size a context-full answer names ("your prompt contains at least N input tokens"), else None."""
    m = _PROMPT_AT_LEAST.search(str(text))
    return int(m.group(1)) if m else None


_HUMAN_INT = re.compile(r"(\d+(?:\.\d+)?)([kKmMgGtT])")
_DECIMAL = {"k": 10 ** 3, "m": 10 ** 6, "g": 10 ** 9, "t": 10 ** 12}
_BINARY = {"K": 2 ** 10, "M": 2 ** 20, "G": 2 ** 30, "T": 2 ** 40}


def human_int(text: str) -> Optional[int]:
    """vLLM 0.30.0's ``--max-model-len`` value (``vllm/utils/argparse_utils.py`` ``human_readable_int_or_auto``, read
    17 Oct 2026): a plain integer, or a number with a decimal (k, m, g, t: x1000 ...) or binary (K, M, G, T: x1024
    ..., integers only) suffix; ``-1`` / ``auto`` (the model's own length) and anything else give None."""
    value = str(text).strip()
    m = _HUMAN_INT.fullmatch(value)
    try:
        if m:
            number, suffix = m.groups()
            return int(float(number) * _DECIMAL[suffix]) if suffix in _DECIMAL else int(number) * _BINARY[suffix]
        n = int(value)
    except (KeyError, ValueError):
        return None
    return n if n > 0 else None


def max_model_len_of(entry: Optional[dict], default: int = DEFAULT_MAX_MODEL_LEN) -> int:
    """Fix round after P3: the context of a check.yaml model entry: ``--max-model-len N`` (or ``=N``, ``human_int``)
    of its ``server_flags``; ``default`` when the flags do not name it or name no positive length (``auto``)."""
    flags = str((entry or {}).get("server_flags") or "") if isinstance(entry, dict) else ""
    try:
        words = shlex.split(flags)
    except ValueError:
        words = flags.split()
    value = None
    for i, w in enumerate(words):
        if w == "--max-model-len" and i + 1 < len(words):
            value = words[i + 1]
        elif w.startswith("--max-model-len="):
            value = w.split("=", 1)[1]
    n = human_int(value) if value is not None else None
    return n if n else int(default)


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
              thinking: bool = False, seed: int = 0, extra_template: Optional[dict] = None,
              repetition_detection: Optional[dict] = None) -> dict:
    """The planner's request. ``repetition_detection`` (fix round after P3; vLLM 0.30.0 request field, see
    ``vlm_client.REPETITION_DETECTION``) is sent only when given."""
    body = {"model": model, "messages": messages, "temperature": 0.0, "seed": seed, "max_tokens": max_tokens,
            "chat_template_kwargs": template_kwargs(thinking, extra_template)}
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"
    if repetition_detection is not None:
        body["repetition_detection"] = dict(repetition_detection)
    return body


def critic_body(model: str, messages: list, schema: dict, *, name: str = "findings",
                max_tokens: int = CRITIC_MAX_TOKENS, seed: int = 0, thinking: bool = False,
                extra_template: Optional[dict] = None, repetition_detection: Optional[dict] = None) -> dict:
    """A JSON-schema request (critic, plan, task); ``repetition_detection`` as in ``chat_body``."""
    body = {"model": model, "messages": messages, "temperature": 0.0, "seed": seed, "max_tokens": max_tokens,
            "response_format": {"type": "json_schema",
                                "json_schema": {"name": name, "schema": VC.grammar_of(schema), "strict": True}},
            "chat_template_kwargs": template_kwargs(thinking, extra_template)}
    if repetition_detection is not None:
        body["repetition_detection"] = dict(repetition_detection)
    return body


def with_compact_note(messages: list) -> list:
    """``messages`` with ``COMPACT_RETRY_NOTE`` added to the last user message (a copy; the images are shared): the
    retry after a JSON answer stopped for repetition is another request, so greedy decoding takes another path."""
    out = list(messages)
    for i in range(len(out) - 1, -1, -1):
        m = out[i]
        if m.get("role") != "user":
            continue
        content = m.get("content")
        if isinstance(content, list):
            out[i] = dict(m, content=list(content) + [{"type": "text", "text": COMPACT_RETRY_NOTE}])
        else:
            out[i] = dict(m, content=f"{content or ''}\n\n{COMPACT_RETRY_NOTE}")
        return out
    return out + [{"role": "user", "content": COMPACT_RETRY_NOTE}]


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
                 retries: int = DEFAULT_RETRIES, max_tokens: Optional[int] = None, planner_thinking: bool = False,
                 post: Optional[Callable[[str, dict, float], dict]] = None, clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], None] = time.sleep, on_call: Optional[Callable[[dict], None]] = None,
                 critic_thinking: bool = False, extra_template: Optional[dict] = None,
                 thinking_max_tokens: int = 0, max_model_len: int = DEFAULT_MAX_MODEL_LEN,
                 repetition_detection: Optional[dict] = VC.REPETITION_DETECTION):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.revision = revision
        self.timeout_s = float(timeout_s)
        self.retries = int(retries)
        self.planner_thinking = bool(planner_thinking)
        # Fix round after P3: the planner's answer budget (``PLANNER_MAX_TOKENS`` with thinking off) and the served
        # context (the loop budgets every planner prompt against it); the repetition stop of every request.
        self.max_tokens = int(max_tokens) if max_tokens else (DEFAULT_MAX_TOKENS if self.planner_thinking
                                                              else PLANNER_MAX_TOKENS)
        self.max_model_len = int(max_model_len or DEFAULT_MAX_MODEL_LEN)
        self.repetition_detection = None if repetition_detection is None else dict(repetition_detection)
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
        """POST with retries; ``(response, attempts, seconds)``; ModelError after the last attempt. Fix round after
        P3: an HTTP 4xx answer (but 408 and 429) is the request's own fault and is raised at once, a context-full 400
        as ``ContextFullError``; the error carries the POSTs sent (``attempts``)."""
        t0 = self.clock()
        last = None
        status = None
        for attempt in range(1, self.retries + 2):
            try:
                resp = self.post(body)
                return resp, attempt, self.clock() - t0
            except VC.VLMError as exc:
                last = exc
                status = http_status(exc)
                if status is not None and 400 <= status < 500 and status not in RETRY_4XX:
                    if is_context_full(str(exc)):
                        raise ContextFullError(f"{self.model}: {exc}", attempts=attempt, status=status,
                                               prompt_tokens=prompt_tokens_floor(str(exc))) from exc
                    raise ModelError(f"{self.model}: {exc}", attempts=attempt, status=status) from exc
                if attempt <= self.retries:
                    self.sleep(min(30.0, 2.0 * attempt))
        raise ModelError(f"{self.model}: {last}", attempts=self.retries + 1, status=status)

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
        """The planner's call: tools offered, ``tool_choice: auto`` (thinking as ``planner_thinking``). Fix round
        after P3: the repetition stop in the request; the call log records the real attempts (also of an error), the
        answer's ``finish_reason`` and the ``max_tokens`` asked for."""
        images = self._check_images(messages)
        limit = int(max_tokens or self.max_tokens)
        body = chat_body(self.model, messages, tools, max_tokens=limit, thinking=self.planner_thinking,
                         extra_template=self.extra_template, repetition_detection=self.repetition_detection)
        try:
            resp, attempts, seconds = self._send(body)
            msg, finish, usage = self._message(resp)
        except ModelError as exc:
            self._log({"call_id": call_id, "kind": "chat", "images": images, "error": str(exc), "seconds": None,
                       "attempts": exc.attempts or self.retries + 1, "prompt_tokens": None,
                       "completion_tokens": None, "max_tokens": limit,
                       "finish_reason": "context_full" if isinstance(exc, ContextFullError) else None})
            raise
        reply = ModelReply(call_id=call_id, content=str(msg.get("content") or ""),
                           tool_calls=parse_tool_calls(msg.get("tool_calls")), usage=usage,
                           seconds=round(seconds, 3), attempts=attempts, finish_reason=finish)
        self._log({"call_id": call_id, "kind": "chat", "images": images, "error": None,
                   "seconds": reply.seconds, "attempts": attempts, "tool_calls": len(reply.tool_calls),
                   "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                   "max_tokens": limit, "finish_reason": finish})
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
                           extra_template=self.extra_template, repetition_detection=self.repetition_detection)
        attempts_total, seconds_total, usage = 0, 0.0, {}
        errors: list = []
        raw = ""
        data = None
        finish = None
        for _try in range(2):
            try:
                resp, attempts, seconds = self._send(body)
                msg, finish, usage = self._message(resp)
            except ModelError as exc:
                self._log({"call_id": call_id, "kind": kind, "images": images, "error": str(exc),
                           "seconds": None, "attempts": attempts_total + (exc.attempts or self.retries + 1),
                           "prompt_tokens": None, "completion_tokens": None, "max_tokens": limit,
                           "finish_reason": "context_full" if isinstance(exc, ContextFullError) else None})
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
            if finish == "repetition":
                # fix round after P3: the same request at temperature 0 gives the same run; the retry asks for one
                # line (vlm_client's compact retry)
                body = dict(body, messages=with_compact_note(body["messages"]))
        self._log({"call_id": call_id, "kind": kind, "images": images, "error": "; ".join(errors[:3]) or None,
                   "seconds": round(seconds_total, 3), "attempts": attempts_total,
                   "prompt_tokens": usage.get("prompt_tokens"), "completion_tokens": usage.get("completion_tokens"),
                   "max_tokens": limit, "finish_reason": finish})
        return CriticReply(call_id=call_id, data=data, errors=errors, raw=raw, usage=usage,
                           seconds=round(seconds_total, 3), attempts=attempts_total)


class MockModel(AgentModel):
    """Scripted answers for the CPU tests (§10). ``chat``: a list of planner answers, each ``{"tool_calls":
    [{"name", "arguments": dict | str}], "content": str}`` or a callable ``(body) -> answer``; ``critic``: a list
    of critic answers (the JSON data; ``{"__raw__": "text"}`` for a raw text answer, with ``"__finish__"`` its finish
    reason, e.g. ``repetition``; a planner answer may name its ``finish_reason`` and its ``usage``, else every answer
    reports 100 prompt tokens) or callables (one may raise ``VLMError``: a server error); ``plan`` (M12): the
    room plans (JSON-schema calls named ``plan``), the same way. An exhausted script answers with no tool call
    (planner), ``{"findings": []}`` (critic) or an empty, invalid plan (the loop then uses the brief's default
    checklist). Every request body is kept in ``requests`` (images included). Thread-safe (parallel sessions)."""

    def __init__(self, chat: Sequence = (), critic: Sequence = (), *, plan: Sequence = (), model: str = "mock/agent",
                 revision: str = "mock-rev", on_call: Optional[Callable[[dict], None]] = None,
                 max_model_len: int = DEFAULT_MAX_MODEL_LEN):
        super().__init__("http://mock/v1", model, revision, on_call=on_call, clock=self._tick, sleep=lambda s: None,
                         max_model_len=max_model_len)
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
        if isinstance(item, dict) and isinstance(item.get("usage"), dict):
            usage = dict(usage, **item["usage"])         # a scripted prompt size (the context-budget tests)
        if "response_format" in body:
            text = item["__raw__"] if isinstance(item, dict) and "__raw__" in item else json.dumps(item)
            finish = item.get("__finish__", "stop") if isinstance(item, dict) and "__raw__" in item else "stop"
            return {"choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": finish}],
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
        finish = item.get("finish_reason") or ("tool_calls" if calls else "stop")
        return {"choices": [{"message": msg, "finish_reason": finish}], "usage": usage}

    def chat_requests(self) -> list:
        return [r for r in self.requests if "response_format" not in r]

    def critic_requests(self) -> list:
        return [r for r in self.requests if "response_format" in r and self.schema_name(r) != "plan"]

    def plan_requests(self) -> list:
        return [r for r in self.requests if self.schema_name(r) == "plan"]


def variant_kwargs(entry: dict, variant: Optional[str]) -> dict:
    """The client options of one bake-off variant (``check.yaml models.bakeoff.<name>.variants.<variant>``):
    ``critic_thinking`` (also the planner's thinking: a variant is measured as one setting) and ``template`` (the
    model's own chat-template keys). ``KeyError`` for a variant the entry does not have."""
    if not variant:
        return {}
    v = (entry.get("variants") or {})[variant]
    thinking = bool(v.get("critic_thinking"))
    return {"critic_thinking": thinking, "planner_thinking": thinking, "extra_template": dict(v.get("template") or {})}


def from_check_yaml(base_url: str, key: str = "agent", check_yaml: Optional[Path] = None, *,
                    variant: Optional[str] = None, **kwargs) -> AgentModel:
    """The client of ``check.yaml models.<key>`` (id, revision) at ``base_url``; M12: a dotted key names a nested
    entry (``bakeoff.fp8``) and ``variant`` one of its bake-off variants (``variant_kwargs``)."""
    from wenart.run import servers as SV
    models = SV.check_models(check_yaml) if check_yaml else SV.check_models()
    m = SV.model_entry(models, key)
    if not m or not m.get("id"):
        raise KeyError(f"no model '{key}' in check.yaml")
    # fix round after P3: the served context of this key (the loop budgets the planner's prompts against it)
    opts = dict(variant_kwargs(m, variant), **dict({"max_model_len": max_model_len_of(m)}, **kwargs))
    return AgentModel(base_url, str(m["id"]), str(m.get("revision") or ""), **opts)
