#!/usr/bin/env bash
# Milestone 13 pod P1 (docs/milestone13.md §13.6, §8): the lever A/B of track T5, the site A/B of track T6 and the
# GPU tests of the Milestone 13 tracks, in one pod. Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo;
# WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE set; /workspace/venv has the CPU deps; Blender at
# /workspace/tools/blender/blender; no agent or vision model is needed).
#
#   scripts/gpu_run.py run --job scripts/jobs/m13_p1.sh --disk 60 --max-minutes 240 --grace 600 --over-5-ok \
#     --purpose "M13 P1: lever A/B (light), site A/B (vegetation, platforms, pools, sky), GPU tests"
#
# What, in order (every step records its failure and the next one still runs; exit 1 at the end when one failed):
#   1. scripts/pod_setup_vegetation.sh: the Sapling Tree Gen extension, the Poly Haven CC0 tree models and the
#      ambientCG leaf atlases under $WENART_ASSETS (idempotent; the site A/B falls back to leaf-card trees without
#      them and says so in its manifests).
#   2. scripts/jobs/levers_ab.sh: 8 fixed interior views of real02 and real03 x the light variants, from the committed
#      Milestone 11 baseline with its cameras replayed; the most telling variants first (base, all, sun300, sun1000,
#      sun100, rig, shell, evcap) so that a cut by the deadline loses the least. Its GPU tests
#      (tests/gpu/test_m13_light.py) run at its end.
#   3. scripts/jobs/site_ab.sh: 3 fixed exterior views of real04 and real02 x the site variants (base, all, hedge, sky,
#      instances, sapling, platforms, pools); its GPU tests (tests/gpu/test_m13_site.py) at its end.
#   4. tests/gpu/test_m13_modules.py (track T2: module builders and families v2 built in Blender).
#
# Why: the lead sets the light constants (SUN_STRENGTH_WM2, LEVER_DEFAULTS rig / shell, RIG_GAIN, the sun-disc
# reference) and the site levers from these images and numbers, not from guesswork (§13.3); one pod, not four.
#
# How: the two A/B jobs read WENART_DEADLINE themselves and skip variants when it nears; this wrapper gives the lever
# A/B the share P1_LEVERS_SHARE (default 0.50) of the time left after the setup and the site A/B the rest minus the
# time of step 4 (P1_TESTS_RESERVE_S, default 600 s), by exporting a tighter WENART_DEADLINE per step. Results land
# under $WENART_RESULTS/ab_m13/ (levers) and $WENART_RESULTS/ab_m13/site/ (site); the runner collects them. Logs in
# /workspace/logs/. Idempotent: the sub-jobs reuse their builds and renders on the volume.
#
# Env: P1_LEVERS_SHARE (0.50), P1_TESTS_RESERVE_S (600), AB_SAMPLES (128, both A/Bs), P1_SKIP_SETUP=1,
#      P1_SKIP_LEVERS=1, P1_SKIP_SITE=1, P1_SKIP_TESTS=1, WENART_LICENCE_MODE (unset = the project briefs: relaxed),
#      and every variable of the two A/B jobs (AB_PROJECTS and AB_VARIANTS are set here per step unless given as
#      P1_LEVERS_VARIANTS / P1_SITE_VARIANTS).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO="${WENART_REPO:-$WS/repo}"
JOB="${JOB_ID:-m13_p1}"
LOG=$LOGS/m13_p1-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
export WENART_ASSETS="$ASSETS" WENART_RESULTS="$RESULTS"
PY="${WENART_PY:-$WS/venv/bin/python}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
if [ -n "${WENART_LICENCE_MODE:-}" ]; then export WENART_LICENCE_MODE; fi
export AB_SAMPLES="${AB_SAMPLES:-128}"
SHARE="${P1_LEVERS_SHARE:-0.50}"
RESERVE="${P1_TESTS_RESERVE_S:-600}"
FINAL_DEADLINE="${WENART_DEADLINE:-}"
FAILED=()

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] m13_p1: $*"; }
trap 'log "error at line $LINENO (exit $?)"' ERR

now_s() { date -u +%s; }
# seconds_left: until the pod's WENART_DEADLINE (a huge number without one).
seconds_left() {
  if [ -n "$FINAL_DEADLINE" ]; then echo $(( ${FINAL_DEADLINE%.*} - $(now_s) )); else echo 999999; fi
}
# step_deadline <share>: now + share x the time left before the final deadline, minus the reserve for step 4;
# empty without a final deadline (the sub-job then runs to its end).
step_deadline() {
  if [ -z "$FINAL_DEADLINE" ]; then echo ""; return; fi
  "$PY" - "$(now_s)" "${FINAL_DEADLINE%.*}" "$1" "$RESERVE" <<'PY'
import sys
now, final, share, reserve = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
left = max(0, final - reserve - now)
print(now + int(left * share))
PY
}
# run_step <name> <command...>: timed, failure recorded, the job goes on.
run_step() {
  local name=$1; shift
  local t0; t0=$(now_s)
  log "step $name: start ($(seconds_left) s left before the final deadline)"
  if "$@"; then
    log "step $name: ok in $(( $(now_s) - t0 )) s"
  else
    local rc=$?
    log "step $name: FAILED (exit $rc) after $(( $(now_s) - t0 )) s"
    FAILED+=("$name")
  fi
}

cd "$REPO"
mkdir -p "$RESULTS" "$ASSETS"
log "job $JOB, results $RESULTS, assets $ASSETS, final deadline ${FINAL_DEADLINE:-none} ($(seconds_left) s left), samples $AB_SAMPLES, levers share $SHARE, tests reserve $RESERVE s"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

# 1. Vegetation setup (the site A/B works without it, with fallbacks).
if [ "${P1_SKIP_SETUP:-0}" != "1" ]; then
  run_step vegetation-setup bash scripts/pod_setup_vegetation.sh
  [ -f "$ASSETS/vegetation_status.json" ] && cp "$ASSETS/vegetation_status.json" "$RESULTS/vegetation_status.json" || true
fi

# 2. Lever A/B (track T5): its share of the time; the most telling variants first.
if [ "${P1_SKIP_LEVERS:-0}" != "1" ]; then
  d=$(step_deadline "$SHARE")
  log "lever A/B deadline: ${d:-none}"
  run_step levers-ab env ${d:+WENART_DEADLINE=$d} AB_PROJECTS="${P1_LEVERS_PROJECTS:-real02 real03}" \
    AB_VARIANTS="${P1_LEVERS_VARIANTS:-base all sun300 sun1000 sun100 rig shell evcap}" AB_GPU_TESTS=1 \
    bash scripts/jobs/levers_ab.sh
fi

# 3. Site A/B (track T6): the rest of the time minus the reserve.
if [ "${P1_SKIP_SITE:-0}" != "1" ]; then
  d=$(step_deadline 1.0)
  log "site A/B deadline: ${d:-none}"
  run_step site-ab env ${d:+WENART_DEADLINE=$d} AB_PROJECTS="${P1_SITE_PROJECTS:-real04 real02}" \
    AB_VARIANTS="${P1_SITE_VARIANTS:-base all hedge sky instances sapling platforms pools}" AB_GPU_TESTS=1 \
    bash scripts/jobs/site_ab.sh
fi

# 4. The module builders' GPU tests (track T2).
if [ "${P1_SKIP_TESTS:-0}" != "1" ]; then
  if [ "$(seconds_left)" -gt 120 ]; then
    run_step gpu-tests-modules "$PY" -m pytest -m gpu tests/gpu/test_m13_modules.py -v -ra \
      --junitxml="$RESULTS/junit-m13-modules.xml"
  else
    log "module GPU tests skipped: $(seconds_left) s left"
    FAILED+=("gpu-tests-modules-skipped")
  fi
fi

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
