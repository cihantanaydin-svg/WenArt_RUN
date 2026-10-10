# Milestone 12 – ground levels, furniture overhaul, a smarter pod AI, library audit

Goal (user, 10 Oct 2026, prompt in `docs/prompts/milestone12.md`): the pipeline reads whole floors (real02, real03),
but the results are not good enough to show anyone. Five problems: (1) ground and floor levels, (2) furniture
placement, (3) decor and soft furnishings that float or cut through their host, and crude furniture, (4) the AI in
the pod reaches few rooms and most of its edits are rejected, (5) the library has unrealistic items, wrong sizes
and wrong categories.

Session: cloud (`CLAUDE_CODE_REMOTE=true`), branch `opus_branch_06`, 10 Oct 2026. Step 0 is CPU only (no pod).

Status: **approved by the user on 10 Oct 2026 (D1–D24 yes, D3a 0.15 m yes, D16 bake-off with Qwen3.8-Flash-Next on 2
GPUs and 2-GPU full runs if it wins yes, GPU plan OK incl. `--over-5-ok` for P1 and 2-GPU pods, `CLAUDE.md` wording
1–5 OK and applied)**; build in progress (step 2, contracts §13).

User answers to the step-0 questions (10 Oct 2026): (1) misread fixed equipment: the AI may set a real product size
and move it up to 0.5 m, logged with evidence – **yes**; (2) real03 exterior: **ground floor only** (no inferred upper
floors); (3) the 18 non-commercial / share-alike Objaverse models: **remove**.

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

## 2. Design overview (step 1)

Four ideas carry the whole milestone:

1. **Read first.** Level marks, furniture symbols and non-furniture symbols are read completely and given a place
   in the building JSON, with evidence. Nothing unexplained is built (no white box, no level mark as a plant).
2. **Groups, not pieces.** A room's program is a list of functional groups. A deterministic solver places whole
   groups and returns ranked candidates; the vision model only chooses the program options and between candidates.
   Layout, completion, the checks, the agent's tools and the tests all speak in groups.
3. **Measure the built scene.** Decor rests on the real surface of the built host mesh; a scene check measures every
   piece and decor item (floor contact, gap, overlap, front, real size) and fails the build when something floats or
   cuts through.
4. **An agent that sees what it may do.** The agent gets a structured room brief (locks, allowed edits, free wall
   spans, group status, fixable findings only), group-level tools, a dry-run tool, a plan per room, memory across
   rounds, parallel room sessions and a correct time budget. A stronger model is chosen by a bake-off on our own tasks.

The library is audited before it is grown, and only audited models are used.

```
drawings ─► ingest: walls, openings, rooms, LEVEL MARKS (§3), FURNITURE + NON-FURNITURE SYMBOLS (§4.1)
        ─► building JSON (levels, room floor offsets, door thresholds, ground points, terrain, entrances)
        ─► program per room (§4.3) ─► group solver: top-3 candidates (§4.4) ─► VLM picks (§4.5)
        ─► fit: audited library only (§4.8, §6) ─► decor in host frame (§4.7)
        ─► Blender: terrain, steps, plinth (§3.4); decor ray-cast / shrinkwrap on the built mesh (§4.7)
        ─► scene checks S1–S6 (§4.6) + group checks G1–G14 + level checks L1–L7 ─► agent rounds (§5) ─► final
```

## 3. A – Ground and levels

### 3.1 D1 – Read every level mark

| Option | What | Verdict |
|---|---|---|
| a | today: only marks on sections, strict pattern | no: real03 has ≈ 280 marks and 0 are read |
| **b** | **text + block attributes + mark symbols on every drawing (plans, sections, site plans, elevations), one reader** | **pick** |
| c | b + the vision model reads marks on scans and photos | later (scans): advisory, trust level 3, two passes (no code check exists) |

- **Text:** one tolerant pattern family (`wenart/ingest/generic/levels.py`, new) for the Turkish and English forms:
  `±0.00`, `+-0.00`, `+-0.00(dük)`, `+0.15`, `-0.45`, `KOT +3.00`, `KOT: +0.15`, `Ü.K.` / `ÜK` (upper level of a
  slab), `S.K.` / `SK`, `T.Z.` / `TABİİ ZEMİN` (natural ground), `TESVİYE` (finished grade), `SB.` / `SUBASMAN`
  (plinth), `BİNA GİRİŞ KOTU` (entrance), `ŞEV ÜST KOTU` (top of a slope), `±0.00 = 93.20` (relative = absolute), a
  value with 2–3 decimals. Each match gives `value`, `relative | absolute`, a `kind` from its keyword, and the raw text.
- **Block attributes:** every INSERT attribute whose tag is in a tag table (`KOT`, `KOT2`, `KOT-BINA`, `KOT-ARAZI`,
  `BDK` "bitmiş döşeme", `TZK` "tabii zemin", `SBK`, `ELEV`, `LEVEL`) or whose value matches the pattern. The block's
  insertion point (or the symbol's apex, `units_check.MARK_REACH`) is the mark's point.
- **Mark symbols:** a triangle or arrow with a leader next to a matching text gives the point it marks (exists for
  sections; extended to plans).
- **Kind of a mark** (one rule table, evidence in every record): inside a room's polygon on a plan → that room's
  finished floor; outside the building outline on a plan or site plan → ground (natural or finished grade by its
  keyword); at a door → threshold / landing; on a section → slab top or ground line (as today); `SB.` → plinth;
  `GİRİŞ` → entrance floor. Unknown → `unknown`, listed.
- **Absolute and relative:** `±0.00 = 93.20` or a site note `TESVİYE 0.00 KOTU : 93.20` sets the datum; absolute
  marks are converted with it. Two datums that disagree → conflict (DWG > vector PDF > scan, CLAUDE.md).
- **Never furniture:** an INSERT read as a level mark, a room-number circle (a circle with one short text inside),
  a north arrow, a section mark or an axis bubble is recorded in `symbols[]` with its kind and evidence and is never
  a furniture candidate (fixes real03 `f_L0_142` and the 5 room-number circles, bug B11).
- Fixes B10 (pattern) and B9 (report).

### 3.2 D2 – A place for levels in the building JSON

| New field | Content |
|---|---|
| `level_marks[]` | id, value, relative/absolute, kind, point (building XY), level id, room id or outside side, drawing (file, layout, entity or text id), method `vector`/`ocr`/`ai`, confidence, `used_for` |
| `project.datum` (exists) | + `absolute_m` (e.g. 93.20), `source` |
| `rooms[].floor_offset_m` | the room's finished floor above its level's elevation (default 0; from marks inside the room; a sunken living room −0.30, a raised entrance +0.15); `evidence`, `inferred` |
| `openings[].threshold_z` | building z of a door's threshold (from the rooms on both sides; an outside door from its room) |
| `site.ground.points[]` | x, y, z with evidence (marks outside the outline, section ground lines placed at their cut position on the plan) |
| `site.terrain` | `kind: flat | planar | tin`, the points used, fitted slope, residual, `inferred` |
| `site.entrances[]` | door id, threshold z, ground z in front, rise, `solution: none | steps | ramp | steps_and_ramp`, steps (n, riser, tread), landing (w × d), ramp (length, slope), `drawn | inferred`, evidence |
| `site.plinth` | height above the ground along each side (from `SB.` marks, else threshold − ground), `inferred` |
| `levels[].elevation_source` | the values `level_mark` and `elevation_drawing` are now written |

The schema (`wenart/schema/building.schema.json`) and the validator get these fields; old buildings stay valid (all
optional).

### 3.3 D3 – Infer what the documents leave out (CLAUDE.md evidence rules)

| Missing | Rule (every result `inferred: true`, listed in the report) |
|---|---|
| Ground at an outside door | the nearest ground point within 5 m of the door, else the terrain model, else the side's section ground line, else the default below |
| **Nothing about the ground at all** | **D3a: the ground floor stands 0.15 m above the ground (one step, inferred)** – options: 0.00 (today: always flush, which reads wrong), 0.15 (pick: the usual minimum rise to keep water out), 0.45 (the facade plinth band of today) |
| Terrain | ≥ 3 ground points → plane fit (residual ≤ 0.10 m) else a triangulated surface (TIN) over the plot; 1–2 points or section lines → per-side levels (today's model); none → flat. Beyond the plot it blends to flat over 20 m |
| Steps at a door | rise ≤ 0.05 m → a flush threshold; rise > 0.05 m → steps: n = ceil(rise / 0.15), riser = rise / n (≤ 0.15 m outdoors), tread 0.30 m, 2·riser + tread ≈ 0.60 m; a landing of door width + 0.6 m × 1.2 m in front of the door; > 12 risers → an intermediate landing (values: secondary sources on TS 9111, flagged in §3.7) |
| Ramp | only when drawn (`RAMPA`, a slope arrow with %) or when the brief asks for an accessible entrance; slope by rise: ≤ 0.15 m 1:12 (8 %), 0.16–0.50 m 1:14 (7 %), 0.51–1.00 m 1:16 (6 %), > 1.00 m 1:20 (5 %) (secondary source on TS 9111, flagged); handrails on both sides above 0.15 m |
| Plinth | `SB.` mark, else threshold − ground; the facade plinth band (`facade.py`) follows this height (min 0.15 m) instead of the fixed 0.45 m paint band |
| A door > 1.5 m above the ground | no longer ignored: finding L2 (door into the air); a balcony or terrace door is fine; else the agent decides (outside stair, or the door is not an entrance) |
| A floor below the terrain | basement if the level is a basement (title, `BODRUM`, negative elevation with walls): light wells / courts as today, now written into the building JSON; else finding L3 |
| A room's floor | the level's elevation unless a mark inside says otherwise; wet rooms keep the level floor (no assumed drop) |

### 3.4 D4 – Build it in Blender

- **Terrain** (`blender/site.py`): the TIN or plane as a ground mesh with the plot, paths and paving draped on it;
  retaining edges where the terrain drops > 0.5 m at the plot boundary; flat beyond.
- **Entrances:** steps (riser/tread from §3.3), landing, cheek walls, handrails above 0.45 m (our assumption, flagged); a ramp with handrails
  when inferred or drawn. All built objects carry the entrance id (object-index pass, checks).
- **Plinth:** the facade plinth is a real raised base from ground to floor, not a paint band.
- **Room floor offsets:** the shell builds a room's floor at its offset; a step (or flight) at each inner door
  between rooms with different floors; the door frames start at the threshold.
- **Single-region projects (U2):** a single drawn floor is built as a ground floor with its site, terrain and
  entrances, unless its title marks it as an upper floor (`1. KAT`, `NORMAL KAT`, `FIRST FLOOR` …). The building
  ends at that floor: a flat roof slab with a parapet (`roof.kind: flat_cut`, `inferred`, note "upper floors not
  drawn") – real03 as you decided; real01 (one level, a house) gets its site too. Exterior cameras for such a
  building: eye level, the entrances and the ground floor; no aerial view.

### 3.5 D5 – Checks L1–L7 (code, in the critic, the validator and the tests)

| Check | Rule | Severity |
|---|---|---|
| L1 | every outside door: top of steps / landing / ground in front = threshold ± 0.02 m | critical (door into the air / into the ground) |
| L2 | a door > 0.05 m above the ground in front with no steps or ramp (all rises, not only 0.05–1.5 m) | critical |
| L3 | a level floor below the terrain at the outline (> 0.05 m) that is not a basement, or a basement window below ground without a light well or court | critical |
| L4 | built floors and ground vs every vector mark: within 0.02 m, else a finding naming the mark (the conflict is listed) | major |
| L5 | steps: outdoor riser 0.10–0.15 m, indoor ≤ 0.18 m, tread ≥ 0.28 m, 0.58 ≤ 2R + T ≤ 0.66 m; ramps within the slope table | major |
| L6 | terrain slope ≤ 1:3 without a retaining edge; no terrain above a window sill without a light well | major |
| L7 | every entrance is seen in ≥ 1 exterior view, and its steps or ramp are in that view's object-index pass | minor |

### 3.6 D6 – Agent tools for levels

Read: `levels` (marks with their kind and use, level and room floors, door thresholds, ground points, terrain,
entrances, conflicts, L-findings). Edit (validated by L1–L7, logged, labelled `corrected_by_ai` or `inferred`):
`set_mark_kind(mark_id, kind, reason)`, `set_room_floor(room_id, offset_m, evidence)` (only from a mark or a drawn
step line), `set_ground_point(x, y, z, evidence)`, `set_entrance(door_id, solution, reason)`, `set_terrain(kind)`.
Geometry from the drawings stays the anchor: a mark wins over the agent unless it is a clear error (CLAUDE.md).

### 3.7 Flags

The step and ramp numbers come from secondary sources quoting TS 9111 (Ankara University course notes; a newspaper
column; a MEB document); the Turkish regulation text (`mevzuat.gov.tr`) and the standard were blocked or paywalled
here. They are defaults in `wenart/defaults.yaml` (`levels:`), flagged in the report, and the brief can change them.
Sources: https://acikders.ankara.edu.tr/mod/resource/view.php?id=6217, https://www.posta.com.tr/yazarlar/tamer-heper/engelli-rampasi-kurallari-2917690,
https://efeler.meb.gov.tr/meb_iys_dosyalar/2018_10/24145413_ERYYEBYLYRLYK_WORD.docx.

## 4. B – Furniture overhaul

### 4.1 D7 – Read the drawn furniture completely (before any layout)

| Step | Rule |
|---|---|
| Non-furniture symbols | level marks, room-number circles, north arrows, axis bubbles, section marks, door-swing arcs (an arc whose centre is a door jamb), dimension outlines, text frames → `symbols[]` with kind and evidence (plan crop); never built, never furniture (CLAUDE.md: "removed only when clearly not furniture, logged with the plan crop") |
| Block names | a TR/EN dictionary (`KANEPE`, `KOLTUK`, `BERJER`, `YATAK`, `KOMODİN`, `GARDIROP`, `DOLAP`, `MASA`, `SANDALYE`, `SEHPA`, `TV`, `LAVABO`, `KLOZET`, `WC`, `DUŞ`, `KÜVET`, `EVYE`, `OCAK`, `FIRIN`, `BUZDOLABI`, `ÇAMAŞIR`, `BULAŞIK` …) on the block name and its nested block names |
| Clusters | an unbuilt cluster is split by block instance, then by connected stroke groups; each part is typed on its own (real03: 6 clusters over 92–100 % of their rooms) |
| Context typing | rules before any AI: chairs around a rectangle → dining table + chairs; two 0.4–0.6 m squares at a bed's head → nightstands; a 0.55–0.65 m deep strip along a wall holding a sink or hob symbol → a counter run with that fixture; a square in front of a sofa → coffee table; a long low strip facing a sofa → TV unit |
| Vision typing | what is left: the strongest model (§5.1) gets the plan crop with the piece outlined, its neighbours and room, and picks one of the size-fitting candidates or `not_furniture` (temperature 0; a second pass only where no code check confirms it, CLAUDE.md) |
| Never a box | a piece still untyped is **not built**, listed with its crop under "needs review" in the report; no grey box in any image (fixes the 42 + 32 white boxes) |
| Misread fixed equipment (U1) | a fixed piece whose drawn size is outside its type's real range by > 30 % (the 1.145 × 0.356 m toilets) gets the nearest real product size; a fixed piece through a wall or in a door swing may move ≤ 0.5 m to the nearest valid spot; `adjusted_by_ai` with `drawn_*` kept, reason and crop |
| Open kitchens | a living room holding kitchen symbols gets a kitchen zone; the room-type rules apply per zone (a living room may hold a kitchen run in its kitchen zone) |

### 4.2 D8 – Groups as data

One YAML file `wenart/furniture/groups.yaml` replaces the five hard-coded templates in `groups.py`. Per group:
anchor type(s), required and optional partners with their position in the anchor's frame (offset ranges, side,
distance to the anchor's front or side), facing (to the anchor, to a focal point, parallel), use zones (where a person
stands or sits), wall rules (back to wall, foot free), clearances, walkways, size variants by room size, and the
source of each number (§4.6).

| Group | Anchor | Partners (required / optional) | Key rules |
|---|---|---|---|
| seating | sofa or corner sofa | TV unit opposite on the sofa's axis / coffee table, 1–2 armchairs, side table, floor lamp, rug | TV ≥ 1.5 m from the sofa front (score: 1.2–1.6 × the screen diagonal), facing it (± 10°); coffee table ≥ 0.30 m (score 0.35–0.45 m) from the sofa front, inside the sofa–TV corridor; armchairs face the coffee table; TV not in front of a window |
| dining | dining table | chairs by table size, evenly around / sideboard, pendant | ≥ 0.81 m behind every chair to a wall or piece (score 0.91 m, 1.12 m where people walk past); chairs face the table |
| sleeping (double) | double bed | 2 nightstands, one per side at the headboard / bench at the foot, rug, wardrobe in the room | headboard on a wall; ≥ 0.60 m free along both long sides and at the foot (score 0.75 m); a nightstand only where its side is free |
| sleeping (single) | single bed | 1 nightstand / desk group | one long side may touch a wall |
| storage | wardrobe | – | back to a wall, ≥ 0.80 m free in front (doors; flagged assumption) |
| work | desk | office chair / bookshelf, lamp | chair in front, ≥ 0.80 m behind the desk front (flagged assumption); daylight from the side preferred |
| kitchen run | counter run (I, L, U, galley) + island | sink, hob, fridge / dishwasher, wall cabinets | order fridge – sink – hob along the run; landing beside the sink ≥ 0.46 m, the hob ≥ 0.30 m, the fridge ≥ 0.38 m on its handle side (§4.9); hob not under a window or beside a tall unit; work triangle legs 1.2–2.7 m, total ≤ 7.9 m; aisle ≥ 0.90 m; sink preferably under a window |
| bathroom set | – | toilet, washbasin, shower or bathtub / washing machine, mirror | ≥ 0.53 m clear in front of the toilet, washbasin and tub (score 0.76 m); toilet centre ≥ 0.38 m from a side wall; shower/bath entry free; the door swing hits nothing |
| entrance | – | shoe cabinet / console, mirror | main walkway ≥ 0.80 m kept |
| children | single bed | desk group, wardrobe / toy storage | as the parts |
| balcony | – | small table + 2 chairs | railing side free |

### 4.3 D9 – Program per room

A rule table turns room type, area, shape, doors, windows, the brief and the drawn anchors into a list of groups
with options (e.g. living 18 m²: seating `{sofa + 2 armchairs | corner sofa}`, dining `{4 | 6}` if the room has
no separate dining room; bedroom 12 m²: double sleeping + storage; < 9 m²: single + work). Drawn pieces are matched
to groups first (a drawn sofa is the seating anchor; a drawn table with chairs is the dining group). A group whose
anchor is drawn is **completed**: only its missing partners are added (`added_by_ai`, `completes_room: true`), never
a second anchor (CLAUDE.md). Rooms with no drawn furniture get the full program in the project style.

### 4.4 D10 – A deterministic group solver

| Option | What | Verdict |
|---|---|---|
| a | today: VLM coordinates for single pieces + per-piece repair | no (§1.2) |
| b | learned layout models (ATISS, DiffuScene, …) | no: trained on 3D-FRONT (non-commercial) |
| c | LLM writes constraints, a solver places (Holodeck, LayoutVLM style) | the constraint idea yes; the LLM writing them no (non-deterministic, our groups are known) |
| **d** | **our group templates + a deterministic candidate search with hard checks and scored soft terms (cost terms after Merrell et al. 2011 / Yu et al. 2011, constraint style after Holodeck / Infinigen); the VLM chooses between the top 3** | **pick** |

How it works (`wenart/furniture/solver.py`, new; pure Python, numpy + shapely):
1. **Free space.** Room polygon minus drawn locked pieces, door swings, window bands (for pieces taller than the
   sill), radiators and the kitchen zone where it does not belong; a 5 cm occupancy raster for walkways.
2. **Anchor candidates.** For back-to-wall groups every free wall span is sampled every 0.10 m with the group's size
   variants (both directions along the span); free-standing anchors (dining table, island) on a 0.10 m grid in the
   largest free area, rotated to the room's axes.
3. **Partners.** Each anchor candidate instantiates its partners at the template positions (small search over the
   allowed offsets and sides); a partner that does not fit is dropped only if optional.
4. **Hard checks** on every group candidate: inside, no overlap, door swings free, windows free for tall pieces, use
   zones free, wall contact where the template says so, and **walkway connectivity**: on the raster (distance
   transform) every door reaches every other door and every use zone with ≥ 0.60 m (0.80 m for the main path from
   the entrance door).
5. **Soft score** (weights in `groups.yaml`, logged per candidate): wall use, sight lines (sofa → TV, bed → door
   seen from the bed head, desk with side light), circulation length and no path through a seating group, daylight
   for desk and dining, distance between groups that belong together (dining near the kitchen zone), balance of the
   free area, distance from the drawn position for completed groups.
6. **Search:** groups in priority order (drawn anchors first, then by area); a beam search (width 32) over the
   groups' candidates; deterministic tie-breaks (score, then position, then id); returns the **top 3 full layouts**
   with their score breakdown and a top-down image each.

Reuse (§4.9): ideas and published cost terms; our own code (shapely, no Unity, no Blender 4.2 pin).

### 4.5 D11 – What the vision model decides

Only three things, each validated by code: (1) the program options of §4.3 (from the allowed list), (2) style
details (materials, colours: as today), (3) **which of the 3 candidates** (top-down images with labels, the plan crop and the
scores), with a reason. Temperature 0, strict JSON; a failed or invalid answer takes
candidate 1. It never gives coordinates.

### 4.6 D12 – Group checks G1–G14, scene checks S1–S6

Group checks replace the counting of F5 and run in the solver, the code critic, the edit validator and the tests
(one function per check, `wenart/furniture/group_checks.py`):

| Check | Rule (minimums; sources and recommended values in §4.9) |
|---|---|
| G1 | TV unit opposite the sofa: on the sofa's axis (± 0.3 m), facing it (± 10°), ≥ 1.5 m away |
| G2 | coffee table between sofa and TV, ≥ 0.30 m from the sofa front |
| G3 | armchairs face the coffee table or the sofa (± 30°), ≤ 2.5 m from it |
| G4 | one nightstand per free side of the bed head, touching the bed side ± 0.10 m, its front in the bed's direction |
| G5 | bed: headboard on a wall; ≥ 0.60 m free along each free long side and at the foot |
| G6 | dining: chairs = seats of the table size, evenly spread, each facing the table, ≥ 0.81 m pull-out behind each |
| G7 | desk + chair in front; ≥ 0.80 m behind the desk front |
| G8 | kitchen order fridge – sink – hob along the run; landings sink 0.46, hob 0.30, fridge 0.38 m; hob not under a window; triangle legs 1.2–2.7 m, sum ≤ 7.9 m; aisle ≥ 0.90 m |
| G9 | kitchen completeness: a sink, a hob, a fridge in every kitchen (zone) |
| G10 | bathroom completeness: toilet + washbasin (+ shower or bath in a bathroom); ≥ 0.53 m clear in front of each fixture; toilet centre ≥ 0.38 m from a side wall |
| G11 | walkways: every door reaches every door and every use zone with ≥ 0.60 m (main path from the entrance ≥ 0.80 m) |
| G12 | windows: no piece taller than the sill + 0.05 m within 0.30 m in front of a window |
| G13 | wardrobe and other door-fronted storage: ≥ 0.80 m free in front |
| G14 | no piece of a type its room (zone) never holds (F1 per zone) |

Scene checks (Blender, after the build; `checks/scene.json`; findings routed to the stage that caused them):

| Check | Rule | Tolerance |
|---|---|---|
| S1 | every floor piece stands on its floor: lowest vertex z − floor z | −0.005 to +0.010 m |
| S2 | no piece cuts a wall or another piece (BVH overlap of evaluated meshes; wall-hung types against their wall excepted) | ≤ 0.010 m depth |
| S3 | the built front direction = the planned front | ≤ 10° |
| S4 | the built size = a real size of its type (size table) | ± 15 % per axis, height included |
| S5 | decor rests on its host (§4.7) | §4.7 |
| S6 | every built piece is a typed, audited model or a by-design parametric type (counter, wall cabinet, stair) | no exception |

### 4.7 D13 – Decor and soft furnishings rest on their host

| Option | What | Verdict |
|---|---|---|
| a | today: a type-table height and the drawn footprint | no (§1.3) |
| b | **ray casts on the built, scaled host mesh (Blender `BVHTree` of the evaluated object)** | **pick** for every decor item |
| c | shrinkwrap a cloth mesh onto the host (deterministic modifier) | **pick** for throws and duvets |
| d | rigid-body settle (≈ 20 frames, fixed substeps, deterministic for the same scene) | option for cushions if b looks stiff; measured on the pod |
| e | cloth simulation | no: slow, not repeatable enough at our budget |

- **Host frame.** Decor is stored in its host's frame (`host_id`, support `seat | mattress | back | headboard | top
  | shelf_k | floor | wall`, u/v in the support's area, lean angle) instead of world x/y. Every edit of the host
  (move, turn, resize, swap) moves its decor with it (fixes B3); the world position is computed in Blender only.
- **Support surface.** A 3 × 3 grid of downward rays under the item's footprint onto the host mesh; the rest height
  is the highest hit for hard items, the median for soft ones. No type-table height is used any more.
- **Cushions.** A horizontal ray from the seat front towards the back at the cushion's centre height finds the real
  backrest; the cushion's back touches it, leaning 10–15°, its bottom on the seat surface. A sofa or bed model whose
  audit says it already has cushions or pillows gets fewer or none (no duplicates).
- **Pillows.** Against the headboard (or the wall), on the mattress top (ray), not on top of the model's own pillows.
- **Throws and duvets.** Procedural textiles (§6.4): our own cloth mesh (folds modelled once) shrinkwrapped onto
  the bed or sofa top with a 5 mm offset, any CC0 fabric in the style colours; never a library object squashed to 5 cm (fixes B7). Every bed whose model has no bedding gets a duvet and
  two pillows this way (fixes the bare mattresses).
- **Objects on shelves, tables and counters:** ray casts as today (they work); shelves get one ray grid per shelf
  board (the board's real height from the mesh).
- **Plants:** on the floor or a top by rays; rugs on the floor (≤ 0.03 m thick, as today).
- **Check S5** for every decor item, from the evaluated meshes: **gap** (item bottom to the support surface below,
  over the 3 × 3 grid) ≤ 0.010 m; **penetration** (depth of the item's sample points inside the host, ray parity)
  ≤ 0.010 m on hard hosts and ≤ 0.030 m on soft hosts (mattress, seat cushion: they would compress); at least 80 %
  of the item's footprint over its support. An item that fails is placed once more (next free spot on the support);
  if it fails again it is **not built** and logged (`decor_not_rested`, with the measured gap or depth). A build
  with a built item that fails S5 fails (it cannot pass by construction; the check guards against bugs).
- CPU tests use a pure-Python mesh ray caster on the same meshes (as `camsearch.py` does for cameras).

### 4.8 D14 – Realistic furniture only

- The fit uses **only models with audit status `keep`** (§6); `fix` models after their fix; `remove` never.
- Style: a family fallback chain (e.g. mediterranean → rustic → classic → neutral; industrial → modern →
  neutral) with recolour by material slots; the choice is logged as `style_fallback`. A type with no audited model
  in any style → a **library gap** finding (§6.4) and the piece is built from the nearest audited model of a related
  type only if its group needs it (a lounge chair for a missing armchair); never a parametric sofa, bed or table.
- Parametric pieces only for the by-design types (kitchen counters and islands, wall cabinets, stairs).
- Fix B1 (`quality_of`): the judges' quality ranks the candidates again; generated models stay last.
- Real proportions: non-uniform fit scale ≤ 10 % (was 15 %), mean scale 0.85–1.20 (was 0.75–1.30); outside →
  the next model; the size table becomes the audit's real-size table (§6).

### 4.9 D15 – What we reuse from open-source layout work (checked 10 Oct 2026)

Licences read from each repository's LICENSE file (raw.githubusercontent.com); papers through their project pages
and Hugging Face paper pages (arxiv.org is blocked here).

| Work | Code licence | Needs | What it is | Verdict |
|---|---|---|---|---|
| Holodeck (CVPR 2024), `allenai/Holodeck` | Apache-2.0 | Objaverse assets, GPT-4o; optional MILP path uses Gurobi (commercial) | LLM writes per-object constraints; grid DFS solver `DFS_Solver_Floor` (shapely) with edge/middle, near/far, in front of / side of, centre-aligned, face-to | **reuse the constraint vocabulary and the solver structure**; not a dependency (the module imports langchain/OpenAI at the top, unseeded `random.shuffle`, 30 s wall-clock stop); any copied code keeps the Apache notice |
| Infinigen Indoors (CVPR 2024), `princeton-vl/infinigen` | BSD-3 | procedural assets; pins `bpy==4.2.0`, Python 3.11 | constraint language: hard constraints separate from score terms (`accessibility_cost`, `focus_score`, `angle_alignment_cost`, `StableAgainst`); simulated annealing | **ideas**: hard vs soft split, the accessibility frustum, focus score, "against a wall = slide along it"; cannot run in our Blender 5.2 |
| ProcTHOR (NeurIPS 2022), `allenai/procthor` | Apache-2.0 | AI2-THOR (Unity) | rule-based houses; "asset groups" as JSON trees (`television-sofa`, `chair-diningtable-4`, `desk-with-chair`) with relative anchors, offsets, randomness, `corner/edge/middle`, room weights | **reuse the group JSON idea** for `groups.yaml` |
| FlairGPT (Eurographics 2025) | no LICENSE (all rights reserved) | OpenAI | LLM picks from a fixed constraint library; scipy SLSQP + shapely solve | **idea only**: its function library is our checklist of score terms (next_to_wall, accessible, under_window, facing, between, surround, aligned, balanced) |
| LayoutVLM (CVPR 2025), I-Design (ECCV-W 2024), AnyHome (ECCV 2024) | no LICENSE | OpenAI, Objaverse | VLM + differentiable relations / scene graphs | idea only |
| HSM / SceneMotifCoder (3DV 2026 / 2025) | MIT | HSSD (non-commercial) | "scene motifs" (groups) as programs | idea (groups as programs) |
| SceneWeaver (NeurIPS 2025) | BSD-3 | some tools on 3D-FUTURE | reason–act–reflect agent | idea for the agent loop |
| Co-Layout (AAAI 2026) | repo unverified | – | grid integer programming for corridor connectivity | idea for G11 |
| ATISS, DiffuScene, InstructScene, LayoutGPT weights, PhyScene, ReSpace, LLplace, SceneTeller | non-commercial licences or 3D-FRONT data | – | learned layouts | **not usable** |
| Merrell et al. 2011 (SIGGRAPH), Yu et al. 2011 "Make It Home" | papers | – | cost terms: clearance, circulation, pairwise relations, conversation distance, alignment, balance; accessibility, visibility, door-to-door path | **our score-term names and starting weights** |

Pick: our own deterministic solver (§4.4) in `wenart/furniture/solver.py` with the Holodeck constraint words, the
Infinigen hard/soft split and the ProcTHOR group format; fixed order and a node budget (no wall clock, no random).

**Default numbers and their sources** (US/UK guidelines; no Turkish furniture-clearance standard was found; the
**minimums are hard checks, the recommended values are score terms**, so small Turkish rooms still get a layout):

| Rule | Minimum (hard) | Recommended (score) | Source |
|---|---|---|---|
| Kitchen work triangle | legs 1.2–2.7 m, sum ≤ 7.9 m | – | NKBA Kitchen Planning Guidelines (media.nkba.org/uploads/2022/05/Kitchen-Planning-Guidelines.pdf), snippet |
| Landing beside the sink | 0.46 m one side | 0.61 + 0.46 m | NKBA, snippet |
| Landing beside the hob | 0.30 m one side | 0.30 + 0.38 m | NKBA, snippet |
| Landing beside the fridge | 0.38 m on the handle side | – | NKBA, snippet |
| Kitchen work aisle | 0.90 m (our minimum for small flats) | 1.07 m (one cook) | NKBA, snippet; our minimum flagged |
| Main walkway | 0.80 m (flagged) | 0.91 m | NKBA, snippet |
| Behind a seated diner | 0.81 m (no traffic) | 0.91 m (edge past), 1.12 m (walk past) | NKBA, snippet |
| In front of toilet / washbasin / tub | 0.53 m | 0.76 m | NKBA Bath Planning Guidelines (media.nkba.org/uploads/2022/05/Bath-Planning-Guidelines.pdf), snippet |
| Toilet centre to a side wall or fixture | 0.38 m | 0.46 m | NKBA bath, snippet |
| Washbasin centre to a side wall | 0.38 m | 0.51 m | NKBA bath, snippet |
| Bed sides and foot | 0.60 m (flagged: blog quoting the withdrawn DIN 18011) | 0.75 m | UK Approved Document M vol. 1, M4(2) (accessible dwellings), snippet |
| Coffee table to the sofa front | 0.30 m | 0.35–0.45 m | blog quoting Panero & Zelnik, *Human Dimension & Interior Space* (flagged) |
| Sofa to TV | 1.5 m | 1.2–1.6 × the screen diagonal (≈ 1.8–2.6 m for a 55" TV) | SMPTE/THX viewing angles via secondary sources (flagged) |
| Secondary walkway between pieces | 0.60 m (flagged, our assumption) | 0.75 m | – |

NKBA has a 5th edition (2024); the build re-checks these values against it if the PDF can be read, else they stay
flagged. §4.2 and §4.6 use these numbers; all of them live in `groups.yaml` and the brief can change them.

## 5. C – A smarter AI in the pod

### 5.1 D16 – The model: a bake-off on our own tasks

Checked 10 Oct 2026 on the Hugging Face API (id, sha, licence tag, safetensors size) and the vLLM v0.30.0 source
(our pin; v0.31.0 adds nothing we need). GB on disk.

| Model (HF id @ sha) | Total / active | Licence | GB | Fits one RTX PRO 6000 next to Cycles | Published numbers (vendor's own) |
|---|---|---|---|---|---|
| `Qwen/Qwen3.8-27B-FP8` @017b9c7a (today) | 27.8B dense | Apache-2.0 | 30.9 | yes (measured 52 GB) | ClawEval-MM 57.4, ERQA 65.5, RealWorldQA 85.9, OSWorld-Verified 84.3 |
| `Qwen/Qwen3.8-27B` (BF16) @1d4bf0f2 | same | Apache-2.0 | 55.6 | yes (≈ 65 GB, est.) | same model, no FP8 loss |
| `meta-models/Muse-Glimmer-30B` @a4e59da5 (Aug 2026) | 29.6B dense | Apache-2.0 | 59.6 | yes (≈ 63 GB, est.) | OSWorld-Verified 65.9, MCP Atlas 75.5, MMMU-Pro 74 |
| `google/gemma-4-31B-it` @842da379 | 30.7B dense | Apache-2.0 | 62.5 | borderline | MMMU-Pro 76.9, Tau2 76.9 |
| `Qwen/Qwen3.5-122B-A10B` (GPTQ-Int4 / NVFP4) | 125B / 10B | Apache-2.0 | 79–84 | no (alone + sleep only) | not better than the 27B on any shared benchmark |
| `mistralai/Mistral-Small-4-119B-2603-NVFP4` | 119B / 6.5B | Apache-2.0 | 70.8 | borderline, unverified | vision numbers only as images (blocked): unverified |
| **`nvidia/Qwen3.8-Flash-Next-NVFP4` @fc694b54** | 180B / 6B | **custom (flag)**: `qwen-community-1.0` (Qwen's FP8 repo) | 132.7 | **no: 2 GPUs (TP2)**, ≈ 67 GB per GPU, Cycles in the rest | ClawEval-MM **64.4**, ERQA **72.3**, RealWorldQA 88.5 (+7, +7, +2.6 over the 27B) |
| `stepfun-ai/Step-3.7-Flash-NVFP4` @4275532f | 198B / 11B | Apache-2.0 | 129.2 | no: 2 GPUs; sm_120 unverified (card: own docker image) | ClawEval-1.1 67.1, V* 95.3 |
| `zai-org/GLM-4.6V-FP8` | 106B | MIT | 110 | no: 2 GPUs | older generation |
| `openai/gpt-oss-120b`, Nemotron-3-Super-120B | 117–120B | Apache-2.0 / NVIDIA custom | 65–80 | – | **text only** |

The Flash-Next licence (read from the repo's LICENSE): commercial use allowed; above 100 M monthly users or US$ 20 M
monthly revenue the model name must be shown in the product; a company running a "Model as a Service" or an "AI
Work Assistant" (coding/office productivity) business needs a separate licence from Qwen for commercial use;
internal use that does not expose the model to third parties is exempt. A rendering pipeline is neither, but a
future product that lets customers send their own prompts to the model could be "Model as a Service": **flag**.

| Option | Verdict |
|---|---|
| a | keep the 27B FP8 and change nothing else | no: the tools are the main problem, but the model was never measured on our tasks |
| b | a separate text planner (gpt-oss-120b) + a VLM critic | no: the planner's tasks are visual (plan crops, top-down candidates), and both do not fit next to Cycles |
| **c** | **one VLM for planner and critic (different modes), code checks as the judge; pick the VLM by a bake-off on our tasks; a second family only for the independent second pass where no code check exists (typing an unknown piece)** | **pick** |

**Bake-off (pod P1)**, a fixed task set prepared on the CPU from the committed real02/real03 data, every answer
scored by code against a known truth:

| Task | Items | Truth |
|---|---|---|
| T1 type an unknown drawn piece from its plan crop (+ neighbours, room) | 40 | labelled by hand from the plans, block names and the drawn context |
| T2 find planted layout errors in top-down images (bed turned 180°, TV away from the sofa, nightstand at the foot, blocked door, chair facing away, 0–2 per room) | 30 rooms | planted by code |
| T3 choose the best of 3 solver candidates (two with planted defects) | 20 | planted |
| T4 find floating / sunk decor and wrong objects in renders | 20 views | the measured gaps of §1.3 and the wrong library objects |
| T5 tool calls on a room brief: valid, allowed, in the plan | 20 | the validator |

Candidates: the 27B FP8 (control) and BF16, each with thinking off and on for the critic; Muse-Glimmer-30B (another
family, fits next to Cycles); Qwen3.8-Flash-Next NVFP4 on 2 GPUs (**needs your OK on the licence flag**; fallback
Step-3.7-Flash, Apache-2.0, if you say no). Measured: accuracy per task, false findings, valid tool calls, seconds per
call, VRAM next to a Cycles render. Rule: the bigger model is taken only if it beats the best single-GPU model by
≥ 10 points on T1–T4 together (it doubles the pod price); else the best single-GPU model.

A 2-GPU pod needs a runner change (`scripts/gpu_run.py` `"count": 1` → 2, container disk ≥ 250 GB for the
weights); it costs $4.98/h (2 × $2.49, live price 10 Oct), i.e. $2.49 per GPU-hour, inside the $5 rule, but a 2 h
worst case is $9.96 (> $5: needs `--over-5-ok`).

### 5.2 D17 – What the agent sees: a room brief

A new read tool `room_brief(room_id)` replaces `room` + `plausibility` for the planner:

| Part | Content |
|---|---|
| Pieces | id, type, source, built or not, size, front (never null: an inferred front is flagged), **lock state and allowed edits** (per tool: allowed / why not / move allowance left), group membership |
| Groups | the program, each group's members, missing partners, its G-check results |
| Free wall spans | id, wall id, start/end, length, what may stand there |
| Findings | only **fixable** ones, each with the tools that can fix it; unfixable findings (locked, not built, needs review) are listed separately as "not yours" |
| Memory | this room's earlier rejected edits with reasons, accepted edits, the open checklist |
| Candidates | the solver's top 3 layouts with scores, top-down image ids |

Unbuilt pieces are no longer drawn in the top-down images or offered to the vision critic (fixes B5).

### 5.3 D18 – Tools that work on groups

| Tool | What | Replaces |
|---|---|---|
| `relayout_room(candidate | program)` | take solver candidate k, or re-solve with other program options | free `move_piece` series |
| `place_group(group, options)` | add a missing group (solver places it) | `add_piece` |
| `complete_group(group_id)` | add a group's missing partners | single adds |
| `move_group(group_id, span_id, offset)` | move a whole group along / to a free span; partners follow | piece moves |
| `retype_piece(piece_id, type)` | candidates only from the size table and the room zone | `change_type` |
| `mark_not_furniture(piece_id, kind, evidence)` | a symbol, mark or line read as furniture | `remove_piece` for misreads |
| `fix_fixture(piece_id, size: product, move ≤ 0.5 m)` | U1 | – |
| `set_front(piece_id, front_deg)` | for drawn pieces without a front | `rotate_piece` |
| `dry_run(edit)` | the validator's answer without applying it; free of the try budget | – |
| levels tools | §3.6 | – |
| `report_library_gap(type, style, reason)` | §6.4 | – |
| existing | `set_lighting`, camera, material, exterior tools, `finish` | kept |

Every edit tool validates by code (G-, F-, L-checks, placer checks, CLAUDE.md locks), returns the failed checks with
numbers ("TV 52° off the sofa axis, needs ≤ 10°"), and is logged as today.

### 5.4 D19 – A plan per room, memory, coverage, budget

- **Plan first:** the first answer of a room session is a JSON plan (program confirmed or changed, groups to fix,
  findings in order, intended tools); the loop checks the plan against the room brief; the session ends when its
  checklist is done or its budget is spent; open items go to the next round's plan.
- **Memory across rounds:** a per-room ledger (`orchestrator/memory.json`): accepted and rejected edits with reasons,
  candidates tried, open checklist. An edit identical to a rejected one is refused by the loop without a model call.
- **Coverage:** code checks run on every room every round (seconds). Rooms are ranked by fixable severity × area,
  then by "not visited yet"; every room with a fixable critical or major finding gets a session before any room gets
  a second one. Room sessions run **in parallel** (4–8 streams on one vLLM server; G1 measured 167 tokens/s at 4
  streams vs 46 at 1). The per-round cap becomes a time cap.
- **Vision where it adds something:** typing unknown pieces (plan crop), choosing among candidates, judging looks
  in renders (realism, wrong objects, decor that looks wrong), and exterior views; never for what code measures.
  The critic gets the code findings so it does not repeat them, and only built pieces.
- **Time budget:** the final-stage estimate uses the measured render throughput of round 0 on this pod (seconds per
  view) instead of a fixed factor (fixes B6: 34.7 min estimated, 19.8 min real); the 20 min margin stays.
- **Self-check:** the prompt asks for `dry_run` before an edit whose checks are unsure; the loop sends one edit at a
  time per piece and shows its result before the next.

### 5.5 D20 – Measure it

Per run, in the log, the report and `orchestrator/metrics.json` (and `results/compare/<p>/agent_metrics.md` across
runs): edits accepted / rejected by reason, rooms covered (code / vision / planner), findings before / after by check
and severity, minutes and calls per room, tokens, time to the first accepted edit, repeats refused by memory.
Targets for real03: ≥ 90 % of rooms with fixable findings visited, ≥ 60 % of edits accepted, critical findings 0,
major findings −50 % against run 3.

## 6. D – Library audit and growth

### 6.1 D21 – The audit job (pod)

`python -m wenart.assets audit` (`scripts/jobs/library_audit.sh`), resumable, results under `results/library/audit/`:

| Part | What |
|---|---|
| Thumbnails | every furniture and decor model (1032 + 34 Poly Haven) rendered at its catalogue scale: 4 views (front ¾, side, top, back) at 512 px on a 0.5 m grid floor **with a scale reference** (a 1.75 m person silhouette and a 0.45 m seat-height bar) and the dimensions printed; every texture set (floors, walls, fabrics, worktops) as a 1 m sample with a 10 cm grid |
| Code checks | size vs the real-size table per type (width, depth, height); pivot at the bottom centre; up axis; front axis vs geometry and judges; unit scale known or guessed; mesh: non-manifold edges, loose parts, flipped normals share, zero-area faces, open drawers (parts outside the main box), face count (crude < 3k faces for furniture); textures: present, resolution, missing files; duplicates (same type, box ± 1 cm, faces ± 1 %, texture hash); licence fields (NC, SA, ND → remove: U3); title vs type in any language (keyword table TR/EN/DE/NL/FR/ES/IT, "outdoor", "street", "low poly", "test", "stylized") |
| Vision check | the picked model (§5.1) sees the 4 views with the scale reference, the title, the type and the dimensions: is it this type, is it a real manufactured product, indoor or outdoor, which styles, quality for a photoreal render (1–5 with anchored descriptions), has it bedding / cushions, decor: its contact surface (flat bottom, hangs, leans); one pass, a second only where code cannot confirm (the type of a model without a title) |
| Decision | `keep` / `fix` / `remove` per item with the reason: **remove** = wrong object, outdoor, NC/SA licence, broken mesh, unfixable proportions, quality ≤ 2; **fix** = pivot, front, unit scale, size off by 15–30 %, missing bedding flag (fixes are catalogue fields, never edits of the GLB); **keep** = everything else |
| Output | `audit.json` / `audit.csv` / `audit.md` (one row per item: id, type, source, licence, dims, checks, vision answers, decision, reason), a contact sheet per type with keep / fix / remove marked, summary tables per type and style |

### 6.2 D22 – Nothing deleted without your OK

"Remove" = the catalogue entry gets `audit: removed` and the fit never uses it; the GLB stays on the volume. The
18 NC/SA models (U3) are removed from the catalogue at the start of the build. Deleting files from the volume needs a
separate OK with the list.

### 6.3 D23 – Size table

One real-size table per type (`wenart/recognition/size_table.yaml` read through `wenart/furniture/sizes.py`; ranges reviewed against the ABO products
with sizes in their titles) is shared by the audit, the fit, F2/S4 and the solver.

### 6.4 D24 – Gap report and growth

- **Gap report** (`results/library/audit/gaps.md`): per room type and style, the group members needed (§4.2) vs the
  `keep` models (target ≥ 5 per anchor type and style family, ≥ 3 per partner type); every gap with the sources that
  could fill it.
- **During a run** the fit and the agent write a `library_gap` finding (type, style, what was used instead) instead
  of using a wrong piece; the report lists them.
- **Growth** only after your OK of a list (source, licence, count, download size).

**Sources checked 10 Oct 2026** (licence pages, APIs and bucket metadata; counts by script):

| Source | Licence | What it has for our gaps | Download | Verdict |
|---|---|---|---|---|
| Poly Haven models (API) | CC0 | 521 models, 34 used: ≈ 45 unused indoor furniture (rustic/farmhouse, classic, Chinese classic, industrial stools, shelves, a day bed), ≈ 18 lights (chandeliers, industrial pendants, sconces), decor (vases 11, books 3, bowls, frames, mirror, clocks, baskets); **no sink, toilet, bath, fridge, washer** | 157 unused models in these categories: 1.0 GB at 2K | **add first** (`polyhaven.py` exists) |
| ABO (bucket metadata) | CC BY 4.0 | 7,953 models, 538 used; unused: pillows 275 (15 used), rugs 817 (19), wall art 599 (13), headboards 206 (0); by the listing's style field: rustic/farmhouse 101 + 49 decor, industrial 108 (95 sofas), classic/traditional 84 + 120 decor; **0 kitchen or bath fixtures, no duvet, throw or curtain** | ≈ 300 picks ≈ 6.5 GB (whole archive 154 GiB: not needed) | **add** (style pass) |
| Procedural textiles (our code; fabrics from ambientCG: 89 fabric, 16 carpet, 50 leather, 19 wicker; Poly Haven: 43 fabric) | CC0 textures, our code | throws, duvets, bed linen, curtains (pleated panel per window), blinds (slats / roller) | textures only | **build** (replaces 17 throws, 20 curtains, 9 blinds that are generated or Objaverse) |
| Infinigen Indoors factories (`princeton-vl/infinigen`) | BSD-3 (LICENSE) | toilet, bathtub, bathroom sink, kitchen sink + tap, oven, dishwasher, microwave, beverage fridge, kitchen cabinets; books, bowls, pots; **no shower, washer or full-size fridge** | generated on the pod (own venv: Python 3.11, `bpy==4.2.0`), exported and converted to GLB | **add after a test batch** (procedural, real scale) |
| Our parametric fixtures | ours | shower (tray + glass), washing machine, full-size fridge in standard sizes | – | **build** |
| Google Scanned Objects (HF mirror) | CC BY 4.0 (object metadata; Google's pages blocked here) | ≈ 16 bowls, 18 mugs, 36 pots/saucers, 15 towels; 0 vases | ≈ 60 picks ≈ 0.5 GB | add (small decor) |
| Objaverse++ annotations + TexVerse | annotations ODC-By; TexVerse objects CC BY / CC0 only (uploader-declared, **flag**) | quality and "realistic/scanned" labels to pre-filter Objaverse; TexVerse counts for our types to be measured on the pod | metadata 239 MB / 837 MB | optional, later |
| Infinigen-Articulated (HF) | CC BY 4.0 (card) | fridge, oven, dishwasher USD archives (1.4–1.6 GB each) | per archive | flag, optional |
| BlenderKit, Sketchfab direct, Fab, CGTrader, TurboSquid | royalty-free with redistribution limits, logins | – | – | **no** |
| Kenney, Quaternius, Poly Pizza | CC0 (Poly Pizza mixed) | low-poly look | – | **no** (not photoreal) |
| HSSD-models, 3D-FUTURE, PartNet-Mobility | non-commercial | – | – | **no** |

So: **no open, commercial-safe library has realistic kitchen or bath fixtures**; they come from code (Infinigen
factories, our parametric fixtures) and the audited generated models. Japandi and mediterranean have almost no
labelled products anywhere (ABO: 0 Japanese-style listings, 6 boho/coastal pieces): those styles rely on the style
fallback chain and recolouring (§4.8).

**Growth order** (each step only after your OK of its list, in pod P4): (1) Poly Haven unused CC0, 1.0 GB;
(2) procedural textiles and parametric shower / washer / fridge (no download); (3) Infinigen fixtures, a test batch
first; (4) ABO style pass, ≈ 300 models, 6.5 GB; (5) GSO small decor, 0.5 GB; (6) optional: Objaverse++ / TexVerse
CC BY and CC0 candidates, counted first.

## 7. E – Tests

CPU (`pytest -m "not gpu"`), one test per rule at least, hand-made rooms and the committed real02/real03 data:

| Area | Tests |
|---|---|
| Levels | every pattern form of §3.1 (positive and negative); attribute tags; mark kind by position; datum conversion and conflict; no mark becomes furniture; terrain fit (plane, TIN, per side); steps and ramp sizing; plinth; L1–L7 pass/fail cases; real02 and real03 regression (marks read, ground points, entrances) |
| Reading | symbol kinds (room-number circle, door arc, dimension outline); block dictionary; cluster split; context typing (chairs around a table, nightstands at a bed head, counter run with sink); misread toilet → product size; untyped → not built + listed |
| Groups | `groups.yaml` schema; each template on a rectangle, an L room and a room with two doors |
| Solver | determinism (same input → same 3 candidates); hard checks; walkway raster; beam search on real03 rooms; drawn anchors kept; completion adds only partners |
| Checks | G1–G14 pass/fail; S1–S6 with mesh fixtures (pure-Python ray caster) |
| Decor | host frame survives move/turn/resize; cushion against the real back; pillow on the mattress; throw shrinkwrap; S5 tolerances; no type-table height left |
| Agent | room brief content; unfixable findings never sent; dry run; memory refuses repeats; parallel sessions with `MockModel`; time budget from measured throughput; metrics |
| Library | audit code checks on fixture GLBs; decisions; NC/SA removed; `quality_of` fixed; gap report |

GPU (`pytest -m gpu`, on the pods): model serving and tool calls of the picked model; bake-off answers stored; audit
thumbnails and a sample of vision answers; scene checks S1–S6 on each full run; decor S5 on every bed and sofa of
the runs; exterior views show the entrances (L7); before/after contact sheets written.

## 8. Pods and GPU cost (estimate per step)

Prices read live on 10 Oct 2026 (`scripts/gpu_run.py gpus`): RTX PRO 6000 $2.49/h (stock HIGH); 2 × RTX PRO 6000
$4.98/h ($2.49 per GPU-hour). Measured times from M10/M11 (real02 G2d 81 min, real03 run 3 66 min, library
thumbnails ≈ 50 min per ≈ 1,000 models, 1,700 judging sheets in ≈ 40 min).

| Pod | Step | GPU | Minutes | Cost | Over $5 worst case? |
|---|---|---|---|---|---|
| P1 | model bake-off (§5.1): 5 tasks × 4–5 configurations, VRAM next to a Cycles render, GPU tests of the agent | 2 × RTX PRO 6000 (single-GPU models run two at a time) | ≤ 100 | ≈ $6–8.3 | **yes: needs `--over-5-ok`** |
| P2 | library audit A (§6.1): thumbnails with scale reference, texture samples, code checks (mesh, size, licence, duplicates) | 1 × RTX PRO 6000 | ≤ 110 | ≈ $4–4.6 | no ($4.6) |
| P3 | library audit B: vision check with the picked model, decisions, contact sheets, gap report | 1 GPU (2 if Flash-Next) | ≈ 50 | ≈ $2–4.2 | no |
| P4 | library growth after your OK of the list (§6.4): downloads (≈ 8 GB), Infinigen fixtures, thumbnails, audit of the new items, catalogue | 1 GPU (2 if Flash-Next judges) | 1–2 pods ≤ 110 each | ≈ $4.6–9.2 (≈ $9–14 on 2 GPUs) | 2 GPUs: yes |
| P5 | real03 full orchestrated run (levels, ground-floor exterior, solver, decor, agent) | 1 GPU (2 if Flash-Next) | 80–110 | ≈ $3.3–4.6 (≈ $6.6–9.1) | 2 GPUs: yes |
| P6 | real02 full run (basement, attic, variant) | 1 (2) | 100–115 | ≈ $4.2–4.8 (≈ $8.3–9.6) | 2 GPUs: yes |
| P7 | real01 + synthetic-01 (+ synthetic-07 if time: it has levels) | 1 (2) | 70–100 | ≈ $2.9–4.2 (≈ $5.8–8.3) | 2 GPUs: yes |
| P8 | fix re-runs: expect 2–3 pods (M10/M11 needed 3–4 per milestone) | 1 (2) | 2–3 × 90 | ≈ $7.5–11 (≈ $15–22) | 2 GPUs: yes |
| **M12** | | | ≈ 12–16 h of pods | **≈ $35–49 on 1 GPU; ≈ $55–80 if the agent runs on 2 GPUs** | |

- Spent so far $89.37 → after M12 ≈ $124–138 (1 GPU) or ≈ $144–169 (2 GPUs), inside the $200 budget either way;
  ≈ $10 kept for a contingency pod. I ask again before anything would pass $200.
- $30 per day: at most ≈ 5 single-GPU or ≈ 3 two-GPU pods per day, so P1–P8 spread over 3–4 days. Today (10 Oct UTC)
  $16.14 is spent; no pod starts before the build of step 2 is done and tested.
- Every pod has the watchdog and self-stop (`scripts/pod_entry.sh`), one pod at a time, max 2 h; the agent loop and
  the audit stop themselves before the deadline.
- Where the money goes: the stronger model (P1 + the 2-GPU premium), the library audit (P2–P4) and more agent rounds
  per run (the time budget fix gives each run ≈ 30 min more agent time at no extra cost). Not on repeated runs that
  fail for the same reason: every pod's failures get CPU tests before the next pod.

## 9. Order of work after your OK

| Step | What | Where |
|---|---|---|
| 2 | Build in parallel tracks with frozen contracts (as M11 §17): **L** levels (reader, schema, terrain, entrances, plinth, floors, single-region site, L-checks, level tools); **R** reading (symbols, dictionary, clusters, context typing, fixture fix, no boxes); **G** groups (`groups.yaml`), program, solver, G-checks, completion through the solver; **S** scene (decor host frame, ray casts, shrinkwrap, bedding, S1–S6, fit changes, B1/B3/B7); **A** agent (room brief, group and level tools, dry run, plan, memory, parallel sessions, budget, metrics, critic filter; the bake-off task set); **B** library (audit job, NC/SA removal, size table, gap report) | CPU, here |
| 3 | CPU regression on real02/real03/real01/synthetic data: before/after top-down sheets, check counts; code review | here |
| 4 | Pod P1 (bake-off) → model decision (report to you if it picks the 2-GPU model) | RunPod |
| 5 | Pods P2, P3 (audit) → audit report and gap list to you → your OK on removals and downloads → P4 | RunPod |
| 6 | Pods P5–P7, fixes, P8 | RunPod |
| 7 | Report: before/after contact sheets per project, agent metrics, audit summary, open items; `docs/progress.md` | here |

Commit, push and `docs/progress.md` after each step; no pod running at the end of a session.

## 10. Risks

| Risk | Mitigation |
|---|---|
| Better reading breaks real02 (it was tuned on it) | regression tests on the committed real02/real03/real01 data before any pod; before/after top-down sheets |
| Group templates do not fit small Turkish rooms | hard checks use the minimums, the recommended values only score; optional partners are dropped first; a room that fits no candidate keeps its drawn pieces and gets a finding, never random pieces |
| Solver too slow in big open-plan rooms | beam width and a node budget per room (deterministic); zones split an open plan into kitchen / dining / living areas first |
| Level marks misread (a dimension read as a mark) | marks need a keyword, a mark symbol or an attribute tag; vector marks win over inference; conflicts listed; L4 compares the built result with every mark |
| Decor ray casts on bad meshes (holes, flipped normals) | the audit removes broken meshes; a ray miss falls back to the host's audited support height, flagged |
| The 2-GPU model on sm_120 with TP2 is unverified | the bake-off is where it is proved; the 27B stays the fallback with the same code path |
| The audit's vision check is as lenient as the M8–M10 judges | it sees the title, the scale reference and the dimensions; code checks decide size, licence, mesh and duplicates; a wrong object needs both the vision answer and the title check to stay |
| Budget | per-pod estimates above; ask before $200; the 2-GPU premium only if the bake-off shows ≥ 10 points |

## 11. `CLAUDE.md` wording (approved 10 Oct 2026, applied)

1. Furniture rules, fixed equipment (your answer 1):
   > Fixed equipment drawn in the documents (…) is treated like walls: same type, position, orientation and footprint
   > as drawn. Style changes only the look. The AI may fix only a clear drawing or reading error, logged as
   > `adjusted_by_ai` with the reason and the plan crop: a front that faces the wall, a misread size (then the size of
   > a real product of that type), a piece through a wall or in a door swing (a move of at most 0.5 m).
2. Furniture rules, new line:
   > Rooms are furnished in functional groups (seating, dining, sleeping, work, kitchen run, bathroom set …) placed by
   > the deterministic solver; the AI chooses the program and between solver candidates, never coordinates. No
   > untyped piece is built: it is typed, recorded as not furniture, or listed for review.
3. New section "Library rules":
   > Only audited library models (`keep`) are used. Non-commercial, share-alike and no-derivatives licences are not
   > used (user, 10 Oct 2026). Nothing is deleted from the volume without the user's OK. When no audited model fits,
   > the run writes a `library gap` finding instead of using a wrong piece.
4. Evidence rules, new line:
   > Level marks (KOT texts, blocks and attributes) are source data for floor levels, door thresholds and the ground,
   > with the same trust order as geometry; steps, ramps, plinth and terrain are inferred from them where not drawn.
5. GPU limits (only if you approve 2-GPU pods in D16):
   > A pod may have 2 GPUs when the price per GPU-hour stays within the limit; its worst case counts as one action.

## 12. Decisions for you

| # | Question | Recommendation |
|---|---|---|
| D1–D6 | Levels: read every mark (text, attributes, symbols), new building-JSON fields, inference rules, terrain/steps/ramps/plinth in Blender, checks L1–L7, level tools (§3) | yes |
| D3a | When nothing about the ground is drawn: the ground floor 0.15 m above the ground (one inferred step) instead of flush | 0.15 m |
| D7 | Read all drawn furniture first; untyped pieces are not built but listed (no more white boxes) (§4.1) | yes |
| D8–D11 | Groups as data, a program per room, a deterministic group solver with top-3 candidates, the VLM only chooses (§4.2–§4.5) | yes |
| D12 | Group checks G1–G14 and scene checks S1–S6; US/UK guideline minimums as hard checks, recommended values as scores (§4.6, §4.9) | yes |
| D13 | Decor in the host frame, ray casts and shrinkwrap on the built mesh; tolerances gap ≤ 1 cm, penetration ≤ 1 cm (hard) / 3 cm (soft hosts) (§4.7) | yes |
| D14 | Only audited models; style fallback chain with recolour; parametric only for counters, wall cabinets, stairs (§4.8) | yes |
| D15 | Our own solver with the Holodeck vocabulary, Infinigen's hard/soft split and ProcTHOR's group format (no dependency) (§4.9) | yes |
| D16 | Model bake-off P1 including **Qwen3.8-Flash-Next** on 2 GPUs (custom licence, flagged: a "Model as a Service" or "AI Work Assistant" business needs a separate Qwen licence); if it wins by ≥ 10 points, the full runs use 2 GPUs | OK to include it (fallback Step-3.7-Flash if not) |
| D17–D20 | Room brief, group tools, dry run, plan per room, memory, parallel sessions, measured time budget, metrics (§5.2–§5.5) | yes |
| D21–D23 | Library audit job (code + vision checks, keep / fix / remove per item, contact sheet per type); "remove" = out of the catalogue, files stay until you OK a delete list; one size table; gap report (§6.1–§6.4) | yes |
| D24 | Growth order of §6.4 (Poly Haven 1.0 GB, procedural textiles and fixtures, Infinigen fixtures after a test batch, ABO style pass 6.5 GB, GSO 0.5 GB); each list shown to you after the audit, nothing downloaded before your OK | yes |
| §8 | GPU plan ≈ $35–49 (1 GPU) or ≈ $55–80 (2-GPU agent); P1 and 2-GPU runs need `--over-5-ok` | OK |
| §11 | `CLAUDE.md` wording 1–4 (5 only with D16) | OK |

## 13. Contracts of the build (frozen 10 Oct 2026; only the lead edits this section)

### 13.1 Tracks and file ownership

| Track | Builds | Owns (only this track edits) | Tests |
|---|---|---|---|
| **L** levels | §3: D1–D6, D3a, B9, B10; single-region site and exterior (U2) | `wenart/levels/**`, `wenart/ingest/generic/levels.py`, `wenart/sheets/**`, `wenart/blender/site.py`, `facade.py`, `shell.py`, `exterior.py`, `exterior_checks.py`, `roof.py`, `cameras.py`, `camsearch.py`, `build.py` (not the S hook block), `wenart/defaults.yaml`, `wenart/brief.py`, `wenart/report/m10.py` | `tests/test_levels_*.py` + the matching existing tests |
| **R** reading | §4.1: D7, B11 (with `levels.marks.parse_mark`), U1 at ingest, kitchen zones, no built unknowns | `wenart/ingest/generic/reading.py`, `wenart/ingest/generic/symbols.py`, `core.py`, `labels.py`, `outlines.py`, `wenart/ingest/dxf_generic.py`, `wenart/ingest/pipeline.py` (not the hook lines), `wenart/ingest/raster.py`, `wenart/furniture/infer.py`, `wenart/recognition/**` (not `size_table.yaml`) | `tests/test_reading_*.py` + matching |
| **G** groups | §4.2–§4.6, §4.9: D8–D12, D15 (groups.yaml, program, solver, G-checks, layout and completion through the solver, group edit ops, `dry_run`, `allowed_edits`, U1 in the validators) | `wenart/furniture/groups.yaml` (new), `groups.py`, `program.py`, `solver.py`, `group_checks.py`, `layout.py`, `complete.py`, `placer.py`, `plausibility.py`, `schemas.py`, `edit_ops.py`, `locked.py`, `prompts.py` | `tests/test_groups_*.py`, `tests/test_solver_*.py` + matching |
| **S** scene | §4.7–§4.8: D13, D14 (host frame, rays, shrinkwrap, procedural textiles and bedding, parametric shower / washer / fridge, curtains, blinds), S1–S6, B1, B3, B7, `catalog.usable` in the fit, style fallback chain | `wenart/furniture/decor.py`, `decor_ai.py`, `fit.py`, `catalog.py`, `wenart/blender/furniture.py`, `parametric.py`, `proxies.py`, `materials.py`, `looks.py`, `scene_checks.py`, the scene-check hook block in `build.py` | `tests/test_scene_*.py`, `tests/test_decor_*.py` + matching |
| **A** agent and run | §5: D16–D20 (bake-off task set and job, TP2 serving, room brief, group and level tools, dry run, plan, memory, parallel sessions, measured budget, metrics, critic filter), B5, B6, B8; wiring of G-, L-, S-checks and `library_gap` findings into the critic; layout stage on the agent model | `wenart/agent/**`, `wenart/run/**`, `wenart/vision_check/**`, `wenart/report/**` (not `m10.py`), `scripts/jobs/*.sh` (not `library_*`), `scripts/pod_setup_*.sh` (not `library`), `scripts/pod_requirements*.txt` | `tests/test_agent_*.py`, `tests/test_run_*.py`, `tests/test_bakeoff_*.py`, `tests/gpu/test_agent.py` + matching |
| **B** library | §6: D21–D24 (audit job, decisions, contact sheets, gap report, size table, growth scaffolding behind your OK), U3 (NC/SA out of the catalogue now) | `wenart/assets/**`, `wenart/furniture/catalog_library.json`, `catalog.json`, `wenart/furniture/sizes.py`, `wenart/recognition/size_table.yaml`, `scripts/jobs/library_*.sh`, `results/library/**` | `tests/test_library_*.py`, `tests/test_audit_*.py`, `tests/gpu/test_library.py` + matching |
| Lead | contracts, stubs, merges | `CLAUDE.md`, `docs/**`, `wenart/schema/building.schema.json`, `scripts/gpu_run.py`, `tests/test_m12_contracts.py`, `tests/test_gpu_run.py` | – |

A track that needs a change in another track's file writes it into its report; the lead decides. Every track keeps
`pytest -m "not gpu"` green for the files it touches and adds tests that fail on the old code.

### 13.2 Interfaces (stubs committed by the lead; signatures frozen, `tests/test_m12_contracts.py`)

| Module (owner) | Functions | Used by |
|---|---|---|
| `wenart/levels/marks.py` (L) | `parse_mark(text) -> {value, relative, absolute, kind_hint, raw} | None`; `MARK_ATTRIBUTE_TAGS` | L, R (marks are never furniture) |
| `wenart/levels/model.py` (L) | `infer_levels(building, brief=None) -> building` | L (ingest), A (after level edits) |
| `wenart/levels/checks.py` (L) | `CHECKS` L1–L7; `check_levels(building, scene_manifest=None, render_manifest=None) -> [Violation]` | A (critic, validator), tests |
| `wenart/levels/edits.py` (L) | `LEVEL_EDIT_OPS`, `LEVEL_EDIT_SCHEMAS`, `apply_level_edit(building, edit) -> apply_edit-style result` | A (level tools) |
| `wenart/ingest/generic/levels.py` (L) | `apply_levels(build, works) -> None` (pipeline hook, before reading) | pipeline |
| `wenart/ingest/generic/reading.py` (R) | `read_furniture(build, works) -> None` (pipeline hook, before the type inference) | pipeline |
| `wenart/furniture/program.py` (G) | `room_program(building, room_id, brief=None, choices=None) -> Program` | G, A (room brief) |
| `wenart/furniture/solver.py` (G) | `solve_room(building, room_id, program=None, *, k=3, fixed_ids=None) -> [Candidate]`; `apply_candidate(building, room_id, candidate) -> building` | G (layout stage), A (`relayout_room`) |
| `wenart/furniture/group_checks.py` (G) | `CHECKS` G1–G14; `check_room(building, room_id) -> [Violation]`; `check_building(building) -> {rooms, counts}` | A, G, tests |
| `wenart/furniture/groups.py` (G) | `load_groups() -> {name: template}`; `group_members(building, room_id) -> [...]`; `place_group` (kept) | G, A |
| `wenart/furniture/edit_ops.py` (G) | `EDIT_OPS` (+ `place_group`, `complete_group`, `move_group`, `retype_piece`, `mark_not_furniture`, `fix_fixture`, `set_front`; `relayout_room` takes `candidate`), `EDIT_SCHEMAS`, `apply_edit` (kept), `dry_run(building, edit, *, catalog=None)`, `allowed_edits(building, piece_id) -> {tool: {allowed, why, move_left_m}}` | A |
| `wenart/furniture/sizes.py` (B) | `real_range(ftype) -> {width, depth, height, product} | None`; `product_size(ftype, drawn) -> (w, d)`; `fits(ftype, size, tolerance=0.15)` | R, G, S, B |
| `wenart/furniture/decor.py` (S) | `sync_to_hosts(building) -> building` | A (after every accepted edit and in `agent apply`) |
| `wenart/furniture/catalog.py` (S) | `usable(entry) -> bool` (audit status, NC/SA/ND) | S (fit), B |
| `wenart/blender/scene_checks.py` (S) | `CHECKS` S1–S6, `TOLERANCES`; `run_scene_checks(building, scene_objects, out_path)` (Blender, hook in `build.py`); `measure_pure(meshes, building)` (CPU tests) | build, A (critic reads `checks/scene_<level>.json`) |

`Violation = {check, severity, target, room_id, message, metrics}` everywhere (the M11 format).

### 13.3 Data between the tracks

- Building JSON (schema committed by the lead, all optional): `level_marks[]`, `symbols[]`, `needs_review[]`,
  `rooms[].floor_offset_m` / `floor_evidence` / `program` / `zones`, `openings[].threshold_z`,
  `site.ground.points` / `surface` (terrain kinds `planar`, `tin`), `site.entrances[]`, `site.plinth`,
  `furniture[].group {group_id, group, role}`, `furniture[].library_gap`, `decor[].host_frame {support, u, v,
  lean_deg, shelf}`.
- Zones (R → G): `rooms[].zones = [{zone_id, kind: kitchen | dining | living | work | sleeping, polygon, evidence}]`;
  the room-type rules apply per zone (G).
- DXF attribute tags: the text evidence of an ATTRIB carries `attrib_tag` (lead, `dxf_generic._run`) for L.
- Catalogue (B → S, A): `entries[]` / `decor[]` get `audit = {status: keep | fix | removed, reasons: [str],
  fixes: {field: value}, version: "m12", checked_utc}` and the flags `real_product`, `has_bedding`, `has_cushions`,
  `has_pillows` (beds and seats), `contact` (decor: `flat_bottom | hangs | leans | drapes`). Until the audit has
  run, an entry without `audit` is usable unless its licence is NC/SA/ND (`catalog.usable`).
- Scene checks (S → A): `outputs/<p>/build/checks/scene_<level>.json` (`{violations, counts, measured}`); the build
  manifest's furniture summary gets `scene_checks: {level: counts}`.
- Agent memory (A): `outputs/<p>/orchestrator/memory.json`; metrics `orchestrator/metrics.json`.
- Layout stage (G's CLI, A's command line): `python -m wenart.furniture.layout <fitted> --style --server --model
  --out --debug --project-dir` stays; in an orchestrated run A passes the agent server and model.
- Bake-off (A): `scripts/jobs/bakeoff_m12.sh`, task set `tests/fixtures/m12_bakeoff/`, results
  `results/bakeoff_m12/`; models in `wenart/vision_check/check.yaml` (`models.bakeoff`): `Qwen/Qwen3.8-27B-FP8`
  @017b9c7af6b5689d5dd426a76e0bc077eb5ca20a, `Qwen/Qwen3.8-27B` @1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0,
  `meta-models/Muse-Glimmer-30B` @a4e59da52a7bc87ae7251dd5545c0dd437c44b68, `nvidia/Qwen3.8-Flash-Next-NVFP4`
  @fc694b54fb0174e0913e6adf86691ef85a4ead47 (TP2; fallback `stepfun-ai/Step-3.7-Flash-NVFP4`
  @4275532ffd9a9496ff36b7a2dc4a9db1048da438).
- Runner (lead): `scripts/gpu_run.py run --gpu-count 2` (the pod gets `WENART_GPU_COUNT`); `--over-5-ok` for P1 and
  every 2-GPU pod (user OK of 10 Oct 2026).

## 14. Build log and lead decisions (step 2)

| Date | Item | Decision |
|---|---|---|
| 10 Oct | Track B merged (`6865c6a`) | audit package, size table with heights and products, 18 NC/SA removals in the catalogue, generated credit fixed, growth lists (Poly Haven 88 CC0 / 501 MB, ABO 232 / 7.8 GB, GSO 36 / 239 MB, Infinigen plan); pod P2 started on an RTX 5090 (no RTX PRO 6000 in stock in EU-RO-1) |
| 10 Oct | Track S merged (`27468ee`) | decor in the host frame and on the built mesh (`blender/rest.py`), procedural textiles (`blender/textiles.py`), parametric shower / washer / fridge, scene checks S1–S6, fit on usable models with the style chain; schema: `host_frame` keys, `decor_dropped`, `asset.method: none` |
| 10 Oct | Fixtures without an audited model (track S question) | **kitchen and bath fixtures** (toilet, washbasin, bathtub, shower, kitchen sink, stove, fridge, washing machine) fall back to the parametric model with a `library_gap` record when no audited model fits; otherwise drawn fixed equipment would vanish, which CLAUDE.md forbids. Sofas, beds and tables never fall back to parametric (§4.8 stays) |
| 10 Oct | Track L merged | level marks (reader, datum, kinds, symbols), terrain, entrances, plinth, room floors, single-floor slab + `flat_cut` roof + site, L1–L7, level edits; real03: the 2 model-space marks (KOT-BINA +0.00 / KOT-ARAZI 93.20) read, datum 93.20, ground by D3a (the other ≈ 284 marks are in unused blocks), 2 entrances with one 0.15 m step, 6 exterior views planned; real02: datum 43.00, the 20 BDK attributes confirmed unused, courts recorded; synthetic-02/-05 (single ground floors) now get a slab and a `flat_cut` roof (U2); schema documents the new fields |
