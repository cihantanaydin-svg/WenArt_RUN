# Polish report: real02 (run)

17 views, 21 attempts (21 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Workstation Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 2.3 s, prompt encoding 2 s, 1.3 s per forward, run 116 s.

Final images: 9 polished, 8 Cycles (gate 5, room 3). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L-1b_acik_mutfak_1 | r_L-1b_acik_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.81 | 1 |
| cam_r_L-1b_acik_mutfak_2 | r_L-1b_acik_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.7 | 1 |
| cam_r_L-1b_acik_mutfak_2_1 | r_L-1b_acik_mutfak_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.79 | 1 |
| cam_r_L-1b_acik_mutfak_2_2 | r_L-1b_acik_mutfak_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.79 | 1 |
| cam_r_L-1b_acik_mutfak_2_3 | r_L-1b_acik_mutfak_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 1 |
| cam_r_L-1b_acik_mutfak_3 | r_L-1b_acik_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.72 | 1 |
| cam_r_L-1b_koridor_1 | r_L-1b_koridor | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.8 | 1 |
| cam_r_L-1b_koridor_2 | r_L-1b_koridor | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.74 | 0 |
| cam_r_L-1b_koridor_3 | r_L-1b_koridor | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.74 | 0 |
| cam_r_L-1b_oda_1 | r_L-1b_oda | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L-1b_oda_2 | r_L-1b_oda | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.78 | 0 |
| cam_r_L-1b_oda_3 | r_L-1b_oda | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.78 | 0 |
| ext_1 | - | cycles (gate) | - | - | - | - | - | - |
| ext_2 | - | cycles (gate) | - | - | - | - | - | - |
| ext_3 | - | cycles (gate) | - | - | - | - | - | - |
| ext_4 | - | cycles (gate) | - | - | - | - | - | - |
| ext_5 | - | cycles (gate) | - | - | - | - | - | - |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L-1b_acik_mutfak | ok | - | 3.22 | - | cam_r_L-1b_acik_mutfak_1, cam_r_L-1b_acik_mutfak_2, cam_r_L-1b_acik_mutfak_3 |
| r_L-1b_acik_mutfak_2 | downgraded | cycles | 5.57 | - | cam_r_L-1b_acik_mutfak_2_1, cam_r_L-1b_acik_mutfak_2_2, cam_r_L-1b_acik_mutfak_2_3 |
| r_L-1b_koridor | ok | - | 3.17 | - | cam_r_L-1b_koridor_1, cam_r_L-1b_koridor_2, cam_r_L-1b_koridor_3 |
| r_L-1b_oda | ok | - | 0.662 | - | cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1b_acik_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.81 | accept | - | - |
| cam_r_L-1b_acik_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.7 | accept | - | - |
| cam_r_L-1b_acik_mutfak_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.71 | reject | depth:f_L-1b_033 0.165 (needs <= 0.14) | - |
| cam_r_L-1b_acik_mutfak_2_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L-1b_acik_mutfak_2_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.79 | accept | - | - |
| cam_r_L-1b_acik_mutfak_2_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | accept | - | - |
| cam_r_L-1b_acik_mutfak_2_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L-1b_acik_mutfak_2_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.79 | accept | - | - |
| cam_r_L-1b_acik_mutfak_2_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | reject | edges:f_L-1b_030 0.679 (needs >= 0.87); edges:f_L-1b_053 0.866 (needs >= 0.87); masks:f_L-1b_030 0.611 (needs >= 0.62) | - |
| cam_r_L-1b_acik_mutfak_2_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.75 | accept | - | - |
| cam_r_L-1b_acik_mutfak_2_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L-1b_acik_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | accept | - | - |
| cam_r_L-1b_koridor_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | reject | edges:f_L-1b_002 0.864 (needs >= 0.87); colour:f_L-1b_006 9.11 (needs <= 8) | - |
| cam_r_L-1b_koridor_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L-1b_koridor_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | accept | - | - |
| cam_r_L-1b_koridor_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | accept | - | - |
| cam_r_L-1b_oda_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L-1b_oda_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | reject | edges:f_L-1b_041 0.861 (needs >= 0.87) | - |
| cam_r_L-1b_oda_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.78 | accept | - | - |
| cam_r_L-1b_oda_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | reject | edges:f_L-1b_042 0.849 (needs >= 0.87) | - |
| cam_r_L-1b_oda_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.78 | accept | - | - |

## Notes

- cam_r_L-1b_acik_mutfak_2_1: room rule ran a3
- cam_r_L-1b_acik_mutfak_2_1: room rule: wall ΔE 5.569 > 5.0 in r_L-1b_acik_mutfak_2; a2 -> cycles
- cam_r_L-1b_acik_mutfak_2_2: room rule ran a2
- cam_r_L-1b_acik_mutfak_2_2: room rule ran a3
- cam_r_L-1b_acik_mutfak_2_2: room rule: wall ΔE 5.569 > 5.0 in r_L-1b_acik_mutfak_2; a1 -> cycles
- cam_r_L-1b_acik_mutfak_2_3: room rule ran a3
- cam_r_L-1b_acik_mutfak_2_3: room rule: wall ΔE 5.569 > 5.0 in r_L-1b_acik_mutfak_2; a2 -> cycles
- ext_1: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_2: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_3: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_4: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_5: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)

## Prompts

- cam_r_L-1b_acik_mutfak_1: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor, tall cabinet, fridge, wall cabinets. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_acik_mutfak_2: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_acik_mutfak_2_1: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor, fridge, wall cabinets. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_acik_mutfak_2_2: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor, kitchen island, bar stool. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_acik_mutfak_2_3: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor, kitchen island, bar stool. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_acik_mutfak_3: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor, tall cabinet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_koridor_1: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1b_koridor_2: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1b_koridor_3: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1b_oda_1: Photorealistic interior photograph of a room in modern style. Warm greige smooth painted walls, light oak wood floor, armchair, bookshelf, dining table, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_oda_2: Photorealistic interior photograph of a room in modern style. Warm greige smooth painted walls, light oak wood floor, bookshelf, dining table, armchair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_oda_3: Photorealistic interior photograph of a room in modern style. Warm greige smooth painted walls, light oak wood floor, armchair, desk, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- ext_1: Photorealistic architectural photograph of a house exterior in modern style, seen from a corner of the plot at eye level, two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 32.46 mm lens.
- ext_2: Photorealistic architectural photograph of a house exterior in modern style, seen from a corner of the plot at eye level, two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 32.46 mm lens.
- ext_3: Photorealistic architectural photograph of a house exterior in modern style, seen from a corner of the plot at eye level, two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 32.46 mm lens.
- ext_4: Photorealistic architectural photograph of a house exterior in modern style, seen from a corner of the plot at eye level, two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 32.46 mm lens.
- ext_5: Photorealistic architectural photograph of a house exterior in modern style, seen in a three-quarter aerial view from above, roof and two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 28.55 mm lens.

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
