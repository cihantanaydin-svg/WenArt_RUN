# Polish report: synthetic-01 (smoke)

2 views, 8 attempts (8 polished now, 0 reused). Device NVIDIA RTX PRO 4500 Blackwell, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 10 s, prompt encoding 5.6 s, 3.77 s per forward, run 485 s.

## Settings

Every setting runs on every view and is gated; nothing stops early.

| k | role | strength / control / scale / size / mode | accepted | views | mean seconds |
|---|---|---|---|---|---|
| a1 | grid | 0.25 / depth / 0.8 / native / plain | 1 | 2 | 8.73 |
| a2 | grid | 0.375 / depth / 0.8 / native / plain | 0 | 2 | 12.4 |
| a3 | grid | 0.375 / canny / 0.8 / native / plain | 1 | 2 | 16.2 |
| a4 | grid | 0.375 / geometry / 0.8 / native / plain | 1 | 2 | 16 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L1_ebeveyn_yatak_odasi_2 | a1 | grid | 0.25 / depth / 0.8 / native / plain | 1 | 0.5 | 2 | 6.35 | reject | depth:global 0.0224 (needs <= 0.02); depth:f_L1_004 0.174 (needs <= 0.05); depth:f_L1_005 0.088 (needs <= 0.05); masks:f_L1_002 0.886 (needs >= 0.9); +1 more | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a2 | grid | 0.375 / depth / 0.8 / native / plain | 2 | 0.643 | 3 | 8.29 | reject | edges:global 0.948 (needs >= 0.95); depth:f_L1_005 0.0862 (needs <= 0.05); masks:f_L1_002 0.862 (needs >= 0.9); masks:f_L1_003 0.857 (needs >= 0.9) | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a3 | grid | 0.375 / canny / 0.8 / native / plain | 3 | 0.643 | 3 | 8.33 | reject | depth:global 0.0202 (needs <= 0.02); depth:f_L1_005 0.109 (needs <= 0.05); masks:f_L1_002 0.809 (needs >= 0.9); masks:f_L1_003 0.774 (needs >= 0.9) | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a4 | grid | 0.375 / geometry / 0.8 / native / plain | 4 | 0.643 | 3 | 8.33 | reject | depth:global 0.0208 (needs <= 0.02); depth:f_L1_004 0.0935 (needs <= 0.05); depth:f_L1_005 0.0839 (needs <= 0.05); masks:f_L1_002 0.866 (needs >= 0.9); +1 more | - |
| cam_r_L0_mutfak_2 | a1 | grid | 0.25 / depth / 0.8 / native / plain | 1 | 0.5 | 2 | 11.1 | accept | - | - |
| cam_r_L0_mutfak_2 | a2 | grid | 0.375 / depth / 0.8 / native / plain | 2 | 0.643 | 3 | 16.6 | reject | masks:f_L0_015 0.878 (needs >= 0.9); masks:f_L0_017 0.891 (needs >= 0.9) | - |
| cam_r_L0_mutfak_2 | a3 | grid | 0.375 / canny / 0.8 / native / plain | 3 | 0.643 | 3 | 24.1 | accept | - | - |
| cam_r_L0_mutfak_2 | a4 | grid | 0.375 / geometry / 0.8 / native / plain | 4 | 0.643 | 3 | 23.7 | accept | - | - |

## Prompts

- cam_r_L1_ebeveyn_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe, desk, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_2: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, dining table, fridge, stove, kitchen sink. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
