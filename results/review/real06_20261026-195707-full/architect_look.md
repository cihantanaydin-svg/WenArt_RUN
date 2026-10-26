# The AI architect looks at the model

25 question(s) and default decision(s) put to Qwen/Qwen3.8-27B-FP8 with each floor's view of the model, 2 decision(s) of its own: 0 carried out (checked by code: settled, no new major point, the model review no worse), 25 default(s) confirmed, 2 refused; 0 open point(s) after (45 s).

| level | kind | key | choice | verdict | why | the model's reason |
|---|---|---|---|---|---|---|
| L0 | decided | `O2:o_L0_002` | door_to_window | confirmed | the same as the default decision | The opening is a bare gap with nothing outside to step on, so it is a misread door that becomes a window at the floor's sill. |
| L0 | decided | `O2:o_L0_003` | door_to_window | confirmed | the same as the default decision | The opening is a bare gap with nothing outside to step on, so it is a misread door that becomes a window at the floor's sill. |
| L0 | decided | `O2:o_L0_004` | door_to_window | confirmed | the same as the default decision | The opening is a bare gap with nothing outside to step on, so it is a misread door that becomes a window at the floor's sill. |
| L0 | decided | `O2:o_L0_005` | door_to_window | confirmed | the same as the default decision | The opening is a bare gap with nothing outside to step on, so it is a misread door that becomes a window at the floor's sill. |
| L0 | decided | `O2:o_L0_006` | door_to_window | confirmed | the same as the default decision | The opening is a bare gap with nothing outside to step on, so it is a misread door that becomes a window at the floor's sill. |
| L0 | decided | `O2:o_L0_007` | door_to_window | confirmed | the same as the default decision | The opening is a bare gap with nothing outside to step on, so it is a misread door that becomes a window at the floor's sill. |
| L0 | decided | `W2:win_L0_001` | interior_glazing | confirmed | the same as the default decision | The kitchen and living room are both dry rooms, so the window between them is kept as a borrowed-light glazing on purpose. |
| L0 | decided | `D5:d_L0_001` | door_type:glazed_sliding | confirmed | the same as the default decision | The 2.15 m outside door into the living is drawn sliding, so it is a glazed sliding door with panels of at most 1.2 m. |
| L0 | decided | `D5:d_L0_004` | door_type:entrance | confirmed | the same as the default decision | The 0.80 m door into the living is the main entrance, so it is the entrance door. |
| L0 | decided | `D5:d_L0_006` | door_type:glazed_sliding | confirmed | the same as the default decision | The 2.95 m outside door into the living is drawn sliding, so it is a glazed sliding door with panels of at most 1.2 m. |
| L1 | decided | `E1:d_L1_001` | door_to_window | confirmed | the same as the default decision | The opening is 3.50 m over the ground with nothing outside to step on, so it is a window at the floor's sill. |
| L1 | decided | `E1:d_L1_004` | door_to_window | confirmed | the same as the default decision | The opening is 3.50 m over the ground with nothing outside to step on, so it is a window at the floor's sill. |
| L1 | decided | `E1:d_L1_005` | door_to_window | confirmed | the same as the default decision | The opening is 3.50 m over the ground with nothing outside to step on, so it is a window at the floor's sill. |
| L1 | decided | `E1:d_L1_010` | door_to_window | confirmed | the same as the default decision | The opening is 3.50 m over the ground with nothing outside to step on, so it is a window at the floor's sill. |
| L1 | decided | `O2:o_L1_001` | gap_to_door | confirmed | the same as the default decision | The bare gap opens onto the terrace os_L1_balkon, so it is the glazed door the reading missed. |
| L1 | decided | `O2:o_L1_003` | door_to_window | confirmed | the same as the default decision | The bare gap is 3.50 m over the ground with nothing outside to step on, so it is a window at the floor's sill. |
| L1 | decided | `O2:o_L1_004` | door_to_window | confirmed | the same as the default decision | The bare gap is 3.50 m over the ground with nothing outside to step on, so it is a window at the floor's sill. |
| L1 | decided | `O2:o_L1_005` | door_to_window | confirmed | the same as the default decision | The bare gap is 3.50 m over the ground with nothing outside to step on, so it is a window at the floor's sill. |
| L1 | decided | `O2:o_L1_006` | door_to_window | confirmed | the same as the default decision | The bare gap is 3.50 m over the ground with nothing outside to step on, so it is a window at the floor's sill. |
| L1 | decided | `O2:o_L1_007` | door_to_window | confirmed | the same as the default decision | The bare gap is 3.50 m over the ground with nothing outside to step on, so it is a window at the floor's sill. |
| L1 | decided | `W2:win_L1_003` | window_to_door | confirmed | the same as the default decision | The storage room has no door, so this opening between the two rooms is its misread door. |
| L1 | decided | `W2:win_L1_004` | high_window | confirmed | the same as the default decision | The 1.80 m sill between the bathroom and storage is a high borrowed-light window for the bathroom's privacy. |
| L1 | decided | `W2:win_L1_005` | high_window | confirmed | the same as the default decision | The 1.80 m sill between the bathroom and storage is a high borrowed-light window for the bathroom's privacy. |
| L1 | decided | `W2:win_L1_008` | interior_glazing | confirmed | the same as the default decision | The opening between the living room and the hall is a borrowed-light window on purpose. |
| L1 | decided | `O1:d_L1_011` | merge_openings | confirmed | the same as the default decision | d_L1_011 overlaps o_L1_001, so it is one opening read twice. |
| L1 | own | `AI.remove_piece:f_L1_006` | remove_piece | refused | f_L1_006 is drawn: a drawn piece is never removed by a decision (CLAUDE.md) | The children's room already has a double bed (f_L1_009), so the second double bed is a duplicate that does not belong. |
| L1 | own | `AI.remove_piece:f_L1_016` | remove_piece | refused | f_L1_016 is drawn: a drawn piece is never removed by a decision (CLAUDE.md) | The living room already has a sofa (f_L1_013), so the second sofa is a duplicate that does not belong. |
