# real04 rerun on the latest code (23 Oct 2026)

User request of 23 Oct 2026: run real04 again on a pod with the latest changes. Pod `udqp9w9972b08f` (RTX PRO 6000,
EU-RO-1, $2.49/h), job `20261023-135954-full`, code 2799c88 (Milestone 13 final pass: windows-only interior sky
+3.5 stops as the default, final-pass fixes). Same job as P6a: `scripts/jobs/full.sh`, `RUN_PROJECTS=real04`,
`RUN_POLISH=off`, `RENDER_SAMPLES=256`, stored recognition answers reused, 3 agent rounds, GPU tests. No sky A/B.

## Files

| File | What |
|---|---|
| `contact_L-1.jpg`, `contact_L0.jpg`, `contact_L1.jpg` | all interior views per level |
| `contact_exterior_base.jpg`, `contact_exterior_l-1b-acik-mutfak.jpg`, `contact_variant_l-1b-acik-mutfak.jpg` | exterior views and the open-kitchen alternative |
| `sheets13/` | one before / after JPEG per view (before = committed M12 run, after = this run; same baseline as P6a's sheets) |
| `metrics13.md`, `metrics13.json` | the 17 metrics of `docs/milestone13.md` §7 (before = M12) |
| `final_report_real04.md` | the run's final report |
| `pytest-full.txt` | GPU tests (45 passed, 2 failed, 9 skipped) |
| `gpu_check_values.json` | per-view values of the olive, glazing and orange GPU checks |

## Results against M12 and P6a

| # | Metric | M12 | P6a (8e8cc97) | This run (2799c88) | Target |
|---|---|---|---|---|---|
| | views (interior / exterior) | 48 | 49 (43 / 6) | 42 (37 / 5) | - |
| 1 | drawn anchors built | 12/34 | 36/36 | 40/40 | 100 % |
| 2 | drawn pieces built, without explained non-furniture | 63 % | 97 % (192/198) | 98 % (190/194) | ≥ 90 % |
| 3 | pieces with `asset.method` none | 43 | 22 | 26 | 0 |
| 4 | parametric share; grey boxes | 33 %; - | 10 %; 0 | 9 %; 0 | ≤ 25 %; 0 |
| 5 | complete sets bath / bed / kitchen / living | 8/10, 4/8, 0/2, 0/4 | 10/10, 8/8, 2/2, 0/4 | 10/10, 8/8, 2/2, 0/4 | ≥ 90 % |
| 6 | last round F8 / S2 > 3 cm / G10 / LG | 38 / 1 / 18 / 66 | 4 / 1 / 18 / 6 | 4 / 3 / 18 / 4 | ≤ 5 / ≤ 3 / - / ≤ 5 |
| 7 | accepted edits whose finding is gone | 13 % | 91 % (30/33) | 91 % (10/11) | ≥ 60 % |
| 8 | library quality ≤ 3 | 12 % | 50 % | 52 % (33/63) | ≤ 25 % |
| 9 | interior views at EV ≥ +5; EV gap lit vs daylight | 9/44; - | 0/43; 0.67 | 0/37; 0.17 | 0; ≤ 2 |
| 10 | fabric colour applied | - | 3/20 | 3/20 | 100 % |
| 11 | trees; hedges; black pixels in the site view | -; -; 29.8 % | 20/20; 4/4; 3.6 % | 20/20; 4/4; 3.6 % | 100 %; -; 0 % |
| 12 | exterior views rendered of planned | 4 of ? | 6/8 | 5/7 (ext_4, ext_6 dropped) | all |
| 13 | views in halls or ≥ 50 % bare wall | 12/48 | 21/49 | 17/42 | ≤ 4 |
| 14 | `in_json_not_rendered` mismatches | 18 | 0 | 0 | 0 |
| 16 | commercial-safe line; flagged assets missing in ATTRIBUTION | 0/48 | 49/49; 0 | 42/42; 0 | 100 %; 0 |
| 17 | stage minutes, USD at $2.49/h | 122, $5.07 | 109, $4.53 | 87, $3.62 | ≤ 150, ≤ $6.50 |

Views missing against P6a (expected): the L1 koridor_2 and teras_2 views (6) are twins of koridor_1 / teras_1 again
and get no views of their own under `render.twin_rooms: one`; the agent's blank-wall `ext_front_entrance` no longer
passes the exterior camera rule (sky ≥ 3 %). Commercial-safe views: 11 of 42 (relaxed mode, HSSD).

Agent: 3 rounds, 16 findings removed by 18 accepted edits (16 predicted), 3 new, net 13, 138 rejected; critical /
major 1 / 88 in the last round.

## GPU tests: 45 passed, 2 failed, 9 skipped

| Test | Failure |
|---|---|
| `test_look_m6.py::test_unverified_pieces_cast_no_colour[real04]` | white-balance tint beyond ±40: cam_r_L0_e_yatak_odasi_2 42.97, cam_r_L0_e_yatak_odasi_3 42.6 |
| `test_furnish.py::test_refit_library_models_fit_the_style[real04]` | f_L0_043 uses abo_B07GFLG5MM, tagged "modern minimal / minimal", not the project style |

Not fixed in this run (the request was the run only).

## Pod

106 min, $4.40 (worst case $9.96 at the 4 h cap, `--over-5-ok`); stopped and terminated by the runner after the
collect. Project total $186.18 of $300. The full results (4,186 files, 271 MB) and the 3D files (`real04.blend`
411 MB, `real04.glb` 1.16 GB) are in the git-ignored `runs/20261023-135954-full/` of this session and on the network
volume (`jobs/20261023-135954-full/`).
