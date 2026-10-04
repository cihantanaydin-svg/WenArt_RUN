#!/bin/bash
# Setup script for the Claude Code cloud environment (CPU only, no GPU work here).
# Paste into: claude.ai/code -> environment settings -> Setup script. Must finish in < 5 minutes.
#
# LibreDWG 0.14 (docs/milestone7.md §5.1): when git, cmake and ninja exist, the same static build as the pod's
# (tag 0.14 = commit d9468ae, scripts/pod_setup_recognition.sh part libredwg) goes into
# ~/.cache/wenart/libredwg/bin (about 3 min on 4 cores, once: reused while VERSION matches and dwg2dxf runs).
# wenart/ingest/dwg.py finds it there; the DWG tests (tests/test_dwg.py) need it. A failed build is reported and
# does not fail the setup (the DWG tests then skip; the pods still build their own).
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y -qq poppler-utils tesseract-ocr tesseract-ocr-tur libgl1 libglib2.0-0 >/dev/null
python3 -m pip install -q --user \
  ezdxf==1.4.4 pdfplumber==0.11.10 pypdfium2==5.13.0 shapely==2.1.2 \
  opencv-python-headless==5.0.0.93 pillow==12.3.0 numpy==2.4.6 pyyaml jsonschema pytest reportlab \
  matplotlib==3.11.2

LIBREDWG_GIT=https://github.com/LibreDWG/libredwg.git
LIBREDWG_TAG=0.14
LIBREDWG_COMMIT=d9468ae948b8f07a08efa756c19f8916052358c0
LIBREDWG_VERSION_STRING="0.14 d9468ae"
LIBREDWG_HOME="$HOME/.cache/wenart/libredwg"
LIBREDWG_BIN="$LIBREDWG_HOME/bin"
LIBREDWG_SRC="$LIBREDWG_HOME/src"

libredwg_usable() {
  local tool
  for tool in dwg2dxf dwgread dxf2dwg; do
    [ -x "$LIBREDWG_BIN/$tool" ] || return 1
  done
  [ "$(head -1 "$LIBREDWG_BIN/VERSION" 2>/dev/null)" = "$LIBREDWG_VERSION_STRING" ] || return 1
  "$LIBREDWG_BIN/dwg2dxf" --help >/dev/null 2>&1 || return 1
}

build_libredwg() {
  rm -rf "$LIBREDWG_SRC"
  mkdir -p "$LIBREDWG_HOME"
  git clone --quiet --depth 1 --branch "$LIBREDWG_TAG" "$LIBREDWG_GIT" "$LIBREDWG_SRC" || return 1
  [ "$(git -C "$LIBREDWG_SRC" rev-parse HEAD)" = "$LIBREDWG_COMMIT" ] || { echo "LibreDWG: unexpected commit"; return 1; }
  git -C "$LIBREDWG_SRC" submodule update --init --depth 1 jsmn >/dev/null 2>&1 || return 1
  cmake -S "$LIBREDWG_SRC" -B "$LIBREDWG_SRC/build" -G Ninja -DCMAKE_BUILD_TYPE=Release -DDISABLE_WERROR=ON \
    -DENABLE_LTO=OFF -DBUILD_SHARED_LIBS=OFF >/dev/null || return 1
  ninja -C "$LIBREDWG_SRC/build" dwg2dxf dwgread dxf2dwg >/dev/null || return 1
  mkdir -p "$LIBREDWG_BIN"
  install -m 0755 "$LIBREDWG_SRC/build/dwg2dxf" "$LIBREDWG_SRC/build/dwgread" "$LIBREDWG_SRC/build/dxf2dwg" \
    "$LIBREDWG_BIN/" || return 1
  echo "$LIBREDWG_VERSION_STRING" > "$LIBREDWG_BIN/VERSION"
  rm -rf "$LIBREDWG_SRC"
  libredwg_usable
}

if libredwg_usable; then
  echo "LibreDWG $LIBREDWG_VERSION_STRING already in $LIBREDWG_BIN"
elif command -v git >/dev/null && command -v cmake >/dev/null && command -v ninja >/dev/null; then
  if build_libredwg; then
    echo "LibreDWG $LIBREDWG_VERSION_STRING built into $LIBREDWG_BIN"
  else
    echo "LibreDWG build failed: DWG tests will skip"
  fi
else
  echo "LibreDWG not built (git, cmake or ninja missing): DWG tests will skip"
fi
echo "cloud setup done"
