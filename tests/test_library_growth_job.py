"""Pod P4's job script (``scripts/jobs/library_growth.sh``) run here with fake commands (no GPU, no network): it
reaches its end, runs every step (five of them in the background, waited for by their pids), copies the results,
goes on when the Infinigen part fails, and a second run resumes: no Infinigen setup when every job is done, no vLLM
server when every answer is current (the setup step still running is stopped, not waited for).

How (as ``tests/test_jobs_flow.py``): a temporary workspace (``WENART_WS``, ``WENART_FAST``, ``WENART_PY``) whose
``python`` answers the ``wenart.assets growth run`` / ``audit`` steps from files, whose ``git`` and ``apt-get``
fail (the Infinigen setup fails at the clone) and whose ``scripts/pod_setup_polish.sh`` only sleeps; a timeout turns
a hang into a failure."""
from __future__ import annotations

import os
import stat
import subprocess
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "scripts" / "jobs" / "library_growth.sh"

FAKE_PY = r'''#!/usr/bin/env python3
import json, os, sys, time
from pathlib import Path
args = sys.argv[1:]
with open(os.environ["FAKE_LOG"], "a") as fh:
    fh.write(" ".join(args) + "\n")


def opt(name, default=None):
    return args[args.index(name) + 1] if name in args else default


def write(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


if args[:4] == ["-m", "wenart.assets", "growth", "run"]:
    step, g, p4 = args[4], Path(opt("--growth")), Path(opt("--p4"))
    rep = g / "report"
    if step == "ingest":
        time.sleep(0.3)
        write(rep / f"ingest_{opt('--source')}.json", "{}")
    elif step == "infinigen-plan":
        done = (g / "infinigen" / "fake_done").exists()
        print(f"growth infinigen-plan: todo {0 if done else 30}, done {30 if done else 0}, failed 0")
    elif step == "gso-licence":
        write(rep / "gso_licences.json", "{}")
    elif step == "catalogue":
        for n in ("catalog_library.json", "catalog.json"):
            write(p4 / "audit" / "catalogue" / n, "{}")
        write(p4 / "audit" / "new_ids.json", '{"ids": ["abo_x"]}')
        write(rep / "catalogue.json", "{}")
    elif step == "ask":
        answered = (p4 / "audit" / "ask" / "answers_fake.json").exists()
        if "--plan-only" in args:
            print(f"growth ask: unanswered {0 if answered else 3}")
        else:
            write(p4 / "audit" / "ask" / "answers_fake.json", "{}")
    elif step == "report":
        write(rep / "growth.md", "# Library growth\n")
    sys.exit(0)
if args[:3] == ["-m", "wenart.assets", "audit"]:
    step, a = args[3], Path(opt("--out")) / "audit"
    if step == "render":
        write(a / "measure.json", "{}")
        write(a / "sheets" / "bowl" / "abo_x.jpg", "a per-model sheet stays on the volume")
    elif step == "decide":
        write(a / "audit.json", '{"items": []}')
    elif step == "sheets":
        write(a / "contact" / "bowl.jpg", "jpg")
    sys.exit(0)
sys.exit(0)
'''


def _exe(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _run(env: dict, cwd: Path, timeout: float = 180) -> tuple[int, str, float]:
    t0 = time.time()
    res = subprocess.run(["bash", str(JOB)], env=env, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
    return res.returncode, res.stdout + res.stderr, time.time() - t0


STEPS = ("demands", "size-grid", "speed-probe",                     # Milestone 13 (track T7), before the ingests
         "gso-licence", "convert-gso", "catalogue", "render-a", "convert-infinigen", "catalogue-b", "render-b",
         "code", "decide", "write", "vision-fields", "pending", "sheets", "gaps", "coverage", "preview", "report",
         "gpu-tests")
BACKGROUND = ("setup-check", "infinigen", "ingest-polyhaven", "ingest-abo", "ingest-gso",
              "ingest-abo-m13", "ingest-polyhaven-m13", "ingest-ambientcg")   # Milestone 13 lists


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_the_growth_job_reaches_its_end_and_resumes_with_fakes(tmp_path):
    ws, fast, fakebin = tmp_path / "ws", tmp_path / "fast", tmp_path / "bin"
    repo = ws / "repo"
    _exe(repo / "scripts" / "pod_setup_polish.sh", '#!/usr/bin/env bash\nsleep "${FAKE_SETUP_SLEEP:-1}"\n')
    _exe(fakebin / "python", FAKE_PY)
    _exe(fakebin / "git", "#!/usr/bin/env bash\necho fake git refuses >&2\nexit 1\n")
    _exe(fakebin / "apt-get", "#!/usr/bin/env bash\nexit 1\n")
    _exe(fast / "venv-uv" / "bin" / "uv", "#!/usr/bin/env bash\nexit 0\n")
    log = tmp_path / "calls.log"
    results = tmp_path / "results"
    env = dict(os.environ, WENART_WS=str(ws), WENART_FAST=str(fast), WENART_PY=str(fakebin / "python"),
               JOB_ID="flow", FAKE_LOG=str(log), WENART_RESULTS=str(results), WENART_JOB_DIR=str(tmp_path / "job"),
               AUDIT_MODEL_KEY="agent", PATH=f"{fakebin}:{os.environ.get('PATH', '')}",
               WENART_BLENDER=str(fakebin / "blender"), GROWTH_MIN_FREE_GB="0")
    env.pop("WENART_DEADLINE", None)
    env.pop("HF_TOKEN", None)                                     # no token: the HSSD step is skipped, loudly

    # the volume guard: too little free space stops the job before any download (nothing is deleted)
    rc, out, _ = _run(dict(env, GROWTH_MIN_FREE_GB="1000000"), tmp_path)
    assert rc == 1 and "no download; ask the user" in out and "step start (background): ingest" not in out, out[-2000:]
    assert not log.exists() or not any("ingest" in c for c in log.read_text().splitlines())

    rc, out, _ = _run(env, tmp_path)
    assert rc == 1, out[-3000:]                                   # the Infinigen part failed (fake git) ...
    assert "FAILED steps: infinigen" in out and "infinigen: fetch of" in out, out[-3000:]
    for step in STEPS + ("ask",):                                 # ... and every other step still ran
        assert f"step start: {step}" in out, f"missing {step!r}:\n{out[-3000:]}"
    for step in BACKGROUND:
        assert f"step start (background): {step}" in out and f"step end: {step} rc=" in out, step
    # Milestone 13: without HF_TOKEN the HSSD ingest never starts and says why (D2: the gated terms)
    assert "ingest-hssd: SKIPPED: HF_TOKEN is not set" in out and "step start (background): ingest-hssd" not in out
    calls = log.read_text().splitlines()
    assert any(c.startswith("-m wenart.assets growth run ingest --source abo --m13") for c in calls)
    assert any("--source polyhaven --m13 --size 2k" in c for c in calls)
    assert any(c.startswith("-m wenart.assets growth run speed-probe") for c in calls)
    assert not any("--source hssd" in c for c in calls)
    assert any(c.startswith("-m wenart.assets growth run ask --model-key agent") for c in calls)
    assert any("--ids-file" in c and c.startswith("-m wenart.assets audit render") for c in calls)
    growth = results / "library" / "growth"
    p4 = results / "library" / "audit" / "p4"
    for f in (growth / "growth.md", growth / "steps.tsv", growth / "ingest_abo.json", p4 / "audit.json",
              p4 / "catalogue" / "catalog_library.json", p4 / "contact" / "bowl.jpg", p4 / "new_ids.json",
              results / "library_growth-flow.log", results / "logs" / "growth-infinigen-flow.log"):
        assert f.is_file(), f
    assert not (p4 / "sheets").exists()                           # per-model sheets stay on the volume
    steps = (growth / "steps.tsv").read_text().splitlines()
    assert any(s.startswith("infinigen\t1\t") for s in steps) and any(s.startswith("catalogue\t0\t") for s in steps)
    assert any(s.startswith("ingest-hssd (skipped: no HF_TOKEN)\t0\t") for s in steps)

    # second run: Infinigen done meanwhile, every answer current -> no setup, no server; the setup is not waited for
    (ws / "library-growth" / "infinigen" / "fake_done").write_text("")
    env["FAKE_SETUP_SLEEP"] = "90"
    n_calls = len(log.read_text().splitlines())
    rc, out, secs = _run(env, tmp_path)
    assert rc == 0, out[-3000:]
    assert "setup skipped" in out and "no server" in out and "stopping background step setup-check" in out
    assert secs < 60, f"the job waited for the setup it did not need ({secs:.0f} s)"
    new_calls = log.read_text().splitlines()[n_calls:]
    assert not any(c.startswith("-m wenart.assets growth run ask --model-key") for c in new_calls)
    assert "all steps ok" in out
