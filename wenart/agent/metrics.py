"""Agent metrics of a run (docs/milestone12.md §5.5 D20).

What: ``compute(log, memory)`` reads the decision log (``orchestrator/log.json``, only the events and calls of the
latest run: ``run_first_seq`` / ``run_first_call``) and the memory, and returns:

| key | content |
|---|---|
| ``edits`` | accepted, rejected, acceptance share, rejected by reason (the first failed check, up to its ``:``), per tool |
| ``rooms`` | covered by code (rooms checked), by vision (a critic call), by the planner (a session), the rooms with fixable critical / major findings and the share of them that got a session |
| ``findings`` | before (round 1) and after (the last round) by check and severity, and the critical / major totals |
| ``per_room`` | minutes and model calls per room session |
| ``tokens`` | prompt and completion tokens per call kind |
| ``time`` | agent minutes, seconds to the first accepted edit |
| ``memory`` | edits refused by the memory, dry runs, plans (valid / default) |

``write(project_out)`` writes ``orchestrator/metrics.json`` (the loop calls it after every round);
``compare_rows`` / ``update_compare(md_path, label, metrics)`` keep ``results/compare/<p>/agent_metrics.md`` (and its
``agent_metrics.json`` with every row) across runs; ``python -m wenart.agent metrics`` is the CLI.

Why: §5.5 targets for real03 (≥ 90 % of the rooms with fixable findings visited, ≥ 60 % of the edits accepted,
critical 0, major −50 % against run 3) need the same numbers from every run, including the M11 baseline (an M11 log
has no ``round`` or ``plan`` events: the rooms then come from the edit and finding events).

How: pure functions of the log and memory dicts; deterministic (sorted keys).
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional

from wenart.agent import log as LG
from wenart.agent import memory as MEM

METRICS_JSON = "metrics.json"
SEVERITIES = ("critical", "major", "minor")


def _t(text: Optional[str]) -> Optional[float]:
    if not text:
        return None
    try:
        return float(time.mktime(time.strptime(text, "%Y-%m-%dT%H:%M:%SZ")))
    except (TypeError, ValueError):
        return None


def reason_of(failed: list) -> str:
    """The rejection reason key: the first failed check up to its first ``:`` (``memory``, ``max_tries``,
    ``score``, ``drawn_lock`` ...)."""
    if not failed:
        return "rejected"
    return str(failed[0]).split(":", 1)[0].strip() or "rejected"


def _session_rooms(events: list[dict]) -> dict:
    """call-id tag (``r1``, ``r1-s2``) -> room, from the plan events."""
    out = {}
    for e in events:
        if e.get("kind") == "plan" and e.get("call_id"):
            out[str(e["call_id"]).rsplit("-plan", 1)[0]] = e.get("room_id")
    return out


def _tag_of(call_id: str) -> Optional[str]:
    parts = str(call_id).split("-")
    if len(parts) >= 2 and parts[1].startswith("s"):
        return f"{parts[0]}-{parts[1]}"
    return parts[0] if parts else None


def _by_check(findings: list[dict]) -> dict:
    out: dict = {}
    for e in findings:
        row = out.setdefault(str(e.get("checklist")), {s: 0 for s in SEVERITIES})
        if e.get("severity") in SEVERITIES:
            row[e["severity"]] += 1
    return {k: out[k] for k in sorted(out)}


def compute(log: dict, memory: Optional[dict] = None, *, since_seq: Optional[int] = None) -> dict:
    """The metrics of the latest run in ``log`` (module docstring); ``since_seq`` overrides the run's first event
    (an M11 log with several runs)."""
    first = int(since_seq if since_seq is not None else log.get("run_first_seq") or 1)
    events = [e for e in log.get("events") or [] if int(e.get("seq") or 0) >= first]
    calls = list(log.get("calls") or [])[int(log.get("run_first_call") or 0):] if since_seq is None else \
        list(log.get("calls") or [])
    if since_seq is not None:
        rounds_seen = {f"r{int(e.get('round') or 0)}" for e in events}
        calls = [c for c in calls if str(c.get("call_id") or "").split("-")[0] in rounds_seen]
    edits = [e for e in events if e.get("kind") in ("edit", "rejected_edit")]
    accepted = [e for e in edits if e["kind"] == "edit"]
    rejected = [e for e in edits if e["kind"] == "rejected_edit"]
    reasons: dict = {}
    for e in rejected:
        key = reason_of((e.get("validation") or {}).get("failed_checks") or [])
        reasons[key] = reasons.get(key, 0) + 1
    tools: dict = {}
    for e in edits:
        row = tools.setdefault(str(e.get("tool")), {"accepted": 0, "rejected": 0})
        row["accepted" if e["kind"] == "edit" else "rejected"] += 1
    rounds = [e for e in events if e.get("kind") == "round"]
    findings = [e for e in events if e.get("kind") == "finding" and not e.get("dropped")]
    round_ids = sorted({int(e.get("round") or 0) for e in findings})
    before = [e for e in findings if round_ids and int(e.get("round") or 0) == round_ids[0]]
    after = [e for e in findings if round_ids and int(e.get("round") or 0) == round_ids[-1]]
    piece_rooms = {e.get("target"): e.get("room_id") for e in findings if e.get("room_id")}
    if rounds:
        code_rooms = max(int((e.get("counts") or {}).get("rooms_code") or 0) for e in rounds)
        vision = sorted({r for e in rounds for r in (e.get("evidence") or {}).get("rooms_vision") or []})
        planner = sorted({r for e in rounds for r in (e.get("evidence") or {}).get("rooms_planner") or []})
        fixable = sorted({r for e in rounds for r in (e.get("evidence") or {}).get("rooms_fixable") or []})
    else:       # an M11 log: rooms of the edits (planner) and of the critical / major findings (fixable, an upper bound)
        code_rooms = len({e.get("room_id") for e in findings if e.get("room_id")})
        vision = sorted({e.get("room_id") for e in findings if e.get("source") == "vision" and e.get("room_id")})
        planner = sorted({e.get("room_id") or piece_rooms.get(e.get("target")) for e in edits
                          if e.get("room_id") or piece_rooms.get(e.get("target"))})
        fixable = sorted({e.get("room_id") for e in findings if e.get("room_id")
                          and e.get("severity") in ("critical", "major")})
    covered = [r for r in fixable if r in planner]
    tags = _session_rooms(events)
    per_room: dict = {}
    for c in calls:
        room = tags.get(_tag_of(c.get("call_id") or ""))
        if room is None or c.get("kind") not in ("chat", "plan"):
            continue
        row = per_room.setdefault(room, {"calls": 0, "seconds": 0.0})
        row["calls"] += 1
        row["seconds"] += float(c.get("seconds") or 0.0)
    tokens: dict = {}
    for c in calls:
        row = tokens.setdefault(str(c.get("kind")), {"calls": 0, "prompt": 0, "completion": 0, "seconds": 0.0})
        row["calls"] += 1
        row["prompt"] += int(c.get("prompt_tokens") or 0)
        row["completion"] += int(c.get("completion_tokens") or 0)
        row["seconds"] = round(row["seconds"] + float(c.get("seconds") or 0.0), 2)
    t_events = [_t(e.get("t")) for e in events if _t(e.get("t")) is not None]
    t0 = min(t_events) if t_events else None
    first_ok = next((_t(e.get("t")) for e in events if e.get("kind") == "edit"), None)
    memory_refused = sum(1 for e in rejected if reason_of((e.get("validation") or {}).get("failed_checks") or [])
                         == "memory")
    plans = [e for e in events if e.get("kind") == "plan"]
    n = len(edits)
    return {
        "schema_version": "m12", "project": log.get("project"), "model": log.get("model"),
        "revision": log.get("revision"), "first_seq": first,
        "rounds": len(rounds) or len(round_ids), "stop": (log.get("stop") or {}).get("reason"),
        "edits": {"accepted": len(accepted), "rejected": len(rejected),
                  "accepted_share": round(len(accepted) / n, 3) if n else None,
                  "rejected_by_reason": {k: reasons[k] for k in sorted(reasons)},
                  "by_tool": {k: tools[k] for k in sorted(tools)}},
        "rooms": {"code": code_rooms, "vision": len(vision), "planner": len(planner), "fixable": len(fixable),
                  "fixable_visited_share": round(len(covered) / len(fixable), 3) if fixable else None,
                  "planner_rooms": planner, "fixable_rooms": fixable},
        "findings": {"before": _by_check(before), "after": _by_check(after),
                     "before_totals": {s: sum(1 for e in before if e.get("severity") == s) for s in SEVERITIES},
                     "after_totals": {s: sum(1 for e in after if e.get("severity") == s) for s in SEVERITIES},
                     "first_round": round_ids[0] if round_ids else None,
                     "last_round": round_ids[-1] if round_ids else None},
        "per_room": {k: {"calls": v["calls"], "minutes": round(v["seconds"] / 60.0, 2)}
                     for k, v in sorted(per_room.items())},
        "tokens": {k: tokens[k] for k in sorted(tokens)},
        "time": {"agent_minutes": round((max(t_events) - t0) / 60.0, 2) if t_events else None,
                 "first_accepted_edit_s": round(first_ok - t0, 1) if first_ok is not None and t0 is not None
                 else None},
        "memory": {"repeats_refused": max(memory_refused, int((memory or {}).get("refused_repeats") or 0)
                                          if since_seq is None else memory_refused),
                   "dry_runs": sum(1 for e in events if e.get("kind") == "dry_run"),
                   "plans": len(plans), "plans_valid": sum(1 for e in plans if e.get("status") == "ok")},
    }


def write(project_out) -> Path:
    """``orchestrator/metrics.json`` of a project output (from its log and memory)."""
    folder = LG.orchestrator_dir(project_out)
    log = json.loads((folder / LG.LOG_JSON).read_text(encoding="utf-8"))
    mem_path = folder / MEM.MEMORY_JSON
    memory = json.loads(mem_path.read_text(encoding="utf-8")) if mem_path.is_file() else None
    return LG.write_json_atomic(folder / METRICS_JSON, compute(log, memory))


# --------------------------------------------------------------------------
# Across runs: results/compare/<p>/agent_metrics.md
# --------------------------------------------------------------------------

COMPARE_HEADER = ["run", "model", "rounds", "edits accepted / rejected", "accepted %", "rooms visited / fixable",
                  "critical before -> after", "major before -> after", "agent min", "calls", "tokens (k)",
                  "first accepted edit (s)", "repeats refused", "dry runs", "top rejection reasons"]


def compare_row(label: str, m: dict) -> list:
    e, r, f, t = m["edits"], m["rooms"], m["findings"], m["time"]
    calls = sum(v["calls"] for v in m["tokens"].values())
    tokens = sum(v["prompt"] + v["completion"] for v in m["tokens"].values())
    top = sorted(e["rejected_by_reason"].items(), key=lambda kv: (-kv[1], kv[0]))[:3]
    share = e["accepted_share"]
    return [label, str(m.get("model") or "-"), m["rounds"], f"{e['accepted']} / {e['rejected']}",
            f"{share * 100:.0f}" if share is not None else "-", f"{r['planner']} / {r['fixable']}",
            f"{f['before_totals']['critical']} -> {f['after_totals']['critical']}",
            f"{f['before_totals']['major']} -> {f['after_totals']['major']}",
            t["agent_minutes"] if t["agent_minutes"] is not None else "-", calls, round(tokens / 1000.0, 1),
            t["first_accepted_edit_s"] if t["first_accepted_edit_s"] is not None else "-",
            m["memory"]["repeats_refused"], m["memory"]["dry_runs"], ", ".join(f"{k} {v}" for k, v in top) or "-"]


def compare_markdown(project: str, rows: list[dict]) -> str:
    lines = [f"# Agent metrics across runs: {project}", "",
             "One row per orchestrated run (docs/milestone12.md §5.5); written by `python -m wenart.agent metrics`.",
             "", "| " + " | ".join(COMPARE_HEADER) + " |", "|" + "---|" * len(COMPARE_HEADER)]
    for row in rows:
        lines.append("| " + " | ".join(str(c).replace("|", "/") for c in compare_row(row["label"], row["metrics"]))
                     + " |")
    return "\n".join(lines) + "\n"


def update_compare(md_path, label: str, metrics: dict) -> Path:
    """Add or replace the row ``label`` in ``agent_metrics.json`` next to ``md_path`` and rewrite the markdown."""
    md_path = Path(md_path)
    side = md_path.with_suffix(".json")
    rows = []
    if side.is_file():
        try:
            rows = list(json.loads(side.read_text(encoding="utf-8")).get("rows") or [])
        except (OSError, ValueError):
            rows = []
    rows = [r for r in rows if r.get("label") != label] + [{"label": label, "metrics": metrics}]
    LG.write_json_atomic(side, {"project": metrics.get("project"), "rows": rows})
    md_path.write_text(compare_markdown(str(metrics.get("project") or md_path.parent.name), rows), encoding="utf-8")
    return md_path
