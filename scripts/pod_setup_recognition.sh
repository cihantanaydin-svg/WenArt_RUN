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
#   apt                      tesseract-ocr tesseract-ocr-tur + build tools for LibreDWG (cmake, ninja)
#   /workspace/tools/libredwg/bin  LibreDWG 0.14 (git tag 0.14 = commit d9468ae; there is no 0.14.1),
#                            built from git on the container disk (/opt/wenart/build/libredwg) as static
#                            binaries dwg2dxf, dwgread, dxf2dwg + VERSION "0.14 d9468ae"
#                            (docs/milestone7.md §5.1); reused when VERSION matches and `dwg2dxf --help` runs.
#                            GPL-3.0: called as separate programs, never shipped with the repository.
#
# Parts (Milestone 5): RECOG_SETUP_PARTS, space separated, default all of
# "vllm paddle libredwg models". The M5 check phase (scripts/pod_setup_polish.sh) runs only
# "vllm models": PaddleOCR and LibreDWG are skipped. The apt step always runs (stamped per pod).
# BAKEOFF_MODELS entries may carry a pinned revision as "<repo id>@<revision>" (M5 passes the
# revisions of wenart/vision_check/check.yaml); without one the main branch is downloaded.
#
# Sources checked on 1 Oct 2026:
#   vLLM 0.30.0 requirements/cuda.txt: torch==2.13.0; PyPI vllm 0.30.0: python >=3.10,<3.15.
#   PaddleOCR v3.7.0 docs/version3.x/paddlepaddle_installation.en.md: pip install
#     paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/
#     (PaddleOCR 3.7.x needs PaddlePaddle >= 3.0.0 per paddleocr_and_paddlex.en.md).
#   LibreDWG tags via `git ls-remote https://github.com/LibreDWG/libredwg.git` (3 Oct 2026): 0.14 =
#     d9468ae948b8f07a08efa756c19f8916052358c0, no 0.14.1. Static cmake/ninja build measured in the session
#     (2 min 41 s on 4 cores); `dwg2dxf --version` prints no version, hence the VERSION file.
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
# LibreDWG 0.14 from git, pinned by commit (docs/milestone7.md §5.1). The pipeline finds the binaries in
# $LIBREDWG_BIN (wenart/ingest/dwg.py) and puts VERSION into its fingerprint.
LIBREDWG_GIT=https://github.com/LibreDWG/libredwg.git
LIBREDWG_TAG=0.14
LIBREDWG_COMMIT=d9468ae948b8f07a08efa756c19f8916052358c0
LIBREDWG_VERSION_STRING="0.14 d9468ae p1"
LIBREDWG_BIN=$TOOLS/libredwg/bin
LIBREDWG_SRC=$FAST/build/libredwg     # container disk: the build tree is thousands of small files
# Space-separated list, overridable from the job (BAKEOFF_MODELS="a/b c/d", or "a/b@<revision>").
read -r -a MODELS <<< "${BAKEOFF_MODELS:-Qwen/Qwen3-VL-8B-Instruct zai-org/GLM-4.6V-Flash}"
VENV_VLLM=$FAST/venv-vllm             # also the home of the `hf` CLI used by the model downloads

log() { echo "[$(date -u +%H:%M:%S)] setup-recognition: $*"; }
step_start() { STEP_NAME="$1"; STEP_T0=$(date +%s); log "start: $STEP_NAME"; }
step_end() { log "done: $STEP_NAME in $(( $(date +%s) - STEP_T0 )) s"; }

# Parts of this setup (see the header). An unknown part is a typo in the job: stop at once.
RECOG_PARTS_ALL="vllm paddle libredwg models"
read -r -a PARTS <<< "${RECOG_SETUP_PARTS:-$RECOG_PARTS_ALL}"
for part in "${PARTS[@]}"; do
  case " $RECOG_PARTS_ALL " in
    *" $part "*) ;;
    *) log "unknown part '$part' in RECOG_SETUP_PARTS (known: $RECOG_PARTS_ALL)"; exit 2 ;;
  esac
done
part_on() { local p; for p in "${PARTS[@]}"; do [ "$p" = "$1" ] && return 0; done; return 1; }
log "parts: ${PARTS[*]}"

# --- OS packages (container disk: redone per pod, fast) ------------------------
step_start "apt packages (tesseract tur, build tools)"
STAMP_APT=/var/lib/wenart-apt-recognition-done
if [ ! -f $STAMP_APT ]; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends tesseract-ocr tesseract-ocr-tur \
    build-essential cmake ninja-build git pkg-config xz-utils curl ca-certificates \
    libgl1 libglib2.0-0 poppler-utils >/dev/null
  touch $STAMP_APT
fi
log "tesseract: $(tesseract --version 2>&1 | head -1); langs: $(tesseract --list-langs 2>&1 | tail -n +2 | tr '\n' ' ')"
step_end

# --- venv-vllm -------------------------------------------------------------------
if part_on vllm; then
  step_start "venv-vllm (vllm==$VLLM_VERSION)"
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
else
  log "skipped: venv-vllm (RECOG_SETUP_PARTS='${PARTS[*]}')"
fi

# --- venv-paddle -----------------------------------------------------------------
if part_on paddle; then
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
else
  log "skipped: venv-paddle (PaddleOCR) (RECOG_SETUP_PARTS='${PARTS[*]}')"
fi

# --- LibreDWG 0.14 from git (static) ---------------------------------------------
# libredwg_usable: the three binaries are installed, VERSION is this pin and dwg2dxf runs (a binary copied
# from another machine or a half-written install fails the --help call).
libredwg_usable() {
  local tool
  for tool in dwg2dxf dwgread dxf2dwg; do
    [ -x "$LIBREDWG_BIN/$tool" ] || return 1
  done
  [ "$(head -1 "$LIBREDWG_BIN/VERSION" 2>/dev/null)" = "$LIBREDWG_VERSION_STRING" ] || return 1
  "$LIBREDWG_BIN/dwg2dxf" --help >/dev/null 2>&1 || return 1
}

# build_libredwg: clone the tag, check the commit, build the three static programs, install them + VERSION.
# Every step returns on failure (the caller logs it); nothing is installed from an unverified checkout.
# patch_libredwg: one fix on top of the pinned commit (found on real03, 10 Oct 2026). dxf_blocks_write passes its
# BLOCK_HEADER loop index to dxf_block_write, which advances it past the attributes of every INSERT it writes, so
# the blocks after a block with attributed INSERTs were left out of the DXF (real03: the four flats, the stairs,
# the columns). The fix gives dxf_block_write a copy of the index. Only dwg2dxf changes (dxf2dwg does not).
patch_libredwg() {
  git -C "$LIBREDWG_SRC" apply --whitespace=nowarn - <<'LIBREDWG_PATCH'
diff --git a/src/out_dxf.c b/src/out_dxf.c
index 8de1989..ea5e780 100644
--- a/src/out_dxf.c
+++ b/src/out_dxf.c
@@ -3903,7 +3903,12 @@ dxf_blocks_write (Bit_Chain *restrict dat, Dwg_Data *restrict dwg)
           if (dat->version < R_11 && obj == mspace)
             ;
           else
-            error |= dxf_block_write (dat, obj, mspace, pspace, &i);
+            {
+              // dxf_block_write may advance its index past INSERT attribs:
+              // give it a copy so the BLOCK_HEADER scan skips no block.
+              int j = i;
+              error |= dxf_block_write (dat, obj, mspace, pspace, &j);
+            }
         }
     }
 
LIBREDWG_PATCH
}

build_libredwg() {
  rm -rf "$LIBREDWG_SRC"
  mkdir -p "$(dirname "$LIBREDWG_SRC")"
  git clone --quiet --depth 1 --branch "$LIBREDWG_TAG" "$LIBREDWG_GIT" "$LIBREDWG_SRC" \
    > "$LOGS/libredwg-clone.log" 2>&1 || return 1
  local head
  head=$(git -C "$LIBREDWG_SRC" rev-parse HEAD) || return 1
  if [ "$head" != "$LIBREDWG_COMMIT" ]; then
    log "LibreDWG tag $LIBREDWG_TAG is commit $head, expected $LIBREDWG_COMMIT: not built"
    return 1
  fi
  git -C "$LIBREDWG_SRC" submodule update --init --depth 1 jsmn >> "$LOGS/libredwg-clone.log" 2>&1 || return 1
  patch_libredwg >> "$LOGS/libredwg-clone.log" 2>&1 || return 1
  cmake -S "$LIBREDWG_SRC" -B "$LIBREDWG_SRC/build" -G Ninja -DCMAKE_BUILD_TYPE=Release -DDISABLE_WERROR=ON \
    -DENABLE_LTO=OFF -DBUILD_SHARED_LIBS=OFF > "$LOGS/libredwg-cmake.log" 2>&1 || return 1
  ninja -C "$LIBREDWG_SRC/build" dwg2dxf dwgread dxf2dwg > "$LOGS/libredwg-ninja.log" 2>&1 || return 1
  rm -rf "$LIBREDWG_BIN"
  mkdir -p "$LIBREDWG_BIN"
  install -m 0755 "$LIBREDWG_SRC/build/dwg2dxf" "$LIBREDWG_SRC/build/dwgread" "$LIBREDWG_SRC/build/dxf2dwg" \
    "$LIBREDWG_BIN/" || return 1
  echo "$LIBREDWG_VERSION_STRING" > "$LIBREDWG_BIN/VERSION"
  libredwg_usable
}

if part_on libredwg; then
  step_start "LibreDWG $LIBREDWG_TAG ($LIBREDWG_VERSION_STRING, static)"
  if libredwg_usable; then
    log "LibreDWG: reusing $LIBREDWG_BIN ($LIBREDWG_VERSION_STRING)"
  elif build_libredwg; then
    log "LibreDWG: built $LIBREDWG_VERSION_STRING into $LIBREDWG_BIN"
  else
    # DWG projects then stop with needs_review ("LibreDWG dwg2dxf not found"); the other parts go on.
    log "LibreDWG: build FAILED (see $LOGS/libredwg-*.log); DWG projects will end needs_review"
  fi
  step_end
else
  log "skipped: LibreDWG (RECOG_SETUP_PARTS='${PARTS[*]}')"
fi

# --- Model checkpoints (hf CLI, cached in HF_HOME on the container disk) ----------
if part_on models; then
  if [ ! -x "$VENV_VLLM/bin/hf" ]; then
    log "no hf CLI in $VENV_VLLM (part 'vllm' never ran on this pod): cannot download the models"; exit 1
  fi
  for entry in "${MODELS[@]}"; do
    model=${entry%@*}                 # "<repo id>[@<revision>]"
    REV_ARG=()
    if [ "$entry" != "$model" ]; then REV_ARG=(--revision "${entry##*@}"); fi
    step_start "download $entry"
    T0=$(date +%s)
    # `hf download` prints the snapshot path last; depending on the version the line is
    # "<path>" or "  path: <path>", so strip that prefix before measuring the folder.
    SNAP_DIR=$("$VENV_VLLM/bin/hf" download "$model" "${REV_ARG[@]}" \
               2> "$LOGS/hf-download-$(echo "$model" | tr '/' '_').log" \
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
else
  log "skipped: model downloads (RECOG_SETUP_PARTS='${PARTS[*]}')"
fi

log "setup done"
