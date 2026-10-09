# Polish report: synthetic-07 (run)

3 views, 3 attempts (3 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Server Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 2.8 s, prompt encoding 1.5 s, 1.37 s per forward, run 41.3 s.

Final images: 3 polished, 0 Cycles. A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L-1b_salon_acik_mutfak_1 | r_L-1b_salon_acik_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 4.61 | 3 |
| cam_r_L-1b_salon_acik_mutfak_2 | r_L-1b_salon_acik_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.94 | 2 |
| cam_r_L-1b_salon_acik_mutfak_3 | r_L-1b_salon_acik_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.96 | 2 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L-1b_salon_acik_mutfak | ok | - | 2.25 | - | cam_r_L-1b_salon_acik_mutfak_1, cam_r_L-1b_salon_acik_mutfak_2, cam_r_L-1b_salon_acik_mutfak_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1b_salon_acik_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.61 | accept | - | - |
| cam_r_L-1b_salon_acik_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.94 | accept | - | - |
| cam_r_L-1b_salon_acik_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.96 | accept | - | - |

## Prompts

- cam_r_L-1b_salon_acik_mutfak_1: Photorealistic interior photograph of a living room in modern minimalist style. White plaster walls, light oak wood floor, sofa, coffee table, armchair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_salon_acik_mutfak_2: Photorealistic interior photograph of a living room in modern minimalist style. White plaster walls, light oak wood floor, sofa, armchair, TV unit, coffee table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1b_salon_acik_mutfak_3: Photorealistic interior photograph of a living room in modern minimalist style. White plaster walls, light oak wood floor, sofa, armchair, coffee table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.

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
