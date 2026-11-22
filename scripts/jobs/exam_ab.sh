#!/usr/bin/env bash
# The AI checks' exam A/B with the drawing text on (22 Nov 2026; user: "start the test pod"). The RL pilot asked its
# exam without the drawing text, so none of its arms compares with today's default (66 of 73 known errors, 11 false).
# Four arms, one after the other: the FP8 agent model (the control: today's default), the FP8 model with the few-shot
# block of fold 0, the BF16 base, the BF16 base with the same block (wenart.reading_check.rl_pilot exam_ab).
# One RTX PRO 6000 (the BF16 base needs ~55 GB), at most 75 min: worst case about $3.40.
#
#   scripts/gpu_run.py run --job scripts/jobs/exam_ab.sh --max-minutes 75 \
#     --purpose "M14 AI checks exam A/B with the drawing text: FP8 / FP8 few-shot / BF16 / BF16 few-shot"
#
# Scored on the CPU afterwards with `critic vt-score`; the few-shot arms only on the marks of fold 0 (never on their
# examples, the marks of fold 1). Env: EXAM_KEYS (default "agent,bakeoff.bf16"), EXAM_SERVER_FLAGS (default
# "--gpu-memory-utilization 0.90 --max-model-len 16384").
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS="${WENART_LOGS:-$WS/logs}"
REPO="${WENART_REPO:-$WS/repo}"
JOB="${JOB_ID:-exam_ab}"
LOG=$LOGS/exam_ab-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
FAST="${WENART_FAST:-/opt/wenart}"
PY="${WENART_PY:-$WS/venv/bin/python}"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_PY="$PY"
EXAM_KEYS="${EXAM_KEYS:-agent,bakeoff.bf16}"
EXAM_SERVER_FLAGS="${EXAM_SERVER_FLAGS:---gpu-memory-utilization 0.90 --max-model-len 16384}"
OUT=$RESULTS/exam_ab
TRAIN=$JOB_DIR/rl_train
START_STAMP=$LOGS/exam_ab-$JOB.start

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] exam_ab: $*"; }

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
  cp -f "$TRAIN"/fewshot_fold*.json "$OUT/" 2>/dev/null || true
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  log "results copied to $RESULTS: $(find "$RESULTS" -type f | wc -l) files"
}

on_error() { log "ERROR at line $1: $2"; exit 1; }
trap 'on_error $LINENO "$BASH_COMMAND"' ERR
on_exit() {
  local rc=$?
  trap - ERR
  set +e
  copy_results
  log "job $JOB ends with exit code $rc"
  exit "$rc"
}
trap 'on_exit' EXIT
trap 'exit 143' TERM

: > "$START_STAMP"
cd "$REPO"
mkdir -p "$RESULTS" "$OUT" "$JOB_DIR" "$TRAIN"
log "job $JOB: keys $EXAM_KEYS, deadline ${WENART_DEADLINE:-none}, server flags '$EXAM_SERVER_FLAGS'"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

log "step: setup"
env AGENT_MODELS="agent bakeoff.bf16" CHECK_MODELS="qwen" POLISH_RECOG_PARTS="vllm models" POLISH_MODE=final \
  POLISH_PHASES="check" bash scripts/pod_setup_polish.sh
export HF_HUB_OFFLINE=1

log "step: few-shot folds"
"$PY" -m wenart.reading_check rl_pilot fewshot --out "$TRAIN"

log "step: exam"
ARGS=(--out "$OUT" --keys "$EXAM_KEYS" --fewshot "$TRAIN/fewshot_fold0.json" --server-flags "$EXAM_SERVER_FLAGS")
if [ -n "${WENART_DEADLINE:-}" ]; then ARGS+=(--deadline "$WENART_DEADLINE"); fi
"$PY" -m wenart.reading_check rl_pilot exam-ab "${ARGS[@]}"
log "all steps ok"
