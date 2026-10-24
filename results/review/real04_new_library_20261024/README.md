# real04 with the new library and the group options 10x (23-24 Oct 2026)

User request of 23 Oct 2026: "after everything completed increase the group furniture options 10x (sofa set etc) then
run the real04 again with this new item library. In real04 there are 2 zemin kat in the DWG file use the one with
matching dimensions the bodrum kat (do not use the zemin kat bulging out)".

Pod `hpd4daiaklaefz` (RTX PRO 6000, EU-RO-1, $2.49/h), job `20261023-222215-full`, code 0f15dbe. Same job as this
morning's rerun (`results/review/real04_rerun_20261023/`): `scripts/jobs/full.sh`, `RUN_PROJECTS=real04`,
`RUN_POLISH=off`, `RENDER_SAMPLES=256`, 3 agent rounds, GPU tests.

What is new in this run:

- **Ground floor from r16**: the sheets stage took r16 (15.17 x 12.00 m, the size of the basement r11) as the L0
  plan and left the bulging r5 (17.17 x 12.00 m) out (`outline_mismatch` conflict `sc_002` in `sheets.json`:
  "r16 matches r11 of level L-1 and is read; r5 not used").
- **3D Warehouse layer** (relaxed licence mode): 44 of the 236 built furniture pieces and 18 of the 105 decor items
  use 3D Warehouse models; every one is credited in the run's `ATTRIBUTION.md` and its views say `commercial-safe:
  no`.
- **Group options 10x** (263 options): the AI-placed groups took a 1.40 m bed with nightstands, a 1.00 m wardrobe, a
  bookshelf with a plant, a narrow bookshelf and a bistro table with a plant on a terrace; the drawn groups were
  completed with the old options (the rule for drawn furniture).

## Files

| File | What |
|---|---|
| `contact_L-1.jpg`, `contact_L0.jpg`, `contact_L1.jpg` | all interior views per level |
| `contact_exterior_base.jpg`, `contact_exterior_l-1b-acik-mutfak.jpg`, `contact_variant_l-1b-acik-mutfak.jpg` | exterior views and the open-kitchen alternative |
| `sheets13/` | one before / after JPEG per view: before = Milestone 13 (`results/baseline/m13/`, the real04 run of 2799c88, the Milestone 13 final code), after = this run |
| `metrics13.md`, `metrics13.json` | the 17 metrics of `docs/milestone13.md` §7, before = Milestone 13, after = this run |
| `final_report_real04.md` | the run's final report |
| `pytest-full.txt` | GPU tests (45 passed, 2 failed, 9 skipped) |
| `gpu_check_values.json` | per-view values of the GPU checks |

## Results: Milestone 13 (before) against this run (after)

Your rule of 24 Oct 2026: every before / after is Milestone 13 against the run with the later changes. Before =
the real04 run of 2799c88 (the Milestone 13 final code, pod `udqp9w9972b08f`, committed as the baseline in
`results/baseline/m13/`); after = this run (0f15dbe: 3D Warehouse layer, group options 10x, ground floor from r16).

| # | Metric | Milestone 13 (2799c88) | This run (0f15dbe) | Target |
|---|---|---|---|---|
| | views (interior / exterior) | 42 (37 / 5) | 42 (37 / 5) | - |
| 1 | drawn anchors built | 40/40 | 40/40 | 100 % |
| 2 | drawn pieces built, without explained non-furniture | 98 % (190/194) | 98 % (186/190) | ≥ 90 % |
| 3 | pieces with `asset.method` none | 26 | 26 | 0 |
| 4 | parametric share; module pieces; grey boxes | 9 % (22/235); 22; 0 | 9 % (22/236); 20; 0 | ≤ 25 %; -; 0 |
| 5 | complete sets bath / bed / kitchen / living | 10/10, 8/8, 2/2, 0/4 | 10/10, 6/8, 2/2, 0/4 | ≥ 90 % |
| 6 | last round F8 / S2 > 3 cm / G10 / LG | 4 / 3 / 18 / 4 | 3 / 6 / 18 / 2 | ≤ 5 / ≤ 3 / - / ≤ 5 |
| 7 | accepted edits whose finding is gone | 91 % (10/11) | 74 % (14/19) | ≥ 60 % |
| 8 | top model share; distinct models; units unknown; library quality ≤ 3 | 5 %; 98; 6 %; 52 % (33/63) | 5 %; 114; 1 %; 36 % (17/47) | ≤ 15 %; ≥ 60; ≤ 10 %; ≤ 25 % |
| 9 | interior views at EV ≥ +5; EV gap lit vs daylight | 0/37; 0.17 | 0/37; 0.33 | 0; ≤ 2 |
| 10 | fabric colour applied | 3/20 | 1/20 | 100 % |
| 11 | trees; hedges; black pixels in the site view | 20/20; 4/4; 3.6 % | 21/21; 4/4; 3.5 % | 100 %; -; 0 % |
| 12 | exterior views rendered of planned | 5/7 | 5/7 (ext_4, ext_6 dropped) | all |
| 13 | views in halls or ≥ 50 % bare wall | 17/42 | 20/42 | ≤ 4 |
| 14 | `in_json_not_rendered` mismatches | 0 | 0 | 0 |
| 16 | commercial-safe line; flagged assets (missing in ATTRIBUTION) | 42/42; 18 (0) | 42/42; 26 (0) | 100 %; 0 |
| 17 | stage minutes, USD at $2.49/h | 87, $3.62 | 94, $3.89 | ≤ 150, ≤ $6.50 |

- Better: 16 more distinct library models (98 → 114), fewer models of unknown units (6 % → 1 %), fewer
  low-quality library pieces (52 % → 36 %), F8 and LG down.
- Worse: bedrooms 8/8 → 6/8 (the two 14 m² ground-floor bedrooms `yatak_odasi_3` and `_4`, read from r16 now,
  have one nightstand each); S2 > 3 cm 3 → 6; bare-wall views 9 → 12; accepted edits whose finding is gone 91 % →
  74 %; fabric colour 3/20 → 1/20 (more models without a recolourable fabric slot). This run's agent used the room
  briefs of 0f15dbe, which listed every offered option (up to 44 per group); 87abeca (pushed during the run) lists 5
  per group and counts the rest.

## GPU tests: 45 passed, 2 failed, 9 skipped

| Test | Failure |
|---|---|
| `test_look_m6.py::test_unverified_pieces_cast_no_colour[real04]` | white-balance tint beyond ±40: cam_r_L0_e_yatak_odasi_2 43.71, cam_r_L0_e_yatak_odasi_3 44.35 (this morning 42.97 / 42.6, the same two views) |
| `test_furnish.py::test_refit_library_models_fit_the_style[real04]` | f_L1_005 uses Poly Haven `round_wooden_table_02`, tagged classic / rustic, not the project style |

Both are of the same kind as this morning's failures and not caused by the new library or options. Not fixed.

## Pod

118 min, $4.90 (worst case $7.68 at the 185 min cap, kept under the $30 day limit, `--over-5-ok`); stopped and
terminated by the runner after the collection.
