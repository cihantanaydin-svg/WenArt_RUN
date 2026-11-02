"""The score budget of a run (2 Nov 2026; user: "start with the score-budget table"): what costs the house score.

``python -m wenart.report.score_budget --results runs/<job>/results --project <p> [--out <md>]`` prints the table:
every family of critical and major findings with the house-score points its removal would give (each alone), every
judge tag with the points its views would give one score higher, and the views below 3 with the judge's note.

Exact when the run wrote it (``orchestrator/score_budget.json``, ``wenart.agent.judge.write_budget``, at the big loop's
measure): it is read as it is. Otherwise approximate from the collected results: the judge's rows
(``final/rubric_per_view.json``) and Argus's house findings in the final manifest (``audit.report.house_findings``: the
code critic's findings on the final renders and the architect's open majors are not in the results, so the defects
part is Argus's alone).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


def _read(path: Path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def find(results: Path, project: str, name: str) -> Optional[Path]:
    """The first ``name`` under the run's results for ``project`` (any area: final, agent, orchestrator copies)."""
    for p in sorted(Path(results).rglob(name)):
        if project in p.parts:
            return p
    return None


def budget_of(results: Path, project: str) -> tuple[Optional[dict], str]:
    """``(budget, note)``: the run's own budget, else the approximation (module docstring); None without data."""
    from wenart.agent import judge as JD

    own = find(results, project, JD.BUDGET_JSON)
    if own is not None and isinstance(_read(own), dict):
        return _read(own), f"exact: {own}"
    rows = _read(find(results, project, "rubric_per_view.json") or Path("/nonexistent")) or []
    manifest = _read(find(results, project, "final_manifest.json") or Path("/nonexistent")) or {}
    rep = ((manifest.get("agent") or {}).get("argus") or {}) if isinstance(manifest, dict) else {}
    if not rows and not rep:
        return None, "no judge rows and no Argus report in the results"
    from wenart.audit import report as AR

    house = AR.house_findings(rep) if rep else []
    views = len(rows) or int((((rep.get("lines") or {}).get("judge") or {}).get("checked") or {}).get("views") or 0) \
        or None
    budget = JD.score_budget(rows, [], house, 0, views)
    return budget, ("approximate: the judge's rows and Argus's house findings of the results (the code critic's "
                    "findings and the architect's open majors were not collected)"
                    + ("" if rows else "; no judge rows: the judge part is the default 50"))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.report.score_budget", description=__doc__.split("\n")[0])
    ap.add_argument("--results", required=True, help="a run's results folder (runs/<job>/results) or results/")
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", default=None, help="write the markdown here too")
    args = ap.parse_args(argv)
    from wenart.agent import judge as JD

    budget, note = budget_of(Path(args.results), args.project)
    if budget is None:
        print(f"score budget of {args.project}: {note}", file=sys.stderr)
        return 2
    md = JD.budget_md(budget, approximate="" if note.startswith("exact") else f"({note}.)")
    print(md)
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
