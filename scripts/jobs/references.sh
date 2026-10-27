#!/usr/bin/env bash
# 27 Oct 2026 (lesson UL42; user: "find the photos yourself and put it into the pod"): reference photo candidates for
# the AI's style recipes (docs/style_references.md). The cloud session reaches no photo host and the pod's Openverse
# and Commons searches found nothing (runs 123917, 130756), so this job searches the captions of PD12M (Spawning/PD12M
# on the Hugging Face Hub: 12.4 M public-domain and CC0 photos) for every space of the style families, downloads the
# matches from the dataset's S3 bucket, ranks them with SigLIP 2 (Apache-2.0) and writes the best REF_PER_SPACE per
# space as 512 px copies with a manifest into the results; the session looks at them, keeps the good ones and commits
# them (assets/references), which every later run copies to the volume before its servers start.
# Run: scripts/gpu_run.py run --job scripts/jobs/references.sh --gpu "RTX PRO 6000" --max-minutes 30 \
#        --env REF_FAMILIES=scandinavian --purpose "..."
# Env: REF_FAMILIES (default "scandinavian"), REF_PER_SPACE (default 30), REF_SHARDS (default 125: every PD12M shard),
#      REF_SPACES (default: every space, the ones every house has first).
set -Eeuo pipefail
trap 'echo "[references] error at line $LINENO (exit $?)" >&2' ERR
cd /workspace/repo
LOGS=/workspace/logs
mkdir -p "$LOGS" "$WENART_RESULTS"
JOB="${JOB_ID:-references}"
log() { echo "[$(date -u +%FT%TZ)] references: $*" | tee -a "$LOGS/references-$JOB.log"; }

# venv-polish (transformers, huggingface-hub, the image's torch) is the environment SigLIP 2 runs in; its "gate" phase
# builds it (and checks its models, cached). pyarrow reads the PD12M metadata.
POLISH_PHASES="gate" POLISH_MODE=final bash scripts/pod_setup_polish.sh >> "$LOGS/references-setup-$JOB.log" 2>&1 \
  || log "warning: pod_setup_polish.sh failed (see references-setup-$JOB.log)"
PY="${WENART_POLISH_PY:-/opt/wenart/venv-polish/bin/python}"
if ! "$PY" -c "import pyarrow" 2>/dev/null; then
  "$PY" -m pip install -q -c /opt/wenart/image-constraints.txt "pyarrow>=15" >> "$LOGS/references-setup-$JOB.log" 2>&1 \
    || "$PY" -m pip install -q "pyarrow>=15" >> "$LOGS/references-setup-$JOB.log" 2>&1
fi
export HF_HOME="${WENART_HF_HOME:-/opt/wenart/hf}" HF_HUB_OFFLINE=0
read -r -a FAMS <<< "${REF_FAMILIES:-scandinavian}"
read -r -a SPACES <<< "${REF_SPACES:-}"
log "families ${FAMS[*]}, ${REF_PER_SPACE:-30} per space, ${REF_SHARDS:-125} shard(s), spaces ${SPACES[*]:-all}"
rc=0
"$PY" -m wenart.style.references candidates --families "${FAMS[@]}" --per-space "${REF_PER_SPACE:-30}" \
  --shards "${REF_SHARDS:-125}" --root /workspace/references/candidates --out "$WENART_RESULTS/references_candidates" \
  ${SPACES[@]:+--spaces "${SPACES[@]}"} 2>&1 | tee -a "$LOGS/references-$JOB.log" || rc=$?
cp "$LOGS/references-$JOB.log" "$LOGS/references-setup-$JOB.log" "$WENART_RESULTS/" 2>/dev/null || true
log "done: exit $rc"
exit "$rc"
