# Architect's review: real04

736 questions asked (33 rules x the elements they apply to), 34 change(s), 13 answered, 0 open point(s).

| rule | topic | asked | fine | changed | answered | open |
|---|---|---|---|---|---|---|
| B1 | arrival | 1 | 1 | 0 | 0 | 0 |
| B2 | parking | 1 | 1 | 0 | 0 | 0 |
| A2 | access | 8 | 1 | 7 | 0 | 0 |
| A5 | decks without a door | 1 | 0 | 1 | 0 | 0 |
| E1 | outside doors | 2 | 2 | 0 | 0 | 0 |
| C1 | circulation | 28 | 28 | 0 | 0 | 0 |
| C2 | kitchen | 2 | 0 | 0 | 2 | 0 |
| T1 | stairs | 2 | 2 | 0 | 0 | 0 |
| T2 | every floor reached | 3 | 3 | 0 | 0 | 0 |
| L1 | daylight | 12 | 8 | 0 | 4 | 0 |
| W2 | windows to the outside | 12 | 12 | 0 | 0 | 0 |
| L2 | fresh air | 10 | 2 | 8 | 0 | 0 |
| W3 | low sills | 0 | 0 | 0 | 0 | 0 |
| P1 | privacy | 8 | 8 | 0 | 0 | 0 |
| R1 | room size | 6 | 6 | 0 | 0 | 0 |
| R2 | use | 18 | 18 | 0 | 0 | 0 |
| R3 | ceiling height | 28 | 28 | 0 | 0 | 0 |
| R4 | room area | 18 | 18 | 0 | 0 | 0 |
| R5 | room type | 28 | 28 | 0 | 0 | 0 |
| O1 | openings in their walls | 37 | 37 | 0 | 0 | 0 |
| D1 | door widths | 22 | 22 | 0 | 0 | 0 |
| D2 | doors lead somewhere | 22 | 22 | 0 | 0 | 0 |
| X1 | outer walls | 16 | 10 | 0 | 6 | 0 |
| F5 | clashing furniture | 160 | 158 | 2 | 0 | 0 |
| F1 | pieces in their rooms | 166 | 166 | 0 | 0 | 0 |
| F2 | free doorways | 22 | 22 | 0 | 0 | 0 |
| F3 | free windows | 12 | 12 | 0 | 0 | 0 |
| F4 | room to use | 59 | 58 | 0 | 1 | 0 |
| S1 | falls | 6 | 6 | 0 | 0 | 0 |
| A3 | outside doors | 2 | 0 | 2 | 0 | 0 |
| A4 | light wells | 2 | 1 | 1 | 0 | 0 |
| A1 | rain water | 1 | 1 | 0 | 0 | 0 |
| G1 | trees | 21 | 21 | 0 | 0 | 0 |

## What the architect changed or settled

- **A2 sp_001**: pool deck sp_001 at -3.00 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_001 to the site's path (14.0 m; inferred)
- **A2 sp_002**: pool deck sp_002 at -1.40 m: no door from the house at its level, no open steps -> the glass railing on edge 1 closed its steps: the railing now stops 0.10 m beside the flight
- **A2 sp_002**: pool deck sp_002 at -1.40 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_002 to the site's path (18.6 m; inferred)
- **A2 sp_003**: pool deck sp_003 at +1.55 m: no door from the house at its level, no open steps -> the glass railing on edge 0 closed its steps: the railing now stops 0.10 m beside the flight
- **A2 sp_003**: pool deck sp_003 at +1.55 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_003 to the site's path (7.7 m; inferred)
- **A2 sp_004**: pool deck sp_004 at -0.20 m: no door from the house at its level, no open steps -> the glass railing on edge 6 closed its steps: the railing now stops 0.10 m beside the flight
- **A2 sp_004**: pool deck sp_004 at -0.20 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_004 to the site's path (20.3 m; inferred)
- **A5 sp_001**: pool deck sp_001 lies at the L-1 floor (-3.00 m) outside window(s) win_L-1_003; no door opens onto it -> reached from outside: its steps and a path to the site's paths (A2); the windows stay as drawn
- **C2 r_L-1_mutfak**: r_L-1_mutfak has no door or opening to a living or dining space (through the hall to r_L-1_salon) -> answered by you ("yes: a separate kitchen on purpose"): keep it as drawn (the question closes; nothing changes)
- **C2 r_L-1_mutfak_2**: r_L-1_mutfak_2 has no door or opening to a living or dining space (through the hall to r_L-1_salon_2) -> answered by you ("yes: a separate kitchen on purpose"): keep it as drawn (the question closes; nothing changes)
- **L1 r_L0_yatak_odasi_3**: glass 1/4 of the floor -> answered by the AI architect ("The room is a habitable bedroom with zero outside glass, so it requires a window to meet daylight codes."): r_L0_yatak_odasi_3: new window win_arch_r_L0_yatak_odasi_3_1 2.68 x 1.20 m on w_L0_009 (glass 3.22 m2 = 1/4 of the floor)
- **L1 r_L0_yatak_odasi_4**: glass 1/4 of the floor -> answered by the AI architect ("The room is a habitable bedroom with zero outside glass, so it requires a window to meet daylight codes."): r_L0_yatak_odasi_4: new window win_arch_r_L0_yatak_odasi_4_1 2.68 x 1.20 m on w_L0_016 (glass 3.22 m2 = 1/4 of the floor)
- **L1 r_L1_oyun_aktivite_ve_dinlenme_odasi**: glass 1/10 of the floor -> answered by you ("yes"): r_L1_oyun_aktivite_ve_dinlenme_odasi: win_L1_001 2.00 -> 4.00 m wide; win_L1_001 sill 0.90 -> 0.69 m (it opens onto a terrace at its floor) (glass 4.09 m2 = 1/10 of the floor)
- **L1 r_L1_oyun_aktivite_ve_dinlenme_odasi_2**: glass 1/10 of the floor -> answered by you ("yes"): r_L1_oyun_aktivite_ve_dinlenme_odasi_2: win_L1_002 2.00 -> 4.00 m wide; win_L1_002 sill 0.90 -> 0.69 m (it opens onto a terrace at its floor) (glass 4.09 m2 = 1/10 of the floor)
- **L2 r_L-1_banyo**: r_L-1_banyo (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **L2 r_L-1_banyo_2**: r_L-1_banyo_2 (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **L2 r_L0_e_banyo**: r_L0_e_banyo (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **L2 r_L0_e_banyo_2**: r_L0_e_banyo_2 (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **L2 r_L0_banyo**: r_L0_banyo (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **L2 r_L0_banyo_2**: r_L0_banyo_2 (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **L2 r_L1_banyo**: r_L1_banyo (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **L2 r_L1_banyo_2**: r_L1_banyo_2 (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **X1 w_L1_005**: w_L1_005 is an outer wall (1.5 m along the outside) only 0.11 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_006**: w_L1_006 is an outer wall (1.5 m along the outside) only 0.11 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_009**: w_L1_009 is an outer wall (9.8 m along the outside) only 0.10 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_010**: w_L1_010 is an outer wall (1.6 m along the outside) only 0.10 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_014**: w_L1_014 is an outer wall (1.6 m along the outside) only 0.10 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_015**: w_L1_015 is an outer wall (9.8 m along the outside) only 0.10 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **F5 f_L-1_073**: table_coffee clashed with f_L-1_071 -> f_L-1_073 (table_coffee) cut f_L-1_071 (armchair) by 0.18 m; f_L-1_073 (table_coffee) moved 0.71 m clear of it (inside its room, clear of the other pieces and the doorways)
- **F5 f_L-1_074**: table_coffee clashed with f_L-1_069 -> f_L-1_074 (table_coffee) cut f_L-1_069 (armchair) by 0.18 m; f_L-1_074 (table_coffee) moved 0.71 m clear of it (inside its room, clear of the other pieces and the doorways)
- **F4 f_L0_014**: only 20% of the 0.5 m in front of f_L0_014 (shower) is free (the wall is close) -> answered by the AI architect ("The shower is a fixed fixture that does not require clearance in front for operation, making the current placement plausible."): keep it as drawn (the question closes; nothing changes)
- **A3 d_L1_003**: door d_L1_003 from r_L1_koridor to the open-air r_L1_teras was an inside door -> built as a glazed outside door
- **A3 d_L1_006**: door d_L1_006 from r_L1_koridor_2 to the open-air r_L1_teras_2 was an inside door -> built as a glazed outside door
- **A4 win_L-1_003**: the terrace sp_001 at -3.00 m lies under the sill -2.10 m: no light well -> light well left out

## Answers about elements not in this reading of the plan

- `W2:win_L0_005` (move_window_to_outer_wall, by you): win_L0_005 is not in this reading of the plan (nothing at the place the answer named)
- `W2:win_L0_006` (move_window_to_outer_wall, by you): win_L0_006 is not in this reading of the plan (nothing at the place the answer named)

## The questions

- **B1 arrival** (major, ok): *Where do I come in? Is there a path from the street to the main entrance door?* Why: a front door nobody can find or reach on foot is the first thing a visitor notices. Asked of 1 element(s).
- **B2 parking** (minor, ok): *Where do I leave the car, and how do I walk from it to the front door?* Why: a parking with no path to the entrance makes people cross the lawn or the driveway's kerb. Asked of 1 element(s).
- **A2 access** (major, fixed): *How do people get to each terrace and pool deck? From the house through a door at its level, or from the garden by steps that no railing closes.* Why: a terrace or pool nobody can walk to is useless and unsafe. Asked of 8 element(s).
- **A5 decks without a door** (minor, ok): *This terrace lies at the floor level of the rooms beside it, right outside their windows, and no door opens onto it: can people still reach it from outside? (The drawn windows stay windows; only when no outside way exists does the architect ask you about a door.)* Why: a deck at the floor's level begs for a door; the drawings decide it. Asked of 1 element(s).
- **E1 outside doors** (major, ok): *Does every outside door open onto something: the ground, a terrace, a balcony or steps?* Why: a door into the air or below the ground is a drawing or level error. Asked of 2 element(s).
- **C1 circulation** (major, ok): *Can I reach every room from the entrance, and without walking through somebody's bedroom?* Why: a room you can only reach through a bedroom is a planning fault (an en-suite bathroom or dressing room is the exception). Asked of 28 element(s).
- **C2 kitchen** (minor, answered): *Is the kitchen next to where people eat and sit (a door or an opening to the living or dining space)?* Why: carrying plates through a hall or another room every day is a sign the plan is not working. Asked of 2 element(s).
- **T1 stairs** (major, ok): *Does every stair lead to another floor?* Why: a stair that ends nowhere is a reading error of the level or the stair room. Asked of 2 element(s).
- **T2 every floor reached** (major, ok): *Can I reach every floor from the entrance?* Why: a floor without a stair or a door from outside cannot be used. Asked of 3 element(s).
- **L1 daylight** (major, ok): *Does every bedroom, living room and kitchen get daylight: a window with glass of at least a tenth of its floor?* Why: a habitable room without enough daylight feels like a cellar; building codes ask for about 1/10. Asked of 12 element(s).
- **W2 windows to the outside** (major, ok): *Does every window look outside (or onto a terrace)?* Why: a window between two rooms is usually a reading error: the dark room needs it on its outer wall. Asked of 12 element(s).
- **L2 fresh air** (minor, fixed): *Can every bathroom and kitchen be aired: a window, else a mechanical extract?* Why: steam and cooking smells need a way out. Asked of 10 element(s).
- **W3 low sills** (major, ok): *Where a window lies more than a metre over the ground, is its sill at least 0.85 m high?* Why: a low sill over a drop is a fall risk (or the window needs a guard). Asked of 0 element(s).
- **P1 privacy** (minor, ok): *Does a bathroom door open straight into the living room, the dining space or the kitchen?* Why: a toilet door in the room where people eat or receive guests is uncomfortable for everybody. Asked of 8 element(s).
- **R1 room size** (minor, ok): *Is every bedroom wide enough for its bed with room to walk around it?* Why: a bedroom narrower than about 2.4 m leaves no passage beside a bed. Asked of 6 element(s).
- **R2 use** (minor, ok): *Is every room furnished for what it is (a bed in each bedroom, a sofa in the living room, a table where people eat, a WC and a basin in each bathroom)?* Why: a room without its main piece reads as unfinished in the renders. Asked of 18 element(s).
- **R3 ceiling height** (minor, ok): *Is every room high enough: 2.40 m for a habitable room, 2.10 m for the others?* Why: a low ceiling feels oppressive and breaks most building codes. Asked of 28 element(s).
- **R4 room area** (minor, ok): *Is every room big enough for what it is (a bedroom 6.5 m2, a living room 10 m2, a kitchen 4 m2, a bathroom 2 m2)?* Why: a room smaller than any room of its type is usually a misread type or size. Asked of 18 element(s).
- **R5 room type** (minor, ok): *Do I know what every room is for?* Why: an untyped room cannot be furnished or lit for its use. Asked of 28 element(s).
- **O1 openings in their walls** (major, ok): *Does every door and window fit in its wall: within its length, clear of the other openings, under the ceiling?* Why: an opening past the wall's end or over another one is a drawing or reading error. Asked of 37 element(s).
- **D1 door widths** (minor, ok): *Is every door wide enough: 0.70 m inside (0.60 m to a WC), 0.80 m to the outside?* Why: a narrow door cannot take furniture or a wheelchair; often a misread width. Asked of 22 element(s).
- **D2 doors lead somewhere** (major, ok): *Does every door join two rooms, or a room and the outside?* Why: a door with the same room or nothing on both sides is on the wrong wall. Asked of 22 element(s).
- **X1 outer walls** (minor, answered): *Is every outer wall thick enough for a facade (0.15 m or more)?* Why: a thin outer wall is usually a partition read as the facade, or a glass wall. Asked of 16 element(s).
- **F5 clashing furniture** (major, fixed): *Does any piece cut another (a side table in a sofa, a lamp in a bed, a chair through its table)?* Why: two pieces through each other are the first thing a client sees in a render. Asked of 160 element(s).
- **F1 pieces in their rooms** (minor, ok): *Does every piece of furniture stand inside its room?* Why: a piece through a wall is a placement error. Asked of 166 element(s).
- **F2 free doorways** (minor, ok): *Can every door open and be walked through without furniture in the way?* Why: a wardrobe in front of a door is the first thing a visitor bumps into. Asked of 22 element(s).
- **F3 free windows** (minor, ok): *Is every window free of tall furniture standing in front of it?* Why: a wardrobe against a window blocks the light and looks wrong from outside. Asked of 12 element(s).
- **F4 room to use** (minor, answered): *Is there room in front of every bed, sofa, wardrobe, WC and counter to use it (0.5 m)?* Why: a piece you cannot reach or open is not usable. Asked of 59 element(s).
- **S1 falls** (major, ok): *Where could somebody fall more than half a metre: is every such terrace, pool deck and roof terrace edge guarded?* Why: an unguarded drop is the first safety question of every design review. Asked of 6 element(s).
- **A3 outside doors** (minor, fixed): *Which doors open to the open air? A door to a terrace or balcony is an outside door: glazed, weather-tight, never the bedroom door of the inside.* Why: an inside door on the open air leaks and looks wrong from outside. Asked of 2 element(s).
- **A4 light wells** (minor, fixed): *Why does this basement window have a light well? Only where the ground outside stands above its sill; a terrace below the sill lights it on its own.* Why: a light well where none is needed is a concrete box in the garden. Asked of 2 element(s).
- **A1 rain water** (minor, ok): *Where does the rain go? Every gutter must drain into a downpipe fixed to a wall all the way down to the ground: no pipe in front of a loggia, across a window or in the air.* Why: rain running down a facade stains it and a pipe in the air looks like a mistake. Asked of 1 element(s).
- **G1 trees** (minor, ok): *Does every tree and shrub stand on open ground, clear of the house, the pools, the paths and the terraces?* Why: a tree through a terrace or in front of a door is a reading or placement error. Asked of 21 element(s).
