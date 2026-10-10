# Milestone 12 – track L (ground and levels): as built

Design: `docs/milestone12.md` §3 (D1–D6, D3a = 0.15 m, user OK of 10 Oct 2026), contracts §13. Cloud session, CPU only,
10 Oct 2026. Branch: the worktree branch of track L.

## 1. What was built

| Part | file:function | What it does |
|---|---|---|
| Mark reader (D1, B10) | `wenart/levels/marks.py`: `parse_mark`, `read_mark`, `MARK_ATTRIBUTE_TAGS`, `tag_kind` | every form of §3.1 (`±0.00`, `+-0.00`, `%%p0.00`, `+-0.00(dük)`, `+0.15`, `-0.45`, `KOT +3.00`, `KOT: +0.15`, `Ü.K.`, `S.K.`, `T.Z.`, `TABİİ ZEMİN`, `TESVİYE 0.00 KOTU : 93.20`, `SB. KOTU : 93.20`, `BİNA GİRİŞ KOTU : 93.20`, `100.18(şev üst kotu)`, `±0.00 = 93.20`, `±0.00 KOT`, `FFL`, `BDK`); kind from the keyword; a mark needs a sign, a keyword, or (`read_mark(bare=True)`) an attribute tag / a mark symbol; a pair gives value + absolute; `note` for a `... KOTU : x` statement |
| Unit check, sections | `wenart/sheets/units_check.py`: `mark_records`, `mark_texts` (MARK_RE removed); `wenart/sheets/heights.py`: `read_section`, `heights` (`mark_z`) | one reader everywhere; section marks keep relative / absolute apart: `±0.00 = 43.00` gives the datum 43.00 and `+3.00` is compared in its own frame |
| Site plan marks | `wenart/sheets/exterior.py`: `site_of` (`marks`) | spot heights of a registered site plan in building metres (sheets.json) |
| Reading into the building (D1, D2, B11) | `wenart/levels/read.py`: `read_marks`, `resolve_datum`, `classify`, `mark_symbols`, `drawn_ramps` | marks from every page text (with ATTRIB tags; a bare value in the same block reference is a companion: `+0.00` / `93.20`), the section's slab-top marks; the datum (pairs, block pairs, the section; most frequent wins, conflicts listed); absolute marks converted; kind by position (room -> floor, outside near an outside door -> threshold, outside within 25 m -> ground, farther -> unknown, site notes keep their keyword); level-mark symbols leave the furniture (`symbols[]`, kind `level_mark`, `former_piece_id`); `RAMPA` texts near a door = a drawn ramp |
| Pipeline hook | `wenart/ingest/generic/levels.py`: `apply_levels`, `_texts`, `_site_plan_texts` | texts to building metres (box centre, `transform_to_building`), the pure steps above, `project.datum`, conflicts and warnings into the build, then `infer_levels`; the building dict is updated in place |
| Inference (D3, D3a, U2) | `wenart/levels/model.py`: `infer_levels`, `level_params`, `whole_single_level`, `steps_for`, `ramp_for`, `opening_sides`, `terrain_for`, `room_floor_z` | single drawn ground floor -> slab `sl_L0`, `flat_cut` roof, site (`to_building.site_block`); level elevation from floor marks; room `floor_offset_m` / `floor_source` / `floor_evidence`; door and opening `threshold_z`; inner steps; ground (points, outliers, `planar` / `tin` / per side / site note / section / D3a), `site.ground.surface`, `terrain`, `source`; `site.entrances` (ground in front, rise, `none` / `steps` / `ramp` / `steps_and_ramp`, landing, flights, intermediate landings every 12 risers, handrails, cheek walls, main entrance, door into the air, below the ground); `site.plinth` (SB. mark else the ground floor, per side, a basement opened by the slope takes its own floor); basements with their light wells / courts in `site.ground.light_wells` (`source: assumed`, `inferred`); everything in `level_inference` (`inferred`, `conflicts`, `warnings`, `inner_steps`, `basements`, `params`, `edits`) |
| Terrain surface | `wenart/levels/terrain.py`: `fit_plane`, `delaunay`, `fit_surface`, `surface_z` | least-squares plane (residual <= 0.10 m) else Bowyer-Watson TIN; flat beyond the points' hull (margin 2 m, blend 20 m); pure math (runs in Blender) |
| Checks L1–L7 (D5) | `wenart/levels/checks.py`: `check_levels` | as the table of the module docstring; L7 needs a manifest |
| Level edits (D6) | `wenart/levels/edits.py`: `apply_level_edit`, `LEVEL_EDIT_SCHEMAS` | `set_mark_kind`, `set_room_floor` (mark or step line), `set_ground_point` (a drawn mark within 2 m wins), `set_entrance`, `set_terrain`; strict schemas with `reason`; validation = the L-score (critical + major) must not rise; `rerun_from: build` |
| Blender: terrain | `wenart/blender/site.py`: `terrain_model` (kind `planar` / `tin`), `ground_z` | the ground mesh (`draped_faces`), plot walls, trees, paths, light wells follow the surface |
| Blender: entrances | `site.py`: `record_entrances`, `record_steps`, `entrance_meshes`, `bar`, `ramp_solid`; `build_site` | landing, flights, intermediate landings, cheek walls, handrails (0.90 m), ramp along the facade; objects `steps_<door>` / `ramp_<door>` / `handrail_<door>` (kinds `site_steps`, `site_ramp`, `site_handrail`, `entrance` = door id) |
| Blender: plinth | `wenart/blender/facade.py`: `plinth_rule`, `plinth_top`, `_plinth` | a raised base from the ground (- 0.05) to the floor (at least 0.15 m), 0.10 m in under the wall, no gap under a raised floor; the M11 0.45 m band only without `site.plinth` |
| Blender: flat_cut roof | `wenart/blender/roof.py`: `roof_model` (`kind`, `parapet`), `parapet_ring`, `roof_solid`; `facade.py` coping on the parapet | a flat roof slab with a 0.30 m parapet |
| Blender: room floors, doors | `wenart/blender/shell.py`: `room_floor_z`, `wall_base_drop`, `inner_step`, `opening_vertical` (threshold), `build_walls`, `build_floors_ceilings`, `_threshold`, `build_skirting` | floors at their offset; walls beside a sunken floor start at it; a step block in a door between floors; door frames from `threshold_z` |
| Cameras | `wenart/blender/cameras.py`: `plan_cameras`; `camsearch.py`: `RoomModel` | interior cameras stand on the room's own floor |
| Exterior views | `wenart/blender/exterior.py`: `flat_cut`, `entrance_views`, `plan_exterior` | `flat_cut`: no aerial view (dropped with its reason), eye-level views framing the entrances (main first, one per 3 m, at most 3) |
| X3 | `wenart/blender/exterior_checks.py`: `_x3` | reads `site.entrances`: every rise; a door > 1.5 m up = critical (door into the air) |
| Fingerprint | `wenart/blender/build.py`: `FINGERPRINT_CODE` | + `wenart/levels/terrain.py` (the build imports it) |
| Defaults, brief | `wenart/defaults.yaml` (`levels:` and `brief.levels`), `wenart/brief.py`: `levels_block`, `VALUE_RULES["levels.ground_rise"]` | all numbers in one block, the TS 9111 ones flagged as secondary sources; the brief's `levels:` overrides any of them |
| Report (B9) | `wenart/report/m10.py`: `building_block` (site ground numbers), `level_summary`, `level_lines` | "ground levels: left 0.00 m (drawn)" instead of "left -"; a Levels and ground block: marks, datum, ground source, plinth, room floors, the entrance table, the inferred list, the flag |

## 2. Decisions taken inside the design

- **Relative or absolute**: a signed value or 0.00 is relative; an unsigned value of 10 m or more is absolute, under
  10 m relative (Turkish drawings sign relative marks; a coastal site with an absolute level under 10 m would be read
  wrongly, documented in `marks.py`).
- **Building z = the relative mark value** (±0.00 = z 0, the schema's convention). An assumed level elevation takes
  the most common floor mark of its rooms; the ground floor moves only when most of its marks agree.
- **Site notes** (`... KOTU : 93.20`) are position-free: TESVİYE gives one ground level for the whole site when
  nothing else does; SB. the plinth top; GİRİŞ is compared with the entrance (L4).
- **Ground marks**: within 25 m of the outline (farther: another drawing on the sheet, `unknown`); a point more than
  3 m from the median of the others is listed, not used. 1–2 points give per-side levels (`from_mark`, made again
  on every run), >= 3 a plane or a TIN.
- **Steps**: tread = max(0.30, 0.58 - 2R) rounded up to cm (keeps 2R + T >= 0.58 for low risers); one step lower
  than 0.10 m (a 0.06–0.10 m rise) is an L5 *minor* (a trip risk, a ramp would do), never a major we cause ourselves.
- **Ramps** run along the facade from the landing's side (compact; the slope table of §3.3); only when a `RAMPA`
  text is drawn near the door or the brief sets `levels.accessible_entrance: true` (the main entrance).
- **Basement doors** below the drawn ground keep the build's M10 rule (its side of the terrain is lowered to the door
  floor): the entrance is flush, `terrain_lowered: true`. A planar / TIN surface is never lowered (a warning).
- **Main entrance**: an entrance-kind mark at a door, else the widest door of the side with the most entrances.
- **Upper floors**: a door in an outer wall of an upper floor with no room outside it is recorded (`into_air`,
  `upper_floor`) but L2 rates it *major*, not critical (a French balcony or a balcony not drawn; the agent decides);
  on the ground floor it stays critical.
- **KOT block pairs**: in real03's `TAG_KOT_PLAN` block the KOT-ARAZI attribute holds the absolute level of the
  KOT-BINA value (`+0.00` / `93.20`): read as the datum ±0.00 = 93.20, and both marks as the room's floor.
- **Symbols**: a piece is a level-mark symbol when its block reference holds a mark text (same INSERT path, piece
  <= 2 m, the text within 0.5 m) or it is a small (<= 1.2 m, <= 0.6 m²) unknown / lamp / plant piece around a mark
  text. Ids `sym_<former piece id>`.
- **flat_cut**: roof `type: flat` + `kind: flat_cut` (the schema's `type` enum has no `flat_cut`), parapet 0.30 m
  (assumed), slab thickness from the brief (0.20 m default), the roof slab 0.30 m (roof.py default).
- **Levels of a building that is not whole** (several levels, no section, e.g. synthetic-01): room floors and door
  thresholds are filled; site, entrances and plinth only for whole buildings (as the build only builds a site then).

## 3. Tests added

| File | Tests | What |
|---|---|---|
| `tests/test_levels_marks.py` | 51 | every form (parametrized), 20 false positives, bare values with a tag, notes, the old pattern rejected the Turkish forms (B10), the unit check, section marks in two frames |
| `tests/test_levels_terrain.py` | 6 | plane, TIN through the points, residual rule, flat beyond, one / two / collinear points, the build reads the surface |
| `tests/test_levels_model.py` | 23 | single ground floor -> whole + flat_cut, D3a, an upper floor's door into the air (L2 major), brief rise and ramp, upper / basement titles not made whole, step sizing and intermediate landings, ramp slope table (5), door into the air, site note, planar ground, one mark per side + outlier, far mark, room floors and thresholds and inner steps, disagreeing marks, level elevation from marks, plinth, the M10 example, idempotence, defaults.yaml = built-in copy |
| `tests/test_levels_read.py` | 11 | companions and block datum, site-note datum and conversion, datum conflict, kinds by position, mark symbols (real03 f_L0_142 shape), drawn ramps, `apply_levels` on a `ProjectBuild`, site plan marks, `site_of` marks, section marks and notes without `point` (schema), no marks |
| `tests/test_levels_checks.py` | 9 | pass case; L1–L7 fail cases; purity |
| `tests/test_levels_edits.py` | 6 | strict schemas; each op accepted and refused; the score rule; the drawn mark wins |
| `tests/test_levels_build.py` | 8 | `prepare` of a single ground floor, flights / landings / ramp / rails / cheeks, M11 steps without records, the raised plinth, flat_cut parapet and no aerial view + entrance views, room floors / thresholds / wall drop / inner step / cameras, X3 on records, report B9 |
| `tests/test_levels_real.py` | 2 | committed real03 and real02 building.json (below) |
| `tests/_levels_fixture.py` | – | the hand-made building and mark records |
| `tests/test_brief.py` | (updated) | the two new assumed brief keys |

## 4. Real data, before / after

`dwg2dxf` is not on the path of this session, and the worktree guard refused fetching LibreDWG; another track built
the patched LibreDWG 0.14 d9468ae p1 in the shared scratchpad, which I used read-only
(`WENART_LIBREDWG_BIN`) to run the CPU pipeline with the committed recognition answers
(`python -m wenart.ingest.pipeline projects/<p> --answers <out>/recognition`, real03 264 s, real02 224 s). "Before" =
the same pipeline at the contract commit (hook stub; the other track's run of 10 Oct 19:51).

What the DWGs hold (an ezdxf scan of the converted DXFs): real03 has **2 level marks in model space** (the `TAG_KOT_PLAN`
block INSERT 7C9C9/48 in the Rüzgarlık: KOT-BINA `+0.00`, KOT-ARAZI `93.20`) and 284 in **unused** block definitions
(D BLOK_1K / NK / BK / CK / ÇATI: `+3.20` … `+41.60`, `-2.00`, `-4.00`, `100.18(şev üst kotu)` ...); the site note
TESVİYE / SB. / BİNA GİRİŞ is not in model space. real02: the 20 BDK attributes (37.00 … 46.00) are all in one
**unused** block (confirms §1.5); the section's MTEXT 43.00 / 40.00 are read by the sheets stage.

| | real03 before | real03 after | real02 before | real02 after |
|---|---|---|---|---|
| level marks | 0 | 2 (floor, both in r_L0_ruzgarlik; tags KOT-BINA, KOT-ARAZI) | 0 | 2 (section slab tops: 43.00 -> L0 z 0, 40.00 -> L-1 z -3.00) |
| datum | none | ±0.00 = 93.20 (the +0.00 / 93.20 block) | 43.00 (section) | 43.00 (section) |
| mark symbols | f_L0_142 built as an unknown box | **f_L0_142 -> symbols** (`sym_f_L0_142`, the block reference holds the marks); 164 pieces | – | – |
| L0 elevation | 0.00 assumed | 0.00 `level_mark` | 0.00 section | 0.00 section |
| whole building | no (no slabs / roof / site: no exterior) | yes: `sl_L0`, roof `flat_cut`, site | yes | yes |
| ground | none | D3a: all -0.15 (assumed; nothing about the ground in model space) | left / right 0.00 (section) | same, source `section` |
| entrances | none | d_L0_019 (main) and d_L0_020: 1 riser 0.15 m, landing 1.2 m | flush, no record | d_L0_011 (main), d_L0_012: `none` (flush, as drawn) |
| door thresholds | none | 47 | none | 29 |
| plinth | 0.45 m band (not built: no exterior) | raised base to the floor, 0.15 m on every side | 0.45 m band | 0.15 m every side |
| basement | – | – | courts only in the scene manifest | L-1 3.00 m under the ground, 3 courts in `site.ground.light_wells` |
| exterior views (planned) | none | ext_1–4 corners, ext_6 frontal, ext_7 entrance (d_L0_019; d_L0_020 0.9 m beside it shares it); ext_5 aerial dropped (flat_cut) | 4 corners, aerial, frontal | unchanged |
| L1–L7 (all severities) | – | 0 | – | 0 |
| status | ok | ok | ok | ok (a first run went needs_review on `level_marks[].point: null`: fixed, regression test) |

The committed `building.json` files of real03 run 3 and real02 G2d give the same ground, entrances, slabs and roof
(`tests/test_levels_real.py`, no DWG needed).

## 5. Left open

- A real03 regression test that runs the DWG pipeline (needs LibreDWG on the path; the numbers of §4 are from a
  manual run): the 2 marks, the datum 93.20, f_L0_142 in `symbols`.
- Mark symbols on plans for **bare** numbers (a triangle next to `3.20`): the plan's strokes are not kept in the
  `PageWork`; only signed, keyword and attribute-tag marks (and companions in the same block) are read on plans.
- Retaining edges where the terrain drops > 0.5 m at the plot boundary (L6 reports a slope over 1:3 instead).
- GPU check of the new objects (steps, ramps, handrails, raised plinth, parapet, sunken floors) in a real render
  (L7 with the object-index pass needs `visible_objects` in the render manifest).

## 6. Changes needed in other tracks' files

| Track / file | Change |
|---|---|
| Lead: `wenart/schema/building.schema.json` | document what is written (all optional, the schema has no `additionalProperties: false` so it validates today): roof `kind` (`flat_cut`), `parapet_height`, `note`, `inferred`; slab `inferred`; top-level `level_inference`; `level_marks[]` extra fields `z`, `note`, `placement`, `door_id`, `pair_of`, `block_ref`, `corrected_by_ai`, `inferred`, `adjusted_by_ai`; `rooms[].floor_source`, `floor_corrected_by_ai`; `site.drawn_ramps`, `site.entrance_overrides`, `site.ground.source`, `terrain_override`, the entrance record's fields (`level_id`, `room_id`, `centre`, `outward`, `face`, `width`, `half_t`, `side`, `main`, `drawn`, `into_air`, `below_ground`, `terrain_lowered`, `ground_source`, `reason`, `adjusted_by_ai`), `site.plinth` (`top_z`, `floors`, `min_height`, `sides`, `source`), light well `opening_ids`, `level_id`, `floor_z`, `top_z`, `kind`, `inferred`, `reason` |
| S: `wenart/blender/furniture.py` (+ decor) | furniture and decor of a room with `floor_offset_m` must stand on the room floor: use `wenart.blender.shell.room_floor_z(room, level)` instead of `level["elevation"]` |
| A: agent tools, critic, validator | a `levels` read tool (marks with kind and use, level / room floors, thresholds, ground points, terrain, entrances, `level_inference`, L-findings); the 5 edit tools through `wenart.levels.edits.apply_level_edit` (schemas `LEVEL_EDIT_SCHEMAS`); L-findings from `wenart.levels.checks.check_levels(building, scene_manifest, render_manifest)` in the critic; exterior cameras' `visible_objects` in the render manifest for L7 |
| R: `wenart/ingest/pipeline.py` | draw the level marks (colour by kind) and the moved symbols on the per-page debug image (CLAUDE.md debug image rule); `read_furniture` runs after `apply_levels`: pieces already moved to `symbols` are gone; symbol ids of track L are `sym_<former piece id>` |
| R / lead: `tests/test_pipeline.py::test_one_drawing_per_page_keeps_the_m2_m9_building` | edited by track L (one expectation): synthetic-02 and synthetic-05 (a single drawn ground floor) now get `sl_L0` and a `flat_cut` roof (U2); the other M10 blocks stay absent. Please keep it when merging track R |
