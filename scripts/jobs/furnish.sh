#!/usr/bin/env bash
# Milestone 4 furnish job. Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo,
# WENART_RESULTS set, /workspace/venv has the CPU deps, Blender at /workspace/tools/blender/blender).
# One Qwen vLLM server for the whole job (venv /opt/wenart/venv-vllm, port 8001 as in bakeoff.sh),
# then the GPU is handed to Cycles: a server holding 90 % of the VRAM leaves no room for a render,
# so the job runs in two phases over the projects (default synthetic-01 synthetic-03):
#   phase A  1. pipeline   python -m wenart.ingest.pipeline projects/<p> --out outputs/<p>
#            2. style      python -m wenart.style               -> outputs/<p>/style.json
#            3. assets     python -m wenart.assets fetch         -> /workspace/assets (textures, HDRI)
#            4. fit        python -m wenart.furniture.fit        -> outputs/<p>/building_fitted.json
#            5. layout     python -m wenart.furniture.layout     -> outputs/<p>/building_furnished.json,
#                          layout.json, layout_report.md, layout_debug/ (server up once for all projects)
#   server stopped
#   phase B  6. decor      python -m wenart.furniture.decor      -> outputs/<p>/building_decor.json
#            7. refit      fit again so the AI pieces get an asset -> outputs/<p>/building_final.json
#            8. build      wenart.blender.cli build (assets + decor) -> outputs/<p>/scene
#            9. render     wenart.blender.cli render --samples 128   -> outputs/<p>/renders
#           10. GPU tests  pytest -m gpu tests/gpu/test_furnish.py (layout) and tests/gpu/test_render.py
#           11. copy of the small files into $WENART_RESULTS (also after every stage and on exit).
# Projects whose building.json is `needs_review` (synthetic-02: raster only) are skipped after the
# pipeline stage, as in render.sh. Style, assets and fit are optional: when one fails the next stage
# uses the previous building file (recorded in the log). Resumable: outputs live on the volume; a
# layout is reused when building_furnished.json exists (FORCE_FURNISH=1 re-runs it), a render when
# its files match the current scene.blend (FORCE_RENDER=1 re-renders). Every stage is timed, a
# failing stage is recorded and the later stages still run (exit code 1 at the end).
# The pod_entry.sh watchdog stops the pod at MAX_RUNTIME_S without signalling the job, so the
# results are copied after every stage and from the EXIT trap.
set -Eeuo pipefail

WS=/workspace
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-furnish}"
LOG=$LOGS/furnish-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
PY="${WENART_PY:-$WS/venv/bin/python}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
FAST=/opt/wenart                      # container disk (see pod_setup_recognition.sh)
VENV_VLLM=$FAST/venv-vllm
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
MODEL="${FURNISH_MODEL:-Qwen/Qwen3-VL-8B-Instruct}"
VLM_PORT="${VLM_PORT:-8001}"
VLM_SERVER="http://127.0.0.1:$VLM_PORT/v1"
SERVER_WAIT_S="${SERVER_WAIT_S:-1500}"
CATALOG=wenart/furniture/catalog.json
SAMPLES="${RENDER_SAMPLES:-128}"
RES="${RENDER_RES:-1920x1080}"
PASSES="${LAYOUT_PASSES:-2}"
FORCE_ARG=""; [ "${FORCE_RENDER:-0}" = "1" ] && FORCE_ARG="--force"
read -r -a PROJECTS <<< "${FURNISH_PROJECTS:-synthetic-01 synthetic-03}"
FAILED=()
ACTIVE=()      # projects with an ok building after the pipeline stage
LAID_OUT=()    # projects whose layout stage produced building_furnished.json
RENDERED=()    # projects whose render stage ran and succeeded
VLLM_PID=""

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] furnish: $*"; }

copy_results() {
  # Small files only: JSON and markdown of every stage, scene/render manifests and logs, JPEG
  # previews (<= 300 KB), top-down level PNGs, the layout debug PNGs and the fit/layout reports.
  mkdir -p "$RESULTS"
  local p
  for p in "${PROJECTS[@]}"; do
    local src=$REPO/outputs/$p dst=$RESULTS/$p
    [ -d "$src" ] || continue
    mkdir -p "$dst"
    find "$src" -maxdepth 1 -type f \( -name '*.json' -o -name '*.md' \) -size -4000k -exec cp -f {} "$dst/" \;
    if [ -d "$src/layout_debug" ]; then
      mkdir -p "$dst/layout_debug"
      find "$src/layout_debug" -maxdepth 1 -type f \( -name '*.json' -o -name '*.png' \) -size -1000k \
        -exec cp -f {} "$dst/layout_debug/" \;
    fi
    if [ -d "$src/scene" ]; then
      find "$src/scene" -maxdepth 1 -type f \( -name '*.json' -o -name '*.log' -o -name 'level_*_top.png' \) \
        -size -4000k -exec cp -f {} "$dst/" \;
    fi
    if [ -d "$src/renders" ]; then
      find "$src/renders" -maxdepth 1 -type f \( -name '*.json' -o -name '*.log' \) -exec cp -f {} "$dst/" \;
      find "$src/renders" -maxdepth 1 -type f -name '*_preview.jpg' -size -301k -exec cp -f {} "$dst/" \;
    fi
  done
  [ -f "$ASSETS/manifest.json" ] && cp -f "$ASSETS/manifest.json" "$RESULTS/assets_manifest.json" || true
  for f in "$LOGS"/vllm-*.log; do [ -f "$f" ] && tail -n 200 "$f" > "$RESULTS/$(basename "$f")"; done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  log "results copied to $RESULTS: $(find "$RESULTS" -type f | wc -l) files"
}

stop_server() {
  if [ -n "$VLLM_PID" ] && kill -0 "$VLLM_PID" 2>/dev/null; then
    log "stopping vllm (pid $VLLM_PID)"
    kill "$VLLM_PID" 2>/dev/null || true
    for _ in $(seq 1 30); do kill -0 "$VLLM_PID" 2>/dev/null || break; sleep 2; done
    kill -9 "$VLLM_PID" 2>/dev/null || true
  fi
  VLLM_PID=""
}

on_error() { log "ERROR at line $1"; exit 1; }
trap 'on_error $LINENO' ERR
on_exit() { trap - ERR; stop_server; copy_results; }
trap 'on_exit' EXIT
trap 'exit 143' TERM

# run_stage <name> <command...>: timed, failure recorded, job continues, results flushed.
run_stage() {
  local name=$1; shift
  local t0; t0=$(date +%s)
  log "stage start: $name"
  local rc=0
  "$@" || rc=$?      # exempt from errexit and the ERR trap
  log "stage end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  if [ "$rc" -ne 0 ]; then FAILED+=("$name"); fi
  copy_results
  return 0
}

# stage_failed <name>: true when run_stage recorded that stage as failed in this run.
stage_failed() {
  local f
  for f in "${FAILED[@]}"; do [ "$f" = "$1" ] && return 0; done
  return 1
}

in_list() { local x=$1; shift; local f; for f in "$@"; do [ "$f" = "$x" ] && return 0; done; return 1; }

building_status() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1])).get("status",""))' "$1" 2>/dev/null || echo ""; }

gpu_mem_mib() { nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ' || echo 0; }

# `vllm serve` flags as in bakeoff.sh (vLLM 0.30.0): fp8 weights, 8192 context and 2 sequences
# below 40 GB of VRAM; the layout prompts are text only (about 1500 tokens) with a 2048-token answer.
server_args() {
  local mem; mem=$(gpu_mem_mib)
  if [ "${mem:-0}" -lt 40000 ]; then
    echo "--quantization fp8 --max-model-len 8192 --max-num-seqs 2"
  else
    echo "--max-model-len 16384 --max-num-seqs 4"
  fi
}

start_server() {
  local extra; extra=$(server_args)
  local slog="$LOGS/vllm-$(basename "$MODEL").log"
  log "starting vllm serve $MODEL --port $VLM_PORT $extra (log $slog)"
  # VLLM_USE_FLASHINFER_SAMPLER=0: FlashInfer's sampler failed on sm_120 (bakeoff run 3).
  # shellcheck disable=SC2086
  VLLM_USE_FLASHINFER_SAMPLER=0 "$VENV_VLLM/bin/vllm" serve "$MODEL" --port "$VLM_PORT" \
    --limit-mm-per-prompt '{"image":1}' --gpu-memory-utilization 0.90 $extra > "$slog" 2>&1 &
  VLLM_PID=$!
  local t0; t0=$(date +%s)
  while true; do
    if curl -sf -m 5 "http://127.0.0.1:$VLM_PORT/health" >/dev/null 2>&1; then
      log "vllm ready for $MODEL after $(( $(date +%s) - t0 )) s"
      return 0
    fi
    if ! kill -0 "$VLLM_PID" 2>/dev/null; then
      log "vllm exited early; last log lines:"; tail -n 40 "$slog"; VLLM_PID=""; return 1
    fi
    if [ $(( $(date +%s) - t0 )) -gt "$SERVER_WAIT_S" ]; then
      log "vllm not ready after ${SERVER_WAIT_S}s"; stop_server; return 1
    fi
    sleep 10
  done
}

cd "$REPO"
mkdir -p "$RESULTS" "$ASSETS" outputs
log "job $JOB, projects: ${PROJECTS[*]}, model $MODEL, samples $SAMPLES, res $RES, blender $("$WENART_BLENDER" --version 2>/dev/null | head -1)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

# 0. Setup: vLLM venv and the Qwen checkpoint (the recognition setup script, one model only).
BAKEOFF_MODELS="$MODEL" run_stage setup bash scripts/pod_setup_recognition.sh

# Phase A: pipeline, style, assets, fit per project (CPU), then the layouts with the server up.
for p in "${PROJECTS[@]}"; do
  out=outputs/$p
  run_stage "pipeline-$p" "$PY" -m wenart.ingest.pipeline "projects/$p" --out "$out"
  status=$(building_status "$out/building.json")
  if [ "$status" != "ok" ]; then
    log "$p: building status '${status:-missing}', furnishing skipped (needs review)"
    # A needs_review building is the pipeline doing its job, not a failed stage.
    if [ "$status" = "needs_review" ]; then
      FAILED=("${FAILED[@]/pipeline-$p}")
      FAILED=($(printf '%s\n' "${FAILED[@]}" | grep -v '^$' || true))
    fi
    continue
  fi
  ACTIVE+=("$p")
  run_stage "style-$p" "$PY" -m wenart.style "projects/$p" --out "$out/style.json"
  run_stage "assets-$p" "$PY" -m wenart.assets fetch --style "$out/style.json" --assets "$ASSETS" --size 2k
  run_stage "fit-$p" "$PY" -m wenart.furniture.fit "$out/building.json" --catalog "$CATALOG" \
    --out "$out/building_fitted.json" --assets "$ASSETS"
  if stage_failed "fit-$p" || [ ! -f "$out/building_fitted.json" ]; then
    log "$p: fit failed, the layout uses building.json (no assets)"
    cp -f "$out/building.json" "$out/building_fitted.json"
  fi
done

SERVER_UP=0
NEED_LAYOUT=()
for p in "${ACTIVE[@]}"; do
  if [ "${FORCE_FURNISH:-0}" != "1" ] && [ -f "outputs/$p/building_furnished.json" ] && [ -f "outputs/$p/layout.json" ]; then
    log "$p: building_furnished.json exists, layout reused (FORCE_FURNISH=1 re-runs it)"
    LAID_OUT+=("$p")
  else
    NEED_LAYOUT+=("$p")
  fi
done
if [ "${#NEED_LAYOUT[@]}" -gt 0 ]; then
  if start_server; then
    SERVER_UP=1
    for p in "${NEED_LAYOUT[@]}"; do
      out=outputs/$p
      STYLE_ARG=(); [ -f "$out/style.json" ] && STYLE_ARG=(--style "$out/style.json")
      run_stage "layout-$p" "$PY" -m wenart.furniture.layout "$out/building_fitted.json" "${STYLE_ARG[@]}" \
        --server "$VLM_SERVER" --model "$MODEL" --out "$out/building_furnished.json" \
        --debug "$out/layout_debug" --passes "$PASSES"
      if ! stage_failed "layout-$p" && [ -f "$out/building_furnished.json" ]; then LAID_OUT+=("$p"); fi
    done
    stop_server
  else
    FAILED+=("vllm-serve")
    log "vllm server did not start: layouts skipped, the scenes get the documented furniture only"
  fi
fi

# Phase B: decor, refit, build, render per project (GPU free for Cycles).
for p in "${ACTIVE[@]}"; do
  out=outputs/$p
  src="$out/building_fitted.json"
  if in_list "$p" "${LAID_OUT[@]}"; then src="$out/building_furnished.json"; else log "$p: no layout, decor on $src"; fi
  run_stage "decor-$p" "$PY" -m wenart.furniture.decor "$src" --out "$out/building_decor.json"
  if stage_failed "decor-$p" || [ ! -f "$out/building_decor.json" ]; then
    log "$p: decor failed, continuing with $src"; cp -f "$src" "$out/building_decor.json"
  fi
  # The AI pieces were added after the first fit: fit again so they get an asset (or the fallback).
  run_stage "refit-$p" "$PY" -m wenart.furniture.fit "$out/building_decor.json" --catalog "$CATALOG" \
    --out "$out/building_final.json" --assets "$ASSETS"
  if stage_failed "refit-$p" || [ ! -f "$out/building_final.json" ]; then
    log "$p: refit failed, the scene is built from building_decor.json"
    cp -f "$out/building_decor.json" "$out/building_final.json"
  fi
  STYLE_ARG=(); [ -f "$out/style.json" ] && STYLE_ARG=(--style "$out/style.json")
  ASSET_ARG=(); [ -f "$ASSETS/manifest.json" ] && ASSET_ARG=(--assets "$ASSETS")
  run_stage "build-$p" "$PY" -m wenart.blender.cli build --building "$out/building_final.json" \
    "${STYLE_ARG[@]}" "${ASSET_ARG[@]}" --out "$out/scene" --preview-samples 32
  if stage_failed "build-$p"; then
    log "$p: build failed in this run, render stage skipped (scene.blend on the volume would be stale)"
  elif [ -f "$out/scene/scene.blend" ]; then
    # shellcheck disable=SC2086
    run_stage "render-$p" "$PY" -m wenart.blender.cli render --scene "$out/scene/scene.blend" \
      --out "$out/renders" --cameras all --samples "$SAMPLES" --res "$RES" $FORCE_ARG
    [ -f "$out/renders/render.log" ] && grep -E "^(DEVICE|RENDERED|RERENDER|SKIP)" "$out/renders/render.log" || true
    if ! stage_failed "render-$p"; then RENDERED+=("$p"); fi
  fi
done

# GPU tests: the layouts of this run (synthetic-01 L1 is the reference) and the renders.
export WENART_OUTPUTS="$REPO/outputs" FURNISH_MODEL="$MODEL"
if [ "${#LAID_OUT[@]}" -eq 0 ]; then
  log "no project laid out, layout GPU tests skipped"
else
  export FURNISH_TEST_PROJECTS="${LAID_OUT[*]}"
  log "layout GPU tests for: $FURNISH_TEST_PROJECTS"
  run_stage gpu-tests-furnish "$PY" -m pytest -m gpu tests/gpu/test_furnish.py -v -ra --junitxml="$RESULTS/junit-furnish.xml"
fi
if [ "${#RENDERED[@]}" -eq 0 ]; then
  log "no project rendered in this run, render GPU tests skipped"
else
  export RENDER_TEST_PROJECTS="${RENDERED[*]}"
  log "render GPU tests for: $RENDER_TEST_PROJECTS"
  run_stage gpu-tests-render "$PY" -m pytest -m gpu tests/gpu/test_render.py -v -ra --junitxml="$RESULTS/junit-render.xml"
fi

copy_results
if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED stages: ${FAILED[*]}"
  exit 1
fi
log "all stages ok (server used: $SERVER_UP)"
