#!/usr/bin/env bash
# Milestone 11 pod G1: the model check of the AI orchestrator (docs/milestone11.md §11 "to be confirmed on the
# model-check pod", §12). Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS,
# WENART_JOB_DIR and WENART_DEADLINE set; /workspace/venv has the CPU deps; Blender at
# /workspace/tools/blender/blender). The watchdog and the self-stop are pod_entry.sh's.
#
#   scripts/gpu_run.py run --job scripts/jobs/agent_check.sh --gpu 'RTX PRO 6000' --disk 150 --max-minutes 60 \
#     --purpose "M11 pod G1: agent model check"
#
# Steps (each timed; a failed step is recorded and the next one still runs; exit 1 when any failed):
#   1. setup: vLLM 0.30.0 + the agent models of check.yaml (AGENT_MODELS, default "agent agent_fast": hf download
#      with the pinned revisions into HF_HOME on the container disk) via scripts/pod_setup_polish.sh (part check
#      only; the M5 VLMs come along, 38 GB, about 40 s);
#   2. podcheck agent: start the server as the orchestrator does (0.55 of the VRAM, 4 images, sleep mode), tokens/s
#      (1 and 4 streams), the temperature-0 repetition check, a tool call with the planner's tools, a JSON-schema
#      critic answer, VRAM with a concurrent Cycles render of one real02 view (RENDER_SCENE, default the volume's
#      outputs/real02/scene/scene.blend; skipped with the reason when missing), sleep / wake, the critic on real02
#      with planted errors (a bed turned 180 deg, a sofa facing its wall) -> $RESULTS/agent_check/agent.json;
#   3. podcheck agent --mtp: MTP speculative decoding on (speed + the tool call) -> agent-mtp.json;
#   4. podcheck agent_fast: the fallback model, the same checks -> agent_fast.json;
#   5. pytest -m gpu tests/gpu/test_agent.py (its own server of AGENT_TEST_MODEL, default agent) -> junit-agent.xml.
# Results: $RESULTS/agent_check/*.json, the top-down images it sent, the vLLM logs (tail 200) and this job's log.
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
REPO=$WS/repo
JOB="${JOB_ID:-agent_check}"
LOG=$LOGS/agent_check-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
FAST="${WENART_FAST:-/opt/wenart}"
PY="${WENART_PY:-$WS/venv/bin/python}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_PY="$PY"
AGENT_MODELS="${AGENT_MODELS:-agent agent_fast}"
RENDER_SCENE="${RENDER_SCENE:-$REPO/outputs/real02/scene/scene.blend}"
OUT=$RESULTS/agent_check
FAILED=()
START_STAMP=$LOGS/agent_check-$JOB.start

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] agent_check: $*"; }

copy_results() {
  mkdir -p "$RESULTS/logs"
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

: > "$START_STAMP"
cd "$REPO"
mkdir -p "$RESULTS" "$OUT" "$JOB_DIR"
log "job $JOB: agent models [$AGENT_MODELS], render scene $RENDER_SCENE, deadline ${WENART_DEADLINE:-none}"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

run_step setup env AGENT_MODELS="$AGENT_MODELS" POLISH_RECOG_PARTS="vllm models" POLISH_MODE=final \
  POLISH_PHASES="check" bash scripts/pod_setup_polish.sh
export HF_HUB_OFFLINE=1

read -r -a KEYS <<< "$AGENT_MODELS"
for key in "${KEYS[@]}"; do
  if [ "$key" = "agent" ]; then
    run_step "podcheck-$key" "$PY" -m wenart.agent.podcheck --key "$key" --render-scene "$RENDER_SCENE" \
      --planted real02 --out "$OUT"
    run_step "podcheck-$key-mtp" "$PY" -m wenart.agent.podcheck --key "$key" --mtp --out "$OUT"
  else
    run_step "podcheck-$key" "$PY" -m wenart.agent.podcheck --key "$key" --planted real02 --out "$OUT"
  fi
done

run_step gpu-tests env AGENT_TEST_MODEL="${AGENT_TEST_MODEL:-agent}" "$PY" -m pytest -m gpu tests/gpu/test_agent.py \
  -v -ra --junitxml="$RESULTS/junit-agent.xml"

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
