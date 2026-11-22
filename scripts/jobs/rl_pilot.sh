#!/usr/bin/env bash
# RL pilot of the AI checks' vision model (22 Nov 2026; user: "Yes, prepare it"; THE POD NEEDS A SEPARATE OK).
# One pod, at most 90 min (RTX PRO 6000 96 GB, about $2.7/h: worst case about $4.05; --over-5-ok not needed).
#
#   scripts/gpu_run.py run --job scripts/jobs/rl_pilot.sh --max-minutes 90 \
#     --purpose "M14 RL pilot: rejection-sampling LoRA of the checks' vision model, few-shot arm, exam"
#
# The CPU side and every number this job writes: wenart/reading_check/rl_pilot.py (its docstring). Steps (each timed;
# a failed step is recorded and the next one still runs when it can; exit 1 when any failed):
#   1. setup (about 12 min): vLLM 0.30.0 and the check models "agent" (Qwen/Qwen3.8-27B-FP8) and "bakeoff.bf16"
#      (Qwen/Qwen3.8-27B, the LoRA's base) of check.yaml on the container disk (scripts/pod_setup_polish.sh, phase
#      check), and a training venv (trl 1.17.1, peft 0.21.3, transformers 5.18.0, accelerate 1.15.0, datasets 5.1.0;
#      the image's torch);
#   2. build (1 min, CPU): the training questions from the synthetic exact truth and the few-shot folds
#      (rl_pilot build, rl_pilot fewshot): 763 questions, 646 to train on, 117 held out (3 synthetic projects);
#   3. phase A (about 25 min, the FP8 agent model): every training question 8 times at temperature 0.8 (5168 answers),
#      the held-out questions once at temperature 0 (the base number), then the zero-training arm's exam: the RC15
#      calls of today's measurement with the few-shot block of fold 0 (rl_pilot phase-sample);
#   4. filter (seconds): rejection sampling: the right answers of the questions neither all right nor all wrong
#      (rl_pilot filter -> sft.jsonl; the step fails, and no LoRA is trained, when nothing is left);
#   5. train (about 15 min): a rank-16 LoRA on the BF16 base, 2 epochs (rl_pilot train);
#   6. phase C (about 25 min): the BF16 base with the LoRA beside it: the held-out questions with both, the exam with
#      the LoRA, then (15 min left) the exam with the BF16 base alone as the control (rl_pilot phase-exam).
# Results: $WENART_RESULTS/rl/ (samples, held-out answers, sft.jsonl, the adapter's config and the training log, the
# exam answers per arm) and this job's log. The exam is scored on the CPU afterwards: `critic calibrate` on each arm's
# answers against the user's marks and results/critic/known_errors.json (never trained on), compared with today's 66
# of 73 known errors found, 11 false findings and the judge's 51 of 62.
#
# Env (all optional): RL_SERVER_FLAGS (default "--gpu-memory-utilization 0.90 --max-model-len 16384"), RL_EPOCHS (2),
# RL_RANK (16), RL_TRAIN_MIN_S (the time a training needs, default 1500 s: skipped with less left before the deadline).
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS="${WENART_LOGS:-$WS/logs}"
REPO="${WENART_REPO:-$WS/repo}"
JOB="${JOB_ID:-rl_pilot}"
LOG=$LOGS/rl_pilot-$JOB.log
mkdir -p "$LOGS"
exec > >(tee -a "$LOG") 2>&1

JOB_DIR="${WENART_JOB_DIR:-$WS/jobs/$JOB}"
RESULTS="${WENART_RESULTS:-$JOB_DIR/results}"
FAST="${WENART_FAST:-/opt/wenart}"
PY="${WENART_PY:-$WS/venv/bin/python}"
VTRAIN="$FAST/venv-train"
export HF_HOME="${WENART_HF_HOME:-$FAST/hf}"
export HF_XET_HIGH_PERFORMANCE=1
export WENART_JOB_DIR="$JOB_DIR" WENART_RESULTS="$RESULTS" WENART_LOGS="$LOGS" WENART_PY="$PY"
RL_SERVER_FLAGS="${RL_SERVER_FLAGS:---gpu-memory-utilization 0.90 --max-model-len 16384}"
RL_EPOCHS="${RL_EPOCHS:-2}"
RL_RANK="${RL_RANK:-16}"
RL_TRAIN_MIN_S="${RL_TRAIN_MIN_S:-1500}"
OUT=$RESULTS/rl
TRAIN=$JOB_DIR/rl_train
FAILED=()
START_STAMP=$LOGS/rl_pilot-$JOB.start

ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
log() { echo "[$(ts)] rl_pilot: $*"; }

case "${WENART_DEADLINE:-}" in
  '') ;;
  *[!0-9.]*) log "WENART_DEADLINE '${WENART_DEADLINE}' is not epoch seconds: ignored"; unset WENART_DEADLINE ;;
esac

seconds_left() {
  if [ -n "${WENART_DEADLINE:-}" ]; then echo $(( ${WENART_DEADLINE%.*} - $(date +%s) )); else echo 999999; fi
}

copy_results() {
  mkdir -p "$RESULTS/logs" "$OUT"
  local f
  for f in "$LOGS"/vllm-*.log "$LOGS"/hf-download-*.log "$LOGS"/setup-polish-*.log; do
    if [ -f "$f" ] && [ "$f" -nt "$START_STAMP" ]; then
      tail -n 200 "$f" > "$RESULTS/logs/$(basename "$f")" 2>/dev/null || true
    fi
  done
  if [ -d "$TRAIN" ]; then
    cp -f "$TRAIN"/manifest.json "$TRAIN"/sft.jsonl "$TRAIN"/fewshot_fold*.json "$OUT/" 2>/dev/null || true
  fi
  if [ -d "$JOB_DIR/adapter" ]; then
    mkdir -p "$OUT/adapter"
    cp -f "$JOB_DIR"/adapter/*.json "$OUT/adapter/" 2>/dev/null || true      # the config and the training state only
  fi
  cp -f "$LOG" "$RESULTS/" 2>/dev/null || true
  log "results copied to $RESULTS: $(find "$RESULTS" -type f | wc -l) files"
}

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

# run_step <name> <command...>: timed, failure recorded, results flushed; returns the step's code.
run_step() {
  local name=$1; shift
  local t0 rc=0
  t0=$(date +%s)
  log "step start: $name ($(seconds_left) s left)"
  "$@" || rc=$?
  log "step end: $name rc=$rc in $(( $(date +%s) - t0 )) s"
  if [ "$rc" -ne 0 ]; then FAILED+=("$name"); fi
  kill_vllm
  copy_results
  return "$rc"
}

setup_train_venv() {
  if [ -f "$VTRAIN/.rl-pilot-1" ]; then log "train venv ready"; return 0; fi
  python3 -m venv --system-site-packages "$VTRAIN"
  "$VTRAIN/bin/pip" install -q "trl==1.17.1" "peft==0.21.3" "transformers==5.18.0" "accelerate==1.15.0" \
    "datasets==5.1.0" pillow pyyaml shapely ezdxf
  "$VTRAIN/bin/python" -c 'import torch, trl, peft, transformers; print("train venv", torch.__version__, trl.__version__, peft.__version__, transformers.__version__, torch.cuda.is_available())'
  touch "$VTRAIN/.rl-pilot-1"
}

: > "$START_STAMP"
cd "$REPO"
mkdir -p "$RESULTS" "$OUT" "$JOB_DIR"
log "job $JOB: deadline ${WENART_DEADLINE:-none}, server flags '$RL_SERVER_FLAGS', epochs $RL_EPOCHS, rank $RL_RANK"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader 2>/dev/null || log "nvidia-smi failed"

run_step setup env AGENT_MODELS="agent bakeoff.bf16" CHECK_MODELS="qwen" POLISH_RECOG_PARTS="vllm models" \
  POLISH_MODE=final POLISH_PHASES="check" bash scripts/pod_setup_polish.sh || true
run_step train-venv setup_train_venv || true
export HF_HUB_OFFLINE=1

run_step build "$PY" -m wenart.reading_check rl_pilot build --out "$TRAIN" || exit 1
run_step fewshot "$PY" -m wenart.reading_check rl_pilot fewshot --out "$TRAIN" || true

A_ARGS=(--train "$TRAIN" --out "$OUT/phase_a" --server-flags "$RL_SERVER_FLAGS")
# RL_FEWSHOT=0 skips the few-shot exam (22 Nov 2026: the rerun after pod 1p2wukgcbep0d8, whose few-shot exam answered 555
# of 555 calls; only the sampling failed)
if [ "${RL_FEWSHOT:-1}" = "1" ]; then A_ARGS+=(--fewshot "$TRAIN/fewshot_fold0.json"); fi
if [ -n "${WENART_DEADLINE:-}" ]; then A_ARGS+=(--deadline "$WENART_DEADLINE"); fi
run_step phase-a "$PY" -m wenart.reading_check rl_pilot phase-sample "${A_ARGS[@]}" || true

if [ -f "$OUT/phase_a/samples.jsonl" ] && run_step filter "$PY" -m wenart.reading_check rl_pilot filter \
    --train "$TRAIN" --samples "$OUT/phase_a/samples.jsonl"; then
  if [ "$(seconds_left)" -ge "$RL_TRAIN_MIN_S" ]; then
    BF16_ID=$("$PY" -c 'from wenart.run import servers as SV; m=SV.model_entry(SV.check_models(), "bakeoff.bf16"); print(m["id"])')
    BF16_REV=$("$PY" -c 'from wenart.run import servers as SV; m=SV.model_entry(SV.check_models(), "bakeoff.bf16"); print(m["revision"])')
    run_step train "$VTRAIN/bin/python" -m wenart.reading_check rl_pilot train --train "$TRAIN" --base "$BF16_ID" \
      --revision "$BF16_REV" --out "$JOB_DIR/adapter" --epochs "$RL_EPOCHS" --rank "$RL_RANK" || true
  else
    log "skipping the training: $(seconds_left) s left (< $RL_TRAIN_MIN_S)"
    FAILED+=("train-skipped")
  fi
fi

if [ -f "$JOB_DIR/adapter/adapter_config.json" ]; then
  C_ARGS=(--train "$TRAIN" --adapter "$JOB_DIR/adapter" --out "$OUT/phase_c" --server-flags "$RL_SERVER_FLAGS"
          --rank "$RL_RANK")
  if [ -n "${WENART_DEADLINE:-}" ]; then C_ARGS+=(--deadline "$WENART_DEADLINE"); fi
  run_step phase-c "$PY" -m wenart.reading_check rl_pilot phase-exam "${C_ARGS[@]}" || true
fi

if [ "${#FAILED[@]}" -gt 0 ]; then
  log "FAILED steps: ${FAILED[*]}"
  exit 1
fi
log "all steps ok"
