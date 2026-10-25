# Architect's review: real04

823 questions asked (41 rules x the elements they apply to), 91 change(s), 26 answered, 2 open point(s).

| rule | topic | asked | fine | changed | answered | open |
|---|---|---|---|---|---|---|
| B1 | arrival | 1 | 1 | 0 | 0 | 0 |
| B2 | parking | 1 | 1 | 0 | 0 | 0 |
| A2 | access | 6 | 4 | 2 | 0 | 0 |
| A5 | decks without a door | 2 | 0 | 2 | 0 | 0 |
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
| R2 | use | 19 | 19 | 0 | 0 | 0 |
| R3 | ceiling height | 28 | 28 | 0 | 0 | 0 |
| R4 | room area | 19 | 19 | 0 | 0 | 0 |
| R5 | room type | 28 | 28 | 0 | 0 | 0 |
| O1 | openings in their walls | 37 | 37 | 0 | 0 | 0 |
| D1 | door widths | 22 | 22 | 0 | 0 | 0 |
| D2 | doors lead somewhere | 22 | 22 | 0 | 0 | 0 |
| D3 | doors to the terraces | 2 | 0 | 2 | 0 | 0 |
| X1 | outer walls | 16 | 10 | 0 | 6 | 0 |
| F5 | clashing furniture | 159 | 156 | 3 | 0 | 0 |
| F1 | pieces in their rooms | 165 | 165 | 0 | 0 | 0 |
| F2 | free doorways | 22 | 22 | 0 | 0 | 0 |
| F3 | free windows | 12 | 12 | 0 | 0 | 0 |
| F4 | room to use | 60 | 59 | 0 | 1 | 0 |
| U1 | outdoor furniture | 7 | 7 | 0 | 0 | 0 |
| S4 | complete furniture groups | 9 | 7 | 0 | 1 | 1 |
| S2 | furniture chosen together | 28 | 0 | 28 | 0 | 0 |
| S3 | styled rooms | 27 | 14 | 0 | 12 | 1 |
| K1 | stair details | 4 | 0 | 4 | 0 | 0 |
| K2 | guards | 11 | 0 | 11 | 0 | 0 |
| K3 | one balustrade language | 1 | 0 | 1 | 0 | 0 |
| S1 | falls | 4 | 4 | 0 | 0 | 0 |
| A3 | outside doors | 2 | 0 | 2 | 0 | 0 |
| A4 | light wells | 2 | 0 | 2 | 0 | 0 |
| A1 | rain water | 1 | 1 | 0 | 0 | 0 |
| G1 | trees | 21 | 21 | 0 | 0 | 0 |

## The architect's questions for you

1. **S4 complete furniture groups** (minor): r_L1_oyun_aktivite_ve_dinlenme_odasi (living) misses side_table or floor_lamp, a rug. *Is the group in r_L1_oyun_aktivite_ve_dinlenme_odasi meant without side_table or floor_lamp, a rug?* Answer key `S4:r_L1_oyun_aktivite_ve_dinlenme_odasi`; options `keep` (keep it as drawn (the question closes; nothing changes))
2. **S3 styled rooms** (minor): r_L1_oyun_aktivite_ve_dinlenme_odasi (living) holds 6 decor item(s), a styled living 9. *Is r_L1_oyun_aktivite_ve_dinlenme_odasi meant to stay this bare?* Answer key `S3:r_L1_oyun_aktivite_ve_dinlenme_odasi`; options `keep` (keep it as drawn (the question closes; nothing changes))

Answers go into `projects/<project>/architect_answers.json` as `{"answers": {"<key>": {"option": "<option>", "answer": "<your words>"}}}`; the next run carries them out and does not ask again. The AI architect on the pod answers the rest it can settle (checked by code).

## What the architect changed or settled

- **A2 sp_001**: pool deck sp_001 at -3.00 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_001 to the site's path (14.0 m; inferred)
- **A2 sp_004**: pool deck sp_004 at +0.00 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_004 to the site's path (12.6 m; inferred)
- **A5 sp_001**: pool deck sp_001 lies at the L-1 floor (-3.00 m) outside window(s) win_L-1_003; no door opens onto it -> reached from outside: its steps and a path to the site's paths (A2); the windows stay as drawn
- **A5 sp_002**: pool deck sp_002 lies at the L-1 floor (-3.00 m) outside window(s) win_L-1_004; no door opens onto it -> reached from outside: its steps and a path to the site's paths (A2); the windows stay as drawn
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
- **D3 d_L1_003**: d_L1_003 to the terrace, 0.82 m -> a glazed door (mostly glass) in the windows' frame finish (code: a library model of at least 45 % glass, else the glazed door)
- **D3 d_L1_006**: d_L1_006 to the terrace, 0.82 m -> a glazed door (mostly glass) in the windows' frame finish (code: a library model of at least 45 % glass, else the glazed door)
- **X1 w_L1_005**: w_L1_005 is an outer wall (1.5 m along the outside) only 0.11 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_006**: w_L1_006 is an outer wall (1.5 m along the outside) only 0.11 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_009**: w_L1_009 is an outer wall (9.8 m along the outside) only 0.10 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_010**: w_L1_010 is an outer wall (1.6 m along the outside) only 0.10 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_014**: w_L1_014 is an outer wall (1.6 m along the outside) only 0.10 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **X1 w_L1_015**: w_L1_015 is an outer wall (9.8 m along the outside) only 0.10 m thick -> answered by the AI architect ("The wall is not flagged as exterior in the drawing, suggesting it is a partition or glass element where the thin thickness is plausible."): keep it as drawn (the question closes; nothing changes)
- **F5 f_L-1_073**: table_coffee clashed with f_L-1_071 -> f_L-1_073 (table_coffee) cut f_L-1_071 (armchair) by 0.18 m; f_L-1_073 (table_coffee) moved 0.71 m clear of it (inside its room, clear of the other pieces and the doorways)
- **F5 f_L-1_074**: table_coffee clashed with f_L-1_069 -> f_L-1_074 (table_coffee) cut f_L-1_069 (armchair) by 0.18 m; f_L-1_074 (table_coffee) moved 0.71 m clear of it (inside its room, clear of the other pieces and the doorways)
- **F5 f_L1_011**: chair clashed with f_L1_009 -> f_L1_011 (chair) cut f_L1_009 (table_dining) by 0.37 m; f_L1_011 (chair) moved 0.07 m clear of it (inside its room, clear of the other pieces and the doorways)
- **F4 f_L0_014**: only 20% of the 0.5 m in front of f_L0_014 (shower) is free (the wall is close) -> answered by the AI architect ("The shower is a fixed fixture that does not require clearance in front for operation, making the current placement plausible."): keep it as drawn (the question closes; nothing changes)
- **S4 r_L0_yatak_odasi_4**: r_L0_yatak_odasi_4 (bedroom) misses 1 nightstand(s) -> answered by the AI architect ("The only available choice is to keep the room as drawn."): keep it as drawn (the question closes; nothing changes)
- **S2 r_L-1_salon**: r_L-1_salon: wood medium, metal black -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L-1_salon_2**: r_L-1_salon_2: wood medium, metal black -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L-1_mutfak**: r_L-1_mutfak: wood -, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L-1_mutfak_2**: r_L-1_mutfak_2: wood -, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L-1_koridor**: r_L-1_koridor: wood -, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L-1_koridor_2**: r_L-1_koridor_2: wood -, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L-1_banyo**: r_L-1_banyo: wood -, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L-1_banyo_2**: r_L-1_banyo_2: wood -, metal black -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_yatak_odasi**: r_L0_yatak_odasi: wood -, metal black -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_e_yatak_odasi**: r_L0_e_yatak_odasi: wood -, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_e_yatak_odasi_2**: r_L0_e_yatak_odasi_2: wood medium, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_yatak_odasi_2**: r_L0_yatak_odasi_2: wood light, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_koridor**: r_L0_koridor: wood light, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_e_banyo**: r_L0_e_banyo: wood -, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_e_banyo_2**: r_L0_e_banyo_2: wood -, metal black -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_koridor_2**: r_L0_koridor_2: wood light, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_yatak_odasi_3**: r_L0_yatak_odasi_3: wood light, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_yatak_odasi_4**: r_L0_yatak_odasi_4: wood medium, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_banyo**: r_L0_banyo: wood -, metal black -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_banyo_2**: r_L0_banyo_2: wood -, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_teras**: r_L1_teras: wood -, metal brass -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_oyun_aktivite_ve_dinlenme_odasi**: r_L1_oyun_aktivite_ve_dinlenme_odasi: wood dark, medium, metal black -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_oyun_aktivite_ve_dinlenme_odasi_2**: r_L1_oyun_aktivite_ve_dinlenme_odasi_2: wood dark, medium, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_koridor**: r_L1_koridor: wood light, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_koridor_2**: r_L1_koridor_2: wood light, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_banyo**: r_L1_banyo: wood -, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_banyo_2**: r_L1_banyo_2: wood -, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_teras_2**: r_L1_teras_2: wood -, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S3 r_L-1_koridor**: r_L-1_koridor (hall) holds 0 decor item(s), a styled hall 2 -> answered by the AI architect ("The only available choice is to keep the hall as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L-1_koridor_2**: r_L-1_koridor_2 (hall) holds 0 decor item(s), a styled hall 2 -> answered by the AI architect ("The only available choice is to keep the hall as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L0_koridor**: r_L0_koridor (hall) holds 0 decor item(s), a styled hall 2 -> answered by the AI architect ("The only available choice is to keep the hall as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L0_koridor_2**: r_L0_koridor_2 (hall) holds 0 decor item(s), a styled hall 2 -> answered by the AI architect ("The only available choice is to keep the hall as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L0_yatak_odasi_3**: r_L0_yatak_odasi_3 (bedroom) holds 2 decor item(s), a styled bedroom 7 -> answered by the AI architect ("The only available choice is to keep the bedroom as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L0_yatak_odasi_4**: r_L0_yatak_odasi_4 (bedroom) holds 2 decor item(s), a styled bedroom 7 -> answered by the AI architect ("The only available choice is to keep the bedroom as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L0_merdiven**: r_L0_merdiven (hall) holds 0 decor item(s), a styled hall 2 -> answered by the AI architect ("The only available choice is to keep the stair hall as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L0_merdiven_2**: r_L0_merdiven_2 (hall) holds 0 decor item(s), a styled hall 2 -> answered by the AI architect ("The only available choice is to keep the stair hall as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L1_koridor**: r_L1_koridor (hall) holds 1 decor item(s), a styled hall 2 -> answered by the AI architect ("The only available choice is to keep the hall as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L1_koridor_2**: r_L1_koridor_2 (hall) holds 1 decor item(s), a styled hall 2 -> answered by the AI architect ("The only available choice is to keep the hall as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L1_banyo**: r_L1_banyo (bathroom) holds 1 decor item(s), a styled bathroom 2 -> answered by the AI architect ("The only available choice is to keep the bathroom as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L1_banyo_2**: r_L1_banyo_2 (bathroom) holds 1 decor item(s), a styled bathroom 2 -> answered by the AI architect ("The only available choice is to keep the bathroom as drawn."): keep it as drawn (the question closes; nothing changes)
- **K1 f_L-1_019**: stair f_L-1_019: drawn with too few treads for its storey -> winders: riser 0.176 m, going 0.28 m, 2R+G 0.63 m; built with 5 winders in the half landing, tread plates with nosings over painted risers, a glass channel balustrade on 2 open side(s)
- **K1 f_L-1_020**: stair f_L-1_020: drawn with too few treads for its storey -> winders: riser 0.176 m, going 0.28 m, 2R+G 0.63 m; built with 5 winders in the half landing, tread plates with nosings over painted risers, a glass channel balustrade on 2 open side(s)
- **K1 f_L0_001**: stair f_L0_001: drawn with too few treads for its storey -> winders: riser 0.175 m, going 0.28 m, 2R+G 0.63 m; built with 7 winders in the half landing, tread plates with nosings over painted risers, a glass channel balustrade on 2 open side(s)
- **K1 f_L0_002**: stair f_L0_002: drawn with too few treads for its storey -> winders: riser 0.175 m, going 0.28 m, 2R+G 0.63 m; built with 6 winders in the half landing, tread plates with nosings over painted risers, a glass channel balustrade on 2 open side(s)
- **K2 r_L1_teras**: balcony r_L1_teras -> a 1.00 m glass channel balustrade on every edge without a wall (gaps under 0.11 m)
- **K2 r_L1_teras_2**: balcony r_L1_teras_2 -> a 1.00 m glass channel balustrade on every edge without a wall (gaps under 0.11 m)
- **K2 ro_001**: roof terrace ro_001: parapet 0.60 m -> a coping on the parapet and a glass channel balustrade to 1.00 m
- **K2 ro_002**: roof terrace ro_002: parapet 0.60 m -> a coping on the parapet and a glass channel balustrade to 1.00 m
- **K2 sp_001**: terrace sp_001: 7 edge(s) over a drop -> a 1.00 m balustrade on them
- **K2 sp_002**: sp_002: retaining walls over 1.2 m hold the ground above it -> a guard on their tops (the fall from the ground into it)
- **K2 sp_003**: sp_003: retaining walls over 1.2 m hold the ground above it -> a guard on their tops (the fall from the ground into it)
- **K2 sp_004**: terrace sp_004: 7 edge(s) over a drop -> a 1.00 m balustrade on them
- **K2 sp_004**: sp_004: retaining walls over 1.2 m hold the ground above it -> a guard on their tops (the fall from the ground into it)
- **K2 sp_002_s1e4**: sp_002_s1e4: retaining walls over 1.2 m hold the ground above it -> a guard on their tops (the fall from the ground into it)
- **K2 sp_002_s1e5**: sp_002_s1e5: retaining walls over 1.2 m hold the ground above it -> a guard on their tops (the fall from the ground into it)
- **K3 house**: balustrades: stairs 4, balconies 2, roof terraces 2, terraces 2 -> one kind for the house: glass channel (from the style)
- **A3 d_L1_003**: door d_L1_003 from r_L1_koridor to the open-air r_L1_teras was an inside door -> built as a glazed outside door
- **A3 d_L1_006**: door d_L1_006 from r_L1_koridor_2 to the open-air r_L1_teras_2 was an inside door -> built as a glazed outside door
- **A4 win_L-1_003**: the terrace sp_001 at -3.00 m lies under the sill -2.10 m: no light well -> light well left out
- **A4 win_L-1_004**: the terrace sp_002 at -3.00 m lies under the sill -2.10 m: no light well -> light well left out

## Answers about elements not in this reading of the plan

- `W2:win_L0_005` (move_window_to_outer_wall, by you): win_L0_005 is not in this reading of the plan (nothing at the place the answer named)
- `W2:win_L0_006` (move_window_to_outer_wall, by you): win_L0_006 is not in this reading of the plan (nothing at the place the answer named)

## The questions

- **B1 arrival** (major, ok): *Where do I come in? Is there a path from the street to the main entrance door?* Why: a front door nobody can find or reach on foot is the first thing a visitor notices. Asked of 1 element(s).
- **B2 parking** (minor, ok): *Where do I leave the car, and how do I walk from it to the front door?* Why: a parking with no path to the entrance makes people cross the lawn or the driveway's kerb. Asked of 1 element(s).
- **A2 access** (major, fixed): *How do people get to each terrace and pool deck? From the house through a door at its level, or from the garden by steps that no railing closes.* Why: a terrace or pool nobody can walk to is useless and unsafe. Asked of 6 element(s).
- **A5 decks without a door** (minor, ok): *This terrace lies at the floor level of the rooms beside it, right outside their windows, and no door opens onto it: can people still reach it from outside? (The drawn windows stay windows; only when no outside way exists does the architect ask you about a door.)* Why: a deck at the floor's level begs for a door; the drawings decide it. Asked of 2 element(s).
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
- **R2 use** (minor, ok): *Is every room furnished for what it is (a bed in each bedroom, a sofa in the living room, a table where people eat, a WC and a basin in each bathroom)?* Why: a room without its main piece reads as unfinished in the renders. Asked of 19 element(s).
- **R3 ceiling height** (minor, ok): *Is every room high enough: 2.40 m for a habitable room, 2.10 m for the others?* Why: a low ceiling feels oppressive and breaks most building codes. Asked of 28 element(s).
- **R4 room area** (minor, ok): *Is every room big enough for what it is (a bedroom 6.5 m2, a living room 10 m2, a kitchen 4 m2, a bathroom 2 m2)?* Why: a room smaller than any room of its type is usually a misread type or size. Asked of 19 element(s).
- **R5 room type** (minor, ok): *Do I know what every room is for?* Why: an untyped room cannot be furnished or lit for its use. Asked of 28 element(s).
- **O1 openings in their walls** (major, ok): *Does every door and window fit in its wall: within its length, clear of the other openings, under the ceiling?* Why: an opening past the wall's end or over another one is a drawing or reading error. Asked of 37 element(s).
- **D1 door widths** (minor, ok): *Is every door wide enough: 0.70 m inside (0.60 m to a WC), 0.80 m to the outside?* Why: a narrow door cannot take furniture or a wheelchair; often a misread width. Asked of 22 element(s).
- **D2 doors lead somewhere** (major, ok): *Does every door join two rooms, or a room and the outside?* Why: a door with the same room or nothing on both sides is on the wrong wall. Asked of 22 element(s).
- **D3 doors to the terraces** (minor, fixed): *Is every door to a terrace or balcony a glazed door, 0.80 m wide or more, in the windows' finish?* Why: a terrace door is part of the facade: a solid inside door there reads wrong and darkens the room. Asked of 2 element(s).
- **X1 outer walls** (minor, answered): *Is every outer wall thick enough for a facade (0.15 m or more)?* Why: a thin outer wall is usually a partition read as the facade, or a glass wall. Asked of 16 element(s).
- **F5 clashing furniture** (major, fixed): *Does any piece cut another (a side table in a sofa, a lamp in a bed, a chair through its table)?* Why: two pieces through each other are the first thing a client sees in a render. Asked of 159 element(s).
- **F1 pieces in their rooms** (minor, ok): *Does every piece of furniture stand inside its room?* Why: a piece through a wall is a placement error. Asked of 165 element(s).
- **F2 free doorways** (minor, ok): *Can every door open and be walked through without furniture in the way?* Why: a wardrobe in front of a door is the first thing a visitor bumps into. Asked of 22 element(s).
- **F3 free windows** (minor, ok): *Is every window free of tall furniture standing in front of it?* Why: a wardrobe against a window blocks the light and looks wrong from outside. Asked of 12 element(s).
- **F4 room to use** (minor, answered): *Is there room in front of every bed, sofa, wardrobe, WC and counter to use it (0.5 m)?* Why: a piece you cannot reach or open is not usable. Asked of 60 element(s).
- **U1 outdoor furniture** (minor, ok): *Is every piece on a balcony, terrace or patio a piece one puts outside, of a model made for outside?* Why: an indoor table with a drawer or upholstered chairs on a terrace look wrong and would not last a winter. Asked of 7 element(s).
- **S4 complete furniture groups** (minor, open): *Is every furniture group complete: a sofa with a coffee table, an end table or a lamp and a rug; a double bed with two nightstands; a dining table with four chairs or more?* Why: a sofa alone or a bed with one nightstand looks half furnished. Asked of 9 element(s).
- **S2 furniture chosen together** (minor, fixed): *Does the furniture of every room look chosen together: one or two wood tones, one metal finish, loud colours only from the style's palette?* Why: a walnut table, a white oak bed and a pine chair with brass and chrome read as a second-hand shop. Asked of 28 element(s).
- **S3 styled rooms** (minor, open): *Is every room styled with enough decor (a living room 9 items, a bedroom 7, a dining room 4)?* Why: a room without lamps, plants, art, cushions and a rug looks unfinished in a render. Asked of 27 element(s).
- **K1 stair details** (minor, fixed): *Is every stair comfortable and finished: risers 0.15-0.19 m, goings 0.25 m+, 2R+G 0.60-0.65 m, 0.80 m wide, treads with nosings, a balustrade on the open side, a handrail?* Why: a steep or narrow stair is unsafe; a stair without nosings, balusters or a handrail looks unfinished. Asked of 4 element(s).
- **K2 guards** (major, fixed): *Does every edge over a drop (a balcony, a roof terrace, a terrace over the garden) have a guard of 1.00 m whose gaps a child cannot pass, and every parapet a coping?* Why: a fall of over a metre needs a guard; a bare parapet top stains the facade. Asked of 11 element(s).
- **K3 one balustrade language** (minor, fixed): *Do the balustrades of the house (stairs, balconies, terraces, parapets) speak one language?* Why: glass on one side and steel bars on the other look like two houses. Asked of 1 element(s).
- **S1 falls** (major, ok): *Where could somebody fall more than half a metre: is every such terrace, pool deck and roof terrace edge guarded?* Why: an unguarded drop is the first safety question of every design review. Asked of 4 element(s).
- **A3 outside doors** (minor, fixed): *Which doors open to the open air? A door to a terrace or balcony is an outside door: glazed, weather-tight, never the bedroom door of the inside.* Why: an inside door on the open air leaks and looks wrong from outside. Asked of 2 element(s).
- **A4 light wells** (minor, fixed): *Why does this basement window have a light well? Only where the ground outside stands above its sill; a terrace below the sill lights it on its own.* Why: a light well where none is needed is a concrete box in the garden. Asked of 2 element(s).
- **A1 rain water** (minor, ok): *Where does the rain go? Every gutter must drain into a downpipe fixed to a wall all the way down to the ground: no pipe in front of a loggia, across a window or in the air.* Why: rain running down a facade stains it and a pipe in the air looks like a mistake. Asked of 1 element(s).
- **G1 trees** (minor, ok): *Does every tree and shrub stand on open ground, clear of the house, the pools, the paths and the terraces?* Why: a tree through a terrace or in front of a door is a reading or placement error. Asked of 21 element(s).

## What the user taught me

25 lessons from the user's requests and corrections (wenart/blender/architect_lessons.json); each is checked on every project.

| Lesson | What I check | Here |
|---|---|---|
| UL01 | Every outer wall carries a facade finish (render, stone, cladding) with a plinth, slab bands, copings and window surrounds; never bare concrete. | build |
| UL02 | Nothing sticks out of the facade unless drawn: a basement window gets a light well or a court only when the ground outside is above its sill, never on a terrace that lies below it. | build, B1 ok |
| UL03 | Outer doors and windows are real products from the library with see-through glass; a door to a terrace is mostly glass, in the windows' frame finish. | D3 fixed, build |
| UL04 | The site is furnished like a real garden: trees, shrubs, hedges, lawn, cars on the parking, from the library. | build, G1 ok |
| UL05 | Gutters run along every eave and downpipes run down solid walls to the ground; nothing hangs in the air. | build |
| UL06 | The roof is closed and real: no gaps, eaves with a fascia, ridges and hips, its form following the plan. | build |
| UL07 | Every terrace and pool deck can be reached: from a door at its level or by steps and a path from the site's paths. | A2 fixed, A5 ok |
| UL08 | The architect asks every rule of every element (thousands of questions), fixes what code can fix safely, asks the user the rest with options, and the AI on the pod answers the open ones. | build |
| UL09 | The top-down views look from the north-east at about 35 degrees with the walls cut at 0.6 m and the windows marked. | build |
| UL10 | Reach a terrace from outside (steps and a path) before turning a drawn window into a door: drawn openings stay as drawn. | A5 ok, A2 fixed |
| UL11 | A window between two rooms is a reading error: it moves to the dark room's outer wall. | W2 ok |
| UL12 | A habitable room gets glass of at least a tenth of its floor; too little glass: the windows are enlarged. | L1 ok |
| UL13 | A separate kitchen may be meant: the architect asks before joining rooms and keeps the answer. | C2 answered |
| UL14 | No two pieces of furniture cut each other in any render; clashes are planned apart before the build. | F5 fixed |
| UL15 | A terrace beside the house sits at the floor its doors and windows serve, never half way between floors; no pit is cut into a terrace; mirrored twins match; walls over 1.2 m step back as planted terraces or carry a guard. | build, A2 fixed, K2 fixed |
| UL16 | The furniture of a room and of the house is one coherent set: one design language, one or two wood tones, one metal finish, a colour palette from the style (60-30-10), real proportions, and one statement piece per room. | S2 fixed |
| UL17 | Rooms are styled like a magazine shoot: every table, console, shelf and nightstand carries a small group of decor, walls carry art, every living room and bedroom has plants, lamps, a rug, cushions and a throw. | S3 open (1 open) |
| UL18 | Every room is complete for its use: a sofa with a coffee table, side tables, a floor lamp and a rug; a bed with two nightstands and lamps (and a bench in a large room); a dining table with its chairs, a pendant and a sideboard. | S4 open (1 open) |
| UL19 | Cushions and pillows rest on and lean against their seat or headboard and sink a little into it; no cushion on a model that has its own. | build |
| UL20 | A terrace is furnished with outdoor pieces (metal, teak, rattan, stone; no indoor desks or upholstery) and reached through a glazed door. | U1 ok, D3 fixed |
| UL21 | Details are built like real products: stairs with comfortable risers, tread plates with nosings, a balustrade and a handrail; guards of 1 m with gaps under 0.11 m; a coping on every parapet; one balustrade language for the house. | K1 fixed, K2 fixed, K3 fixed |
| UL22 | Every fix is a general rule with a test, never a patch for one project. | process |
| UL23 | Library models are chosen for the look of the render (fitting together, carrying the style), not for their licence (licence_mode relaxed). | process |
| UL24 | A reading problem is fixed in the reader, so the pod handles the next drawing of that kind alone. | process |
| UL25 | Every new request or correction of the user becomes a lesson here (python -m wenart.agent.lessons add); open lessons are checked by the AI architect on every run until a rule checks them. | process |
