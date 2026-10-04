#!/usr/bin/env bash
# Milestone 1 smoke job: GPU tests on the pod. Run by pod_entry.sh with the venv active.
set -Eeuo pipefail
cd /workspace/repo
python -m pytest -m gpu tests/gpu -v -ra --junitxml="$WENART_RESULTS/junit.xml" 2>&1 | tee "$WENART_RESULTS/pytest.txt"
exit "${PIPESTATUS[0]}"
