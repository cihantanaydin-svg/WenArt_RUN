#!/usr/bin/env bash
# Milestone 2 recognition bake-off job. Run by scripts/pod_entry.sh on a RunPod pod
# (cwd /workspace/repo, WENART_RESULTS set; HF_HOME is moved to the container disk). Stages:
#   1. scripts/pod_setup_recognition.sh      (venvs, tesseract, LibreDWG, model downloads)
#   2. DWG round trip  dxf2dwg -> dwg2dxf on the synthetic DXFs   -> results/bakeoff/dwg_roundtrip.json
#   3. OCR (PaddleOCR + Tesseract) on every synthetic scan/photo  -> results/bakeoff/*_ocr.json
#   4. per model: start `vllm serve`, wait for /health, GPU tests (first model only),
#      bake-off VLM stage, stop the server
#   5. two-pass agreement + summary.md / summary.json
#   6. copy the small result files into $WENART_RESULTS
# Resumable: results live under /workspace/repo/results/bakeoff on the volume and
# pages with an existing result JSON are skipped. Every stage is timed. A failing
# stage is recorded and the later stages still run, so one pod run collects as
# much as possible; the exit code is 1 if anything failed.
#
# vLLM listens on port 8001 (not 8000: pod_entry.sh's status server owns 8000).
# `vllm serve` flags (vLLM 0.30.0 docs/cli/README.md and vllm/engine/arg_utils.py):
#   --port, --max-model-len, --limit-mm-per-prompt '{"image":2}', --gpu-memory-utilization,
#   --reasoning-parser glm45 (GLM-4.xV thinking goes to the `reasoning` field, content stays JSON),
#   --max-num-seqs, --quantization fp8 (on-the-fly weight quantisation; Marlin kernels on Ampere).
# Env VLLM_USE_FLASHINFER_SAMPLER (vllm/envs.py v0.30.0): 0 disables the FlashInfer sampler.
set -Eeuo pipefail

WS=/workspace
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-bakeoff}"
LOG=$LOGS/bakeoff-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

OUT=$REPO/results/bakeoff
RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
FAST=/opt/wenart                      # container disk (see pod_setup_recognition.sh)
VENV_VLLM=$FAST/venv-vllm
VENV_PADDLE=$FAST/venv-paddle
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
PY=$VENV_PADDLE/bin/python
VLM_PORT="${VLM_PORT:-8001}"
VLM_SERVER="http://127.0.0.1:$VLM_PORT/v1"
read -r -a MODELS <<< "${BAKEOFF_MODELS:-Qwen/Qwen3-VL-8B-Instruct zai-org/GLM-4.6V-Flash}"
SERVER_WAIT_S="${SERVER_WAIT_S:-1500}"
FAILED=()
VLLM_PID=""

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] bakeoff: $*"; }
slug() { basename "$1"; }

stop_server() {
  if [ -n "$VLLM_PID" ] && kill -0 "$VLLM_PID" 2>/dev/null; then
    log "stopping vllm (pid $VLLM_PID)"
    kill "$VLLM_PID" 2>/dev/null || true
    for _ in $(seq 1 30); do kill -0 "$VLLM_PID" 2>/dev/null || break; sleep 2; done
    kill -9 "$VLLM_PID" 2>/dev/null || true
  fi
  VLLM_PID=""
}

copy_results() {
  # Small files only: JSON, markdown, JPEG previews <= 300 KB, logs of the servers (tails).
  mkdir -p "$RESULTS"
  if [ -d "$OUT" ]; then
    find "$OUT" -maxdepth 1 -type f \( -name '*.json' -o -name '*.md' \) -size -2000k -exec cp -f {} "$RESULTS/" \;
    find "$OUT" -maxdepth 1 -type f -name '*.jpg' -size -301k -exec cp -f {} "$RESULTS/" \;
  fi
  for f in "$LOGS"/vllm-*.log; do [ -f "$f" ] && tail -n 200 "$f" > "$RESULTS/$(basename "$f")"; done
  [ -f "$LOGS/paddle-install.txt" ] && cp -f "$LOGS/paddle-install.txt" "$RESULTS/" || true
  log "results copied to $RESULTS: $(ls "$RESULTS" | wc -l) files"
}

on_error() {
  log "ERROR at line $1"
  stop_server
  copy_results
  exit 1
}
trap 'on_error $LINENO' ERR

# run_stage <name> <command...>: timed, failure recorded, job continues.
run_stage() {
  local name=$1; shift
  local t0; t0=$(date +%s)
  log "stage start: $name"
  # `cmd || rc=$?` is exempt from both errexit and the ERR trap (a plain `set +e` is
  # not enough: the ERR trap still fires on a failing command and would end the job).
  local rc=0
  "$@" || rc=$?
  log "stage end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  if [ "$rc" -ne 0 ]; then FAILED+=("$name"); fi
  return 0
}

gpu_mem_mib() { nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || echo 0; }

# Extra `vllm serve` flags per model. Override with BAKEOFF_ARGS_<SLUG with - and . as _>.
model_args() {
  local model=$1 s; s=$(slug "$model" | tr '.-' '__')
  local override="BAKEOFF_ARGS_$s"
  if [ -n "${!override:-}" ]; then echo "${!override}"; return; fi
  local args="" mem; mem=$(gpu_mem_mib)
  case "$model" in
    *GLM-4*V*) args="--reasoning-parser glm45" ;;
  esac
  # bf16 weights: Qwen3-VL-8B 17.5 GB, GLM-4.6V-Flash 20.6 GB. On a 24 GB card (run 3,
  # 1 Oct 2026) Qwen3-VL in bf16 loaded but left only 1.92 GiB for the KV cache, too
  # little for a 16384 context, so below 40 GB both models get fp8 weights (vLLM online
  # dynamic quantisation, --quantization fp8), an 8192 context and 2 concurrent sequences.
  # The prompts use one image at <= 1600 px plus a short text, well under 8192 tokens.
  if [ "${mem:-0}" -lt 40000 ]; then
    echo "$args --quantization fp8 --max-model-len 8192 --max-num-seqs 2"
  else
    echo "$args --max-model-len 16384 --max-num-seqs 4"
  fi
}

start_server() {
  local model=$1
  local extra; extra=$(model_args "$model")
  local slog="$LOGS/vllm-$(slug "$model").log"
  log "starting vllm serve $model --port $VLM_PORT $extra (log $slog)"
  # VLLM_USE_FLASHINFER_SAMPLER=0: on the RTX PRO 4000 (Blackwell, sm_120) FlashInfer's
  # sampling kernel failed its capability check ("FlashInfer requires GPUs with sm75 or
  # higher", run 3) and killed the GLM server; vLLM's own sampler is used instead.
  # shellcheck disable=SC2086
  VLLM_USE_FLASHINFER_SAMPLER=0 "$VENV_VLLM/bin/vllm" serve "$model" --port "$VLM_PORT" \
    --limit-mm-per-prompt '{"image":2}' --gpu-memory-utilization 0.90 $extra > "$slog" 2>&1 &
  VLLM_PID=$!
  local t0; t0=$(date +%s)
  while true; do
    if curl -sf -m 5 "http://127.0.0.1:$VLM_PORT/health" >/dev/null 2>&1; then
      log "vllm ready for $model after $(( $(date +%s) - t0 )) s"
      return 0
    fi
    if ! kill -0 "$VLLM_PID" 2>/dev/null; then
      log "vllm exited early for $model; last log lines:"; tail -n 40 "$slog"; VLLM_PID=""; return 1
    fi
    if [ $(( $(date +%s) - t0 )) -gt "$SERVER_WAIT_S" ]; then
      log "vllm not ready after ${SERVER_WAIT_S}s for $model"; stop_server; return 1
    fi
    sleep 10
  done
}

cd "$REPO"
mkdir -p "$OUT" "$RESULTS"
log "job $JOB, models: ${MODELS[*]}, gpu: $(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || echo '?')"

# 1. Setup.
run_stage setup bash scripts/pod_setup_recognition.sh

# 2. DWG round trip (LibreDWG).
run_stage dwg-roundtrip "$PY" -m wenart.recognition.bakeoff --stage dwg --projects projects --out "$OUT" \
  --libredwg-bin "$WS/tools/libredwg/bin"

# 3. OCR on every raster page (PaddleOCR on the GPU while vLLM is not running, Tesseract on CPU).
run_stage ocr "$PY" -m wenart.recognition.bakeoff --stage ocr --projects projects --out "$OUT" --retry-errors

# 4. Per model: server up, (GPU tests once), VLM stage, server down.
first=1
for model in "${MODELS[@]}"; do
  if ! start_server "$model"; then
    FAILED+=("vllm-serve-$(slug "$model")")
    continue
  fi
  if [ "$first" -eq 1 ]; then
    first=0
    export VLM_SERVER
    run_stage gpu-tests "$PY" -m pytest -m gpu tests/gpu/test_recognition.py -v -ra \
      --junitxml="$RESULTS/junit-recognition.xml"
  fi
  run_stage "vlm-$(slug "$model")" "$PY" -m wenart.recognition.bakeoff --stage vlm --projects projects \
    --out "$OUT" --models "$model" --server "$VLM_SERVER" --retry-errors
  stop_server
done

# 5. Two-pass agreement and summary.
run_stage twopass-summary "$PY" -m wenart.recognition.bakeoff --stage twopass --projects projects --out "$OUT" \
  --models "${MODELS[@]}"

# 6. Results.
copy_results
if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED stages: ${FAILED[*]}"
  exit 1
fi
log "all stages ok"
