#!/usr/bin/env bash
# Milestone 7 prep job (docs/milestone7.md §9.2, §10): what the M7 full runs need before they start. Run by
# scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE
# set; /workspace/venv has the CPU deps; Blender at /workspace/tools/blender/blender). The bash parts follow
# scripts/jobs/full.sh (traps, tee log, exports, cgroup thread budget, setup, EXIT trap); `python -m
# wenart.run.prep` does the rest in a fixed order: Objaverse survey (the last download), thumbnails, detector
# calibration on the M6 outputs, GPU timings, the prep projects' pipelines, the Qwen and GLM sessions
# (8-sequence probe, recognition answers, library judging), pipeline_final, the library catalogue, the copy and
# the GPU tests (wenart/run/prep.py).
#
#   scripts/gpu_run.py run --job scripts/jobs/prep.sh --gpu 'RTX PRO 6000' --disk 150 --max-minutes 90 \
#     --grace 600 --purpose "M7 prep pod: recognition answers, Objaverse library, detector calibration, timings"
#
# (§10: RTX PRO 6000, 96 GB, $2.09/h -> worst case $3.14; never L4. --disk 150: the VLMs, the polish/gate/OWLv2
# models, the Objaverse candidates, venv-vllm, venv-polish and the LibreDWG build live on the container disk.)
# --max-minutes 90 gives WENART_DEADLINE = entry + 75 min; a cut pod exits 1 and the same command resumes
# (answers, thumbnail measurements, detector boxes and timing renders are reused from the volume).
#
# Env (all optional):
#   PREP_PROJECTS   prep projects (default "real01 synthetic-02 synthetic-06 real01-scan real01-photo")
#   PREP_SKIP       steps to leave out, comma separated; PREP_ONLY: only these (python -m wenart.run.prep --help)
#   CHECK_MODELS    check.yaml model keys of the setup (default "qwen glm")
#   RENDER_SAMPLES  Cycles samples of the timing renders (default 128)
#   RUN_THREADS     CPU threads per process (default: the pod's cgroup CPU quota, see cpu_budget)
#
# Results ($RESULTS, collected by the runner): prep_manifest.json, setup_polish.json, library/, detect/,
# timing/gpu_speed.json, recognition/<p>/, furniture/<p>/, tests/, and this job's logs (tails) in logs/. The
# pipeline outputs stay in /workspace/outputs-prep, the persistent work in /workspace/prep (both outside the repo:
# pod_entry.sh's git clean never touches them).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"           # WENART_WS / WENART_FAST: CPU tests only
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-prep}"
LOG=$LOGS/prep-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
FAST="${WENART_FAST:-/opt/wenart}"     # container disk (see pod_setup_polish.sh)
PY="${WENART_PY:-$WS/venv/bin/python}"
POLISH_PY="${WENART_POLISH_PY:-$FAST/venv-polish/bin/python}"
PREP_OUTPUTS="${WENART_PREP_OUTPUTS:-$WS/outputs-prep}"
PREP_ROOT="${WENART_PREP_ROOT:-$WS/prep}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export WENART_OUTPUTS="$REPO/outputs"   # the M6 outputs on the volume (detector calibration, timings)
export CHECK_MODELS="${CHECK_MODELS:-qwen glm}"
export RENDER_SAMPLES="${RENDER_SAMPLES:-128}"
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_ASSETS="$ASSETS" WENART_FAST="$FAST" \
  WENART_POLISH_PY="$POLISH_PY" WENART_LOGS="$LOGS" WENART_PREP_OUTPUTS="$PREP_OUTPUTS" WENART_PREP_ROOT="$PREP_ROOT"
CGROUP="${WENART_CGROUP:-/sys/fs/cgroup}"   # CPU tests only
PID_FILE=$JOB_DIR/vllm.pid
START_STAMP=$LOGS/prep-$JOB.start     # files older than this were written by earlier jobs

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] prep: $*"; }

case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

# The prep's arguments (lists are passed through: spaces or commas).
PREP_ARGS=(--results "$RESULTS" --outputs "$PREP_OUTPUTS" --prep-root "$PREP_ROOT")
if [ -n "${PREP_PROJECTS:-}" ]; then PREP_ARGS+=(--projects "$PREP_PROJECTS"); fi
if [ -n "${PREP_SKIP:-}" ]; then PREP_ARGS+=(--skip "$PREP_SKIP"); fi
if [ -n "${PREP_ONLY:-}" ]; then PREP_ARGS+=(--only "$PREP_ONLY"); fi

# stamp <file>: an empty file whose mtime is the volume's own time minus 2 s (full.sh).
stamp() {
  local t
  rm -f "$1" 2>/dev/null || true
  : > "$1" || return 1
  t=$(stat -c %Y "$1" 2>/dev/null) || return 0
  touch -d "@$(( t - 2 ))" "$1" 2>/dev/null || true
}

# copy_job_logs: this job's vLLM, setup, download and LibreDWG logs (tail 200) and the prep's step logs (tail 400)
# into $RESULTS/logs; /workspace/logs keeps every earlier pod's, so only files newer than START_STAMP.
copy_job_logs() {
  local dest="$RESULTS/logs" f
  mkdir -p "$dest" 2>/dev/null || return 0
  for f in "$LOGS"/vllm-*.log "$LOGS"/setup-polish-*.log "$LOGS"/hf-download-*.log "$LOGS"/libredwg-*.log; do
    if [ -f "$f" ] && [ "$f" -nt "$START_STAMP" ]; then
      tail -n 200 "$f" > "$dest/$(basename "$f")" 2>/dev/null || true
    fi
  done
  if [ -d "$LOGS/prep-$JOB" ]; then
    mkdir -p "$dest/prep" 2>/dev/null || true
    for f in "$LOGS/prep-$JOB"/*.log; do
      if [ -f "$f" ]; then tail -n 400 "$f" > "$dest/prep/$(basename "$f")" 2>/dev/null || true; fi
    done
  fi
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
}

# cpu_budget: the CPUs this pod may use (full.sh): its cgroup CPU quota rounded up, at most nproc, at least 1.
cpu_budget() {
  local n quota="" period=""
  n=$(env -u OMP_NUM_THREADS -u OMP_THREAD_LIMIT nproc 2>/dev/null) || n=1
  if [ -r "$CGROUP/cpu.max" ]; then
    read -r quota period < "$CGROUP/cpu.max" || true
  elif [ -r "$CGROUP/cpu/cpu.cfs_quota_us" ] && [ -r "$CGROUP/cpu/cpu.cfs_period_us" ]; then
    quota=$(cat "$CGROUP/cpu/cpu.cfs_quota_us" 2>/dev/null) || quota=""
    period=$(cat "$CGROUP/cpu/cpu.cfs_period_us" 2>/dev/null) || period=""
  fi
  if [[ "$quota" =~ ^[0-9]+$ ]] && [[ "$period" =~ ^[0-9]+$ ]] && [ "$quota" -gt 0 ] && [ "$period" -gt 0 ]; then
    local q=$(( (quota + period - 1) / period ))
    if [ "$q" -lt "$n" ]; then n=$q; fi
  fi
  if ! [[ "$n" =~ ^[0-9]+$ ]] || [ "$n" -lt 1 ]; then n=1; fi
  echo "$n"
}

# set_threads: export the thread budget (RUN_THREADS, else cpu_budget) to every step (full.sh).
set_threads() {
  local n="${RUN_THREADS:-}" src="RUN_THREADS"
  if ! [[ "$n" =~ ^[1-9][0-9]*$ ]]; then
    if [ -n "$n" ]; then log "RUN_THREADS '$n' is not a positive number: ignored"; fi
    n=$(cpu_budget); src="cgroup CPU quota / nproc"
  fi
  export WENART_CPU_THREADS=$n OMP_NUM_THREADS=$n OPENBLAS_NUM_THREADS=$n MKL_NUM_THREADS=$n \
    NUMEXPR_NUM_THREADS=$n VECLIB_MAXIMUM_THREADS=$n OPENCV_FOR_THREADS_NUM=$n
  log "CPU budget: $n thread(s) per process (from $src): OMP/OPENBLAS/MKL/NUMEXPR/VECLIB/OPENCV_FOR_THREADS_NUM=$n"
}

# alive <pid>: the process runs (a zombie nobody has reaped yet counts as gone).
alive() {
  local st
  kill -0 "$1" 2>/dev/null || return 1
  st=$(ps -o stat= -p "$1" 2>/dev/null) || return 0
  st=${st//[[:space:]]/}
  [[ "$st" != Z* ]]
}

# kill_vllm: a vLLM server the prep left behind (it died before its own stop): TERM to its process group, wait
# 60 s, KILL (full.sh).
kill_vllm() {
  local pid
  [ -f "$PID_FILE" ] || return 0
  pid=$(cat "$PID_FILE" 2>/dev/null) || pid=""
  if [[ "$pid" =~ ^[0-9]+$ ]] && alive "$pid"; then
    log "stopping vllm (pid $pid) left by the prep"
    kill -TERM -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    for _ in $(seq 1 30); do alive "$pid" || break; sleep 2; done
    if alive "$pid"; then kill -KILL -- "-$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true; fi
  fi
  rm -f "$PID_FILE"
}

on_error() { log "ERROR at line $1: $2"; exit 1; }
trap 'on_error $LINENO "$BASH_COMMAND"' ERR
on_exit() {
  local rc=$?
  trap - ERR
  set +e
  kill_vllm
  # The prep projects' answers and files once more (the prep may have died before its own copy step).
  "$PY" -m wenart.run.prep "${PREP_ARGS[@]}" --copy-only || log "results copy failed (rc $?)"
  copy_job_logs
  log "job $JOB ends with exit code $rc"
  exit "$rc"
}
trap 'on_exit' EXIT
trap 'exit 143' TERM

stamp "$START_STAMP" || log "warning: no start stamp $START_STAMP: earlier jobs' logs may be copied"
cd "$REPO"
mkdir -p "$RESULTS" "$ASSETS" "$JOB_DIR" "$PREP_OUTPUTS" "$PREP_ROOT"
log "job $JOB: projects [${PREP_PROJECTS:-default}], skip [${PREP_SKIP:-}], only [${PREP_ONLY:-}]," \
    "samples $RENDER_SAMPLES, check models $CHECK_MODELS, deadline ${WENART_DEADLINE:-none}"
set_threads
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

# Setup: venv-polish, the polish + gate models and the OWLv2 detector (part models), vLLM + Qwen + GLM and
# LibreDWG 0.14 (part check: the recognition setup's parts 'vllm libredwg models', M7 §5.1). Every Hugging Face
# download of the setup happens here, before the offline switch.
setup_rc=0
POLISH_RECOG_PARTS="vllm libredwg models" POLISH_MODE=final \
  POLISH_PHASES="polish gate check tests" bash scripts/pod_setup_polish.sh || setup_rc=$?
if [ "$setup_rc" -ne 0 ]; then
  log "warning: pod_setup_polish.sh exit $setup_rc (see setup_polish.json): the steps that need a missing part fail"
fi
# The prep's first step, the Objaverse survey, is the last download (M7 §7.1, into $HF_HOME); wenart.run.prep
# runs every step after it with HF_HUB_OFFLINE=1.
export HF_HUB_OFFLINE=0

rc=0
"$PY" -m wenart.run.prep "${PREP_ARGS[@]}" || rc=$?
log "prep exit $rc"
exit "$rc"
