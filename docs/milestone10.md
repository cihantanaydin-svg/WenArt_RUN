# Milestone 10 – AI completes rooms with drawn furniture; sheet analysis, the whole building and exterior views; a larger material, colour and furniture library

Goal (user, 8 Oct 2026): three features.

| # | Feature | What it means | Why (evidence today) |
|---|---|---|---|
| 1 | AI completes rooms with drawn furniture | in a room with furniture in the documents, AI may redesign the drawn pieces (type, size, height, look) and add the pieces the room type misses; for a drawn piece only its **location** (centre) and **position** (front, wall) are locked | `wenart/furniture/layout.py` furnishes only rooms without documented furniture; a bedroom with only a bed drawn gets no nightstands, no wardrobe |
| 2 | Sheets first, then the whole building, then exterior views | a new first stage `sheets` splits every sheet into drawing regions and classifies them (plans, alternatives, section, elevations, site …); all levels are registered into one frame and stacked with slabs, stairs, attic, roof, facade and site; exterior views per variant | real02 (`one_building.dwg`) holds 4 plans + a section on one sheet and ended `needs review` ("no building walls found"); `site` is "recorded, not built"; no roof, no exterior view |
| 3 | A larger material, colour and furniture library | ≥ 40 named colours, more wall, wet-wall, floor, door, window, cabinet, exterior and lighting looks, 14 new furniture types, 12 new decor types | `python -m wenart.style projects/real02` leaves 7 of 12 brief terms unmatched |

The no-hallucination rules stay. Two `CLAUDE.md` furniture rules change for Feature 1 only after the user's OK
(wording proposal in §1.7). Every value no drawing gives is `assumed` and listed; AI proposes, title text,
geometry and the source plan decide.

## 0. Session research (8 Oct 2026)

LibreDWG 0.14 (d9468ae) was built in the session (`scripts/cloud-setup.sh`), `one_building.dwg` converted with
`dwg2dxf` (audit 0 errors, 116 fixes) and read with ezdxf 1.4.4. Prototypes are in the session scratchpad, not
committed.

### 0.1 real02 (`projects/real02/one_building.dwg`)

| Fact | Measured |
|---|---|
| File | AC1027 (R2013); model space 8,156 entities (LINE 5,118, ELLIPSE 948, ARC 722, LWPOLYLINE 548, SPLINE 540, INSERT 178, MTEXT 45, CIRCLE 36, WIPEOUT 10, HATCH 7, DIMENSION 4); paper-space layouts `Layout1`, `Layout2` are empty |
| Sheet | one frame (LWPOLYLINE `2F086`, 6,004 × 7,878 units) with a title box `PLANLAR` (`2F087`) and five drawings |
| Drawings and titles (MTEXT, height 75) | `BODRUM KAT PLANI BRÜT 92 M2` (basement, `36A77`), `BODRUM KAT PLANI BRÜT 92 M2 ( Açık mutfak)` (basement, open kitchen, `2F090`), `ZEMİN KAT PLANI BRÜT 92M2` (ground floor, `2F08F`), `ÇATI KAT PLANI` (attic, `2FD2F`); the section has no title, only the level marks `40.00` and `43.00` |
| Title placement | every title is **below** its drawing (140–245 units; the attic title touches the roof outline) |
| Stray entities | HATCH `6633` (layer `_P3_S_Duvar_T`, SOLID) ≈ 230 m left of and 220 m above the frame; DIMENSIONs `34CEC`, `34CF2` (layer `Deko_Olcu Ic`) 16 m right of the frame |
| Units | `$INSUNITS` = 4 (mm), but the geometry is in **centimetres**: the section's slab lines are 300 units apart where the level marks read 40.00 and 43.00; slabs are 15 units; the four room labels of a basement dwelling (49 + 14.5 + 7 + 4.9 = 75.4 m²) match its 719 × 1,050-unit outline only in cm (75.5 m²). The M9-era run took 0.001 m/unit, so the building was 1 m wide and no wall rule could fire |
| Building | a **semi-detached pair**: every plan draws two mirrored dwellings around a party wall; every room label appears twice (basement: Salon 49, Mutfak 14.5, Koridor 7, Banyo 4.9; open-kitchen basement: Salon 46, Açık Mutfak 8.5, Oda 13, Koridor 7, Banyo 4.9; ground: Yatak Odası 17 and 16, E. Yatak Odası 17, E. Banyo 4, Banyo 4.9, Koridor 7; attic: Oyun Aktivite ve Dinlenme Odası 40, Teras 22, Koridor 10, Banyo 4.9) |
| Section (vector) | cut across both dwellings (1,517 units = the width of the pair); three slab bands of 15 units (tops 300 and 315 units apart: floor to floor 3.00 m basement → ground, 3.15 m ground → attic); the mark `40.00` points at the **bottom** of the lowest slab, `43.00` at the top of the middle slab (a 15 cm disagreement to list); roof with two slopes per side, 40° at the eaves and 13° up to the ridge on the party wall; eaves 0.50 m above the attic floor and 0.50 m outside the wall; ridge 3.64 m above the attic floor (the DIMENSION `2FD10` spans the same 364 units); ground lines at both marks on both sides |
| Attic plan | carries the roof outline (LWPOLYLINE `304CA`, 16.17 × 13.00 m: 0.50 m overhang at the sides, 1.25 m front and back) and an inner closed outline (`2F87A`, 11.77 × 8.60 m) close to where the slope changes in the section (12.17 m): steep slopes on all four sides, i.e. a **mansard** roof (to be confirmed by the reader); a 22 m² roof terrace per dwelling |
| DIMENSIONs | the two in the section come out of LibreDWG with measurement 0 (as M7 found for `dxf2dwg`): they are measured from their definition points |
| Text extents | MTEXT boxes from `ezdxf.bbox` are the column width (≈ 2,900 units for a 15-unit label): text never bridges two drawings; texts are attached after clustering by their insertion point |

Prototype: entity boxes clustered with a 100-unit gap (texts excluded, the frame excluded) give exactly the five
drawings, the title box and the strays. The ground-floor region alone, cut out with cm units and run through
today's pipeline: still no walls (§0.4).

### 0.2 real02 brief today

`python -m wenart.style projects/real02`: floor `wood_oak_light`, walls **`plaster_cream`** — taken from "rattan
and **cream** pots" (a bare colour word becomes a wall colour), while `warm greige walls` is unmatched. The phrase
splitter cuts "many large indoor plants (palms, monstera, ferns) in rattan and cream pots" at the commas inside the
brackets. Unmatched: `warm greige walls`, `light grey fabric sofa`, `natural light wood furniture`, `glass coffee
table`, `many large indoor plants (palms`, `monstera`, `dark bronze window frames`.

### 0.3 What the session can do

| Need | Session (8 Oct 2026) |
|---|---|
| LibreDWG `dwg2dxf` / `dxf2dwg` | built (`~/.cache/wenart/libredwg/bin`) |
| Poly Haven API, ambientCG API | reachable (HTTP 200): texture ids are verified here |
| `download.blender.org` | reachable: Blender 5.2.2 (the pod's version) runs here for CPU build tests and small CPU test renders |
| ABO (`amazon-berkeley-objects.s3.amazonaws.com`) | reachable: ABO listings surveyed here |
| Objaverse, LFS downloads | not reachable: Objaverse survey on the pod (as in M7–M9) |
| GPU | none: model inference, Cycles renders, polish, generation, judging on RunPod |

### 0.4 Ground-floor prototype: the split and the units are necessary, not sufficient

The ground-floor region cut out (1,851 entities) with `$INSUNITS` = cm and run through today's pipeline
(`--no-ai`): still `needs review`, **no building walls found**. The walls are drawn as **open face lines**: 92
two-point LWPOLYLINEs on layer `DBM_w_sld` (one per wall face, inner walls 10 cm, outer 15–20 cm), the dwelling
outline as one open 5-point polyline whose ends meet, and the columns as 18 closed rectangles on layer `A-BA`
(betonarme). None of M7's wall primitives fires: no hatch comb, no dark fill, no closed outline polygon, and the
layer name has no wall word (`WALL|DUVAR|MUR|PARED`). Doors and sanitary ware are blocks (`A_Kapi*`, `Piu_Vitrifiye`,
`ebeveynlavabo`); a floor-tile layer (`Deko_Zemin Seramik5`: 1,170 lines, 220 ellipses, 126 splines on this floor
alone) adds clutter. The dwelling outlines differ: 759 × 1,050 units on the ground floor, 719 × 1,050 in the
basement (0.40 m per dwelling; the section is 1,517 = 2 × 759 wide): the registration must say whether this is real.
So real02 also needs a new wall primitive (§3.1 item 11, track A3).

## 1. Contracts (frozen before any track starts; only the lead edits these files)

### 1.1 Building JSON (`wenart/schema/building.schema.json`, `docs/examples/building.example.json`, new `docs/examples/building_m10.example.json`)

| Where | New field | Meaning |
|---|---|---|
| `levels[]` | `variant_group` | `vg_<base level id>` when the level has alternative plans, else null |
| `levels[]` | `variant`, `variant_slug` | `base`, or the alternative's name as titled (`Açık mutfak`) and its ASCII slug (`acik-mutfak`); alternative levels get the id `<base id>b`, `<base id>c` … (`L-1b`) |
| `levels[]` | `kind` | `basement`, `floor`, `attic` |
| `levels[]` | `region_id` | the `sheets.json` region the level was read from |
| `levels[]` | `elevation_source`, `floor_to_floor` | `section`, `elevation_drawing`, `level_mark`, `assumed_default`; floor to floor with source |
| `variants[]` (new, top level) | `id`, `label`, `levels`, `base`, `changes`, `rooms_changed`, `exterior_changed` | one entry per buildable combination: `base` plus one per alternative (only that level differs); `rooms_changed` and `exterior_changed` are filled by the build |
| `slabs[]` (new) | `id`, `below_level_id`, `above_level_id`, `z_top`, `thickness`, `thickness_source`, `outline`, `openings` (`stair_void` with the stair id), `evidence` | the slabs between levels and under the lowest level |
| `roof` (new) | `type` (`flat`, `gable`, `hip`, `mansard`, `gambrel`, `shed`, `other`), `type_source` (`roof_plan`, `section`, `elevation`, `assumed`), `eaves_height`, `ridge_height`, `pitches_deg`, `overhang`, `thickness`, `outline`, `break_line`, `planes` (3D polygons), `openings` (roof terraces), `covering`, `evidence`, `assumed` | |
| `facade` (new) | `faces[]` (`wall_id`, `side`, `material`, `source`: `elevation`, `brief`, `style`, `assumed`, `evidence`), `sills`, `default` | |
| `site` | `ground` (`levels` per side with source), `north_deg` (value + source), `paving`, `grass`, `parking`, `terrain`, `build` per element | `site` becomes buildable (§3.2) |
| `furniture[]` | `modified_by_ai`, `drawn_type`, `drawn_footprint`, `drawn_height`, `anchor` (`kind`: `centre` / `back_edge`, `point`, `wall_id`), `type_proposal` | Feature 1: a drawn piece the AI changed |
| `furniture[]` | `completes_room` | Feature 1: a piece added to a room with drawn furniture |
| `furniture[]` | `design` (`front_style`, `colour`, `handle`, `worktop`, `material`), `shape` (`L` with `chaise_side`, `chaise_depth`) | Feature 3 looks; the corner sofa |
| `furniture[].type` | + `sofa_corner`, `chaise`, `ottoman`, `bench`, `bar_stool`, `office_chair`, `console_table`, `crib`, `bunk_bed`, `sideboard`, `shoe_cabinet`, `display_cabinet`, `tall_cabinet`, `wall_cabinet` | 14 new types |
| `decor[].type` | + `curtain`, `blind`, `throw`, `books`, `candle`, `basket`, `tray`, `clock`, `sculpture`, `plant_large`, `pendant_light`, `ceiling_light`; fields `species`, `pot`, `window_id`, `light_on` | 12 new decor types (`books` = library book stacks next to the parametric `book_set`) |
| `rooms[]` | `room_subtype` (`child`), `twin_of`, `same_as` | a child's room (cribs, bunk beds); the mirror twin of a semi-detached pair; the base room an alternative level's room equals |
| `documents[].pages[]` | `region_id`, `region_box`, `region_class` | one page record per region |

### 1.2 `sheets.json` (`results/run/<p>/sheets.json`; schema `wenart/schema/sheets.schema.json`)

```
{schema_version, kind: "sheets", project,
 documents: [{file, format, converter, units: {insunits, metres_per_unit, method, checks, conflict},
              sheets: [{id, space: model | layout:<name> | page:<n>, box, frames, debug_image}]}],
 regions:  [{id, file, sheet, box, box_m, entities, frame,
             class, class_method: title | geometry | ai | none, class_confidence, status: verified | unverified,
             title: {text, entity, box, language} | null, features: {...},
             level: {order, label, id, kind, method, evidence} | null,
             variant_group, variant, variant_slug,
             ai: [{pass, model, class, level_word, confidence, reason}],
             transform_to_building, registration: {reference, method, rotation_deg, shift_m, residual_m,
                                                  matched, stairs_aligned},
             use: read | heights | exterior | ignored, ignored_reason, evidence, conflicts}],
 stray:    [{file, sheet, entity, type, layer, box, distance_m, reason}],
 levels:   [{id, order, label, kind, base_region, alternatives: [{region, variant, slug}], evidence}],
 variants: [{id, label, regions}],
 heights:  {levels: [{level_id, floor_z, ceiling_height, floor_to_floor}], slabs: [{between, thickness}],
            ground: [{side, z}], roof: {eaves, ridge, pitches, knee_wall, overhang, thickness}},
 exterior: {roof, facade, openings_seen, site, north},
 conflicts, warnings, needs_review: [{region, reason}], questions}
```

Every height and exterior value is `{value, method: vector | ocr | ai | assumed, confidence, evidence, note}`.
Region classes: `floor_plan`, `alternative_floor_plan`, `furniture_plan` (kept from M2–M7: synthetic-03 and -05
have furniture plans), `section`, `elevation`, `roof_plan`, `site_plan`, `detail`, `3d_view`, `title_block`,
`legend`, `other`.

### 1.3 Brief keys (`wenart/defaults.yaml`, `wenart/brief.py`)

| Key | Default | Values |
|---|---|---|
| `furnished_rooms` | `complete` (user, 8 Oct 2026) | `keep` (M9's behaviour) / `complete` |
| `furnished_rooms_keep` | `[]` | room ids or labels that always stay `keep` |
| `furnished_rooms_keep_size` | `false` | `true`: drawn type and size stay, only the look changes |
| `variants` | `all` (user) | `all` / `base` / a list of alternative names |
| `failed_levels` | `leave_out` (user) | `leave_out` / `stop` |
| `site` | `full` (user) | `full` (plot, paving, grass, plot wall, parking as drawn) / `ground` (neutral ground plane) |
| `exterior` | `{}` | words for `facade`, `roof`, `window_frame`, `door`, `paving`, `garden`; empty = the interior style's words where they fit (window frames, the wall colour as smooth render), the rest assumed: roof covering anthracite concrete tiles, paving grey concrete pavers, garden grass (question 5 not answered: these defaults, listed as assumed) |
| `render.exterior_views` | `true` | exterior cameras on/off |
| `render.twin_rooms` | `one` (user) | `one` / `all` |

### 1.4 New vocabulary slugs (`wenart/style/vocabulary.py` re-exports; tables in new modules, §4)

Colours `colour:<name>` (≥ 40, §4.2); wall finishes `paint`, `lime_plaster`, `microcement`, `venetian_plaster`,
`wallpaper_<pattern>` (≥ 6), `wood_slat`, `stone_wall_<kind>`, `brick_<variant>`, `concrete_exposed`; wet walls
`tiles_subway`, `tiles_large_porcelain`, `tiles_zellige`, `tiles_hexagon`, `tiles_mosaic`, `marble_slab`;
floors (≥ 25, §4.3); cabinet fronts `flat`, `shaker`, `slatted`, `glass`; worktops `stone`, `wood`, `terrazzo`,
`steel`; handles `brushed_steel`, `black`, `brass`; doors `flush`, `shaker_panel`, `glazed`, `pocket`,
`sliding`, `barn`, `double`, `entrance`; window frames `pvc_white`, `aluminium_anthracite`, `steel_black`,
`dark_bronze`, `oak`, `painted:<colour>`; exterior `render:<colour>`, `brick_*`, `stone_cladding`,
`wood_cladding`, `fibre_cement`, roofs `clay_tiles`, `concrete_tiles`, `slate`, `standing_seam`, `green_roof`,
ground `paving`, `gravel`, `grass`, `decking`; lighting moods `bright noon`, `blue hour`, `cloudy soft`,
`interior evening`.

### 1.5 Stages (`wenart/run/stages.py`, `wenart/run/scheduler.py`)

`intake` → **`sheets`** (cpu, new) → `pipeline` (reads one page record per plan region) → `recognize` (also answers
the `sheet_region` questions, pass 1 Qwen3-VL-8B, pass 2 GLM-4.6V-Flash, as the M7 symbol questions) →
`pipeline_final` (runs `sheets --answers`, then the pipeline) → `photos` → `style` → `assets` → `fit` →
`layout` (empty rooms **and** the completion of furnished rooms, one Qwen session) → `decor_ask` → `decor` →
`refit` (+ the locked check, §2.7) → `build` / `render` / `export` **per variant** → `controls` → `gate` →
`polish` → `detect` → `expected` → `check` → `combine` → `report`. No new server start: the sheet questions ride
in the recognition sessions, the completion in the layout session.

### 1.6 Outputs per variant

`outputs/<p>/scene/scene.blend` and `renders/` stay the base variant (paths of M9 unchanged); an alternative
is the sub-output `outputs/<p>/variants/<variant id>/` (§1.6b row 9) with only the rooms that differ and, when its
outside differs, its exterior views. 3D files: `<p>.blend` / `<p>.glb` (base, the whole building) and
`<p>-<variant id>.blend` / `<p>-<variant id>.glb`.

### 1.6a Interfaces (commands, files, exit codes)

| Command / function | Owner | Contract |
|---|---|---|
| `python -m wenart.sheets <project_dir> --out outputs/<p> [--answers <out>/sheets] [--no-ai] [--work DIR]`; `wenart.sheets.analyse(project_dir, out_dir, answers=None, no_ai=False) -> dict` | A1 | writes `<out>/sheets.json` (schema §1.2), `<out>/sheets_report.md`, `<out>/sheets_debug/<file>_<sheet>.png`, and the `sheet_region` questions in `<out>/sheets/requests.json` (the M7 request format of `wenart/recognition/answers.py`, task `sheet_region`, crops in `<out>/sheets/crops/`); answered by `python -m wenart.recognition.answers ask <out>/sheets --model-key qwen\|glm ...` in the same server session as the recognition questions. Exit 0 done (answers complete, or `--no-ai`), 4 questions written and answers missing, 1 needs review (no readable plan region or no unit agreement in any document; `sheets.json` still written), 2 usage or crash |
| `python -m wenart.ingest.pipeline <project> --out <out> [--answers ...] [--no-ai]` | A1 | reads `<out>/sheets.json` when present, else runs `wenart.sheets.analyse` in-process (standalone runs and old tests); one page record per `use: read` region (`documents[].pages[].region_id`); writes `levels` (variant fields, kinds, section heights), `variants`, `levels_left_out`, `slabs` (outline, thickness, stair voids), `roof` (type, heights, outline, break line, ridge lines, terrace openings; `planes` may be empty), `facade` (drawn faces and `elevations`, §1.6b row 12), `site` (plot, areas, paving, parking, drawn ground levels, north), `variants[].rooms_changed / exterior_changed`, `rooms[].twin_transform`, `rooms[].room_subtype / twin_of / same_as`; exit codes unchanged |
| `wenart.blender.roof.planes_for(roof, building) -> list` (pure Python) | E | derives `roof.planes` when the pipeline leaves them empty; the builder records them in the scene manifest |
| `python -m wenart.furniture.layout <building_fitted.json> --style ... --out building_furnished.json --debug layout_debug/ --passes 2 [--project-dir projects/<p>]` | B | reads `furnished_rooms`, `furnished_rooms_keep`, `furnished_rooms_keep_size`, `render.twin_rooms` through `wenart.brief.load_brief(project_dir)` (default: the building's `project.source_folder`); also writes `completion.json` and `completion_report.md`; runs `locked.check(source=building_fitted.json, final=building_furnished.json)`: a violation exits 1 |
| `wenart.furniture.locked.check(source, final, mode, keep_rooms=None) -> list[str]` | B | as built (§1.6b row 16); an empty list = pass; called by the layout CLI and by `fit --source building.json --completion completion.json` (refit; F adds the flags, the lead passes them) |
| `python -m wenart.blender.cli build\|render\|export ... [--variant <id>]` | E | `--variant` default `base`: the base writes the M9 paths, an alternative writes `outputs/<p>/variants/<id>/{scene,renders,export}/`; exterior views are cameras `ext_<n>` in the same render list (kind `exterior` in the scene manifest); `views_for(building, variant)` in `wenart/views.py` returns the interior views of the variant's rooms to render (base: every room except a second twin with `twin_rooms: one`; alternative: `rooms_changed`) and the exterior views (base; an alternative only when `exterior_changed`) |
| Style profile (`style.json`) | C | adds the slots `exterior` (facade, roof, window_frame, door, paving, garden: slug, colour, source, assumed), `colours` (the brief's colour words per object), `wall_accent`, `wet_walls` (tile kind, size, colour, grout), `cabinets` (front, colour, handle, worktop), `doors`, `window_frame`, `furniture` (fabric colour, wood, material tags), `decor` (species, pots, cushion colours); `style.exterior_fallback` of `defaults.yaml` for the rest |

Every new output is listed by the stage records (`run/<stage>.json` `outputs`) and copied by `wenart.run copy` (lead).

### 1.6b Amendment 1 (contract review of 8 Oct 2026: 6 review lenses, one adversarial verifier; 82 findings confirmed)

Where this list and older text above or below disagree, this list wins. Schema, examples and tests changed with it
(commit "M10 contracts amendment 1"); `tests/test_m10_contracts.py` pins the examples, their cross-file agreement and the
conventions below.

| # | Topic | Contract now |
|---|---|---|
| 1 | Frames and angles | Building z = 0 at the finished floor of the order-0 level; fields say "building z" (absolute) or "above the level floor". The building XY frame is the reference plan's frame in metres, origin at the min corner of its outer outline (outer wall faces, the `generic/core.py` step-8 rule); `registration.shift_m` / `rotation_deg` map a region's drawing (source units × metres_per_unit) onto the reference drawing (`p_ref = R·p + shift_m`), `transform_to_building` = the reference's origin step after that map, and the extractor uses it instead of its own origin step. Angles: degrees counter-clockwise from +X, front = local −Y, `front_deg = (270 + rotation_deg) mod 360`; compass bearings (`azimuth_deg`, `north_deg`) clockwise from north. Sides: `$defs/side` (compass when north is known, else front = −Y, back = +Y, left = −X, right = +X). Sections: x → building coordinate along `cut_axis` (`cut_at`, `flipped`), y → building z; elevations: x from the facade's left end seen from outside; site plans registered through their building outline (`site_outline`). The examples are shifted into this frame |
| 2 | Region ids, page records | Region ids `r<n>` unique in the project (documents in `classify.project_documents` order, then sheets, then reading order). One page record per region with use `read`, `heights` or `exterior` (`region_box` always set); ignored regions only in `sheets.json`. Page work is keyed by (file, page, region_id); a region record takes level id, label, order, kind and label source from `sheets.json`; an alternative never merges into its base. Debug images and plan crops of a region page render only its `region_box` (`debug_image.raster_from_dxf(..., clip_box=)`; H passes it in `plan_crop`) |
| 3 | Units | `pages[].scale.method` += `unit_check` (the unit check decided; evidence names the agreeing checks; a `unit_mismatch` conflict names the header). The examples show the real02 case ($INSUNITS 4, cm) |
| 4 | Copies vs alternatives | An alternative group needs ≥ 2 plans of one level **in the same document** whose titles differ by an alternative word or an extra bracket. The same level in another document or with the same title is a copy: the trust-order master is `base_region`, the others `secondary_regions` (M7 cross-check evidence), never an alternative (synthetic-01/02/04 keep their M7 behaviour) |
| 5 | Titles, strays | A title is searched only among the texts joined to the region; one title entity serves one region. With a frame, a cluster outside every frame with < 1 % of the entities is stray; without a frame the 10 × median rule |
| 6 | Heights | `sheets.heights.levels`: one entry per base level; alternatives copy their base's values. `level_mark` = printed mark − datum (building z), `level_mark_target_z` = the z the mark points at; > 5 cm apart → `level_mark_mismatch`. `project.datum` = the printed absolute level at z 0. No section: floor to floor 3.00 m, slab = brief `slab_thickness`, ceiling = brief `ceiling_height`, all `assumed` (the rest an assumed plenum). `$defs/value`: `assumed` needs a note and confidence 0; vector/raster/ocr/derived need evidence; `ai` never builds geometry |
| 7 | Brief keys in the pipeline | The pipeline (A1) reads `failed_levels`, `variants`, `slab_thickness`, `ceiling_height` through `wenart.brief.load_brief`. `leave_out`: the level (and the base levels above it) go to `levels_left_out`, status stays `ok` while ≥ 1 level remains; a failed alternative removes only its variant; `stop`: `needs_review`. `variants: base`: alternatives read but not in `variants[]`; a list keeps alternatives whose name, slug, gloss or id matches after `fold_ascii` + strip; unknown names are a warning |
| 8 | Variants | Ids `base` or `wenart.building.variant_id(level_id, slug)` (`l-1b-acik-mutfak`), slugs `wenart.building.variant_slug` (hyphens); patterns in the schema. `rooms_changed` / `exterior_changed` are written by the pipeline (A1) (rooms with `same_as` null; outer walls or openings without a base match), read by build, render and `views_for`. A slab that differs for an alternative is written again as `sl_<above>__<variant id>`; otherwise ids name base levels/stairs and a variant maps them through `changes` |
| 9 | Variant outputs | An alternative is a sub-output `outputs/<p>/variants/<variant id>/` with a project output's layout (`scene`, `renders`, `export`, `controls`, `check`, `gate`, `polish`, `detect`, `final`, `run`); its scene manifest names `outputs/<p>/building_final.json` and `--variant <id>`; every downstream CLI runs unchanged with `--project-out outputs/<p>/variants/<id>`; the gate calibration is the base project's (reused); 3D files `<p>-<variant id>.blend/.glb` hold the whole building with the alternative level; its renders only the changed rooms (and the exterior views when `exterior_changed`). The CLI keeps an explicit `--out`; the scheduler picks the paths (lead); H's report adds a Variants section |
| 10 | `views_for` | `wenart.views.views_for(building, variant="base", brief=None) -> {variant, rooms: [ids to render], skipped: [{room_id, reason: "twin of <id>" / "same as <id>" / "unchanged in variant"}], exterior: bool, exterior_from: "base" / <id>}`; base = every room of the base levels minus second twins (`twin_rooms: one`); alternative = `rooms_changed` minus second twins; exterior = `render.exterior_views` and (base or `exterior_changed`). Cameras are matched afterwards from the scene manifest |
| 11 | Scene manifest (E owns `wenart/blender/schemas.py`) | Camera `{name, kind: interior/exterior, room_id (null for exterior), level_id, index ≥ 1, variant, view: corner/aerial/elevation/null, sides, region_id, dropped_reason}`; object kinds += `slab`, `roof`, `facade`, `terrain`, `site_wall`, `site_area`, `site_decor`, `light_well`, `railing`; `views.KIND_MAP` never maps them to furniture; H's `expected.py` cross-checks the openings on the exterior walls of the variant's levels for exterior cameras |
| 12 | Drawn vs resolved looks | `facade` holds drawn faces only (`side` + optional `wall_id`, `z_range` in building z, source `elevation`, evidence ≥ 1) and `elevations[]` (one per elevation region: `region_id`, `side`, `view_bearing_deg`, counts, positions; `plan_check` filled by the pipeline). `roof.covering` only when drawn. Every other look is resolved by the build (`wenart.blender.exterior.resolve_looks(building, style)`, E, pure: documents > brief `exterior:` words > `style.json` exterior > `style.exterior_fallback`), recorded in the scene manifest (`exterior_looks`) and the report, never written back. Site: `ground` holds drawn levels only (one assumed `all 0.0` when none); the basement-door terrain and light wells are the build's, in the manifest; `site.areas` are label records (`build: false`), built surfaces are `plot`, `paving`, `grass`, `parking` (`area_id`), `boundary_walls`, `site.decor` |
| 13 | Roof | `planes[].points`, `eaves_height`, `ridge_height`: the top surface, building z; `thickness` perpendicular to the slope; `overhang` only without a drawn outline; `knee_wall` a cross-check (walls and attic ceilings are cut from the planes' underside); `profile {region_id, cut_axis, points [s, z], method}` from the section; `aspect_deg` in the front convention (not a compass bearing); terrace openings extend over the outer walls to the outline (`parapet_wall_ids`). Attic `ceiling_height` = the flat ceiling part (else the underside at the ridge); attic walls end at the roof underside. No roof evidence → `roof: null` and the build makes a flat roof over the top level (assumed) |
| 14 | Slugs and colours | A slug never carries a colour: `{material, colour}` with `colour` a `wenart/style/colours.py` name; `defaults.yaml style.exterior_fallback` reshaped so (facade render + the wall colour, roof concrete tiles anthracite, paving grey, garden grass). `design.material_tags` enum glass, wood, metal, fabric, rattan, marble; `design.wood` a `wood_veneer_*` slug |
| 15 | Furniture | `mount_bottom_m` (wall-hung pieces: wall cabinets 1.45 by rule; not floor obstacles: exempt from no_overlap with floor pieces, door strips and walkways; never over a window or within 0.3 m of one, never over the stove **or a door**); L shape: `chaise_side` (right = local +X, a viewer facing the front), `seat_depth`, `chaise_width` (default 0.9), `chaise_depth` = footprint depth, `schemas.l_parts` the one geometry source; conditional rules: `modified_by_ai` → drawn values and anchor, `completes_room` → `added_by_ai`, `type_proposal` → `unverified`, `shape L` → `sofa_corner`, `wall_cabinet` → `mount_bottom_m`; `rule`, `checks` documented; `design` written by the layout stage (B) for every piece of a completed or kept room (cabinets from `style.json`; vanity = washbasin depth ≥ 0.45; built-in = wardrobe touching walls at both ends; agreed colour → `fabric_colour` for upholstered types, else `colour`), only read by the fit and the build. A type proposal keeps `drawn_type` (e.g. `unknown`), footprint and front; no `modified_by_ai` |
| 16 | Locked check (as built by B) | `locked.check(source, final, mode, keep_rooms=None)`; `mode` from `completion.json` (`locked.mode_of`), `keep_rooms` from `locked.keep_rooms_of`; `furnished_rooms_keep_size` asks no changes (empty `changes`) but allows additions. Refit: `fit --source building.json --completion completion.json` runs it and exits 1 on a violation (F adds the flags; the lead passes them) |
| 17 | Openings | `operation` (swing, double, sliding, pocket, folding, fixed, unknown; null = swing, assumed) + `operation_source`, written by A3 (openings, symbols), read by F (door looks) |
| 18 | Twins | `rooms[].twin_transform` (affine, first twin → this room) and `twin_residual_m`, written by the pipeline (A1, `wenart/ingest/twins.py`); B also derives the mirror from the polygons when absent; decor of second twins and `same_as` rooms is copied (mirrored) from the partner (F: `decor_ai` skips them, `decor` copies with `mirrored_from`) |
| 19 | Evidence | `region_id` and `rule` in both schemas' evidence (`wenart.building.evidence(..., region_id=, rule=)`) |
| 20 | Ownership changes | A1 += `wenart/ingest/{model,debug_image,dxf_extract}.py`, `wenart/ingest/generic/{core,labels}.py` (the M10 level-word table lives in `wenart/sheets/levels.py`; `building.normalise_level_label` unchanged). E += `wenart/blender/schemas.py`, `resolve_looks`. F += §4.8 exterior materials in Blender, a new `wenart/blender/looks.py` of pure functions E calls from `shell.py` (`wall_face_material`, `accent_walls`, `wet_wall_look`, `door_look`, `window_frame_look`, `facade_look`; each starts as today's default) and `materials.exterior_material(library, slug, colour=None)`, decor host tables for the new types, decor twins. C += the `defaults.yaml` blocks `style.profile` and `style.exterior_fallback`, `profile.BUILTIN_DEFAULTS` (incl. `exterior_fallback`), the polish word tables `MATERIAL_WORDS` / `MOOD_WORDS` / `FAMILY_WORDS`, `tests/test_assets.py`, `tests/test_blender_materials.py` (lead reviews). H += `wenart/polish/{prompt,runner}.py` exterior prompts and the per-kind (interior / exterior) gate decision, `wenart/gate/colour.py`. Lead: `FURNITURE_WORDS` for the 14 types (done), `wenart/run/plan.py` |

### 1.7 `CLAUDE.md` furniture rules (the user's OK of 8 Oct 2026; `CLAUDE.md` edited)

Today:
> - Furniture and fixed equipment drawn in the documents are treated like walls: same type, position, orientation
>   and footprint size as drawn. Style changes only the look (materials, colors, design details).
> - Rooms that have furniture in the documents: never add, remove or move furniture. Small decor (cushions,
>   plants, books) only if the brief allows it (default: yes).

Proposed:
> - Fixed equipment drawn in the documents (stairs, kitchen counter runs and appliances, sanitary ware) is treated
>   like walls: same type, position, orientation and footprint size as drawn. Style changes only the look.
> - Drawn furniture is never removed. Its location (footprint centre ± 5 cm; against a wall: the back edge on the
>   same wall line) and position (front ± 1°, the same wall) are locked. With `furnished_rooms: complete` AI may
>   change its type (within the room type's types), size, height and look: it stays `from_documents`, gets
>   `modified_by_ai: true` and keeps the drawn values (`drawn_type`, `drawn_footprint`, `drawn_height`). With
>   `keep` or `furnished_rooms_keep_size` only the look changes.
> - Rooms that have furniture in the documents: with `furnished_rooms: complete` AI may add the pieces the room
>   type misses (`added_by_ai`, `completes_room: true`), through the same placer checks as empty rooms; never a
>   second anchor piece. Small decor (cushions, plants, books) only if the brief allows it (default: yes).

## 2. Feature 1 – AI completes rooms with drawn furniture (`wenart/furniture/complete.py`, new)

### 2.1 Rooms

A room is completed when `furnished_rooms: complete`, it has documented furniture, its type is furnishable
(`schemas.ALLOWED_TYPES`), it is not a never-furnished type (prayer; storage and balcony have no allowed types)
and it is not in `furnished_rooms_keep` (by id or label). Every other room keeps M9's behaviour. Rooms of an
alternative level that equal a base room (`same_as`) and mirror twins (`twin_of`, when `render.twin_rooms: one`)
take the answer of their partner (copied, mirrored for twins), so they stay identical and are asked once.

### 2.2 Drawn pieces

| Kind | Types | What AI may do |
|---|---|---|
| Fixed equipment | `stair`, `kitchen_counter`, `sink_kitchen`, `stove`, `fridge`, `washing_machine`, `kitchen_island`, `toilet`, `washbasin`, `shower`, `bathtub` (user, 8 Oct 2026) | nothing but the look (cabinet fronts, colours, §4.4) |
| Not furniture (`build: false`) | drawn symbols both AI passes call not furniture | nothing (obstacle) |
| Changeable furniture | every other drawn type | type (within the room type's allowed types), width, depth, height, model, design, materials, colours |

Locked for a changeable piece (checked, §2.7): the **anchor** point (a free piece: the footprint centre; a piece
whose back edge touches a wall within 5 cm, `placer.WALL_TOUCH_M`: the midpoint of the back edge, and the wall id)
within ± 5 cm; `front_deg` within ± 1°; the same wall. A new footprint grows or shrinks around the anchor: a free
piece around its centre, an against-wall piece from the wall line (its centre moves along the front direction by
half the depth change). With `furnished_rooms_keep_size: true` the drawn type and size stay and only the look
changes (M9's behaviour for drawn pieces). An `unknown` or `unverified` drawn piece keeps `status: unverified` and
its drawn values; an agreed AI type becomes its `type` with `type_proposal: true`, drawn in the debug image with
the proposal mark and listed with the unverified items.

### 2.3 Question and answer

Same server, model and request shape as M4 (`layout.build_text_request`: Qwen3-VL-8B, two passes, temperature 0,
pass 2 with another block order and seed, strict JSON schema as the vLLM grammar). The question gives the room
(label, type, subtype, polygon, area), doors (approach, swing), windows (sill), the drawn pieces (id, type, box,
front, anchor, against-wall wall, fixed or changeable), the room type's allowed types with their size options and
the **missing** types (`EXPECTED_TYPES`, below), and the style text. The schema is built per room:

```
{"changes": [{"id": <enum: changeable drawn ids>, "type": <enum: allowed types>, "size": [w, d],
              "style": <enum: style families>, "colour": <enum: vocabulary colours>, "reason": str}],
 "added":   [{"type": <enum: allowed types>, "center": [x, y], "rotation_deg": n, "size": [w, d],
              "against_wall": bool, "reason": str}]}
```

| Room type | Anchor (one only) | Expected (missing → asked for) | May also add (max count) |
|---|---|---|---|
| bedroom | bed (`bed_double`, `bed_single`; child: `bed_single`, `bunk_bed`, `crib`) | `nightstand` (2 with a double bed, 1 with a single bed), `wardrobe` | `dresser`, `desk` + `office_chair`, `bench` (bed foot), `armchair`, `bookshelf`, `ottoman` (1 each) |
| living | `sofa` / `sofa_corner` | `table_coffee`, `tv_unit` | `armchair` (2), `chaise`, `ottoman`, `console_table`, `sideboard`, `bookshelf`, `display_cabinet` (1 each) |
| dining | `table_dining` | `chair` (4 at 1.2 m, 6 at 1.6 m, 8 at 2.0 m table length) | `sideboard`, `display_cabinet`, `bench` |
| kitchen | `kitchen_counter` (fixed) | – | `bar_stool` (2–4, only at a drawn island), `table_dining` + `chair` (when ≥ 1.2 m free), `tall_cabinet`, `wall_cabinet` (rule, §4.4) |
| hall | – | – | `console_table`, `shoe_cabinet`, `bench` |
| other | – | – | as M4 |
| bathroom, wc | fixed | – | nothing (sanitary ware hangs on plumbing) |

A type counts as covered when the room holds its maximum count of it; a second anchor is never allowed (no second
bed, sofa, dining table, toilet). Changes may only name changeable drawn ids; added pieces only uncovered types.

### 2.4 Agreement

- A **change** is kept when both passes change the same drawn piece to the same type; the size is the smaller of
  the two size options, the style and colour the ones both name (else the project's). A change only one pass
  proposes is listed, not applied (a drawn piece needs both).
- **Added** pieces as M4: the pass with the fewest dropped pieces wins (ties: pass 1); a piece the other pass also
  proposed (same type, centre within 0.5 m) gets confidence 0.9, the rest 0.6.

### 2.5 Placement (`wenart/furniture/placer.py`)

Order: fixed and unchanged drawn pieces are locked obstacles; changed drawn pieces are placed next at their anchor
and front (repairs: `shrink` to the next smaller size option, then `revert` to the drawn type and size; never
snap, slide or relocate); then the added pieces with the full M4 repairs (snap, slide, shrink, relocate, drop),
giving way to every drawn piece. Checks: the six M4 checks (inside the room, no overlap, front clearance, doors
and the 0.9 m walkways, the window band, wall contact). A changed piece may not fail a check its drawn version
passes and may not make another piece fail; a check the drawn layout already fails is recorded as
`drawn_layout`, not counted against the AI. New: the L-shaped `sofa_corner` (`shape: L`) is an L polygon in every
check (its free inner corner can hold a coffee table).

### 2.6 Labels, report, debug image

- Changed drawn piece: `source: from_documents`, `modified_by_ai: true`, `drawn_type`, `drawn_footprint`,
  `drawn_height`, the anchor, and two more evidence entries (`method: ai`, `model`, `pass`, `text`: the reason).
- Added piece: `source: added_by_ai`, `completes_room: true`, `status: verified`, evidence as M4 with the six
  checks.
- `completion.json` and `completion_report.md` (per room: both passes, agreed changes `drawn type / size → new
  type / size`, added pieces, dropped and refused proposals with the reason, `drawn_layout` notes) and one PNG +
  JSON per room in `layout_debug/` with three colours: drawn as drawn (green), drawn but changed by AI (blue, the
  drawn outline dashed under the new one, the anchor marked), added by AI (orange); proposals for unverified pieces
  hatched.
- The final report lists every change per room (drawn → new) and every added piece.

### 2.7 Locked check (`wenart/furniture/locked.py`, new)

`locked.check(source, final)` compares every drawn piece of `building.json` with `building_final.json`: present
(never removed), same level and room, anchor within 5 cm, `front_deg` within 1°, the same wall, `from_documents`
kept, fixed equipment unchanged in type and footprint (byte-equal), walls, openings and rooms unchanged
(byte-equal). It runs at the end of `layout` and of `refit`; a violation fails the stage. In `keep` mode it is the
old byte rule (`fit.FROZEN_KEYS`) for every drawn piece. `fit.FROZEN_KEYS` stays as the fit's own in/out guard.

### 2.8 Downstream

`decor_ask` / `decor` run after the completion, so the new and changed pieces get decor (M9 slots). `refit` fits
the new types and sizes. `expected`, `check`, `plan_crop`, `detect` and the controls read `building_final.json`, so
a changed type or size and an added piece are expected (never flagged as a mismatch or an insertion); the
cross-check against the source plan checks the anchor and front of every drawn piece against its drawn footprint;
the plan crop draws the three colours of §2.6.

## 3. Feature 2 – sheets first, the whole building, exterior views

### 3.1 Stage `sheets` (`wenart/sheets/`, new)

1. **Split** (`split.py`). DXF/DWG: model space and every non-empty layout (viewports give regions). Entity boxes
   (INSERTs by their block geometry) are clustered with a gap of 1.5 % of the sheet's diagonal (the frame's, else the 2–98 % entity box's; real02:
   149 units, the drawings are 500–665 units apart; tested 0.5–3 %);
   frames (closed rectangles holding ≥ 2 clusters) and texts never bridge clusters; texts join the nearest region
   by insertion point; title boxes and title blocks (a rectangle on the frame edge with many short texts) are their
   own regions. A cluster far outside the frame or > 10 × the median region size away with < 1 % of the entities is
   **stray**: listed, ignored. PDF vector pages: the same on path boxes. Raster pages: the M7 crop-to-drawing code
   finds ink components at 50 dpi, grouped with the same gap rule.
2. **Classify** (`classify.py`). Evidence order: the region's own title (TEXT/MTEXT or OCR; the largest text
   within 0.3 × the region height below or above it) through a keyword table (Turkish, English, German, French:
   `KAT PLANI`, `PLAN`, `FLOOR PLAN`, `GRUNDRISS`, `PLAN DU`; `KESİT`, `SECTION`, `SCHNITT`, `COUPE`; `GÖRÜNÜŞ`,
   `ELEVATION`, `ANSICHT`, `FAÇADE`; `VAZİYET PLANI`, `SITE PLAN`, `LAGEPLAN`, `PLAN DE MASSE`; `ÇATI PLANI`,
   `ROOF PLAN`, `DACHAUFSICHT`, `PLAN DE TOITURE`; `DETAY`, `DETAIL`; `MOBİLYA PLANI`, `FURNITURE PLAN`; `LEJANT`,
   `LEGEND`; `PERSPEKTİF`, `3D`); then geometry (plan: closed wall loops and room labels, M7's wall test; section:
   ≥ 2 long horizontal line pairs (slab bands) across ≥ 50 % of the width, a roof line above, level marks; elevation:
   a ground line, an outline and ≥ 3 window-like rectangles in rows, no slab bands; site plan: a small closed
   building outline inside a larger boundary, a north arrow or street words; roof plan: a closed outline with hip,
   valley or ridge lines and no room labels); then two AI passes on a rendered crop (`sheet_region` question,
   1024 px, temperature 0, strict schema: class enum, level word, confidence, reason). AI proposes, title text and
   geometry decide: an AI-only class is `unverified` and never makes a plan.
3. **Levels** (`levels.py`): `BODRUM` / `BASEMENT` / `UNTERGESCHOSS` / `KELLER` / `SOUS-SOL` = −1; `ZEMİN` /
   `GROUND` / `ERDGESCHOSS` / `REZ-DE-CHAUSSÉE` = 0; `1. KAT`, `FIRST FLOOR`, `1. OG`, `1ER ÉTAGE` … = n; `ÇATI KAT`
   / `ATTIC` / `LOFT` / `DACHGESCHOSS` / `COMBLES` = the top level, kind `attic` (`ÇATI PLANI` without `KAT` is a
   roof plan). An untitled plan gets a level only when exactly one level is free and its outline fits (assumed,
   listed); else M7's `needs review`.
4. **Alternatives** (`variants.py`): two plans of one level form a group; the base is the one whose title has no
   alternative word (`ALTERNATİF`, `SEÇENEK`, `OPSİYON`, `VARYANT`, `ALTERNATIVE`, `OPTION`, `VARIANT`,
   `VARIANTE`) and no extra bracket; the others are alternatives named by that word or bracket (`( Açık mutfak)` →
   `Açık mutfak`; a short gloss table adds `open kitchen`). Unclear → the first in reading order is the base,
   `unverified`, and the report asks. Alternatives are never merged: each becomes its own level.
5. **Registration** (`register.py`): the reference is the base ground-floor plan (else the lowest base plan with a
   closed outline). Every other plan: candidates from the outline box centres at 0/90/180/270° (a mirror is a
   conflict), refined by ICP of the outer outline vertices; matching grid bubbles (circle + one letter or number)
   and columns win when ≥ 3 match; stairs of adjacent levels must overlap. The shift, rotation and residual (RMS
   outline distance) are recorded; a residual over 5 cm is a conflict `registration_residual`. The registered
   outlines go through the existing outline cross-check.
6. **Units** (`units_check.py`): every DXF/DWG gets a unit check before any wall is read: candidate units (mm, cm,
   m, inch, ft) scored by room-area labels vs region areas, section level marks vs slab spacing, door arcs (0.6–1.2
   m), wall thicknesses (0.08–0.6 m) and text heights; `$INSUNITS` is used when the checks agree with it; when ≥ 2
   independent checks agree on another unit and none supports the header, that unit is used and the conflict
   `unit_mismatch` is listed (user, 8 Oct 2026); no agreement → `needs review` with the region named.
7. **Heights** (`heights.py`) from the section and elevations (vector): slab bands (thickness, top), floor to floor,
   ceiling heights (floor to the underside above; the attic to the roof underside), level marks (`±0.00`, `+3.00`,
   `43.00` next to a mark triangle) as cross-checks (a mismatch over 5 cm is listed, geometry wins), ground lines per
   side, roof pitches, eaves and ridge heights, overhang, roof thickness, the attic knee wall; DIMENSION entities
   measured from their points. Section levels map to the plan levels bottom-up; the section width must match the
   registered plans' extent along one axis (± 1 % or 5 cm), which also gives the cut direction. What no drawing
   gives is `assumed` and listed (ceiling 2.70 m, slab 0.20 m, as today's defaults).
8. **Exterior evidence** (`exterior.py`): from elevations, the roof plan, the site plan and the top plan's roof
   lines: roof type (flat, gable, hip, mansard, as drawn; the roof outline and a closed break line on a plan mean a
   mansard), facade materials where hatched or labelled (`SIVA`, `TAŞ KAPLAMA`, `AHŞAP`, `TUĞLA`, render, brick,
   stone, timber), windows and doors seen from outside (count and position per facade, cross-checked against the
   plans), balconies, terraces, chimneys, plot wall, paving, garden, parking, trees, the north arrow.
9. **Output**: `sheets.json` (§1.2) and one debug image per sheet (every region boxed and labelled with class,
   level and variant, coloured by method and confidence; strays circled; registration residuals per plan). The
   pipeline then reads each plan region as its own page record (`region_id`, the region box as a clip; DXF
   entities by box, PDF pages cropped, raster images cropped). A project whose sheets are one region per page
   (synthetic-01 … -06, real01) gives today's page records unchanged.
10. **Stop rules**: missing scale or no closed outer walls on a needed plan → `needs review` with the region named,
   or, with `failed_levels: leave_out` (the default, user), that level is left out, listed as missing, and the
   building above it is not built floating (levels above a missing level are left out too).
11. **Walls drawn as face lines** (`wenart/ingest/generic/walls.py`, track A3; found on real02, §0.4): a new wall
   primitive for DXF/DWG and vector PDF: straight strokes of one layer that pair up as parallel faces 0.05–0.60 m
   apart with ≥ 0.4 m overlap and no stroke between them, joined at corners and T-junctions; columns (small closed
   rectangles or solid fills on a structural layer, or 0.15–0.8 m squares where pairs meet) join the wall mask.
   The wall layer is chosen by evidence, not by its name: per layer the share of its strokes that pair up, the
   pair widths, whether the paired network closes around the room labels; the best layer wins when it explains
   ≥ 70 % of the labelled rooms, the choice and the runner-up are reported. Confidence 0.8 (`vector`), the layer
   choice in the evidence. A polyline whose ends meet within 1 mm counts as closed. Furniture, tile and decor
   layers never feed walls (a layer whose pairs do not close around labels is ignored). synthetic-07 draws its
   walls this way too.

### 3.2 The whole building (`wenart/blender/`)

1. Levels stacked at their elevations; slabs from the outline of the outer walls (`slabs[]`), thickness from the
   section; stairs connect the levels through a stair void cut in the slab above (M7's `plan_stairs` with the floor
   to floor rise; the upper level's stair must sit over the lower one, else a warning).
2. Attic: room ceilings follow the roof underside (sloped faces from the roof planes, flat where the section shows a
   flat part); outer walls end at the roof underside (knee walls); the stair void through the attic floor.
3. Roof from the section profile and the roof outline / break line of the plans (mansard on real02); without a roof
   plan or elevation the profile is extruded across the building and the hip/gable choice is `assumed`; roof
   terraces (balcony or terrace rooms of the top level) stay open to the sky with a parapet (height assumed when not
   drawn); covering from the exterior style.
4. Facade material on the outward faces of the outer walls (`facade`); window frames and glass visible from
   outside; exterior sills (assumed size); balconies with railings (height assumed when not drawn).
5. Site (`site: full`): ground plane at the ground level of each side, plot wall, paving, grass, parking, trees as
   drawn; a basement wall with an outside door gets the terrain at the basement floor on that side, basement
   windows below ground get a light well (both `assumed`). With `site: ground` only the ground plane and the light
   wells. Every detail no drawing gives is `assumed` in the scene manifest.
6. One scene per variant (only the alternative level changes). Rooms: a room of an alternative level differs when
   no base room equals it (polygon within 2 cm, the same openings, the same drawn furniture); the alternative renders
   only those (`variants[].rooms_changed`) and its exterior views only when its outer walls or outer openings differ
   (`exterior_changed`); otherwise the base images are listed for it.
7. Twins (semi-detached pairs, `twin_of`, user: `one`): with `render.twin_rooms: one` only the first twin of
   each mirrored pair is rendered; the AI completion and decor of the first twin are mirrored onto the second, so the
   exterior and the 3D files show both dwellings the same.
8. 3D files per variant (`<p>.blend` / `.glb`, `<p>-<slug>.blend` / `.glb`), packed and split as in M9.

### 3.3 Exterior views (`wenart/blender/exterior.py`, new)

1. Cameras: 4 eye-level views (1.6 m above the terrain) from the plot corners, or 10–15 m from each building corner
   along its diagonal when no plot is drawn, aimed at the corner so both facades show; one 3/4 aerial view (30°
   down); one view per drawn elevation (same direction as the drawing). Vertical lines stay straight (camera level,
   lens shift); a camera inside a wall, roof, tree or the plot wall, or whose view of the building is blocked, moves
   along its diagonal (10–15 m) and is dropped with the reason when no place works.
2. Light: the style's HDRI and sun; the building's north from the site plan's north arrow, else +Y (`assumed`).
3. Style: the brief's `exterior:` words (§4.8), the style photos, documents win where they say something.
4. Checks: the gate and the vision check run on exterior views too (expected: the facade openings in view); the
   elevation check compares per facade the window and door count and positions (building JSON vs drawn elevation,
   deterministic) and the built ridge and eaves heights vs the section; the VLM counts windows per visible facade
   (advisory, as the other vision checks).
5. Polish of exterior views under the same gate, calibrated per project with exterior negatives; a failed
   validation keeps the exterior views Cycles only.
6. Report: a "Building" section (levels, variants, heights drawn or assumed, roof, facade, conflicts) and a contact
   sheet of the exterior views per variant.

### 3.4 Test data: synthetic-07

One DXF sheet (model space; a DWG copy through `dxf2dwg`) with a frame and title block, a basement plan, its
alternative `BODRUM KAT PLANI (AÇIK MUTFAK)`, a ground-floor plan, an attic plan (`ÇATI KAT PLANI`) with the roof
outline, a section `A-A KESİTİ` with level marks and a gable roof, two elevations (`GÜNEY GÖRÜNÜŞÜ`, `DOĞU
GÖRÜNÜŞÜ`) with hatched facade parts, a site plan (`VAZİYET PLANI`) with a north arrow, plot wall, parking and
garden labels, a legend, and one stray entity far away; drawn in cm with `$INSUNITS` = cm. Ground truth
(`projects/synthetic-07/truth/`): every region box, class, level, variant, the registration shifts, every height
(floor to floor 3.00 m, slab 0.20 m, ceiling 2.80 m, pitch 35°, eaves, ridge, knee wall 1.00 m, ground ±0.00) and
the per-facade openings. Unit tests add rotated plans, a mm/cm unit conflict, an untitled alternative and a
section with marks that disagree. Documented in `docs/synthetic.md`.

## 4. Feature 3 – a larger material, colour and furniture library

Rules kept: textures CC0 only (Poly Haven, ambientCG), every id verified against the live APIs (here, 8 Oct 2026;
a site the session cannot reach is verified on the pod and recorded); models from ABO, Objaverse (licence flagged)
and TRELLIS.2 for gaps, judged by both vision models on thumbnails, front agreed, style tags; credits in
`ATTRIBUTION.md`; keyword tables deterministic; unknown words listed, never guessed.

### 4.1 Phrase parsing (`wenart/style/profile.py`)

Phrases split at commas and semicolons **outside** brackets. Each phrase gets an **object** (walls, accent wall,
floor, ceiling, sofa, armchair, chair, bed, cushions, throws, curtains, rug, cabinets, kitchen, worktop, furniture
wood, coffee / dining table, doors, handles, window frames, pots, plants, facade, roof, paving, garden, lighting)
from an object word table, then its colours, modifiers and materials. A colour applies to the phrase's object only
("cream pots" colours the pots, never the walls); a bare colour phrase with no object stays M3's wall colour. Two
colours with "and": cushions, throws and rugs alternate them; walls take the first as the main colour and the
second for one accent wall per living room and bedroom (the wall behind the sofa or the bed head, else the longest
wall without a window), listed; "one sage accent wall" names the accent alone.

### 4.2 Colours (`wenart/style/colours.py`, new)

≥ 40 named colours (whites, off-white, ivory, cream, greige, taupe, beige, sand, light / mid / dark grey,
anthracite, charcoal, black, sage, olive, forest green, emerald, navy, dusty blue, sky blue, teal, terracotta, rust,
mustard, ochre, blush, dusty pink, burgundy, plum, chocolate, walnut brown, camel, caramel, bronze, brass, copper,
…), each a documented sRGB value with its source (W3C CSS Color 4 named colours, RAL Classic sRGB references, the
xkcd colour survey (CC0); the source per value in the table), converted to linear RGB in code (IEC 61966-2-1
transfer function). Modifiers in CIELAB: `light` / `dark` (L* ± 12), `pale` / `deep` (chroma × 0.6 / 1.3), `warm` /
`cool` (hue ± 8° towards yellow / blue), `muted` (chroma × 0.7). Colours work on walls, fabrics, cabinets, doors,
window frames, facades, pots.

### 4.3 Wall finishes, wet walls, floors (`wenart/style/finishes.py`, new)

| Area | Today | Target |
|---|---|---|
| Walls | plaster white / cream / charcoal, brick, wood panel | paint in any vocabulary colour, lime plaster, microcement, Venetian plaster, wallpaper (≥ 6 patterns: stripe, botanical, geometric, check, herringbone, grasscloth), wood slat panelling, stone, brick (red, white-painted, grey, reclaimed), exposed concrete; accent walls (§4.1) |
| Wet walls | one procedural tile | subway (7.5 × 15 cm), large-format porcelain (60 × 120), zellige (10 × 10, colour spread), hexagon, mosaic (2.5 cm), marble slab; tile size, colour and grout colour from the brief |
| Floors | 8 | ≥ 25: oak natural / white-washed / smoked / grey, wide plank, herringbone and chevron in 3 tones, walnut, ash, bamboo, terrazzo, travertine, limestone, slate, large porcelain, cement tiles, hexagon tiles, vinyl, cork, carpet in vocabulary colours, sisal |

Each slug: source and asset id (verified, real-world size from the API) or `procedural` (tiles, wallpaper patterns,
slats: node groups in Blender, no external file), the albedo mode (M5 §2.2), roughness, the wet-room rule.

### 4.4 Cabinets

Parametric builders with exact sizes: kitchen base cabinets (the counter run gets fronts, plinth and worktop),
wall cabinets (`wall_cabinet`, along a counter run at 1.45–2.15 m, never over a window or within 0.3 m of one,
never over the stove or a door; `mount_bottom_m` 1.45; added only with `furnished_rooms: complete`, `added_by_ai`, method `rule`), tall / pantry
cabinet, kitchen island, bathroom vanity (a drawn washbasin's look when its depth ≥ 0.45 m: type stays
`washbasin`), sideboard, shoe cabinet, display cabinet, built-in wardrobe (a drawn wardrobe spanning wall to wall:
type stays `wardrobe`, `design.built_in`). Fronts flat / shaker / slatted / glass; colour and handle from the brief;
worktops stone, wood, terrazzo, steel. Library models for sideboard, shoe, display and tall cabinets where the
sources have them.

### 4.5 Furniture types and models

New types (§1.1): bar stool, bench, ottoman, office chair, console table, crib, bunk bed, chaise, plus the corner
sofa and the cabinet types. Target: ≥ 20 models per type and ≥ 3 style families per type (all 24 existing types
already have ≥ 3 families; 6 are below 20 models, M9 §9). Recolour: a library model whose materials split into
fabric and wood parts (material names and a part-class judgement on the library pod: each material slot rendered
highlighted, both vision models answer fabric / wood / metal / glass / other) gets the brief's fabric and wood
colours; a model without separable parts is skipped for that brief and the fit picks another. Material tags
(`glass`, `wood`, `metal`, `fabric`, `rattan`, `marble`) from the same judgement let the fit honour "glass coffee
table".

### 4.6 Decor

New types (§1.1) with ≥ 15 models per type: curtains and blinds (per window, by window size, never over a door),
throws (sofa, bed), books, candles, baskets, trays, clocks (wall), sculptures (top, floor), large floor plants
(`plant_large`, species palm, monstera, fiddle-leaf fig, olive, fern; pot material and colour from the brief),
pendant and ceiling lights (ceiling slots over a dining table, a coffee table, a bed, the room centre). They get M9
slots (`window`, `ceiling` are new slot kinds) and parametric fallbacks.

### 4.7 Doors and windows

Doors: flush, shaker panel, glazed, pocket, sliding, barn, double, entrance; oak, walnut, white lacquer, black,
grey, any vocabulary colour; handles brushed steel, black, brass; the drawn opening type (swing, sliding, double)
always wins. Windows: white PVC, anthracite aluminium, black steel, dark bronze, oak, any vocabulary colour;
mullions and transoms when an elevation draws them; inside and outside sills; curtains from decor.

### 4.8 Exterior

Facade render in vocabulary colours, brick, stone cladding, wood cladding, fibre-cement boards; roofs clay tiles,
concrete tiles, slate, standing-seam metal, green roof; paving, gravel, grass, decking.

### 4.9 Lighting moods

Add `bright noon`, `blue hour`, `cloudy soft`, `interior evening` (lamps on: table, floor, pendant and ceiling
lights emit; HDRI at dusk), each with a verified Poly Haven HDRI.

### 4.10 real02 brief (target)

| Term | Slot and value |
|---|---|
| Modern natural | family `modern` (+ `natural`: light wood, linen, rattan accents) |
| warm greige walls | walls `paint`, colour `greige` + `warm` |
| light oak plank floor | floor oak natural, plank |
| light grey fabric sofa | sofa fabric, colour `light grey` (recolour or model choice) |
| natural light wood furniture | furniture wood: light oak veneer, natural |
| glass coffee table | coffee table, material tag `glass` (library) or the parametric glass top |
| many large indoor plants (palms, monstera, ferns) in rattan and cream pots | decor `plant_large`, species palm, monstera, fern, pots rattan and cream, "many": up to 2 per living room corner slot set |
| cream and mustard cushions | cushions alternating cream and mustard |
| dark bronze window frames | window frames `dark_bronze` (inside and outside) |
| warm daylight | lighting `warm daylight` |

### 4.11 Coverage table (filled from the survey and the library pods)

| Item | Today | Target | M10 (9 Oct 2026, after pod L2c) |
|---|---|---|---|
| Colours | 3 (white, cream, charcoal) | ≥ 40 + 6 modifiers | 53 named colours (W3C CSS Color 4, xkcd) + 7 modifiers |
| Wall finishes | 5 | ≥ 14 + any paint colour | 25 + any paint colour |
| Wet-wall tiles | 1 | 6 kinds × size / colour / grout | 6 kinds (subway, large porcelain, zellige, hexagon, mosaic, cement) with size, colour and grout |
| Floors | 8 | ≥ 25 | 32 |
| Cabinet front styles / worktops / handles | 0 / 1 / 0 | 4 / 4 / 3 | 4 / 4 / 3 |
| Furniture types | 24 (+ 4 documented-only) | 38 | 38: 37 with library models, `wall_cabinet` parametric by design (built along the counter run) |
| Models per furniture type | 10–20 (18 of 24 at 20) | ≥ 20 per type where sources allow; reasons listed | 669 models; 23 of 37 at 20. Below: crib 8, display_cabinet 8, bunk_bed 10, chaise 10, shower 10, sink_kitchen 15, tall_cabinet 17, dresser 18, nightstand 18, chair 19 (one accepted M9 model's GLB was on M9's container disk), fridge 19, sofa_corner 19, stove 19, toilet 19. Reasons: few real models in ABO / Objaverse for the new types; the judges refuse many generated sanitary and kitchen models (M9); the generation ran in one pod (L2c, 40 min, the 13 thinnest new types first) |
| Style families per type | ≥ 3 for all 24 | ≥ 3 for all 38 | ≥ 3 for all 37 library types (GPU test, pod L2c) |
| Decor types | 8 | 20, ≥ 15 models each | 20 types, 363 models; 18 of 20 with ≥ 15. Below: blind 9, plant_large 10 (generated only: no real source) |
| Material slots and tags | — | judged by both models | 1264 models judged (recolourable: fabric 184, wood 207); 101 generated models have none (made after the slot renders, or their GLB changed; §10.4) |
| Door styles / window frames | 1 / 1 | 8 / 6 + colours | 8 / 6 + frame colours |
| Exterior materials | 1 | ≥ 13 | 28 |
| Lighting moods | 5 | 9 | 9 |

`python -m wenart.style projects/real02` (9 Oct 2026): all 10 brief terms matched, no unmatched term; the exterior values the
brief does not name are assumed (facade render warm greige, roof concrete tiles anthracite, paving grey, garden grass).

## 5. Acceptance

| # | Check | Target |
|---|---|---|
| 1 | real02 end state | `ok` (was `needs review`) |
| 2 | real02 sheet analysis | 4 plans (basement, basement "Açık mutfak", ground, attic) + 1 section; the stray HATCH listed (and the two DIMENSIONs outside the frame); levels −1, 0, 1 (attic) and the basement variant group right; units cm with the `unit_mismatch` conflict listed |
| 3 | real02 build | 3 levels stacked with slabs, stairs connect, attic with sloped ceilings and the mansard roof from the section and the attic plan, heights with evidence or `assumed` (§0.1 values) |
| 4 | real02 renders | interiors per variant (only the changed rooms in the alternative) + ≥ 5 exterior views per variant (an alternative with an unchanged outside lists the base views) |
| 5 | synthetic-07 | every region class, level, variant, registration shift (± 1 cm) and height (± 1 cm) equals the ground truth; the stray listed |
| 6 | Feature 1 | in `complete` mode ≥ 1 added piece in each furnished bedroom and living room of real01 / real02 that misses an expected type; every drawn piece keeps its anchor (± 5 cm) and front (± 1°), checked against the source plan; every type or size change listed with the drawn values; 0 placer violations by AI changes or additions |
| 7 | Feature 3 | `python -m wenart.style projects/real02` has no unmatched term (or each listed with a reason); coverage table (§4.11) meets the targets or says why not |
| 8 | No regressions | synthetic-03 and real01 results as in M9 or better; `pytest -m "not gpu"` and `pytest -m gpu` green |

## 6. Order of work and parallel tracks

1. Spec, the user's answers, the `CLAUDE.md` change after the OK. The lead freezes the contracts (§1): schema,
   example building JSONs (one per new block, used as fixtures by every track), `sheets.schema.json`, brief keys,
   new type and slug names, stage list.
2. Tracks (branch `m10-<track>` from `opus_branch_04`, each in its own git worktree; the lead merges each into
   `opus_branch_04`, runs `pytest -m "not gpu"` after every merge, then pushes):

| Track | Content | Agent model | Owns | Must pass | Size |
|---|---|---|---|---|---|
| A1 sheets | §3.1 split, classify, levels, alternatives, registration, units, heights, exterior evidence; region page records in the pipeline; `sheet_region` questions | Opus | `wenart/sheets/**`, `wenart/ingest/{classify,pipeline,dxf_generic,pdf_extract,cad_pdf,raster,dwg}.py`, `wenart/ingest/generic/scale.py`, twin and `same_as` detection (`wenart/ingest/twins.py`), `wenart/recognition/answers.py` (the `sheet_region` request kind; its prompt and schema in `wenart/sheets/question.py`), `tests/test_sheets_*.py`, `tests/test_{classify,pipeline}.py` | CPU suite; real02 sheet readings of §0.1 in the session; synthetic-07 truth after A2 | L (≈ 3,000 lines) |
| A3 face-line walls | §3.1 item 11; openings and rooms on such walls; the new furniture types (corner sofa, …) in the symbol typing | Opus | `wenart/ingest/generic/{walls,openings,topology,symbols}.py`, `wenart/recognition/{symbols,prompts,schemas}.py`, `wenart/recognition/size_table.yaml`, `tests/test_generic_{walls,openings,topology}.py`, `tests/test_symbols.py` | CPU suite; the real02 ground floor reads closed walls, its rooms and doors in the session; real01 and synthetic-06 unchanged | M (≈ 1,200) |
| A2 synthetic-07 | §3.4 | Sonnet | `wenart/synthetic/**` (synthetic-07 parts), `projects/synthetic-07/`, `docs/synthetic.md` (its section), `tests/test_synthetic.py` | generator deterministic, committed files current, truth complete | M (≈ 900) |
| B completion | §2 | Opus | `wenart/furniture/{complete,locked,placer,layout,schemas,prompts}.py`, `tests/test_{complete,locked,placer,layout}*.py` | CPU suite; placer tests per check with changed and added pieces | M (≈ 1,800) |
| C vocabulary | §4.1–4.3, 4.8, 4.9 tables | Sonnet | `wenart/style/{colours,finishes,objects}.py` (new), `wenart/style/profile.py`, `wenart/assets/{polyhaven,ambientcg,fetch}.py`, `tests/test_{style,colours,finishes}*.py` | live id checks recorded; real02 brief matched | M (≈ 1,500) |
| D library configs | §4.5, 4.6 sources | Sonnet | `wenart/assets/{abo.yaml,abo.py,objaverse.yaml,objaverse.py,generate.yaml,generate.py,models.py}`, `wenart/assets/recolour.py` (new), `tests/test_{abo,objaverse,generate}*.py`, `tests/gpu/test_library.py` | ABO survey counts in the session | M (≈ 1,000) |
| E building + exterior | §3.2, 3.3 | Opus | `wenart/blender/{shell,build,cli,render,export,cameras,camsearch,lighting}.py`, `wenart/blender/{roof,site,exterior}.py` (new), `wenart/views.py`, `wenart/run/pack3d.py`, `tests/test_blender_{shell,roof,site,exterior}*.py` | Blender 5.2.2 CPU tests in the session on the example JSONs, then synthetic-07 | L (≈ 3,000) |
| F looks in Blender | §4.4–4.7 in Blender, new decor slots | Sonnet (Opus if the review rejects it) | `wenart/blender/{parametric,materials,furniture,proxies}.py`, `wenart/furniture/{fit,decor,decor_ai,catalog}.py`, `tests/test_blender_furniture.py`, `tests/test_{decor,furniture_fit}*.py` | Blender CPU tests | L (≈ 2,200) |
| H checks + report | §2.8, §3.3 items 4–6 | Sonnet | `wenart/vision_check/**`, `wenart/gate/{detect,api,calibrate}.py`, `wenart/report/**`, `tests/test_vision_check_*.py`, `tests/test_report.py`, `tests/gpu/test_m10.py` | CPU suite | M (≈ 1,200) |
| Lead | contracts, merges, scheduler | Opus | `building.schema.json`, `sheets.schema.json`, `defaults.yaml`, `wenart/brief.py`, `wenart/building.py`, `wenart/style/vocabulary.py` (wiring), `wenart/run/{scheduler,stages,state,copy}.py`, `CLAUDE.md`, `docs/*` | full suite after each merge | – |

   Waves (at most 4 subagents at a time): A1, A3, B, E first (E and B work from the contract fixtures, A1 and A3
   from real02 and unit fixtures); then A2 (synthetic-07), C, D, F and H as slots free up (F after C, H after B;
   A1 adds its synthetic-07 truth tests after A2 is merged). Haiku or
   `Explore` for read-only searches, log reading and coverage counts. Every subagent prompt holds the `CLAUDE.md`
   rules that apply, the frozen contract, its files, what it must not touch, its tests and the report format.
   Subagents never push, never touch pods or secrets.
   Tests that fail on the frozen contracts (new enums) and who fixes them: A3 `test_recognition_cpu.py` (symbol prompt
   vs schema, 2), `test_symbols.py` (size table, incl. track B's size options); F `test_decor_m8.py` (schema decor
   types), `test_decor_ai.py` (`candle` is now valid: use a non-schema word), `test_furniture_fit.py`
   (`catalog.FURNITURE_TYPES`), `test_blender_furniture.py` (parametric types); H `test_vision_check_prompts.py`
   (category hints; the decoy now gives `console_table`); E `tests/gpu/test_render.py` (exterior cameras without a room;
   second twins listed). Fixed by the lead: the detector words (623bf30), `test_layout.py` (B, merged),
   `test_polish_parts.py` furniture words, `tests/gpu/test_furnish.py` (completion pieces). Each track also reports the
   files `tests/test_run_stages.py::test_code_lists_cover_the_import_closure` needs and the lead adds them to the stage
   code lists at the merge. The lead's scheduler wiring of the `sheets` stage waits on a local branch `m10-lead` until
   A1's package is merged.
3. Library pod L1 (needs A1, C, D merged), then L2 (generation).
4. Code review (Workflow: parallel finders per lens, an adversarial verifier per finding, a failing-then-passing
   test per confirmed finding; < 10 agents).
5. Full runs F1, F2; GPU tests green.
6. Commit and push after every merged track; `docs/progress.md`, `docs/gpu-log.md`; §10 "As built" per track.

## 7. Pods and cost

| Pod | When | Steps | Est. minutes | Est. cost |
|---|---|---|---|---|
| L1 | A1, C, D merged | ABO survey for the new types (40 per type), Objaverse survey for gaps, thumbnails, judging by both models (with material tags and the recolour part classes), accept (20 per type, decor 15), catalogue; the `sheet_region` AI passes of real02 and synthetic-07 (stored answers) | 90–110 | $3.1–3.8 |
| L1b, L1c, L1d | L1 cut at 2 h (8 Oct: it surveyed every type, 55 min of ABO downloads) | L1b: `--types new` surveys (caches on the volume), thumbnails (cut); L1c: the rest of the thumbnails, judge requests, material slots (cut); L1d: the sheet and recognition answers, both judge sessions, accept, recolour tags, catalogue, GPU tests | 139 + 115 + ≤ 115 (actual) | $1.32 + $4.76 + ≤ $4.8 |
| L2 | after L1 | TRELLIS.2 generation for the types the real sources cannot fill (`plan --target 20`, decor 15), thumbnails, the rest of the material slots, judging, catalogue | ≤ 115 | ≤ $4.8 |
| L3 | only if L2 is cut | the rest of the generation plan | ≤ 110 | ≤ $3.9 |
| F1 | after the review | full run of real02 (base + `Açık mutfak`), GPU tests | 80–115 | $2.8–4.0 |
| F2 | after F1 | full runs of real01, synthetic-03, synthetic-07, GPU tests | 90–115 | $3.1–4.0 |
| R | only if needed | one re-run of a failed project | ≤ 115 | ≤ $4.0 |

Prices at the RTX PRO 6000 ($2.09/h; the runner takes the fastest GPU in stock under $5/h, worst case per pod
< $5); one pod at a time; at most 3 pods per day (≤ $12/day). Expected $13–18, worst case $23.7 (spent so far
$33.80 of $100). real02 without twin rooms rendered once would need about twice the render time (≈ 90 instead of
≈ 45 interior views) and a second pod (+ ≈ $4).

## 8. Risks

| Risk | What we do |
|---|---|
| real02 still finds no closed walls after A3 (stairs, the party wall, terrace parapets) | A3's target is the real02 ground floor in the session before any pod; a failing plan is named in the report, never filled in |
| The basement / ground outline difference (0.40 m per dwelling) is real | the registration lists it as a conflict; each level is built as drawn |
| One section and no elevation or roof plan (real02) | roof profile from the section, its outline and break line from the attic plan; everything else `assumed` and listed |
| Library models without separable fabric / wood parts | the fit picks another model for the brief; the coverage table lists per type how many can be recoloured |
| ABO has few cribs, bunk beds, chaises, clocks, sculptures | Objaverse (flagged licences) and TRELLIS.2 fill; shortfalls listed with the reason |
| The gate refuses the polish of exterior views | exterior views stay Cycles (as real01's interiors in M8/M9) |
| real02 render time | twin rooms once (question 7), alternatives only render the rooms that differ |
| 3D files of a whole building | `.glb` per variant may pass 300 MB: M9's 24 MiB zip parts |

## 9. Decisions (user, 8 Oct 2026)

| # | Question | Answer |
|---|---|---|
| 1 | Feature 1 default | `furnished_rooms: complete` for every project |
| 2 | Variants | `all`: every alternative is built and rendered (its changed rooms; its exterior views when its outside differs, else the base views are listed for it) |
| 3 | A level that fails | `leave_out`: left out and listed (levels above it too) |
| 4 | Site | `full`: plot, garden, paving and parking as drawn |
| 5 | real02 exterior look | not answered: the defaults apply, listed as assumed (window frames dark bronze from the brief; facade smooth render in the brief's greige; roof covering anthracite concrete tiles; paving grey concrete pavers; garden grass) |
| 6 | Kitchen appliances and a drawn island | fixed, as drawn |
| 7 | real02 twin rooms | rendered once; the AI furniture and decor mirrored onto the other dwelling (`render.twin_rooms: one`) |
| 8 | Unit check may override `$INSUNITS` | yes, when ≥ 2 independent checks agree; the conflict is listed; no agreement → `needs review` |
| 9 | `CLAUDE.md` furniture rules | replaced with the wording of §1.7 |

## 10. As built

### 10.1 Tracks (all merged into `opus_branch_04`, 8 Oct 2026)

| Track | Built | Tests (CPU) | Notes |
|---|---|---|---|
| A1 sheets | `wenart/sheets/` (split, titles, levels, variants, unit check, classify, register, heights, exterior, sheet_region questions, report, debug image, to_building), `wenart/ingest/twins.py`, the pipeline handover (one page record per region, frame shift, unit override, levels left out, variants, slabs, roof, facade, site) | 148 + 18 (synthetic-07) + review tests | M2–M9 `building.json` byte-identical (synthetic-01..06, real01). sheet_region questions only for regions that title and geometry leave undecided (lead decision; before: every region asked) |
| A2 synthetic-07 | `wenart/synthetic/{sheet,sheet_writer,sheet_truth}.py`, `projects/synthetic-07/` (one CAD sheet, cm, R2000 with `\U+` escapes; DWG in `source/`), truth files | 96 synthetic tests | knee wall truth = underside (the schema writes the top surface; the note gives the underside) |
| A3 face-line walls | face pairs (layer by evidence: rays from room labels, ≥ 70 %, runner-up listed), columns, joins, 2-line windows, opening `operation`, 14 types in symbol typing and the size table, L outline → `sofa_corner` | 23 (real02 walls) + pipeline test | real02 basement rooms needed the lead's `clip_page` tolerance (3-decimal region boxes) |
| B completion | `wenart/furniture/{complete,locked}.py`, placer, schemas (`l_parts`), prompts, layout | 61 + 34 + 25 + … | review: a changed piece never fails a check more than its drawn version; any drawn bed is the anchor; type proposals must fit the footprint |
| C vocabulary | `wenart/style/{colours,finishes,objects}.py`, phrase parser in `profile.py`, `style.schema.json`, `asset_checks_m10.json` (62 textures + 9 HDRIs checked live) | ~350 | 53 colours (W3C CSS Color 4, xkcd CC0; RAL left out: no verifiable sRGB); greige = xkcd "greyish" |
| D library | ABO / Objaverse rules for the new types, TRELLIS.2 prompts, judge words, `recolour.py` (material slots and tags), `--types new` surveys | ~600 | wall cabinets parametric only; corner sofa `chaise_side` from the footprint |
| E whole building | `wenart/blender/{roof,site,exterior}.py`, stacked levels, slabs, attic under the roof, facade, site, exterior cameras (4 corners, aerial, 1 per elevation), variants (`--variant`, `views_for`) | ~700 (Blender) | review: mansard from the section profile (real02: eaves 3.65, break 5.35, ridge 6.79, 40.4° / 13.3°) |
| F looks | `wenart/blender/looks.py`, materials for every new slug, 14 type builders, cabinets, doors (8 styles) and windows (6 frames, mullions, sills) in the shell, decor slots, recolour in the fit, `fit --source/--completion` | ~940 | M3–M9 projects build as before (M10 geometry only with M10 values) |
| H checks and report | exterior and elevation checks, drawn-piece check, exterior gate, report sections (Sheets, Building, Feature 1, Exterior, Variants, assumed values) | ~770 | |
| P prep job | recolour steps, sheet questions on the prep pod, survey types, GLB caches on the volume, partial copies after the deadline | 88 | |
| Lead | sheets stage, variant runs, copy rules, plan, contracts, merges, review triage | run tests | |

### 10.2 Lead decisions during the build

| # | Topic | Decision |
|---|---|---|
| 1 | sheet_region AI passes | asked only for regions whose class neither title nor geometry decides (§3.1 item 2 read as a fall-through); an AI-only answer never makes a plan |
| 2 | Variant runs | an alternative runs after the base's refit as its own sub-output; the base's gate calibration is copied and validated; its report runs before the base's; a variant with no view gets build and export only |
| 3 | Pipeline fingerprint | `sheets.json` is not hashed (pipeline_final rewrites it); pipeline_final is reused only while `sheets.json` is the answered one it wrote |
| 4 | real02 roof break | the section wins over the plan's break line (20 cm apart; four attic openings reach 5 cm into the 20 cm roof; listed) |
| 5 | Knee wall | the schema's top-surface value stays; the note gives the underside the section draws |
| 6 | Window frames | a metal frame word with a colour that has its own metal look takes it ("dark bronze aluminium" → `dark_bronze`) |
| 7 | Library pods | new types only (`--types new`, §7), M9 models kept; GLB caches on the volume so a cut pod keeps its downloads |
| 8 | Alternative in a second document | not supported (needs a contract change; no project has it) |
| 9 | Network volume | full on 9 Oct 2026 (pod L2b and a diagnostic pod failed: the M10 GLB caches, the material-slot GLB copies and the new assets, about 35 GB); grown from 120 to 250 GB with your OK (`gpu_run.py volume-resize`, about $17.50/month, +$9.10) |

### 10.3 Code review (workflow: 8 subsystem reviewers, one adversarial verifier per finding)

58 agents; 47 findings confirmed, 3 refuted, 18 low ones listed without verification. Every confirmed finding was
fixed with a test that failed before (a few were already fixed by later merges: #12, #29, #34). Highest: #10
(real02 basement rooms lost), #17 (changed drawn piece growing through walls), #22 (mansard ignored the section),
#38 (plant species slug broke the catalogue), #46 (a variant could keep an older gate decision).

### 10.4 Known limitations

- An alternative drawn in a second document is read as a copy of the base (needs `secondary_regions` on alternatives).
- Extra walls from a secondary page get the default 2.70 m height (`pipeline._merge_secondary`); twin order for a
  horizontal mirror axis is inverted (`twins.py`).
- `completion_report.md` shows the drawn type for a reverted change (the final report shows the refused proposal).
- A private project's report names its sheet debug image paths (staged names, never copied).
- Objaverse LVIS category names are checked against the LVIS v1 list, not the Objaverse file (unverified until a pod).
- A toilet's `height` has two meanings: `furniture.schemas.HEIGHTS` gives an added toilet 0.8 m (the cistern top), while `parametric._toilet` and the proxy tables read it as the bowl (0.4 m), so an AI-added parametric toilet is built 1.2 m tall with a 0.77 m bowl (real01 `f_L0_021`; synthetic-03 in M7). The camera model follows the built mesh; a fix changes real01's renders.
- `recolour slots` rebuilds every model's record and sheet after Blender on each run (reads the masks and renders from the network volume, about 15 min for 1646 models) and does not watch the deadline there; the GLB copies with renamed materials before Blender neither. The prep job therefore runs `recolour_slots` only where the slots are new (L2b leaves it out: the generated models get no material fields: a colour brief skips them and the fit takes another model, `wenart/assets/recolour.py`).

### 10.5 Pods

| Pod | GPU | Minutes | Cost | What it did | Result |
|---|---|---|---|---|---|
| L1 `2yv5dyxk11jis1` | RTX 5090 | 125 | $2.48 | the survey of every type (ABO 55 min, Objaverse 24 min), thumbnails | cut by the watchdog; 3 result files collected, the container-disk downloads lost → `--types new`, GLB caches on the volume |
| L1b `3qvwb0h3gzt94o` | RTX PRO 4000 | 139 | $1.32 | `--types new` surveys: ABO 1217 candidates (7 min), Objaverse 825 (30 min); thumbnails cut after 54 min | the job ran into the watchdog (library copy), nothing collected; the work is on the volume |
| L1c `5j6x21hcj34t42` | RTX PRO 6000 | 115 | $4.76 | the rest of the thumbnails (50 min), 1646 judging sheets, material slots cut after 18 min | the same: the byte-for-byte library copy after every late step outran the watchdog → size and mtime compare, 16 copies at once; the runner collects 16 files at once; `--max-minutes 95 --grace 1200` |
| L1d `5wbmxoz3cdezq6` | RTX PRO 6000 | 68 | $2.81 | sheets and pipelines of the four prep projects (real02: 92 questions, synthetic-07 and real02: no sheet_region question), both sessions (recognition, library judging), final pipelines, catalogue 618 + 316 decor models, copy, GPU tests | GPU tests: 2 library failures (a kept ABO record has no GLB on the pod: the test fixed; crib in 2 style families: L2's generation); real02 failed the schema (drawn wall cabinets without `mount_bottom_m`: fixed, real02 `ok` locally with the answers) |
| L2a `md5uwkua9n8mey` | RTX PRO 6000 | 112 | $4.65 | the rest of the material slots (1264 of 1646 ready models with slots, 1275 sheets, 57 min), Qwen judged them (7 min) | GLM could not start before the deadline: the slots step overran its reserve by 15 min (it rebuilds every model's record and sheet after Blender, unbounded by the deadline), then the late steps ran into the watchdog; nothing collected. The generation's input images (310 MB) no longer go to `$RESULTS` |
| L2b `k5vdwxva8alqyr` | RTX PRO 6000 | 58 | $2.43 | generation (target 20, every type: 438 pairs) | the network volume filled during the generation (120 GB): the job could not write, ended, and the pod stopped itself after its grace; nothing collected |
| diagnostic `dg3ea8edhye1l2` | RTX PRO 4000 | 7 | $0.06 | `volume_report.sh` | could not start: volume full |
| — | — | — | — | volume grown to 250 GB (your OK, decision #9) | |
| diagnostic `2aw8p6a9m8kvsw` | RTX PRO 4000 | 5 | $0.04 | `volume_report.sh`: prep 34 GB (19 GB material-slot GLB copies), pip cache 17 GB, assets 14 GB, jobs 8 GB; L2b's logs | ok |
| L2c `6d8e6zae3wsqxt` | RTX PRO 6000 | 81 | $3.37 | generation for the 13 thinnest new types (`WENART_GENERATE_TYPES`, 40 min: 387 generated candidates in all), thumbnails, 1769 judging sheets, both sessions (GLM: the material sheets), catalogue 669 + 363 decor models, copy (47 s), GPU tests | GPU tests: 3 wrong expectations fixed (a `mixed` slot material, `wall_cabinet` parametric only, an accepted record write-catalog refused); the runner's retries re-fetched everything (fixed: a retry fetches only the missing files) |
| F1 `puc0tntgfvz5he` | RTX PRO 6000 | 59 | $2.44 | full run of real02 (base 48 views, variant `l-1b-acik-mutfak` 17 views, 5 exterior views each, gate ok, polish on for the rooms, 3D files 854 MB) | real02 end state **ok**; 5 GPU tests failed (§10.6): diagnosed by a workflow (one agent per failure, an adversarial verifier each), fixed in 4 worktrees |
| F1b `twdf5bhj1h28ou` | RTX PRO 6000 WK | 54 | $2.33 | real02 again after the F1 fixes (base 47 views, variant 17) | end state ok, **every GPU test green** (full 34 + 5 skipped, polish 13); gate ok for the rooms (97.7 % of 176 comparisons), exterior polish off (84.6 % < 90 %) |
| F2 `3ywy7xcrpf1fn3` | RTX PRO 6000 WK | 85 | $3.66 | full runs of real01 (20 views), synthetic-03 (44), synthetic-07 (30 + variant 3) | every project ok; 3 GPU tests failed (§10.6): all code bugs, fixed |

### 10.6 The GPU test failures of pod F1 (real02)

| Test | Cause | Fix |
|---|---|---|
| `test_every_room_has_three_views` | test bug: it passed the scene manifest's variant record (an object since M10) where `views_for` takes the variant id | the id from the record; the rooms cross-checked against the record's `views` |
| `test_passes_exist_and_depth_is_plausible` | code bug: real02's stair core `r_L0_oda` is filled by a U stair; the camera search's fallback point sat in the 0.20 m stair well, 8 cm from a step, and no rule rejected a surface that close (the share rules missed it). Also a test gap: exterior views and the open roof terrace have sky by design | `camsearch`: a view whose nearest model surface is under 0.12 m is blocked (`SCORE["blocked_min_depth"]`, docs/milestone6.md §4.1); only real02's stair-core views change. The test checks every view, exterior views up to the exterior clip end without the coverage bound, open-sky rooms without the coverage bound |
| `test_index_pass_contains_every_visible_proxy` | test expectation: a library wardrobe's fitted box grazes the frame edge by 1 cm while its mesh (domed cornice) stays outside | a library piece may be absent when shrinking its box by 2 cm per side hides it and its built box matches its footprint (± 1 cm) |
| `test_ai_decor_is_built` | test bug: it checked the base scene only; L-1b decor is built in the variant's scene | every variant scene, decor on its own levels; every AI item in some scene. Also a code bug found on the way: decor copies along a chain of partner rooms (same_as of a twin) missed the root's decor (`decor.copy_partner_decor` copies in dependency order) |
| `test_gate_validation_recorded` | test bug and a count bug: M10's exterior comparisons share the calibration file; the rates count the interior ones, the test recomputed over all, and `n_benign`/`n_negative` counted all | `decide_validation(kind=...)` counts the comparisons of one view kind; the test recomputes the interior ones |

### 10.7 The GPU test failures of pod F2 (synthetic-03, synthetic-07)

| Test | Cause | Fix |
|---|---|---|
| `test_index_pass_contains_every_visible_proxy[synthetic-03]` | code bug in the camera model: an AI-added library toilet was modelled with a 0.8 m bowl (its JSON height is the cistern top; the builder's toilet height is the bowl) | `camsearch.piece_profile`: a library toilet takes the type's 0.4 m bowl; no camera moves (a rebuild swaps the names of synthetic-03's `cam_r_L1_banyo_1` and `_2`) |
| `test_passes_exist_and_depth_is_plausible[synthetic-07]` | code bug: the attic's east gable wall (a parapet piece and a gable piece) was lost by the exact boolean that cuts its window (touching pieces need `use_self`); the hall looked out through the missing wall | `shell.build_walls`: `use_self` for walls built from pieces; a guard after the cuts stops the build when a wall loses faces or volume outside its cutters (`shell.wall_cut_problems`); only this wall of all projects changes |
| `test_every_empty_room_was_laid_out[synthetic-07]` | code bug in ingest: the attic plan's 11 m roof ridge line touched a door leaf and became an unknown "furniture" piece, so the empty play room looked furnished | `symbols.furniture`: a long straight stroke that crosses the building outline is no furniture stroke (noted); only synthetic-07 changes, and it now matches its truth |

Open (§10.4): an AI-added parametric toilet is built 1.2 m tall (the builder reads its 0.8 m JSON height as the bowl);
fixing the meaning of a toilet's height changes real01's renders and is left for a later milestone.

### 10.8 Top-floor stairs (seen in the exterior views of F1b and F2)

A stair drawn on the top level was built as a new flight rising to a level that does not exist: real02's attic
stairs reached 7.05 m with their shafts against a ridge at 6.79 m (white boxes above the roof), synthetic-07's
attic stair rose out of its gable roof. The documents draw the same stair block at the same place on every plan
(real02 "merdiven", synthetic-07 MERDIVEN, "stairs aligned"), so the attic stair is the drawn upper end of the stair
below. Fix (whole M10 buildings only; M3–M9 buildings keep the M7 path):

- `shell.stair_arrival`: a top-level stair over a stair of the level below (at least half of the smaller footprint)
  is that stair's upper end: not built, listed in `furniture.not_built` with `arrives_from` and `slab_opening`, an
  assumed `stair_arrival` entry; the attic ceilings are no longer cut for it.
- A top-level stair over no stair stops 5 mm under the roof underside (assumed, a warning "the roof access is not
  drawn (needs review)"); with less than 0.30 m of room it is not built (a warning).
- The camera model (`camsearch.RoomModel`) and the vision check's JSON cross-check (`expected.json_crosscheck`)
  leave out a stair the builder does not build.
