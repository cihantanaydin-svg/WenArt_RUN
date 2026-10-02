"""CLI of the AI polish (docs/milestone5.md §3.6).

    python -m wenart.polish run   --project-out outputs/<p> [--views all|cam,...] [--out DIR] [--force] [--deadline S]
    python -m wenart.polish sweep --project-out outputs/<p> [--views auto|cam,...] [--grid sweep|<file>] ...
    python -m wenart.polish smoke --project-out outputs/<p> [--views auto|cam,...] [--grid smoke|<file>] ...
    python -m wenart.polish report <polish_manifest.json> [--out polish_report.md]

``run`` writes into ``outputs/<p>/polish/`` (``<cam>_a<k>.png``,
``<cam>_control_<type>.png``, ``<cam>_a<k>_preview.jpg`` of the final
attempts, ``<cam>_a<k>_gate.jpg``, ``polish_manifest.json`` rewritten after
every attempt, ``polish_report.md``, ``determinism.json``); ``sweep`` into
``polish/sweep/`` and ``smoke`` into ``polish/smoke/`` (previews of every
attempt at 960 px; ``--previews final|all|none`` changes that).
``--deadline`` defaults to the environment variable ``WENART_DEADLINE``
(epoch seconds; set by ``scripts/pod_entry.sh``): after it no new attempt
starts and the manifest says ``"incomplete": true`` (exit 0).

Exit codes: 0 done (also when the deadline cut the run short), 1 when an
attempt or a gate reference failed (the view keeps the Cycles render and the
manifest says why), 2 for bad inputs (no M5 views, unknown camera or grid).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

from wenart.polish.runner import Deps, PolishError, run_polish


def env_deadline(environ=None) -> Optional[float]:
    """``WENART_DEADLINE`` as epoch seconds, None when unset or empty (ValueError when not a number)."""
    value = (os.environ if environ is None else environ).get("WENART_DEADLINE", "").strip()
    return float(value) if value else None


def summary(m: dict) -> str:
    """One line for the job log."""
    views = m.get("views") or []
    attempts = [a for v in views for a in v.get("attempts") or []]
    text = f"{m.get('kind')} {m.get('project')}: {len(views)} views, {len(attempts)} attempts"
    if m.get("kind") == "run":
        finals = Counter(v.get("final") for v in views)
        reasons = Counter(v.get("reason") for v in views if v.get("final") == "cycles")
        text += f", {finals.get('polished', 0)} polished, {finals.get('cycles', 0)} cycles"
        if reasons:
            text += " (" + ", ".join(f"{r} {n}" for r, n in sorted(reasons.items(), key=lambda x: str(x[0]))) + ")"
    else:
        ok = sum(1 for a in attempts if (a.get("gate") or {}).get("decision") == "accept" and not a.get("error"))
        text += f", {ok} accepted by the gate"
    if m.get("incomplete"):
        text += "; INCOMPLETE (deadline)"
    return text


def has_errors(m: dict) -> bool:
    """True when any attempt failed or a view could not be gated."""
    for v in m.get("views") or []:
        if v.get("error") or v.get("reason") == "error":
            return True
        if any(a.get("error") for a in v.get("attempts") or []):
            return True
    return False


def main(argv=None, deps: Optional[Deps] = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m wenart.polish",
                                     description="AI polish of the Cycles renders (Z-Image-Turbo + ControlNet, gated)")
    sub = parser.add_subparsers(dest="command", required=True)
    for name, views_default, help_text in (
            ("run", "all", "the attempt ladder on every view (the milestone result)"),
            ("sweep", "auto", "every setting of a grid on the sweep views, each gated, no early stop"),
            ("smoke", "auto", "4 settings on a few views, with timings (pod run 0)")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--project-out", required=True, help="outputs/<project> (scene/, renders/ inside)")
        p.add_argument("--views", default=views_default,
                       help=f"cameras: {'all' if name == 'run' else 'auto'} or a comma list (default {views_default})")
        p.add_argument("--out", default=None, help="output folder (default outputs/<p>/polish"
                       + ("" if name == "run" else f"/{name}") + ")")
        p.add_argument("--force", action="store_true", help="ignore the previous manifest (no reuse)")
        p.add_argument("--deadline", type=float, default=None,
                       help="epoch seconds after which no new attempt starts (default: $WENART_DEADLINE)")
        p.add_argument("--device", default="cuda", help="torch device (default cuda)")
        p.add_argument("--config", default=None, help="polish.yaml to use (default: wenart/polish/polish.yaml)")
        p.add_argument("--previews", choices=("final", "all", "none"), default=None,
                       help="preview JPEGs: final attempts (run default), all attempts at 960 px "
                            "(sweep/smoke default) or none")
        if name != "run":
            p.add_argument("--grid", default=name, help=f"grid name of polish.yaml or a YAML/JSON file (default {name})")
    rp = sub.add_parser("report", help="rewrite polish_report.md from a manifest")
    rp.add_argument("manifest", help="polish_manifest.json")
    rp.add_argument("--out", default=None, help="report path (default: polish_report.md next to the manifest)")
    args = parser.parse_args(argv)

    if args.command == "report":
        from wenart.polish.report import write_report
        mpath = Path(args.manifest)
        m = json.loads(mpath.read_text(encoding="utf-8"))
        out = write_report(m, Path(args.out) if args.out else mpath.with_name("polish_report.md"))
        print(f"report -> {out}")
        return 0

    try:
        deadline = args.deadline if args.deadline is not None else env_deadline()
    except ValueError:
        print("ERROR WENART_DEADLINE is not a number", file=sys.stderr)
        return 2
    try:
        from wenart.polish.config import load_config
        cfg = load_config(args.config)
        m = run_polish(args.project_out, args.command, views=args.views, out_dir=args.out, force=args.force,
                       deadline=deadline, grid_name=getattr(args, "grid", None), cfg=cfg, device=args.device,
                       deps=deps, previews=args.previews)
    except PolishError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    print(summary(m))
    return 1 if has_errors(m) else 0


if __name__ == "__main__":
    raise SystemExit(main())
