#!/usr/bin/env bash
# Milestone 8 setup of the generated-furniture step (docs/milestone8.md §3) on a RunPod pod: builds
# /opt/wenart/venv-trellis for `python -m wenart.assets.generate run` (Z-Image-Turbo text-to-image, then
# TRELLIS.2-4B image-to-3D and GLB export). Run by the prep job's `trellis_setup` step after scripts/pod_setup.sh.
# Idempotent and timed: every part is stamped or cached, so a second run on the same pod only checks; the built
# wheels are cached on the volume, so the next pod installs them in minutes. Logs in /workspace/logs/.
#
# Parts (TRELLIS_SETUP_PARTS, default all, in this order):
#   preflight  GPU (nvidia-smi name, driver, compute_cap -> TORCH_CUDA_ARCH_LIST: 12.0 on the Blackwell
#              RTX PRO 6000, 9.0 on H100/H200, 8.9 on L40S/RTX 4090, ...; TRELLIS_ARCH_LIST overrides; < 8.0 is
#              refused), the image's python3 and torch (version, CUDA, C++11 ABI), nvcc of CUDA_HOME (12.8 or newer
#              for sm_120), build tools (apt build-essential when g++ is missing), free disk, HF_TOKEN set (yes/no;
#              the value is never printed).
#   venv       /opt/wenart/venv-trellis on the container disk, --system-site-packages like venv-polish (the image's
#              torch 2.9.1 stays; every pip install runs with -c of the image's torch/torchvision/torchaudio/triton
#              pins): diffusers==0.40.0 transformers==5.18.0 accelerate==1.15.0 huggingface-hub==1.33.0
#              safetensors>=0.8.0 opencv-python-headless==4.14.0.94 numpy>=2 (the versions validated with
#              Z-Image-Turbo by the polish), the TRELLIS.2 inference deps of its setup.sh --basic (trimesh 4.12.2,
#              easydict, plyfile, zstandard, kornia, timm, einops, tqdm; BiRefNet's remote code needs timm, kornia,
#              einops), the build tools (ninja, setuptools, wheel) and the repo's CPU deps (as venv-polish).
#              Not installed: gradio, tensorboard, pandas, lpips, imageio (demo and training only), utils3d and
#              pillow-simd (render previews only).
#   src        TRELLIS.2 at TRELLIS_COMMIT into /opt/wenart/src/TRELLIS.2 (with its o-voxel eigen submodule), put on
#              the venv's path by a .pth file; the extension sources at pinned commits into /opt/wenart/src/ext
#              (upstream setup.sh clones CuMesh and FlexGEMM at their branch heads: pinned here).
#   ext        CUDA extensions built with TORCH_CUDA_ARCH_LIST, MAX_JOBS from the pod's cgroup CPU and memory:
#              nvdiffrast v0.4.0, CuMesh (+ cubvh, xatlas), FlexGEMM, o-voxel (required: o_voxel.postprocess.to_glb
#              imports nvdiffrast, cumesh, flex_gemm) and nvdiffrec renderutils (optional: PBR preview rendering only;
#              a failure is a warning). Each is built once into /workspace/wheels/trellis/<key>/ (key = TRELLIS.2
#              commit, torch, CUDA, python, arch list and a hash of every pin) and installed from there with
#              --no-deps when present (o-voxel names its deps as unpinned git URLs). The FlexGEMM autotune cache
#              (keyed by GPU name; the package ships A100/MI300X entries only) lives on the volume
#              (/workspace/cache/flex_gemm/autotune_cache.json), so the Triton tuning on a new GPU happens once.
#   attn       the attention backend of TRELLIS.2 (trellis2/modules/attention/config.py: xformers, flash_attn,
#              flash_attn_3, sdpa, naive; trellis2/modules/sparse/config.py: xformers, flash_attn, flash_attn_3 only;
#              the windowed sparse attention: xformers, flash_attn only -> sdpa alone can not run TRELLIS.2).
#              TRELLIS_ATTN=auto (default): flash-attn 2.8.3 (the cached wheel, else the official prebuilt release
#              wheel for this torch/CUDA/python/ABI, built with CUDA 12.9 for sm 80/90/100/120; a source build only
#              with TRELLIS_FA_SOURCE_BUILD=1, FLASH_ATTN_CUDA_ARCHS from the GPU, bounded by
#              TRELLIS_FA_BUILD_TIMEOUT), else xformers 0.0.33.post2 (its PyPI wheel requires torch==2.9.1, the
#              image's). Each candidate must pass a bf16 varlen attention check on the GPU against torch SDPA; a
#              failed one is uninstalled. TRELLIS_ATTN=flash_attn|xformers forces one.
#   models     huggingface_hub.snapshot_download of every model of wenart/assets/generate.yaml (pinned revision and
#              allow patterns) into HF_HOME=/opt/wenart/hf (container disk); the gated DINOv3 first, so a missing
#              access grant fails in seconds with the reason (no other download is started then).
#   check      in venv-trellis on the GPU: sm_XX kernels of torch for this GPU, nvdiffrast rasterizes a triangle,
#              CuMesh builds a mesh, flex_gemm / o_voxel / trellis2 / Trellis2ImageTo3DPipeline / diffusers
#              ZImagePipeline import, the attention backend TRELLIS.2 reports is the chosen one, and the pinned
#              pipeline.json passes wenart.assets.generate.pipeline_args (the names checked for this revision).
# Writes venv-trellis/trellis_env.json (ATTN_BACKEND, FlexGEMM cache path, TRELLIS.2 source and commit; read by
# wenart.assets.generate) and setup_trellis.json ($WENART_RESULTS, else /workspace/logs): status ok|failed, reason,
# per part state and seconds, versions, commits, backend, wheel cache key and hits, models, seconds.
# Exit 0 when every required part is ok, else 1 with the reason (the prep job then builds the library without
# generated models and says so). TRELLIS_SETUP_PLAN_ONLY=1 prints the plan (arch list, key, pins) and changes
# nothing.
#
# Sources checked on 4 Oct 2026: TRELLIS.2 main @75fbf01 (README, setup.sh, example.py, app.py,
# trellis2/pipelines/trellis2_image_to_3d.py, o-voxel/o_voxel/postprocess.py to_glb, the attention configs);
# git ls-remote of CuMesh (main @12289e1 includes "Fix Blackwell (sm_120) illegal memory access", Mar 2026),
# FlexGEMM (main @6dd94a8), nvdiffrast (tag v0.4.0 @253ac4f), nvdiffrec (branch renderutils @b296927); PyPI
# metadata of xformers 0.0.33.post2 (torch==2.9.1) and flash-attn 2.8.3 (setup.py default archs 80;90;100;120;
# the release wheel flash_attn-2.8.3+cu12torch2.9cxx11abiTRUE-cp312-cp312-linux_x86_64.whl exists); the Hugging
# Face API for every model of generate.yaml (DINOv3 is gated with manual approval).
set -Eeuo pipefail
trap 'echo "[setup-trellis] ERROR at line $LINENO" >&2' ERR

WS="${WENART_WS:-/workspace}"          # WENART_WS / WENART_FAST: CPU tests only
LOGS=$WS/logs
FAST="${WENART_FAST:-/opt/wenart}"     # container disk: fast, wiped with the pod
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV=$FAST/venv-trellis
export TRELLIS_VENV=$VENV                # recorded in setup_trellis.json
SRC=$FAST/src
TRELLIS_SRC=$SRC/TRELLIS.2
EXT_SRC=$SRC/ext
BUILD=$FAST/build-trellis
STATE_DIR=$FAST/setup-trellis
CONSTRAINTS=$FAST/trellis-constraints.txt
WHEELS_ROOT="${TRELLIS_WHEELS:-$WS/wheels/trellis}"
FLEX_CACHE="${TRELLIS_FLEX_CACHE:-$WS/cache/flex_gemm/autotune_cache.json}"
GEN_YAML=$REPO_DIR/wenart/assets/generate.yaml
mkdir -p "$LOGS"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export HF_HUB_OFFLINE=0                # downloads happen here; the job goes offline afterwards
export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_CACHE_DIR=$WS/pip-cache
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}"
PIP_LOG=$LOGS/setup-trellis-pip.log
BUILD_LOG=$LOGS/setup-trellis-build.log

# --- pins ---------------------------------------------------------------------------------
TRELLIS_REPO=https://github.com/microsoft/TRELLIS.2
TRELLIS_COMMIT=75fbf0183001ed9876c8dbb35de6b68552ee08bd      # = generate.yaml trellis_code.commit (test checks)
NVDIFFRAST_REPO=https://github.com/NVlabs/nvdiffrast
NVDIFFRAST_COMMIT=253ac4fcea7de5f396371124af597e6cc957bfae   # tag v0.4.0 (upstream setup.sh: -b v0.4.0)
NVDIFFREC_REPO=https://github.com/JeffreyXiang/nvdiffrec
NVDIFFREC_COMMIT=b296927cc7fd01c2ac1087c8065c4d7248f72da4    # branch renderutils
CUMESH_REPO=https://github.com/JeffreyXiang/CuMesh
CUMESH_COMMIT=12289e1062f0603f2f0d0771b02e1395d247f26f       # main, 9 May 2026 (sm_120 stream fix)
FLEXGEMM_REPO=https://github.com/JeffreyXiang/FlexGEMM
FLEXGEMM_COMMIT=6dd94a859c26ee8246888502eada3dd8ad85532e     # main, 22 Apr 2026
FLASH_ATTN_VERSION=2.8.3
XFORMERS_VERSION=0.0.33.post2                                # requires torch==2.9.1
TORCHVISION_FALLBACK=0.24.1                                  # pairs with the image's torch 2.9.1
TORCH_INDEX=https://download.pytorch.org/whl/cu128
PINS=("diffusers==0.40.0" "transformers==5.18.0" "accelerate==1.15.0" "huggingface-hub==1.33.0"
      "safetensors>=0.8.0" "opencv-python-headless==4.14.0.94" "numpy>=2")
TRELLIS_DEPS=("trimesh==4.12.2" "easydict==1.13" "plyfile==1.1.5" "zstandard==0.25.0" "kornia==0.8.3"
              "timm==1.0.30" "einops==0.8.2" "tqdm==4.70.1" "ninja==1.13.2" "setuptools==80.9.0" "wheel==0.45.1")
# name|source dir|wheel name prefix|required
EXTENSIONS=("nvdiffrast|$EXT_SRC/nvdiffrast|nvdiffrast|1" "cumesh|$EXT_SRC/CuMesh|cumesh|1"
            "flex_gemm|$EXT_SRC/FlexGEMM|flex_gemm|1" "o_voxel|$TRELLIS_SRC/o-voxel|o_voxel|1"
            "nvdiffrec|$EXT_SRC/nvdiffrec|nvdiffrec_render|0")

read -r -a PARTS <<< "${TRELLIS_SETUP_PARTS:-preflight venv src ext attn models check}"
ALL_PARTS="preflight venv src ext attn models check"
for part in "${PARTS[@]}"; do
  case " $ALL_PARTS " in
    *" $part "*) ;;
    *) echo "[setup-trellis] unknown part '$part' in TRELLIS_SETUP_PARTS (known: $ALL_PARTS)" >&2; exit 2 ;;
  esac
done
has_part() { local p; for p in "${PARTS[@]}"; do [ "$p" = "$1" ] && return 0; done; return 1; }

log() { echo "[$(date -u +%H:%M:%S)] setup-trellis: $*"; }
FAIL_REASON=""
fail() { log "FAILED: $*"; if [ -z "$FAIL_REASON" ]; then FAIL_REASON="$*"; fi; return 1; }

# gpu_arch_list: TORCH_CUDA_ARCH_LIST for the visible GPUs ("12.0", "9.0", "8.9;12.0", ...), from
# nvidia-smi --query-gpu=compute_cap or TRELLIS_ARCH_LIST; empty when unknown.
gpu_arch_list() {
  local caps
  if [ -n "${TRELLIS_ARCH_LIST:-}" ]; then echo "$TRELLIS_ARCH_LIST"; return 0; fi
  caps=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | tr -d ' \r' | grep -E '^[0-9]+\.[0-9]+$' \
    | sort -u -t. -k1,1n -k2,2n | paste -sd';' - || true)
  echo "$caps"
}

# arch_ok <list>: every entry is N.M with N >= 8 (Ampere or newer: flash-attn 2 and TRELLIS.2's bf16 models).
arch_ok() {
  local a
  [ -n "$1" ] || return 1
  IFS=';' read -r -a _archs <<< "$1"
  for a in "${_archs[@]}"; do
    [[ "$a" =~ ^([0-9]+)\.[0-9]+$ ]] || return 1
    [ "${BASH_REMATCH[1]}" -ge 8 ] || return 1
  done
}

# arch_tag "8.9;12.0" -> sm89-sm120 ; fa_archs "8.9;12.0" -> 89;120 (FLASH_ATTN_CUDA_ARCHS)
arch_tag() { echo "$1" | tr ';' '\n' | sed -E 's/^([0-9]+)\.([0-9]+)$/sm\1\2/' | paste -sd'-' -; }
fa_archs() { echo "$1" | tr ';' '\n' | sed -E 's/^([0-9]+)\.([0-9]+)$/\1\2/' | paste -sd';' -; }

# image_python_info: "<python> <torch> <torch cuda> <cxx11abi TRUE|FALSE>" of the image's python3 (or "unknown").
image_python_info() {
  python3 - <<'PY' 2>/dev/null || echo "unknown unknown unknown unknown"
import sys
pyv = "%d.%d.%d" % sys.version_info[:3]
try:
    import torch
    print(pyv, torch.__version__, torch.version.cuda or "none", str(bool(torch._C._GLIBCXX_USE_CXX11_ABI)).upper())
except Exception:
    print(pyv, "none", "none", "FALSE")
PY
}

# build_jobs <GiB per job>: parallel compile jobs from the pod's cgroup CPU quota and memory limit (or the host's).
build_jobs() {
  local per=$1 cpus mem_kb mem_gib q p limit jobs
  if [ -n "${TRELLIS_MAX_JOBS:-}" ]; then echo "$TRELLIS_MAX_JOBS"; return 0; fi
  cpus=$(nproc 2>/dev/null || echo 4)
  if [ -r /sys/fs/cgroup/cpu.max ]; then
    read -r q p < /sys/fs/cgroup/cpu.max || true
    if [[ "${q:-max}" =~ ^[0-9]+$ ]] && [[ "${p:-0}" =~ ^[0-9]+$ ]] && [ "$p" -gt 0 ]; then
      cpus=$(( q / p > 0 ? q / p : 1 ))
    fi
  fi
  mem_kb=$(awk '/^MemAvailable:/ {print $2}' /proc/meminfo 2>/dev/null || echo 16777216)
  mem_gib=$(( ${mem_kb:-16777216} / 1048576 ))
  limit=""
  if [ -r /sys/fs/cgroup/memory.max ]; then limit=$(cat /sys/fs/cgroup/memory.max 2>/dev/null || true)
  elif [ -r /sys/fs/cgroup/memory/memory.limit_in_bytes ]; then limit=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes 2>/dev/null || true); fi
  if [[ "$limit" =~ ^[0-9]+$ ]] && [ "${#limit}" -lt 19 ]; then
    if [ $(( limit / 1073741824 )) -lt "$mem_gib" ]; then mem_gib=$(( limit / 1073741824 )); fi
  fi
  jobs=$(( mem_gib / per ))
  if [ "$jobs" -gt "$cpus" ]; then jobs=$cpus; fi
  if [ "$jobs" -gt 32 ]; then jobs=32; fi
  if [ "$jobs" -lt 1 ]; then jobs=1; fi
  echo "$jobs"
}

ARCH_LIST=$(gpu_arch_list)
read -r PYV TORCH_VER TORCH_CUDA TORCH_ABI <<< "$(image_python_info)"
PIN_HASH=$(printf '%s\n' "$TRELLIS_COMMIT" "$NVDIFFRAST_COMMIT" "$NVDIFFREC_COMMIT" "$CUMESH_COMMIT" \
  "$FLEXGEMM_COMMIT" "$FLASH_ATTN_VERSION" "$XFORMERS_VERSION" "${PINS[@]}" "${TRELLIS_DEPS[@]}" | sha256sum | cut -c1-8)
WHEEL_KEY="${TRELLIS_COMMIT:0:8}-torch${TORCH_VER//+/_}-cu${TORCH_CUDA//./}-py${PYV%.*}-$(arch_tag "${ARCH_LIST:-none}")-$PIN_HASH"
WHEEL_KEY="${WHEEL_KEY//./}"
WHEELS_DIR=$WHEELS_ROOT/$WHEEL_KEY

if [ "${TRELLIS_SETUP_PLAN_ONLY:-0}" = "1" ]; then
  echo "PLAN parts=${PARTS[*]}"
  echo "PLAN arch_list=${ARCH_LIST:-unknown} arch_ok=$(arch_ok "$ARCH_LIST" && echo yes || echo no)"
  echo "PLAN fa_archs=$(fa_archs "${ARCH_LIST:-}")"
  echo "PLAN python=$PYV torch=$TORCH_VER cuda=$TORCH_CUDA cxx11abi=$TORCH_ABI"
  echo "PLAN wheel_key=$WHEEL_KEY"
  echo "PLAN wheels_dir=$WHEELS_DIR"
  echo "PLAN trellis_commit=$TRELLIS_COMMIT attn=${TRELLIS_ATTN:-auto} flash_attn=$FLASH_ATTN_VERSION xformers=$XFORMERS_VERSION"
  exit 0
fi

mkdir -p "$FAST" "$STATE_DIR" "$SRC" "$EXT_SRC" "$BUILD"
rm -f "$STATE_DIR"/ext.tsv "$STATE_DIR"/attn.tsv "$STATE_DIR"/models.json "$STATE_DIR"/check.txt "$STATE_DIR"/preflight.env
T_START=$(date +%s)
DISK_BEFORE=$(df -B1 --output=avail "$FAST" 2>/dev/null | tail -1 | tr -d ' ' || echo "")
declare -A PART_STATE=([preflight]=skipped [venv]=skipped [src]=skipped [ext]=skipped [attn]=skipped [models]=skipped [check]=skipped)
declare -A PART_SECONDS=([preflight]=0 [venv]=0 [src]=0 [ext]=0 [attn]=0 [models]=0 [check]=0)
ATTN_BACKEND=""

# run_part <name> <function> [needed part ...]: timed; skipped when a needed part is not ok.
run_part() {
  local name=$1 fn=$2 rc=0 t0 need
  shift 2
  for need in "$@"; do
    if [ "${PART_STATE[$need]}" != "ok" ]; then
      PART_STATE[$name]="skipped (needs $need)"
      log "$name skipped: part $need is ${PART_STATE[$need]}"
      return 0
    fi
  done
  t0=$(date +%s)
  log "start: $name"
  "$fn" || rc=$?
  PART_SECONDS[$name]=$(( $(date +%s) - t0 ))
  if [ "$rc" -eq 0 ]; then PART_STATE[$name]=ok; else PART_STATE[$name]=failed; log "$name FAILED (rc $rc)"; fi
  log "done: $name in ${PART_SECONDS[$name]} s (${PART_STATE[$name]})"
  return 0
}

# --- part preflight -----------------------------------------------------------------------
part_preflight() {
  local gpu nvcc_ver hf
  {
    echo "gpu=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 || true)"
    echo "driver=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 || true)"
    echo "compute_cap=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1 || true)"
    echo "vram_mib=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 || true)"
  } > "$STATE_DIR/preflight.env"
  gpu=$(sed -n 's/^gpu=//p' "$STATE_DIR/preflight.env")
  log "GPU: ${gpu:-none}; arch list: ${ARCH_LIST:-unknown}; python $PYV, torch $TORCH_VER (CUDA $TORCH_CUDA, cxx11abi $TORCH_ABI)"
  [ -n "$gpu" ] || { fail "no GPU visible (nvidia-smi)"; return 1; }
  arch_ok "$ARCH_LIST" || { fail "GPU compute capability '${ARCH_LIST:-unknown}' is not 8.0 or newer (or not readable)"; return 1; }
  [ "$TORCH_VER" != "none" ] && [ "$TORCH_VER" != "unknown" ] || { fail "the image's python3 has no torch"; return 1; }
  if [ ! -x "$CUDA_HOME/bin/nvcc" ]; then
    fail "no nvcc at $CUDA_HOME/bin/nvcc: the CUDA extensions can not be built (a CUDA devel image is needed)"; return 1
  fi
  nvcc_ver=$("$CUDA_HOME/bin/nvcc" --version | sed -n 's/.*release \([0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' | head -1)
  echo "nvcc=$nvcc_ver" >> "$STATE_DIR/preflight.env"
  log "nvcc $nvcc_ver ($CUDA_HOME)"
  if [[ ";$ARCH_LIST;" == *";12."* ]] || [[ ";$ARCH_LIST;" == *";10."* ]]; then
    if ! printf '%s\n%s\n' "12.8" "$nvcc_ver" | sort -V -C; then
      fail "nvcc $nvcc_ver can not compile for Blackwell ($ARCH_LIST): CUDA 12.8 or newer is needed"; return 1
    fi
  fi
  if ! command -v g++ >/dev/null 2>&1 || ! command -v git >/dev/null 2>&1; then
    log "installing build-essential and git (apt)"
    export DEBIAN_FRONTEND=noninteractive
    { apt-get update -qq && apt-get install -y -qq --no-install-recommends build-essential git ca-certificates; } \
      >> "$BUILD_LOG" 2>&1 || { fail "apt-get install build-essential git failed (see $BUILD_LOG)"; return 1; }
  fi
  hf=no
  if [ -n "${HF_TOKEN:-}" ]; then hf=yes; fi
  echo "hf_token_set=$hf" >> "$STATE_DIR/preflight.env"
  log "HF_TOKEN set: $hf; free on $FAST: $(df -h --output=avail "$FAST" 2>/dev/null | tail -1 | tr -d ' ')"
  log "wheel cache: $WHEELS_DIR"
  # Gated models (generate.yaml `gated:`): probe one small file per repo before any build, so a pod whose token
  # has no access stops in seconds, not after the CUDA builds. The token is never in curl's arguments or the log.
  local row repo rev file code probe_py
  probe_py=""
  for probe_py in "${WENART_PY:-/workspace/venv/bin/python}" python3; do
    if command -v "$probe_py" >/dev/null 2>&1 && "$probe_py" -c 'import yaml' 2>/dev/null; then break; fi
    probe_py=""
  done
  if [ -z "$probe_py" ]; then log "no python with pyyaml for the gated-model probe: the models part checks access"; return 0; fi
  while read -r row; do
    [ -n "$row" ] || continue
    read -r repo rev file <<< "$row"
    if [ -n "${HF_TOKEN:-}" ]; then
      # curl >= 8.3 reads the token from its own environment (--variable %NAME, --expand-header): the shell
      # never expands it.
      code=$(curl -s -o /dev/null -w '%{http_code}' --variable %HF_TOKEN \
        --expand-header 'Authorization: Bearer {{HF_TOKEN}}' -I -L --max-time 30 \
        "https://huggingface.co/$repo/resolve/$rev/$file" || echo 000)
    else
      code=401
    fi
    echo "gated_access_${repo//[^A-Za-z0-9]/_}=$code" >> "$STATE_DIR/preflight.env"
    case "$code" in
      200|302) log "gated model $repo: access ok (HTTP $code)" ;;
      000) log "gated model $repo: probe failed (no answer); the models part will tell" ;;
      *) fail "$repo is gated: the Hugging Face account of the RunPod secret hf_token has no access yet (HTTP $code; request it on https://huggingface.co/$repo and wait for the approval)"; return 1 ;;
    esac
  done < <("$probe_py" - "$GEN_YAML" <<'PY'
import sys
import yaml
cfg = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
for m in (cfg.get("models") or {}).values():
    if m.get("gated"):
        files = m.get("files") or ["config.json"]
        print(m["repo"], m["revision"], files[0])
PY
)
}

# --- part venv ----------------------------------------------------------------------------
part_venv() {
  local req_hash stamp reqs
  { python3 -m pip freeze 2>/dev/null | grep -iE '^(torch|torchvision|torchaudio|triton)==' || true; } > "$CONSTRAINTS"
  if ! grep -qiE '^torch==' "$CONSTRAINTS"; then
    python3 -c 'import torch; print("torch==" + torch.__version__)' >> "$CONSTRAINTS" 2>/dev/null || true
  fi
  grep -qiE '^torch==' "$CONSTRAINTS" || { fail "no torch in the image's python: refusing a venv that could pull its own"; return 1; }
  log "image constraints: $(tr '\n' ' ' < "$CONSTRAINTS")"
  reqs=$FAST/trellis-requirements.txt
  grep -viE '^huggingface[-_]hub' "$REPO_DIR/scripts/pod_requirements.txt" | grep -viE '^opencv-python-headless' \
    | sed -E 's/^(numpy|pillow|matplotlib)[[:space:]]*==.*$/\1/' > "$reqs" || true
  req_hash=$( { printf '%s\n' "${PINS[@]}" "${TRELLIS_DEPS[@]}"; cat "$reqs" "$CONSTRAINTS"; echo "$PYV ${WENART_IMAGE:-}"; } \
    | sha256sum | cut -c1-16)
  stamp=$VENV/.trellis-venv-$req_hash
  if [ -f "$stamp" ]; then log "venv-trellis already stamped good ($stamp)"; return 0; fi
  [ -x "$VENV/bin/python" ] || python3 -m venv --system-site-packages "$VENV" || { fail "python3 -m venv failed"; return 1; }
  "$VENV/bin/python" -m pip install -q --upgrade pip >> "$PIP_LOG" 2>&1 || { fail "pip upgrade failed (see $PIP_LOG)"; return 1; }
  if ! "$VENV/bin/python" -c "import torchvision" 2>/dev/null; then
    log "no torchvision in the image: torchvision==$TORCHVISION_FALLBACK from $TORCH_INDEX (--no-deps)"
    "$VENV/bin/python" -m pip install -q --no-deps -c "$CONSTRAINTS" "torchvision==$TORCHVISION_FALLBACK" \
      --index-url "$TORCH_INDEX" >> "$PIP_LOG" 2>&1 || { fail "torchvision install failed (see $PIP_LOG)"; return 1; }
    echo "torchvision==$TORCHVISION_FALLBACK" >> "$CONSTRAINTS"
  fi
  log "pip install ${PINS[*]} ${TRELLIS_DEPS[*]} + $(wc -l < "$reqs") repo requirements (log $PIP_LOG)"
  if ! "$VENV/bin/python" -m pip install -q -c "$CONSTRAINTS" "${PINS[@]}" "${TRELLIS_DEPS[@]}" -r "$reqs" >> "$PIP_LOG" 2>&1; then
    tail -n 20 "$PIP_LOG"; fail "pip install of the venv-trellis requirements failed (see $PIP_LOG)"; return 1
  fi
  if ! "$VENV/bin/python" - >> "$PIP_LOG" 2>&1 <<'PY'
import cv2, diffusers, easydict, einops, kornia, plyfile, timm, torch, transformers, trimesh, yaml, zstandard  # noqa
from diffusers import ZImagePipeline  # noqa: F401
from transformers import AutoModelForImageSegmentation, DINOv3ViTModel  # noqa: F401
print("venv imports ok", torch.__version__, diffusers.__version__, transformers.__version__)
PY
  then
    tail -n 20 "$PIP_LOG"; fail "venv-trellis imports failed (see $PIP_LOG)"; return 1
  fi
  find "$VENV" -maxdepth 1 -name '.trellis-venv-*' -delete
  touch "$stamp"
  log "venv-trellis stamped good ($stamp)"
}

# --- part src -----------------------------------------------------------------------------
# clone_at <url> <commit> <dir> <submodules 0|1>: the tree at exactly <commit> (stamped .wenart-commit).
clone_at() {
  local url=$1 commit=$2 dir=$3 subs=$4 part
  if [ -f "$dir/.wenart-commit" ] && [ "$(cat "$dir/.wenart-commit")" = "$commit" ]; then
    log "$(basename "$dir") @${commit:0:8} already checked out"; return 0
  fi
  part="$dir.partial"
  rm -rf "$part"
  mkdir -p "$part"
  {
    git -C "$part" init -q && git -C "$part" remote add origin "$url" \
      && git -C "$part" fetch -q --depth 1 origin "$commit" && git -C "$part" checkout -q FETCH_HEAD
  } >> "$BUILD_LOG" 2>&1 || { fail "git fetch of $url @$commit failed (see $BUILD_LOG)"; return 1; }
  [ "$(git -C "$part" rev-parse HEAD)" = "$commit" ] || { fail "$url: HEAD is not $commit"; return 1; }
  if [ "$subs" = "1" ]; then
    if ! git -C "$part" submodule update -q --init --recursive --depth 1 >> "$BUILD_LOG" 2>&1; then
      log "$(basename "$dir"): shallow submodule fetch failed, retrying with full history"
      git -C "$part" submodule update -q --init --recursive >> "$BUILD_LOG" 2>&1 \
        || { fail "submodules of $url @$commit failed (see $BUILD_LOG)"; return 1; }
    fi
  fi
  echo "$commit" > "$part/.wenart-commit"
  rm -rf "$dir"
  mv "$part" "$dir"
  log "$(basename "$dir") @${commit:0:8} checked out"
}

part_src() {
  local site
  clone_at "$TRELLIS_REPO" "$TRELLIS_COMMIT" "$TRELLIS_SRC" 1 || return 1
  [ -f "$TRELLIS_SRC/o-voxel/third_party/eigen/Eigen/Core" ] || { fail "o-voxel's eigen submodule is missing"; return 1; }
  clone_at "$NVDIFFRAST_REPO" "$NVDIFFRAST_COMMIT" "$EXT_SRC/nvdiffrast" 0 || return 1
  clone_at "$NVDIFFREC_REPO" "$NVDIFFREC_COMMIT" "$EXT_SRC/nvdiffrec" 0 || return 1
  clone_at "$CUMESH_REPO" "$CUMESH_COMMIT" "$EXT_SRC/CuMesh" 1 || return 1
  clone_at "$FLEXGEMM_REPO" "$FLEXGEMM_COMMIT" "$EXT_SRC/FlexGEMM" 1 || return 1
  site=$("$VENV/bin/python" -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])') \
    || { fail "venv-trellis python not usable"; return 1; }
  echo "$TRELLIS_SRC" > "$site/wenart_trellis2.pth"
  log "trellis2 on the venv path ($site/wenart_trellis2.pth)"
}

# --- part ext -----------------------------------------------------------------------------
# install_ext <name> <src dir> <wheel prefix> <required 0|1>: from the wheel cache, else built and cached.
install_ext() {
  local name=$1 dir=$2 prefix=$3 required=$4 whl stamp t0 hit=0 jobs out
  stamp=$VENV/.trellis-ext-$name-$WHEEL_KEY
  t0=$(date +%s)
  if [ -f "$stamp" ]; then
    printf '%s\tok\tinstalled\t0\t%s\n' "$name" "$(cat "$stamp")" >> "$STATE_DIR/ext.tsv"
    log "$name already installed from $(cat "$stamp")"; return 0
  fi
  whl=$(find "$WHEELS_DIR" -maxdepth 1 -name "${prefix}-*.whl" 2>/dev/null | sort | head -1)
  if [ -n "$whl" ]; then
    hit=1
    log "$name: cached wheel $(basename "$whl")"
  else
    jobs=$(build_jobs 4)
    out=$BUILD/wheels-$name
    rm -rf "$out"
    mkdir -p "$out"
    log "$name: building (TORCH_CUDA_ARCH_LIST=$ARCH_LIST MAX_JOBS=$jobs; log $BUILD_LOG)"
    if ! (cd "$dir" && PATH="$VENV/bin:$CUDA_HOME/bin:$PATH" TORCH_CUDA_ARCH_LIST="$ARCH_LIST" MAX_JOBS="$jobs" \
          BUILD_TARGET=cuda LIBRARY_PATH="$CUDA_HOME/lib64/stubs:${LIBRARY_PATH:-}" \
          "$VENV/bin/python" -m pip wheel --no-build-isolation --no-deps -w "$out" . >> "$BUILD_LOG" 2>&1); then
      printf '%s\tfailed\tbuild\t%s\t-\n' "$name" "$(( $(date +%s) - t0 ))" >> "$STATE_DIR/ext.tsv"
      tail -n 30 "$BUILD_LOG"
      if [ "$required" = "1" ]; then fail "building $name failed (see $BUILD_LOG)"; return 1; fi
      log "WARNING: optional $name did not build (not needed for generation)"; return 0
    fi
    whl=$(find "$out" -maxdepth 1 -name "${prefix}-*.whl" | sort | head -1)
    [ -n "$whl" ] || { fail "$name: no ${prefix}-*.whl after the build"; return 1; }
    mkdir -p "$WHEELS_DIR"
    cp -f "$whl" "$WHEELS_DIR/.$(basename "$whl").tmp" && mv -f "$WHEELS_DIR/.$(basename "$whl").tmp" "$WHEELS_DIR/$(basename "$whl")"
    whl=$WHEELS_DIR/$(basename "$whl")
  fi
  if ! "$VENV/bin/python" -m pip install -q --no-deps --force-reinstall "$whl" >> "$PIP_LOG" 2>&1; then
    printf '%s\tfailed\tinstall\t%s\t%s\n' "$name" "$(( $(date +%s) - t0 ))" "$(basename "$whl")" >> "$STATE_DIR/ext.tsv"
    if [ "$required" = "1" ]; then fail "installing $(basename "$whl") failed (see $PIP_LOG)"; return 1; fi
    log "WARNING: optional $name did not install"; return 0
  fi
  echo "$(basename "$whl")" > "$stamp"
  printf '%s\tok\t%s\t%s\t%s\n' "$name" "$([ "$hit" = 1 ] && echo cache_hit || echo built)" \
    "$(( $(date +%s) - t0 ))" "$(basename "$whl")" >> "$STATE_DIR/ext.tsv"
  log "$name installed ($([ "$hit" = 1 ] && echo 'cache hit' || echo built) in $(( $(date +%s) - t0 )) s)"
}

part_ext() {
  local spec name dir prefix required
  mkdir -p "$WHEELS_DIR"
  printf '%s\n' "TRELLIS.2 $TRELLIS_COMMIT" "nvdiffrast $NVDIFFRAST_COMMIT" "nvdiffrec $NVDIFFREC_COMMIT" \
    "CuMesh $CUMESH_COMMIT" "FlexGEMM $FLEXGEMM_COMMIT" "torch $TORCH_VER" "cuda $TORCH_CUDA" "python $PYV" \
    "arch $ARCH_LIST" > "$WHEELS_DIR/pins.txt"
  for spec in "${EXTENSIONS[@]}"; do
    IFS='|' read -r name dir prefix required <<< "$spec"
    install_ext "$name" "$dir" "$prefix" "$required" || return 1
  done
  # FlexGEMM: the shipped autotune cache seeds the one on the volume (entries keyed by GPU name; merged by setup.py
  # only when it runs, i.e. not for a cached wheel).
  if [ ! -s "$FLEX_CACHE" ]; then
    mkdir -p "$(dirname "$FLEX_CACHE")"
    cp -f "$EXT_SRC/FlexGEMM/autotune_cache.json" "$FLEX_CACHE" || { fail "cannot seed $FLEX_CACHE"; return 1; }
  fi
  "$VENV/bin/python" -c "import nvdiffrast.torch, cumesh, flex_gemm, o_voxel" >> "$PIP_LOG" 2>&1 \
    || { tail -n 20 "$PIP_LOG"; fail "the extensions do not import (see $PIP_LOG)"; return 1; }
}

# --- part attn ----------------------------------------------------------------------------
ATTN_CHECK=$(cat <<'PY'
import sys

import torch

backend = sys.argv[1]
torch.manual_seed(0)
lens, heads, dim = [77, 300], 8, 64
q, k, v = (torch.randn(sum(lens), heads, dim, device="cuda", dtype=torch.bfloat16) for _ in range(3))
if backend == "flash_attn":
    import flash_attn
    cu = torch.tensor([0, lens[0], sum(lens)], device="cuda", dtype=torch.int32)
    out = flash_attn.flash_attn_varlen_func(q, k, v, cu, cu, max(lens), max(lens))
    version = flash_attn.__version__
else:
    import xformers
    import xformers.ops as xops
    mask = xops.fmha.BlockDiagonalMask.from_seqlens(lens, lens)
    out = xops.memory_efficient_attention(q.unsqueeze(0), k.unsqueeze(0), v.unsqueeze(0), mask)[0]
    version = xformers.__version__
torch.cuda.synchronize()
ref, start = [], 0
for n in lens:
    qq, kk, vv = (t[start:start + n].transpose(0, 1).float() for t in (q, k, v))
    ref.append(torch.nn.functional.scaled_dot_product_attention(qq, kk, vv).transpose(0, 1))
    start += n
err = float((out.float() - torch.cat(ref)).abs().max())
if not err < 3e-2:
    sys.exit(f"{backend} {version}: max abs error {err} against torch SDPA")
print(f"ATTN_CHECK {backend} {version} max_abs_err={err:.4g}")
PY
)

attn_check() {
  local backend=$1 out
  if out=$("$VENV/bin/python" -c "$ATTN_CHECK" "$backend" 2>&1); then
    log "$(echo "$out" | tail -1)"; return 0
  fi
  log "$backend check failed: $(echo "$out" | tail -3 | tr '\n' ' ')"; return 1
}

# fa_wheel_name: the official release wheel name for this torch/CUDA/python/ABI (flash-attn setup.py get_wheel_url).
fa_wheel_name() {
  local tm py cu
  tm=$(echo "$TORCH_VER" | cut -d. -f1,2)
  py="cp$(echo "$PYV" | cut -d. -f1,2 | tr -d .)"
  cu=$(echo "$TORCH_CUDA" | cut -d. -f1)
  echo "flash_attn-${FLASH_ATTN_VERSION}+cu${cu}torch${tm}cxx11abi${TORCH_ABI}-${py}-${py}-linux_x86_64.whl"
}

try_flash_attn() {
  local whl name url tmp jobs out
  whl=$(find "$WHEELS_DIR" -maxdepth 1 -name "flash_attn-${FLASH_ATTN_VERSION}*.whl" 2>/dev/null | sort | head -1)
  if [ -z "$whl" ]; then
    name=$(fa_wheel_name)
    url="https://github.com/Dao-AILab/flash-attention/releases/download/v${FLASH_ATTN_VERSION}/${name}"
    tmp=$BUILD/$name
    log "flash-attn: release wheel $url"
    if curl -fsSL --retry 3 -o "$tmp" "$url" 2>> "$BUILD_LOG"; then
      whl=$tmp
    elif [ "${TRELLIS_FA_SOURCE_BUILD:-0}" = "1" ]; then
      jobs=$(build_jobs 9)
      out=$BUILD/wheels-flash_attn
      rm -rf "$out"; mkdir -p "$out"
      log "flash-attn: no release wheel; source build (FLASH_ATTN_CUDA_ARCHS=$(fa_archs "$ARCH_LIST"), MAX_JOBS=$jobs, timeout ${TRELLIS_FA_BUILD_TIMEOUT:-3600} s)"
      if ! PATH="$VENV/bin:$CUDA_HOME/bin:$PATH" FLASH_ATTENTION_FORCE_BUILD=TRUE FLASH_ATTN_CUDA_ARCHS="$(fa_archs "$ARCH_LIST")" \
           MAX_JOBS="$jobs" NVCC_THREADS=2 timeout "${TRELLIS_FA_BUILD_TIMEOUT:-3600}" \
           "$VENV/bin/python" -m pip wheel --no-build-isolation --no-deps -w "$out" "flash-attn==$FLASH_ATTN_VERSION" \
           >> "$BUILD_LOG" 2>&1; then
        log "flash-attn: source build failed or timed out (see $BUILD_LOG)"; return 1
      fi
      whl=$(find "$out" -maxdepth 1 -name "flash_attn-*.whl" | sort | head -1)
    else
      log "flash-attn: no release wheel for this torch/CUDA/python ($name); source build off (TRELLIS_FA_SOURCE_BUILD=1)"
      return 1
    fi
  fi
  [ -n "$whl" ] && [ -f "$whl" ] || return 1
  "$VENV/bin/python" -m pip install -q --no-deps --force-reinstall "$whl" "einops==0.8.2" >> "$PIP_LOG" 2>&1 \
    || { log "flash-attn: install of $(basename "$whl") failed"; return 1; }
  if ! attn_check flash_attn; then
    "$VENV/bin/python" -m pip uninstall -y -q flash-attn >> "$PIP_LOG" 2>&1 || true
    return 1
  fi
  if [ "$(dirname "$whl")" != "$WHEELS_DIR" ]; then
    cp -f "$whl" "$WHEELS_DIR/.$(basename "$whl").tmp" && mv -f "$WHEELS_DIR/.$(basename "$whl").tmp" "$WHEELS_DIR/$(basename "$whl")"
  fi
}

try_xformers() {
  local whl
  whl=$(find "$WHEELS_DIR" -maxdepth 1 -name "xformers-${XFORMERS_VERSION}-*.whl" 2>/dev/null | sort | head -1)
  if [ -z "$whl" ]; then
    "$VENV/bin/python" -m pip download -q --no-deps -d "$BUILD/xformers" "xformers==$XFORMERS_VERSION" >> "$PIP_LOG" 2>&1 \
      || { log "xformers: download of $XFORMERS_VERSION failed"; return 1; }
    whl=$(find "$BUILD/xformers" -maxdepth 1 -name "xformers-${XFORMERS_VERSION}-*.whl" | sort | head -1)
    [ -n "$whl" ] || { log "xformers: no wheel for $XFORMERS_VERSION"; return 1; }
    cp -f "$whl" "$WHEELS_DIR/.$(basename "$whl").tmp" && mv -f "$WHEELS_DIR/.$(basename "$whl").tmp" "$WHEELS_DIR/$(basename "$whl")"
    whl=$WHEELS_DIR/$(basename "$whl")
  fi
  "$VENV/bin/python" -m pip install -q --no-deps --force-reinstall "$whl" >> "$PIP_LOG" 2>&1 \
    || { log "xformers: install of $(basename "$whl") failed"; return 1; }
  if ! attn_check xformers; then
    "$VENV/bin/python" -m pip uninstall -y -q xformers >> "$PIP_LOG" 2>&1 || true
    return 1
  fi
}

part_attn() {
  local mode=${TRELLIS_ATTN:-auto} stamp backend
  stamp=$VENV/.trellis-attn-$WHEEL_KEY
  mkdir -p "$WHEELS_DIR"
  case "$mode" in auto|flash_attn|xformers) ;; *) fail "TRELLIS_ATTN=$mode (auto, flash_attn or xformers)"; return 1 ;; esac
  if [ -f "$stamp" ]; then
    backend=$(cat "$stamp")
    if { [ "$mode" = auto ] || [ "$mode" = "$backend" ]; } && attn_check "$backend"; then
      ATTN_BACKEND=$backend
      printf '%s\tok\tstamped\n' "$backend" >> "$STATE_DIR/attn.tsv"
      return 0
    fi
    rm -f "$stamp"
  fi
  if [ "$mode" != xformers ]; then
    if try_flash_attn; then ATTN_BACKEND=flash_attn; printf 'flash_attn\tok\t-\n' >> "$STATE_DIR/attn.tsv"
    else printf 'flash_attn\tfailed\t-\n' >> "$STATE_DIR/attn.tsv"; fi
  fi
  if [ -z "$ATTN_BACKEND" ] && [ "$mode" != flash_attn ]; then
    if try_xformers; then ATTN_BACKEND=xformers; printf 'xformers\tok\t-\n' >> "$STATE_DIR/attn.tsv"
    else printf 'xformers\tfailed\t-\n' >> "$STATE_DIR/attn.tsv"; fi
  fi
  if [ -z "$ATTN_BACKEND" ]; then
    fail "no attention backend works on this GPU (TRELLIS_ATTN=$mode; flash-attn $FLASH_ATTN_VERSION, xformers $XFORMERS_VERSION; TRELLIS.2's sparse attention has no sdpa path)"
    return 1
  fi
  echo "$ATTN_BACKEND" > "$stamp"
  log "attention backend: $ATTN_BACKEND"
}

# trellis_env.json: what wenart.assets.generate sets before importing trellis2.
write_env() {
  python3 - "$VENV/trellis_env.json" "$ATTN_BACKEND" "$FLEX_CACHE" "$TRELLIS_SRC" "$TRELLIS_COMMIT" "$ARCH_LIST" \
    "$WHEEL_KEY" <<'PY'
import json
import sys

path, attn, flex, src, commit, arch, key = sys.argv[1:8]
env = {"ATTN_BACKEND": attn or None, "FLEX_GEMM_AUTOTUNE_CACHE_PATH": flex, "trellis_src": src,
       "trellis_commit": commit, "arch_list": arch, "wheel_key": key}
with open(path, "w", encoding="utf-8") as fh:
    json.dump(env, fh, indent=1)
PY
}

# --- part models --------------------------------------------------------------------------
part_models() {
  "$VENV/bin/python" - "$GEN_YAML" "$STATE_DIR/models.json" <<'PY'
import json
import os
import sys
import time
from pathlib import Path

import yaml
from huggingface_hub import snapshot_download

cfg = yaml.safe_load(Path(sys.argv[1]).read_text(encoding="utf-8"))
out_path = Path(sys.argv[2])
token_set = bool(os.environ.get("HF_TOKEN"))
order = sorted(cfg["models"], key=lambda k: (not cfg["models"][k].get("gated"), k))   # gated first: fail fast
records, failed = [], None
for key in order:
    m = cfg["models"][key]
    rec = {"key": key, "repo": m["repo"], "revision": m["revision"], "licence": m.get("licence"),
           "gated": m.get("gated"), "expected_gb": m.get("size_gb"), "path": None, "n_files": 0, "bytes": 0,
           "seconds": None, "ok": False, "error": None}
    t0 = time.time()
    try:
        snap = Path(snapshot_download(m["repo"], revision=m["revision"], allow_patterns=m.get("allow_patterns")))
        files = [f for f in snap.rglob("*") if f.is_file()]
        rec.update(path=str(snap), n_files=len(files), bytes=sum(f.stat().st_size for f in files))
        missing = [f for f in (m.get("files") or []) if not (snap / f).is_file()]
        if missing or not files:
            raise FileNotFoundError(f"missing in the snapshot: {missing or 'every file'}")
        rec["ok"] = True
    except Exception as exc:  # noqa: BLE001 - recorded with the reason
        text = f"{type(exc).__name__}: {exc}".splitlines()[0][:400]
        low = text.lower()
        if any(s in low for s in ("gated", "401", "403", "restricted", "unauthorized", "forbidden")):
            text = (f"{m['repo']} is gated ({m.get('gated') or 'access needed'}): the Hugging Face account of the "
                    f"RunPod secret hf_token must be granted access on https://huggingface.co/{m['repo']} "
                    f"(HF_TOKEN set: {'yes' if token_set else 'no'}); {text}")
        rec["error"] = text
        failed = failed or text
    rec["seconds"] = round(time.time() - t0, 1)
    print(f"download {key} {m['repo']}@{m['revision'][:12]}: {'ok' if rec['ok'] else 'FAILED ' + str(rec['error'])}, "
          f"{rec['bytes'] / 1e9:.2f} GB (listed {m.get('size_gb')}) in {rec['seconds']} s", flush=True)
    records.append(rec)
    if failed:
        break                                          # nothing else is downloaded for a pod that can not generate
out_path.write_text(json.dumps({"models": records, "error": failed}, indent=1), encoding="utf-8")
sys.exit(1 if failed else 0)
PY
  local rc=$?
  if [ "$rc" -ne 0 ]; then
    fail "$("$VENV/bin/python" -c 'import json,sys; print(json.load(open(sys.argv[1]))["error"])' "$STATE_DIR/models.json" 2>/dev/null || echo "model download failed")"
    return 1
  fi
}

# --- part check ---------------------------------------------------------------------------
TRELLIS_CHECK=$(cat <<'PY'
import json
import os
import sys

out = {"python": sys.version.split()[0]}
import torch

if not torch.cuda.is_available():
    sys.exit("torch.cuda.is_available() is False")
cap = torch.cuda.get_device_capability(0)
arch = torch.cuda.get_arch_list()
out.update(torch=torch.__version__, cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0), capability=list(cap),
           torch_arch_list=arch)
if cap[0] >= 12 and "sm_120" not in arch:
    sys.exit(f"Blackwell GPU (capability {cap}) but this torch has no sm_120 kernels: {arch}")
import nvdiffrast
import nvdiffrast.torch as dr

ctx = dr.RasterizeCudaContext()
pos = torch.tensor([[[-0.8, -0.8, 0.0, 1.0], [0.8, -0.8, 0.0, 1.0], [0.0, 0.8, 0.0, 1.0]]], device="cuda")
tri = torch.tensor([[0, 1, 2]], device="cuda", dtype=torch.int32)
rast, _ = dr.rasterize(ctx, pos, tri, resolution=[64, 64])
covered = int((rast[..., 3] > 0).sum())
if covered < 500:
    sys.exit(f"nvdiffrast covered {covered} pixels of 4096 for a large triangle")
import cumesh

verts = torch.tensor([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], device="cuda", dtype=torch.float32)
faces = torch.tensor([[0, 2, 1], [0, 1, 3], [0, 3, 2], [1, 2, 3]], device="cuda", dtype=torch.int32)
mesh = cumesh.CuMesh()
mesh.init(verts, faces)
if int(mesh.num_faces) != 4:
    sys.exit(f"CuMesh: {mesh.num_faces} faces after init, expected 4")
import flex_gemm
import o_voxel
import o_voxel.postprocess
import diffusers
import transformers
from diffusers import ZImagePipeline  # noqa: F401
import trellis2
from trellis2.modules.attention import config as attn_config
from trellis2.modules.sparse import config as sparse_config
from trellis2.pipelines import Trellis2ImageTo3DPipeline  # noqa: F401

want = os.environ.get("ATTN_BACKEND")
if attn_config.BACKEND != want or sparse_config.ATTN != want:
    sys.exit(f"TRELLIS.2 uses attention {attn_config.BACKEND} / sparse {sparse_config.ATTN}, setup chose {want}")
out.update(attn_backend=attn_config.BACKEND, sparse_conv=sparse_config.CONV, diffusers=diffusers.__version__,
           transformers=transformers.__version__, trellis2=os.path.dirname(trellis2.__file__),
           nvdiffrast=getattr(nvdiffrast, "__version__", None))
from wenart.assets import generate as G
from wenart.hfcache import local_snapshot

cfg = G.load_config()
m = cfg["models"]["trellis"]
snap = local_snapshot(m["repo"], m["revision"], m.get("allow_patterns"))
doc = json.loads((snap / "pipeline.json").read_text(encoding="utf-8"))
G.pipeline_args(doc, cfg, "dinov3", "rembg")
out["pipeline_json"] = "names as checked"
print("TRELLIS_CHECK " + json.dumps(out))
PY
)

part_check() {
  if ! (cd "$REPO_DIR" && ATTN_BACKEND="$ATTN_BACKEND" FLEX_GEMM_AUTOTUNE_CACHE_PATH="$FLEX_CACHE" HF_HUB_OFFLINE=1 \
          "$VENV/bin/python" -c "$TRELLIS_CHECK") \
       > "$STATE_DIR/check.txt" 2>&1; then
    tail -n 30 "$STATE_DIR/check.txt"
    fail "venv-trellis check failed: $(grep -v '^\[' "$STATE_DIR/check.txt" | tail -1)"; return 1
  fi
  grep '^TRELLIS_CHECK ' "$STATE_DIR/check.txt" | tail -1
}

# setup_trellis.json: status, reason, parts, versions, commits, backend, wheel cache, models, seconds.
write_summary() {
  local out_dir=${WENART_RESULTS:-$LOGS} status=$1 disk_after
  mkdir -p "$out_dir"
  disk_after=$(df -B1 --output=avail "$FAST" 2>/dev/null | tail -1 | tr -d ' ' || echo "")
  local parts_arg=() p
  for p in preflight venv src ext attn models check; do parts_arg+=("$p=${PART_STATE[$p]}:${PART_SECONDS[$p]}"); done
  python3 - "$out_dir/setup_trellis.json" "$STATE_DIR" "$status" "$FAIL_REASON" "$ATTN_BACKEND" "$ARCH_LIST" \
    "$WHEEL_KEY" "$WHEELS_DIR" "$PYV" "$TORCH_VER" "$TORCH_CUDA" "$TORCH_ABI" "$(( $(date +%s) - T_START ))" \
    "${DISK_BEFORE:-}" "${disk_after:-}" "$TRELLIS_REPO $TRELLIS_COMMIT" \
    "nvdiffrast=$NVDIFFRAST_REPO@$NVDIFFRAST_COMMIT" "nvdiffrec=$NVDIFFREC_REPO@$NVDIFFREC_COMMIT" \
    "cumesh=$CUMESH_REPO@$CUMESH_COMMIT" "flex_gemm=$FLEXGEMM_REPO@$FLEXGEMM_COMMIT" \
    "o_voxel=$TRELLIS_REPO@$TRELLIS_COMMIT" -- "${parts_arg[@]}" <<'PY' || true
import json
import os
import sys
import time
from pathlib import Path

a = sys.argv[1:]
out, state = Path(a[0]), Path(a[1])
status, reason, attn, arch, key, wheels, pyv, torch_v, torch_cuda, abi, secs, d0, d1, trellis = a[2:16]
sep = a.index("--")
ext_src = dict(item.split("=", 1) for item in a[16:sep])
parts = {}
for item in a[sep + 1:]:
    name, _, rest = item.partition("=")
    st, _, s = rest.rpartition(":")
    parts[name] = {"state": st, "seconds": int(s or 0)}


def gib(v):
    return round(int(v) / 2 ** 30, 1) if v.strip().isdigit() else None


pre = {}
if (state / "preflight.env").is_file():
    for line in (state / "preflight.env").read_text().splitlines():
        k, _, v = line.partition("=")
        pre[k] = v
extensions = {}
for name, src in ext_src.items():
    repo, _, commit = src.rpartition("@")
    extensions[name] = {"repo": repo, "commit": commit, "state": "not run", "cache": None, "seconds": None,
                        "wheel": None}
if (state / "ext.tsv").is_file():
    for line in (state / "ext.tsv").read_text().splitlines():
        f = line.split("\t")
        if len(f) >= 5 and f[0] in extensions:
            extensions[f[0]].update(state=f[1], cache=f[2], seconds=int(f[3]) if f[3].isdigit() else None,
                                    wheel=None if f[4] == "-" else f[4])
hits = sum(1 for e in extensions.values() if e["cache"] in ("cache_hit", "installed"))
built = sum(1 for e in extensions.values() if e["cache"] == "built")
tried = []
if (state / "attn.tsv").is_file():
    tried = [dict(zip(("backend", "state", "note"), line.split("\t"))) for line in
             (state / "attn.tsv").read_text().splitlines() if line.strip()]
models = json.loads((state / "models.json").read_text())["models"] if (state / "models.json").is_file() else []
versions = None
if (state / "check.txt").is_file():
    for line in (state / "check.txt").read_text(errors="replace").splitlines():
        if line.startswith("TRELLIS_CHECK "):
            versions = json.loads(line[len("TRELLIS_CHECK "):])
repo, _, commit = trellis.partition(" ")
data = {
    "schema_version": "0.1", "kind": "setup_trellis", "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "status": status, "reason": reason or None, "seconds": int(secs), "parts": parts,
    "trellis": {"repo": repo, "commit": commit}, "extensions": extensions,
    "attn_backend": attn or None, "attn_tried": tried,
    "wheel_cache": {"dir": wheels, "key": key, "hits": hits, "built": built,
                    "cache_hit": bool(hits) and not built},
    "arch_list": arch, "gpu": pre.get("gpu"), "driver": pre.get("driver"), "compute_cap": pre.get("compute_cap"),
    "vram_mib": int(pre["vram_mib"]) if pre.get("vram_mib", "").isdigit() else None, "nvcc": pre.get("nvcc"),
    "python": pyv, "torch": torch_v, "torch_cuda": torch_cuda, "cxx11abi": abi,
    "hf_token_set": pre.get("hf_token_set") == "yes", "hf_home": os.environ.get("HF_HOME"),
    "venv": os.environ.get("TRELLIS_VENV"), "versions": versions, "models": models,
    "models_gb": round(sum(m.get("bytes") or 0 for m in models) / 1e9, 2),
    "disk_free_gib_before": gib(d0), "disk_free_gib_after": gib(d1), "image": os.environ.get("WENART_IMAGE"),
}
out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"setup_trellis.json -> {out} (status {status})")
PY
  cp -f "$out_dir/setup_trellis.json" "$LOGS/setup_trellis.json" 2>/dev/null || true
}

log "parts: ${PARTS[*]}; HF_HOME=$HF_HOME; venv $VENV; wheel key $WHEEL_KEY"
if has_part preflight; then run_part preflight part_preflight; else PART_STATE[preflight]=ok; fi
if has_part venv; then run_part venv part_venv preflight; elif [ -x "$VENV/bin/python" ]; then PART_STATE[venv]=ok; fi
if has_part src; then run_part src part_src venv; elif [ -f "$TRELLIS_SRC/.wenart-commit" ]; then PART_STATE[src]=ok; fi
if has_part ext; then run_part ext part_ext src; fi
if has_part attn; then run_part attn part_attn venv; fi
if [ -n "$ATTN_BACKEND" ]; then write_env; fi
if has_part models; then run_part models part_models venv; fi
if has_part check; then run_part check part_check ext attn models; fi

STATUS=ok
for part in "${PARTS[@]}"; do
  if [ "${PART_STATE[$part]}" != "ok" ]; then
    STATUS=failed
    if [ -z "$FAIL_REASON" ]; then FAIL_REASON="part $part: ${PART_STATE[$part]}"; fi
  fi
done
write_summary "$STATUS"
if [ "$STATUS" != "ok" ]; then
  log "setup FAILED: $FAIL_REASON"
  exit 1
fi
log "setup done in $(( $(date +%s) - T_START )) s (attention $ATTN_BACKEND, wheel key $WHEEL_KEY)"
