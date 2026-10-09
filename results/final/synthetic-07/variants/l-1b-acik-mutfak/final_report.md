# Final report: synthetic-07

3 views: 2 polished, 1 Cycles (check_incomplete 1). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 3 |
| interior / exterior views | 3 / 0 |
| variant | l-1b-acik-mutfak |
| polished | 2 |
| Cycles | 1 (check_incomplete 1) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 0 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 1 |
| advisory | yes |
| advisory flags | 7 |
| exposure | +8.00 .. +8.00 EV (3 at a limit), modes auto |
| window pull | 3 view(s), -1 .. -1 EV |
| camera policy | search 3 |
| camera score (min / mean / max) | 3.41 / 3.48 / 3.57 |
| rooms by number of views | 1 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 86.9 s / 10.6 s / 4.5 s |
| seconds: polish / gate / check | 15.3 s / 3.8 s / 3.3 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 1 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [synthetic-07-l-1b-acik-mutfak.blend](3d/synthetic-07-l-1b-acik-mutfak.blend) | 128.8 MB |
| [synthetic-07-l-1b-acik-mutfak.glb](3d/synthetic-07-l-1b-acik-mutfak.glb) | 287.9 MB |

3 cameras; textures scaled to at most 1024 px (140 scaled) for the download.

## Advisory flags and open items

- vision check advisory: removal_flagged 0.6667 misses >= 0.8; removal_confirmed 0.0 misses >= 0.6; insertion 0.0 misses >= 0.6; decoy_accept[qwen] 0.3333 misses <= 0.1
- check target missed: removal_flagged 0.667 (needs >= 0.8)
- check target missed: removal_confirmed 0.000 (needs >= 0.6)
- check target missed: insertion 0.000 (needs >= 0.6)
- check target missed: decoy_accept[qwen] 0.333 (needs <= 0.1)
- elevation check: 2 facade(s) differ from the drawn elevation; roof heights ok
- AI completion: 5 proposal(s) refused, reverted or not placed (listed per room)

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 100.0 % (limit 95 %), 64 comparisons |
| negative controls rejected | 97.7 % (limit 90 %), 176 comparisons |
| effect | polish allowed |

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L-1b: [contact_L-1b.jpg](contact_L-1b.jpg)

## Side-by-side sheets (Cycles | polished)

Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the last attempt the gate saw) with the gate decision, both check verdicts and the final decision.

- r_L-1b_salon_acik_mutfak: [contact_sbs_r_L-1b_salon_acik_mutfak.jpg](contact_sbs_r_L-1b_salon_acik_mutfak.jpg)

| room | view | polish attempt | gate | check Cycles | check polished | detector | final |
|---|---|---|---|---|---|---|---|
| r_L-1b_salon_acik_mutfak | cam_r_L-1b_salon_acik_mutfak_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1b_salon_acik_mutfak | cam_r_L-1b_salon_acik_mutfak_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | cycles (check_incomplete) |
| r_L-1b_salon_acik_mutfak | cam_r_L-1b_salon_acik_mutfak_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1b_salon_acik_mutfak_1 | r_L-1b_salon_acik_mutfak | L-1b | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +8.00 (limit) | -1 | search 3.57 | D4 A4 | 0 | no | [preview](cam_r_L-1b_salon_acik_mutfak_1_final_preview.jpg) [plan](cam_r_L-1b_salon_acik_mutfak_1_plan.jpg) |
| cam_r_L-1b_salon_acik_mutfak_2 | r_L-1b_salon_acik_mutfak | L-1b | cycles | check_incomplete | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +8.00 (limit) | -1 | search 3.45 | D4 A5 | 0 | no | [preview](cam_r_L-1b_salon_acik_mutfak_2_final_preview.jpg) [plan](cam_r_L-1b_salon_acik_mutfak_2_plan.jpg) |
| cam_r_L-1b_salon_acik_mutfak_3 | r_L-1b_salon_acik_mutfak | L-1b | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +8.00 (limit) | -1 | search 3.41 | D4 A4 | 0 | no | [preview](cam_r_L-1b_salon_acik_mutfak_3_final_preview.jpg) [plan](cam_r_L-1b_salon_acik_mutfak_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L-1b_hol | hall | L-1b | 0 | 0 | 0 | - |
| r_L-1b_salon_acik_mutfak | living | L-1b | 3 | 2 | 1 | cam_r_L-1b_salon_acik_mutfak_1, cam_r_L-1b_salon_acik_mutfak_2, cam_r_L-1b_salon_acik_mutfak_3 |
| r_L0_banyo | bathroom | L0 | 0 | 0 | 0 | - |
| r_L0_hol | hall | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi | bedroom | L0 | 0 | 0 | 0 | - |
| r_L1_hol | hall | L1 | 0 | 0 | 0 | - |
| r_L1_oyun_odasi | other | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 0 | 0 | 0 | - |

Rooms not rendered on purpose: r_L-1b_hol (same as r_L-1_hol), r_L0_banyo (unchanged in variant), r_L0_hol (unchanged in variant), r_L0_yatak_odasi (unchanged in variant), r_L1_hol (unchanged in variant), r_L1_oyun_odasi (unchanged in variant), r_L1_teras (unchanged in variant).

### Why Cycles

- cam_r_L-1b_salon_acik_mutfak_2: check_incomplete: polished image: unreliable pass (qwen saw the decoy)

## Mismatches (never auto-fixed)

None.

## Needs review

None.

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

None.

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L-1_mutfak | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_002 | area_label_vs_computed | r_L-1_hol | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_003 | area_label_vs_computed | r_L-1b_salon_acik_mutfak | Label says 57,20 m², polygon gives 57,19 m² (0.0%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_004 | area_label_vs_computed | r_L-1b_hol | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_005 | area_label_vs_computed | r_L0_banyo | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_006 | area_label_vs_computed | r_L0_hol | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_007 | area_label_vs_computed | r_L1_teras | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_008 | area_label_vs_computed | r_L1_hol | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |

## This report: variant `l-1b-acik-mutfak`

An alternative's sub-output: it renders the rooms its plan changes, and its exterior views only when its outside differs from the base. The sheets and the other variants are in the base project's report (`../../final/final_report.md`). The base exterior views of this run: ext_2, ext_3, ext_5, ext_6, ext_7.

## Building

The whole building as it was read and built: every level stacked on one frame with its slabs, the roof over the top level, the facade and the site. Each height says whether a document gave it or it was assumed (never silently).

Levels:

| level | label | kind | floor level | ceiling height | variant | region |
|---|---|---|---|---|---|---|
| L-1 | Bodrum Kat | basement | -3,00 m (section) | 2,80 m (section) | base | r1 |
| L-1b | Bodrum Kat | basement | -3,00 m (section) | 2,80 m (section) | Açık mutfak | r2 |
| L0 | Zemin Kat | floor | 0,00 m (section) | 2,80 m (section) | base | r3 |
| L1 | Çatı Katı | attic | 3,00 m (section) | 3,80 m (section) | base | r4 |

Variants:

| variant | label | levels | rooms changed | outside changed |
|---|---|---|---|---|
| base | Base | L-1, L0, L1 | 0 | no |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | 1 | no |

Heights (drawn = read from a document; assumed = a default, listed again under Assumed values):

| item | value | state | from | note |
|---|---|---|---|---|
| L-1 ceiling height | 2,80 m | drawn | section | - |
| L-1 floor level | -3,00 m | drawn | section | - |
| L-1 floor to floor | 3,00 m | drawn | vector | - |
| L-1b ceiling height | 2,80 m | drawn | section | - |
| L-1b floor level | -3,00 m | drawn | section | - |
| L-1b floor to floor | 3,00 m | drawn | vector | - |
| L0 ceiling height | 2,80 m | drawn | section | - |
| L0 floor level | 0,00 m | drawn | section | - |
| L0 floor to floor | 3,00 m | drawn | vector | - |
| L1 ceiling height | 3,80 m | drawn | section | - |
| L1 floor level | 3,00 m | drawn | section | - |
| sl_L-1 thickness | 0,20 m | drawn | section | - |
| sl_L0 thickness | 0,20 m | drawn | section | - |
| sl_L1 thickness | 0,20 m | drawn | section | - |
| roof eaves height | 3,96 m | drawn | vector | 0.96 m above the top floor |
| roof ridge height | 7,11 m | drawn | vector | 4.11 m above the top floor |
| roof overhang | 0,50 m | drawn | vector | left 0.50 m, right 0.50 m |
| roof thickness | 0,25 m | drawn | vector | perpendicular to the first slope |
| roof knee wall | 1,30 m | drawn | vector | the roof's top surface at the outer face of the outer wall above the top floor (a cross-check); the underside meets the outer face 1.00 m above the floor |
| north direction (deg) | 0 deg | drawn | vector | - |

Slabs:

| slab | carries level | top | thickness | from | stair voids | variants | status |
|---|---|---|---|---|---|---|---|
| sl_L-1 | L-1 | -3,00 m | 0,20 m | section | 0 | all | verified |
| sl_L0 | L0 | 0,00 m | 0,20 m | section | 1 | all | verified |
| sl_L1 | L1 | 3,00 m | 0,20 m | section | 1 | all | verified |

Roof:

- type gable (section)
- over level L1
- eaves 3,96 m (drawn)
- ridge 7,11 m (drawn)
- overhang 0,50 m (drawn)
- thickness 0,25 m (drawn)
- knee wall 1,30 m (drawn)
- pitch 35 deg (drawn)
- 0 planes, 1 opening(s)
- covering clay_tiles (elevation)

Assumed for the roof: the ridge runs across the cut (a gable read from one section).

Facade:

| side | wall | level | material | colour | source |
|---|---|---|---|---|---|
| south | - | - | render | - | elevation |
| south | - | L0 | stone_cladding | - | elevation |
| east | - | - | render | - | elevation |

| elevation | title | side | windows | doors | plan check |
|---|---|---|---|---|---|
| r7 | GÜNEY GÖRÜNÜŞÜ | south | 2 | 1 | matched 3, missing 0, extra 0, plan_windows 2, plan_doors 1, walls ['w_L-1_001', 'w_L0_001', 'w_L1_001'] |
| r8 | DOĞU GÖRÜNÜŞÜ | east | 2 | 0 | matched 2, missing 0, extra 0, plan_windows 2, plan_doors 0, walls ['w_L-1_006', 'w_L0_006', 'w_L1_006'] |

Site:

- plot drawn
- 0 paving area(s), 1 grass, 1 parking built
- 4 boundary wall(s), 3 decor item(s) built
- 2 labelled area(s), 2 recorded only (label, not built)
- drawn ground levels: south -, north -
- terrain flat, 0 light well(s)
- north 0 deg (drawn)

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 21 piece(s) added, 0 wall cabinet run(s).

### Salon (r_L-1_salon, living): completed

- added f_L-1_007: table_coffee 1.00 x 0.60 (confidence 0.90, ai)
- added f_L-1_008: tv_unit 1.60 x 0.45 (confidence 0.60, ai)
- added f_L-1_009: armchair 0.90 x 0.90 (confidence 0.90, ai)
- added f_L-1_010: sideboard 1.60 x 0.45 (confidence 0.60, ai)

### Mutfak (r_L-1_mutfak, kitchen): completed

- added f_L-1_011: tall_cabinet 0.40 x 0.58 (confidence 0.60, ai)
- added f_L-1_012: table_dining 1.20 x 0.80 (confidence 0.60, ai)
- added f_L-1_013: chair 0.45 x 0.45 (confidence 0.90, ai)
- added f_L-1_014: chair 0.45 x 0.45 (confidence 0.60, ai)
- added f_L-1_015: chair 0.45 x 0.45 (confidence 0.60, ai)
- added f_L-1_016: chair 0.45 x 0.45 (confidence 0.60, ai)
- not placed table_dining: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no table_dining in the room)
- not placed chair: no free place passed the placer checks (no table_dining in the room)
- not placed chair: no free place passed the placer checks (no table_dining in the room)
- not placed chair: no free place passed the placer checks (no table_dining in the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_006

### Hol (r_L-1_hol, hall): completed

- added f_L-1_017: console_table 1.20 x 0.35 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_001

### Salon + Açık Mutfak (r_L-1b_salon_acik_mutfak, living): completed

- added f_L-1b_007: table_coffee 1.00 x 0.60 (confidence 0.90, ai)
- added f_L-1b_008: tv_unit 1.20 x 0.40 (confidence 0.60, ai)
- added f_L-1b_009: armchair 0.90 x 0.90 (confidence 0.60, ai)
- added f_L-1b_010: sideboard 1.60 x 0.45 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_002, f_L-1b_003, f_L-1b_004, f_L-1b_006

### Hol (r_L-1b_hol, hall): copied (decisions of r_L-1_hol (same_as), not asked again)

- added f_L-1b_011: console_table 1.20 x 0.35 (confidence 0.60, ai, mirrored from f_L-1_017)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_001

### Yatak Odası (r_L0_yatak_odasi, bedroom): completed

- added f_L0_006: nightstand 0.50 x 0.40 (confidence 0.90, ai)
- added f_L0_007: nightstand 0.50 x 0.40 (confidence 0.90, ai)
- added f_L0_008: wardrobe 1.80 x 0.60 (confidence 0.60, ai)

### Banyo (r_L0_banyo, bathroom): completed (nothing to ask: no changeable drawn piece and nothing the room may get)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_004, f_L0_005

### Hol (r_L0_hol, hall): completed

- added f_L0_009: console_table 1.20 x 0.35 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001

### Hol (r_L1_hol, hall): completed

- added f_L1_006: console_table 1.20 x 0.35 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 18 of 18 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 18 ok, 0 failed; 0 changed by the AI.

## Exterior views

0 of 0 exterior view(s) of variant `l-1b-acik-mutfak` rendered.

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | render | white | brief | no | brief exterior.facade: 'white render' (as the style profile reads it) |
| roof | clay_tiles | - | documents | no | roof.covering (elevation) |
| window_frame | aluminium_anthracite | - | brief | no | brief exterior.window_frame: 'anthracite aluminium' (as the style profile reads it) |
| door | wood_oak_light | - | fallback | yes | style profile exterior.door (assumed) |
| paving | paving | grey | fallback | yes | style profile exterior.paving (assumed) |
| garden | grass | - | fallback | yes | style profile exterior.garden (assumed) |
| sill | stone | - | build | yes | exterior sill not drawn |
| light_well | concrete | - | build | yes | light well: concrete (not drawn) |
| railing | steel_brushed | - | build | yes | railing not drawn: steel rail and glass panel |
| soffit | soffit | - | build | yes | roof soffit: painted (not drawn) |
| bark | bark | - | build | yes | parametric tree |
| foliage | foliage | - | build | yes | parametric tree |
| ground | soil | - | build | yes | neutral ground (brief site: ground) |
| plot_wall | render | white | build | yes | plot wall finish not drawn: the facade's look |

Elevation check (window and door counts and positions per facade, building JSON against the drawn elevation; built eaves and ridge against the section; deterministic):

Source: building.json facade.elevations. 2 facade(s): 0 ok, 2 mismatch, 0 not checked; roof ok.

| elevation | side | drawn win/door | built win/door | result | notes |
|---|---|---|---|---|---|
| r7 | south | 2/1 | 5/1 | mismatch | the drawn heights are +0.60 m from the building's (an elevation without a level mark takes its ground as z 0.00, assumed): a common offset, listed |
| r8 | east | 2/0 | 3/0 | mismatch | the drawn heights are +3.15 m from the building's: more than the 1.0 m a drawn ground at z 0.00 can explain; positions not trusted |

Roof heights: built eaves 3,96 m, ridge 7,11 m; drawn eaves 3,96 m (vector), ridge 7,11 m (vector); result ok.

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| sheet.dxf | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: block_name 14, rule 4. Recognition questions: -; answer files: none. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

## Site

The plot, paving, grass, parking and boundary walls marked built are built in the 3D scene and show in the exterior views; an area that is only a label (not built) is recorded, not built.

| id | what | detail |
|---|---|---|
| sw_L0_001 | boundary wall (plot) | 19,70 m long, 0,20 m thick, built |
| sw_L0_002 | boundary wall (plot) | 23,70 m long, 0,20 m thick, built |
| sw_L0_003 | boundary wall (plot) | 19,70 m long, 0,20 m thick, built |
| sw_L0_004 | boundary wall (plot) | 23,70 m long, 0,20 m thick, built |
| sa_L0_otopark | area 'Otopark' (parking) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_bahce | area 'Bahçe' (garden) | label size -, measured - (-), no closed outline, recorded only (not built) |
| - | decor | tree x 3 |

## Separators

None.

## Assumed values

- brief empty_rooms: ai (default, not in brief.yaml)
- brief decor: True (default, not in brief.yaml)
- brief polish: True (default, not in brief.yaml)
- brief style_photos: [] (default, not in brief.yaml)
- brief ceiling_height: 2.7 (default, not in brief.yaml)
- brief slab_thickness: 0.2 (default, not in brief.yaml)
- brief furnished_rooms: complete (default, not in brief.yaml)
- brief furnished_rooms_keep: [] (default, not in brief.yaml)
- brief furnished_rooms_keep_size: False (default, not in brief.yaml)
- brief variants: all (default, not in brief.yaml)
- brief failed_levels: leave_out (default, not in brief.yaml)
- brief site: full (default, not in brief.yaml)
- brief exterior.door:  (default, not in brief.yaml)
- brief exterior.paving:  (default, not in brief.yaml)
- brief exterior.garden:  (default, not in brief.yaml)
- brief render.views_per_room: 3 (default, not in brief.yaml)
- brief render.resolution: [1920, 1080] (default, not in brief.yaml)
- brief render.samples: 256 (default, not in brief.yaml)
- brief render.lens_mm: auto (default, not in brief.yaml)
- brief render.exterior_views: True (default, not in brief.yaml)
- brief render.twin_rooms: one (default, not in brief.yaml)
- door height 2,10 m: 12 opening(s) (d_L-1_001, d_L-1_002, d_L-1_003, d_L-1b_001, d_L-1b_002, d_L-1b_003 ...)
- window height 1,20 m: 22 opening(s) (win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L-1_005, win_L-1_006 ...)
- window sill height 0,90 m: 22 opening(s) (win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L-1_005, win_L-1_006 ...)
- f_L-1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- f_L-1b_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- f_L0_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- f_L1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- roof: the ridge runs across the cut (a gable read from one section) assumed
- outside look door: wood_oak_light (fallback: style profile exterior.door (assumed))
- outside look paving: paving in grey (fallback: style profile exterior.paving (assumed))
- outside look garden: grass (fallback: style profile exterior.garden (assumed))
- outside look sill: stone (build: exterior sill not drawn)
- outside look light_well: concrete (build: light well: concrete (not drawn))
- outside look railing: steel_brushed (build: railing not drawn: steel rail and glass panel)
- outside look soffit: soffit (build: roof soffit: painted (not drawn))
- outside look bark: bark (build: parametric tree)
- outside look foliage: foliage (build: parametric tree)
- outside look ground: soil (build: neutral ground (brief site: ground))
- outside look plot_wall: render in white (build: plot wall finish not drawn: the facade's look)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L-1b_hol: room has little daylight (window/floor 0.054 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1b_hol |
| area_light | 1 | r_L0_hol: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_hol |
| area_light | 1 | r_L1_hol: room has little daylight (window/floor 0.054 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_hol |
| area_light | 1 | r_L1_oyun_odasi: room has little daylight (window/floor 0.033 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_odasi |
| area_light | 1 | r_L1_teras: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras |
| counter_fronts | 1 | design detail of the counter (fronts and handles inside its own box); the documents show only the footprint | furn_f_L-1b_004 |
| direction | 2 | no UP arrow, break line or riser text drawn: rise direction and flight order are assumed | furn_f_L-1b_001, furn_f_L0_001 |
| door | 1 | style profile exterior.door (assumed) | exterior |
| door_handles | 7 | design detail of the documented door (lever handles on both faces); not in the documents | d_L-1b_001_handle, d_L-1b_002_handle, d_L0_001_handle |
| door_handles | 1 | design detail of the documented double door (brushed_steel handles on both faces); not in the documents | d_L0_003_handle |
| door_handles | 1 | design detail of the documented sliding door (brushed_steel rail and handle); not in the documents | d_L-1b_003_handle |
| door_side | 1 | sliding door: rooms on both sides or none and no swing_side; hung on the wall's right face | d_L-1b_003 |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
| garden | 1 | style profile exterior.garden (assumed) | exterior |
| ground:+x | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| ground:-x | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| handrail | 2 | design detail on every flight side not against a wall; not in the documents | furn_f_L-1b_001, furn_f_L0_001 |
| height | 9 | door height listed as assumed in the building JSON | d_L-1b_001, d_L-1b_002, d_L-1b_003 |
| height | 1 | no height in the JSON; type height for bed_double | furn_f_L0_002 |
| height | 1 | no height in the JSON; type height for fridge | furn_f_L-1b_002 |
| height | 1 | no height in the JSON; type height for kitchen_counter | furn_f_L-1b_004 |
| height | 1 | no height in the JSON; type height for shower | furn_f_L0_003 |
| height | 1 | no height in the JSON; type height for sink_kitchen | furn_f_L-1b_006 |
| height | 1 | no height in the JSON; type height for sofa | furn_f_L-1b_005 |
| height | 1 | no height in the JSON; type height for stove | furn_f_L-1b_003 |
| height | 1 | no height in the JSON; type height for toilet | furn_f_L0_004 |
| height | 1 | no height in the JSON; type height for washbasin | furn_f_L0_005 |
| height | 4 | plot wall height not drawn | sw_L0_001, sw_L0_002, sw_L0_003 |
| height | 15 | window height listed as assumed in the building JSON | win_L-1b_001, win_L-1b_002, win_L-1b_003 |
| height_lift | 1 | footprint overlaps another piece of the same height; lifted so the top faces do not coincide | furn_f_L-1b_004 |
| light_well:win_L-1b_001 | 1 | window sill -2.10 m, ground outside 0.00 m: an open concrete light well 0.8 m deep, 1.60 m wide (no light well drawn) | site |
| light_well:win_L-1b_002 | 1 | window sill -2.10 m, ground outside 0.00 m: an open concrete light well 0.8 m deep, 1.60 m wide (no light well drawn) | site |
| light_well:win_L-1b_003 | 1 | window sill -2.10 m, ground outside 0.00 m: an open concrete light well 0.8 m deep, 1.60 m wide (no light well drawn) | site |
| light_well:win_L-1b_004 | 1 | window sill -2.10 m, ground outside 0.00 m: an open concrete light well 0.8 m deep, 1.60 m wide (no light well drawn) | site |
| light_well:win_L-1b_005 | 1 | window sill -2.10 m, ground outside 0.00 m: an open concrete light well 0.8 m deep, 1.60 m wide (no light well drawn) | site |
| light_well:win_L-1b_006 | 1 | window sill -2.10 m, ground outside 0.00 m: an open concrete light well 0.8 m deep, 1.60 m wide (no light well drawn) | site |
| light_well:win_L-1b_007 | 1 | window sill -2.10 m, ground outside 0.00 m: an open concrete light well 0.8 m deep, 1.00 m wide (no light well drawn) | site |
| parapet | 1 | roof terrace ro_001: its walls end at a 1.0 m parapet (height assumed) | w_L1_001,w_L1_006 |
| parapet_height:ro_001 | 1 | not drawn | roof |
| paving | 1 | style profile exterior.paving (assumed) | exterior |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.000 m / 13 drawn risers | furn_f_L-1b_001, furn_f_L0_001 |
| roof | 1 | listed as assumed in the building JSON | roof |
| sill | 4 | outside sill 0.66 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1b_007_sill, win_L0_002_sill, win_L0_006_sill |
| sill | 11 | outside sill 1.26 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1b_001_sill, win_L-1b_002_sill, win_L-1b_003_sill |
| sill_height | 15 | window sill_height listed as assumed in the building JSON | win_L-1b_001, win_L-1b_002, win_L-1b_003 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 6 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L-1b_salon_acik_mutfak, skirting_r_L-1b_hol, skirting_r_L0_yatak_odasi |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_001 (100% of the smaller footprint; slab opening sv_L1_001); read as its upper end, not built as a second flight | f_L1_001 |
| tree | 3 | parametric tree: crown 2.4 m as drawn, 4.0 m tall (height assumed) | tree_sd_L0_001, tree_sd_L0_002, tree_sd_L0_003 |
| waist | 2 | the documents show the stair in plan only | furn_f_L-1b_001, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L-1b_salon_acik_mutfak | cam_r_L-1b_salon_acik_mutfak_1, cam_r_L-1b_salon_acik_mutfak_3 | cam_r_L-1b_salon_acik_mutfak_2 (check_incomplete) | ok |

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| polish base | Tongyi-MAI/Z-Image-Turbo | f332072aa78be7aecdf3ee76d5c247082da564a6 | Apache-2.0 | polish_manifest.json |
| polish controlnet | alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1 | 5155fc56d17821007d6f62ac192c09e0f0e72016 | Apache-2.0 | polish_manifest.json |
| gate depth | depth-anything/Depth-Anything-V2-Small-hf | 5426e4f0f36572d16453bbda7a8389317b1bef99 | Apache-2.0 | polish_manifest.json |
| gate sam | facebook/sam2.1-hiera-large | 665f8e2ad61cf5f53d65644ff27c8ee525124610 | Apache-2.0 | polish_manifest.json |
| gate dino | facebook/dinov2-base | f9e44c814b77203eaa57a6bdbbd535f21ede1415 | Apache-2.0 | polish_manifest.json |
| check qwen | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | check_manifest.json |
| check glm | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | check_manifest.json |
| detector | google/owlv2-base-patch16-ensemble | cfd3195ba4ea9592eec887ded089f4c08eff231d | Apache-2.0 | check_manifest.json |

Assets: textures CC0 x 11; furniture/decor models CC-BY-4.0 x 61, CC0 x 2, generated (TRELLIS.2-4B, MIT) x 12 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Bed" by Ambriel (https://sketchfab.com/3d-models/08f7f65edfea417b8ed9ca748381e507), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_002)
- "Pia Texturizada por Wellington Marques" by mendesviana (https://sketchfab.com/3d-models/3a406e651e69409e87323ab42a214874), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L-1_007)
- "Scarf" by Viatorestw (https://sketchfab.com/3d-models/511d44e5693549ca9c4002752a35fcb2), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L-1_003)
- "Old Fridge" by golddog (https://sketchfab.com/3d-models/68d69bbf7a454a09a2536ac0762532f3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L-1_002, f_L-1b_002)
- "Stove from Poly by Google" by IronEqual (https://sketchfab.com/3d-models/68e164f1a9414c29820ac2eaf6d8ac04), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L-1_003, f_L-1b_003)
- "Bathroom1" by neutralize (https://sketchfab.com/3d-models/f76c502218884914a27148f656a9b656), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_005)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_r_L-1b_salon_acik_mutfak_1 | calibrated | yes | no | - |
| cam_r_L-1b_salon_acik_mutfak_2 | calibrated | yes | no | - |
| cam_r_L-1b_salon_acik_mutfak_3 | calibrated | yes | no | - |

## Stages

This run (`20261009-134613-full-20261009T135146Z`):

| stage | status | seconds | note |
|---|---|---|---|
| build | ok | 92.6 s | - |
| render | ok | 39.9 s | - |
| export | ok | 31.3 s | - |
| controls | ok | 28.1 s | - |
| gate | ok | 1.1 s | gate decision ok (the base project's calibration) |
| polish | ok | 43.6 s | - |
| detect | ok | 5.0 s | - |
| expected | ok | 6.7 s | - |
| check | ok | 44.1 s | - |
| combine | ok | 5.9 s | - |

The report stage itself is recorded after this report.

## Warnings

None.
