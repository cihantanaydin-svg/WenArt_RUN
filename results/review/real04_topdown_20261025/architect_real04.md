# Architect's review: real04

15 questions, 18 change(s), 6 open point(s).

## The architect's questions for you

1. **L1 daylight** (major): r_L0_yatak_odasi_3 (bedroom, 16.6 m2) has no window to the outside; its only window win_L0_006 looks into r_L0_yatak_odasi_2. *Is win_L0_006 on the outer wall in the drawing (a reading error the architect should correct), or a borrowed-light window on purpose?* (answer key `L1:r_L0_yatak_odasi_3`)
2. **L1 daylight** (major): r_L0_yatak_odasi_4 (bedroom, 16.7 m2) has no window to the outside; its only window win_L0_005 looks into r_L0_yatak_odasi. *Is win_L0_005 on the outer wall in the drawing (a reading error the architect should correct), or a borrowed-light window on purpose?* (answer key `L1:r_L0_yatak_odasi_4`)
3. **L1 daylight** (major): r_L1_oyun_aktivite_ve_dinlenme_odasi (other, 40.5 m2) has 1.63 m2 of glass: 1/25 of its floor. *Should the windows of r_L1_oyun_aktivite_ve_dinlenme_odasi be larger?* (answer key `L1:r_L1_oyun_aktivite_ve_dinlenme_odasi`)
4. **L1 daylight** (major): r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (other, 40.5 m2) has 1.63 m2 of glass: 1/25 of its floor. *Should the windows of r_L1_oyun_aktivite_ve_dinlenme_odasi_2 be larger?* (answer key `L1:r_L1_oyun_aktivite_ve_dinlenme_odasi_2`)
5. **C2 kitchen** (minor): r_L-1_mutfak has no door or opening to a living or dining space (through the hall to r_L-1_salon). *Is r_L-1_mutfak open to the living space (the drawing shows a wall), or is it a separate kitchen on purpose?* (answer key `C2:r_L-1_mutfak`)
6. **C2 kitchen** (minor): r_L-1_mutfak_2 has no door or opening to a living or dining space (through the hall to r_L-1_salon_2). *Is r_L-1_mutfak_2 open to the living space (the drawing shows a wall), or is it a separate kitchen on purpose?* (answer key `C2:r_L-1_mutfak_2`)

Answers go into the building's `architect_answers` (`{"L1:<room>": "store room"}` and so on); the next run acts on them and does not ask again.

## B1 arrival (ok)

*Where do I come in? Is there a path from the street to the main entrance door?* Why: a front door nobody can find or reach on foot is the first thing a visitor notices.

- **d_L0_006**: main entrance d_L0_006: reached by path_d_L0_006_d_L0_014

## B2 parking (ok)

*Where do I leave the car, and how do I walk from it to the front door?* Why: a parking with no path to the entrance makes people cross the lawn or the driveway's kerb.

- **spk_001**: parking spk_001 meets a path

## A2 access (fixed)

*How do people get to each terrace and pool deck? From the house through a door at its level, or from the garden by steps that no railing closes.* Why: a terrace or pool nobody can walk to is useless and unsafe.

- **sp_001**: pool deck sp_001 at -3.00 m: reached by steps to the garden
- **sp_001**: pool deck sp_001 at -3.00 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_001 to the site's path (13.8 m; inferred)
- **sp_002**: pool deck sp_002 at -1.40 m: no door from the house at its level, no open steps -> the glass railing on edge 1 closed its steps: the railing now stops 0.10 m beside the flight
- **sp_002**: pool deck sp_002 at -1.40 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_002 to the site's path (18.6 m; inferred)
- **sp_003**: pool deck sp_003 at +1.55 m: reached by steps to the garden
- **sp_003**: pool deck sp_003 at +1.55 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_003 to the site's path (10.2 m; inferred)
- **sp_004**: pool deck sp_004 at -0.20 m: no door from the house at its level, no open steps -> the glass railing on edge 6 closed its steps: the railing now stops 0.10 m beside the flight
- **sp_004**: pool deck sp_004 at -0.20 m: its steps led onto the lawn and nowhere else -> a path from the steps of sp_004 to the site's path (20.2 m; inferred)

## A5 decks without a door (ok)

*This terrace lies at the floor level of the rooms beside it, right outside their windows, and no door opens onto it: can people still reach it from outside? (The drawn windows stay windows; only when no outside way exists does the architect ask you about a door.)* Why: a deck at the floor's level begs for a door; the drawings decide it.

- **sp_001**: pool deck sp_001 lies at the L-1 floor (-3.00 m) outside window(s) win_L-1_003; no door opens onto it -> reached from outside: its steps and a path to the site's paths (A2); the windows stay as drawn

## E1 outside doors (ok)

*Does every outside door open onto something: the ground, a terrace, a balcony or steps?* Why: a door into the air or below the ground is a drawing or level error.

- **doors**: every outside door lands on the ground, a terrace or steps

## C1 circulation (ok)

*Can I reach every room from the entrance, and without walking through somebody's bedroom?* Why: a room you can only reach through a bedroom is a planning fault (an en-suite bathroom or dressing room is the exception).

- **plan**: all 30 rooms reached from r_L0_koridor, r_L0_koridor_2; none only through a bedroom

## C2 kitchen (open)

*Is the kitchen next to where people eat and sit (a door or an opening to the living or dining space)?* Why: carrying plates through a hall or another room every day is a sign the plan is not working.

- **r_L-1_mutfak**: r_L-1_mutfak has no door or opening to a living or dining space (through the hall to r_L-1_salon) **Question for you: Is r_L-1_mutfak open to the living space (the drawing shows a wall), or is it a separate kitchen on purpose?**
- **r_L-1_mutfak_2**: r_L-1_mutfak_2 has no door or opening to a living or dining space (through the hall to r_L-1_salon_2) **Question for you: Is r_L-1_mutfak_2 open to the living space (the drawing shows a wall), or is it a separate kitchen on purpose?**

## L1 daylight (open)

*Does every bedroom, living room and kitchen get daylight: a window with glass of at least a tenth of its floor?* Why: a habitable room without enough daylight feels like a cellar; building codes ask for about 1/10.

- **r_L0_yatak_odasi_3**: r_L0_yatak_odasi_3 (bedroom, 16.6 m2) has no window to the outside; its only window win_L0_006 looks into r_L0_yatak_odasi_2 **Question for you: Is win_L0_006 on the outer wall in the drawing (a reading error the architect should correct), or a borrowed-light window on purpose?**
- **r_L0_yatak_odasi_4**: r_L0_yatak_odasi_4 (bedroom, 16.7 m2) has no window to the outside; its only window win_L0_005 looks into r_L0_yatak_odasi **Question for you: Is win_L0_005 on the outer wall in the drawing (a reading error the architect should correct), or a borrowed-light window on purpose?**
- **r_L1_oyun_aktivite_ve_dinlenme_odasi**: r_L1_oyun_aktivite_ve_dinlenme_odasi (other, 40.5 m2) has 1.63 m2 of glass: 1/25 of its floor **Question for you: Should the windows of r_L1_oyun_aktivite_ve_dinlenme_odasi be larger?**
- **r_L1_oyun_aktivite_ve_dinlenme_odasi_2**: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (other, 40.5 m2) has 1.63 m2 of glass: 1/25 of its floor **Question for you: Should the windows of r_L1_oyun_aktivite_ve_dinlenme_odasi_2 be larger?**

## L2 fresh air (fixed)

*Can every bathroom and kitchen be aired: a window, else a mechanical extract?* Why: steam and cooking smells need a way out.

- **r_L-1_banyo**: r_L-1_banyo (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **r_L-1_banyo_2**: r_L-1_banyo_2 (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **r_L0_e_banyo**: r_L0_e_banyo (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **r_L0_e_banyo_2**: r_L0_e_banyo_2 (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **r_L0_banyo**: r_L0_banyo (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **r_L0_banyo_2**: r_L0_banyo_2 (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **r_L1_banyo**: r_L1_banyo (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)
- **r_L1_banyo_2**: r_L1_banyo_2 (bathroom) has no window -> a mechanical extract is assumed (inferred; listed in the report)

## P1 privacy (ok)

*Does a bathroom door open straight into the living room, the dining space or the kitchen?* Why: a toilet door in the room where people eat or receive guests is uncomfortable for everybody.

- nothing to look at in this building

## R1 room size (ok)

*Is every bedroom wide enough for its bed with room to walk around it?* Why: a bedroom narrower than about 2.4 m leaves no passage beside a bed.

- nothing to look at in this building

## R2 use (ok)

*Is every room furnished for what it is (a bed in each bedroom, a sofa in the living room, a table where people eat, a WC and a basin in each bathroom)?* Why: a room without its main piece reads as unfinished in the renders.

- nothing to look at in this building

## S1 falls (ok)

*Where could somebody fall more than half a metre: is every such terrace, pool deck and roof terrace edge guarded?* Why: an unguarded drop is the first safety question of every design review.

- **sp_001**: sp_001: 7 edge(s) over a drop of more than 0.5 m carry a glass railing (max drop 1.86 m)
- **sp_002**: sp_002: 6 edge(s) over a drop of more than 0.5 m carry a glass railing (max drop 1.38 m)
- **sp_003**: sp_003: 5 edge(s) over a drop of more than 0.5 m carry a glass railing (max drop 1.08 m)
- **sp_004**: sp_004: 7 edge(s) over a drop of more than 0.5 m carry a glass railing (max drop 1.69 m)
- **ro_001**: roof terrace ro_001: guarded to 1.00 m (parapet 0.60 m + glass railing)
- **ro_002**: roof terrace ro_002: guarded to 1.00 m (parapet 0.60 m + glass railing)

## A3 outside doors (fixed)

*Which doors open to the open air? A door to a terrace or balcony is an outside door: glazed, weather-tight, never the bedroom door of the inside.* Why: an inside door on the open air leaks and looks wrong from outside.

- **d_L1_003**: door d_L1_003 from r_L1_koridor to the open-air r_L1_teras was an inside door -> built as a glazed outside door
- **d_L1_006**: door d_L1_006 from r_L1_koridor_2 to the open-air r_L1_teras_2 was an inside door -> built as a glazed outside door

## A4 light wells (fixed)

*Why does this basement window have a light well? Only where the ground outside stands above its sill; a terrace below the sill lights it on its own.* Why: a light well where none is needed is a concrete box in the garden.

- **win_L-1_004**: window sill 1.18 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 5.36 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn)
- **win_L-1_003**: the terrace sp_001 at -3.00 m lies under the sill -2.10 m: no light well -> light well left out
