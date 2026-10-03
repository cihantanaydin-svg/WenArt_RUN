"""Recognition questions and their answers: one round of questions, answered on the pod (docs/milestone7.md §1.4).

What: the CPU pipeline cannot call a vision-language model, so it writes every question it has into
``<out>/recognition/requests.json`` and exits 4; a GPU stage answers them with this module's CLI; the pipeline then
runs again and reads the answers with ``load``.

- ``requests.json`` = ``{"schema_version": "0.1", "kind": "recognition_requests", "project", "crop_version",
  "models": {key: {id, slug, pass}}, "items": [{"key", "task": "symbol_type|room_label", "page", "images":
  ["crops/<key>_ctx.png", "crops/<key>_iso.png"] (or ["crops/<key>.png"]), "context": {...},
  "input_sha256"}]}``; image paths are relative to ``<out>/recognition/``. ``write_requests`` writes it,
  ``read_requests`` reads it.
- ``answers_<slug>.json`` (``slug`` from ``check.yaml models.<key>.slug``) = the M5 answer-store pattern:
  ``{"schema_version", "kind": "recognition_answers", "model_key", "model", "slug", "incomplete", "calls": {<key>:
  {task, input_sha256, data, raw_text, error, attempts, latency_s, model, seed, images[, seeded_from]}}}``,
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
# Requests
# --------------------------------------------------------------------------

def check_item(item: dict) -> None:
    """ValueError when a request item does not have the §1.4 shape."""
    for name in ("key", "task", "images", "input_sha256"):
        if name not in item:
            raise ValueError(f"request item without {name!r}: {item.get('key')!r}")
    if item["task"] not in schemas.M7_TASKS:
        raise ValueError(f"request {item['key']!r}: unknown task {item['task']!r}")
    if not item["images"] or not all(isinstance(p, str) for p in item["images"]):
        raise ValueError(f"request {item['key']!r}: images must be a non-empty list of paths")
    if not _SHA256.match(str(item["input_sha256"])):
        raise ValueError(f"request {item['key']!r}: input_sha256 is not a sha256 hex digest")


def write_requests(out_dir: Path, project: str, items: list[dict]) -> Path:
    """Write ``<out_dir>/requests.json`` (``out_dir`` = ``<out>/recognition``); items keep the caller's order."""
    from wenart.recognition.crops import CROP_VERSION
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
    return data is not None and task in schemas.M7_SCHEMAS and not schemas.validation_errors(task, data)


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
        stored answers stale even under the same slug)."""
        if not rec or rec.get("input_sha256") != item["input_sha256"]:
            return False
        model = self.data.get("model") or ""
        return not (model and rec.get("model") and rec.get("model") != model)

    def valid(self, item: dict) -> Optional[dict]:
        """The stored record of ``item`` when it is current (key, input hash, model) and schema-valid, else None."""
        rec = self.calls.get(item["key"])
        if not self.current(rec, item):
            return None
        if not valid_answer(item["task"], rec.get("data")):
            return None
        return rec

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
    is schema-valid into ``store`` (only for items that have no current answer). Returns the number copied."""
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
        rec = calls.get(item["key"])
        if not store.current(rec, item):
            continue
        if not valid_answer(item["task"], rec.get("data")):
            continue
        new = dict(rec)
        new["seeded_from"] = str(seed_path)
        store.put(item["key"], new, save=False)
        copied += 1
    if copied:
        store.save()
    return copied


# --------------------------------------------------------------------------
# Asking
# --------------------------------------------------------------------------

def call_args(item: dict, rec_dir: Path) -> dict:
    """The ``VLMClient.run_schema`` arguments of one request item."""
    task = item["task"]
    images = [Path(rec_dir) / p for p in item["images"]]
    labels = list(prompts.SYMBOL_IMAGE_LABELS) if task == "symbol_type" else None
    if labels is not None and len(labels) != len(images):
        labels = None
    return {"images": images, "prompt": prompts.m7_prompt(task), "schema": schemas.M7_SCHEMAS[task],
            "labels": labels, "task": task}


def record_of(item: dict, result, model: str, seed: int) -> dict:
    return {"task": item["task"], "input_sha256": item["input_sha256"], "data": result.data,
            "raw_text": result.raw_text, "error": result.error, "attempts": result.attempts,
            "latency_s": round(float(result.latency_s), 3), "model": model, "seed": seed,
            "images": list(item["images"])}


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

    Only this thread writes the answers file. Returns ``{"asked", "reused", "failed", "left", "incomplete"}``.
    """
    stats = {"asked": 0, "reused": 0, "failed": 0, "left": 0, "incomplete": False}
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
    started, abandoned = 0, 0
    while True:
        while started < len(pending) and len(running) < max(1, int(workers)):
            if deadline is not None and clock() >= deadline:
                break
            item = pending[started]
            args = call_args(item, rec_dir)
            running[started] = item

            def call(args=args):
                return client.run_schema([str(p) for p in args["images"]], args["prompt"], args["schema"],
                                         seed=seed, task=args["task"], max_side=0, labels=args["labels"],
                                         system_prompt=prompts.M7_SYSTEM_PROMPT)
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
        store.put(item["key"], rec)
        stats["asked"] += 1
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
          f"({stats['failed']} failed), {stats['reused']} reused, {stats['left']} left"
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
