#!/usr/bin/env bash
# Profile the scene build of an earlier job on the pod (29 Oct 2026).
# Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS and JOB_ID set; Blender and
# /workspace/venv from scripts/pod_setup.sh).
#
# What: builds PROFILE_PROJECT (default real06) from the building and style of job PROFILE_JOB on the volume
# (results/furniture/<p>/building_final.json, results/renders/<p>/style.json) under cProfile ($WENART_PROFILE,
# wenart/blender/build.py profiled_main), once as the full job builds (Blender's own thread count) and, with
# PROFILE_THREADS=1 (default), once more with Blender held to the pod's CPU budget (WENART_BLENDER_THREADS, -t).
# Why: real06 run 20261029-100801-full spent 1,023 s a build in the furniture phase (3.9 min builds the day before,
# 4 s on a CPU without the library models); the library models live on the volume only.
# How: outputs go to the container disk ($FAST/profile/<run>); the build logs, scene manifests and the profiles
# (stats and text) go to $WENART_RESULTS/profile/<run>/. Nothing on the volume is changed. Idempotent.
#
# Usage: python3 scripts/gpu_run.py run --job scripts/jobs/profile_build.sh --max-minutes 60 \
#          --env PROFILE_JOB=<job id> --purpose "profile the build of job <job id>"
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
JOB="${JOB_ID:-profile_build}"
mkdir -p "$LOGS"
LOG=$LOGS/profile_build-$JOB.log
exec > >(tee -a "$LOG") 2>&1
trap 'echo "[$(date -u +%H:%M:%S)] profile_build: error at line $LINENO (exit $?)"' ERR

SRC_JOB="${PROFILE_JOB:-}"
P="${PROFILE_PROJECT:-real06}"
RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
FAST="${WENART_FAST:-/opt/wenart}"
PY="${WENART_PY:-$WS/venv/bin/python}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
CGROUP=/sys/fs/cgroup
if [ -z "$SRC_JOB" ]; then echo "profile_build: PROFILE_JOB=<job id> is required"; exit 2; fi
case "$SRC_JOB$P" in */*|*..*) echo "profile_build: bad job id or project"; exit 2;; esac
SRC=$WS/jobs/$SRC_JOB/results
BUILDING=$SRC/furniture/$P/building_final.json
STYLE=$SRC/renders/$P/style.json
[ -f "$STYLE" ] || STYLE=$SRC/furniture/$P/style.json
for f in "$BUILDING" "$STYLE"; do
  if [ ! -f "$f" ]; then echo "profile_build: missing $f on the volume"; exit 3; fi
done

# the pod's CPU budget (cgroup quota, as full.sh cpu_budget)
budget() {
  local n quota="" period=""
  n=$(env -u OMP_NUM_THREADS -u OMP_THREAD_LIMIT nproc 2>/dev/null) || n=1
  if [ -r "$CGROUP/cpu.max" ]; then read -r quota period < "$CGROUP/cpu.max" || true; fi
  if [[ "$quota" =~ ^[0-9]+$ ]] && [[ "$period" =~ ^[0-9]+$ ]] && [ "$period" -gt 0 ]; then
    local q=$(( (quota + period - 1) / period ))
    if [ "$q" -lt "$n" ]; then n=$q; fi
  fi
  echo "$n"
}
N=$(budget)
export WENART_CPU_THREADS=$N OMP_NUM_THREADS=$N OPENBLAS_NUM_THREADS=$N MKL_NUM_THREADS=$N \
  NUMEXPR_NUM_THREADS=$N VECLIB_MAXIMUM_THREADS=$N OPENCV_FOR_THREADS_NUM=$N
echo "[$(date -u +%H:%M:%S)] profile_build: $P of $SRC_JOB; CPU budget $N (cpu.max '$(cat $CGROUP/cpu.max 2>/dev/null)'," \
     "nproc $(nproc --all 2>/dev/null))"

one_build() {   # one_build <run name> [blender threads]
  local run=$1 threads=${2:-} out=$FAST/profile/$1 dst=$RESULTS/profile/$1 rc=0
  rm -rf "$out"; mkdir -p "$out" "$dst"
  local t0; t0=$(date +%s)
  echo "[$(date -u +%H:%M:%S)] profile_build: build $run (blender threads: ${threads:-Blender default})"
  WENART_PROFILE="$dst/build.prof" WENART_BLENDER_THREADS="$threads" "$PY" -m wenart.blender.cli build \
    --building "$BUILDING" --style "$STYLE" --assets "$WS/assets" --out "$out/scene" --preview-samples 32 \
    --camera-policy search --brief "projects/$P" > "$dst/cli.log" 2>&1 || rc=$?
  echo "[$(date -u +%H:%M:%S)] profile_build: build $run rc $rc in $(( $(date +%s) - t0 )) s"
  for f in build.log scene_manifest.json; do
    if [ -f "$out/scene/$f" ]; then cp -f "$out/scene/$f" "$dst/"; fi
  done
  grep -h "BUILD_PHASES\|BUILD_DONE" "$dst/build.log" 2>/dev/null | cut -c1-3000 || true
}

one_build default
if [ "${PROFILE_THREADS:-1}" = "1" ]; then one_build threads "$N"; fi
echo "[$(date -u +%H:%M:%S)] profile_build: done; $(find "$RESULTS" -type f | wc -l) files in $RESULTS"
