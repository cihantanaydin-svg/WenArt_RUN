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
| 2026-10-01 21:07 | bodeqlsdru5ws8 | NVIDIA RTX PRO 4000 Blackwell | 16 | 0.15 | M3 final renders after review fixes (thresholds, cameras, albedo), GPU tests | ok, self-stop ok |
| 2026-10-01 21:37 | i4h5dj2fdee5ys | NVIDIA RTX PRO 4000 Blackwell | 24 | 0.23 | M4: bake-off re-run with tiled symbol pass and LibreDWG 0.14.1 | exit 1, self-stop ok |
| 2026-10-01 22:24 | a1jrdpb5qxf2xz | NVIDIA RTX PRO 4000 Blackwell | 31 | 0.29 | M4 furnish: fit, AI layout (Qwen), decor, build with assets, renders, GPU tests | exit 1, self-stop ok |
| 2026-10-01 23:05 | ubfnmea29jobm5 | NVIDIA RTX PRO 4000 Blackwell | 38 | 0.37 | M4 furnish run 2: anchor-safe placer, library assets resolved, 128 samples, GPU tests | exit 1 (furnish tests), self-stop ok (reattached) |
| 2026-10-01 23:51 | mbiozud3c2dmfw | NVIDIA RTX PRO 4000 Blackwell | 37 | 0.35 | M4 furnish run 3: anchor-first placer, thin shower glass, 128 samples, GPU tests | ok, self-stop ok |
| 2026-10-01 23:55 | ju9pt0hh89dahn | NVIDIA RTX PRO 4000 Blackwell | 3 | 0.03 | M4 furnish run 4: review fixes (plants, camera boxes, corner-door walkways, allowed types), 128 samples, GPU tests | stopped by me after 3 min: library-asset UV bug found in run 3 previews, fixed before run 5 |
| 2026-10-02 00:37 | dn0gxnfxqtd5yr | NVIDIA RTX PRO 4000 Blackwell | 40 | 0.38 | M4 furnish run 5: review fixes + asset UV render layer, 128 samples, GPU tests | ok, self-stop ok |
| 2026-10-02 10:14 | 6js4pqqxk0j7of | NVIDIA RTX PRO 4500 Blackwell | 35 | 0.41 | M5 run 0 smoke: look synthetic-01, polish smoke 2 views x 4 settings, check 2 models | exit 1: polish could not load the tokenizer offline (fixed: local snapshot paths); setup 4.4 min, look 30 views ok, check 60 calls ok; self-stop ok |
| 2026-10-02 10:35 | dcpj3jtzhd8b4b | NVIDIA RTX PRO 4500 Blackwell | 20 | 0.24 | M5 run 0b smoke: polish path only (local snapshot loading fix), 2 views x 4 settings | ok: models load offline; 3.8 s/forward at 1920x1088, peak 22.5 GiB resident, 3 of 8 attempts gated in; gate slowed by CPU oversubscription (112 host threads); self-stop ok |
| 2026-10-02 13:51 | pending:20261002-135133-polish | RTX 4090 | 115 | 1.42 | M5 run 1a sweep: look both projects, controls, polish sweep (8 views x 10 + presumed-bad), gate calibration, sweep report | creating (provisional, worst case) |

**Total spent so far: $5.79** (budget: $100; limits: $1.00/GPU-hour, $10/day, 2 h/run)
