# Polish report: synthetic-04 (run)

14 views, 20 attempts (20 polished now, 0 reused). Device NVIDIA RTX PRO 4500 Blackwell, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 15.7 s, prompt encoding 8.1 s, 2.84 s per forward, run 247 s.

Final images: 11 polished, 3 Cycles (room 3). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L3_banyo_1 | r_L3_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.54 | 1 |
| cam_r_L3_banyo_2 | r_L3_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 1 |
| cam_r_L3_cocuk_odasi_1 | r_L3_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.28 | 2 |
| cam_r_L3_cocuk_odasi_2 | r_L3_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.26 | 1 |
| cam_r_L3_cocuk_odasi_3 | r_L3_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.28 | 1 |
| cam_r_L3_hol_1 | r_L3_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.28 | 0 |
| cam_r_L3_hol_2 | r_L3_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.28 | 0 |
| cam_r_L3_hol_3 | r_L3_hol | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.29 | 0 |
| cam_r_L3_salon_mutfak_1 | r_L3_salon_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.3 | 2 |
| cam_r_L3_salon_mutfak_2 | r_L3_salon_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.31 | 3 |
| cam_r_L3_salon_mutfak_3 | r_L3_salon_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.3 | 2 |
| cam_r_L3_yatak_odasi_1 | r_L3_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L3_yatak_odasi_2 | r_L3_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.77 | 2 |
| cam_r_L3_yatak_odasi_3 | r_L3_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.81 | 2 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L3_banyo | ok | - | 1.17 | - | cam_r_L3_banyo_1, cam_r_L3_banyo_2 |
| r_L3_cocuk_odasi | ok | - | 4.2 | - | cam_r_L3_cocuk_odasi_1, cam_r_L3_cocuk_odasi_2, cam_r_L3_cocuk_odasi_3 |
| r_L3_hol | ok | - | 1.3 | - | cam_r_L3_hol_1, cam_r_L3_hol_2, cam_r_L3_hol_3 |
| r_L3_salon_mutfak | ok | - | 2.72 | - | cam_r_L3_salon_mutfak_1, cam_r_L3_salon_mutfak_2, cam_r_L3_salon_mutfak_3 |
| r_L3_yatak_odasi | downgraded | cycles | 7.66 | - | cam_r_L3_yatak_odasi_1, cam_r_L3_yatak_odasi_2, cam_r_L3_yatak_odasi_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L3_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.54 | accept | - | - |
| cam_r_L3_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L3_cocuk_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.28 | accept | - | - |
| cam_r_L3_cocuk_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L3_cocuk_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.28 | accept | - | - |
| cam_r_L3_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.28 | accept | - | - |
| cam_r_L3_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.28 | accept | - | - |
| cam_r_L3_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.29 | accept | - | - |
| cam_r_L3_salon_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.3 | accept | - | - |
| cam_r_L3_salon_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.31 | accept | - | - |
| cam_r_L3_salon_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.3 | accept | - | - |
| cam_r_L3_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.29 | accept | - | - |
| cam_r_L3_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L3_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.78 | accept | - | - |
| cam_r_L3_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.3 | accept | - | - |
| cam_r_L3_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | accept | - | - |
| cam_r_L3_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.77 | accept | - | - |
| cam_r_L3_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.3 | reject | depth:f_L3_015 0.212 (needs <= 0.14) | - |
| cam_r_L3_yatak_odasi_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.07 | accept | - | - |
| cam_r_L3_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.81 | accept | - | - |

## Notes

- cam_r_L3_yatak_odasi_1: room rule ran a2
- cam_r_L3_yatak_odasi_1: room rule ran a3
- cam_r_L3_yatak_odasi_1: room rule: wall ΔE 7.655 > 5.0 in r_L3_yatak_odasi; a1 -> cycles
- cam_r_L3_yatak_odasi_2: room rule ran a2
- cam_r_L3_yatak_odasi_2: room rule ran a3
- cam_r_L3_yatak_odasi_2: room rule: wall ΔE 7.655 > 5.0 in r_L3_yatak_odasi; a1 -> cycles
- cam_r_L3_yatak_odasi_3: room rule ran a3
- cam_r_L3_yatak_odasi_3: room rule: wall ΔE 7.655 > 5.0 in r_L3_yatak_odasi; a2 -> cycles

## Prompts

- cam_r_L3_banyo_1: Photorealistic interior photograph of a bathroom in Japandi style. Light ceramic tile walls, light ceramic tile floor, bathtub, toilet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_banyo_2: Photorealistic interior photograph of a bathroom in Japandi style. Light ceramic tile walls, light ceramic tile floor, bathtub. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_cocuk_odasi_1: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, single bed, desk, chair, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_cocuk_odasi_2: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, single bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_cocuk_odasi_3: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, single bed, desk, nightstand, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_hol_1: Photorealistic interior photograph of a hallway in Japandi style. Cream plaster walls, dark walnut wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_hol_2: Photorealistic interior photograph of a hallway in Japandi style. Cream plaster walls, dark walnut wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_hol_3: Photorealistic interior photograph of a hallway in Japandi style. Cream plaster walls, dark walnut wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_salon_mutfak_1: Photorealistic interior photograph of a living room in Japandi style. Cream plaster walls, dark walnut wood floor, sofa, bookshelf, TV unit, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_salon_mutfak_2: Photorealistic interior photograph of a living room in Japandi style. Cream plaster walls, dark walnut wood floor, sofa, coffee table, bookshelf, dining table, kitchen counter, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_salon_mutfak_3: Photorealistic interior photograph of a living room in Japandi style. Cream plaster walls, dark walnut wood floor, sofa, armchair, TV unit. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_yatak_odasi_1: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, wardrobe, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, wardrobe, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L3_yatak_odasi_3: Photorealistic interior photograph of a bedroom in Japandi style. Cream plaster walls, dark walnut wood floor, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
