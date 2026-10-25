#!/usr/bin/env bash
# Milestone 6/7 job: one-command full project run (docs/milestone6.md §2.4, docs/milestone7.md §9). Run by
# scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE
# set; /workspace/venv has the CPU deps; Blender at /workspace/tools/blender/blender). This script keeps the
# proven bash parts of scripts/jobs/polish.sh (traps, tee log, exports, cgroup thread budget, setup, HF offline,
# flock copy loop, EXIT trap); the orchestrator `python -m wenart.run pod` does the rest: stages 0-20 of every
# project batched by GPU holder, the vLLM server sessions (pid in $WENART_JOB_DIR/vllm.pid), the deadline,
# needs_review, the fingerprints, the realism A/B, the GPU tests and the run manifests (wenart/run/scheduler.py).
#
#   scripts/gpu_run.py run --job scripts/jobs/full.sh --gpu 'RTX PRO 6000' --disk 150 --max-minutes 115 \
#     --grace 600 --env RUN_PROJECTS='real01 synthetic-01 synthetic-04' --purpose "M7 pod B: full run"
#
# (M7 §9.5, §10: the RTX PRO 6000, 96 GB, is GPU_PRIORITY[0] of scripts/gpu_run.py; without stock the runner's
# order applies (--gpu left out), never L4. --disk 150: the VLMs, the polish/gate/OWLv2 models, venv-vllm,
# venv-polish and the LibreDWG build live on the container disk.) --max-minutes 115 gives WENART_DEADLINE =
# entry + 100 min; a pod that the deadline cuts exits 1 and the same command resumes from the volume (stage
# fingerprints, render keys, polish attempts, recognition and check answers). Run the prep job
# (scripts/jobs/prep.sh, M7 §9.2) first: it measures GPU_SPEED and max_seqs and builds the Objaverse library.
#
# Env (one of RUN_PROJECTS, PRIVATE_PROJECTS, AB_PROJECTS required; PRIVATE_SELFTEST=1 alone also runs):
#   RUN_PROJECTS        public projects, e.g. "synthetic-01 synthetic-03"
#   PRIVATE_PROJECTS    private aliases uploaded to /workspace/projects-private/<alias> (docs/intake.md)
#   PRIVATE_SELFTEST=1  adds selftest-02 (tests/fixtures/projects/review-01 copied to /workspace/projects-private;
#                       a stale copy, e.g. the M6 synthetic-02 one, is moved to /workspace/outputs-archive first)
#   AB_PROJECTS         realism A/B projects (§6.3), AB_CONTROL_PROJECT the one with the control sets,
#   AB_PHASE            all (default) | render | judge
#   RUN_FORCE           stages whose fingerprint is ignored, comma separated (e.g. photos,layout)
#   RUN_POLISH=off      Milestone 11 (pod G2): no gate and polish for any project of this run (WENART_POLISH)
#   RUN_VEGETATION_SETUP=0  Milestone 13: skip scripts/pod_setup_vegetation.sh (Sapling extension, tree models, leaf
#                       atlases; default: run it, idempotent, about a minute)
#   DRIVE_UPLOAD=1      set by gpu_run.py --drive-upload: the 3D files of RUN_PROJECTS to Google Drive (RCLONE_CONF)
#   RENDER_SAMPLES      Cycles samples (default 128)
#   CHECK_MODELS        check.yaml model keys (default "qwen glm"; recognition, layout and --no-orchestrator checks)
#   NO_ORCHESTRATOR=1   Milestone 11: the M10 chain (`pod --no-orchestrator`); default: the AI orchestrator
#                       (docs/milestone11.md §8: agent rounds, the agent model's one-pass check; its model is
#                       downloaded by the setup, AGENT_MODELS)
#   AGENT_MODEL         agent (default, Qwen/Qwen3.8-27B-FP8) | agent_fast (Qwen/Qwen3.6-35B-A3B-FP8)
#   AGENT_ROUNDS        max orchestrator rounds (default 3 since Milestone 13 K4, docs/milestone13.md §3.0; the
#                       time budget still stops earlier)
#   CAMERAS_FROM        Milestone 13 (K8): a scene_manifest.json whose cameras the build replays, {name} = the
#                       project (e.g. results/renders/{name}/scene_manifest.json for P4); default $WENART_CAMERAS_FROM
#                       (build.py reads that variable itself, so either way works)
#   CAMERAS_EXTRA=1     with CAMERAS_FROM also search every room and add those cameras (default $WENART_CAMERAS_EXTRA)
#   WHITE_BALANCE       Milestone 13 (K5): project (one whitepoint per project) | kelvin:K; default: the brief's
#                       render.white_balance_k, else project
#   RUN_FRESH_RECOGNITION  fix round after P3 (part 2, 17 Oct 2026, pod P5): project ids (spaces or commas) whose
#                       stored AI answers must be asked again (real04's L0 answers were given on the wrong crops: the
#                       second plan region r16 wrote its crops over r5's of the same key). Before the run, the
#                       project's recognition/answers*.json and sheets/answers*.json (under $WENART_OUTPUTS/<p>, or
#                       /workspace/outputs-private/<p>) are MOVED, never deleted, to <p>/recognition/set_aside_<UTC
#                       stamp>/ (the sheets ones to its sheets/), with a log line; requests.json and the crops stay.
#                       Idempotent: done once per id (the ledger /workspace/logs/fresh_recognition.log lists each
#                       set-aside), so the resumed command keeps the answers asked since; "<p>:<tag>" sets them
#                       aside again once per new tag. Committed seeds (results/recognition/<p>/) are not touched: a
#                       warning names them (the recognition step copies a seed back when its key and input hash
#                       match). A failed move stops the job before the setup (the run would use the stale answers).
#   WENART_AGENT_SLEEP  on | off | auto (default: the agent server sleeps for the gate and polish below 80 GB)
#   RUN_THREADS         CPU threads per process (default: the pod's cgroup CPU quota, see cpu_budget)
#   RESTORE_OUTPUTS=1   25 Oct 2026: move the pipeline outputs a failed pod set aside ($WS/.repo-broken-*/outputs/<p>)
#                       back into $WENART_OUTPUTS before the run (a move, never a delete; see the step below)
#   WENART_ARCHITECT_AI=0  25 Oct 2026: skip the AI architect's answers to the open questions (agent phase)
#
# Results: the background loop (every 300 s, under flock) and the EXIT trap run `python -m wenart.run copy`
# (small files only, into the committed layout $RESULTS/<area>/<p>/; private projects: an allow-list into
# /workspace/results-private/<alias>/, linked as $JOB_DIR/results-private/<alias>); the copy prints only file
# counts. This job's vLLM and setup logs (tail 200) go to $RESULTS/logs/, or to
# $JOB_DIR/results-private/_logs/ when a private project is in the run (a vLLM log can hold prompts).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"           # WENART_WS / WENART_FAST: CPU tests only
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-full}"
LOG=$LOGS/full-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
ASSETS="${WENART_ASSETS:-$WS/assets}"
FAST="${WENART_FAST:-/opt/wenart}"     # container disk (see pod_setup_polish.sh)
PY="${WENART_PY:-$WS/venv/bin/python}"
POLISH_PY="${WENART_POLISH_PY:-$FAST/venv-polish/bin/python}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export WENART_OUTPUTS="$REPO/outputs"
export CHECK_MODELS="${CHECK_MODELS:-qwen glm}"
export RENDER_SAMPLES="${RENDER_SAMPLES:-128}"
# Milestone 13 (docs/milestone13.md §13.3): the licence mode of the fit; unset = the project brief (relaxed for real02/03/04) or defaults.yaml
if [ -n "${WENART_LICENCE_MODE:-}" ]; then export WENART_LICENCE_MODE; fi
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_ASSETS="$ASSETS" WENART_FAST="$FAST" \
  WENART_POLISH_PY="$POLISH_PY" WENART_LOGS="$LOGS"
RUN_PROJECTS="${RUN_PROJECTS:-}" PRIVATE_PROJECTS="${PRIVATE_PROJECTS:-}" AB_PROJECTS="${AB_PROJECTS:-}"
RUN_FRESH_RECOGNITION="${RUN_FRESH_RECOGNITION:-}"
AB_PHASE="${AB_PHASE:-all}"
COPY_EVERY_S="${RUN_COPY_EVERY_S:-300}"
LOCK=$LOGS/full-$JOB.copy.lock
export WENART_COPY_LOCK="$LOCK"       # the orchestrator's own copy before the GPU tests takes the same lock
START_STAMP=$LOGS/full-$JOB.start     # files older than this were written by earlier jobs
COPY_STAMP=$LOGS/full-$JOB.copied     # renewed by `wenart.run copy --since` after every finished copy
COPY_OVERLAP_S=2                      # stamps lie 2 s back: the volume's timestamps may have 1 s steps
CGROUP="${WENART_CGROUP:-/sys/fs/cgroup}"   # CPU tests only
PID_FILE=$JOB_DIR/vllm.pid
COPY_PID=""

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] full: $*"; }

# private_run: true when a private project is in the run (logs then never go to $RESULTS).
private_run() {
  [ -n "${PRIVATE_PROJECTS//[[:space:],]/}" ] || [ "${PRIVATE_SELFTEST:-0}" = "1" ]
}

if [ -z "${RUN_PROJECTS//[[:space:],]/}" ] && [ -z "${PRIVATE_PROJECTS//[[:space:],]/}" ] \
    && [ -z "${AB_PROJECTS//[[:space:],]/}" ] && [ "${PRIVATE_SELFTEST:-0}" != "1" ]; then
  log "nothing to run: set RUN_PROJECTS, PRIVATE_PROJECTS or AB_PROJECTS (or PRIVATE_SELFTEST=1)"
  exit 2
fi
case "$AB_PHASE" in
  all|render|judge) ;;
  *) log "unknown AB_PHASE '$AB_PHASE' (all|render|judge)"; exit 2 ;;
esac
case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

# The orchestrator's and the copy's arguments (lists are passed through: spaces or commas).
POD_ARGS=(--results "$RESULTS" --profile full)
COPY_ARGS=(--results "$RESULTS")
if [ -n "${RUN_PROJECTS:-}" ]; then POD_ARGS+=(--projects "$RUN_PROJECTS"); COPY_ARGS+=(--projects "$RUN_PROJECTS"); fi
if [ -n "${PRIVATE_PROJECTS:-}" ]; then
  POD_ARGS+=(--private "$PRIVATE_PROJECTS"); COPY_ARGS+=(--private "$PRIVATE_PROJECTS")
fi
if [ "${PRIVATE_SELFTEST:-0}" = "1" ]; then POD_ARGS+=(--private-selftest); COPY_ARGS+=(--private-selftest); fi
if [ -n "${AB_PROJECTS:-}" ]; then
  POD_ARGS+=(--ab "$AB_PROJECTS" --ab-phase "$AB_PHASE"); AB_COPY="$AB_PROJECTS"
  # the control project may be outside AB_PROJECTS (M7 §8.2): copy its A/B files too, once
  case " $AB_PROJECTS " in *" ${AB_CONTROL_PROJECT:-} "*) ;; *) AB_COPY="$AB_PROJECTS $AB_CONTROL_PROJECT" ;; esac
  COPY_ARGS+=(--ab "$AB_COPY")
  if [ -n "${AB_CONTROL_PROJECT:-}" ]; then POD_ARGS+=(--ab-controls "$AB_CONTROL_PROJECT"); fi
fi
if [ -n "${RUN_FORCE:-}" ]; then POD_ARGS+=(--force "$RUN_FORCE"); fi
if [ "${RUN_POLISH:-on}" = "off" ]; then export WENART_POLISH=off; fi
# Milestone 11: orchestrated by default (the CLI's default); the agent model is downloaded with the VLMs.
AGENT_SETUP="${AGENT_MODEL:-agent}"
if [ "${NO_ORCHESTRATOR:-0}" = "1" ]; then POD_ARGS+=(--no-orchestrator); AGENT_SETUP=""; fi
if [ -n "${AGENT_MODEL:-}" ]; then POD_ARGS+=(--agent-model "$AGENT_MODEL"); fi
# 11 Oct 2026 (user: pods get more time): more orchestrator rounds when the pod has the time; Milestone 13 (K4,
# the user's rule of 12 Oct 2026): the default is 3 (python -m wenart.run pod --agent-rounds)
if [ -n "${AGENT_ROUNDS:-}" ]; then POD_ARGS+=(--agent-rounds "$AGENT_ROUNDS"); fi
# Milestone 13 (K8, K5): the camera replay and the white balance as pod flags; the environment variables
# WENART_CAMERAS_FROM / WENART_CAMERAS_EXTRA keep working (build.py reads them when the flags are absent).
CAMERAS_FROM="${CAMERAS_FROM:-${WENART_CAMERAS_FROM:-}}"
if [ -n "$CAMERAS_FROM" ]; then POD_ARGS+=(--cameras-from "$CAMERAS_FROM"); fi
case "${CAMERAS_EXTRA:-${WENART_CAMERAS_EXTRA:-}}" in 1|true|yes|on) POD_ARGS+=(--cameras-extra) ;; esac
if [ -n "${WHITE_BALANCE:-}" ]; then POD_ARGS+=(--white-balance "$WHITE_BALANCE"); fi

# stamp <file>: an empty file whose mtime is the volume's own time minus COPY_OVERLAP_S, so a file
# written in the same second as the stamp still counts as newer (polish.sh).
stamp() {
  local t
  rm -f "$1" 2>/dev/null || true
  : > "$1" || return 1
  t=$(stat -c %Y "$1" 2>/dev/null) || return 0
  touch -d "@$(( t - COPY_OVERLAP_S ))" "$1" 2>/dev/null || true
}

# copy_results [full]: `wenart.run copy` of the files changed since the last finished copy (all of them for
# 'full' and for the job's first copy: the stamp is removed at the start).
copy_results() {
  local -a since=()
  if [ "${1:-}" != "full" ]; then since=(--since "$COPY_STAMP"); fi
  "$PY" -m wenart.run copy "${COPY_ARGS[@]}" "${since[@]}" || log "results copy failed (rc $?)"
}

# copy_results_locked [wait_s] [full]: one copy at a time (the background loop, the EXIT trap).
copy_results_locked() {
  if command -v flock >/dev/null 2>&1; then
    ( flock -w "${1:-120}" 9 || { log "results copy busy, skipped"; exit 0; }; copy_results "${2:-}" ) 9>"$LOCK"
  else
    copy_results "${2:-}"
  fi
}

copy_loop() {
  trap - ERR
  set +e
  while true; do
    sleep "$COPY_EVERY_S" </dev/null >/dev/null 2>&1
    copy_results_locked 60
  done
}

# copy_job_logs: this job's vLLM, setup and download logs (tail 200) and its own log; /workspace/logs keeps
# every earlier pod's, so only files newer than START_STAMP.
copy_job_logs() {
  local dest="$RESULTS/logs" f
  if private_run; then dest="$JOB_DIR/results-private/_logs"; fi
  mkdir -p "$dest" 2>/dev/null || return 0
  for f in "$LOGS"/vllm-*.log "$LOGS"/setup-polish-*.log "$LOGS"/hf-download-*.log; do
    if [ -f "$f" ] && [ "$f" -nt "$START_STAMP" ]; then
      tail -n 200 "$f" > "$dest/$(basename "$f")" 2>/dev/null || true
    fi
  done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
}

# cpu_budget: the CPUs this pod may use: its cgroup CPU quota (v2 cpu.max '<quota> <period>' or
# 'max ...'; v1 cpu/cpu.cfs_quota_us and cpu.cfs_period_us, -1 = none) rounded up, at most the CPUs
# this process may run on (nproc, without the OMP_* variables nproc honours), at least 1. Run 0b:
# os.cpu_count() saw the host's 112 CPUs; numpy/OpenBLAS, OpenCV and torch each started that many
# threads under a much smaller quota and the gate's CPU work ran 10-50x slower (polish.sh).
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

# set_threads: export the thread budget (RUN_THREADS, else cpu_budget) to every stage: OpenMP (torch
# intra-op, libgomp), OpenBLAS (numpy), MKL (torch on x86), numexpr, Accelerate, and OpenCV
# (OPENCV_FOR_THREADS_NUM; opencv-python-headless ignores OMP_NUM_THREADS). WENART_CPU_THREADS goes into
# setup_polish.json.
set_threads() {
  local n="${RUN_THREADS:-}" src="RUN_THREADS" quota="none"
  if ! [[ "$n" =~ ^[1-9][0-9]*$ ]]; then
    if [ -n "$n" ]; then log "RUN_THREADS '$n' is not a positive number: ignored"; fi
    n=$(cpu_budget); src="cgroup CPU quota / nproc"
  fi
  if [ -r "$CGROUP/cpu.max" ]; then quota="cpu.max '$(cat "$CGROUP/cpu.max" 2>/dev/null)'"
  elif [ -r "$CGROUP/cpu/cpu.cfs_quota_us" ]; then
    quota="cfs_quota_us $(cat "$CGROUP/cpu/cpu.cfs_quota_us" 2>/dev/null)"
    quota+=" / cfs_period_us $(cat "$CGROUP/cpu/cpu.cfs_period_us" 2>/dev/null)"
  fi
  local cpus; cpus=$(env -u OMP_NUM_THREADS -u OMP_THREAD_LIMIT nproc 2>/dev/null) || cpus="?"
  export WENART_CPU_THREADS=$n OMP_NUM_THREADS=$n OPENBLAS_NUM_THREADS=$n MKL_NUM_THREADS=$n \
    NUMEXPR_NUM_THREADS=$n VECLIB_MAXIMUM_THREADS=$n OPENCV_FOR_THREADS_NUM=$n
  log "CPU budget: $n thread(s) per process (from $src; $quota; nproc $cpus," \
      "host $(nproc --all 2>/dev/null || echo ?)): OMP/OPENBLAS/MKL/NUMEXPR/VECLIB/OPENCV_FOR_THREADS_NUM=$n"
}

# alive <pid>: the process runs (a zombie nobody has reaped yet counts as gone).
alive() {
  local st
  kill -0 "$1" 2>/dev/null || return 1
  st=$(ps -o stat= -p "$1" 2>/dev/null) || return 0
  st=${st//[[:space:]]/}
  [[ "$st" != Z* ]]
}

# kill_vllm: a vLLM server the orchestrator left behind (it died before its own stop): TERM to its process
# group (vLLM starts engine children; the orchestrator starts it in its own session), wait 60 s, KILL.
kill_vllm() {
  local pid
  [ -f "$PID_FILE" ] || return 0
  pid=$(cat "$PID_FILE" 2>/dev/null) || pid=""
  if [[ "$pid" =~ ^[0-9]+$ ]] && alive "$pid"; then
    log "stopping vllm (pid $pid) left by the orchestrator"
    kill -TERM -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    for _ in $(seq 1 30); do alive "$pid" || break; sleep 2; done
    if alive "$pid"; then kill -KILL -- "-$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true; fi
  fi
  rm -f "$PID_FILE"
}

# set_aside_answers <p>[:<tag>]: fix round after P3 (part 2, 17 Oct 2026, RUN_FRESH_RECOGNITION): move (never delete)
# the stored AI answers of project <p> (recognition/answers*.json, sheets/answers*.json) to
# <p>/recognition/set_aside_<UTC stamp>/ (the sheets ones to its sheets/), so the run asks those questions again.
# Once per <p> and <tag> (default "fresh"): the ledger $LOGS/fresh_recognition.log gets "<p> <tag> <stamp> <folder>
# <recognition files>+<sheets files>" per set-aside, also when there was nothing to move (folder "-"; a resumed run
# keeps what the first one asked). Nothing is created in an out_dir that has no answers (the orchestrator moves an
# out_dir without run/ to the archive, a marker there would go with it). An id that names no project is logged and
# skipped; returns 1 when a move or the ledger line fails.
set_aside_answers() {
  local entry="$1" p tag="fresh" out rec done_line="" stamp dest folder="-" n=1 f
  local ledger="$LOGS/fresh_recognition.log"
  local -a found=() sheets=()
  p="${entry%%:*}"
  if [[ "$entry" == *:* ]]; then tag="${entry#*:}"; fi
  if ! [[ "$p" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || ! [[ "$tag" =~ ^[A-Za-z0-9._-]+$ ]]; then
    log "RUN_FRESH_RECOGNITION: '$entry' is no project id[:tag]: skipped"
    return 0
  fi
  out="$WENART_OUTPUTS/$p"
  if [ ! -d "$out" ] && [ -d "$WS/outputs-private/$p" ]; then out="$WS/outputs-private/$p"; fi
  if [ ! -d "$out" ] && [ ! -d "$REPO/projects/$p" ] && [ ! -d "$WS/projects-private/$p" ]; then
    log "RUN_FRESH_RECOGNITION: no project '$p' (no outputs, no project folder): skipped"
    return 0
  fi
  if [ -f "$ledger" ]; then
    done_line=$(awk -v p="$p" -v t="$tag" '$1 == p && $2 == t { print; exit }' "$ledger") || done_line=""
  fi
  if [ -n "$done_line" ]; then
    log "$p: the stored answers were set aside for '$tag' before (${done_line#"$p $tag "}): the answers asked" \
        "since are kept"
    return 0
  fi
  rec="$out/recognition"
  for f in "$rec"/answers*.json; do if [ -f "$f" ]; then found+=("$f"); fi; done
  for f in "$out/sheets"/answers*.json; do if [ -f "$f" ]; then sheets+=("$f"); fi; done
  stamp=$(date -u +%Y%m%dT%H%M%SZ) || return 1
  if [ "${#found[@]}" -gt 0 ] || [ "${#sheets[@]}" -gt 0 ]; then
    dest="$rec/set_aside_$stamp"
    while [ -e "$dest" ]; do n=$((n + 1)); dest="$rec/set_aside_${stamp}_$n"; done
    mkdir -p "$dest" || return 1
    if [ "${#found[@]}" -gt 0 ]; then mv -- "${found[@]}" "$dest/" || return 1; fi
    if [ "${#sheets[@]}" -gt 0 ]; then
      { mkdir -p "$dest/sheets" && mv -- "${sheets[@]}" "$dest/sheets/"; } || return 1
    fi
    folder="recognition/${dest##*/}"
    log "$p: ${#found[@]} recognition and ${#sheets[@]} sheets answer file(s) moved to $folder/" \
        "(RUN_FRESH_RECOGNITION '$tag'): their questions are asked again"
  else
    log "$p: no stored answers to set aside (RUN_FRESH_RECOGNITION '$tag')"
  fi
  echo "$p $tag $stamp $folder ${#found[@]}+${#sheets[@]}" >> "$ledger" || return 1
  for f in "$REPO/results/recognition/$p"/answers*.json "$REPO/results/recognition/$p/sheets"/answers*.json; do
    if [ -f "$f" ]; then
      log "warning: $p: committed answers in results/recognition/$p/ are copied back where their key and input" \
          "hash match (ask --seed-answers): move them in git to ask those questions afresh"
      break
    fi
  done
}

on_error() { log "ERROR at line $1: $2"; exit 1; }
trap 'on_error $LINENO "$BASH_COMMAND"' ERR
on_exit() {
  local rc=$?
  trap - ERR
  set +e
  kill_vllm
  if [ -n "$COPY_PID" ]; then
    kill "$COPY_PID" 2>/dev/null || true
    wait "$COPY_PID" 2>/dev/null || true
  fi
  copy_results_locked 300 full      # one full copy at the end, in case a timestamp misled a copy
  copy_job_logs
  log "job $JOB ends with exit code $rc"
  exit "$rc"
}
trap 'on_exit' EXIT
trap 'exit 143' TERM

stamp "$START_STAMP" || log "warning: no start stamp $START_STAMP: earlier jobs' logs may be copied"
rm -f "$COPY_STAMP" "$COPY_STAMP.next"      # the job's first results copy is a full one
cd "$REPO"
mkdir -p "$RESULTS" "$ASSETS" "$WENART_OUTPUTS" "$JOB_DIR"
log "job $JOB: projects [${RUN_PROJECTS:-}], private [${PRIVATE_PROJECTS:-}] selftest ${PRIVATE_SELFTEST:-0}," \
    "A/B [${AB_PROJECTS:-}] (${AB_PHASE}, controls ${AB_CONTROL_PROJECT:-none}), force [${RUN_FORCE:-}]," \
    "samples $RENDER_SAMPLES, check models $CHECK_MODELS, agent ${AGENT_SETUP:-off}, deadline ${WENART_DEADLINE:-none}"
# Fix round after P3 (part 2, 17 Oct 2026): the stored answers of RUN_FRESH_RECOGNITION are set aside before anything
# else runs (header); a failed move stops the job here, before the setup.
if [ -n "${RUN_FRESH_RECOGNITION//[[:space:],]/}" ]; then
  read -r -a FRESH_LIST <<< "${RUN_FRESH_RECOGNITION//,/ }"
  for entry in "${FRESH_LIST[@]}"; do
    set_aside_answers "$entry" || { log "RUN_FRESH_RECOGNITION: the stored answers of '$entry' could not be set" \
                                        "aside: stopping (the run would use them)"; exit 1; }
  done
fi
# 25 Oct 2026 (user OK "Both", volume clean-up): a pod that found the volume full moved the repo, with every
# project's pipeline outputs, aside to $WS/.repo-broken-<stamp>. RESTORE_OUTPUTS=1 moves (never deletes) the newest
# such folder's outputs/<p> back into $WENART_OUTPUTS; a project folder the fresh repo made since is moved aside to
# <p>.fresh-<stamp> first. Idempotent: what was moved is no longer there.
if [ "${RESTORE_OUTPUTS:-0}" = "1" ]; then
  broken=$(ls -d "$WS"/.repo-broken-* 2>/dev/null | sort | tail -1 || true)
  if [ -n "$broken" ] && [ -d "$broken/outputs" ]; then
    stamp=$(date -u +%Y%m%dT%H%M%SZ)
    for src in "$broken"/outputs/*; do
      [ -d "$src" ] || continue
      dst=$WENART_OUTPUTS/$(basename "$src")
      if [ -e "$dst" ]; then mv "$dst" "$dst.fresh-$stamp" && log "RESTORE_OUTPUTS: $dst moved aside to $dst.fresh-$stamp"; fi
      mv "$src" "$dst" && log "RESTORE_OUTPUTS: $src -> $dst"
    done
  else
    log "RESTORE_OUTPUTS: no .repo-broken-*/outputs to restore"
  fi
fi
set_threads
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"
copy_loop &
COPY_PID=$!

# Setup: venv-polish, the polish + gate models (+ the OWLv2 detector), vLLM + both VLMs (+ the agent model, M11)
# and LibreDWG 0.14 for DWG projects (every part: the phases list asks for all; M7 §5.1: the recognition setup's
# 'libredwg' part).
setup_rc=0
AGENT_MODELS="$AGENT_SETUP" POLISH_RECOG_PARTS="vllm libredwg models" POLISH_MODE=final \
  POLISH_PHASES="look controls polish gate check report tests" bash scripts/pod_setup_polish.sh || setup_rc=$?
if [ "$setup_rc" -ne 0 ]; then
  log "warning: pod_setup_polish.sh exit $setup_rc (see setup_polish.json): the stages that need a missing part fail"
fi
# Milestone 13 (16 Oct 2026, before pod P3): the vegetation setup of the site build (scripts/pod_setup_vegetation.sh:
# the Sapling Tree Gen extension into this pod's Blender, the Poly Haven tree models and the ambientCG leaf atlases on
# the volume). The extension lives in $HOME, on the container disk, so a new pod has none; without it the site build
# falls back to leaf-card trees (recorded in the scene manifest). Idempotent, about a minute; a failure is a warning
# only. RUN_VEGETATION_SETUP=0 skips it (a run with no exterior views).
if [ "${RUN_VEGETATION_SETUP:-1}" != "0" ]; then
  bash scripts/pod_setup_vegetation.sh || log "warning: pod_setup_vegetation.sh failed (see vegetation_status.json): trees fall back to leaf cards"
fi
export HF_HUB_OFFLINE=1       # every model is in HF_HOME now; nothing is fetched behind our back

rc=0
"$PY" -m wenart.run pod "${POD_ARGS[@]}" || rc=$?
log "orchestrator exit $rc"
# User request of 25 Oct 2026: angled top-down views of every level with the ceilings off and the room names
# (wenart/blender/topdown.py, wenart/report/topdown_labels.py) into outputs/<p>/renders/top_<level>_plan.jpg, which
# the results copy takes; a failure is a warning only. RUN_TOPDOWN=0 skips it.
if [ "${RUN_TOPDOWN:-1}" != "0" ] && [ -n "${RUN_PROJECTS//[[:space:],]/}" ]; then
  read -r -a TOP_LIST <<< "${RUN_PROJECTS//,/ }"
  for p in "${TOP_LIST[@]}"; do
    scene="$WENART_OUTPUTS/$p/scene/scene.blend"
    if [ ! -f "$scene" ]; then log "topdown $p: no scene.blend"; continue; fi
    "$WENART_BLENDER" -b "$scene" -P wenart/blender/topdown.py -- --out "$WENART_OUTPUTS/$p/topdown" --device GPU \
      --samples 48 > "$LOGS/topdown-$JOB-$p.log" 2>&1 \
      && "$PY" -m wenart.report.topdown_labels "$WENART_OUTPUTS/$p/building_final.json" "$WENART_OUTPUTS/$p/topdown" \
           --out "$WENART_OUTPUTS/$p/renders" --architect "$WENART_OUTPUTS/$p/scene/architect.json" \
           >> "$LOGS/topdown-$JOB-$p.log" 2>&1 \
      && log "topdown $p: done" || log "warning: topdown $p failed (see $LOGS/topdown-$JOB-$p.log)"
  done
fi
# User request of 10 Oct 2026: the 3D files of the public projects to Google Drive (gpu_run.py --drive-upload passes
# the RunPod secret rclone_conf); a failure is a warning only. Private projects never leave the volume this way.
if [ "${DRIVE_UPLOAD:-0}" = "1" ] && [ -n "${RUN_PROJECTS//[[:space:],]/}" ]; then
  read -r -a DRIVE_LIST <<< "${RUN_PROJECTS//,/ }"
  bash scripts/drive_upload.sh "$WENART_OUTPUTS" "${DRIVE_LIST[@]}" || log "warning: drive upload failed"
fi
exit "$rc"
