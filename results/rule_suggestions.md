# Rule suggestions (22 Nov 2026, self-improvement round, part 4)

Mined from `results/reading_corrections.jsonl` (96 records, 59 placeable), `results/critic/user_marks.json` (25 marks)
and `wenart/blender/architect_lessons.json` (352 lessons, 26 open), plus what parts 0-3 of this round measured. Each
entry is a pattern that repeats (two or more records, marks or lessons) and that no rule covers yet. **None of these is
implemented: the user picks.** Every rule would be general (UL338) and ship with its synthetic test and a check.

**Update 22 Nov 2026 (the user: "build S5, S3, S4, S6"): S3, S4, S5 and S6 are BUILT** (lessons UL355-UL358; tests
`tests/test_rules_s3_s6_20261122.py`; synthetic-29-upper-floor-door, synthetic-30-fire-stair, synthetic-31-plain-layers,
synthetic-32-sliding-window-tag in the gated set; `docs/progress.md`, "22 Nov 2026, S3-S6 round"). S1 and S2 stay open.

**Update 22 Nov 2026 (the user: "build S2 and double-wall rule"): S2 is BUILT** (lesson UL361, `walls.split_stair_edges`,
check RC14 `stair_edge_wall`, synthetic-28-stair-edge-run, `tests/test_rules_s2_doublewall_20261122.py`), with the
double-wall rule (UL362, `ingest.generic.double_leaf`, check RC14 `double_leaf_walls`, synthetic-33-double-wall).
C0053 is no S2 case after all (see S2 below); S1 stays open.

**Update 22 Nov 2026 (the user: "build the open-passage rule"): the open-passage rule, C0053's case, is BUILT** (lesson
UL363, UL327's general form: `openings.passage_marks` + `twins.open_passages`; check RC14 `open_passage`;
synthetic-34-open-passage; `tests/test_rules_open_passage_20261122.py`; `docs/progress.md`, "22 Nov 2026,
open-passage round"). C0053 is satisfied (real07 95.5 -> 100). See the note under S2 below.

**Update 22 Nov 2026 (the user: "yes start C0089"): the grille rule, C0089's case, is BUILT** (S7 below; lesson UL365,
`openings._grille_bars` + `openings.blocked_passage`; check RC14 `unnamed_exit`; synthetic-35-grille-slot;
`tests/test_rules_c0089_20261122.py`; `docs/progress.md`, "22 Nov 2026, C0089 round"). C0089 is satisfied (real10 99.2
-> 100): it was no S3 case (L-1 stands at the ground) but a grille read as a door.

How they were found: records grouped by element kind and by what the user said ("no wall", "it is a window", "kitchen
... window", "not a real room"); records still unsatisfied on today's reading (`score`: real07 C0053, real10 C0035,
C0086, C0089; C0085 and C0091 were fixed in this round, part 2, by the sash rule); the marks the user gave per AI-check kind; open
lessons with no check.

| # | proposed rule | evidence (records, marks, lessons) | still wrong today |
|---|---|---|---|
| S1 | kitchen daylight | marks P1 right 3/3 (real09 L2, real20 L0, real20 L1); C0055, C0096; real20: "Separate window too" | real20 L0/L1 (not drawn) |
| S2 | a flight's open side on a long wall | C0053; synthetic-25 (free-standing case fixed today) | real07 L1 |
| S3 | an upper-floor door onto nothing | C0089; known errors door_into_air 20 (real20 L2-L4); RC17 door_into_air real06 L1 x2 | real10 L-1, real06 L1 |
| S4 | a fire stair's enclosure is closed | C0035 (7 typical floors), C0040, UL307, UL316 | real10 L0-L6 |
| S5 | layer names are no evidence for walls | read twice: real09 loses 290 of 388 walls with renamed layers; real07 26 places | real09, real07 |
| S6 | a window-high size tag types door-layer sliding leaves as a window | C0085/C0091 (fixed today on the window layer), C0086, C0087 | real10 L0 (C0086) |

## S1. Kitchen daylight

- **Update 22 Nov 2026 (UL354).** The user marked the real20 kitchens' 1.20 m '120/210' unit to the balcony: "this marked section could be seen as window or a door". That unit is the window meant; real20 needs no added window. If S1 is built, a kitchen opening to a balcony or terrace counts as its daylight, read as door or window.

- **Rule.** A kitchen (room type kitchen) whose walls hold no window, and whose only outer wall holds a door to a
  balcony or terrace, gets its window looked for again: (1) a window symbol or frame lines in the rest of that outer wall
  on any layer, (2) a window size tag (W/H, H < 2.0 m) within 1.2 m, (3) the elevation of that facade (a window drawn
  there at the kitchen's place). If none is found, the reading keeps the door alone and the architect (not the reader)
  may add a window beside the door in a solid stretch of at least 0.60 m, marked `inferred` with the reason "a kitchen
  needs daylight (the user's rule)", listed in the report and never counted as read.
- **Evidence.** The user marked the AI's `kitchen_no_window` right every time asked (real09 L2 kitchen, real20 L0 and
  L1 kitchens, 21 Nov). real09 L2: the window was drawn and read as a sliding door (C0096, fixed by UL349). real10:
  every kitchen window was drawn as a frame read as wall pieces (C0055). real20 L0/L1: no window is drawn (this round,
  part 0: the 1.20 m '120/210' door-and-side-leaf unit `fm-door2` and a solid 1.07 m wall; crop
  `outputs/si/real20_L1_kitchen_balcony_wall.png`), yet the user says "Separate window too".
- **Draft synthetic test.** `synthetic-27-kitchen-balcony`: the base flat with the MUTFAK's facade window removed and a
  1.20 m door to a drawn balcony (BALKON label, parapet line) in its place, plus a 1.0 m solid stretch beside it.
  Truth A (drawn variant): a 0.80 m window drawn beside the door on PENCERE, read as a window. Truth B (undrawn
  variant): no window read; the architect's model has one `inferred` window in the solid stretch, the reading score
  unchanged (an inferred element is no read element).

## S2. A flight's open side on a long wall

- **BUILT 22 Nov 2026 (UL361).** `walls.stair_edge_spans` + `walls.split_stair_edges`: a thin piece (<= 0.12 m) at one
  face of which a flight's treads end (none at the other face) is split at the flight's ends when the part along the
  flight parts nothing (its two sides joined round it within 2 m, no other room's label in sight beyond it); the parts
  beyond stay walls. synthetic-28-stair-edge-run 92.8 -> 100. **C0053 is not reached and is no S2 case:** on the
  drawing (real07 L1) the top flight (treads 10-18, x 7.6-9.89) ends on the BANYO's 0.18 m wall, a real wall with a
  room beyond; the C0053 span (9.75-11.98) lies beyond the flight's top end and holds no line at all, only the axis and
  the floor hatch: a partition (the BANYO's corner at 9.89) ends short of a column (11.65), and the reader bridges the
  gap into the wall run w_L1_023 with a 2.23 m opening 2.10 m high. It is UL327's general form ("where a drawn
  partition simply ends short of the next wall, with no door and no frame in the gap, the gap is an open passage from
  floor to ceiling"), built so far only for dressing rooms (`twins.open_passages`).
- **The open-passage rule: BUILT 22 Nov 2026 (UL363, the user: "build the open-passage rule").** The openings reader
  records what is drawn in every doorless gap (`openings.passage_marks`: `clear` when only floor hatch, tiles, the
  notation and lines that end beyond the wall band are there; else swing, jambs, lintel, tag or lines); a clear gap in
  an inner partition (not exterior, not a party wall, at most 0.20 m thick) between two rooms, at least 0.60 m wide and
  not into a shaft, technical room, garage, balcony, shelter or wet room, becomes an open passage up to the ceiling
  (`twins.open_passages`, the dressing-room case of UL327 kept); a wet room's gap stays at door height and its only
  way in is an RC14 `open_passage` info finding. real07 L1's o_L1_001 (C0053) is open now; the KEMER arches of real07
  L0 keep their heads.

- **Rule.** Where the treads of a flight end on one face of a wall piece and nothing ends on its other face, the part
  of the piece along the flight (from the first to the last tread, within 0.35 m) is the stair's edge (stringer and
  balustrade): the piece is split at the flight's ends and that part is not built as a wall. Today's rule
  (`walls._drop_stair_edge_pairs`) only drops a thin pair as long as the flight, free at both ends.
- **Evidence.** C0053 (real07 L1, "This wall do not exist"): the curved stair's top edge was read as a wall; today the
  wall w_L1_023 (6.68-15.90 m, 0.18 m) runs through the stair's edge (9.75-11.98 m), so the free-standing rule does not
  reach it. synthetic-25-stair-edge (part 2) reads right since this round.
- **Draft synthetic test.** `synthetic-28-stair-edge-run`: synthetic-25 with the balustrade's two lines continuing as
  the faces of a 0.10 m partition 1.5 m beyond the flight's top end. Truth: the partition beyond the flight is a wall,
  no wall along the flight.

## S3. An upper-floor door onto nothing

- **Rule.** On a storey above the ground, a door read in an outer wall with nothing outside to step onto (no balcony,
  terrace or the roof of the storey below; RC17 `door_into_air`) and drawn without a swing arc or a door block (leaves as
  lines only) is a window when it lies on the window layer or carries a window tag, else it stays a door and becomes a
  question for the user (never silently built as a door to the air).
- **Evidence.** C0089 (real10 L-1, "there is no doors to outside"); the known errors' 20 doors into the air (real20
  L2-L4, before the typical-floor fix); RC17 door_into_air on real06 L1 (d_L1_001 2.15 m, d_L1_010 0.45 m) today. The
  AI check P8 door_into_air: user marks 3 right, 1 wrong.
- **Draft synthetic test.** `synthetic-29-upper-floor-door`: a two-storey house whose L1 facade has (a) a 1.2 m pair of
  leaves drawn as lines on PENCERE with no balcony outside (truth: a window) and (b) a swung door onto a drawn balcony
  (truth: a door).

## S4. A fire stair's enclosure is closed

- **Rule.** A stair room labelled or recognised as a fire escape (YANGIN MERDİVENİ, KAÇIŞ, a second stair of the core)
  has no doorless opening to a flat or a hall: its only openings are doors (a gap with nothing drawn becomes wall unless a
  door symbol or tag is there), and the door to the shared hall is its entrance.
- **Evidence.** C0035 (real10, "There should have been fire escape ladders here, and a door to reach there via Hall
  halls the common use area"): seven absent openings, one per typical floor, still read as openings today; C0040, UL307,
  UL316 (common areas and their doors).
- **Draft synthetic test.** `synthetic-30-fire-stair`: synthetic-13's typical floor with a second U stair in a closed
  enclosure, a 1.40 m door with tag 140/230 to the hall and one empty 0.9 m gap to a flat. Truth: the door, no opening
  at the gap, on every typical floor.

## S5. Layer names are no evidence for walls

- **Rule.** The wall layer and the wall pieces are chosen by geometry first (face pairs, closing the labels, the pair
  share), the layer name only breaking ties: a drawing with renamed layers (L1, L2, ...) reads the same walls.
- **Evidence.** Part 3 (read twice, layers renamed): real09 loses 290 of 388 walls and 25 rooms, real17 and real10
  change hundreds of places, real06 gains 16 windows. So many places change that the signal cannot point at the user's
  corrections (lift 0.96 against chance, `results/read_twice/value_20261122.json`): the reading depends on the layer
  names far beyond what the drawing's geometry says.
- **Draft synthetic test.** `synthetic-31-plain-layers`: the base flat with every layer renamed L1..L7 (layer 0 kept).
  Truth: the base house exactly (stability's `layers` variant as a gated synthetic project).

## S6. A window-high size tag types door-layer sliding leaves as a window

- **Rule.** The reverse of what part 2 built (sashes on a window layer are a window unless a door-high tag, a door word
  or a balcony label says door): sliding leaves on a door layer, or on a layer with no role, with a size tag W/H of the
  gap's width within 1.2 m whose H is under 1.80 m are a sliding window; a lift's sliding door keeps its door (a lift
  label behind it).
- **Evidence.** C0085, C0091 (sliding windows on the window layer, fixed this round), C0086 (real10 L0, "it is a sliding
  window", still not satisfied: the window is read 0.39 m off the user's place, the outer layer of the double wall an
  opening), C0087 (real10 L-2, "it is a sliding door for the lift").
- **Draft synthetic test.** `synthetic-24` with one door-layer sliding pair tagged 160/140 (truth: a window) beside the
  lift's sliding door tagged 90/210 (truth: a door).

## S7. A grille is no door (BUILT, 22 Nov 2026, UL365)

- **Rule.** Equal bars across a wall gap at a pitch finer than any stair's going (a grille, louvres, slats), filling it,
  standing out of the wall on one side only and ending at its jambs, on any layer but a wall, hatch, finish, stair or
  notation layer, are a fixed grille: the gap is a window (operation fixed), never a door. A door drawn open at 90
  degrees with no swing arc needs a clear passage: bars of the leaves' own length standing between them make them bars
  of a grille, slats, treads or a window's lines, no door (and the ranker may not type the gap a door). A drawn swing, a
  door block or a door tag keeps the door.
- **Evidence.** C0089 (real10 L-1, "it is not a real room and there is no doors to outside"): a light slot's grille on
  TEFRİŞ, 32 bars 0.64 m long in pairs at a 0.10 m pitch, read as a 1.80 m double door opened at 90 degrees; the same
  grille RC16 step b turned down as a stair (`symbols._grille`). The general class `door_invented` (weak-spot rank 3).
  On the bench the clear-passage test also turned down a 'door' read from the lines of the window round the corner in
  an end gap (swiss-b1747), which found its own 40/140 window and the stair behind it.
- **Test.** `synthetic-35-grille-slot` (gated): the grille slot (truth: a window, the slot a light well), beside an
  entrance drawn open with no arc above a step, a French window over a balustrade's bars and a doorless way in crossed
  by floor boards (truth: each as drawn). Check: RC14 `unnamed_exit`.

## Seen but covered (no suggestion)

- Mirrored halves (C0004, C0023, C0028, C0043, C0058): UL276 and the mirror rules.
- Stairs missed (C0013, C0054, C0088, C0093): all satisfied on today's readings.
- AI-check kinds the user marked wrong every time (P3 flat_no_entrance, P6 stair_no_landing_door, P7
  storey_no_stair_access, inventory room_missing on basements): demoted already (UL347, UL351).
