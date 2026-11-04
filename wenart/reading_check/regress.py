"""The reading regression set (2 Nov 2026; user: "go ahead with all 4", "can we keep improving this regression set?").

What: ``python -m wenart.reading_check regress [--projects real02,real10] [--update] [--work DIR]`` reads every project
of the set (``results/reading_baseline/<project>.json``; ``--projects`` names others to add) with the CPU pipeline
(no AI answers, so a reading change is judged by itself), runs the reading check and compares the project's key numbers
with its baseline:

- exact: the levels, the levels left out, the reading's status, the check's verdict;
- within ``COUNT_TOL`` (a share, at least ``COUNT_MIN`` items): rooms, walls, doors, windows, openings per level;
- within ``AREA_TOL``: the room area per level;
- the check's critical findings never more, its stacking offsets never larger by ``STACK_TOL_M``.

A difference is printed per project and number; the command exits 1 when any project regressed. ``--update`` writes
the new numbers as the baseline (after a change the user accepted: the set keeps improving, one project at a time).

Why: real10's reading fixes of 2 Nov 2026 broke 18 tests of real02, real06 and the wall rules before anyone saw it; a
rule for one project must never quietly change another.
"""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parents[2]
BASELINE_DIR = REPO / "results" / "reading_baseline"
PROJECTS_DIR = REPO / "projects"
COUNT_TOL = 0.10
COUNT_MIN = 2
AREA_TOL = 0.03
STACK_TOL_M = 0.05
PER_LEVEL = ("rooms", "walls", "doors", "windows", "openings")


def numbers(out_dir: Path) -> dict:
    """The key numbers of a pipeline output (the module docstring)."""
    from wenart import reading_check as RC

    out_dir = Path(out_dir)
    b = json.loads((out_dir / "building.json").read_text(encoding="utf-8"))
    res = RC.check(out_dir)
    per: dict = {}
    for lv in b.get("levels") or []:
        lid = lv["id"]
        rooms = [r for r in b.get("rooms") or [] if r.get("level_id") == lid]
        ops = [o for o in b.get("openings") or [] if o.get("level_id") == lid]
        per[lid] = {"rooms": len(rooms), "walls": sum(1 for w in b.get("walls") or [] if w.get("level_id") == lid),
                    "doors": sum(1 for o in ops if o.get("type") == "door"),
                    "windows": sum(1 for o in ops if o.get("type") == "window"),
                    "openings": sum(1 for o in ops if o.get("type") not in ("door", "window")),
                    "room_area": round(sum(float(r.get("area_computed") or 0) for r in rooms), 1)}
    stack = {f["level_id"]: f.get("offset_m") for f in res["findings"] if f["check"] == "RC2"}
    return {"project": (b.get("project") or {}).get("id"), "status": b.get("status"),
            "levels": [lv["id"] for lv in b.get("levels") or []],
            "levels_left_out": sorted(str(lo.get("label")) for lo in b.get("levels_left_out") or []),
            "per_level": per, "check": {"verdict": res["verdict"], "counts": res["counts"], "stacking": stack}}


def compare(base: dict, new: dict) -> list[str]:
    """The regressions of ``new`` against ``base`` (pure; an improvement is no regression)."""
    out = []
    for key in ("status", "levels", "levels_left_out"):
        if base.get(key) != new.get(key):
            better = key == "levels_left_out" and set(new.get(key) or []) < set(base.get(key) or [])
            better = better or (key == "levels" and set(base.get(key) or []) < set(new.get(key) or []))
            better = better or (key == "status" and new.get(key) == "ok")
            if not better:
                out.append(f"{key}: {base.get(key)} -> {new.get(key)}")
    bc, nc = base.get("check") or {}, new.get("check") or {}
    if bc.get("verdict") == "ready" and nc.get("verdict") != "ready":
        out.append(f"check verdict: ready -> {nc.get('verdict')}")
    if (nc.get("counts") or {}).get("critical", 0) > (bc.get("counts") or {}).get("critical", 0):
        out.append(f"critical findings: {(bc.get('counts') or {}).get('critical', 0)} -> "
                   f"{(nc.get('counts') or {}).get('critical', 0)}")
    for lid, off in (nc.get("stacking") or {}).items():
        if lid not in (base.get("levels") or []):
            continue                                   # 4 Nov 2026: a level the baseline never read cannot regress
        was = (bc.get("stacking") or {}).get(lid) or 0.0
        if off is not None and off > was + STACK_TOL_M:
            out.append(f"{lid} stacking offset: {was:.2f} -> {off:.2f} m")
    for lid, b in (base.get("per_level") or {}).items():
        n = (new.get("per_level") or {}).get(lid)
        if n is None:
            continue                                   # a level gone is reported by "levels"
        for key in PER_LEVEL:
            tol = max(COUNT_MIN, COUNT_TOL * b.get(key, 0))
            if abs(n.get(key, 0) - b.get(key, 0)) > tol:
                out.append(f"{lid} {key}: {b.get(key)} -> {n.get(key)}")
        ba, na = float(b.get("room_area") or 0), float(n.get("room_area") or 0)
        if ba and abs(na - ba) > AREA_TOL * ba:
            out.append(f"{lid} room area: {ba:.1f} -> {na:.1f} m2")
    return out


def read_project(project: str, work: Path) -> Path:
    """The CPU reading of ``projects/<project>`` into ``work/<project>`` (no AI answers)."""
    from wenart.ingest import pipeline as PL

    out = Path(work) / project
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    PL.run_project(PROJECTS_DIR / project, out, no_ai=True)
    return out


def main(args) -> int:
    projects = [p.strip() for p in (args.projects or "").split(",") if p.strip()] or \
        sorted(p.stem for p in BASELINE_DIR.glob("*.json"))
    if not projects:
        print("reading regress: no baseline in results/reading_baseline/ and no --projects")
        return 2
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="reading_regress_"))
    failed = 0
    for p in projects:
        new = numbers(read_project(p, work))
        path = BASELINE_DIR / f"{p}.json"
        if args.update or not path.is_file():
            BASELINE_DIR.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(new, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"{p}: baseline {'updated' if args.update else 'written'} ({new['check']['verdict']}, "
                  f"{len(new['levels'])} levels)")
            continue
        diffs = compare(json.loads(path.read_text(encoding="utf-8")), new)
        if diffs:
            failed += 1
            print(f"{p}: REGRESSED\n  " + "\n  ".join(diffs))
        else:
            print(f"{p}: ok ({new['check']['verdict']}, {len(new['levels'])} levels)")
    return 1 if failed else 0
