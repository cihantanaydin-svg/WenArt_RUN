# Argus: the audit of real06

Argus checks everything a run makes, not only the looks: what the documents hold against the model (nothing lost between stages, every label and symbol used), the run itself (stages, warnings nobody acted on, tests, time), the model's sense, the inspector's and the judge's findings. Every finding has a kind (where such problems arise and the guards that catch them), an owner (the stage that caused it) and, where the run can carry it out, a fix.

Score **11.1** / 100 (100 = nothing open; 10 points per critical, 3 per major, 0.5 per minor). Open: 12 critical, 82 major, 70 minor; 27 notes.

## Lines

| line | findings | checked | note |
|---|---|---|---|
| conservation | 26 | {"reading": 243, "fit": 243, "layout": 249, "decor": 249, "agent": 249, "final": 249, "build": 248} |  |
| process | 24 | {"stages": 27, "warnings": 131, "test_reports": 1, "missing_records": []} |  |
| model | 0 | {"M1": 16, "M2": 8, "M6": 52, "M7": 8, "M3": 0, "M4": 6, "M5": 7, "M8": 4} |  |
| inspector | 0 | {"round": 1, "seen": 0, "visitor": 0, "fixed": 0, "handed": 0, "open": 0, "dropped": 0, "architect_open": 0, "architect_open_major": 0, "model_checks": {"M1": 0 |  |
| judge | 173 | {"views": 34, "mean": 2.26} |  |
| sense | 2 | {"rooms": 12, "joins": 15, "reached": 12} |  |
| render_check | 10 | {"views": 34, "required_elements": 62, "drawn_pieces": 57, "elevations": 4} |  |
| consistency | 0 | {"critic_findings": 0} |  |
| ledger | 10 | {"by_kind": {"element:furniture": {"items": 57, "must": 57, "accounted": 57, "unaccounted": 0}, "element:openings": {"items": 36, "must": 36, "accounted": 36, " |  |
| plan_vs_model | 10 | {"levels": 2, "elevation_calls": 6, "plans": {"L0": "strokes", "L1": "strokes"}} |  |
| argus_ai | 0 | {} |  |

## Problem kinds

| kind | critical | major | minor | with a fix | owners | arises | guards |
|---|---|---|---|---|---|---|---|
| misread | 8 | 12 | 11 | 2 | building, architect, reading, fit, layout | reading | plan_vs_model (B*), the room-sense rules (G*, R*), model review M7 |
| taste | 2 | 49 | 28 | 4 | building, scene, fit, agent | fit, decor, opening models | judge (J*), visitor checks Q5, Q7, the fit's matched sets |
| geometry | 2 | 2 | 10 | 0 | scene, build | layout, agent | code critic (F*, G*), architect F-rules |
| lost | 0 | 8 | 16 | 7 | build, building, cameras, render, reading, site | any stage boundary: reading -> building, fit, layout, build, render | ledger (A*), conservation (C*), plan_vs_model (B*), process (P*) |
| no_sense | 0 | 7 | 2 | 0 |  | architect, build | sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*) |
| process | 0 | 3 | 3 | 1 | building, scene, tests, agent, check | scheduler | process (P*) |
| silent | 0 | 1 | 0 | 0 | scene | any stage | process P2 (warnings that say something was left out) |

## geometry: pieces through walls or each other, blocked doors and windows, no walkway

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | f_L1_009 | A second double bed (f_L1_009) is duplicated on top of the first (f_L1_006). The frames and mattresses intersect and cut through each other, which is a broken/overlapping model state. | judge:F9, judge:D1 |  |  |
| critical | f_L1_016 | There is a broken, floating object (looks like a shattered piece of furniture or a glitch) resting on the grey sofa. This is a major rendering error. | judge:D1 |  |  |
| major | L0:S2 | scene check S2 on L0: 1 of 24 failed | process:P5 | build |  |
| major | o_L0_001 | The large opening in the wall is a raw, unframed hole with a floating horizontal bar, which looks like a broken model or a construction error rather than a designed feature. | judge:F9 |  |  |
| minor | dec_L0_009 | decor that could not rest on its host: decor cushion dec_L0_009 on f_L0_008: not rested (67% of the footprint over the support < 80%); not built | process:P2, process:P5 | scene |  |
| minor | dec_L1_017 | decor that could not rest on its host: decor plant_small dec_L1_017 on f_L1_030: not rested (no top found on the built host (attempt 2)); not built | process:P2, process:P5 | scene |  |
| minor | f_L1_007 | The desk is placed directly under the window, which is a common but often awkward placement. It blocks the window sill and feels cramped, as if it was dropped in without considering the room's flow. | judge:Q6 |  |  |
| minor | f_L1_012 | The bed is cut off by the camera frame, making it look like it's floating or improperly placed. The headboard is not visible. | judge:F9 |  |  |
| minor | f_L1_023 | The toilet (f_L1_023) is only visible as a small, cut-off fragment in the bottom-left corner. Its placement is awkward and it does not contribute to a coherent view of the room. | judge:F9 |  |  |
| minor | o_L0_002 | The outdoor environment is a flat, featureless green plane with a hard horizon line. There is no landscaping, paving texture, or context, which makes the building look like it is floating in a void. | judge:F9 |  |  |
| minor | r_L1_oda | The walls are a flat, untextured beige. The lack of any material detail, lighting, or shadowing makes the space feel like a grey-box model rather than a real room. | judge:F9 |  |  |
| minor | r_L1_soyunma_odasi | The walls are a flat, untextured grey plaster. This 'grey box' look is a clear sign of an unfinished model, not a rendered, client-ready space. | judge:F9 |  |  |
| minor | w_L0_001 | The whole exterior is set on a flat, textureless green field with a hard horizon and no ground plane, paving, driveway or planting, which makes the render look like an untextured grey-box study instead of a believable house. | judge:F9 |  |  |
| minor | win_L1_008 | The sunlight coming through the window is blown out and creates harsh, unrealistic white patches on the floor and the white sofa, indicating a lighting problem. | judge:F9 |  |  |

## lost: something the documents or an earlier stage hold is missing from the model (a labelled veranda, drawn site symbols, a room, an opening, a piece)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | TEXT:2772EB | the documents name a washing_machine ('çamaşır mak.') on L1; the model has f_L1_021 washbasin, f_L1_024 toilet within 1.2 m | ledger:A6 | reading | {'action': 'add_piece', 'type': 'washing_machine', 'level_id': 'L1', 'anchor': [7.981, 12.109], 'named_by': 'TEXT:2772EB'} |
| major | TEXT:29ABD3 | the documents name a dresser ('*SIFONIYER') on L1; the model has f_L1_019 unknown (not built) within 1.2 m | ledger:A6 | reading | {'action': 'type_piece', 'element_id': 'f_L1_019', 'type': 'dresser', 'named_by': 'TEXT:29ABD3'} |
| major | TEXT:29AC0C | the documents name a dresser ('*SIFONIYER') on L1; the model has f_L1_007 desk, f_L1_008 unknown (not built), f_L1_006 bed_double within 1.2 m | ledger:A6 | reading | {'action': 'type_piece', 'element_id': 'f_L1_008', 'type': 'dresser', 'named_by': 'TEXT:29AC0C'} |
| major | TEXT:29AC25 | the documents name a dresser ('*SIFONIYER') on L1; the model has no piece within 1.2 m | ledger:A6 | reading | {'action': 'add_piece', 'type': 'dresser', 'level_id': 'L1', 'anchor': [8.106, 4.909], 'named_by': 'TEXT:29AC25'} |
| major | d_L1_007 | door d_L1_007 (from_documents) is not seen in 1 of the 2 view(s) that must show it: cam_r_L1_ebeveyn_y_odasi_2 | render:K1 | render |  |
| major | f_L1_031 | The plan draws a shower (f_L1_031) in the bathroom (BANYO) which is not built in the model. | plan_vs_model:B8 | furniture |  |
| major | r_L0_mutfak:TEXT:294BCF | the documents name a space 'ANTRE m²' that is a second label of room r_L0_mutfak (Mutfak, kitchen): it is not a room of its own in the model | ledger:A3 | reading | {'action': 'split_room', 'room_id': 'r_L0_mutfak', 'label': 'ANTRE m²', 'anchor': [5.14, 10.809], 'area_m2': None} |
| major | win_L0_007 | window win_L0_007 (from_documents) is not seen in 1 of the 2 view(s) that must show it: cam_r_L0_mutfak_3 | render:K1 | render |  |
| minor | TEXT:294BCE | printed area '9,00 m²' of 'HOL' on L1 is not used: the area check of that space is lost | ledger:A4 | reading | {'action': 'check_area_label', 'label': 'HOL', 'text': '9,00 m²', 'anchor': [5.031, 9.884]} |
| minor | entity types not read | source entities the reading did not read (the ledger checks what they hold): real06.dwg: entity types not read: ATTDEF x28 | process:P2 | building |  |
| minor | f_L1_002 | The plan draws a piece of furniture (f_L1_002) in the child's room (ÇOCUK ODASI) which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_003 | The plan draws a piece of furniture (f_L1_003) in the child's room (ÇOCUK ODASI) which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_004 | The plan draws a piece of furniture (f_L1_004) in the child's room (ÇOCUK ODASI) which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_008 | The plan draws a piece of furniture (f_L1_008) in the child's room (ÇOCUK ODASI) which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_010 | The plan draws a nightstand (f_L1_010) in the child's room which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_011 | The plan draws a piece of furniture (f_L1_011) in the child's room (ÇOCUK ODASI) which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_014 | The plan draws a piece of furniture (f_L1_014) in the living room (ODA) which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_015 | The plan draws a piece of furniture (f_L1_015) in the living room (ODA) which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_019 | The plan draws a piece of furniture (f_L1_019) in the master bedroom (EBEVEYN Y.ODASI) which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | r_L0_salon:TEXT:295858 | the documents name a space 'YEMEK BÖLÜMÜ' (17.35 m²) that is a second label of room r_L0_salon (Salon, living): it is not a room of its own in the model | ledger:A3 | reading | {'action': 'split_room', 'room_id': 'r_L0_salon', 'label': 'YEMEK BÖLÜMÜ', 'anchor': [1.815, 6.334], 'area_m2': 17.35} |
| minor | site | items the reading found and no stage used: site: 42 decor read outside the walls of L1 not used (the site is the ground floor's, L0); 26 of them repeat the ground plan's symbols at the same place (site.decor_other_levels) | process:P2 | building |  |
| minor | warning:7 | the reading says: real06.dwg: walls drawn as face lines: layer 'SIVA' chosen by evidence (closes in 5 of 6 labelled rooms, 85% of its long strokes pair, widths 0.15, 0.25, 0.30, 0.35, 0.40, 0.45, 0.49, 0.50 m); runner-up 'DUVAR' (5 of 6); 6 other wall primitives off that layer left out | ledger:A7 | reading |  |
| minor | warning:8 | the reading says: real06.dwg: walls drawn as face lines: layer 'SIVA' chosen by evidence (closes in 7 of 8 labelled rooms, 84% of its long strokes pair, widths 0.15, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.54 m); runner-up 'DUVAR' (7 of 8); 64 other wall primitives off that layer left out | ledger:A7 | reading |  |
| minor | warning:9 | the reading says: site: 42 decor read outside the walls of L1 not used (the site is the ground floor's, L0); 26 of them repeat the ground plan's symbols at the same place (site.decor_other_levels) | ledger:A7 | site |  |
| info | 2 elements | not built: the model of f_L1_009 has its own cushions/pillows (dec_L1_009, dec_L1_010) | conservation:C6 | build |  |
| info | 2 elements | not built: drawn on 'AKS': a structural grid bubble (the axis label), drawing annotation; not built (sd_L0_006, sd_L0_037) | conservation:C6 | build |  |
| info | 2 elements | not built: drawn on 'KOLON': a column; built as a post of the veranda os_L0_veranda (sd_L0_009, sd_L0_010) | conservation:C6 | build |  |
| info | 2 elements | not built: drawn on 'kot': a level mark symbol; not built (sd_L0_015, sd_L0_025) | conservation:C6 | build |  |
| info | 2 elements | not built: exterior label: its surface is built from site.paving / parking / grass (sa_L0_veranda, sa_L1_balkon) | conservation:C6 | build |  |
| info | 26 elements | not built: drawn on 'AKS YAZI': a structural grid bubble (the axis label), drawing annotation; not built (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_007, sd_L0_008, sd_L0_012 ...) | conservation:C6 | build |  |
| info | 6 elements | not built: untyped (CLAUDE.md: no untyped piece is built) (f_L0_009, f_L0_010, f_L1_011, f_L1_014, f_L1_015, f_L1_019) | conservation:C6 | build |  |
| info | 7 elements | not built: drawn on 'DENIZLIK': a window sill or coping line; not built (sd_L0_011, sd_L0_017, sd_L0_021, sd_L0_024, sd_L0_028, sd_L0_035, sd_L0_036) | conservation:C6 | build |  |
| info | dec_L1_012 | not built: its host f_L1_010 is not built (dec_L1_012) | conservation:C6 | build |  |
| info | f_L0_002 | not built: architect F5: f_L0_002 (kitchen_counter) lies inside f_L0_031 (kitchen_counter): one object read twice; built once (f_L0_002) | conservation:C6 | build |  |
| info | f_L0_003 | not built: drawn inside the kitchen_counter f_L0_002 (60% or more of it): the same piece drawn twice, or a part of it (not built) (f_L0_003) | conservation:C6 | build |  |
| info | f_L0_004 | not built: the kitchen run drawn as one outline with its fixtures (sink: 8 circles): replaced by its counter legs f_L0_031, f_L0_032 along the walls (not built); plan crop recognition/reading/f_L0_004_ctx.png (f_L0_004) | conservation:C6 | build |  |
| info | f_L0_005 | not built: outline 3.89 x 1.65 m around 3 other piece(s) (f_L0_006, f_L0_007, f_L0_008): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_005) | conservation:C6 | build |  |
| info | f_L0_006 | not built: outline 2.12 x 0.78 m around 1 other piece(s) (f_L0_009): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_006) | conservation:C6 | build |  |
| info | f_L0_014 | not built: outline 1.52 x 0.78 m around 2 other piece(s) (f_L0_012, f_L0_013): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_014) | conservation:C6 | build |  |
| info | f_L1_001 | not built: arrives from f_L0_001 (L0 -> L1): the drawn upper end of that stair; no level above, not built again (f_L1_001) | conservation:C6 | build |  |
| info | f_L1_002 | not built: cluster larger than 4.5 m on a side: a group of drawn pieces, not built (f_L1_002) | conservation:C6 | build |  |
| info | f_L1_003 | not built: 2.25 x 0.18 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_003) | conservation:C6 | build |  |
| info | f_L1_004 | not built: 0.50 x 0.12 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_004) | conservation:C6 | build |  |
| info | f_L1_008 | not built: drawn inside bed_double f_L1_006 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) (f_L1_008) | conservation:C6 | build |  |
| info | f_L1_010 | not built: architect F5: it cut f_L1_009 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built (f_L1_010) | conservation:C6 | build |  |
| info | f_L1_031 | not built: the answer to AI.remove_piece:f_L1_031: not built (f_L1_031) | conservation:C6 | build |  |
| info | o_L1_001 | o_L1_001 (opening) of the final stage is gone after the build stage, named in openings[38].evidence[2].text: one opening with o_L1_001 (read twice): 1.98 m wide | conservation:C1 | build |  |
| info | r_L0_oda | room Oda (2.1 m2) has no view: no furniture after layout and decor and 2.13 m2 < 2.5 m2: no view (docs/milestone7.md §6.2) | process:P6 | cameras |  |
| info | sd_L0_014 | not built: drawn on 'KAPI': a door symbol; not built (sd_L0_014) | conservation:C6 | build |  |
| info | sd_L0_016 | not built: drawn on 'TARAMA': a hatch; not built (sd_L0_016) | conservation:C6 | build |  |
| info | sd_L0_018 | not built: drawn on 'BALKON': a detail of an outdoor space (its edge or steps); built with the veranda os_L0_veranda (its drawn steps or edge) (sd_L0_018) | conservation:C6 | build |  |

## misread: the reading typed, sized or placed something wrong (armchairs read as tables with chairs, a vanity read as a kitchen counter)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | f_L0_002 | The kitchen is missing its main functional anchor: there is no hob or cooktop on the worktop, making the room feel incomplete and non-functional. | judge:Q4 |  |  |
| critical | f_L0_026 | The washbasin is a main piece of the bathroom but is completely missing from the frame. A bathroom render that shows only a toilet and a door makes no sense to a client. | judge:Q4 |  |  |
| critical | f_L1_017 | The scheduled armchair (and its pair f_L1_018) is absent; the bedroom has no seating or reading corner, so the main group is just a bed and the room feels incomplete. | judge:Q4 |  |  |
| critical | f_L1_020 | The shower (f_L1_020) is completely missing from the frame. A bathroom render that shows no shower, no toilet, and only a fragment of a sink fails to present the room's main function. | judge:Q4 |  |  |
| critical | f_L1_024 | The toilet (f_L1_024) is missing from the render. A bathroom without a toilet is a fundamental, client-visible failure. | judge:Q4 |  |  |
| critical | f_L1_029 | Bathroom with no basin: the washbasin is listed for this room but is not visible anywhere in the frame, so the room is missing its main fixture. | judge:Q4 |  |  |
| critical | f_L1_031 | The shower is missing entirely; a bathroom with no shower/wet zone makes no sense. | judge:Q4, sense:N5 | architect | retype_piece |
| critical | r_L1_soyunma_odasi | The dressing room (soyunma odasi) is completely empty. It has no wardrobe, bench, mirror, or any of the fixtures a dressing room requires. This is a missing-anchor failure: the room's entire purpose is absent. | judge:Q4 |  |  |
| major | f_L0_015 | The coffee table (f_L0_015) is listed in the room data but is missing from the render. This leaves the seating area without a central anchor, making the layout feel incomplete and the space between the armchairs and sofa empty. | judge:Q4 |  |  |
| major | f_L0_024 | The toilet (f_L0_024) is not visible in the frame. A bathroom render that omits the toilet looks unfinished and makes the room feel empty. | judge:Q4 |  |  |
| major | f_L0_033 | The wall cabinets listed in the JSON are not visible in the render, leaving the upper wall completely bare and the kitchen feeling unfinished. | judge:Q4 |  |  |
| major | f_L0_036 | The shower (f_L0_036) is only hinted at by a glass edge on the right; it is not legible as a designed shower zone, leaving the room feeling incomplete. | judge:Q4 |  |  |
| major | f_L1_010 | The nightstand (f_L1_010) is listed but not visible in the render. The bed has no bedside table, leaving the main furniture group incomplete. | judge:Q4 |  |  |
| major | f_L1_011 | r_L1_banyo: bathroom without a shower or a bathtub, while f_L1_011 (unknown, not built: untyped (CLAUDE.md: no untyped piece is built), 2.42 x 0.98 m) stands in it; the AI passes said: The object has a curved shape and is in a bathroom, likely a bathtub or shower, not matchi / The object's footprint and shape match a bunk bed, with a headboard-like line and a ladder: most likely the missing shower | sense:N5 | reading | retype_piece |
| major | f_L1_022 | The floor lamp is missing, leaving the only light source as a small bedside lamp; the right half of the room is dark and unlit, which reads as an unfinished render. | judge:Q4 |  |  |
| major | f_L1_025 | The second washbasin (f_L1_025) is missing. Only one basin is visible, leaving the room feeling sparse and unfinished. | judge:Q4 |  |  |
| major | f_L1_027 | The room is missing its main anchor piece, the floor lamp (f_L1_027). A living room with only two mismatched sofas and no lighting or decor looks like an empty, unfinished space. | judge:Q4 |  |  |
| major | r_L1_banyo | The room is largely empty. Aside from the basic toilet and basin, there is no shower, no storage, and no decor. This makes the space feel like an unfinished shell rather than a designed, livable room. | judge:Q4 |  |  |
| major | r_L1_hol | The hall is completely empty and unfinished. There is no lighting, no skirting boards, no floor finish, and no decor. It looks like a grey-box construction site, not a livable space. | judge:Q4 |  |  |
| major | r_L1_oda | The room is essentially empty. A 3.1 m2 hall should have some sense of purpose or at least be styled, but this is just a bare box with a door. | judge:Q4 |  |  |
| minor | d_L0_004 | door d_L0_004 looks like something else in 1 view(s): cam_r_L0_salon_1 (seen as wall_art) | render:K2 | fit |  |
| minor | f_L0_012 | The potted plant (f_L0_012) is listed in the room data but is missing from the render. The lack of greenery or vertical elements makes the room feel sterile and flat. | judge:Q4 |  |  |
| minor | f_L0_020 | The sink is present but the surrounding area is bare; there is no faucet visible in the main view, and the sink basin looks like a simple cutout rather than a finished fixture. | judge:Q4 |  |  |
| minor | f_L0_027 | ottoman f_L0_027 differs from the drawing (tolerance 0.05 m): 0.86 m from its drawn place; size [0.5, 0.5] vs drawn [0.446, 0.325] | render:K3 | layout |  |
| minor | f_L0_028 | ottoman f_L0_028 differs from the drawing (tolerance 0.05 m): 0.09 m from its drawn place; size [0.5, 0.5] vs drawn [0.447, 0.325] | render:K3 | layout |  |
| minor | f_L0_029 | ottoman f_L0_029 differs from the drawing (tolerance 0.05 m): 0.63 m from its drawn place; size [0.5, 0.5] vs drawn [0.447, 0.325] | render:K3 | layout |  |
| minor | f_L0_030 | ottoman f_L0_030 differs from the drawing (tolerance 0.05 m): 0.07 m from its drawn place; size [0.5, 0.5] vs drawn [0.446, 0.325] | render:K3 | layout |  |
| minor | f_L1_007 | desk f_L1_007 differs from the drawing (tolerance 0.05 m): 0.15 m from its drawn place | render:K3 | layout |  |
| minor | f_L1_021 | The single visible washbasin (f_L1_021) is the only piece of furniture, which emphasizes the emptiness of the room and makes the render look like a placeholder. | judge:Q4 |  |  |
| minor | room '...' has more labels | one room outline holds the labels of two rooms (a wall not read?): room '...' has more labels: 2 cases, e.g. L0: room 'Salon' has more labels: YEMEK BÖLÜMÜ; the label with the largest printed area (else the first) kept | process:P2 | building |  |
| minor | sym_L1_008 | a piece whose type the room does not allow, kept unverified: sym_L1_008: sofa is not a type allowed in a bedroom room: kept, unverified | process:P2 | building |  |

## no_sense: the model makes no sense to a visitor (a door into the air, a basin at knee height, stairs running into each other, a railing across a door)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | d_L0_001 | The main entrance is a dark, undefined void under the porch. There is no visible door leaf, handle, or threshold, making the entry point look unfinished and inaccessible. | judge:Q9 |  |  |
| major | d_L1_001 | The door leaf is a flat slab with no frame, no visible threshold and no destination behind it; it opens onto a blank wall, so it makes no sense in the plan. | judge:Q1, judge:Q3 |  |  |
| major | d_L1_009 | The door opens directly into the basin/toilet cluster, blocking the approach to the fixtures. | judge:Q9 |  |  |
| major | f_L1_001 | The stair opening and landing edge have a flimsy, incomplete guard. The glass panel is a thin placeholder with a large open gap below it and no proper balustrade, which is a clear fall risk and looks broken. | judge:Q3, judge:Q1 |  |  |
| major | f_L1_025 | The washbasin sits too low and is wedged behind the toilet, so it is not at a usable working height and cannot be reached. | judge:Q2 |  |  |
| major | o_L0_002 | The entrance area is poorly resolved. The steps and handrails are basic, untextured geometry. The large terrace slab to the left is a raw, floating concrete block with no finish, making the whole approach look unfinished and un-stylish. | judge:Q9 |  |  |
| major | o_L1_001 | The balcony railing is a crude, thin wireframe that looks like a construction placeholder. It does not read as a safe, finished guardrail, and the balcony slab itself looks like a floating grey box. | judge:Q3 |  |  |
| minor | w_L0_001 | The downpipes are rendered as simple black lines that look like cracks or shadows rather than functional drainage. They lack the volume and materiality of real pipes. | judge:Q8 |  |  |
| minor | w_L1_001 | The downpipe on the corner is a simple, dark cylinder that looks like a placeholder. It lacks the proper brackets and connection to the gutter that would make it look like a real, functional part of the building. | judge:Q8 |  |  |

## process: the run itself: a stage failed or was skipped, a test failed, time was left unused, a question stayed unanswered

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | big_loop | the big loop did not raise the house score (first 31.34; 0 cycle(s); stop: cycle 1: deadline) | process:P9 | agent | more_cycles |
| major | test_sky_and_window_pulls_reach_their_targets[real06] | test tests.gpu.test_render::test_sky_and_window_pulls_reach_their_targets[real06] failure: AssertionError: real06: [('window panes', 'median pane saturation 0.0526 under 0.065: grey cards, not the sky', [('cam_r_L0_banyo_1', 0.0612), ('cam_r_L0_banyo_3', 0.0971), ('cam_r_L0_mutfak_1', 0.0246), ('cam_r_L0_mutfak_3', 0.0459), ('cam_r_L0_salon_1', 0.0481), ('cam_r_L0_salon_2', 0.0483), ('cam_r_L0_sal | process:P4 | tests |  |
| major | views | 2 view(s) marked for review: cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_3 | render:K4 | check |  |
| minor | elevation r# (all) | a check that could not run: elevation r# (all): 4 cases, e.g. elevation r1 (all): its openings are not checked against the plans (the side needs the north arrow) | process:P2 | building |  |
| minor | elevations | 4 elevation(s) could not be compared with the model (r1, r2, r7, r8): the elevation has neither a view bearing nor a side: nothing to compare | render:K4 | check |  |
| minor | the drawn section r# is not checked point by point against the roof | a check that could not run: the drawn section r5 is not checked point by point against the roof: its ends at s -0.50 / 16.80 m and the roof outline's at -0.28 / 15.03 m along y are up to 1.77 m apart (over 0.30 m: the section does not run one-to-one with the plan); its roof line drops 1.43 m at s 8.55 m on the way up to its highest point (trusses, trims or another roof drawn with it: not one roof  | process:P2 | scene |  |

## silent: a stage noted a problem in a warning and nothing acted on it

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | inferred trees | a stage placed fewer items than it planned: inferred trees: placed 0 of 3 (74 candidates; removed by building 1, path 15, sightline 36, window 66, front 27; most by window; the first pass placed 0, the second pass with the window band narrowed to 4 m added 0) | process:P2 | scene |  |

## taste: the house does not look designed (pieces that do not match, plain or dated rooms, a garage door look)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | f_L1_009 | The bedding on this bed is a crude, melted-looking blob. It does not look like a duvet or pillows; it looks like a failed simulation or a low-poly placeholder. This is the single most embarrassing element in the render. | judge:D3, judge:D2 |  |  |
| critical | f_L1_013 | The main sofa is a crude, low-poly white block. It has no texture, no realistic form, and looks like a placeholder model, not a piece of furniture. | judge:D2, judge:Q5, judge:D3 |  |  |
| major | cam_r_L0_banyo_1 | the judge scores view cam_r_L0_banyo_1 2/5 (a client would not accept it): The render is a near-empty bathroom: the camera is aimed at a blank tiled wall, the toilet is missing from view, and the only visible furniture is a small washbasin. It reads as a grey-box placeholder, not a finished, stylish bathroom. | judge:J1 | agent |  |
| major | cam_r_L0_banyo_2 | the judge scores view cam_r_L0_banyo_2 2/5 (a client would not accept it): The render is a dead-end view of a toilet and a door; the room's other main pieces are not in frame, so it reads as a corridor, not a bathroom. The visible toilet is a dated, bulky two-piece model that clashes with the clean, modern tile and door. The camera is poorly placed, framing a wall corner and a door leaf instead of | judge:J1 | agent |  |
| major | cam_r_L0_mutfak_1 | the judge scores view cam_r_L0_mutfak_1 2/5 (a client would not accept it): The render shows a kitchen that is mostly empty and unfinished. The main run of base cabinets is present, but there is no hob, no upper cabinets, and no visible appliances, so the room reads as a shell rather than a designed kitchen. The large opening in the wall (o_L0_001) is a raw, unframed hole with a strange floating b | judge:J1 | agent |  |
| major | cam_r_L0_mutfak_2 | the judge scores view cam_r_L0_mutfak_2 2/5 (a client would not accept it): The kitchen reads as a single freestanding island with a stone top and a sink, but it is the only piece in a 24.8 m2 room: no wall run, no hob, no tall units, no stools, and the plaster walls and bare tile floor are completely untextured. A client would immediately ask where the cooking and storage are. The one element tha | judge:J1 | agent |  |
| major | cam_r_L0_salon_1 | the judge scores view cam_r_L0_salon_1 2/5 (a client would not accept it): The render shows a disjointed and unfinished living space. The furniture selection is incoherent, mixing a dark, modern ribbed chair with a beige tufted armchair and a large cream sectional, which creates a 'mismatched set' that looks like a showroom display rather than a designed home. Furthermore, the room is missing key  | judge:J1 | agent |  |
| major | cam_r_L0_salon_3 | the judge scores view cam_r_L0_salon_3 2/5 (a client would not accept it): The room is a 55 m2 salon that reads as a showroom of mismatched, cheap-looking pieces. The main sofa group is pushed into the far corner and is not anchored to the room, while the foreground is dominated by a single armchair and a cut-off dining chair. The furniture styles and colours do not belong together, and the two po | judge:J1 | agent |  |
| major | cam_r_L1_banyo_1 | the judge scores view cam_r_L1_banyo_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation. The room is listed as a bathroom with a shower (f_L1_031), yet the shower is completely missing, leaving a large, empty, unexplained corner. The visible fixtures (basin and toilet) are basic, and the room lacks any styling, accessories, or texture to make i | judge:J1 | agent |  |
| major | cam_r_L1_banyo_2 | the judge scores view cam_r_L1_banyo_2 2/5 (a client would not accept it): The render is clean and the camera is fine, but the room does not read as a finished bathroom. The shower (f_L1_031) is completely absent, so the main wet zone is missing. The washbasin (f_L1_025) is jammed into the corner behind the toilet (f_L1_024) at a height that looks too low and is unusable, and the door (d_L1_009) o | judge:J1 | agent |  |
| major | cam_r_L1_banyo_3 | the judge scores view cam_r_L1_banyo_3 1/5 (a client would not accept it): The render is a near-empty bathroom: the toilet, the second washbasin and the shower are all absent, so the room reads as a shell rather than a finished, stylish space. The camera is also poorly chosen, framing a blank tiled wall and the door instead of the only fixture present. | judge:J1 | agent |  |
| major | cam_r_L1_cocuk_odasi_1 | the judge scores view cam_r_L1_cocuk_odasi_1 2/5 (a client would not accept it): A client would not accept this as a finished children's room. The two beds are from completely different design languages (a white ornate metal frame vs. a plain modern upholstered one), the desk is a generic mid-century placeholder, and the walls are flat, untextured plaster. The room feels like a furniture showroom, | judge:J1 | agent |  |
| major | cam_r_L1_cocuk_odasi_2 | the judge scores view cam_r_L1_cocuk_odasi_2 2/5 (a client would not accept it): The render is not client-ready. The most glaring issue is a duplicated bed: two double beds are placed in the same spot, with one frame and mattress visibly cutting through the other. This is a broken model state, not a design choice. Beyond that, the room reads as a generic, low-effort placeholder: a thin white metal | judge:J1 | agent |  |
| major | cam_r_L1_cocuk_odasi_3 | the judge scores view cam_r_L1_cocuk_odasi_3 2/5 (a client would not accept it): The room is a mess of clashing styles and broken models. The two beds are completely different (one ornate white metal, one plain white frame), the desk is a crude blocky placeholder, and the bedding on the right bed is a melted, low-poly blob that looks like a rendering error. The overall look is cheap and incoherent | judge:J1 | agent |  |
| major | cam_r_L1_dus_1 | the judge scores view cam_r_L1_dus_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation for a 4.5 m2 bathroom. The most serious issue is that the washbasin (f_L1_029) is completely absent from the frame, so the room reads as a toilet-and-shower box rather than a finished bathroom. Everything else is flat white tile with no vanity, mirror, towel,  | judge:J1 | agent |  |
| major | cam_r_L1_dus_2 | the judge scores view cam_r_L1_dus_2 2/5 (a client would not accept it): The render is a dead-end view of a tiled corner and a door; the shower (the room's namesake) is not in frame, and the visible washbasin is a crude, floating white slab. The client would ask, 'Where is the shower? And what is that sink?' | judge:J1 | agent |  |
| major | cam_r_L1_ebeveyn_y_odasi_1 | the judge scores view cam_r_L1_ebeveyn_y_odasi_1 2/5 (a client would not accept it): The render is a near-empty shell: the bed is the only piece of furniture in a 23 m2 master bedroom, and the two armchairs, floor lamp and second nightstand from the schedule are missing, so the room reads as a grey box with a bed in it. The two doors (d_L1_001, d_L1_002) are identical flat light-oak slabs with no  | judge:J1 | agent |  |
| major | cam_r_L1_ebeveyn_y_odasi_2 | the judge scores view cam_r_L1_ebeveyn_y_odasi_2 2/5 (a client would not accept it): The room is a mess of clashing styles and broken geometry. The two 'identical' armchairs are actually different models in different colors (one pink, one brown), which is a glaring error. The floor lamp is absurdly tall and thin, looking like a placeholder. The walls are flat, untextured beige, making the room fee | judge:J1 | agent |  |
| major | cam_r_L1_hol_2 | the judge scores view cam_r_L1_hol_2 2/5 (a client would not accept it): The hall is a bare, unfinished shell: flat plaster walls, no skirting, no lighting, no decor, and a stair that reads as a white block. The railing is a crude placeholder and the door is a plain slab. It does not look like a designed home. | judge:J1 | agent |  |
| major | cam_r_L1_oda_1 | the judge scores view cam_r_L1_oda_1 2/5 (a client would not accept it): The render is a dead-end hallway shot, not a room. The camera is aimed straight at a door, so the frame is 80% wall and door leaf. The only furniture, the shoe cabinet, is a crude, low-poly slatted box cut off in the corner. The space is completely bare: no lighting, no decor, no texture on the walls, and the wood tones of th | judge:J1 | agent |  |
| major | cam_r_L1_oda_2_1 | the judge scores view cam_r_L1_oda_2_1 2/5 (a client would not accept it): The room is a mess of broken models. The main sofa is a low-poly white block, the second sofa has a floating, broken object on it, and the light is blown out. A client would not accept this. | judge:J1 | agent |  |
| major | cam_r_L1_oda_2_2 | the judge scores view cam_r_L1_oda_2_2 2/5 (a client would not accept it): The room is bright and the camera is fine, but it fails as a designed living room. The two seating pieces are completely different in style, colour and form, and the decor is a mess. A client would immediately ask why the room has two competing sofas and a random pineapple poster. | judge:J1 | agent |  |
| major | cam_r_L1_oda_2_3 | the judge scores view cam_r_L1_oda_2_3 2/5 (a client would not accept it): The room reads as an unfinished shell, not a designed living room. The two sofas are of completely different styles and colours (a white classic/curved sofa vs. a grey modern one), the walls are bare plaster, and the floor lamp from the list is missing. The camera is also poorly framed, cutting off the main seating group. | judge:J1 | agent |  |
| major | cam_r_L1_soyunma_odasi_1 | the judge scores view cam_r_L1_soyunma_odasi_1 1/5 (a client would not accept it): The render shows a bare, unfurnished shell: raw plaster walls, a plain wood floor, and a door that reads as a flat slab. It looks like a construction site, not a finished dressing room, and the camera is aimed at a corner rather than a designed space. It is not client-ready. | judge:J1, judge:V1 | agent |  |
| major | d_L0_001 | The entrance door is a plain flat slab with a basic handle; it looks cheap and generic for a modern two-storey house and does not give a confident, designed front entry. | judge:Q7 |  |  |
| major | d_L0_007 | The camera is poorly placed. It is aimed at a corner and a door leaf, which fills the right half of the frame. The room's main group (the wet zone) is not visible. | judge:V1, judge:Q7 |  |  |
| major | d_L1_002 | Second identical flat-slab door with no frame or hardware detail; two bare slabs side by side look like placeholders rather than finished doors. | judge:Q7, judge:V1 |  |  |
| major | d_L1_003 | The camera is poorly placed. It is aimed at a corner and a door (d_L1_003), which dominates the center of the frame. This is a 'bad camera' shot that does not showcase the room's layout or key fixtures. | judge:V1, judge:Q7 |  |  |
| major | d_L1_009 | The camera is poorly framed. It is angled towards the door (d_L1_009) and a large blank wall, failing to show the room's main group of fixtures in a coherent way. | judge:V1 |  |  |
| major | ext_4 | the judge scores view ext_4 2/5 (a client would not accept it): This is a raw massing model, not a finished render. The client would see a white block with black holes for windows, a floating balcony, and a void for a garden. It is not presentable. | judge:J1 | agent |  |
| major | ext_6 | the judge scores view ext_6 2/5 (a client would not accept it): The render is a raw grey-box massing study, not a client-ready image. The materials are flat and untextured, the landscape is a void, and the architectural details (like the balcony) are crude placeholders. A client would not accept this as a design presentation. | judge:J1 | agent |  |
| major | f_L0_007 | The dark grey ribbed armchair (f_L0_007) clashes severely with the beige/cream palette of the sofa (f_L0_011) and the other armchair (f_L0_008). It looks like a piece from a different, darker design scheme, breaking the visual coherence of the room. | judge:Q5, judge:D3, judge:V1 |  |  |
| major | f_L0_008 | The beige armchair (f_L0_008) is a different style (tufted, blocky) from the sofa (f_L0_011) and the dark chair (f_L0_007). The three pieces do not form a cohesive set, making the room look like a collection of random furniture rather than a curated interior. | judge:Q5, judge:D3 |  |  |
| major | f_L0_011 | The cream corner sofa with its four round ottomans is a different, lighter set from the darker taupe armchairs (f_L0_007, f_L0_008, f_L0_016-f_L0_019); two competing sofa groups in one salon. | judge:Q5 |  |  |
| major | f_L0_015 | The bright honey-oak coffee table is a third, clashing wood tone against the pale floor and the muted upholstery; it does not belong to the room's palette. | judge:D3 |  |  |
| major | f_L0_024 | The toilet is a bulky, dated two-piece model. It does not match the clean, modern aesthetic suggested by the large-format tiles and the simple, modern door. | judge:D3 |  |  |
| major | f_L0_033 | The wall-cabinet run (and the whole kitchen set) is a flat, untextured white with no appliances, cooktop or styling; it reads as a plain placeholder, not a designed kitchen for the project's style. | process:P7, judge:D3 | fit | library_gap |
| major | f_L1_001 | The stair and its metal-and-glass railing are a plain, generic system that does not express the project's style; it looks like a default placeholder rather than a designed element. | judge:Q7 |  |  |
| major | f_L1_006 | The ornate white metal bed frame is a dated, classic style that clashes completely with the modern, minimalist aesthetic of the other furniture and the room itself. | judge:D3, judge:Q5, judge:D2 |  |  |
| major | f_L1_007 | The desk is a generic, blocky placeholder model. It does not feel like a carefully chosen piece for a stylish home and looks out of place. | judge:D3, judge:D2 |  |  |
| major | f_L1_016 | Mismatched set: this grey, textured, low-profile sofa clashes completely with the other sofa (f_L1_013). They are different models, different colours, and different styles. A living room needs a coherent seating group, not two competing pieces. | judge:Q5, judge:V1 |  |  |
| major | f_L1_017 | The two armchairs are a mismatched set. One is a pink, low-poly model, and the other is a brown, high-back model. They do not belong together. | judge:Q5 |  |  |
| major | f_L1_018 | The brown armchair clashes with the pink one and the rest of the neutral room. Its style and color are inconsistent with the other furniture. | judge:D3 |  |  |
| major | f_L1_022 | The floor lamp is a crude, low-poly model. It is disproportionately tall and thin, with a simple cone shade that looks like a placeholder. | judge:D2 |  |  |
| major | f_L1_027 | The floor lamp is an ornate, turned-wood classic style that clashes with the otherwise neutral and modern feel of the room. It feels out of place. | judge:D3 |  |  |
| major | f_L1_029 | The washbasin (f_L1_029) in the bottom right is a crude, low-poly model. It looks like a simple white box with a faucet, not a finished, stylish sink. It also appears to be floating or cut off by the frame. | judge:D2 |  |  |
| major | f_L1_030 | The shoe cabinet is a crude, low-poly model. It looks like a placeholder box with a grid texture, not a finished piece of furniture. | judge:D2, judge:D3 |  |  |
| major | o_L0_002 | The camera is pointed almost entirely at a blank wall (the opening o_L0_002 side). The main fixtures are pushed to the far right edge, so the shot does not present the room's main group. | process:P2, judge:V1 | scene |  |
| major | w_L0_001 | The entire facade reads as a flat, untextured white surface. The windows are simple dark rectangles with no visible frames, mullions, or glass reflections. This is a classic 'grey box' look that lacks the material richness and detail a client expects to see. | judge:Q7 |  |  |
| major | w_L1_001 | The windows are rendered as flat, opaque black rectangles. They have no frames, mullions, or glass reflections, making the facade look like a hole-punched cardboard box rather than a house. | judge:Q7 |  |  |
| major | win_L0_004 | The view through the window is a flat, featureless grey void. This 'flat_outdoor' look makes the render look unfinished and unconvincing. | judge:Q7 |  |  |
| minor | d_L1_004 | The door leaf and frame are a flat, untextured slab with a bare handle; it does not match a finished, styled interior and looks like a placeholder. | judge:Q7 |  |  |
| minor | f_L0_001 | The stair f_L0_001 is not visible in this view; if it is meant to be in the kitchen, its absence leaves the room's layout unexplained, and if it is elsewhere the camera framing hides the room's main circulation. | judge:D3 |  |  |
| minor | f_L0_002 | The base cabinets are a plain, flat white with no texture or detail, which looks cheap and unstyled for a modern kitchen. | judge:D3 |  |  |
| minor | f_L0_020 | sink_kitchen f_L0_020 built below the library level: fitting chose the parametric mesh | process:P7, judge:D3 | fit | library_gap |
| minor | f_L0_026 | The washbasin (f_L0_026) is the only piece in view and sits in a large empty tiled area, making the composition look sparse and unstyled. | judge:D3 |  |  |
| minor | f_L0_027 | The four round ottomans (f_L0_027-f_L0_030) read as a cluster of stools rather than a designed seating group, reinforcing the mismatched, improvised feel. | judge:Q5 |  |  |
| minor | f_L0_031 | The second counter f_L0_031 at the right edge is cut off and shows only a bare slab; it does not connect to the island or to any wall run, so the two pieces do not read as one coherent set. | judge:D3 |  |  |
| minor | f_L0_034 | wall_cabinet f_L0_034 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_035 | wall_cabinet f_L0_035 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_036 | The shower area is very plain. The glass partition is a simple slab, and the fixtures are basic, contributing to the overall 'grey box' feel. | judge:D3 |  |  |
| minor | f_L1_010 | The nightstand is a simple, untextured block. It lacks the detail and finish of the other pieces and contributes to the 'placeholder' feel of the room. | judge:D3 |  |  |
| minor | f_L1_012 | The bed, nightstand and rug are a coherent light-oak set, but the floral cushions and the single botanical print are the only decor in the room, so the styling feels thin and showroom-empty rather than a lived-in master bedroom. | judge:D3 |  |  |
| minor | f_L1_021 | The washbasin (f_L1_021) is a very basic, blocky model. While the black and white contrast is a design choice, the overall look is plain and lacks the styling or detail expected in a high-end project. | judge:D3, judge:Q5 |  |  |
| minor | f_L1_023 | Toilet is a plain white tank-and-bowl unit with no styling or hardware detail; it looks like a default placeholder rather than a chosen fixture. | judge:Q7 |  |  |
| minor | f_L1_024 | The toilet (f_L1_024) is a standard, unstyled model. It does not clash, but it contributes to the overall 'bare' and un-finished feel of the room. | judge:D3 |  |  |
| minor | f_L1_026 | Only one nightstand is present while the schedule lists two (f_L1_026, f_L1_028); the bed is asymmetric with a lamp on one side and nothing on the other. | judge:Q5, judge:D3 |  |  |
| minor | o_L1_002 | The opening to the bedroom is a raw, untrimmed hole in the wall with no architrave or reveal, reinforcing the unfinished look. | judge:Q7 |  |  |
| minor | r_L1_ebeveyn_y_odasi | a group the room should have found no place: r_L1_ebeveyn_y_odasi: completion added nothing, nothing fits: storage: no candidate position fits the room; work: no place passes the checks | process:P2 | building |  |
| minor | r_L1_hol | a group the room should have found no place: r_L1_hol: completion added nothing, nothing fits: entrance: no place passes the checks | process:P2 | building |  |
| minor | w_L0_002 | The ground floor windows are also flat black slabs. The lack of depth or framing makes the entire building look like a 3D modeling exercise rather than a realistic architectural visualization. | judge:Q7 |  |  |
| minor | win_L0_006 | no library model: built parametric or not at all: opening win_L0_006: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 1.10 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2 | scene |  |
| minor | win_L1_001 | no library model: built parametric or not at all: opening win_L1_001: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 0.95 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2, judge:Q7 | scene |  |
| minor | win_L1_002 | The window is a very basic, unadorned model. While not terrible, it lacks the detail one would expect in a high-end render and contributes to the overall plainness. | judge:D3 |  |  |
| minor | win_L1_004 | Window and surrounding wall are flat untextured white with no sill, frame depth, or curtain; combined with the all-white tile it reads as a bare material study. | judge:Q7 |  |  |
| minor | win_L1_005 | Second window is identical and equally bare; the pair looks like a placeholder pair rather than a designed window treatment. | judge:Q7 |  |  |
| minor | win_L1_006 | The windows are simple white uPVC-style units with no frames, mouldings or finish that ties them to the interior; they read as construction-phase glazing. | judge:Q7, judge:D3 |  |  |
| minor | win_L1_007 | The camera angle is acceptable, but it emphasizes the emptiness of the room. The view is dominated by the blank tiled wall and the missing shower area, which draws attention to what is absent rather than what is present. | judge:V1 |  |  |
| minor | win_L1_008 | The window (win_L1_008) is a simple, unadorned white frame that looks generic. It doesn't add to the style of the room and the view outside is a flat, untextured gradient, which looks like a placeholder. | judge:D3 |  |  |

## Prevention: the kinds to guard

Each open kind with the findings no fix of the run covers, or that came back from an earlier run: these need a new rule or check (a general one, for every project), not a one-off patch.

- **misread** (31 open, 2 with a fix; arises: reading; guards: plan_vs_model (B*), the room-sense rules (G*, R*), model review M7)
  - judge:Q4 f_L0_024: The toilet (f_L0_024) is not visible in the frame. A bathroom render that omits the toilet looks unfinished and makes the room feel empty.
  - judge:Q4 f_L0_036: The shower (f_L0_036) is only hinted at by a glass edge on the right; it is not legible as a designed shower zone, leaving the room feeling incomplete.
  - judge:Q4 f_L0_026: The washbasin is a main piece of the bathroom but is completely missing from the frame. A bathroom render that shows only a toilet and a door makes no sense to a client.
  - judge:Q4 f_L0_002: The kitchen is missing its main functional anchor: there is no hob or cooktop on the worktop, making the room feel incomplete and non-functional.
  - judge:Q4 f_L0_033: The wall cabinets listed in the JSON are not visible in the render, leaving the upper wall completely bare and the kitchen feeling unfinished.
  - judge:Q4 f_L0_015: The coffee table (f_L0_015) is listed in the room data but is missing from the render. This leaves the seating area without a central anchor, making the layout feel incomplete and the space between th
  - judge:Q4 r_L1_banyo: The room is largely empty. Aside from the basic toilet and basin, there is no shower, no storage, and no decor. This makes the space feel like an unfinished shell rather than a designed, livable room.
  - judge:Q4 f_L1_024: The toilet (f_L1_024) is missing from the render. A bathroom without a toilet is a fundamental, client-visible failure.
  - judge:Q4 f_L1_025: The second washbasin (f_L1_025) is missing. Only one basin is visible, leaving the room feeling sparse and unfinished.
  - judge:Q4 f_L1_010: The nightstand (f_L1_010) is listed but not visible in the render. The bed has no bedside table, leaving the main furniture group incomplete.
  - judge:Q4 f_L1_029: Bathroom with no basin: the washbasin is listed for this room but is not visible anywhere in the frame, so the room is missing its main fixture.
  - judge:Q4 f_L1_020: The shower (f_L1_020) is completely missing from the frame. A bathroom render that shows no shower, no toilet, and only a fragment of a sink fails to present the room's main function.
  - judge:Q4 f_L1_017: The scheduled armchair (and its pair f_L1_018) is absent; the bedroom has no seating or reading corner, so the main group is just a bed and the room feels incomplete.
  - judge:Q4 f_L1_022: The floor lamp is missing, leaving the only light source as a small bedside lamp; the right half of the room is dark and unlit, which reads as an unfinished render.
  - judge:Q4 r_L1_hol: The hall is completely empty and unfinished. There is no lighting, no skirting boards, no floor finish, and no decor. It looks like a grey-box construction site, not a livable space.
  - judge:Q4 r_L1_oda: The room is essentially empty. A 3.1 m2 hall should have some sense of purpose or at least be styled, but this is just a bare box with a door.
  - judge:Q4 f_L1_027: The room is missing its main anchor piece, the floor lamp (f_L1_027). A living room with only two mismatched sofas and no lighting or decor looks like an empty, unfinished space.
  - judge:Q4 r_L1_soyunma_odasi: The dressing room (soyunma odasi) is completely empty. It has no wardrobe, bench, mirror, or any of the fixtures a dressing room requires. This is a missing-anchor failure: the room's entire purpose i
- **taste** (79 open, 4 with a fix; arises: fit, decor, opening models; guards: judge (J*), visitor checks Q5, Q7, the fit's matched sets)
  - judge:V1 o_L0_002: The camera is pointed almost entirely at a blank wall (the opening o_L0_002 side). The main fixtures are pushed to the far right edge, so the shot does not present the room's main group.
  - RECURRING judge:J1 cam_r_L0_banyo_1: the judge scores view cam_r_L0_banyo_1 2/5 (a client would not accept it): The render is a near-empty bathroom: the camera is aimed at a blank tiled wall, the toilet is missing from view, and the only
  - judge:Q7 win_L0_004: The view through the window is a flat, featureless grey void. This 'flat_outdoor' look makes the render look unfinished and unconvincing.
  - RECURRING judge:J1 cam_r_L0_banyo_2: the judge scores view cam_r_L0_banyo_2 2/5 (a client would not accept it): The render is a dead-end view of a toilet and a door; the room's other main pieces are not in frame, so it reads as a corrido
  - judge:V1 d_L0_007: The camera is poorly placed. It is aimed at a corner and a door leaf, which fills the right half of the frame. The room's main group (the wet zone) is not visible.
  - judge:D3 f_L0_024: The toilet is a bulky, dated two-piece model. It does not match the clean, modern aesthetic suggested by the large-format tiles and the simple, modern door.
  - RECURRING judge:J1 cam_r_L0_mutfak_1: the judge scores view cam_r_L0_mutfak_1 2/5 (a client would not accept it): The render shows a kitchen that is mostly empty and unfinished. The main run of base cabinets is present, but there is no ho
  - RECURRING judge:J1 cam_r_L0_mutfak_2: the judge scores view cam_r_L0_mutfak_2 2/5 (a client would not accept it): The kitchen reads as a single freestanding island with a stone top and a sink, but it is the only piece in a 24.8 m2 room: n
  - judge:J1 cam_r_L0_salon_1: the judge scores view cam_r_L0_salon_1 2/5 (a client would not accept it): The render shows a disjointed and unfinished living space. The furniture selection is incoherent, mixing a dark, modern ribbe
  - judge:Q5 f_L0_007: The dark grey ribbed armchair (f_L0_007) clashes severely with the beige/cream palette of the sofa (f_L0_011) and the other armchair (f_L0_008). It looks like a piece from a different, darker design s
  - judge:Q5 f_L0_008: The beige armchair (f_L0_008) is a different style (tufted, blocky) from the sofa (f_L0_011) and the dark chair (f_L0_007). The three pieces do not form a cohesive set, making the room look like a col
  - judge:Q5 f_L0_011: The cream corner sofa with its four round ottomans is a different, lighter set from the darker taupe armchairs (f_L0_007, f_L0_008, f_L0_016-f_L0_019); two competing sofa groups in one salon.
  - judge:D3 f_L0_015: The bright honey-oak coffee table is a third, clashing wood tone against the pale floor and the muted upholstery; it does not belong to the room's palette.
  - judge:J1 cam_r_L0_salon_3: the judge scores view cam_r_L0_salon_3 2/5 (a client would not accept it): The room is a 55 m2 salon that reads as a showroom of mismatched, cheap-looking pieces. The main sofa group is pushed into th
  - RECURRING judge:J1 cam_r_L1_banyo_1: the judge scores view cam_r_L1_banyo_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation. The room is listed as a bathroom with a shower (f_L1_031)
  - RECURRING judge:J1 cam_r_L1_banyo_2: the judge scores view cam_r_L1_banyo_2 2/5 (a client would not accept it): The render is clean and the camera is fine, but the room does not read as a finished bathroom. The shower (f_L1_031) is compl
  - RECURRING judge:J1 cam_r_L1_banyo_3: the judge scores view cam_r_L1_banyo_3 1/5 (a client would not accept it): The render is a near-empty bathroom: the toilet, the second washbasin and the shower are all absent, so the room reads as a s
  - judge:V1 d_L1_009: The camera is poorly framed. It is angled towards the door (d_L1_009) and a large blank wall, failing to show the room's main group of fixtures in a coherent way.
  - RECURRING judge:J1 cam_r_L1_cocuk_odasi_1: the judge scores view cam_r_L1_cocuk_odasi_1 2/5 (a client would not accept it): A client would not accept this as a finished children's room. The two beds are from completely different design languag
  - judge:D3 f_L1_006: The ornate white metal bed frame is a dated, classic style that clashes completely with the modern, minimalist aesthetic of the other furniture and the room itself.
  - judge:D3 f_L1_007: The desk is a generic, blocky placeholder model. It does not feel like a carefully chosen piece for a stylish home and looks out of place.
  - judge:D2 f_L1_009: The bedding on this bed is a crude, melted-looking blob. It does not look like a duvet or pillows; it looks like a failed simulation or a low-poly placeholder. This is the single most embarrassing ele
  - RECURRING judge:J1 cam_r_L1_cocuk_odasi_2: the judge scores view cam_r_L1_cocuk_odasi_2 2/5 (a client would not accept it): The render is not client-ready. The most glaring issue is a duplicated bed: two double beds are placed in the same spot
  - RECURRING judge:J1 cam_r_L1_cocuk_odasi_3: the judge scores view cam_r_L1_cocuk_odasi_3 2/5 (a client would not accept it): The room is a mess of clashing styles and broken models. The two beds are completely different (one ornate white metal,
  - RECURRING judge:J1 cam_r_L1_dus_1: the judge scores view cam_r_L1_dus_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation for a 4.5 m2 bathroom. The most serious issue is that the wa
  - RECURRING judge:J1 cam_r_L1_dus_2: the judge scores view cam_r_L1_dus_2 2/5 (a client would not accept it): The render is a dead-end view of a tiled corner and a door; the shower (the room's namesake) is not in frame, and the visible w
  - judge:V1 d_L1_003: The camera is poorly placed. It is aimed at a corner and a door (d_L1_003), which dominates the center of the frame. This is a 'bad camera' shot that does not showcase the room's layout or key fixture
  - judge:D2 f_L1_029: The washbasin (f_L1_029) in the bottom right is a crude, low-poly model. It looks like a simple white box with a faucet, not a finished, stylish sink. It also appears to be floating or cut off by the 
  - RECURRING judge:J1 cam_r_L1_ebeveyn_y_odasi_1: the judge scores view cam_r_L1_ebeveyn_y_odasi_1 2/5 (a client would not accept it): The render is a near-empty shell: the bed is the only piece of furniture in a 23 m2 master bedroom, and the two arm
  - judge:Q7 d_L1_002: Second identical flat-slab door with no frame or hardware detail; two bare slabs side by side look like placeholders rather than finished doors.
  - RECURRING judge:J1 cam_r_L1_ebeveyn_y_odasi_2: the judge scores view cam_r_L1_ebeveyn_y_odasi_2 2/5 (a client would not accept it): The room is a mess of clashing styles and broken geometry. The two 'identical' armchairs are actually different mod
  - judge:Q5 f_L1_017: The two armchairs are a mismatched set. One is a pink, low-poly model, and the other is a brown, high-back model. They do not belong together.
  - judge:D2 f_L1_022: The floor lamp is a crude, low-poly model. It is disproportionately tall and thin, with a simple cone shade that looks like a placeholder.
  - judge:D3 f_L1_018: The brown armchair clashes with the pink one and the rest of the neutral room. Its style and color are inconsistent with the other furniture.
  - judge:Q7 f_L1_001: The stair and its metal-and-glass railing are a plain, generic system that does not express the project's style; it looks like a default placeholder rather than a designed element.
  - RECURRING judge:J1 cam_r_L1_hol_2: the judge scores view cam_r_L1_hol_2 2/5 (a client would not accept it): The hall is a bare, unfinished shell: flat plaster walls, no skirting, no lighting, no decor, and a stair that reads as a white
  - RECURRING judge:J1 cam_r_L1_oda_1: the judge scores view cam_r_L1_oda_1 2/5 (a client would not accept it): The render is a dead-end hallway shot, not a room. The camera is aimed straight at a door, so the frame is 80% wall and door le
  - judge:D2 f_L1_030: The shoe cabinet is a crude, low-poly model. It looks like a placeholder box with a grid texture, not a finished piece of furniture.
  - RECURRING judge:J1 cam_r_L1_oda_2_1: the judge scores view cam_r_L1_oda_2_1 2/5 (a client would not accept it): The room is a mess of broken models. The main sofa is a low-poly white block, the second sofa has a floating, broken object o
  - judge:D2 f_L1_013: The main sofa is a crude, low-poly white block. It has no texture, no realistic form, and looks like a placeholder model, not a piece of furniture.
  - judge:D3 f_L1_027: The floor lamp is an ornate, turned-wood classic style that clashes with the otherwise neutral and modern feel of the room. It feels out of place.
  - RECURRING judge:J1 cam_r_L1_oda_2_2: the judge scores view cam_r_L1_oda_2_2 2/5 (a client would not accept it): The room is bright and the camera is fine, but it fails as a designed living room. The two seating pieces are completely diff
  - judge:Q5 f_L1_016: Mismatched set: this grey, textured, low-profile sofa clashes completely with the other sofa (f_L1_013). They are different models, different colours, and different styles. A living room needs a coher
  - RECURRING judge:J1 cam_r_L1_oda_2_3: the judge scores view cam_r_L1_oda_2_3 2/5 (a client would not accept it): The room reads as an unfinished shell, not a designed living room. The two sofas are of completely different styles and colou
  - judge:J1 cam_r_L1_soyunma_odasi_1: the judge scores view cam_r_L1_soyunma_odasi_1 1/5 (a client would not accept it): The render shows a bare, unfurnished shell: raw plaster walls, a plain wood floor, and a door that reads as a flat sl
  - judge:Q7 w_L0_001: The entire facade reads as a flat, untextured white surface. The windows are simple dark rectangles with no visible frames, mullions, or glass reflections. This is a classic 'grey box' look that lacks
  - judge:Q7 d_L0_001: The entrance door is a plain flat slab with a basic handle; it looks cheap and generic for a modern two-storey house and does not give a confident, designed front entry.
  - RECURRING judge:J1 ext_4: the judge scores view ext_4 2/5 (a client would not accept it): This is a raw massing model, not a finished render. The client would see a white block with black holes for windows, a floating balcony,
  - judge:Q7 w_L1_001: The windows are rendered as flat, opaque black rectangles. They have no frames, mullions, or glass reflections, making the facade look like a hole-punched cardboard box rather than a house.
  - RECURRING judge:J1 ext_6: the judge scores view ext_6 2/5 (a client would not accept it): The render is a raw grey-box massing study, not a client-ready image. The materials are flat and untextured, the landscape is a void, an
  - rule proposed by Argus AI (1 run(s)): Fixture models must be finished and detailed, and must match the room's specified material palette; plain boxes or exposed services are not acceptable unless explicitly specified.
  - rule proposed by Argus AI (1 run(s)): Fixture models must conceal plumbing or use a specified exposed-service finish; unexplained exposed pipes or mismatched service materials are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Furniture models must be selected from a coherent style set and must match the room's material palette; generic boxes that do not coordinate with the room are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Doors in the same architectural set must have consistent leaf height, width, and style; mismatched door leaves are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Paired furniture must use the same model and finish; a bed-side nightstand pair must be a matched set.
  - rule proposed by Argus AI (1 run(s)): Paired furniture must use the same model and finish; mismatched nightstands are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Furniture models must be scaled and detailed appropriately for the room and adjacent pieces; flimsy or out-of-scale models are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Window models must include appropriate joinery or trim and must match the architectural style; plain untrimmed uPVC is not acceptable in a styled project.
  - rule proposed by Argus AI (1 run(s)): Stair models must use finished materials consistent with the surrounding floor and wall finishes; raw concrete or exposed voids are not acceptable unless specified.
  - rule proposed by Argus AI (1 run(s)): Furniture models must be finished, not low-detail placeholders; crude slat or box models are not acceptable in a furnished render.
  - rule proposed by Argus AI (1 run(s)): Door frames must use a finish that is part of the room's specified material palette; unexplained third materials are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Exterior glazing frames must be proportionate and stylistically consistent with the facade; heavy industrial frames are not acceptable on a light residential facade.
- **geometry** (14 open, 0 with a fix; arises: layout, agent; guards: code critic (F*, G*), architect F-rules)
  - RECURRING process:P5 L0:S2: scene check S2 on L0: 1 of 24 failed
  - judge:F9 o_L0_001: The large opening in the wall is a raw, unframed hole with a floating horizontal bar, which looks like a broken model or a construction error rather than a designed feature.
  - judge:F9 f_L1_009: A second double bed (f_L1_009) is duplicated on top of the first (f_L1_006). The frames and mattresses intersect and cut through each other, which is a broken/overlapping model state.
  - judge:D1 f_L1_016: There is a broken, floating object (looks like a shattered piece of furniture or a glitch) resting on the grey sofa. This is a major rendering error.
- **lost** (24 open, 7 with a fix; arises: any stage boundary: reading -> building, fit, layout, build, render; guards: ledger (A*), conservation (C*), plan_vs_model (B*), process (P*))
  - render:K1 win_L0_007: window win_L0_007 (from_documents) is not seen in 1 of the 2 view(s) that must show it: cam_r_L0_mutfak_3
  - render:K1 d_L1_007: door d_L1_007 (from_documents) is not seen in 1 of the 2 view(s) that must show it: cam_r_L1_ebeveyn_y_odasi_2
  - plan_vs_model:B8 f_L1_031: The plan draws a shower (f_L1_031) in the bathroom (BANYO) which is not built in the model.
- **no_sense** (9 open, 0 with a fix; arises: architect, build; guards: sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*))
  - judge:Q2 f_L1_025: The washbasin sits too low and is wedged behind the toilet, so it is not at a usable working height and cannot be reached.
  - judge:Q9 d_L1_009: The door opens directly into the basin/toilet cluster, blocking the approach to the fixtures.
  - judge:Q1 d_L1_001: The door leaf is a flat slab with no frame, no visible threshold and no destination behind it; it opens onto a blank wall, so it makes no sense in the plan.
  - judge:Q3 f_L1_001: The stair opening and landing edge have a flimsy, incomplete guard. The glass panel is a thin placeholder with a large open gap below it and no proper balustrade, which is a clear fall risk and looks 
  - judge:Q9 o_L0_002: The entrance area is poorly resolved. The steps and handrails are basic, untextured geometry. The large terrace slab to the left is a raw, floating concrete block with no finish, making the whole appr
  - judge:Q9 d_L0_001: The main entrance is a dark, undefined void under the porch. There is no visible door leaf, handle, or threshold, making the entry point look unfinished and inaccessible.
  - judge:Q3 o_L1_001: The balcony railing is a crude, thin wireframe that looks like a construction placeholder. It does not read as a safe, finished guardrail, and the balcony slab itself looks like a floating grey box.
- **process** (6 open, 1 with a fix; arises: scheduler; guards: process (P*))
  - RECURRING process:P4 test_sky_and_window_pulls_reach_their_targets[real06]: test tests.gpu.test_render::test_sky_and_window_pulls_reach_their_targets[real06] failure: AssertionError: real06: [('window panes', 'median pane saturation 0.0526 under 0.065: grey cards, not the sky
  - RECURRING process:P9 big_loop: the big loop did not raise the house score (first 31.34; 0 cycle(s); stop: cycle 1: deadline)
  - RECURRING render:K4 views: 2 view(s) marked for review: cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_3
- **silent** (1 open, 0 with a fix; arises: any stage; guards: process P2 (warnings that say something was left out))
  - RECURRING process:P2 inferred trees: a stage placed fewer items than it planned: inferred trees: placed 0 of 3 (74 candidates; removed by building 1, path 15, sightline 36, window 66, front 27; most by window; the first pass placed 0, th

## Warnings by rule

Every warning of the reading, the build and the site, matched to a rule (``process.WARN_RULES``); 'other' = no rule yet.

assumed 50, read_by 25, not_built 16, disagree 13, not_checked 5, other 4, no_model 3, outside_built 2, more_labels 2, no_label 2, nothing_fits 2, not_rested 2, not_read 1, not_allowed 1, not_used 1, drawn_mismatch 1, shortfall 1

Warnings no rule knows yet (Argus AI reads each one; a new rule in ``process.WARN_RULES`` when one keeps coming):

- building frame: the outer wall faces of the reference r3 start (+3.161, +3.975) m from the sheets outline corner; every region and the sheets coordinates move with them
- levels: the ground floor (building z 0) is printed +0.50 in the section: every relative mark of the plans is read +0.50 m lower (one height frame)
- levels: f_L0_022 moved to symbols (sym_f_L0_022): a level-mark symbol, not furniture (a small drawn piece around a level mark text: '+0,50'); drawn as unknown 0.88 x 0.34 m
- r_L0_oda: no AI furniture, no groups for this room (hall 2.1 m²: nothing)
