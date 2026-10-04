# Polish report: real01 (run)

20 views, 42 attempts (42 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Server Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 7.1 s, prompt encoding 3.3 s, 1.85 s per forward, run 498 s.

Final images: 10 polished, 10 Cycles (gate 1, room 9). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_1 | r_L0_bath_toilet | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 4.13 | 0 |
| cam_r_L0_bath_toilet_2 | r_L0_bath_toilet | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L0_022 0.212 (needs <= 0.14) | 1.83 | 0 |
| cam_r_L0_bed_room_1 | r_L0_bed_room | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.08 | 1 |
| cam_r_L0_bed_room_2 | r_L0_bed_room | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 9.12 | 2 |
| cam_r_L0_bed_room_2_1 | r_L0_bed_room_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 8.91 | 1 |
| cam_r_L0_bed_room_2_2 | r_L0_bed_room_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 4.21 | 2 |
| cam_r_L0_bed_room_2_3 | r_L0_bed_room_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 4.61 | 2 |
| cam_r_L0_bed_room_3 | r_L0_bed_room | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.56 | 1 |
| cam_r_L0_dining_1 | r_L0_dining | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.79 | 2 |
| cam_r_L0_dining_2 | r_L0_dining | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.77 | 1 |
| cam_r_L0_dining_3 | r_L0_dining | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 4.66 | 1 |
| cam_r_L0_drawing_room_1 | r_L0_drawing_room | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.8 | 1 |
| cam_r_L0_drawing_room_2 | r_L0_drawing_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 4.99 | 1 |
| cam_r_L0_drawing_room_3 | r_L0_drawing_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.76 | 1 |
| cam_r_L0_kitchen_1 | r_L0_kitchen | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.77 | 2 |
| cam_r_L0_kitchen_2 | r_L0_kitchen | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.77 | 2 |
| cam_r_L0_kitchen_3 | r_L0_kitchen | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.82 | 2 |
| cam_r_L0_room_1 | r_L0_room | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 5.41 | 0 |
| cam_r_L0_room_2 | r_L0_room | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 4.14 | 0 |
| cam_r_L0_room_3 | r_L0_room | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 5.98 | 0 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L0_bath_toilet | ok | - | - | - | cam_r_L0_bath_toilet_1 |
| r_L0_bed_room | downgraded | cycles | 5.25 | - | cam_r_L0_bed_room_1, cam_r_L0_bed_room_2, cam_r_L0_bed_room_3 |
| r_L0_bed_room_2 | downgraded | cycles | 5.19 | - | cam_r_L0_bed_room_2_1, cam_r_L0_bed_room_2_2, cam_r_L0_bed_room_2_3 |
| r_L0_dining | ok | - | 3.21 | - | cam_r_L0_dining_1, cam_r_L0_dining_2, cam_r_L0_dining_3 |
| r_L0_drawing_room | ok | - | 1.22 | - | cam_r_L0_drawing_room_1, cam_r_L0_drawing_room_2, cam_r_L0_drawing_room_3 |
| r_L0_kitchen | ok | - | 2.26 | - | cam_r_L0_kitchen_1, cam_r_L0_kitchen_2, cam_r_L0_kitchen_3 |
| r_L0_room | downgraded | cycles | 5.46 | - | cam_r_L0_room_1, cam_r_L0_room_2, cam_r_L0_room_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.13 | accept | - | - |
| cam_r_L0_bath_toilet_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | depth:f_L0_022 0.211 (needs <= 0.14) | - |
| cam_r_L0_bath_toilet_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | reject | depth:f_L0_022 0.374 (needs <= 0.14) | - |
| cam_r_L0_bath_toilet_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | reject | depth:f_L0_022 0.212 (needs <= 0.14) | - |
| cam_r_L0_bed_room_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_bed_room_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L0_bed_room_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.08 | accept | - | - |
| cam_r_L0_bed_room_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.83 | accept | - | - |
| cam_r_L0_bed_room_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 16.5 | accept | - | - |
| cam_r_L0_bed_room_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 9.12 | accept | - | - |
| cam_r_L0_bed_room_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L0_bed_room_2_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 8.09 | accept | - | - |
| cam_r_L0_bed_room_2_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 8.91 | accept | - | - |
| cam_r_L0_bed_room_2_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.02 | accept | - | - |
| cam_r_L0_bed_room_2_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L0_bed_room_2_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 4.21 | accept | - | - |
| cam_r_L0_bed_room_2_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L0_bed_room_2_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.69 | accept | - | - |
| cam_r_L0_bed_room_2_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 4.61 | accept | - | - |
| cam_r_L0_bed_room_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.04 | accept | - | - |
| cam_r_L0_bed_room_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L0_bed_room_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.56 | accept | - | - |
| cam_r_L0_dining_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.95 | reject | edges:win_L0_009 0.848 (needs >= 0.87) | - |
| cam_r_L0_dining_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.79 | accept | - | - |
| cam_r_L0_dining_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L0_dining_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.66 | accept | - | - |
| cam_r_L0_drawing_room_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | reject | masks:d_L0_003 0.0491 (needs >= 0.62) | - |
| cam_r_L0_drawing_room_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L0_drawing_room_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.99 | accept | - | - |
| cam_r_L0_drawing_room_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L0_kitchen_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L0_kitchen_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L0_kitchen_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.82 | accept | - | - |
| cam_r_L0_room_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | colour:struct:floor 8.41 (needs <= 8) | - |
| cam_r_L0_room_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L0_room_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 5.41 | accept | - | - |
| cam_r_L0_room_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 11.1 | accept | - | - |
| cam_r_L0_room_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.16 | accept | - | - |
| cam_r_L0_room_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 4.14 | accept | - | - |
| cam_r_L0_room_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_room_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 4.27 | accept | - | - |
| cam_r_L0_room_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 5.98 | accept | - | - |

## Notes

- cam_r_L0_bed_room_1: room rule ran a2
- cam_r_L0_bed_room_1: room rule ran a3
- cam_r_L0_bed_room_1: room rule: wall ΔE 5.251 > 5.0 in r_L0_bed_room; a1 -> cycles
- cam_r_L0_bed_room_2: room rule ran a2
- cam_r_L0_bed_room_2: room rule ran a3
- cam_r_L0_bed_room_2: room rule: wall ΔE 5.251 > 5.0 in r_L0_bed_room; a1 -> cycles
- cam_r_L0_bed_room_2_1: room rule ran a2
- cam_r_L0_bed_room_2_1: room rule ran a3
- cam_r_L0_bed_room_2_1: room rule: wall ΔE 5.187 > 5.0 in r_L0_bed_room_2; a1 -> cycles
- cam_r_L0_bed_room_2_2: room rule ran a2
- cam_r_L0_bed_room_2_2: room rule ran a3
- cam_r_L0_bed_room_2_2: room rule: wall ΔE 5.187 > 5.0 in r_L0_bed_room_2; a1 -> cycles
- cam_r_L0_bed_room_2_3: room rule ran a2
- cam_r_L0_bed_room_2_3: room rule ran a3
- cam_r_L0_bed_room_2_3: room rule: wall ΔE 5.187 > 5.0 in r_L0_bed_room_2; a1 -> cycles
- cam_r_L0_bed_room_3: room rule ran a2
- cam_r_L0_bed_room_3: room rule ran a3
- cam_r_L0_bed_room_3: room rule: wall ΔE 5.251 > 5.0 in r_L0_bed_room; a1 -> cycles
- cam_r_L0_room_1: room rule ran a3
- cam_r_L0_room_1: room rule: wall ΔE 5.46 > 5.0 in r_L0_room; a2 -> cycles
- cam_r_L0_room_2: room rule ran a2
- cam_r_L0_room_2: room rule ran a3
- cam_r_L0_room_2: room rule: wall ΔE 5.46 > 5.0 in r_L0_room; a1 -> cycles
- cam_r_L0_room_3: room rule ran a2
- cam_r_L0_room_3: room rule ran a3
- cam_r_L0_room_3: room rule: wall ΔE 5.46 > 5.0 in r_L0_room; a1 -> cycles

## Prompts

- cam_r_L0_bath_toilet_1: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bath_toilet_2: Photorealistic interior photograph of a bathroom in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bed_room_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bed_room_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bed_room_2_1: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bed_room_2_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bed_room_2_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bed_room_3: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_dining_1: Photorealistic interior photograph of a dining room in Scandinavian style. White plaster walls, light oak wood floor, dining table, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_dining_2: Photorealistic interior photograph of a dining room in Scandinavian style. White plaster walls, light oak wood floor, dining table, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_dining_3: Photorealistic interior photograph of a dining room in Scandinavian style. White plaster walls, light oak wood floor, chair, dining table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_drawing_room_1: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, coffee table, floor lamp. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_drawing_room_2: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, coffee table, floor lamp. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_drawing_room_3: Photorealistic interior photograph of a living room in Scandinavian style. White plaster walls, light oak wood floor, sofa, floor lamp. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kitchen_1: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kitchen_2: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kitchen_3: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_room_1: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_room_2: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_room_3: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
