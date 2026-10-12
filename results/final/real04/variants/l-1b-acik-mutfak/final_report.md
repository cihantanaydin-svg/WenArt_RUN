# Final report: l-1b-acik-mutfak

Status: **not_rendered**: no renders in this run. `renders/render_manifest.json` was not found, so this report has no view to show.

This run stopped the project before its renders: build failed (exit 1: Error: script failed, file: '/workspace/repo/wenart/blender/build.py', exiting.). A `failed` stage has its log in `run/logs/<stage>.log` on the volume.

0 views: 0 polished, 0 Cycles (none). Stages: render not_run, gate validation not_run, polish not_run, vision check not_run (calibration not_run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 0 |
| interior / exterior views | 0 / 0 |
| variant | l-1b-acik-mutfak |
| polished | 0 |
| Cycles | 0 (none) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 0 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 3 |
| exposure | - |
| window pull | - |
| camera policy | - |
| camera score (min / mean / max) | - |
| rooms by number of views | - |
| gate validation | not recorded |
| seconds: build / render / metering | - / - / - |
| seconds: polish / gate / check | - / - / - |
| brief polish | yes |
| unit system | - |
| side-by-side sheets | 0 |

## Advisory flags and open items

- polish not run (every view is the Cycles render)
- vision check not run
- AI completion: 9 proposal(s) refused, reverted or not placed (listed per room)

## Gate validation

Not recorded: the gate calibration and validation did not run.

## Side-by-side sheets (Cycles | polished)

None: the polish did not run in this run.

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

None.

## Mismatches (never auto-fixed)

Not computed: the vision check and the expected lists did not run.

## Needs review

None.

## Building JSON: unverified items and conflicts

Status: -.

Unverified items:

None.

Drawn pieces left for review (untyped, not built; docs/milestone12.md §4.1):

None.

Drawn symbols read as not furniture (never built): none.

Library models kept with a vision doubt (user decision 1a; the room critic and the final check look at them):

None.

Conflicts:

None.

## This report: variant `l-1b-acik-mutfak`

An alternative's sub-output: it renders the rooms its plan changes, and its exterior views only when its outside differs from the base. The sheets and the other variants are in the base project's report (`../../final/final_report.md`). The base exterior views of this run: not known yet (see the base report).

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 23 piece(s) added, 12 wall cabinet run(s).

### Salon (r_L-1_salon, living): completed

- added f_L-1_089: bookshelf 1.00 x 0.35 (confidence -, rule)
- not placed dining: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_021, f_L-1_024, f_L-1_027, f_L-1_028, f_L-1_029, f_L-1_030, f_L-1_031, f_L-1_032, f_L-1_033, f_L-1_034, f_L-1_035, f_L-1_036, f_L-1_037, f_L-1_049, f_L-1_059, f_L-1_060, f_L-1_063, f_L-1_064, f_L-1_070, f_L-1_071, f_L-1_075, f_L-1_077, f_L-1_087

### Salon (r_L-1_salon_2, living): mirrored (decisions of r_L-1_salon (twin), not asked again)

- added f_L-1_094: bookshelf 1.00 x 0.35 (confidence -, rule, mirrored from f_L-1_089)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_022, f_L-1_023, f_L-1_038, f_L-1_039, f_L-1_040, f_L-1_041, f_L-1_042, f_L-1_043, f_L-1_044, f_L-1_045, f_L-1_046, f_L-1_047, f_L-1_048, f_L-1_050, f_L-1_057, f_L-1_058, f_L-1_065, f_L-1_066, f_L-1_069, f_L-1_072, f_L-1_076, f_L-1_078, f_L-1_088

### Mutfak (r_L-1_mutfak, kitchen): completed (nothing fits: kitchen_run: no place passes the checks; dining: no place passes the checks)

- 3 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no place passes the checks)
- not placed dining: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_001, f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_005, f_L-1_008, f_L-1_009, f_L-1_067, f_L-1_081, f_L-1_083, f_L-1_085

### Mutfak (r_L-1_mutfak_2, kitchen): mirrored (decisions of r_L-1_mutfak (twin), not asked again)

- 3 wall cabinet run(s) over the drawn counter
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_010, f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_014, f_L-1_017, f_L-1_018, f_L-1_068, f_L-1_082, f_L-1_084, f_L-1_086

### Koridor (r_L-1_koridor, hall): mirrored (decisions of r_L-1_koridor_2 (twin), not asked again)

- added f_L-1_098: shoe_cabinet 0.60 x 0.30 (confidence -, rule, mirrored from f_L-1_093)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_020

### Koridor (r_L-1_koridor_2, hall): completed

- added f_L-1_093: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_019

### Banyo (r_L-1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_026, f_L-1_051, f_L-1_056

### Banyo (r_L-1_banyo_2, bathroom): mirrored (decisions of r_L-1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_025, f_L-1_052, f_L-1_055

### Salon (r_L-1b_salon, living): completed (nothing fits: kitchen_run: no candidate position fits the room)

- 3 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_002, f_L-1b_009, f_L-1b_010, f_L-1b_012, f_L-1b_013, f_L-1b_014, f_L-1b_026, f_L-1b_027, f_L-1b_028, f_L-1b_029, f_L-1b_030, f_L-1b_031, f_L-1b_032, f_L-1b_033, f_L-1b_034, f_L-1b_040, f_L-1b_046, f_L-1b_049, f_L-1b_050, f_L-1b_051, f_L-1b_052, f_L-1b_053, f_L-1b_054, f_L-1b_055, f_L-1b_056, f_L-1b_064, f_L-1b_068, f_L-1b_070

### Salon (r_L-1b_salon_2, living): completed (nothing fits: kitchen_run: no candidate position fits the room; partner r_L-1b_salon (twin) not used: the twin's drawn furniture does not map onto this room: drawn unknown f_L-1b_046 has no counterpart here; completed itself)

- 3 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_001, f_L-1b_003, f_L-1b_004, f_L-1b_006, f_L-1b_007, f_L-1b_008, f_L-1b_017, f_L-1b_018, f_L-1b_019, f_L-1b_020, f_L-1b_021, f_L-1b_022, f_L-1b_023, f_L-1b_024, f_L-1b_025, f_L-1b_039, f_L-1b_045, f_L-1b_047, f_L-1b_048, f_L-1b_057, f_L-1b_058, f_L-1b_059, f_L-1b_060, f_L-1b_061, f_L-1b_062, f_L-1b_063, f_L-1b_067, f_L-1b_069

### Koridor (r_L-1b_koridor, hall): completed

- added f_L-1b_082: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_016

### Koridor (r_L-1b_koridor_2, hall): mirrored (decisions of r_L-1b_koridor (twin), not asked again)

- added f_L-1b_086: shoe_cabinet 0.60 x 0.30 (confidence -, rule, mirrored from f_L-1b_082)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_015

### Banyo (r_L-1b_banyo, bathroom): copied (decisions of r_L-1_banyo (same_as), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_036, f_L-1b_038, f_L-1b_044

### Banyo (r_L-1b_banyo_2, bathroom): copied (decisions of r_L-1_banyo_2 (same_as), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_035, f_L-1b_037, f_L-1b_043

### Yatak Odası (r_L0_yatak_odasi, bedroom): completed

- added f_L0_049: nightstand 0.40 x 0.40 (confidence -, rule)
- added f_L0_050: nightstand 0.40 x 0.40 (confidence -, rule)
- added f_L0_051: desk 1.20 x 0.60 (confidence -, rule)
- added f_L0_052: office_chair 0.60 x 0.60 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_017, f_L0_024, f_L0_026, f_L0_038

### E.yatak Odası (r_L0_e_yatak_odasi, bedroom): completed (nothing fits: storage: no candidate position fits the room; work: no place passes the checks)

- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- not placed work: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_007, f_L0_019, f_L0_029, f_L0_030

### E.yatak Odası (r_L0_e_yatak_odasi_2, bedroom): mirrored (decisions of r_L0_e_yatak_odasi (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_008, f_L0_020, f_L0_031, f_L0_032

### Yatak Odası (r_L0_yatak_odasi_2, bedroom): completed (partner r_L0_yatak_odasi (twin) not used: 2 of 4 copied pieces fail a check here (office_chair: the copy fails doors_free here; desk: the copy fails doors_free here); completed itself)

- added f_L0_053: nightstand 0.40 x 0.40 (confidence -, rule)
- added f_L0_054: nightstand 0.40 x 0.40 (confidence -, rule)
- added f_L0_055: desk 1.20 x 0.60 (confidence -, rule)
- added f_L0_056: office_chair 0.60 x 0.60 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_018, f_L0_021, f_L0_025, f_L0_040

### E.banyo (r_L0_e_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_006, f_L0_011, f_L0_013

### E.banyo (r_L0_e_banyo_2, bathroom): mirrored (decisions of r_L0_e_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_004, f_L0_012, f_L0_014

### Yatak Odası (r_L0_yatak_odasi_3, bedroom): mirrored (decisions of r_L0_yatak_odasi_4 (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_022, f_L0_035, f_L0_036, f_L0_039, f_L0_042, f_L0_045

### Merdiven (r_L0_merdiven, hall): completed (nothing fits: entrance: no candidate position fits the room)

- not placed entrance: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001

### Merdiven (r_L0_merdiven_2, hall): mirrored (decisions of r_L0_merdiven (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_002

### Yatak Odası (r_L0_yatak_odasi_4, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_009, f_L0_023, f_L0_033, f_L0_034, f_L0_037, f_L0_041, f_L0_046

### Banyo (r_L0_banyo, bathroom): completed (nothing fits: bathroom_set: no candidate position fits the room)

- not placed bathroom_set: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_003, f_L0_016, f_L0_043

### Banyo (r_L0_banyo_2, bathroom): mirrored (decisions of r_L0_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_005, f_L0_015, f_L0_044

### Teras (r_L1_teras, balcony): completed

- added f_L1_040: table_dining 0.70 x 0.70 (confidence -, rule)
- added f_L1_041: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_042: chair 0.45 x 0.45 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_022

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi, other): completed

- added f_L1_043: desk 1.20 x 0.60 (confidence -, rule)
- added f_L1_044: office_chair 0.60 x 0.60 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_009, f_L1_033, f_L1_034

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): completed (partner r_L1_oyun_aktivite_ve_dinlenme_odasi (twin) not used: the twin's drawn furniture does not map onto this room: drawn unknown f_L1_033 has no counterpart here; completed itself)

- added f_L1_047: desk 1.20 x 0.60 (confidence -, rule)
- added f_L1_048: office_chair 0.60 x 0.60 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_006, f_L1_010, f_L1_035, f_L1_036

### Koridor (r_L1_koridor, hall): completed

- added f_L1_045: console_table 0.90 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_021, f_L1_023

### Koridor (r_L1_koridor_2, hall): completed

- added f_L1_046: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_024, f_L1_025, f_L1_026

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_007, f_L1_013, f_L1_019

### Banyo (r_L1_banyo_2, bathroom): mirrored (decisions of r_L1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_008, f_L1_014, f_L1_020

## Units

No building JSON: unknown.

## Recognition (AI typing and raster labels)

No building JSON.

## Site

Recorded, not built.

None.

## Separators

None.

## Assumed values

None.

## Rooms mixing polished and Cycles views

None.

## Models and licences

No AI model ran for this report (polish and vision check not run).

## Attribution

No CC BY or Objaverse model in this project (Poly Haven CC0 models and parametric meshes need no credit).

## Added-object detector

Not run: the vision check did not run.

## Stages

This run (`20261011-153030-full-20261011T153556Z`):

| stage | status | seconds | note |
|---|---|---|---|
| build | failed | 2.6 min | exit 1: Error: script failed, file: '/workspace/repo/wenart/blender/build.py', exiting. |

The report stage itself is recorded after this report.

## Warnings

- project inputs not fully readable (FileNotFoundError: [Errno 2] No such file or directory: '/workspace/repo/outputs/real04/variants/l-1b-acik-mutfak/scene/scene_manifest.json'); brief not loaded, polish permission taken as the default (true)
- scene/scene_manifest.json not readable: no element table or building
- renders/render_manifest.json not found: no rendered views
