# Polish report: synthetic-01 (sweep)

4 views, 44 attempts (44 polished now, 0 reused). Device NVIDIA GeForce RTX 4090, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 21.5 GiB, model load 5.2 s, prompt encoding 3.9 s, 2.01 s per forward, run 330 s.

## Settings

Every setting runs on every view and is gated; nothing stops early.

| k | role | strength / control / scale / size / mode | accepted | views | mean seconds |
|---|---|---|---|---|---|
| a1 | grid | 0.125 / depth / 0.8 / native / plain | 0 | 4 | 3 |
| a2 | grid | 0.25 / depth / 0.8 / native / plain | 0 | 4 | 4.84 |
| a3 | grid | 0.375 / depth / 0.8 / native / plain | 0 | 4 | 6.71 |
| a4 | grid | 0.5 / depth / 0.8 / native / plain | 0 | 4 | 8.6 |
| a5 | grid | 0.25 / canny / 0.8 / native / plain | 1 | 4 | 4.84 |
| a6 | grid | 0.375 / canny / 0.8 / native / plain | 0 | 4 | 6.73 |
| a7 | grid | 0.25 / geometry / 0.8 / native / plain | 1 | 4 | 4.85 |
| a8 | grid | 0.375 / geometry / 0.8 / native / plain | 2 | 4 | 6.73 |
| a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 2 | 4 | 3.71 |
| a10 | grid | 0.375 / depth / 0.8 / native / anchor | 3 | 4 | 6.99 |
| a11 | presumed_bad | 0.75 / none / - / native / plain | 0 | 4 | 7.35 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L1_ebeveyn_yatak_odasi_2 | a1 | grid | 0.125 / depth / 0.8 / native / plain | 1 | 0.3 | 1 | 3.14 | reject | depth:f_L1_004 0.138 (needs <= 0.05); depth:f_L1_005 0.0709 (needs <= 0.05); masks:f_L1_002 0.89 (needs >= 0.9); masks:f_L1_003 0.899 (needs >= 0.9) | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a2 | grid | 0.25 / depth / 0.8 / native / plain | 2 | 0.5 | 2 | 4.82 | reject | depth:f_L1_005 0.0878 (needs <= 0.05); masks:f_L1_002 0.834 (needs >= 0.9); masks:f_L1_003 0.881 (needs >= 0.9) | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a3 | grid | 0.375 / depth / 0.8 / native / plain | 3 | 0.643 | 3 | 6.68 | reject | depth:global 0.0202 (needs <= 0.02); depth:f_L1_005 0.0974 (needs <= 0.05); masks:f_L1_002 0.849 (needs >= 0.9); masks:f_L1_003 0.897 (needs >= 0.9) | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a4 | grid | 0.5 / depth / 0.8 / native / plain | 4 | 0.75 | 4 | 8.56 | reject | edges:dec_L1_004 0.847 (needs >= 0.85); depth:global 0.0258 (needs <= 0.02); depth:f_L1_004 0.146 (needs <= 0.05); depth:f_L1_005 0.0868 (needs <= 0.05); +2 more | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a5 | grid | 0.25 / canny / 0.8 / native / plain | 5 | 0.5 | 2 | 4.83 | reject | depth:f_L1_004 0.0567 (needs <= 0.05); depth:f_L1_005 0.0792 (needs <= 0.05); masks:f_L1_002 0.898 (needs >= 0.9) | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a6 | grid | 0.375 / canny / 0.8 / native / plain | 6 | 0.643 | 3 | 6.72 | reject | depth:global 0.0274 (needs <= 0.02); depth:f_L1_004 0.187 (needs <= 0.05); depth:f_L1_005 0.101 (needs <= 0.05); masks:f_L1_002 0.714 (needs >= 0.9); +1 more | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a7 | grid | 0.25 / geometry / 0.8 / native / plain | 7 | 0.5 | 2 | 4.84 | reject | depth:f_L1_004 0.0697 (needs <= 0.05); depth:f_L1_005 0.0693 (needs <= 0.05); masks:f_L1_002 0.873 (needs >= 0.9); masks:f_L1_003 0.878 (needs >= 0.9) | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a8 | grid | 0.375 / geometry / 0.8 / native / plain | 8 | 0.643 | 3 | 6.71 | reject | depth:f_L1_004 0.102 (needs <= 0.05); depth:f_L1_005 0.0665 (needs <= 0.05); masks:f_L1_002 0.871 (needs >= 0.9); masks:f_L1_003 0.885 (needs >= 0.9) | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 9 | 0.643 | 3 | 3.69 | reject | depth:global 0.0345 (needs <= 0.02); depth:f_L1_004 0.181 (needs <= 0.05); depth:f_L1_005 0.115 (needs <= 0.05); masks:f_L1_002 0.879 (needs >= 0.9); +1 more | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a10 | grid | 0.375 / depth / 0.8 / native / anchor | 10 | 0.643 | 3 | 6.98 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a11 | presumed_bad | 0.75 / none / - / native / plain | 11 | 0.9 | 6 | 7.34 | reject | edges:global 0.33 (needs >= 0.95); edges:win_L1_003 0.387 (needs >= 0.85); edges:f_L1_001 0.396 (needs >= 0.85); edges:f_L1_002 0.214 (needs >= 0.85); +14 more | - |
| cam_r_L0_mutfak_2 | a1 | grid | 0.125 / depth / 0.8 / native / plain | 1 | 0.3 | 1 | 2.94 | reject | depth:global 0.0229 (needs <= 0.02) | - |
| cam_r_L0_mutfak_2 | a2 | grid | 0.25 / depth / 0.8 / native / plain | 2 | 0.5 | 2 | 4.85 | reject | masks:f_L0_015 0.889 (needs >= 0.9) | - |
| cam_r_L0_mutfak_2 | a3 | grid | 0.375 / depth / 0.8 / native / plain | 3 | 0.643 | 3 | 6.73 | reject | masks:f_L0_017 0.886 (needs >= 0.9) | - |
| cam_r_L0_mutfak_2 | a4 | grid | 0.5 / depth / 0.8 / native / plain | 4 | 0.75 | 4 | 8.63 | reject | edges:global 0.908 (needs >= 0.95); edges:f_L0_019 0.816 (needs >= 0.85); depth:global 0.0296 (needs <= 0.02); masks:f_L0_017 0.849 (needs >= 0.9) | - |
| cam_r_L0_mutfak_2 | a5 | grid | 0.25 / canny / 0.8 / native / plain | 5 | 0.5 | 2 | 4.86 | accept | - | - |
| cam_r_L0_mutfak_2 | a6 | grid | 0.375 / canny / 0.8 / native / plain | 6 | 0.643 | 3 | 6.73 | reject | masks:f_L0_017 0.88 (needs >= 0.9) | - |
| cam_r_L0_mutfak_2 | a7 | grid | 0.25 / geometry / 0.8 / native / plain | 7 | 0.5 | 2 | 4.86 | accept | - | - |
| cam_r_L0_mutfak_2 | a8 | grid | 0.375 / geometry / 0.8 / native / plain | 8 | 0.643 | 3 | 6.75 | accept | - | - |
| cam_r_L0_mutfak_2 | a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 9 | 0.643 | 3 | 3.72 | accept | - | - |
| cam_r_L0_mutfak_2 | a10 | grid | 0.375 / depth / 0.8 / native / anchor | 10 | 0.643 | 3 | 7.01 | accept | - | - |
| cam_r_L0_mutfak_2 | a11 | presumed_bad | 0.75 / none / - / native / plain | 11 | 0.9 | 6 | 7.36 | reject | edges:global 0.38 (needs >= 0.95); edges:f_L0_015 0.488 (needs >= 0.85); edges:f_L0_016 0 (needs >= 0.85); edges:f_L0_017 0.166 (needs >= 0.85); +8 more | - |
| cam_r_L1_hol_1 | a1 | grid | 0.125 / depth / 0.8 / native / plain | 1 | 0.3 | 1 | 2.95 | reject | depth:global 0.0269 (needs <= 0.02); depth:d_L1_004 0.0616 (needs <= 0.05) | - |
| cam_r_L1_hol_1 | a2 | grid | 0.25 / depth / 0.8 / native / plain | 2 | 0.5 | 2 | 4.84 | reject | depth:global 0.0205 (needs <= 0.02) | - |
| cam_r_L1_hol_1 | a3 | grid | 0.375 / depth / 0.8 / native / plain | 3 | 0.643 | 3 | 6.73 | reject | depth:global 0.0471 (needs <= 0.02); depth:d_L1_004 0.104 (needs <= 0.05); masks:d_L1_001 0.882 (needs >= 0.9) | - |
| cam_r_L1_hol_1 | a4 | grid | 0.5 / depth / 0.8 / native / plain | 4 | 0.75 | 4 | 8.6 | reject | edges:global 0.939 (needs >= 0.95); depth:global 0.0434 (needs <= 0.02); depth:d_L1_004 0.0919 (needs <= 0.05); masks:d_L1_001 0.893 (needs >= 0.9) | - |
| cam_r_L1_hol_1 | a5 | grid | 0.25 / canny / 0.8 / native / plain | 5 | 0.5 | 2 | 4.85 | reject | depth:global 0.0305 (needs <= 0.02); depth:d_L1_004 0.066 (needs <= 0.05) | - |
| cam_r_L1_hol_1 | a6 | grid | 0.375 / canny / 0.8 / native / plain | 6 | 0.643 | 3 | 6.73 | reject | depth:global 0.04 (needs <= 0.02); depth:d_L1_004 0.0903 (needs <= 0.05); masks:d_L1_001 0.876 (needs >= 0.9) | - |
| cam_r_L1_hol_1 | a7 | grid | 0.25 / geometry / 0.8 / native / plain | 7 | 0.5 | 2 | 4.85 | reject | depth:global 0.0274 (needs <= 0.02); depth:d_L1_004 0.0575 (needs <= 0.05) | - |
| cam_r_L1_hol_1 | a8 | grid | 0.375 / geometry / 0.8 / native / plain | 8 | 0.643 | 3 | 6.73 | accept | - | - |
| cam_r_L1_hol_1 | a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 9 | 0.643 | 3 | 3.71 | reject | depth:global 0.0376 (needs <= 0.02); depth:d_L1_004 0.0846 (needs <= 0.05); masks:d_L1_001 0.889 (needs >= 0.9); masks:f_L1_007 0.88 (needs >= 0.9) | - |
| cam_r_L1_hol_1 | a10 | grid | 0.375 / depth / 0.8 / native / anchor | 10 | 0.643 | 3 | 6.97 | accept | - | - |
| cam_r_L1_hol_1 | a11 | presumed_bad | 0.75 / none / - / native / plain | 11 | 0.9 | 6 | 7.35 | reject | edges:global 0.312 (needs >= 0.95); edges:d_L1_001 0.0296 (needs >= 0.85); edges:d_L1_003 0.691 (needs >= 0.85); edges:f_L1_007 0.443 (needs >= 0.85); +15 more | - |
| cam_r_L0_hol_2 | a1 | grid | 0.125 / depth / 0.8 / native / plain | 1 | 0.3 | 1 | 2.96 | reject | depth:global 0.0255 (needs <= 0.02); depth:d_L0_005 0.11 (needs <= 0.05) | - |
| cam_r_L0_hol_2 | a2 | grid | 0.25 / depth / 0.8 / native / plain | 2 | 0.5 | 2 | 4.84 | reject | depth:global 0.0428 (needs <= 0.02); depth:d_L0_005 0.203 (needs <= 0.05) | - |
| cam_r_L0_hol_2 | a3 | grid | 0.375 / depth / 0.8 / native / plain | 3 | 0.643 | 3 | 6.72 | reject | depth:global 0.0218 (needs <= 0.02) | - |
| cam_r_L0_hol_2 | a4 | grid | 0.5 / depth / 0.8 / native / plain | 4 | 0.75 | 4 | 8.6 | reject | edges:global 0.92 (needs >= 0.95); edges:f_L0_014 0.84 (needs >= 0.85); depth:global 0.0326 (needs <= 0.02); depth:d_L0_005 0.0771 (needs <= 0.05); +1 more | - |
| cam_r_L0_hol_2 | a5 | grid | 0.25 / canny / 0.8 / native / plain | 5 | 0.5 | 2 | 4.83 | reject | depth:global 0.028 (needs <= 0.02); depth:d_L0_005 0.117 (needs <= 0.05) | - |
| cam_r_L0_hol_2 | a6 | grid | 0.375 / canny / 0.8 / native / plain | 6 | 0.643 | 3 | 6.74 | reject | depth:global 0.0346 (needs <= 0.02); depth:d_L0_005 0.119 (needs <= 0.05) | - |
| cam_r_L0_hol_2 | a7 | grid | 0.25 / geometry / 0.8 / native / plain | 7 | 0.5 | 2 | 4.84 | reject | depth:global 0.0287 (needs <= 0.02); depth:d_L0_005 0.139 (needs <= 0.05) | - |
| cam_r_L0_hol_2 | a8 | grid | 0.375 / geometry / 0.8 / native / plain | 8 | 0.643 | 3 | 6.73 | reject | depth:global 0.0249 (needs <= 0.02); depth:d_L0_002 0.0672 (needs <= 0.05) | - |
| cam_r_L0_hol_2 | a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 9 | 0.643 | 3 | 3.71 | accept | - | - |
| cam_r_L0_hol_2 | a10 | grid | 0.375 / depth / 0.8 / native / anchor | 10 | 0.643 | 3 | 6.99 | reject | depth:global 0.0268 (needs <= 0.02) | - |
| cam_r_L0_hol_2 | a11 | presumed_bad | 0.75 / none / - / native / plain | 11 | 0.9 | 6 | 7.36 | reject | edges:global 0.311 (needs >= 0.95); edges:d_L0_002 0 (needs >= 0.85); edges:d_L0_004 0.172 (needs >= 0.85); edges:win_L0_003 0 (needs >= 0.85); +10 more | - |

## Prompts

- cam_r_L1_ebeveyn_yatak_odasi_2: Photorealistic interior photograph of a bedroom in Scandinavian style. White plaster walls, light oak wood floor, double bed, wardrobe, desk, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_2: Photorealistic interior photograph of a kitchen in Scandinavian style. Light ceramic tile walls, light ceramic tile floor, kitchen counter, dining table, fridge, stove, kitchen sink. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_1: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, chair, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_2: Photorealistic interior photograph of a hallway in Scandinavian style. White plaster walls, light oak wood floor, dresser. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
