"""The prep pod's job (docs/milestone7.md §9.2, §10): what the M7 full runs need before they start.

    python -m wenart.run.prep --results $RESULTS [--outputs /workspace/outputs-prep] [--projects "real01 ..."]
                              [--skip step,...] [--only step,...] [--no-tests] [--copy-only]
    (also ``python -m wenart.run prep ...``; run by ``scripts/jobs/prep.sh`` after the setup)

What, in this fixed order (``STEPS``; every command runs with cwd = the repo root, its output appended to
``<logs>/prep-<job>/<step>.log``):

1. ``survey``: ``wenart.assets.objaverse survey --cache $HF_HOME`` (the Objaverse metadata and candidate GLBs
   into the container-disk cache) -> ``library/survey.json``. It runs with ``HF_HUB_OFFLINE=0``; every later
   step runs with ``HF_HUB_OFFLINE=1`` (the setup downloaded the VLMs, the polish/gate models and OWLv2 before).
2. ``thumbnails``: ``objaverse thumbnails --work <prep-root>/library-work`` (Blender, Cycles on the GPU; no vLLM
   server runs yet).
3. ``judge_requests``: ``objaverse judge-requests`` -> ``library/judge/requests.json``.
4. ``detect_calibrate``: ``wenart.gate detect-calibrate --project-outs`` the M6 outputs of synthetic-01/03/04/05
   on the volume, ``--cache <prep-root>/detect-cache`` (venv-polish) -> ``detect/``.
5. ``timings``: 10 views of synthetic-04 rendered with the M7 render code from its M6 ``scene/scene.blend``
   (built with the M7 build code from its ``building_final.json`` when the blend is missing) and the 4 smoke
   polish attempts of one view, against the committed M6 times of the same cameras (RTX PRO 4500, M6 pod B)
   -> ``timing/gpu_speed.json`` (seconds per view and per forward, speeds).
6. ``pipelines``: ``wenart.ingest.pipeline <project> --out <outputs>/<p>`` for real01, synthetic-02,
   synthetic-06 and the real01 raster fixtures (exit 4: recognition questions written).
7. ``session_qwen``: vLLM Qwen with the 8-sequence probe (8 sequences and 32k context first; a server that does
   not come up is recorded as ``max_seqs`` 4 and started again with 4), then ``wenart.recognition.answers ask``
   for every project with questions and ``objaverse judge``.
8. ``session_glm``: the same with GLM.
9. ``pipeline_final``: ``pipeline --answers <out>/recognition`` (``--no-ai`` when ``answers status`` finds an
   answer missing, so it never exits 4).
10. ``library``: ``objaverse accept``, ``write-catalog --assets``, ``report`` and ``ATTRIBUTION.md``
    (``wenart.run.copy.library_attribution``) -> ``library/``.
11. ``copy``: the prep projects' small files (``wenart.run.copy.copy_project``) -> ``recognition/<p>/``
    (requests, both answer files, crops) and ``furniture/<p>/`` (building.json, report.md, debug images).
12. ``tests``: ``pytest -m gpu`` ``tests/gpu/test_recognition.py -k m7`` (``WENART_PREP_OUTPUTS``),
    ``tests/gpu/test_library.py`` (``WENART_LIBRARY``, ``WENART_ASSETS``) and ``tests/gpu/test_detect.py``
    (``DETECT_CALIBRATION``, venv-polish) -> ``tests/junit-<group>.xml``.

Deadline (``WENART_DEADLINE``, epoch seconds; ``scripts/pod_entry.sh`` sets start + max - 15 min): a download or
GPU step (``HEAVY``) starts only when now + its estimate (``EST_S``) < deadline, else it ends ``deadline``; the CPU
steps, the copy and the GPU tests always run (they take seconds or are the pod's record; their timeout is the
deadline + 10 min, like the orchestrator's late stages). The steps that watch the deadline themselves
(thumbnails, ask, judge, render, polish) exit 3 when it cuts them: the step is then ``deadline`` too.

Resume: a cut pod runs the same command again. The pipeline outputs and their answer stores stay in
``--outputs`` (answers are reused by key and input hash), the thumbnail measurements in
``<prep-root>/library-work``, the detector boxes in ``<prep-root>/detect-cache``, the timing renders and polish
attempts in ``<prep-root>/timing/<gpu>/``; the library judge answers are saved to ``<prep-root>/library-answers``
after each session and seeded from there (``objaverse judge --seed-answers``: only answers whose key and hash
match are taken), because ``$RESULTS`` is a new folder per job.

Results (``$RESULTS``, collected by ``scripts/gpu_run.py``): ``prep_manifest.json`` (written after every step:
status, exit codes, seconds and log of each step, the sessions' probe, the per-project states, and the
``proposals`` the integrator commits between the prep pod and the full runs: ``check.yaml
models.<k>.max_seqs``, ``plan.GPU_SPEED``, the detector block), ``library/``, ``detect/``,
``timing/gpu_speed.json``, ``recognition/<p>/`` (requests, both answer files, crops), ``furniture/<p>/``
(building.json, report.md, debug images) and ``tests/``.

Exit: 0 when every step ended ``ok``, ``warning`` or ``skipped`` and every GPU test group passed; 1 otherwise
(the same command resumes); 2 for bad options.

How: ``Prep`` takes the subprocess runner, the server factory (default ``wenart.run.servers.server``), the
clock and the GPU query as arguments, so ``tests/test_prep_job.py`` drives the whole job with fakes.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from wenart.run import copy as CP
from wenart.run import servers as SV
from wenart.run import stages as S
from wenart.run.projects import REPO_ROOT, ProjectError, ProjectRef, check_name

STEPS = ("survey", "thumbnails", "judge_requests", "detect_calibrate", "timings", "pipelines", "session_qwen",
         "session_glm", "pipeline_final", "library", "copy", "tests")
# Download and GPU steps: they start only when now + EST_S < deadline (seconds; §10 table, measured on nothing
# yet: the prep pod is where they are measured).
HEAVY = ("survey", "thumbnails", "detect_calibrate", "timings", "session_qwen", "session_glm")
EST_S = {"survey": 300.0, "thumbnails": 180.0, "detect_calibrate": 240.0, "timings": 420.0}
EST_CALLS_MIN_S = 120.0                    # a session starts only with room for its server start and some calls
SESSION_KEYS = {"session_qwen": "qwen", "session_glm": "glm"}     # pass 1, then pass 2 (§3.3, §9.2)
STATUSES = ("ok", "warning", "skipped", "deadline", "failed")
GOOD = ("ok", "warning", "skipped")

PREP_PROJECTS = ("real01", "synthetic-02", "synthetic-06", "real01-scan", "real01-photo")
# Where a prep project lives: the committed projects, the real01 raster fixtures (area S, §4.4), the test projects.
PROJECT_ROOTS = (Path("projects"), Path("tests") / "fixtures" / "real01_raster",
                 Path("tests") / "fixtures" / "projects")
DETECT_PROJECTS = ("synthetic-01", "synthetic-03", "synthetic-04", "synthetic-05")   # the 29 M6 hide/normal pairs
TIMING_PROJECT = "synthetic-04"
TIMING_VIEWS = 10
TIMING_RES = "1920x1080"
# The committed M6 results of synthetic-04 (M6 pod B, docs/gpu-log.md 3 Oct 2026 04:16 UTC, RTX PRO 4500
# Blackwell): the same cameras rendered and polished on the GPU that plan.GPU_SPEED counts as 1.0.
TIMING_REFERENCE = {"render": Path("results") / "renders" / TIMING_PROJECT / "render_manifest.json",
                    "polish": Path("results") / "polish" / TIMING_PROJECT / "polish_manifest.json"}
REFERENCE_GPU = "RTX PRO 4500"
REFERENCE_NOTE = "M6 pod B (docs/gpu-log.md, 2026-10-03 04:16 UTC, NVIDIA RTX PRO 4500 Blackwell)"
PROBE_SEQS = (8, 4)                        # §9.2: 8 sequences first; a server that does not come up -> 4
PROBE_RETRY_REASONS = ("early_exit", "timeout")
TEST_GROUPS = (   # (group, interpreter attribute, pytest arguments)
    ("recognition", "py", ["tests/gpu/test_recognition.py", "-k", "m7"]),
    ("library", "py", ["tests/gpu/test_library.py"]),
    ("detect", "polish_py", ["tests/gpu/test_detect.py"]),
)
LATE_S = 600.0                             # CPU steps and tests may run until the deadline + 10 min
NO_DEADLINE_TIMEOUT_S = 4 * 3600.0
MANIFEST = "prep_manifest.json"
GPU_SPEED_JSON = "gpu_speed.json"


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def split_names(text) -> list[str]:
    """``"a b"``, ``"a,b"`` or a list -> ``["a", "b"]`` (order kept, duplicates dropped)."""
    out: list[str] = []
    items = text if isinstance(text, (list, tuple)) else str(text or "").replace(",", " ").split()
    for item in items:
        for part in str(item).replace(",", " ").split():
            if part not in out:
                out.append(part)
    return out


def read_json(path) -> Optional[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, (dict, list)) else None


def write_json(path: Path, data) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def items_in(path: Path) -> int:
    """Number of request items of a ``requests.json`` (0 when missing or unreadable)."""
    data = read_json(path)
    return len(data.get("items") or []) if isinstance(data, dict) else 0


def slug(text: Optional[str]) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(text or "unknown gpu").lower()).strip("-") or "unknown-gpu"


def env_deadline() -> Optional[float]:
    text = os.environ.get("WENART_DEADLINE", "").strip()
    try:
        return float(text) if text else None
    except ValueError:
        return None


def priority_names(path: Path = REPO_ROOT / "scripts" / "gpu_run.py") -> list[str]:
    """``GPU_PRIORITY`` of ``scripts/gpu_run.py`` read with ``ast`` (the runner's network code is never imported)."""
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "GPU_PRIORITY"
                                                for t in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                return []
            return [str(v) for v in value] if isinstance(value, (list, tuple)) else []
    return []


def gpu_key(name: Optional[str]) -> Optional[str]:
    """The RunPod name of an ``nvidia-smi`` GPU name (``NVIDIA RTX PRO 6000 Blackwell Server Edition`` -> ``RTX PRO
    6000``): the longest ``GPU_PRIORITY`` name it contains as whole words (the key ``plan.GPU_SPEED`` uses)."""
    if not name:
        return None
    text = " ".join(str(name).upper().split())
    found = [k for k in priority_names() if re.search(rf"(?<![A-Z0-9]){re.escape(k.upper())}(?![A-Z0-9])", text)]
    return max(found, key=len) if found else None


def default_gpu_query() -> dict:
    """``{"name", "memory_mib"}`` of the pod's first GPU (``nvidia-smi``); ``(None, 0)`` without one."""
    try:
        proc = subprocess.run(SV.NVIDIA_SMI_QUERY, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return {"name": None, "memory_mib": 0}
    name, mem = SV.gpu_from_text(proc.stdout if proc.returncode == 0 else "")
    return {"name": name, "memory_mib": mem}


def default_runner(cmd: list, env: dict, cwd, timeout: Optional[float], log_path) -> int:
    """The orchestrator's subprocess runner (``wenart.run.scheduler.subprocess_runner``): output appended to
    ``log_path``, TERM/KILL to the process group at ``timeout``."""
    from wenart.run.scheduler import subprocess_runner   # lazy: the scheduler imports the whole run package
    return subprocess_runner(cmd, env, cwd, timeout, log_path)


def mean(values) -> Optional[float]:
    vals = [float(v) for v in values if isinstance(v, (int, float))]
    return round(sum(vals) / len(vals), 3) if vals else None


def ratio(reference: Optional[float], measured: Optional[float]) -> Optional[float]:
    """Speed = time on the reference GPU / time here (plan.GPU_SPEED: larger is faster)."""
    if not reference or not measured:
        return None
    return round(float(reference) / float(measured), 3)


# --------------------------------------------------------------------------
# Options
# --------------------------------------------------------------------------

@dataclass
class PrepOptions:
    results: Path                                          # $RESULTS (the runner collects it)
    outputs: Path = Path("/workspace/outputs-prep")        # the prep projects' pipeline outputs (persistent)
    projects: list = field(default_factory=lambda: list(PREP_PROJECTS))
    m6_outputs: Path = REPO_ROOT / "outputs"               # the M6 outputs on the volume (detector, timings)
    detect_projects: list = field(default_factory=lambda: list(DETECT_PROJECTS))
    timing_project: str = TIMING_PROJECT
    prep_root: Path = Path("/workspace/prep")              # persistent work: library-work, caches, timing renders
    assets: Path = Path("/workspace/assets")
    hf_cache: Path = Path("/opt/wenart/hf")
    logs_dir: Path = Path("/workspace/logs")
    job_dir: Optional[Path] = None
    job_id: str = "prep"
    deadline: Optional[float] = None
    py: str = sys.executable
    polish_py: str = "/opt/wenart/venv-polish/bin/python"
    render_samples: int = 128
    skip: tuple = ()
    only: tuple = ()
    tests: bool = True
    repo_root: Path = REPO_ROOT

    @property
    def library(self) -> Path:
        return Path(self.results) / "library"

    @property
    def step_logs(self) -> Path:
        return Path(self.logs_dir) / f"prep-{self.job_id}"


@dataclass
class Project:
    name: str
    project_dir: Optional[Path]           # None: not found in PROJECT_ROOTS
    out_dir: Path
    pipeline_rc: Optional[int] = None     # first pipeline of this run
    final_rc: Optional[int] = None
    complete: Optional[bool] = None       # answers of both models for every item (answers status)

    @property
    def requests(self) -> Path:
        return self.out_dir / S.RECOGNITION_DIR / "requests.json"

    def ref(self, results: Path) -> ProjectRef:
        return ProjectRef(name=self.name, private=False, project_dir=self.project_dir or self.out_dir,
                          out_dir=self.out_dir, results_dir=Path(results))


# --------------------------------------------------------------------------
# The job
# --------------------------------------------------------------------------

class Prep:
    """One prep job (module docstring). ``runner(cmd, env, cwd, timeout, log) -> rc``; ``server_factory(key,
    deadline, stats, seqs, mem_mib)`` -> a context manager yielding the base URL or raising
    ``servers.ServerError`` (default ``servers.server``); ``gpu_query() -> {"name", "memory_mib"}``."""

    def __init__(self, opts: PrepOptions, *, runner: Optional[Callable] = None,
                 server_factory: Optional[Callable] = None, clock: Callable[[], float] = time.time,
                 out: Callable[[str], None] = print, gpu_query: Optional[Callable[[], dict]] = None) -> None:
        self.opts = opts
        self.runner = runner or default_runner
        self.server_factory = server_factory
        self.clock = clock
        self.out = out
        self.gpu_query = gpu_query or default_gpu_query
        self.tools = S.Tools(py=opts.py, polish_py=opts.polish_py, assets=Path(opts.assets),
                             render_samples=opts.render_samples)
        self.offline = False                      # HF_HUB_OFFLINE=1 for every step after the survey
        self.gpu: Optional[dict] = None
        self.steps: list[dict] = []
        self.sessions: dict = {}
        self.timing: Optional[dict] = None
        self.tests: list[dict] = []
        self.started_utc = utc_now()
        self.exit_code: Optional[int] = None
        self.projects = [self.find_project(n) for n in opts.projects]
        self._current: Optional[dict] = None
        self._commit: Optional[str] = None

    # ----- helpers --------------------------------------------------------

    def find_project(self, name: str) -> Project:
        out_dir = Path(self.opts.outputs) / check_name(name)
        for root in PROJECT_ROOTS:
            folder = Path(self.opts.repo_root) / root / name
            if folder.is_dir():
                return Project(name, folder, out_dir)
        return Project(name, None, out_dir)

    def now(self) -> float:
        return float(self.clock())

    def can_start(self, estimate_s: float) -> bool:
        return self.opts.deadline is None or self.now() + float(estimate_s) < float(self.opts.deadline)

    def timeout(self, late: bool) -> float:
        if self.opts.deadline is None:
            return NO_DEADLINE_TIMEOUT_S
        left = float(self.opts.deadline) - self.now()
        return max(300.0, left + LATE_S) if late else max(60.0, left)

    def child_env(self, extra: Optional[dict] = None) -> dict:
        env = dict(os.environ)
        if self.opts.deadline is not None:
            d = float(self.opts.deadline)
            env["WENART_DEADLINE"] = str(int(d)) if d.is_integer() else str(d)
        env["HF_HOME"] = str(self.opts.hf_cache)
        env["HF_HUB_OFFLINE"] = "1" if self.offline else "0"
        env.setdefault("CHECK_MODELS", " ".join(SESSION_KEYS.values()))
        if self.opts.job_dir is not None:
            env["WENART_JOB_DIR"] = str(self.opts.job_dir)
        if extra:
            env.update({k: str(v) for k, v in extra.items()})
        return env

    def run(self, cmd: list, extra_env: Optional[dict] = None, late: bool = False, log_name: Optional[str] = None,
            what: Optional[str] = None) -> int:
        """One command of the current step; recorded in its entry (command line, rc, seconds)."""
        step = self._current or {"name": "prep", "commands": []}
        log = Path(self.opts.step_logs) / f"{log_name or step['name']}.log"
        cmd = [str(c) for c in cmd]
        t0 = self.now()
        try:
            rc = int(self.runner(cmd, self.child_env(extra_env), Path(self.opts.repo_root), self.timeout(late), log))
        except OSError as exc:
            self.out(f"prep: cannot run {cmd[0]}: {exc}")
            rc = 127
        seconds = round(max(0.0, self.now() - t0), 2)
        step.setdefault("commands", []).append({"what": what, "cmd": shlex.join(cmd), "rc": rc, "seconds": seconds})
        step["log"] = str(log)
        return rc

    def gpu_info(self) -> dict:
        if self.gpu is None:
            try:
                info = dict(self.gpu_query() or {})
            except Exception as exc:  # noqa: BLE001 - recorded, the job goes on without a GPU name
                info = {"error": f"{type(exc).__name__}: {exc}"}
            info.setdefault("name", None)
            info.setdefault("memory_mib", 0)
            info["key"] = gpu_key(info["name"])
            self.gpu = info
        return self.gpu

    def selected(self, step: str) -> Optional[str]:
        """None when the step runs, else why it is skipped (``--only`` / ``--skip``)."""
        if self.opts.only and step not in self.opts.only:
            return "not in --only"
        if step in self.opts.skip:
            return "in --skip"
        if step == "tests" and not self.opts.tests:
            return "--no-tests"
        return None

    def pending(self) -> list[Project]:
        """Projects with recognition questions: the first pipeline of this run exited 4, or (pipelines not run in
        this job: ``--skip``/``--only``) a requests.json with items from an earlier job in ``--outputs``."""
        return [p for p in self.projects
                if (p.pipeline_rc == 4 or (p.pipeline_rc is None and items_in(p.requests) > 0))]

    def seeds(self, p: Project) -> Optional[Path]:
        seeds = S.recognition_seeds(p.ref(self.opts.results), Path(self.opts.repo_root))
        return seeds if seeds is not None and seeds.is_dir() else None

    @property
    def library_seeds(self) -> Path:
        return Path(self.opts.prep_root) / "library-answers"

    def save_library_answers(self) -> int:
        """Copy the library judge answers to ``<prep-root>/library-answers`` (seeds of a resumed job)."""
        judge = self.opts.library / "judge"
        n = 0
        for f in sorted(judge.glob("answers_*.json")) if judge.is_dir() else []:
            self.library_seeds.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, self.library_seeds / f.name)
            n += 1
        return n

    # ----- the step frame -------------------------------------------------

    def step(self, name: str, fn: Callable[[dict], tuple]) -> dict:
        entry = {"name": name, "status": None, "note": None, "seconds": 0.0, "commands": [], "log": None,
                 "started_utc": utc_now()}
        self.steps.append(entry)
        why = self.selected(name)
        if why is None and name in HEAVY and not self.can_start(self.estimate(name)):
            entry.update(status="deadline", note=f"not started: the deadline leaves less than "
                                                 f"{self.estimate(name) / 60:.0f} min")
        elif why is not None:
            entry.update(status="skipped", note=why)
        else:
            self._current = entry
            t0 = self.now()
            try:
                status, note = fn(entry)
            except Exception as exc:  # noqa: BLE001 - one step's crash never stops the job
                status, note = "failed", f"{type(exc).__name__}: {exc}"
            finally:
                self._current = None
            entry.update(status=status, note=note, seconds=round(max(0.0, self.now() - t0), 1))
        self.out(f"prep {name}: {entry['status']}" + (f" ({entry['note']})" if entry["note"] else "")
                 + f" in {entry['seconds']:.0f} s")
        if name == "survey":
            self.offline = True               # the HF downloads are over: nothing is fetched behind our back
        self.write_manifest()
        return entry

    def estimate(self, name: str) -> float:
        if name in SESSION_KEYS:
            return S.est_server(SESSION_KEYS[name]) + EST_CALLS_MIN_S
        return EST_S.get(name, 60.0)

    # ----- library steps ----------------------------------------------------

    def objaverse(self, *args) -> list:
        return [self.opts.py, "-m", "wenart.assets.objaverse", *[str(a) for a in args]]

    def do_survey(self, entry: dict) -> tuple:
        rc = self.run(self.objaverse("survey", "--cache", self.opts.hf_cache, "--out", self.opts.library))
        survey = read_json(self.opts.library / "survey.json")
        n = len(survey.get("candidates") or []) if isinstance(survey, dict) else 0
        entry["candidates"] = n
        if rc != 0:
            return "failed", f"exit {rc}" + ("" if rc != 1 else ": no candidate")
        return "ok", f"{n} candidate(s)"

    def do_thumbnails(self, entry: dict) -> tuple:
        if not (self.opts.library / "survey.json").is_file():
            return "skipped", "no survey.json"
        rc = self.run(self.objaverse("thumbnails", "--out", self.opts.library, "--work",
                                     Path(self.opts.prep_root) / "library-work"))
        thumbs = read_json(self.opts.library / "thumbnails.json")
        entry["counts"] = thumbs.get("counts") if isinstance(thumbs, dict) else None
        entry["device"] = thumbs.get("device") if isinstance(thumbs, dict) else None
        if rc == 3:
            return "deadline", "cut by the deadline (a resumed job reuses the measured objects)"
        return ("ok", None) if rc == 0 else ("failed", f"exit {rc}")

    def do_judge_requests(self, entry: dict) -> tuple:
        if not (self.opts.library / "thumbnails.json").is_file():
            return "skipped", "no thumbnails.json"
        rc = self.run(self.objaverse("judge-requests", "--out", self.opts.library), late=True)
        entry["items"] = items_in(self.opts.library / "judge" / "requests.json")
        return ("ok", f"{entry['items']} sheet(s) to judge") if rc == 0 else ("failed", f"exit {rc}")

    def do_library(self, entry: dict) -> tuple:
        lib = self.opts.library
        if not (lib / "thumbnails.json").is_file():
            return "skipped", "no thumbnails.json"
        rc_accept = self.run(self.objaverse("accept", "--out", lib), late=True, what="accept")
        rc_catalog = None
        if rc_accept == 0:
            rc_catalog = self.run(self.objaverse("write-catalog", "--out", lib, "--assets", self.opts.assets),
                                  late=True, what="write-catalog")
        rc_report = self.run(self.objaverse("report", "--out", lib), late=True, what="report")
        attribution = CP.library_attribution(lib)
        catalog = read_json(lib / "catalog_objaverse.json")
        entries = catalog.get("entries") if isinstance(catalog, dict) else catalog
        entry.update(accepted_models=len(entries or []) if isinstance(entries, list) else 0,
                     attribution=attribution is not None)
        if rc_accept == 1:
            return "warning", "nothing accepted: every type stays Poly Haven or parametric (library_report.md)"
        if rc_accept != 0 or rc_catalog not in (0, None) or rc_report != 0:
            return "failed", f"accept {rc_accept}, write-catalog {rc_catalog}, report {rc_report}"
        return "ok", f"{entry['accepted_models']} model(s) in catalog_objaverse.json"

    # ----- detector, timings ------------------------------------------------

    def do_detect_calibrate(self, entry: dict) -> tuple:
        outs = [Path(self.opts.m6_outputs) / p for p in self.opts.detect_projects]
        found = [o for o in outs if o.is_dir()]
        entry["project_outs"] = [str(o) for o in found]
        if not found:
            return "failed", f"no M6 outputs of {', '.join(self.opts.detect_projects)} under {self.opts.m6_outputs}"
        rc = self.run([self.opts.polish_py, "-m", "wenart.gate", "detect-calibrate", "--project-outs", *found,
                       "--out", Path(self.opts.results) / "detect", "--cache",
                       Path(self.opts.prep_root) / "detect-cache", "--device", "cuda"])
        cal = read_json(Path(self.opts.results) / "detect" / "detector_calibration.json")
        if isinstance(cal, dict):
            entry["calibration"] = {k: cal.get(k) for k in ("usable", "t_det", "t_strong")}
        missing = [str(o) for o in outs if not o.is_dir()]
        if rc != 0:
            return "failed", f"exit {rc}"
        return ("warning", f"missing M6 outputs: {', '.join(missing)}") if missing else ("ok", None)

    def do_timings(self, entry: dict) -> tuple:
        doc = self.measure_timings()
        self.timing = doc
        entry["speed"] = doc.get("speed")
        if doc["render"].get("seconds_per_view") is None:
            return "failed", doc["render"].get("note") or "no render time measured"
        if doc["polish"].get("seconds_per_forward") is None:
            return "warning", "render timed; polish: " + str(doc["polish"].get("note") or "not timed")
        return "ok", f"speed {doc.get('speed')} vs the {REFERENCE_GPU}"

    def measure_timings(self) -> dict:
        """§9.2 timings -> ``$RESULTS/timing/gpu_speed.json`` (module docstring)."""
        o = self.opts
        gpu = self.gpu_info()
        src = Path(o.m6_outputs) / o.timing_project
        work = Path(o.prep_root) / "timing" / slug(gpu.get("name"))
        doc = {"schema_version": "0.1", "kind": "gpu_speed", "generated_utc": utc_now(),
               "gpu": {k: gpu.get(k) for k in ("name", "memory_mib", "key")}, "project": o.timing_project,
               "reference_gpu": REFERENCE_GPU, "reference_note": REFERENCE_NOTE,
               "render": {"note": None}, "polish": {"note": None}, "speed": None,
               "speed_rule": "the lower of the render and the polish speed (plan.GPU_SPEED: time on the "
                             "RTX PRO 4500 / time here; never overestimates this GPU)"}
        render, polish = doc["render"], doc["polish"]
        blend = src / "scene" / "scene.blend"
        scene_manifest = src / "scene" / "scene_manifest.json"
        if blend.is_file():
            render["scene_source"] = f"the M6 scene of {o.timing_project} (rendered with the M7 render code)"
        elif (src / "building_final.json").is_file():
            rc = self.run([o.py, "-m", "wenart.blender.cli", "build", "--building", src / "building_final.json",
                           "--style", src / "style.json", "--assets", o.assets, "--out", work / "scene",
                           "--preview-samples", str(S.PREVIEW_SAMPLES), "--camera-policy", "search", "--reuse"],
                          what="build")
            blend, scene_manifest = work / "scene" / "scene.blend", work / "scene" / "scene_manifest.json"
            render["scene_source"] = f"built with the M7 build code from the M6 building_final.json (rc {rc})"
        if not blend.is_file():
            render["note"] = f"no scene of {o.timing_project} under {o.m6_outputs}"
        reference = read_json(Path(o.repo_root) / TIMING_REFERENCE["render"])
        ref_secs = {str(e.get("camera")): e.get("seconds") for e in (reference or {}).get("renders") or []
                    if isinstance(e, dict) and not e.get("skipped") and isinstance(e.get("seconds"), (int, float))}
        scene = read_json(scene_manifest) or {}
        cams = sorted(str(c.get("name")) for c in scene.get("cameras") or [] if isinstance(c, dict) and c.get("name"))
        chosen = [c for c in cams if c in ref_secs][:TIMING_VIEWS] or cams[:TIMING_VIEWS]
        render["cameras"] = chosen
        if blend.is_file() and chosen:
            rc = self.run([o.py, "-m", "wenart.blender.cli", "render", "--scene", blend, "--out", work / "renders",
                           "--cameras", ",".join(chosen), "--samples", str(o.render_samples), "--res", TIMING_RES,
                           "--exposure", "auto", "--white-balance", "auto"], what="render")
            measured = read_json(work / "renders" / "render_manifest.json") or {}
            secs = {str(e.get("camera")): e.get("seconds") for e in measured.get("renders") or []
                    if isinstance(e, dict) and e.get("camera") in chosen and isinstance(e.get("seconds"), (int, float))}
            same = [c for c in chosen if c in secs and c in ref_secs]
            render.update(rc=rc, samples=o.render_samples, resolution=TIMING_RES, seconds=secs,
                          seconds_per_view=mean(secs.values()), device=measured.get("device"),
                          reference={"source": TIMING_REFERENCE["render"].as_posix(),
                                     "seconds": {c: ref_secs[c] for c in chosen if c in ref_secs},
                                     "seconds_per_view": mean(ref_secs[c] for c in chosen if c in ref_secs)},
                          speed=ratio(mean(ref_secs[c] for c in same), mean(secs[c] for c in same)),
                          compared_cameras=len(same))
            if rc != 0:
                render["note"] = f"render exit {rc}"
        elif blend.is_file():
            render["note"] = "the scene manifest lists no camera"
        # Polish: the 4 smoke settings on one view of the M6 renders (its own out folder; nothing in the project).
        ref_polish = read_json(Path(o.repo_root) / TIMING_REFERENCE["polish"]) or {}
        polish["reference"] = {"source": TIMING_REFERENCE["polish"].as_posix(), "device": ref_polish.get("device"),
                               "seconds_per_forward": ref_polish.get("seconds_per_forward")}
        if not chosen or not (src / "renders").is_dir() or not (src / "scene" / "scene_manifest.json").is_file():
            polish["note"] = f"no M6 renders of {o.timing_project}: polish not timed"
        else:
            rc = self.run([o.polish_py, "-m", "wenart.polish", "smoke", "--project-out", src, "--views", chosen[0],
                           "--out", work / "polish", "--previews", "none"], extra_env=S.CUDA_ALLOC, what="polish")
            pm = read_json(work / "polish" / "polish_manifest.json") or {}
            attempts = [a for v in pm.get("views") or [] for a in (v.get("attempts") or []) if isinstance(a, dict)]
            polish.update(rc=rc, view=chosen[0], attempts=len(attempts), device=pm.get("device"),
                          seconds_per_forward=pm.get("seconds_per_forward"), forwards=pm.get("forwards"),
                          load_seconds=pm.get("load_seconds"),
                          seconds_per_attempt=mean(a.get("seconds") for a in attempts),
                          speed=ratio(ref_polish.get("seconds_per_forward"), pm.get("seconds_per_forward")))
            if rc != 0:
                polish["note"] = f"polish exit {rc}"
        speeds = [s for s in (render.get("speed"), polish.get("speed")) if s]
        doc["speed"] = min(speeds) if speeds else None
        write_json(Path(o.results) / "timing" / GPU_SPEED_JSON, doc)
        write_json(work / GPU_SPEED_JSON, doc)
        return doc

    # ----- pipelines and sessions -------------------------------------------

    def do_pipelines(self, entry: dict) -> tuple:
        missing, failed, states = [], [], {}
        for p in self.projects:
            if p.project_dir is None:
                missing.append(p.name)
                states[p.name] = "missing"
                continue
            p.out_dir.mkdir(parents=True, exist_ok=True)
            p.pipeline_rc = self.run(S.pipeline(self.tools, p.ref(self.opts.results)), late=True,
                                     log_name=f"pipeline-{p.name}", what=p.name)
            states[p.name] = {0: "ok", 1: "needs_review", 4: "pending"}.get(p.pipeline_rc, "failed")
            if states[p.name] == "failed":
                failed.append(p.name)
        entry["projects"] = states
        if missing or failed:
            return "failed", "; ".join(x for x in (
                f"not found: {', '.join(missing)}" if missing else "",
                f"pipeline failed: {', '.join(failed)}" if failed else "") if x)
        return "ok", f"{len(self.pending())} project(s) with questions"

    def open_server(self, key: str, seqs: int, stats: list):
        mem = self.gpu_info().get("memory_mib") or None
        if self.server_factory is not None:
            return self.server_factory(key, self.opts.deadline, stats, seqs, mem)
        return SV.server(key, self.opts.deadline, stats=stats, seqs=seqs, mem_mib=mem,
                         logs_dir=Path(self.opts.logs_dir), job_dir=self.opts.job_dir, clock=self.clock, out=self.out,
                         spawn=self.spawn_server)

    def spawn_server(self, cmd: list, env: dict, log_path: Path):
        """``servers.popen_spawn`` with the prep's Hugging Face settings: the vLLM server reads the models from
        ``HF_HOME`` offline (every download happened in the setup, before the survey ended)."""
        env = dict(env, HF_HOME=str(self.opts.hf_cache), HF_HUB_OFFLINE="1" if self.offline else "0")
        return SV.popen_spawn(cmd, env, log_path)

    def do_session(self, entry: dict, key: str) -> tuple:
        mem = self.gpu_info().get("memory_mib") or 0
        tier = SV.server_seqs(mem)                      # no check.yaml cap: the probe measures it
        candidates = list(PROBE_SEQS) if tier >= PROBE_SEQS[0] else [tier]
        info = {"key": key, "tier": tier, "probe": tier >= PROBE_SEQS[0], "tried": [], "max_seqs": None,
                "asks": [], "judge": None}
        if not info["probe"]:
            info["note"] = f"GPU below {SV.VRAM_LARGE_MIB} MiB: no 8-sequence probe ({tier} sequences)"
        self.sessions[key] = info
        entry["session"] = info
        for i, seqs in enumerate(candidates):
            if i and not self.can_start(S.est_server(key) + EST_CALLS_MIN_S):
                info["tried"].append({"seqs": seqs, "ok": False, "reason": "deadline", "note": "not started"})
                break
            stats: list = []
            try:
                with self.open_server(key, seqs, stats) as url:
                    info["tried"].append({"seqs": seqs, "ok": True, "seconds_to_ready":
                                          (stats[-1] if stats else {}).get("seconds_to_ready")})
                    if info["probe"]:
                        info["max_seqs"] = seqs
                    self.ask_all(key, url, seqs, info)
                break
            except SV.ServerError as exc:
                info["tried"].append({"seqs": seqs, "ok": False, "reason": exc.reason, "error": str(exc)})
                self.keep_server_log(key, seqs)
                if exc.reason not in PROBE_RETRY_REASONS:
                    break
                if info["probe"] and seqs == PROBE_SEQS[0]:
                    info["max_seqs"] = PROBE_SEQS[1]    # §9.2: 8 sequences do not come up -> max_seqs 4
        self.write_manifest()
        up = [t for t in info["tried"] if t["ok"]]
        if not up:
            info["max_seqs"] = None                    # nothing came up: no measured value
            self.write_manifest()
            last = info["tried"][-1] if info["tried"] else {}
            if last.get("reason") == "deadline":
                return "deadline", "server not started before the deadline"
            return "failed", f"server did not come up ({', '.join(str(t.get('reason')) for t in info['tried'])})"
        rcs = [a["rc"] for a in info["asks"]] + ([info["judge"]["rc"]] if info["judge"] else [])
        if any(rc not in (0, 3) for rc in rcs):
            return "failed", "exit codes " + ", ".join(str(rc) for rc in rcs)
        if 3 in rcs:
            return "deadline", "cut by the deadline (answers are kept and reused by the next job)"
        return "ok", (f"{up[-1]['seqs']} sequences; {len(info['asks'])} project(s) asked"
                      + (", library judged" if info["judge"] else ""))

    def keep_server_log(self, key: str, seqs: int) -> None:
        """The vLLM log of a failed start (the next start truncates ``vllm-<key>.log``)."""
        log = Path(self.opts.logs_dir) / f"vllm-{key}.log"
        if log.is_file():
            try:
                shutil.copyfile(log, log.with_name(f"vllm-{key}-seqs{seqs}.log"))
            except OSError:
                pass

    def ask_all(self, key: str, url: str, seqs: int, info: dict) -> None:
        """Inside a session: the recognition requests of every project with questions, then the library judge."""
        for p in self.pending():
            seeds = self.seeds(p)
            rc = self.run(S.recognize(self.tools, p.ref(self.opts.results), key, url, seqs, seeds),
                          log_name=f"ask-{key}", what=p.name)
            info["asks"].append({"project": p.name, "rc": rc, "items": items_in(p.requests),
                                 "seconds": self._current["commands"][-1]["seconds"] if self._current else None,
                                 "seeded_from": str(seeds) if seeds else None})
        judge_requests = self.opts.library / "judge" / "requests.json"
        if items_in(judge_requests):
            cmd = self.objaverse("judge", "--out", self.opts.library, "--model-key", key, "--server", url,
                                 "--workers", str(seqs))
            if self.library_seeds.is_dir() and any(self.library_seeds.glob("answers_*.json")):
                cmd += ["--seed-answers", str(self.library_seeds)]
            rc = self.run(cmd, log_name=f"judge-{key}", what="library judge")
            info["judge"] = {"rc": rc, "items": items_in(judge_requests),
                             "seconds": self._current["commands"][-1]["seconds"] if self._current else None}
            self.save_library_answers()

    def do_pipeline_final(self, entry: dict) -> tuple:
        pending = self.pending()
        if not pending:
            return "skipped", "no questions"
        states, failed = {}, []
        for p in pending:
            rc_status = self.run([self.opts.py, "-m", "wenart.recognition.answers", "status",
                                  p.out_dir / S.RECOGNITION_DIR], late=True, log_name=f"pipeline_final-{p.name}",
                                 what=f"{p.name} answers status")
            p.complete = rc_status == 0
            p.final_rc = self.run(S.pipeline_final(self.tools, p.ref(self.opts.results), answers=True,
                                                   no_ai=not p.complete),
                                  late=True, log_name=f"pipeline_final-{p.name}", what=p.name)
            states[p.name] = {"rc": p.final_rc, "answers_complete": p.complete}
            if p.final_rc not in (0, 1):
                failed.append(p.name)
        entry["projects"] = states
        if failed:
            return "failed", f"pipeline_final failed: {', '.join(failed)}"
        incomplete = [p.name for p in pending if not p.complete]
        if incomplete:
            return "warning", f"answers missing (run with --no-ai): {', '.join(incomplete)}"
        return "ok", None

    # ----- copy and tests -----------------------------------------------------

    def copy_projects(self) -> dict:
        counts = {}
        for p in self.projects:
            if p.out_dir.is_dir():
                counts[p.name] = CP.copy_project(p.ref(self.opts.results))
        return counts

    def do_copy(self, entry: dict) -> tuple:
        entry["files"] = self.copy_projects()
        entry["library_answers_saved"] = self.save_library_answers()
        if CP.library_attribution(self.opts.library) is not None:
            entry["library_attribution"] = True
        return "ok", f"{sum(entry['files'].values())} file(s)"

    def test_env(self, group: str) -> dict:
        o = self.opts
        env = {"WENART_RESULTS": str(o.results), "WENART_OUTPUTS": str(o.m6_outputs)}
        if group == "recognition":
            env.update(WENART_PREP_OUTPUTS=str(o.outputs),
                       WENART_PREP_PROJECTS=" ".join(p.name for p in self.projects if p.project_dir is not None))
        elif group == "library":
            env.update(WENART_LIBRARY=str(o.library), WENART_ASSETS=str(o.assets))
        else:
            env.update(DETECT_CALIBRATION=str(Path(o.results) / "detect" / "detector_calibration.json"),
                       DETECT_TEST_PROJECTS="")
        return env

    def do_tests(self, entry: dict) -> tuple:
        failed = []
        for group, attr, args in TEST_GROUPS:
            junit = Path(self.opts.results) / "tests" / f"junit-{group}.xml"
            junit.parent.mkdir(parents=True, exist_ok=True)
            cmd = [getattr(self.opts, attr), "-m", "pytest", "-m", "gpu", *args, "-v", "-ra", "-p",
                   "no:cacheprovider", f"--junitxml={junit}"]
            rc = self.run(cmd, extra_env=self.test_env(group), late=True, log_name=f"pytest-{group}", what=group)
            status = "passed" if rc == 0 else "failed"
            self.tests.append({"group": group, "rc": rc, "status": status, "junit": f"tests/{junit.name}"})
            if rc != 0:
                failed.append(f"{group} (rc {rc})")
        return ("failed", "failed: " + ", ".join(failed)) if failed else ("ok", None)

    # ----- the job --------------------------------------------------------------

    def run_all(self) -> int:
        self.out(f"prep job {self.opts.job_id}: projects {', '.join(p.name for p in self.projects)}; deadline "
                 f"{self.opts.deadline if self.opts.deadline is not None else 'none'}")
        gpu = self.gpu_info()
        self.out(f"prep GPU: {gpu.get('name') or 'none'} ({gpu.get('memory_mib') or 0} MiB, key {gpu.get('key')})")
        table = {"survey": self.do_survey, "thumbnails": self.do_thumbnails, "judge_requests": self.do_judge_requests,
                 "detect_calibrate": self.do_detect_calibrate, "timings": self.do_timings,
                 "pipelines": self.do_pipelines, "session_qwen": lambda e: self.do_session(e, "qwen"),
                 "session_glm": lambda e: self.do_session(e, "glm"), "pipeline_final": self.do_pipeline_final,
                 "library": self.do_library, "copy": self.do_copy, "tests": self.do_tests}
        for name in STEPS:
            self.step(name, table[name])
        bad = [s["name"] for s in self.steps if s["status"] not in GOOD]
        self.exit_code = 1 if bad else 0
        self.write_manifest(final=True)
        self.out(f"prep job ends with exit code {self.exit_code}" + (f" (not ok: {', '.join(bad)})" if bad else ""))
        return self.exit_code

    def copy_only(self) -> int:
        """The EXIT trap of prep.sh: the prep projects' small files and the library seeds, nothing else."""
        counts = self.copy_projects()
        saved = self.save_library_answers()
        CP.library_attribution(self.opts.library)
        self.out(f"prep copy: {sum(counts.values())} file(s) of {len(counts)} project(s); "
                 f"{saved} library answer file(s) saved")
        return 0

    # ----- manifest ---------------------------------------------------------------

    def proposals(self) -> dict:
        """What the integrator commits between the prep pod and the full runs (§9.2)."""
        out: dict = {"check_yaml_max_seqs": {k: s["max_seqs"] for k, s in self.sessions.items()
                                             if s.get("probe") and s.get("max_seqs")},
                     "plan_gpu_speed": None, "detector": None, "catalog_objaverse": None}
        gpu = self.gpu or {}
        if self.timing and self.timing.get("speed") and gpu.get("key"):
            out["plan_gpu_speed"] = {gpu["key"]: self.timing["speed"]}
        cal = read_json(Path(self.opts.results) / "detect" / "detector_calibration.json")
        if isinstance(cal, dict):
            out["detector"] = {"usable": cal.get("usable"), "t_det": cal.get("t_det"), "t_strong": cal.get("t_strong"),
                               "file": "detect/detector_calibration.json"}
        if (self.opts.library / "catalog_objaverse.json").is_file():
            out["catalog_objaverse"] = "library/catalog_objaverse.json"
        return out

    def manifest(self, final: bool) -> dict:
        def project_entry(p: Project) -> dict:
            return {"name": p.name, "project_dir": S.t(p.project_dir) if p.project_dir else None,
                    "out_dir": str(p.out_dir), "pipeline_rc": p.pipeline_rc, "questions": items_in(p.requests),
                    "answers_complete": p.complete, "pipeline_final_rc": p.final_rc}

        return {"schema_version": "0.1", "kind": "prep_manifest", "job": self.opts.job_id,
                "git_commit": self.commit(), "started_utc": self.started_utc,
                "finished_utc": utc_now() if final else None, "final": final, "deadline": self.opts.deadline,
                "exit_code": self.exit_code if final else None, "gpu": self.gpu, "steps": self.steps,
                "projects": [project_entry(p) for p in self.projects], "sessions": self.sessions,
                "timing": self.timing, "tests": self.tests, "proposals": self.proposals(),
                "outputs": str(self.opts.outputs), "prep_root": str(self.opts.prep_root)}

    def commit(self) -> Optional[str]:
        if self._commit is None:
            self._commit = git_commit(self.opts.repo_root) or ""
        return self._commit or None

    def write_manifest(self, final: bool = False) -> None:
        try:
            write_json(Path(self.opts.results) / MANIFEST, self.manifest(final))
        except OSError as exc:
            self.out(f"prep: manifest not written: {exc}")


def git_commit(repo_root: Path) -> Optional[str]:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo_root), capture_output=True, text=True,
                              timeout=30).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _env_path(name: str, default) -> Path:
    value = os.environ.get(name, "").strip()
    return Path(value) if value else Path(default)


def parse_args(argv) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="python -m wenart.run.prep",
                                description="the prep pod's job (docs/milestone7.md §9.2); steps: " + ", ".join(STEPS))
    p.add_argument("--results", default=os.environ.get("WENART_RESULTS") or None,
                   help="$RESULTS (default $WENART_RESULTS)")
    p.add_argument("--outputs", default=None, help="pipeline outputs of the prep projects (default "
                                                   "$WENART_PREP_OUTPUTS or /workspace/outputs-prep)")
    p.add_argument("--projects", default=" ".join(PREP_PROJECTS), help="prep projects, spaces or commas")
    p.add_argument("--m6-outputs", default=None, help="M6 outputs on the volume (default $WENART_OUTPUTS or "
                                                      "<repo>/outputs)")
    p.add_argument("--detect-projects", default=" ".join(DETECT_PROJECTS))
    p.add_argument("--timing-project", default=TIMING_PROJECT)
    p.add_argument("--prep-root", default=None, help="persistent work (default $WENART_PREP_ROOT or /workspace/prep)")
    p.add_argument("--assets", default=None, help="default $WENART_ASSETS or /workspace/assets")
    p.add_argument("--hf-cache", default=None, help="default $HF_HOME or /opt/wenart/hf")
    p.add_argument("--logs", default=None, help="default $WENART_LOGS or /workspace/logs")
    p.add_argument("--job-dir", default=None, help="default $WENART_JOB_DIR")
    p.add_argument("--deadline", type=float, default=None, help="epoch seconds (default $WENART_DEADLINE)")
    p.add_argument("--polish-py", default=None, help="default $WENART_POLISH_PY or /opt/wenart/venv-polish/bin/python")
    p.add_argument("--render-samples", type=int, default=None, help="default $RENDER_SAMPLES or 128")
    p.add_argument("--skip", default="", help="steps to leave out, comma separated")
    p.add_argument("--only", default="", help="only these steps, comma separated")
    p.add_argument("--no-tests", action="store_true")
    p.add_argument("--copy-only", action="store_true", help="only copy the prep projects' files (prep.sh EXIT trap)")
    return p.parse_args(argv)


def options_from_args(args) -> PrepOptions:
    if not args.results:
        raise ValueError("--results (or WENART_RESULTS) is required")
    skip, only = tuple(split_names(args.skip)), tuple(split_names(args.only))
    unknown = [s for s in skip + only if s not in STEPS]
    if unknown:
        raise ValueError(f"unknown step(s) {', '.join(unknown)} (steps: {', '.join(STEPS)})")
    projects = split_names(args.projects)
    for name in projects + split_names(args.detect_projects) + [args.timing_project]:
        check_name(name)
    samples = args.render_samples
    if samples is None:
        try:
            samples = int(os.environ.get("RENDER_SAMPLES", "128") or 128)
        except ValueError:
            samples = 128
    job_dir = args.job_dir or os.environ.get("WENART_JOB_DIR") or None
    return PrepOptions(
        results=Path(args.results), outputs=Path(args.outputs) if args.outputs else
        _env_path("WENART_PREP_OUTPUTS", "/workspace/outputs-prep"), projects=projects,
        m6_outputs=Path(args.m6_outputs) if args.m6_outputs else _env_path("WENART_OUTPUTS", REPO_ROOT / "outputs"),
        detect_projects=split_names(args.detect_projects), timing_project=args.timing_project,
        prep_root=Path(args.prep_root) if args.prep_root else _env_path("WENART_PREP_ROOT", "/workspace/prep"),
        assets=Path(args.assets) if args.assets else _env_path("WENART_ASSETS", "/workspace/assets"),
        hf_cache=Path(args.hf_cache) if args.hf_cache else _env_path("HF_HOME", "/opt/wenart/hf"),
        logs_dir=Path(args.logs) if args.logs else _env_path("WENART_LOGS", "/workspace/logs"),
        job_dir=Path(job_dir) if job_dir else None, job_id=os.environ.get("JOB_ID") or "prep",
        deadline=args.deadline if args.deadline is not None else env_deadline(), py=sys.executable,
        polish_py=args.polish_py or os.environ.get("WENART_POLISH_PY") or "/opt/wenart/venv-polish/bin/python",
        render_samples=samples, skip=skip, only=only, tests=not args.no_tests)


def main(argv=None, **kwargs) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    try:
        opts = options_from_args(args)
    except (ValueError, ProjectError) as exc:
        print(f"prep: {exc}", file=sys.stderr)
        return 2
    job = Prep(opts, **kwargs)
    return job.copy_only() if args.copy_only else job.run_all()


if __name__ == "__main__":
    raise SystemExit(main())
