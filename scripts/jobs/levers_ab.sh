#!/usr/bin/env bash
# Milestone 13 lever A/B job (docs/milestone13.md §13.3, track T5; pod P1 runs it through scripts/jobs/m13_p1.sh).
# Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and
# WENART_DEADLINE set; /workspace/venv has the CPU deps; Blender at /workspace/tools/blender/blender).
#
# What: for every light variant of WENART_LIGHT_VARIANT (wenart/blender/lighting.py: base, sun100, sun300, sun1000,
# evcap, rig, shell, all) the 8 fixed interior views of real02 and the 8 of real03 (wenart.run.ab.M13_AB_VIEWS) are
# built from the committed Milestone 11 baseline (results/furniture/<p>/building_final.json, the style of the
# baseline's scene manifest, its cameras replayed with WENART_CAMERAS_FROM) and rendered at AB_SAMPLES (128)
# into outputs/<p>/ab_m13/<variant>/; the render manifest (seconds, EV, lighting_dark, VRAM per view), the previews,
# the scene manifest's lighting block and the variant's nvidia-smi peak go to $RESULTS/ab_m13/<variant>/<p>/, one
# contact sheet per view (the M11 baseline and every variant side by side) to $RESULTS/ab_m13/sheets/ and the
# numbers to $RESULTS/ab_m13/summary.{json,md}. The GPU tests of the track (tests/gpu/test_m13_light.py) run at
# the end when time is left.
#
# Why: the sun constant, the EV cap, the room rig and the shell table are decided by the lead from these images
# and numbers (P1), not by guesswork; every variant renders the same cameras as the baseline.
#
# How: one Blender build and one render per project and variant (the build reuses its fingerprint: a variant is
# part of it, so a resumed job rebuilds nothing it has); every stage is timed, a failing stage is recorded and the
# job goes on (exit 1 at the end); results are copied after every stage and from the EXIT trap. The deadline
# (WENART_DEADLINE, epoch seconds, set by pod_entry.sh) is checked before every variant with AB_VARIANT_EST_S
# (default 300 s per project and variant) and render.py stops new views itself when it passes; the pod_entry.sh
# watchdog stops the pod at MAX_RUNTIME_S whatever happens here. Idempotent: outputs and renders live on the volume.
#
# Env: AB_PROJECTS (default "real02 real03"), AB_VARIANTS (default all nine: m11 = the Milestone 11 look, the
#      "before"; base = the production defaults of round 3, §14.3), AB_SAMPLES (128), AB_RES (1920x1080),
#      AB_VARIANT_EST_S (300), AB_GPU_TESTS (1 = run tests/gpu/test_m13_light.py at the end), AB_BASELINE_DIR
#      (default results/renders/{name}: the committed baseline files; equal to commit 93aff07, checked 15 Oct 2026),
#      WENART_LICENCE_MODE (unset = the project brief: relaxed for real02 / real03).
#
# Pod P6a (22 Oct 2026, the interior sky A/B; scripts/jobs/m13_p6.sh sets these, every default is P1's):
#      AB_VIEW_SET (levers = wenart.run.ab.M13_AB_VIEWS; sky = M13_SKY_AB_VIEWS, checked against the prepared scene
#      manifest by `wenart.run.ab m13-views`: a missing camera -> the next camera of its room), AB_SOURCE (baseline =
#      the committed baseline of AB_BASELINE_DIR; run = this pod's own run of the project: AB_RUN_DIR, default
#      outputs/{name}, its building_final.json, style.json, scene/scene_manifest.json cameras and renders/ previews,
#      the "before" column labelled AB_BASELINE_LABEL, default "run final"), AB_NAME (ab_m13: the folder under
#      outputs/<p>/ for the variant scenes and under $RESULTS for the results, e.g. ab_m13/sky).
# Fix round after P6a (22-23 Oct 2026): AB_VIEW_SET=skywin (wenart.run.ab.M13_SKYWIN_AB_VIEWS: real02's five window
#      views and one rig-lit hall, real04's sky views and hall) with AB_PROJECTS=real02 and AB_VARIANTS "base skywin35
#      sky35" is the windows-only sky A/B of pod P6c (scripts/jobs/m13_p6.sh sets them from P6_SKY_*); nothing else
#      changed here.
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO="${WENART_REPO:-$WS/repo}"
JOB="${JOB_ID:-levers_ab}"
LOG=$LOGS/levers_ab-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
PY="${WENART_PY:-$WS/venv/bin/python}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export WENART_OUTPUTS="$REPO/outputs"
if [ -n "${WENART_LICENCE_MODE:-}" ]; then export WENART_LICENCE_MODE; fi
SAMPLES="${AB_SAMPLES:-128}"
RES="${AB_RES:-1920x1080}"
EST_S="${AB_VARIANT_EST_S:-300}"
BASELINE_DIR="${AB_BASELINE_DIR:-$REPO/results/renders/{name}}"
read -r -a PROJECTS <<< "${AB_PROJECTS:-real02 real03}"
read -r -a VARIANTS <<< "${AB_VARIANTS:-m11 base sun100 sun300 sun1000 evcap rig shell all}"
VIEW_SET="${AB_VIEW_SET:-levers}"
SOURCE="${AB_SOURCE:-baseline}"
NAME="${AB_NAME:-ab_m13}"
RUN_DIR_T="${AB_RUN_DIR:-$REPO/outputs/{name}}"
AB_OUT=$RESULTS/$NAME
FAILED=()
SKIPPED=()

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] levers_ab: $*"; }

case "$SOURCE" in
  baseline) BASE_COL=baseline_m11; LABEL="${AB_BASELINE_LABEL:-M11 baseline}" ;;
  run) BASE_COL=run_final; LABEL="${AB_BASELINE_LABEL:-run final}" ;;
  *) log "unknown AB_SOURCE '$SOURCE' (baseline|run)"; exit 2 ;;
esac
case "$NAME" in
  ''|/*|*..*) log "AB_NAME '$NAME' must be a relative folder name"; exit 2 ;;
esac

# views_of <p>: the views of the set (comma separated); the sky set is checked against the prepared scene manifest.
views_of() {
  local scene=$REPO/outputs/$1/ab/m13/scene_manifest.json
  local -a sc=()
  if [ "$VIEW_SET" != "levers" ] && [ -f "$scene" ]; then sc=(--scene "$scene"); fi
  "$PY" -m wenart.run.ab m13-views --project "$1" --view-set "$VIEW_SET" "${sc[@]}" || true
}

# seconds_left: until WENART_DEADLINE (a huge number without one)
seconds_left() {
  case "${WENART_DEADLINE:-}" in
    ''|*[!0-9.]*) echo 999999 ;;
    *) echo $(( ${WENART_DEADLINE%.*} - $(date +%s) )) ;;
  esac
}

copy_results() {
  # Small files only: the render manifest, the previews, the lighting block of the scene manifest, the VRAM peak,
  # the build and render logs. Full-size PNGs and EXR passes stay on the volume.
  mkdir -p "$AB_OUT"
  local p v src dst
  for p in "${PROJECTS[@]}"; do
    for v in "${VARIANTS[@]}"; do
      src=$REPO/outputs/$p/$NAME/$v
      [ -d "$src" ] || continue
      dst=$AB_OUT/$v/$p
      mkdir -p "$dst"
      if [ -d "$src/renders" ]; then
        find "$src/renders" -maxdepth 1 -type f \( -name 'render_manifest.json' -o -name '*.log' -o -name 'vram.json' \) \
          -exec cp -f {} "$dst/" \;
        find "$src/renders" -maxdepth 1 -type f -name '*_preview.jpg' -size -400k -exec cp -f {} "$dst/" \;
      fi
      if [ -f "$src/scene/scene_manifest.json" ]; then
        "$PY" - "$src/scene/scene_manifest.json" "$dst/lighting.json" <<'PY' || true
import json, sys
m = json.load(open(sys.argv[1]))
keep = {k: m.get(k) for k in ("lighting", "light_variant", "cameras_from", "build_fingerprint", "camera_policy", "seconds")}
keep["materials_shell"] = {k: v for k, v in (m.get("materials") or {}).items() if v.get("shell_slot") or v.get("shell_layers")}
json.dump(keep, open(sys.argv[2], "w"), indent=1)
PY
        cp -f "$src/scene/build.log" "$dst/" 2>/dev/null || true
      fi
    done
    # the baseline previews of the views (the "before" column of the sheets; AB_SOURCE=run: the run's final renders)
    local base=${BASELINE_DIR//\{name\}/$p}
    if [ "$SOURCE" = "run" ]; then base=${RUN_DIR_T//\{name\}/$p}/renders; fi
    if [ -d "$base" ]; then
      mkdir -p "$AB_OUT/$BASE_COL/$p"
      for cam in $(views_of "$p" | tr ',' ' '); do
        cp -f "$base/${cam}_preview.jpg" "$AB_OUT/$BASE_COL/$p/" 2>/dev/null || true
      done
    fi
    cp -f "$REPO/outputs/$p/ab/m13/prepare_m13.json" "$AB_OUT/prepare_$p.json" 2>/dev/null || true
  done
  cp -f "$LOG" "$AB_OUT/" 2>/dev/null || true
  log "results copied to $AB_OUT: $(find "$AB_OUT" -type f | wc -l) files"
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
  "$@" || rc=$?
  log "stage end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  if [ "$rc" -ne 0 ]; then FAILED+=("$name"); fi
  copy_results
  return 0
}

stage_failed() {
  local f
  for f in "${FAILED[@]}"; do [ "$f" = "$1" ] && return 0; done
  return 1
}

# vram_sampler <file>: nvidia-smi memory.used every second into <file> until stopped (the variant's peak).
vram_sampler() {
  local file=$1
  : > "$file"
  while true; do
    nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 >> "$file" || true
    sleep 1
  done
}

write_vram_json() {
  local samples=$1 out=$2
  "$PY" - "$samples" "$out" <<'PY' || true
import json, sys
vals = []
for line in open(sys.argv[1]):
    line = line.strip()
    if line.replace(".", "").isdigit():
        vals.append(int(float(line)))
json.dump({"peak_mib": max(vals) if vals else None, "samples": len(vals), "source": "nvidia-smi memory.used, 1 s"},
          open(sys.argv[2], "w"), indent=1)
PY
}

cd "$REPO"
mkdir -p "$RESULTS" "$ASSETS" outputs "$AB_OUT"
log "job $JOB, projects: ${PROJECTS[*]}, variants: ${VARIANTS[*]}, samples $SAMPLES, res $RES, views $VIEW_SET, source $SOURCE, out $NAME, deadline in $(seconds_left) s, blender $("$WENART_BLENDER" --version 2>/dev/null | head -1)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

# 1. The baseline files of every project (the committed Milestone 11 run; AB_SOURCE=run: this pod's run) into
#    outputs/<p>/ab/m13/.
for p in "${PROJECTS[@]}"; do
  if [ "$SOURCE" = "run" ]; then
    rd=${RUN_DIR_T//\{name\}/$p}
    if [ -f "$rd/building_final.json" ] && [ -f "$rd/scene/scene_manifest.json" ]; then
      run_stage "prepare-$p" "$PY" -m wenart.run.ab m13-prepare --project "$p" --project-out "outputs/$p" \
        --from-run "$rd" --view-set "$VIEW_SET"
    else
      log "$p: no run output to prepare from ($rd: building_final.json, scene/scene_manifest.json)"
      FAILED+=("prepare-$p")
    fi
    if stage_failed "prepare-$p"; then continue; fi     # never build an earlier prepare's files
  else
    base=${BASELINE_DIR//\{name\}/$p}
    if [ -d "$base" ]; then
      run_stage "prepare-$p" "$PY" -m wenart.run.ab m13-prepare --project "$p" --project-out "outputs/$p" --from "$base"
    else
      run_stage "prepare-$p" "$PY" -m wenart.run.ab m13-prepare --project "$p" --project-out "outputs/$p"
    fi
  fi
  if [ -f "outputs/$p/ab/m13/style.json" ]; then
    run_stage "assets-$p" "$PY" -m wenart.assets fetch --style "outputs/$p/ab/m13/style.json" --assets "$ASSETS" --size 2k
  fi
done

# 2. Build and render per project and variant.
for v in "${VARIANTS[@]}"; do
  for p in "${PROJECTS[@]}"; do
    m13=outputs/$p/ab/m13
    if [ ! -f "$m13/scene_manifest.json" ] || [ ! -f "$m13/building_final.json" ]; then
      log "$p: no baseline scene manifest or building (prepare failed?), variant $v skipped"
      SKIPPED+=("$v/$p"); continue
    fi
    if [ "$SOURCE" = "run" ] && stage_failed "prepare-$p"; then
      log "$p: the run output was not prepared, variant $v skipped"
      SKIPPED+=("$v/$p"); continue
    fi
    left=$(seconds_left)
    if [ "$left" -lt "$EST_S" ]; then
      log "$p $v: $left s left before WENART_DEADLINE (< $EST_S s): skipped"
      SKIPPED+=("$v/$p"); continue
    fi
    views=$(views_of "$p")
    if [ -z "$views" ]; then
      log "$p $v: no view of the set '$VIEW_SET' in the prepared cameras: skipped"
      SKIPPED+=("$v/$p"); continue
    fi
    out=outputs/$p/$NAME/$v
    mkdir -p "$out"
    export WENART_LIGHT_VARIANT="$v"
    export WENART_CAMERAS_FROM="$m13/scene_manifest.json"
    unset WENART_CAMERAS_EXTRA
    STYLE_ARG=(); [ -f "$m13/style.json" ] && STYLE_ARG=(--style "$m13/style.json")
    ASSET_ARG=(); [ -f "$ASSETS/manifest.json" ] && ASSET_ARG=(--assets "$ASSETS")
    run_stage "build-$p-$v" "$PY" -m wenart.blender.cli build --building "$m13/building_final.json" \
      "${STYLE_ARG[@]}" "${ASSET_ARG[@]}" --out "$out/scene" --preview-samples 4 --camera-policy search \
      --brief "projects/$p" --reuse
    if stage_failed "build-$p-$v" || [ ! -f "$out/scene/scene.blend" ]; then
      log "$p $v: build failed, render skipped"
      continue
    fi
    mkdir -p "$out/renders"
    vram_sampler "$out/renders/vram_samples.txt" &
    SAMPLER=$!
    run_stage "render-$p-$v" "$PY" -m wenart.blender.cli render --scene "$out/scene/scene.blend" \
      --out "$out/renders" --cameras "$views" --samples "$SAMPLES" --res "$RES" \
      --exposure auto --white-balance project --preview-quality 85
    kill "$SAMPLER" 2>/dev/null || true
    wait "$SAMPLER" 2>/dev/null || true
    write_vram_json "$out/renders/vram_samples.txt" "$out/renders/vram.json"
    [ -f "$out/renders/render.log" ] && grep -E "^(DEVICE|LIGHT_VARIANT|WHITE_BALANCE|RENDERED|RERENDER|SKIP|RENDER_INCOMPLETE)" "$out/renders/render.log" || true
    copy_results
  done
done
unset WENART_LIGHT_VARIANT WENART_CAMERAS_FROM

# 3. Contact sheets and the summary (a view set other than the levers' is resolved against the prepared cameras).
VIEW_ARGS=(--view-set "$VIEW_SET")
if [ "$VIEW_SET" != "levers" ]; then VIEW_ARGS+=(--scene "$REPO/outputs/{name}/ab/m13/scene_manifest.json"); fi
run_stage sheets "$PY" -m wenart.run.ab m13-sheets --results "$AB_OUT" --projects "$(IFS=,; echo "${PROJECTS[*]}")" \
  --variants "$(IFS=,; echo "${VARIANTS[*]}")" --baseline "$AB_OUT/$BASE_COL/{name}" --baseline-label "$LABEL" \
  "${VIEW_ARGS[@]}"
run_stage summary "$PY" -m wenart.run.ab m13-summary --results "$AB_OUT" --projects "$(IFS=,; echo "${PROJECTS[*]}")" \
  --variants "$(IFS=,; echo "${VARIANTS[*]}")" "${VIEW_ARGS[@]}"

# 4. The track's GPU tests (small scenes per variant; skipped when the deadline is near).
if [ "${AB_GPU_TESTS:-1}" = "1" ] && [ "$(seconds_left)" -gt "$EST_S" ]; then
  run_stage gpu-tests "$PY" -m pytest -m gpu tests/gpu/test_m13_light.py -v -ra --junitxml="$RESULTS/junit-m13-light.xml"
else
  log "GPU tests skipped (AB_GPU_TESTS=${AB_GPU_TESTS:-1}, $(seconds_left) s left)"
fi

copy_results
if [ "${#SKIPPED[@]}" -gt 0 ]; then log "skipped (deadline or missing baseline): ${SKIPPED[*]}"; fi
if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED stages: ${FAILED[*]}"
  exit 1
fi
log "all stages ok"
