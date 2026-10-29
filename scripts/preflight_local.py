#!/usr/bin/env python3
"""Local preflight before a pod run (29 Oct 2026: real04 run 20261029-180458-full stopped after 29 min in the decor
stage on a schema error, and a local Blender build had caught an import crash the CPU tests missed).

What: for each project, the CPU stages a code change touches most, on the project's own inputs from an earlier run's
results (``runs/<job>/results``): the decor stage's ``apply`` (no AI: the stored answers), the building schema on its
output, then the scene build in the local Blender (``$WENART_BLENDER``, no textures, one preview sample) from that
output. A failure prints the stage and the tail of its log and the script exits 1, so the pod run is not started.

Usage: python3 scripts/preflight_local.py --project real04=runs/20261029-180458-full --project real06=runs/<job>
       [--out <dir>] [--no-build]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def run(cmd: list[str], log: Path) -> int:
    with open(log, "w", encoding="utf-8") as fh:
        rc = subprocess.run(cmd, cwd=str(REPO), stdout=fh, stderr=subprocess.STDOUT).returncode
    if rc:
        tail = log.read_text(encoding="utf-8", errors="replace").splitlines()[-25:]
        print(f"  FAILED (rc {rc}): {' '.join(cmd[:4])} ...\n    " + "\n    ".join(tail))
    return rc


def preflight(project: str, job_dir: Path, out: Path, build: bool) -> int:
    src = job_dir / "results" / "furniture" / project
    need = [src / "building_furnished.json", src / "style.json", src / "decor_ai_answers.json"]
    missing = [str(p) for p in need if not p.is_file()]
    if missing:
        print(f"{project}: missing inputs {missing}")
        return 1
    dst = out / project
    dst.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    print(f"{project}: decor apply")
    if run([py, "-m", "wenart.furniture.decor_ai", "apply", str(need[0]), "--style", str(need[1]), "--answers",
            str(need[2]), "--out", str(dst / "building_decor.json"), "--debug", str(dst / "decor_debug")],
           dst / "decor.log"):
        return 1
    if not build:
        return 0
    if not os.environ.get("WENART_BLENDER"):
        print(f"{project}: no WENART_BLENDER: the build is not checked")
        return 1
    print(f"{project}: Blender build")
    return run([py, "-m", "wenart.blender.cli", "build", "--building", str(dst / "building_decor.json"), "--style",
                str(need[1]), "--assets", "assets", "--out", str(dst / "scene"), "--preview-samples", "1",
                "--camera-policy", "search", "--brief", f"projects/{project}", "--no-textures"], dst / "build.log")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="scripts/preflight_local.py")
    ap.add_argument("--project", action="append", required=True, help="<project>=runs/<job> (repeatable)")
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-build", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out or tempfile.mkdtemp(prefix="preflight_"))
    failed = 0
    for spec in a.project:
        project, _, job = spec.partition("=")
        failed += preflight(project, REPO / job, out, not a.no_build)
    print(f"preflight: {'FAILED' if failed else 'ok'} ({out})")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
