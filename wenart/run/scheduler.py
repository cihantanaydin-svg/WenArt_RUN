"""The full-run scheduler (docs/milestone6.md §2.3, docs/milestone7.md §9.1): all stages of all projects,
batched by GPU holder.

What: ``Orchestrator(options).run()`` runs the 11 phases over the projects of
one pod, each phase over all active projects in the given order, and stops a
project at its first terminal state (``needs_review``, ``failed``,
``incomplete``):

 1. CPU: intake, pipeline (exit 4 -> ``pending``: recognition questions
    written; the stored answers of both models are copied from
    ``results/recognition/<p>/`` when they complete the set), fit (not for a
    pending project: it fits after ``pipeline_final``); style (with the photo
    terms when the stored photo answers are complete); A/B prepare part 1
    for the control project whose control renders are missing.
 2. VLM GLM session, only when some project has style photos without a GLM
    answer or recognition questions without a GLM answer: recognize (glm),
    photos (glm).
 3. VLM Qwen session, only when some project needs Qwen recognition answers,
    a layout or Qwen photo answers: recognize (qwen); pipeline_final (the
    pipeline with ``--answers``, ``--no-ai`` when an answer is still
    missing) and fit for the pending projects; photos (qwen), photo combine +
    style again for projects that got new answers, layout.
 4. CPU: assets, decor, refit (``--style``); A/B prepare part 2 (M5 files
    from git) for the control project whose control renders are missing.
 5. Blender: build, render (``--alt-look None`` for the A/B projects),
    controls; the control project's A/B build, render, camera check, control
    views and control renders when they are missing (else the M6 ones on the
    volume are reused).
 6. Diffusion: gate calibrate (a complete calibration of the same renders,
    controls and gate code is reused) -> gate validate -> polish (when the
    decision allows it) -> detect (OWLv2 on the Cycles and polished images).
 7. CPU: expected, plan crops; A/B pairs (``realism2-pairs``; ``--ab-phase
    judge``: the render pod's complete ``ab/pairs_v2.json`` is reused).
 8. VLM Qwen session: check run (``--kinds cycles,polished,controls``),
    preference, style-photo test; realism v2 (every pair set).
 9. VLM GLM session: the same.
10. CPU (always): combine (reads ``detect/``) + calibrate,
    realism2-combine, realism2-summary, report for every project (also
    needs_review and incomplete ones).
11. One copy of the small result files (``wenart.run copy``), the GPU tests
    (full profile), then ``run_manifest.json``.

Rules: a heavy stage (build, render, controls, gate, polish, detect, a
server start, any VLM stage) starts only when ``now + estimate / GPU speed <
WENART_DEADLINE`` (``wenart.run.plan.GPU_SPEED`` of the pod's GPU, 1.0 when
not measured), else the project becomes ``incomplete``; subprocess timeouts
are ``max(60, deadline - now)`` in phases 1-9 and ``max(300, deadline + 600 -
now)`` in phases 10-11 (TERM, then KILL, status ``incomplete``); a server
session starts only when some project needs it; ``--force`` ignores the
fingerprints (and passes ``--force`` to render, polish and detect); a public
out_dir without ``run/`` (an earlier job that is not ``wenart.run``) is
moved to ``$WENART_OUTPUTS_ARCHIVE`` (default ``<repo>/../outputs-archive``)
before its project starts; ``--ab-phase judge`` without ``--ab-controls``
takes the one A/B project with ``ab/control_views.json``; a project's state
counts its project stages only (the A/B stages count in the exit code on
their own); a pending project without a ``pipeline_final`` of this run ends
``incomplete``.

The A/B (realism v2, M7 §8.2): ``--ab`` names the look_alt projects
(``renders/<cam>_preview.jpg`` = AgX - Punchy vs ``<cam>_alt_preview.jpg``
= look None, rendered in this run when the project is in ``--projects``,
else taken from the volume); ``--ab-controls`` the control project (in
``--ab`` or not) whose M6 control renders (``ab/renders``, ``ab/ctl_*``,
``ab/nuisance_ev``) give the control sets.

Why: one GPU holder at a time (each vLLM server takes 90 % of the VRAM;
Blender and the polish need the GPU), as few server starts as possible (at
most 4: 3 without style photos or questions, 2 without empty rooms, photos
or questions, 2 for ``--ab-phase judge``), and a pod that the deadline cuts
resumes from the volume with the same command.

How: every subprocess goes through ONE injectable function
``runner(cmd, env, cwd, timeout, log_path) -> rc`` (cwd = repo root, output
into ``<out>/run/logs/<stage>.log``); the clock, the server sessions, the
GPU size and name and the A/B control-view choice are injectable too, so the
CPU tests drive the whole schedule with fakes. Nothing about a private
project reaches stdout except ``<alias> <stage> <status> <seconds>s``.
"""
from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import signal
import subprocess
import sys
import time
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable, Optional

from wenart import intake as INTAKE
from wenart.run import servers as SV
from wenart.run import stages as S
from wenart.run import state as ST
from wenart.run.projects import (PRIVATE_OUTPUTS, PRIVATE_RESULTS, PRIVATE_ROOT, REPO_ROOT, ProjectError,
                                 ProjectRef, check_alias, check_name, private_project, project_folder,
                                 public_project, upload_dir)

TIMEOUT_RC = 124                    # the runner's return code for a subprocess it stopped at its timeout
NO_DEADLINE_TIMEOUT_S = 4 * 3600.0  # bound for a subprocess when no deadline is set (session runs)
LOG_MARK = "[wenart.run]"
SELFTEST_ALIAS = "selftest-02"
# The private self-test's source: a needs_review test project (two untitled plan pages, M7 §9.1); synthetic-02 is
# a normal raster project since M7.
SELFTEST_SOURCE = "review-01"
AB_PHASES = ("all", "render", "judge")
PROFILES = ("full", "smoke")
PHASE_NAMES = {
    1: "cpu: intake, pipeline, fit, style",
    2: "vlm glm: recognition, style photos",
    3: "vlm qwen: recognition, pipeline_final, fit, style photos, layout, decor questions",
    4: "cpu: assets, decor, refit, A/B prepare",
    5: "blender: build, render, 3D export, controls, A/B control renders",
    6: "diffusion: gate, polish, detect",
    7: "cpu: expected, plan crops, A/B pairs",
    8: "vlm qwen: check, realism",
    9: "vlm glm: check, realism",
    10: "cpu: combine, realism summary, report",
    11: "gpu tests, run manifest",
}
# The control renders of the control project (M6 §6.2): ab/renders plus one render folder per control set.
CONTROL_RENDER_MANIFESTS = ("ab/renders/render_manifest.json",) + tuple(
    f"ab/{name}/renders/render_manifest.json" for name in S.CONTROL_RENDERS)
# Notes that may be recorded for a private project (its records reach the session, §2.1): the intake's
# fixed needs_review reasons, which never name a file of the upload (wenart/intake.py).
PRIVATE_NOTES = (INTAKE.NOT_UPLOADED, INTAKE.COLLISION, INTAKE.ROOT_SYMLINK, INTAKE.NO_DOCUMENT,
                 INTAKE.OVER_FILE_CAP, INTAKE.OVER_PROJECT_CAP, INTAKE.UNREADABLE, INTAKE.BAD_NAME)
GPU_TEST_GROUPS = (
    # (group, interpreter attribute, [(test file, list variables that must not all be empty)])
    ("full", "py", [("tests/gpu/test_full_run.py", ("RUN_TEST_PROJECTS", "NEEDS_REVIEW_TEST_PROJECTS",
                                                    "SELFTEST_TEST_ALIAS")),
                    ("tests/gpu/test_render.py", ("RENDER_TEST_PROJECTS",)),
                    ("tests/gpu/test_look_m6.py", ("RENDER_TEST_PROJECTS",)),
                    ("tests/gpu/test_furnish.py", ("FURNISH_TEST_PROJECTS",)),
                    ("tests/gpu/test_check.py", ("CHECK_TEST_PROJECTS",)),
                    ("tests/gpu/test_realism.py", ("AB_TEST_PROJECTS",)),
                    ("tests/gpu/test_m9.py", ("RENDER_TEST_PROJECTS",))]),          # Milestone 9: AI decor, 3D files
    ("polish", "polish_py", [("tests/gpu/test_polish.py", ("POLISH_TEST_PROJECTS", "GATE_TEST_PROJECTS")),
                             ("tests/gpu/test_polish_backend.py", ("POLISH_TEST_PROJECTS", "GATE_TEST_PROJECTS")),
                             ("tests/gpu/test_detect.py", ("DETECT_TEST_PROJECTS",))]),
)
# The prep pod's detector calibration as the integrator commits it (M7 §9.2); tests/gpu/test_detect.py reads it.
DETECT_CALIBRATION = Path("results") / "detect" / "detector_calibration.json"
TEST_LISTS = ("RUN_TEST_PROJECTS", "NEEDS_REVIEW_TEST_PROJECTS", "RENDER_TEST_PROJECTS", "FURNISH_TEST_PROJECTS",
              "CHECK_TEST_PROJECTS", "POLISH_TEST_PROJECTS", "GATE_TEST_PROJECTS", "DETECT_TEST_PROJECTS",
              "AB_TEST_PROJECTS", "AB_CONTROL_PROJECT", "SELFTEST_TEST_ALIAS")


class RunError(RuntimeError):
    """A run that cannot start (bad options)."""


# --------------------------------------------------------------------------
# The one subprocess runner
# --------------------------------------------------------------------------

def _stop_group(proc: subprocess.Popen, wait_s: float = 30.0) -> None:
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                proc.send_signal(sig)
            except (ProcessLookupError, OSError):
                pass
        try:
            proc.wait(timeout=wait_s)
            return
        except subprocess.TimeoutExpired:
            continue


def subprocess_runner(cmd: list, env: dict, cwd, timeout: Optional[float], log_path) -> int:
    """Run ``cmd`` (cwd ``cwd``, env ``env``) with stdout+stderr appended to ``log_path``; its exit code,
    ``TIMEOUT_RC`` when it was stopped at ``timeout`` seconds (TERM to its process group, then KILL)."""
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "ab") as log:
        log.write(f"{LOG_MARK} {ST.utc_now()} $ {shlex.join(str(c) for c in cmd)}\n".encode("utf-8"))
        log.flush()
        try:
            proc = subprocess.Popen([str(c) for c in cmd], stdout=log, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, cwd=str(cwd), env=env, start_new_session=True)
        except OSError as exc:
            log.write(f"{LOG_MARK} cannot start: {exc}\n".encode("utf-8"))
            return 127
        try:
            rc = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            _stop_group(proc)
            rc = TIMEOUT_RC
            log.write(f"{LOG_MARK} timeout after {timeout:.0f} s: stopped (TERM, then KILL)\n".encode("utf-8"))
        log.write(f"{LOG_MARK} {ST.utc_now()} rc {rc}\n".encode("utf-8"))
    return rc


def split_names(text) -> list[str]:
    """``"a b"``, ``"a,b"`` or a list -> ``["a", "b"]`` (order kept, duplicates dropped)."""
    if text is None:
        return []
    items = text if isinstance(text, (list, tuple)) else str(text).replace(",", " ").split()
    out: list[str] = []
    for item in items:
        for part in str(item).replace(",", " ").split():
            if part and part not in out:
                out.append(part)
    return out


def read_json(path) -> Optional[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, (dict, list)) else None


def last_line(path) -> Optional[str]:
    try:
        lines = [ln.strip() for ln in Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
                 if ln.strip() and not ln.startswith(LOG_MARK)]
    except OSError:
        return None
    return lines[-1][:300] if lines else None


def download_failures(path) -> int:
    """Furniture pieces of a fitted building JSON whose model download failed (``asset.fallback_reason``
    ``download of <id> failed (...); parametric fallback``, ``wenart.furniture.fit.download_fitted``)."""
    data = read_json(path)
    if not isinstance(data, dict):
        return 0
    n = 0
    for piece in data.get("furniture") or []:
        asset = piece.get("asset") if isinstance(piece, dict) else None
        reason = asset.get("fallback_reason") if isinstance(asset, dict) else None
        if isinstance(reason, str) and reason.startswith(S.DOWNLOAD_FALLBACK_PREFIX):
            n += 1
    return n


def render_digest(path) -> Optional[str]:
    """sha256 of a render manifest's identity: sorted ``(camera, scene_sha256, render_key)`` of its entries and its
    ``not_rendered`` list (None when missing). The manifest's ``deadline``, ``skipped`` and ``warnings`` change on
    every run that reuses the renders."""
    data = read_json(path)
    if not isinstance(data, dict):
        return None
    entries = sorted([str(e.get(k) or "") for k in ("camera", "scene_sha256", "render_key")]
                     for e in data.get("renders") or [] if isinstance(e, dict))
    payload = [entries, sorted(str(c) for c in data.get("not_rendered") or [])]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode("utf-8")).hexdigest()


def env_deadline() -> Optional[float]:
    text = os.environ.get("WENART_DEADLINE", "").strip()
    try:
        return float(text) if text else None
    except ValueError:
        return None


def tree_digest(folder) -> Optional[dict]:
    """``{relative path: sha256}`` of every file below ``folder`` (a symlink counts as ``"symlink"``, an empty folder
    as ``"dir"``); None when ``folder`` is not a folder. Two trees with the same digest hold the same files."""
    root = Path(folder)
    if root.is_symlink() or not root.is_dir():
        return None
    out: dict = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            out[rel] = "symlink"
        elif path.is_file():
            out[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir() and not any(path.iterdir()):
            out[rel] = "dir"
    return out


# --------------------------------------------------------------------------
# Options and per-project state
# --------------------------------------------------------------------------

@dataclass
class RunOptions:
    projects: list = field(default_factory=list)          # public projects (full run)
    private: list = field(default_factory=list)           # private aliases (full run)
    private_selftest: bool = False                        # + selftest-02 (a private copy of review-01)
    ab: list = field(default_factory=list)                # realism A/B (look_alt) projects (M7 §8.2)
    ab_controls: Optional[str] = None                     # the control project (its M6 ab/ control renders)
    ab_phase: str = "all"                                 # all | render | judge
    results: Optional[Path] = None                        # $RESULTS
    profile: str = "full"                                 # full | smoke
    force: frozenset = frozenset()
    vlm_url: Optional[str] = None
    repo_root: Path = REPO_ROOT
    outputs: Optional[Path] = None                        # public outputs root (default <repo>/outputs)
    private_root: Path = PRIVATE_ROOT
    private_outputs: Path = PRIVATE_OUTPUTS
    private_results: Path = PRIVATE_RESULTS
    job_dir: Optional[Path] = None                        # $WENART_JOB_DIR (default: the results' parent)
    assets: Path = Path("/workspace/assets")
    render_samples: int = 128
    deadline: Optional[float] = None
    check_models: tuple = ("qwen", "glm")
    py: str = sys.executable
    polish_py: str = "/opt/wenart/venv-polish/bin/python"
    logs_dir: Path = Path("/workspace/logs")
    job_id: str = "run"
    tests: bool = True                                    # phase 11 GPU tests (never in the smoke profile)

    @property
    def smoke(self) -> bool:
        return self.profile == "smoke"


@dataclass
class ProjectRun:
    ref: ProjectRef
    full: bool = True                   # in --projects / --private (the whole run)
    ab: bool = False                    # an A/B project of this run: in --ab, or the control project
    look_alt: bool = False              # in --ab: its main renders give look_alt pairs (M7 §8.2)
    controls_needed: bool = False       # the control project whose control renders are missing: render them
    pending: bool = False               # the pipeline wrote recognition questions (exit 4, M7 §1.4)
    finalized: bool = False             # pipeline_final ran (or was reused) in this run
    records: dict = field(default_factory=dict)       # stage -> StageRecord of this run
    previous: dict = field(default_factory=dict)      # stage -> StageRecord found on the volume
    parts: dict = field(default_factory=dict)         # stage -> list of steps of this run (multi-part stages)
    terminal: Optional[str] = None
    ab_dropped: Optional[str] = None
    photos: list = field(default_factory=list)
    photos_asked: set = field(default_factory=set)    # model keys asked in this run (--force photos)
    new_photo_answers: bool = False
    terms_applied: bool = False
    layout_rooms: int = 0
    decor_rooms: Optional[int] = None    # Milestone 9: rooms the AI decor asks about (None: not counted yet)
    gate_decision: Optional[str] = None
    views: int = 0
    polish_ran: bool = False
    archived: Optional[str] = None      # where the out_dir of an earlier, non-wenart.run job was moved (§2.3)
    archive_note: Optional[str] = None  # that move, for the note of the project's first stage record of this run

    @property
    def name(self) -> str:
        return self.ref.name

    @property
    def out(self) -> Path:
        return self.ref.out_dir

    @property
    def active(self) -> bool:
        return self.full and self.terminal is None

    @property
    def ab_active(self) -> bool:
        return self.ab and self.ab_dropped is None


# --------------------------------------------------------------------------
# The orchestrator
# --------------------------------------------------------------------------

class Orchestrator:
    def __init__(self, opts: RunOptions, *, runner: Callable = subprocess_runner,
                 clock: Callable[[], float] = time.time, server_factory: Optional[Callable] = None,
                 out: Optional[Callable[[str], None]] = None, control_views: Optional[Callable] = None,
                 gpu_mem: Optional[Callable[[], int]] = None, check_models: Optional[dict] = None,
                 gpu_name: Optional[Callable[[], Optional[str]]] = None):
        self.opts = opts
        self.runner = runner
        self.clock = clock
        self.server_factory = server_factory
        self.out = out or (lambda line: print(line, flush=True))
        self._control_views = control_views
        self._gpu_mem = gpu_mem
        self._gpu_name = gpu_name
        self.repo_root = Path(opts.repo_root)
        self.outputs_root = Path(opts.outputs) if opts.outputs else self.repo_root / "outputs"
        self.results = Path(opts.results) if opts.results else None
        self.job_dir = Path(opts.job_dir) if opts.job_dir else (self.results.parent if self.results else None)
        self.deadline = opts.deadline
        self.models = check_models if check_models is not None else SV.check_models()
        self.tools = S.Tools(py=opts.py, polish_py=opts.polish_py, assets=Path(opts.assets),
                             render_samples=int(opts.render_samples), smoke=opts.smoke,
                             check_models=self.models, private_root=Path(opts.private_root))
        self.commit = ST.git_commit(self.repo_root)
        self.started_utc = ST.utc_now()
        self.run_id = f"{opts.job_id}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
        self.runs: list[ProjectRun] = []          # full-run projects, public then private
        self.ab_runs: list[ProjectRun] = []       # A/B projects (some also in self.runs)
        self.phases: list[dict] = []
        self.servers: list[dict] = []
        self.tests: list[dict] = []
        self.job_records: dict = {}               # job-level stages (realism_summary)
        # The A/B project with the control sets: --ab-controls, or in --ab-phase judge the one A/B project
        # whose ab/control_views.json an earlier render pod wrote (setup).
        self.ab_controls: Optional[str] = opts.ab_controls
        self._code_cache: dict = {}
        self._seqs: dict = {}                     # model key -> sequences of its server
        self._gpu: Optional[dict] = None          # {"name", "memory_mib"} of the pod's GPU (queried once)
        self._speed: Optional[dict] = None        # {"name", "speed", "matched"} (wenart.run.plan.gpu_speed)
        self._libredwg: Optional[tuple] = None    # (LibreDWG VERSION string,) once looked up
        self.phase = 0
        self.exit_code: Optional[int] = None

    # ----- small helpers -------------------------------------------------

    @property
    def any_private(self) -> bool:
        return any(pr.ref.private for pr in self.runs)

    def now(self) -> float:
        return float(self.clock())

    def can_start(self, estimate_s: float) -> bool:
        """A heavy stage starts only when ``now + estimate / GPU speed < deadline`` (§2.3; the estimates were
        measured on the RTX PRO 4500, M7 §9.3)."""
        if self.deadline is None:
            return True
        return self.now() + float(estimate_s) / self.gpu_speed() < float(self.deadline)

    def gpu_speed(self) -> float:
        """``wenart.run.plan.GPU_SPEED`` of this pod's GPU (1.0 for an unknown or unmeasured GPU and with
        ``--vlm-url``, the smoke profile on the CPU)."""
        if self._speed is None:
            from wenart.run.plan import gpu_speed   # lazy: plan imports this module
            name = None if self.opts.vlm_url else self.gpu_info().get("name")
            self._speed = gpu_speed(name)
        return float(self._speed["speed"])

    def timeout(self, late: bool = False) -> float:
        if self.deadline is None:
            return NO_DEADLINE_TIMEOUT_S
        left = float(self.deadline) - self.now()
        return max(300.0, left + 600.0) if late else max(60.0, left)

    def code(self, stage: str) -> str:
        if stage not in self._code_cache:
            self._code_cache[stage] = ST.code_hash(S.STAGES[stage].code, self.repo_root)
        return self._code_cache[stage]

    def forced(self, stage: str) -> bool:
        return stage in self.opts.force

    def child_env(self, extra: Optional[dict] = None) -> dict:
        env = dict(os.environ)
        if self.deadline is not None:
            env["WENART_DEADLINE"] = str(int(self.deadline)) if float(self.deadline).is_integer() \
                else str(self.deadline)
        env.setdefault("CHECK_MODELS", " ".join(self.opts.check_models))
        if extra:
            env.update(extra)
        return env

    def exec(self, log: Path, cmd: list, env: Optional[dict] = None, late: bool = False) -> tuple[int, float]:
        t0 = self.now()
        rc = self.runner([str(c) for c in cmd], self.child_env(env), self.repo_root, self.timeout(late), log)
        return int(rc), max(0.0, self.now() - t0)

    def say(self, pr: ProjectRun, stage: str, status: str, seconds: float, note: Optional[str]) -> None:
        line = f"{pr.name} {stage} {status} {seconds:.1f}s"
        if note and not pr.ref.private:
            line += f": {note}"
        self.out(line)

    def previous(self, pr: ProjectRun, stage: str) -> Optional[ST.StageRecord]:
        if stage not in pr.previous:
            pr.previous[stage] = ST.read_record(pr.out, stage)
        return pr.previous[stage]

    def run_step(self, pr: ProjectRun, stage: str, step: str, cmd: list, env: Optional[dict] = None,
                 late: bool = False) -> int:
        """One command of ``stage``; the step is kept for the stage record."""
        rc, seconds = self.exec(ST.log_path(pr.out, stage), cmd, env, late)
        pr.parts.setdefault(stage, []).append({"name": step, "rc": rc, "seconds": round(seconds, 2)})
        return rc

    def private_note(self, pr: ProjectRun, note: Optional[str]) -> Optional[str]:
        """A private project's record keeps no text taken from a log (its records reach the session, §2.1):
        ``exit N: <last log line>`` becomes ``exit N (details in the stage log on the volume)``. The other
        notes are the orchestrator's own words."""
        if note is None or not pr.ref.private:
            return note
        if note.startswith("exit ") and ": " in note:
            return note.split(": ", 1)[0] + " (details in the stage log on the volume)"
        return note

    def finish(self, pr: ProjectRun, stage: str, status: str, note: Optional[str] = None, *,
               fingerprint: Optional[str] = None, inputs: Optional[dict] = None,
               outputs: Optional[list] = None, merge: bool = False, written: Optional[dict] = None) -> ST.StageRecord:
        """Write the record of ``stage`` (all steps of this run so far); ``merge`` keeps the worse of the
        status already recorded in this run and ``status`` (stages that span two model sessions)."""
        steps = list(pr.parts.get(stage, []))
        prev = pr.records.get(stage)
        if merge and prev is not None:
            status = ST.worst([prev.status, status]) or status
            if prev.note and note and prev.note != note:
                note = f"{prev.note}; {note}"
            else:
                note = note or prev.note
        if pr.archive_note and status != "skipped":
            # The earlier outputs moved aside at the start (§2.3): said once, in the first record that is not a
            # skip (a skip's note is its reason).
            note = f"{note}; {pr.archive_note}" if note else pr.archive_note
            pr.archive_note = None
        rc = next((s["rc"] for s in steps if s["rc"] != 0), steps[-1]["rc"] if steps else None)
        first = prev.started_utc if prev is not None else ST.utc_now()
        rec = ST.StageRecord(project=pr.name, stage=stage, status=status, rc=rc,
                             seconds=sum(s["seconds"] for s in steps), fingerprint=fingerprint,
                             inputs=dict(inputs or {}),
                             outputs=list(outputs if outputs is not None else S.outputs_of(stage, pr.name)),
                             started_utc=first, git_commit=self.commit, log=f"logs/{stage}.log",
                             note=self.private_note(pr, note), run_id=self.run_id, steps=steps,
                             written=dict(written or {}))
        pr.records[stage] = rec
        ST.write_record(pr.out, rec)
        self.say(pr, stage, status, rec.seconds, rec.note)
        if stage in S.PROJECT_STAGES and status in ST.TERMINAL and pr.full and pr.terminal is None:
            pr.terminal = status
        return rec

    def skip(self, pr: ProjectRun, stage: str, reason: str) -> ST.StageRecord:
        if reason not in ST.SKIP_REASONS:
            raise ValueError(f"unknown skip reason {reason!r}")
        pr.parts.pop(stage, None)
        return self.finish(pr, stage, "skipped", reason, outputs=[])

    def not_started(self, pr: ProjectRun, stage: str, what: str = "") -> ST.StageRecord:
        """The deadline did not leave time to start ``stage``: incomplete (§2.3)."""
        return self.finish(pr, stage, "incomplete", f"deadline: {what or stage} not started", merge=True)

    def status_of(self, pr: ProjectRun, stage: str) -> Optional[str]:
        rec = pr.records.get(stage)
        return rec.status if rec is not None else None

    def fp_stage(self, pr: ProjectRun, stage: str, cmd: list, inputs: list, args: Optional[list] = None,
                 late: bool = False) -> ST.StageRecord:
        """A stage with ``reuse: fingerprint`` (§1.2): reused when nothing changed, else run. fit and refit: a
        model download that failed (parametric fallback, exit 0) is a ``warning`` and never reused, so the next
        run tries the download again."""
        ins = ST.file_hashes(inputs)
        fp = ST.fingerprint(stage, S.STAGE_VERSION[stage], list(args if args is not None else cmd[1:]), ins,
                            self.code(stage))
        prev = self.previous(pr, stage)
        fitted = pr.out / S.outputs_of(stage, pr.name)[0] if stage in S.DOWNLOAD_STAGES else None
        if not self.forced(stage) and ST.reusable(prev, fp, pr.out) \
                and not (fitted is not None and download_failures(fitted)):
            return self.finish(pr, stage, "reused", fingerprint=fp, inputs=ins, outputs=prev.outputs)
        rc = self.run_step(pr, stage, stage, cmd, late=late)
        if rc == 0:
            failed = download_failures(fitted) if fitted is not None else 0
            if failed:
                return self.finish(pr, stage, "warning", f"{failed} model download(s) failed: parametric fallback",
                                   fingerprint=fp, inputs=ins)
            return self.finish(pr, stage, "ok", fingerprint=fp, inputs=ins)
        if rc == TIMEOUT_RC:
            return self.finish(pr, stage, "incomplete", "timeout", fingerprint=fp, inputs=ins)
        return self.finish(pr, stage, S.STAGES[stage].on_failure, f"exit {rc}", fingerprint=fp, inputs=ins)

    def simple_stage(self, pr: ProjectRun, stage: str, steps: list, late: bool = False) -> ST.StageRecord:
        """Run ``[(step, cmd, env)]`` in order, stopping at the first failure; ok, timeout -> incomplete,
        else the stage's failure status."""
        for step, cmd, env in steps:
            rc = self.run_step(pr, stage, step, cmd, env, late)
            if rc == TIMEOUT_RC:
                return self.finish(pr, stage, "incomplete", f"timeout in {step}")
            if rc != 0:
                return self.finish(pr, stage, S.STAGES[stage].on_failure, f"{step} exit {rc}")
        return self.finish(pr, stage, "ok")

    # ----- setup -----------------------------------------------------------

    def setup(self) -> None:
        o = self.opts
        if o.profile not in PROFILES:
            raise RunError(f"unknown profile {o.profile!r} (full | smoke)")
        if o.ab_phase not in AB_PHASES:
            raise RunError(f"unknown --ab-phase {o.ab_phase!r} (all | render | judge)")
        if o.smoke and not o.vlm_url:
            raise RunError("--profile smoke needs --vlm-url (the fake VLM server, §2.5)")
        unknown = sorted(set(o.force) - set(S.STAGES))
        if unknown:
            raise RunError(f"--force: unknown stage(s) {', '.join(unknown)} (known: {', '.join(S.STAGES)})")
        if self.results is None:
            raise RunError("--results is required")
        names = split_names(o.projects)
        aliases = split_names(o.private)
        if o.private_selftest and SELFTEST_ALIAS not in aliases:
            aliases.append(SELFTEST_ALIAS)
        ab_names = split_names(o.ab)
        if not (names or aliases or ab_names):
            raise RunError("nothing to run: give --projects, --private, --private-selftest or --ab")
        try:
            for n in names + ab_names:
                check_name(n)
        except ProjectError as exc:
            raise RunError(str(exc)) from exc
        for a in aliases:
            try:
                check_alias(a)
            except ProjectError:
                # Not echoed: a wrong alias may be the client or project name typed by mistake (§7.1).
                raise RunError(f"invalid private alias (#{aliases.index(a) + 1} of --private): use real-01, "
                               "real-02, ... (real- and 2-3 digits)") from None
        for n in names + ab_names:
            if not project_folder(n, self.repo_root).is_dir():
                raise RunError(f"no project folder projects/{n}")
        if ab_names:
            controls = o.ab_controls
            if controls:
                # M7 §8.2: the control project may be outside --ab (its M6 control renders on the volume).
                try:
                    check_name(controls)
                except ProjectError as exc:
                    raise RunError(f"--ab-controls: {exc}") from exc
                if not project_folder(controls, self.repo_root).is_dir():
                    raise RunError(f"--ab-controls: no project folder projects/{controls}")
        elif o.ab_controls:
            raise RunError("--ab-controls without --ab")
        if o.private_selftest:
            self.prepare_selftest()
        for n in names:
            ref = replace(public_project(n, self.results, self.repo_root), out_dir=self.outputs_root / n)
            self.runs.append(ProjectRun(ref))
        for a in aliases:
            try:
                ref = private_project(a, Path(o.private_root), Path(o.private_outputs), Path(o.private_results),
                                      self.repo_root)
            except ProjectError as exc:
                raise RunError(str(exc)) from exc
            self.runs.append(ProjectRun(ref))
        by_name = {pr.name: pr for pr in self.runs}
        for n in ab_names:
            pr = by_name.get(n)
            if pr is None:
                ref = replace(public_project(n, self.results, self.repo_root), out_dir=self.outputs_root / n)
                pr = ProjectRun(ref, full=False)
                by_name[n] = pr
            pr.ab = pr.look_alt = True
            self.ab_runs.append(pr)
        if ab_names and o.ab_phase == "judge" and not self.ab_controls:
            self.ab_controls = self.judge_controls(ab_names)
        if self.ab_controls and self.ab_controls not in ab_names:
            n = self.ab_controls
            pr = by_name.get(n)
            if pr is None:
                ref = replace(public_project(n, self.results, self.repo_root), out_dir=self.outputs_root / n)
                pr = ProjectRun(ref, full=False)
            pr.ab = True
            self.ab_runs.append(pr)
        for pr in self.runs + [p for p in self.ab_runs if not p.full]:
            self.archive_old_outputs(pr)
        control = self.controls_run()
        if control is not None and self.opts.ab_phase != "judge":
            missing = self.control_renders_missing(control)
            control.controls_needed = bool(missing)
            if missing:
                self.out(f"A/B controls: {control.name} has no control renders ({missing[0]} missing): they are "
                         "rendered in this run")
        for pr in self.runs + self.ab_runs:
            ST.run_dir(pr.out).mkdir(parents=True, exist_ok=True)
        if aliases and self.job_dir is not None:
            self.link_private_results(aliases)

    def judge_controls(self, ab_names: list) -> Optional[str]:
        """``--ab-phase judge`` without ``--ab-controls``: the one A/B project whose ``ab/control_views.json`` the
        render pod wrote (its control sets are judged and the summary reads them); refused when several have one."""
        found = [n for n in ab_names if (self.outputs_root / n / "ab" / "control_views.json").is_file()]
        if len(found) > 1:
            raise RunError(f"--ab-phase judge: {', '.join(found)} all have control renders (ab/control_views.json): "
                           "pass --ab-controls with the render pod's control project")
        if found:
            self.out(f"A/B controls: {found[0]} (its ab/control_views.json from the render pod; "
                     "--ab-controls not given)")
        return found[0] if found else None

    def archive_root(self) -> Path:
        """``$WENART_OUTPUTS_ARCHIVE``, else ``<repo>/../outputs-archive`` (pod: ``/workspace/outputs-archive``,
        outside the repo, so ``git clean`` in ``pod_entry.sh`` never touches it)."""
        env = os.environ.get("WENART_OUTPUTS_ARCHIVE", "").strip()
        return Path(env) if env else self.repo_root.parent / "outputs-archive"

    def archive_old_outputs(self, pr: ProjectRun) -> None:
        """§2.3: a public out_dir that exists, is not empty and has no ``run/`` folder was written by an earlier job
        that is not ``wenart.run`` (the M5 ``polish.sh`` wrote ``outputs/synthetic-01`` and ``-03``: renders of
        cameras the search no longer makes, an old polish manifest, ...). It is renamed, never deleted, to
        ``<archive root>/<name>-<UTC stamp>`` so none of its files is reused, reported or copied. Private out_dirs
        are created by ``wenart.run`` and are never moved."""
        out = pr.out
        if pr.ref.private or out.is_symlink() or not out.is_dir() or ST.run_dir(out).exists():
            return
        try:
            if not any(out.iterdir()):
                return
        except OSError:
            return
        root = self.archive_root()
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        target, n = root / f"{pr.name}-{stamp}", 2
        while target.exists() or target.is_symlink():
            target, n = root / f"{pr.name}-{stamp}-{n}", n + 1
        try:
            root.mkdir(parents=True, exist_ok=True)
            out.rename(target)
        except OSError as exc:
            pr.archive_note = (f"{S.t(out)} holds outputs of an earlier job (no run/ folder) and could not be moved "
                               f"aside ({type(exc).__name__}): its files may show up in this run")
            self.out(f"{pr.name}: {pr.archive_note}")
            return
        pr.archived = S.t(target)
        pr.archive_note = f"earlier outputs without run records moved to {pr.archived}"
        self.out(f"{pr.name}: {pr.archive_note}")

    def prepare_selftest(self) -> None:
        """``--private-selftest``: ``tests/fixtures/projects/review-01`` (two untitled plan pages: needs_review)
        copied to ``<private_root>/selftest-02``. An existing copy is kept only when it is the current source
        (the same files with the same sha256); any other (the M6 copy of synthetic-02, a changed fixture) is moved
        to ``<archive root>/selftest-02-upload-<UTC stamp>`` (never deleted) and the source is copied again."""
        source = project_folder(SELFTEST_SOURCE, self.repo_root)
        target = upload_dir(SELFTEST_ALIAS, Path(self.opts.private_root))
        if target.exists() or target.is_symlink():
            if not target.is_symlink() and tree_digest(target) == tree_digest(source):
                return
            root = self.archive_root()
            stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
            aside, n = root / f"{SELFTEST_ALIAS}-upload-{stamp}", 2
            while aside.exists() or aside.is_symlink():
                aside, n = root / f"{SELFTEST_ALIAS}-upload-{stamp}-{n}", n + 1
            root.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(aside))
            self.out(f"private self-test: the upload was not a copy of {SELFTEST_SOURCE} (stale): moved to "
                     f"{S.t(aside)}, copied again")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)

    @staticmethod
    def control_renders_missing(pr: ProjectRun) -> list:
        """The control render manifests (``CONTROL_RENDER_MANIFESTS``) the control project lacks: none when its M6
        control renders are on the volume (they are used as they are, M7 §8.2)."""
        return [rel for rel in CONTROL_RENDER_MANIFESTS if not (pr.out / rel).is_file()]

    def link_private_results(self, aliases: list) -> None:
        """``$JOB_DIR/results-private/<a>`` -> ``<private_results>/<a>`` (collected by the runner, §1.1)."""
        base = self.job_dir / "results-private"
        base.mkdir(parents=True, exist_ok=True)
        for a in aliases:
            target = Path(self.opts.private_results) / a
            target.mkdir(parents=True, exist_ok=True)
            link = base / a
            if link.is_symlink() or link.exists():
                if link.is_symlink() and Path(os.readlink(link)) == target:
                    continue
                if link.is_symlink():
                    link.unlink()
                else:
                    continue
            link.symlink_to(target, target_is_directory=True)

    # ----- phases ----------------------------------------------------------

    @contextmanager
    def phase_block(self, n: int):
        self.phase = n
        entry = {"phase": n, "name": PHASE_NAMES[n], "start_utc": ST.utc_now(), "end_utc": None, "seconds": None}
        t0 = self.now()
        self.out(f"phase {n} start: {PHASE_NAMES[n]}")
        try:
            yield entry
        finally:
            entry["end_utc"] = ST.utc_now()
            entry["seconds"] = round(self.now() - t0, 1)
            self.phases.append(entry)
            self.out(f"phase {n} end ({entry['seconds']:.0f} s)")

    def run(self) -> int:
        """All phases; the exit code (§2.1)."""
        self.setup()
        left = "no deadline" if self.deadline is None else f"{self.deadline - self.now():.0f} s to the deadline"
        self.out(f"run {self.run_id}: projects [{' '.join(pr.name for pr in self.runs)}], A/B "
                 f"[{' '.join(pr.name for pr in self.ab_runs)}] ({self.opts.ab_phase}), profile {self.opts.profile}, "
                 f"{left}")
        steps = [self.phase1, self.phase2, self.phase3, self.phase4, self.phase5, self.phase6, self.phase7,
                 lambda: self.vlm_phase(8, "qwen"), lambda: self.vlm_phase(9, "glm"), self.phase10]
        for n, fn in enumerate(steps, start=1):
            with self.phase_block(n):
                fn()
        with self.phase_block(11):
            lists = self.phase11()
        self.exit_code = self.compute_exit()
        self.write_manifests(lists, final=True)
        self.out(f"run {self.run_id} done: exit {self.exit_code}")
        return self.exit_code

    # ----- phase 1: CPU ---------------------------------------------------

    def phase1(self) -> None:
        for pr in self.runs:
            self.stage_intake(pr)
            if not pr.active:
                continue
            self.stage_pipeline(pr)
            if not pr.active:
                continue
            if pr.pending:
                # The questions of the first run: the stored (or committed) answers that complete a model's set are
                # copied now; fit follows pipeline_final in phase 3 (M7 §9.1).
                for key in self.recognition_keys():
                    if not self.recognition_missing(pr, key):
                        self.recognize_part(pr, key, None)
            else:
                self.skip(pr, "recognize", "no questions")
                self.skip(pr, "pipeline_final", "no questions")
                self.stage_fit(pr)
            if not pr.active:
                continue
            self.photos_prepare(pr)
            self.stage_style(pr, terms=pr.terms_applied)
        for pr in self.ab_runs:
            if pr.full:
                continue
            if self.opts.ab_phase == "judge":
                self.skip(pr, "ab_prepare", "not in this phase")
                continue
            if pr.controls_needed:
                self.ab_prepare_part1(pr)

    def stage_fit(self, pr: ProjectRun) -> None:
        """Stage fit (the building's documented pieces; ``catalog_objaverse.json`` is merged by catalog.load, so it
        is an input too)."""
        self.fp_stage(pr, "fit", S.fit(self.tools, pr.ref),
                      [pr.out / "building.json", self.repo_root / S.CATALOG, self.repo_root / S.CATALOG_OBJAVERSE,
                       self.repo_root / S.CATALOG_LIBRARY])

    # ----- recognition (M7 §1.4, §9.1) --------------------------------------

    def recognition_keys(self) -> list:
        """The model keys that answer recognition questions in this run (both passes, ``CHECK_MODELS`` order)."""
        return [k for k in self.opts.check_models if k in self.models]

    def recognition_dir(self, pr: ProjectRun) -> Path:
        return pr.out / S.RECOGNITION_DIR

    def recognition_items(self, pr: ProjectRun) -> list:
        data = read_json(self.recognition_dir(pr) / "requests.json")
        items = data.get("items") if isinstance(data, dict) else None
        return [i for i in items or [] if isinstance(i, dict) and i.get("key") and i.get("input_sha256")]

    def answers_file(self, pr: ProjectRun, key: str) -> Path:
        return self.recognition_dir(pr) / f"answers_{self.tools.model_slug(key)}.json"

    def recognition_missing(self, pr: ProjectRun, key: str) -> list:
        """The question keys without a current, schema-valid answer of ``key`` in ``<out>/recognition`` or in the
        committed seeds (``results/recognition/<p>/``): what a server would have to answer."""
        from wenart.recognition import answers as A    # lazy: jsonschema
        items = self.recognition_items(pr)
        if not items or key not in self.models:
            return [i["key"] for i in items]
        store = A.AnswerStore.for_model(self.recognition_dir(pr), key, self.models)
        seeds = S.recognition_seeds(pr.ref, self.repo_root)
        seed = None
        if seeds is not None and (seeds / store.path.name).is_file():
            seed = A.AnswerStore(seeds / store.path.name, key, store.data["slug"], self.tools.model_id(key))
        return [i["key"] for i in items if store.valid(i) is None and (seed is None or seed.valid(i) is None)]

    def recognition_complete(self, pr: ProjectRun) -> bool:
        """Every question has a current answer of both models in ``<out>/recognition`` (the pipeline's own rule)."""
        from wenart.recognition import answers as A    # lazy: jsonschema
        items = self.recognition_items(pr)
        if not items:
            return True
        return A.is_complete(A.load(self.recognition_dir(pr), items, self.models))

    def recognize_part(self, pr: ProjectRun, key: str, url: Optional[str], seqs: int = 1) -> None:
        """One model's answers (``url`` None: the stored and committed answers only, no server)."""
        missing = self.recognition_missing(pr, key) if url is not None else []
        if url is not None and not self.can_start(S.est_calls(len(missing), seqs)):
            self.finish(pr, "recognize", "incomplete", f"deadline: recognition ({key}) not started", merge=True,
                        outputs=self.recognition_outputs(pr))
            return
        seeds = S.recognition_seeds(pr.ref, self.repo_root)
        cmd = S.recognize(self.tools, pr.ref, key, url, seqs, seeds if seeds is not None and seeds.is_dir() else None)
        step = f"{'ask' if url is not None else 'stored answers'} {key}"
        rc = self.run_step(pr, "recognize", step, cmd)
        if rc == 0:
            status, note = ("ok", None) if url is not None else ("reused", None)
        elif rc in (3, TIMEOUT_RC):
            status, note = "incomplete", f"deadline: recognition ({key}) cut"
        else:
            status, note = "warning", f"recognition {key} exit {rc}: its unanswered pieces stay unknown, unverified"
        self.finish(pr, "recognize", status, note, merge=True, outputs=self.recognition_outputs(pr))

    def recognition_outputs(self, pr: ProjectRun) -> list:
        return [f"{S.RECOGNITION_DIR}/{self.answers_file(pr, k).name}" for k in self.recognition_keys()
                if self.answers_file(pr, k).is_file()]

    def finalize(self, pr: ProjectRun) -> None:
        """A pending project once its answers are in (or will not come): pipeline_final, then fit (phase 3)."""
        if not pr.active or not pr.pending or pr.finalized:
            return
        if self.status_of(pr, "recognize") is None:
            # No model was asked in this run (no recognition model in CHECK_MODELS).
            self.finish(pr, "recognize", "warning", "no recognition model in CHECK_MODELS: the pieces stay unknown, "
                        "unverified", outputs=self.recognition_outputs(pr))
        self.stage_pipeline_final(pr)
        if pr.active:
            self.stage_fit(pr)

    def pipeline_final_inputs(self, pr: ProjectRun) -> dict:
        ins = ST.file_hashes([pr.ref.project_dir] + [self.answers_file(pr, k) for k in self.models])
        ins.update(self.converter_inputs())
        return ins

    def stage_pipeline_final(self, pr: ProjectRun) -> None:
        """The pipeline again with ``--answers`` (``--no-ai`` when an answer is missing, so it never exits 4; the
        smoke profile: ``--no-ai`` and no answers). Reused only while the stored ``building.json`` is the one it
        wrote (its canonical sha256 in ``written``): a re-run first pipeline overwrites it.

        Exit 4 although every answer was in (the answers opened new questions, e.g. a raster page's second-round
        symbol questions): never ``failed``; the pipeline runs once more with ``--no-ai`` (the new items stay
        unknown/unverified and are listed in its report) and the stage is a ``warning``
        (``SECOND_ROUND_NOTE``). The record keeps the first command's fingerprint; a resumed run whose
        requests.json now lists the new questions asks them in its sessions and runs pipeline_final again."""
        pr.finalized = True
        complete = self.recognition_complete(pr)
        smoke = self.opts.smoke
        no_ai = smoke or not complete
        cmd = S.pipeline_final(self.tools, pr.ref, answers=not smoke, no_ai=no_ai)
        ins = self.pipeline_final_inputs(pr)
        fp = ST.fingerprint("pipeline_final", S.STAGE_VERSION["pipeline_final"], cmd[1:], ins,
                            self.code("pipeline_final"))
        prev = self.previous(pr, "pipeline_final")
        building = pr.out / "building.json"
        if not self.forced("pipeline_final") and ST.reusable(prev, fp, pr.out) \
                and prev.written.get("building.json") == ST.canonical_sha256(building):
            self.finish(pr, "pipeline_final", "reused", fingerprint=fp, inputs=ins, outputs=prev.outputs,
                        written=prev.written)
            return
        rc = self.run_step(pr, "pipeline_final", "pipeline_final", cmd)
        second_round = rc == S.EXIT_QUESTIONS and not no_ai
        if second_round:
            rc = self.run_step(pr, "pipeline_final", "pipeline_final --no-ai",
                               S.pipeline_final(self.tools, pr.ref, answers=not smoke, no_ai=True))
        data = read_json(building)
        status = data.get("status") if isinstance(data, dict) else None
        written = {"building.json": ST.canonical_sha256(building)}
        rec = {"fingerprint": fp, "inputs": ins, "written": written}
        how = ("smoke profile: --no-ai" if smoke else "answers applied" if complete
               else "--no-ai: the unanswered pieces stay unknown, unverified")
        if second_round and rc == 0 and status == "ok":
            self.finish(pr, "pipeline_final", "warning", S.SECOND_ROUND_NOTE, **rec)
        elif rc == 0 and status == "ok":
            self.finish(pr, "pipeline_final", "ok", how, **rec)
        elif rc == 1 and status == "needs_review":
            self.finish(pr, "pipeline_final", "needs_review", "building needs review (report.md)", **rec)
        elif rc == TIMEOUT_RC:
            self.finish(pr, "pipeline_final", "incomplete", "timeout", **rec)
        else:
            self.finish(pr, "pipeline_final", "failed", f"exit {rc}, building status {status}", **rec)

    def converter_inputs(self) -> dict:
        """The LibreDWG ``VERSION`` string in the pipeline fingerprint (M7 §5.1; None without a binary)."""
        if self._libredwg is None:
            try:
                from wenart.ingest.dwg import libredwg_version
                self._libredwg = (libredwg_version(),)
            except Exception:  # noqa: BLE001 - recorded as unknown; the pipeline reports a broken converter itself
                self._libredwg = ("unknown",)
        return {"<LibreDWG VERSION>": self._libredwg[0]}

    def stage_intake(self, pr: ProjectRun) -> None:
        if not pr.ref.private:
            self.skip(pr, "intake", "private only")
            return
        # A missing upload goes through the intake CLI as well: it writes a fresh needs_review manifest ("not
        # uploaded") and removes an older staged copy, so neither an earlier ok intake_manifest.json nor its
        # staged documents reach the report (§7.1).
        upload = upload_dir(pr.name, Path(self.opts.private_root))
        cmd = S.intake(self.tools, pr.ref)
        # The upload's listing (path, size, mtime), never its bytes: an upload may hold GBs of files the intake
        # skips; the intake's own sha256 of the kept files drives the later stages' reuse.
        ins = {S.t(upload): ST.listing_sha256(upload)}
        fp = ST.fingerprint("intake", S.STAGE_VERSION["intake"], cmd[1:], ins, self.code("intake"))
        prev = self.previous(pr, "intake")
        if not self.forced("intake") and ST.reusable(prev, fp, pr.out):
            self.finish(pr, "intake", "reused", fingerprint=fp, inputs=ins, outputs=prev.outputs)
            return
        rc = self.run_step(pr, "intake", "stage", cmd)
        manifest = read_json(pr.out / "intake_manifest.json")
        manifest = manifest if isinstance(manifest, dict) else {}
        if rc == INTAKE.EXIT_NEEDS_REVIEW or manifest.get("status") == "needs_review":
            # Exit 4 = needs_review (wenart/intake.py). Only the intake's fixed reasons are recorded.
            reasons = [str(r) for r in manifest.get("reasons") or []]
            note = next((r for r in reasons if r in PRIVATE_NOTES), None) or "needs review (intake_manifest.json)"
            self.finish(pr, "intake", "needs_review", note, fingerprint=fp, inputs=ins)
        elif rc == 0:
            self.finish(pr, "intake", "ok", fingerprint=fp, inputs=ins)
        else:
            self.finish(pr, "intake", "failed", f"exit {rc}", fingerprint=fp, inputs=ins)

    def stage_pipeline(self, pr: ProjectRun) -> None:
        """Stage pipeline. Exit 4 (checked first) = recognition questions written: ``pending`` (M7 §9.1); a stored
        pending record is reused as ``pending`` (pipeline_final may have rewritten the building since)."""
        if not pr.ref.project_dir.is_dir():
            self.finish(pr, "pipeline", "failed", "no project folder")
            return
        cmd = S.pipeline(self.tools, pr.ref)
        ins = ST.file_hashes([pr.ref.project_dir])
        ins.update(self.converter_inputs())
        fp = ST.fingerprint("pipeline", S.STAGE_VERSION["pipeline"], cmd[1:], ins, self.code("pipeline"))
        prev = self.previous(pr, "pipeline")
        if not self.forced("pipeline") and ST.reusable(prev, fp, pr.out):
            if prev.status == "pending":
                pr.pending = True
                self.finish(pr, "pipeline", "pending", self.pending_note(pr, reused=True), fingerprint=fp,
                            inputs=ins, outputs=prev.outputs)
            else:
                self.finish(pr, "pipeline", "reused", fingerprint=fp, inputs=ins, outputs=prev.outputs)
            return
        rc = self.run_step(pr, "pipeline", "pipeline", cmd)
        building = read_json(pr.out / "building.json")
        status = building.get("status") if isinstance(building, dict) else None
        if rc == 4:
            pr.pending = True
            self.finish(pr, "pipeline", "pending", self.pending_note(pr), fingerprint=fp, inputs=ins)
        elif rc != 0 and status == "needs_review":
            self.finish(pr, "pipeline", "needs_review", "building needs review (report.md)", fingerprint=fp,
                        inputs=ins)
        elif rc == 0 and status == "ok":
            self.finish(pr, "pipeline", "ok", fingerprint=fp, inputs=ins)
        elif rc == TIMEOUT_RC:
            self.finish(pr, "pipeline", "incomplete", "timeout", fingerprint=fp, inputs=ins)
        else:
            self.finish(pr, "pipeline", "failed", f"exit {rc}, building status {status}", fingerprint=fp,
                        inputs=ins)

    def pending_note(self, pr: ProjectRun, reused: bool = False) -> str:
        n = len(self.recognition_items(pr))
        return f"{'reused: ' if reused else ''}{n} recognition question(s) written (recognition/requests.json)"

    def stage_style(self, pr: ProjectRun, terms: bool) -> None:
        pr.parts.pop("style", None)
        self.simple_stage(pr, "style", [("style", S.style(self.tools, pr.ref, terms=terms), None)])

    def ab_prepare_part1(self, pr: ProjectRun) -> None:
        """§6.3 AB prepare part 1: pipeline, style without photos, assets (A/B projects not in --projects)."""
        self.stage_pipeline(pr)
        if self.status_of(pr, "pipeline") in ST.GOING_ON:
            self.stage_style(pr, terms=False)
        if self.status_of(pr, "style") in ST.GOING_ON:
            self.simple_stage(pr, "assets", [("assets", S.assets(self.tools, pr.ref), None)])
        bad = [(s, self.status_of(pr, s)) for s in ("pipeline", "style")
               if self.status_of(pr, s) not in ST.GOING_ON]
        if bad:
            stage, status = bad[0]
            pr.ab_dropped = f"{stage} {status}"
            self.finish(pr, "ab_prepare", "failed", f"dropped from the A/B: {stage} {status}", outputs=[])
        else:
            self.finish(pr, "ab_prepare", "ok", outputs=[])

    # ----- style photos (stage 2) -----------------------------------------

    def photo_list(self, pr: ProjectRun) -> list:
        from wenart.brief import load_brief
        from wenart.style.photos import style_photo_paths
        try:
            brief = load_brief(pr.ref.project_dir)
        except Exception:  # noqa: BLE001 - a broken brief is the style stage's error to report
            brief = None
        return list(style_photo_paths(pr.ref.project_dir, brief)[0])

    def photo_missing(self, pr: ProjectRun, key: str) -> list:
        """The photos without a valid answer (data, no error) of ``check.yaml models.<key>.id``."""
        if self.forced("photos") and key not in pr.photos_asked:
            return list(pr.photos)
        data = read_json(pr.out / "style_photos" / "passes.json")
        calls = data.get("calls") if isinstance(data, dict) else None
        model_id = self.tools.model_id(key)
        missing = []
        for photo in pr.photos:
            try:
                sha = hashlib.sha256(Path(photo).read_bytes()).hexdigest()
            except OSError:
                missing.append(photo)
                continue
            if not any(self._valid_photo_call(c, sha, model_id) for c in calls or []):
                missing.append(photo)
        return missing

    @staticmethod
    def _valid_photo_call(call: dict, sha: str, model_id: str) -> bool:
        if not isinstance(call, dict) or call.get("sha256") != sha or call.get("error"):
            return False
        result = call.get("result") if isinstance(call.get("result"), dict) else {}
        for p in result.get("passes") or []:
            if isinstance(p, dict) and p.get("model") == model_id and isinstance(p.get("data"), dict) \
                    and not p.get("error"):
                return True
        return False

    def photos_complete(self, pr: ProjectRun) -> bool:
        return bool(pr.photos) and all(not self.photo_missing(pr, k) for k in self.opts.check_models)

    def photos_prepare(self, pr: ProjectRun) -> None:
        """Phase 1: no photos -> skipped; complete stored answers -> combine (terms for the first style)."""
        pr.photos = self.photo_list(pr)
        if not pr.photos:
            self.skip(pr, "photos", "no style photos")
            return
        if self.photos_complete(pr):
            self.apply_terms(pr, restyle=False)

    def apply_terms(self, pr: ProjectRun, restyle: bool) -> bool:
        """Photo combine; on success the next (or this, ``restyle``) style stage uses the terms."""
        rc = self.run_step(pr, "photos", "combine", S.photos_combine(self.tools, pr.ref))
        pr.terms_applied = rc == 0
        if restyle and pr.terms_applied:
            self.stage_style(pr, terms=True)
        return pr.terms_applied

    def photos_session_part(self, pr: ProjectRun, key: str, url: str, seqs: int) -> None:
        missing = self.photo_missing(pr, key)
        if not missing:
            return
        if not self.can_start(S.est_calls(len(missing), seqs)):
            self.not_started(pr, "photos", f"photos ({key})")
            return
        rc = self.run_step(pr, "photos", f"read {key}", S.photos_read(self.tools, pr.ref, key, url, missing))
        pr.photos_asked.add(key)
        if rc == TIMEOUT_RC:
            self.finish(pr, "photos", "incomplete", f"timeout reading photos ({key})", merge=True)
            return
        if len(self.photo_missing(pr, key)) < len(missing):
            pr.new_photo_answers = True

    def photos_finish(self, pr: ProjectRun) -> None:
        """End of phase 3: ok / reused when every photo has both answers, else warning (brief only)."""
        if not pr.photos or pr.terminal is not None or self.status_of(pr, "photos") == "incomplete":
            return
        if self.photos_complete(pr):
            if not pr.terms_applied:
                self.apply_terms(pr, restyle=True)
            asked = any(s["name"].startswith("read ") for s in pr.parts.get("photos", []))
            if pr.terms_applied:
                self.finish(pr, "photos", "ok" if asked else "reused")
            else:
                self.finish(pr, "photos", "warning", "photo combine failed: style from the brief only")
        else:
            missing = {k: len(self.photo_missing(pr, k)) for k in self.opts.check_models}
            text = ", ".join(f"{k} {n}" for k, n in missing.items() if n)
            self.finish(pr, "photos", "warning", f"photo answers missing ({text}): style from the brief only")

    # ----- server sessions ---------------------------------------------------

    def seqs(self, key: str = "qwen") -> int:
        """Sequences of ``key``'s server: ``servers.server_seqs(VRAM, check.yaml models.<key>.max_seqs)`` (2 with
        ``--vlm-url``)."""
        if key not in self._seqs:
            if self.opts.vlm_url:
                self._seqs[key] = 2
            else:
                self._seqs[key] = SV.server_seqs(self.gpu_info().get("memory_mib"), SV.max_seqs_of(self.models, key))
        return self._seqs[key]

    def gpu_info(self) -> dict:
        """``{"name", "memory_mib"}`` of the pod's GPU: the injected callables, else one ``nvidia-smi`` query (name
        None and 0 MiB when it fails)."""
        if self._gpu is None:
            if self._gpu_mem is not None or self._gpu_name is not None:
                self._gpu = {"name": self._gpu_name() if self._gpu_name is not None else None,
                             "memory_mib": self._gpu_mem() if self._gpu_mem is not None else 0}
            else:
                self._gpu = self.query_gpu()
        return self._gpu

    def query_gpu(self) -> dict:
        log = (self.job_dir or self.outputs_root) / "logs" / "nvidia-smi.log"
        rc, _ = self.exec(log, SV.NVIDIA_SMI_QUERY)
        if rc != 0:
            return {"name": None, "memory_mib": 0}
        try:
            text = log.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return {"name": None, "memory_mib": 0}
        lines = [ln for ln in text.splitlines() if not ln.startswith(LOG_MARK)]
        name, mem = SV.gpu_from_text("\n".join(lines[-4:]))
        return {"name": name, "memory_mib": mem}

    @contextmanager
    def session(self, key: str):
        """A server session (``--vlm-url``: the external server)."""
        stats: list = []
        try:
            if self.server_factory is not None:
                cm = self.server_factory(key, self.deadline, stats)
            elif self.opts.vlm_url:
                cm = SV.external_server(self.opts.vlm_url, key, stats=stats)
            else:
                cm = SV.server(key, self.deadline, stats=stats, seqs=self.seqs(key),
                               mem_mib=self.gpu_info().get("memory_mib") or None, logs_dir=self.opts.logs_dir,
                               job_dir=self.job_dir, private=self.any_private, clock=self.clock, out=self.out)
            with cm as url:
                yield url
        finally:
            for s in stats:
                s.update(phase=self.phase, started_utc=s.get("started_utc") or ST.utc_now())
                self.servers.append(s)

    def start_session(self, key: str, need: list, on_fail: Callable[[ProjectRun, str, str], None]):
        """``(context manager or None)``: None when the deadline leaves no time for the start (the projects in
        ``need`` are told through ``on_fail(pr, status, note)``)."""
        if not self.can_start(S.est_server(key)):
            self.out(f"deadline: no {key} server session")
            for pr in need:
                on_fail(pr, "incomplete", f"deadline: {key} server not started")
            return None
        return self.session(key)

    # ----- phase 2: GLM photos ---------------------------------------------

    def recognition_needs(self, key: str) -> list:
        """Active pending projects (not yet finalized) with questions ``key`` still has to answer."""
        if key not in self.recognition_keys():
            return []
        return [pr for pr in self.runs if pr.active and pr.pending and not pr.finalized
                and self.recognition_missing(pr, key)]

    def recognition_server_failed(self, pr: ProjectRun, key: str, exc: "SV.ServerError") -> None:
        if exc.reason == "deadline":
            self.finish(pr, "recognize", "incomplete", f"deadline: {key} server not ready", merge=True,
                        outputs=self.recognition_outputs(pr))
        else:
            self.finish(pr, "recognize", "warning", f"server {key}: {exc.reason}: its unanswered pieces stay "
                        "unknown, unverified", merge=True, outputs=self.recognition_outputs(pr))

    def phase2(self) -> None:
        need_recog = self.recognition_needs("glm")
        need_photos = [pr for pr in self.runs if pr.active and pr.photos and self.photo_missing(pr, "glm")]
        if "glm" not in self.opts.check_models or not (need_photos or need_recog):
            self.out("phase 2: no project needs a GLM recognition or photo answer: no server")
            return
        need = need_recog + [pr for pr in need_photos if pr not in need_recog]

        def fail(pr, status, note):
            if status != "incomplete":
                return
            if pr in need_recog:
                self.finish(pr, "recognize", "incomplete", note, merge=True, outputs=self.recognition_outputs(pr))
            if pr in need_photos:
                self.finish(pr, "photos", "incomplete", note, merge=True)

        cm = self.start_session("glm", need, fail)
        if cm is None:
            return
        try:
            with cm as url:
                for pr in need_recog:
                    if pr.active:
                        self.recognize_part(pr, "glm", url, self.seqs("glm"))
                for pr in need_photos:
                    if pr.active:
                        self.photos_session_part(pr, "glm", url, self.seqs("glm"))
        except SV.ServerError as exc:
            self.out(f"phase 2: {exc}")
            for pr in need_recog:
                if pr.active and "ask glm" not in [s["name"] for s in pr.parts.get("recognize", [])]:
                    self.recognition_server_failed(pr, "glm", exc)
            for pr in need_photos:
                if exc.reason == "deadline" and pr.active:
                    fail(pr, "incomplete", "deadline: glm server not ready")

    # ----- phase 3: Qwen photos + layout -----------------------------------

    def layout_needed(self, pr: ProjectRun) -> int:
        """Rooms the layout furnishes (0 when there is none or the brief switches AI furnishing off)."""
        building = read_json(pr.out / "building_fitted.json")
        if not isinstance(building, dict):
            return 0
        mode = ((building.get("project") or {}).get("brief") or {}).get("empty_rooms", "ai")
        if mode != "ai":
            return 0
        from wenart.furniture.layout import empty_rooms
        return len(empty_rooms(building))

    def layout_fp(self, pr: ProjectRun) -> tuple[str, dict, list]:
        cmd = S.layout(self.tools, pr.ref, "<server>")
        args = list(cmd[1:])
        args[args.index("<server>")] = f"{self.tools.model_id('qwen')}@{self.tools.model_revision('qwen')}"
        ins = ST.file_hashes([pr.out / "building_fitted.json", pr.out / "style.json"])
        return ST.fingerprint("layout", S.STAGE_VERSION["layout"], args, ins, self.code("layout")), ins, args

    def layout_reusable(self, pr: ProjectRun) -> bool:
        fp, _ins, _args = self.layout_fp(pr)
        return not self.forced("layout") and ST.reusable(self.previous(pr, "layout"), fp, pr.out)

    def stage_layout(self, pr: ProjectRun, url: Optional[str]) -> None:
        fp, ins, _args = self.layout_fp(pr)
        prev = self.previous(pr, "layout")
        if not self.forced("layout") and ST.reusable(prev, fp, pr.out):
            self.finish(pr, "layout", "reused", fingerprint=fp, inputs=ins, outputs=prev.outputs)
            return
        if url is None:
            self.finish(pr, "layout", "failed", "server qwen not available", fingerprint=fp, inputs=ins)
            return
        # The layout sends its calls one at a time (2 passes per room): no division by the server's sequences.
        if not self.can_start(S.est_calls(2 * pr.layout_rooms, 1)):
            self.not_started(pr, "layout")
            return
        rc = self.run_step(pr, "layout", "layout", S.layout(self.tools, pr.ref, url))
        if rc == 0:
            self.finish(pr, "layout", "ok", fingerprint=fp, inputs=ins)
        elif rc == TIMEOUT_RC:
            self.finish(pr, "layout", "incomplete", "timeout", fingerprint=fp, inputs=ins)
        elif rc == 3:
            self.finish(pr, "layout", "failed", "exit 3: the server did not answer", fingerprint=fp, inputs=ins)
        else:
            self.finish(pr, "layout", "failed", f"exit {rc}", fingerprint=fp, inputs=ins)

    def phase3(self) -> None:
        # Photos that the GLM session just completed: the terms reach the style before any decision.
        for pr in self.runs:
            if pr.active and pr.photos and pr.new_photo_answers and not pr.terms_applied and self.photos_complete(pr):
                self.apply_terms(pr, restyle=True)
        # Pending projects whose answers are all in (or whose Qwen pass is not asked): the final building now.
        need_recog = self.recognition_needs("qwen")
        for pr in self.runs:
            if pr.active and pr.pending and pr not in need_recog:
                self.finalize(pr)
        for pr in self.runs:
            if pr.active and not (pr.pending and not pr.finalized):
                self.layout_prepare(pr)
        need_photos = [pr for pr in self.runs if pr.active and pr.photos and "qwen" in self.opts.check_models
                       and self.photo_missing(pr, "qwen")]
        need_layout = [pr for pr in self.runs if pr.active and pr.layout_rooms and not self.layout_reusable(pr)]
        # Milestone 9: the AI decor asks after the layout, in the same session (a reused layout keeps its building).
        need_decor = [pr for pr in self.runs if pr.active and not (pr.pending and not pr.finalized)
                      and pr not in need_layout and self.decor_wanted(pr)]
        if not need_photos and not need_layout and not need_recog and not need_decor:
            self.out("phase 3: no project needs Qwen recognition answers, a layout, a Qwen photo answer or decor "
                     "answers: no server")
            for pr in self.runs:
                if pr.active and pr.layout_rooms:
                    self.stage_layout(pr, None)
                if pr.active:
                    self.stage_decor_ask(pr, None)
                self.photos_finish(pr)
            return
        need = need_recog + [pr for pr in need_photos + need_layout + need_decor if pr not in need_recog]

        def fail(pr, status, note):
            if pr in need_recog and not pr.finalized:
                self.finish(pr, "recognize", status if status == "incomplete" else "warning", note, merge=True,
                            outputs=self.recognition_outputs(pr))
            if pr in need_layout:
                self.finish(pr, "layout", status, note)
            elif status == "incomplete" and pr in need_photos:
                self.finish(pr, "photos", "incomplete", note, merge=True)
            if pr in need_decor and "decor_ask" not in pr.records:
                self.finish(pr, "decor_ask", "warning", f"{note}: rule decor")

        cm = self.start_session("qwen", need, fail)
        if cm is not None:
            try:
                with cm as url:
                    for pr in need_recog:
                        if pr.active:
                            self.recognize_part(pr, "qwen", url, self.seqs("qwen"))
                        self.finalize(pr)
                        if pr.active:
                            self.layout_prepare(pr)
                    for pr in need_photos:
                        if pr.active:
                            self.photos_session_part(pr, "qwen", url, self.seqs("qwen"))
                    for pr in self.runs:
                        if pr.active and pr.photos and pr.new_photo_answers and not pr.terms_applied \
                                and self.photos_complete(pr):
                            self.apply_terms(pr, restyle=True)
                    for pr in self.runs:
                        if pr.active and pr.layout_rooms:
                            self.stage_layout(pr, url)
                        if pr.active and not (pr.pending and not pr.finalized):
                            self.stage_decor_ask(pr, url)
            except SV.ServerError as exc:
                self.out(f"phase 3: {exc}")
                status = "incomplete" if exc.reason == "deadline" else "failed"
                for pr in need_recog:
                    if pr.active and not pr.finalized and \
                            "ask qwen" not in [s["name"] for s in pr.parts.get("recognize", [])]:
                        self.recognition_server_failed(pr, "qwen", exc)
                for pr in need_layout:
                    if pr.active and "layout" not in pr.records:
                        self.finish(pr, "layout", status, f"server qwen: {exc.reason}")
                for pr in need_decor:
                    if pr.active and "decor_ask" not in pr.records:
                        self.finish(pr, "decor_ask", "warning", f"server qwen: {exc.reason}: rule decor")
        for pr in self.runs:
            # Questions without a Qwen session (a server error): the final building with the answers there are.
            if pr.active and pr.pending and not pr.finalized:
                self.finalize(pr)
                if pr.active:
                    self.layout_prepare(pr)
            if pr.active and pr.layout_rooms and "layout" not in pr.records:
                self.stage_layout(pr, None)
            if pr.active and not (pr.pending and not pr.finalized) and "decor_ask" not in pr.records:
                self.stage_decor_ask(pr, None)
            self.photos_finish(pr)

    def decor_wanted(self, pr: ProjectRun) -> bool:
        """The AI decor needs the server: rooms to ask about and no reusable answers (the layout runs first)."""
        self.decor_prepare(pr)
        return bool(pr.decor_rooms) and "decor_ask" not in pr.records and not self.decor_ask_reusable(pr)

    def layout_prepare(self, pr: ProjectRun) -> None:
        """The rooms the layout furnishes, or the layout skipped (``no empty room``); once per project."""
        if "layout" in pr.records or pr.layout_rooms:
            return
        pr.layout_rooms = self.layout_needed(pr)
        if not pr.layout_rooms:
            self.skip(pr, "layout", "no empty room")

    # ----- Milestone 9: the AI decor's questions (docs/milestone9.md §4) ---------------------------------------

    def decor_source(self, pr: ProjectRun) -> Path:
        """The building the decor reads: the layout's when it furnished rooms in this run (or reused one), else the
        fitted one (as the decor stage of phase 4)."""
        furnished = self.status_of(pr, "layout") in ("ok", "reused") or (
            pr.layout_rooms and (pr.out / "building_furnished.json").is_file() and self.layout_reusable(pr))
        return pr.out / ("building_furnished.json" if furnished else "building_fitted.json")

    def decor_rooms_needed(self, pr: ProjectRun) -> int:
        """Rooms the AI decor asks about (0: brief decor off or rules, no furnished room with a slot)."""
        building = read_json(self.decor_source(pr))
        if not isinstance(building, dict):
            return 0
        from wenart.furniture import decor_ai as DA
        if DA.decor_mode(building) != "ai":
            return 0
        style = read_json(pr.out / "style.json")
        try:
            return len(DA.room_questions(building, DA.style_text_of(style, building)))
        except Exception as exc:  # noqa: BLE001 - a broken building: the decor stage says why
            self.out(f"{pr.name} decor questions not counted: {type(exc).__name__}: {exc}")
            return 0

    def decor_ask_fp(self, pr: ProjectRun) -> tuple[str, dict, list]:
        src = self.decor_source(pr)
        cmd = S.decor_ask(self.tools, pr.ref, src.name == "building_furnished.json", "<server>")
        args = list(cmd[1:])
        args[args.index("<server>")] = f"{self.tools.model_id('qwen')}@{self.tools.model_revision('qwen')}"
        ins = ST.file_hashes([src, pr.out / "style.json"])
        return ST.fingerprint("decor_ask", S.STAGE_VERSION["decor_ask"], args, ins, self.code("decor_ask")), ins, args

    def decor_ask_reusable(self, pr: ProjectRun) -> bool:
        fp, _ins, _args = self.decor_ask_fp(pr)
        return not self.forced("decor_ask") and ST.reusable(self.previous(pr, "decor_ask"), fp, pr.out)

    def decor_prepare(self, pr: ProjectRun) -> None:
        """Count the rooms the AI decor asks about; skipped (``no decor questions``) when there is none."""
        if "decor_ask" in pr.records or pr.decor_rooms is not None:
            return
        pr.decor_rooms = self.decor_rooms_needed(pr)
        if not pr.decor_rooms:
            self.skip(pr, "decor_ask", "no decor questions")

    def stage_decor_ask(self, pr: ProjectRun, url: Optional[str]) -> None:
        """The AI decor's two passes per room (``decor_ai ask``); without a server the stage is a warning and the
        decor stage falls back to the rules for the rooms without answers (never silently)."""
        self.decor_prepare(pr)
        if not pr.decor_rooms or "decor_ask" in pr.records:
            return
        fp, ins, _args = self.decor_ask_fp(pr)
        prev = self.previous(pr, "decor_ask")
        if not self.forced("decor_ask") and ST.reusable(prev, fp, pr.out):
            self.finish(pr, "decor_ask", "reused", fingerprint=fp, inputs=ins, outputs=prev.outputs)
            return
        if url is None:
            self.finish(pr, "decor_ask", "warning", "server qwen not available: rule decor", inputs=ins)
            return
        if not self.can_start(S.est_calls(2 * pr.decor_rooms, 1)):
            self.not_started(pr, "decor_ask")
            return
        src = self.decor_source(pr)
        rc = self.run_step(pr, "decor_ask", "decor_ask",
                           S.decor_ask(self.tools, pr.ref, src.name == "building_furnished.json", url))
        if rc == 0:
            self.finish(pr, "decor_ask", "ok", fingerprint=fp, inputs=ins)
        elif rc == TIMEOUT_RC:
            self.finish(pr, "decor_ask", "incomplete", "timeout", fingerprint=fp, inputs=ins)
        elif rc == 3:
            self.finish(pr, "decor_ask", "warning", "exit 3: some calls did not reach the server: rule decor there",
                        inputs=ins)
        else:
            self.finish(pr, "decor_ask", "warning", f"exit {rc}: rule decor", inputs=ins)

    # ----- phase 4: CPU ----------------------------------------------------

    def phase4(self) -> None:
        for pr in self.runs:
            if not pr.active:
                continue
            self.simple_stage(pr, "assets", [("assets", S.assets(self.tools, pr.ref), None)])
            furnished = self.status_of(pr, "layout") in ("ok", "reused")
            src = pr.out / ("building_furnished.json" if furnished else "building_fitted.json")
            # Milestone 9: the AI decor's answers (the rules per room without them) and the style text it asked with.
            self.fp_stage(pr, "decor", S.decor(self.tools, pr.ref, furnished),
                          [src, pr.out / "style.json", pr.out / S.DECOR_ANSWERS])
            if not pr.active:
                continue
            self.fp_stage(pr, "refit", S.refit(self.tools, pr.ref),
                          [pr.out / "building_decor.json", pr.out / "style.json", self.repo_root / S.CATALOG,
                           self.repo_root / S.CATALOG_OBJAVERSE, self.repo_root / S.CATALOG_LIBRARY])
        if self.opts.ab_phase == "judge":
            return
        for pr in self.ab_runs:
            if not pr.ab_active or not pr.controls_needed:
                continue
            if pr.full and self.status_of(pr, "style") not in ST.GOING_ON:
                pr.ab_dropped = "the project has no style"
                self.finish(pr, "ab_m5", "failed", "dropped from the A/B: the project has no style.json", outputs=[])
                continue
            self.simple_stage(pr, "ab_m5", [("ab-m5", S.ab_m5(self.tools, pr.ref), None)])
            if self.status_of(pr, "ab_m5") != "ok":
                pr.ab_dropped = "ab_m5 failed"

    # ----- phase 5: Blender --------------------------------------------------

    def scene_views(self, pr: ProjectRun, scene: str = "scene") -> int:
        data = read_json(pr.out / scene / "scene_manifest.json")
        return len(data.get("cameras") or []) if isinstance(data, dict) else 0

    def build_note(self, pr: ProjectRun, scene_dir: Path, rc: int) -> str:
        line = last_line(scene_dir / "build.log") or last_line(ST.log_path(pr.out, "build"))
        return f"exit {rc}: {line}" if line else f"exit {rc}"

    def phase5(self) -> None:
        for pr in self.runs:
            if not pr.active:
                continue
            self.stage_build(pr)
            if pr.active:
                self.stage_render(pr)
            if pr.active:
                self.stage_export(pr)
            if pr.active:
                self.stage_controls(pr)
        if self.opts.ab_phase == "judge":
            return
        controls = self.controls_run()
        if controls is None or not controls.ab_active:
            return
        if controls.controls_needed:
            self.ab_render_stage(controls)
            if controls.ab_active:
                self.ab_controls_stage(controls)
        else:
            note = "the M6 control renders on the volume (ab/renders, ab/ctl_*, ab/nuisance_ev) are used as they are"
            self.finish(controls, "ab_render", "reused", note, outputs=[])
            self.finish(controls, "ab_controls", "reused", note, outputs=[])

    def stage_build(self, pr: ProjectRun) -> None:
        if not self.can_start(S.EST_BUILD_S):
            self.not_started(pr, "build")
            return
        rc = self.run_step(pr, "build", "build", S.build(self.tools, pr.ref, force=self.forced("build"),
                                                          lens_mm=self.brief_lens(pr)))
        if rc == 0:
            self.finish(pr, "build", "ok")
        elif rc == TIMEOUT_RC:
            self.finish(pr, "build", "incomplete", "timeout")
        else:
            self.finish(pr, "build", "failed", self.build_note(pr, pr.out / "scene", rc))

    def render_status(self, rc: int, manifest_path: Path) -> tuple[str, Optional[str]]:
        manifest = read_json(manifest_path)
        cut = isinstance(manifest, dict) and bool(manifest.get("incomplete"))
        if rc == 3 or rc == TIMEOUT_RC or cut:
            return "incomplete", ("timeout" if rc == TIMEOUT_RC else "deadline: render cut")
        if rc != 0:
            return "failed", f"exit {rc}"
        return "ok", None

    def stage_render(self, pr: ProjectRun) -> None:
        """Stage render; a look_alt project of the A/B also saves the alt previews (``--alt-look None``)."""
        pr.views = self.scene_views(pr)
        if not self.can_start(S.est_render(pr.views)):
            self.not_started(pr, "render")
            return
        cmd = S.render(self.tools, pr.ref, force=self.forced("render"), alt_look=pr.look_alt)
        rc = self.run_step(pr, "render", "render", cmd)
        status, note = self.render_status(rc, pr.out / "renders" / "render_manifest.json")
        self.finish(pr, "render", status, note)

    def stage_export(self, pr: ProjectRun) -> None:
        """Milestone 9 (user request of 4 Oct 2026): ``<p>.blend`` (packed) and ``<p>.glb`` of the final scene in
        ``<out>/export``; a failure is a warning (the renders stand)."""
        if self.opts.smoke:
            self.skip(pr, "export", "smoke profile")
            return
        if not self.can_start(S.EST_EXPORT_S):
            self.not_started(pr, "export")
            return
        rc = self.run_step(pr, "export", "export", S.export(self.tools, pr.ref))
        if rc == 0:
            self.finish(pr, "export", "ok")
        elif rc == TIMEOUT_RC:
            self.finish(pr, "export", "incomplete", "timeout")
        else:
            self.finish(pr, "export", "warning", f"exit {rc}: no 3D files")

    def stage_controls(self, pr: ProjectRun) -> None:
        rc = self.run_step(pr, "controls", "select-controls", S.select_controls(self.tools, pr.ref))
        if rc != 0:
            status = "incomplete" if rc == TIMEOUT_RC else "warning"
            self.finish(pr, "controls", status, f"select-controls exit {rc}: the check stays advisory")
            return
        selection = read_json(pr.out / "check" / "controls.json")
        hide_sets = selection.get("hide_sets") if isinstance(selection, dict) else ""
        hide_sets = S.limit_hide_sets(hide_sets or "", S.SMOKE_CONTROL_VIEWS if self.opts.smoke else None)
        if not hide_sets:
            self.finish(pr, "controls", "ok", "no control selected")
            return
        n = len(hide_sets.split(";"))
        if not self.can_start(S.est_controls(n)):
            self.not_started(pr, "controls", "control renders")
            return
        rc = self.run_step(pr, "controls", "control renders", S.control_render(self.tools, pr.ref, hide_sets))
        if rc == 0:
            self.finish(pr, "controls", "ok")
        elif rc in (3, TIMEOUT_RC):
            self.finish(pr, "controls", "incomplete", "timeout" if rc == TIMEOUT_RC else "deadline: control renders cut")
        else:
            self.finish(pr, "controls", "warning", f"control renders exit {rc}: the check stays advisory")

    # ----- A/B renders (phase 5) ----------------------------------------------

    def controls_run(self) -> Optional[ProjectRun]:
        name = self.ab_controls
        return next((pr for pr in self.ab_runs if pr.name == name), None) if name else None

    def ab_cameras(self, pr: ProjectRun) -> Optional[list]:
        """The A/B cameras to render: all (None), or the first 2 M5 cameras in the smoke profile."""
        if not self.opts.smoke:
            return None
        from wenart.run.ab import m5_cameras
        return m5_cameras(pr.out)[:S.SMOKE_AB_CAMERAS]

    def ab_render_stage(self, pr: ProjectRun) -> None:
        stage = "ab_render"
        if not self.can_start(S.EST_BUILD_S):
            self.not_started(pr, stage, "A/B build")
            return
        rc = self.run_step(pr, stage, "build", S.ab_build(self.tools, pr.ref))
        if rc != 0:
            status = "incomplete" if rc == TIMEOUT_RC else "failed"
            self.finish(pr, stage, status, self.build_note(pr, pr.out / "ab" / "scene", rc))
            pr.ab_dropped = "A/B build failed"
            return
        cams = self.ab_cameras(pr)
        views = len(cams) if cams is not None else self.scene_views(pr, "ab/scene")
        if not self.can_start(S.est_render(views)):
            self.not_started(pr, stage, "A/B render")
            return
        rc = self.run_step(pr, stage, "render", S.ab_render(self.tools, pr.ref, cams))
        status, note = self.render_status(rc, pr.out / "ab" / "renders" / "render_manifest.json")
        if status != "ok":
            self.finish(pr, stage, status, note)
            return
        try:
            from wenart.run.ab import write_cameras_check
            result = write_cameras_check(pr.out)
        except (OSError, ValueError, KeyError) as exc:
            self.finish(pr, stage, "failed", f"camera check: {type(exc).__name__}")
            return
        self.finish(pr, stage, "ok", f"{len(result['kept'])} camera(s) kept, {len(result['dropped'])} dropped")

    def control_views(self, pr: ProjectRun, n: int) -> list:
        fn = self._control_views
        if fn is None:
            from wenart.vision_check.realism import control_views as fn
        render = read_json(pr.out / "ab" / "renders" / "render_manifest.json") or {}
        scene = read_json(pr.out / "ab" / "scene" / "scene_manifest.json") or {}
        return list(fn(render, scene, n=n))

    def ab_controls_stage(self, pr: ProjectRun) -> None:
        stage = "ab_controls"
        if self.status_of(pr, "ab_render") != "ok":
            self.finish(pr, stage, "failed", "no A/B render of the control project", outputs=[])
            return
        n = S.SMOKE_AB_CAMERAS if self.opts.smoke else S.CONTROL_VIEWS
        try:
            views = self.control_views(pr, n)
        except Exception as exc:  # noqa: BLE001 - recorded; the controls then fail, the A/B is not measurable
            self.finish(pr, stage, "failed", f"control views: {type(exc).__name__}: {exc}", outputs=[])
            return
        ST.write_json(pr.out / "ab" / "control_views.json",
                      {"schema_version": "0.1", "kind": "control_views", "views": views})
        if not views:
            self.finish(pr, stage, "failed", "no control view", outputs=[])
            return
        for variant in ("ctl_flat", "ctl_proxy"):
            if not self.can_start(S.EST_BUILD_S):
                self.not_started(pr, stage, f"{variant} build")
                return
            rc = self.run_step(pr, stage, f"build {variant}", S.ab_build(self.tools, pr.ref, variant))
            if rc != 0:
                status = "incomplete" if rc == TIMEOUT_RC else "failed"
                self.finish(pr, stage, status, f"{variant} build exit {rc}", outputs=[])
                return
        for set_name in S.CONTROL_RENDERS:
            if not self.can_start(S.est_controls(len(views))):
                self.not_started(pr, stage, f"{set_name} renders")
                return
            rc = self.run_step(pr, stage, f"render {set_name}", S.ab_control_render(self.tools, pr.ref, set_name, views))
            status, note = self.render_status(rc, pr.out / "ab" / set_name / "renders" / "render_manifest.json")
            if status != "ok":
                self.finish(pr, stage, status, f"{set_name}: {note}", outputs=[])
                return
        self.finish(pr, stage, "ok", f"{len(views)} control view(s)", outputs=[])

    # ----- phase 6: diffusion -------------------------------------------------

    def brief_lens(self, pr: ProjectRun) -> Optional[float]:
        """The brief's ``render.lens_mm`` for the build (Milestone 8), None for ``auto`` (18 / 16 mm by room)."""
        from wenart.brief import lens_mm, load_brief
        try:
            return lens_mm(load_brief(pr.ref.project_dir))
        except Exception:  # noqa: BLE001 - the style stage already reported a broken brief
            return None

    def polish_on(self, pr: ProjectRun) -> bool:
        from wenart.brief import load_brief, value
        try:
            return bool(value(load_brief(pr.ref.project_dir), "polish", True))
        except Exception:  # noqa: BLE001 - the style stage already reported a broken brief
            return True

    def phase6(self) -> None:
        for pr in self.runs:
            if not pr.active:
                continue
            if self.opts.smoke:
                for stage in ("gate", "polish", "detect"):
                    self.skip(pr, stage, "smoke profile")
                continue
            if not self.polish_on(pr):
                for stage in ("gate", "polish", "detect"):
                    self.skip(pr, stage, "polish off")
                continue
            self.stage_gate(pr)
            if not pr.active:
                continue
            if pr.gate_decision in ("ok", "flagged"):
                self.stage_polish(pr)
                if pr.active:
                    self.stage_detect(pr)
            else:
                self.skip(pr, "polish", "gate not validated")
                self.skip(pr, "detect", "gate not validated")

    def gate_inputs(self, pr: ProjectRun) -> dict:
        """What a calibration depends on besides the gate code: the renders, the control selection and its hidden
        renders, the polish sweep. Render manifests are reduced to ``(camera, scene_sha256, render_key)`` per
        entry (what the render's own reuse checks): their ``deadline`` and ``skipped`` change on every pod."""
        out = pr.out
        ins = {S.t(out / "renders" / "render_manifest.json"): render_digest(out / "renders" / "render_manifest.json")}
        ins.update(ST.file_hashes([out / "check" / "controls.json", out / "polish" / "sweep" / "polish_manifest.json"]))
        for m in sorted((out / "controls").glob("hide_*/render_manifest.json")):
            ins[S.t(m)] = render_digest(m)
        return ins

    def calibration_reusable(self, pr: ProjectRun, fp: str) -> bool:
        """The stored calibration is complete and was made from the same inputs and gate code (R4: gate calibrate
        has no resume of its own; a resumed pod would pay ~150 s per project again)."""
        if self.forced("gate"):
            return False
        prev = self.previous(pr, "gate")
        if prev is None or prev.fingerprint != fp:
            return False
        if not any(s.get("name") == "calibrate" and s.get("rc") == 0 for s in prev.steps):
            return False
        cal = read_json(pr.out / "gate" / "gate_calibration.json")
        return isinstance(cal, dict) and cal.get("kind") == "gate_calibration" and cal.get("incomplete") is False \
            and isinstance(cal.get("rates"), dict)

    def stage_gate(self, pr: ProjectRun) -> None:
        cmd = S.gate_calibrate(self.tools, pr.ref)
        ins = self.gate_inputs(pr)
        fp = ST.fingerprint("gate", S.STAGE_VERSION["gate"], cmd[1:], ins, self.code("gate"))
        cal_path = pr.out / "gate" / "gate_calibration.json"
        reused = self.calibration_reusable(pr, fp)
        if reused:
            # Never moved aside: the calibration is complete and nothing it depends on changed.
            pr.parts.setdefault("gate", []).append({"name": "calibrate", "rc": 0, "seconds": 0.0, "reused": True})
            rc = 0
        elif not self.can_start(S.EST_GATE_S):
            self.not_started(pr, "gate", "gate calibrate")
            return
        else:
            rc = self.run_step(pr, "gate", "calibrate", cmd, S.CUDA_ALLOC)
        calibration = read_json(cal_path)
        cut = isinstance(calibration, dict) and bool(calibration.get("incomplete"))
        if rc != 0 and not cut and cal_path.is_file():
            # gate calibrate has no resume: after a crash the file is an older run's or a partial one that
            # looks complete. Moved aside, so neither validate nor the report reads it (§0, §7.3).
            cal_path.replace(cal_path.with_name("gate_calibration.failed.json"))
        # Always validated, so gate_validation.json describes this run (not_validated when the calibration
        # is missing or cut) and the report never shows an older decision.
        rc2 = self.run_step(pr, "gate", "validate", S.gate_validate(self.tools, pr.ref))
        validation = read_json(pr.out / "gate" / "gate_validation.json")
        rec = {"fingerprint": fp, "inputs": ins}
        if rc == TIMEOUT_RC or cut:
            pr.gate_decision = None
            self.finish(pr, "gate", "incomplete", "timeout" if rc == TIMEOUT_RC else "deadline: calibration cut",
                        **rec)
            return
        if rc != 0:
            # No complete calibration of this run: no polish, whatever a validation file says (§0, §7.3).
            pr.gate_decision = None
            self.finish(pr, "gate", "warning", f"gate decision not_validated (calibrate exit {rc})", **rec)
            return
        pr.gate_decision = validation.get("decision") if isinstance(validation, dict) and rc2 == 0 else None
        decision = pr.gate_decision or "not_validated"
        again = " (calibration reused)" if reused else ""
        if rc2 == 0:
            self.finish(pr, "gate", "ok", f"gate decision {decision}{again}", **rec)
        else:
            self.finish(pr, "gate", "warning", f"gate decision {decision} (validate exit {rc2}){again}", **rec)

    def stage_polish(self, pr: ProjectRun) -> None:
        if not self.can_start(S.est_polish(pr.views)):
            self.not_started(pr, "polish")
            return
        rc = self.run_step(pr, "polish", "polish", S.polish(self.tools, pr.ref, force=self.forced("polish")),
                           S.CUDA_ALLOC)
        pr.polish_ran = True
        manifest = read_json(pr.out / "polish" / "polish_manifest.json")
        if rc == TIMEOUT_RC or (isinstance(manifest, dict) and manifest.get("incomplete")):
            self.finish(pr, "polish", "incomplete", "timeout" if rc == TIMEOUT_RC else "deadline: polish cut")
        elif rc == 0:
            self.finish(pr, "polish", "ok")
        elif rc == 1:
            self.finish(pr, "polish", "warning", "exit 1: some views keep Cycles")
        else:
            self.finish(pr, "polish", "failed", f"exit {rc}")

    def stage_detect(self, pr: ProjectRun) -> None:
        """Stage detect (M7 §8.1): OWLv2 boxes of the Cycles and the chosen polished image of every polished view
        and of the control renders, read by combine. A failure is a warning (with a calibrated detector, combine
        then keeps those views' Cycles images); a deadline cut is incomplete."""
        if not self.can_start(S.est_detect(pr.views)):
            self.not_started(pr, "detect")
            return
        rc = self.run_step(pr, "detect", "detect", S.detect(self.tools, pr.ref, force=self.forced("detect")),
                           S.CUDA_ALLOC)
        manifest = read_json(pr.out / "detect" / "detect_manifest.json")
        manifest = manifest if isinstance(manifest, dict) else {}
        if rc == TIMEOUT_RC or manifest.get("incomplete"):
            self.finish(pr, "detect", "incomplete", "timeout" if rc == TIMEOUT_RC else "deadline: detection cut")
        elif rc == 0:
            self.finish(pr, "detect", "ok", f"skipped: {manifest['skipped']}" if manifest.get("skipped") else None)
        else:
            self.finish(pr, "detect", "warning", f"exit {rc}: no detection in this run")

    # ----- phase 7: CPU ----------------------------------------------------

    def phase7(self) -> None:
        for pr in self.runs:
            if pr.active:
                self.simple_stage(pr, "expected", [("expected", S.expected(self.tools, pr.ref), None),
                                                   ("plan-crops", S.plan_crops(self.tools, pr.ref), None)])
        outs = self.look_alt_outs()
        for pr in self.ab_runs:
            if not pr.ab_active:
                continue
            controls = pr.name == self.ab_controls
            stored = read_json(pr.out / "ab" / "pairs_v2.json")
            stored = stored if isinstance(stored, dict) else {}
            if not (controls or stored.get("controls")) and pr.out not in outs:
                why = ("no render of this run" if pr.full else "no renders/render_manifest.json on the volume")
                self.finish(pr, "ab_pairs", "failed", f"look_alt: {why}", outputs=[])
                pr.ab_dropped = why
                continue
            if self.opts.ab_phase == "judge" and self.pairs_complete(pr, stored, controls, outs):
                # Judge: the render pod's pairs file is kept as it is (§2.1), control sets included.
                self.finish(pr, "ab_pairs", "reused", f"ab/pairs_v2.json of the render pod ({len(stored['pairs'])} "
                            f"pairs{', controls' if stored.get('controls') else ''})")
                continue
            # A rebuild never drops the control sets a stored pairs file has (the M6 renders stay on the volume).
            controls = controls or bool(stored.get("controls"))
            self.simple_stage(pr, "ab_pairs", [("realism2-pairs", S.realism2_pairs(self.tools, pr.ref, controls, outs),
                                                None)])
            if self.status_of(pr, "ab_pairs") != "ok":
                pr.ab_dropped = "no pairs"

    def look_alt_outs(self) -> list:
        """The outputs of the look_alt projects with usable renders, in ``--ab`` order (the same
        ``--project-outs`` list for every ``realism2-pairs`` of the run): a project of ``--projects`` whose render
        stage ended ok in this run, another one whose ``renders/render_manifest.json`` is on the volume (an earlier
        run of it with ``--ab``)."""
        outs = []
        for pr in self.ab_runs:
            if not pr.look_alt or not pr.ab_active:
                continue
            if pr.full:
                usable = self.status_of(pr, "render") == "ok"
            else:
                usable = (pr.out / "renders" / "render_manifest.json").is_file()
            if usable:
                outs.append(pr.out)
        return outs

    @staticmethod
    def pairs_complete(pr: ProjectRun, stored: dict, controls: bool, outs: list) -> bool:
        """A stored ``ab/pairs_v2.json`` that the judge phase can use as it is: a v2 pairs file with pairs whose image
        files all exist, with the control sets when ``pr`` is the control project, made over the same look_alt
        projects."""
        pairs = stored.get("pairs")
        if stored.get("kind") != "realism2_pairs" or not isinstance(pairs, list) or not pairs:
            return False
        if controls and not stored.get("controls"):
            return False
        made_over = (stored.get("look_alt") or {}).get("projects")
        # realism2-pairs without --project-outs (no look_alt project in the run) takes the project alone.
        expected = sorted(Path(o).name for o in outs) if outs else [pr.out.name]
        if isinstance(made_over, list) and sorted(made_over) != expected:
            return False
        for p in pairs:
            if not isinstance(p, dict) or not p.get("a") or not p.get("b"):
                return False
            if not ((pr.out / str(p["a"])).is_file() and (pr.out / str(p["b"])).is_file()):
                return False
        return True

    # ----- phases 8 and 9: check and realism ---------------------------------

    def check_calls(self, pr: ProjectRun) -> int:
        """Rough call count of one model's check of ``pr`` (deadline estimate only): 2 per Cycles and per polished
        view, 4 per insertion control (removal and insertion, ``--kinds controls``, M7 §8.1), 1 style-photo test."""
        views = pr.views or self.scene_views(pr)
        polished = views if pr.polish_ran else 0
        selection = read_json(pr.out / "check" / "controls.json")
        hide_sets = selection.get("hide_sets") if isinstance(selection, dict) else ""
        hide_sets = S.limit_hide_sets(hide_sets or "", S.SMOKE_CONTROL_VIEWS if self.opts.smoke else None)
        controls = len(hide_sets.split(";")) if hide_sets else 0
        return 2 * views + 2 * polished + 4 * controls + (0 if pr.ref.private else 1)

    def pair_counts(self, pr: ProjectRun) -> dict:
        data = read_json(pr.out / "ab" / "pairs_v2.json")
        pairs = data.get("pairs") if isinstance(data, dict) else data
        counts: dict = {}
        for p in pairs or []:
            if isinstance(p, dict) and p.get("set"):
                counts[p["set"]] = counts.get(p["set"], 0) + 1
        return counts

    def realism_ready(self) -> list:
        if self.opts.ab_phase == "render":
            return []
        return [pr for pr in self.ab_runs if pr.ab_active and self.status_of(pr, "ab_pairs") in ("ok", "reused")]

    def answers_incomplete(self, path: Path) -> bool:
        data = read_json(path)
        return isinstance(data, dict) and bool(data.get("incomplete"))

    def vlm_phase(self, n: int, key: str) -> None:
        if key not in self.opts.check_models:
            self.out(f"phase {n}: model {key} not in CHECK_MODELS: no server")
            return
        checks = [pr for pr in self.runs if pr.active and self.status_of(pr, "expected") == "ok"]
        ab = self.realism_ready()
        if not checks and not ab:
            self.out(f"phase {n}: nothing to check: no {key} server")
            return

        def fail(pr, status, note):
            if pr in checks:
                self.finish(pr, "check", status, note, merge=True, outputs=[])
            if pr in ab:
                self.finish(pr, "ab_realism", status, note, merge=True, outputs=[])

        cm = self.start_session(key, checks + [pr for pr in ab if pr not in checks], fail)
        if cm is None:
            return
        try:
            with cm as url:
                seqs = self.seqs(key)
                for pr in checks:
                    if pr.active:
                        self.check_part(pr, key, url, seqs)
                for pr in ab:
                    self.realism_part(pr, key, url, seqs)
        except SV.ServerError as exc:
            self.out(f"phase {n}: {exc}")
            status = "incomplete" if exc.reason == "deadline" else "failed"
            for pr in checks + [pr for pr in ab if pr not in checks]:
                fail(pr, status, f"server {key}: {exc.reason}")

    def check_part(self, pr: ProjectRun, key: str, url: str, seqs: int) -> None:
        if not self.can_start(S.est_calls(self.check_calls(pr), seqs)):
            self.finish(pr, "check", "incomplete", f"deadline: check ({key}) not started", merge=True, outputs=[])
            return
        steps = [(f"run {key}", S.check_run(self.tools, pr.ref, key, url, seqs)),
                 (f"preference {key}", S.preference(self.tools, pr.ref, key, url, seqs))]
        if not pr.ref.private:
            steps.append((f"style-photo test {key}", S.style_photo_test(self.tools, pr.ref, key, url)))
        slug = self.tools.model_slug(key)
        answers = pr.out / "check" / f"answers_{slug}.json"
        status, note = "ok", None
        cut = False
        for step, cmd in steps:
            rc = self.run_step(pr, "check", step, cmd)
            # Deadline cuts are read from the answers files, whatever the exit code (§2.2), after every step that
            # writes answers_<slug>.json: run and preference share it, and a preference that asks nothing (no
            # polished view, every answer reused) rewrites it with incomplete: false.
            if not step.startswith("style-photo"):
                cut = cut or self.answers_incomplete(answers)
            if rc == TIMEOUT_RC:
                status, note = "incomplete", f"timeout in {step}"
                break
            if rc != 0:
                status, note = "failed", f"{step} exit {rc}"
                break
        cut = cut or self.answers_incomplete(answers) or self.answers_incomplete(
            pr.out / "check" / "style_photo_test.json")
        if cut and status != "incomplete":
            status, note = "incomplete", f"deadline: {key} answers incomplete"
        out = [f"check/answers_{self.tools.model_slug(k)}.json" for k in self.opts.check_models]
        self.finish(pr, "check", status, note, merge=True, outputs=out)

    def realism_part(self, pr: ProjectRun, key: str, url: str, seqs: int) -> None:
        """Every pair set of ``ab/pairs_v2.json`` (realism v2, M7 §8.2): 8 calls per pair, ``null_identical`` one
        call at a time. Deadline cuts are read from ``answers_realism2_<slug>.json``."""
        counts = self.pair_counts(pr)
        if not counts:
            self.finish(pr, "ab_realism", "failed", "no pair in ab/pairs_v2.json", merge=True, outputs=[])
            return
        if not self.can_start(S.est_realism2(sum(counts.values()), counts.get(S.NULL_IDENTICAL, 0), seqs)):
            self.finish(pr, "ab_realism", "incomplete", f"deadline: realism ({key}) not started", merge=True,
                        outputs=[])
            return
        rc = self.run_step(pr, "ab_realism", f"realism2 {key}", S.realism2(self.tools, pr.ref, key, url, seqs))
        answers = pr.out / "check" / "realism" / f"answers_realism2_{self.tools.model_slug(key)}.json"
        if rc == TIMEOUT_RC or self.answers_incomplete(answers):
            self.finish(pr, "ab_realism", "incomplete", f"deadline: realism ({key}) cut", merge=True, outputs=[])
        elif rc != 0:
            self.finish(pr, "ab_realism", "failed", f"realism2 {key} exit {rc}", merge=True, outputs=[])
        else:
            self.finish(pr, "ab_realism", "ok", merge=True, outputs=[])

    # ----- phase 10: CPU, always -----------------------------------------

    def phase10(self) -> None:
        for pr in self.runs:
            if not any((pr.out / "check").glob("answers_*.json")) or "check" not in pr.records:
                continue
            self.simple_stage(pr, "combine", [("combine", S.combine(self.tools, pr.ref), None),
                                              ("calibrate", S.calibrate(self.tools, pr.ref), None)], late=True)
        combined = []
        if self.opts.ab_phase != "render":
            for pr in self.ab_runs:
                if not pr.ab_active or "ab_realism" not in pr.records:
                    continue
                if not any((pr.out / "check" / "realism").glob("answers_realism2_*.json")):
                    continue
                rec = self.simple_stage(pr, "ab_combine", [("realism2-combine",
                                                            S.realism2_combine(self.tools, pr.ref), None)], late=True)
                if rec.status == "ok":
                    combined.append(pr)
            if any(pr.look_alt for pr in combined):
                self.realism_summary(combined)
        for pr in self.runs:
            self.stage_report(pr)

    def stage_report(self, pr: ProjectRun) -> None:
        """Stage report, for every project. A project that already ended ``incomplete`` or ``failed`` before its first
        render has nothing to report (the report exits 1, ``stages.render: not_run``): a ``warning``, so the
        deadline cut stays ``incomplete`` (resumed with the same command) instead of turning into ``failed``."""
        before = pr.terminal
        t0 = time.time()
        rc = self.run_step(pr, "report", "report", S.report(self.tools, pr.ref), late=True)
        if rc == 0:
            self.finish(pr, "report", "ok")
        elif rc == TIMEOUT_RC:
            self.finish(pr, "report", "incomplete", "timeout in report")
        elif rc == 1 and before in ("incomplete", "failed") and self.report_not_rendered(pr, t0):
            self.finish(pr, "report", "warning", "no renders in this run")
        else:
            self.finish(pr, "report", S.STAGES["report"].on_failure, f"report exit {rc}")

    @staticmethod
    def report_not_rendered(pr: ProjectRun, since: float) -> bool:
        """``final/final_manifest.json`` written by this report (not an older one) says nothing was rendered."""
        path = pr.out / "final" / "final_manifest.json"
        try:
            if path.stat().st_mtime < since - 2.0:      # 2 s: coarse file system time stamps
                return False
        except OSError:
            return False
        manifest = read_json(path)
        stages = manifest.get("stages") if isinstance(manifest, dict) else None
        return isinstance(stages, dict) and stages.get("render") == "not_run"

    def realism_summary(self, combined: list) -> None:
        """``realism2-summary`` over the combined look_alt projects, with the control project's output folder when
        its combine ended ok (else no control table: the summary reports no signal)."""
        controls = self.controls_run()
        controls_out = controls.out if controls is not None and controls in combined else None
        out_dir = self.results / "realism"
        cmd = S.realism2_summary(self.tools, [pr.ref for pr in combined if pr.look_alt], controls_out, out_dir)
        log = self.results / "logs" / "realism_summary.log"
        rc, seconds = self.exec(log, cmd, late=True)
        status = "ok" if rc == 0 else ("incomplete" if rc == TIMEOUT_RC else "failed")
        note = None if rc == 0 else f"exit {rc}"
        if rc == 0 and controls_out is None:
            note = "no control project combined: the summary has no control table"
        self.job_records["realism_summary"] = {"stage": "realism_summary", "status": status, "rc": rc,
                                               "seconds": round(seconds, 1), "note": note}
        self.out(f"realism_summary {status} {seconds:.1f}s")

    # ----- phase 11: GPU tests and the run manifest -----------------------------

    @staticmethod
    def project_state(pr: ProjectRun) -> str:
        """The project's state from its project stages only: the A/B stages of a project that is also in ``--ab``
        count in the exit code on their own, not in the project's state."""
        return ST.project_state(rec for stage, rec in pr.records.items() if stage in S.PROJECT_STAGES)

    def test_lists(self) -> dict:
        public_full = [pr for pr in self.runs if not pr.ref.private]
        state = {pr.name: self.project_state(pr) for pr in self.runs}
        ok = [pr for pr in public_full if state[pr.name] == "ok"]

        def names(items):
            return " ".join(pr.name for pr in items)

        furnish = [pr for pr in ok if self.status_of(pr, "layout") in ("ok", "reused") and self.ai_rooms(pr)]
        polish = [pr for pr in ok if self.status_of(pr, "polish") in ("ok", "reused", "warning")
                  and pr.gate_decision in ("ok", "flagged")]
        gate = [pr for pr in public_full if self.status_of(pr, "gate") not in (None, "skipped")
                and any(s["name"] == "calibrate" for s in pr.parts.get("gate", []))]
        detect = [pr for pr in ok if self.status_of(pr, "detect") in ("ok", "warning")
                  and any(s["name"] == "detect" for s in pr.parts.get("detect", []))]
        done = [pr for pr in self.ab_runs if pr.ab_active and self.status_of(pr, "ab_realism") == "ok"
                and self.status_of(pr, "ab_combine") == "ok"]
        control = self.controls_run()
        selftest = any(pr.name == SELFTEST_ALIAS for pr in self.runs) and self.opts.private_selftest
        return {"RUN_TEST_PROJECTS": names(ok),
                "NEEDS_REVIEW_TEST_PROJECTS": names(pr for pr in public_full if state[pr.name] == "needs_review"),
                "RENDER_TEST_PROJECTS": names(ok), "FURNISH_TEST_PROJECTS": names(furnish),
                "CHECK_TEST_PROJECTS": names(ok), "POLISH_TEST_PROJECTS": names(polish),
                "GATE_TEST_PROJECTS": names(gate), "DETECT_TEST_PROJECTS": names(detect),
                "AB_TEST_PROJECTS": names(pr for pr in done if pr.look_alt),
                "AB_CONTROL_PROJECT": control.name if control is not None and control in done else "",
                "SELFTEST_TEST_ALIAS": SELFTEST_ALIAS if selftest else ""}

    def ai_rooms(self, pr: ProjectRun) -> int:
        building = read_json(pr.out / "building_furnished.json")
        if not isinstance(building, dict):
            return 0
        return len({f.get("room_id") for f in building.get("furniture") or [] if f.get("source") == "added_by_ai"})

    def test_env(self, lists: dict) -> dict:
        env = dict(lists)
        env.update(WENART_OUTPUTS=str(self.outputs_root), WENART_RESULTS=str(self.results),
                   WENART_PRIVATE_RESULTS=str(self.opts.private_results),
                   CHECK_MODELS=" ".join(self.opts.check_models))
        if (self.repo_root / DETECT_CALIBRATION).is_file():
            env["DETECT_CALIBRATION"] = str(self.repo_root / DETECT_CALIBRATION)
        return env

    def phase11(self) -> dict:
        """The GPU tests (full profile) after a preliminary run manifest (``final: false``) that
        ``tests/gpu/test_full_run.py`` reads; the final manifest follows the tests (``run``)."""
        lists = self.test_lists()
        self.write_manifests(lists, final=False)
        self.copy_results()
        if self.opts.smoke or not self.opts.tests:
            self.out("phase 11: no GPU tests in the smoke profile" if self.opts.smoke else "phase 11: tests off")
        else:
            self.run_tests(lists)
        return lists

    def copy_results(self) -> None:
        """One full copy of every project's small files before the GPU tests: ``test_full_run.py`` reads the
        private allow-list under ``results-private/<alias>/`` and ``full.sh``'s copy loop runs only every 300 s.
        Under the job's copy lock (``WENART_COPY_LOCK``); prints only file counts (§1.1)."""
        from wenart.run import copy as CP
        refs = [pr.ref for pr in self.runs] + [pr.ref for pr in self.ab_runs if not pr.full]
        try:
            with CP.copy_lock(os.environ.get("WENART_COPY_LOCK")):
                counts = CP.copy_results(refs)
            self.out(CP.summary_line(counts))
        except (OSError, TimeoutError) as exc:
            self.out(f"copy before the GPU tests failed: {type(exc).__name__}")

    def run_tests(self, lists: dict) -> None:
        env = self.test_env(lists)
        for group, attr, files in GPU_TEST_GROUPS:
            chosen = [f for f, keys in files if any(lists.get(k) for k in keys)]
            entry = {"group": group, "files": chosen, "rc": None, "status": "skipped",
                     "junit": None, "seconds": 0.0}
            if not chosen:
                self.out(f"GPU tests {group}: every project list is empty: skipped")
                self.tests.append(entry)
                continue
            junit = self.results / f"junit-{group}.xml"
            cmd = [getattr(self.tools, attr), "-m", "pytest", "-m", "gpu"] + chosen + [
                "-v", "-ra", f"--junitxml={junit}"]
            if "tests/gpu/test_detect.py" in chosen and "DETECT_CALIBRATION" not in env:
                # The calibration is the prep pod's (committed as results/detect/, M7 §9.2), never this job's.
                cmd += ["--deselect", "tests/gpu/test_detect.py::test_calibration_recorded"]
                entry["note"] = f"no committed {DETECT_CALIBRATION.as_posix()}: test_calibration_recorded deselected"
            rc, seconds = self.exec(self.results / "logs" / f"pytest-{group}.log", cmd, env, late=True)
            entry.update(rc=rc, status="passed" if rc == 0 else "failed", junit=junit.name,
                         seconds=round(seconds, 1))
            self.out(f"GPU tests {group}: {entry['status']} (rc {rc}) in {seconds:.0f} s")
            self.tests.append(entry)

    def compute_exit(self) -> int:
        states = [self.project_state(pr) for pr in self.runs]
        projects_ok = all(s in ("ok", "needs_review") for s in states)
        ab_ok = True
        for pr in self.ab_runs:
            for stage, rec in pr.records.items():
                if stage in S.AB_STAGES and stage not in S.AB_NOT_COUNTED and rec.status in ("failed", "incomplete"):
                    ab_ok = False
        if any(r["status"] in ("failed", "incomplete") for r in self.job_records.values()):
            ab_ok = False
        tests_ok = all(t["status"] != "failed" for t in self.tests)
        return 0 if projects_ok and ab_ok and tests_ok else 1

    def project_entry(self, pr: ProjectRun, details: bool) -> dict:
        entry = {"name": pr.name, "private": pr.ref.private, "state": self.project_state(pr)}
        if details:
            entry.update(out_dir=S.t(pr.out),
                         stages=[pr.records[s].brief() for s in S.PROJECT_STAGES if s in pr.records],
                         gate_decision=pr.gate_decision, views=pr.views or None)
            if pr.archived:
                entry["archived_outputs"] = pr.archived
        return entry

    def ab_entry(self, pr: ProjectRun) -> dict:
        entry = {"name": pr.name, "controls": pr.name == self.ab_controls, "look_alt": pr.look_alt,
                 "controls_rendered": pr.controls_needed, "dropped": pr.ab_dropped,
                 "stages": [pr.records[s].brief() for s in S.AB_STAGES + ("pipeline", "style", "assets")
                            if s in pr.records and (s in S.AB_STAGES or not pr.full)]}
        if pr.archived and not pr.full:
            entry["archived_outputs"] = pr.archived
        return entry

    def manifest(self, lists: dict, private: bool, final: bool) -> dict:
        # Public manifest: public projects with every detail, private aliases with their state only.
        # Private manifest ($JOB_DIR/results-private/): the private projects' details.
        projects = [self.project_entry(pr, details=private or not pr.ref.private)
                    for pr in self.runs if pr.ref.private or not private]
        states = [p["state"] for p in projects]
        data = {"schema_version": "0.1", "kind": "private_run_manifest" if private else "run_manifest",
                "run_id": self.run_id, "job": self.opts.job_id, "git_commit": self.commit,
                "profile": self.opts.profile, "deadline": self.deadline, "started_utc": self.started_utc,
                "finished_utc": ST.utc_now() if final else None, "final": final,
                "exit_code": self.exit_code if final else None, "projects": projects,
                "totals": {s: states.count(s) for s in ST.PROJECT_STATES}}
        if not private:
            data.update(ab_phase=self.opts.ab_phase, ab_controls=self.ab_controls,
                        ab=[self.ab_entry(pr) for pr in self.ab_runs],
                        realism_summary=self.job_records.get("realism_summary"),
                        phases=list(self.phases), servers=list(self.servers), tests=list(self.tests),
                        test_lists=lists, force=sorted(self.opts.force), gpu=self.gpu_entry())
        return data

    def gpu_entry(self) -> Optional[dict]:
        """The GPU the estimates were scaled for (None when no deadline or server needed it)."""
        if self._gpu is None and self._speed is None:
            return None
        entry = {"name": (self._gpu or {}).get("name"), "memory_mib": (self._gpu or {}).get("memory_mib")}
        if self._speed is not None:
            entry.update(speed=self._speed["speed"], speed_of=self._speed.get("matched"))
        entry["seqs"] = dict(self._seqs)
        return entry

    def write_manifests(self, lists: dict, final: bool) -> None:
        ST.write_json(self.results / "run_manifest.json", self.manifest(lists, private=False, final=final))
        if any(pr.ref.private for pr in self.runs) and self.job_dir is not None:
            ST.write_json(self.job_dir / "results-private" / "_run_manifest.json",
                          self.manifest(lists, private=True, final=final))


# --------------------------------------------------------------------------
# Entry point used by ``python -m wenart.run pod``
# --------------------------------------------------------------------------

def run_pod(opts: RunOptions, *, out: Optional[Callable[[str], None]] = None, **kwargs) -> int:
    """Run the orchestrator; every exception is caught (§1.1): with a private project in the run the
    traceback goes to ``$JOB_DIR/results-private/_logs/orchestrator.log`` and stdout only gets
    ``orchestrator error <ExceptionType>``; exit 1 (2 for bad options)."""
    out = out or (lambda line: print(line, flush=True))
    orch = None
    try:
        orch = Orchestrator(opts, out=out, **kwargs)
        return orch.run()
    except RunError as exc:
        out(f"orchestrator: {exc}")
        return 2
    except Exception as exc:  # noqa: BLE001 - the job must end with its manifests and the EXIT-trap copy
        private = bool(split_names(opts.private)) or opts.private_selftest
        if private:
            job_dir = Path(opts.job_dir) if opts.job_dir else (Path(opts.results).parent if opts.results else None)
            if job_dir is not None:
                log = job_dir / "results-private" / "_logs" / "orchestrator.log"
                log.parent.mkdir(parents=True, exist_ok=True)
                with open(log, "a", encoding="utf-8") as fh:
                    fh.write(f"[{ST.utc_now()}] {traceback.format_exc()}\n")
            out(f"orchestrator error {type(exc).__name__}")
        else:
            out(f"orchestrator error {type(exc).__name__}: {exc}")
            out(traceback.format_exc())
        if orch is not None and orch.results is not None:
            try:
                orch.exit_code = 1
                orch.write_manifests(orch.test_lists(), final=True)
            except Exception:  # noqa: BLE001 - best effort; the error above is the one that counts
                pass
        return 1
