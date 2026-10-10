"""The pod jobs' control flow, run here with fake commands (no GPU, no network): a job must reach its end.

Why: pod P1 of 10 Oct 2026 (docs/gpu-log.md, `kmnn2d9uanyqab`, $8.51) hung for 84 minutes after its first downloads:
`scripts/jobs/bakeoff_m12.sh` sends its output through `exec > >(tee ...)`, and a bare `wait` in bash >= 5.1 also
waits for that process substitution, which never ends. Nothing exercised the script's flow before the pod.

How: the job runs in a temporary workspace (`WENART_WS`, `WENART_FAST`, `WENART_PY`) whose `python` answers the
`wenart.agent.bakeoff` subcommands from files, whose `hf` downloads nothing and whose `pod_setup_recognition.sh` is
empty; a timeout turns a hang into a failure.
"""
from __future__ import annotations

import os
import re
import stat
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "scripts" / "jobs"

FAKE_PY = r'''#!/usr/bin/env bash
# fake python: -m wenart.agent.bakeoff <cmd> ...; anything else succeeds
if [ "$1" = "-m" ] && [ "$2" = "wenart.agent.bakeoff" ]; then
  cmd=$3; shift 3
  out=""; key=""; name=""
  while [ $# -gt 0 ]; do
    case "$1" in --out) out=$2; shift 2;; --key) key=$2; shift 2;; --name) name=$2; shift 2;; *) shift;; esac
  done
  case "$cmd" in
    models) printf '%s\n' "fp8 bakeoff.fp8 Qwen/x rev1 1 30 4" "muse bakeoff.muse meta/x rev2 1 60 2" \
                          "bf16 bakeoff.bf16 Qwen/y rev3 1 56 2" "flash_next bakeoff.flash_next nvidia/z rev4 2 133 2" \
                          "step_flash bakeoff.step_flash step/w rev5 2 129 2";;
    run) mkdir -p "$out"; echo '{}' > "$out/${key#bakeoff.}.json";;
    started) [ -f "$out/$name.json" ];;
    summary) mkdir -p "$out"; echo '{"pick": "fp8"}' > "$out/summary.json";;
  esac
  exit $?
fi
exit 0
'''

FAKE_HF = '''#!/usr/bin/env bash
# fake hf download <id> --revision <rev>: logs the id
echo "$2" >> "${FAKE_HF_LOG:?}"
sleep 0.2
'''


def _exe(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def test_no_bare_wait_after_a_tee_redirect():
    """A bare `wait` in a job that redirects through `exec > >(tee ...)` never returns (bash >= 5.1)."""
    for job in sorted(JOBS.glob("*.sh")) + sorted((ROOT / "scripts").glob("*.sh")):
        text = job.read_text(encoding="utf-8")
        if "exec > >(tee" not in text:
            continue
        bare = [n for n, line in enumerate(text.splitlines(), 1)
                if re.match(r"^\s*wait\s*(;|$|#|\|\|)", line)]
        assert not bare, f"{job.relative_to(ROOT)}: bare wait at line(s) {bare}; wait for explicit pids"


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_the_bakeoff_job_reaches_its_end_with_fakes(tmp_path):
    ws, fast = tmp_path / "ws", tmp_path / "fast"
    repo = ws / "repo"
    _exe(repo / "scripts" / "pod_setup_recognition.sh", "#!/usr/bin/env bash\nexit 0\n")
    _exe(tmp_path / "bin" / "python", FAKE_PY)
    _exe(fast / "venv-vllm" / "bin" / "hf", FAKE_HF)
    hf_log = tmp_path / "hf.log"
    env = dict(os.environ, WENART_WS=str(ws), WENART_FAST=str(fast), WENART_PY=str(tmp_path / "bin" / "python"),
               WENART_GPU_COUNT="2", BAKEOFF_VLLM_RETRY="", JOB_ID="flowtest", FAKE_HF_LOG=str(hf_log),
               WENART_RESULTS=str(tmp_path / "results"), WENART_JOB_DIR=str(tmp_path / "job"))
    env.pop("WENART_DEADLINE", None)
    res = subprocess.run(["bash", str(JOBS / "bakeoff_m12.sh")], env=env, cwd=str(tmp_path), capture_output=True,
                         text=True, timeout=120)
    out = res.stdout + res.stderr
    assert res.returncode == 0, out[-3000:]
    for step in ("step start: phase-a fp8+muse", "step start: phase-b bf16", "step start: phase-c flash_next",
                 "step start: summary", "all steps ok"):
        assert step in out, f"missing {step!r}:\n{out[-3000:]}"
    downloaded = hf_log.read_text(encoding="utf-8").split()
    assert {"Qwen/x", "meta/x", "Qwen/y", "nvidia/z"} <= set(downloaded)
    assert "step/w" not in downloaded            # the fallback is downloaded only when flash_next did not start
