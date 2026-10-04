# Polish report: synthetic-06 (run)

17 views, 19 attempts (19 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Server Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 2.7 s, prompt encoding 1.9 s, 1.27 s per forward, run 124 s.

Final images: 17 polished, 0 Cycles. A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_1 | r_L0_bath | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.92 | 1 |
| cam_r_L0_bath_2 | r_L0_bath | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 1.84 | 0 |
| cam_r_L0_bed_room_1 | r_L0_bed_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 2 |
| cam_r_L0_bed_room_2 | r_L0_bed_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 2 |
| cam_r_L0_bed_room_3 | r_L0_bed_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L0_kitchen_1 | r_L0_kitchen | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 2 |
| cam_r_L0_kitchen_2 | r_L0_kitchen | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L0_kitchen_3 | r_L0_kitchen | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.77 | 0 |
| cam_r_L0_living_room_1 | r_L0_living_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 2 |
| cam_r_L0_living_room_2 | r_L0_living_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 2 |
| cam_r_L0_living_room_3 | r_L0_living_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L0_lobby_1 | r_L0_lobby | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L0_lobby_2 | r_L0_lobby | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L0_lobby_3 | r_L0_lobby | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L0_master_bed_room_1 | r_L0_master_bed_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L0_master_bed_room_2 | r_L0_master_bed_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 1 |
| cam_r_L0_master_bed_room_3 | r_L0_master_bed_room | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 2 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L0_bath | ok | - | 0.686 | - | cam_r_L0_bath_1, cam_r_L0_bath_2 |
| r_L0_bed_room | ok | - | 0.902 | - | cam_r_L0_bed_room_1, cam_r_L0_bed_room_2, cam_r_L0_bed_room_3 |
| r_L0_kitchen | ok | - | 2.79 | - | cam_r_L0_kitchen_1, cam_r_L0_kitchen_2, cam_r_L0_kitchen_3 |
| r_L0_living_room | ok | - | 1.29 | - | cam_r_L0_living_room_1, cam_r_L0_living_room_2, cam_r_L0_living_room_3 |
| r_L0_lobby | ok | - | 1.29 | - | cam_r_L0_lobby_1, cam_r_L0_lobby_2, cam_r_L0_lobby_3 |
| r_L0_master_bed_room | ok | - | 3.67 | - | cam_r_L0_master_bed_room_1, cam_r_L0_master_bed_room_2, cam_r_L0_master_bed_room_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.92 | accept | - | - |
| cam_r_L0_bath_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | depth:global 0.0759 (needs <= 0.05) | - |
| cam_r_L0_bath_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.82 | reject | depth:global 0.06 (needs <= 0.05) | - |
| cam_r_L0_bath_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.84 | accept | - | - |
| cam_r_L0_bed_room_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_bed_room_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_bed_room_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_kitchen_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_kitchen_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_kitchen_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L0_living_room_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_living_room_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_living_room_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_lobby_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_lobby_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_lobby_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_master_bed_room_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_master_bed_room_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_master_bed_room_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |

## Prompts

- cam_r_L0_bath_1: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor, toilet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bath_2: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bed_room_1: Photorealistic interior photograph of a bedroom in modern style. White plaster walls, dark walnut wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bed_room_2: Photorealistic interior photograph of a bedroom in modern style. White plaster walls, dark walnut wood floor, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_bed_room_3: Photorealistic interior photograph of a bedroom in modern style. White plaster walls, dark walnut wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kitchen_1: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor, dining table, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kitchen_2: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor, dining table, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kitchen_3: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor, dining table, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_living_room_1: Photorealistic interior photograph of a living room in modern style. White plaster walls, dark walnut wood floor, sofa. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_living_room_2: Photorealistic interior photograph of a living room in modern style. White plaster walls, dark walnut wood floor, sofa. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_living_room_3: Photorealistic interior photograph of a living room in modern style. White plaster walls, dark walnut wood floor, sofa. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_lobby_1: Photorealistic interior photograph of a hallway in modern style. White plaster walls, dark walnut wood floor, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_lobby_2: Photorealistic interior photograph of a hallway in modern style. White plaster walls, dark walnut wood floor, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_lobby_3: Photorealistic interior photograph of a hallway in modern style. White plaster walls, dark walnut wood floor, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_master_bed_room_1: Photorealistic interior photograph of a bedroom in modern style. White plaster walls, dark walnut wood floor, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_master_bed_room_2: Photorealistic interior photograph of a bedroom in modern style. White plaster walls, dark walnut wood floor, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_master_bed_room_3: Photorealistic interior photograph of a bedroom in modern style. White plaster walls, dark walnut wood floor, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
