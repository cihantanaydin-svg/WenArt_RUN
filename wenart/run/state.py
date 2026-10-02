"""Stage records, fingerprints and project states of a full run (docs/milestone6.md §1.2).

What: one JSON record per project and stage, ``<out_dir>/run/<stage>.json``::

    {"schema_version": "0.1", "kind": "stage_record", "project": "synthetic-04", "stage": "layout",
     "rc": 0, "status": "ok", "seconds": 91.2, "fingerprint": "<sha256>",
     "inputs": {"<path>": "<canonical sha256>"}, "outputs": ["building_furnished.json"],
     "started_utc": "...", "git_commit": "...", "log": "logs/layout.log", "note": null,
     "run_id": "...", "steps": [{"name": "layout", "rc": 0, "seconds": 91.2}]}

``run_id`` names the run that wrote the record (an older run's record of a
stage this run did not reach stays on the volume, and the run manifest lists
only this run's records); ``steps`` lists the commands of the stage without
their arguments (a private project's file names stay in the log only).

Why: a pod that the deadline cut is resumed with the same command; a stage
whose inputs, arguments and code did not change is then skipped (status
``reused``) instead of being run again. The hash of a JSON input ignores the
volatile keys (``created_utc``, ``seconds``, ...), so a re-run pipeline that
only wrote a new time stamp does not re-run every later stage.

How:
- ``canonical_sha256`` (re-exported from ``wenart.canonical``) hashes inputs;
- ``fingerprint(stage, version, args, inputs, code)`` =
  sha256 of ``json([stage, version, args, sorted(inputs.items()), code])``;
- ``code_hash(patterns)`` = sha256 of the source files of the stage (globs
  relative to the repo root, ``**`` for a folder);
- ``reusable(previous, fingerprint, out_dir)``: the stored fingerprint
  equals the new one, the stored status is ``ok`` or ``warning`` (or
  ``reused``, which carries over the status of the run that made the
  outputs) and every listed output exists;
- ``project_state(records)``: ``needs_review`` when stage 0 or 1 says so,
  ``failed`` when any stage failed, ``incomplete`` when any stage was cut,
  else ``ok``.

Stdlib only (the orchestrator imports it before any heavy package).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional, Union

from wenart.canonical import VOLATILE_KEYS, canonical_json_bytes, canonical_sha256, strip_volatile  # noqa: F401

__all__ = ["VOLATILE_KEYS", "canonical_json_bytes", "canonical_sha256", "strip_volatile", "STATUSES", "GOING_ON",
           "TERMINAL", "REUSABLE", "SKIP_REASONS", "PROJECT_STATES", "StageRecord", "record_path", "log_path",
           "read_record", "write_record", "write_json", "private_record", "file_hashes", "code_hash", "fingerprint",
           "reusable", "project_state", "git_commit", "utc_now", "worst"]
REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "0.1"

STATUSES = ("ok", "reused", "warning", "skipped", "failed", "needs_review", "incomplete")
# A project goes on after these; it stops at the others (its first terminal state).
GOING_ON = ("ok", "reused", "warning", "skipped")
TERMINAL = ("failed", "needs_review", "incomplete")
# A stored record can be reused when it ended ok or warning; a "reused" record carries over the status of the
# run that made the outputs, so it can be reused again (a third run of an unchanged project).
REUSABLE = ("ok", "warning", "reused")
SKIP_REASONS = ("private only", "no style photos", "polish off", "no empty room", "smoke profile",
                "gate not validated", "not in this phase")
PROJECT_STATES = ("ok", "needs_review", "failed", "incomplete")
# Stages whose own needs_review makes the whole project needs_review (§1.2).
REVIEW_STAGES = ("intake", "pipeline")
# How bad a status is, when several parts of one stage (two model sessions) are merged.
SEVERITY = {"skipped": 0, "reused": 1, "ok": 2, "warning": 3, "incomplete": 4, "failed": 5, "needs_review": 6}


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def worst(statuses: Iterable[str]) -> Optional[str]:
    """The most severe status of ``statuses`` (None for none)."""
    found = [s for s in statuses if s in SEVERITY]
    return max(found, key=lambda s: SEVERITY[s]) if found else None


# --------------------------------------------------------------------------
# Records
# --------------------------------------------------------------------------

@dataclass
class StageRecord:
    project: str
    stage: str
    status: str
    rc: Optional[int] = None
    seconds: float = 0.0
    fingerprint: Optional[str] = None
    inputs: dict = field(default_factory=dict)
    outputs: list = field(default_factory=list)
    started_utc: str = ""
    git_commit: Optional[str] = None
    log: Optional[str] = None
    note: Optional[str] = None
    run_id: Optional[str] = None
    steps: list = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.status not in STATUSES:
            raise ValueError(f"unknown stage status {self.status!r} (known: {', '.join(STATUSES)})")

    def to_dict(self) -> dict:
        return {"schema_version": SCHEMA_VERSION, "kind": "stage_record", "project": self.project,
                "stage": self.stage, "rc": self.rc, "status": self.status, "seconds": round(float(self.seconds), 2),
                "fingerprint": self.fingerprint, "inputs": dict(self.inputs), "outputs": list(self.outputs),
                "started_utc": self.started_utc, "git_commit": self.git_commit, "log": self.log,
                "note": self.note, "run_id": self.run_id, "steps": [dict(s) for s in self.steps]}

    @classmethod
    def from_dict(cls, data: dict) -> "StageRecord":
        return cls(project=str(data.get("project") or ""), stage=str(data.get("stage") or ""),
                   status=str(data.get("status") or "failed"), rc=data.get("rc"),
                   seconds=float(data.get("seconds") or 0.0), fingerprint=data.get("fingerprint"),
                   inputs=dict(data.get("inputs") or {}), outputs=list(data.get("outputs") or []),
                   started_utc=str(data.get("started_utc") or ""), git_commit=data.get("git_commit"),
                   log=data.get("log"), note=data.get("note"), run_id=data.get("run_id"),
                   steps=list(data.get("steps") or []))

    def brief(self) -> dict:
        """``{stage, status, seconds, note}`` (the run manifest's stage list)."""
        return {"stage": self.stage, "status": self.status, "seconds": round(float(self.seconds), 1),
                "note": self.note}


def run_dir(out_dir: Union[str, Path]) -> Path:
    return Path(out_dir) / "run"


def record_path(out_dir: Union[str, Path], stage: str) -> Path:
    return run_dir(out_dir) / f"{stage}.json"


def log_path(out_dir: Union[str, Path], stage: str) -> Path:
    """Where every subprocess of ``stage`` writes its output (§1.1)."""
    return run_dir(out_dir) / "logs" / f"{stage}.log"


def read_record(out_dir: Union[str, Path], stage: str) -> Optional[StageRecord]:
    """The stored record of ``stage`` (None when missing or unreadable)."""
    path = record_path(out_dir, stage)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return StageRecord.from_dict(data) if isinstance(data, dict) else None
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def write_json(path: Union[str, Path], data) -> Path:
    """JSON with indent 1, written to a temporary file first and then renamed (a reader never sees half)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def write_record(out_dir: Union[str, Path], record: StageRecord) -> Path:
    return write_json(record_path(out_dir, record.stage), record.to_dict())


def private_record(data: dict) -> dict:
    """A stage record as a private project's results keep it: without the ``inputs`` map (§2.1)."""
    return {k: v for k, v in data.items() if k != "inputs"}


# --------------------------------------------------------------------------
# Hashes and fingerprints
# --------------------------------------------------------------------------

def _text(path) -> str:
    from wenart.views import repo_path_text   # lazy: wenart.views imports numpy
    return repo_path_text(path)


def file_hashes(paths: Iterable[Union[str, Path]]) -> dict[str, Optional[str]]:
    """``{path text: canonical sha256}`` (None for a missing file or folder)."""
    return {_text(p): canonical_sha256(p) for p in paths}


def _code_files(patterns: Iterable[str], repo_root: Path) -> list[Path]:
    files: set[Path] = set()
    for pattern in patterns:
        if pattern.endswith("/**"):                 # a whole folder
            matches = (repo_root / pattern[:-3]).rglob("*")
        elif any(ch in pattern for ch in "*?["):
            matches = repo_root.glob(pattern)
        else:
            path = repo_root / pattern
            matches = path.rglob("*") if path.is_dir() else [path]
        for m in matches:
            if m.is_file() and "__pycache__" not in m.parts and m.suffix != ".pyc":
                files.add(m)
    return sorted(files)


def code_hash(patterns: Iterable[str], repo_root: Union[str, Path] = REPO_ROOT) -> str:
    """sha256 of the sorted ``(relative path, raw sha256)`` list of the files matched by ``patterns``."""
    root = Path(repo_root)
    entries = []
    for f in _code_files(patterns, root):
        entries.append([f.relative_to(root).as_posix(), hashlib.sha256(f.read_bytes()).hexdigest()])
    return hashlib.sha256(json.dumps(entries, separators=(",", ":")).encode("utf-8")).hexdigest()


def fingerprint(stage: str, version: str, args: list, inputs: dict, code: str) -> str:
    """sha256 of ``json([stage, version, args, sorted(inputs.items()), code])``."""
    payload = [stage, version, list(args), sorted([str(k), v] for k, v in inputs.items()), code]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
                          .encode("utf-8")).hexdigest()


def reusable(previous: Optional[StageRecord], fp: str, out_dir: Union[str, Path]) -> bool:
    """True when ``previous`` has this fingerprint, ended ok, warning or reused and all its outputs exist."""
    if previous is None or not fp or previous.fingerprint != fp or previous.status not in REUSABLE:
        return False
    out = Path(out_dir)
    return all((out / rel).exists() for rel in previous.outputs)


# --------------------------------------------------------------------------
# Project state
# --------------------------------------------------------------------------

def project_state(records: Iterable[StageRecord]) -> str:
    """``needs_review`` | ``failed`` | ``incomplete`` | ``ok`` of one project's records (§1.2)."""
    records = list(records)
    if any(r.stage in REVIEW_STAGES and r.status == "needs_review" for r in records):
        return "needs_review"
    if any(r.status in ("failed", "needs_review") for r in records):
        return "failed"
    if any(r.status == "incomplete" for r in records):
        return "incomplete"
    return "ok"


# --------------------------------------------------------------------------
# Git commit (read from .git, no subprocess)
# --------------------------------------------------------------------------

def _git_dir(repo_root: Path) -> Optional[Path]:
    dot = repo_root / ".git"
    if dot.is_dir():
        return dot
    if dot.is_file():   # a worktree: "gitdir: <path>"
        text = dot.read_text(encoding="utf-8").strip()
        if text.startswith("gitdir:"):
            path = Path(text.split(":", 1)[1].strip())
            return path if path.is_absolute() else (repo_root / path).resolve()
    return None


def _packed_ref(git_dir: Path, ref: str) -> Optional[str]:
    packed = git_dir / "packed-refs"
    if not packed.is_file():
        return None
    for line in packed.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[1] == ref and not line.startswith(("#", "^")):
            return parts[0]
    return None


def git_commit(repo_root: Union[str, Path] = REPO_ROOT) -> Optional[str]:
    """The checked-out commit (sha) of ``repo_root``, None when it cannot be read."""
    try:
        git_dir = _git_dir(Path(repo_root))
        if git_dir is None:
            return None
        head = (git_dir / "HEAD").read_text(encoding="utf-8").strip()
        if not head.startswith("ref:"):
            return head or None
        ref = head.split(":", 1)[1].strip()
        dirs = [git_dir]
        common = git_dir / "commondir"
        if common.is_file():
            c = Path(common.read_text(encoding="utf-8").strip())
            dirs.append(c if c.is_absolute() else (git_dir / c).resolve())
        for d in dirs:
            if (d / ref).is_file():
                return (d / ref).read_text(encoding="utf-8").strip() or None
        for d in dirs:
            sha = _packed_ref(d, ref)
            if sha:
                return sha
    except OSError:
        return None
    return None
