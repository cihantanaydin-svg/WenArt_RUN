"""CLI of the one-command full run (docs/milestone6.md §2.1, docs/milestone7.md §9).

    python -m wenart.run plan --projects synthetic-01,synthetic-03 [--gpu NAME] [--out run_plan.json]
    python -m wenart.run pod  --projects "synthetic-01 synthetic-03" [--private "real-01"] [--private-selftest]
                              [--ab "synthetic-01 synthetic-03"] [--ab-controls synthetic-01]
                              [--ab-phase all|render|judge] --results $RESULTS [--profile full|smoke]
                              [--force stage[,stage]] [--vlm-url URL]
    python -m wenart.run copy --projects ... [--private ...] [--ab ...] --results $RESULTS [--since STAMP]
    python -m wenart.run ab-m5 --project <p> --project-out <out> [--commit SHA]   (A/B prepare part 2)
    python -m wenart.run prep ...      (the prep pod's job, M7 §9.2: ``wenart.run.prep.main(argv)``)

- ``plan`` (CPU, session or pod): stage 1 per project, the numbers and a pod
  split for the GPU ``--gpu`` (default ``GPU_PRIORITY[0]`` of
  ``scripts/gpu_run.py``; ``wenart/run/plan.py``).
- ``pod`` (inside ``scripts/jobs/full.sh``): the whole run
  (``wenart/run/scheduler.py``). Exit 0 when every project ended ``ok`` or
  ``needs_review``, no A/B stage failed or ended incomplete (``look_alt``
  excluded) and every GPU test group passed; else 1 (2 for bad options).
- ``copy``: the small result files into the results layout
  (``wenart/run/copy.py``); prints only file counts.
- ``ab-m5``: the M5 files of the A/B from git (``wenart/run/ab.py``), started
  by ``pod`` through its runner.
- ``prep``: every argument after ``prep`` goes to ``wenart.run.prep.main``
  (``scripts/jobs/prep.sh``).

Project lists take spaces or commas. Defaults from the job's environment:
``WENART_OUTPUTS`` (public outputs root), ``WENART_ASSETS``,
``WENART_JOB_DIR``, ``WENART_DEADLINE``, ``RENDER_SAMPLES``,
``WENART_POLISH_PY``, ``CHECK_MODELS``, ``WENART_LOGS``, ``JOB_ID``,
``WENART_OUTPUTS_ARCHIVE`` (where ``pod`` moves a public out_dir that has no
``run/`` folder; default ``<repo>/../outputs-archive``).
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import replace
from pathlib import Path
from typing import Optional

from wenart.run.projects import (PRIVATE_OUTPUTS, PRIVATE_RESULTS, PRIVATE_ROOT, REPO_ROOT, ProjectError,
                                 private_project, public_project)


def _env_path(name: str, default) -> Optional[Path]:
    value = os.environ.get(name, "").strip()
    return Path(value) if value else (Path(default) if default is not None else None)


def _private_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--private", default="", help="private aliases (real-01 ...), spaces or commas")
    p.add_argument("--private-selftest", action="store_true",
                   help="add selftest-02 (a private copy of tests/fixtures/projects/review-01)")
    p.add_argument("--private-root", default=str(PRIVATE_ROOT), help=f"uploads (default {PRIVATE_ROOT})")
    p.add_argument("--private-outputs", default=str(PRIVATE_OUTPUTS), help=f"default {PRIVATE_OUTPUTS}")
    p.add_argument("--private-results", default=str(PRIVATE_RESULTS), help=f"default {PRIVATE_RESULTS}")


def parse_args(argv) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m wenart.run",
                                     description="one-command full project run (docs/milestone6.md §2, "
                                                 "docs/milestone7.md §9)")
    sub = parser.add_subparsers(dest="command", required=True)

    pl = sub.add_parser("plan", help="stage 1 per project, minutes and a pod split (CPU)")
    pl.add_argument("--projects", required=True, help="public projects, spaces or commas")
    pl.add_argument("--out", default=None, help="plan JSON (default: print only)")
    pl.add_argument("--outputs", default=None, help="public outputs root (default $WENART_OUTPUTS or outputs/)")
    pl.add_argument("--gpu", default=None, help="the pod's GPU (GPU_SPEED, vLLM sequences; default GPU_PRIORITY[0] "
                                                "of scripts/gpu_run.py)")

    pod = sub.add_parser("pod", help="the whole run (inside scripts/jobs/full.sh)")
    pod.add_argument("--projects", default="", help="public projects, spaces or commas")
    _private_args(pod)
    pod.add_argument("--ab", default="", help="realism A/B projects (§6.3)")
    pod.add_argument("--ab-controls", default=None,
                     help="the A/B project with the control sets (the same in render and judge; judge without it: "
                          "the one A/B project with ab/control_views.json)")
    pod.add_argument("--ab-phase", default="all", choices=["all", "render", "judge"])
    pod.add_argument("--results", required=True, help="$RESULTS (the runner collects it)")
    pod.add_argument("--profile", default="full", choices=["full", "smoke"])
    pod.add_argument("--force", default="", help="stages whose fingerprint is ignored, comma separated")
    pod.add_argument("--vlm-url", default=None, help="an external VLM server (smoke profile: the fake)")
    pod.add_argument("--outputs", default=None, help="public outputs root (default $WENART_OUTPUTS or outputs/)")
    pod.add_argument("--assets", default=None, help="assets folder (default $WENART_ASSETS or /workspace/assets)")
    pod.add_argument("--job-dir", default=None, help="job folder (default $WENART_JOB_DIR or the results' parent)")
    pod.add_argument("--render-samples", type=int, default=None, help="default $RENDER_SAMPLES or 128")
    pod.add_argument("--deadline", type=float, default=None, help="epoch seconds (default $WENART_DEADLINE)")
    pod.add_argument("--no-tests", action="store_true", help="skip the GPU tests of phase 11")

    cp = sub.add_parser("copy", help="small result files into the results layout (counts only)")
    cp.add_argument("--projects", default="")
    _private_args(cp)
    cp.add_argument("--ab", default="")
    cp.add_argument("--results", required=True)
    cp.add_argument("--since", default=None, help="stamp file: only files newer than it (renewed afterwards)")
    cp.add_argument("--outputs", default=None, help="public outputs root (default $WENART_OUTPUTS or outputs/)")

    ab = sub.add_parser("ab-m5", help="A/B prepare part 2: the M5 files of a project from git")
    ab.add_argument("--project", required=True)
    ab.add_argument("--project-out", required=True)
    ab.add_argument("--commit", default=None)

    pp = sub.add_parser("prep", help="the prep pod's job (wenart.run.prep, docs/milestone7.md §9.2)",
                        add_help=False)
    pp.add_argument("args", nargs=argparse.REMAINDER, help="passed to wenart.run.prep.main")
    return parser.parse_args(argv)


def cmd_plan(args) -> int:
    from wenart.run import plan as P
    from wenart.run.scheduler import split_names
    names = split_names(args.projects)
    outputs = Path(args.outputs) if args.outputs else _env_path("WENART_OUTPUTS", None)
    try:
        plan = P.make_plan(names, outputs=outputs, out=lambda line: print(line, flush=True), gpu=args.gpu)
    except ProjectError as exc:
        print(f"plan: {exc}", file=sys.stderr)
        return 2
    print(P.plan_text(plan), end="")
    if args.out:
        print(f"plan -> {P.write_plan(plan, Path(args.out))}")
    return 0


def cmd_pod(args) -> int:
    from wenart.run import scheduler as SC
    deadline = args.deadline if args.deadline is not None else SC.env_deadline()
    samples = args.render_samples
    if samples is None:
        try:
            samples = int(os.environ.get("RENDER_SAMPLES", "128") or 128)
        except ValueError:
            samples = 128
    opts = SC.RunOptions(
        projects=SC.split_names(args.projects), private=SC.split_names(args.private),
        private_selftest=args.private_selftest, ab=SC.split_names(args.ab), ab_controls=args.ab_controls,
        ab_phase=args.ab_phase, results=Path(args.results), profile=args.profile,
        force=frozenset(SC.split_names(args.force)), vlm_url=args.vlm_url, repo_root=REPO_ROOT,
        outputs=Path(args.outputs) if args.outputs else _env_path("WENART_OUTPUTS", None),
        private_root=Path(args.private_root), private_outputs=Path(args.private_outputs),
        private_results=Path(args.private_results),
        job_dir=Path(args.job_dir) if args.job_dir else _env_path("WENART_JOB_DIR", None),
        assets=Path(args.assets) if args.assets else _env_path("WENART_ASSETS", "/workspace/assets"),
        render_samples=samples, deadline=deadline,
        check_models=tuple(SC.split_names(os.environ.get("CHECK_MODELS") or "qwen glm")),
        py=sys.executable,
        polish_py=os.environ.get("WENART_POLISH_PY") or "/opt/wenart/venv-polish/bin/python",
        logs_dir=_env_path("WENART_LOGS", "/workspace/logs"), job_id=os.environ.get("JOB_ID") or "run",
        tests=not args.no_tests)
    return SC.run_pod(opts)


def cmd_copy(args) -> int:
    from wenart.run import copy as CP
    from wenart.run.scheduler import SELFTEST_ALIAS, split_names
    results = Path(args.results)
    outputs = Path(args.outputs) if args.outputs else _env_path("WENART_OUTPUTS", REPO_ROOT / "outputs")
    refs = []
    names = split_names(args.projects) + [n for n in split_names(args.ab) if n not in split_names(args.projects)]
    aliases = split_names(args.private)
    if args.private_selftest and SELFTEST_ALIAS not in aliases:
        aliases.append(SELFTEST_ALIAS)
    try:
        for n in names:
            ref = public_project(n, results, REPO_ROOT)
            refs.append(replace(ref, out_dir=outputs / n))
    except ProjectError as exc:
        print(f"copy: {exc}", file=sys.stderr)
        return 2
    for i, a in enumerate(aliases, start=1):
        try:
            refs.append(private_project(a, Path(args.private_root), Path(args.private_outputs),
                                        Path(args.private_results), REPO_ROOT))
        except ProjectError:
            # Counts only: a wrong alias is never echoed (it may be a client name typed by mistake).
            print(f"copy: private alias #{i} is not valid (real-01, real-02, ...) or is a committed project name",
                  file=sys.stderr)
            return 2
    counts = CP.copy_results(refs, Path(args.since) if args.since else None)
    print(CP.summary_line(counts))
    return 0


def cmd_ab_m5(args) -> int:
    from wenart.run import ab as AB
    from wenart.run.stages import M5_LOOK_COMMIT
    try:
        info = AB.prepare_m5(args.project, Path(args.project_out), args.commit or M5_LOOK_COMMIT)
    except FileNotFoundError as exc:
        print(f"ab-m5: {exc}", file=sys.stderr)
        return 1
    print(f"ab-m5 {info['project']}: {info['previews']} of {info['cameras']} M5 previews from "
          f"{info['commit'][:12]}" + (f"; missing: {', '.join(info['missing'])}" if info["missing"] else ""))
    return 0 if not info["missing"] else 1


def cmd_prep(args) -> int:
    try:
        from wenart.run import prep as PREP     # the prep pod's job (scripts/jobs/prep.sh, docs/milestone7.md §9.2)
    except ImportError as exc:
        print(f"prep: wenart.run.prep cannot be imported ({exc})", file=sys.stderr)
        return 2
    return int(PREP.main(list(args.args)) or 0)


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["prep"]:
        # Everything after "prep" belongs to wenart.run.prep (its own --help and flags).
        return cmd_prep(argparse.Namespace(args=argv[1:]))
    args = parse_args(argv)
    if args.command == "plan":
        return cmd_plan(args)
    if args.command == "pod":
        return cmd_pod(args)
    if args.command == "copy":
        return cmd_copy(args)
    if args.command == "prep":
        return cmd_prep(args)
    return cmd_ab_m5(args)


if __name__ == "__main__":
    raise SystemExit(main())
