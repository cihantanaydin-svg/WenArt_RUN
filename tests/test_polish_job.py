"""CPU tests of the Milestone 5 pod scripts (docs/milestone5.md §8, §9 "job scripts").

- Conventions of scripts/jobs/polish.sh, scripts/pod_setup_polish.sh, the parts switch of
  scripts/pod_setup_recognition.sh and the deadline of scripts/pod_entry.sh: ``bash -n``,
  shebang, ``set -Eeuo pipefail``, ERR trap, logs under /workspace/logs, executable bit.
- Every phase and command of the §8.2 table is in polish.sh, each with its venv.
- polish.sh itself runs in a sandbox (WENART_WS / WENART_FAST point into tmp_path) with fake
  interpreters that record every call and write the files the real CLIs write; the tests check
  the phases per mode, the order, the venv and the environment of every call, the vLLM flags,
  the --hide-sets built from the CONTROL lines, the building_final.json fallback copy, the
  deadline handling and the layout of the copied results.
- The documented run command uses the RTX PRO 4500 (never L4) and the runner accepts it:
  --gpu name, --disk, --grace and the POLISH_* / CHECK_MODELS --env knobs reach the pod.
"""
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import textwrap
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "scripts" / "jobs" / "polish.sh"
SETUP = ROOT / "scripts" / "pod_setup_polish.sh"
RECOG = ROOT / "scripts" / "pod_setup_recognition.sh"
ENTRY = ROOT / "scripts" / "pod_entry.sh"
PHASE_TABLE = {   # §8.2: phase -> commands that must appear in polish.sh
    "look": [r'"\$PY" -m wenart\.style "projects/\$p" --out "outputs/\$p/style\.json"',
             r'terms_arg=\(--photo-terms "\$terms"\)',
             r'"\$PY" -m wenart\.assets fetch --style "outputs/\$p/style\.json" --assets "\$ASSETS" --size 2k',
             r'"\$PY" -m wenart\.blender\.cli build --building "\$out/building_final\.json"',
             r'--preview-samples 32 --reuse',
             r'"\$PY" -m wenart\.blender\.cli render --scene "\$out/scene/scene\.blend" --out "\$out/renders"',
             r'--cameras all --samples "\$SAMPLES" --res "\$RES" --exposure auto --white-balance auto'],
    "controls": [r'"\$PY" -m wenart\.vision_check select-controls --project-out "\$out"',
                 r'--hide-sets "\$sets" --look-from "\$out/renders/render_manifest\.json"'],
    "polish": [r'"\$POLISH_PY" -m wenart\.polish "\$\{args\[@\]\}"', r'args=\(run\)',
               r'args=\(sweep --views auto --grid sweep\)', r'args=\(smoke --views "\$SMOKE_VIEWS"\)'],
    "gate": [r'"\$POLISH_PY" -m wenart\.gate calibrate --project-out'],
    "check": [r'"\$PY" -m wenart\.vision_check expected', r'"\$PY" -m wenart\.vision_check plan-crops',
              r'"\$PY" -m wenart\.vision_check run ', r'"\$PY" -m wenart\.vision_check preference ',
              r'"\$PY" -m wenart\.vision_check style-photo ', r'"\$PY" -m wenart\.vision_check combine ',
              r'"\$PY" -m wenart\.vision_check calibrate '],
    "report": [r'"\$PY" -m wenart\.report "\$kind" --project-out'],
    "tests": [r'"\$PY" -m pytest -m gpu tests/gpu/test_render\.py tests/gpu/test_check\.py',
              r'"\$POLISH_PY" -m pytest -m gpu tests/gpu/test_polish\.py'],
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _bash_function_body(text: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}\(\) \{{\n(.*?)^\}}", text, re.S | re.M)
    assert match, f"function {name} not found"
    return match.group(1)


# --------------------------------------------------------------------------
# Static checks
# --------------------------------------------------------------------------

@pytest.mark.parametrize("path", [JOB, SETUP, RECOG, ENTRY], ids=lambda p: p.name)
def test_scripts_follow_the_conventions(path):
    text = _text(path)
    assert text.startswith("#!/usr/bin/env bash\n")
    assert "set -Eeuo pipefail" in text
    assert re.search(r"^trap '[^']*' ERR$", text, re.M), "no ERR trap"
    assert os.access(path, os.X_OK), f"{path.name} is not executable"
    assert subprocess.run(["bash", "-n", str(path)], capture_output=True).returncode == 0


@pytest.mark.parametrize("path", [JOB, SETUP], ids=lambda p: p.name)
def test_m5_scripts_log_under_workspace_logs(path):
    text = _text(path)
    assert 'WS="${WENART_WS:-/workspace}"' in text and "LOGS=$WS/logs" in text
    assert 'mkdir -p "$LOGS"' in text or 'mkdir -p "$LOGS" ' in text


def test_every_phase_and_command_of_the_table_is_in_the_job():
    text = _text(JOB)
    for phase, patterns in PHASE_TABLE.items():
        assert re.search(rf"^phase_{phase}\(\) \{{", text, re.M), f"no phase_{phase}"
        assert f"if has_phase {phase}; then phase_{phase}; fi" in text
        body = _bash_function_body(text, f"phase_{phase}")
        flat = re.sub(r"\\\n\s*", "", body)          # join continued lines
        for pattern in patterns:
            assert re.search(pattern, flat), f"phase {phase}: no command matching {pattern}"
    # Phases run in the order of the table whatever the order in POLISH_PHASES.
    order = [text.index(f"if has_phase {p}; then") for p in PHASE_TABLE]
    assert order == sorted(order)
    assert 'smoke) DEFAULT_PHASES="look polish check"' in text
    assert 'sweep) DEFAULT_PHASES="look controls polish gate report"' in text
    assert 'final) DEFAULT_PHASES="look polish check report tests"' in text
    for knob in ("POLISH_PROJECTS:-synthetic-01 synthetic-03", "POLISH_MODE:-final", "RENDER_SAMPLES:-128",
                 "FORCE_RENDER", "FORCE_POLISH", "CHECK_MODELS:-qwen glm", "SMOKE_VIEWS"):
        assert knob in text, knob


def test_each_phase_uses_its_venv():
    text = re.sub(r"\\\n\s*", "", _text(JOB))
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        if re.search(r"-m wenart\.(polish|gate)\b", line) or "tests/gpu/test_polish.py" in line:
            assert '"$POLISH_PY"' in line and '"$PY"' not in line, line
        if re.search(r"-m wenart\.(style|assets|blender\.cli|vision_check|report)\b", line) \
                or "tests/gpu/test_render.py" in line:
            assert '"$PY"' in line and "POLISH_PY" not in line, line
    assert 'POLISH_PY="${WENART_POLISH_PY:-$FAST/venv-polish/bin/python}"' in text
    assert 'PY="${WENART_PY:-$WS/venv/bin/python}"' in text
    assert 'export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"' in text and "export HF_XET_HIGH_PERFORMANCE=1" in text
    # Offline only after the setup.
    assert text.index("run_stage setup-polish bash scripts/pod_setup_polish.sh") < text.index("export HF_HUB_OFFLINE=1")


def test_documented_run_command_uses_the_rtx_pro_4500_never_l4():
    text = _text(JOB)
    lines = [ln for ln in text.splitlines() if "gpu_run.py run" in ln]
    assert lines, "no documented run command"
    i = text.splitlines().index(lines[0])
    command = " ".join(text.splitlines()[i:i + 2])
    assert "--gpu 'RTX PRO 4500'" in command and "--disk 130" in command
    # The grace (results collection, 0.81 s per file) stays below the 900 s deadline margin.
    grace = re.search(r"--grace (\d+)", command)
    assert grace and 420 <= int(grace.group(1)) < 900
    assert "--env POLISH_MODE=" in command and "--env POLISH_PHASES=" in command
    assert "L4" not in command


def test_runner_accepts_the_documented_run_command(tmp_path, monkeypatch):
    """--gpu 'RTX PRO 4500' picks that catalog entry, --disk/--grace/--env reach the pod request."""
    spec = importlib.util.spec_from_file_location("gpu_run_m5", ROOT / "scripts" / "gpu_run.py")
    gpu_run = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gpu_run)
    catalog = [{"name": n, "id": f"NVIDIA {n}", "memory": m, "price": {"secure": p}, "availability": "HIGH"}
               for n, m, p in (("L4", 24, 0.49), ("RTX PRO 4000", 24, 0.57), ("RTX PRO 4500", 32, 0.72))]
    assert "RTX PRO 4500" in gpu_run.GPU_PRIORITY
    assert gpu_run.pick_gpu(catalog, {"RTX PRO 4500": "MEDIUM", "L4": "HIGH"}, "RTX PRO 4500")["name"] == "RTX PRO 4500"
    with pytest.raises(RuntimeError, match="no stock"):        # never silently another card
        gpu_run.pick_gpu(catalog, {"L4": "HIGH"}, "RTX PRO 4500")

    sent = {}

    def fake_api(method, path, body=None, **_kw):
        if method == "POST" and path == "/v2/pods":
            sent.update(body)
            raise gpu_run.ApiError("stop here: no pod in a test")
        raise AssertionError(f"unexpected API call {method} {path}")

    def fake_git(*args):
        return {"rev-parse": "abc123", "status": "", "branch": "origin/x"}.get(args[0], args[-1])

    monkeypatch.setenv("RUNPOD_API_KEY", "test-key")
    monkeypatch.setattr(gpu_run, "api", fake_api)
    monkeypatch.setattr(gpu_run, "git", fake_git)
    monkeypatch.setattr(gpu_run, "all_pods", lambda: [])
    monkeypatch.setattr(gpu_run, "find_volume", lambda: {"id": "vol1", "dataCenter": "EU-RO-1"})
    monkeypatch.setattr(gpu_run, "catalog", lambda: catalog)
    monkeypatch.setattr(gpu_run, "dc_availability", lambda dc: {"RTX PRO 4500": "MEDIUM", "L4": "HIGH"})
    monkeypatch.setattr(gpu_run, "spent_today", lambda pods=None: 0.0)
    monkeypatch.setattr(gpu_run, "log_run", lambda *a, **k: None)
    monkeypatch.setattr(gpu_run, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(gpu_run.signal, "signal", lambda *a: None)
    rc = gpu_run.main(["run", "--job", "scripts/jobs/polish.sh", "--gpu", "RTX PRO 4500", "--disk", "130",
                       "--grace", "420", "--env", "POLISH_MODE=final", "--env", "POLISH_PHASES=look polish check",
                       "--env", "CHECK_MODELS=qwen glm", "--env", "SMOKE_VIEWS=cam_a", "--env", "FORCE_POLISH=1"])
    assert rc == 1 and sent, "the runner never built the pod request"
    assert sent["gpu"]["id"] == "NVIDIA RTX PRO 4500" and sent["disk"] == 130
    env = sent["env"]
    assert env["JOB_SCRIPT"] == "scripts/jobs/polish.sh" and env["GRACE_S"] == "420"
    assert env["POLISH_MODE"] == "final" and env["POLISH_PHASES"] == "look polish check"
    assert env["CHECK_MODELS"] == "qwen glm" and env["SMOKE_VIEWS"] == "cam_a" and env["FORCE_POLISH"] == "1"


# --------------------------------------------------------------------------
# pod_entry.sh deadline, setup parts
# --------------------------------------------------------------------------

def test_pod_entry_exports_the_deadline_before_the_job():
    text = _text(ENTRY)
    body = _bash_function_body(text, "deadline_epoch")
    script = "\n".join(["set -Eeuo pipefail", "DEADLINE_MARGIN_S=900", "deadline_epoch() {", body, "}",
                        'echo "$(deadline_epoch 1000 7200) $(deadline_epoch 1000 600)"'])
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True).stdout.split()
    assert out == [str(1000 + 7200 - 900), str(1000 + 300)]   # 2 h run: 15 min margin; 10 min run: half
    assert "export WENART_DEADLINE" in text
    assert text.index("export WENART_DEADLINE") < text.index('bash "$JOB_SCRIPT"')
    assert text.index('START_S=$(date +%s)') < text.index("( sleep \"$MAX_RUNTIME_S\"")


def _setup_plan(tmp_path: Path, **env) -> str:
    run_env = dict(os.environ, WENART_WS=str(tmp_path / "ws"), WENART_FAST=str(tmp_path / "fast"),
                   WENART_PY=sys.executable, POLISH_SETUP_PLAN_ONLY="1")
    for key in ("POLISH_PHASES", "POLISH_MODE", "CHECK_MODELS"):
        run_env.pop(key, None)
    run_env.update(env)
    proc = subprocess.run(["bash", str(SETUP)], capture_output=True, text=True, env=run_env, timeout=60)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    return proc.stdout


def test_setup_parts_follow_the_phases(tmp_path):
    from wenart.vision_check.config import load_config

    models = load_config()["models"]
    plan = _setup_plan(tmp_path, POLISH_MODE="final", POLISH_PHASES="look polish check report tests")
    assert "PLAN venv=1 models=1 check=1" in plan
    # M7 §5.1/§9.5: the check part also builds (or reuses) LibreDWG 0.14 for the DWG projects.
    assert "PLAN RECOG_SETUP_PARTS=vllm libredwg models" in plan
    want = f"{models['qwen']['id']}@{models['qwen']['revision']} {models['glm']['id']}@{models['glm']['revision']}"
    assert f"PLAN BAKEOFF_MODELS={want}" in plan
    plan = _setup_plan(tmp_path, POLISH_MODE="sweep", POLISH_PHASES="check report tests", CHECK_MODELS="glm")
    # test_polish runs with the polish venv; tests/gpu/test_polish_backend.py loads the pinned polish models
    # (CUDA OOM retry of the review fix G1), so a tests pod downloads them too.
    assert "PLAN venv=1 models=1 check=1" in plan
    assert f"PLAN BAKEOFF_MODELS={models['glm']['id']}@{models['glm']['revision']}\n" in plan
    plan = _setup_plan(tmp_path, POLISH_MODE="final", POLISH_PHASES="check", POLISH_RECOG_PARTS="vllm models")
    assert "PLAN RECOG_SETUP_PARTS=vllm models\n" in plan
    plan = _setup_plan(tmp_path, POLISH_MODE="sweep", POLISH_PHASES="look controls gate report")
    assert "PLAN venv=1 models=1 check=0" in plan and "BAKEOFF_MODELS" not in plan
    plan = _setup_plan(tmp_path, POLISH_MODE="smoke", POLISH_PHASES="look")
    assert "PLAN venv=1 models=1 check=0" in plan
    plan = _setup_plan(tmp_path, POLISH_MODE="final", POLISH_PHASES="look report")
    assert "PLAN venv=0 models=0 check=0" in plan
    plan = _setup_plan(tmp_path, POLISH_MODE="final", POLISH_PHASES="report tests")
    assert "PLAN venv=1 models=1 check=0" in plan


def test_setup_installs_with_the_image_constraints_and_stamps_after_the_gpu_checks():
    text = _text(SETUP)
    assert "python3 -m pip freeze" in text and "'^(torch|torchvision|torchaudio|triton)=='" in text
    installs = [ln for ln in text.splitlines() if "pip install" in ln and "--upgrade pip" not in ln
                and not ln.lstrip().startswith("#") and "log " not in ln]
    assert installs and all('-c "$CONSTRAINTS"' in ln for ln in installs), installs
    for pin in ("DIFFUSERS_VERSION=0.40.0", "TRANSFORMERS_VERSION=5.18.0", "ACCELERATE_VERSION=1.15.0",
                "HUB_VERSION=1.33.0", "OPENCV_VERSION=4.14.0.94", "TORCHVISION_FALLBACK=0.24.1",
                '"safetensors>=0.8.0"', '"numpy>=2"', "https://download.pytorch.org/whl/cu128",
                "--system-site-packages", "--no-deps"):
        assert pin in text, pin
    assert "grep -viE '^huggingface[-_]hub'" in text       # pod_requirements.txt without its hub pin
    assert 'RECOG_PARTS="${POLISH_RECOG_PARTS:-vllm libredwg models}"' in text
    assert 'RECOG_SETUP_PARTS="$RECOG_PARTS" BAKEOFF_MODELS="$entries"' in text
    check = re.search(r"^POLISH_CHECK=\$\(cat <<'PY'\n(.*?)^PY\n\)", text, re.S | re.M)
    assert check, "POLISH_CHECK snippet not found"
    snippet = check.group(1)
    compile(snippet, "POLISH_CHECK", "exec")
    for needle in ("torch.bfloat16", '"sm_120" not in arch', "(1, 30, 8320, 128",
                   "sdpa_kernel([SDPBackend.FLASH_ATTENTION, SDPBackend.EFFICIENT_ATTENTION])",
                   "nms(", "ZImageControlNetPipeline", "ZImageControlNetModel", "Sam2Model", "Sam2Processor",
                   "AutoModelForDepthEstimation", "AutoModel,", "Owlv2ForObjectDetection", "Owlv2Processor",
                   "wenart.polish", "wenart.gate", "iter_modules"):
        assert needle in snippet, needle
    # The stamp is written only after the check passed.
    assert text.index('-c "$POLISH_CHECK"') < text.index('touch "$stamp"')
    # Downloads: snapshot_download with the pinned revision and allow patterns of both YAML files.
    assert "snapshot_download(m[\"repo\"], revision=m[\"revision\"], allow_patterns=m.get(\"allow_patterns\"))" in text
    assert '"polish" / "polish.yaml"' in text and '"gate" / "models.yaml"' in text
    for key in ("MemTotal", "MemAvailable", "nproc", "disk_free_gib_before", "versions", "setup_polish.json"):
        assert key in text, key


SESSION_PINS = {"numpy": "2.4.6", "pillow": "12.3.0", "opencv-python-headless": "5.0.0.93", "matplotlib": "3.11.2"}


def test_pod_requirements_pin_the_session_versions_and_venv_polish_drops_the_pins(tmp_path):
    """M7 §9.1: /workspace/venv gets the session's matplotlib, opencv, pillow and numpy (the pipeline's crops must
    hash as in the session; scripts/cloud-setup.sh pins the same); venv-polish keeps its own opencv pin and the
    unpinned rest (the versions its M5/M6 gate validation ran with)."""
    reqs = [ln.strip() for ln in (ROOT / "scripts" / "pod_requirements.txt").read_text().splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]
    pins = dict(ln.split("==", 1) for ln in reqs if "==" in ln)
    for name, version in SESSION_PINS.items():
        assert pins.get(name) == version, name
        assert f"{name}=={version}" in _text(ROOT / "scripts" / "cloud-setup.sh"), name
    snippet = next(ln.strip() for ln in _text(SETUP).splitlines() if "grep -viE '^huggingface[-_]hub'" in ln)
    cont = _text(SETUP).split(snippet, 1)[1].splitlines()[1].strip()          # the continued sed line
    requirements = str(ROOT / "scripts" / "pod_requirements.txt")
    command = (snippet.rstrip("\\").strip() + " " + cont).replace('"$REPO_DIR/scripts/pod_requirements.txt"',
                                                                  requirements)
    command = command.replace('> "$reqs" || true', "")
    out = subprocess.run(["bash", "-c", "set -o pipefail; " + command], capture_output=True, text=True, check=True)
    lines = [ln for ln in out.stdout.splitlines() if ln.strip() and not ln.startswith("#")]
    assert not [ln for ln in lines if ln.lower().startswith(("opencv", "huggingface"))]
    for name in ("numpy", "pillow", "matplotlib"):
        assert name in lines, name                                          # unpinned in venv-polish
    assert "ezdxf==1.4.4" in lines and "pytest==9.1.1" in lines


FAKE_HUB = '''
import json, os
from pathlib import Path


def snapshot_download(repo_id, *, revision=None, allow_patterns=None, **kwargs):
    log = Path(os.environ["FAKE_HUB_LOG"])
    calls = json.loads(log.read_text()) if log.is_file() else []
    calls.append({"repo": repo_id, "revision": revision, "allow_patterns": allow_patterns, "kwargs": sorted(kwargs)})
    log.write_text(json.dumps(calls))
    snap = Path(os.environ["FAKE_HUB_ROOT"]) / repo_id.replace("/", "--") / revision
    snap.mkdir(parents=True, exist_ok=True)
    for pattern in allow_patterns or []:
        if os.environ.get("FAKE_HUB_DROP") and os.environ["FAKE_HUB_DROP"] in pattern:
            continue
        name = pattern.replace("*", "config.json")
        (snap / name).parent.mkdir(parents=True, exist_ok=True)
        (snap / name).write_bytes(b"x" * 1000)
    return str(snap)
'''


def _heredoc(text: str, opener: str) -> str:
    """The body of the first <<'PY' here-document at or after ``opener``."""
    start = text.index("<<'PY'", text.index(opener))
    body_start = text.index("\n", start) + 1
    end = text.index("\nPY\n", body_start)
    return text[body_start:end + 1]


def test_setup_downloads_exactly_the_pinned_models(tmp_path):
    """The download snippet of pod_setup_polish.sh with a fake huggingface_hub.snapshot_download."""
    snippet = _heredoc(_text(SETUP), '"$VENV/bin/python" - "$REPO_DIR" "$STATE_DIR/models.json" <<\'PY\'')
    (tmp_path / "fakehub" / "huggingface_hub").mkdir(parents=True)
    (tmp_path / "fakehub" / "huggingface_hub" / "__init__.py").write_text(FAKE_HUB, encoding="utf-8")
    script = tmp_path / "download.py"
    script.write_text(snippet, encoding="utf-8")
    env = dict(os.environ, PYTHONPATH=str(tmp_path / "fakehub"), FAKE_HUB_LOG=str(tmp_path / "hub.json"),
               FAKE_HUB_ROOT=str(tmp_path / "hf"))
    out = tmp_path / "models.json"
    proc = subprocess.run([sys.executable, str(script), str(ROOT), str(out)], capture_output=True, text=True, env=env)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    from wenart.gate.api import load_models_config
    from wenart.polish.config import load_config

    want = [(m["repo"], m["revision"], m["allow_patterns"]) for m in load_config()["models"].values()]
    want += [(m["repo"], m["revision"], m["allow_patterns"]) for m in load_models_config()["models"].values()]
    det = load_models_config()["detect"]           # the OWLv2 detector (M7 §8.1), outside the gate's models
    want.append((det["repo"], det["revision"], det["allow_patterns"]))
    calls = json.loads((tmp_path / "hub.json").read_text())
    assert [(c["repo"], c["revision"], c["allow_patterns"]) for c in calls] == want
    assert det["repo"] == "google/owlv2-base-patch16-ensemble"
    assert det["revision"] == "cfd3195ba4ea9592eec887ded089f4c08eff231d"
    records = json.loads(out.read_text())["models"]
    assert [r["role"] for r in records] == ["base", "controlnet", "depth", "sam", "dino", "detect"]
    assert records[-1]["group"] == "gate" and records[-1]["licence"] == "Apache-2.0"
    assert all(r["ok"] and r["bytes"] > 0 and r["licence"] and r["seconds"] is not None for r in records)
    assert "download polish/controlnet alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1@5155fc56d178: ok" in proc.stdout
    # A snapshot without the ControlNet file is a failed download (exit 1, error recorded).
    env.update(FAKE_HUB_DROP="8steps.safetensors", FAKE_HUB_ROOT=str(tmp_path / "hf2"))
    proc = subprocess.run([sys.executable, str(script), str(ROOT), str(out)], capture_output=True, text=True, env=env)
    assert proc.returncode == 1
    failed = [r for r in json.loads(out.read_text())["models"] if not r["ok"]]
    assert [r["role"] for r in failed] == ["controlnet"] and "missing in the snapshot" in failed[0]["error"]


def test_setup_summary_json(tmp_path):
    text = _text(SETUP)
    snippet = _heredoc(text, 'python3 - "$out_dir/setup_polish.json" "$STATE_DIR"')
    state = tmp_path / "state"
    state.mkdir()
    (state / "venv_check.txt").write_text('pip noise\nPOLISH_CHECK {"torch": "2.9.1+cu128", "diffusers": "0.40.0"}\n')
    (state / "models.json").write_text(json.dumps({"models": [{"role": "base", "bytes": 2_000_000_000}]}))
    constraints = tmp_path / "image-constraints.txt"
    constraints.write_text("torch==2.9.1+cu128\ntriton==3.5.1\n")
    script = tmp_path / "summary.py"
    script.write_text(snippet, encoding="utf-8")
    out = tmp_path / "setup_polish.json"
    proc = subprocess.run([sys.executable, str(script), str(out), str(state), "final", "look polish check", "qwen glm",
                           "venv=ok:120", "models=ok:300", "check=failed:40", "107374182400", "53687091200",
                           str(constraints)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(out.read_text())
    assert data["parts"] == {"venv": {"state": "ok", "seconds": 120}, "models": {"state": "ok", "seconds": 300},
                             "check": {"state": "failed", "seconds": 40}}
    assert data["versions"] == {"torch": "2.9.1+cu128", "diffusers": "0.40.0"} and data["models_gb"] == 2.0
    assert data["disk_free_gib_before"] == 100.0 and data["disk_free_gib_after"] == 50.0
    assert data["image_constraints"] == ["torch==2.9.1+cu128", "triton==3.5.1"]
    assert data["phases"] == ["look", "polish", "check"] and data["check_models"] == ["qwen", "glm"]
    assert data["nproc"] >= 1 and "MemTotal_gib" in data and "MemAvailable_gib" in data


def test_recognition_setup_parts_switch():
    text = _text(RECOG)
    assert 'RECOG_PARTS_ALL="vllm paddle libredwg models"' in text
    assert 'read -r -a PARTS <<< "${RECOG_SETUP_PARTS:-$RECOG_PARTS_ALL}"' in text   # default: everything
    for part in ("vllm", "paddle", "libredwg", "models"):
        assert f"if part_on {part}; then" in text
    # Pinned revisions: "<id>@<revision>" entries download that revision.
    assert 'model=${entry%@*}' in text and 'REV_ARG=(--revision "${entry##*@}")' in text
    assert '"$VENV_VLLM/bin/hf" download "$model" "${REV_ARG[@]}"' in text
    # Parsing and part_on in isolation.
    start = text.index('RECOG_PARTS_ALL="vllm paddle libredwg models"')
    end = text.index('log "parts: ${PARTS[*]}"')
    snippet = text[start:end]
    for parts, on, rc in (("", "vllm paddle libredwg models", 0), ("vllm models", "vllm models", 0),
                          ("vllm ocr", "", 2)):
        script = "\n".join(["set -Eeuo pipefail", 'log() { echo "log: $*"; }', f'RECOG_SETUP_PARTS="{parts}"'
                            if parts else "unset RECOG_SETUP_PARTS", snippet,
                            'for p in vllm paddle libredwg models; do part_on "$p" && echo "ON $p"; done; true'])
        proc = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        assert proc.returncode == rc, proc.stdout + proc.stderr
        assert [ln[3:] for ln in proc.stdout.splitlines() if ln.startswith("ON ")] == on.split()


# --------------------------------------------------------------------------
# polish.sh in a sandbox
# --------------------------------------------------------------------------

FAKE_PY = r'''#!__PYTHON__
"""Fake interpreter for polish.sh tests: records the call, writes what the real CLI writes."""
import json, os, re, sys
from pathlib import Path

REAL, ROLE = "__PYTHON__", "__ROLE__"
argv = sys.argv[1:]
if argv[:1] in (["-c"], ["-"]):
    os.execv(REAL, [REAL] + argv)
ENV_KEYS = ("HF_HUB_OFFLINE", "PYTORCH_CUDA_ALLOC_CONF", "WENART_DEADLINE", "RENDER_TEST_PROJECTS",
            "CHECK_TEST_PROJECTS", "POLISH_TEST_PROJECTS", "CHECK_MODELS", "WENART_OUTPUTS", "HF_HOME",
            "WENART_CPU_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENCV_FOR_THREADS_NUM")
record = {"role": ROLE, "argv": argv, "cwd": os.getcwd(), "env": {k: os.environ.get(k) for k in ENV_KEYS}}
if os.environ.get("FAKE_SEEN"):        # what the results folder holds when this stage starts
    res = Path(os.environ["WENART_RESULTS"])
    record["results"] = sorted(str(f.relative_to(res)) for f in res.rglob("*") if f.is_file()) if res.is_dir() else []
with open(os.environ["FAKE_CALLS"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps(record) + "\n")
fail = os.environ.get("FAKE_FAIL")
if fail and re.search(fail, " ".join(argv)):
    print("fake failure", file=sys.stderr)
    sys.exit(1)


def opt(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


def write(path, text="{}", size=None):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if size:
        p.write_bytes(b"x" * size)
    else:
        p.write_text(text, encoding="utf-8")


mod = argv[1] if argv[:1] == ["-m"] else None
sub = argv[2] if len(argv) > 2 else None
out = Path(opt("--project-out", ".")) if "--project-out" in argv else None
if mod == "wenart.style":
    write(opt("--out"))
    for i in range(2, int(os.environ.get("FAKE_STYLE_PROFILES", "1")) + 1):   # a brief with several styles
        write(Path(opt("--out")).with_name(f"style_{i}.json"))
elif mod == "wenart.blender.cli" and sub == "build":
    d = Path(opt("--out"))
    write(d / "scene.blend", size=10)
    write(d / "scene_manifest.json")
    write(d / "build.log", "build log\n")
    print("BUILD_REUSED fp")
elif mod == "wenart.blender.cli" and sub == "render":
    d = Path(opt("--out"))
    if "--hide-sets" in argv:
        write(d / "render.log", "control renders\n")      # run_blender's log_path = <out>/render.log
        for item in opt("--hide-sets").split(";"):
            cam, rest = item.split(":")
            hid = rest.split("+")[0]
            write(d / f"hide_{hid}" / "render_manifest.json")
            write(d / f"hide_{hid}" / f"{cam}_preview.jpg", size=1000)
            write(d / f"hide_{hid}" / f"{cam}.png", size=1000)
    else:
        write(d / "render_manifest.json")
        write(d / "render.log", "DEVICE OPTIX\nRENDERED cam_a\n")
        write(d / "cam_a_preview.jpg", size=2000)
        write(d / "cam_big_preview.jpg", size=400 * 1024)
        write(d / "cam_a.png", size=5000)
elif mod == "wenart.vision_check":
    c = out / "check"
    if sub == "select-controls":
        write(c / "controls.json")
        print("CONTROL\tsofa_1\tcam_a\t0\tcontrols/hide_sofa_1")
        print("CONTROL\twin_2\tcam_b\t1\tcontrols/hide_win_2")
        print("HIDE_SETS\tcam_a:sofa_1;cam_b:win_2+plug")
    elif sub == "expected":
        write(c / "expected_views.json")
    elif sub == "plan-crops":
        write(c / "cam_a_plan.jpg", size=1500)
    elif sub in ("run", "preference"):
        write(c / f"answers_{opt('--model-key')}.json")
    elif sub == "style-photo":
        write(opt("--out") or (c / "style_photos.json"))
    elif sub == "combine":
        write(c / "check_manifest.json")
        write(c / "cam_a_cycles_check.jpg", size=1500)
        if os.environ.get("FAKE_COARSE_MTIME"):     # 1 s timestamps: the mtime lags the write by up to 1 s
            import time
            t = time.time() - 1.0
            os.utime(c / "check_manifest.json", (t, t))
    elif sub == "calibrate":
        write(c / "check_calibration.json")
        write(c / "check_report.md", "# Check\n")
elif mod == "wenart.style.photos":
    write(opt("--out"))
elif mod == "wenart.polish":
    d = out / "polish" / ({"run": "", "sweep": "sweep", "smoke": "smoke"}[sub])
    write(d / "polish_manifest.json")
    write(d / "polish_report.md", "# Polish\n")
    write(d / "cam_a_a1_preview.jpg", size=3000)
    write(d / "cam_a_a1_gate.jpg", size=3000)
    write(d / "cam_a_a1.png", size=9000)
elif mod == "wenart.gate":
    write(out / "gate" / "gate_calibration.json")
    write(out / "gate" / "gate_calibration.md", "# Gate\n")
elif mod == "wenart.report":
    d = out / "final"
    if sub == "final":
        write(d / "final_manifest.json")
        write(d / "final_report.md", "# Final\n")
        write(d / "contact_L0.jpg", size=4000)
        write(d / "cam_a_final_preview.jpg", size=4000)
    else:
        write(d / "sweep_report.md", "# Sweep\n")
elif mod == "pytest":
    write(opt("--junitxml") or [a.split("=", 1)[1] for a in argv if a.startswith("--junitxml=")][0], "<testsuite/>")
'''

FAKE_SETUP = """#!/usr/bin/env bash
echo "fake setup: offline=${HF_HUB_OFFLINE:-unset} phases=$POLISH_PHASES mode=$POLISH_MODE models=$CHECK_MODELS" \
  "threads=${WENART_CPU_THREADS:-unset} omp=${OMP_NUM_THREADS:-unset}" >> "$FAKE_SETUP_LOG"
mkdir -p "$WENART_FAST/venv-polish"
if [ "${FAKE_SETUP_STAMP:-1}" = "1" ]; then touch "$WENART_FAST/venv-polish/.polish-test"; fi
if [ "${FAKE_SETUP_JSON:-1}" = "1" ]; then echo '{"kind": "setup_polish"}' > "$WS_LOGS/setup_polish.json"; fi
exit "${FAKE_SETUP_RC:-0}"
"""

FAKE_VLLM = """#!/usr/bin/env bash
echo "VLLM_USE_FLASHINFER_SAMPLER=$VLLM_USE_FLASHINFER_SAMPLER HF_HUB_OFFLINE=$HF_HUB_OFFLINE ARGS $*" >> "$FAKE_VLLM_LOG"
exec sleep 300
"""

# cp on the job's PATH: one JSON line of arguments per process, then the real cp.
FAKE_CP = """#!/usr/bin/env bash
if [ -n "${FAKE_CP_LOG:-}" ]; then
  __PYTHON__ -c 'import json, sys; print(json.dumps(sys.argv[1:]))' "$@" >> "$FAKE_CP_LOG"
fi
exec __CP__ "$@"
"""


def _exe(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


class Sandbox:
    """A fake /workspace + /opt/wenart for one run of polish.sh."""

    def __init__(self, tmp_path: Path):
        self.root = tmp_path
        self.ws = tmp_path / "ws"
        self.fast = tmp_path / "fast"
        self.repo = self.ws / "repo"
        self.results = tmp_path / "results"
        self.calls_log = tmp_path / "calls.jsonl"
        self.vllm_log = tmp_path / "vllm.log"
        self.setup_log = tmp_path / "setup.log"
        self.cp_log = tmp_path / "cp.jsonl"
        bin_dir = tmp_path / "bin"
        _exe(bin_dir / "curl", "#!/usr/bin/env bash\nexit 0\n")
        _exe(bin_dir / "cp", FAKE_CP.replace("__PYTHON__", sys.executable).replace("__CP__", shutil.which("cp")))
        self.py = _exe(tmp_path / "venv" / "bin" / "python",
                       FAKE_PY.replace("__PYTHON__", sys.executable).replace("__ROLE__", "PY"))
        self.polish_py = _exe(self.fast / "venv-polish" / "bin" / "python",
                              FAKE_PY.replace("__PYTHON__", sys.executable).replace("__ROLE__", "POLISH_PY"))
        _exe(self.fast / "venv-vllm" / "bin" / "vllm", FAKE_VLLM)
        _exe(self.repo / "scripts" / "pod_setup_polish.sh", FAKE_SETUP)
        check_yaml = self.repo / "wenart" / "vision_check" / "check.yaml"
        check_yaml.parent.mkdir(parents=True)
        check_yaml.write_text(_text(ROOT / "wenart" / "vision_check" / "check.yaml"), encoding="utf-8")
        # synthetic-01: only the committed building (copied by the job); synthetic-03: on the volume.
        committed = self.repo / "results" / "furniture" / "synthetic-01" / "building_final.json"
        committed.parent.mkdir(parents=True)
        committed.write_text('{"committed": true}', encoding="utf-8")
        on_volume = self.repo / "outputs" / "synthetic-03" / "building_final.json"
        on_volume.parent.mkdir(parents=True)
        on_volume.write_text('{"volume": true}', encoding="utf-8")
        self.env = {
            "PATH": f"{bin_dir}:{os.environ['PATH']}", "HOME": str(tmp_path), "LANG": "C.UTF-8",
            "WENART_WS": str(self.ws), "WENART_FAST": str(self.fast), "WENART_PY": str(self.py),
            "WENART_RESULTS": str(self.results), "JOB_ID": "test", "FAKE_CALLS": str(self.calls_log),
            "FAKE_VLLM_LOG": str(self.vllm_log), "FAKE_SETUP_LOG": str(self.setup_log),
            "WS_LOGS": str(self.ws / "logs"), "SERVER_WAIT_S": "30", "FAKE_CP_LOG": str(self.cp_log),
        }

    def run(self, **env) -> subprocess.CompletedProcess:
        run_env = dict(self.env)
        run_env.update({k: str(v) for k, v in env.items()})
        proc = subprocess.run(["bash", str(JOB)], capture_output=True, text=True, env=run_env, timeout=180)
        self.output = proc.stdout + proc.stderr
        return proc

    def calls(self) -> list[dict]:
        if not self.calls_log.is_file():
            return []
        return [json.loads(ln) for ln in self.calls_log.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def commands(self) -> list[str]:
        """``<ROLE> <module> <subcommand>`` per call, in order (without ``-c`` helpers)."""
        out = []
        for c in self.calls():
            a = c["argv"]
            out.append(" ".join([c["role"]] + a[1:3]) if a[:1] == ["-m"] else c["role"] + " " + " ".join(a[:2]))
        return out

    def vllm_starts(self) -> list[str]:
        return self.vllm_log.read_text(encoding="utf-8").splitlines() if self.vllm_log.is_file() else []

    def cp_calls(self) -> list[list[str]]:
        """The arguments of every cp process the job started, in order."""
        if not self.cp_log.is_file():
            return []
        return [json.loads(ln) for ln in self.cp_log.read_text(encoding="utf-8").splitlines() if ln.strip()]

    def write_old(self, path: Path, data: bytes = b"x" * 500, age_s: float = 3600) -> Path:
        """A file an earlier job left on the volume (``age_s`` old)."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        t = time.time() - age_s
        os.utime(path, (t, t))
        return path


def _find(calls, module, sub=None, project=None):
    found = []
    for c in calls:
        a = c["argv"]
        if a[:2] != ["-m", module] or (sub is not None and (len(a) < 3 or a[2] != sub)):
            continue
        joined = " ".join(a)
        if project is not None and f"outputs/{project}" not in joined:
            continue
        found.append(c)
    return found


def _arg(call, name):
    a = call["argv"]
    return a[a.index(name) + 1]


@pytest.fixture(scope="module")
def final_run(tmp_path_factory):
    box = Sandbox(tmp_path_factory.mktemp("final"))
    proc = box.run(POLISH_MODE="final")
    return box, proc


def test_final_mode_runs_its_phases_in_order(final_run):
    box, proc = final_run
    assert proc.returncode == 0, box.output
    cmds = box.commands()
    first = {key: next(i for i, c in enumerate(cmds) if c.startswith(key)) for key in (
        "PY wenart.style", "PY wenart.assets", "PY wenart.blender.cli build", "PY wenart.blender.cli render",
        "POLISH_PY wenart.polish run", "PY wenart.vision_check expected", "PY wenart.vision_check run",
        "PY wenart.vision_check combine", "PY wenart.report final", "PY pytest", "POLISH_PY pytest")}
    assert list(first.values()) == sorted(first.values()), cmds
    assert not [c for c in cmds if "select-controls" in c or "wenart.gate" in c or "sweep" in c]
    # Style and assets of every project before the first build.
    builds = [i for i, c in enumerate(cmds) if c.startswith("PY wenart.blender.cli build")]
    assets = [i for i, c in enumerate(cmds) if c.startswith("PY wenart.assets")]
    assert len(builds) == 2 and len(assets) == 2 and max(assets) < min(builds)
    assert "all stages ok" in box.output


def test_final_mode_commands_and_environment(final_run):
    box, _proc = final_run
    calls = box.calls()
    for p in ("synthetic-01", "synthetic-03"):
        (build,) = _find(calls, "wenart.blender.cli", "build", p)
        assert _arg(build, "--building") == f"outputs/{p}/building_final.json" and "--reuse" in build["argv"]
        assert _arg(build, "--preview-samples") == "32" and _arg(build, "--style") == f"outputs/{p}/style.json"
        (render,) = _find(calls, "wenart.blender.cli", "render", p)
        for flag, value in (("--cameras", "all"), ("--samples", "128"), ("--res", "1920x1080"),
                            ("--exposure", "auto"), ("--white-balance", "auto")):
            assert _arg(render, flag) == value
        assert "--force" not in render["argv"]
        (polish,) = _find(calls, "wenart.polish", "run", p)
        assert polish["role"] == "POLISH_PY" and polish["env"]["HF_HUB_OFFLINE"] == "1"
        assert polish["env"]["PYTORCH_CUDA_ALLOC_CONF"] == "expandable_segments:True"
        assert "--force" not in polish["argv"]
        runs = _find(calls, "wenart.vision_check", "run", p)
        assert [_arg(c, "--model-key") for c in runs] == ["qwen", "glm"]
        assert all(_arg(c, "--kinds") == "cycles,polished" and _arg(c, "--server") == "http://127.0.0.1:8001/v1"
                   for c in runs)
        prefs = _find(calls, "wenart.vision_check", "preference", p)
        assert [_arg(c, "--kinds") for c in prefs] == ["polished", "polished"]
        # As many calls at once as the server takes sequences (--max-num-seqs 2 below 40 GB).
        assert [_arg(c, "--workers") for c in runs + prefs] == ["2"] * 4
        photos = _find(calls, "wenart.vision_check", "style-photo", p)
        tests = [c for c in photos if "--photo" in c["argv"]]
        assert len(photos) == 4 and len(tests) == 2
        assert all(_arg(c, "--photo") == "tests/fixtures/style_photo_synthetic-03_salon.jpg"
                   and _arg(c, "--out") == f"outputs/{p}/check/style_photo_test.json" for c in tests)
        assert _find(calls, "wenart.vision_check", "combine", p) and _find(calls, "wenart.vision_check", "calibrate", p)
        # The test photo's passes are agreed for the GPU test; the project photos' passes become the
        # terms the next look phase passes to wenart.style --photo-terms.
        combined = {c["argv"][3]: _arg(c, "--out") for c in _find(calls, "wenart.style.photos", "combine", p)}
        assert combined == {f"outputs/{p}/check/style_photo_test.json": f"outputs/{p}/check/style_photo_test_terms.json",
                            f"outputs/{p}/check/style_photos.json": f"outputs/{p}/check/style_photo_terms.json"}
        (report,) = _find(calls, "wenart.report", "final", p)
        assert report["role"] == "PY"
    # Every call after the setup is offline; the setup itself is not.
    assert all(c["env"]["HF_HUB_OFFLINE"] == "1" for c in calls if c["argv"][:1] == ["-m"])
    assert "offline=unset" in box.setup_log.read_text(encoding="utf-8")
    assert "phases=look polish check report tests mode=final models=qwen glm" in box.setup_log.read_text()
    # GPU tests: the render/check tests with PY, the polish tests with POLISH_PY, the projects exported.
    pytests = [c for c in calls if c["argv"][:2] == ["-m", "pytest"]]
    assert [c["role"] for c in pytests] == ["PY", "POLISH_PY"]
    assert "tests/gpu/test_render.py" in pytests[0]["argv"] and "tests/gpu/test_check.py" in pytests[0]["argv"]
    assert "tests/gpu/test_polish.py" in pytests[1]["argv"]
    # The Z-Image backend's CUDA OOM retry with the real models (review fix G1), in the same polish-venv run.
    assert "tests/gpu/test_polish_backend.py" in pytests[1]["argv"]
    for c in pytests:
        assert c["env"]["RENDER_TEST_PROJECTS"] == "synthetic-01 synthetic-03"
        assert c["env"]["CHECK_TEST_PROJECTS"] == "synthetic-01 synthetic-03"
        assert c["env"]["POLISH_TEST_PROJECTS"] == "synthetic-01 synthetic-03"
        assert c["env"]["CHECK_MODELS"] == "qwen glm" and c["env"]["WENART_OUTPUTS"] == str(box.repo / "outputs")
    assert (box.results / "junit-render-check.xml").is_file() and (box.results / "junit-polish.xml").is_file()


def test_final_mode_serves_one_model_at_a_time_with_the_check_flags(final_run):
    from wenart.vision_check.config import load_config

    box, _proc = final_run
    models = load_config()["models"]
    starts = box.vllm_starts()
    assert len(starts) == 2
    for line, key in zip(starts, ("qwen", "glm")):
        m = models[key]
        assert line.startswith("VLLM_USE_FLASHINFER_SAMPLER=0 HF_HUB_OFFLINE=1 ARGS serve " + m["id"] + " ")
        assert f"--revision {m['revision']}" in line and f"--served-model-name {m['id']}" in line
        assert '--limit-mm-per-prompt {"image":2}' in line and "--port 8001" in line
        assert "--gpu-memory-utilization 0.90" in line
        assert "--quantization fp8 --max-model-len 8192 --max-num-seqs 2" in line     # no nvidia-smi: < 40 GB
        assert ("--reasoning-parser glm45" in line) == (key == "glm")
    # Server qwen is stopped before glm starts: every qwen call comes before every glm call.
    order = [_arg(c, "--model-key") for c in box.calls() if "--model-key" in c["argv"]]
    assert order == sorted(order, key=lambda k: ["qwen", "glm"].index(k))
    assert box.output.count("stopping vllm") == 2


def test_final_mode_copies_the_building_and_mirrors_the_results(final_run):
    box, _proc = final_run
    copied = box.repo / "outputs" / "synthetic-01" / "building_final.json"
    assert json.loads(copied.read_text()) == {"committed": True}
    assert json.loads((box.repo / "outputs" / "synthetic-03" / "building_final.json").read_text()) == {"volume": True}
    r = box.results
    for p in ("synthetic-01", "synthetic-03"):
        for rel in (f"renders/{p}/render_manifest.json", f"renders/{p}/cam_a_preview.jpg", f"renders/{p}/render.log",
                    f"renders/{p}/scene_manifest.json", f"renders/{p}/style.json",
                    f"polish/{p}/polish_manifest.json", f"polish/{p}/polish_report.md",
                    f"polish/{p}/cam_a_a1_preview.jpg", f"polish/{p}/cam_a_a1_gate.jpg",
                    f"check/{p}/check_manifest.json", f"check/{p}/cam_a_plan.jpg", f"check/{p}/cam_a_cycles_check.jpg",
                    f"check/{p}/style_photo_test.json", f"check/{p}/answers_qwen.json", f"check/{p}/answers_glm.json",
                    f"final/{p}/final_manifest.json", f"final/{p}/final_report.md", f"final/{p}/contact_L0.jpg",
                    f"final/{p}/cam_a_final_preview.jpg"):
            assert (r / rel).is_file(), rel
        assert not (r / f"renders/{p}/cam_big_preview.jpg").exists()     # > 300 KB
        assert not list(r.rglob("*.png")) and not list(r.rglob("*.blend"))
    assert (r / "polish-test.log").is_file() and (r / "setup_polish.json").is_file()
    assert (r / "logs" / "vllm-qwen.log").is_file() and (r / "logs" / "vllm-glm.log").is_file()


def test_sweep_mode_renders_the_controls_and_calibrates_the_gate(tmp_path):
    box = Sandbox(tmp_path)
    proc = box.run(POLISH_MODE="sweep", RENDER_SAMPLES="64", FORCE_RENDER="1", FORCE_POLISH="1")
    assert proc.returncode == 0, box.output
    calls = box.calls()
    cmds = box.commands()
    assert not [c for c in cmds if "wenart.vision_check run" in c or "pytest" in c or "report final" in c]
    assert box.vllm_starts() == []
    for p in ("synthetic-01", "synthetic-03"):
        (render,) = [c for c in _find(calls, "wenart.blender.cli", "render", p) if "--hide-sets" not in c["argv"]]
        assert "--force" in render["argv"] and _arg(render, "--samples") == "64"
        (sel,) = _find(calls, "wenart.vision_check", "select-controls", p)
        (ctl,) = [c for c in _find(calls, "wenart.blender.cli", "render", p) if "--hide-sets" in c["argv"]]
        assert calls.index(render) < calls.index(sel) < calls.index(ctl)
        assert _arg(ctl, "--hide-sets") == "cam_a:sofa_1;cam_b:win_2+plug"
        assert _arg(ctl, "--look-from") == f"outputs/{p}/renders/render_manifest.json"
        assert _arg(ctl, "--out") == f"outputs/{p}/controls" and _arg(ctl, "--samples") == "64"
        assert _arg(ctl, "--res") == "1920x1080" and "--force" not in ctl["argv"]
        (sweep,) = _find(calls, "wenart.polish", "sweep", p)
        assert sweep["role"] == "POLISH_PY" and _arg(sweep, "--views") == "auto" and _arg(sweep, "--grid") == "sweep"
        assert "--force" in sweep["argv"]
        (gate,) = _find(calls, "wenart.gate", "calibrate", p)
        assert gate["role"] == "POLISH_PY" and gate["env"]["PYTORCH_CUDA_ALLOC_CONF"] == "expandable_segments:True"
        assert calls.index(sweep) < calls.index(gate)
        (report,) = _find(calls, "wenart.report", "sweep", p)
        assert calls.index(gate) < calls.index(report)
        r = box.results
        assert (r / f"renders/{p}/controls/hide_sofa_1/render_manifest.json").is_file()
        assert (r / f"renders/{p}/controls/hide_win_2/cam_b_preview.jpg").is_file()
        assert (r / f"polish/{p}/sweep/polish_manifest.json").is_file()
        assert (r / f"gate/{p}/gate_calibration.json").is_file() and (r / f"gate/{p}/gate_calibration.md").is_file()


def test_check_only_sweep_run_and_a_failing_stage(tmp_path):
    box = Sandbox(tmp_path)
    proc = box.run(POLISH_MODE="sweep", POLISH_PHASES="tests report check", CHECK_MODELS="glm",
                   FAKE_FAIL=r"vision_check plan-crops --project-out outputs/synthetic-01")
    assert proc.returncode == 1, box.output
    assert "FAILED stages: plan-crops-synthetic-01" in box.output
    cmds = box.commands()
    assert not [c for c in cmds if "blender" in c or "wenart.polish" in c or "wenart.gate" in c]
    calls = box.calls()
    runs = _find(calls, "wenart.vision_check", "run")
    assert len(runs) == 2 and all(_arg(c, "--kinds") == "cycles,controls,plan_ab" and _arg(c, "--model-key") == "glm"
                                  for c in runs)
    assert [_arg(c, "--kinds") for c in _find(calls, "wenart.vision_check", "preference")] == ["sweep", "sweep"]
    # Order of the table, not of POLISH_PHASES: check, then report, then tests.
    idx = {k: next(i for i, c in enumerate(cmds) if k in c) for k in ("vision_check run", "report sweep", "pytest")}
    assert idx["vision_check run"] < idx["report sweep"] < idx["pytest"]
    # Only the render/check GPU tests (no polish run manifest in sweep mode); no rendered project.
    pytests = [c for c in calls if c["argv"][:2] == ["-m", "pytest"]]
    assert [c["role"] for c in pytests] == ["PY"]
    assert pytests[0]["env"]["RENDER_TEST_PROJECTS"] == "" and pytests[0]["env"]["POLISH_TEST_PROJECTS"] == ""
    assert pytests[0]["env"]["CHECK_TEST_PROJECTS"] == "synthetic-01 synthetic-03"
    assert len(box.vllm_starts()) == 1 and "--reasoning-parser glm45" in box.vllm_starts()[0]


FAKE_NVIDIA_SMI = """#!/usr/bin/env bash
case "$*" in
  *nounits*) echo "49140" ;;
  *) echo "NVIDIA RTX A6000, 49140 MiB" ;;
esac
"""


def test_check_calls_on_a_48_gb_card_match_the_server_sequences(tmp_path):
    """From 40 GB of VRAM vLLM serves 4 sequences (bf16, 16384 context): `vision_check run` and
    `preference` then send 4 calls at once (review G4: check.yaml calls.workers 2 matches the 2 sequences
    below 40 GB only)."""
    box = Sandbox(tmp_path)
    _exe(tmp_path / "bin" / "nvidia-smi", FAKE_NVIDIA_SMI)
    proc = box.run(POLISH_MODE="sweep", POLISH_PHASES="check", POLISH_PROJECTS="synthetic-01", CHECK_MODELS="qwen")
    assert proc.returncode == 0, box.output
    (start,) = box.vllm_starts()
    assert "--max-model-len 16384 --max-num-seqs 4" in start and "--quantization" not in start
    calls = box.calls()
    asked = _find(calls, "wenart.vision_check", "run") + _find(calls, "wenart.vision_check", "preference")
    assert len(asked) == 2 and [_arg(c, "--workers") for c in asked] == ["4", "4"]


def test_deadline_skips_the_heavy_phases_but_reports_and_copies(tmp_path):
    box = Sandbox(tmp_path)
    proc = box.run(POLISH_MODE="final", WENART_DEADLINE=str(int(time.time()) - 5))
    assert proc.returncode == 1, box.output
    cmds = box.commands()
    heavy = [c for c in cmds if any(k in c for k in ("wenart.style", "wenart.assets", "blender", "wenart.polish",
                                                     "vision_check"))]
    assert heavy == [], heavy
    assert box.vllm_starts() == []
    assert [c for c in cmds if "wenart.report final" in c] == ["PY wenart.report final"] * 2
    assert "INCOMPLETE: the deadline stopped" in box.output and "deadline passed" in box.output
    assert (box.results / "final" / "synthetic-01" / "final_report.md").is_file()
    assert (box.results / "polish-test.log").is_file()


def test_smoke_mode_and_a_setup_without_stamp(tmp_path):
    box = Sandbox(tmp_path)
    proc = box.run(POLISH_MODE="smoke", POLISH_PROJECTS="synthetic-01", SMOKE_VIEWS="cam_a,cam_b",
                   FAKE_SETUP_STAMP="0", FAKE_SETUP_RC="1")
    assert proc.returncode == 1, box.output
    calls = box.calls()
    assert not _find(calls, "wenart.polish")          # venv-polish not stamped: no polish attempt
    assert "polish-venv" in box.output and "setup-polish" in box.output
    runs = _find(calls, "wenart.vision_check", "run")
    assert [_arg(c, "--kinds") for c in runs] == ["cycles", "cycles"]
    assert not _find(calls, "wenart.vision_check", "preference")
    assert not [c for c in calls if c["argv"][:2] == ["-m", "pytest"]]
    assert not _find(calls, "wenart.report")
    assert {c["argv"][c["argv"].index("--project-out") + 1] for c in calls if "--project-out" in c["argv"]} == \
        {"outputs/synthetic-01"}

    box2 = Sandbox(tmp_path / "again")
    proc = box2.run(POLISH_MODE="smoke", POLISH_PROJECTS="synthetic-01", SMOKE_VIEWS="cam_a,cam_b",
                    POLISH_PHASES="polish")
    assert proc.returncode == 0, box2.output
    (smoke,) = _find(box2.calls(), "wenart.polish", "smoke")
    assert _arg(smoke, "--views") == "cam_a,cam_b" and smoke["role"] == "POLISH_PY"
    assert (box2.results / "polish" / "synthetic-01" / "smoke" / "polish_manifest.json").is_file()


def test_bad_mode_phase_or_missing_building(tmp_path):
    box = Sandbox(tmp_path)
    assert box.run(POLISH_MODE="fast").returncode == 2
    assert "unknown POLISH_MODE" in box.output
    assert box.run(POLISH_PHASES="look polsh").returncode == 2
    assert "unknown phase 'polsh'" in box.output
    proc = box.run(POLISH_PROJECTS="synthetic-02", POLISH_PHASES="report")
    assert proc.returncode == 1 and "building-synthetic-02" in box.output
    assert not _find(box.calls(), "wenart.report")


def test_copy_results_runs_under_a_lock_after_every_stage_and_on_exit():
    text = _text(JOB)
    assert "copy_results_locked" in _bash_function_body(text, "run_stage")
    exit_trap = re.search(r"^trap '([^']*)' EXIT", text, re.M)
    handler = exit_trap.group(1).split()[0]
    body = _bash_function_body(text, handler)
    assert "copy_results_locked" in body and "stop_server" in body and 'kill "$COPY_PID"' in body
    assert "flock -w" in _bash_function_body(text, "copy_results_locked")
    loop = _bash_function_body(text, "copy_loop")
    assert 'sleep "$COPY_EVERY_S"' in loop and "copy_results_locked" in loop
    assert 'COPY_EVERY_S="${POLISH_COPY_EVERY_S:-300}"' in text
    assert "local p " in _bash_function_body(text, "copy_results")       # never clobbers a caller's $p


def test_hide_sets_from_control_lines(tmp_path):
    text = _text(JOB)
    body = _bash_function_body(text, "hide_sets_from")
    lines = tmp_path / "ctl.txt"
    lines.write_text(textwrap.dedent("""\
        CONTROL\tsofa_1\tcam_r_L0_salon_1\t0\tcontrols/hide_sofa_1
        some other line
        CONTROL\twin_3\tcam_r_L1_oda_2\t1\tcontrols/hide_win_3
        HIDE_SETS\tignored
        """).replace("\\t", "\t"), encoding="utf-8")
    script = f"hide_sets_from() {{\n{body}}}\nhide_sets_from '{lines}'"
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True).stdout
    assert out == "cam_r_L0_salon_1:sofa_1;cam_r_L1_oda_2:win_3+plug"
    lines.write_text("no controls\n", encoding="utf-8")
    assert subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True).stdout == ""


# --------------------------------------------------------------------------
# Review findings (2 Oct 2026): results copy, stale files, CPU threads, run plan
# --------------------------------------------------------------------------

def test_results_copy_is_incremental_and_batched(tmp_path):
    """Every stage copied every result file again, one cp per file (run 0b: about 45 ms per file on
    the network volume; about 1000 files and 45 copies in run 2). Unchanged files of earlier runs are
    now copied once by the job's first copy and once by the full copy on exit; one cp takes many files;
    a file a stage wrote is in the results when the next stage starts, also when its timestamp lags
    by up to 1 s (1 s timestamps on the volume)."""
    box = Sandbox(tmp_path)
    out3 = box.repo / "outputs" / "synthetic-03"
    earlier = [box.write_old(out3 / "polish" / "sweep" / name) for name in
               ("cam_s_a1_preview.jpg", "cam_s_a1_gate.jpg", "polish_manifest.json")]
    earlier.append(box.write_old(out3 / "check" / "cam_s_plan.jpg"))
    proc = box.run(POLISH_MODE="final", FAKE_SEEN="1", FAKE_COARSE_MTIME="1")
    assert proc.returncode == 0, box.output
    cps = box.cp_calls()
    for f in earlier:
        n = sum(str(f) in argv for argv in cps)
        assert 1 <= n <= 2, f"{f.relative_to(box.repo)} copied {n} times"
    assert (box.results / "polish/synthetic-03/sweep/cam_s_a1_preview.jpg").is_file()
    assert (box.results / "check/synthetic-03/cam_s_plan.jpg").is_file()
    preview, gate = (str(f) for f in earlier[:2])
    assert any(preview in argv and gate in argv for argv in cps), "one cp per file, not per batch"
    for p in ("synthetic-01", "synthetic-03"):
        (report,) = _find(box.calls(), "wenart.report", "final", p)
        assert f"polish/{p}/polish_manifest.json" in report["results"]
        assert f"check/{p}/check_manifest.json" in report["results"]
        assert f"check/{p}/check_report.md" in report["results"]
    # The results equal the outputs at the end (the full copy on exit).
    for p in ("synthetic-01", "synthetic-03"):
        src = box.repo / "outputs" / p / "check" / "check_manifest.json"
        assert (box.results / "check" / p / "check_manifest.json").read_bytes() == src.read_bytes()


def test_results_hold_only_this_jobs_logs_and_style_profiles(tmp_path):
    """/workspace/logs and outputs/ keep the files of every earlier pod: the M4 vLLM logs, an earlier
    pod's download logs and a style_2.json of an older brief ended up in run 0/0b's results as if
    they were that run's. The control renders' Blender log was not copied."""
    box = Sandbox(tmp_path)
    logs = box.ws / "logs"
    stale_logs = ("vllm-GLM-4.6V-Flash.log", "vllm-Qwen3-VL-8B-Instruct.log", "vllm-qwen.log", "vllm-glm.log",
                  "hf-download-zai-org_GLM-4.6V-Flash.log", "setup-polish-pip.log")
    for name in stale_logs:
        box.write_old(logs / name, b"an earlier pod\n")
    box.write_old(logs / "setup_polish.json", b'{"kind": "setup_polish", "old": true}')
    out3 = box.repo / "outputs" / "synthetic-03"
    box.write_old(out3 / "style_2.json", b'{"old brief": true}')
    # Run without the check phase (1a): no vLLM, no downloads, no pip, no setup_polish.json in this job.
    proc = box.run(POLISH_MODE="sweep", POLISH_PROJECTS="synthetic-03", FAKE_SETUP_JSON="0")
    assert proc.returncode == 0, box.output
    r = box.results
    assert sorted(f.name for f in (r / "logs").glob("*")) == []
    assert not (r / "setup_polish.json").exists()
    assert (r / "renders/synthetic-03/style.json").is_file()
    assert not (r / "renders/synthetic-03/style_2.json").exists()
    assert (r / "renders/synthetic-03/controls/render.log").read_text() == "control renders\n"
    assert (r / "renders/synthetic-03/controls/hide_sofa_1/render_manifest.json").is_file()

    # A run with the check phase: this job's vLLM logs, not the M4 ones; a brief with two styles.
    box2 = Sandbox(tmp_path / "check")
    for name in stale_logs:
        box2.write_old(box2.ws / "logs" / name, b"an earlier pod\n")
    box2.write_old(box2.repo / "outputs" / "synthetic-03" / "style_3.json", b'{"old brief": true}')
    proc = box2.run(POLISH_MODE="final", POLISH_PROJECTS="synthetic-03", FAKE_STYLE_PROFILES="2")
    assert proc.returncode == 0, box2.output
    r = box2.results
    assert sorted(f.name for f in (r / "logs").glob("*")) == ["vllm-glm.log", "vllm-qwen.log"]
    assert (r / "setup_polish.json").is_file()
    assert (r / "renders/synthetic-03/style_2.json").is_file()       # written with this style.json
    assert not (r / "renders/synthetic-03/style_3.json").exists()    # older than this style.json


def _cgroup(root: Path, files: dict[str, str]) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    return root


THREAD_VARS = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
               "VECLIB_MAXIMUM_THREADS", "OPENCV_FOR_THREADS_NUM", "WENART_CPU_THREADS")


@pytest.mark.parametrize("files, env, want", [
    ({"cgroup.controllers": "cpu memory\n", "cpu.max": "200000 100000\n"}, {}, 2),
    ({"cgroup.controllers": "cpu memory\n", "cpu.max": "150000 100000\n"}, {}, 2),       # 1.5 CPUs: rounded up
    ({"cpu/cpu.cfs_quota_us": "300000\n", "cpu/cpu.cfs_period_us": "100000\n"}, {}, 3),  # cgroup v1
    ({"cpu/cpu.cfs_quota_us": "-1\n", "cpu/cpu.cfs_period_us": "100000\n"}, {}, None),   # v1, no quota
    ({"cgroup.controllers": "cpu\n", "cpu.max": "max 100000\n"}, {}, None),              # v2, no quota
    ({}, {}, None),                                                                      # no cgroup files
    ({"cgroup.controllers": "cpu\n", "cpu.max": "200000 100000\n"}, {"POLISH_THREADS": "5"}, 5),
], ids=["v2", "v2-fraction", "v1", "v1-none", "v2-max", "none", "override"])
def test_cpu_thread_budget_from_the_cgroup_reaches_every_stage(tmp_path, files, env, want):
    """Run 0b: os.cpu_count() saw the host's 112 CPUs; numpy/OpenBLAS, OpenCV and torch each started
    that many threads under the pod's much smaller CPU quota and the gate's CPU work ran 10-50x
    slower. The job exports the quota (rounded up, at most nproc) to every stage."""
    nproc = len(os.sched_getaffinity(0))
    want = nproc if want is None else (want if env else min(want, nproc))
    box = Sandbox(tmp_path)
    cgroup = _cgroup(tmp_path / "cgroup", files)
    proc = box.run(POLISH_MODE="final", POLISH_PHASES="look report", POLISH_PROJECTS="synthetic-03",
                   WENART_CGROUP=str(cgroup), **env)
    assert proc.returncode == 0, box.output
    calls = box.calls()
    assert len(calls) >= 5
    for c in calls:
        assert {k: c["env"][k] for k in THREAD_VARS} == {k: str(want) for k in THREAD_VARS}, c["argv"]
    assert f"threads={want} omp={want}" in box.setup_log.read_text()       # the setup (setup_polish.json) too
    assert re.search(rf"CPU budget: {want} thread", box.output), box.output


def test_setup_summary_records_the_pod_limits(tmp_path):
    """setup_polish.json had only the host's RAM and CPU count (251 GiB, 112 CPUs) while vLLM saw a
    cgroup limit of about 26 GiB free on the same pod: the pod's own limits are recorded too."""
    snippet = _heredoc(_text(SETUP), 'python3 - "$out_dir/setup_polish.json" "$STATE_DIR"')
    script = tmp_path / "summary.py"
    script.write_text(snippet, encoding="utf-8")
    state = tmp_path / "state"
    state.mkdir()
    constraints = tmp_path / "image-constraints.txt"
    constraints.write_text("torch==2.9.1+cu128\n")

    def summary(cgroup: Path, **env) -> dict:
        out = tmp_path / "setup_polish.json"
        run_env = {k: v for k, v in os.environ.items() if k not in THREAD_VARS}
        run_env.update(WENART_CGROUP=str(cgroup), **env)
        proc = subprocess.run([sys.executable, str(script), str(out), str(state), "final", "look polish", "qwen",
                               "venv=ok:1", "models=ok:1", "check=skipped:0", "", "", str(constraints)],
                              capture_output=True, text=True, env=run_env)
        assert proc.returncode == 0, proc.stderr
        return json.loads(out.read_text())

    v2 = _cgroup(tmp_path / "v2", {"cgroup.controllers": "cpu memory\n", "cpu.max": "1200000 100000\n",
                                   "memory.max": str(25 * 2**30) + "\n", "memory.current": str(5 * 2**30) + "\n"})
    data = summary(v2, WENART_CPU_THREADS="12", OMP_NUM_THREADS="12", OPENCV_FOR_THREADS_NUM="12")
    limits = data["pod_limits"]
    assert limits["cgroup"] == "v2" and limits["cpu_max"] == "1200000 100000" and limits["cpu_quota"] == 12.0
    assert limits["mem_limit_gib"] == 25.0 and limits["mem_current_gib"] == 5.0
    assert limits["threads"] == 12 and limits["thread_env"] == {"OMP_NUM_THREADS": "12", "OPENCV_FOR_THREADS_NUM": "12"}
    assert limits["affinity_cpus"] == len(os.sched_getaffinity(0))
    assert "host" in limits["note"]
    assert "MemTotal_gib" in data and data["nproc"] >= 1           # the host values stay, labelled by the note

    v1 = _cgroup(tmp_path / "v1", {"cpu/cpu.cfs_quota_us": "900000\n", "cpu/cpu.cfs_period_us": "100000\n",
                                   "memory/memory.limit_in_bytes": "9223372036854771712\n",
                                   "memory/memory.usage_in_bytes": str(2**30) + "\n"})
    limits = summary(v1)["pod_limits"]
    assert limits["cgroup"] == "v1" and limits["cpu_quota"] == 9.0 and limits["cpu_max"] == "900000 100000"
    assert limits["mem_limit_gib"] is None and limits["mem_current_gib"] == 1.0   # no memory limit
    assert limits["threads"] is None and limits["thread_env"] == {}               # not started by polish.sh

    limits = summary(tmp_path / "missing")["pod_limits"]
    assert limits["cgroup"] is None and limits["cpu_quota"] is None and limits["mem_limit_gib"] is None


def test_run_2_is_split_into_pods_that_each_fit():
    """Run 2 in one pod (look, polish, check with both VLMs, report and tests for 87 views) cannot end
    before WENART_DEADLINE (105 min of a 2 h run) at the speeds runs 0 and 0b measured: it is split
    into pods that resume from the volume, in the plan and in the job's documented commands."""
    doc = _text(ROOT / "docs" / "milestone5.md")
    plan = doc[doc.index("### 8.3 Pod plan"):doc.index("## 9. Tests")]
    rows = {m.group(1): m.group(0) for m in re.finditer(r"^\| (\w+) \|.*$", plan, re.M)}
    assert "2" not in rows, "run 2 as one pod"
    assert "`look polish`" in rows["2a"] and "`check report tests`" in rows["2b"]
    assert "POLISH_PROJECTS" in rows["2a"]                     # one project per pod
    header = _text(JOB).split("set -Eeuo pipefail")[0]
    lines = header.splitlines()
    commands = [" ".join(lines[i:i + 2]) for i, ln in enumerate(lines) if "gpu_run.py run" in ln]
    phases = [re.search(r"POLISH_PHASES='([^']*)'", c).group(1) for c in commands]
    assert "look polish" in phases and "check report tests" in phases, phases
    assert "look polish check report tests" not in phases
    for c in commands:
        assert "--gpu 'RTX PRO 4500'" in c and "--disk 130" in c and "L4" not in c
