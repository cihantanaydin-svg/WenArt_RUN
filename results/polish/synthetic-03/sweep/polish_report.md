# Polish report: synthetic-03 (sweep)

4 views, 44 attempts (44 polished now, 0 reused). Device NVIDIA GeForce RTX 4090, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 21.5 GiB, model load 3.5 s, prompt encoding 2.2 s, 2.06 s per forward, run 453 s.

## Settings

Every setting runs on every view and is gated; nothing stops early.

| k | role | strength / control / scale / size / mode | accepted | views | mean seconds |
|---|---|---|---|---|---|
| a1 | grid | 0.125 / depth / 0.8 / native / plain | 3 | 4 | 3.3 |
| a2 | grid | 0.25 / depth / 0.8 / native / plain | 2 | 4 | 5.41 |
| a3 | grid | 0.375 / depth / 0.8 / native / plain | 2 | 4 | 7.27 |
| a4 | grid | 0.5 / depth / 0.8 / native / plain | 0 | 4 | 9.2 |
| a5 | grid | 0.25 / canny / 0.8 / native / plain | 2 | 4 | 5.06 |
| a6 | grid | 0.375 / canny / 0.8 / native / plain | 3 | 4 | 7.46 |
| a7 | grid | 0.25 / geometry / 0.8 / native / plain | 4 | 4 | 5.08 |
| a8 | grid | 0.375 / geometry / 0.8 / native / plain | 2 | 4 | 6.91 |
| a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 2 | 4 | 3.7 |
| a10 | grid | 0.375 / depth / 0.8 / native / anchor | 4 | 4 | 7.41 |
| a11 | presumed_bad | 0.75 / none / - / native / plain | 0 | 4 | 7.34 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_hol_1 | a1 | grid | 0.125 / depth / 0.8 / native / plain | 1 | 0.3 | 1 | 3.6 | accept | - | - |
| cam_r_L-1_hol_1 | a2 | grid | 0.25 / depth / 0.8 / native / plain | 2 | 0.5 | 2 | 6.15 | accept | - | - |
| cam_r_L-1_hol_1 | a3 | grid | 0.375 / depth / 0.8 / native / plain | 3 | 0.643 | 3 | 8.13 | accept | - | - |
| cam_r_L-1_hol_1 | a4 | grid | 0.5 / depth / 0.8 / native / plain | 4 | 0.75 | 4 | 10.2 | reject | depth:d_L-1_004 0.0781 (needs <= 0.05); masks:d_L-1_002 0.862 (needs >= 0.9) | - |
| cam_r_L-1_hol_1 | a5 | grid | 0.25 / canny / 0.8 / native / plain | 5 | 0.5 | 2 | 5.21 | accept | - | - |
| cam_r_L-1_hol_1 | a6 | grid | 0.375 / canny / 0.8 / native / plain | 6 | 0.643 | 3 | 8.97 | accept | - | - |
| cam_r_L-1_hol_1 | a7 | grid | 0.25 / geometry / 0.8 / native / plain | 7 | 0.5 | 2 | 5.18 | accept | - | - |
| cam_r_L-1_hol_1 | a8 | grid | 0.375 / geometry / 0.8 / native / plain | 8 | 0.643 | 3 | 6.78 | accept | - | - |
| cam_r_L-1_hol_1 | a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 9 | 0.643 | 3 | 3.7 | accept | - | - |
| cam_r_L-1_hol_1 | a10 | grid | 0.375 / depth / 0.8 / native / anchor | 10 | 0.643 | 3 | 7.22 | accept | - | - |
| cam_r_L-1_hol_1 | a11 | presumed_bad | 0.75 / none / - / native / plain | 11 | 0.9 | 6 | 7.34 | reject | edges:global 0.353 (needs >= 0.95); edges:d_L-1_001 0.4 (needs >= 0.85); edges:d_L-1_002 0.187 (needs >= 0.85); edges:d_L-1_003 0.701 (needs >= 0.85); +11 more | - |
| cam_r_L0_hol_1 | a1 | grid | 0.125 / depth / 0.8 / native / plain | 1 | 0.3 | 1 | 3.03 | accept | - | - |
| cam_r_L0_hol_1 | a2 | grid | 0.25 / depth / 0.8 / native / plain | 2 | 0.5 | 2 | 5.15 | accept | - | - |
| cam_r_L0_hol_1 | a3 | grid | 0.375 / depth / 0.8 / native / plain | 3 | 0.643 | 3 | 6.92 | accept | - | - |
| cam_r_L0_hol_1 | a4 | grid | 0.5 / depth / 0.8 / native / plain | 4 | 0.75 | 4 | 8.63 | reject | edges:global 0.909 (needs >= 0.95); edges:d_L0_006 0.682 (needs >= 0.85); depth:d_L0_006 0.0657 (needs <= 0.05) | - |
| cam_r_L0_hol_1 | a5 | grid | 0.25 / canny / 0.8 / native / plain | 5 | 0.5 | 2 | 4.87 | accept | - | - |
| cam_r_L0_hol_1 | a6 | grid | 0.375 / canny / 0.8 / native / plain | 6 | 0.643 | 3 | 7.01 | accept | - | - |
| cam_r_L0_hol_1 | a7 | grid | 0.25 / geometry / 0.8 / native / plain | 7 | 0.5 | 2 | 5.06 | accept | - | - |
| cam_r_L0_hol_1 | a8 | grid | 0.375 / geometry / 0.8 / native / plain | 8 | 0.643 | 3 | 6.93 | accept | - | - |
| cam_r_L0_hol_1 | a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 9 | 0.643 | 3 | 3.7 | accept | - | - |
| cam_r_L0_hol_1 | a10 | grid | 0.375 / depth / 0.8 / native / anchor | 10 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_hol_1 | a11 | presumed_bad | 0.75 / none / - / native / plain | 11 | 0.9 | 6 | 7.34 | reject | edges:global 0.388 (needs >= 0.95); edges:d_L0_004 0.525 (needs >= 0.85); edges:d_L0_005 0.692 (needs >= 0.85); edges:d_L0_006 0.112 (needs >= 0.85); +9 more | - |
| cam_r_L-1_yatak_odasi_3 | a1 | grid | 0.125 / depth / 0.8 / native / plain | 1 | 0.3 | 1 | 2.95 | reject | masks:f_L-1_003 0.859 (needs >= 0.9) | - |
| cam_r_L-1_yatak_odasi_3 | a2 | grid | 0.25 / depth / 0.8 / native / plain | 2 | 0.5 | 2 | 5.01 | reject | depth:f_L-1_006 0.0689 (needs <= 0.05); masks:f_L-1_003 0.822 (needs >= 0.9) | - |
| cam_r_L-1_yatak_odasi_3 | a3 | grid | 0.375 / depth / 0.8 / native / plain | 3 | 0.643 | 3 | 7.33 | reject | depth:f_L-1_006 0.0712 (needs <= 0.05) | - |
| cam_r_L-1_yatak_odasi_3 | a4 | grid | 0.5 / depth / 0.8 / native / plain | 4 | 0.75 | 4 | 8.98 | reject | edges:global 0.938 (needs >= 0.95); depth:f_L-1_006 0.158 (needs <= 0.05); masks:f_L-1_003 0.827 (needs >= 0.9); masks:f_L-1_006 0.835 (needs >= 0.9) | - |
| cam_r_L-1_yatak_odasi_3 | a5 | grid | 0.25 / canny / 0.8 / native / plain | 5 | 0.5 | 2 | 4.82 | reject | depth:f_L-1_006 0.0586 (needs <= 0.05); masks:f_L-1_003 0.88 (needs >= 0.9) | - |
| cam_r_L-1_yatak_odasi_3 | a6 | grid | 0.375 / canny / 0.8 / native / plain | 6 | 0.643 | 3 | 7.17 | accept | - | - |
| cam_r_L-1_yatak_odasi_3 | a7 | grid | 0.25 / geometry / 0.8 / native / plain | 7 | 0.5 | 2 | 4.82 | accept | - | - |
| cam_r_L-1_yatak_odasi_3 | a8 | grid | 0.375 / geometry / 0.8 / native / plain | 8 | 0.643 | 3 | 6.84 | reject | masks:f_L-1_003 0.842 (needs >= 0.9) | - |
| cam_r_L-1_yatak_odasi_3 | a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 9 | 0.643 | 3 | 3.7 | reject | depth:f_L-1_003 0.0594 (needs <= 0.05); depth:f_L-1_006 0.119 (needs <= 0.05); masks:f_L-1_003 0.801 (needs >= 0.9) | - |
| cam_r_L-1_yatak_odasi_3 | a10 | grid | 0.375 / depth / 0.8 / native / anchor | 10 | 0.643 | 3 | 7.19 | accept | - | - |
| cam_r_L-1_yatak_odasi_3 | a11 | presumed_bad | 0.75 / none / - / native / plain | 11 | 0.9 | 6 | 7.34 | reject | edges:global 0.251 (needs >= 0.95); edges:d_L-1_003 0.387 (needs >= 0.85); edges:d_L-1_005 0.578 (needs >= 0.85); edges:f_L-1_003 0.095 (needs >= 0.85); +10 more | - |
| cam_r_L0_salon_3 | a1 | grid | 0.125 / depth / 0.8 / native / plain | 1 | 0.3 | 1 | 3.62 | accept | - | - |
| cam_r_L0_salon_3 | a2 | grid | 0.25 / depth / 0.8 / native / plain | 2 | 0.5 | 2 | 5.31 | reject | depth:f_L0_004 0.0528 (needs <= 0.05) | - |
| cam_r_L0_salon_3 | a3 | grid | 0.375 / depth / 0.8 / native / plain | 3 | 0.643 | 3 | 6.71 | reject | edges:global 0.948 (needs >= 0.95); edges:f_L0_002 0.819 (needs >= 0.85); depth:f_L0_004 0.0914 (needs <= 0.05) | - |
| cam_r_L0_salon_3 | a4 | grid | 0.5 / depth / 0.8 / native / plain | 4 | 0.75 | 4 | 9.02 | reject | edges:global 0.902 (needs >= 0.95); edges:f_L0_001 0.581 (needs >= 0.85); edges:f_L0_002 0.768 (needs >= 0.85); depth:f_L0_004 0.0859 (needs <= 0.05) | - |
| cam_r_L0_salon_3 | a5 | grid | 0.25 / canny / 0.8 / native / plain | 5 | 0.5 | 2 | 5.35 | reject | depth:f_L0_004 0.0678 (needs <= 0.05) | - |
| cam_r_L0_salon_3 | a6 | grid | 0.375 / canny / 0.8 / native / plain | 6 | 0.643 | 3 | 6.71 | reject | depth:f_L0_004 0.0924 (needs <= 0.05) | - |
| cam_r_L0_salon_3 | a7 | grid | 0.25 / geometry / 0.8 / native / plain | 7 | 0.5 | 2 | 5.26 | accept | - | - |
| cam_r_L0_salon_3 | a8 | grid | 0.375 / geometry / 0.8 / native / plain | 8 | 0.643 | 3 | 7.09 | reject | depth:f_L0_004 0.0704 (needs <= 0.05) | - |
| cam_r_L0_salon_3 | a9 | grid | 0.375 / depth / 0.8 / 1536x864 / plain | 9 | 0.643 | 3 | 3.7 | reject | edges:global 0.936 (needs >= 0.95); depth:f_L0_004 0.0941 (needs <= 0.05) | - |
| cam_r_L0_salon_3 | a10 | grid | 0.375 / depth / 0.8 / native / anchor | 10 | 0.643 | 3 | 6.97 | accept | - | - |
| cam_r_L0_salon_3 | a11 | presumed_bad | 0.75 / none / - / native / plain | 11 | 0.9 | 6 | 7.36 | reject | edges:global 0.393 (needs >= 0.95); edges:f_L0_001 0.293 (needs >= 0.85); edges:f_L0_002 0.126 (needs >= 0.85); edges:f_L0_003 0.261 (needs >= 0.85); +12 more | - |

## Prompts

- cam_r_L-1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_3: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, sofa, armchair, coffee table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
