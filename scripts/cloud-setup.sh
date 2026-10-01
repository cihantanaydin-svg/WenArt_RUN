#!/bin/bash
# Setup script for the Claude Code cloud environment (CPU only, no GPU work here).
# Paste into: claude.ai/code -> environment settings -> Setup script. Must finish in < 5 minutes.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y -qq poppler-utils tesseract-ocr tesseract-ocr-tur libgl1 libglib2.0-0 >/dev/null
python3 -m pip install -q --user \
  ezdxf==1.4.4 pdfplumber==0.11.10 pypdfium2==5.13.0 shapely==2.1.2 \
  opencv-python-headless pillow numpy pyyaml jsonschema pytest reportlab matplotlib
echo "cloud setup done"
