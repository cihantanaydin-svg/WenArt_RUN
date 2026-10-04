# Polish report: synthetic-04 (run)

14 views, 30 attempts (30 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Server Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 2.4 s, prompt encoding 1.7 s, 1.39 s per forward, run 184 s.

Final images: 7 polished, 7 Cycles (gate 2, room 5). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L3_banyo_1 | r_L3_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 5.05 | 1 |
| cam_r_L3_banyo_2 | r_L3_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.8 | 1 |
| cam_r_L3_cocuk_odasi_1 | r_L3_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.83 | 2 |
| cam_r_L3_cocuk_odasi_2 | r_L3_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.83 | 1 |
| cam_r_L3_cocuk_odasi_3 | r_L3_cocuk_odasi | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L3_025 0.377 (needs <= 0.14) | 1.83 | 1 |
| cam_r_L3_hol_1 | r_L3_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L3_hol_2 | r_L3_hol | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.81 | 0 |
| cam_r_L3_hol_3 | r_L3_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 0 |
| cam_r_L3_salon_mutfak_1 | r_L3_salon_mutfak | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | edges:global 0.922 (needs >= 0.935); edges:dec_L3_004 0.845 (needs >= 0.87) | 1.83 | 3 |
| cam_r_L3_salon_mutfak_2 | r_L3_salon_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 2 |
| cam_r_L3_salon_mutfak_3 | r_L3_salon_mutfak | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.8 | 3 |
| cam_r_L3_yatak_odasi_1 | r_L3_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.83 | 1 |
| cam_r_L3_yatak_odasi_2 | r_L3_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.84 | 1 |
| cam_r_L3_yatak_odasi_3 | r_L3_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.83 | 1 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L3_banyo | ok | - | 0.37 | - | cam_r_L3_banyo_1, cam_r_L3_banyo_2 |
| r_L3_cocuk_odasi | downgraded | cycles | 6.46 | - | cam_r_L3_cocuk_odasi_1, cam_r_L3_cocuk_odasi_2 |
| r_L3_hol | ok | - | 1.19 | - | cam_r_L3_hol_1, cam_r_L3_hol_2, cam_r_L3_hol_3 |
| r_L3_salon_mutfak | ok | - | 1.85 | - | cam_r_L3_salon_mutfak_2, cam_r_L3_salon_mutfak_3 |
| r_L3_yatak_odasi | downgraded | cycles | 5.8 | - | cam_r_L3_yatak_odasi_1, cam_r_L3_yatak_odasi_2, cam_r_L3_yatak_odasi_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L3_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 5.05 | accept | - | - |
| cam_r_L3_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L3_cocuk_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.93 | accept | - | - |
| cam_r_L3_cocuk_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L3_cocuk_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | accept | - | - |
| cam_r_L3_cocuk_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.81 | accept | - | - |
| cam_r_L3_cocuk_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L3_cocuk_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | accept | - | - |
| cam_r_L3_cocuk_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | depth:f_L3_025 0.41 (needs <= 0.14) | - |
| cam_r_L3_cocuk_odasi_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 7.33 | reject | depth:f_L3_025 0.37 (needs <= 0.14) | - |
| cam_r_L3_cocuk_odasi_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | reject | depth:f_L3_025 0.377 (needs <= 0.14) | - |
| cam_r_L3_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L3_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | masks:f_L3_022 0.581 (needs >= 0.62) | - |
| cam_r_L3_hol_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L3_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L3_salon_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | edges:global 0.86 (needs >= 0.935); edges:dec_L3_004 0.72 (needs >= 0.87) | - |
| cam_r_L3_salon_mutfak_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | reject | edges:global 0.881 (needs >= 0.935); edges:dec_L3_004 0.766 (needs >= 0.87) | - |
| cam_r_L3_salon_mutfak_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | reject | edges:global 0.922 (needs >= 0.935); edges:dec_L3_004 0.845 (needs >= 0.87) | - |
| cam_r_L3_salon_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L3_salon_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | masks:d_L3_002 0.0952 (needs >= 0.62) | - |
| cam_r_L3_salon_mutfak_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L3_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L3_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L3_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | accept | - | - |
| cam_r_L3_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L3_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L3_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.84 | accept | - | - |
| cam_r_L3_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L3_yatak_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L3_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | accept | - | - |

## Notes

- cam_r_L3_cocuk_odasi_1: room rule ran a2
- cam_r_L3_cocuk_odasi_1: room rule ran a3
- cam_r_L3_cocuk_odasi_1: room rule: wall ΔE 6.456 > 5.0 in r_L3_cocuk_odasi; a1 -> cycles
- cam_r_L3_cocuk_odasi_2: room rule ran a2
- cam_r_L3_cocuk_odasi_2: room rule ran a3
- cam_r_L3_cocuk_odasi_2: room rule: wall ΔE 6.456 > 5.0 in r_L3_cocuk_odasi; a1 -> cycles
- cam_r_L3_yatak_odasi_1: room rule ran a2
- cam_r_L3_yatak_odasi_1: room rule ran a3
- cam_r_L3_yatak_odasi_1: room rule: wall ΔE 5.8 > 5.0 in r_L3_yatak_odasi; a1 -> cycles
- cam_r_L3_yatak_odasi_2: room rule ran a2
- cam_r_L3_yatak_odasi_2: room rule ran a3
- cam_r_L3_yatak_odasi_2: room rule: wall ΔE 5.8 > 5.0 in r_L3_yatak_odasi; a1 -> cycles
- cam_r_L3_yatak_odasi_3: room rule ran a2
- cam_r_L3_yatak_odasi_3: room rule ran a3
- cam_r_L3_yatak_odasi_3: room rule: wall ΔE 5.8 > 5.0 in r_L3_yatak_odasi; a1 -> cycles

## Prompts

- cam_r_L3_banyo_1: Photorealistic interior photograph of a bathroom in Japandi style. Light ceramic tile walls, light ceramic tile floor, bathtub, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L3_banyo_2: Photorealistic interior photograph of a bathroom in Japandi style. Light ceramic tile walls, light ceramic tile floor, bathtub. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L3_cocuk_odasi_1: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, wardrobe, single bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L3_cocuk_odasi_2: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, wardrobe, single bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L3_cocuk_odasi_3: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, single bed, nightstand, wardrobe. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L3_hol_1: Photorealistic interior photograph of a hallway in Japandi style. Cream plaster walls, dark walnut wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L3_hol_2: Photorealistic interior photograph of a hallway in Japandi style. Cream plaster walls, dark walnut wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L3_hol_3: Photorealistic interior photograph of a hallway in Japandi style. Cream plaster walls, dark walnut wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L3_salon_mutfak_1: Photorealistic interior photograph of a living room in Japandi style. Cream plaster walls, dark walnut wood floor, sofa, coffee table, bookshelf, dining table, kitchen counter. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L3_salon_mutfak_2: Photorealistic interior photograph of a living room in Japandi style. Cream plaster walls, dark walnut wood floor, sofa, TV unit, armchair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L3_salon_mutfak_3: Photorealistic interior photograph of a living room in Japandi style. Cream plaster walls, dark walnut wood floor, sofa, bookshelf, fridge, kitchen counter, dining table, chair, stove. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L3_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L3_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L3_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, double bed, wardrobe. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.

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
