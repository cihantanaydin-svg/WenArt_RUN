#!/usr/bin/env bash
# Job: upload the 3D files already on the network volume (outputs/<p>/export/*.blend, *.glb) to Google Drive
# (user request of 10 Oct 2026). No GPU work; the cheapest pod is enough.
#
#   scripts/gpu_run.py run --job scripts/jobs/drive_upload.sh --drive-upload --max-minutes 20 \
#     --env DRIVE_PROJECTS='real02 real01 synthetic-01' --purpose "upload the 3D files to Google Drive"
set -Eeuo pipefail
trap 'echo "[drive_upload job] ERROR at line $LINENO"; exit 1' ERR

WS="${WENART_WS:-/workspace}"
mkdir -p "$WS/logs"
OUTPUTS="${WENART_OUTPUTS:-$WS/repo/outputs}"
read -r -a PROJECTS <<< "${DRIVE_PROJECTS:-}"
if [ "${#PROJECTS[@]}" -eq 0 ]; then echo "[drive_upload job] set DRIVE_PROJECTS"; exit 2; fi
bash "$WS/repo/scripts/drive_upload.sh" "$OUTPUTS" "${PROJECTS[@]}"
mkdir -p "${WENART_RESULTS:-$WS/jobs/drive_upload/results}"
cp -f "$WS"/logs/drive-upload-*.log "${WENART_RESULTS:-$WS/jobs/drive_upload/results}/" 2>/dev/null || true
