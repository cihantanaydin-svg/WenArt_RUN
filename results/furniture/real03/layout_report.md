# AI layout: real03

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hava Bacası (r_L0_hava_bacasi) | shaft | - | - | - | - | room stays empty: shaft room: never furnished by AI (docs/milestone7.md §0) |
| Oda (r_L0_oda_8) | hall | 2/0/2 (2.8 s) | 0/0/0 (0.1 s) | - | - | room stays empty: model answered nothing usable (pass 1: no usable piece; pass 2: no usable piece) |
| Oda (r_L0_oda_9) | hall | 2/0/2 (1.9 s) | 0/0/0 (0.1 s) | - | - | room stays empty: model answered nothing usable (pass 1: no usable piece; pass 2: no usable piece) |

Repair steps of the chosen proposals: 0

