# Polish report: synthetic-01 (run)

29 views, 44 attempts (44 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Server Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 4.5 s, prompt encoding 3.1 s, 1.48 s per forward, run 387 s.

Final images: 25 polished, 4 Cycles (gate 1, room 3). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.29 | 1 |
| cam_r_L0_banyo_2 | r_L0_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 7.46 | 1 |
| cam_r_L0_banyo_3 | r_L0_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 7.13 | 0 |
| cam_r_L0_hol_1 | r_L0_hol | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 5.19 | 0 |
| cam_r_L0_hol_2 | r_L0_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 5.56 | 0 |
| cam_r_L0_mutfak_1 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.8 | 1 |
| cam_r_L0_mutfak_2 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L0_mutfak_3 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 10.3 | 1 |
| cam_r_L0_salon_1 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L0_salon_2 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L0_salon_3 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 2 |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.82 | 1 |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.77 | 1 |
| cam_r_L1_banyo_1 | r_L1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.81 | 1 |
| cam_r_L1_banyo_2 | r_L1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.8 | 0 |
| cam_r_L1_banyo_3 | r_L1_banyo | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | masks:f_L1_012 0.226 (needs >= 0.62) | 1.83 | 0 |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.83 | 1 |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.84 | 1 |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.83 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 2 |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 2 |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 2 |
| cam_r_L1_hol_1 | r_L1_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L1_hol_2 | r_L1_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L1_hol_3 | r_L1_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.77 | 0 |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 1 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L0_banyo | ok | - | 2.24 | - | cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_banyo_3 |
| r_L0_hol | ok | - | 1.94 | - | cam_r_L0_hol_1, cam_r_L0_hol_2 |
| r_L0_mutfak | ok | - | 4.34 | - | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | ok | - | 1.03 | - | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_yatak_odasi | ok | - | 2.82 | - | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_banyo | ok | - | 0.906 | - | cam_r_L1_banyo_1, cam_r_L1_banyo_2 |
| r_L1_cocuk_odasi | downgraded | cycles | 6.91 | - | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | ok | - | 2.08 | - | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | ok | - | 3.95 | - | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | ok | - | 4.6 | - | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.29 | accept | - | - |
| cam_r_L0_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | edges:f_L0_012 0.826 (needs >= 0.87); added_lines:struct:floor 0.049 (needs <= 0.04) | - |
| cam_r_L0_banyo_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 7.46 | accept | - | - |
| cam_r_L0_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 6.38 | reject | edges:f_L0_012 0.857 (needs >= 0.87) | - |
| cam_r_L0_banyo_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 7.13 | accept | - | - |
| cam_r_L0_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | reject | edges:d_L0_005 0.812 (needs >= 0.87) | - |
| cam_r_L0_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 7.26 | reject | edges:d_L0_005 0.834 (needs >= 0.87) | - |
| cam_r_L0_hol_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 5.19 | accept | - | - |
| cam_r_L0_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 5.56 | accept | - | - |
| cam_r_L0_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L0_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 10.3 | accept | - | - |
| cam_r_L0_salon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_salon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_salon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | edges:dec_L0_010 0.863 (needs >= 0.87) | - |
| cam_r_L0_yatak_odasi_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.82 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | depth:global 0.0637 (needs <= 0.05); depth:f_L1_014 0.151 (needs <= 0.14); depth:f_L1_015 0.442 (needs <= 0.14) | - |
| cam_r_L1_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | depth:global 0.0547 (needs <= 0.05) | - |
| cam_r_L1_banyo_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L1_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | masks:f_L1_012 0.592 (needs >= 0.62) | - |
| cam_r_L1_banyo_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | reject | masks:f_L1_012 0.229 (needs >= 0.62) | - |
| cam_r_L1_banyo_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | reject | masks:f_L1_012 0.226 (needs >= 0.62) | - |
| cam_r_L1_cocuk_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.84 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |

## Notes

- cam_r_L1_cocuk_odasi_1: room rule ran a2
- cam_r_L1_cocuk_odasi_1: room rule ran a3
- cam_r_L1_cocuk_odasi_1: room rule: wall ΔE 6.908 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_cocuk_odasi_2: room rule ran a2
- cam_r_L1_cocuk_odasi_2: room rule ran a3
- cam_r_L1_cocuk_odasi_2: room rule: wall ΔE 6.908 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_cocuk_odasi_3: room rule ran a2
- cam_r_L1_cocuk_odasi_3: room rule ran a3
- cam_r_L1_cocuk_odasi_3: room rule: wall ΔE 6.908 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles

## Prompts

- cam_r_L0_banyo_1: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, washing machine, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_banyo_2: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, washing machine. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_banyo_3: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_hol_1: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_hol_2: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_mutfak_1: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, dining table, stove, fridge, kitchen sink. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_mutfak_2: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, dining table, fridge, stove. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_mutfak_3: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_salon_1: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, bookshelf, coffee table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_salon_2: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, bookshelf, armchair, coffee table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_salon_3: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, coffee table, TV unit, bookshelf. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_banyo_1: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, toilet, bathtub, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_banyo_2: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_banyo_3: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, shower, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_cocuk_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, single bed, wardrobe, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_cocuk_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, wardrobe, single bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_cocuk_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, wardrobe, single bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_hol_1: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_hol_2: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_hol_3: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.

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
