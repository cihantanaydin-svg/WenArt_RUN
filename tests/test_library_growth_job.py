"""Pod P4's job script (``scripts/jobs/library_growth.sh``) run here with fake commands (no GPU, no network): it
reaches its end, runs every step (five of them in the background, waited for by their pids), copies the results,
goes on when the Infinigen part fails, and a second run resumes: no Infinigen setup when every job is done, no vLLM
server when every answer is current (the setup step still running is stopped, not waited for).

How (as ``tests/test_jobs_flow.py``): a temporary workspace (``WENART_WS``, ``WENART_FAST``, ``WENART_PY``) whose
``python`` answers the ``wenart.assets growth run`` / ``audit`` steps from files, whose ``git`` and ``apt-get``
fail (the Infinigen setup fails at the clone) and whose ``scripts/pod_setup_polish.sh`` only sleeps; a timeout turns
a hang into a failure.

Milestone 13 round 3 (docs/milestone13.md §14.6): the ``refetch`` step, the reason column of ``steps.tsv`` (a failed
step's last line; P2 had ``preview 1 0`` and nothing else) and the ``GROWTH_ONLY=hssd`` mode of pod P2b (its exact
step list, nothing else downloaded or catalogued, a second run resumes)."""
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
    if step == os.environ.get("FAKE_FAIL_STEP"):
        print("some output first")
        print(f"growth {step}: FAILED: a fake reason\tfor the test")
        print("")
        sys.exit(1)
    if step == "ingest":
        time.sleep(0.3)
        write(rep / f"ingest_{opt('--source')}.json", "{}")
        if opt("--source") == "hssd" and not os.environ.get("FAKE_NO_HSSD"):
            write(Path(opt("--assets")) / "models" / "hssd" / "hssd_fake.glb", "glTF")
        if opt("--source") == "3dwh" and not os.environ.get("FAKE_NO_3DWH"):
            write(Path(opt("--assets")) / "models" / "3dwh" / "3dwh_fake.glb", "glTF")
    elif step == "infinigen-plan":
        done = (g / "infinigen" / "fake_done").exists()
        print(f"growth infinigen-plan: todo {0 if done else 30}, done {30 if done else 0}, failed 0")
    elif step == "gso-licence":
        write(rep / "gso_licences.json", "{}")
    elif step == "catalogue":
        for n in ("catalog_library.json", "catalog.json"):
            write(p4 / "audit" / "catalogue" / n, "{}")
        only = opt("--only")
        write(p4 / "audit" / "new_ids.json", json.dumps({"ids": ["hssd_fake"], "only": [only], "kept_ids": ["abo_x"]})
              if only else '{"ids": ["abo_x"]}')
        write(rep / "catalogue.json", "{}")
    elif step == "ask":
        answered = (p4 / "audit" / "ask" / "answers_fake.json").exists()
        if "--plan-only" in args:
            print(f"growth ask: unanswered {0 if answered else 3}")
        else:
            write(p4 / "audit" / "ask" / "answers_fake.json", "{}")
    elif step == "report":
        write(rep / "growth.md", "# Library growth\n")
        if os.environ.get("FAKE_BIG_JSON"):                 # over the runner's 20 MB limit: also copied as .json.gz
            write(rep / "big.json", json.dumps({"x": "y" * 16_000_000}))
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
         "gso-licence", "convert-gso", "refetch", "catalogue", "render-a", "convert-infinigen", "catalogue-b",
         "render-b", "code", "decide", "write", "vision-fields", "pending", "sheets", "gaps", "coverage", "preview",
         "report", "gpu-tests")
# GROWTH_ONLY=hssd (pod P2b): exactly these steps, in this order (the background setup-check first)
HSSD_STEPS = ("ingest-hssd", "refetch", "catalogue", "render", "code", "ask", "decide", "write", "vision-fields",
              "gaps", "coverage", "report", "gpu-tests")
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


def _workspace(tmp_path):
    ws, fast, fakebin = tmp_path / "ws", tmp_path / "fast", tmp_path / "bin"
    _exe(ws / "repo" / "scripts" / "pod_setup_polish.sh", '#!/usr/bin/env bash\nsleep "${FAKE_SETUP_SLEEP:-1}"\n')
    _exe(fakebin / "python", FAKE_PY)
    _exe(fakebin / "git", "#!/usr/bin/env bash\necho fake git refuses >&2\nexit 1\n")
    _exe(fakebin / "apt-get", "#!/usr/bin/env bash\nexit 1\n")
    env = dict(os.environ, WENART_WS=str(ws), WENART_FAST=str(fast), WENART_PY=str(fakebin / "python"),
               JOB_ID="p2b", FAKE_LOG=str(tmp_path / "calls.log"), WENART_RESULTS=str(tmp_path / "results"),
               WENART_JOB_DIR=str(tmp_path / "job"), AUDIT_MODEL_KEY="agent",
               PATH=f"{fakebin}:{os.environ.get('PATH', '')}", WENART_BLENDER=str(fakebin / "blender"),
               GROWTH_MIN_FREE_GB="0", GROWTH_ONLY="hssd")
    for k in ("WENART_DEADLINE", "HF_TOKEN", "FAKE_FAIL_STEP", "FAKE_NO_HSSD"):
        env.pop(k, None)
    return ws, env


def _started(out: str) -> list:
    """The step names in the order the job started them (foreground and background)."""
    import re
    return re.findall(r"library_growth: step start(?: \(background\))?: ([^\s,]+)", out)


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_growth_only_hssd_runs_the_hssd_layer_alone_and_resumes(tmp_path):
    """Pod P2b (GROWTH_ONLY=hssd): setup-check, ingest-hssd, refetch, catalogue --only hssd, render of the new ids,
    code, ask, decide, write, vision-fields, gaps, coverage, report, GPU tests and nothing else (no other download,
    conversion, Infinigen, demand, pending, sheet or preview step); the token is never written; a failed step is
    recorded with its last line as the reason; a second run resumes (every answer current: no server)."""
    ws, env = _workspace(tmp_path)
    env["HF_TOKEN"] = "hf_fake_secret_value_for_the_test"
    rc, out, _ = _run(dict(env, FAKE_FAIL_STEP="gaps"), tmp_path)
    assert rc == 1 and "FAILED steps: gaps" in out, out[-3000:]
    assert _started(out) == ["setup-check", *HSSD_STEPS], _started(out)
    assert "mode: GROWTH_ONLY=hssd" in out and "step end: gaps rc=1" in out and "a fake reason for the test" in out
    calls = (tmp_path / "calls.log").read_text().splitlines()
    assert any(c.startswith("-m wenart.assets growth run ingest --source hssd --workers 8 --token-env HF_TOKEN")
               for c in calls)
    assert any(c.startswith("-m wenart.assets growth run catalogue --only hssd") for c in calls)
    assert any(c.startswith("-m wenart.assets growth run refetch") for c in calls)
    assert any(c.startswith("-m wenart.assets audit render") and "--ids-file" in c for c in calls)
    for never in ("--source abo", "--source polyhaven", "--source gso", "--source ambientcg", "growth run demands",
                  "growth run speed-probe", "growth run convert", "growth run gso-licence", "growth run preview",
                  "growth run pending", "audit sheets", "infinigen"):
        assert not any(never in c for c in calls), never
    steps = (ws / "library-growth" / "report" / "steps.tsv").read_text().splitlines()
    rows = {r.split("\t")[0]: r.split("\t") for r in steps}
    assert rows["gaps"][1] == "1" and rows["gaps"][3] == "growth gaps: FAILED: a fake reason for the test"
    assert rows["catalogue"][1] == "0" and rows["catalogue"][3] == ""
    results = tmp_path / "results"
    texts = [p.read_text(errors="replace") for p in results.rglob("*") if p.is_file()]
    assert texts and not any("hf_fake_secret_value_for_the_test" in t for t in texts + [out])

    # second run: the failure gone, every answer current -> no server; the setup step is stopped, not waited for
    rc, out, secs = _run(dict(env, FAKE_SETUP_SLEEP="90"), tmp_path)
    assert rc == 0 and "all steps ok" in out, out[-3000:]
    assert "no server" in out and "stopping background step setup-check" in out and secs < 60
    assert _started(out) == ["setup-check", *[s for s in HSSD_STEPS if s != "ask"]]


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_growth_only_hssd_stops_without_a_token_a_model_or_a_known_mode(tmp_path):
    ws, env = _workspace(tmp_path)
    rc, out, _ = _run(env, tmp_path)                                   # no HF_TOKEN: nothing to do
    assert rc == 1 and "GROWTH_ONLY=hssd has nothing to do" in out and not _started(out)
    assert not (tmp_path / "calls.log").exists() or "ingest" not in (tmp_path / "calls.log").read_text()
    steps = (ws / "library-growth" / "report" / "steps.tsv").read_text()
    assert "ingest-hssd (skipped: no HF_TOKEN)\t1\t0\tHF_TOKEN is not set" in steps
    env["HF_TOKEN"] = "hf_fake"
    rc, out, _ = _run(dict(env, FAKE_NO_HSSD="1"), tmp_path)          # the gate refused: no model on the volume
    assert rc == 1 and "no HSSD model on the volume" in out
    assert _started(out) == ["setup-check", "ingest-hssd", "report"]
    rc, out, _ = _run(dict(env, GROWTH_ONLY="abo"), tmp_path)
    assert rc == 1 and "is not a mode of this job (all | hssd | 3dwh)" in out and not _started(out)


def test_the_job_header_documents_the_p2b_command():
    text = JOB.read_text(encoding="utf-8")
    assert ('python3 scripts/gpu_run.py run --job scripts/jobs/library_growth.sh --disk 150 --max-minutes 90 '
            '--over-5-ok \\\n#       --env GROWTH_ONLY=hssd --env AUDIT_MODEL_KEY=agent --purpose "M13 P2b: HSSD layer"'
            ) in text
    assert 'GROWTH_ONLY="${GROWTH_ONLY:-all}"' in text and "reason_of" in text
    assert 'printf \'%s\\t%s\\t%s\\t%s\\n\'' in text                  # steps.tsv: name rc seconds reason


# --------------------------------------------------------------------------
# GROWTH_ONLY=3dwh (23 Oct 2026, the user's request): the 3D Warehouse layer in one pod
# --------------------------------------------------------------------------

WH_STEPS = ("download-3dwh", "ingest-3dwh", "catalogue", "render", "code", "ask", "decide", "write", "vision-fields",
            "sheets", "gaps", "coverage", "report", "gpu-tests")     # the extras are audited: no preview step
# a fake curl: logs its call, writes FAKE_CURL_BODY (default: WH_BYTES bytes of zip data) to the -o file
FAKE_CURL = r'''#!/usr/bin/env bash
echo "curl $*" >> "$FAKE_CURL_LOG"
out=""
while [ $# -gt 0 ]; do
  if [ "$1" = "-o" ]; then out="$2"; shift; fi
  shift
done
if [ -n "${FAKE_CURL_BODY:-}" ]; then printf '%s' "$FAKE_CURL_BODY" > "$out"; else head -c "$WH_BYTES" /dev/zero > "$out"; fi
exit "${FAKE_CURL_RC:-0}"
'''


def _wh_workspace(tmp_path):
    ws, env = _workspace(tmp_path)
    _exe(tmp_path / "bin" / "curl", FAKE_CURL)
    env.update(GROWTH_ONLY="3dwh", WH_BYTES="64", FAKE_CURL_LOG=str(tmp_path / "curl.log"))
    for k in ("FAKE_CURL_BODY", "FAKE_CURL_RC", "FAKE_NO_3DWH", "WH_ROOT"):
        env.pop(k, None)
    return ws, env


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_growth_only_3dwh_downloads_fixes_and_audits_the_zip_in_one_pod_and_resumes(tmp_path):
    """GROWTH_ONLY=3dwh: setup-check, the Drive download (drive.usercontent.google.com, confirm=t, resumable, the
    size checked), ingest --source 3dwh, catalogue --only 3dwh, render, code, ask, decide, write, vision-fields,
    sheets, gaps, coverage, preview, report, GPU tests and nothing else; a second run keeps the zip (no download)."""
    ws, env = _wh_workspace(tmp_path)
    rc, out, _ = _run(env, tmp_path)
    assert rc == 0 and "all steps ok" in out, out[-3000:]
    assert _started(out) == ["setup-check", *WH_STEPS], _started(out)
    zip_path = ws / "library" / "3dwh" / "zip" / "3D Warehouse Furniture.zip"
    assert zip_path.stat().st_size == 64 and not zip_path.with_name(zip_path.name + ".part").exists()
    curl = (tmp_path / "curl.log").read_text().splitlines()
    assert len(curl) == 1 and "-C -" in curl[0] and ("https://drive.usercontent.google.com/download?id="
                                                    "1nSHF5dvjLLcpruowus8zZUx8kSiDxkjD&export=download&confirm=t") in curl[0]
    calls = (tmp_path / "calls.log").read_text().splitlines()
    assert any(c.startswith(f"-m wenart.assets growth run ingest --source 3dwh --library {ws}/library/3dwh "
                            "--workers 16") for c in calls)
    assert any(c.startswith("-m wenart.assets growth run catalogue --only 3dwh") for c in calls)
    for never in ("--source hssd", "--source abo", "--source polyhaven", "--source gso", "--source ambientcg",
                  "growth run demands", "growth run speed-probe", "growth run convert", "growth run gso-licence",
                  "growth run pending", "growth run refetch", "growth run preview", "infinigen"):
        assert not any(never in c for c in calls), never
    rc, out, _ = _run(dict(env, FAKE_BIG_JSON="1"), tmp_path)
    assert rc == 0 and "present (64 bytes): kept" in out
    assert len((tmp_path / "curl.log").read_text().splitlines()) == 1
    import gzip
    import json
    big = tmp_path / "results" / "library" / "growth" / "big.json.gz"
    assert big.is_file() and big.stat().st_size < 1_000_000
    assert json.loads(gzip.decompress(big.read_bytes()))["x"] == "y" * 16_000_000


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_growth_only_3dwh_moves_an_html_answer_aside_and_stops_without_a_model(tmp_path):
    """Drive answers with a web page (the file is not shared as "anyone with the link"): the download step fails
    with that reason, the page is moved aside (never deleted, never resumed into), and with no fixed model the job
    stops after the report."""
    ws, env = _wh_workspace(tmp_path)
    rc, out, _ = _run(dict(env, FAKE_CURL_BODY="<!DOCTYPE html><html>Google Drive</html>", FAKE_NO_3DWH="1"),
                      tmp_path)
    assert rc == 1 and "sent an HTML page, not the zip" in out and "no fixed 3D Warehouse model" in out
    assert _started(out) == ["setup-check", "download-3dwh", "ingest-3dwh", "report"]
    folder = ws / "library" / "3dwh" / "zip"
    assert [p.name.split(".part.")[1][:5] for p in folder.iterdir()] == ["html-"]
    steps = (ws / "library-growth" / "report" / "steps.tsv").read_text()
    assert "download-3dwh\t1\t" in steps and "is the file shared as 'anyone with the link'?" in steps
