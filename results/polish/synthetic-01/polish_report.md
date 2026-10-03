# Polish report: synthetic-01 (run)

29 views, 54 attempts (54 polished now, 0 reused). Device NVIDIA RTX PRO 4500 Blackwell, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 9.5 s, prompt encoding 5.5 s, 2.88 s per forward, run 536 s.

Final images: 18 polished, 11 Cycles (gate 2, room 9). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.01 | 1 |
| cam_r_L0_banyo_2 | r_L0_banyo | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L0_banyo_3 | r_L0_banyo | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.0516 (needs <= 0.05) | 3.79 | 0 |
| cam_r_L0_hol_1 | r_L0_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L0_hol_2 | r_L0_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L0_mutfak_1 | r_L0_mutfak | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L0_mutfak_2 | r_L0_mutfak | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.76 | 1 |
| cam_r_L0_mutfak_3 | r_L0_mutfak | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.76 | 1 |
| cam_r_L0_salon_1 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 1 |
| cam_r_L0_salon_2 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 1 |
| cam_r_L0_salon_3 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 2 |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.77 | 0 |
| cam_r_L1_banyo_1 | r_L1_banyo | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.0563 (needs <= 0.05) | 3.8 | 0 |
| cam_r_L1_banyo_2 | r_L1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.03 | 1 |
| cam_r_L1_banyo_3 | r_L1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L1_017 0.211 (needs <= 0.14) | 3.79 | 1 |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | cycles (room) | - | 0.25 / canny / 0.8 / native / plain | accept | - | 6.02 | 1 |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | cycles (room) | - | 0.25 / canny / 0.8 / native / plain | accept | - | 6.01 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 2 |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 0 |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 1 |
| cam_r_L1_hol_1 | r_L1_hol | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.03 | 1 |
| cam_r_L1_hol_2 | r_L1_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_hol_3 | r_L1_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 0 |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 1 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L0_banyo | ok | - | 0.285 | - | cam_r_L0_banyo_1, cam_r_L0_banyo_2 |
| r_L0_hol | ok | - | 0.688 | - | cam_r_L0_hol_1, cam_r_L0_hol_2 |
| r_L0_mutfak | downgraded | cycles | 10.2 | - | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | ok | - | 4.74 | - | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_yatak_odasi | downgraded | cycles | 7.32 | - | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_banyo | ok | - | 1.2 | - | cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | downgraded | cycles | 5.33 | - | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | ok | - | 2.58 | - | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | ok | - | 0.855 | - | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | ok | - | 3.3 | - | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.42 | reject | depth:global 0.106 (needs <= 0.05); depth:d_L0_005 0.268 (needs <= 0.14); depth:f_L0_011 0.546 (needs <= 0.14); depth:f_L0_013 0.159 (needs <= 0.14) | - |
| cam_r_L0_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |
| cam_r_L0_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.2 | reject | depth:global 0.0534 (needs <= 0.05); depth:d_L0_005 0.797 (needs <= 0.14) | - |
| cam_r_L0_banyo_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | reject | depth:d_L0_005 0.548 (needs <= 0.14) | - |
| cam_r_L0_banyo_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L0_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | reject | depth:global 0.0922 (needs <= 0.05); depth:f_L0_012 0.321 (needs <= 0.14) | - |
| cam_r_L0_banyo_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | reject | depth:global 0.0686 (needs <= 0.05); depth:f_L0_012 0.254 (needs <= 0.14) | - |
| cam_r_L0_banyo_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.79 | reject | depth:global 0.0516 (needs <= 0.05) | - |
| cam_r_L0_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L0_mutfak_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L0_mutfak_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L0_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_mutfak_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |
| cam_r_L0_mutfak_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | accept | - | - |
| cam_r_L0_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L0_mutfak_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.02 | accept | - | - |
| cam_r_L0_mutfak_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | accept | - | - |
| cam_r_L0_salon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_salon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_salon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.78 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.79 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.02 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.77 | accept | - | - |
| cam_r_L1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.106 (needs <= 0.05); depth:f_L1_012 0.166 (needs <= 0.14) | - |
| cam_r_L1_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | reject | depth:global 0.0855 (needs <= 0.05) | - |
| cam_r_L1_banyo_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.8 | reject | depth:global 0.0563 (needs <= 0.05) | - |
| cam_r_L1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.0764 (needs <= 0.05); depth:f_L1_012 0.157 (needs <= 0.14) | - |
| cam_r_L1_banyo_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L1_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.79 | reject | depth:f_L1_017 0.211 (needs <= 0.14) | - |
| cam_r_L1_cocuk_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.02 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | masks:d_L1_004 0.499 (needs >= 0.62) | - |
| cam_r_L1_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |

## Notes

- cam_r_L0_mutfak_1: room rule ran a2
- cam_r_L0_mutfak_1: room rule ran a3
- cam_r_L0_mutfak_1: room rule: wall ΔE 10.15 > 5.0 in r_L0_mutfak; a1 -> cycles
- cam_r_L0_mutfak_2: room rule ran a2
- cam_r_L0_mutfak_2: room rule ran a3
- cam_r_L0_mutfak_2: room rule: wall ΔE 10.15 > 5.0 in r_L0_mutfak; a1 -> cycles
- cam_r_L0_mutfak_3: room rule ran a2
- cam_r_L0_mutfak_3: room rule ran a3
- cam_r_L0_mutfak_3: room rule: wall ΔE 10.15 > 5.0 in r_L0_mutfak; a1 -> cycles
- cam_r_L0_yatak_odasi_1: room rule ran a2
- cam_r_L0_yatak_odasi_1: room rule ran a3
- cam_r_L0_yatak_odasi_1: room rule: wall ΔE 7.318 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L0_yatak_odasi_2: room rule ran a2
- cam_r_L0_yatak_odasi_2: room rule ran a3
- cam_r_L0_yatak_odasi_2: room rule: wall ΔE 7.318 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L0_yatak_odasi_3: room rule ran a2
- cam_r_L0_yatak_odasi_3: room rule ran a3
- cam_r_L0_yatak_odasi_3: room rule: wall ΔE 7.318 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L1_cocuk_odasi_1: room rule ran a2
- cam_r_L1_cocuk_odasi_1: room rule ran a3
- cam_r_L1_cocuk_odasi_1: room rule: wall ΔE 5.335 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_cocuk_odasi_2: room rule ran a2
- cam_r_L1_cocuk_odasi_2: room rule: wall ΔE 5.335 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_cocuk_odasi_3: room rule ran a2
- cam_r_L1_cocuk_odasi_3: room rule: wall ΔE 5.335 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles

## Prompts

- cam_r_L0_banyo_1: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, washing machine, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_banyo_2: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, washing machine, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_banyo_3: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_1: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_2: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_1: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, dining table, fridge, kitchen sink, stove, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_2: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, dining table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_3: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_1: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, bookshelf, coffee table, armchair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_2: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, coffee table, armchair, TV unit. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_3: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, coffee table, bookshelf, TV unit. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, wardrobe, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, wardrobe, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_1: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_2: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_3: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, toilet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, single bed, wardrobe, bookshelf, nightstand, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, wardrobe, bookshelf, single bed, nightstand, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, single bed, wardrobe, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, wardrobe, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, desk. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_1: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_2: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, chair, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_3: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, chair, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
