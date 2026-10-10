# Milestone 12 – track S (scene): decor resting on its host, realistic furniture, scene checks

Design: `docs/milestone12.md` §4.6 (S1–S6), §4.7 (D13), §4.8 (D14), §6.4 (procedural textiles, parametric fixtures),
contracts §13. Session: cloud, CPU only (no Blender here: the Blender code is thin, every rule is a pure function
with CPU tests). 10 Oct 2026.

## As built

### 1. Host frame and `sync_to_hosts` (D13, B3) – `wenart/furniture/decor.py`

| What | Where |
|---|---|
| Every decor item gets `host_frame` = `support` (seat, mattress, back, headboard, top, shelf, floor, wall, ceiling), `u` / `v` (its centre as shares of the host footprint, -0.5 … +0.5, +v = back), `turn_deg`, `lean_deg` (12° for cushions on a back or headboard), `shelf` (books: board 1); anchored items (rug, picture, pendant) also `anchor_id`, wall items `wall_offset` | `decor.host_frame_of`, `decor.attach_host_frames` (called by `add_decor` and `decor_ai.apply`) |
| `sync_to_hosts(building)`: hosted items take the host's new centre / rotation / room / level (move, turn, resize, swap); a throw across a bed's foot takes 0.95 × the new width; top/seat/mattress items never wider than the host; a rug and a pendant follow their first anchor; wall art slides along its wall with its piece. Dropped into `decor_dropped` with the reason: host gone, not built (`piece_is_built`: `build: false`, `unknown`, library gap), retyped without the support; all anchors gone; a picture whose piece left its wall. Idempotent, deterministic | `decor.sync_to_hosts`, `_follow_wall` |
| Support rules and the S5 tolerances (pure numpy, also used inside Blender, where shapely is missing) | `wenart/blender/rest.py`: `support_of`, `support_fits`, `item_support`, `REST_TOLERANCES` (rules re-exported by `decor.py`, tolerances by `scene_checks.TOLERANCES`) |
| No decor cushions on a seat or bed whose model has its own (`has_cushions`, `has_pillows`, `has_bedding`) | `decor.takes_cushions`, `decor_ai._cushions`, `decor.rule_decor_room` |
| Real cushion sizes: `CUSHION_SIZE` 0.45 × 0.15 × 0.45 m (standing), `PILLOW_SIZE` 0.50 × 0.15 × 0.50 m (leaning at a bed head) | `decor.py` constants |

### 2. Resting on the built mesh (D13) – `wenart/blender/rest.py` (new, pure numpy) + `wenart/blender/furniture.py`

| What | Where |
|---|---|
| Ray casters: `MeshCaster` (numpy Möller–Trumbore, CPU tests), `BVHCaster` (`mathutils.bvhtree.BVHTree` of the evaluated, world-space mesh, Blender), `MultiCaster` (bed + its bedding) | `rest.py` |
| Tops, seats, mattresses: 3 × 3 grid of downward rays under the footprint, highest hit (hard) / median (soft), ≥ 80 % hits, else the next spot towards the host centre | `rest.place_on_top`, `support_height` |
| Cushions on a back / pillows on a headboard: seat probed at the item's own x from the front (an L sofa's empty inner corner skipped), horizontal rays from the front at 5 heights of the item find the real back; the leaning back face touches the nearest; side rays at two heights keep it 5 mm off the arms (shift, else narrow ≥ 0.30 m, else none); kept on the host's width; faces the seat's front | `rest.place_leaning`, `back_face_offset` |
| Books: one downward ray finds every board top (upward face) and its clearance; the frame's board (or the next with room), then a grid on that board | `rest.board_tops`, `place_on_shelf` |
| Plan per item: place → build in place → measure S5 → place once more (moved) → else not built with the measured numbers | `rest.plan_decor`, `plan_throw` |
| Blender: hosted decor goes through the plan on the host's evaluated mesh (cached caster per host, with its dressing); library decor models are fitted in their own frame first; the object records `wenart_rest_footprint`; not rested → `summary["decor_not_rested"]` | `furniture._create_hosted_decor`, `_host_caster`, `local_decor_mesh` |
| No type-table rest height: `parametric.decor_rest_height` removed; `furniture.decor_height_above_floor` = the item's own `center[2]` or the floor (a proxy box's top only behind `--proxies`) | `parametric.py`, `furniture.py` |
| Rigid-body settle | not built (an option of the design; off by default; only if the rays look stiff on the pod) |

### 3. Procedural textiles (§6.4, B7) – `wenart/blender/textiles.py` (new; the host-free mesh makers in `parametric.py`)

| What | Where |
|---|---|
| Filled cushion / pillow (two bulging faces, thin seam, drawn-in edges, closed mesh), standing or lying | `parametric.cushion_mesh`, `lying_cushion_mesh` (re-exported by `textiles`); `parametric.decor_parts("cushion")` |
| Cloth draped like a shrinkwrap: grid rays down onto the host, underside 5 mm above the hit + modelled folds; points past the top hang down by the length they reach past the edge, pushed out of the side by horizontal rays | `textiles.drape`, `throw_parts`; `parametric.cloth_solid`, `flat_cloth` |
| Every library bed without bedding (a mattress model: not a M8 frame, audit says no bedding) gets a duvet over the foot 75 % (0.30 m overhang, ends before the pillows), a turned-down band and 2 pillows (1 on beds < 1.30 m) lying 14° against the headboard on the mattress; object `dress_<id>` with the bed's id and pass index, recorded as assumed | `textiles.duvet_and_pillows`; `furniture.needs_dressing`, `_dress_bed` |
| Curtains: an open pair of pleated panels (sine pleats, 0.12 m pitch) under a rod; blinds: roller (default) or slats (`blind_kind: slats`) | `parametric.curtain_parts`, `blind_parts` (via `parametric.decor_parts`) |
| Throws, curtains and blinds never take a library model (B7: no "JuiceMachine" squashed to 5 cm) | `fit.PROCEDURAL_DECOR_TYPES` |

### 4. Parametric fixtures (§6.4) – `wenart/blender/parametric.py`

Fridge-freezer (carcass, dark ventilation plinth, freezer + fridge doors with 3 mm gaps, bar handles inside the footprint),
front-loading washing machine (top plate, kick plate, control panel with drawer, display and dial, porthole: glass over
the dark drum in a chrome ring), shower (tray with drain, glass front of fixed panel + door, glass sides in chrome
profiles, stabiliser rail, riser, arm, round rain head, mixer). Boxes = footprint (handles no longer 8 mm proud).

### 5. Scene checks S1–S6 – `wenart/blender/scene_checks.py`

`measure(meshes, building, caster_factory)` is the one code path; `measure_pure` uses the numpy caster, `run_scene_checks`
reads the evaluated objects (`object_mesh`, world space, modifiers applied) and uses the BVH caster, writes
`checks/scene_<level>.json`. S1 lowest vertex − (level elevation + room `floor_offset_m`) in −0.005 … +0.010 (wall-hung
pieces skipped); S2 sample points inside the walls' boxes (`wall_boxes`, `depth_in_wall`) and between pieces (ray parity in
three directions, depth = shortest axis ray), kitchen-run members excepted; S3 `wenart_front_deg` of the object vs
`front_deg`; S4 built box in the piece frame vs `sizes.real_range` ± 15 % (by-design types skipped); S5 decor on its host
(+ `<id>#dressing`) or the floor (`rest.measure_rest`: gap incl. the touching point, penetration hard 1 cm / soft 3 cm,
≥ 80 % support); S6 `catalog.usable` asset or `catalog.by_design_parametric`, never `unknown`. Severities: S5 critical,
S4 minor, the others major; `counts.failed_build` when a built item fails S5. Hook in `build.py` (track S block): the
report's counts go to the manifest's `furniture.scene_checks`, `decor_not_rested` and `dressed_beds` are aggregated,
a failed S5 sets `scene_checks_failed` and a warning (the render goes on: decision below).

### 6. Fit (D14, B1) – `wenart/furniture/fit.py`, `catalog.py`

| Rule | Where |
|---|---|
| Only `catalog.usable` models (audit not removed, no NC/SA/ND by licence text or `licence_flag`); an audit `fix` is used as track B's writer left it (the fixes are in the catalogue fields; `audit.fixes` holds the new values, `before` the old); refused ones listed under `excluded` | `fit.split_usable`, `catalog.usable`, `unusable_reason`, `audit_status` |
| B1: `quality_of` takes the mean of the judges' list | `fit.quality_of` |
| Caps: non-uniform ≤ 10 % (was 15), mean scale 0.85–1.20 (was 0.75–1.30) | `fit.NON_UNIFORM_CAP`, `UNIFORM_RANGE` |
| One size table (D23): the fitted height must be inside the type's real height range of `wenart.furniture.sizes.real_range` ± 15 % (a 0.89 m bathtub, a 0.54 m stove: the next model); every tried candidate records `height_m`, `height_ok` | `fit.real_height_range`, `height_fits` |
| Track B's flags when present: `real_product: true` ranks first within its size step; `has_bedding` / `has_pillows` / `has_cushions` decide the bed dressing and the decor cushions; decor models need a `contact` that suits their type (`flat_bottom` on tops and floors, `hangs` on walls and ceilings, cushions `leans` / `flat_bottom`); `audit`, `real_product`, `has_*`, `contact` travel with the asset | `fit.rank_key`, `fit.AUDIT_ASSET_FIELDS`, `catalog.DECOR_CONTACTS`, `contact_fits`, `decor.takes_cushions`, `furniture.needs_dressing` |
| Style chain (neutral at every step): mediterranean → rustic → classic; rustic → classic → mediterranean; classic → rustic; industrial → modern; japandi → scandinavian → minimal; scandinavian → minimal → modern; modern minimal → minimal → modern; minimal → modern minimal → modern; modern → modern minimal → minimal; logged `style_fallback`; a design colour no model can show is dropped before a gap (`design_not_shown`) | `fit.STYLE_FALLBACK`, `style_chain` |
| Parametric only by design: counters, islands, wall cabinets, stairs, and the kitchen/bath fixtures (shower, washing machine, fridge, toilet, washbasin, bathtub, kitchen sink, stove) when no audited model fits (with a `library_gap` record) | `catalog.BY_DESIGN_PARAMETRIC_TYPES`, `PARAMETRIC_FIXTURE_TYPES`, `by_design_parametric` (also a vanity / built-in wardrobe design) |
| Nearest related type only when the group needs the piece (a group member or a drawn piece): `fit.RELATED_TYPES` (armchair → chair, TV unit → sideboard/dresser, …; never sofas, beds, tables, fixtures) | `fit._no_model`, `group_needs` |
| Else a library gap: `asset.method = "none"`, `furniture[].library_gap = {type, style, used, reason}`; the builder does not build it | `fit.gap_fit`, `fit_building`, `furniture.refused_piece` |
| Cushion models keep their proportions (uniform scale, ≤ 10 % between width and height, thickness 6–28 cm); lying cushions are procedural | `fit._decor_fit` |
| Decor models are usable ones only | `fit.decor_entries` |

### 7. No grey box – `wenart/blender/furniture.py`

`unknown` pieces and library gaps are refused (`refused_piece`, listed in `not_built`); `--proxies` keeps the Milestone 3
boxes for debugging. Pieces, floor decor and wall art stand on their room's floor (`piece_floor_z`, with the room's
`floor_offset_m`); pendant and ceiling lights keep the level's floor (the ceiling does not rise with a raised floor).

## Decisions within the design

1. **Fixed equipment never left out.** §4.8 lists counters, wall cabinets and stairs as the only parametric types; but
   CLAUDE.md says drawn fixed equipment is built like a wall and §6.4 says kitchen and bath fixtures come from code. With
   only the three, real02/real03 would lose 4–10 toilets, washbasins, bathtubs and stoves each (not built). So all
   kitchen/bath fixtures fall back to our parametric fixture, with a `library_gap` finding (lead: please confirm).
2. **u / v as shares of the host footprint** (not metres): decor scales with a resized host and stays on it.
3. **Related types** need `group` (track G) or a drawn piece; added pieces without a group become gaps.
4. **A failed S5 on a built item** is a critical violation and `scene_checks_failed` in the manifest; the build does not
   abort (it cannot happen by construction; a crash would lose a whole pod run). The critic (track A) treats it as
   critical.
5. **Leaning items face the seat's front** (turn 0): Milestone 11 data has cushions turned by agent edits (B3).
6. **Single beds get one pillow** (two do not fit side by side under 1.30 m).
7. **The dressing is its own object** (`dress_<id>`, same `wenart_id` / pass index as the bed) and its own scene-check mesh
   (`<id>#dressing`): S5 rests decor on it, S2 does not count a duvet touching a nightstand as a cut.

## Tests added or changed

New: `tests/test_decor_host_frame.py` (16: frame fields, follow move/turn/resize/swap, drops, anchors, wall art,
idempotency, committed real02/real03), `tests/test_decor_rest.py` (16: real seat and reclined back, arms, mattress
heights, bare-bed bedding, throws on bed and sofa, shelves, tops, S5 tolerances, re-placement, closed textile meshes,
committed parametric hosts), `tests/test_scene_checks.py` (14: S1–S6 pass/fail, floor offset, kitchen-run exception,
dressing, report), `tests/test_scene_fit.py` (18: B1, usable filter, audit fix as track B's writer leaves it, real products first, height
check against `sizes.real_range`, decor `contact`, style chain, never a parametric sofa/bed/table, related types,
by-design, gap on the piece, B7, usable decor, committed real02/real03).

Changed (they pinned the old behaviour): `test_furniture_fit.py`, `test_furniture_fit_v2.py`, `test_recolour_apply.py`
(caps, gaps instead of parametric, NC model refused, cushion proportions), `test_blender_furniture.py` (no type height;
Blender tests: unknown not built, decor on rays), `test_blender_bedframe_decor.py` (cushions on the mattress, not the
pillow top), `test_look_m6.py` (no type height; new fixture boxes), `test_decor_ai.py` (no `decor_rest_height`).

## Before → after on the committed data (pure measurements)

Cushions on the committed **parametric** seats and beds (rays on the parametric host mesh; library hosts need the GLBs:
measured on the pod by S5):

| | real02 (14 cushions, 2 corner sofas) | real03 (7 cushions, 2 sofas, 2 beds) |
|---|---|---|
| S5 pass, Milestone 11 placement | 0 | 1 |
| S5 pass, rays | 14 | 7 |
| penetration max / mean before | 0.087 / 0.048 m | 0.100 / 0.029 m |
| penetration max after | 0.000 m | 0.003 m |
| bed cushions' bottom above the mattress | – | before 0.17–0.21 m (on the pillow top), after 0.045–0.05 m (on the duvet band, in front of the pillows) |

| | real01 | real02 | real03 |
|---|---|---|---|
| throws with a library model (B7) before → after | 3 → 0 | 2 → 0 | 12 ("JuiceMachine" 2, "Bench with Cloth" 3, "Saoura Traditional bench", "Scarf", generated 5) → 0 |
| library beds without bedding: bare before → dressed after | 2 | 6 | 8 |
| built `unknown` grey boxes before → after | – | 32 → 0 | 42 → 0 |
| hosted decor on its host after every host is moved 0.6 m and turned 90° (B3): no sync → sync | 7 → 14 of 14 | 15 → 37 of 40 (3 on unbuilt hosts dropped) | 15 → 51 of 51 |

Fit per style family (pieces that can take a model: real02 193, real03 113; library / parametric / gap; "fb" = taken
through the style chain):

| | modern | scandinavian | japandi | industrial | classic | rustic | mediterranean |
|---|---|---|---|---|---|---|---|
| real02 before (lib / param) | 148 / 45 | 144 / 49 | 114 / 79 | 67 / 126 | 74 / 119 | 54 / 139 | 62 / 131 |
| real02 after (lib (fb) / param / gap) | 143 (12) / 28 / 22 | 139 (22) / 28 / 26 | 135 (35) / 32 / 26 | 135 (98) / 28 / 30 | 56 (8) / 38 / 99 | 56 (26) / 38 / 99 | 56 (42) / 38 / 99 |
| real03 before | 89 / 24 | 53 / 60 | 52 / 61 | 35 / 78 | 40 / 73 | 45 / 68 | 10 / 103 |
| real03 after | 78 (1) / 12 / 23 | 78 (37) / 12 / 23 | 68 (25) / 22 / 23 | 78 (68) / 12 / 23 | 39 (9) / 39 / 35 | 39 (18) / 39 / 35 | 39 (33) / 39 / 35 |

With track B's merged size table (heights) and catalogue (18 NC/SA entries `removed`) the height check refuses
124–293 tried candidates per run and family but nearly always another model fits: real02 unchanged, real03 modern /
scandinavian / industrial 78 → 75 library (3 fixtures that are too high or too low go parametric), japandi 68 → 65.

After, "parametric" = by-design types only (fixtures). Gaps, real02 modern: wardrobe 4, dining table 4, tall cabinet 3,
sofa 2, coffee table 2, double bed 2; real02 classic/rustic/mediterranean: chair 40, bench 8, bar stool 7, double bed 6;
real03: console table 6–8, TV unit 7 (classic), bookshelf 3, sofa 2–3, shoe cabinet 3. The classic/rustic/
mediterranean gaps (chairs) need the ABO style pass (§6.4 growth) or a broader last step of the chain.

## What is left

- GPU/pod: the Blender path (`_create_hosted_decor`, `_dress_bed`, `run_scene_checks` with the BVH caster) has never run
  here (no Blender); the `needs_blender` tests were updated and must run on the pod; S5/S2 on library GLBs (thin or
  open meshes: ray parity) to be measured on P5–P7.
- Rigid-body settle (option, off) not built.
- Library hosts' cushion heights before/after need the GLBs (pod).
- `has_cushions` / `has_pillows` / `has_bedding` come from track B's audit; until then every mattress model is dressed and
  every seat takes cushions.

## Changes needed in other tracks' files

1. **Lead / track L – `wenart/blender/build.py` `FINGERPRINT_CODE`**: add `"wenart/furniture/__init__.py",
   "wenart/furniture/catalog.py", "wenart/furniture/sizes.py", "wenart/recognition/size_table.yaml"`: the scene checks
   (S4 size table, S6 usable/by-design) and the bed dressing read them inside Blender;
   `tests/test_blender_look.py::test_fingerprint_code_covers_the_build_import_closure` fails until then.
   **Lead / track A – `wenart/run/stages.py` `FIT_CODE`** (fit and refit): add `"wenart/furniture/sizes.py",
   "wenart/recognition/size_table.yaml"` (the fit's height check, D23);
   `tests/test_run_stages.py::test_code_lists_cover_the_import_closure` fails until then (every other stage closure
   is unchanged: the textile meshes live in `parametric.py`, the support rules and S5 tolerances in `rest.py`).
2. **Lead – `wenart/schema/building.schema.json`**: `decor[].host_frame` also carries `turn_deg`, `anchor_id`,
   `wall_offset`; add a top-level `decor_dropped` array (`{id, type, host_id, anchor_ids, room_id, reason}`); `furniture[]
   .asset.method` may be `"none"` (a library gap, not built).
3. **Track A**: call `decor.sync_to_hosts` after every accepted edit and in `agent apply` (contract); read
   `checks/scene_<level>.json` (S5 critical) and the manifest's `furniture.decor_not_rested`, `scene_checks_failed`;
   treat `library_gap` as a finding.
4. **Tracks A, G, L (views, top-down, critic, cameras, solver)**: a piece with `asset.method == "none"` or type `unknown`
   is not built – treat it like `build: false` (`decor.piece_is_built`); `parametric.piece_bbox` still gives its box.
5. **Track B**: the audit's `has_bedding`, `has_pillows`, `has_cushions` (beds and seats) and `audit.fixes`; real heights in
   `sizes.real_range` make S4 check the height too.
6. **Track G**: `furniture[].group` lets the fit use a related type for a needed partner (`fit.group_needs`).
