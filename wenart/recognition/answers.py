"""Recognition questions and their answers: one round of questions, answered on the pod (docs/milestone7.md §1.4).

What: the CPU pipeline cannot call a vision-language model, so it writes every question it has into
``<out>/recognition/requests.json`` and exits 4; a GPU stage answers them with this module's CLI; the pipeline then
runs again and reads the answers with ``load``.

- ``requests.json`` = ``{"schema_version": "0.1", "kind": "recognition_requests", "project", "crop_version",
  "models": {key: {id, slug, pass}}, "items": [{"key", "task": "symbol_type|room_label", "page", "images":
  ["crops/<key>_ctx.png", "crops/<key>_iso.png"] (or ["crops/<key>.png"]), "context": {...},
  "question": {facts} (symbol_type only), "input_sha256"}]}``; image paths are relative to ``<out>/recognition/``.
  ``write_requests`` writes it, ``read_requests`` reads it. A ``symbol_type`` item's ``question`` holds the facts
  its question was built and hashed from (``symbols.question_facts``: room, fitting types, neighbours, crop kind);
  ``call_args`` asks exactly that question (prompt and narrowed type enum, from ``crops.question_digest``). Items
  without facts get the generic question and the full type list.
- ``answers_<slug>.json`` (``slug`` from ``check.yaml models.<key>.slug``) = the M5 answer-store pattern:
  ``{"schema_version", "kind": "recognition_answers", "model_key", "model", "slug", "incomplete", "calls": {<key>:
  {task, input_sha256, data, raw_text, error, attempts, latency_s, model, seed, images[, seeded_from, seeded_key,
  seeded_images]}}}``,
  rewritten (calls in key order) after every answer. An answer counts only while its key **and** ``input_sha256``
  match the request, it comes from the model id configured for its key, and its ``data`` passes the task's JSON
  schema (validated again on every read, so a hand-edited or truncated file can never reach the building).
  Temperature 0, seed 0, structured outputs (``vlm_client``).
- ``load(out_dir, items=None) -> {key: {model_key: answer dict | None}}`` for the pipeline; ``is_complete`` tells
  whether every item has an answer from every model (the pipeline's exit 4 rule). Whether two answers *agree* is
  decided by ``symbols.decide`` and ``room_labels.decide`` (empty, null or "" values never agree).

CLI::

    python -m wenart.recognition.answers ask <out>/recognition --model-key qwen|glm --server URL --workers N
        [--deadline T] [--seed-answers DIR]
    python -m wenart.recognition.answers status <out>/recognition [--json]

``ask`` first copies stored answers from ``--seed-answers DIR`` (a results folder holding ``answers_<slug>.json``)
whose key, ``input_sha256`` and model id match and whose data is schema-valid, then asks the server for the rest,
``--workers`` calls at once, until ``--deadline`` (epoch seconds, default env ``WENART_DEADLINE``): no call starts
after it and none is waited for past it (the file is then marked ``incomplete``). Exit 0 = every item answered,
3 = the deadline left items unanswered, 2 = the server is unreachable, an answer failed (transport error or not
schema-valid after the client's retries) or a usage error (unknown model key, no ``requests.json``). ``status``
prints answered / stale / failed / missing per model and exits 0 when complete, 1 otherwise.

Model keys and passes: ``qwen`` = pass 1 (Qwen3-VL-8B), ``glm`` = pass 2 (GLM-4.6V-Flash), ids, revisions and
slugs from ``wenart/vision_check/check.yaml`` (read here, never edited).

Milestone 10 (docs/milestone10.md §1.5, §1.6a): the task ``sheet_region`` (one crop per drawing region of the sheets
stage, ``<out>/sheets/requests.json``) has its schema, prompt and input hash in ``wenart.sheets.question``;
``ask`` and ``status`` work on the ``<out>/sheets`` folder exactly as on ``<out>/recognition``.

Milestone 13 round 4 (pod P3, 16 Oct 2026: 5 of 8 ``sheet_region`` answers of Qwen3-VL-8B were an endless run of
blank lines inside the JSON, 151 s each, three identical requests): every question is asked with a ``max_tokens``
sized from its schema (``call_args``: ``vlm_client.schema_max_tokens``; 1,322 tokens for ``sheet_region``
instead of 4,096) and through the client's whitespace guard (vLLM ``repetition_detection``, a repair of an answer
whose run is at its end, else one retry asking for one-line JSON; ``vlm_client`` module docstring). Each answer
record keeps ``max_tokens``, ``finish_reason`` and ``guard`` (the guard's steps), and ``ask`` logs every step.

Fix round after P4a (17 Oct 2026; real02: six answers seeded by input hash from other keys kept those keys' crop
paths, which in the run's ``crops`` folder show other symbols): a seeded record's ``images`` are the request item's
own crops (the input hash covers the crop description, so they show what was answered); ``seeded_key`` and
``seeded_images`` keep the key and the crop paths it had in the seed file, for the trail.

Fix round after P5 (22 Oct 2026; pod P5, real04). What: a request item may carry ``crop_sha256`` (``PIXELS_KEY``:
``crops.pixels_sha256`` of the crops ``crops.render_pair`` drew for it) and an answer record ``image_sha256``
(``SHOWN_KEY``: the pixel hash of the crop files the model was shown, read from disk when it was asked or, for a
seeded answer from before this round, from the seed folder's crop files). An answer is current only while both
hashes, when known, are equal (``shown_matches``); ``seed_answers`` skips an old answer whose seed crop files show
other pixels than the item's crops, and ``ask`` never sends crop files that show other pixels than the item's
crops (a failed record "overwritten: not asked"). Records and items from before this round have no pixel hash, and
the canonical ``input_sha256`` is unchanged, so the committed answers of unchanged crops are reused as before. Why:
``input_sha256`` hashes what should be drawn, not the file; P3's crop file of sym_L0_007 showed another symbol (a key
collision of the secondary page overwrote it), and its answers stayed reusable because the hash did not change.
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import sys
import threading
import time
from pathlib import Path
from typing import Callable, Optional

from wenart.recognition import prompts, schemas

SCHEMA_VERSION = "0.1"
REQUESTS_NAME = "requests.json"
CROPS_DIR = "crops"
CHECK_YAML = Path(__file__).resolve().parents[1] / "vision_check" / "check.yaml"
MODEL_KEYS: tuple[str, ...] = ("qwen", "glm")       # pass 1, pass 2 (§3.3)
DEFAULT_SERVER = "http://127.0.0.1:8001/v1"
EXIT_OK, EXIT_INCOMPLETE, EXIT_SERVER, EXIT_DEADLINE = 0, 1, 2, 3
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
# Fix round after P5 (module docstring): the pixels a request item's crops show (``crops.pixels_sha256``, set by
# ``crops.render_pair`` and carried by the item) and the pixels of the files an answer was given for.
PIXELS_KEY = "crop_sha256"
SHOWN_KEY = "image_sha256"


class UsageError(ValueError):
    """A wrong model key or a folder without requests: the CLI prints it and exits 2."""


# --------------------------------------------------------------------------
# Models (check.yaml, read only)
# --------------------------------------------------------------------------

def load_models(path: Optional[Path] = None) -> dict:
    """``check.yaml: models`` as a dict ``{key: {id, revision, slug, ...}}``."""
    import yaml
    with open(CHECK_YAML if path is None else path, encoding="utf-8") as fh:
        return (yaml.safe_load(fh) or {}).get("models") or {}


def model_info(key: str, models: Optional[dict] = None) -> dict:
    """``{"key", "id", "slug", "pass"}`` of a model key (UsageError for a key that is not a recognition pass)."""
    models = load_models() if models is None else models
    if key not in MODEL_KEYS or key not in models:
        raise UsageError(f"--model-key must be one of {', '.join(k for k in MODEL_KEYS if k in models)} "
                         f"(got {key!r})")
    m = models[key]
    return {"key": key, "id": str(m["id"]), "slug": str(m["slug"]), "pass": MODEL_KEYS.index(key) + 1}


def answers_path(rec_dir: Path, slug: str) -> Path:
    return Path(rec_dir) / f"answers_{slug}.json"


# --------------------------------------------------------------------------
# JSON files
# --------------------------------------------------------------------------

def read_json(path: Path) -> Optional[dict]:
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> Path:
    """indent=1, ensure_ascii=False, via a temporary file (as every M5 JSON)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


# --------------------------------------------------------------------------
# Tasks of other stages (Milestone 10)
# --------------------------------------------------------------------------

SHEET_TASK = "sheet_region"


def tasks() -> tuple[str, ...]:
    """Every per-item task: the M7 recognition tasks and the M10 ``sheet_region`` question."""
    return tuple(schemas.M7_TASKS) + (SHEET_TASK,)


def task_schema(task: str) -> dict:
    """The JSON schema of a task's answer."""
    if task == SHEET_TASK:
        from wenart.sheets import question
        return question.SCHEMA
    return schemas.M7_SCHEMAS[task]


def task_errors(task: str, data) -> list[str]:
    """Schema violations of an answer (empty = valid)."""
    if task != SHEET_TASK:
        return schemas.validation_errors(task, data)
    import jsonschema
    validator = jsonschema.Draft202012Validator(task_schema(task))
    return [f"{'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}" for e in validator.iter_errors(data)]


# --------------------------------------------------------------------------
# Requests
# --------------------------------------------------------------------------

def check_item(item: dict) -> None:
    """ValueError when a request item does not have the §1.4 shape."""
    for name in ("key", "task", "images", "input_sha256"):
        if name not in item:
            raise ValueError(f"request item without {name!r}: {item.get('key')!r}")
    if item["task"] not in tasks():
        raise ValueError(f"request {item['key']!r}: unknown task {item['task']!r}")
    if not item["images"] or not all(isinstance(p, str) for p in item["images"]):
        raise ValueError(f"request {item['key']!r}: images must be a non-empty list of paths")
    if not _SHA256.match(str(item["input_sha256"])):
        raise ValueError(f"request {item['key']!r}: input_sha256 is not a sha256 hex digest")
    if PIXELS_KEY in item and not _SHA256.match(str(item[PIXELS_KEY])):
        raise ValueError(f"request {item['key']!r}: {PIXELS_KEY} is not a sha256 hex digest")
    if "question" in item:
        facts = item["question"]
        ok = isinstance(facts, dict) and item["task"] == "symbol_type"
        if ok:
            choices = facts.get("choices")
            ok = facts.get("kind", "vector") in ("vector", "raster") and (
                choices is None or (isinstance(choices, list) and bool(choices)
                                    and all(c in schemas.SYMBOL_TYPE_CHOICES for c in choices)))
        if not ok:
            raise ValueError(f"request {item['key']!r}: question facts must be a dict with kind vector|raster and "
                             f"choices from the symbol types (got {facts!r})")


def write_requests(out_dir: Path, project: str, items: list[dict], crop_version: Optional[str] = None) -> Path:
    """Write ``<out_dir>/requests.json`` (``out_dir`` = ``<out>/recognition``, or ``<out>/sheets`` with the sheets
    stage's ``crop_version``); items keep the caller's order."""
    from wenart.recognition.crops import CROP_VERSION as RECOGNITION_CROP_VERSION
    CROP_VERSION = crop_version or RECOGNITION_CROP_VERSION
    keys = set()
    for item in items:
        check_item(item)
        if item["key"] in keys:
            raise ValueError(f"duplicate request key {item['key']!r}")
        keys.add(item["key"])
    try:
        models = {k: {n: v for n, v in model_info(k).items() if n != "key"} for k in MODEL_KEYS}
    except (OSError, KeyError, UsageError):                 # check.yaml missing: the file still describes the items
        models = {}
    doc = {"schema_version": SCHEMA_VERSION, "kind": "recognition_requests", "project": project,
           "crop_version": CROP_VERSION, "models": models, "items": list(items)}
    return write_json(Path(out_dir) / REQUESTS_NAME, doc)


def read_requests(out_dir: Path) -> Optional[dict]:
    """The requests document of ``<out>/recognition`` or None when there is none."""
    doc = read_json(Path(out_dir) / REQUESTS_NAME)
    if doc is None:
        return None
    if doc.get("kind") != "recognition_requests":
        raise ValueError(f"{Path(out_dir) / REQUESTS_NAME}: not a recognition requests file")
    for item in doc.get("items") or []:
        check_item(item)
    return doc


# --------------------------------------------------------------------------
# Answer store
# --------------------------------------------------------------------------

def valid_answer(task: str, data) -> bool:
    """True when ``data`` is a schema-valid answer of ``task`` (a JSON null or a broken answer is not)."""
    return data is not None and task in tasks() and not task_errors(task, data)


def key_by_input(calls: dict, item: dict, current: Callable) -> Optional[str]:
    """The first key (in key order) of ``calls`` whose record has the item's input hash, is current by ``current``
    and is schema-valid, else None (fix round after P4a: the seed's key goes into the seeded record's trail)."""
    sha = item.get("input_sha256")
    if not sha:
        return None
    for key in sorted(calls):
        rec = calls[key]
        if isinstance(rec, dict) and rec.get("input_sha256") == sha and current(rec, item) \
                and valid_answer(item["task"], rec.get("data")):
            return key
    return None


def find_by_input(calls: dict, item: dict, current: Callable) -> Optional[dict]:
    """Milestone 11: the record (in key order) of ``calls`` whose input hash is the item's, current by ``current`` and
    schema-valid, else None."""
    key = key_by_input(calls, item, current)
    return None if key is None else calls[key]


def shown_matches(rec: dict, item: dict) -> bool:
    """Fix round after P5 (module docstring): False when the record names the pixels it was given for
    (``SHOWN_KEY``) and the item names its crops' pixels (``PIXELS_KEY``) and they differ; True otherwise (a record
    or an item from before this round)."""
    shown, crop = rec.get(SHOWN_KEY), item.get(PIXELS_KEY)
    return not (shown and crop and shown != crop)


def shown_sha256(rec_dir: Path, images: list) -> Optional[str]:
    """Fix round after P5: ``crops.image_sha256`` of the files ``images`` (relative to ``rec_dir``), None when one is
    missing or unreadable."""
    from wenart.recognition.crops import image_sha256
    return image_sha256([Path(rec_dir) / p for p in images or []]) if images else None


class AnswerStore:
    """``<out>/recognition/answers_<slug>.json``: every answer of one model, rewritten after each answer."""

    def __init__(self, path: Path, model_key: str, slug: str, model: str = "") -> None:
        self.path = Path(path)
        data = read_json(self.path) or {}
        self.data = {"schema_version": SCHEMA_VERSION, "kind": "recognition_answers", "model_key": model_key,
                     "model": model or data.get("model") or "", "slug": slug,
                     "incomplete": bool(data.get("incomplete", False)), "calls": dict(data.get("calls") or {})}

    @classmethod
    def for_model(cls, rec_dir: Path, key: str, models: Optional[dict] = None) -> "AnswerStore":
        info = model_info(key, models)
        return cls(answers_path(rec_dir, info["slug"]), key, info["slug"], info["id"])

    @property
    def calls(self) -> dict:
        return self.data["calls"]

    def get(self, key: str) -> Optional[dict]:
        return self.calls.get(key)

    def current(self, rec: Optional[dict], item: dict) -> bool:
        """Same input hash and, when both are known, the same model id (a model changed in check.yaml makes the
        stored answers stale even under the same slug). Fix round after P5: and, when both are known, the pixels the
        answer was given for (``SHOWN_KEY``) are the item's crops (``PIXELS_KEY``)."""
        if not rec or rec.get("input_sha256") != item["input_sha256"]:
            return False
        if not shown_matches(rec, item):
            return False                # fix round after P5: the answer was given for another picture
        model = self.data.get("model") or ""
        return not (model and rec.get("model") and rec.get("model") != model)

    def valid(self, item: dict) -> Optional[dict]:
        """The stored record of ``item`` when it is current (key, input hash, model) and schema-valid, else None.

        Milestone 11: an answer follows its crop. When the record under the item's key is not current, a current
        record under another key with the same ``input_sha256`` is used (the same crops and question: a group split
        of the ingest that took a candidate away renumbers the later keys of the page, docs/milestone11.md §1.2 U8)."""
        rec = self.calls.get(item["key"])
        if self.current(rec, item) and valid_answer(item["task"], rec.get("data")):
            return rec
        return self.by_input(item)

    def by_input(self, item: dict) -> Optional[dict]:
        """A current, schema-valid record of another key with the item's ``input_sha256`` (None when there is none)."""
        return find_by_input(self.calls, item, self.current)

    def put(self, key: str, record: dict, save: bool = True) -> None:
        self.calls[key] = record
        if save:
            self.save()

    def save(self) -> None:
        """Write the file (calls in key order: the content does not depend on the answer order)."""
        self.data["calls"] = dict(sorted(self.calls.items()))
        write_json(self.path, self.data)


def item_state(store: AnswerStore, item: dict) -> str:
    """``answered`` | ``stale`` (other input hash or model) | ``failed`` (no schema-valid data) | ``missing``."""
    rec = store.get(item["key"])
    if (rec is None or not store.current(rec, item)) and store.by_input(item) is not None:
        return "answered"                                  # Milestone 11: the answer of the same crop, re-keyed
    if rec is None:
        return "missing"
    if not store.current(rec, item):
        return "stale"
    return "answered" if valid_answer(item["task"], rec.get("data")) else "failed"


def load(out_dir: Path, items: Optional[list[dict]] = None, models: Optional[dict] = None) -> dict:
    """``{key: {model_key: answer data or None}}`` for ``items`` (default: the items of ``requests.json``).

    An answer is returned only when its key and ``input_sha256`` match the item and it is schema-valid; a missing
    answers file, a stale or a failed answer gives None. Every model key of ``MODEL_KEYS`` is present per item.
    """
    out_dir = Path(out_dir)
    if items is None:
        doc = read_requests(out_dir)
        items = (doc or {}).get("items") or []
    models = load_models() if models is None else models
    result: dict[str, dict] = {item["key"]: {} for item in items}
    for key in MODEL_KEYS:
        store = AnswerStore.for_model(out_dir, key, models) if key in models else None
        for item in items:
            rec = store.valid(item) if store is not None else None
            result[item["key"]][key] = rec.get("data") if rec else None
    return result


def is_complete(loaded: dict, keys: Optional[list[str]] = None) -> bool:
    """True when every item (``keys``, default all) has an answer from every model key."""
    keys = list(loaded) if keys is None else keys
    return all(all(loaded.get(k, {}).get(m) is not None for m in MODEL_KEYS) for k in keys)


def status(out_dir: Path, models: Optional[dict] = None) -> dict:
    """``{"items": n, "complete": bool, "models": {key: {slug, answered, stale, failed, missing, incomplete}}}``."""
    doc = read_requests(out_dir)
    if doc is None:
        raise UsageError(f"{Path(out_dir) / REQUESTS_NAME} not found")
    items = doc.get("items") or []
    models = load_models() if models is None else models
    out = {"items": len(items), "models": {}}
    for key in MODEL_KEYS:
        store = AnswerStore.for_model(out_dir, key, models)
        counts = {"answered": 0, "stale": 0, "failed": 0, "missing": 0}
        for item in items:
            counts[item_state(store, item)] += 1
        out["models"][key] = {"slug": store.data["slug"], **counts, "incomplete": bool(store.data["incomplete"])}
    out["complete"] = all(m["answered"] == len(items) for m in out["models"].values())
    return out


# --------------------------------------------------------------------------
# Seeding from a results folder
# --------------------------------------------------------------------------

def seed_answers(store: AnswerStore, items: list[dict], seed_dir: Path, log: Callable = print) -> int:
    """Copy the answers of ``<seed_dir>/answers_<slug>.json`` whose key, input hash and model id match and whose data
    is schema-valid into ``store`` (only for items that have no current answer). Returns the number copied.

    Fix round after P4a: the copy's ``images`` are the item's own crop paths (an answer found under another key by
    the input hash kept that key's paths, which in this run's crops show another symbol); ``seeded_key`` and
    ``seeded_images`` record the key and the crop paths the answer had in the seed file."""
    seed_path = answers_path(seed_dir, store.data["slug"])
    seed = read_json(seed_path)
    if seed is None:
        log(f"recognition answers: no {seed_path.name} in {seed_dir}: nothing seeded")
        return 0
    seed_model = str(seed.get("model") or "")
    if store.data["model"] and seed_model and seed_model != store.data["model"]:
        log(f"recognition answers: {seed_path} is from {seed_model}, not {store.data['model']}: nothing seeded")
        return 0
    calls = seed.get("calls") or {}
    copied = 0
    for item in items:
        if store.valid(item) is not None:
            continue
        seed_key = item["key"]
        rec = calls.get(seed_key)
        if not store.current(rec, item) or not valid_answer(item["task"], rec.get("data")):
            seed_key = key_by_input(calls, item, store.current)  # Milestone 11: the same crop under another key
            if seed_key is None:
                continue
            rec = calls[seed_key]
        new = dict(rec)
        if not rec.get(SHOWN_KEY):
            # Fix round after P5 (module docstring): an answer from before this round names no pixels; the crop
            # files of its seed folder show what it was given for. Another picture than the item's crops: not seeded.
            shown = shown_sha256(seed_dir, rec.get("images") or [])
            if shown is not None and item.get(PIXELS_KEY) and shown != item[PIXELS_KEY]:
                log(f"recognition answers: {item['key']}: the seed answer {seed_key} was given for other crop pixels "
                    f"(its crop files in {seed_dir} show another picture): not seeded")
                continue
            if shown is not None:
                new[SHOWN_KEY] = shown
        new.update(images=list(item["images"]), seeded_from=str(seed_path), seeded_key=seed_key,
                   seeded_images=list(rec.get("images") or []))
        store.put(item["key"], new, save=False)
        copied += 1
    if copied:
        store.save()
    return copied


# --------------------------------------------------------------------------
# Asking
# --------------------------------------------------------------------------

def call_args(item: dict, rec_dir: Path) -> dict:
    """The ``VLMClient.run_schema`` arguments of one request item: the question that was hashed into its
    ``input_sha256`` (``crops.question_digest`` of the item's facts: prompt and, for ``symbol_type``, the type enum
    narrowed to the item's choices)."""
    task = item["task"]
    images = [Path(rec_dir) / p for p in item["images"]]
    if task == SHEET_TASK:
        from wenart.sheets import question
        return {"images": images, "prompt": question.PROMPT, "schema": question.SCHEMA, "labels": None, "task": task,
                "max_tokens": schema_max_tokens(question.SCHEMA)}
    from wenart.recognition.crops import question_digest
    digest = question_digest(task, item.get("question") if task == "symbol_type" else None)
    labels = list(digest["image_labels"]) if "image_labels" in digest else None
    if labels is not None and len(labels) != len(images):
        labels = None
    return {"images": images, "prompt": digest["prompt"], "schema": digest["schema"], "labels": labels, "task": task,
            "max_tokens": schema_max_tokens(digest["schema"])}


def schema_max_tokens(schema: dict) -> int:
    """Milestone 13 round 4: the ``max_tokens`` of a question, sized from its answer schema
    (``vlm_client.schema_max_tokens``; the answers are short: at most 85 Qwen tokens in the stored runs, 4,096 let
    one whitespace run of P3 cost about 50 s per request)."""
    from wenart.recognition.vlm_client import schema_max_tokens as sized
    return sized(schema)


def record_of(item: dict, result, model: str, seed: int) -> dict:
    """One answer record. Milestone 13 round 4: also ``max_tokens`` (of the first request), ``finish_reason`` (of the
    last answer) and ``guard`` (the whitespace / length guard's steps, ``vlm_client.VLMResult.guard``)."""
    return {"task": item["task"], "input_sha256": item["input_sha256"], "data": result.data,
            "raw_text": result.raw_text, "error": result.error, "attempts": result.attempts,
            "latency_s": round(float(result.latency_s), 3), "model": model, "seed": seed,
            "images": list(item["images"]), "max_tokens": int(getattr(result, "max_tokens", 0) or 0),
            "finish_reason": getattr(result, "finish_reason", None), "guard": list(getattr(result, "guard", None) or [])}


def guard_text(guard: list) -> str:
    """The guard's steps in one line for the log, e.g. ``attempt 1: whitespace run 48 chars, finish repetition ->
    compact_retry``."""
    parts = []
    for step in guard or []:
        run = step.get("whitespace_run") or 0
        what = f"whitespace run {run} chars, " if run else ""
        parts.append(f"attempt {step.get('attempt')}: {what}finish {step.get('finish_reason')} -> {step.get('action')}")
    return "; ".join(parts)


def _error_record(item: dict, error: str, model: str, seed: int) -> dict:
    return {"task": item["task"], "input_sha256": item["input_sha256"], "data": None, "raw_text": "",
            "error": error, "attempts": 0, "latency_s": 0.0, "model": model, "seed": seed,
            "images": list(item["images"])}


def _spawn(fn: Callable, tag: int, results: "queue.Queue") -> None:
    """Run ``fn()`` in a daemon thread (a wedged call cannot keep the process alive) and queue its outcome."""
    def target():
        try:
            results.put((tag, fn(), None))
        except Exception as exc:  # noqa: BLE001 - recorded as a failed answer by the waiting thread
            results.put((tag, None, exc))

    threading.Thread(target=target, name=f"recognition-call-{tag}", daemon=True).start()


def ask(items: list[dict], store: AnswerStore, client, rec_dir: Path, *, workers: int = 1,
        deadline: Optional[float] = None, seed: int = 0, log: Callable = print,
        clock: Callable[[], float] = time.time) -> dict:
    """Ask every item without a current answer, ``workers`` at once, until ``deadline`` (epoch s).

    Only this thread writes the answers file. Returns ``{"asked", "reused", "failed", "left", "incomplete",
    "guarded"}`` (``guarded``: answers whose call needed the whitespace / length guard, Milestone 13 round 4).
    """
    stats = {"asked": 0, "reused": 0, "failed": 0, "left": 0, "incomplete": False, "guarded": 0}
    if deadline is not None and hasattr(client, "deadline"):
        client.deadline = float(deadline)          # VLMClient caps each request and retry to it
    model = str(getattr(client, "model", "") or store.data.get("model") or "")
    pending = []
    for item in items:
        if store.valid(item) is None:
            pending.append(item)
        else:
            stats["reused"] += 1
    results: "queue.Queue" = queue.Queue()
    running: dict[int, dict] = {}
    item_shown: dict[int, Optional[str]] = {}
    started, abandoned = 0, 0
    while True:
        while started < len(pending) and len(running) < max(1, int(workers)):
            if deadline is not None and clock() >= deadline:
                break
            item = pending[started]
            shown = shown_sha256(rec_dir, item["images"])
            if shown is not None and item.get(PIXELS_KEY) and shown != item[PIXELS_KEY]:
                # Fix round after P5 (module docstring): the files on disk are not the item's crops (overwritten by
                # another candidate of the same key): never ask the model about another picture
                rec = _error_record(item, f"the crop files of {item['key']} show other pixels than its crops "
                                          f"(overwritten): not asked", model, seed)
                rec[SHOWN_KEY] = shown
                store.put(item["key"], rec)
                stats["failed"] += 1
                log(f"recognition answers: {item['key']}: {rec['error']}")
                pending.pop(started)
                continue
            args = call_args(item, rec_dir)
            running[started] = item
            item_shown[started] = shown

            def call(args=args):
                return client.run_schema([str(p) for p in args["images"]], args["prompt"], args["schema"],
                                         seed=seed, task=args["task"], max_side=0, labels=args["labels"],
                                         system_prompt=prompts.M7_SYSTEM_PROMPT, max_tokens=args["max_tokens"])
            _spawn(call, started, results)
            started += 1
        if not running:
            break
        left = None if deadline is None else max(0.0, deadline - clock())
        try:
            tag, result, exc = results.get(timeout=left)
        except queue.Empty:
            abandoned = len(running)
            log(f"recognition answers: deadline reached with {abandoned} call(s) unanswered: "
                f"{', '.join(i['key'] for i in running.values())}")
            break
        item = running.pop(tag)
        if exc is not None:
            rec = _error_record(item, f"{type(exc).__name__}: {exc}", model, seed)
        else:
            rec = record_of(item, result, model, seed)
        if item_shown.get(tag):
            rec[SHOWN_KEY] = item_shown[tag]     # fix round after P5: the pixels this answer was given for
        store.put(item["key"], rec)
        stats["asked"] += 1
        if rec.get("guard"):
            stats["guarded"] += 1
            log(f"recognition answers: {item['key']}: guard: {guard_text(rec['guard'])}"
                f"{'' if rec['data'] is None else ' (answered)'}")
        if not valid_answer(item["task"], rec["data"]):
            stats["failed"] += 1
            log(f"recognition answers: {item['key']}: {rec['error'] or 'answer not schema-valid'}")
    stats["left"] = len(pending) - started + abandoned
    stats["incomplete"] = stats["left"] > 0
    store.data["incomplete"] = stats["incomplete"]
    if model:
        store.data["model"] = model
    store.save()
    return stats


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def deadline_of(value: Optional[float]) -> Optional[float]:
    """``--deadline`` or the ``WENART_DEADLINE`` env (epoch seconds), None when neither is set."""
    if value is not None:
        return float(value)
    env = os.environ.get("WENART_DEADLINE", "").strip()
    return float(env) if env else None


def default_client(info: dict, server: str, retries: int = 3, timeout_s: float = 600.0):
    from wenart.recognition.vlm_client import VLMClient
    return VLMClient(server, model=info["id"], retries=retries, timeout_s=timeout_s)


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m wenart.recognition.answers",
                                     description="answer the recognition requests of a pipeline output "
                                                 "(docs/milestone7.md §1.4)")
    parser.add_argument("command", choices=["ask", "status"])
    parser.add_argument("rec_dir", help="<out>/recognition (holds requests.json)")
    parser.add_argument("--model-key", help="ask: qwen (pass 1) | glm (pass 2)")
    parser.add_argument("--server", default=DEFAULT_SERVER, help=f"ask: vLLM base URL (default {DEFAULT_SERVER})")
    parser.add_argument("--workers", type=int, default=None, help="ask: calls at once (default check.yaml "
                                                                  "calls.workers, else 1)")
    parser.add_argument("--deadline", type=float, default=None, help="ask: epoch seconds (default env "
                                                                     "WENART_DEADLINE)")
    parser.add_argument("--seed-answers", default=None, help="ask: results folder with answers_<slug>.json to "
                                                             "copy matching answers from first")
    parser.add_argument("--retries", type=int, default=3, help="ask: client attempts per call (default 3)")
    parser.add_argument("--timeout", type=float, default=600.0, help="ask: seconds per HTTP request (default 600)")
    parser.add_argument("--json", action="store_true", help="status: print the summary as JSON")
    return parser.parse_args(argv)


def _workers_default() -> int:
    try:
        import yaml
        cfg = yaml.safe_load(CHECK_YAML.read_text(encoding="utf-8")) or {}
        return int((cfg.get("calls") or {}).get("workers", 1))
    except (OSError, ValueError, TypeError):
        return 1


def cmd_ask(args, client_factory=None) -> int:
    rec_dir = Path(args.rec_dir)
    models = load_models()
    info = model_info(args.model_key or "", models)
    doc = read_requests(rec_dir)
    if doc is None:
        raise UsageError(f"{rec_dir / REQUESTS_NAME} not found")
    items = doc.get("items") or []
    store = AnswerStore.for_model(rec_dir, info["key"], models)
    if args.seed_answers:
        n = seed_answers(store, items, Path(args.seed_answers))
        print(f"recognition answers [{info['key']}]: {n} answer(s) seeded from {args.seed_answers}")
    pending = [i for i in items if store.valid(i) is None]
    if not pending:
        store.data["incomplete"] = False
        store.save()
        print(f"recognition answers [{info['key']}]: all {len(items)} item(s) answered -> {store.path}")
        return EXIT_OK
    deadline = deadline_of(args.deadline)
    if deadline is not None and time.time() >= deadline:
        store.data["incomplete"] = True
        store.save()
        print(f"recognition answers [{info['key']}]: deadline already passed, {len(pending)} item(s) left")
        return EXIT_DEADLINE
    if client_factory is None:
        from wenart.recognition import vlm_client
        if not vlm_client.health(args.server):
            print(f"recognition answers [{info['key']}]: no vLLM server answers at {args.server}", file=sys.stderr)
            return EXIT_SERVER
        client = default_client(info, args.server, retries=args.retries, timeout_s=args.timeout)
    else:
        client = client_factory(info, args.server)
    workers = args.workers or _workers_default()
    stats = ask(items, store, client, rec_dir, workers=workers, deadline=deadline)
    print(f"recognition answers [{info['key']}]: {len(items)} item(s): {stats['asked']} asked "
          f"({stats['failed']} failed{', ' + str(stats['guarded']) + ' guarded' if stats['guarded'] else ''}), "
          f"{stats['reused']} reused, {stats['left']} left"
          f"{' (deadline: incomplete)' if stats['incomplete'] else ''} -> {store.path}")
    if stats["left"]:
        return EXIT_DEADLINE
    if any(store.valid(i) is None for i in items):
        return EXIT_SERVER
    return EXIT_OK


def cmd_status(args) -> int:
    summary = status(Path(args.rec_dir))
    if args.json:
        print(json.dumps(summary, indent=1))
    else:
        print(f"recognition status {args.rec_dir}: {summary['items']} item(s)")
        for key, m in summary["models"].items():
            print(f"  {key} ({m['slug']}): {m['answered']} answered, {m['stale']} stale, {m['failed']} failed, "
                  f"{m['missing']} missing{' (incomplete)' if m['incomplete'] else ''}")
    return EXIT_OK if summary["complete"] else EXIT_INCOMPLETE


def main(argv=None, client_factory=None) -> int:
    """``client_factory(info, server)`` replaces the vLLM client (tests); it skips the health check."""
    args = parse_args(argv)
    try:
        if args.command == "ask":
            return cmd_ask(args, client_factory)
        return cmd_status(args)
    except (UsageError, ValueError) as exc:
        print(f"recognition answers {args.command}: {exc}", file=sys.stderr)
        return EXIT_SERVER


if __name__ == "__main__":
    sys.exit(main())
