#!/usr/bin/env bash
# Milestone 3 render job. Run by scripts/pod_entry.sh on a RunPod pod
# (cwd /workspace/repo, WENART_RESULTS set, /workspace/venv has the CPU deps,
# Blender at /workspace/tools/blender/blender). Stages per project in projects/:
#   1. pipeline   python -m wenart.ingest.pipeline projects/<p> --out outputs/<p>
#   2. style      python -m wenart.style (brief -> outputs/<p>/style.json)
#   3. assets     python -m wenart.assets (CC0 textures + HDRI into /workspace/assets)
#   4. build      wenart.blender.cli build  -> outputs/<p>/scene (blend, glb, manifests, top-down PNGs)
#   5. render     wenart.blender.cli render --samples 256 -> outputs/<p>/renders (time per view logged)
# then  6. pytest -m gpu tests/gpu/test_render.py  and  7. copy of the small files into $WENART_RESULTS.
# Projects whose building.json is `needs_review` (synthetic-02: raster only) are skipped
# after the pipeline stage. Style and asset stages are optional: when they fail the
# build runs with the default style profile and flat colours (recorded in the manifest).
# Idempotent: the pipeline output, the scene and the renders live on the volume; renders
# whose PNG exists are skipped unless FORCE_RENDER=1. Every stage is timed, a failing
# stage is recorded and the later stages still run (exit code 1 at the end).
# Results are copied after every stage and from the EXIT trap: the pod_entry.sh
# watchdog stops the pod at MAX_RUNTIME_S without signalling the job.
set -Eeuo pipefail

WS=/workspace
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-render}"
LOG=$LOGS/render-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
PY="${WENART_PY:-$WS/venv/bin/python}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
SAMPLES="${RENDER_SAMPLES:-256}"
RES="${RENDER_RES:-1920x1080}"
FORCE_ARG=""; [ "${FORCE_RENDER:-0}" = "1" ] && FORCE_ARG="--force"
read -r -a PROJECTS <<< "${RENDER_PROJECTS:-$(ls -d projects/*/ 2>/dev/null | xargs -n1 basename | tr '\n' ' ')}"
FAILED=()

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] render: $*"; }

copy_results() {
  # Small files only: manifests, reports, logs, JPEG previews (<= 300 KB each) and the
  # top-down level PNGs. Full-size PNGs and EXR passes stay on the volume.
  mkdir -p "$RESULTS"
  for p in "${PROJECTS[@]}"; do
    local src=$REPO/outputs/$p dst=$RESULTS/$p
    [ -d "$src" ] || continue
    mkdir -p "$dst"
    find "$src" -maxdepth 1 -type f \( -name '*.json' -o -name '*.md' \) -exec cp -f {} "$dst/" \;
    if [ -d "$src/scene" ]; then
      find "$src/scene" -maxdepth 1 -type f \( -name '*.json' -o -name '*.log' -o -name 'level_*_top.png' \) \
        -size -4000k -exec cp -f {} "$dst/" \;
    fi
    if [ -d "$src/renders" ]; then
      find "$src/renders" -maxdepth 1 -type f \( -name '*.json' -o -name '*.log' \) -exec cp -f {} "$dst/" \;
      find "$src/renders" -maxdepth 1 -type f -name '*_preview.jpg' -size -301k -exec cp -f {} "$dst/" \;
    fi
  done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  log "results copied to $RESULTS: $(find "$RESULTS" -type f | wc -l) files"
}

on_error() { log "ERROR at line $1"; exit 1; }
trap 'on_error $LINENO' ERR
on_exit() { trap - ERR; copy_results; }
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

building_status() { "$PY" -c 'import json,sys; print(json.load(open(sys.argv[1])).get("status",""))' "$1" 2>/dev/null || echo ""; }

cd "$REPO"
mkdir -p "$RESULTS" "$ASSETS" outputs
log "job $JOB, projects: ${PROJECTS[*]}, samples $SAMPLES, res $RES, blender $("$WENART_BLENDER" --version 2>/dev/null | head -1)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

for p in "${PROJECTS[@]}"; do
  out=outputs/$p
  run_stage "pipeline-$p" "$PY" -m wenart.ingest.pipeline "projects/$p" --out "$out"
  status=$(building_status "$out/building.json")
  if [ "$status" != "ok" ]; then
    log "$p: building status '${status:-missing}', scene build skipped (needs review)"
    continue
  fi
  # Style profile and assets (modules maintained with the style/assets work; optional here).
  run_stage "style-$p" "$PY" -m wenart.style "projects/$p" --out "$out/style.json"
  STYLE_ARG=(); [ -f "$out/style.json" ] && STYLE_ARG=(--style "$out/style.json")
  run_stage "assets-$p" "$PY" -m wenart.assets fetch --style "$out/style.json" --assets "$ASSETS" --size 2k
  ASSET_ARG=(); [ -f "$ASSETS/manifest.json" ] && ASSET_ARG=(--assets "$ASSETS")
  run_stage "build-$p" "$PY" -m wenart.blender.cli build --building "$out/building.json" \
    "${STYLE_ARG[@]}" "${ASSET_ARG[@]}" --out "$out/scene" --preview-samples 32
  if [ -f "$out/scene/scene.blend" ]; then
    # shellcheck disable=SC2086
    run_stage "render-$p" "$PY" -m wenart.blender.cli render --scene "$out/scene/scene.blend" \
      --out "$out/renders" --cameras all --samples "$SAMPLES" --res "$RES" $FORCE_ARG
    [ -f "$out/renders/render.log" ] && grep -E "^(DEVICE|RENDERED|SKIP)" "$out/renders/render.log" || true
  fi
done

export WENART_OUTPUTS="$REPO/outputs"
run_stage gpu-tests "$PY" -m pytest -m gpu tests/gpu/test_render.py -v -ra --junitxml="$RESULTS/junit-render.xml"

copy_results
if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED stages: ${FAILED[*]}"
  exit 1
fi
log "all stages ok"
