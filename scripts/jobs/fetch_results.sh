#!/usr/bin/env bash
# Fetch an earlier job's results from the network volume (Milestone 13, 22 Oct 2026).
# Run by scripts/pod_entry.sh on a RunPod pod (cwd /workspace/repo; WENART_RESULTS and JOB_ID set).
#
# What: copies /workspace/jobs/$FETCH_JOB/results/ (and that job's status.json and job.log as fetched_status.json and
# fetched_job.log) into this job's results folder, so the runner collects them as usual.
# Why: a pod that stopped itself at its job's end while no runner was attached (the session's container restarted)
# keeps its results only on the volume; 'gpu_run.py attach' then finds the pod EXITED and cannot download them.
# How: a plain copy, nothing is moved or deleted on the volume; FETCH_SKIP_3D=1 leaves out the 3D files
# (final/<p>/3d/). Idempotent: a second run copies the same files again.
#
# Usage: python3 scripts/gpu_run.py run --job scripts/jobs/fetch_results.sh --max-minutes 30 \
#          --env FETCH_JOB=<job id> --purpose "fetch the results of job <job id> from the volume"
set -Eeuo pipefail

WS="${WENART_WS:-/workspace}"
LOGS=$WS/logs
JOB="${JOB_ID:-fetch_results}"
mkdir -p "$LOGS"
LOG=$LOGS/fetch_results-$JOB.log
exec > >(tee -a "$LOG") 2>&1
trap 'echo "[$(date -u +%H:%M:%S)] fetch_results: error at line $LINENO (exit $?)"' ERR

SRC_JOB="${FETCH_JOB:-}"
RESULTS="${WENART_RESULTS:-$WS/jobs/$JOB/results}"
if [ -z "$SRC_JOB" ]; then echo "fetch_results: FETCH_JOB=<job id> is required"; exit 2; fi
case "$SRC_JOB" in */*|..*) echo "fetch_results: bad job id '$SRC_JOB'"; exit 2;; esac
SRC=$WS/jobs/$SRC_JOB
if [ ! -d "$SRC/results" ]; then echo "fetch_results: no $SRC/results on the volume"; exit 3; fi
mkdir -p "$RESULTS"

echo "[$(date -u +%H:%M:%S)] fetch_results: copying $SRC/results -> $RESULTS ($(du -sh "$SRC/results" | cut -f1))"
if [ "${FETCH_SKIP_3D:-0}" = "1" ]; then
  tar -C "$SRC/results" --exclude='./final/*/3d' -cf - . | tar -C "$RESULTS" -xf -
else
  cp -a "$SRC/results/." "$RESULTS/"
fi
for f in status.json job.log; do
  if [ -f "$SRC/$f" ]; then cp -a "$SRC/$f" "$RESULTS/fetched_$f"; fi
done
if [ -f "$LOGS/$SRC_JOB.log" ]; then cp -a "$LOGS/$SRC_JOB.log" "$RESULTS/fetched_pod_entry.log"; fi
echo "[$(date -u +%H:%M:%S)] fetch_results: $(find "$RESULTS" -type f | wc -l) files in $RESULTS"
