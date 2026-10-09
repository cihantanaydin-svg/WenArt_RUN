#!/usr/bin/env bash
# Milestone 10 diagnostic job: what fills the network volume, and the end of an earlier job's logs. Read only: it
# never deletes or moves anything (deleting data needs the user's OK, CLAUDE.md). Run by scripts/pod_entry.sh:
#
#   scripts/gpu_run.py run --job scripts/jobs/volume_report.sh --gpu 'RTX PRO 4000' --max-minutes 20 --grace 300 \
#     --env REPORT_JOB=20261009-034343-prep --purpose "M10: volume usage and the L2b logs"
#
# Env: REPORT_JOB  an earlier job id whose logs are tailed (optional).
# Results ($WENART_RESULTS): volume_report.txt (df, du of the top folders), logs/<job>/ (the last 300 lines of the
# job's own log, its prep step logs and job.log; its prep_manifest.json and status.json).
set -Eeuo pipefail
trap 'echo "[volume_report] ERROR at line $LINENO" >&2' ERR
WS="${WENART_WS:-/workspace}"
RESULTS="${WENART_RESULTS:?WENART_RESULTS is set by pod_entry.sh}"
LOGS=$WS/logs
mkdir -p "$LOGS" "$RESULTS"
exec > >(tee -a "$LOGS/volume_report-${JOB_ID:-job}.log") 2>&1
OUT=$RESULTS/volume_report.txt
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
section() { echo; echo "== $*"; }
{
  echo "volume report $(ts)"
  section "df"
  df -h "$WS" /opt 2>/dev/null || true
  section "du -sh $WS/* (largest first)"
  timeout 600 du -sh "$WS"/* 2>/dev/null | sort -rh || true
  for d in prep prep/library prep/library-work prep/cache outputs outputs-prep assets jobs; do
    if [ -d "$WS/$d" ]; then
      section "du -sh $WS/$d/* (largest first)"
      timeout 300 du -sh "$WS/$d"/* 2>/dev/null | sort -rh | head -40 || true
    fi
  done
} > "$OUT" 2>&1
echo "[volume_report] $(ts) report written: $(wc -l < "$OUT") lines"
JOB="${REPORT_JOB:-}"
if [ -n "$JOB" ]; then
  if ! [[ "$JOB" =~ ^[A-Za-z0-9_.-]+$ ]]; then
    echo "[volume_report] REPORT_JOB '$JOB' is not a job id: ignored"
  else
    dst=$RESULTS/logs/$JOB
    mkdir -p "$dst"
    for f in "$LOGS/$JOB.log" "$WS/jobs/$JOB/job.log"; do
      [ -f "$f" ] && tail -n 300 "$f" > "$dst/$(basename "$(dirname "$f")")-$(basename "$f")" || true
    done
    if [ -d "$LOGS/prep-$JOB" ]; then
      mkdir -p "$dst/prep"
      for f in "$LOGS/prep-$JOB"/*.log; do
        [ -f "$f" ] && tail -n 300 "$f" > "$dst/prep/$(basename "$f")" || true
      done
    fi
    for f in "$WS/jobs/$JOB/status.json" "$WS/jobs/$JOB/results/prep_manifest.json"; do
      [ -f "$f" ] && cp -f "$f" "$dst/" || true
    done
    echo "[volume_report] $(ts) logs of $JOB: $(find "$dst" -type f | wc -l) file(s)"
  fi
fi
echo "[volume_report] $(ts) done"
