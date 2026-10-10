#!/usr/bin/env bash
# Milestone 5 setup on a RunPod pod (docs/milestone5.md §8.1), run by scripts/jobs/polish.sh
# after scripts/pod_setup.sh (Blender, /workspace/venv). Idempotent and timed; every part is
# stamped or cached, so a second run on the same pod only checks. Logs in /workspace/logs/.
#
# Parts, chosen by the job's phases (POLISH_PHASES, POLISH_MODE; standalone: everything):
#   venv     /opt/wenart/venv-polish (container disk, --system-site-packages: the image's torch
#            2.9.1 stays): diffusers==0.40.0 transformers==5.18.0 accelerate==1.15.0
#            huggingface-hub==1.33.0 "safetensors>=0.8.0" opencv-python-headless==4.14.0.94
#            "numpy>=2" + the repo's CPU deps (scripts/pod_requirements.txt without its hub and
#            opencv lines and without the numpy/pillow/matplotlib version pins: those pins are for
#            /workspace/venv, where the pipeline's crops must hash as in the session, M7 §9.1; this
#            venv keeps the opencv pin above and the versions validated by the M5/M6 gate runs).
#            Every pip install runs with -c /opt/wenart/image-constraints.txt (the image's torch,
#            torchvision, torchaudio, triton pins from `python3 -m pip freeze`), so it can never
#            replace the image's torch. torchvision==0.24.1 (the pair of torch 2.9.1, --no-deps,
#            cu128 index) only when the image has none. The venv is stamped good only after the
#            checks of POLISH_CHECK pass on the GPU: a bf16 matmul, sm_120 kernels on Blackwell,
#            bf16 SDPA [1, 30, 8320, 128] under sdpa_kernel([FLASH_ATTENTION,
#            EFFICIENT_ATTENTION]), torchvision.ops.nms on CUDA, the diffusers/transformers
#            classes the polish and the gate load, and every wenart.polish / wenart.gate module.
#            Needed by the phases polish, gate and tests (tests/gpu/test_polish.py runs here).
#   models   the polish models (wenart/polish/polish.yaml) and the gate models
#            (wenart/gate/models.yaml `models:`, plus its `detect:` block: the OWLv2 added-object
#            detector google/owlv2-base-patch16-ensemble @cfd3195, Apache-2.0, docs/milestone7.md
#            §8.1, kept outside `models:` so it never enters the gate key): huggingface_hub.
#            snapshot_download with the pinned revision and allow patterns of those files, into
#            HF_HOME=/opt/wenart/hf (container disk; the job runs the polish, the gate and the
#            detector with HF_HUB_OFFLINE=1 afterwards).
#            Needed by the phases polish, gate and tests (tests/gpu/test_polish_backend.py
#            loads the polish models) and by POLISH_MODE=smoke.
#   check    scripts/pod_setup_recognition.sh with RECOG_SETUP_PARTS = POLISH_RECOG_PARTS (default
#            "vllm libredwg models": no PaddleOCR; LibreDWG 0.14 for the DWG projects of the full and
#            prep jobs, docs/milestone7.md §5.1, reused from /workspace/tools/libredwg/bin once built)
#            and BAKEOFF_MODELS = the ids of CHECK_MODELS (default "qwen glm") from
#            wenart/vision_check/check.yaml, each with its pinned revision ("<id>@<revision>").
#            Needed by the phase check. Milestone 11: AGENT_MODELS (check.yaml keys, e.g. "agent") adds the agent
#            model(s) of an orchestrated run (scripts/jobs/full.sh, scripts/jobs/agent_check.sh).
# Writes setup_polish.json ($WENART_RESULTS, else /workspace/logs): per part state and seconds,
# model sizes and seconds, free disk, MemTotal, MemAvailable, nproc (the host's: /proc/meminfo and
# os.cpu_count() in a container), pod_limits (the pod's cgroup v2/v1 CPU quota, memory limit and
# usage, CPU affinity, and the thread budget polish.sh exported) and the versions the check
# printed. Exit 1 when a needed part failed (the job then skips the phases that need it).
# POLISH_SETUP_PLAN_ONLY=1 prints the plan (parts, BAKEOFF_MODELS) and exits without changes.
#
# Sources checked on 2 Oct 2026: huggingface_hub 1.33.0 wheel (_snapshot_download.py:
# snapshot_download(repo_id, *, revision, cache_dir, allow_patterns, ...) -> local folder);
# diffusers 0.40.0 __init__ (ZImageControlNetPipeline, ZImageControlNetModel); transformers
# 5.18.0 (Sam2Model, Sam2Processor, AutoModelForDepthEstimation, AutoModel in __all__);
# torch.nn.attention.sdpa_kernel(list of SDPBackend) (torch >= 2.3).
set -Eeuo pipefail
trap 'echo "[setup-polish] ERROR at line $LINENO" >&2' ERR

WS="${WENART_WS:-/workspace}"          # WENART_WS / WENART_FAST: CPU tests only
LOGS=$WS/logs
FAST="${WENART_FAST:-/opt/wenart}"     # container disk: fast, wiped with the pod
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PY="${WENART_PY:-$WS/venv/bin/python}"   # reads check.yaml (PyYAML)
if [ ! -x "$PY" ]; then PY=python3; fi
VENV=$FAST/venv-polish
CONSTRAINTS=$FAST/image-constraints.txt
STATE_DIR=$FAST/setup-polish
mkdir -p "$LOGS" "$FAST" "$STATE_DIR"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export HF_HUB_OFFLINE=0                # downloads happen here; the job goes offline afterwards
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_CACHE_DIR=$WS/pip-cache      # few large wheels: fine on the volume, survives pods
PIP_LOG=$LOGS/setup-polish-pip.log

DIFFUSERS_VERSION=0.40.0
TRANSFORMERS_VERSION=5.18.0
ACCELERATE_VERSION=1.15.0
HUB_VERSION=1.33.0
OPENCV_VERSION=4.14.0.94
TORCHVISION_FALLBACK=0.24.1             # pairs with the image's torch 2.9.1
TORCH_INDEX=https://download.pytorch.org/whl/cu128
PINS=("diffusers==$DIFFUSERS_VERSION" "transformers==$TRANSFORMERS_VERSION" "accelerate==$ACCELERATE_VERSION"
      "huggingface-hub==$HUB_VERSION" "safetensors>=0.8.0" "opencv-python-headless==$OPENCV_VERSION" "numpy>=2")

MODE="${POLISH_MODE:-final}"
read -r -a PHASES <<< "${POLISH_PHASES:-look controls polish gate check report tests}"
read -r -a CHECK_KEYS <<< "${CHECK_MODELS:-qwen glm}"
# Milestone 11 (docs/milestone11.md §11, §12): the agent model(s) of an orchestrated run, check.yaml keys (agent,
# agent_fast), downloaded with the VLMs by the part check (hf download with the pinned revision into HF_HOME on the
# container disk, about 31 GB for agent at ~1.1 GB/s). Empty (the default): no agent model.
read -r -a AGENT_KEYS <<< "${AGENT_MODELS:-}"
RECOG_PARTS="${POLISH_RECOG_PARTS:-vllm libredwg models}"   # the recognition setup's parts for the phase check

log() { echo "[$(date -u +%H:%M:%S)] setup-polish: $*"; }
step_start() { STEP_NAME="$1"; STEP_T0=$(date +%s); log "start: $STEP_NAME"; }
step_end() { log "done: $STEP_NAME in $(( $(date +%s) - STEP_T0 )) s"; }
has_phase() { local p; for p in "${PHASES[@]}"; do [ "$p" = "$1" ] && return 0; done; return 1; }

# Which parts this job needs (see the header).
NEED_VENV=0; NEED_MODELS=0; NEED_CHECK=0
if has_phase polish || has_phase gate || has_phase tests || [ "$MODE" = "smoke" ]; then NEED_VENV=1; fi
# tests: tests/gpu/test_polish_backend.py loads the pinned polish models (CUDA OOM retry, §3.1).
if has_phase polish || has_phase gate || has_phase tests || [ "$MODE" = "smoke" ]; then NEED_MODELS=1; NEED_VENV=1; fi
if has_phase check; then NEED_CHECK=1; fi

# vlm_entries: "<id>@<revision> ..." of CHECK_MODELS (+ AGENT_MODELS, Milestone 11) from check.yaml (the single
# source, §1.6; a key named twice is downloaded once). Milestone 12: dotted keys name nested entries
# ("bakeoff.fp8" = models.bakeoff.fp8, as wenart.run.servers.model_entry reads them).
vlm_entries() {
  "$PY" - "$REPO_DIR/wenart/vision_check/check.yaml" "${CHECK_KEYS[@]}" "${AGENT_KEYS[@]}" <<'PY'
import sys

import yaml

with open(sys.argv[1], encoding="utf-8") as fh:
    models = yaml.safe_load(fh)["models"]


def entry(key):
    node = models
    for part in key.split("."):
        node = node[part]
    return node


keys = list(dict.fromkeys(sys.argv[2:]))
print(" ".join(f"{entry(k)['id']}@{entry(k)['revision']}" for k in keys))
PY
}

if [ "${POLISH_SETUP_PLAN_ONLY:-0}" = "1" ]; then
  echo "PLAN venv=$NEED_VENV models=$NEED_MODELS check=$NEED_CHECK mode=$MODE phases=${PHASES[*]}"
  if [ "$NEED_CHECK" = "1" ]; then
    echo "PLAN RECOG_SETUP_PARTS=$RECOG_PARTS"
    echo "PLAN BAKEOFF_MODELS=$(vlm_entries)"
  fi
  exit 0
fi

declare -A PART_STATE=([venv]=skipped [models]=skipped [check]=skipped)
declare -A PART_SECONDS=([venv]=0 [models]=0 [check]=0)
DISK_BEFORE=$(df -B1 --output=avail "$FAST" 2>/dev/null | tail -1 | tr -d ' ' || echo "")

# run_part <name> <function>: timed; the state is ok/failed; the setup goes on either way.
run_part() {
  local name=$1 fn=$2 rc=0 t0
  t0=$(date +%s)
  step_start "$name"
  "$fn" || rc=$?
  PART_SECONDS[$name]=$(( $(date +%s) - t0 ))
  if [ "$rc" -eq 0 ]; then PART_STATE[$name]=ok; else PART_STATE[$name]=failed; log "$name FAILED (rc $rc)"; fi
  step_end
  return 0
}

# The stamp check (python -c "$POLISH_CHECK" in the repo, so the wenart package is importable).
# The last line it prints is "POLISH_CHECK {json of versions}".
POLISH_CHECK=$(cat <<'PY'
import importlib
import json
import pkgutil
import sys

out = {"python": sys.version.split()[0]}
import torch

out.update(torch=torch.__version__, cuda=torch.version.cuda)
if not torch.cuda.is_available():
    sys.exit("torch.cuda.is_available() is False: the polish needs a GPU")
dev = torch.device("cuda:0")
cap = torch.cuda.get_device_capability(0)
arch = torch.cuda.get_arch_list()
out.update(gpu=torch.cuda.get_device_name(0), capability=list(cap), arch_list=arch)
if cap[0] >= 12 and "sm_120" not in arch:
    sys.exit(f"Blackwell GPU (capability {cap}) but this torch has no sm_120 kernels: {arch}")
a = torch.full((256, 256), 0.5, device=dev, dtype=torch.bfloat16)
y = (a @ a).float()
torch.cuda.synchronize()
if abs(float(y[0, 0]) - 64.0) > 0.5:
    sys.exit(f"bf16 matmul returned {float(y[0, 0])!r}, expected 64.0")
from torch.nn.attention import SDPBackend, sdpa_kernel

g = torch.Generator(device=dev).manual_seed(0)
q = torch.randn(1, 30, 8320, 128, device=dev, dtype=torch.bfloat16, generator=g)
with sdpa_kernel([SDPBackend.FLASH_ATTENTION, SDPBackend.EFFICIENT_ATTENTION]):
    o = torch.nn.functional.scaled_dot_product_attention(q, q, q)
torch.cuda.synchronize()
if not bool(torch.isfinite(o).all()):
    sys.exit("bf16 SDPA returned non-finite values")
import torchvision
from torchvision.ops import nms

boxes = torch.tensor([[0.0, 0.0, 10.0, 10.0], [1.0, 1.0, 11.0, 11.0], [50.0, 50.0, 60.0, 60.0]], device=dev)
keep = nms(boxes, torch.tensor([0.9, 0.8, 0.7], device=dev), 0.5).tolist()
if keep != [0, 2]:
    sys.exit(f"torchvision.ops.nms on CUDA kept {keep}, expected [0, 2]")
out["torchvision"] = torchvision.__version__
from diffusers import ZImageControlNetModel, ZImageControlNetPipeline  # noqa: F401
from transformers import (AutoModel, AutoModelForDepthEstimation, Owlv2ForObjectDetection,  # noqa: F401
                          Owlv2Processor, Sam2Model, Sam2Processor)

import accelerate
import cv2
import diffusers
import huggingface_hub
import numpy
import safetensors
import transformers

out.update(diffusers=diffusers.__version__, transformers=transformers.__version__,
           accelerate=accelerate.__version__, huggingface_hub=huggingface_hub.__version__,
           safetensors=safetensors.__version__, opencv=cv2.__version__, numpy=numpy.__version__)
import wenart.gate
import wenart.polish

modules = []
for pkg in (wenart.polish, wenart.gate):
    for info in pkgutil.iter_modules(pkg.__path__):
        if info.name != "__main__":
            importlib.import_module(f"{pkg.__name__}.{info.name}")
            modules.append(f"{pkg.__name__}.{info.name}")
out["wenart_modules"] = modules
print("POLISH_CHECK " + json.dumps(out))
PY
)

# --- part venv ----------------------------------------------------------------------------
part_venv() {
  local pyv req_hash stamp reqs
  { python3 -m pip freeze 2>/dev/null | grep -iE '^(torch|torchvision|torchaudio|triton)==' || true; } > "$CONSTRAINTS"
  if ! grep -qiE '^torch==' "$CONSTRAINTS"; then
    # pip freeze prints "torch @ <url>" for a torch installed from a URL: pin its version instead.
    python3 -c 'import torch; print("torch==" + torch.__version__)' >> "$CONSTRAINTS" 2>/dev/null || true
  fi
  log "image constraints: $(tr '\n' ' ' < "$CONSTRAINTS")"
  if ! grep -qiE '^torch==' "$CONSTRAINTS"; then
    log "no torch in the image's python: refusing to install a venv that could pull its own torch"; return 1
  fi
  reqs=$FAST/polish-requirements.txt
  grep -viE '^huggingface[-_]hub' "$REPO_DIR/scripts/pod_requirements.txt" | grep -viE '^opencv-python-headless' \
    | sed -E 's/^(numpy|pillow|matplotlib)[[:space:]]*==.*$/\1/' > "$reqs" || true
  pyv=$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')
  req_hash=$( { printf '%s\n' "${PINS[@]}"; cat "$reqs" "$CONSTRAINTS"; echo "$pyv ${WENART_IMAGE:-}"; } | sha256sum | cut -c1-16)
  stamp=$VENV/.polish-$req_hash
  if [ -f "$stamp" ]; then
    log "venv-polish already stamped good ($stamp)"
    cat "$STATE_DIR/venv_check.txt" 2>/dev/null | tail -1 || true
    return 0
  fi
  [ -x "$VENV/bin/python" ] || python3 -m venv --system-site-packages "$VENV" || return 1
  "$VENV/bin/python" -m pip install -q --upgrade pip >> "$PIP_LOG" 2>&1 || return 1
  if ! "$VENV/bin/python" -c "import torchvision" 2>/dev/null; then
    log "no torchvision in the image: torchvision==$TORCHVISION_FALLBACK from $TORCH_INDEX (--no-deps)"
    if ! "$VENV/bin/python" -m pip install -q --no-deps -c "$CONSTRAINTS" "torchvision==$TORCHVISION_FALLBACK" \
         --index-url "$TORCH_INDEX" >> "$PIP_LOG" 2>&1; then
      log "torchvision install failed (see $PIP_LOG)"; return 1
    fi
    echo "torchvision==$TORCHVISION_FALLBACK" >> "$CONSTRAINTS"
  fi
  log "pip install ${PINS[*]} + $(wc -l < "$reqs") repo requirements (log $PIP_LOG)"
  if ! "$VENV/bin/python" -m pip install -q -c "$CONSTRAINTS" "${PINS[@]}" -r "$reqs" >> "$PIP_LOG" 2>&1; then
    log "pip install failed; last lines:"; tail -n 20 "$PIP_LOG"; return 1
  fi
  # The stamp depends on the GPU checks, not on pip: a wheel without kernels for this GPU
  # installs fine and fails only here.
  if ! (cd "$REPO_DIR" && "$VENV/bin/python" -c "$POLISH_CHECK") > "$STATE_DIR/venv_check.txt" 2>&1; then
    log "venv-polish check FAILED, not stamped:"; tail -n 30 "$STATE_DIR/venv_check.txt"; return 1
  fi
  tail -n 1 "$STATE_DIR/venv_check.txt"
  find "$VENV" -maxdepth 1 -name '.polish-*' -delete
  touch "$stamp"
  log "venv-polish stamped good ($stamp)"
}

# --- part models --------------------------------------------------------------------------
part_models() {
  if [ ! -x "$VENV/bin/python" ] || [ "${PART_STATE[venv]}" != "ok" ]; then
    log "venv-polish is not ready: no downloads"; return 1
  fi
  log "free on $FAST before the downloads: $(df -h --output=avail "$FAST" 2>/dev/null | tail -1 | tr -d ' ')"
  "$VENV/bin/python" - "$REPO_DIR" "$STATE_DIR/models.json" <<'PY'
import json
import sys
import time
from pathlib import Path

import yaml
from huggingface_hub import snapshot_download

repo, out_path = Path(sys.argv[1]), Path(sys.argv[2])
sources = (("polish", repo / "wenart" / "polish" / "polish.yaml"), ("gate", repo / "wenart" / "gate" / "models.yaml"))
records, failed = [], 0
for group, path in sources:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    # The OWLv2 detector (docs/milestone7.md §8.1) is the gate file's `detect:` block, outside `models:`.
    extra = [("detect", cfg["detect"])] if group == "gate" and "detect" in cfg else []
    for role, m in list(cfg["models"].items()) + extra:
        rec = {"group": group, "role": role, "repo": m["repo"], "revision": m["revision"],
               "licence": m.get("licence"), "allow_patterns": m.get("allow_patterns"), "files": m.get("files"),
               "expected_gb": m.get("size_gb"), "path": None, "n_files": 0, "bytes": 0, "seconds": None,
               "ok": False, "error": None}
        t0 = time.time()
        try:
            snap = Path(snapshot_download(m["repo"], revision=m["revision"], allow_patterns=m.get("allow_patterns")))
            files = [f for f in snap.rglob("*") if f.is_file()]      # snapshot entries link into blobs/
            rec.update(path=str(snap), n_files=len(files), bytes=sum(f.stat().st_size for f in files))
            missing = [f for f in (m.get("files") or []) if not (snap / f).is_file()]
            if missing or not files:
                raise FileNotFoundError(f"missing in the snapshot: {missing or 'every file'}")
            rec["ok"] = True
        except Exception as exc:  # noqa: BLE001 - recorded, the part fails below
            rec["error"] = f"{type(exc).__name__}: {exc}"
            failed += 1
        rec["seconds"] = round(time.time() - t0, 1)
        gb = rec["bytes"] / 1e9
        rate = gb * 1000 / rec["seconds"] if rec["seconds"] and rec["seconds"] > 5 else None
        print(f"download {group}/{role} {m['repo']}@{m['revision'][:12]}: "
              f"{'ok' if rec['ok'] else 'FAILED ' + str(rec['error'])}, {gb:.2f} GB (listed {m.get('size_gb')}) "
              f"in {rec['seconds']} s" + (f" = {rate:.0f} MB/s" if rate else " (cached)"), flush=True)
        records.append(rec)
out_path.write_text(json.dumps({"models": records}, indent=1, ensure_ascii=False), encoding="utf-8")
sys.exit(1 if failed else 0)
PY
}

# --- part check (vLLM + the two VLMs) -------------------------------------------------------
part_check() {
  local entries
  entries=$(vlm_entries) || { log "cannot read the VLM ids of '${CHECK_KEYS[*]}' from check.yaml"; return 1; }
  log "recognition setup: RECOG_SETUP_PARTS='$RECOG_PARTS' BAKEOFF_MODELS='$entries'"
  RECOG_SETUP_PARTS="$RECOG_PARTS" BAKEOFF_MODELS="$entries" bash "$REPO_DIR/scripts/pod_setup_recognition.sh"
}

# setup_polish.json: what was done, sizes, seconds, machine and versions.
write_summary() {
  local out_dir=${WENART_RESULTS:-$LOGS}
  mkdir -p "$out_dir"
  local disk_after
  disk_after=$(df -B1 --output=avail "$FAST" 2>/dev/null | tail -1 | tr -d ' ' || echo "")
  python3 - "$out_dir/setup_polish.json" "$STATE_DIR" "$MODE" "${PHASES[*]}" "${CHECK_KEYS[*]}" \
    "venv=${PART_STATE[venv]}:${PART_SECONDS[venv]}" "models=${PART_STATE[models]}:${PART_SECONDS[models]}" \
    "check=${PART_STATE[check]}:${PART_SECONDS[check]}" "${DISK_BEFORE:-}" "${disk_after:-}" "$CONSTRAINTS" <<'PY' || true
import json
import os
import sys
import time
from pathlib import Path

out, state_dir, mode, phases, check_keys = sys.argv[1:6]
parts_raw, disk_before, disk_after, constraints = sys.argv[6:9], sys.argv[9], sys.argv[10], sys.argv[11]
parts = {}
for item in parts_raw:
    name, _, rest = item.partition("=")
    status, _, secs = rest.partition(":")
    parts[name] = {"state": status, "seconds": int(secs or 0)}
mem = {}
try:
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in ("MemTotal", "MemAvailable"):
            mem[key + "_gib"] = round(int(value.split()[0]) / 1048576, 2)
except OSError:
    pass
versions = None
check_txt = Path(state_dir) / "venv_check.txt"
if check_txt.is_file():
    for line in check_txt.read_text(errors="replace").splitlines():
        if line.startswith("POLISH_CHECK "):
            versions = json.loads(line[len("POLISH_CHECK "):])
models_json = Path(state_dir) / "models.json"
models = json.loads(models_json.read_text())["models"] if models_json.is_file() else []
def gib(v):
    return round(int(v) / 2**30, 1) if v.strip().isdigit() else None


# The pod's own limits: /proc/meminfo and os.cpu_count() show the host (run 0: 251 GiB, 112 CPUs)
# while the container runs under a cgroup (vLLM saw about 26 GiB free on the same pod).
def read(path):
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def number(text, no_limit_from=2**62):
    """A cgroup value in bytes or microseconds; None for 'max', -1, the v1 'unlimited' value or junk."""
    return int(text) if text and text.isdigit() and int(text) < no_limit_from else None


cg = Path(os.environ.get("WENART_CGROUP") or "/sys/fs/cgroup")   # WENART_CGROUP: CPU tests only
quota = period = limit = current = None
if (cg / "cgroup.controllers").is_file():                          # cgroup v2
    version = "v2"
    cpu_max = read(cg / "cpu.max")
    if cpu_max:
        q, _, p = cpu_max.partition(" ")
        quota, period = number(q), number(p)
    limit, current = number(read(cg / "memory.max")), number(read(cg / "memory.current"))
elif (cg / "cpu").is_dir() or (cg / "memory").is_dir():          # cgroup v1
    version = "v1"
    q, p = read(cg / "cpu" / "cpu.cfs_quota_us"), read(cg / "cpu" / "cpu.cfs_period_us")
    cpu_max = f"{q} {p}" if q is not None and p is not None else None
    quota, period = number(q), number(p)
    limit = number(read(cg / "memory" / "memory.limit_in_bytes"))
    current = number(read(cg / "memory" / "memory.usage_in_bytes"))
else:
    version = cpu_max = None
thread_env = {k: os.environ[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
              "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OPENCV_FOR_THREADS_NUM") if k in os.environ}
threads = os.environ.get("WENART_CPU_THREADS", "")
pod_limits = {
    "note": "MemTotal_gib, MemAvailable_gib and nproc are the host's (/proc/meminfo, os.cpu_count()); "
            "the pod may use only these cgroup limits",
    "cgroup": version, "cpu_max": cpu_max,
    "cpu_quota": round(quota / period, 2) if quota and period else None,
    "affinity_cpus": len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
    "mem_limit_gib": round(limit / 2**30, 2) if limit is not None else None,
    "mem_current_gib": round(current / 2**30, 2) if current is not None else None,
    "threads": int(threads) if threads.isdigit() else None,         # exported by scripts/jobs/polish.sh
    "thread_env": thread_env,
}
data = {"schema_version": "0.1", "kind": "setup_polish", "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mode": mode, "phases": phases.split(), "check_models": check_keys.split(), "parts": parts,
        "models": models, "models_gb": round(sum(m.get("bytes") or 0 for m in models) / 1e9, 2),
        "disk_free_gib_before": gib(disk_before), "disk_free_gib_after": gib(disk_after),
        **mem, "nproc": os.cpu_count(), "pod_limits": pod_limits, "versions": versions,
        "image_constraints": Path(constraints).read_text().split() if Path(constraints).is_file() else [],
        "hf_home": os.environ.get("HF_HOME"), "image": os.environ.get("WENART_IMAGE")}
Path(out).write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"setup_polish.json -> {out}")
PY
  cp -f "$out_dir/setup_polish.json" "$LOGS/setup_polish.json" 2>/dev/null || true
}

log "mode $MODE, phases: ${PHASES[*]}; parts: venv=$NEED_VENV models=$NEED_MODELS check=$NEED_CHECK; HF_HOME=$HF_HOME"
if [ "$NEED_VENV" = "1" ]; then run_part venv part_venv; fi
if [ "$NEED_MODELS" = "1" ]; then run_part models part_models; fi
if [ "$NEED_CHECK" = "1" ]; then run_part check part_check; fi
write_summary
FAILED_PARTS=()
for part in venv models check; do
  if [ "${PART_STATE[$part]}" = "failed" ]; then FAILED_PARTS+=("$part"); fi
done
if [ "${#FAILED_PARTS[@]}" -gt 0 ]; then
  log "FAILED parts: ${FAILED_PARTS[*]}"
  exit 1
fi
log "setup done (venv=${PART_STATE[venv]} models=${PART_STATE[models]} check=${PART_STATE[check]})"
