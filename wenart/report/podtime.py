"""Where a pod's time goes (29 Oct 2026, user: "Give me the breakdown of the pod time for each pod how much time each
thing is taking").

``python -m wenart.report.podtime --results runs/<job>/results --project <p> [--minutes N] [--md PATH]``

The run manifest gives the job's start and end and the agent phase; every stage log line
``[wenart.run] <utc> $ <command>`` ... ``[wenart.run] <utc> rc N`` gives one command's time. Commands are put in
``KINDS`` buckets; the time between commands inside the agent phase is the agent model's own work (the architect, Argus
AI, the critic and planner rounds, the judge, the inspector, a variant's build), outside it the model servers' starts
and the glue. The pod start is read from the job id (``YYYYMMDD-HHMMSS-<name>``, the runner's creation time) and the
pod's end from ``--minutes`` (the billed minutes of docs/gpu-log.md); without them those two rows are left out.
Pure apart from reading the files; the timeline lists every command and every gap of at least ``GAP_MIN_S``.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

LINE = re.compile(r"^\[wenart\.run\] (\S+Z) (\$ (.*)|rc (-?\d+).*)$")
GAP_MIN_S = 60.0
AGENT = "AI agent model (architect, Argus AI, critic/planner rounds, judge, inspector)"
GLUE = "model server starts, waits, glue"
KINDS = (("cli build", "Blender: build the scene"),
         ("cli render", "Blender: render (final, previews, controls)"), ("cli topdown", "Blender: top-down views"),
         ("cli export", "Blender: 3D export"))
STAGE_KINDS = {"polish": "diffusion: gate, polish, detect", "gate": "diffusion: gate, polish, detect",
               "detect": "diffusion: gate, polish, detect", "check": "AI vision check, layout, decor questions",
               "decor_ask": "AI vision check, layout, decor questions",
               "layout": "AI vision check, layout, decor questions"}
CPU = "CPU: reading, fit, apply, expected, report, sheets"


def _utc(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def kind_of(stage: str, cmd: str) -> str:
    """The bucket of one stage command (pure)."""
    for key, name in KINDS:
        if key in cmd:
            return name
    return STAGE_KINDS.get(stage, CPU)


def commands(results: str, project: str, t0: datetime, t1: datetime) -> list[tuple]:
    """(start, end, stage, command) of every stage command of the run window, in time order."""
    rows = []
    for f in glob.glob(os.path.join(results, "run", project, "logs", "*.log")):
        stage, cur = os.path.basename(f)[:-4], None
        for line in open(f, errors="replace", encoding="utf-8"):
            m = LINE.match(line.rstrip("\n"))
            if not m:
                continue
            ts = _utc(m.group(1))
            if m.group(3) is not None:
                cur = (ts, m.group(3))
            elif cur is not None:
                if t0 <= cur[0] <= t1:            # the stage logs keep the older runs' lines
                    rows.append((cur[0], ts, stage, cur[1]))
                cur = None
    return sorted(rows)


def pod_created(job: str) -> Optional[datetime]:
    m = re.match(r"(\d{8}-\d{6})", job or "")
    return datetime.strptime(m.group(1), "%Y%m%d-%H%M%S").replace(tzinfo=timezone.utc) if m else None


def breakdown(results: str, project: str, minutes: Optional[float] = None) -> dict:
    """``{"rows": [(bucket, seconds)], "timeline": [...], "total_s"}`` of one run (module docstring)."""
    man = json.load(open(os.path.join(results, "run_manifest.json"), encoding="utf-8"))
    t0, t1 = _utc(man["started_utc"]), _utc(man["finished_utc"])
    phases = {p["phase"]: p for p in man.get("phases") or []}
    a0, a1 = (_utc(phases[12]["start_utc"]), _utc(phases[12]["end_utc"])) if 12 in phases else (t1, t1)
    rows = commands(results, project, t0, t1)
    agg: collections.Counter = collections.Counter()
    timeline = []
    for a, b, stage, cmd in rows:
        agg[kind_of(stage, cmd)] += (b - a).total_seconds()
    cur = t0
    for a, b, stage, cmd in rows + [(t1, t1, "", "")]:
        if a > cur:
            inside = max(timedelta(0), min(a, a1) - max(cur, a0)).total_seconds()
            agg[AGENT] += inside
            agg[GLUE] += (a - cur).total_seconds() - inside
            if (a - cur).total_seconds() >= GAP_MIN_S:
                timeline.append((cur, a, "gap", AGENT if inside else GLUE))
        if stage:
            timeline.append((a, b, stage, kind_of(stage, cmd)))
        cur = max(cur, b)
    tests = float((phases.get(11) or {}).get("seconds") or 0.0)
    if tests:
        agg[GLUE] -= tests
        agg["GPU tests, run manifest"] += tests
    created = pod_created(man.get("job") or os.path.basename(os.path.dirname(os.path.abspath(results))))
    if created is not None and created <= t0:
        agg["pod start and setup (venvs, model downloads)"] = (t0 - created).total_seconds()
    if created is not None and minutes:
        end = created + timedelta(minutes=float(minutes))
        if end > t1:
            agg["results upload and pod stop"] = (end - t1).total_seconds()
    out = sorted(((k, v) for k, v in agg.items() if v > 0.5), key=lambda kv: -kv[1])
    return {"rows": out, "timeline": timeline, "total_s": sum(v for _k, v in out)}


def markdown(bd: dict, title: str) -> str:
    tot = bd["total_s"] or 1.0
    lines = [f"## Pod time: {title}", "", "| what | min | share |", "|---|---:|---:|"]
    lines += [f"| {k} | {v / 60:.1f} | {100 * v / tot:.0f} % |" for k, v in bd["rows"]]
    lines += [f"| total | {tot / 60:.1f} | |", "", "| from | to | min | stage | what |", "|---|---|---:|---|---|"]
    lines += [f"| {a:%H:%M:%S} | {b:%H:%M:%S} | {(b - a).total_seconds() / 60:.1f} | {st} | {k} |"
              for a, b, st, k in bd["timeline"]]
    return "\n".join(lines) + "\n"


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.report.podtime")
    ap.add_argument("--results", required=True)
    ap.add_argument("--project", required=True)
    ap.add_argument("--minutes", type=float, default=None, help="the pod's billed minutes (docs/gpu-log.md)")
    ap.add_argument("--md", default=None)
    a = ap.parse_args(argv)
    if not os.path.isfile(os.path.join(a.results, "run_manifest.json")):
        print(f"no run_manifest.json in {a.results}")
        return 2
    text = markdown(breakdown(a.results, a.project, a.minutes), f"{a.project}, {a.results}")
    if a.md:
        with open(a.md, "w", encoding="utf-8") as fh:
            fh.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
