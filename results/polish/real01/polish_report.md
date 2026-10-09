# Polish report: real01 (run)

20 views, 41 attempts (41 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Workstation Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 2.4 s, prompt encoding 1.9 s, 1.32 s per forward, run 199 s.

Final images: 11 polished, 9 Cycles (room 9). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_1 | r_L0_bath_toilet | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.77 | 0 |
| cam_r_L0_bath_toilet_2 | r_L0_bath_toilet | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.67 | 0 |
| cam_r_L0_bed_room_1 | r_L0_bed_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.68 | 1 |
| cam_r_L0_bed_room_2 | r_L0_bed_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.69 | 2 |
| cam_r_L0_bed_room_2_1 | r_L0_bed_room_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.79 | 1 |
| cam_r_L0_bed_room_2_2 | r_L0_bed_room_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 2 |
| cam_r_L0_bed_room_2_3 | r_L0_bed_room_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.79 | 2 |
| cam_r_L0_bed_room_3 | r_L0_bed_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.7 | 2 |
| cam_r_L0_dining_1 | r_L0_dining | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.71 | 2 |
| cam_r_L0_dining_2 | r_L0_dining | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.75 | 1 |
| cam_r_L0_dining_3 | r_L0_dining | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 1 |
| cam_r_L0_drawing_room_1 | r_L0_drawing_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.74 | 1 |
| cam_r_L0_drawing_room_2 | r_L0_drawing_room | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.77 | 1 |
| cam_r_L0_drawing_room_3 | r_L0_drawing_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L0_kitchen_1 | r_L0_kitchen | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.79 | 2 |
| cam_r_L0_kitchen_2 | r_L0_kitchen | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L0_026 0.233 (needs <= 0.14) | 1.78 | 2 |
| cam_r_L0_kitchen_3 | r_L0_kitchen | cycles (room) | - | 0.25 / canny / 0.8 / native / plain | accept | - | 2.77 | 2 |
| cam_r_L0_room_1 | r_L0_room | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.79 | 0 |
| cam_r_L0_room_2 | r_L0_room | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L0_room_3 | r_L0_room | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.79 | 0 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L0_bath_toilet | ok | - | 4.65 | - | cam_r_L0_bath_toilet_1, cam_r_L0_bath_toilet_2 |
| r_L0_bed_room | ok | - | 3.88 | - | cam_r_L0_bed_room_1, cam_r_L0_bed_room_2, cam_r_L0_bed_room_3 |
| r_L0_bed_room_2 | downgraded | cycles | 6.12 | - | cam_r_L0_bed_room_2_1, cam_r_L0_bed_room_2_2, cam_r_L0_bed_room_2_3 |
| r_L0_dining | ok | - | 4.65 | - | cam_r_L0_dining_1, cam_r_L0_dining_2, cam_r_L0_dining_3 |
| r_L0_drawing_room | ok | - | 1.21 | - | cam_r_L0_drawing_room_1, cam_r_L0_drawing_room_2, cam_r_L0_drawing_room_3 |
| r_L0_kitchen | downgraded | cycles | 9.59 | - | cam_r_L0_kitchen_1, cam_r_L0_kitchen_2, cam_r_L0_kitchen_3 |
| r_L0_room | downgraded | cycles | 8.1 | - | cam_r_L0_room_1, cam_r_L0_room_2, cam_r_L0_room_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L0_bath_toilet_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.67 | accept | - | - |
| cam_r_L0_bed_room_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.68 | accept | - | - |
| cam_r_L0_bed_room_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.69 | accept | - | - |
| cam_r_L0_bed_room_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.69 | accept | - | - |
| cam_r_L0_bed_room_2_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_bed_room_2_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.79 | accept | - | - |
| cam_r_L0_bed_room_2_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.69 | accept | - | - |
| cam_r_L0_bed_room_2_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_bed_room_2_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_bed_room_2_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.71 | accept | - | - |
| cam_r_L0_bed_room_2_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_bed_room_2_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.79 | accept | - | - |
| cam_r_L0_bed_room_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.7 | accept | - | - |
| cam_r_L0_dining_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.71 | accept | - | - |
| cam_r_L0_dining_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.71 | reject | edges:win_L0_005 0.843 (needs >= 0.87) | - |
| cam_r_L0_dining_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.75 | accept | - | - |
| cam_r_L0_dining_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | reject | edges:f_L0_014 0.84 (needs >= 0.87) | - |
| cam_r_L0_dining_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | reject | edges:f_L0_014 0.858 (needs >= 0.87) | - |
| cam_r_L0_dining_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_drawing_room_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | accept | - | - |
| cam_r_L0_drawing_room_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | reject | depth:f_L0_018 0.164 (needs <= 0.14); masks:d_L0_003 0.0111 (needs >= 0.62) | - |
| cam_r_L0_drawing_room_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_drawing_room_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L0_kitchen_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | reject | edges:f_L0_001 0.807 (needs >= 0.87); edges:f_L0_027 0.793 (needs >= 0.87) | - |
| cam_r_L0_kitchen_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L0_kitchen_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.79 | accept | - | - |
| cam_r_L0_kitchen_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | reject | depth:f_L0_026 0.247 (needs <= 0.14) | - |
| cam_r_L0_kitchen_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.78 | accept | - | - |
| cam_r_L0_kitchen_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | reject | depth:f_L0_026 0.233 (needs <= 0.14) | - |
| cam_r_L0_kitchen_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L0_kitchen_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_room_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L0_room_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.78 | accept | - | - |
| cam_r_L0_room_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.79 | accept | - | - |
| cam_r_L0_room_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | reject | edges:global 0.898 (needs >= 0.935); edges:d_L0_002 0.736 (needs >= 0.87); edges:f_L0_001 0.833 (needs >= 0.87) | - |
| cam_r_L0_room_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.78 | accept | - | - |
| cam_r_L0_room_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_room_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L0_room_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_room_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.79 | accept | - | - |

## Notes

- cam_r_L0_bed_room_2_1: room rule ran a2
- cam_r_L0_bed_room_2_1: room rule ran a3
- cam_r_L0_bed_room_2_1: room rule: wall ΔE 6.115 > 5.0 in r_L0_bed_room_2; a1 -> cycles
- cam_r_L0_bed_room_2_2: room rule ran a2
- cam_r_L0_bed_room_2_2: room rule ran a3
- cam_r_L0_bed_room_2_2: room rule: wall ΔE 6.115 > 5.0 in r_L0_bed_room_2; a1 -> cycles
- cam_r_L0_bed_room_2_3: room rule ran a2
- cam_r_L0_bed_room_2_3: room rule ran a3
- cam_r_L0_bed_room_2_3: room rule: wall ΔE 6.115 > 5.0 in r_L0_bed_room_2; a1 -> cycles
- cam_r_L0_kitchen_1: room rule ran a3
- cam_r_L0_kitchen_1: room rule: wall ΔE 9.59 > 5.0 in r_L0_kitchen; a2 -> cycles
- cam_r_L0_kitchen_2: room rule ran a3
- cam_r_L0_kitchen_2: room rule: wall ΔE 9.59 > 5.0 in r_L0_kitchen; a2 -> cycles
- cam_r_L0_kitchen_3: room rule ran a2
- cam_r_L0_kitchen_3: room rule: wall ΔE 9.59 > 5.0 in r_L0_kitchen; a1 -> cycles
- cam_r_L0_room_1: room rule ran a2
- cam_r_L0_room_1: room rule ran a3
- cam_r_L0_room_1: room rule: wall ΔE 8.1 > 5.0 in r_L0_room; a1 -> cycles
- cam_r_L0_room_2: room rule ran a3
- cam_r_L0_room_2: room rule: wall ΔE 8.1 > 5.0 in r_L0_room; a2 -> cycles
- cam_r_L0_room_3: room rule ran a2
- cam_r_L0_room_3: room rule ran a3
- cam_r_L0_room_3: room rule: wall ΔE 8.1 > 5.0 in r_L0_room; a1 -> cycles

## Prompts

- cam_r_L0_bath_toilet_1: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_bath_toilet_2: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_bed_room_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_bed_room_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_bed_room_2_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_bed_room_2_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_bed_room_2_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_bed_room_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_dining_1: Photorealistic interior photograph of a dining room in Scandinavian style. White plaster walls, light oak wood floor, dining table, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_dining_2: Photorealistic interior photograph of a dining room in Scandinavian style. White plaster walls, light oak wood floor, dining table, sideboard, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_dining_3: Photorealistic interior photograph of a dining room in Scandinavian style. White plaster walls, light oak wood floor, dining table, sideboard, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_drawing_room_1: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, TV unit, coffee table, floor lamp. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_drawing_room_2: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, coffee table, TV unit, floor lamp. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_drawing_room_3: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, coffee table, floor lamp, TV unit. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_kitchen_1: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, wall cabinets. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_kitchen_2: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, tall cabinet, wall cabinets. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_kitchen_3: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, tall cabinet, wall cabinets. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_room_1: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_room_2: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_room_3: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.

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
