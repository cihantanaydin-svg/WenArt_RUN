"""A fake vLLM server for the smoke profile of the full run (docs/milestone6.md §2.5).

What: a stdlib ``http.server`` on a free local port with ``GET /health``,
``GET /v1/models`` and ``POST /v1/chat/completions``. Every completion
answers a minimal valid instance of the JSON schema the request carries
(``structured_outputs.json`` as ``wenart.recognition.vlm_client`` sends it,
or an OpenAI ``response_format.json_schema.schema``): enum -> first value,
const -> the value, integer -> minimum (else 0), number -> minimum (else 0),
string -> "" (``minLength`` x's when the schema asks for more), boolean ->
false, array -> ``minItems`` copies, object -> its required keys. The answer
is deterministic (the same request gives the same answer).

Like vLLM's structured-output backend (xgrammar), it refuses a schema that
uses a JSON-schema keyword xgrammar does not implement (``GRAMMAR_UNSUPPORTED``:
uniqueItems, patternProperties, if/then/else, not, contains, minContains,
maxContains, dependentRequired, propertyNames), anywhere in the schema, with
HTTP 400 and vLLM's error body (``{"error": {"message": "Grammar error:
Unimplemented keys: [\"uniqueItems\"]", "type": "BadRequestError", ...}}``,
as the M7 prep pod's vLLM answered every Objaverse judge call on 3 Oct 2026).
So a schema the real server would refuse fails in the CPU tests too.

Why: the orchestrator's smoke run (``python -m wenart.run pod --profile
smoke --vlm-url URL``) drives every VLM stage (recognition questions, style
photos, layout, vision check, realism v2) through the real clients without a
GPU or a model. Its answers are the first enum value of every field, so the
two recognition passes always agree: the smoke profile runs
``pipeline_final`` with ``--no-ai`` (docs/milestone7.md §9.1), so these
answers never type a piece.

How: ``with FakeVLM() as url: ...`` in a test, or ``python
tests/fakes/fake_vlm.py [--port N]`` (prints ``FAKE_VLM_URL <url>``, serves
until stopped). ``FakeVLM.requests`` counts the completions per model.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_YAML = REPO_ROOT / "wenart" / "vision_check" / "check.yaml"
# JSON-schema keywords vLLM's xgrammar backend does not implement: a request whose schema uses one is refused with
# HTTP 400 "Grammar error: Unimplemented keys: [...]" (prep pod log, 3 Oct 2026: uniqueItems).
GRAMMAR_UNSUPPORTED = ("uniqueItems", "patternProperties", "if", "then", "else", "not", "contains", "minContains",
                       "maxContains", "dependentRequired", "propertyNames")
_NAME_MAPS = ("properties", "patternProperties", "$defs", "definitions", "dependentSchemas")   # name -> subschema
_SUBSCHEMA_LISTS = ("anyOf", "oneOf", "allOf", "prefixItems")
_SUBSCHEMAS = ("items", "additionalProperties", "not", "if", "then", "else", "contains", "propertyNames",
               "unevaluatedProperties", "unevaluatedItems")


def default_models() -> list[str]:
    """The model ids of ``check.yaml`` (the clients ask for them by name)."""
    try:
        import yaml
        models = (yaml.safe_load(CHECK_YAML.read_text(encoding="utf-8")) or {}).get("models") or {}
        return [str(m["id"]) for m in models.values() if isinstance(m, dict) and m.get("id")]
    except Exception:  # noqa: BLE001 - a fake without PyYAML still serves something
        return ["fake/model"]


def _resolve(ref: str, root: dict) -> dict:
    if not ref.startswith("#/"):
        return {}
    node: Any = root
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or part not in node:
            return {}
        node = node[part]
    return node if isinstance(node, dict) else {}


def minimal_instance(schema: Any, root: Optional[dict] = None, depth: int = 0) -> Any:
    """The smallest valid instance of ``schema`` under the rules of the module docstring."""
    if not isinstance(schema, dict) or depth > 50:
        return None
    root = schema if root is None else root
    if "$ref" in schema:
        return minimal_instance(_resolve(str(schema["$ref"]), root), root, depth + 1)
    if "const" in schema:
        return schema["const"]
    if isinstance(schema.get("enum"), list) and schema["enum"]:
        return schema["enum"][0]
    for key in ("anyOf", "oneOf", "allOf"):
        if isinstance(schema.get(key), list) and schema[key]:
            return minimal_instance(schema[key][0], root, depth + 1)
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = next((k for k in kind if k != "null"), kind[0] if kind else None)
    if kind is None:
        kind = "object" if "properties" in schema else "array" if "items" in schema else None
    if kind == "object":
        props = schema.get("properties") or {}
        return {k: minimal_instance(props.get(k, {}), root, depth + 1) for k in schema.get("required") or []}
    if kind == "array":
        n = int(schema.get("minItems") or 0)
        prefix = schema.get("prefixItems") if isinstance(schema.get("prefixItems"), list) else []
        out = [minimal_instance(p, root, depth + 1) for p in prefix[:n]]
        item = schema.get("items") if isinstance(schema.get("items"), dict) else {}
        out += [minimal_instance(item, root, depth + 1) for _ in range(n - len(out))]
        return out
    if kind == "string":
        return "x" * int(schema.get("minLength") or 0)
    if kind in ("integer", "number"):
        if "minimum" in schema:
            value = schema["minimum"]
        elif "exclusiveMinimum" in schema:
            value = schema["exclusiveMinimum"] + (1 if kind == "integer" else 1e-6)
        else:
            value = 0
            if "maximum" in schema and schema["maximum"] < 0:
                value = schema["maximum"]
        return int(value) if kind == "integer" else value
    if kind == "boolean":
        return False
    return None


def unsupported_keys(schema: Any) -> list[str]:
    """The ``GRAMMAR_UNSUPPORTED`` keywords used anywhere in ``schema`` (walked into properties, $defs, items,
    anyOf/oneOf/allOf, ...; a property *named* like a keyword is not one), in order of appearance."""
    found: list[str] = []

    def walk(node: Any, depth: int = 0) -> None:
        if not isinstance(node, dict) or depth > 100:
            return
        for key in node:
            if key in GRAMMAR_UNSUPPORTED and key not in found:
                found.append(key)
        for key, value in node.items():
            if key in _NAME_MAPS and isinstance(value, dict):
                for sub in value.values():
                    walk(sub, depth + 1)
            elif key in _SUBSCHEMA_LISTS and isinstance(value, list):
                for sub in value:
                    walk(sub, depth + 1)
            elif key == "items" and isinstance(value, list):
                for sub in value:
                    walk(sub, depth + 1)
            elif key in _SUBSCHEMAS and isinstance(value, dict):
                walk(value, depth + 1)

    walk(schema)
    return found


def grammar_error(schema: Any) -> Optional[dict]:
    """vLLM's HTTP 400 body for a schema xgrammar cannot compile (None when it can)."""
    keys = unsupported_keys(schema)
    if not keys:
        return None
    return {"error": {"message": f"Grammar error: Unimplemented keys: {json.dumps(keys)}",
                      "type": "BadRequestError", "param": None, "code": 400}}


def request_schema(body: dict) -> Optional[dict]:
    """The JSON schema of a chat-completions request (vLLM ``structured_outputs`` or OpenAI ``response_format``)."""
    so = body.get("structured_outputs")
    if isinstance(so, dict) and isinstance(so.get("json"), dict):
        return so["json"]
    rf = body.get("response_format")
    if isinstance(rf, dict) and isinstance(rf.get("json_schema"), dict):
        schema = rf["json_schema"].get("schema")
        if isinstance(schema, dict):
            return schema
    if isinstance(body.get("guided_json"), dict):
        return body["guided_json"]
    return None


def completion(body: dict, served: list[str], n: int) -> dict:
    schema = request_schema(body)
    answer = minimal_instance(schema) if schema is not None else {}
    model = str(body.get("model") or (served[0] if served else "fake/model"))
    return {"id": f"fake-{n}", "object": "chat.completion", "created": 0, "model": model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": json.dumps(answer)},
                         "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}}


class FakeVLM:
    """The fake server; ``with FakeVLM() as url`` gives the OpenAI base URL (``http://127.0.0.1:<port>/v1``)."""

    def __init__(self, models: Optional[list[str]] = None, port: int = 0, host: str = "127.0.0.1"):
        self.models = list(models) if models else default_models()
        self.requests: dict[str, int] = {}
        self.refused: list[list[str]] = []      # the unsupported keywords of every refused request
        self._lock = threading.Lock()
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):  # quiet
                return

            def _send(self, code: int, data) -> None:
                raw = json.dumps(data).encode("utf-8") if data is not None else b""
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_GET(self):  # noqa: N802 - http.server API
                if self.path == "/health":
                    self._send(200, None)
                elif self.path.rstrip("/") == "/v1/models":
                    self._send(200, {"object": "list", "data": [{"id": m, "object": "model", "owned_by": "fake"}
                                                                for m in fake.models]})
                else:
                    self._send(404, {"error": "not found"})

            def do_POST(self):  # noqa: N802 - http.server API
                if self.path.rstrip("/") != "/v1/chat/completions":
                    self._send(404, {"error": "not found"})
                    return
                length = int(self.headers.get("Content-Length") or 0)
                try:
                    body = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
                except ValueError:
                    self._send(400, {"error": "bad json"})
                    return
                schema = request_schema(body)
                refusal = grammar_error(schema) if schema is not None else None
                with fake._lock:
                    model = str(body.get("model") or "")
                    fake.requests[model] = fake.requests.get(model, 0) + 1
                    n = sum(fake.requests.values())
                    if refusal is not None:
                        fake.refused.append(unsupported_keys(schema))
                if refusal is not None:
                    self._send(400, refusal)
                    return
                self._send(200, completion(body, fake.models, n))

        self.server = ThreadingHTTPServer((host, port), Handler)
        self.server.daemon_threads = True
        self._thread: Optional[threading.Thread] = None

    @property
    def port(self) -> int:
        return int(self.server.server_address[1])

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/v1"

    def start(self) -> str:
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self._thread.start()
        return self.url

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def __enter__(self) -> str:
        return self.start()

    def __exit__(self, *exc) -> None:
        self.stop()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="fake vLLM server (minimal schema-valid answers)")
    parser.add_argument("--port", type=int, default=0, help="port (default: a free one)")
    parser.add_argument("--models", default=None, help="served model ids, comma separated (default check.yaml)")
    args = parser.parse_args(argv)
    fake = FakeVLM([m for m in (args.models or "").split(",") if m] or None, port=args.port)
    print(f"FAKE_VLM_URL {fake.url}", flush=True)
    try:
        fake.server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        fake.server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
