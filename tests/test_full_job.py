"""CPU tests of scripts/jobs/full.sh (docs/milestone6.md §2.4, §9 "full.sh static checks").

- Static: shebang, ``set -Eeuo pipefail``, ERR trap (line + command), TERM -> 143, logs under
  /workspace/logs (tee), the exports of polish.sh, the cgroup thread budget, the setup with every part
  before ``HF_HUB_OFFLINE=1``, the flock copy loop, the EXIT trap that kills the vLLM pid, the
  documented run command (M7 §9.5: RTX PRO 6000, --disk 150, never L4), the recognition setup parts with
  LibreDWG (M7 §5.1).
- Sandbox: full.sh runs with fake interpreters (WENART_WS / WENART_FAST point into tmp_path) that record
  every call: the orchestrator's arguments and environment, the setup's parts, the copy loop with
  ``--since`` and the full copy from the EXIT trap, a vLLM process the "orchestrator" left behind is
  stopped, this job's logs go to $RESULTS/logs or, with a private project, to results-private/_logs.
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
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "scripts" / "jobs" / "full.sh"


def _text() -> str:
    return JOB.read_text(encoding="utf-8")


def _flat() -> str:
    return re.sub(r"\\\n\s*", "", _text())


def _body(name: str) -> str:
    match = re.search(rf"^{re.escape(name)}\(\) \{{\n(.*?)^\}}", _text(), re.S | re.M)
    assert match, f"function {name} not found"
    return match.group(1)


# --------------------------------------------------------------------------
# Static checks
# --------------------------------------------------------------------------

def test_conventions():
    text = _text()
    assert text.startswith("#!/usr/bin/env bash\n")
    assert "\nset -Eeuo pipefail\n" in text
    assert re.search(r"^trap 'on_error \$LINENO \"\$BASH_COMMAND\"' ERR$", text, re.M), "no ERR trap with line+command"
    assert 'on_error() { log "ERROR at line $1: $2"; exit 1; }' in text
    assert re.search(r"^trap 'exit 143' TERM$", text, re.M)
    assert re.search(r"^trap 'on_exit' EXIT$", text, re.M)
    assert os.access(JOB, os.X_OK), "full.sh is not executable"
    assert subprocess.run(["bash", "-n", str(JOB)], capture_output=True).returncode == 0


def test_logs_under_workspace_logs_with_tee():
    text = _text()
    assert 'WS="${WENART_WS:-/workspace}"' in text and "LOGS=$WS/logs" in text
    assert "LOG=$LOGS/full-$JOB.log" in text and 'mkdir -p "$LOGS"' in text
    assert 'exec > >(tee -a "$LOG") 2>&1' in text
    assert text.index('exec > >(tee -a "$LOG") 2>&1') < text.index("set_threads\n")


def test_exports_of_polish_sh():
    text = _text()
    for line in ('export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"',
                 'export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"', "export HF_XET_HIGH_PERFORMANCE=1",
                 'export WENART_OUTPUTS="$REPO/outputs"', 'export CHECK_MODELS="${CHECK_MODELS:-qwen glm}"',
                 'FAST="${WENART_FAST:-/opt/wenart}"', 'PY="${WENART_PY:-$WS/venv/bin/python}"',
                 'POLISH_PY="${WENART_POLISH_PY:-$FAST/venv-polish/bin/python}"',
                 'export RENDER_SAMPLES="${RENDER_SAMPLES:-128}"', "REPO=$WS/repo"):
        assert line in text, line
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS", "OPENCV_FOR_THREADS_NUM"):
        assert f"{var}=$n" in _flat(), var
    budget = _body("cpu_budget")
    assert '"$CGROUP/cpu.max"' in budget and "cpu.cfs_quota_us" in budget and "(quota + period - 1) / period" in budget


def test_setup_then_offline_then_orchestrator():
    text = _flat()
    setup = text.index("bash scripts/pod_setup_polish.sh")
    offline = text.index("export HF_HUB_OFFLINE=1")
    pod = text.index('"$PY" -m wenart.run pod "${POD_ARGS[@]}"')
    assert setup < offline < pod
    assert 'POLISH_MODE=final POLISH_PHASES="look controls polish gate check report tests" bash scripts/pod_setup_polish.sh' in text
    assert 'POLISH_RECOG_PARTS="vllm libredwg models" POLISH_MODE=final' in text      # M7 §5.1: DWG projects
    assert text.index("copy_loop &") < setup


def test_flock_copy_loop_and_exit_trap():
    locked = _body("copy_results_locked")
    assert 'flock -w "${1:-120}" 9' in locked and '9>"$LOCK"' in locked
    assert '"$PY" -m wenart.run copy "${COPY_ARGS[@]}" "${since[@]}"' in _body("copy_results")
    assert 'since=(--since "$COPY_STAMP")' in _body("copy_results")
    loop = _body("copy_loop")
    assert 'sleep "$COPY_EVERY_S"' in loop and "copy_results_locked 60" in loop
    assert 'COPY_EVERY_S="${RUN_COPY_EVERY_S:-300}"' in _text()
    on_exit = _body("on_exit")
    assert on_exit.index("kill_vllm") < on_exit.index('kill "$COPY_PID"') < on_exit.index("copy_results_locked 300 full")
    assert "copy_job_logs" in on_exit and 'exit "$rc"' in on_exit
    kill = _body("kill_vllm")
    assert 'cat "$PID_FILE"' in kill and 'kill -TERM -- "-$pid"' in kill and "kill -KILL" in kill
    assert "PID_FILE=$JOB_DIR/vllm.pid" in _text()
    logs = _body("copy_job_logs")
    assert 'dest="$JOB_DIR/results-private/_logs"' in logs and 'tail -n 200 "$f"' in logs
    assert '"$f" -nt "$START_STAMP"' in logs


def test_documented_run_command_and_runner():
    lines = _text().splitlines()
    i = next(n for n, ln in enumerate(lines) if "gpu_run.py run" in ln)
    command = " ".join(lines[i:i + 2])
    assert "--job scripts/jobs/full.sh" in command and "--gpu 'RTX PRO 6000'" in command   # M7 §9.5
    assert "--disk 150" in command and "--max-minutes 115" in command and "--env RUN_PROJECTS=" in command
    grace = re.search(r"--grace (\d+)", command)
    assert grace and int(grace.group(1)) < 900
    assert "L4" not in command and "never L4" in _text()
    spec = importlib.util.spec_from_file_location("gpu_run_m6", ROOT / "scripts" / "gpu_run.py")
    gpu_run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gpu_run)
    assert gpu_run.JOB_RE.match("scripts/jobs/full.sh")
    assert gpu_run.GPU_PRIORITY[0] == "RTX PRO 6000"            # the documented GPU is the runner's first choice


def test_env_knobs_reach_the_orchestrator_arguments():
    text = _flat()
    for knob in ("RUN_PROJECTS", "PRIVATE_PROJECTS", "PRIVATE_SELFTEST", "AB_PROJECTS", "AB_CONTROL_PROJECT",
                 "AB_PHASE", "RUN_FORCE", "RENDER_SAMPLES"):
        assert knob in text, knob
    for flag in ("--projects", "--private", "--private-selftest", "--ab", "--ab-phase", "--ab-controls", "--force",
                 "--results", "--profile full"):
        assert flag in text, flag


# --------------------------------------------------------------------------
# full.sh in a sandbox
# --------------------------------------------------------------------------

FAKE_PY = r'''#!__PYTHON__
"""Fake interpreter for full.sh tests: records the call; the 'pod' can leave a vLLM process behind."""
import json, os, subprocess, sys, time
from pathlib import Path

argv = sys.argv[1:]
if argv[:1] in (["-c"], ["-"]):
    os.execv("__PYTHON__", ["__PYTHON__"] + argv)
KEYS = ("HF_HUB_OFFLINE", "HF_HOME", "HF_XET_HIGH_PERFORMANCE", "WENART_BLENDER", "WENART_OUTPUTS", "CHECK_MODELS",
        "WENART_JOB_DIR", "WENART_RESULTS", "WENART_POLISH_PY", "WENART_ASSETS", "WENART_LOGS", "RENDER_SAMPLES",
        "WENART_DEADLINE", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS", "OPENCV_FOR_THREADS_NUM", "WENART_CPU_THREADS")
rec = {"argv": argv, "cwd": os.getcwd(), "env": {k: os.environ.get(k) for k in KEYS}, "t": time.time()}
if argv[:3] == ["-m", "wenart.run", "pod"]:
    logs = Path(os.environ["WENART_LOGS"])
    (logs / "vllm-qwen.log").write_text("".join(f"v{i}\n" for i in range(300)))
    if os.environ.get("FAKE_VLLM") == "1":
        p = subprocess.Popen(["sleep", "300"], start_new_session=True, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        Path(os.environ["WENART_JOB_DIR"], "vllm.pid").write_text(f"{p.pid}\n")
        rec["vllm_pid"] = p.pid
    with open(os.environ["FAKE_CALLS"], "a") as fh:
        fh.write(json.dumps(rec) + "\n")
    time.sleep(float(os.environ.get("FAKE_POD_SLEEP", "0")))
    print("orchestrator: fake run done")
    sys.exit(int(os.environ.get("FAKE_POD_RC", "0")))
with open(os.environ["FAKE_CALLS"], "a") as fh:
    fh.write(json.dumps(rec) + "\n")
if argv[:3] == ["-m", "wenart.run", "copy"]:
    print("copy: 0 public file(s), 0 private file(s) (full copy)")
'''

FAKE_SETUP = """#!/usr/bin/env bash
echo "SETUP POLISH_MODE=${POLISH_MODE:-} POLISH_PHASES=${POLISH_PHASES:-} HF_HUB_OFFLINE=${HF_HUB_OFFLINE:-unset} CHECK_MODELS=$CHECK_MODELS OMP=${OMP_NUM_THREADS:-} RECOG=${POLISH_RECOG_PARTS:-}" >> "$FAKE_SETUP_LOG"
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
        (cgroup / "cpu.max").write_text("150000 100000\n")          # 1.5 CPUs -> 2 threads
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


def test_sandbox_public_run(tmp_path):
    box = Box(tmp_path)
    proc = box.run(RUN_PROJECTS="synthetic-01 synthetic-03", AB_PROJECTS="synthetic-01 synthetic-03",
                   AB_CONTROL_PROJECT="synthetic-01", AB_PHASE="render", RUN_FORCE="photos", FAKE_VLLM="1",
                   FAKE_POD_SLEEP="2.5", RUN_COPY_EVERY_S="1", FAKE_POD_RC="1")
    assert proc.returncode == 1, box.output                          # the orchestrator's exit code
    calls = box.calls()
    pod = next(c for c in calls if c["argv"][:3] == ["-m", "wenart.run", "pod"])
    assert pod["argv"][3:] == ["--results", str(box.results), "--profile", "full",
                               "--projects", "synthetic-01 synthetic-03",
                               "--ab", "synthetic-01 synthetic-03", "--ab-phase", "render",
                               "--ab-controls", "synthetic-01", "--force", "photos"]
    env = pod["env"]
    assert env["HF_HUB_OFFLINE"] == "1" and env["HF_HOME"] == str(tmp_path / "fast" / "hf")
    assert env["HF_XET_HIGH_PERFORMANCE"] == "1" and env["CHECK_MODELS"] == "qwen glm"
    assert env["WENART_BLENDER"] == str(box.ws / "tools" / "blender" / "blender")
    assert env["WENART_OUTPUTS"] == str(box.ws / "repo" / "outputs") and env["RENDER_SAMPLES"] == "128"
    assert env["WENART_POLISH_PY"] == str(tmp_path / "fast" / "venv-polish" / "bin" / "python")
    assert env["WENART_JOB_DIR"] == str(box.job_dir) and env["WENART_DEADLINE"] == "1999999999"
    assert {env[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                             "VECLIB_MAXIMUM_THREADS", "OPENCV_FOR_THREADS_NUM", "WENART_CPU_THREADS")} == {"2"}
    assert pod["cwd"] == str(box.ws / "repo")
    # Setup with every part, before the offline switch.
    setup = box.setup_log.read_text()
    assert ("POLISH_MODE=final POLISH_PHASES=look controls polish gate check report tests HF_HUB_OFFLINE=unset"
            in setup)
    assert "RECOG=vllm libredwg models" in setup
    # The copy loop (with --since) ran during the orchestrator; the EXIT trap made one full copy at the end.
    copies = [c for c in calls if c["argv"][:3] == ["-m", "wenart.run", "copy"]]
    assert any("--since" in c["argv"] for c in copies), copies
    assert "--since" not in copies[-1]["argv"] and copies[-1]["t"] >= pod["t"]
    assert copies[-1]["argv"][3:] == ["--results", str(box.results), "--projects", "synthetic-01 synthetic-03",
                                      "--ab", "synthetic-01 synthetic-03"]
    since = next(c for c in copies if "--since" in c["argv"])
    assert since["argv"][-1] == str(box.logs / "full-test.copied")
    # The vLLM process left behind is stopped by the EXIT trap and its pid file removed.
    deadline = time.time() + 10
    while not _pid_gone(pod["vllm_pid"]) and time.time() < deadline:
        time.sleep(0.2)
    assert _pid_gone(pod["vllm_pid"]) and not (box.job_dir / "vllm.pid").exists()
    assert "stopping vllm (pid" in box.output
    # This job's logs (not the earlier pod's) go to $RESULTS/logs; the job log too.
    assert sorted(p.name for p in (box.results / "logs").iterdir()) == ["vllm-qwen.log"]
    assert len((box.results / "logs" / "vllm-qwen.log").read_text().splitlines()) == 200
    assert (box.results / "full-test.log").is_file()
    log = (box.logs / "full-test.log").read_text()
    assert "CPU budget: 2 thread(s) per process" in log and "orchestrator exit 1" in log
    assert "job test ends with exit code 1" in log


def test_sandbox_private_run_keeps_logs_private(tmp_path):
    box = Box(tmp_path)
    proc = box.run(PRIVATE_PROJECTS="real-01", PRIVATE_SELFTEST="1")
    assert proc.returncode == 0, box.output
    pod = next(c for c in box.calls() if c["argv"][:3] == ["-m", "wenart.run", "pod"])
    assert pod["argv"][3:] == ["--results", str(box.results), "--profile", "full", "--private", "real-01",
                               "--private-selftest"]
    assert not (box.results / "logs").exists()
    assert (box.job_dir / "results-private" / "_logs" / "vllm-qwen.log").is_file()
    copies = [c for c in box.calls() if c["argv"][:3] == ["-m", "wenart.run", "copy"]]
    assert copies[-1]["argv"][3:] == ["--results", str(box.results), "--private", "real-01", "--private-selftest"]


@pytest.mark.parametrize("env, msg", [({}, "nothing to run"), ({"RUN_PROJECTS": "x", "AB_PHASE": "both"},
                                                                 "unknown AB_PHASE")])
def test_sandbox_refuses_bad_env(tmp_path, env, msg):
    box = Box(tmp_path)
    proc = box.run(**env)
    assert proc.returncode == 2 and msg in box.output
    assert not [c for c in box.calls() if c["argv"][:3] == ["-m", "wenart.run", "pod"]]


def test_sandbox_setup_failure_is_a_warning(tmp_path):
    box = Box(tmp_path)
    proc = box.run(RUN_PROJECTS="synthetic-01", FAKE_SETUP_RC="1")
    assert proc.returncode == 0, box.output
    assert "warning: pod_setup_polish.sh exit 1" in box.output
