# Polish report: synthetic-03 (run)

44 views, 77 attempts (77 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Server Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 7.6 s, prompt encoding 3.6 s, 1.34 s per forward, run 1.23e+03 s.

Final images: 28 polished, 16 Cycles (gate 1, room 15). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 4.02 | 0 |
| cam_r_L-1_banyo_2 | r_L-1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.8 | 0 |
| cam_r_L-1_hol_1 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L-1_hol_2 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L-1_hol_3 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L-1_kiler_1 | r_L-1_kiler | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.88 | 0 |
| cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.89 | 0 |
| cam_r_L-1_wc_1 | r_L-1_wc | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.89 | 0 |
| cam_r_L-1_wc_2 | r_L-1_wc | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.89 | 0 |
| cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 3.19 | 0 |
| cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L0_antre_1 | r_L0_antre | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 4.01 | 0 |
| cam_r_L0_antre_2 | r_L0_antre | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.86 | 0 |
| cam_r_L0_hol_1 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L0_hol_2 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L0_hol_3 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L0_kiler_1 | r_L0_kiler | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L0_mutfak_1 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.8 | 1 |
| cam_r_L0_mutfak_2 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.83 | 1 |
| cam_r_L0_mutfak_3 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.82 | 1 |
| cam_r_L0_salon_1 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L0_salon_2 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.83 | 1 |
| cam_r_L0_salon_3 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L0_wc_1 | r_L0_wc | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 0 |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 1 |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 1 |
| cam_r_L1_balkon_1 | r_L1_balkon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L1_banyo_1 | r_L1_banyo | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.0684 (needs <= 0.05) | 1.83 | 0 |
| cam_r_L1_banyo_2 | r_L1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.86 | 0 |
| cam_r_L1_banyo_3 | r_L1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.82 | 1 |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 2 |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 1 |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 0 |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L1_hol_1 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L1_hol_2 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L1_hol_3 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.82 | 0 |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.79 | 0 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L-1_banyo | ok | - | 0.194 | - | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_hol | downgraded | cycles | 9.93 | - | cam_r_L-1_hol_1, cam_r_L-1_hol_2, cam_r_L-1_hol_3 |
| r_L-1_kiler | ok | - | - | - | cam_r_L-1_kiler_1 |
| r_L-1_kiler_2 | ok | - | - | - | cam_r_L-1_kiler_2_1 |
| r_L-1_wc | ok | - | 0.472 | - | cam_r_L-1_wc_1, cam_r_L-1_wc_2 |
| r_L-1_yatak_odasi | ok | - | 2.11 | - | cam_r_L-1_yatak_odasi_1, cam_r_L-1_yatak_odasi_2, cam_r_L-1_yatak_odasi_3 |
| r_L0_antre | ok | - | 0.887 | - | cam_r_L0_antre_1, cam_r_L0_antre_2 |
| r_L0_hol | downgraded | cycles | 15.4 | - | cam_r_L0_hol_1, cam_r_L0_hol_2, cam_r_L0_hol_3 |
| r_L0_kiler | ok | - | - | - | cam_r_L0_kiler_1 |
| r_L0_mutfak | ok | - | 4.54 | - | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | ok | - | 2.88 | - | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_wc | ok | - | - | - | cam_r_L0_wc_1 |
| r_L0_yatak_odasi | downgraded | cycles | 6.65 | - | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_balkon | ok | - | - | - | cam_r_L1_balkon_1 |
| r_L1_banyo | ok | - | 1.6 | - | cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | downgraded | cycles | 6.97 | - | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | ok | - | 1.39 | - | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | downgraded | cycles | 6.83 | - | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | ok | - | 4.51 | - | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.02 | accept | - | - |
| cam_r_L-1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L-1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | reject | neutral:struct:ceiling 2.3 (needs <= 2) | - |
| cam_r_L-1_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.97 | accept | - | - |
| cam_r_L-1_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L-1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L-1_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L-1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L-1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | reject | neutral:struct:ceiling 2.53 (needs <= 2) | - |
| cam_r_L-1_hol_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.09 | accept | - | - |
| cam_r_L-1_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L-1_kiler_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.88 | accept | - | - |
| cam_r_L-1_kiler_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.89 | accept | - | - |
| cam_r_L-1_wc_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.89 | accept | - | - |
| cam_r_L-1_wc_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.89 | accept | - | - |
| cam_r_L-1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L-1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.88 | reject | masks:f_L-1_003 0.399 (needs >= 0.62) | - |
| cam_r_L-1_yatak_odasi_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.19 | accept | - | - |
| cam_r_L-1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L0_antre_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.01 | accept | - | - |
| cam_r_L0_antre_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.86 | accept | - | - |
| cam_r_L0_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | reject | neutral:struct:ceiling 2.19 (needs <= 2) | - |
| cam_r_L0_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L0_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L0_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L0_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | neutral:struct:ceiling 2.39 (needs <= 2) | - |
| cam_r_L0_hol_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | reject | neutral:struct:ceiling 2.07 (needs <= 2) | - |
| cam_r_L0_hol_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L0_kiler_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L0_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.83 | accept | - | - |
| cam_r_L0_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.82 | accept | - | - |
| cam_r_L0_salon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_salon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.83 | accept | - | - |
| cam_r_L0_salon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_wc_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | edges:f_L0_018 0.843 (needs >= 0.87) | - |
| cam_r_L0_yatak_odasi_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L1_balkon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | edges:d_L1_004 0.864 (needs >= 0.87); depth:global 0.0803 (needs <= 0.05) | - |
| cam_r_L1_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.81 | reject | depth:global 0.0577 (needs <= 0.05) | - |
| cam_r_L1_banyo_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.83 | reject | depth:global 0.0684 (needs <= 0.05) | - |
| cam_r_L1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.86 | accept | - | - |
| cam_r_L1_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | edges:f_L1_019 0.852 (needs >= 0.87) | - |
| cam_r_L1_banyo_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.82 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.82 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | reject | neutral:struct:ceiling 2.36 (needs <= 2) | - |
| cam_r_L1_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.83 | accept | - | - |
| cam_r_L1_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.83 | accept | - | - |
| cam_r_L1_hol_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.8 | accept | - | - |
| cam_r_L1_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.82 | accept | - | - |
| cam_r_L1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.78 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.79 | accept | - | - |

## Notes

- cam_r_L-1_hol_1: room rule ran a3
- cam_r_L-1_hol_1: room rule: wall ΔE 9.931 > 5.0 in r_L-1_hol; a2 -> cycles
- cam_r_L-1_hol_2: room rule ran a2
- cam_r_L-1_hol_2: room rule ran a3
- cam_r_L-1_hol_2: room rule: wall ΔE 9.931 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L-1_hol_3: room rule ran a3
- cam_r_L-1_hol_3: room rule: wall ΔE 9.931 > 5.0 in r_L-1_hol; a2 -> cycles
- cam_r_L0_hol_1: room rule ran a3
- cam_r_L0_hol_1: room rule: wall ΔE 15.351 > 5.0 in r_L0_hol; a2 -> cycles
- cam_r_L0_hol_2: room rule ran a3
- cam_r_L0_hol_2: room rule: wall ΔE 15.351 > 5.0 in r_L0_hol; a1 -> cycles
- cam_r_L0_hol_3: room rule: wall ΔE 15.351 > 5.0 in r_L0_hol; a3 -> cycles
- cam_r_L0_yatak_odasi_1: room rule ran a2
- cam_r_L0_yatak_odasi_1: room rule ran a3
- cam_r_L0_yatak_odasi_1: room rule: wall ΔE 6.654 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L0_yatak_odasi_2: room rule ran a2
- cam_r_L0_yatak_odasi_2: room rule ran a3
- cam_r_L0_yatak_odasi_2: room rule: wall ΔE 6.654 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L0_yatak_odasi_3: room rule ran a3
- cam_r_L0_yatak_odasi_3: room rule: wall ΔE 6.654 > 5.0 in r_L0_yatak_odasi; a2 -> cycles
- cam_r_L1_cocuk_odasi_1: room rule ran a2
- cam_r_L1_cocuk_odasi_1: room rule ran a3
- cam_r_L1_cocuk_odasi_1: room rule: wall ΔE 6.975 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_cocuk_odasi_2: room rule ran a2
- cam_r_L1_cocuk_odasi_2: room rule ran a3
- cam_r_L1_cocuk_odasi_2: room rule: wall ΔE 6.975 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_cocuk_odasi_3: room rule ran a2
- cam_r_L1_cocuk_odasi_3: room rule ran a3
- cam_r_L1_cocuk_odasi_3: room rule: wall ΔE 6.975 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_hol_1: room rule ran a3
- cam_r_L1_hol_1: room rule: wall ΔE 6.834 > 5.0 in r_L1_hol; a2 -> cycles
- cam_r_L1_hol_2: room rule ran a2
- cam_r_L1_hol_2: room rule ran a3
- cam_r_L1_hol_2: room rule: wall ΔE 6.834 > 5.0 in r_L1_hol; a1 -> cycles
- cam_r_L1_hol_3: room rule ran a2
- cam_r_L1_hol_3: room rule ran a3
- cam_r_L1_hol_3: room rule: wall ΔE 6.834 > 5.0 in r_L1_hol; a1 -> cycles

## Prompts

- cam_r_L-1_banyo_1: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_banyo_2: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_2_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_wc_1: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_wc_2: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_antre_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_antre_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kiler_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_1: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, kitchen counter, fridge, stove, dining table, kitchen sink. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_2: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, kitchen counter, stove, dining table, chair, kitchen sink. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_3: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, stove, dining table, kitchen counter, chair, kitchen sink. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_1: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, sofa, coffee table, bookshelf, TV unit, armchair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_2: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, bookshelf, TV unit. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_3: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, sofa, armchair, coffee table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_wc_1: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, toilet, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, dresser, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, wardrobe, dresser, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, nightstand, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_balkon_1: Photorealistic interior photograph of a balcony in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_1: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_2: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_3: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, single bed, bookshelf, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, wardrobe, desk, single bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, wardrobe, single bed, desk. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, desk. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, wardrobe, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, wardrobe, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, desk, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
