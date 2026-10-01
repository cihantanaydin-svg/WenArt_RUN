#!/usr/bin/env bash
# One-time setup on a RunPod pod. Idempotent and crash-safe: everything lands under
# /workspace (the Network Volume), each step is marked done only after it succeeded,
# so a pod killed mid-step redoes that step next time instead of trusting a half result.
# Base image: runpod/pytorch:1.4.0-cu1281-torch291-ubuntu2404 (torch 2.9.1 system-wide).
# Writes what it did into $WENART_RESULTS/setup.json when that variable is set.
set -Eeuo pipefail
trap 'echo "[setup] ERROR at line $LINENO" >&2' ERR
mkdir -p /workspace/logs /workspace/hf /workspace/tools /workspace/jobs
log() { echo "[$(date -u +%H:%M:%S)] setup: $*"; }
APT_STATE=reused; BLENDER_STATE=reused; VENV_STATE=reused
HERE="$(cd "$(dirname "$0")" && pwd)"

# --- OS packages (container disk, fast) ---------------------------------------
STAMP_APT=/var/lib/wenart-apt-done
if [ ! -f $STAMP_APT ]; then
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends git curl xz-utils ca-certificates \
    libxi6 libxxf86vm1 libxfixes3 libxrender1 libgl1 libxkbcommon0 libsm6 libice6 \
    libglib2.0-0 poppler-utils tesseract-ocr tesseract-ocr-tur >/dev/null
  touch $STAMP_APT
  APT_STATE=installed
  log "apt packages installed"
fi

# --- Blender 5.2.2 LTS (sha256 verified, extracted atomically, on the volume) ---
BL_VER=5.2.2
BL_SHA=84098912789dc450e95697c4184fb8a90acbe5111c2ba4aede3fecb57806a168
BL_DIR=/workspace/tools/blender-$BL_VER-linux-x64
if [ ! -f "$BL_DIR/.wenart-ok" ]; then
  log "downloading Blender $BL_VER"
  TAR=/workspace/tools/blender-$BL_VER-linux-x64.tar.xz
  STAGE=/workspace/tools/.blender-$BL_VER.partial
  curl -sSL --retry 3 -o "$TAR" "https://download.blender.org/release/Blender5.2/blender-$BL_VER-linux-x64.tar.xz"
  echo "$BL_SHA  $TAR" | sha256sum -c - >/dev/null
  rm -rf /workspace/tools/.blender-5.2.2.partial
  mkdir -p "$STAGE"
  tar -xJf "$TAR" -C "$STAGE"
  rm -rf /workspace/tools/blender-5.2.2-linux-x64
  mv "$STAGE/blender-$BL_VER-linux-x64" "$BL_DIR"
  rm -rf /workspace/tools/.blender-5.2.2.partial /workspace/tools/blender-5.2.2-linux-x64.tar.xz
  touch "$BL_DIR/.wenart-ok"
  BLENDER_STATE=installed
  log "Blender $BL_VER ready"
fi
ln -sfn "$BL_DIR" /workspace/tools/blender

# --- Python venv (reuses the image's torch via system site packages) ----------
# The stamp covers the requirements, the interpreter version and the image tag, so a
# changed base image rebuilds the venv instead of reusing one built for another python.
PYV=$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')
REQ_HASH=$( { cat "$HERE/pod_requirements.txt"; echo "$PYV"; echo "${WENART_IMAGE:-}"; } | sha256sum | cut -c1-16)
VENV=/workspace/venv
if [ ! -f "$VENV/.req-$REQ_HASH" ] || [ -e /workspace/venv.building ] || [ ! -x "$VENV/bin/python" ]; then
  if [ -e /workspace/venv.building ] || [ ! -x "$VENV/bin/python" ] || ! "$VENV/bin/python" -c "import sys" 2>/dev/null; then
    rm -rf /workspace/venv
  fi
  touch /workspace/venv.building
  [ -x "$VENV/bin/python" ] || python3 -m venv --system-site-packages "$VENV"
  "$VENV/bin/python" -m pip install -q --upgrade pip
  "$VENV/bin/python" -m pip install -q -r "$HERE/pod_requirements.txt"
  find /workspace/venv -maxdepth 1 -name '.req-*' -delete
  touch "$VENV/.req-$REQ_HASH"
  rm -f /workspace/venv.building
  VENV_STATE=installed
  log "venv updated"
fi

if [ -n "${WENART_RESULTS:-}" ]; then
  mkdir -p "$WENART_RESULTS"
  printf '{"apt": "%s", "blender": "%s", "venv": "%s", "python": "%s", "image": "%s"}\n' \
    "$APT_STATE" "$BLENDER_STATE" "$VENV_STATE" "$PYV" "${WENART_IMAGE:-}" > "$WENART_RESULTS/setup.json"
fi
log "done: python $PYV, blender $("$BL_DIR/blender" --version 2>/dev/null | head -1), apt=$APT_STATE blender=$BLENDER_STATE venv=$VENV_STATE"
