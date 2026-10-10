# Milestone 12 – track R (furniture reading): as built

Design: `docs/milestone12.md` §4.1 (D7), contracts §13 (`read_furniture(build, works) -> None`, unchanged).
Cloud session, CPU only, 10 Oct 2026. Branch: `worktree-agent-afb1a61e1c58afb82` (merged with `opus_branch_06` at
`9635c95`). No pods, nothing downloaded.

## 1. What was built

| Part (§4.1 row) | file:function | What it does |
|---|---|---|
| Layer words | `wenart/ingest/generic/symbols.py`: `FURNITURE_LAYER_WORDS`, `LAYER_WORDS`, `layer_kind`, `stroke_kind`, `split_symbol_strokes` | a layer name (folded Turkish, upper case; keys of up to 3 letters only as a whole word, longer ones anywhere in a word: `Pkapı` is a door layer) says what its strokes are: furniture (wins: `TEFRIS`, `MOBILYA`, `VITRIFIYE`, ...), a symbol kind (`KOT`, `ALAN`, `TEXT`, `AKS`, `KESIT`, `KUZEY`, ...), `door`, `structure` (column), `decor`, or nothing; a stroke in a furniture-named block is furniture whatever its layer; only the layer's own name counts (`xref$0$...`) |
| Symbol shapes (non-furniture symbols) | `symbols.py`: `room_number_sign`, `north_arrow_sign`, `door_swing`, `opening_jambs`, `whole_symbol` | a 0.20–0.70 m circle with a short number inside = room-number tag; a circle with an arrow and N/K = north arrow; a 45–135° arc of 0.40–1.40 m with its leaf (a strip ≤ 8 cm from the hinge, ≥ 70 % of the radius) or hinged at an opening's jamb = door swing (a quadrant shower, a chair back, a furniture-named block are not); a piece ≥ 90 % on symbol layers (none on a furniture layer) = that symbol, a column (kept not built as an obstacle) or decor |
| Block names (TR/EN dictionary) | `symbols.py`: `BLOCK_KEYWORDS_M12`, `keyword_type(name, extended)`, `block_type(..., extended)`, `_block_item(..., extended)`, `_appliance_type(s, extended)`, `trim_stray_lines` | M12 words tried first (folded: `KOMODİN`, `ÇAMAŞIR`, `BULAŞIK`, `EVYE`, `FIRIN`, `BERJER`, `ÇEKYAT`, `GARDIROP`, `ORTA SEHPA`, `DISHWASHER`, `REFRIGERATOR`, `VANITY`, ...) on the block name and its nested names; the M7–M11 words stay as they were. A named block whose footprint does not fit its type leaves out up to 2 straight lines sticking out of it (real03's toilet axis line: 1.145 × 0.356 m → 0.36 × 0.53 m) |
| Clusters split | `symbols.py`: `_object_key`, `containers_of`, `object_groups`, `_counter_runs`, `counter_rule(loose_in_blocks)`, `counter_legs(short_corner)`, `reread`; `furniture(..., extra_out, symbols_out)`, `_m12_pass`, `extra_candidate` | an untyped cluster (oversized, a composite fitting no type, an AI candidate still unknown after its answers) is re-read: symbol strokes out (their groups become symbols; a column's stays a not-built piece), counter runs drawn as loose outlines or front lines along the walls, then one part per block instance (a block holding no other block is one object; a flat block's own strokes are clustered at 20 mm; containers are taken page-wide), each part typed on its own: room-number / north arrow / door swing → symbol; a door swing on a box → `details["door"]`; stair rule; a bowl with a drain in a counter leg or beside a kitchen block → kitchen sink; a part ≥ 60 % inside a counter leg → detail; block name; table + chairs split; else `unknown` with its reasons |
| Copies of one block drawing | `symbols.py`: `copy_keys`; `reading.py`: `copies` | the same entity of the same block definition in two inserts (real03's four 1+1 B flats) is the same piece: an untyped copy takes the type its typed copies agree on (same size ± 2 cm), a copy of a symbol is a symbol |
| Vision typing (leftovers) | `core.py`: `_ask_and_apply(..., base)`, `_room_fields`, `_reread_unknowns`, `extract` wiring; `symbols.py`: `extra_key` | never-asked unknown parts that fit a type become extra recognition questions (same question and answer files; the candidates are the size-fitting types plus `unknown` and `not_furniture`) keyed by a hash of their stroke ids (`sym_<level>_x<8 hex>`), so the sequential keys and input hashes of earlier rounds do not move and their answers still apply; their neighbour facts are computed among the base candidates |
| M12 words after the answers | `core.py`: `_m12_named` | a candidate asked before the M12 words existed keeps its question; after the answers its block name (M12 words alone) types it when the footprint fits, against the AI passes (`details["ai_overridden"]` → a `type_disagreement` conflict, `reading.log_overrides`) |
| Symbols into the building | `reading.py`: `move_symbols`, `_is_mark`, `_next_symbol_id` | pieces the core marked (`details["symbol"]`) leave `furniture` for `building["symbols"]` (`id sy_<level>_NNN`, kind, `former_piece_id`, reason, evidence + the rule's, the plan crop of its question); both AI passes typing it → `type_disagreement` conflict; columns and decor stay as not-built pieces (`inferred_as`); the re-read's symbols are added; a level mark still among the pieces (track L moves them first) is moved as `level_mark` |
| Context typing | `reading.py`: `context_types`, `_facing`, `_beside_head`, `_l_body`, `_seat_sized`, `_side_of`, `duplicates` | before the size inference and again after it (partners of the anchors it typed): an L outline with seat-deep arms in a living room = corner sofa; a box with a door swing beside the kitchen run, or one closing the counter run and standing proud of it at a wall = fridge; a 0.5–0.75 m strip along a wall holding a sink or hob = counter; small squares at a bed's head = nightstands; a table-sized piece with ≥ 3 seats drawn around it on ≥ 2 sides = dining table; small pieces ≤ 0.4 m from a dining table = chairs facing it (a back drawn alone reaches 0.45 m deep); a bowl with a drain in a bathroom = washbasin, the counter under it its vanity (not built); two equal seats on opposite sides of a coffee table = armchairs facing it; a table in front of a sofa or in an L sofa's open corner = coffee table; a long low strip at a wall facing a sofa = TV unit; a fixed piece ≥ 60 % inside another of its type = drawn twice (not built) |
| Inference | `reading.py`: `infer` (→ `wenart.furniture.infer`) | size, room and position for what is still unknown; a piece whose question waits for its answers is left to them |
| Misread fixed equipment (U1) | `reading.py`: `misread_share`, `oriented_share`, `fix_fixed`, `_product` (→ `sizes.product_size`), `_resized`, `swing_polys`, `problems`, `_nearest_valid` | > 30 % outside its type's real range → the nearest product size, the back (or the side on a wall) kept in place; through a wall (> 5 cm past the room outline) or in a door swing (> 5 % of its area; the two quarter discs of the leaf within the opening's width) → the nearest valid spot ≤ 0.5 m (5 cm steps); `drawn_type/drawn_footprint/drawn_front_deg/drawn_height` kept, `adjusted_by_ai` {reason, changed, rule, crop}, evidence; a frontless fixed piece gets its front first |
| Fronts | `reading.py`: `infer_fronts`, `_front_of`, `_free_ray` | a drawn piece of a fronted type without a front: a chair faces its table, a nightstand the way its bed faces, a TV unit its seat; the only side on a wall is the back; in a corner a bed's / toilet's short side, else the long side; against 2–3 walls the free side facing the most room; `front_inferred`, `inferred`, evidence |
| Open kitchens | `reading.py`: `kitchen_zones` | a room that is not a kitchen holding kitchen fixtures gets `rooms[].zones = [{zone_id, kind: kitchen, polygon, piece_ids, evidence}]`: the fixtures and the 1 m in front of them (convex hull, clipped to the room) |
| Never a box | `reading.py`: `never_a_box`, `_refresh_rooms` | a piece still `unknown` is `build: false` (`not_built_reason`) and listed in `building["needs_review"]` (`kind: untyped_piece`, reason with size, room, AI candidates, crop); a piece whose question waits is not built and not listed |
| Hook | `reading.py`: `read_furniture` | the steps in order; counts in `build.reading` |
| Report | `pipeline.py`: `_reading_section` (in `write_report`) | context rule counts, symbols by kind (table with reason and crop), needs review (table with crop), adjusted fixed equipment (drawn and new size, reason), kitchen zones |
| Debug image | `pipeline.py`: `_generic_debug_items`, `SYMBOL_COLOUR`, `LEVEL_MARK_COLOUR` | pieces as the reading step left them (type, footprint, "not built" dashed), the moved symbols (purple, dashed, also track L's `sym_<piece>` level-mark symbols) and the level marks (`building["level_marks"]`, orange) on the per-page image |

## 2. Decisions taken inside the design

- **Old answers keep working.** The recognition answers of earlier rounds apply only when the question key and its
  input hash match, and the keys are sequential. So the main pass decides its candidates exactly as before: the M12
  block words are not used there (`keyword_type(extended=False)`, `_block_keyword`), and everything new happens
  after the answers (`_m12_named`, the re-read of still-unknown candidates) or under new content keys
  (`extra_key`: a hash of the stroke ids). Checked on real03 and real02: with this track's code every old key keeps
  its hash (track B's new size table changes the choices of some questions: §4).
- **Only answered candidates are re-read.** A candidate the passes left `unknown` (disagreeing, or both unknown) is
  re-read; one without answers (`--no-ai`, or answers that no longer apply) keeps its piece and its open question.
  Re-reading unanswered candidates split real02's two L1 corridors differently (one bench is loose lines, its twin a
  block), so the mirror twins were lost; the M11 contract "`--no-ai` only changes the report" holds again. Never-asked
  clusters (oversized, composites fitting no type) are always re-read, and an M12 block name types a candidate with
  or without answers.
- **The drawing outranks the AI passes** (CLAUDE.md trust order) for symbols: a room-number circle both passes called
  a floor lamp, a door detail called a console table, become symbols, with a `type_disagreement` conflict. Same for a
  block name the M12 words read and a table with chairs drawn around it (`ai_overridden` → conflict).
- **A layer name says less than a rule or a block name**: a piece typed by a rule or its block name stays furniture
  even when its layer is a symbol layer (real02's counters on the decor layer `DEKOAKRILIK01`). Shapes (room-number
  circle, door swing, north arrow) always count.
- **Door swings** need their leaf (a thin strip from the hinge) or a hinge at an opening's jamb; a lone arc does not
  make a door (a quadrant shower's arc, a chair's back). An arc in a furniture-named block is never a door.
- **Columns and decor stay in `furniture`** as not-built pieces (`inferred_as: column | decor`): a column is still an
  obstacle for the layout, decor is the decor stage's business. Only symbols leave the furniture. Inside a re-read
  cluster a column is a not-built piece too, but decor strokes there (accessories, tile hatches drawn over a piece)
  are `other` symbols: track G's solver treats every drawn piece, built or not, as an obstacle.
- **Context typing is an inference** (CLAUDE.md: type from size, room and neighbours): the piece keeps its
  `type_method` and `status` (as M11's size inference does), carries `inferred: true`, `inferred_reason` and an
  evidence entry (`rule: reading.context`), and is listed in the report's inferred section.
- **A dishwasher block is a counter piece** (a base unit of the run), not an appliance of its own.
- **Copies** of one block drawing (real03's four flats) take each other's type only at the same size (± 2 cm).
- **Never a box**: the reason is kept in `not_built_reason` and the `needs_review` entry, not as a new evidence entry
  (evidence lists sources; `tests/test_pipeline.py` checks the secondary-page piece has one). A piece whose question
  waits for its answers is not built and not listed (the pipeline lists the open questions). A cluster still over
  4.5 m after the re-read is `oversize`, not built, listed.
- **Misread fixed equipment** (U1) uses two problems only: through a wall (> 5 cm past the room outline) and in a door
  swing (> 5 % of the piece). Overlaps with other fixed pieces are not this rule's business (a sink stands in its
  counter; the duplicates rule handles a piece drawn twice). The swing is the two quarter discs of the leaf hinged
  at either jamb, within the opening's width (the hinge side is not read): a piece beside the frame is not in it
  (real02's washbasins). Counters and stairs are not resized (runs and flights have no product size).
- **Product size**: `sizes.product_size` (track B, orientation-aware). Without a front the drawn sides are read the
  way round that fits the type best. The back (or the side on a wall) stays where it is drawn.
- **Crib fronts**: after track B's size table (the crib's front is a long side), the reading's corner rule treats a
  crib like a cabinet (long side on the wall = back), not like a bed.
- **Open-kitchen zone** = the kitchen fixtures and the 1 m in front of them, convex hull clipped to the room; one zone
  per room (kind `kitchen`), with `piece_ids` and evidence.

## 3. Tests added

Every rule is new: each test fails on the code before track R (the hook was a stub, the functions did not exist).

Changed expectation (an existing test of track R's files):
`tests/test_real01.py::test_every_reference_footprint_is_found` (--no-ai: an untyped piece is not built and is listed
for review; was: every piece built). Without the AI 16 of real01's 20 pieces are now typed (before 5): 4 nightstands,
the dining table and its 6 chairs by context. Added to the slow real-data modules (LibreDWG; they reuse the modules'
pipeline runs): `tests/test_outline_walls.py::test_real03_furniture_is_read_completely`,
`tests/test_real02_pipeline.py::test_m12_every_drawn_piece_is_typed_or_explained`.

| File | Tests | What |
|---|---|---|
| `tests/test_reading_symbols.py` | 18 | layer words (folded, whole-word short keys, furniture words win, xref names); a furniture-named block on a services layer; the M12 block words (KOMODİN, ÇAMAŞIR, EVYE, Dishwasher, BERJER, ORTA SEHPA, GARDİROP, REFRIGERATOR) and that the main pass does not use them (`extended=False`); room-number circle (number inside, not a name, not too large); door swing with its leaf, the swing split from a fridge box; quadrant shower, chair back and a named block are no doors, a jamb hinge is; north arrow; layer symbols, column, decor, door layer, mixed with furniture; object groups (a sink block is one object, a flat block's own strokes clustered, page-wide containers); copy keys; extra keys and `expand_ids`; the toilet axis line trimmed; an oversized cluster chained by trace lines re-read into sofa and table with an `other` symbol; a room-number tag among the furniture; the re-read's unknown part asked under its content key; a counter outline along two walls re-read as two legs with its sink (drain); a column inside a re-read cluster stays a not-built obstacle, decor strokes there are symbols |
| `tests/test_reading_building.py` | 20 | symbols moved with crop, conflict when the AI typed one, a column kept not built; copies; nightstands; dining chairs facing the table; a table with seats around it is a dining set; coffee table and TV unit facing the sofa; armchair pair; counter holding a sink and the fridge closing the run; vanity under a washbasin; misread toilet → product size, back on the wall, `drawn_*`, `adjusted_by_ai` with crop; washbasin through a wall moved back; toilet in the door swing moved out; a piece beside the door frame left alone; fronts from the wall (wardrobe, bed in a corner, crib after track B); kitchen zone in a living room, none in a kitchen; never a box (`needs_review` with crop, evidence unchanged); a waiting piece left to its answers; a stove drawn twice; unbuilt pieces say why, an oversized cluster is listed; the report section |

## 4. Real data, before / after

`pipeline.run_project` with the committed recognition answers (`results/recognition/<project>`), CPU, LibreDWG from
`scripts/cloud-setup.sh`. Before = the fork point (`4a6701e`, M11 reading); after = this branch merged with
`opus_branch_06` (tracks A, B, G, L, S). real03: 173 s, real02: 228 s.

| real03 (D Blok ground floor, 8 flats) | before | after |
|---|---|---|
| built unknown boxes | 43 | **0** |
| oversized clusters (> 4.5 m, 92–100 % of their rooms, not built) | 7 | **0** (all 7 re-read into pieces and symbols) |
| candidates the passes left unknown, re-read | – | 4 |
| symbols (never built) | 0 | **71**: other 32 (trace, view, door-detail lines), door_arc 20, room_number 8, text_frame 8, dimension_outline 3 (+ track L's level-mark symbol) |
| AI types the drawing overrules (conflicts) | – | 7 `type_disagreement`: 3 "floor lamps" are room-number circles, a "stair" is a trace line, a "side table" a view line, 2 "sofas" are a table with its chairs (before the merge also 4 "console tables" on the door layer, whose answers no longer apply, see below) |
| kitchen counters / sinks / fridges / stoves | 0 / 0 / 0 / 10 | **14 / 8 / 8 / 8** (2 hobs drawn twice inside the OCAK block, not built) |
| dining tables / chairs | 0 / 0 | **6 / 18** (2 drawn sets the AI called sofas) |
| corner sofas / coffee tables / TV units | 2 / 0 / 0 | **8 / 8 / 8** |
| washbasins / toilets / showers / bathtubs | 0 / 8 / 10 / 3 | 2 / 8 / 10 / 4 |
| toilets > 30 % outside their size range | 8 (1.145 x 0.356 m) | **0** (0.36 x 0.53 m: the axis line left out at extraction) |
| fixed pieces adjusted (U1) | – | 7 (6 showers and a washbasin through a wall, moved 0.10–0.15 m) |
| drawn fronted pieces without a front | 31 of 80 | **4 of 128** (29 fronts inferred) |
| kitchen zones (open kitchens in living rooms) | 0 | 8 |
| not built, explained | 33 (unknown) | 21 details (vanities, drawn twice, small marks), 4 columns (inside re-read clusters), 2 untyped |
| needs review | – | 2 (a 1.50 x 0.60 m piece the passes call dresser / wardrobe, a 0.40 x 0.20 m mark) |
| recognition questions | 95 | 95 old (keys kept) + 26 extra (content keys, unanswered) |

| real02 (villa, 4 plan regions) | before | after |
|---|---|---|
| built unknown boxes | 40 | **0** |
| symbols / columns / decor (not built) | 0 / 0 / 0 | 0 / **10** (`A-BA` layer, 2 of them inside re-read clusters; kept as obstacles) / 6 (`Deko_*` layers) |
| sinks (EVYE blocks: the M12 word) | 0 (4 called fridge by the AI) | **4** (+ 8 parts of the same blocks drawn twice, not built); fridges 4 → 0 |
| dining tables / chairs | 4 / 36 | 10 / 50 (two 0.79 m round tables by size and room with their 2 chairs; four 0.79 x 0.65 tables with 2 chairs each split by geometry) |
| armchairs | 2 | 8 (4 by the pair rule at a coffee table) |
| fixed pieces adjusted (U1) | – | 0 (the washbasins beside the bathroom doors are beside the swing, not in it) |
| drawn fronted pieces without a front | 16 of 116 | **2 of 134** |
| kitchen zones | 0 | 2 (L-1b "Açık Mutfak + Salon") |
| needs review | – | 24 (mostly pieces whose answers no longer apply after the merge, see below; the two kitchen-side clusters of 5.54 x 0.60 and 5.14 x 2.37 m in the Salons) |
| recognition questions | 90 | 90 old (keys kept) + 6 extra |

**Old answers after the merge (for the lead).** With this track's code alone every old question kept its key and
input hash (real03 95/95, real02 90/90, checked before the merge). After merging track B's size table, the
`question.choices` of 28 real03 and 26 real02 questions change (new fitting types: `floor_lamp` 21, `bar_stool` 10,
`tall_cabinet` 1, `dresser` 1 on real03), so their input hashes change and those answers no longer apply. Nothing
else in the questions changed. The next recognition round must ask them again (or the choices of a question could be
frozen to the size table it was asked with). Until then those pieces are typed by the building-level context
rules and the size inference where they can be, else not built and listed for review.

`--no-ai` (what `tests/test_outline_walls.py` runs on real03; the asked candidates get no answers, those no rule
types stay unknown, not built and listed): 0 built unknown, 12 counter legs, 6 sinks, 6 fridges, 8 toilets, 8 corner
sofas, 6 coffee tables, 6 TV units, 11 nightstands, 71 symbols, 8 kitchen zones, 29 needs review. real01 `--no-ai`: 16 of 20 pieces typed (before 5),
4 needs review (the drawing room's sofas, coffee table and round piece, which only the AI types).

## 5. What is left

- **The extra questions need a GPU round.** The re-read's unknown parts that fit a type are written to
  `recognition/requests.json` under content keys (format unchanged: real03 26, real02 6); until a recognition round
  answers them the context rules and the size inference type what they can, the rest is not built and listed under
  "needs review". The same round should ask again the 28 + 26 questions whose choices track B's size table changed
  (§4). No pod was run in this track.
- **Axis bubbles and section marks** are told by their layer names only; a grid bubble with a digit inside on a
  furniture-neutral layer is caught by the room-number shape (kind `room_number`, still never furniture). No shape
  rule for section marks.
- **AI types that no code check contradicts stay**: 6 of real03's bathroom bowls with a drain (0.70 x 0.68 m, block
  `A$C38267379`) are "showers" for both AI passes; a re-read of them without the answers (an earlier experiment of
  this track) called them washbasins (bowl with a drain in a bathroom). Both sizes are borderline for both types, so
  the agreeing passes win; the agent's critic can look at them.
- **real02**: the two kitchen-side clusters of 5.54 x 0.60 m and 5.14 x 2.37 m in the L-1 / L-1b Salons stay untyped
  after the re-read (listed for review); most real02 review items are pieces whose two AI passes disagree.
- **real02 L1 twins with the answers**: each attic corridor holds a 1.52 x 0.60 m table with seats drawn around it.
  The AI called one a bench (both passes) and disagreed on the other; the reading splits both into a table and its
  seats (the table-with-chairs rule over the AI on one, the re-read on the other), but the two are drawn differently
  (a block and two polylines; loose lines, two stool blocks and a chair whose centre lies in the terrace), so the L1
  corridor and terrace pairs are no longer mirror twins in the answers run (each is rendered on its own). The
  `--no-ai` run keeps them (`tests/test_real02_pipeline.py::test_attic_rooms_and_twins`).
- **Crops**: a symbol or a review item has a crop only when its piece was asked (`recognition/crops/<key>_ctx.png`);
  the others are on the per-page debug image.
- **Vision typing model**: the leftovers go through the existing two-pass recognition questions (candidates = the
  size-fitting types + `unknown` + `not_furniture`); moving them to one pass of the strongest model with a code
  critique (§4.1 row "Vision typing", §5.1) is the recognition runner's change (lead / track A).

## 6. Changes needed in other tracks' files

| Track | File | Request |
|---|---|---|
| G | `wenart/furniture/program.py`, `solver.py` | nothing required (checked after the merge): `room_program` and the solver read `rooms[].zones` (R writes `{zone_id, kind: "kitchen", polygon, piece_ids, evidence}`), `_fixed_items` keeps every drawn piece built or not as an obstacle (R's columns, decor, details and untyped `needs_review` pieces) and skips `symbols[]` by `former_piece_id`. Note: an `inferred_as: "detail"` piece (a vanity under its washbasin, a hob drawn twice) lies inside its host |
| A | agent critic and tools | show `building["needs_review"]` (crop, reason) and the reading's `type_disagreement` conflicts to the critic: they are the pieces where `retype_piece` / `mark_not_furniture` help. `fix_fixture` needs no change: `edit_ops` keeps R's `drawn_*` (`setdefault`) and measures its 0.5 m from the drawn centre, so ingest and agent moves together stay within 0.5 m |
| lead | `wenart/report/final.py` | list `building["needs_review"]` (piece, room, reason, crop) and the symbol counts in the final report too (the ingest `report.md` has them in "Reading (Milestone 12)") |
| lead | `wenart/schema/building.schema.json` | document: furniture `front_inferred` (text), `not_built_reason`, `inferred_as` (`column`, `decor`, `detail`, `rug`), `adjusted_by_ai.rule` / `changed` / `crop`; `needs_review[]` `room_id` / `level_id`; the items of `rooms[].zones` (as above); symbol ids `sy_<level>_NNN` (track R) next to `sym_<piece>` (track L) |
| lead / A | recognition runner (pod round) | answer the extra questions (`sym_<level>_x<8 hex>` keys) in the next recognition round; the answer files and their format are unchanged |
| B / lead | `wenart/recognition/size_table.yaml`, `recognition/symbols.py` | `sizes.product_size`, `real_range` and `fits` are used as they are. Note: a question's choices come from the size table, so the new table changed the input hashes of 28 real03 and 26 real02 questions and their answers no longer apply (§4): re-ask them in the next round, or freeze a question's choices to the table it was asked with |
| lead | `tests/test_real02_pipeline.py` | `test_alternative_basement_rooms_twins_and_same_as` fails on `opus_branch_06` itself (checked on an export of `9635c95`): the L-1b face is labelled "Salon" ("the label with the largest printed area (else the first) kept"), the test expects "Açık Mutfak"; not touched by track R |
| L | – | nothing: a level mark still among the pieces after `apply_levels` is moved as `level_mark` (`_is_mark` uses `marks.parse_mark`) |
