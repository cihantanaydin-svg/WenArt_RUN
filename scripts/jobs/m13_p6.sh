#!/usr/bin/env bash
# Milestone 13 pod P6a (docs/milestone13.md §14.13 decision 4; the user's OK of 22 Oct 2026): the final full run of
# real04 and, when time is left, the interior sky A/B. Run by scripts/pod_entry.sh on a RunPod pod (cwd
# /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE set; /workspace/venv has the CPU deps; Blender at
# /workspace/tools/blender/blender).
#
#   scripts/gpu_run.py run --job scripts/jobs/m13_p6.sh --gpu 'RTX PRO 6000' --disk 150 --max-minutes 240 \
#     --grace 600 --over-5-ok --env RUN_POLISH=off --env RENDER_SAMPLES=256 \
#     --purpose "M13 P6a: real04 full run (fix round after P5; polish off; 256 spp; GPU tests) + interior sky A/B"
#
# What, in order (a failing step is recorded and the next one still runs; exit 1 at the end when one failed):
#   1. scripts/jobs/full.sh for RUN_PROJECTS (default real04) with the pod's own WENART_DEADLINE: every stage, the
#      agent rounds, the final renders, the report and the GPU tests of the full profile (phase 11, which the
#      orchestrator always runs, also late). full.sh reads its own variables (RENDER_SAMPLES, RUN_POLISH,
#      CAMERAS_FROM, RUN_FRESH_RECOGNITION, AGENT_ROUNDS, ...) from this job's environment.
#   2. The interior sky A/B (P6_SKY_AB=1; only for P6_SKY_PROJECT, default real04, only when it is in RUN_PROJECTS and
#      this job's run built it): scripts/jobs/levers_ab.sh with AB_SOURCE=run (this pod's building, style and
#      cameras of that project), AB_VIEW_SET P6_SKY_VIEW_SET (sky: the 6 views of wenart.run.ab.M13_SKY_AB_VIEWS),
#      AB_VARIANTS P6_SKY_VARIANTS
#      ("sky0 sky2 sky35 sky52": the old interior world and that world +2 / +3.5 / +5.2 stops, wenart.blender.lighting
#      SKY_VARIANTS; P6a ran "base sky2 sky35 sky52" when base was the old world), AB_SAMPLES P6_SKY_SAMPLES (128),
#      AB_NAME P6_SKY_NAME (ab_m13/sky) and no GPU tests of its own. Results in $WENART_RESULTS/ab_m13/sky/: per
#      variant the render manifest, previews and lighting block, one contact sheet per view (the run's final render
#      first, then sky0, sky2, sky35, sky52) and summary.{json,md}. It starts only
#      when the time left before WENART_DEADLINE minus the reserve (P6_RESERVE_S for the copy and the collect, plus
#      P6_TESTS_RESERVE_S when step 3 still has to run the GPU tests) covers P6_SKY_MIN_VARIANTS variants of
#      P6_SKY_VARIANT_EST_S, and it gets that deadline (levers_ab.sh skips the variants that no longer fit).
#   3. The GPU tests: kept to one run. full.sh ran them when $WENART_RESULTS/junit-full.xml is newer than this job's
#      start; else (the orchestrator died before phase 11, or P6_SKIP_FULL=1) the full group of tests/gpu runs once
#      here with the project lists of this job's run manifest (wenart.run.scheduler.GPU_TEST_GROUPS, TEST_LISTS),
#      when more than P6_TESTS_MIN_S are left; otherwise the step fails with the reason.
#
# Why: P5's windows showed a dark sky over a near-white ground band and the rooms facing the lawn read green; both
# come from the interior HDRI about 5.2 stops under the exterior sky pair (materials.world_nodes). The user picks the
# level from the sheets (the same building, cameras and production levers; only the interior world differs). real03
# and real02 (pods P6b, P6c) run scripts/jobs/full.sh as before (this job with P6_SKY_AB=0 would do the same).
#
# How: the wrapper never stops the pod (pod_entry.sh's watchdog does, at MAX_RUNTIME_S whatever happens here); every
# step is timed; the sub-jobs copy their results themselves (full.sh: wenart.run copy in its loop and EXIT trap;
# levers_ab.sh after every stage and on EXIT); this job's log goes to $WENART_RESULTS on EXIT. Idempotent: the same
# command resumes (full.sh's stage fingerprints and render keys, levers_ab.sh's build fingerprints with the variant
# in them, render keys). Logs in /workspace/logs/.
#
# Fix round after P6a (22-23 Oct 2026; the user's decision of 22 Oct 2026, "Windows only +3.5", needs one short A/B on
# pod P6c, real02, before it becomes the default): the project, the view set and the folder of the A/B come from the
# environment; every default is P6a's. P6c:
#
#   scripts/gpu_run.py run --job scripts/jobs/m13_p6.sh --gpu 'RTX PRO 6000' --disk 150 --max-minutes 240 \
#     --grace 600 --over-5-ok --env RUN_PROJECTS=real02 \
#     --env 'CAMERAS_FROM=results/renders/{name}/scene_manifest.json' --env RUN_POLISH=off --env RENDER_SAMPLES=256 \
#     --env P6_SKY_PROJECT=real02 --env P6_SKY_VIEW_SET=skywin --env 'P6_SKY_VARIANTS=sky0 skywin35 sky35' \
#     --env P6_SKY_NAME=ab_m13/skywin \
#     --purpose "M13 P6c: real02 final full run (M11 cameras replayed; polish off; 256 spp; GPU tests) + windows-only
#                sky A/B (sky0, skywin35, sky35)"
#
# (wenart.run.ab.M13_SKYWIN_AB_VIEWS: five real02 views with windows and one rig-lit hall; skywin35 = the interior world
# +3.5 stops on the camera's paths only, wenart.blender.lighting.SKY_WINDOW_VARIANTS; sky35 = the whole world, P6a's).
#
# Milestone 13 final pass (23 Oct 2026; the user's decision after pod P6c): skywin35 is production
# (wenart.blender.lighting.PRODUCTION_SKY_STOPS), so base is no longer the old world; sky0
# (lighting.SKY_OLD_WORLD_VARIANT) is the A/B's "before" in the defaults and in the P6c command above. P6c itself ran
# 'P6_SKY_VARIANTS=base skywin35 sky35' (base = the old world then): its results/review/m13_p6c/sky_ab folders are
# base, skywin35, sky35.
#
# Env: RUN_PROJECTS (real04), P6_SKY_AB (1), P6_SKY_PROJECT (real04), P6_SKY_VARIANTS ("sky0 sky2 sky35 sky52"),
#      P6_SKY_VIEW_SET (sky; skywin for the windows-only A/B), P6_SKY_NAME (ab_m13/sky; a relative folder),
#      P6_SKY_SAMPLES (128), P6_SKY_VARIANT_EST_S (660: a real04 build of about 460 s plus 6 views), P6_SKY_MIN_VARIANTS
#      (2), P6_RESERVE_S (600), P6_TESTS_RESERVE_S (900), P6_TESTS_MIN_S (300), P6_SKIP_FULL=1 (the full run is
#      done: only steps 2 and 3), P6_FULL_JOB / P6_AB_JOB (the sub-job scripts; for the CPU tests), and every
#      variable of full.sh and levers_ab.sh.
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO="${WENART_REPO:-$WS/repo}"
JOB="${JOB_ID:-m13_p6}"
LOG=$LOGS/m13_p6-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
export WENART_RESULTS="$RESULTS"
PY="${WENART_PY:-$WS/venv/bin/python}"
export WENART_OUTPUTS="$REPO/outputs"
export RUN_PROJECTS="${RUN_PROJECTS:-real04}"
SKY_AB="${P6_SKY_AB:-1}"
SKY_PROJECT="${P6_SKY_PROJECT:-real04}"
SKY_VARIANTS="${P6_SKY_VARIANTS:-sky0 sky2 sky35 sky52}"   # final pass: sky0 = the old world (base until P6c)
SKY_VIEW_SET="${P6_SKY_VIEW_SET:-sky}"          # fix round after P6a: skywin = the windows-only A/B's views
SKY_NAME="${P6_SKY_NAME:-ab_m13/sky}"
SKY_SAMPLES="${P6_SKY_SAMPLES:-128}"
EST_S="${P6_SKY_VARIANT_EST_S:-660}"
MIN_VARIANTS="${P6_SKY_MIN_VARIANTS:-2}"
RESERVE_S="${P6_RESERVE_S:-600}"
TESTS_RESERVE_S="${P6_TESTS_RESERVE_S:-900}"
TESTS_MIN_S="${P6_TESTS_MIN_S:-300}"
FULL_JOB="${P6_FULL_JOB:-scripts/jobs/full.sh}"
AB_JOB="${P6_AB_JOB:-scripts/jobs/levers_ab.sh}"
START_STAMP=$LOGS/m13_p6-$JOB.start
FAILED=()

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] m13_p6: $*"; }
now_s() { date -u +%s; }

for pair in "P6_SKY_VARIANT_EST_S=$EST_S" "P6_SKY_MIN_VARIANTS=$MIN_VARIANTS" "P6_RESERVE_S=$RESERVE_S" \
            "P6_TESTS_RESERVE_S=$TESTS_RESERVE_S" "P6_TESTS_MIN_S=$TESTS_MIN_S" "P6_SKY_SAMPLES=$SKY_SAMPLES"; do
  if ! [[ "${pair#*=}" =~ ^[0-9]+$ ]]; then log "${pair%%=*} '${pair#*=}' is not a whole number"; exit 2; fi
done
case "$SKY_VIEW_SET" in
  ''|*[!a-z0-9_]*) log "P6_SKY_VIEW_SET '$SKY_VIEW_SET' is no view set name"; exit 2 ;;
esac
case "$SKY_NAME" in
  ''|/*|*..*) log "P6_SKY_NAME '$SKY_NAME' must be a relative folder name"; exit 2 ;;
esac
case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac
FINAL_DEADLINE="${WENART_DEADLINE:-}"

# seconds_left: until the pod's WENART_DEADLINE (a huge number without one).
seconds_left() {
  if [ -n "$FINAL_DEADLINE" ]; then echo $(( ${FINAL_DEADLINE%.*} - $(now_s) )); else echo 999999; fi
}

# run_step <name> <command...>: timed, failure recorded, the job goes on.
run_step() {
  local name=$1; shift
  local t0; t0=$(now_s)
  log "step $name: start ($(seconds_left) s left before the deadline)"
  if "$@"; then
    log "step $name: ok in $(( $(now_s) - t0 )) s"
  else
    local rc=$?
    log "step $name: FAILED (exit $rc) after $(( $(now_s) - t0 )) s"
    FAILED+=("$name")
  fi
}

# in_projects <p>: <p> is one of RUN_PROJECTS (spaces or commas).
in_projects() {
  local -a list
  read -r -a list <<< "${RUN_PROJECTS//,/ }"
  local x
  for x in "${list[@]}"; do [ "$x" = "$1" ] && return 0; done
  return 1
}

# tests_ran: full.sh's GPU tests wrote junit-full.xml in this job (newer than the start stamp).
tests_ran() {
  [ -f "$RESULTS/junit-full.xml" ] && [ "$RESULTS/junit-full.xml" -nt "$START_STAMP" ]
}

# run_built <p>: this job's run manifest records a build of <p> (status ok or reused), so outputs/<p> holds the
# building and the scene this pod rendered, not an earlier pod's.
run_built() {
  [ -f "$RESULTS/run_manifest.json" ] || return 1
  "$PY" - "$RESULTS/run_manifest.json" "$1" <<'PY'
import json, sys
try:
    m = json.load(open(sys.argv[1], encoding="utf-8"))
except (OSError, ValueError):
    sys.exit(1)
for p in m.get("projects") or []:
    if p.get("name") == sys.argv[2]:
        ok = any(s.get("stage") == "build" and s.get("status") in ("ok", "reused") for s in p.get("stages") or [])
        sys.exit(0 if ok else 1)
sys.exit(1)
PY
}

# gpu_test_plan <run manifest> env|files: the test lists of this job's run (KEY=VALUE lines) or the files of the
# full group whose lists are not all empty (as the scheduler's run_tests chooses them).
gpu_test_plan() {
  "$PY" - "$1" "$2" <<'PY'
import json, sys
from wenart.run.scheduler import GPU_TEST_GROUPS, TEST_LISTS
m = json.load(open(sys.argv[1], encoding="utf-8"))
lists = {k: str(v or "") for k, v in (m.get("test_lists") or {}).items() if k in TEST_LISTS}
if sys.argv[2] == "env":
    for k in TEST_LISTS:
        print(f"{k}={lists.get(k, '')}")
else:
    for group, _attr, files in GPU_TEST_GROUPS:
        if group == "full":
            for f, keys in files:
                if any(lists.get(k) for k in keys):
                    print(f)
PY
}

# run_gpu_tests: the full group once, with the run manifest's lists (step 3's fallback).
run_gpu_tests() {
  local manifest=$RESULTS/run_manifest.json
  local -a envs=() files=()
  mapfile -t envs < <(gpu_test_plan "$manifest" env)
  mapfile -t files < <(gpu_test_plan "$manifest" files)
  if [ "${#files[@]}" -eq 0 ]; then
    log "GPU tests: every project list of $manifest is empty: nothing to run"
    return 1
  fi
  local check="${CHECK_MODELS:-qwen glm}"
  if [ "${NO_ORCHESTRATOR:-0}" != "1" ]; then check="${AGENT_MODEL:-agent}"; fi    # the scheduler's check_keys
  mkdir -p "$RESULTS/logs"
  timeout "$(( $(seconds_left) + 600 ))" env "${envs[@]}" WENART_OUTPUTS="$REPO/outputs" WENART_RESULTS="$RESULTS" \
    CHECK_MODELS="$check" "$PY" -m pytest -m gpu "${files[@]}" -v -ra --junitxml="$RESULTS/junit-full.xml" \
    > "$RESULTS/logs/pytest-full-m13_p6.log" 2>&1
}

on_exit() {
  local rc=$?
  trap - ERR
  set +e
  log "job $JOB ends with exit code $rc"
  mkdir -p "$RESULTS" && cp -f "$LOG" "$RESULTS/" 2>/dev/null
  exit "$rc"
}
trap 'log "error at line $LINENO (exit $?)"' ERR
trap 'on_exit' EXIT
trap 'exit 143' TERM

# stamp_start: the job's start stamp, 2 s back (the volume's timestamps may have 1 s steps; full.sh's stamp).
stamp_start() {
  local t
  : > "$START_STAMP" || return 1
  t=$(stat -c %Y "$START_STAMP" 2>/dev/null) || return 0
  touch -d "@$(( t - 2 ))" "$START_STAMP" 2>/dev/null || true
}
stamp_start || log "warning: no start stamp $START_STAMP: a junit-full.xml of an earlier job would count"
cd "$REPO"
mkdir -p "$RESULTS"
log "job $JOB: projects [$RUN_PROJECTS], sky A/B ${SKY_AB} on $SKY_PROJECT ($SKY_VARIANTS at $SKY_SAMPLES spp," \
    "views $SKY_VIEW_SET into $SKY_NAME," \
    "about $EST_S s per variant, at least $MIN_VARIANTS), reserve $RESERVE_S s (+$TESTS_RESERVE_S s for missing GPU" \
    "tests), deadline ${FINAL_DEADLINE:-none} ($(seconds_left) s left)"

# 1. The full run (its GPU tests at its end).
if [ "${P6_SKIP_FULL:-0}" != "1" ]; then
  run_step full bash "$FULL_JOB"
else
  log "full run skipped (P6_SKIP_FULL=1)"
fi

# 2. The interior sky A/B on this pod's output of P6_SKY_PROJECT, when time is left.
if [ "$SKY_AB" != "1" ] || ! in_projects "$SKY_PROJECT"; then
  log "sky A/B off (P6_SKY_AB=$SKY_AB, $SKY_PROJECT in [$RUN_PROJECTS]: $(in_projects "$SKY_PROJECT" && echo yes || echo no))"
else
  rd=$REPO/outputs/$SKY_PROJECT
  reserve=$RESERVE_S
  # review: a rerun with P6_SKIP_FULL=1 never runs the GPU tests here (the full-run pod ran them): no test reserve
  if [ "${P6_SKIP_FULL:-0}" != "1" ] && ! tests_ran; then reserve=$(( RESERVE_S + TESTS_RESERVE_S )); fi
  left=$(( $(seconds_left) - reserve ))
  need=$(( EST_S * MIN_VARIANTS ))
  if [ ! -f "$rd/building_final.json" ] || [ ! -f "$rd/scene/scene_manifest.json" ]; then
    log "sky A/B: no run output of $SKY_PROJECT ($rd: building_final.json, scene/scene_manifest.json)"
    FAILED+=("sky-ab-no-run-output")
  elif [ "${P6_SKIP_FULL:-0}" != "1" ] && ! run_built "$SKY_PROJECT"; then
    log "sky A/B: this job's run manifest records no build of $SKY_PROJECT: the A/B would build an earlier run's files"
    FAILED+=("sky-ab-not-built")
  elif [ "$left" -lt "$need" ]; then
    log "sky A/B skipped: $left s left after the $reserve s reserve, $need s needed ($MIN_VARIANTS x $EST_S s)"
  else
    d=""
    cap=()
    if [ -n "$FINAL_DEADLINE" ]; then
      d=$(( ${FINAL_DEADLINE%.*} - reserve ))
      # review: a hard bound too (render.py only stops starting new views at the deadline; a hung Blender would run
      # into the watchdog and leave the full run's results on the volume)
      cap=(timeout -k 60 "$(( d - $(now_s) ))")
    fi
    log "sky A/B deadline: ${d:-none} ($left s for the variants)"
    run_step sky-ab "${cap[@]}" env ${d:+WENART_DEADLINE=$d} AB_PROJECTS="$SKY_PROJECT" AB_VARIANTS="$SKY_VARIANTS" \
      AB_SAMPLES="$SKY_SAMPLES" AB_VIEW_SET="$SKY_VIEW_SET" AB_SOURCE=run AB_NAME="$SKY_NAME" \
      AB_VARIANT_EST_S="$EST_S" AB_GPU_TESTS=0 JOB_ID="$JOB" bash "$AB_JOB"
  fi
fi

# 3. One GPU test run: full.sh's, else here.
if tests_ran; then
  log "GPU tests: full.sh ran them ($RESULTS/junit-full.xml)"
elif [ "${P6_SKIP_FULL:-0}" = "1" ]; then
  log "GPU tests: run by the full-run pod (P6_SKIP_FULL=1)"
elif [ ! -f "$RESULTS/run_manifest.json" ]; then
  log "GPU tests did not run and cannot run here: no run manifest in $RESULTS (the full run stopped early);" \
      "the same command resumes the run and its tests"
  FAILED+=("gpu-tests-missing")
elif [ "$(seconds_left)" -lt "$TESTS_MIN_S" ]; then
  log "GPU tests did not run in full.sh and $(seconds_left) s are left (< $TESTS_MIN_S s): rerun the same command"
  FAILED+=("gpu-tests-missing")
else
  log "GPU tests did not run in full.sh: running the full group once with the run manifest's project lists"
  run_step gpu-tests run_gpu_tests
fi

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
