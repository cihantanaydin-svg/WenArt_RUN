"""Canonical content hashes (docs/milestone6.md §1.2).

What: ``canonical_sha256(path)`` is a sha256 that ignores what changes on every
run without changing the content: for a ``.json`` file the sha256 of its
canonical JSON (sorted keys, compact separators) after removing the volatile
keys (``created_utc``, ``seconds``, ...) at any depth; for any other file its raw
bytes; for a folder the sha256 of the sorted ``(relative path, sha)`` list.

Why: the pipeline writes a new ``created_utc`` on every run; fit and decor copy
it, so the bytes of ``building_final.json`` changed on every re-run and every
stage after it (build, render, polish, check) ran again although nothing had
changed (M6 research, two pipeline runs differ only in that key).

How: stdlib only, so it also runs inside Blender's Python (``build.py``).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Union

VOLATILE_KEYS = frozenset({"created_utc", "updated_utc", "generated_utc", "started_utc", "finished_utc",
                           "seconds", "latency_s"})


def strip_volatile(obj: Any) -> Any:
    """A copy of ``obj`` without the volatile keys at any depth."""
    if isinstance(obj, dict):
        return {k: strip_volatile(v) for k, v in obj.items() if k not in VOLATILE_KEYS}
    if isinstance(obj, list):
        return [strip_volatile(v) for v in obj]
    return obj


def canonical_json_bytes(obj: Any) -> bytes:
    """Sorted-key compact JSON of ``obj`` without the volatile keys (UTF-8)."""
    return json.dumps(strip_volatile(obj), sort_keys=True, ensure_ascii=False,
                      separators=(",", ":")).encode("utf-8")


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_sha256(path: Union[str, Path]) -> str | None:
    """Canonical sha256 (hex) of a file or folder; None when ``path`` does not exist.

    A ``.json`` file that is not valid JSON is hashed by its raw bytes.
    """
    p = Path(path)
    if p.is_dir():
        entries = []
        for f in sorted(q for q in p.rglob("*") if q.is_file()):
            entries.append([f.relative_to(p).as_posix(), canonical_sha256(f)])
        return hashlib.sha256(json.dumps(entries, separators=(",", ":")).encode("utf-8")).hexdigest()
    if not p.is_file():
        return None
    if p.suffix.lower() == ".json":
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return _file_sha256(p)
        return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()
    return _file_sha256(p)
