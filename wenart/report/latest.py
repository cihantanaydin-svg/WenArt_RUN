"""Before / after against the project's latest run (user rule of 25 Oct 2026: "From now on every run is against its
latest run compare not according to milestones"; it replaces the Milestone 13 rule of 24 Oct 2026).

What: ``latest_run(after)`` is the run of the same project that came last before ``after`` (a final folder,
``.../final/<p>``), from

- every run the runner collected, ``runs/<job>/results/final/<p>`` (a fetch job's folder holds the run it fetched),
- the committed copy of each project's latest run, ``results/baseline/latest/final/<p>`` (``LATEST``), and
- the committed Milestone 13 runs, ``results/baseline/m13/final/<p>`` (kept, never replaced; older than any later
  run, so they are "before" only when nothing newer is known),

identified by the ``run_id`` of their ``final_manifest.json``: the newest run older than ``after``'s, with at least
one rendered preview (a pod that stopped before its renders is not a "before"). When a run's files were collected
into several folders (a download cut, then a fetch job), the most complete folder is taken.

``promote(after)`` copies a finished run into ``LATEST`` (the files ``sheets13`` and ``metrics13`` read, the same
set as the Milestone 13 copy) and records it in ``LATEST/runs.json``, so a new session or the Mac finds it; run it
after the run's before / after::

    python -m wenart.report latest --out runs/<job>/results/final/<p>            # which run is "before"
    python -m wenart.report latest --out runs/<job>/results/final/<p> --promote  # the run becomes the latest

Why: the user compares each run with the one before it, to see what the last changes did.
"""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wenart.report import metrics13 as M

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "runs"
BASELINE = ROOT / "results" / "baseline"
LATEST = BASELINE / "latest"
COMMITTED = (LATEST, BASELINE / "m13")
INDEX = "runs.json"
PREVIEW = "_final_preview.jpg"


@dataclass
class Candidate:
    final_dir: Path
    run_id: str
    found: int                      # input files ``metrics13.locate`` finds
    previews: int
    source: str                     # "runs" | "latest" | "m13"
    warnings: list = field(default_factory=list)

    @property
    def job(self) -> str:
        return job_of(self.run_id)


def job_of(run_id: str) -> str:
    """``20261025-115105-full-20261025T115639Z`` -> ``20261025-115105-full`` (the runner's job id)."""
    head, sep, _ = str(run_id or "").rpartition("-")
    return head if sep and head else str(run_id or "")


def run_id_of(final_dir) -> Optional[str]:
    path = Path(final_dir) / "final_manifest.json"
    try:
        rid = json.loads(path.read_text(encoding="utf-8")).get("run_id")
    except (OSError, ValueError, AttributeError):
        return None
    return str(rid) if rid else None


def own_renders(final_dir: Path, rid: str) -> bool:
    """Whether the run ``rid`` rendered the previews of ``final_dir`` itself (28 Oct 2026: two real06 starts that
    stopped before the render carried the earlier run's previews and render record, and the before / after took one
    of them as "before"): its render stage record (``run/<p>/render.json``) names this run; True when there is no
    record (a committed copy)."""
    rec = final_dir.parent.parent / "run" / final_dir.name / "render.json"
    try:
        data = json.loads(rec.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return True
    return str(data.get("run_id") or "") == rid


def _candidate(final_dir: Path, source: str) -> Optional[Candidate]:
    rid = run_id_of(final_dir)
    if not rid:
        return None
    run = M.locate(final_dir)
    previews = len(list(final_dir.glob(f"*{PREVIEW}"))) if own_renders(final_dir, rid) else 0
    return Candidate(final_dir=final_dir, run_id=rid, found=sum(1 for v in run.paths.values() if v),
                     previews=previews, source=source)


def candidates(project: str, runs_dir: Optional[Path] = None, committed=None) -> list[Candidate]:
    """Every known run of ``project`` with a run id, one folder per run (the most complete one), newest first."""
    runs_dir = RUNS if runs_dir is None else runs_dir
    committed = COMMITTED if committed is None else committed
    found: list[Candidate] = []
    if Path(runs_dir).is_dir():
        for d in sorted(Path(runs_dir).glob(f"*/results/final/{project}")):
            c = _candidate(d, "runs")
            if c:
                found.append(c)
    for base in committed:
        d = Path(base) / "final" / project
        if d.is_dir():
            c = _candidate(d, Path(base).name)
            if c:
                found.append(c)
    best: dict[str, Candidate] = {}
    for c in found:
        old = best.get(c.run_id)
        if old is None or (c.found, c.previews, c.source == "runs") > (old.found, old.previews, old.source == "runs"):
            best[c.run_id] = c
    return sorted(best.values(), key=lambda c: c.run_id, reverse=True)


def latest_run(after, runs_dir: Optional[Path] = None, committed=None) -> Optional[Candidate]:
    """The run of the same project just before ``after`` (a ``.../final/<p>`` folder): the newest known run whose
    run id is older than ``after``'s (any other run when ``after`` has none), with at least one preview."""
    after = Path(after).resolve()
    project = after.name
    rid = run_id_of(after)
    for c in candidates(project, runs_dir, committed):
        if c.final_dir.resolve() == after or (rid and c.run_id >= rid):
            continue
        if c.previews:
            return c
    return None


def _files(final_dir: Path) -> dict[str, Path]:
    """``{relative path under the results root: file}`` of one run folder: the set the Milestone 13 copy holds."""
    p = final_dir.name
    root = final_dir.parent.parent
    out: dict[str, Path] = {}

    def take(rel: str):
        f = root / rel
        if f.is_file():
            out[rel] = f

    take(f"furniture/{p}/building_final.json")
    for name in ("scene_manifest.json", "render_manifest.json"):
        take(f"renders/{p}/{name}")
    for f in sorted((root / "renders" / p / "variants").glob("*/scene_manifest.json")):
        out[str(f.relative_to(root))] = f
    # 28 Oct 2026 (user: "Where are the top down views of the last 2 runs"): the floors' top-down views go with the run
    for f in sorted((root / "renders" / p).glob("top_*_plan.jpg")):
        out[str(f.relative_to(root))] = f
    for name in ("final_manifest.json", "final_report.md", "ATTRIBUTION.md"):
        take(f"final/{p}/{name}")
    for f in sorted(final_dir.glob(f"*{PREVIEW}")):
        out[f"final/{p}/{f.name}"] = f
    take(f"agent/{p}/log.json")
    for f in sorted((root / "run" / p).glob("*.json")):
        out[f"run/{p}/{f.name}"] = f
    return out


def promote(after, runs_dir: Optional[Path] = None, latest: Optional[Path] = None, note: str = "") -> dict:
    """Copy the run of ``after`` into ``latest`` (replacing the project's earlier copy there; git keeps it) and record
    it in ``latest/runs.json``. Files the run's other local folders hold (a fetch job's) fill the gaps."""
    runs_dir = RUNS if runs_dir is None else runs_dir
    latest = LATEST if latest is None else latest
    after = Path(after).resolve()
    project, rid = after.name, run_id_of(after)
    if not rid:
        raise ValueError(f"{after} has no final_manifest.json with a run_id: not a finished run")
    files = _files(after)
    if Path(runs_dir).is_dir():
        for d in sorted(Path(runs_dir).glob(f"*/results/final/{project}")):
            if d.resolve() != after and run_id_of(d) == rid:
                for rel, f in _files(d).items():
                    files.setdefault(rel, f)
    latest = Path(latest)
    for area in ("furniture", "renders", "final", "agent", "run"):
        old = latest / area / project
        if old.is_dir():
            shutil.rmtree(old)
    for rel, f in sorted(files.items()):
        dest = latest / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
    index_path = latest / INDEX
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        index = {}
    record = {"run_id": rid, "job": job_of(rid), "source": str(after.relative_to(ROOT)) if after.is_relative_to(ROOT)
              else str(after), "files": len(files),
              "previews": sum(1 for rel in files if rel.endswith(PREVIEW))}
    if note:
        record["note"] = note
    index[project] = record
    latest.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return record


def label(final_dir) -> str:
    """``run 20261025-115105-full`` for a sheet label, ``run ?`` without a run id."""
    rid = run_id_of(final_dir)
    return f"run {job_of(rid)}" if rid else "run ?"
