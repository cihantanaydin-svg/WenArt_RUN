# Polish report: synthetic-07 (run)

30 views, 51 attempts (51 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Server Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 2 s, prompt encoding 1.7 s, 1.44 s per forward, run 372 s.

Final images: 17 polished, 13 Cycles (gate 7, room 6). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_hol_1 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.31 | 0 |
| cam_r_L-1_hol_2 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.83 | 1 |
| cam_r_L-1_hol_3 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.85 | 1 |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.8 | 0 |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.81 | 1 |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 1 |
| cam_r_L-1_salon_1 | r_L-1_salon | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | edges:global 0.879 (needs >= 0.935); edges:dec_L-1_004 0.821 (needs >= 0.87) | 2.08 | 3 |
| cam_r_L-1_salon_2 | r_L-1_salon | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | edges:f_L-1_007 0.863 (needs >= 0.87); depth:f_L-1_007 0.253 (needs <= 0.14) | 1.82 | 2 |
| cam_r_L-1_salon_3 | r_L-1_salon | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 2 |
| cam_r_L0_banyo_1 | r_L0_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.83 | 1 |
| cam_r_L0_banyo_2 | r_L0_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L0_banyo_3 | r_L0_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 2 |
| cam_r_L0_hol_1 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.9 | 0 |
| cam_r_L0_hol_2 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L0_hol_3 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 2.81 | 0 |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 1.84 | 2 |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 3 |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 3 |
| cam_r_L1_hol_1 | r_L1_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 5.04 | 0 |
| cam_r_L1_hol_2 | r_L1_hol | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.89 | 1 |
| cam_r_L1_hol_3 | r_L1_hol | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 3.98 | 1 |
| cam_r_L1_oyun_odasi_1 | r_L1_oyun_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.85 | 1 |
| cam_r_L1_oyun_odasi_2 | r_L1_oyun_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 4.05 | 1 |
| cam_r_L1_oyun_odasi_3 | r_L1_oyun_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L1_teras_1 | r_L1_teras | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| ext_2 | - | cycles (gate) | - | - | - | - | - | - |
| ext_3 | - | cycles (gate) | - | - | - | - | - | - |
| ext_5 | - | cycles (gate) | - | - | - | - | - | - |
| ext_6 | - | cycles (gate) | - | - | - | - | - | - |
| ext_7 | - | cycles (gate) | - | - | - | - | - | - |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L-1_hol | downgraded | cycles | 5.59 | - | cam_r_L-1_hol_1, cam_r_L-1_hol_2, cam_r_L-1_hol_3 |
| r_L-1_mutfak | ok | - | 4.8 | - | cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3 |
| r_L-1_salon | ok | - | - | - | cam_r_L-1_salon_3 |
| r_L0_banyo | ok | - | 1.48 | - | cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_banyo_3 |
| r_L0_hol | downgraded | cycles | 6.33 | - | cam_r_L0_hol_1, cam_r_L0_hol_2, cam_r_L0_hol_3 |
| r_L0_yatak_odasi | ok | - | 1.35 | - | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_hol | ok | - | 2.97 | - | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_oyun_odasi | ok | - | 1.02 | - | cam_r_L1_oyun_odasi_1, cam_r_L1_oyun_odasi_2, cam_r_L1_oyun_odasi_3 |
| r_L1_teras | ok | - | - | - | cam_r_L1_teras_1 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.92 | accept | - | - |
| cam_r_L-1_hol_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L-1_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.31 | accept | - | - |
| cam_r_L-1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L-1_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 4.69 | accept | - | - |
| cam_r_L-1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | accept | - | - |
| cam_r_L-1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L-1_hol_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 4.63 | accept | - | - |
| cam_r_L-1_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.85 | accept | - | - |
| cam_r_L-1_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L-1_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.81 | reject | edges:f_L-1_016 0.867 (needs >= 0.87) | - |
| cam_r_L-1_mutfak_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L-1_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | edges:f_L-1_013 0.799 (needs >= 0.87); edges:f_L-1_015 0.816 (needs >= 0.87); depth:f_L-1_004 0.358 (needs <= 0.14) | - |
| cam_r_L-1_mutfak_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | reject | depth:f_L-1_004 0.303 (needs <= 0.14) | - |
| cam_r_L-1_mutfak_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L-1_salon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | edges:global 0.636 (needs >= 0.935); edges:dec_L-1_004 0.459 (needs >= 0.87) | - |
| cam_r_L-1_salon_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.18 | reject | edges:global 0.745 (needs >= 0.935); edges:dec_L-1_004 0.622 (needs >= 0.87) | - |
| cam_r_L-1_salon_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 2.08 | reject | edges:global 0.879 (needs >= 0.935); edges:dec_L-1_004 0.821 (needs >= 0.87) | - |
| cam_r_L-1_salon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | edges:global 0.744 (needs >= 0.935); edges:dec_L-1_004 0.613 (needs >= 0.87); depth:f_L-1_007 0.247 (needs <= 0.14) | - |
| cam_r_L-1_salon_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.38 | reject | edges:global 0.918 (needs >= 0.935); depth:f_L-1_007 0.233 (needs <= 0.14) | - |
| cam_r_L-1_salon_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | reject | edges:f_L-1_007 0.863 (needs >= 0.87); depth:f_L-1_007 0.253 (needs <= 0.14) | - |
| cam_r_L-1_salon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | edges:global 0.664 (needs >= 0.935); edges:dec_L-1_004 0.409 (needs >= 0.87); depth:f_L-1_007 0.305 (needs <= 0.14) | - |
| cam_r_L-1_salon_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.92 | reject | edges:global 0.892 (needs >= 0.935); edges:dec_L-1_004 0.815 (needs >= 0.87); depth:f_L-1_007 0.874 (needs <= 0.14) | - |
| cam_r_L-1_salon_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L0_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | edges:dec_L0_008 0.739 (needs >= 0.87) | - |
| cam_r_L0_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.83 | accept | - | - |
| cam_r_L0_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | reject | edges:f_L-1_001 0.859 (needs >= 0.87) | - |
| cam_r_L0_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.95 | accept | - | - |
| cam_r_L0_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.9 | accept | - | - |
| cam_r_L0_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.91 | reject | edges:dec_L0_010 0.858 (needs >= 0.87) | - |
| cam_r_L0_hol_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.96 | reject | depth:global 0.0513 (needs <= 0.05); depth:struct:floor 0.14 (needs <= 0.14) | - |
| cam_r_L0_hol_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L0_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 2.81 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | reject | edges:win_L0_003 0.67 (needs >= 0.87); edges:win_L0_004 0.797 (needs >= 0.87) | - |
| cam_r_L0_yatak_odasi_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.24 | reject | edges:win_L0_003 0.778 (needs >= 0.87); edges:win_L0_004 0.729 (needs >= 0.87) | - |
| cam_r_L0_yatak_odasi_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.84 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 5.04 | accept | - | - |
| cam_r_L1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | edges:f_L0_001 0.659 (needs >= 0.87) | - |
| cam_r_L1_hol_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.89 | accept | - | - |
| cam_r_L1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.95 | reject | edges:global 0.914 (needs >= 0.935); edges:f_L0_001 0.573 (needs >= 0.87); edges:f_L1_006 0.857 (needs >= 0.87) | - |
| cam_r_L1_hol_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.98 | accept | - | - |
| cam_r_L1_oyun_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | edges:f_L1_005 0.773 (needs >= 0.87) | - |
| cam_r_L1_oyun_odasi_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.85 | accept | - | - |
| cam_r_L1_oyun_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.05 | accept | - | - |
| cam_r_L1_oyun_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_teras_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |

## Notes

- cam_r_L-1_hol_1: room rule ran a2
- cam_r_L-1_hol_1: room rule ran a3
- cam_r_L-1_hol_1: room rule: wall ΔE 5.586 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L-1_hol_2: room rule ran a2
- cam_r_L-1_hol_2: room rule ran a3
- cam_r_L-1_hol_2: room rule: wall ΔE 5.586 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L-1_hol_3: room rule ran a2
- cam_r_L-1_hol_3: room rule ran a3
- cam_r_L-1_hol_3: room rule: wall ΔE 5.586 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L0_hol_1: room rule ran a3
- cam_r_L0_hol_1: room rule: wall ΔE 6.327 > 5.0 in r_L0_hol; a2 -> cycles
- cam_r_L0_hol_2: room rule: wall ΔE 6.327 > 5.0 in r_L0_hol; a3 -> cycles
- cam_r_L0_hol_3: room rule ran a3
- cam_r_L0_hol_3: room rule: wall ΔE 6.327 > 5.0 in r_L0_hol; a1 -> cycles
- ext_2: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.717 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_3: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.717 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_5: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.717 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_6: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.717 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_7: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.717 < 0.90 (60 comparisons): the gate lets geometry changes through)

## Prompts

- cam_r_L-1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. White plaster walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. White plaster walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. White plaster walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_mutfak_1: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, dining table, tall cabinet, chair, fridge. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_mutfak_2: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, light ceramic tile floor, dining table, kitchen counter, tall cabinet, chair, fridge. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_mutfak_3: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, light ceramic tile floor, dining table, kitchen counter, chair, tall cabinet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_salon_1: Photorealistic interior photograph of a living room in modern minimalist style. White plaster walls, light oak wood floor, sofa, armchair, coffee table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_salon_2: Photorealistic interior photograph of a living room in modern minimalist style. White plaster walls, light oak wood floor, sofa, armchair, coffee table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_salon_3: Photorealistic interior photograph of a living room in modern minimalist style. White plaster walls, light oak wood floor, sofa, armchair, coffee table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_banyo_1: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, light ceramic tile floor, shower. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_banyo_2: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, light ceramic tile floor, shower, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_banyo_3: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, light ceramic tile floor, shower, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. White plaster walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. White plaster walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. White plaster walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. White plaster walls, light oak wood floor, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. White plaster walls, light oak wood floor, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. White plaster walls, light oak wood floor, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_oyun_odasi_1: Photorealistic interior photograph of a room in modern minimalist style. White plaster walls, light oak wood floor, armchair, bookshelf, desk, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_oyun_odasi_2: Photorealistic interior photograph of a room in modern minimalist style. White plaster walls, light oak wood floor, armchair, desk, bookshelf, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_oyun_odasi_3: Photorealistic interior photograph of a room in modern minimalist style. White plaster walls, light oak wood floor, armchair, chair, bookshelf, desk. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_teras_1: Photorealistic interior photograph of a balcony in modern minimalist style. White plaster walls, light oak wood floor. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- ext_2: Photorealistic architectural photograph of a house exterior in modern minimalist style, seen from a corner of the plot at eye level, two facades in view. White smooth rendered facade, clay tile roof, anthracite aluminium window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 27.71 mm lens.
- ext_3: Photorealistic architectural photograph of a house exterior in modern minimalist style, seen from a corner of the plot at eye level, two facades in view. White smooth rendered facade, clay tile roof, anthracite aluminium window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 24.24 mm lens.
- ext_5: Photorealistic architectural photograph of a house exterior in modern minimalist style, seen in a three-quarter aerial view from above, roof and two facades in view. White smooth rendered facade, clay tile roof, anthracite aluminium window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 28.03 mm lens.
- ext_6: Photorealistic architectural photograph of a house exterior in modern minimalist style, seen straight on from the front, one facade in view. White smooth rendered facade, clay tile roof, anthracite aluminium window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 45.59 mm lens.
- ext_7: Photorealistic architectural photograph of a house exterior in modern minimalist style, seen straight on from the front, one facade in view. White smooth rendered facade, clay tile roof, anthracite aluminium window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 39.66 mm lens.

## Models

| role | repo | revision | licence | files |
|---|---|---|---|---|
| polish base | Tongyi-MAI/Z-Image-Turbo | `f332072aa78b` | Apache-2.0 | model_index.json, scheduler/*, text_encoder/*, tokenizer/*, transformer/*, vae/* |
| polish controlnet | alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1 | `5155fc56d178` | Apache-2.0 | Z-Image-Turbo-Fun-Controlnet-Union-2.1-2602-8steps.safetensors |
| gate depth | depth-anything/Depth-Anything-V2-Small-hf | `5426e4f0f365` | Apache-2.0 | - |
| gate dino | facebook/dinov2-base | `f9e44c814b77` | Apache-2.0 | - |
| gate sam | facebook/sam2.1-hiera-large | `665f8e2ad61c` | Apache-2.0 | - |

## Warnings

- exterior gate polish_disabled: 5 exterior views keep the Cycles render
