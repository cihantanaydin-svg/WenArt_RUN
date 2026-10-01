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
"""
from __future__ import annotations

import base64
import io
import json
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

    def to_dict(self) -> dict:
        return {
            "task": self.task, "model": self.model, "data": self.data, "raw_text": self.raw_text,
            "latency_s": round(self.latency_s, 3), "attempts": self.attempts, "error": self.error,
            "usage": self.usage, "image_size": list(self.image_size), "page_size": list(self.page_size),
        }


# --------------------------------------------------------------------------
# Pure helpers (no network): request body, image encoding, box conversion
# --------------------------------------------------------------------------

def build_request(model: str, prompt: str, image_data_url: str, schema: dict, *,
                  max_tokens: int = DEFAULT_MAX_TOKENS, seed: int = 0, temperature: float = 0.0,
                  enable_thinking: bool = False, system_prompt: str = prompts.SYSTEM_PROMPT) -> dict:
    """The JSON body for ``POST /v1/chat/completions`` (see module docstring for the sources)."""
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": image_data_url}},
                {"type": "text", "text": prompt},
            ]},
        ],
        "temperature": temperature,
        "seed": seed,
        "max_tokens": max_tokens,
        "structured_outputs": {"json": schema},
        "chat_template_kwargs": {"enable_thinking": enable_thinking},
    }


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
    img.save(buf, format="PNG", optimize=True)
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


def norm1000_to_pixels(box, width: int, height: int) -> list[float]:
    """A 0..1000 normalised box -> pixel box ``[x0, y0, x1, y1]`` of a ``width`` x ``height`` image."""
    x0, y0, x1, y1 = (float(v) for v in box)
    sx, sy = width / schemas.BOX_MAX, height / schemas.BOX_MAX
    xs = sorted((x0 * sx, x1 * sx))
    ys = sorted((y0 * sy, y1 * sy))
    return [round(xs[0], 1), round(ys[0], 1), round(xs[1], 1), round(ys[1], 1)]


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
    """Talks to one vLLM server. ``model`` defaults to the first served model."""

    def __init__(self, base_url: str = DEFAULT_BASE_URL, model: Optional[str] = None, *,
                 timeout_s: float = 600.0, retries: int = 3, max_side: int = DEFAULT_MAX_SIDE,
                 max_tokens: int = DEFAULT_MAX_TOKENS, enable_thinking: bool = False) -> None:
        self.base_url = base_url.rstrip("/")
        self._model = model
        self.timeout_s = timeout_s
        self.retries = max(1, retries)
        self.max_side = max_side
        self.max_tokens = max_tokens
        self.enable_thinking = enable_thinking

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

    def run_task(self, task: str, image, *, prompt: Optional[str] = None) -> VLMResult:
        """Run one task on one image; the answer's boxes are converted to page pixels."""
        schema = schemas.grammar_schema(task)
        data_url, sent_size, page_size = encode_image(image, self.max_side)
        text = prompt if prompt is not None else prompts.prompt_for(task, *sent_size)
        try:
            model = self.model
        except VLMError as exc:
            return VLMResult(task=task, model="?", data=None, raw_text="", latency_s=0.0, attempts=0,
                             error=str(exc), image_size=sent_size, page_size=page_size)
        body = build_request(model, text, data_url, schema, max_tokens=self.max_tokens,
                             enable_thinking=self.enable_thinking)
        url = self.base_url + "/chat/completions"
        t0 = time.monotonic()
        raw_text, error, usage, parsed = "", None, {}, None
        attempts = 0
        for attempts in range(1, self.retries + 1):
            try:
                resp = post_json(url, body, self.timeout_s)
                raw_text = resp["choices"][0]["message"].get("content") or ""
                usage = resp.get("usage") or {}
                parsed = parse_answer(raw_text)
                error = None
                break
            except VLMError as exc:
                error = str(exc)
                if attempts < self.retries:
                    time.sleep(min(30.0, 2.0 * attempts))
            except (KeyError, IndexError, json.JSONDecodeError, ValueError) as exc:
                error = f"bad answer: {exc}"
        latency = time.monotonic() - t0
        data = None
        if parsed is not None:
            problems = schemas.validation_errors(task, parsed)
            if problems:
                error = "schema: " + "; ".join(problems[:5])
            else:
                data = boxes_to_pixels(parsed, *page_size)
        return VLMResult(task=task, model=model, data=data, raw_text=raw_text, latency_s=latency,
                         attempts=attempts, error=error, usage=usage, image_size=sent_size, page_size=page_size)
