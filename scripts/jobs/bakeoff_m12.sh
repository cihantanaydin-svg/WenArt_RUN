#!/usr/bin/env bash
# Milestone 12 pod P1: the agent model bake-off (docs/milestone12.md §5.1; wenart/agent/bakeoff.py). Run by
# scripts/pod_entry.sh on a 2-GPU RunPod pod (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR, WENART_DEADLINE
# and WENART_GPU_COUNT set; /workspace/venv has the CPU deps; Blender at /workspace/tools/blender/blender). The
# watchdog and the self-stop are pod_entry.sh's (the pod stops itself at --max-minutes whatever this job does).
#
#   python3 scripts/gpu_run.py run --job scripts/jobs/bakeoff_m12.sh --gpu-count 2 --gpu 'RTX PRO 6000' --disk 500 \
#     --max-minutes 100 --over-5-ok --purpose "M12 P1: agent model bake-off"
#
# Steps (each timed; a failed step is recorded and the next one still runs; exit 1 when any failed):
#   1. setup: vLLM 0.30.0 (scripts/pod_setup_recognition.sh, part vllm only); the models of check.yaml
#      models.bakeoff with their pinned revisions (`hf download` into HF_HOME on the container disk, ~1.1 GB/s):
#      the first pair in the foreground, the others in the background while the first pair runs; with
#      BAKEOFF_VLLM_RETRY (default 0.31.0, empty = off) a second vLLM venv is installed in the background, used
#      only when a 2-GPU model does not start on 0.30.0 (its card asks for a newer vLLM; reported, not adopted);
#   2. phase A: fp8 on GPU 0 (port 8001, every variant, then the GPU tests against its live server) and muse on
#      GPU 1 (port 8002) at the same time; each with a Cycles render of RENDER_SCENE next to its server;
#   3. phase B: bf16 on GPU 0;
#   4. phase C: flash_next on both GPUs (tensor parallel 2); step_flash only when flash_next did not start
#      (its fallback), and only while the deadline allows;
#   5. summary: results/bakeoff_m12/summary.{json,md} with the pick of the decision rule.
# Every model writes $RESULTS/bakeoff_m12/<name>.json (server, VRAM, Cycles) and <name>-<variant>.json (answers,
# scores) as soon as a variant ends, and the results are copied after every step, so a cut pod keeps what it
# measured. Expected: about 75 minutes (setup 6, phase A 25, phase B 19, phase C 22, summary 1; BAKEOFF_CAP_S
# = 720 s per variant at most).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-bakeoff_m12}"
LOG=$LOGS/bakeoff_m12-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
FAST="${WENART_FAST:-/opt/wenart}"
PY="${WENART_PY:-$WS/venv/bin/python}"
VENV_VLLM=$FAST/venv-vllm
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_PY="$PY"
OUT=$RESULTS/bakeoff_m12
STATE=$JOB_DIR/bakeoff_state
RENDER_SCENE="${RENDER_SCENE:-$REPO/outputs/real02/scene/scene.blend}"
CAP_S="${BAKEOFF_CAP_S:-720}"                       # one variant's time cap (the deadline of phase C)
RETRY_VLLM="${BAKEOFF_VLLM_RETRY-0.31.0}"
DOWNLOAD_WAIT_S="${BAKEOFF_DOWNLOAD_WAIT_S:-1800}"
FAILED=()
START_STAMP=$LOGS/bakeoff_m12-$JOB.start

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] bakeoff_m12: $*"; }

copy_results() {
  mkdir -p "$RESULTS/logs"
  local f
  for f in "$LOGS"/vllm-*.log "$LOGS"/hf-download-*.log "$LOGS"/setup-*.log "$LOGS"/bakeoff-run-*.log; do
    if [ -f "$f" ] && [ "$f" -nt "$START_STAMP" ]; then
      tail -n 300 "$f" > "$RESULTS/logs/$(basename "$f")" 2>/dev/null || true
    fi
  done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  log "results copied to $RESULTS: $(find "$RESULTS" -type f | wc -l) files"
}

# kill_vllm: every server a step left behind (the pid files of wenart.run.servers under the job folder).
kill_vllm() {
  local f pid
  while IFS= read -r f; do
    pid=$(cat "$f" 2>/dev/null) || pid=""
    if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
      log "stopping vllm (pid $pid) left by a step"
      kill -TERM -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
      sleep 10
      kill -KILL -- "-$pid" 2>/dev/null || true
    fi
    rm -f "$f"
  done < <(find "$JOB_DIR" -name vllm.pid 2>/dev/null)
}

on_error() { log "ERROR at line $1: $2"; exit 1; }
trap 'on_error $LINENO "$BASH_COMMAND"' ERR
on_exit() {
  local rc=$?
  trap - ERR
  set +e
  kill_vllm
  "$PY" -m wenart.agent.bakeoff summary --out "$OUT" || true
  copy_results
  log "job $JOB ends with exit code $rc"
  exit "$rc"
}
trap 'on_exit' EXIT
trap 'exit 143' TERM

# run_step <name> <command...>: timed, failure recorded, the job goes on, servers stopped, results flushed.
run_step() {
  local name=$1; shift
  local t0 rc=0
  t0=$(date +%s)
  log "step start: $name"
  "$@" || rc=$?
  log "step end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  if [ "$rc" -ne 0 ]; then FAILED+=("$name"); fi
  kill_vllm
  copy_results
  return 0
}

# --- models ------------------------------------------------------------------------------------------------------
declare -A MODEL_ID MODEL_REV MODEL_GPUS
load_models() {
  local name key id rev gpus _size _variants
  while read -r name key id rev gpus _size _variants; do
    [ -n "$name" ] || continue
    MODEL_ID[$name]=$id; MODEL_REV[$name]=$rev; MODEL_GPUS[$name]=$gpus
  done < <("$PY" -m wenart.agent.bakeoff models)
  log "bake-off models: ${!MODEL_ID[*]}"
}

# download <name>: hf download of the pinned revision; marks $STATE/<name>.ok or .fail.
download() {
  local name=$1 id=${MODEL_ID[$1]} rev=${MODEL_REV[$1]} t0
  t0=$(date +%s)
  if "$VENV_VLLM/bin/hf" download "$id" --revision "$rev" > "$LOGS/hf-download-$name.log" 2>&1; then
    log "download $name ($id@${rev:0:12}) done in $(( $(date +%s) - t0 )) s"
    touch "$STATE/$name.ok"
  else
    log "download $name ($id) FAILED (see hf-download-$name.log)"
    touch "$STATE/$name.fail"
    return 1
  fi
}

# wait_model <name>: until its download is done (ok: 0, failed or too long: 1).
wait_model() {
  local name=$1 t0
  t0=$(date +%s)
  while [ ! -f "$STATE/$name.ok" ]; do
    if [ -f "$STATE/$name.fail" ]; then log "no $name: its download failed"; return 1; fi
    if [ $(( $(date +%s) - t0 )) -gt "$DOWNLOAD_WAIT_S" ]; then log "no $name: download not done"; return 1; fi
    sleep 10
  done
}

# bakeoff <name> <device> <port> [extra args]: one model, every variant (wenart.agent.bakeoff run).
bakeoff() {
  local name=$1 device=$2 port=$3; shift 3
  wait_model "$name" || return 1
  HF_HUB_OFFLINE=1 "$PY" -m wenart.agent.bakeoff run --key "bakeoff.$name" --device "$device" --port "$port" \
    --out "$OUT" --cap-s "$CAP_S" --scene "$RENDER_SCENE" "$@" > "$LOGS/bakeoff-run-$name.log" 2>&1
}

# pair <name A> <name B>: A on GPU 0 (port 8001) and B on GPU 1 (port 8002) at the same time.
pair() {
  local a=$1 b=$2 rc_a=0 rc_b=0 pid_b
  bakeoff "$b" 1 8002 & pid_b=$!
  bakeoff "$a" 0 8001 ${PAIR_A_ARGS:-} || rc_a=$?
  wait "$pid_b" || rc_b=$?
  log "pair $a (rc $rc_a) + $b (rc $rc_b)"
  [ "$rc_a" -eq 0 ] && [ "$rc_b" -eq 0 ]
}

# two_gpu <name>: tensor parallel 2 on both GPUs; once more on the retry vLLM when it did not start.
two_gpu() {
  local name=$1 rc=0
  bakeoff "$name" "0,1" 8001 || rc=$?
  if [ "$rc" -ne 0 ] && [ -n "$RETRY_VLLM" ] && [ -x "$FAST/venv-vllm-$RETRY_VLLM/bin/vllm" ] \
      && ! "$PY" -m wenart.agent.bakeoff started --out "$OUT" --name "$name"; then
    log "$name did not start on vLLM 0.30.0; once more on vLLM $RETRY_VLLM (reported, not adopted)"
    rc=0
    WENART_VLLM="$FAST/venv-vllm-$RETRY_VLLM/bin/vllm" bakeoff "$name" "0,1" 8001 || rc=$?
  fi
  return "$rc"
}

retry_venv() {
  local v=$FAST/venv-vllm-$RETRY_VLLM
  [ -x "$v/bin/vllm" ] && return 0
  python3 -m venv "$v" && "$v/bin/pip" install -q --upgrade pip \
    && "$v/bin/pip" install -q "vllm==$RETRY_VLLM" > "$LOGS/setup-vllm-$RETRY_VLLM.log" 2>&1 \
    && "$v/bin/python" -c "import vllm; print('vllm', vllm.__version__)" >> "$LOGS/setup-vllm-$RETRY_VLLM.log" 2>&1
}

: > "$START_STAMP"
cd "$REPO"
mkdir -p "$RESULTS" "$OUT" "$JOB_DIR" "$STATE"
log "job $JOB: ${WENART_GPU_COUNT:-1} GPU(s), render scene $RENDER_SCENE, deadline ${WENART_DEADLINE:-none}"
nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"
if [ "${WENART_GPU_COUNT:-1}" -lt 2 ]; then log "WARNING: one GPU only: the 2-GPU models will be refused"; fi

run_step setup env RECOG_SETUP_PARTS="vllm" bash scripts/pod_setup_recognition.sh
load_models
# The first pair in the foreground (both at once), the rest in the background in the order they are needed; a
# failed download leaves its .fail marker (the model's step then fails) and the next download still runs.
# Explicit pids: a bare `wait` also waits for the `exec > >(tee ...)` process substitution in bash >= 5.1 and never
# returns (pod P1 of 10 Oct 2026 hung here until its watchdog; tests/test_jobs_flow.py runs this flow with fakes).
( download fp8 || true ) & dl_fp8=$!
( download muse || true ) & dl_muse=$!
wait "$dl_fp8" "$dl_muse" || true
# step_flash (129 GB) is only the fallback of flash_next: downloaded in its phase, when flash_next did not start.
( download bf16 || true; download flash_next || true ) &
if [ -n "$RETRY_VLLM" ]; then ( retry_venv || log "vLLM $RETRY_VLLM venv FAILED" ) & fi
export HF_HUB_OFFLINE=1

PAIR_A_ARGS="--gpu-tests" run_step "phase-a fp8+muse" pair fp8 muse
run_step "phase-b bf16" bakeoff bf16 0 8001
run_step "phase-c flash_next" two_gpu flash_next
if ! "$PY" -m wenart.agent.bakeoff started --out "$OUT" --name flash_next; then
  ( download step_flash || true ) & dl_step=$!
  wait "$dl_step" || true
  run_step "phase-c step_flash (fallback)" two_gpu step_flash
fi
run_step summary "$PY" -m wenart.agent.bakeoff summary --out "$OUT"

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
