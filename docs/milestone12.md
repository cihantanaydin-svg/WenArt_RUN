# Milestone 12 – ground levels, furniture overhaul, a smarter pod AI, library audit

Goal (user, 10 Oct 2026, prompt in `docs/prompts/milestone12.md`): the pipeline reads whole floors (real02, real03),
but the results are not good enough to show anyone. Five problems: (1) ground and floor levels, (2) furniture
placement, (3) decor and soft furnishings that float or cut through their host, and crude furniture, (4) the AI in
the pod reaches few rooms and most of its edits are rejected, (5) the library has unrealistic items, wrong sizes
and wrong categories.

Session: cloud (`CLAUDE_CODE_REMOTE=true`), branch `opus_branch_06`, 10 Oct 2026. Step 0 is CPU only (no pod).

Status: **Step 0 (diagnosis) done, 10 Oct 2026; waiting for the user before Step 1 (design).**

## 1. Diagnosis (step 0, CPU, 10 Oct 2026)

### 1.0 Inputs and method

- Results: the committed real03 run 3 (pod `oesbppzw7hsnmb`, 84 views) and real02 G2d (`rx88jd2u31clb6`), plus
  real01 G3 for decor: `results/{final,furniture,agent,check,renders,compare,library}/<p>/`.
- The agent log `results/agent/real03/log.json` holds several runs. **Run 3 = events seq 184–913 (16:08–16:38 UTC)
  and `calls[138:]`** (144 model calls); the earlier events are the core-only run and runs 1–2.
- Code: `wenart/agent/`, `wenart/furniture/`, `wenart/blender/`, `wenart/sheets/`, `wenart/ingest/`, `wenart/assets/`,
  the catalogues `wenart/furniture/catalog.json` (Poly Haven) and `catalog_library.json` (1032 models).
- Five read-only reviews (furniture, decor, agent, levels, library). Every count was computed with a script
  (python3 on the committed JSON), not estimated; the key claims were re-checked by hand. No code was changed.
- Not available in git: the layout debug PNGs (`.gitignore:27` ignores `results/**/*.png`; the room JSONs are there)
  and the library GLB files (on the pod volume, `/workspace/assets/models/`).

### 1.1 Short version

| Area | What the user sees | Main cause (details below) |
|---|---|---|
| Furniture | pieces scattered, TV not facing the sofa, nightstands at mid-bed, lone stoves in living rooms, white boxes | most drawn pieces are not read into usable pieces (real03: 42 built `unknown` boxes, 6 unbuilt clusters over 92–100 % of their rooms); the AI adds **single pieces with raw coordinates**; the placer repairs each piece alone; the 5 group templates exist but **no stage uses them**; the checks count pieces, they do not judge arrangements |
| Decor | cushions float over beds or sink into sofa backs, throws hang in the air or are not throws | cushion and throw height comes from a **fixed table per type** (bed 0.55 m, sofa seat 0.45 m), not from the built model; x/y from the drawn footprint; agent edits move the furniture and leave the decor behind; nothing measures gaps |
| Realism | boxy sofas, bare mattresses, low-poly lamps, stretched pillows | 42 + 28 boxes or code-made pieces in real03; library models that are the wrong object; a bug makes the judges' quality score unused |
| Agent | 5 of 78 edits accepted (73 rejected), 12 of 35 rooms visited, no plan | 73 % of the rejected edits target pieces **no tool may change** (locked fixed equipment, unbuilt pieces); tools take raw coordinates and do not show locks or free space; 120-call cap per round, a time estimate 15 min too long; no memory, no dry run |
| Levels | buildings on flat ground, doors flush on the grass, no exterior at all for real01/real03 | level marks (KOT) on plans, site plans and in blocks are **never read** (the one pattern rejects the Turkish forms); the model has no room floor levels, door thresholds or terrain; the ground defaults to ±0.00 so the ground floor always sits at grade; single-region projects skip site and exterior |
| Library | air bed as a double bed, "Corpse" as a throw, table lamp stretched to a floor lamp, bathtubs 0.89 m high | judges see a 256 px sheet with no scale reference and no title; no real-size check for the 286 models without real units; the quality score is lost; 28 % of the furniture is generated |

### 1.2 Furniture placement

**How it works today**

| Area | file:line | What it does |
|---|---|---|
| Empty-room layout | `furniture/layout.py:288-331`, `prompts.py:57-82`, `:150` | two **text-only** passes of Qwen3-VL-8B (no image); the pass with the fewest dropped pieces wins; groups appear only as prose ("sofa facing a tv_unit …") |
| Answer schema | `schemas.py:383` (`LAYOUT`), `prompts.py:209` | a flat list of ≤ 12 **single pieces**: `type, center, rotation_deg, size, against_wall, reason`; no group, anchor or relative offset |
| Placer repair | `placer.py:887`, `:940`, `:1019`, `:817-857` | one piece at a time: snap to the **nearest** wall → slide ≤ 2.5 m (free pieces on a ±1 m grid, turned 90°) → shrink → **another wall** → drop |
| Placer checks | `placer.py:579` | 6 per piece: inside, no overlap, clearance, doors, windows, wall contact; none between pieces |
| Completion of furnished rooms | `complete.py:1041`, `:862`, `:576` | the VLM adds single pieces with coordinates; `filter_added` caps counts; the placer repairs them; an unbuilt drawn piece is an obstacle (`:371`, `:800`) |
| Companions | `complete.py:603-635`, `schemas.py:283` | only chair, office chair, bar stool have a host ("within 0.6 m", then turned to it); nightstands, coffee tables, TV units have none |
| Group templates | `groups.py:34`, `:105-139`, `:292` | dining_set, bed_set, living_set, desk_set, kitchen_run (a straight line fridge-counter-sink-stove; no L/U, no landing space) |
| Who uses them | `edit_ops.py:510` | **only** the agent's `add_group`; called 0 times in every real02/real03 run; 0 built pieces carry a group |
| Type inference | `infer.py:31`, `:176`, `:237-249` | a type only when exactly one type fits; a 0.8 m square fits coffee table and armchair → stays `unknown` |
| Room-type tables | `schemas.py:154` `ALLOWED_TYPES`, `:257`, `:259`, `:320` | living rooms allow no kitchen type (open kitchens cannot be completed); baths and WCs never get a piece added (not even a missing washbasin) |
| White boxes | `blender/furniture.py:791`, `proxies.py:34`, `:143-157`, `materials.py:96` | every built `unknown` = 0.8 m box, flat grey (reads white in daylight); F9 only reports it |
| Plausibility | `plausibility.py:209` F1/F2, `:335` F3/F4, `:385` F5, `:422` F6/F7/R3, `:494` F8, `:515` F9 | F2 accepts a size "either way" (a bed turned 90° passes); F4: front not into a wall, facing one `front_to` target within 45°; F5 only **counts** partners nearby (nightstand ≤ 0.5 m, coffee table ≤ 2 m, chairs ≤ 0.8 m) |

**Not checked by any rule today:** TV opposite the sofa on its axis; coffee table between sofa and TV; one nightstand
on each side of the headboard; chairs spread around the table; free access on both long sides of a bed; kitchen
work order (sink, hob, fridge), landing space, continuous counter, a sink at all; bathroom set (washbasin present,
clear zone in front of the toilet, access to shower/bath); walkway to each piece's use side (only door-to-door and
door-to-window); a TV unit or shelf in front of a window; a bed turned 90°.

**Counts (`building_final.json`, findings of the last round)**

| | real03 run 3 | real02 G2d |
|---|---|---|
| Pieces / built | 193 / 158 | 282 / 257 |
| Built: from documents / added by AI | 130 / 28 | 185 / 72 |
| Pieces from the empty-room layout | **0** (2 halls asked, every piece dropped) | 10 in 4 rooms |
| **Built `unknown` (white boxes)** | **42** (living 17, hall 14, bedroom 6, stair 2) | **32** (kitchen 14, living 13, other 5) |
| Drawn pieces built with no front (guessed) | 31 (105 of 193 have `front_deg: null`) | 18 |
| Types missing although drawn | kitchen counter, kitchen sink, fridge, washbasin, dining table, chair: **0 built** | kitchen sink: 0 |
| Type not allowed in the room (F1) | 14: 10 stoves in living rooms, 4 washing machines in entrance halls | 5 |
| Facing a wall (F4) | 16 | 9 |
| Door blocked (F7 critical) / window blocked / door swing hit (R3) | 8 / 10 / 8 | 0 / 3 / 10 |
| Findings (code + vision) | 259: 18 critical, 178 major, 63 minor (F9 87, F6 52, F3 31, F4 26, F7 18, F1 16) | 187: 6 critical, 118 major, 63 minor |

**Group relations measured by hand (no check covers them):**
- Nightstands: real03, 5 added, 4 not at the headboard (`f_L0_166`/`167` both on one side at mid-length, `f_L0_173`
  mid-side, `f_L0_177` at the foot); real02, 12 added, 8 at mid-side or foot; **none of the 6 double beds of real02
  has one nightstand on each side of its headboard.**
- Sofa and TV: real03 `yasama`, `_7`, `_8`: the TV front points 57–65° away from the sofa; `yasama_3` 74° off its
  axis; `yasama_5`, `_6` got a TV unit and have no sofa. real02 `salon`: TV 90° off the sofa axis, coffee tables
  3.8–4.7 m away **behind** the sofas.

**Evidence** (RP random placement, GB group broken, WF wrong facing, DW door/window blocked, WB white box, WS wrong
scale, RT wrong room type or misread)

| # | Project / view | Piece(s) | What is wrong | Cat. | Cause |
|---|---|---|---|---|---|
| 1 | real03 `yasama_1` | f_L0_168/169/170 | the VLM put the sofa centre on the stove centre, coffee table and TV 0.5 / 1.6 m away, all rotation 0; the placer snapped the TV to the nearest wall: 65° off the sofa | GB WF | single-piece schema; `placer.py:1019` |
| 2 | same | f_L0_171 | armchair behind the sofa's back, looking at it | RP | grid slide accepts any spot passing the 6 checks |
| 3 | same plan | added sofa, TV, armchair | sit on a drawn dining set, counter run and sofa that ingest never read | RP | drawn pieces missing |
| 4 | real03 `yasama_4_1` | f_L0_047, f_L0_003 | 22 m² room with only a stove (the "lone blue stove"); the unbuilt cluster f_L0_003 (6.15 × 5.85 m, 98 % of the room) blocked all 9 proposed pieces | RP | `complete.py:371`, `:800` |
| 5 | real03 `yasama_5_1` | f_L0_131, 093, 091, 094 | grey boxes 0.8², 0.74², 0.9 × 1.4, 0.49² m; candidates coffee table/armchair, sofa/dining table, floor lamp/plant | WB | `infer.py:237-249` |
| 6 | same | f_L0_180 | TV unit placed where the drawn sofa is (the sofa is lost in the unbuilt cluster f_L0_004) | GB | single add; obstacle rule |
| 7 | real03 `yasama_2_2` | f_L0_102 (and f_L0_095) | a 0.9 × 1.4 m "sofa" is the drawn dining table (chairs drawn around it) | RT WS | AI typing; F2 either way |
| 8 | same | f_L0_104, f_L0_105 | the "armchair" is a door-swing arc; the "floor lamp" is room-number circle 2 and blocks door o_L0_016 and window win_L0_025 | DW RT | AI typing; agent may move a drawn piece only 0.3 m |
| 9 | real03 `yasama_7_2` | f_L0_073, 078, 038/160 | the counter run (hob and sink drawn) is a 3.54 × 0.85 × 0.8 m slab; a lamp is room-number circle 5; two stoves overlap 0.29 m² | WB RT | `infer.py:31`; no kitchen types in living rooms |
| 10 | real03, all flats | f_L0_078, 079, 094, 098, 105 | 5 of 6 room-number circles (inserts 7C9C9/49–54) are built as furniture | RT WB | no filter for drawn symbols |
| 11 | real03 `ebeveyn_odasi_1` | f_L0_024 | a 3.93 × 2.25 m unknown built as a 0.8 m box over half the bedroom | WB | `proxies.py:143-157` |
| 12 | same | f_L0_166/167 | both added nightstands on one long side of bed f_L0_059, mid-length | GB | completion singles; F5 counts only |
| 13 | real03 `ebeveyn_odasi_3`, `oda_01` | f_L0_173, f_L0_177 | nightstand at mid-side; one at the foot of bed_single f_L0_061 | GB | same |
| 14 | real03 `ebeveyn_odasi_4` | f_L0_119, f_L0_175 | a second double bed with no front faces a wall 0.01 m away; nightstand on the same side as the drawn one | WF GB | no front; locked moves |
| 15 | real03 `banyo_*` (all 8) | f_L0_039/040/044/048/066–069 | every toilet is 1.145 × 0.356 m (misread), 6 block the door, they reach through the wall; **no washbasin built in any bath** although drawn | WS DW | `schemas.py:220`, `:257`; fixed lock |
| 16 | real03 `banyo_*` | f_L0_128, 164, 123, … | 10 showers and 3 bathtubs with a guessed front; 8 face a wall | WF | default front |
| 17 | real03 `giris_holu_1–4` | f_L0_062–065 | washing machines in entrance halls facing the wall; f_L0_064 through the wall | RT WF | fixed lock (`schemas.py:227`) |
| 18 | real03 `kat_holu` | f_L0_087/146, 150–154, 179 | console tables break 16 walkways; 0.56 × 0.28 m unknowns as boxes; shoe cabinet mid-hall | DW WB | infer; single add |
| 19 | real03 `yasama_8` | f_L0_192, 141, 116 | TV unit and bookshelf in front of window win_L0_046; corner sofa does not face the TV | DW WF | F7 checks only the sill height |
| 20 | real02 `r_L-1b_oda` | f_L-1b_061–065 | empty-room layout: desk without chair; dining table with 1 chair 1 m away facing a wall; armchair floating | RP GB | VLM coordinates + placer |
| 21 | real02 `salon_2` | f_L-1_089, 073, 090 | TV at the window wall 90° off the corner sofa; coffee table 3.8 m away behind the sofa | GB | completion singles |
| 22 | same | f_L-1_059/063/064; 070/071/087/060 | drawn palms built as floor lamps; drawn lounge chairs as unknown boxes | RT WB | AI typing; infer |
| 23 | real02 `e_yatak_odasi_1` | f_L0_007, 031/032, 042/043, 044 | agent resized the bed 2.55 × 2.0 → 2.0 × 1.6 but kept rotation 270: the bed is turned 90°; drawn nightstands with lamps typed as floor lamps; both added nightstands on one side; bench at the headboard | WS GB | resize "either way" |
| 24 | real02 `yatak_odasi_3/_4` | f_L0_045/046, 055/056, 047 | both nightstands of each bed on one side toward the foot; bench at the headboard | GB | completion singles |
| 25 | real02 `mutfak`, `acik_mutfak` | f_L-1_008/067, 007, f_L-1b_044–052, f_L-1_093 | no sink in any kitchen; stove and fridge overlap the counters; fridge in front of window win_L-1_003; 8 unknown boxes in the open kitchen; dining table with 2 of 6 chairs | GB WB DW | no kitchen-run rule; infer |

**Root causes, ranked**
1. **The drawn furniture is mostly not read into usable pieces** (real03: 42 unknown boxes, 6 unbuilt clusters over
   92–100 % of their rooms, counter runs, sinks, fridges, washbasins, dining sets and sofas lost; room-number circles
   and door arcs built as furniture). Added pieces then land on furniture the pipeline cannot see.
2. **The AI layout is a list of single pieces with raw coordinates** from a text-only 8B model (no image, no groups).
3. **The placer repairs each piece alone** (nearest wall, slide, other wall); no check between pieces.
4. **The group templates are never used** by layout or completion.
5. **The checks count pieces, they do not judge the arrangement** (§ "Not checked" above).
6. **Unknown pieces stay unknown, and misread fixed equipment cannot be fixed** (one-fit rule; fixed lock).
7. **The room-type tables block the obvious fixes** (open kitchens in living rooms; nothing added to baths).

### 1.3 Decor, soft furnishings and crude furniture

**How it works today**

| Step | file:line | What it does |
|---|---|---|
| Cushion x/y | `decor.py:169-199`, `:110-111`; `decor_ai.py:378-388` | in the piece's frame at `y = d/2 − size/2 − 0.1` of the **drawn footprint**, not the model's back or headboard; sofa cushion 0.45 × 0.15, bed pillow 0.5 × 0.3 m; no z stored |
| Throw | `decor_ai.py:1168-1190` | 0.95 × bed width × 0.5 × **0.05 m** |
| Cushion/throw height | `blender/furniture.py:519-532` → `parametric.py:2206-2229`, `proxies.py:28-44` | `proxy_height(type)` from **`PROXY_HEIGHTS`**: a library bed always 0.55 m; sofa, armchair, corner sofa, chaise seat `min(0.45, 0.55·h)` = 0.45 m; a parametric bed uses `bedding_top` = **the top of its pillows** (throw 0.03 m below) |
| Library bed frame | `furniture.py:1355-1357`, `parametric.py:421` | all decor at `bedding.top_m` (again the pillow top) |
| Ray onto the real surface | `furniture.py:1273`, `:1290`, `:1358-1374` | only `SURFACE_DECOR_TYPES` (vase, lamp, small plant, candle …) and AI book sets; **cushions and throws excluded** |
| Library furniture scale | `fit.py:162-168`, `furniture.py:297` | x, y to the footprint; z = mean of x and y (0.78–1.26 in these runs); decor height ignores it |
| Library decor scale | `fit.py:551`, `:606-644`, `furniture.py:1417` | stretch cap 1.5; a throw squashed to 0.05 m whatever the model; bed pillows stretched to 0.5 × 0.3 × **0.60 m tall** |
| Agent edits | `agent/overrides.py:8-14`, `edit_ops.py:527`, `:582` | moves, turns and resizes are replayed on `building_decor.json`; decor is dropped only when its piece is removed, **never moved with it** |

**Measured on the committed results** (104 hosted items, real01–03): every cushion and throw on a library bed sits at
**0.550 m** (library beds 0.71–1.46 m tall, z-scale 0.79–1.03); every cushion on a library sofa/armchair at **0.45 m**
(z-scale 0.80–1.03). Surface decor (22 items): gap 0.000 m, correct. Parametric corner sofa f_L-1_053 and sofa
f_L0_095: **50–64 % of each cushion inside the backrest**. Parametric beds f_L0_119, f_L0_061: cushions on the pillow
top, **0.17–0.23 m above the mattress**; throw 0.07–0.11 m above the duvet.

**Evidence**

| View | Piece / decor | What is wrong | Cause |
|---|---|---|---|
| real02 `L0_e_yatak_odasi_1/_2` | dec_L0_010 throw on f_L0_007 | long white slab in the air past the bed foot, wider than the bed | bed resized by the agent after decor |
| same | dec_L0_008/009 | cushions high above the duvet on the model's own pillows | 0.55 m type height, model z-scale 0.789 |
| real02 `L0_yatak_odasi_3_1` | dec_L0_019/020 on f_L0_021 | clear gap and shadow under both cushions | 0.55 m above a lower mattress |
| real02 `L0_yatak_odasi_1` | dec_L0_003 on f_L0_019 | blue crumpled blob on the bed foot | "JuiceMachine" (objaverse_6b46b3…) as a throw, squashed to 5 cm |
| real03 `ebeveyn_odasi_2_1` | dec_L0_010 on f_L0_046 | large blue lump at the bed foot; 0.6 m tall pillows; bare mattress | same model; pillow stretch |
| real03 `ebeveyn_odasi_1` | dec_L0_003 on f_L0_059 | crumpled scrap hanging off the mattress; 3.9 × 2.2 × 0.8 m box f_L0_024 | generated throw squashed; unknown proxy |
| real03 `oda_01_1/_2` | f_L0_061, dec_L0_033/034 | cushion on top of the built-in pillows, throw hovering; headboard on the 1.95 m side | `bedding_top`; footprint w/d swapped |
| real03 `yasama_2_1` | dec_L0_026/027 on f_L0_102 | cushions in mid-air beside the sofa | agent rotation after decor |
| real03 `yasama_8_1` | dec_L0_100–102 on f_L0_116 | cushions sunk inside the back cushions | fixed offset and 0.45 m, not the model's back |
| real03 `yasama_1` | dec_L0_013/014 on f_L0_168 | cushions cut through the back and stick out over the top | same |
| real03 `yasama_7_1` | dec_L0_086 on f_L0_187 | cushion pierces the armchair back | same |
| real02 `L-1_salon_1/_2` | dec_L-1_001–007 on f_L-1_053 | cushions half inside the back | 50–52 % inside |
| real02 `L1_oyun_1/_2` | dec_L1_001/002 on f_L1_009; dec_L1_003 on f_L1_029 | decor cushions wedged behind the model's own cushions; armchair cushion floats behind the chair | duplicates; agent turned the chair |
| real01 `drawing_room_1` | dec_L0_010–012 on f_L0_017 | cushions and throw hover above the seat | 0.45 m vs a model at z-scale 0.906 |
| real01 `bed_room_1` | dec_L0_003 on f_L0_007 | the throw is inside the mattress (only a sliver shows) | 0.55 m below this mattress top |

Correct today: wall art, rugs, floor plants, lamps and plants on nightstands and TV units (ray cast).

**Crude or unrealistic furniture**
- Boxes: built `unknown` proxies (real02 32, real03 42).
- Code-made (parametric) pieces among the built typed pieces: real02 77 of 225 (32 by design: counters, wall
  cabinets, stairs, islands; 45 because no library model fit: washbasins 10, bathtubs 8, ottomans 8, toilets 4 …),
  real03 28 of 116 (3 stairs; 25 no fit: toilets 8, console tables 5, bookshelves 3 …). They look boxy: sofas as
  white boxes, blobby beds, plain shelves. Library: real02 148 (ABO 72, Objaverse 70, generated 6), real03 88 (ABO
  53, generated 22, Objaverse 13).
- Low-poly or odd library models used many times: "low poly Lamp 3d model" (objaverse_53409613…, 2,456 faces, a
  table lamp stretched to a 1.03–1.37 m floor lamp) 12–13×; "Stove from Poly by Google" 10× (real03, mostly in
  living rooms); an ABO nightstand of 1,748 faces 15×; one Objaverse chair 42× in real02.
- Library beds chosen are mattress models: they render as **bare mattresses** with no duvet or sleeping pillows
  (bedding is only added to `bed_frame` models; none was chosen).
- Wrong proportions: a six-seat corner sofa (abo_B084XMQNTQ) scaled 0.78–0.82; dressers scaled up 1.21–1.32; beds
  turned 90° (real02), a single bed with its head on the long side (real03); 0.6 m pillows.

**Root causes, ranked**
1. Soft-decor height from a **type table**, not the built model (no ray, no settle).
2. Soft-decor x/y from the **drawn footprint** with a fixed 0.1 m offset; the real back, headboard and the model's own
   pillows are ignored (cushions inside backs, on pillows, duplicated).
3. "Bedding top" means the **pillow top** on parametric beds and bed frames.
4. **Agent edits do not carry decor** along with its piece.
5. Wrong objects in the decor library (throws that are a juice machine, a bench, a corpse; all throws squashed to 5 cm).
6. Proxies and parametric boxes are still built when typing or fitting fails.

**Checked today:** GPU test `tests/gpu/test_m9.py:107-123` (vase, bowl, small plant, table lamp only: bottom between
host bottom + 0.15 m and the host's box top; a vase sunk 30 cm passes). CPU tests pin the current behaviour
(`tests/test_blender_furniture.py:388-392` "library bed: type height", `tests/test_blender_bedframe_decor.py:215-225`).
**Not checked:** cushions, throws and books on shelves (no gap, no overlap, no x/y-inside-host check); decor
following its host after edits; whether a decor model is really its type; any render-side contact test with a
tolerance.

### 1.4 The agent in the pod (real03 run 3: 5 accepted, 73 rejected, 12 of 35 rooms)

**Rejected edits by failed check** (73; by tool: move 30, remove 15, change_type 12, resize 11, rotate 5)

| Failed check | n | Examples (seq) |
|---|---|---|
| fixed equipment lock (never moved 13, never removed 7, keeps size 6, keeps type 5, rotation that fixes nothing 4) | 35 | 591, 563, 592, 565, 614 |
| product size table | 8 | 564, 586 |
| `max_tries` (3 tries per target per round) | 8 | 567, 610 |
| piece already not built (`no_change`) | 5 | 562, 605 |
| wall snap: no free place | 5 | 572, 581 |
| drawn piece moved > 0.3 m | 4 | 579, 909 |
| placer `doors_free` / `inside_room` | 4 | 574, 603 |
| plausibility score drop | 3 | 575, 585 |
| room type does not allow the type | 1 | 901 |

| Target of the rejected edits | n |
|---|---|
| drawn fixed equipment (19 toilet, 6 shower, 6 stove, 3 bathtub, 3 washing machine) | 37 |
| pieces that are not built: f_L0_003 (6.15 × 5.85 m), f_L0_001 (13.2 × 2.68 m) | 16 |
| the two drawn double beds of `ebeveyn_odasi_4` (f_L0_119, f_L0_058) | 14 |
| other | 6 |

**53 of 73 (73 %) aimed at pieces no edit is allowed to change.**

**Accepted (5; §19.8 of M11 counted 4 applied):** a floor lamp moved 0.3 m (its door-blocking critical stays open), a sofa turned to face its TV, a
room-number circle and a dimension outline removed (real fixes), and `r_L0_oda_19` retyped `living` (wrong: it is a
lift lobby).

**Why the model proposes what the validator refuses**
- **Unfixable findings go to the planner as "fix these"** (`prompts.py:161`). The code critic reports the misread
  toilets (1.145 × 0.356 m, 6 of them "blocks the door", critical) while `edit_ops.py:28-30` allows fixed equipment only
  a rotation. The model is often right ("1.15 m is not a real toilet", a clear error per CLAUDE.md) but the validator
  has no path to accept it. Rule 2's example "a stove in a bedroom" leads the model to treat stoves in living rooms
  the same way; `schemas.misplaced_fixed` (`schemas.py:227-238`) does not cover that.
- **Unbuilt pieces look real to the critic.** The top-down image draws `build: false` pieces (`topdown.py:45`,
  `:91-104`), the critic's id list includes them (`critic_vision.py:53`), and F9 is vision-only, so code never
  contradicts it. Result: 6 critical "giant box" findings on pieces that are in no render; those two rooms ranked
  first in both rounds.
- **The model works blind on raw coordinates.** The `room` tool (`tools.py:414-418`) gives no locked/build flag, no
  allowed types or sizes, no remaining move allowance (0.3 / 1.2 m), no free wall spans; 105 of 193 pieces have
  `front_deg: null` and the "front = rotation − 90" rule is never told. Moves are absolute (`center [x, y]` or
  `snap_wall_id + offset`, `edit_ops.py:91-97`), no relational move. So the model guesses 0.1–0.2 m nudges or moves of
  0.97 / 0.39 / 0.303 m.
- **Better edits existed**: a dry run of `apply_edit` shows that removing the second double bed f_L0_119 (score
  67 → 90) or the misread floor lamp f_L0_105 (−56 → 24) would have been accepted.

**Coverage and time**

| Item | Run 3 |
|---|---|
| Faces | 55 (19 slivers or shafts, 6 m² in all, no pieces, no views) |
| Rooms with open critical or major findings | 35 |
| Rooms with a vision critic call | 36 in round 1, 3 in round 2 |
| Rooms with a planner session / an edit attempt / an accepted edit | **12 / 11 / 4** |
| Model calls | 144: 39 critic (mean 5.6 s), 105 planner (mean 3.1 s, ≈ 10.4k prompt tokens) |
| Agent time | 14.3 min of a ≈ 61 min job (23 %): vision 3.3, planner 4.3, re-run after round 1 4.8, round 2 1.4 |

- **Per-round cap 120** (`loop.py:47`, `:329`): sessions 1–11 used 118 calls, session 12 got 2; rooms #13–#35 never
  reached. Half the calls were reads or `finish`; the first edit always came at reply 3.
- **Time estimate too long**: the final stages were estimated at 34.7 min (`stages.py:712-729`, `scheduler.py:1750`,
  factor 1.6) and took 19.8 min; with the 20 min margin the loop had to stop at 16:18; the pod ended ≈ 30 min before
  its deadline. Rounds 3–4 and the final critical round never started.
- **Room order** (`loop.py:323`): most criticals first. Unfixable criticals put the two unbuilt boxes first and six
  baths with locked toilets at #6–#11; the order is the same every round.

**Planning and memory:** no plan or checklist (`prompts.py:154-168`: findings JSON + "start with the most severe");
a fresh conversation per room (`loop.py:349`) and a fresh `ToolContext` per round (`loop.py:402`), so rejections
are forgotten: 11 of 17 rejections of round 2 repeat round 1 exactly (real02 G2d: 108 of 177); the vision cache serves
the same findings again; `finish`'s open findings are thrown away (`loop.py:334`); the model re-sends an edit it has
just applied (605 after 604); no dry-run tool although `apply_edit` is pure (`edit_ops.py:627`); two edits per reply
without seeing the first result.

**Critic quality:** round 1: 238 code findings, 101 vision findings of which 72 dropped (60 duplicates of code
findings although the prompt says "do not repeat them", 12 contradicted by code). Of 24 kept critical/major vision
findings, 12 target unbuilt pieces (false). 18 edits followed vision findings: 17 rejected, the 1 accepted is the
wrong retype. The 3 critical "black render" findings got no `set_lighting` call.

| | real02 G2d | real03 run 3 |
|---|---|---|
| Rounds, stop | 4, max rounds | 2, time budget |
| Accepted / rejected | 20 / 177 (10 %) | 5 / 73 (6 %) |
| Model calls (critic, planner) | 312 (50, 262) | 144 (39, 105) |
| Rooms with a planner session | 11–12 of 33, same rooms every round | 12 of 35 |
| Rejected by the fixed-equipment lock | 68 (38 %) | 35 (48 %) |
| Exact repeats of an earlier rejection | 108 (61 %) | 11 |
| Agent minutes | 36 | 14.3 |

**Root causes, ranked**
1. Unfixable findings are sent as "fix these" and decide the room order (53 of 73 rejections, 8 of 12 sessions).
2. The model works blind on raw coordinates (tool outputs hide locks, build flags, allowed types and sizes, move
   allowance, free wall spans, fronts).
3. Throughput: 120 calls per round, calls one at a time, half of them reads, the same worst-first order every round.
4. Time budget: final stages over-estimated by 15 min plus a 20 min margin; 2 rounds in 14 min.
5. No memory, plan, self-check or dry run.
6. The model itself (Qwen3.8-27B-FP8) was picked in M11 on one planted-error test (bed found, sofa missed); it was
   never measured on planning quality. Whether a stronger model helps is a Step 1 question; the five causes above
   would hold back any model.

### 1.5 Ground and floor levels

No converted DXF of real02/real03 is in the repo and LibreDWG is not built in this session, so the drawings were
scanned for text with a small DWG string decompressor (scratchpad `levels_diag/dwg_strings.py`). It shows which texts
and attribute values a file holds, **not** whether they are in model space or on a visible layer (marked "scan").

**What the building JSON holds today** (real02 = `results/furniture/real02/building_final.json`)

| Field | Written at | real02 value |
|---|---|---|
| `project.datum` | `ingest/pipeline.py:1949` (from `sheets/heights.py:341-346`) | 43.00 (MTEXT 304D9, the section) |
| `levels[].elevation`, `elevation_source` | `sheets/to_building.py:62-65`; no section: `pipeline.py:334` (order × 3.00 m) | L-1 −3.00, L0 0.00, L1 3.15, all `section` |
| `levels[].ceiling_height`, `floor_to_floor` | `to_building.py:66-70` | 2.85 / 3.00 / 3.43; 3.00 / 3.15 / – |
| `slabs[].z_top`, `thickness` | `to_building.py:192` | −3.00, 0.00, 3.15; 0.15 |
| `site.ground.levels[]` (one z per side) | `to_building.py:497-543` | left 0.00, right 0.00 (section ground lines); note "also drawn: −3.15" |
| `site.ground.terrain`, `light_wells` | `to_building.py:543` | `flat`, `[]` (always) |
| `roof.eaves_height` / `ridge_height` | `to_building.py:275` | 3.65 / 6.79 |
| door `sill_height` | ingest | null: every door starts at its level's floor |
| conflict `level_mark_mismatch` | `heights.py:355` | the mark 40.00 points at −3.15 (geometry wins) |

**No field at all** for: a room's own floor level (sunken living room, raised entrance, wet-room step; schema
`building.schema.json:366-392`), a door's threshold vs the ground outside, spot heights, contours, road level, the
plinth (subasman) level. `elevation_source` allows `level_mark` and `elevation_drawing`, but no code writes them. The
per-level `level_mark` lives only in `sheets.json` (`heights.py:386-399`). real01 and real03 are single-region
projects: the sheets/heights step is skipped (`pipeline.py:2036`, `:2191`); their L0 sits at 0.0 with no datum, no
slabs and `site.ground: null`.

**Where level marks are read**

| Reader | file:line | Use |
|---|---|---|
| Section | `heights.py:177-181` → `units_check.py:224-279` | the mark at the ground-floor slab top becomes the datum; other marks are only compared with the slab lines (`heights.py:347-360`): a difference is a conflict, the geometry wins |
| Elevation drawing | `sheets/exterior.py:208-253` | drawing y → building z for facade bands only |
| Unit check | `units_check.py:281-304` | pairs of marks set the drawing unit |
| **Floor plans, site plans** | – | **never read**: `ingest/generic/labels.py:202-221` skips bare numbers; `site_of` (`exterior.py:394-460`) reads no heights |
| Block attributes (KOT, BDK, TZK, KOT-BINA, KOT-ARAZI) | – | never read |

The mark pattern `MARK_RE` (`units_check.py:60`) accepts `±0.00`, `+0.15`, `-0.45`, `43.00`, `KOT +3.00` and **rejects**
the common Turkish forms `+-0.00`, `+-0.00(dük)`, `KOT: +0.15`, `Ü.K. +0.15`, `T.Z. -0.45`, `±0.00 KOT`,
`SB. KOTU : 93.20`, `BİNA GİRİŞ KOTU : 93.20` (tested).

**How Blender places floors and ground**

| Item | Code | Today |
|---|---|---|
| Floors | `blender/shell.py:1631`, `:184-220` | every room of a level at `level.elevation`; doors from the level floor |
| Ground | `blender/site.py:126-203`, `:243-264`, `:1005-1011` | one z per side, blended at the corners; a side with no data takes the mean of the others; **no ground drawn → z 0 with a basement, else the lowest floor: the ground floor always sits exactly at grade**; flat to 1000 m |
| Basement | `site.py:206-240`, `:365-452`, `:972-993` | an outside door below ground lowers that side to the door's floor; a window below ground gets a 0.8 m light well, > 1 m below an inferred 3 m sunken court with a parapet |
| Entrance steps | `site.py:650-668`, `:721-740` | only doors 0.05–1.5 m above the ground get a landing and 0.17 m steps; **no ramps**; a door > 1.5 m up is ignored |
| Plinth | `blender/facade.py:33`, `:210-230` | a 0.45 m band painted at the wall foot; it never raises the floor |
| Slope, terraces, retaining walls | – | none (per-side levels only) |
| Single-region projects | `blender/build.py:545-548` (`is_whole_building`: slabs, roof or variants) | **no ground, site or exterior views at all**: real01 18 + 0 views, real03 83 + 0 (this is why real03 has no exterior, §19.8 open item) |

**Where the information is lost**
1. Drawing → ingest: marks on plans and site plans are never read; the pattern rejects the Turkish forms; a mark
   symbol on a plan can become furniture (real03 `f_L0_142`, below).
2. Section → `sheets.json`: a mark that is not at a slab top only makes a conflict; lower ground lines go into a
   note (`heights.py:419-426`); marks never set the ground.
3. `sheets.json` → building JSON: `level_fields` drops the per-level `level_mark` (`to_building.py:48-75`);
   single-region projects drop the whole heights and site step.
4. Building JSON → Blender: default ground ±0.00 (`site.py:1011`); doors > 1.5 m above ground ignored
   (`site.py:662`); the built light wells and courts exist only in the scene manifest, not in the building JSON.
5. Report: `report/m10.py:327`, `:422` print the ground z object as "-" (real02 `final_report.md:685`: "drawn ground
   levels: left -, right -" although the JSON has 0.00).

**Checks and agent tools:** X1 levels stacked (`exterior_checks.py:189-210`), X3 an entrance > 0.05 m above ground
without steps (only doors the site code counts as entrances, rise ≤ 1.5 m, `:303-311`), X4 ground/path/plot
(`:314-343`), X5 storey height 2.6–3.3 m, door and sill heights (`:346-384`). **Missing:** floors or ground against the
level marks; a door > 1.5 m above ground (into the air); a floor below the terrain without a basement (a door below
the drawn ground is only a warning, `site.py:403`). The agent can read level elevations and `site.ground`
(`agent/tools.py:357`, `:481-499`); `set_exterior` changes only roof, ground look, path, fence, trees, front court
and sun; `correct_geometry` only gaps, duplicate walls and off-wall openings (and is record-only, M11 §18.1). **No
tool sets a level elevation, ground z, slope, steps, ramp, plinth height or room floor offset.**

**Evidence**

| Project | Drawn | Built |
|---|---|---|
| real02 (`one_building.dwg`) | section: MTEXT marks `43.00` (datum) and `40.00`, ground lines ±0.00 and −3.15 on both sides; scan: 20 `KOT_PLN` block attributes, tag BDK "Bitmiş Döşeme Kotu" (finished floor; a TZK "Tabi Zemin Kotu" prompt too): 37.00, 40.00 ×5, 43.00 ×7, 44.00, 45.00, 46.00 ×5 – none reached `sheets.json` (the region text counts equal the 45 model-space MTEXTs, so they are probably in unused block definitions; to confirm on the converted DXF) | flat ground 0.00 on all four sides (front and back = "mean of the drawn sides"); ground floor at grade, both entrances (d_L0_011/012) rise 0.00, no steps: the doors sit flush on the grass (`ext_6`); the basement fully buried with 3 inferred 3 m sunken courts and parapets (white boxes in `ext_1`); the −3.15 line ignored (footing or lower garden: nothing decides) |
| real03 (`tekkat.dwg`) | scan: site note "D BLOK 1BK+ZK+12K / TESVİYE 0.00 KOTU : 93.20 / SB. KOTU : 93.20 / BİNA GİRİŞ KOTU : 93.20"; ≈ 280 level-mark attribute values (tags KOT, KOT2, KOT-BINA, KOT-ARAZI: +0.00, +3.20 … +44.80, −2.00, −4.00, 93.20); `+-0.00(dük)`, "Subasman Kotu:", "100.18(şev üst kotu)", a road-levels xref; on the plan a "+0.00 / 93.20" mark in the Rüzgarlık (`cam_r_L0_ruzgarlik_1_plan.jpg`) | the mark became furniture **`f_L0_142`** (unknown, 0.90 × 0.34 m, INSERT 7C9C9/48; pass 1 "circle with crosshairs", pass 2 "potted_plant"), built as a 0.8 m box; L0 at 0.00 with an assumed 2.70 m ceiling, no datum, no ground, no exterior; the unit check reports "level_marks: 0 samples" |
| real01 (PDF) | 47 words, no level marks | flat L0 at 0 (consistent), but no ground and no exterior |

**Root causes, ranked**
1. **Level marks on plans, site plans and in blocks are never read**, and the one pattern that reads them rejects the
   usual Turkish forms.
2. **The model has no place for them**: no per-room floor level, no door threshold vs ground, no spot heights or
   terrain; the ground is one z per side and defaults to ±0.00, so the ground floor always sits at grade.
3. **Single-region projects skip heights, site and exterior altogether** (real01, real03).
4. **Steps only for 0.05–1.5 m rises, no ramps; the plinth is paint**, not a raised floor.
5. **No check or agent tool for levels**: nothing compares the built floors and ground with the marks, nothing
   catches a door into the air or into the ground, and the agent cannot correct a level.

### 1.6 The library

**How it is built**

| Step | Code | What happens |
|---|---|---|
| Survey | `objaverse.py survey`, `abo.py survey`, `generate.py run` | Objaverse: category → type, face and file limits, textured; ABO: product type + English word rules; generated: Z-Image-Turbo picture → TRELLIS.2 model |
| Thumbnails | `objaverse.py thumbnails` (Blender) | 4 views at 256 px; unit guess ×1 / 0.01 / 0.0254 / 0.001 into the type's size range, else **scaled to the typical footprint**; ABO in metres, refused outside the range |
| Judging | Qwen3-VL-8B + GLM-4.6V-Flash, temperature 0, strict JSON | one 2×2 sheet on grey, **no scale reference**, size only as text, **no title**; accept if both say single object and matching type, both quality ≥ 4 (5 detailed … 2 crude), bed mattress agreed, fronts agree, a shared style |
| Accept | `objaverse.decide` / `accept` | ≤ 20 per type, 5 per (type, style) first, then filled up |
| Materials | `recolour.py` | material slots named by both judges (931 of 1032) |
| Catalogue | `write-catalog`, `catalog.load` | `catalog_library.json` + Poly Haven `catalog.json`; GLBs on the volume (sha256), not in git |

| Source | Models (furniture + decor) | Licence | Real units |
|---|---|---|---|
| ABO (Amazon products) | 538 (375 + 163) | CC BY 4.0 | yes (metres) |
| Objaverse (Sketchfab uploads) | 213 (98 + 115) | 193 CC BY, 2 CC0, **12 NC (7 NC + 5 NC-SA), 6 SA** (user OK in M8: any licence, flagged) | 111 by unit guess, 102 scaled to the typical footprint |
| Generated (TRELLIS.2) | 281 (196 + 85) | generated (TRELLIS.2-4B, MIT) | **none**: 97 at ×1 (TRELLIS outputs a unit cube), 184 scaled to the typical footprint |
| Poly Haven | 30 + 4 | CC0 | yes |

**Counts per type** (abo / objaverse / generated / polyhaven = total)

| Group | Types |
|---|---|
| Beds, seating | bed_single 7/2/11/0=20, bed_double 18/2/0/1=21, sofa 17/1/2/3=23, armchair 14/6/0/3=23, chair 13/6/0/3=22, sofa_corner 17/1/1/0=19, chaise 5/0/5/0=10, ottoman 14/6/0/0=20, bench 11/9/0/0=20, bar_stool 20/0/0/0=20, office_chair 20/0/0/0=20 |
| Tables | table_dining 18/2/0/3=23, table_coffee 15/5/0/3=23, desk 18/2/0/3=23, side_table 20=20, console_table 15/0/5/0=20 |
| Storage | wardrobe 10/6/4/0=20, tv_unit 20/0/0/2=22, bookshelf 13/7/0/3=23, nightstand 18/0/0/3=21, dresser 18/0/0/2=20, sideboard 20=20, shoe_cabinet 12/0/8/0=20, display_cabinet 1/0/7/0=8, tall_cabinet 9/0/8/0=17 |
| Kitchen, bath | fridge 0/5/14/0=19, stove 0/3/16/1=20, sink_kitchen 0/0/15/0=15, washbasin 0/8/12/0=20, toilet 0/8/11/0=19, shower 0/0/10/0=10, bathtub 0/1/19/0=20, washing_machine 0/0/20/0=20 |
| Other | floor_lamp 12/6/2/0=20, potted_plant 0/6/14/0=20, crib 0/2/6/0=8, bunk_bed 0/4/6/0=10 |
| Always parametric | kitchen_counter, kitchen_island, wall_cabinet, stair, unknown |
| Decor | cushion 20 ABO, rug 20 ABO, wall_art 17 ABO, vase 20 ABO, table_lamp 20 ABO, mirror 17 ABO; bowl 19 gen, plant_small 20 gen, plant_large 10 gen, blind 9 gen; curtain 13 obj + 7 gen, throw 10 obj + 7 gen, books 11 obj + 9 gen, candle 2 + 18 obj, basket 3 + 17 obj, tray 4 + 16 obj, clock 10 + 10 obj, sculpture 15 obj + 2 gen, pendant_light 15 + 5 obj, ceiling_light 15 + 2 gen; plant 0 own (uses potted_plant + 3 Poly Haven) |

- Generated share: furniture 196 of 699 (28 %), decor 85 of 367 (23 %). **100 % generated:** sink_kitchen, shower,
  washing_machine, bowl, plant_small, plant_large, blind. ≥ 50 %: bathtub 19/20, stove 16/20, fridge 14/19,
  washbasin 12/20, potted_plant 14/20, bed_single 11/20, display_cabinet, crib, bunk_bed, chaise.
- No `real_product` field: only ABO entries (brand, item id, metres) are known real products.

**Per style** (furniture / decor models tagged): modern minimal 479/215, modern 478/211, minimal 400/219, scandinavian
203/144, japandi 131/93, industrial 78/24, classic 67/41, rustic 56/18, neutral 29/120, **mediterranean 4/9**.
(Type, style) pairs with `neutral` counted as fitting every style: furniture 333 pairs, **68 empty**, 55 with 1–2
models, 36 generated-only (empty per style: mediterranean 21, rustic 15, japandi 11, industrial 8, classic 8,
scandinavian 5, modern/minimal 0; toilet, shower, bathtub, washing machine empty for ≥ 6 styles). Decor: 189 pairs,
10 empty, 19 thin, 36 generated-only.

A re-run of the fit on the committed buildings for every style shows how many pieces fall back to code-made boxes:

| Pieces that can take a model | modern | scandinavian | japandi | industrial | classic | rustic | mediterranean |
|---|---|---|---|---|---|---|---|
| real02 (196): parametric | 46 | 52 | 82 | 129 | 122 | 142 | 134 |
| real03 (114): parametric | 24 | 60 | 62 | 78 | 73 | 69 | 104 |

**Wrong objects that both judges accepted** (checked on the judge sheets where marked ✓)

| Model | Filed as | What it is | Used |
|---|---|---|---|
| abo_B01N6AQX0A | bed_double | inflatable air bed ("Luchtbed") ✓ | – |
| objaverse_6b46b33b… | throw | "JuiceMachine", a blue cloth blob ✓ | real02, real03 (4×) |
| objaverse_be9b0345… | throw | "Corpse", a sheet-covered body ✓ | – |
| objaverse_00392182… | throw | a terrain scan ✓ | – |
| objaverse_53409613… | floor_lamp | a low-poly table lamp stretched to 1.03–1.37 m ✓ | 12–13× |
| objaverse_1b256f6c… | desk | "3D Test" model with a drawer pulled out ✓ | 4× |
| 7 Objaverse benches; 3 floor lamps | bench; floor_lamp | park/street benches; street lamps, lampposts | – |
| 2 Objaverse dining tables | table_dining | "Dining Set", "A table, chairs & few cups" (chairs baked in) | – |
| Objaverse trays | tray | 2 ceiling lamps, a square sink, a cutting board, a "Low Poly Couch" | – |
| 7 of 9 ABO tall cabinets | tall_cabinet | wardrobes, display cabinets, a dressing table | – |
| 5 ABO "Bagley Sectional Component" | sofa | parts of a sectional | – |
| "Bench with Cloth" ×3, "Saoura Traditional bench" | throw | benches squashed to 5 cm | real02/real03 |

**Wrong sizes:** 10 models outside the repo's own size ranges; 114 whose height is wrong when scaled to the typical
footprint (40 by > 15 %; 52 of them generated). Worst: all 10 bunk beds face the long side (never fit, always
parametric); 19 generated bathtubs 1.24–1.53 m long and 0.80 m high (one built 0.89 m high in real03); generated
stoves built 0.54–0.63 m high; a pallet table as a 0.25 m coffee table; ABO "shoe cabinets" 1.79 m tall; a 2.60 m
wardrobe; generated decor with one fixed size (every bowl 0.35 × 0.35 m, every large plant 1.00 m). Fit pass rate
at the layout's default footprint: bathtub 0/20, bunk_bed 0/10, tall_cabinet 1/17, display_cabinet 1/8, stove 2/20,
bookshelf 3/23. ABO sizes are good: of 77 product titles with sizes in cm, all but one match the box within 15 %.

**What is checked today:** licence and credit fields, unique id, sha256, positive box, front axis one of 4, up +Z
(`catalog._validate_model`); footprint ±15 % and height inside the size range (`objaverse.fits_type`); faces, file size,
textures; front by geometry + both judges or ABO's documented front; beds need a mattress or a measured deck.
**Not checked:** title vs type (English-only filter words), indoor vs outdoor, real proportions of the 286 models
without real units, low-poly or crude models beyond one score on 256 px tiles (14 Objaverse titles say "low poly",
"stylized", "test"), decor contact surfaces, mesh faults (normals, loose parts, open drawers), duplicates (18 groups,
23 extra copies), orientation against the layout's size table.

**How a run picks models:** `fit.py` scales x, y to the footprint, z by their mean; refused if they differ by > 15 % or
the mean is outside 0.75–1.30; rank: generated last, real units first, real-size error in 5 % steps, judge quality,
aspect, source. Only the refit uses the style family (`fit.style_family_of`): a model must carry the family or
`neutral`; no fallback to a related style; else a parametric piece ("no model for style F"). Decor without a model
of the style becomes parametric or is not built.

### 1.7 Plain bugs found (not fixed: step 0 is report only)

| # | Bug | Where | Effect |
|---|---|---|---|
| B1 | `fit.quality_of` expects a number; the catalogue stores `quality` as a list `[q1, q2]` | `fit.py:221-226` | every model gets quality 3.0 (948 / 498 candidate records in real02 / real03): **the judges' quality never affects the choice** |
| B2 | all 281 generated entries carry `via: "Objaverse (allenai/objaverse, ODC-By 1.0)"` | `catalog_library.json` | wrong credit line |
| B3 | decor is not moved, turned or resized with its host when an agent edit is replayed | `agent/overrides.py`, `edit_ops.py:527`, `:582` | cushions and throws left in the air (§1.3) |
| B4 | resize keeps the rotation while swapping the proportions | `edit_ops` resize + F2 "either way" | beds turned 90° (real02 f_L0_007/008) |
| B5 | the top-down image and the critic id list include `build: false` pieces | `topdown.py:45`, `critic_vision.py:53` | false critical findings on pieces in no render |
| B6 | final-stage time estimate 15 min too long without polish | `scheduler.py:1750` (factor 1.6) | the agent stops after 2 rounds, the pod ends 30 min early |
| B7 | throws squashed to 0.05 m whatever the model; bed pillows stretched to 0.6 m tall | `fit.py:606-644`, `decor_ai.py:1168-1190` | slabs and towers instead of throws and pillows |
| B8 | `loop.py:10` docstring says 40 calls per round, the code 120 | `loop.py` | doc only |
| B9 | the report prints the ground z object as "-" | `report/m10.py:327`, `:422` | "drawn ground levels: left -, right -" in real02's report |
| B10 | `MARK_RE` rejects `+-0.00`, `KOT:`, `Ü.K.`, `T.Z.`, `SB. KOTU :` | `units_check.py:60` | real03: 0 level marks read |
| B11 | level-mark and room-number symbols are typed as furniture | `infer.py`, recognition | real03 f_L0_142 (a KOT mark), 5 room-number circles as lamps and boxes |

### 1.8 What this means for the design

- **Levels are a reading problem first.** The drawings hold the marks (real03 ≈ 280 KOT attributes and a site note
  with 93.20 m); the pipeline reads none of them on plans. Read them, give the building JSON a place for them (room
  floor levels, door thresholds, ground points), then build steps, ramps, plinth and terrain from them and check them.
- **Read before you place.** Most of the visible chaos in real03 starts at ingest: drawn pieces not typed, misread
  sizes, symbols and labels built as furniture, whole furnished areas lost in unbuilt clusters. A group-based solver
  cannot fix a room whose drawn sofa, table and counter run are invisible to it.
- **Groups everywhere, not as an agent tool.** Layout, completion, the checks and the agent must all speak in groups
  (anchor + partners + relative rules), and the checks must judge arrangements, not counts.
- **Decor from the built mesh.** Soft decor needs the real support surface and the real back/headboard of the built
  model, and must follow its host after every edit; a contact check with a tolerance must fail the build.
- **The agent must see what it may change** (locks, allowed edits, free space, fronts), get a dry-run tool, keep
  memory across rounds, skip findings no tool can fix, cover every room in a budget, and work on groups.
- **The library needs a real audit** (title, scale reference, real size, crude/low-poly, contact surfaces, licence)
  before more items are added; the gaps are biggest for kitchen and bath fixtures and for non-modern styles.
