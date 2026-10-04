"""CPU tests of the Milestone 7 prep job (docs/milestone7.md §9.2, §10, §11 R "prep job static checks and order").

- scripts/jobs/prep.sh, static: shebang, ``set -Eeuo pipefail``, ERR trap (line + command), TERM -> 143, logs under
  /workspace/logs (tee), the exports, the setup (venv-polish, models incl. OWLv2, vLLM + VLMs + LibreDWG) before
  the prep, the EXIT trap that kills the vLLM pid and copies, the documented run command (RTX PRO 6000, --disk
  150, 90 min, never L4) and that the runner accepts it.
- prep.sh in a sandbox (fake interpreters): the prep's arguments and environment, the setup's parts, the EXIT
  trap's ``--copy-only``, a vLLM process left behind is stopped, this job's logs go to $RESULTS/logs.
- wenart/run/prep.py with fakes (no GPU, no server, no subprocess): the fixed step order and the commands of
  every step, survey online / everything after it offline, the 8-sequence probe and its fallback to 4, the
  deadline (heavy steps not started, exit 3 of a step), pipeline_final with --answers / --no-ai, the copy into
  $RESULTS/recognition/<p>/, the library seeds of a resumed job, the timings and gpu_speed.json, the GPU test
  environments, the manifest and its proposals, the CLI.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import stat
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import pytest

from wenart.run import prep as P
from wenart.run import servers as SV

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "scripts" / "jobs" / "prep.sh"
SETUP = ROOT / "scripts" / "pod_setup_polish.sh"
GPU_6000 = {"name": "NVIDIA RTX PRO 6000 Blackwell Server Edition", "memory_mib": 97887}
TIMING_REFERENCE = Path("wenart") / "run" / "timing_reference.json"     # the frozen M6 times (orch-5)


def _text() -> str:
    return JOB.read_text(encoding="utf-8")


def _flat() -> str:
    return re.sub(r"\\\n\s*", "", _text())


def _body(name: str) -> str:
    match = re.search(rf"^{re.escape(name)}\(\) \{{\n(.*?)^\}}", _text(), re.S | re.M)
    assert match, f"function {name} not found"
    return match.group(1)


def _gpu_run():
    spec = importlib.util.spec_from_file_location("gpu_run_prep", ROOT / "scripts" / "gpu_run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# prep.sh: static checks
# --------------------------------------------------------------------------

def test_prep_sh_conventions():
    text = _text()
    assert text.startswith("#!/usr/bin/env bash\n")
    assert "\nset -Eeuo pipefail\n" in text
    assert re.search(r"^trap 'on_error \$LINENO \"\$BASH_COMMAND\"' ERR$", text, re.M), "no ERR trap with line+command"
    assert 'on_error() { log "ERROR at line $1: $2"; exit 1; }' in text
    assert re.search(r"^trap 'exit 143' TERM$", text, re.M)
    assert re.search(r"^trap 'on_exit' EXIT$", text, re.M)
    assert os.access(JOB, os.X_OK), "prep.sh is not executable"
    assert subprocess.run(["bash", "-n", str(JOB)], capture_output=True).returncode == 0


def test_prep_sh_logs_under_workspace_logs_with_tee():
    text = _text()
    assert 'WS="${WENART_WS:-/workspace}"' in text and "LOGS=$WS/logs" in text
    assert "LOG=$LOGS/prep-$JOB.log" in text and 'mkdir -p "$LOGS"' in text
    assert 'exec > >(tee -a "$LOG") 2>&1' in text
    assert text.index('exec > >(tee -a "$LOG") 2>&1') < text.index("set_threads\n")
    logs = _body("copy_job_logs")
    assert '"$f" -nt "$START_STAMP"' in logs and 'tail -n 200 "$f"' in logs and '"$LOGS/prep-$JOB"' in logs
    for pattern in ("vllm-*.log", "setup-polish-*.log", "hf-download-*.log", "libredwg-*.log"):
        assert pattern in logs, pattern


def test_prep_sh_exports_and_thread_budget():
    text = _text()
    for line in ('export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"',
                 'export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"', "export HF_XET_HIGH_PERFORMANCE=1",
                 'export WENART_OUTPUTS="$REPO/outputs"', 'export CHECK_MODELS="${CHECK_MODELS:-qwen glm}"',
                 'FAST="${WENART_FAST:-/opt/wenart}"', 'PY="${WENART_PY:-$WS/venv/bin/python}"',
                 'POLISH_PY="${WENART_POLISH_PY:-$FAST/venv-polish/bin/python}"',
                 'PREP_OUTPUTS="${WENART_PREP_OUTPUTS:-$WS/outputs-prep}"',
                 'PREP_ROOT="${WENART_PREP_ROOT:-$WS/prep}"'):
        assert line in text, line
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS", "OPENCV_FOR_THREADS_NUM"):
        assert f"{var}=$n" in _flat(), var
    assert "(quota + period - 1) / period" in _body("cpu_budget")


def test_prep_sh_setup_then_prep_and_downloads_before_offline():
    text = _flat()
    setup = text.index("bash scripts/pod_setup_polish.sh")
    prep = text.index('"$PY" -m wenart.run.prep "${PREP_ARGS[@]}" || rc=$?')
    assert 'POLISH_RECOG_PARTS="vllm libredwg models" POLISH_MODE=final POLISH_PHASES="polish gate check tests"' in text
    assert setup < text.index("export HF_HUB_OFFLINE=0") < prep
    assert "HF_HUB_OFFLINE=1" not in text.replace("HF_HUB_OFFLINE=1 for every step", "").replace(
        "with HF_HUB_OFFLINE=1", "")                      # the prep itself switches after the survey


def test_prep_setup_plan_has_every_part_and_libredwg(tmp_path):
    """The setup the job asks for: venv-polish, the models (polish, gate, OWLv2) and the check part with LibreDWG."""
    env = dict(os.environ, WENART_WS=str(tmp_path / "ws"), WENART_FAST=str(tmp_path / "fast"),
               WENART_PY=sys.executable, POLISH_SETUP_PLAN_ONLY="1", POLISH_RECOG_PARTS="vllm libredwg models",
               POLISH_MODE="final", POLISH_PHASES="polish gate check tests")
    env.pop("CHECK_MODELS", None)
    proc = subprocess.run(["bash", str(SETUP)], capture_output=True, text=True, env=env, timeout=60)
    assert proc.returncode == 0, proc.stderr
    assert "PLAN venv=1 models=1 check=1" in proc.stdout
    assert "PLAN RECOG_SETUP_PARTS=vllm libredwg models" in proc.stdout


def test_prep_sh_exit_trap_kills_vllm_then_copies():
    on_exit = _body("on_exit")
    assert on_exit.index("kill_vllm") < on_exit.index('"$PY" -m wenart.run.prep "${PREP_ARGS[@]}" --copy-only')
    assert on_exit.index("--copy-only") < on_exit.index("copy_job_logs") and 'exit "$rc"' in on_exit
    kill = _body("kill_vllm")
    assert 'cat "$PID_FILE"' in kill and 'kill -TERM -- "-$pid"' in kill and "kill -KILL" in kill
    assert "PID_FILE=$JOB_DIR/vllm.pid" in _text()


def test_prep_sh_documented_run_command():
    lines = _text().splitlines()
    i = next(n for n, ln in enumerate(lines) if "gpu_run.py run" in ln)
    command = " ".join(lines[i:i + 2])
    assert "--job scripts/jobs/prep.sh" in command and "--gpu 'RTX PRO 6000'" in command
    assert "--disk 150" in command and "--max-minutes 90" in command
    grace = re.search(r"--grace (\d+)", command)
    assert grace and int(grace.group(1)) < 900
    assert "L4" not in command and "never L4" in _text()
    gpu_run = _gpu_run()
    assert gpu_run.JOB_RE.match("scripts/jobs/prep.sh") and gpu_run.GPU_PRIORITY[0] == "RTX PRO 6000"
    # §10: 90 min at $2.09/h = $3.14 stays under the $5-per-action limit without the user's OK.
    assert gpu_run.action_price_limit(90) >= 2.09 and 2.09 * 90 / 60 == pytest.approx(3.135)


def test_prep_sh_env_knobs_reach_the_prep():
    text = _flat()
    for knob, flag in (("PREP_PROJECTS", "--projects"), ("PREP_SKIP", "--skip"), ("PREP_ONLY", "--only")):
        assert f'PREP_ARGS+=({flag} "${knob}")' in text, knob
    assert 'PREP_ARGS=(--results "$RESULTS" --outputs "$PREP_OUTPUTS" --prep-root "$PREP_ROOT")' in text


def test_prep_sh_header_documents_targeted_library_reruns():
    """orch-3: the header says where the library work lives (the persistent prep root, $RESULTS/library is a copy)
    and that a targeted library re-run on a new pod needs survey (the accepted GLBs are on the container disk)."""
    header = " ".join(ln.lstrip("#").strip() for ln in _text().splitlines() if ln.startswith("#"))
    assert "needs the library work of an earlier job in /workspace/prep/library" in header
    assert "on a new pod add survey" in header and "PREP_ONLY=survey,session_qwen,session_glm,library" in header
    assert "$RESULTS/library is its copy" in header


# --------------------------------------------------------------------------
# prep.sh in a sandbox
# --------------------------------------------------------------------------

FAKE_PY = r'''#!__PYTHON__
"""Fake interpreter for prep.sh tests: records the call; the prep can leave a vLLM process behind."""
import json, os, subprocess, sys, time
from pathlib import Path

argv = sys.argv[1:]
if argv[:1] in (["-c"], ["-"]):
    os.execv("__PYTHON__", ["__PYTHON__"] + argv)
KEYS = ("HF_HUB_OFFLINE", "HF_HOME", "WENART_BLENDER", "WENART_OUTPUTS", "CHECK_MODELS", "WENART_JOB_DIR",
        "WENART_RESULTS", "WENART_POLISH_PY", "WENART_ASSETS", "WENART_LOGS", "RENDER_SAMPLES", "WENART_DEADLINE",
        "WENART_PREP_OUTPUTS", "WENART_PREP_ROOT", "OMP_NUM_THREADS", "WENART_CPU_THREADS", "JOB_ID")
rec = {"argv": argv, "cwd": os.getcwd(), "env": {k: os.environ.get(k) for k in KEYS}, "t": time.time()}
if argv[:3] == ["-m", "wenart.run.prep", "--results"] and "--copy-only" not in argv:
    logs = Path(os.environ["WENART_LOGS"])
    (logs / "vllm-qwen.log").write_text("".join(f"v{i}\n" for i in range(300)))
    step_logs = logs / f"prep-{os.environ['JOB_ID']}"
    step_logs.mkdir(parents=True, exist_ok=True)
    (step_logs / "survey.log").write_text("survey ok\n")
    if os.environ.get("FAKE_VLLM") == "1":
        p = subprocess.Popen(["sleep", "300"], start_new_session=True, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        Path(os.environ["WENART_JOB_DIR"], "vllm.pid").write_text(f"{p.pid}\n")
        rec["vllm_pid"] = p.pid
with open(os.environ["FAKE_CALLS"], "a") as fh:
    fh.write(json.dumps(rec) + "\n")
if argv[:2] == ["-m", "wenart.run.prep"] and "--copy-only" not in argv:
    print("prep: fake run done")
    sys.exit(int(os.environ.get("FAKE_PREP_RC", "0")))
'''

FAKE_SETUP = """#!/usr/bin/env bash
echo "SETUP POLISH_MODE=${POLISH_MODE:-} POLISH_PHASES=${POLISH_PHASES:-} RECOG=${POLISH_RECOG_PARTS:-} HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-unset} CHECK_MODELS=$CHECK_MODELS" >> "$FAKE_SETUP_LOG"
exit "${FAKE_SETUP_RC:-0}"
"""


def _exe(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


class Box:
    def __init__(self, tmp_path: Path):
        self.tmp = tmp_path
        self.ws = tmp_path / "ws"
        self.logs = self.ws / "logs"
        self.results = tmp_path / "results"
        self.job_dir = tmp_path / "job"
        self.calls_log = tmp_path / "calls.jsonl"
        self.setup_log = tmp_path / "setup.log"
        self.py = _exe(tmp_path / "venv" / "bin" / "python", FAKE_PY.replace("__PYTHON__", sys.executable))
        _exe(self.ws / "repo" / "scripts" / "pod_setup_polish.sh", FAKE_SETUP)
        cgroup = tmp_path / "cgroup"
        cgroup.mkdir()
        (cgroup / "cpu.max").write_text("300000 100000\n")          # 3 CPUs
        self.logs.mkdir(parents=True)
        old = self.logs / "vllm-glm.log"                               # an earlier pod's log
        old.write_text("old\n")
        t = time.time() - 3600
        os.utime(old, (t, t))
        self.env = {"PATH": os.environ["PATH"], "HOME": str(tmp_path), "LANG": "C.UTF-8",
                    "WENART_WS": str(self.ws), "WENART_FAST": str(tmp_path / "fast"), "WENART_PY": str(self.py),
                    "WENART_RESULTS": str(self.results), "WENART_JOB_DIR": str(self.job_dir), "JOB_ID": "test",
                    "WENART_CGROUP": str(cgroup), "FAKE_CALLS": str(self.calls_log),
                    "FAKE_SETUP_LOG": str(self.setup_log), "WENART_DEADLINE": "1999999999"}

    def run(self, timeout=120, **env) -> subprocess.CompletedProcess:
        run_env = dict(self.env)
        run_env.update({k: str(v) for k, v in env.items()})
        proc = subprocess.run(["bash", str(JOB)], capture_output=True, text=True, env=run_env, timeout=timeout)
        self.output = proc.stdout + proc.stderr
        return proc

    def calls(self) -> list[dict]:
        if not self.calls_log.is_file():
            return []
        return [json.loads(ln) for ln in self.calls_log.read_text().splitlines() if ln.strip()]


def _pid_gone(pid: int) -> bool:
    try:
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (FileNotFoundError, IndexError):
        return True
    return state == "Z"


def test_sandbox_prep_run(tmp_path):
    box = Box(tmp_path)
    proc = box.run(PREP_PROJECTS="real01 synthetic-06", PREP_SKIP="timings", FAKE_VLLM="1", FAKE_PREP_RC="1")
    assert proc.returncode == 1, box.output                         # the prep's exit code
    calls = box.calls()
    main = [c for c in calls if c["argv"][:2] == ["-m", "wenart.run.prep"] and "--copy-only" not in c["argv"]]
    assert len(main) == 1
    prep = main[0]
    outputs, root = str(box.ws / "outputs-prep"), str(box.ws / "prep")
    assert prep["argv"][2:] == ["--results", str(box.results), "--outputs", outputs, "--prep-root", root,
                                "--projects", "real01 synthetic-06", "--skip", "timings"]
    env = prep["env"]
    assert env["HF_HUB_OFFLINE"] == "0" and env["HF_HOME"] == str(tmp_path / "fast" / "hf")
    assert env["WENART_BLENDER"] == str(box.ws / "tools" / "blender" / "blender")
    assert env["WENART_OUTPUTS"] == str(box.ws / "repo" / "outputs") and env["CHECK_MODELS"] == "qwen glm"
    assert env["WENART_POLISH_PY"] == str(tmp_path / "fast" / "venv-polish" / "bin" / "python")
    assert env["WENART_PREP_OUTPUTS"] == outputs and env["WENART_PREP_ROOT"] == root
    assert env["WENART_DEADLINE"] == "1999999999" and env["OMP_NUM_THREADS"] == "3" == env["WENART_CPU_THREADS"]
    assert prep["cwd"] == str(box.ws / "repo")
    assert box.setup_log.read_text().strip() == (
        "SETUP POLISH_MODE=final POLISH_PHASES=polish gate check tests RECOG=vllm libredwg models "
        "HF_HUB_OFFLINE=unset CHECK_MODELS=qwen glm")
    # The EXIT trap: the vLLM left behind is stopped, then one copy-only call with the same arguments.
    copy = [c for c in calls if "--copy-only" in c["argv"]]
    assert len(copy) == 1 and copy[0]["argv"][2:-1] == prep["argv"][2:] and copy[0]["t"] >= prep["t"]
    deadline = time.time() + 10
    while not _pid_gone(prep["vllm_pid"]) and time.time() < deadline:
        time.sleep(0.2)
    assert _pid_gone(prep["vllm_pid"]) and not (box.job_dir / "vllm.pid").exists()
    assert "stopping vllm (pid" in box.output
    # This job's logs (not the earlier pod's) go to $RESULTS/logs; the step logs to logs/prep/.
    assert sorted(p.name for p in (box.results / "logs").iterdir()) == ["prep", "vllm-qwen.log"]
    assert len((box.results / "logs" / "vllm-qwen.log").read_text().splitlines()) == 200
    assert (box.results / "logs" / "prep" / "survey.log").read_text() == "survey ok\n"
    assert (box.results / "prep-test.log").is_file()
    log = (box.logs / "prep-test.log").read_text()
    assert "CPU budget: 3 thread(s) per process" in log and "prep exit 1" in log
    assert "job test ends with exit code 1" in log


def test_sandbox_setup_failure_is_a_warning(tmp_path):
    box = Box(tmp_path)
    proc = box.run(FAKE_SETUP_RC="1")
    assert proc.returncode == 0, box.output
    assert "warning: pod_setup_polish.sh exit 1" in box.output
    prep = [c for c in box.calls() if c["argv"][:2] == ["-m", "wenart.run.prep"] and "--copy-only" not in c["argv"]]
    assert prep and "--projects" not in prep[0]["argv"]              # the prep's own default list


# --------------------------------------------------------------------------
# wenart/run/prep.py with fakes
# --------------------------------------------------------------------------

class Clock:
    def __init__(self, t: float = 1_000_000.0):
        self.t = t

    def __call__(self) -> float:
        return self.t


def _label(cmd: list) -> str:
    """A short name of a command line (the module and its sub-command, the project or the model key)."""
    if "-m" not in cmd:
        return " ".join(cmd)
    mod = cmd[cmd.index("-m") + 1]
    rest = cmd[cmd.index("-m") + 2:]
    if mod == "wenart.assets.objaverse":
        if rest[0] == "judge":
            return f"objaverse judge {rest[rest.index('--model-key') + 1]}"
        return f"objaverse {rest[0]}"
    if mod == "wenart.gate":
        return f"gate {rest[0]}"
    if mod == "wenart.blender.cli":
        return f"blender {rest[0]}"
    if mod == "wenart.polish":
        return f"polish {rest[0]}"
    if mod == "wenart.ingest.pipeline":
        return ("pipeline_final " if "--answers" in rest else "pipeline ") + Path(rest[rest.index("--out") + 1]).name
    if mod == "wenart.recognition.answers":
        project = Path(rest[1]).parent.name
        if rest[0] == "ask":
            return f"ask {rest[rest.index('--model-key') + 1]} {project}"
        return f"status {project}"
    if mod == "pytest":
        return "pytest " + next(a for a in rest if a.startswith("tests/gpu/"))
    return mod


class World:
    """The fake pod: a repo root, M6 outputs, a runner that writes what the real CLIs write, a server factory."""

    def __init__(self, tmp_path: Path, *, pipeline_rc=None, status_rc=None, rc=None, server_fail=None,
                 step_s: float = 1.0, gpu=GPU_6000, projects=("real01", "synthetic-02", "synthetic-06", "real01-scan")):
        self.tmp = tmp_path
        self.repo = tmp_path / "repo"
        self.results = tmp_path / "results"
        self.outputs = tmp_path / "outputs-prep"
        self.m6 = tmp_path / "m6"
        self.prep_root = tmp_path / "prep"
        self.logs = tmp_path / "logs"
        self.assets = tmp_path / "assets"
        self.clock = Clock()
        self.events: list = []
        self.calls: list = []
        self.lines: list = []
        self.pipeline_rc = {"real01": 4, "synthetic-02": 4, "synthetic-06": 0, "real01-scan": 4,
                            **(pipeline_rc or {})}
        self.status_rc = status_rc or {}
        self.rc = rc or {}
        self.server_fail = server_fail or {}
        self.judge_answers: dict = {}            # key -> fn(library) writing complete judge answers
        self.second_round: set = set()           # projects whose pipeline_final exits 4 without --no-ai
        self.step_s = step_s
        self.gpu = dict(gpu)
        for name in projects:
            root = "projects" if not name.startswith("real01-") else "tests/fixtures/real01_raster"
            (self.repo / root / name).mkdir(parents=True)
        (self.repo / "results" / "recognition" / "real01").mkdir(parents=True)     # committed seeds of real01
        for p in P.DETECT_PROJECTS:
            (self.m6 / p).mkdir(parents=True)
        self.timing_fixture()

    # -- the M6 outputs of synthetic-04 and the committed M6 reference times
    def timing_fixture(self, blend: bool = True) -> None:
        src = self.m6 / "synthetic-04"
        cams = [f"cam_r_{i:02d}" for i in range(12)]
        (src / "scene").mkdir(parents=True, exist_ok=True)
        (src / "renders").mkdir(parents=True, exist_ok=True)
        if blend:
            (src / "scene" / "scene.blend").write_bytes(b"blend")
        (src / "scene" / "scene_manifest.json").write_text(json.dumps({"cameras": [{"name": c} for c in cams]}))
        (src / "building_final.json").write_text("{}")
        (src / "style.json").write_text("{}")
        # The frozen M6 reference (wenart/run/timing_reference.json of the fake repo). cam_r_00 has no reference
        # time: the first 10 cameras with one are cam_r_01 .. cam_r_10.
        self.timing_reference({"render": {"device": "OPTIX", "seconds": {c: 6.0 for c in cams[1:]}},
                               "polish": {"device": "NVIDIA RTX PRO 4500 Blackwell", "seconds_per_forward": 1.0}})

    def timing_reference(self, parts: dict, gpu: str = "NVIDIA RTX PRO 4500 Blackwell") -> Path:
        doc = {"schema_version": "0.1", "kind": "timing_reference", "project": "synthetic-04", "gpu": gpu,
               "gpu_key": "RTX PRO 4500", "pod_id": "pxy56z9yyehx1t", "pod_note": "M6 pod B",
               "source_commit": "0cfcea04f0681224e826021bd526b0bc42794a59", **parts}
        return P.write_json(self.repo / TIMING_REFERENCE, doc)

    def opts(self, **kw) -> P.PrepOptions:
        base = dict(results=self.results, outputs=self.outputs, projects=list(self.pipeline_rc)[:4],
                    m6_outputs=self.m6, prep_root=self.prep_root, assets=self.assets, hf_cache=self.tmp / "hf",
                    logs_dir=self.logs, job_dir=self.tmp / "job", job_id="t1", deadline=None, py="/venv/python",
                    polish_py="/fast/venv-polish/python", repo_root=self.repo)
        base.update(kw)
        return P.PrepOptions(**base)

    def prep(self, **kw) -> P.Prep:
        return P.Prep(self.opts(**kw), runner=self.runner, server_factory=self.server, clock=self.clock,
                      out=self.lines.append, gpu_query=lambda: dict(self.gpu))

    def labels(self) -> list[str]:
        return [e[1] if e[0] == "run" else f"{e[0]} {e[1]} {e[2]}" if e[0] == "start" else f"stop {e[1]}"
                for e in self.events]

    # -- the fake runner
    def runner(self, cmd, env, cwd, timeout, log):
        Path(log).parent.mkdir(parents=True, exist_ok=True)
        with open(log, "a") as fh:
            fh.write(" ".join(cmd) + "\n")
        label = _label(cmd)
        self.calls.append({"cmd": cmd, "env": env, "label": label, "timeout": timeout, "log": str(log),
                           "t": self.clock.t})
        self.events.append(("run", label))
        rc = self.write(cmd, label)
        self.clock.t += self.step_s
        return self.rc.get(label, rc)

    def write(self, cmd: list, label: str) -> int:
        def arg(flag):
            return cmd[cmd.index(flag) + 1]

        lib = Path(arg("--out")) if label.startswith("objaverse ") else None

        if label == "objaverse survey":
            P.write_json(lib / "survey.json", {"candidates": [{"uid": "u1"}, {"uid": "u2"}]})
        elif label == "objaverse thumbnails":
            P.write_json(lib / "thumbnails.json", {"counts": {"rendered": 2}, "device": "OPTIX"})
        elif label == "objaverse judge-requests":
            P.write_json(lib / "judge" / "requests.json", {"items": [{"key": "u1"}, {"key": "u2"}]})
        elif label.startswith("objaverse judge "):
            key = label.split()[-1]
            if key in self.judge_answers:                 # schema-valid answers of every item (the real store)
                self.judge_answers[key](lib)
            else:
                P.write_json(lib / "judge" / f"answers_{key}.json", {"answers": {}})
        elif label == "objaverse accept":
            P.write_json(lib / "accepted.json", {"accepted": ["u1"]})
        elif label == "objaverse write-catalog":
            P.write_json(lib / "catalog_objaverse.json", {"entries": [
                {"id": "objaverse_u1", "uid": "u1", "type": "sofa", "licence": "CC-BY-4.0",
                 "attribution": '"Sofa" by A (https://sketchfab.com/3d-models/u1), CC BY 4.0'}]})
        elif label == "objaverse report":
            (lib / "library_report.md").write_text("# library\n")
        elif label == "gate detect-calibrate":
            P.write_json(Path(arg("--out")) / "detector_calibration.json",
                         {"usable": True, "t_det": 0.3, "t_strong": 0.6})
        elif label == "blender build":
            out = Path(arg("--out"))
            out.mkdir(parents=True, exist_ok=True)
            (out / "scene.blend").write_bytes(b"blend")
            P.write_json(out / "scene_manifest.json", {"cameras": [{"name": f"cam_r_{i:02d}"} for i in range(12)]})
        elif label == "blender render":
            cams = arg("--cameras").split(",")
            P.write_json(Path(arg("--out")) / "render_manifest.json", {"device": "OPTIX", "renders": [
                {"camera": c, "seconds": 3.0} for c in cams]})
        elif label == "polish smoke":
            P.write_json(Path(arg("--out")) / "polish_manifest.json", {
                "device": "NVIDIA RTX PRO 6000", "seconds_per_forward": 0.8, "forwards": 12, "load_seconds": 40,
                "views": [{"camera": arg("--views"), "attempts": [{"seconds": 4.0}] * 4}]})
        elif label.startswith("pipeline "):
            name = label.split()[1]
            out = Path(arg("--out"))
            rc = self.pipeline_rc[name]
            P.write_json(out / "building.json", {"id": name})
            (out / "report.md").write_text("# report\n")
            if rc == 4:
                rec = out / "recognition"
                P.write_json(rec / "requests.json", {"items": [{"key": "sym_L0_1"}, {"key": "sym_L0_2"}]})
                (rec / "crops").mkdir(parents=True, exist_ok=True)
                (rec / "crops" / "sym_L0_1_ctx.png").write_bytes(b"png")
            return rc
        elif label.startswith("ask "):
            _, key, _project = label.split()
            P.write_json(Path(cmd[cmd.index("ask") + 1]) / f"answers_{key}.json", {"answers": {}})
        elif label.startswith("status "):
            return self.status_rc.get(label.split()[1], 0)
        elif label.startswith("pipeline_final "):
            name = label.split()[1]
            out = Path(arg("--out"))
            if name in self.second_round and "--no-ai" not in cmd:
                # The answers opened new questions (a raster page's second round): exit 4 although complete.
                P.write_json(out / "building.json", {"id": name, "stage": "final", "no_ai": False})
                return 4
            P.write_json(out / "building.json", {"id": name, "stage": "final", "no_ai": "--no-ai" in cmd})
            return 0
        return 0

    # -- the fake vLLM server
    def server(self, key, deadline, stats, seqs, mem_mib):
        @contextmanager
        def cm():
            self.events.append(("start", key, seqs))
            reason = self.server_fail.get((key, seqs))
            if reason:
                stats.append({"key": key, "seqs": seqs, "ok": False})
                raise SV.ServerError(key, reason, f"fake {reason}")
            stats.append({"key": key, "seqs": seqs, "seconds_to_ready": 42.0, "ok": True})
            try:
                yield "http://127.0.0.1:8001/v1"
            finally:
                self.events.append(("stop", key))
        return cm()

    def manifest(self) -> dict:
        return json.loads((self.results / P.MANIFEST).read_text())

    def steps(self) -> dict:
        return {s["name"]: s for s in self.manifest()["steps"]}

    @staticmethod
    def manifest_of(results: Path) -> dict:
        return json.loads((Path(results) / P.MANIFEST).read_text())

    def steps_of(self, results: Path) -> dict:
        return {s["name"]: s for s in self.manifest_of(results)["steps"]}

    def call(self, label: str) -> dict:
        return next(c for c in self.calls if c["label"] == label)


def test_full_prep_runs_every_step_in_the_fixed_order(tmp_path):
    w = World(tmp_path)
    assert w.prep().run_all() == 0, w.lines
    assert [s["name"] for s in w.manifest()["steps"]] == list(P.STEPS)
    assert {s["name"]: s["status"] for s in w.manifest()["steps"]} == {name: "ok" for name in P.STEPS}
    assert w.labels() == [
        "objaverse survey", "objaverse thumbnails", "objaverse judge-requests", "gate detect-calibrate",
        "blender render", "polish smoke",
        "pipeline real01", "pipeline synthetic-02", "pipeline synthetic-06", "pipeline real01-scan",
        "start qwen 8", "ask qwen real01", "ask qwen synthetic-02", "ask qwen real01-scan", "objaverse judge qwen",
        "stop qwen",
        "start glm 8", "ask glm real01", "ask glm synthetic-02", "ask glm real01-scan", "objaverse judge glm",
        "stop glm",
        "status real01", "pipeline_final real01", "status synthetic-02", "pipeline_final synthetic-02",
        "status real01-scan", "pipeline_final real01-scan",
        "objaverse accept", "objaverse write-catalog", "objaverse report",
        "pytest tests/gpu/test_recognition.py", "pytest tests/gpu/test_library.py", "pytest tests/gpu/test_detect.py"]


def test_commands_of_every_step(tmp_path):
    w = World(tmp_path)
    w.prep().run_all()
    lib = str(w.prep_root / "library")              # the persistent library work folder (orch-3)
    assert w.call("objaverse survey")["cmd"] == ["/venv/python", "-m", "wenart.assets.objaverse", "survey",
                                                 "--cache", str(tmp_path / "hf"), "--out", lib]
    thumbs = w.call("objaverse thumbnails")["cmd"][3:]
    assert thumbs == ["thumbnails", "--out", lib, "--work", str(w.prep_root / "library-work")]
    det = w.call("gate detect-calibrate")["cmd"]
    assert det[:4] == ["/fast/venv-polish/python", "-m", "wenart.gate", "detect-calibrate"]
    assert det[4:] == (["--project-outs"] + [str(w.m6 / p) for p in P.DETECT_PROJECTS]
                       + ["--out", str(w.results / "detect"), "--cache", str(w.prep_root / "detect-cache"),
                          "--device", "cuda"])
    pipe = w.call("pipeline real01")["cmd"]
    assert pipe == ["/venv/python", "-m", "wenart.ingest.pipeline", str(w.repo / "projects" / "real01"), "--out",
                    str(w.outputs / "real01")]
    raster = w.repo / "tests" / "fixtures" / "real01_raster" / "real01-scan"
    assert w.call("pipeline real01-scan")["cmd"][3] == str(raster)
    ask = w.call("ask qwen real01")["cmd"]
    assert ask == ["/venv/python", "-m", "wenart.recognition.answers", "ask", str(w.outputs / "real01" / "recognition"),
                   "--model-key", "qwen", "--server", "http://127.0.0.1:8001/v1", "--workers", "8", "--seed-answers",
                   str(w.repo / "results" / "recognition" / "real01")]
    assert "--seed-answers" not in w.call("ask qwen synthetic-02")["cmd"]          # nothing committed for it
    judge = w.call("objaverse judge qwen")["cmd"]
    assert judge[3:] == ["judge", "--out", lib, "--model-key", "qwen", "--server", "http://127.0.0.1:8001/v1",
                         "--workers", "8"]
    # The judge answers live in the persistent library folder (a resumed job asks only what is missing there).
    assert w.call("objaverse judge glm")["cmd"][3:] == ["judge", "--out", lib, "--model-key", "glm", "--server",
                                                        "http://127.0.0.1:8001/v1", "--workers", "8"]
    final = w.call("pipeline_final real01")["cmd"]
    assert final == pipe + ["--answers", str(w.outputs / "real01" / "recognition")]
    assert w.call("objaverse write-catalog")["cmd"][3:] == ["write-catalog", "--out", lib, "--assets", str(w.assets)]
    assert w.call("pytest tests/gpu/test_detect.py")["cmd"][:3] == ["/fast/venv-polish/python", "-m", "pytest"]
    assert w.call("pytest tests/gpu/test_recognition.py")["cmd"][3:8] == ["-m", "gpu", "tests/gpu/test_recognition.py",
                                                                          "-k", "m7"]
    # Every step logs under <logs>/prep-<job>/.
    assert {Path(c["log"]).parent for c in w.calls} == {w.logs / "prep-t1"}
    assert (w.logs / "prep-t1" / "survey.log").read_text().startswith("/venv/python -m wenart.assets.objaverse survey")


def test_survey_downloads_then_everything_runs_offline(tmp_path):
    w = World(tmp_path)
    w.prep().run_all()
    assert w.calls[0]["label"] == "objaverse survey" and w.calls[0]["env"]["HF_HUB_OFFLINE"] == "0"
    assert all(c["env"]["HF_HUB_OFFLINE"] == "1" for c in w.calls[1:])
    assert {c["env"]["HF_HOME"] for c in w.calls} == {str(tmp_path / "hf")}
    # Skipping the survey still switches to offline for the rest.
    w2 = World(tmp_path / "b")
    w2.prep(skip=("survey",)).run_all()
    assert w2.calls and all(c["env"]["HF_HUB_OFFLINE"] == "1" for c in w2.calls)


def test_the_8_sequence_probe_falls_back_to_4(tmp_path):
    w = World(tmp_path, server_fail={("qwen", 8): "early_exit"})
    w.logs.mkdir(parents=True)
    (w.logs / "vllm-qwen.log").write_text("CUDA out of memory\n")
    assert w.prep().run_all() == 0
    labels = w.labels()
    assert labels[labels.index("start qwen 8") + 1] == "start qwen 4"
    assert w.call("ask qwen real01")["cmd"][-3:-2] == ["4"]                   # --workers 4 ... --seed-answers
    assert w.call("objaverse judge qwen")["cmd"][-1] == "4"
    session = w.manifest()["sessions"]["qwen"]
    assert [(t["seqs"], t["ok"]) for t in session["tried"]] == [(8, False), (4, True)]
    assert session["tried"][0]["reason"] == "early_exit" and session["max_seqs"] == 4
    assert w.manifest()["proposals"]["check_yaml_max_seqs"] == {"qwen": 4, "glm": 8}
    assert (w.logs / "vllm-qwen-seqs8.log").read_text() == "CUDA out of memory\n"   # the failed start's log kept


def test_a_server_that_never_comes_up_fails_the_session_but_not_the_job_order(tmp_path):
    w = World(tmp_path, server_fail={("glm", 8): "early_exit", ("glm", 4): "timeout"}, status_rc={
        "real01": 1, "synthetic-02": 1, "real01-scan": 1})
    assert w.prep().run_all() == 1
    steps = w.steps()
    assert steps["session_glm"]["status"] == "failed" and "early_exit, timeout" in steps["session_glm"]["note"]
    assert w.manifest()["sessions"]["glm"]["max_seqs"] is None
    assert w.manifest()["proposals"]["check_yaml_max_seqs"] == {"qwen": 8}
    # pipeline_final still runs, with --no-ai (an answer is missing), so it never exits 4.
    assert w.call("pipeline_final real01")["cmd"][-1] == "--no-ai"
    assert steps["pipeline_final"]["status"] == "warning"
    assert [s["name"] for s in w.manifest()["steps"]] == list(P.STEPS)


def test_no_probe_below_80_gb(tmp_path):
    w = World(tmp_path, gpu={"name": "NVIDIA RTX PRO 4500 Blackwell", "memory_mib": 32607})
    w.prep().run_all()
    assert "start qwen 2" in w.labels() and "start qwen 8" not in w.labels()
    session = w.manifest()["sessions"]["qwen"]
    assert session["probe"] is False and session["max_seqs"] is None and "no 8-sequence probe" in session["note"]
    assert w.manifest()["proposals"]["check_yaml_max_seqs"] == {}


def test_deadline_stops_heavy_steps_and_lets_cpu_steps_and_tests_run(tmp_path):
    w = World(tmp_path, step_s=100.0)
    deadline = w.clock.t + 500.0
    assert w.prep(deadline=deadline).run_all() == 1
    status = {name: s["status"] for name, s in w.steps().items()}
    # survey (300 s) at t+0 and thumbnails (180 s) at t+100 fit; detect_calibrate (240 s) at t+300 does not.
    assert status["survey"] == "ok" and status["thumbnails"] == "ok" and status["judge_requests"] == "ok"
    assert status["detect_calibrate"] == "deadline" and status["timings"] == "deadline"
    assert status["session_qwen"] == "deadline" and status["session_glm"] == "deadline"
    assert "not started" in w.steps()["session_qwen"]["note"]
    assert status["pipelines"] == "ok" and status["copy"] == "ok" and status["tests"] == "ok"
    assert status["pipeline_final"] == "ok"            # the fake status says complete
    assert not [e for e in w.events if e[0] == "start"]
    # The deadline reaches every command; late (CPU) steps get the deadline + 10 min as their timeout.
    assert {c["env"]["WENART_DEADLINE"] for c in w.calls} == {str(int(deadline))}
    pipe = w.call("pipeline real01")
    assert pipe["timeout"] == pytest.approx(deadline - pipe["t"] + P.LATE_S)


def test_a_step_cut_by_its_own_deadline_is_deadline(tmp_path):
    w = World(tmp_path, rc={"objaverse thumbnails": 3, "ask glm real01": 3})
    assert w.prep().run_all() == 1
    steps = w.steps()
    assert steps["thumbnails"]["status"] == "deadline" and steps["session_glm"]["status"] == "deadline"
    assert steps["session_qwen"]["status"] == "ok"


def test_projects_without_questions_get_no_asks_and_no_final(tmp_path):
    w = World(tmp_path, pipeline_rc={"real01": 0, "synthetic-02": 1, "real01-scan": 0})
    assert w.prep().run_all() == 0
    labels = w.labels()
    assert not [x for x in labels if x.startswith(("ask ", "status ", "pipeline_final "))]
    assert "start qwen 8" in labels and "objaverse judge qwen" in labels    # the probe and the library still run
    steps = w.steps()
    assert steps["pipeline_final"]["status"] == "skipped" and steps["pipeline_final"]["note"] == "no questions"
    assert steps["pipelines"]["projects"] == {"real01": "ok", "synthetic-02": "needs_review", "synthetic-06": "ok",
                                              "real01-scan": "ok"}


def test_a_missing_project_fails_the_pipelines_step_and_is_left_out_of_the_tests(tmp_path):
    w = World(tmp_path, projects=("real01", "synthetic-02", "synthetic-06"))
    assert w.prep().run_all() == 1
    step = w.steps()["pipelines"]
    assert step["status"] == "failed" and step["note"] == "not found: real01-scan"
    assert "pipeline real01-scan" not in w.labels()
    env = w.call("pytest tests/gpu/test_recognition.py")["env"]
    assert env["WENART_PREP_PROJECTS"] == "real01 synthetic-02 synthetic-06"
    assert env["WENART_PREP_OUTPUTS"] == str(w.outputs)


def test_copy_writes_the_answers_and_the_library_credits_into_results(tmp_path):
    w = World(tmp_path)
    w.prep().run_all()
    rec = w.results / "recognition" / "real01"
    assert sorted(p.name for p in rec.iterdir()) == ["answers_glm.json", "answers_qwen.json", "crops",
                                                     "requests.json"]
    assert (rec / "crops" / "sym_L0_1_ctx.png").read_bytes() == b"png"
    assert (w.results / "furniture" / "real01" / "building.json").is_file()
    assert (w.results / "recognition" / "real01-scan" / "answers_qwen.json").is_file()
    attribution = (w.results / "library" / "ATTRIBUTION.md").read_text()
    assert '"Sofa" by A' in attribution and "ODC-By" in attribution
    # The library work stays in <prep-root>/library (outside the per-job $RESULTS); $RESULTS/library is its copy.
    work = w.prep_root / "library"
    files = sorted(f.relative_to(work).as_posix() for f in work.rglob("*") if f.is_file())
    assert "judge/answers_glm.json" in files and "judge/requests.json" in files and "survey.json" in files
    assert sorted(f.relative_to(w.results / "library").as_posix() for f in (w.results / "library").rglob("*")
                  if f.is_file()) == files


def test_copy_only(tmp_path):
    w = World(tmp_path)
    w.prep(only=("pipelines",)).run_all()
    assert not (w.results / "recognition").exists()
    assert w.prep().copy_only() == 0
    assert (w.results / "recognition" / "real01" / "requests.json").is_file()


def test_timings_measure_the_speed_against_the_m6_reference(tmp_path):
    w = World(tmp_path)
    w.prep(only=("timings",)).run_all()
    render = w.call("blender render")["cmd"]
    cams = [f"cam_r_{i:02d}" for i in range(1, 11)]
    work = w.prep_root / "timing" / "nvidia-rtx-pro-6000-blackwell-server-edition"
    assert render == ["/venv/python", "-m", "wenart.blender.cli", "render", "--scene",
                      str(w.m6 / "synthetic-04" / "scene" / "scene.blend"), "--out", str(work / "renders"),
                      "--cameras", ",".join(cams), "--samples", "128", "--res", "1920x1080", "--exposure", "auto",
                      "--white-balance", "auto"]
    polish = w.call("polish smoke")
    assert polish["cmd"] == ["/fast/venv-polish/python", "-m", "wenart.polish", "smoke", "--project-out",
                             str(w.m6 / "synthetic-04"), "--views", "cam_r_01", "--out", str(work / "polish"),
                             "--previews", "none"]
    assert polish["env"]["PYTORCH_CUDA_ALLOC_CONF"] == "expandable_segments:True"
    doc = json.loads((w.results / "timing" / "gpu_speed.json").read_text())
    assert doc["render"]["seconds_per_view"] == 3.0 and doc["render"]["reference"]["seconds_per_view"] == 6.0
    assert doc["render"]["speed"] == 2.0 and doc["render"]["compared_cameras"] == 10
    assert doc["polish"]["seconds_per_forward"] == 0.8 and doc["polish"]["attempts"] == 4
    assert doc["polish"]["speed"] == 1.25 and doc["speed"] == 1.25            # the lower of the two
    assert doc["gpu"]["key"] == "RTX PRO 6000" and doc["reference_gpu"] == "RTX PRO 4500"
    assert w.manifest()["proposals"]["plan_gpu_speed"] == {"RTX PRO 6000": 1.25}
    assert (work / "gpu_speed.json").is_file() and w.steps()["timings"]["status"] == "ok"


def test_timings_build_the_scene_when_the_m6_blend_is_missing(tmp_path):
    w = World(tmp_path)
    (w.m6 / "synthetic-04" / "scene" / "scene.blend").unlink()
    w.prep(only=("timings",)).run_all()
    labels = w.labels()
    assert labels[:2] == ["blender build", "blender render"]
    build = w.call("blender build")["cmd"]
    work = w.prep_root / "timing" / "nvidia-rtx-pro-6000-blackwell-server-edition"
    assert build[3:] == ["build", "--building", str(w.m6 / "synthetic-04" / "building_final.json"), "--style",
                         str(w.m6 / "synthetic-04" / "style.json"), "--assets", str(w.assets), "--out",
                         str(work / "scene"), "--preview-samples", "32", "--camera-policy", "search", "--reuse"]
    assert w.call("blender render")["cmd"][5] == str(work / "scene" / "scene.blend")


def test_timings_without_m6_outputs_fail_without_a_command(tmp_path):
    w = World(tmp_path)
    import shutil
    shutil.rmtree(w.m6 / "synthetic-04")
    w.prep(only=("timings",)).run_all()
    step = w.steps()["timings"]
    assert step["status"] == "failed" and "no scene of synthetic-04" in step["note"] and not w.calls


def test_detector_and_library_proposals(tmp_path):
    w = World(tmp_path)
    w.prep().run_all()
    proposals = w.manifest()["proposals"]
    assert proposals["detector"] == {"usable": True, "t_det": 0.3, "t_strong": 0.6,
                                     "file": "detect/detector_calibration.json"}
    assert proposals["catalog_objaverse"] == "library/catalog_objaverse.json"
    assert w.steps()["library"]["accepted_models"] == 1
    m = w.manifest()
    assert m["final"] is True and m["exit_code"] == 0 and m["gpu"]["key"] == "RTX PRO 6000"
    assert [p["name"] for p in m["projects"]] == ["real01", "synthetic-02", "synthetic-06", "real01-scan"]
    real01 = m["projects"][0]
    assert real01["pipeline_rc"] == 4 and real01["questions"] == 2 and real01["pipeline_final_rc"] == 0


def test_nothing_accepted_is_a_warning_and_writes_no_catalog(tmp_path):
    w = World(tmp_path, rc={"objaverse accept": 1})
    assert w.prep().run_all() == 0
    assert "objaverse write-catalog" not in w.labels() and "objaverse report" in w.labels()
    assert w.steps()["library"]["status"] == "warning"


def test_gpu_test_environments(tmp_path):
    w = World(tmp_path)
    w.prep().run_all()
    lib = w.call("pytest tests/gpu/test_library.py")
    assert lib["env"]["WENART_LIBRARY"] == str(w.prep_root / "library")
    assert lib["env"]["WENART_ASSETS"] == str(w.assets)
    det = w.call("pytest tests/gpu/test_detect.py")
    assert det["env"]["DETECT_CALIBRATION"] == str(w.results / "detect" / "detector_calibration.json")
    assert det["env"]["DETECT_TEST_PROJECTS"] == ""
    assert f"--junitxml={w.results / 'tests' / 'junit-detect.xml'}" in det["cmd"]
    assert {c["env"]["WENART_RESULTS"] for c in w.calls if c["label"].startswith("pytest")} == {str(w.results)}
    assert [t["status"] for t in w.manifest()["tests"]] == ["passed"] * 3


def test_a_failed_test_group_fails_the_job(tmp_path):
    w = World(tmp_path, rc={"pytest tests/gpu/test_library.py": 1})
    assert w.prep().run_all() == 1
    assert w.steps()["tests"]["note"] == "failed: library (rc 1)"
    assert [t["status"] for t in w.manifest()["tests"]] == ["passed", "failed", "passed"]


def test_skip_only_and_no_tests(tmp_path):
    w = World(tmp_path)
    assert w.prep(only=("pipelines", "copy"), tests=False).run_all() == 0
    status = {s["name"]: (s["status"], s["note"]) for s in w.manifest()["steps"]}
    assert status["survey"] == ("skipped", "not in --only") and status["pipelines"][0] == "ok"
    assert status["tests"] == ("skipped", "not in --only")
    w2 = World(tmp_path / "b")
    w2.prep(skip=("timings", "detect_calibrate"), tests=False).run_all()
    status = {s["name"]: (s["status"], s["note"]) for s in w2.manifest()["steps"]}
    assert status["timings"] == ("skipped", "in --skip") and status["tests"] == ("skipped", "--no-tests")


# --------------------------------------------------------------------------
# Review fixes after the first prep pod (orch-1, orch-3, orch-5, orch-6)
# --------------------------------------------------------------------------

def test_pipeline_final_exit_4_runs_again_with_no_ai_and_is_a_warning(tmp_path):
    """orch-1: real01-scan/-photo's pipeline_final exited 4 on the first prep pod (second-round symbol questions)
    and the step failed. Exit 4 with complete answers is never failed: once more with --no-ai, warning."""
    w = World(tmp_path)
    w.second_round = {"real01-scan"}
    assert w.prep().run_all() == 0, w.lines
    finals = [c for c in w.calls if c["label"] == "pipeline_final real01-scan"]
    assert len(finals) == 2 and "--no-ai" not in finals[0]["cmd"] and finals[1]["cmd"] == finals[0]["cmd"] + ["--no-ai"]
    assert len([c for c in w.calls if c["label"] == "pipeline_final real01"]) == 1
    step = w.steps()["pipeline_final"]
    assert step["status"] == "warning"
    assert step["note"] == "second-round questions left unanswered (no-ai): real01-scan"
    assert step["projects"]["real01-scan"] == {"rc": 0, "answers_complete": True, "second_round": True}
    scan = next(p for p in w.manifest()["projects"] if p["name"] == "real01-scan")
    assert scan["pipeline_final_rc"] == 0
    rec = json.loads((w.outputs / "real01-scan" / "run" / "pipeline_final.json").read_text())
    assert rec["status"] == "warning" and rec["note"] == "second-round questions left unanswered (no-ai)"
    assert [s["name"] for s in rec["steps"]] == ["pipeline_final", "pipeline_final --no-ai"]
    assert json.loads((w.outputs / "real01-scan" / "building.json").read_text())["no_ai"] is True


def test_a_resumed_prep_never_reruns_the_first_pipeline_over_the_final_building(tmp_path):
    """orch-1: the first pipeline's stage record (orchestrator format) is reused while its fingerprint holds, as
    the scheduler's pending logic does; a changed project runs it again."""
    w = World(tmp_path)
    assert w.prep().run_all() == 0
    rec = json.loads((w.outputs / "real01" / "run" / "pipeline.json").read_text())
    assert rec["status"] == "pending" and rec["rc"] == 4 and rec["fingerprint"]
    final = (w.outputs / "real01" / "building.json").read_text()
    assert json.loads(final)["stage"] == "final"
    # A targeted re-run of the pipelines step: the final buildings stay.
    w.calls.clear()
    w.events.clear()
    assert w.prep(results=tmp_path / "results-2", only=("pipelines",)).run_all() == 0
    assert w.labels() == []
    assert (w.outputs / "real01" / "building.json").read_text() == final
    step = w.steps_of(tmp_path / "results-2")["pipelines"]
    assert step["projects"] == {"real01": "pending", "synthetic-02": "pending", "synthetic-06": "ok",
                                "real01-scan": "pending"}
    assert step["reused"] == ["real01", "synthetic-02", "synthetic-06", "real01-scan"]
    # A whole resumed job: no first pipeline, the questions stay pending, pipeline_final runs on them.
    assert w.prep(results=tmp_path / "results-3").run_all() == 0
    labels = w.labels()
    assert not [x for x in labels if x.startswith("pipeline ")]
    assert [x for x in labels if x.startswith("pipeline_final ")] == [
        "pipeline_final real01", "pipeline_final synthetic-02", "pipeline_final real01-scan"]
    # A changed project: its first pipeline runs again (the others stay reused).
    (w.repo / "projects" / "real01" / "plan.pdf").write_bytes(b"changed")
    w.calls.clear()
    w.events.clear()
    w.prep(results=tmp_path / "results-4", only=("pipelines",)).run_all()
    assert w.labels() == ["pipeline real01"]


def _models() -> dict:
    from wenart.recognition import answers as A
    return A.load_models()


def _store(path: Path, key: str, items: list, data) -> None:
    """A complete answer store of ``key`` (the recognition / judge AnswerStore format)."""
    m = _models()[key]
    P.write_json(path, {"schema_version": "0.1", "kind": "recognition_answers", "model_key": key, "model": m["id"],
                        "slug": m["slug"], "incomplete": False,
                        "calls": {i["key"]: {"input_sha256": i["input_sha256"], "model": m["id"], "data": data}
                                  for i in items}})


def _answered_world(tmp_path, judge_complete=("qwen", "glm")):
    """An earlier job's outputs: real01 with two symbol questions (Qwen answers stored, GLM answers in the
    committed seeds) and a library whose judge answers are complete for ``judge_complete``."""
    from fakes.fake_vlm import minimal_instance
    from wenart.assets import objaverse as OV
    from wenart.recognition import schemas as RS
    w = World(tmp_path)
    items = [{"key": f"sym_L0_{i}", "task": "symbol_type", "images": [f"crops/sym_L0_{i}_ctx.png"],
              "input_sha256": f"{i:064x}"} for i in (1, 2)]
    rec = w.outputs / "real01" / "recognition"
    P.write_json(rec / "requests.json", {"kind": "recognition_requests", "items": items})
    answer = minimal_instance(RS.M7_SCHEMAS["symbol_type"])
    assert not RS.validation_errors("symbol_type", answer)
    _store(rec / f"answers_{_models()['qwen']['slug']}.json", "qwen", items, answer)
    _store(w.repo / "results" / "recognition" / "real01" / f"answers_{_models()['glm']['slug']}.json", "glm",
           items, answer)
    lib = w.prep_root / "library"
    jitems = [{"key": f"lib_u{i}", "task": "library_judge", "images": [f"sheets/u{i}.jpg"],
               "input_sha256": f"{i + 10:064x}"} for i in (1, 2)]
    P.write_json(lib / "judge" / "requests.json", {"kind": "objaverse_judge_requests", "items": jitems})
    judgement = minimal_instance(OV.judge_schema())
    assert OV.valid_judgement(judgement)
    for key in ("qwen", "glm"):
        done = jitems if key in judge_complete else jitems[:1]
        _store(lib / "judge" / f"answers_{_models()[key]['slug']}.json", key, done, judgement)
    return w


def test_no_server_starts_when_nothing_is_left_to_ask(tmp_path):
    """orch-3: every recognition answer is stored (or in the committed seeds) and every judge item answered: no
    vLLM start, probe 'not run'; the seeds are copied by ``ask`` without a server."""
    w = _answered_world(tmp_path)
    assert w.prep(only=("session_qwen", "session_glm")).run_all() == 0, w.lines
    assert not [e for e in w.events if e[0] == "start"]
    assert w.labels() == ["ask glm real01"]
    ask = w.call("ask glm real01")["cmd"]
    assert "--server" not in ask and ask[-2:] == ["--seed-answers", str(w.repo / "results" / "recognition" / "real01")]
    sessions = w.manifest()["sessions"]
    assert sessions["qwen"]["probe"] == "not run" and sessions["glm"]["probe"] == "not run"
    assert sessions["qwen"]["missing"] == {"recognition": {"real01": 0}, "judge": 0}
    steps = w.steps()
    assert steps["session_qwen"]["status"] == "ok" and "no server started" in steps["session_qwen"]["note"]
    assert w.manifest()["proposals"]["check_yaml_max_seqs"] == {}
    # One unanswered judge item of GLM: only the GLM server starts, and it judges.
    w2 = _answered_world(tmp_path / "b", judge_complete=("qwen",))
    assert w2.prep(only=("session_qwen", "session_glm")).run_all() == 0, w2.lines
    assert [e for e in w2.events if e[0] == "start"] == [("start", "glm", 8)]
    assert "objaverse judge glm" in w2.labels() and "objaverse judge qwen" not in w2.labels()
    assert w2.manifest()["sessions"]["glm"]["missing"]["judge"] == 1


def test_a_targeted_rerun_judges_the_library_of_an_earlier_job(tmp_path):
    """orch-3: the library work lives in <prep-root>/library, so PREP_ONLY=session_qwen,session_glm,library on a new
    pod (a new $RESULTS) finds the judge requests of the earlier job and judges them; the EXIT-trap copy puts the
    library into this job's $RESULTS/library."""
    w = World(tmp_path)
    assert w.prep(skip=("session_qwen", "session_glm", "library", "tests")).run_all() == 0
    assert not (w.results / "library" / "judge" / "answers_qwen.json").exists()
    w.calls.clear()
    w.events.clear()
    results2 = tmp_path / "results-2"
    job = w.prep(results=results2, only=("session_qwen", "session_glm", "library"))
    assert job.run_all() == 0, w.lines
    labels = w.labels()
    assert "objaverse judge qwen" in labels and "objaverse judge glm" in labels and "objaverse accept" in labels
    lib = str(w.prep_root / "library")
    assert w.call("objaverse judge qwen")["cmd"][5] == lib and w.call("objaverse accept")["cmd"][-1] == lib
    assert w.manifest_of(results2)["sessions"]["qwen"]["judge"]["items"] == 2
    assert job.copy_only() == 0
    for name in ("judge/requests.json", "judge/answers_qwen.json", "judge/answers_glm.json", "survey.json",
                 "thumbnails.json", "catalog_objaverse.json", "ATTRIBUTION.md"):
        assert (results2 / "library" / name).is_file(), name


def test_selected_library_and_session_steps_fail_when_their_inputs_are_missing(tmp_path):
    """orch-3: a selected step whose inputs are missing fails (it used to be skipped or ok, judging nothing)."""
    w = World(tmp_path)
    assert w.prep(only=("thumbnails", "judge_requests", "session_qwen", "library")).run_all() == 1
    steps = w.steps()
    assert {n: steps[n]["status"] for n in ("thumbnails", "judge_requests", "session_qwen", "library")} == {
        n: "failed" for n in ("thumbnails", "judge_requests", "session_qwen", "library")}
    assert "no survey.json" in steps["thumbnails"]["note"] and "no thumbnails.json" in steps["library"]["note"]
    assert "no judge/requests.json" in steps["session_qwen"]["note"]
    assert not w.calls and not [e for e in w.events if e[0] == "start"]
    # The library with thumbnails but never judged (no judge requests): failed before accept, not "nothing
    # accepted" (a warning, exit 0).
    P.write_json(w.prep_root / "library" / "thumbnails.json", {"counts": {"rendered": 2}})
    assert w.prep(results=tmp_path / "results-2", only=("library",)).run_all() == 1
    step = w.steps_of(tmp_path / "results-2")["library"]
    assert step["status"] == "failed" and "no judge/requests.json" in step["note"] and not w.calls
    # With recognition work and the library step but no library work: the session asks, then fails for the
    # missing judge requests.
    w2 = World(tmp_path / "b")
    assert w2.prep(only=("pipelines", "session_qwen", "library")).run_all() == 1
    assert "ask qwen real01" in w2.labels()
    assert w2.steps()["session_qwen"]["status"] == "failed"
    assert "library not judged" in w2.steps()["session_qwen"]["note"]


def test_a_recognition_only_job_needs_no_library(tmp_path):
    """orch-3: a job that leaves the library step out (PREP_ONLY=pipelines,session_qwen,session_glm,pipeline_final,
    e.g. after a recognition prompt change) asks its questions and ends 0; the sessions note that nothing was
    judged instead of failing for the judge requests that step would need."""
    w = World(tmp_path)
    assert w.prep(only=("pipelines", "session_qwen", "session_glm", "pipeline_final")).run_all() == 0, w.lines
    assert "ask qwen real01" in w.labels() and "ask glm real01" in w.labels()
    assert not [x for x in w.labels() if x.startswith("objaverse")]
    steps = w.steps()
    assert steps["session_qwen"]["status"] == "ok" and steps["session_glm"]["status"] == "ok"
    session = w.manifest()["sessions"]["qwen"]
    assert session["judge"] is None and session["missing"]["judge"] is None
    assert session["judge_note"] == "library not judged: the library step is not in --only"
    # The same with --skip library.
    w2 = World(tmp_path / "b")
    assert w2.prep(skip=("survey", "thumbnails", "judge_requests", "library", "tests")).run_all() == 0, w2.lines
    assert w2.manifest()["sessions"]["glm"]["judge_note"] == "library not judged: the library step is in --skip"


def test_a_library_rerun_on_a_new_pod_names_the_missing_glbs(tmp_path):
    """orch-3 (verifier): the accepted GLBs live in the survey's container-disk cache. A targeted library re-run on
    a new pod (no survey in it) fails at write-catalog; the note names the missing GLBs and says to include survey."""
    w = World(tmp_path)
    lib = w.prep_root / "library"
    glb = tmp_path / "hf-old-pod" / "u1.glb"
    P.write_json(lib / "survey.json", {"candidates": [{"uid": "u1", "glb": str(glb)}, {"uid": "u2", "glb": None}]})
    P.write_json(lib / "thumbnails.json", {"counts": {"rendered": 2}})
    P.write_json(lib / "judge" / "requests.json", {"items": [{"key": "u1"}]})
    fake_write = w.write

    def write(cmd, label):
        if label == "objaverse accept":                   # the real accepted.json: one decision per object
            P.write_json(lib / "accepted.json", {"accepted": [{"uid": "u1", "type": "sofa"}]})
            return 0
        if label == "objaverse write-catalog":            # every accepted GLB refused as glb_changed: exit 1
            return 1
        return fake_write(cmd, label)

    w.write = write
    assert w.prep(only=("library",)).run_all() == 1
    step = w.steps()["library"]
    assert step["status"] == "failed" and step["glbs_missing"] == 1
    assert f"1 accepted GLB(s) not on this pod's disk (e.g. {glb})" in step["note"]
    assert "must include survey" in step["note"]
    # The GLB present (the survey ran on this pod): a write-catalog failure is reported without that diagnosis.
    glb.parent.mkdir(parents=True)
    glb.write_bytes(b"glTF")
    assert w.prep(results=tmp_path / "results-2", only=("library",)).run_all() == 1
    step = w.steps_of(tmp_path / "results-2")["library"]
    assert step["note"] == "accept 0, write-catalog 1, report 0" and "glbs_missing" not in step


def test_nothing_accepted_removes_an_earlier_catalogue_from_the_work_folder(tmp_path):
    """The library work folder outlives the job: a catalogue of an earlier accept is not proposed again."""
    w = World(tmp_path)
    assert w.prep().run_all() == 0
    assert (w.prep_root / "library" / "catalog_objaverse.json").is_file()
    w.rc["objaverse accept"] = 1
    results2 = tmp_path / "results-2"
    assert w.prep(results=results2, only=("library", "copy")).run_all() == 0
    assert not (w.prep_root / "library" / "catalog_objaverse.json").exists()
    assert not (results2 / "library" / "catalog_objaverse.json").exists()
    assert w.manifest_of(results2)["proposals"]["catalog_objaverse"] is None
    assert w.steps_of(results2)["library"]["stale_removed"] == ["catalog_objaverse.json", "ATTRIBUTION.md"]


def test_timings_use_the_frozen_reference_not_the_live_results(tmp_path):
    """orch-5: the reference times come from wenart/run/timing_reference.json; the live results files (rewritten by
    any later full run of synthetic-04, here with RTX PRO 6000 times) are never read."""
    w = World(tmp_path)
    live = w.repo / "results" / "renders" / "synthetic-04" / "render_manifest.json"
    P.write_json(live, {"renders": [{"camera": f"cam_r_{i:02d}", "seconds": 1.5} for i in range(12)]})
    P.write_json(w.repo / "results" / "polish" / "synthetic-04" / "polish_manifest.json",
                 {"device": "NVIDIA RTX PRO 6000 Blackwell Server Edition", "seconds_per_forward": 0.5})
    w.prep(only=("timings",)).run_all()
    doc = json.loads((w.results / "timing" / "gpu_speed.json").read_text())
    assert doc["render"]["reference"]["seconds_per_view"] == 6.0 and doc["render"]["speed"] == 2.0
    assert doc["polish"]["reference"]["seconds_per_forward"] == 1.0 and doc["polish"]["speed"] == 1.25
    assert doc["reference_file"] == "wenart/run/timing_reference.json"
    assert doc["render"]["reference"]["source"] == "wenart/run/timing_reference.json"
    assert "pxy56z9yyehx1t" in doc["reference_note"]


@pytest.mark.parametrize("gpu, polish_device", [
    ("NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA RTX PRO 6000 Blackwell Server Edition"),
    ("NVIDIA RTX PRO 4500 Blackwell", "NVIDIA GeForce RTX 4090"),
    (None, "NVIDIA RTX PRO 4500 Blackwell"),
])
def test_a_reference_from_another_gpu_is_refused(tmp_path, gpu, polish_device):
    """orch-5: a reference whose recorded GPU is not the reference GPU (RTX PRO 4500) gives no speed: failed, and
    nothing is rendered or polished."""
    w = World(tmp_path)
    w.timing_reference({"render": {"seconds": {f"cam_r_{i:02d}": 6.0 for i in range(12)}},
                        "polish": {"device": polish_device, "seconds_per_forward": 1.0}}, gpu=gpu)
    assert w.prep(only=("timings",)).run_all() == 1
    step = w.steps()["timings"]
    assert step["status"] == "failed" and "not the reference GPU RTX PRO 4500: refused" in step["note"]
    assert not w.calls and not (w.results / "timing" / "gpu_speed.json").exists()
    assert w.manifest()["proposals"]["plan_gpu_speed"] is None


def test_the_committed_timing_reference_is_the_m6_pod_b_record():
    """orch-5: wenart/run/timing_reference.json holds the synthetic-04 times of M6 pod B (RTX PRO 4500 Blackwell,
    pxy56z9yyehx1t) as committed at 0cfcea0, and the prep accepts it."""
    assert P.TIMING_REFERENCE == TIMING_REFERENCE
    ref = json.loads((ROOT / TIMING_REFERENCE).read_text())
    assert ref["kind"] == "timing_reference" and ref["project"] == "synthetic-04"
    assert ref["gpu"] == "NVIDIA RTX PRO 4500 Blackwell" and ref["pod_id"] == "pxy56z9yyehx1t"
    assert ref["source_commit"].startswith("0cfcea0")
    secs = ref["render"]["seconds"]
    assert len(secs) == 14 and secs["cam_r_L3_banyo_1"] == 5.26 and secs["cam_r_L3_salon_mutfak_2"] == 4.28
    assert ref["render"]["samples"] == 128 and ref["render"]["resolution"] == [1920, 1080]
    assert ref["polish"]["device"] == "NVIDIA RTX PRO 4500 Blackwell" and ref["polish"]["seconds_per_forward"] == 2.843
    job = P.Prep.__new__(P.Prep)
    job.opts = P.PrepOptions(results=Path("/nonexistent"))
    assert job.timing_reference() == (ref, None)
    # The prep pod's measured render speed (1.634, results of job 20261003-173020-prep) follows from these times:
    # the mean of the first 10 cameras is 4.617 s.
    first10 = [secs[c] for c in sorted(secs)][:10]
    assert round(sum(first10) / 10, 3) == 4.617


def test_raster_room_label_tests_run_only_for_the_prep_projects(tmp_path):
    """orch-6: tests/gpu/test_recognition.py::test_m7_raster_room_labels is parametrised over the raster projects but
    skips those not in WENART_PREP_PROJECTS (the prep job leaves a missing project out of that list)."""
    junit = tmp_path / "junit.xml"
    env = dict(os.environ, WENART_PREP_OUTPUTS=str(tmp_path / "outputs-prep"), WENART_RESULTS=str(tmp_path / "r"),
               WENART_PREP_PROJECTS="real01 synthetic-02 synthetic-06")
    proc = subprocess.run([sys.executable, "-m", "pytest", "-m", "gpu", "tests/gpu/test_recognition.py", "-k",
                           "raster_room_labels", "-p", "no:cacheprovider", "-q", f"--junitxml={junit}"],
                          cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    text = junit.read_text()
    cases = dict(re.findall(r'<testcase [^>]*name="test_m7_raster_room_labels\[([^\]]+)\]"[^>]*>(.*?)</testcase>',
                            text, re.S))
    assert sorted(cases) == ["real01-photo", "real01-scan", "synthetic-02"], proc.stdout
    assert "<skipped" in cases["real01-scan"] and "<skipped" in cases["real01-photo"]
    assert "not in WENART_PREP_PROJECTS" in cases["real01-scan"]
    # synthetic-02 is a prep project: it runs (and fails here: no building.json in the empty outputs folder).
    assert "<skipped" not in cases["synthetic-02"] and "<failure" in cases["synthetic-02"]


def test_gpu_key_names_the_runpod_gpu():
    assert P.gpu_key("NVIDIA RTX PRO 6000 Blackwell Server Edition") == "RTX PRO 6000"
    assert P.gpu_key("NVIDIA RTX PRO 6000 Blackwell Workstation Edition") == "RTX PRO 6000"
    assert P.gpu_key("NVIDIA GeForce RTX 4090") == "RTX 4090"
    assert P.gpu_key("NVIDIA RTX PRO 4500 Blackwell") == "RTX PRO 4500"
    assert P.gpu_key(None) is None and P.gpu_key("Some GPU") is None


def test_cli_options_and_the_wenart_run_entry(tmp_path, monkeypatch):
    for var in ("WENART_RESULTS", "WENART_DEADLINE", "WENART_PREP_OUTPUTS", "WENART_PREP_ROOT"):
        monkeypatch.delenv(var, raising=False)
    assert P.main([]) == 2                                              # no --results
    assert P.main(["--results", str(tmp_path / "r"), "--skip", "surveys"]) == 2
    assert P.main(["--results", str(tmp_path / "r"), "--projects", "../x"]) == 2
    monkeypatch.setenv("WENART_DEADLINE", "1999999999")
    monkeypatch.setenv("WENART_PREP_OUTPUTS", str(tmp_path / "out"))
    opts = P.options_from_args(P.parse_args(["--results", str(tmp_path / "r"), "--projects", "real01,synthetic-06",
                                             "--skip", "timings,tests"]))
    assert opts.deadline == 1999999999.0 and opts.outputs == tmp_path / "out"
    assert opts.projects == ["real01", "synthetic-06"] and opts.skip == ("timings", "tests")
    assert opts.detect_projects == list(P.DETECT_PROJECTS) and opts.timing_project == "synthetic-04"
    # ``python -m wenart.run prep`` hands everything after "prep" to wenart.run.prep.main.
    from wenart.run import __main__ as RUN
    calls = []
    monkeypatch.setattr(P, "main", lambda argv: calls.append(argv) or 0)
    assert RUN.main(["prep", "--results", "x", "--copy-only"]) == 0 and calls == [["--results", "x", "--copy-only"]]


def test_estimates_cover_every_heavy_step():
    w_est = {name: P.Prep.estimate(P.Prep.__new__(P.Prep), name) for name in P.HEAVY}
    assert all(v > 0 for v in w_est.values())
    assert w_est["session_qwen"] > w_est["session_glm"]                 # Qwen starts slower (M6 measurements)
    assert set(P.HEAVY) <= set(P.STEPS) and P.STEPS.index("thumbnails") < P.STEPS.index("session_qwen")
    assert P.STEPS.index("survey") == 0 and P.STEPS[-2:] == ("copy", "tests")


def test_the_real_server_session_starts_vllm_offline(tmp_path, monkeypatch):
    """Without a server factory the prep uses wenart.run.servers.server; the vLLM process gets HF_HUB_OFFLINE=1
    (after the survey) and HF_HOME, the size flags of the probe and the pid file of the EXIT trap."""
    spawned = {}

    class Proc:
        pid = 4242

        def __init__(self):
            self.rc = None

        def poll(self):
            return self.rc

        def terminate(self):
            self.rc = 0

        def kill(self):
            self.rc = -9

        def wait(self, timeout=None):
            return self.rc

    def fake_spawn(cmd, env, log_path):
        spawned.update(cmd=cmd, env=env, pid_file=(tmp_path / "job" / "vllm.pid").read_text()
                       if (tmp_path / "job" / "vllm.pid").exists() else None)
        return Proc()

    monkeypatch.setattr(SV, "popen_spawn", fake_spawn)
    monkeypatch.setattr(SV, "http_health", lambda port=SV.VLM_PORT: True)
    w = World(tmp_path)
    prep = P.Prep(w.opts(), runner=w.runner, clock=w.clock, out=w.lines.append, gpu_query=lambda: dict(GPU_6000))
    prep.offline = True
    stats: list = []
    with prep.open_server("qwen", 8, stats) as url:
        assert url == "http://127.0.0.1:8001/v1"
        assert (tmp_path / "job" / "vllm.pid").read_text() == "4242\n"
    assert not (tmp_path / "job" / "vllm.pid").exists()
    assert spawned["env"]["HF_HUB_OFFLINE"] == "1" and spawned["env"]["HF_HOME"] == str(tmp_path / "hf")
    assert spawned["cmd"][-4:] == ["--max-model-len", "32768", "--max-num-seqs", "8"]
    assert stats and stats[0]["ok"] and stats[0]["seqs"] == 8
