# GPU run log

Every RunPod pod run is logged here by `scripts/gpu_run.py` (and by hand if the
runner could not write it). Costs are estimates from the on-demand price at start.

| Date (UTC) | Pod ID | GPU | Minutes | Cost (USD) | Purpose | Result |
|---|---|---|---|---|---|---|
| 2026-10-01 12:07 | hnltxoyrkeqry4 | NVIDIA A40 | 7 | 0.05 | M1 smoke test, no volume | ok, self-stop ok |
| 2026-10-01 12:23 | mjc9fjlc771w3u | NVIDIA RTX PRO 4000 Blackwell | 10 | 0.10 | M1 smoke on volume, first run (installs) | ok, self-stop ok |
| 2026-10-01 12:28 | vlxccfsnjrosbb | NVIDIA RTX PRO 4000 Blackwell | 5 | 0.05 | M1 smoke on volume, second run (must skip install) | ok, self-stop ok |
| 2026-10-01 15:13 | 5ge4m2jbfysiue | NVIDIA RTX PRO 4000 Blackwell | 62 | 0.59 | M2 recognition bake-off (setup, downloads, OCR, 2 VLMs) | stopped by me: pip install of vLLM stalled on the network volume |
| 2026-10-01 15:35 | nrxzbuon1dgho7 | NVIDIA RTX PRO 4000 Blackwell | 21 | 0.20 | M2 recognition bake-off, container-disk layout | exit 1, self-stop ok |
| 2026-10-01 16:00 | ib8rk52cos62l2 | NVIDIA RTX PRO 4000 Blackwell | 25 | 0.24 | M2 recognition bake-off, run 3 (stage trap fixed) | exit 1, self-stop ok |
| 2026-10-01 16:28 | 81v79dcc2d335t | NVIDIA RTX PRO 4000 Blackwell | 28 | 0.27 | M2 recognition bake-off, run 4 (fp8, 8192 ctx, sampler fix, OCR CPU fallback) | exit 1, self-stop ok |
| 2026-10-01 17:28 | z9zsnvqjme4xt1 | NVIDIA L4 | 16 | 0.13 | M2 verification run (review fixes, GPU tests before vLLM) | exit 1, self-stop ok |
| 2026-10-01 18:35 | yydldegr7x1xi8 | NVIDIA L4 | 20 | 0.16 | M3 renders: 3 synthetic projects, 3 views per room, 128 samples | exit 1, self-stop ok |
| 2026-10-01 18:50 | eeypik8qo2n5mn | NVIDIA RTX PRO 4000 Blackwell | 14 | 0.13 | M3 renders: synthetic-01 and -03 with their own styles, full result collection | ok, self-stop ok |

**Total spent so far: $1.92** (budget: $100; limits: $1.00/GPU-hour, $10/day, 2 h/run)
