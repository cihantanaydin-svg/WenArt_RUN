"""CLI of the orchestrator (docs/milestone11.md §2 "CLI", contract §17.3).

    python -m wenart.agent apply <project_out>
    python -m wenart.agent run <project_out> --server URL [--model-key agent] [--rounds 4] [--deadline EPOCH]
                                              [--workers 4]
    python -m wenart.agent check-log <project_out>
    python -m wenart.agent metrics <project_out> [--compare results/compare/<p>/agent_metrics.md --label L]

- ``apply``: replays the accepted furniture, room and level edits of ``orchestrator/overrides.json`` on
  ``building_decor.json`` and writes ``building_agent.json`` with ``agent_overrides`` (``overrides.apply``; M12: the
  decor follows its hosts after every replayed edit); idempotent. Exit 0, 1 without ``building_decor.json``. The
  pod's stage ``agent_apply`` (``wenart.run``) runs it before ``refit``.
- ``run``: the critic and planner rounds on an existing project output against a running agent server, without
  re-running stages (the accepted edits go to ``overrides.json``; the next ``wenart.run pod`` applies them). The
  pod runs the loop inside the scheduler instead, with re-runs and previews (``wenart.run.scheduler``).
- ``check-log``: validates ``orchestrator/log.json`` against ``log.schema.json`` (exit 1 on an error).
- ``metrics`` (M12, docs/milestone12.md §5.5): ``orchestrator/metrics.json`` and a row across runs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def cmd_apply(args) -> int:
    from wenart.agent import overrides as OV
    try:
        summary = OV.apply(Path(args.project_out))
    except FileNotFoundError as exc:
        print(f"agent apply: {exc}", file=sys.stderr)
        return 1
    print(f"agent apply: {summary['edits']} accepted edit(s), {len(summary['replayed'])} furniture edit(s) replayed, "
          f"{len(summary['not_replayed'])} not replayed -> {summary['out']}")
    return 0


def cmd_run(args) -> int:
    from wenart.agent import loop as LP
    from wenart.agent import model as M
    model = M.from_check_yaml(args.server, args.model_key)
    loop = LP.AgentLoop(Path(args.project_out), model, deadline=args.deadline, max_rounds=args.rounds,
                        workers=args.workers,
                        out=lambda line: print(line, flush=True))
    summary = loop.run()
    print(f"agent run: {summary['accepted']} edit(s) accepted in {len(summary['rounds'])} round(s); stop: "
          f"{(summary['stop'] or {}).get('reason')}")
    return 0


def cmd_metrics(args) -> int:
    """Milestone 12 (§5.5): ``orchestrator/metrics.json`` of a project output, and with ``--compare`` its row in
    ``results/compare/<p>/agent_metrics.md`` (``--label``; ``--since-seq`` for an old log with several runs)."""
    from wenart.agent import log as LG
    from wenart.agent import memory as MEM
    from wenart.agent import metrics as MX
    folder = LG.orchestrator_dir(args.project_out)
    try:
        log = json.loads((folder / LG.LOG_JSON).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"agent metrics: {exc}", file=sys.stderr)
        return 1
    mem_path = folder / MEM.MEMORY_JSON
    memory = json.loads(mem_path.read_text(encoding="utf-8")) if mem_path.is_file() else None
    m = MX.compute(log, memory, since_seq=args.since_seq, since_call=args.since_call)
    LG.write_json_atomic(folder / MX.METRICS_JSON, m)
    if args.compare:
        MX.update_compare(Path(args.compare), args.label or log.get("started_utc") or "run", m)
    e = m["edits"]
    print(f"agent metrics: {e['accepted']} accepted, {e['rejected']} rejected; rooms visited {m['rooms']['planner']} "
          f"of {m['rooms']['fixable']} with fixable findings -> {folder / MX.METRICS_JSON}")
    return 0


def cmd_check_log(args) -> int:
    from wenart.agent import log as LG
    path = LG.orchestrator_dir(args.project_out) / LG.LOG_JSON
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"agent check-log: {path}: {exc}", file=sys.stderr)
        return 1
    errors = LG.validate_log(data)
    for e in errors[:20]:
        print(f"agent check-log: {e}", file=sys.stderr)
    print(f"agent check-log: {len(data.get('events') or [])} events, {len(errors)} schema error(s)")
    return 1 if errors else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m wenart.agent", description="the M11 orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)
    ap = sub.add_parser("apply", help="replay overrides.json on building_decor.json -> building_agent.json")
    ap.add_argument("project_out")
    rp = sub.add_parser("run", help="critic and planner rounds against a running agent server (no re-runs)")
    rp.add_argument("project_out")
    rp.add_argument("--server", required=True, help="OpenAI base URL of the agent server (http://127.0.0.1:8001/v1)")
    rp.add_argument("--model-key", default="agent", help="check.yaml models key (agent | agent_fast)")
    rp.add_argument("--rounds", type=int, default=4)
    rp.add_argument("--deadline", type=float, default=None, help="epoch seconds")
    rp.add_argument("--workers", type=int, default=4, help="parallel room sessions (the server's sequences)")
    cl = sub.add_parser("check-log", help="validate orchestrator/log.json")
    cl.add_argument("project_out")
    mp = sub.add_parser("metrics", help="orchestrator/metrics.json (+ a row of results/compare/<p>/agent_metrics.md)")
    mp.add_argument("project_out")
    mp.add_argument("--compare", help="results/compare/<p>/agent_metrics.md to add this run's row to")
    mp.add_argument("--label", help="the row's label (default: the log's start time)")
    mp.add_argument("--since-seq", type=int, default=None, help="first event of the run (an M11 log with several runs)")
    mp.add_argument("--since-call", type=int, default=None, help="first model call of the run (with --since-seq)")
    args = parser.parse_args(argv)
    if args.command == "apply":
        return cmd_apply(args)
    if args.command == "run":
        return cmd_run(args)
    if args.command == "metrics":
        return cmd_metrics(args)
    return cmd_check_log(args)


if __name__ == "__main__":
    raise SystemExit(main())
