#!/usr/bin/env bash
# Recognition bake-off setup on a RunPod pod (Milestone 2, section 3). Idempotent:
# everything persistent lands under /workspace (the Network Volume); finished steps
# are skipped on the next pod. Every step is timed and printed.
#
# Installs (the two venvs and the model cache live on the CONTAINER DISK, /opt/wenart:
# the network volume writes small files at a few MB/s, a pip install of vLLM took > 55 min
# there on 1 Oct 2026 and never finished; on the container disk it takes minutes. They are
# rebuilt per pod; the runner gives the bake-off pod an 80 GB container disk):
#   /opt/wenart/venv-vllm    vllm==0.30.0 (brings torch 2.13.0; own venv, no system site packages
#                            because the image ships torch 2.9.1) + the `hf` download CLI
#   /opt/wenart/venv-paddle  paddlepaddle-gpu 3.x (PaddlePaddle wheel index, cu126 -> cu129 -> CPU
#                            fallback, the winner is logged) + paddleocr==3.7.0 + the repo's CPU deps.
#                            The venv is stamped as good only after a real kernel launch on gpu:0
#                            (a matmul): pip accepts any wheel, the GPU does not.
#   /opt/wenart/hf           the two VLM checkpoints (HF cache; download speed logged in MB/s)
#   apt                      tesseract-ocr tesseract-ocr-tur + build tools for LibreDWG
#   /workspace/tools/libredwg  GNU LibreDWG 0.14.1 built from the GNU tarball, 0.13.3 when the
#                            0.14.1 download fails (./configure --disable-bindings --disable-python
#                            --prefix=...); rebuilt when the installed VERSION differs
#
# Sources checked on 1 Oct 2026:
#   vLLM 0.30.0 requirements/cuda.txt: torch==2.13.0; PyPI vllm 0.30.0: python >=3.10,<3.15.
#   PaddleOCR v3.7.0 docs/version3.x/paddlepaddle_installation.en.md: pip install
#     paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
#     (PaddleOCR 3.7.x needs PaddlePaddle >= 3.0.0 per paddleocr_and_paddlex.en.md).
#   LibreDWG 0.13.3 README: ./configure [--disable-bindings] [--disable-python] ...; NEWS: 0.13.3 of 2023-02-26.
#   LibreDWG 0.14.1 tarball URL from docs/milestone3.md (ftp.gnu.org is not reachable from the
#     cloud session's proxy, so the URL is verified on the pod: a failed download falls back to 0.13.3).
#   huggingface_hub >= 1.0 (vllm needs >= 1.31): hf_transfer is no longer used; the fast path is
#     hf_xet with HF_XET_HIGH_PERFORMANCE=1. HF_HUB_ENABLE_HF_TRANSFER=1 is still exported for
#     older hubs and only warns when HF_XET_HIGH_PERFORMANCE is unset.
set -Eeuo pipefail
trap 'echo "[setup-recognition] ERROR at line $LINENO" >&2' ERR

WS=/workspace
LOGS=$WS/logs
TOOLS=$WS/tools
FAST=/opt/wenart                       # container disk: fast, wiped with the pod
mkdir -p "$LOGS" "$TOOLS" "$FAST"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
mkdir -p "$HF_HOME"
# Leftovers of the earlier layout on the volume (half-built venvs) only waste space.
rm -rf /workspace/venv-vllm /workspace/venv-paddle
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_XET_HIGH_PERFORMANCE=1
export PIP_DISABLE_PIP_VERSION_CHECK=1
# Wheels are few large files, so the pip cache can live on the volume and survive pods
# (the venvs themselves cannot: tens of thousands of small files are far too slow there).
export PIP_CACHE_DIR=/workspace/pip-cache
mkdir -p "$PIP_CACHE_DIR"

VLLM_VERSION=0.30.0
PADDLEOCR_VERSION=3.7.0
PADDLE_VERSION=3.2.0
# LibreDWG: 0.14.1 first (docs/milestone3.md section 5); when neither the GNU mirror nor the
# GitHub release serves that tarball, 0.13.3 (the Milestone 2 build) is used and logged.
# The version that was built ends up in $TOOLS/libredwg/VERSION and, through
# `dwg2dxf --version`, in results/bakeoff/dwg_roundtrip.json.
LIBREDWG_VERSION=0.14.1
LIBREDWG_FALLBACK_VERSION=0.13.3
libredwg_url() { echo "https://ftp.gnu.org/gnu/libredwg/libredwg-$1.tar.xz"; }
libredwg_url_fallback() { echo "https://github.com/LibreDWG/libredwg/releases/download/$1/libredwg-$1.tar.xz"; }
# Space-separated list, overridable from the job (BAKEOFF_MODELS="a/b c/d").
read -r -a MODELS <<< "${BAKEOFF_MODELS:-Qwen/Qwen3-VL-8B-Instruct zai-org/GLM-4.6V-Flash}"

log() { echo "[$(date -u +%H:%M:%S)] setup-recognition: $*"; }
step_start() { STEP_NAME="$1"; STEP_T0=$(date +%s); log "start: $STEP_NAME"; }
step_end() { log "done: $STEP_NAME in $(( $(date +%s) - STEP_T0 )) s"; }

# --- OS packages (container disk: redone per pod, fast) ------------------------
step_start "apt packages (tesseract tur, build tools)"
STAMP_APT=/var/lib/wenart-apt-recognition-done
if [ ! -f $STAMP_APT ]; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends tesseract-ocr tesseract-ocr-tur \
    build-essential autoconf automake libtool pkg-config xz-utils curl ca-certificates \
    libgl1 libglib2.0-0 poppler-utils >/dev/null
  touch $STAMP_APT
fi
log "tesseract: $(tesseract --version 2>&1 | head -1); langs: $(tesseract --list-langs 2>&1 | tail -n +2 | tr '\n' ' ')"
step_end

# --- venv-vllm -------------------------------------------------------------------
step_start "venv-vllm (vllm==$VLLM_VERSION)"
VENV_VLLM=$FAST/venv-vllm
if [ ! -f "$VENV_VLLM/.vllm-$VLLM_VERSION" ]; then
  [ -x "$VENV_VLLM/bin/python" ] || python3 -m venv "$VENV_VLLM"
  "$VENV_VLLM/bin/pip" install -q --upgrade pip
  # The PyPI vllm wheel pulls torch built for CUDA 13.0, which needs an R580+ host driver.
  # Hosts with an older driver (CUDA 12.8/12.9, e.g. driver 570) get the cu128 torch index
  # instead (vLLM docs, "Install vLLM with CUDA 12.x": --extra-index-url download.pytorch.org/whl/cuXXX).
  HOST_CUDA=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader 2>/dev/null | head -1 | cut -d. -f1)
  TORCH_INDEX=""
  if [ -n "$HOST_CUDA" ] && [ "$HOST_CUDA" -lt 580 ]; then
    TORCH_INDEX="--extra-index-url https://download.pytorch.org/whl/cu128"
    log "host driver $HOST_CUDA < 580: installing the CUDA 12.8 torch variant"
  fi
  # shellcheck disable=SC2086
  "$VENV_VLLM/bin/pip" install -q "vllm==$VLLM_VERSION" hf_transfer $TORCH_INDEX 2>&1 | tail -n 5 || true
  "$VENV_VLLM/bin/python" -c "import vllm, torch; print('vllm', vllm.__version__, 'torch', torch.__version__)"
  rm -f "$VENV_VLLM"/.vllm-*; touch "$VENV_VLLM/.vllm-$VLLM_VERSION"
fi
log "$("$VENV_VLLM/bin/python" -c "import vllm, torch, huggingface_hub; print('vllm', vllm.__version__, 'torch', torch.__version__, 'huggingface_hub', huggingface_hub.__version__)")"
step_end

# --- venv-paddle -----------------------------------------------------------------
step_start "venv-paddle (paddlepaddle-gpu $PADDLE_VERSION, paddleocr==$PADDLEOCR_VERSION)"
VENV_PADDLE=$FAST/venv-paddle
PADDLE_LOG=$LOGS/paddle-install.txt
if [ ! -f "$VENV_PADDLE/.paddleocr-$PADDLEOCR_VERSION" ]; then
  [ -x "$VENV_PADDLE/bin/python" ] || python3 -m venv "$VENV_PADDLE"
  PIP="$VENV_PADDLE/bin/pip"
  "$PIP" install -q --upgrade pip
  PADDLE_SOURCE=""
  # Fallback chain for the framework wheel; the first index that installs wins.
  # Blackwell GPUs (compute capability 12.x) need the CUDA 12.9 build: the cu126 wheel
  # installs fine but fails at run time with "Unsupported GPU architecture" (seen on an
  # RTX PRO 4000 on 1 Oct 2026), so they try cu129 with the newest Paddle first.
  CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1 | cut -d. -f1)
  if [ -n "$CC" ] && [ "$CC" -ge 12 ]; then
    CANDIDATES="3.3.1:cu129 $PADDLE_VERSION:cu129 $PADDLE_VERSION:cu126"
  else
    CANDIDATES="$PADDLE_VERSION:cu126 $PADDLE_VERSION:cu129"
  fi
  for cand in $CANDIDATES; do
    ver=${cand%%:*}; idx=${cand##*:}
    if "$PIP" install -q "paddlepaddle-gpu==$ver" -i "https://www.paddlepaddle.org.cn/packages/stable/$idx/" 2>>"$PADDLE_LOG"; then
      PADDLE_SOURCE="paddlepaddle-gpu==$ver from $idx index (compute capability ${CC:-?})"; break
    fi
    log "paddlepaddle-gpu $ver from $idx index failed (see $PADDLE_LOG)"
  done
  if [ -z "$PADDLE_SOURCE" ]; then
    if "$PIP" install -q "paddlepaddle-gpu==$PADDLE_VERSION" 2>>"$PADDLE_LOG"; then
      PADDLE_SOURCE="paddlepaddle-gpu==$PADDLE_VERSION from PyPI"
    elif "$PIP" install -q "paddlepaddle>=3.0.0" 2>>"$PADDLE_LOG"; then
      PADDLE_SOURCE="paddlepaddle (CPU) from PyPI - no GPU wheel could be installed"
    else
      log "no PaddlePaddle wheel could be installed; PaddleOCR will fail (Tesseract still runs)"
      PADDLE_SOURCE="none"
    fi
  fi
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $PADDLE_SOURCE" >> "$PADDLE_LOG"
  log "PaddlePaddle: $PADDLE_SOURCE"
  "$PIP" install -q "paddleocr==$PADDLEOCR_VERSION" 2>&1 | tail -n 3 || true
  "$PIP" install -q -r "$REPO_DIR/scripts/pod_requirements.txt" 2>&1 | tail -n 3 || true
  # The stamp is written only when the check below passes, so a broken install is
  # retried on the next pod instead of being skipped. With a GPU present the check
  # is a real kernel launch (matmul on gpu:0): a wheel built without kernels for
  # this GPU imports fine and only fails here ("no kernel image is available",
  # "Unsupported GPU architecture"). On failure nothing is stamped, the failure is
  # logged, and the OCR stage falls back to PaddleOCR on the CPU (wenart/recognition/ocr.py).
  PADDLE_CHECK=$(cat <<'PY'
import sys
import ezdxf  # noqa: F401 - the venv must be complete (repo CPU deps)
import pytest  # noqa: F401
import paddle
import paddleocr
expect = sys.argv[1] if len(sys.argv) > 1 else "cpu"
print("paddleocr", paddleocr.__version__, "paddle", paddle.__version__,
      "cuda", paddle.is_compiled_with_cuda(), "gpus", paddle.device.cuda.device_count())
if expect == "gpu":
    if not paddle.is_compiled_with_cuda() or paddle.device.cuda.device_count() < 1:
        sys.exit("paddle sees no GPU although nvidia-smi reports one")
    paddle.set_device("gpu:0")
    x = paddle.ones([64, 64], dtype="float32")
    y = (x @ x).numpy()                      # the kernel launch that a wrong wheel cannot do
    if float(y[0, 0]) != 64.0:
        sys.exit(f"paddle gpu matmul returned {y[0, 0]!r}, expected 64.0")
    print("paddle gpu:0 matmul ok")
else:
    print("paddle: no GPU reported by nvidia-smi, import check only (CPU)")
PY
)
  EXPECT=cpu
  if [ -n "$CC" ]; then EXPECT=gpu; fi   # nvidia-smi reported a GPU: the kernel launch must work
  if "$VENV_PADDLE/bin/python" -c "$PADDLE_CHECK" "$EXPECT" 2>&1 | tee -a "$PADDLE_LOG"; then   # pipefail: python decides
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) check ok ($EXPECT): venv-paddle stamped" >> "$PADDLE_LOG"
    rm -f "$VENV_PADDLE"/.paddleocr-*; touch "$VENV_PADDLE/.paddleocr-$PADDLEOCR_VERSION"
  else
    echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) check FAILED ($EXPECT): venv-paddle not stamped" >> "$PADDLE_LOG"
    log "venv-paddle check failed ($EXPECT), not stamped: PaddleOCR runs on the CPU fallback or records the error; Tesseract still runs"
  fi
fi
"$VENV_PADDLE/bin/python" - <<'PY' || log "paddle check failed (see above)"
import paddleocr
print("paddleocr", paddleocr.__version__)
try:
    import paddle
    print("paddle", paddle.__version__, "cuda", paddle.is_compiled_with_cuda(), "gpus", paddle.device.cuda.device_count())
except Exception as exc:  # noqa: BLE001
    print("paddle import failed:", exc)
PY
step_end

# --- LibreDWG from the GNU tarball ----------------------------------------------
step_start "LibreDWG $LIBREDWG_VERSION (fallback $LIBREDWG_FALLBACK_VERSION)"
LIBREDWG_PREFIX=$TOOLS/libredwg
SRC=$FAST/src                         # build on the container disk, install into the volume
mkdir -p "$SRC"

# fetch_libredwg <version> <tarball>: GNU mirror first, then the GitHub release. `-f` makes a
# 404 a failure instead of an HTML "tarball"; a partial file is removed so the next try is clean.
fetch_libredwg() {
  local ver=$1 tar=$2
  [ -s "$tar" ] && return 0
  if curl -fsSL --retry 3 -o "$tar" "$(libredwg_url "$ver")"; then return 0; fi
  log "LibreDWG $ver: GNU mirror failed, trying the GitHub release"
  if curl -fsSL --retry 3 -o "$tar" "$(libredwg_url_fallback "$ver")"; then return 0; fi
  rm -f "$tar"
  return 1
}
# The version that is installed on the volume (empty when none): first x.y.z in the VERSION file.
libredwg_installed() {
  { grep -oE '[0-9]+\.[0-9]+\.[0-9]+' "$LIBREDWG_PREFIX/VERSION" 2>/dev/null || true; } | head -1
}
libredwg_usable() {
  [ -x "$LIBREDWG_PREFIX/bin/dwg2dxf" ] && [ -x "$LIBREDWG_PREFIX/bin/dxf2dwg" ]
}

# Decide which version this pod builds: the wanted one when its tarball can be fetched (or is
# already installed), otherwise the fallback. The decision is logged either way.
LIBREDWG_BUILD=""
if libredwg_usable && [ "$(libredwg_installed)" = "$LIBREDWG_VERSION" ]; then
  LIBREDWG_BUILD=$LIBREDWG_VERSION
elif fetch_libredwg "$LIBREDWG_VERSION" "$SRC/libredwg-$LIBREDWG_VERSION.tar.xz"; then
  LIBREDWG_BUILD=$LIBREDWG_VERSION
else
  log "LibreDWG $LIBREDWG_VERSION tarball not available; falling back to $LIBREDWG_FALLBACK_VERSION"
  if libredwg_usable && [ "$(libredwg_installed)" = "$LIBREDWG_FALLBACK_VERSION" ]; then
    LIBREDWG_BUILD=$LIBREDWG_FALLBACK_VERSION
  elif fetch_libredwg "$LIBREDWG_FALLBACK_VERSION" "$SRC/libredwg-$LIBREDWG_FALLBACK_VERSION.tar.xz"; then
    LIBREDWG_BUILD=$LIBREDWG_FALLBACK_VERSION
  else
    log "LibreDWG: no tarball could be downloaded ($LIBREDWG_VERSION, $LIBREDWG_FALLBACK_VERSION); the DWG round trip will report the missing tools"
  fi
fi

if [ -n "$LIBREDWG_BUILD" ] && { ! libredwg_usable || [ "$(libredwg_installed)" != "$LIBREDWG_BUILD" ]; }; then
  TAR=$SRC/libredwg-$LIBREDWG_BUILD.tar.xz
  rm -rf "$SRC/libredwg-$LIBREDWG_BUILD"
  tar -xJf "$TAR" -C "$SRC"
  rm -rf "$LIBREDWG_PREFIX"            # an older build must not survive next to the new one
  (
    cd "$SRC/libredwg-$LIBREDWG_BUILD"
    ./configure --disable-bindings --disable-python --prefix="$LIBREDWG_PREFIX" > "$LOGS/libredwg-configure.log" 2>&1
    make -j"$(nproc)" > "$LOGS/libredwg-make.log" 2>&1
    make install > "$LOGS/libredwg-install.log" 2>&1
  )
  "$LIBREDWG_PREFIX/bin/dwg2dxf" --version > "$LIBREDWG_PREFIX/VERSION" 2>&1 || true
  # Some releases print only the program name; make sure the file names the version.
  grep -qE '[0-9]+\.[0-9]+\.[0-9]+' "$LIBREDWG_PREFIX/VERSION" 2>/dev/null || echo "libredwg $LIBREDWG_BUILD" >> "$LIBREDWG_PREFIX/VERSION"
fi
log "LibreDWG: $(head -1 "$LIBREDWG_PREFIX/VERSION" 2>/dev/null || echo "not installed") (wanted $LIBREDWG_VERSION, built $LIBREDWG_BUILD)"
step_end

# --- Model checkpoints (hf CLI, cached in HF_HOME on the container disk) ----------
for model in "${MODELS[@]}"; do
  step_start "download $model"
  T0=$(date +%s)
  # `hf download` prints the snapshot path last; depending on the version the line is
  # "<path>" or "  path: <path>", so strip that prefix before measuring the folder.
  SNAP_DIR=$("$VENV_VLLM/bin/hf" download "$model" 2> "$LOGS/hf-download-$(echo "$model" | tr '/' '_').log" \
             | tail -1 | sed -E 's/^[[:space:]]*path:[[:space:]]*//')
  T1=$(date +%s)
  BYTES=$(du -sbL "$SNAP_DIR" 2>/dev/null | cut -f1 || echo 0)   # -L: snapshot files are symlinks into blobs/
  SECS=$(( T1 - T0 ))
  if [ "$SECS" -gt 5 ]; then
    log "$model: $(( BYTES / 1048576 )) MB in $SECS s = $(( BYTES / 1048576 / SECS )) MB/s -> $SNAP_DIR"
  else
    log "$model: $(( BYTES / 1048576 )) MB already cached -> $SNAP_DIR"
  fi
  step_end
done

log "setup done"
