# Polish report: synthetic-01 (run)

30 views, 52 attempts (52 polished now, 0 reused). Device NVIDIA RTX PRO 4500 Blackwell, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 7.9 s, prompt encoding 5.8 s, 2.86 s per forward, run 527 s.

Final images: 24 polished, 6 Cycles (room 6). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.52 | 0 |
| cam_r_L0_banyo_2 | r_L0_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.15 | 0 |
| cam_r_L0_banyo_3 | r_L0_banyo | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 3.76 | 0 |
| cam_r_L0_hol_1 | r_L0_hol | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 5.98 | 0 |
| cam_r_L0_hol_2 | r_L0_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.22 | 0 |
| cam_r_L0_hol_3 | r_L0_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 0 |
| cam_r_L0_mutfak_1 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 0 |
| cam_r_L0_mutfak_2 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 1 |
| cam_r_L0_mutfak_3 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 1 |
| cam_r_L0_salon_1 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 3 |
| cam_r_L0_salon_2 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.26 | 3 |
| cam_r_L0_salon_3 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.81 | 0 |
| cam_r_L1_banyo_1 | r_L1_banyo | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 3.79 | 0 |
| cam_r_L1_banyo_2 | r_L1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_banyo_3 | r_L1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.03 | 0 |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 0 |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 1 |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.03 | 0 |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.27 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.03 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.04 | 1 |
| cam_r_L1_hol_1 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.77 | 0 |
| cam_r_L1_hol_2 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.77 | 1 |
| cam_r_L1_hol_3 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:d_L1_002 0.147 (needs <= 0.14) | 3.81 | 0 |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.03 | 0 |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 0 |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L0_banyo | ok | - | 1.14 | - | cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_banyo_3 |
| r_L0_hol | ok | - | 0.55 | - | cam_r_L0_hol_1, cam_r_L0_hol_2, cam_r_L0_hol_3 |
| r_L0_mutfak | ok | - | 0.632 | - | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | ok | - | 3.21 | - | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_yatak_odasi | downgraded | cycles | 5.16 | - | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_banyo | ok | - | 0.722 | - | cam_r_L1_banyo_1, cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | ok | - | 1.88 | - | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | ok | - | 3.98 | - | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | downgraded | cycles | 5.64 | - | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | ok | - | 1.78 | - | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.52 | accept | - | - |
| cam_r_L0_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.15 | accept | - | - |
| cam_r_L0_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.16 | reject | depth:global 0.0556 (needs <= 0.05); depth:f_L0_012 0.225 (needs <= 0.14) | - |
| cam_r_L0_banyo_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | reject | depth:global 0.0656 (needs <= 0.05); depth:f_L0_012 0.164 (needs <= 0.14) | - |
| cam_r_L0_banyo_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | accept | - | - |
| cam_r_L0_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.19 | reject | depth:global 0.0782 (needs <= 0.05) | - |
| cam_r_L0_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.98 | accept | - | - |
| cam_r_L0_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.22 | accept | - | - |
| cam_r_L0_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L0_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L0_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_salon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_salon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L0_salon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.78 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.28 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.79 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.29 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.81 | accept | - | - |
| cam_r_L1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.0527 (needs <= 0.05) | - |
| cam_r_L1_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | reject | depth:global 0.0606 (needs <= 0.05) | - |
| cam_r_L1_banyo_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.79 | accept | - | - |
| cam_r_L1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.0637 (needs <= 0.05) | - |
| cam_r_L1_banyo_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.0588 (needs <= 0.05); depth:f_L1_020 0.165 (needs <= 0.14) | - |
| cam_r_L1_cocuk_odasi_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.27 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | reject | depth:f_L1_004 0.235 (needs <= 0.14); masks:f_L1_001 0.294 (needs >= 0.62) | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | reject | depth:f_L1_001 0.201 (needs <= 0.14); masks:f_L1_004 0.113 (needs >= 0.62) | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | accept | - | - |
| cam_r_L1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_hol_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L1_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.77 | accept | - | - |
| cam_r_L1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L1_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.77 | accept | - | - |
| cam_r_L1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L1_hol_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |
| cam_r_L1_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.81 | reject | depth:d_L1_002 0.147 (needs <= 0.14) | - |
| cam_r_L1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | reject | added_lines:struct:walls 0.0409 (needs <= 0.04) | - |
| cam_r_L1_yatak_odasi_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |

## Notes

- cam_r_L0_yatak_odasi_1: room rule ran a2
- cam_r_L0_yatak_odasi_1: room rule ran a3
- cam_r_L0_yatak_odasi_1: room rule: wall ΔE 5.164 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L0_yatak_odasi_2: room rule ran a2
- cam_r_L0_yatak_odasi_2: room rule ran a3
- cam_r_L0_yatak_odasi_2: room rule: wall ΔE 5.164 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L0_yatak_odasi_3: room rule ran a2
- cam_r_L0_yatak_odasi_3: room rule ran a3
- cam_r_L0_yatak_odasi_3: room rule: wall ΔE 5.164 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L1_hol_1: room rule ran a2
- cam_r_L1_hol_1: room rule ran a3
- cam_r_L1_hol_1: room rule: wall ΔE 5.645 > 5.0 in r_L1_hol; a1 -> cycles
- cam_r_L1_hol_2: room rule ran a2
- cam_r_L1_hol_2: room rule ran a3
- cam_r_L1_hol_2: room rule: wall ΔE 5.645 > 5.0 in r_L1_hol; a1 -> cycles
- cam_r_L1_hol_3: room rule ran a2
- cam_r_L1_hol_3: room rule ran a3
- cam_r_L1_hol_3: room rule: wall ΔE 5.645 > 5.0 in r_L1_hol; a1 -> cycles

## Prompts

- cam_r_L0_banyo_1: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, washing machine, washbasin, toilet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_banyo_2: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, washbasin, washing machine, toilet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_banyo_3: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_1: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_2: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_3: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_1: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, dining table, fridge, stove, kitchen sink. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_2: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, dining table, fridge, stove, kitchen sink. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_3: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, fridge, dining table, stove, kitchen sink. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_1: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, armchair, TV unit, coffee table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_2: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, TV unit, coffee table, bookshelf, sofa. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_3: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, armchair, coffee table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, wardrobe, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, wardrobe, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_1: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_2: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_3: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, bookshelf, single bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, single bed, chair, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, bookshelf. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe, desk, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, wardrobe, double bed, desk, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_1: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, chair, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_2: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_3: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, chair, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, chair, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

## Models

| role | repo | revision | licence | files |
|---|---|---|---|---|
| polish base | Tongyi-MAI/Z-Image-Turbo | `f332072aa78b` | Apache-2.0 | model_index.json, scheduler/*, text_encoder/*, tokenizer/*, transformer/*, vae/* |
| polish controlnet | alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1 | `5155fc56d178` | Apache-2.0 | Z-Image-Turbo-Fun-Controlnet-Union-2.1-2602-8steps.safetensors |
| gate depth | depth-anything/Depth-Anything-V2-Small-hf | `5426e4f0f365` | Apache-2.0 | - |
| gate dino | facebook/dinov2-base | `f9e44c814b77` | Apache-2.0 | - |
| gate sam | facebook/sam2.1-hiera-large | `665f8e2ad61c` | Apache-2.0 | - |

## Warnings

None.
