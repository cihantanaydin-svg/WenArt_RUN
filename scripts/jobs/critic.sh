#!/usr/bin/env bash
# Milestone 14 R6 (6 Nov 2026; user, 4 Nov 2026: "some AI or something else to give the feedbacks by itself instead of
# me at some point"): the vision critic RC15 asked about every level of the committed input set
# (results/critic/inputs/, made on the CPU by `python -m wenart.reading_check critic prepare`): the agent model of
# check.yaml (Qwen3.8-27B-FP8) and, when time is left, `qwen` (Qwen3-VL-8B-Instruct) for comparison. Run by
# scripts/pod_entry.sh (cwd /workspace/repo; WENART_RESULTS, WENART_JOB_DIR and WENART_DEADLINE set; the watchdog and
# the self-stop are pod_entry.sh's).
#
#   scripts/gpu_run.py run --job scripts/jobs/critic.sh --max-minutes 40 --purpose "M14 R6: vision critic calibration"
#
# Steps (each timed; a failed step is recorded and the next one still runs; exit 1 when any failed):
#   1. setup: vLLM + the agent model and qwen of check.yaml (scripts/pod_setup_polish.sh, part check; HF_HOME on the
#      container disk); skipped when CRITIC_VLM_URL names a server already running (the CPU preflight with
#      tests/fakes/fake_vlm.py);
#   2. ask-agent: python -m wenart.reading_check critic ask --key agent --serve ... (wenart.run.servers starts the
#      server with the model's own flags; CRITIC_SERVER_FLAGS are appended: no render runs beside the server on this
#      pod, so it may take 0.90 of the VRAM instead of check.yaml's 0.55, which on a 48 GB card would not hold the
#      31 GB of weights); nothing new is sent after WENART_DEADLINE;
#   3. ask-qwen: the same with the second model, only when at least CRITIC_SECOND_MIN_S seconds are left.
# Results: $WENART_RESULTS/critic/<key>/answers.json (every raw answer and the call log), server.json, the vLLM logs
# (tail 200) and this job's log. The calibration runs on the CPU afterwards (`critic calibrate`).
#
# Env (all optional): CRITIC_MODELS (default "agent qwen"), CRITIC_INPUTS (default results/critic/inputs),
# CRITIC_SERVER_FLAGS (default "--gpu-memory-utilization 0.90 --max-model-len 16384"), CRITIC_SECOND_MIN_S (default
# 600), CRITIC_SETS
# (default all), CRITIC_VLM_URL (preflight: an external server, no setup, no vLLM).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS="${WENART_LOGS:-$WS/logs}"
REPO="${WENART_REPO:-$WS/repo}"
JOB="${JOB_ID:-critic}"
LOG=$LOGS/critic-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
FAST="${WENART_FAST:-/opt/wenart}"
PY="${WENART_PY:-$WS/venv/bin/python}"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_PY="$PY"
CRITIC_MODELS="${CRITIC_MODELS:-agent qwen}"
CRITIC_INPUTS="${CRITIC_INPUTS:-results/critic/inputs}"
# No render beside the server on this pod: 0.90 of the VRAM (check.yaml's 0.55 would not hold the 31 GB of weights on
# a 48 GB card); 16k of context (two 1600 px images are about 4.5k tokens, the longest answer 4k), so the KV cache and
# the start-up profiling fit beside the weights on 48 GB too. Both repeat a flag of serve_command; the later one wins.
CRITIC_SERVER_FLAGS="${CRITIC_SERVER_FLAGS:---gpu-memory-utilization 0.90 --max-model-len 16384}"
CRITIC_SECOND_MIN_S="${CRITIC_SECOND_MIN_S:-600}"
OUT=$RESULTS/critic
FAILED=()
START_STAMP=$LOGS/critic-$JOB.start

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] critic: $*"; }

case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

copy_results() {
  mkdir -p "$RESULTS/logs" "$OUT"
  local f
  for f in "$LOGS"/vllm-*.log "$LOGS"/hf-download-*.log "$LOGS"/setup-polish-*.log; do
    if [ -f "$f" ] && [ "$f" -nt "$START_STAMP" ]; then
      tail -n 200 "$f" > "$RESULTS/logs/$(basename "$f")" 2>/dev/null || true
    fi
  done
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  log "results copied to $RESULTS: $(find "$RESULTS" -type f | wc -l) files"
}

# kill_vllm: a server left behind by a step that died (the pid file of wenart.run.servers).
kill_vllm() {
  local pid
  [ -f "$JOB_DIR/vllm.pid" ] || return 0
  pid=$(cat "$JOB_DIR/vllm.pid" 2>/dev/null) || pid=""
  if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
    log "stopping vllm (pid $pid) left by a step"
    kill -TERM -- "-$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    sleep 10
    kill -KILL -- "-$pid" 2>/dev/null || true
  fi
  rm -f "$JOB_DIR/vllm.pid"
}

on_error() { log "ERROR at line $1: $2"; exit 1; }
trap 'on_error $LINENO "$BASH_COMMAND"' ERR
on_exit() {
  local rc=$?
  trap - ERR
  set +e
  kill_vllm
  copy_results
  log "job $JOB ends with exit code $rc"
  exit "$rc"
}
trap 'on_exit' EXIT
trap 'exit 143' TERM

# run_step <name> <command...>: timed, failure recorded, the job goes on, results flushed.
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

seconds_left() {
  if [ -n "${WENART_DEADLINE:-}" ]; then echo $(( ${WENART_DEADLINE%.*} - $(date +%s) )); else echo 999999; fi
}

: > "$START_STAMP"
cd "$REPO"
mkdir -p "$RESULTS" "$OUT" "$JOB_DIR"
log "job $JOB: models [$CRITIC_MODELS], inputs $CRITIC_INPUTS, deadline ${WENART_DEADLINE:-none}, server flags '$CRITIC_SERVER_FLAGS'"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"
if [ ! -f "$CRITIC_INPUTS/index.json" ]; then
  log "no $CRITIC_INPUTS/index.json: run 'python -m wenart.reading_check critic prepare' and commit the inputs first"
  exit 1
fi
log "input set: $("$PY" -c 'import json,sys; d=json.load(open(sys.argv[1])); print(len(d["entries"]), "levels")' "$CRITIC_INPUTS/index.json")"

if [ -z "${CRITIC_VLM_URL:-}" ]; then
  run_step setup env AGENT_MODELS="agent" CHECK_MODELS="qwen" POLISH_RECOG_PARTS="vllm models" POLISH_MODE=final \
    POLISH_PHASES="check" bash scripts/pod_setup_polish.sh
  export HF_HUB_OFFLINE=1
else
  log "CRITIC_VLM_URL set: no setup, asking the server at $CRITIC_VLM_URL"
fi

read -r -a KEYS <<< "$CRITIC_MODELS"
n=0
for key in "${KEYS[@]}"; do
  n=$((n + 1))
  if [ "$n" -gt 1 ] && [ "$(seconds_left)" -lt "$CRITIC_SECOND_MIN_S" ]; then
    log "skipping $key: $(seconds_left) s left before the deadline (< $CRITIC_SECOND_MIN_S)"
    continue
  fi
  ASK_ARGS=(--key "$key" --inputs "$CRITIC_INPUTS" --out "$OUT" --job-dir "$JOB_DIR" --logs-dir "$LOGS")
  if [ -n "${WENART_DEADLINE:-}" ]; then ASK_ARGS+=(--deadline "$WENART_DEADLINE"); fi
  if [ -n "${CRITIC_SETS:-}" ]; then ASK_ARGS+=(--sets "$CRITIC_SETS"); fi
  if [ -n "${CRITIC_VLM_URL:-}" ]; then
    ASK_ARGS+=(--vlm-url "$CRITIC_VLM_URL" --workers 2)
  else
    ASK_ARGS+=(--server-flags "$CRITIC_SERVER_FLAGS")
  fi
  run_step "ask-$key" "$PY" -m wenart.reading_check critic ask "${ASK_ARGS[@]}"
done

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
