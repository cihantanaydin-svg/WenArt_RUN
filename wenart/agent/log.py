"""The decision log of the orchestrator (docs/milestone11.md §9; CLAUDE.md: "Everything is logged").

What: ``AgentLog`` keeps one entry per event (``check``, ``finding``, ``edit``, ``rejected_edit``, ``rerun``,
``render``, ``stop``) and every model call, and writes

- ``outputs/<p>/orchestrator/log.json`` (schema ``wenart/agent/log.schema.json``; inside this package because
  ``wenart/schema`` is the lead's),
- ``outputs/<p>/orchestrator/log.md``: the same as tables per round, before/after images side by side,
- ``outputs/<p>/orchestrator/images/``: the top-down images and the preview copies the entries link to
  (paths in the log are relative to ``orchestrator/``).

Why: nothing the agent changes may change silently; the report (``wenart/report/agent.py``) and the tests read
this file.

How: ``event(kind, round, **fields)`` numbers the entries (``seq`` from 1) and stamps them with the injectable
clock (UTC ISO text); ``save()`` writes both files atomically after every round, so a pod cut by its deadline
keeps the log of the finished rounds.
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Callable, Optional

SCHEMA_PATH = Path(__file__).with_name("log.schema.json")
LOG_DIR = "orchestrator"
LOG_JSON = "log.json"
LOG_MD = "log.md"
IMAGES_DIR = "images"
# Milestone 12: "plan" (a room session's checked plan), "dry_run" (a free validator answer) and "round" (the round
# summary with its coverage, read by metrics.py).
KINDS = ("check", "finding", "edit", "rejected_edit", "rerun", "render", "stop", "plan", "dry_run", "round")


def utc_text(t: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(float(t)))


def orchestrator_dir(project_out) -> Path:
    return Path(project_out) / LOG_DIR


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_log(data: dict) -> list[str]:
    """All violations of ``data`` against ``log.schema.json`` (empty = valid)."""
    import jsonschema
    validator = jsonschema.Draft202012Validator(load_schema())
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in sorted(validator.iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path])]


def write_json_atomic(path: Path, data) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


class AgentLog:
    """``orchestrator/log.json`` + ``log.md`` + ``images/`` of one project output (module docstring)."""

    def __init__(self, project_out, project: str = "", model: str = "", revision: str = "",
                 clock: Callable[[], float] = time.time):
        self.dir = orchestrator_dir(project_out)
        self.project = project or Path(project_out).name
        self.model = model
        self.revision = revision
        self.clock = clock
        self.events: list[dict] = []
        self.calls: list[dict] = []
        self.stop: Optional[dict] = None
        self.started_utc = utc_text(clock())
        self.finished_utc: Optional[str] = None
        self.lock = threading.RLock()        # Milestone 12: parallel room sessions log from several threads
        existing = self.dir / LOG_JSON
        if existing.is_file():
            # A resumed pod continues the earlier log (the rounds of the cut run stay listed).
            try:
                old = json.loads(existing.read_text(encoding="utf-8"))
                self.events = list(old.get("events") or [])
                self.calls = list(old.get("calls") or [])
                self.started_utc = old.get("started_utc") or self.started_utc
            except (OSError, ValueError):
                pass
        # The first event and call of this run (a resumed log keeps the earlier runs; metrics count this run).
        self.first_seq = self.next_seq()
        self.first_call = len(self.calls)

    @property
    def images_dir(self) -> Path:
        path = self.dir / IMAGES_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    def rel(self, path) -> Optional[str]:
        """``path`` relative to ``orchestrator/`` (POSIX), or as it is when outside."""
        if path is None:
            return None
        try:
            return Path(path).resolve().relative_to(self.dir.resolve()).as_posix()
        except ValueError:
            return Path(path).as_posix()

    def next_seq(self) -> int:
        return (self.events[-1]["seq"] + 1) if self.events else 1

    def event(self, kind: str, round_no: int, **fields) -> dict:
        if kind not in KINDS:
            raise ValueError(f"unknown log event kind {kind!r}")
        with self.lock:
            entry = {"seq": self.next_seq(), "round": int(round_no), "t": utc_text(self.clock()), "kind": kind}
            entry.update({k: v for k, v in fields.items() if v is not None})
            self.events.append(entry)
            if kind == "stop":
                self.stop = {"round": int(round_no), "reason": fields.get("reason"), "seq": entry["seq"]}
            return entry

    def call(self, entry: dict) -> None:
        """One model call (``AgentModel.on_call``)."""
        keep = ("call_id", "kind", "model", "revision", "seconds", "attempts", "prompt_tokens",
                "completion_tokens", "images", "tool_calls", "error")
        with self.lock:
            self.calls.append({k: entry.get(k) for k in keep if k in entry})

    def data(self) -> dict:
        with self.lock:
            return {"schema_version": "0.1", "kind": "agent_log", "project": self.project, "model": self.model,
                    "revision": self.revision, "started_utc": self.started_utc, "finished_utc": self.finished_utc,
                    "stop": self.stop, "run_first_seq": self.first_seq, "run_first_call": self.first_call,
                    "events": list(self.events), "calls": list(self.calls)}

    def save(self, final: bool = False) -> Path:
        with self.lock:
            if final:
                self.finished_utc = utc_text(self.clock())
            data = self.data()
            write_json_atomic(self.dir / LOG_JSON, data)
            (self.dir / LOG_MD).write_text(log_markdown(data), encoding="utf-8")
            return self.dir / LOG_JSON


# --------------------------------------------------------------------------
# log.md
# --------------------------------------------------------------------------

def _cell(value) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ")[:300]


def _table(header: list, rows: list) -> list[str]:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(_cell(c) for c in row) + " |" for row in rows]
    return lines


def _img(path: Optional[str]) -> str:
    return f"![]({path})" if path else ""


def _score(v: dict) -> str:
    before, after = v.get("score_before"), v.get("score_after")
    if before is None and after is None:
        return ""
    return f"{before if before is not None else '-'} -> {after if after is not None else '-'}"


def log_markdown(data: dict) -> str:
    """``log.md``: per round the checks, findings, edits (before/after images side by side), re-runs, renders and
    the stop."""
    events = data.get("events") or []
    lines = [f"# AI orchestrator log: {data.get('project')}", "",
             f"Model `{data.get('model') or '-'}` @ `{data.get('revision') or '-'}`; started "
             f"{data.get('started_utc') or '-'}, finished {data.get('finished_utc') or '-'}; "
             f"{len(events)} events, {len(data.get('calls') or [])} model calls."]
    stop = data.get("stop")
    if stop:
        lines.append(f"Stopped in round {stop.get('round')}: {stop.get('reason')}.")
    for rnd in sorted({int(e.get("round", 0)) for e in events}):
        ev = [e for e in events if int(e.get("round", 0)) == rnd]
        lines += ["", f"## Round {rnd}", ""]
        checks = [e for e in ev if e["kind"] == "check"]
        if checks:
            lines += _table(["seq", "critic", "of", "status", "counts", "note"],
                            [[e["seq"], e.get("source") or "", e.get("tool") or e.get("target") or "", e.get("status"),
                              json.dumps(e.get("counts")) if e.get("counts") else "", e.get("note")] for e in checks])
            lines.append("")
        findings = [e for e in ev if e["kind"] == "finding"]
        lines.append(f"Findings: {len(findings)} "
                     f"({sum(1 for e in findings if e.get('dropped'))} dropped).")
        if findings:
            lines += [""] + _table(["seq", "source", "check", "severity", "target", "finding", "dropped"],
                                   [[e["seq"], e.get("source"), e.get("checklist"), e.get("severity"), e.get("target"),
                                     e.get("finding"), e.get("dropped") or ""] for e in findings])
        edits = [e for e in ev if e["kind"] in ("edit", "rejected_edit")]
        if edits:
            lines += ["", "Edits:", ""]
            lines += _table(["seq", "tool", "args", "accepted", "failed checks", "score", "label", "reason",
                             "re-run from", "before", "after"],
                            [[e["seq"], e.get("tool"), json.dumps(e.get("args"), ensure_ascii=False)[:160],
                              (e.get("validation") or {}).get("accepted"),
                              ", ".join((e.get("validation") or {}).get("failed_checks") or []),
                              _score(e.get("validation") or {}), e.get("label"), e.get("reason"), e.get("rerun_from"),
                              _img(e.get("before")), _img(e.get("after"))] for e in edits])
        other = [e for e in ev if e["kind"] in ("rerun", "render")]
        if other:
            lines += ["", "Re-runs and renders:", ""]
            lines += _table(["seq", "kind", "from", "status", "views", "seconds", "before", "after", "note"],
                            [[e["seq"], e["kind"], e.get("rerun_from"), e.get("status"),
                              ", ".join(e.get("views") or []), e.get("seconds"), _img(e.get("before")),
                              _img(e.get("after")), e.get("note")] for e in other])
        stops = [e for e in ev if e["kind"] == "stop"]
        for e in stops:
            lines += ["", f"Stop: {e.get('reason')}" + (f" ({e.get('note')})" if e.get("note") else "")]
    return "\n".join(lines) + "\n"
