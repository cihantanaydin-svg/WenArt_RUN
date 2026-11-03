#!/usr/bin/env bash
# Inspect a zip of 3D models from the user's Google Drive before it joins the library (the user's request of 3 Nov
# 2026: "There is a beds.zip file in Google Drive, take a look inside and tell me if we can use the models inside in
# the projects. Disregard the licence things for now"). The cloud session's proxy refuses drive.google.com and
# drive.usercontent.google.com, so the pod downloads the file (it must be shared as "anyone with the link":
# drive.usercontent.google.com with confirm=t, the form wenart.assets.warehouse uses), then
# python -m wenart.assets.zip_inspect run: every member listed, non-GLB models converted in Blender, each model typed,
# measured (unit and up axis against the type's real size range), fixed up, rendered from the front and the back,
# contact sheets and report.md / inspect.csv / inspect.json in the results. Nothing joins the catalogue; nothing on
# the volume is deleted; a second run resumes (the zip by size, the extracted files by size).
#
#   python3 scripts/gpu_run.py run --job scripts/jobs/zip_inspect.sh --max-minutes 45 \
#     --env ZIP_FILE_ID=1iYSSFbHkn1DH2qtAJ7LF44bZccQ_SYwL --env ZIP_BYTES=462846689 --env ZIP_NAME=beds.zip \
#     --env ZIP_TYPES=bed_single,bed_double --purpose "inspect beds.zip from Google Drive (user request)"
#
# Env: ZIP_FILE_ID (required), ZIP_BYTES (the Drive size; checked when given), ZIP_NAME (file name on the volume),
# ZIP_TYPES (expected types, comma-separated), ZIP_RENDER_MIN (render budget, minutes; default 25).
set -Eeuo pipefail
trap 'echo "[zip_inspect] ERROR at line $LINENO" >&2' ERR
WS="${WENART_WS:-/workspace}"
RESULTS="${WENART_RESULTS:?WENART_RESULTS is set by pod_entry.sh}"
LOGS=$WS/logs
mkdir -p "$LOGS" "$RESULTS"
exec > >(tee -a "$LOGS/zip_inspect-${JOB_ID:-job}.log") 2>&1
ts() { date -u +%Y-%m-%dT%H:%M:%SZ; }
PY="${WENART_PY:-$WS/venv/bin/python}"
export WENART_BLENDER="${WENART_BLENDER:-$WS/tools/blender/blender}"
FILE_ID="${ZIP_FILE_ID:?ZIP_FILE_ID is required}"
if ! [[ "$FILE_ID" =~ ^[A-Za-z0-9_-]+$ ]]; then echo "[zip_inspect] ZIP_FILE_ID is not a Drive id"; exit 2; fi
NAME="${ZIP_NAME:-$FILE_ID.zip}"
NAME="$(basename "$NAME")"
BYTES="${ZIP_BYTES:-}"
TYPES="${ZIP_TYPES:-}"
RENDER_MIN="${ZIP_RENDER_MIN:-25}"
ROOT=$WS/library/inbox/$FILE_ID
ZIP=$ROOT/$NAME
FAST=/opt/wenart/zip_inspect/$FILE_ID          # container disk: fast, wiped with the pod
mkdir -p "$ROOT" "$FAST"

have=$(stat -c %s "$ZIP" 2>/dev/null || echo 0)
if [ -n "$BYTES" ] && [ "$have" = "$BYTES" ]; then
  echo "[zip_inspect] $(ts) $NAME already on the volume ($have bytes)"
else
  URL="https://drive.usercontent.google.com/download?id=$FILE_ID&export=download&confirm=t"
  echo "[zip_inspect] $(ts) downloading $NAME"
  for i in 1 2 3 4; do
    if curl -fL --retry 3 -C - -o "$ZIP" "$URL"; then break; fi
    echo "[zip_inspect] download attempt $i failed"; sleep $((2 ** i))
  done
  have=$(stat -c %s "$ZIP" 2>/dev/null || echo 0)
  echo "[zip_inspect] $(ts) downloaded $have bytes"
  if [ -n "$BYTES" ] && [ "$have" != "$BYTES" ]; then
    echo "[zip_inspect] size $have != Drive size $BYTES (is the file shared as 'anyone with the link'?)"
    head -c 600 "$ZIP" | tr -cd '[:print:]\n' | head -20 || true
    exit 3
  fi
fi
if [ "$(head -c 2 "$ZIP")" != "PK" ]; then echo "[zip_inspect] $NAME is not a zip"; exit 3; fi

# Assimp (BSD-3) converts 3DS, which Blender 5.2 no longer imports without an extension; best effort
if ! command -v assimp >/dev/null 2>&1; then
  apt-get install -y -qq --no-install-recommends assimp-utils >/dev/null 2>&1 \
    || { apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq --no-install-recommends assimp-utils >/dev/null 2>&1; } \
    || echo "[zip_inspect] assimp-utils could not be installed: 3DS files go to Blender only"
fi
command -v assimp >/dev/null 2>&1 && echo "[zip_inspect] $(assimp version 2>/dev/null | head -3 | tr '\n' ' ')"

# the zip itself stays on the volume; the extraction and the fixed GLBs go to the fast container disk
"$PY" -m wenart.assets.zip_inspect run --zip "$ZIP" --work "$FAST" --out "$RESULTS/zip_inspect" \
  --types "$TYPES" --blender "$WENART_BLENDER" --render-minutes "$RENDER_MIN"
cp -f "$FAST"/blender_*.log "$RESULTS/zip_inspect/" 2>/dev/null || true
cp -f "$FAST"/blender_*_result.json "$RESULTS/zip_inspect/" 2>/dev/null || true
echo "[zip_inspect] $(ts) done"
