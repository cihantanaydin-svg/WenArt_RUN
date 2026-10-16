"""OpenAI-compatible client for a local vLLM server (``vllm serve``).

What it does: sends one image plus one task prompt to ``/v1/chat/completions``
with temperature 0, seed 0 and the task's JSON schema as the structured-output
grammar, then parses and validates the answer and records the latency.

Verified against vLLM 0.30.0 (docs/features/structured_outputs.md and
docs/serving/online_serving/openai_compatible_server.md at tag v0.30.0):

- the request field is ``"structured_outputs": {"json": <schema>}`` (the old
  ``guided_json`` was removed in v0.12.0); it is an extra, non-OpenAI field
  that goes straight into the JSON body;
- images go in the message content as
  ``{"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}``
  (docs/features/multimodal_inputs.md, online serving section);
- ``seed`` and ``temperature`` are standard chat-completion fields;
- ``chat_template_kwargs: {"enable_thinking": false}`` switches GLM-4.xV
  thinking off (its chat template emits ``<think></think>`` for that value);
  Qwen3-VL-Instruct has no thinking and ignores the kwarg.

Only the standard library is used for HTTP (urllib), so the module imports
without the ``openai`` package. Pillow is imported lazily for image encoding.

Box convention: the models answer boxes normalised to 0..1000 of the image
width/height (schemas.py); ``boxes_to_pixels`` converts them to pixels of the
original page, which does not depend on any downscaling done before sending.

Milestone 5 (docs/milestone5.md §1.5): ``build_request(..., images=[...],
labels=[...])`` sends several images in one user message (image parts in
order, each optionally preceded by a text label, then the prompt), and
``VLMClient.run_schema`` runs any caller-made JSON schema on a list of images
with the same transport, retries and jsonschema validation, without box
conversion. vLLM 0.30.0 accepts several ``image_url`` parts in one message and
text interleaved with them (docs/features/multimodal_inputs.md, online
serving); the server must be started with ``--limit-mm-per-prompt`` allowing
that many images.

Milestone 13 round 4 (pod P3, 16 Oct 2026): Qwen3-VL-8B answered 5 of 8
``sheet_region`` questions with an endless run of blank lines inside the JSON
(``{"class": ..., "variant_word": null`` then ``"\\n  "`` until max_tokens 4096,
about 50 s per request); the client sent the same request 3 times (151 s per
item, every time the same answer at temperature 0) and the regions stayed
decided by title and geometry (``results/recognition/real04/sheets/
answers_qwen3-vl-8b.json``, ``run/real04/logs/recognize.log``). Checked in the
vLLM v0.30.0 source (tag v0.30.0 on github.com):

- the whitespace switch is server-wide only: ``StructuredOutputsConfig.
  disable_any_whitespace`` (``vllm/config/structured_outputs.py``; only with the
  ``xgrammar`` or ``guidance`` backend, the default ``auto`` refuses it). The
  request fields ``structured_outputs.disable_any_whitespace`` and
  ``whitespace_pattern`` exist (``vllm/sampling_params.py``
  ``StructuredOutputsParams``) but the V1 xgrammar and guidance backends never
  read them (``backend_xgrammar.py`` / ``backend_guidance.py`` read
  ``vllm_config.structured_outputs_config.disable_any_whitespace``), so they are
  not sent. The real fix is the server flag ``--structured-outputs-config
  '{"backend": "xgrammar", "disable_any_whitespace": true}'`` (``vllm serve``,
  ``wenart/run/servers.py`` / ``check.yaml server_flags``; not in this module).
  Checked with xgrammar 0.2.8 and the Qwen3-VL-8B tokenizer: with
  ``any_whitespace=False`` the only token allowed after the P3 prefix is ``,``.
- per request, ``repetition_detection`` (``ChatCompletionRequest``,
  ``vllm/entrypoints/openai/chat_completion/protocol.py``; fields
  ``max_pattern_size``, ``min_pattern_size``, ``min_count`` of
  ``RepetitionDetectionParams``; ``vllm/v1/core/sched/utils.py``
  ``check_stop`` ends the request with finish reason ``repetition`` when the last
  ``min_count`` x n tokens repeat one n-gram, n in min..max) stops such a run
  after a few dozen tokens when its token stream is periodic (estimated offline,
  not measured on the pod; see ``REPETITION_DETECTION``). Every ``VLMClient``
  request sends ``REPETITION_DETECTION``.

The guard of this client (``_post``): an answer that does not parse and ends in
a whitespace run (or stopped for repetition) is first repaired by closing its
open objects (only when the run is at the end, so no value was cut, no array
is open, and the result holds every property and passes the schema);
otherwise it is asked once more with a
note asking for one-line JSON (a different prompt: at temperature 0 the same
request gives the same run), never the same request again. An answer cut by a
schema-sized ``max_tokens`` (``schema_max_tokens``) is asked once more with the
client's ``max_tokens``. Every step is recorded in ``VLMResult.guard``.
"""
from __future__ import annotations

import base64
import copy
import io
import json
import math
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from wenart.recognition import prompts, schemas

DEFAULT_BASE_URL = "http://127.0.0.1:8000/v1"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_MAX_SIDE = 1600  # longest image side sent to the model, in pixels (0 = original size)

# vLLM 0.30.0 ``repetition_detection`` (module docstring): stop when the last 16 x n output tokens are one n-gram
# (n = 1..4) repeated 16 times. Checked with vLLM's rule and the Qwen3-VL-8B tokenizer on the stored answers (16 Oct
# 2026): none of the 443 distinct schema-valid recognition answers (both models, all runs) would have been stopped,
# nor any of the 5,917 distinct parsed answers of every stage in the repository (vision check 1,373, library 3,245,
# furniture 422, realism 359, test fixtures 75; review of round 4); the 5 P3 whitespace runs, re-tokenized, stop at
# token 38-39. This is an estimate: the pod generated about 2 characters per token in those runs (8,145 run
# characters in about 4,075 tokens) while the re-tokenized text has about 6, so the real token stream differs; a run
# that is not periodic within 4 tokens is not stopped and ends at the schema-sized max_tokens (1,322 tokens for
# sheet_region, about 15 s at the 87 tokens/s per sequence of vllm-qwen.log) before the guard of ``_post``.
REPETITION_DETECTION: dict = {"max_pattern_size": 4, "min_pattern_size": 1, "min_count": 16}
# A run of at least this many whitespace characters with 2 or more line breaks, outside JSON strings, in an answer
# that does not parse, is a whitespace run (pretty-printed JSON indents by at most ~20 characters per line).
WHITESPACE_RUN_CHARS = 16
# The one guard retry after a whitespace run (appended to the prompt text, so greedy decoding takes another path).
COMPACT_RETRY_NOTE = "Write the JSON answer on one line, with no line breaks and no indentation."
# ``schema_max_tokens``: a string without maxLength counts as this many characters (= REASON_MAX_CHARS of the
# questions); a number as NUMBER_CHARS; every value gets ELEMENT_EXTRA characters for its key quotes, colon, comma
# and indentation; the sum is an upper bound in characters, and the budget is ``ceil(chars x factor) + margin``
# tokens. Measured with the Qwen3-VL-8B tokenizer: a Turkish string costs 0.92 tokens per character, the longest
# stored answers 2.0-3.2 characters per token (85 tokens at most).
FREE_STRING_CHARS = 160
NUMBER_CHARS = 24
ELEMENT_EXTRA = 8
MAX_TOKENS_FACTOR = 2.0
MAX_TOKENS_MARGIN = 64

# System prompt of ``run_schema`` (the default of ``build_request`` is about Turkish drawings).
SCHEMA_SYSTEM_PROMPT = (
    "You look at images and answer only with JSON that follows the given schema. Report only "
    "what is visible in the images. Never invent elements. When unsure, say so in the answer."
)


class VLMError(RuntimeError):
    """Transport or protocol error talking to the server."""


@dataclass
class VLMResult:
    """One model call. ``data`` is the schema-valid answer (boxes in page pixels) or None."""
    task: str
    model: str
    data: Optional[dict]
    raw_text: str
    latency_s: float
    attempts: int
    error: Optional[str] = None
    usage: dict = field(default_factory=dict)
    image_size: tuple[int, int] = (0, 0)       # size of the image as sent
    page_size: tuple[int, int] = (0, 0)        # size of the original page image
    max_tokens: int = 0                        # max_tokens of the first request (0 = not known)
    finish_reason: Optional[str] = None        # of the last answer: stop | length | repetition | None
    # Whitespace / length guard steps (module docstring): [{attempt, finish_reason, whitespace_run, action}],
    # action = repaired | compact_retry | length_retry | gave_up | parsed (a parsed answer cut by length/repetition).
    guard: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "task": self.task, "model": self.model, "data": self.data, "raw_text": self.raw_text,
            "latency_s": round(self.latency_s, 3), "attempts": self.attempts, "error": self.error,
            "usage": self.usage, "image_size": list(self.image_size), "page_size": list(self.page_size),
            "max_tokens": self.max_tokens, "finish_reason": self.finish_reason, "guard": list(self.guard),
        }


# --------------------------------------------------------------------------
# Pure helpers (no network): request body, image encoding, box conversion
# --------------------------------------------------------------------------

def build_request(model: str, prompt: str, image_data_url: Optional[str], schema: dict, *,
                  max_tokens: int = DEFAULT_MAX_TOKENS, seed: int = 0, temperature: float = 0.0,
                  enable_thinking: bool = False, system_prompt: str = prompts.SYSTEM_PROMPT,
                  images: Optional[list[str]] = None, labels: Optional[list[Optional[str]]] = None,
                  repetition_detection: Optional[dict] = None) -> dict:
    """The JSON body for ``POST /v1/chat/completions`` (see module docstring for the sources).

    One image: ``image_data_url``. Several: ``images`` (data URLs, sent in
    order; ``image_data_url`` must then be None). ``labels`` (one per image,
    None or "" for no label) puts a text part right before each image, e.g.
    "Image 1 (render):". The prompt text always comes last.
    ``repetition_detection`` (vLLM 0.30.0 request field, e.g.
    ``REPETITION_DETECTION``) is sent only when given.
    """
    if images is not None and image_data_url is not None:
        raise ValueError("pass either image_data_url or images, not both")
    urls = list(images) if images is not None else ([image_data_url] if image_data_url is not None else [])
    if labels is not None and len(labels) != len(urls):
        raise ValueError(f"{len(labels)} labels for {len(urls)} images")
    content: list[dict] = []
    for i, url in enumerate(urls):
        if labels is not None and labels[i]:
            content.append({"type": "text", "text": labels[i]})
        content.append({"type": "image_url", "image_url": {"url": url}})
    content.append({"type": "text", "text": prompt})
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        "temperature": temperature,
        "seed": seed,
        "max_tokens": max_tokens,
        "structured_outputs": {"json": schema},
        "chat_template_kwargs": {"enable_thinking": enable_thinking},
    }
    if repetition_detection is not None:
        body["repetition_detection"] = dict(repetition_detection)
    return body


def load_image(image):
    """Open ``image`` (path or PIL image) as an RGB PIL image. Pillow is imported here, lazily."""
    from PIL import Image
    if isinstance(image, (str, Path)):
        img = Image.open(image)
    else:
        img = image
    return img.convert("RGB")


def encode_image(image, max_side: int = DEFAULT_MAX_SIDE) -> tuple[str, tuple[int, int], tuple[int, int]]:
    """PNG data URL of ``image``, downscaled so the longest side is <= ``max_side`` (0 = no limit).

    Returns ``(data_url, sent_size, original_size)``.
    """
    from PIL import Image
    img = load_image(image)
    original = img.size
    if max_side and max(img.size) > max_side:
        scale = max_side / max(img.size)
        new_size = (max(1, round(img.width * scale)), max(1, round(img.height * scale)))
        img = img.resize(new_size, Image.LANCZOS)
    buf = io.BytesIO()
    # Lossless PNG at the default zlib level; no ``optimize`` pass (0.6 s instead of 0.13 s per 1600x900
    # image for a 5 % smaller file: it was a large part of every vision-check call's overhead).
    img.save(buf, format="PNG")
    data = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{data}", img.size, original


def parse_answer(text: str) -> Any:
    """``json.loads`` with tolerance for a ```json fence around the answer."""
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:]
    return json.loads(stripped)


def _outside_string_runs(text: str) -> list[tuple[int, int]]:
    """``(start, end)`` of every whitespace run outside JSON strings (a run inside a string is the answer's text)."""
    runs: list[tuple[int, int]] = []
    in_string = escape = False
    start = None
    for i, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch in " \t\r\n":
            if start is None:
                start = i
            continue
        if start is not None:
            runs.append((start, i))
            start = None
        if ch == '"':
            in_string = True
    if start is not None and not in_string:
        runs.append((start, len(text)))
    return runs


def whitespace_run(text: str) -> int:
    """Length of the longest whitespace run outside JSON strings that is at least ``WHITESPACE_RUN_CHARS`` long and
    holds 2 or more line breaks (0 = none): the P3 failure, ``null`` followed by ``"\\n  "`` until max_tokens."""
    best = 0
    for start, end in _outside_string_runs(text):
        if end - start >= WHITESPACE_RUN_CHARS and text.count("\n", start, end) >= 2:
            best = max(best, end - start)
    return best


def close_truncated_json(text: str) -> Optional[str]:
    """The answer with its trailing whitespace run removed and its open ``{``/``[`` closed, or None.

    Only for an answer that ENDS in a whitespace run (``whitespace_run`` of its tail): JSON ends a number or a
    literal at whitespace, so the last value before the run is complete and closing the brackets adds no value and
    changes none. None when the run is not at the end, the text ends inside a string, after a ``,``, ``:``, ``{`` or
    ``[``, an array is open (closing it could drop items the model had still to write), or there is nothing to close.
    The caller still parses and checks the result (``has_every_property`` and the schema: a field that never came
    fails)."""
    runs = _outside_string_runs(text)
    if not runs or runs[-1][1] != len(text) or whitespace_run(text[runs[-1][0]:]) == 0:
        return None
    body = text[:runs[-1][0]]
    stack: list[str] = []
    in_string = escape = False
    for ch in body:
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch in "{[":
            stack.append(ch)
        elif ch in "}]":
            if not stack or {"}": "{", "]": "["}[ch] != stack[-1]:
                return None
            stack.pop()
    if in_string or not stack or "[" in stack or not body or body[-1] in ",:{[":
        return None
    return body + "}" * len(stack)


def has_every_property(data: Any, schema: Any, root: Optional[dict] = None, depth: int = 0) -> bool:
    """True when every object of ``data`` has every property its schema lists (optional ones too), walked through
    nested objects. A repaired answer must pass it: closing an object early must not drop a field the model would
    still have written. Arrays and schemas without ``properties`` are not walked."""
    root = schema if root is None else root
    if depth > 32 or not isinstance(schema, dict):
        return True
    if "$ref" in schema:
        return has_every_property(data, _resolve_ref(schema["$ref"], root), root, depth + 1)
    if isinstance(data, dict) and isinstance(schema.get("properties"), dict):
        props = schema["properties"]
        if any(name not in data for name in props):
            return False
        return all(has_every_property(data[name], sub, root, depth + 1) for name, sub in props.items())
    return True


def compact_retry_body(body: dict) -> dict:
    """``body`` with ``COMPACT_RETRY_NOTE`` appended to the prompt (the last text part of the user message); the
    caller's body is not changed. Temperature, seed, schema and max_tokens stay as they are."""
    out = copy.deepcopy(body)
    for message in reversed(out.get("messages") or []):
        if message.get("role") != "user":
            continue
        content = message.get("content")
        if isinstance(content, str):
            message["content"] = content + "\n\n" + COMPACT_RETRY_NOTE
            return out
        for part in reversed(content or []):
            if part.get("type") == "text":
                part["text"] = part["text"] + "\n\n" + COMPACT_RETRY_NOTE
                return out
        content.append({"type": "text", "text": COMPACT_RETRY_NOTE})
        return out
    return out


def _resolve_ref(ref: str, root: dict) -> Any:
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return None
    node: Any = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def _max_chars(node: Any, root: dict, depth: int = 0) -> Optional[int]:
    """Upper bound of the characters of a JSON value valid under ``node`` (None = no bound: an array without
    maxItems, an object that allows other keys, ``true``, a $ref that does not resolve, a deep recursion)."""
    if depth > 32 or not isinstance(node, dict):
        return None
    if "$ref" in node:
        return _max_chars(_resolve_ref(node["$ref"], root), root, depth + 1)
    if "const" in node:
        return len(json.dumps(node["const"], ensure_ascii=False))
    if "enum" in node:
        return max([len(json.dumps(v, ensure_ascii=False)) for v in node["enum"]] or [0])
    for key in ("anyOf", "oneOf"):
        if key in node:
            parts = [_max_chars(sub, root, depth + 1) for sub in node[key] or []]
            return None if not parts or any(p is None for p in parts) else max(parts)
    if "allOf" in node:                      # the value satisfies every branch: the smallest known bound holds
        parts = [p for p in (_max_chars(sub, root, depth + 1) for sub in node["allOf"] or []) if p is not None]
        return min(parts) if parts else None
    types = node.get("type")
    if types is None:
        types = "object" if "properties" in node else ("array" if "items" in node else None)
    if types is None:
        return None
    best = 0
    for kind in ([types] if isinstance(types, str) else list(types)):
        if kind == "null":
            size: Optional[int] = 4
        elif kind == "boolean":
            size = 5
        elif kind in ("number", "integer"):
            size = NUMBER_CHARS
        elif kind == "string":
            size = int(node.get("maxLength", FREE_STRING_CHARS)) + 2
        elif kind == "array":
            if "maxItems" not in node:
                return None
            item = _max_chars(node.get("items", {}), root, depth + 1) if "items" in node else None
            if item is None:
                return None
            size = 2 + int(node["maxItems"]) * (item + ELEMENT_EXTRA)
        elif kind == "object":
            if node.get("additionalProperties", True) is not False:
                return None
            size = 2
            for name, sub in (node.get("properties") or {}).items():
                value = _max_chars(sub, root, depth + 1)
                if value is None:
                    return None
                size += len(json.dumps(name, ensure_ascii=False)) + ELEMENT_EXTRA + value
        else:
            return None
        best = max(best, size)
    return best


def schema_max_tokens(schema: dict, cap: int = DEFAULT_MAX_TOKENS) -> int:
    """``max_tokens`` for an answer of ``schema``: ``ceil(chars x MAX_TOKENS_FACTOR) + MAX_TOKENS_MARGIN`` where
    chars is an upper bound of the answer's characters (``_max_chars``), at most ``cap``; ``cap`` when the schema
    has no bound. A whitespace run then costs at most this many tokens, not 4096 (P3: about 50 s per request).
    One token is at most one character for the answers seen (Qwen3-VL-8B tokenizer: Turkish 0.92 tokens per
    character), so the factor 2 leaves room for escapes and odd scripts; an answer still cut by it is asked once
    more with the client's ``max_tokens`` (``_post``)."""
    chars = _max_chars(schema, schema)
    if chars is None:
        return int(cap)
    return int(min(cap, math.ceil(chars * MAX_TOKENS_FACTOR) + MAX_TOKENS_MARGIN))


def norm1000_to_pixels(box, width: int, height: int) -> list[float]:
    """A 0..1000 normalised box -> pixel box ``[x0, y0, x1, y1]`` of a ``width`` x ``height`` image."""
    x0, y0, x1, y1 = (float(v) for v in box)
    sx, sy = width / schemas.BOX_MAX, height / schemas.BOX_MAX
    xs = sorted((x0 * sx, x1 * sx))
    ys = sorted((y0 * sy, y1 * sy))
    return [round(xs[0], 1), round(ys[0], 1), round(xs[1], 1), round(ys[1], 1)]


def grammar_of(schema: dict) -> dict:
    """``schema`` as sent to vLLM: a shallow copy without ``$schema`` (as ``schemas.grammar_schema``)."""
    return {k: v for k, v in schema.items() if k != "$schema"}


def schema_errors(schema: dict, data: Any) -> list[str]:
    """All violations of ``data`` against a caller-made ``schema`` (jsonschema Draft 2020-12; empty = valid)."""
    import jsonschema
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path])
    return [f"{'/'.join(str(p) for p in err.absolute_path) or '<root>'}: {err.message}" for err in errors]


def boxes_to_pixels(data: dict, width: int, height: int) -> dict:
    """Convert every ``box`` under ``items`` to page pixels (new dict; the input is not changed)."""
    out = json.loads(json.dumps(data))
    for item in out.get("items", []):
        if "box" in item:
            item["box"] = norm1000_to_pixels(item["box"], width, height)
    return out


# --------------------------------------------------------------------------
# HTTP
# --------------------------------------------------------------------------

def _get(url: str, timeout_s: float = 10.0) -> tuple[int, bytes]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def post_json(url: str, body: dict, timeout_s: float) -> dict:
    """POST ``body`` as JSON and return the parsed JSON answer. Raises VLMError on any failure."""
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, method="POST",
                                 headers={"Content-Type": "application/json", "Authorization": "Bearer -"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:2000]
        raise VLMError(f"HTTP {exc.code} from {url}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise VLMError(f"cannot reach {url}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise VLMError(f"timeout after {timeout_s}s talking to {url}") from exc


def server_root(base_url: str) -> str:
    """``http://host:port/v1`` -> ``http://host:port`` (``/health`` lives at the root)."""
    return base_url[:-3] if base_url.endswith("/v1") else base_url.rstrip("/")


def health(base_url: str = DEFAULT_BASE_URL, timeout_s: float = 5.0) -> bool:
    """True when ``GET /health`` answers 200."""
    try:
        status, _ = _get(server_root(base_url) + "/health", timeout_s)
        return status == 200
    except (urllib.error.URLError, OSError):
        return False


def served_models(base_url: str = DEFAULT_BASE_URL, timeout_s: float = 10.0) -> list[str]:
    """Model IDs from ``GET /v1/models`` (empty list when the server is down)."""
    try:
        status, raw = _get(base_url.rstrip("/") + "/models", timeout_s)
    except (urllib.error.URLError, OSError):
        return []
    if status != 200:
        return []
    data = json.loads(raw.decode("utf-8"))
    return [m["id"] for m in data.get("data", [])]


def wait_for_server(base_url: str = DEFAULT_BASE_URL, timeout_s: float = 900.0, interval_s: float = 5.0) -> bool:
    """Poll ``/health`` until it answers or ``timeout_s`` passes."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if health(base_url):
            return True
        time.sleep(interval_s)
    return False


# --------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------

class VLMClient:
    """Talks to one vLLM server. ``model`` defaults to the first served model.

    ``deadline`` (attribute, epoch seconds or None): no request starts after it, each request's timeout
    is capped to the time left, and no retry pause runs past it (the vision check sets it to
    ``WENART_DEADLINE``, so a call it abandons at the deadline also stops holding a vLLM slot).

    ``repetition_detection`` (default ``REPETITION_DETECTION``, None = not sent) goes into every request: vLLM
    0.30.0 ends a run of one repeated pattern early (finish reason ``repetition``, module docstring).
    """

    def __init__(self, base_url: str = DEFAULT_BASE_URL, model: Optional[str] = None, *,
                 timeout_s: float = 600.0, retries: int = 3, max_side: int = DEFAULT_MAX_SIDE,
                 max_tokens: int = DEFAULT_MAX_TOKENS, enable_thinking: bool = False,
                 repetition_detection: Optional[dict] = REPETITION_DETECTION) -> None:
        self.base_url = base_url.rstrip("/")
        self._model = model
        self.timeout_s = timeout_s
        self.retries = max(1, retries)
        self.max_side = max_side
        self.max_tokens = max_tokens
        self.enable_thinking = enable_thinking
        self.repetition_detection = None if repetition_detection is None else dict(repetition_detection)
        self.deadline: Optional[float] = None

    @property
    def model(self) -> str:
        if self._model is None:
            models = served_models(self.base_url)
            if not models:
                raise VLMError(f"no model served at {self.base_url}")
            self._model = models[0]
        return self._model

    def health(self) -> bool:
        return health(self.base_url)

    def _max_tokens_for(self, max_tokens: Optional[int]) -> int:
        """The caller's ``max_tokens`` (e.g. ``schema_max_tokens``) capped to the client's; None = the client's."""
        return int(self.max_tokens) if max_tokens is None else int(max(1, min(int(max_tokens), self.max_tokens)))

    def run_task(self, task: str, image, *, prompt: Optional[str] = None) -> VLMResult:
        """Run one task on one image; the answer's boxes are converted to page pixels. ``max_tokens`` is sized
        from the task's schema (``schema_max_tokens``; the client's ``max_tokens`` for a list without maxItems)."""
        schema = schemas.grammar_schema(task)
        data_url, sent_size, page_size = encode_image(image, self.max_side)
        text = prompt if prompt is not None else prompts.prompt_for(task, *sent_size)
        try:
            model = self.model
        except VLMError as exc:
            return VLMResult(task=task, model="?", data=None, raw_text="", latency_s=0.0, attempts=0,
                             error=str(exc), image_size=sent_size, page_size=page_size)
        max_tokens = self._max_tokens_for(schema_max_tokens(schema, cap=self.max_tokens))
        body = build_request(model, text, data_url, schema, max_tokens=max_tokens,
                             enable_thinking=self.enable_thinking, repetition_detection=self.repetition_detection)
        post = self._post(body, check=lambda d: schemas.validation_errors(task, d) + (
            [] if has_every_property(d, schema) else ["<root>: a property is missing"]))
        raw_text, error, usage, parsed, attempts, latency, finish, guard = post
        data = None
        if parsed is not None:
            problems = schemas.validation_errors(task, parsed)
            if problems:
                error = "schema: " + "; ".join(problems[:5])
            else:
                data = boxes_to_pixels(parsed, *page_size)
        return VLMResult(task=task, model=model, data=data, raw_text=raw_text, latency_s=latency,
                         attempts=attempts, error=error, usage=usage, image_size=sent_size, page_size=page_size,
                         max_tokens=max_tokens, finish_reason=finish, guard=guard)

    def run_schema(self, images: list, prompt: str, schema: dict, *, seed: int = 0, task: str = "custom",
                   max_side: Optional[int] = None, labels: Optional[list[Optional[str]]] = None,
                   system_prompt: Optional[str] = None, max_tokens: Optional[int] = None) -> VLMResult:
        """One call with any JSON schema on a list of images (paths or PIL images), in order.

        ``labels``: optional text before each image (one per image). The answer
        is validated against ``schema`` (jsonschema Draft 2020-12); boxes are
        NOT converted (the caller knows its own box convention). On any
        failure ``data`` is None and ``error`` is set; nothing raises except a
        broken ``schema`` or a label count that does not match the images.
        ``image_size``/``page_size`` describe the first image. ``max_side``
        None means the client's ``max_side``; ``system_prompt`` None means
        ``SCHEMA_SYSTEM_PROMPT``; ``max_tokens`` None means the client's
        (the recognition questions pass ``schema_max_tokens(schema)``).
        """
        import jsonschema
        jsonschema.Draft202012Validator.check_schema(schema)
        if labels is not None and len(labels) != len(images):
            raise ValueError(f"{len(labels)} labels for {len(images)} images")
        side = self.max_side if max_side is None else max_side
        encoded = [encode_image(image, side) for image in images]
        sent_size = encoded[0][1] if encoded else (0, 0)
        page_size = encoded[0][2] if encoded else (0, 0)
        try:
            model = self.model
        except VLMError as exc:
            return VLMResult(task=task, model="?", data=None, raw_text="", latency_s=0.0, attempts=0,
                             error=str(exc), image_size=sent_size, page_size=page_size)
        tokens = self._max_tokens_for(max_tokens)
        body = build_request(model, prompt, None, grammar_of(schema), max_tokens=tokens, seed=seed,
                             enable_thinking=self.enable_thinking,
                             system_prompt=SCHEMA_SYSTEM_PROMPT if system_prompt is None else system_prompt,
                             images=[e[0] for e in encoded], labels=labels,
                             repetition_detection=self.repetition_detection)
        post = self._post(body, check=lambda d: schema_errors(schema, d) + (
            [] if has_every_property(d, schema) else ["<root>: a property is missing"]))
        raw_text, error, usage, parsed, attempts, latency, finish, guard = post
        data = None
        if error is None:                 # an answer was parsed (even a JSON null): validate it
            problems = schema_errors(schema, parsed)
            if problems:
                error = "schema: " + "; ".join(problems[:5])
            else:
                data = parsed
        return VLMResult(task=task, model=model, data=data, raw_text=raw_text, latency_s=latency,
                         attempts=attempts, error=error, usage=usage, image_size=sent_size, page_size=page_size,
                         max_tokens=tokens, finish_reason=finish, guard=guard)

    def _post(self, body: dict, check=None) -> tuple:
        """POST with retries: ``(raw_text, error, usage, parsed, attempts, latency_s, finish_reason, guard)``.

        Transport errors are retried with a growing pause; an answer that is
        not JSON is asked again (same request) until the retries are used up.
        With ``self.deadline`` no request starts after it, each timeout is
        capped to the time left and a pause that would end past it ends the
        retries (``attempts`` = requests sent).

        Guard (Milestone 13 round 4, pod P3; module docstring): an answer that
        does not parse and holds a whitespace run (``whitespace_run``) or
        stopped for repetition is never sent again unchanged (temperature 0:
        the same request gives the same run). It is repaired when the run is
        at its end and closing its objects gives an answer ``check`` (a
        function data -> list of problems) accepts; else it is asked once with
        ``compact_retry_body``; a second run ends the call. An answer cut by
        ``max_tokens`` below the client's is asked once with the client's
        ``max_tokens``. These guard requests are allowed once each even when
        ``retries`` is used up. ``guard`` lists every step.
        """
        url = self.base_url + "/chat/completions"
        t0 = time.monotonic()
        raw_text, error, usage, parsed = "", None, {}, None
        finish: Optional[str] = None
        guard: list[dict] = []
        attempts = 0
        limit = self.retries
        compact_done = length_done = False
        while attempts < limit:
            timeout = self.timeout_s
            if self.deadline is not None:
                left = float(self.deadline) - time.time()
                if left <= 0:
                    error = (f"{error}; " if error else "") + "deadline reached: no request sent"
                    break
                timeout = min(timeout, left)
            attempts += 1
            try:
                resp = post_json(url, body, timeout)
                choice = resp["choices"][0]
                raw_text = choice["message"].get("content") or ""
                finish = choice.get("finish_reason")
                usage = resp.get("usage") or {}
            except VLMError as exc:
                error = str(exc)
                if attempts < limit:
                    pause = min(30.0, 2.0 * attempts)
                    if self.deadline is not None and time.time() + pause >= float(self.deadline):
                        error += "; deadline reached: no retry"
                        break
                    time.sleep(pause)
                continue
            except (KeyError, IndexError, TypeError, AttributeError) as exc:
                error = f"bad answer: {exc}"
                continue
            run = whitespace_run(raw_text)
            try:
                parsed = parse_answer(raw_text)
            except ValueError as exc:            # json.JSONDecodeError is a ValueError
                parsed = None
                error = f"bad answer: {exc}"
            else:
                error = None
                if finish in ("length", "repetition") or run:
                    guard.append({"attempt": attempts, "finish_reason": finish, "whitespace_run": run,
                                  "action": "parsed"})
                break
            if run or finish == "repetition":
                step = {"attempt": attempts, "finish_reason": finish, "whitespace_run": run}
                fixed = close_truncated_json(raw_text)
                if fixed is not None:
                    try:
                        candidate = parse_answer(fixed)
                    except ValueError:
                        candidate = None
                    if candidate is not None and not (check(candidate) if check is not None else []):
                        guard.append(dict(step, action="repaired"))
                        parsed, error = candidate, None
                        break
                if not compact_done:
                    guard.append(dict(step, action="compact_retry"))
                    compact_done = True
                    body = compact_retry_body(body)
                    limit = max(limit, attempts + 1)
                    continue
                guard.append(dict(step, action="gave_up"))
                error += f" (whitespace run of {run} characters, finish {finish}: not asked again)"
                break
            if finish == "length" and not length_done and int(body.get("max_tokens") or 0) < int(self.max_tokens):
                guard.append({"attempt": attempts, "finish_reason": finish, "whitespace_run": run,
                              "action": "length_retry", "max_tokens": int(self.max_tokens)})
                length_done = True
                body = dict(body, max_tokens=int(self.max_tokens))
                limit = max(limit, attempts + 1)
                continue
        return raw_text, error, usage, parsed, attempts, time.monotonic() - t0, finish, guard
