# Polish report: synthetic-03 (run)

44 views, 102 attempts (102 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Workstation Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 2.4 s, prompt encoding 2.3 s, 1.35 s per forward, run 467 s.

Final images: 16 polished, 28 Cycles (gate 2, room 26). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.8 | 0 |
| cam_r_L-1_banyo_2 | r_L-1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.75 | 0 |
| cam_r_L-1_hol_1 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L-1_hol_2 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L-1_hol_3 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L-1_kiler_1 | r_L-1_kiler | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.72 | 1 |
| cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.72 | 1 |
| cam_r_L-1_wc_1 | r_L-1_wc | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.72 | 0 |
| cam_r_L-1_wc_2 | r_L-1_wc | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.73 | 0 |
| cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L0_antre_1 | r_L0_antre | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.73 | 0 |
| cam_r_L0_antre_2 | r_L0_antre | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L0_hol_1 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L0_hol_2 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L0_hol_3 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L0_kiler_1 | r_L0_kiler | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.78 | 1 |
| cam_r_L0_mutfak_1 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L0_mutfak_2 | r_L0_mutfak | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | edges:dec_L0_022 0.854 (needs >= 0.87) | 1.78 | 1 |
| cam_r_L0_mutfak_3 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.74 | 1 |
| cam_r_L0_salon_1 | r_L0_salon | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.77 | 0 |
| cam_r_L0_salon_2 | r_L0_salon | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L0_salon_3 | r_L0_salon | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 1 |
| cam_r_L0_wc_1 | r_L0_wc | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 2 |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | masks:dec_L0_019 0.483 (needs >= 0.62) | 1.79 | 0 |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 1 |
| cam_r_L1_balkon_1 | r_L1_balkon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L1_banyo_1 | r_L1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.79 | 1 |
| cam_r_L1_banyo_2 | r_L1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L1_banyo_3 | r_L1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 2.79 | 0 |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 2 |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.77 | 2 |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 2 |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L1_hol_1 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L1_hol_2 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.77 | 0 |
| cam_r_L1_hol_3 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 1 |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 0 |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 1 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L-1_banyo | ok | - | 0.941 | - | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_hol | downgraded | cycles | 5.27 | - | cam_r_L-1_hol_1, cam_r_L-1_hol_2, cam_r_L-1_hol_3 |
| r_L-1_kiler | ok | - | - | - | cam_r_L-1_kiler_1 |
| r_L-1_kiler_2 | ok | - | - | - | cam_r_L-1_kiler_2_1 |
| r_L-1_wc | ok | - | 0.282 | - | cam_r_L-1_wc_1, cam_r_L-1_wc_2 |
| r_L-1_yatak_odasi | downgraded | cycles | 8.81 | - | cam_r_L-1_yatak_odasi_1, cam_r_L-1_yatak_odasi_2, cam_r_L-1_yatak_odasi_3 |
| r_L0_antre | ok | - | 1.42 | - | cam_r_L0_antre_1, cam_r_L0_antre_2 |
| r_L0_hol | downgraded | cycles | 19.4 | - | cam_r_L0_hol_1, cam_r_L0_hol_2, cam_r_L0_hol_3 |
| r_L0_kiler | ok | - | - | - | cam_r_L0_kiler_1 |
| r_L0_mutfak | ok | - | 2.14 | - | cam_r_L0_mutfak_1, cam_r_L0_mutfak_3 |
| r_L0_salon | downgraded | cycles | 9.17 | - | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_wc | ok | - | - | - | cam_r_L0_wc_1 |
| r_L0_yatak_odasi | downgraded | cycles | 12.3 | - | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_3 |
| r_L1_balkon | ok | - | - | - | cam_r_L1_balkon_1 |
| r_L1_banyo | ok | - | 2.76 | - | cam_r_L1_banyo_1, cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | downgraded | cycles | 14.7 | - | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | downgraded | cycles | 16.5 | - | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | downgraded | cycles | 13.5 | - | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | downgraded | cycles | 24.8 | - | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L-1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.7 | reject | depth:f_L-1_009 0.185 (needs <= 0.14) | - |
| cam_r_L-1_banyo_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.75 | accept | - | - |
| cam_r_L-1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.7 | accept | - | - |
| cam_r_L-1_hol_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L-1_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L-1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.71 | accept | - | - |
| cam_r_L-1_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L-1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L-1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.71 | accept | - | - |
| cam_r_L-1_hol_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L-1_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L-1_kiler_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | accept | - | - |
| cam_r_L-1_kiler_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | accept | - | - |
| cam_r_L-1_wc_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | accept | - | - |
| cam_r_L-1_wc_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | accept | - | - |
| cam_r_L-1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | accept | - | - |
| cam_r_L-1_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L-1_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L-1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | accept | - | - |
| cam_r_L-1_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L-1_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L-1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | accept | - | - |
| cam_r_L-1_yatak_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L-1_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_antre_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | accept | - | - |
| cam_r_L0_antre_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L0_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | accept | - | - |
| cam_r_L0_hol_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L0_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | accept | - | - |
| cam_r_L0_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L0_hol_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_kiler_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | reject | depth:d_L0_007 0.147 (needs <= 0.14) | - |
| cam_r_L0_kiler_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.78 | accept | - | - |
| cam_r_L0_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L0_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | reject | edges:dec_L0_022 0.824 (needs >= 0.87); depth:f_L0_011 0.172 (needs <= 0.14) | - |
| cam_r_L0_mutfak_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | reject | edges:dec_L0_022 0.818 (needs >= 0.87) | - |
| cam_r_L0_mutfak_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | reject | edges:dec_L0_022 0.854 (needs >= 0.87) | - |
| cam_r_L0_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.74 | accept | - | - |
| cam_r_L0_salon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | reject | edges:dec_L0_007 0.281 (needs >= 0.87) | - |
| cam_r_L0_salon_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.79 | accept | - | - |
| cam_r_L0_salon_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.77 | accept | - | - |
| cam_r_L0_salon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L0_salon_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_salon_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_salon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | reject | edges:f_L0_004 0.819 (needs >= 0.87) | - |
| cam_r_L0_salon_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.78 | accept | - | - |
| cam_r_L0_salon_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_wc_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | reject | edges:dec_L0_019 0.736 (needs >= 0.87); masks:dec_L0_019 0.439 (needs >= 0.62) | - |
| cam_r_L0_yatak_odasi_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.79 | reject | masks:dec_L0_019 0.447 (needs >= 0.62) | - |
| cam_r_L0_yatak_odasi_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.79 | reject | masks:dec_L0_019 0.483 (needs >= 0.62) | - |
| cam_r_L0_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | reject | edges:dec_L0_021 0.815 (needs >= 0.87) | - |
| cam_r_L0_yatak_odasi_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.79 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_balkon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.87 | reject | depth:global 0.0601 (needs <= 0.05) | - |
| cam_r_L1_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.79 | accept | - | - |
| cam_r_L1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L1_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | reject | edges:d_L1_004 0.79 (needs >= 0.87) | - |
| cam_r_L1_banyo_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.79 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | reject | masks:dec_L1_020 0.483 (needs >= 0.62) | - |
| cam_r_L1_cocuk_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.77 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.77 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L1_hol_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L1_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L1_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.77 | accept | - | - |
| cam_r_L1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.75 | accept | - | - |
| cam_r_L1_hol_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L1_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L1_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L1_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | reject | edges:dec_L1_014 0.863 (needs >= 0.87) | - |
| cam_r_L1_yatak_odasi_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.78 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |

## Notes

- cam_r_L-1_hol_1: room rule ran a2
- cam_r_L-1_hol_1: room rule ran a3
- cam_r_L-1_hol_1: room rule: wall ΔE 5.273 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L-1_hol_2: room rule ran a2
- cam_r_L-1_hol_2: room rule ran a3
- cam_r_L-1_hol_2: room rule: wall ΔE 5.273 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L-1_hol_3: room rule ran a2
- cam_r_L-1_hol_3: room rule ran a3
- cam_r_L-1_hol_3: room rule: wall ΔE 5.273 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L-1_yatak_odasi_1: room rule ran a2
- cam_r_L-1_yatak_odasi_1: room rule ran a3
- cam_r_L-1_yatak_odasi_1: room rule: wall ΔE 8.812 > 5.0 in r_L-1_yatak_odasi; a1 -> cycles
- cam_r_L-1_yatak_odasi_2: room rule ran a2
- cam_r_L-1_yatak_odasi_2: room rule ran a3
- cam_r_L-1_yatak_odasi_2: room rule: wall ΔE 8.812 > 5.0 in r_L-1_yatak_odasi; a1 -> cycles
- cam_r_L-1_yatak_odasi_3: room rule ran a2
- cam_r_L-1_yatak_odasi_3: room rule ran a3
- cam_r_L-1_yatak_odasi_3: room rule: wall ΔE 8.812 > 5.0 in r_L-1_yatak_odasi; a1 -> cycles
- cam_r_L0_hol_1: room rule ran a2
- cam_r_L0_hol_1: room rule ran a3
- cam_r_L0_hol_1: room rule: wall ΔE 19.391 > 5.0 in r_L0_hol; a1 -> cycles
- cam_r_L0_hol_2: room rule ran a2
- cam_r_L0_hol_2: room rule ran a3
- cam_r_L0_hol_2: room rule: wall ΔE 19.391 > 5.0 in r_L0_hol; a1 -> cycles
- cam_r_L0_hol_3: room rule ran a2
- cam_r_L0_hol_3: room rule ran a3
- cam_r_L0_hol_3: room rule: wall ΔE 19.391 > 5.0 in r_L0_hol; a1 -> cycles
- cam_r_L0_salon_1: room rule ran a3
- cam_r_L0_salon_1: room rule: wall ΔE 9.172 > 5.0 in r_L0_salon; a2 -> cycles
- cam_r_L0_salon_2: room rule ran a2
- cam_r_L0_salon_2: room rule ran a3
- cam_r_L0_salon_2: room rule: wall ΔE 9.172 > 5.0 in r_L0_salon; a1 -> cycles
- cam_r_L0_salon_3: room rule ran a3
- cam_r_L0_salon_3: room rule: wall ΔE 9.172 > 5.0 in r_L0_salon; a2 -> cycles
- cam_r_L0_yatak_odasi_1: room rule ran a2
- cam_r_L0_yatak_odasi_1: room rule ran a3
- cam_r_L0_yatak_odasi_1: room rule: wall ΔE 12.255 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L0_yatak_odasi_3: room rule ran a3
- cam_r_L0_yatak_odasi_3: room rule: wall ΔE 12.255 > 5.0 in r_L0_yatak_odasi; a2 -> cycles
- cam_r_L1_cocuk_odasi_1: room rule ran a2
- cam_r_L1_cocuk_odasi_1: room rule ran a3
- cam_r_L1_cocuk_odasi_1: room rule: wall ΔE 14.723 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_cocuk_odasi_2: room rule ran a3
- cam_r_L1_cocuk_odasi_2: room rule: wall ΔE 14.723 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_cocuk_odasi_3: room rule ran a3
- cam_r_L1_cocuk_odasi_3: room rule: wall ΔE 14.723 > 5.0 in r_L1_cocuk_odasi; a1 -> cycles
- cam_r_L1_ebeveyn_yatak_odasi_1: room rule ran a2
- cam_r_L1_ebeveyn_yatak_odasi_1: room rule ran a3
- cam_r_L1_ebeveyn_yatak_odasi_1: room rule: wall ΔE 16.455 > 5.0 in r_L1_ebeveyn_yatak_odasi; a1 -> cycles
- cam_r_L1_ebeveyn_yatak_odasi_2: room rule ran a2
- cam_r_L1_ebeveyn_yatak_odasi_2: room rule ran a3
- cam_r_L1_ebeveyn_yatak_odasi_2: room rule: wall ΔE 16.455 > 5.0 in r_L1_ebeveyn_yatak_odasi; a1 -> cycles
- cam_r_L1_ebeveyn_yatak_odasi_3: room rule ran a2
- cam_r_L1_ebeveyn_yatak_odasi_3: room rule ran a3
- cam_r_L1_ebeveyn_yatak_odasi_3: room rule: wall ΔE 16.455 > 5.0 in r_L1_ebeveyn_yatak_odasi; a1 -> cycles
- cam_r_L1_hol_1: room rule ran a2
- cam_r_L1_hol_1: room rule ran a3
- cam_r_L1_hol_1: room rule: wall ΔE 13.515 > 5.0 in r_L1_hol; a1 -> cycles
- cam_r_L1_hol_2: room rule ran a2
- cam_r_L1_hol_2: room rule ran a3
- cam_r_L1_hol_2: room rule: wall ΔE 13.515 > 5.0 in r_L1_hol; a1 -> cycles
- cam_r_L1_hol_3: room rule ran a2
- cam_r_L1_hol_3: room rule ran a3
- cam_r_L1_hol_3: room rule: wall ΔE 13.515 > 5.0 in r_L1_hol; a1 -> cycles
- cam_r_L1_yatak_odasi_1: room rule ran a2
- cam_r_L1_yatak_odasi_1: room rule ran a3
- cam_r_L1_yatak_odasi_1: room rule: wall ΔE 24.768 > 5.0 in r_L1_yatak_odasi; a1 -> cycles
- cam_r_L1_yatak_odasi_2: room rule ran a2
- cam_r_L1_yatak_odasi_2: room rule ran a3
- cam_r_L1_yatak_odasi_2: room rule: wall ΔE 24.768 > 5.0 in r_L1_yatak_odasi; a1 -> cycles
- cam_r_L1_yatak_odasi_3: room rule ran a3
- cam_r_L1_yatak_odasi_3: room rule: wall ΔE 24.768 > 5.0 in r_L1_yatak_odasi; a2 -> cycles

## Prompts

- cam_r_L-1_banyo_1: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1_banyo_2: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, toilet, shower, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, console table, shoe cabinet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, shoe cabinet, console table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, shoe cabinet, console table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1_kiler_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_kiler_2_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_wc_1: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1_wc_2: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, double bed, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, desk, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, double bed, nightstand, desk. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_antre_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, console table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_antre_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, console table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, shoe cabinet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, console table, shoe cabinet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, console table, shoe cabinet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_kiler_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_mutfak_1: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, kitchen counter, dining table, tall cabinet, wall cabinets, fridge, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_mutfak_2: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, kitchen counter, tall cabinet, fridge, wall cabinets, dining table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_mutfak_3: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, fridge, kitchen counter. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_salon_1: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, sofa, coffee table, armchair, ottoman. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_salon_2: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, sofa, armchair, ottoman, coffee table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_salon_3: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, armchair, sofa, ottoman, coffee table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_wc_1: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, washbasin, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, wardrobe, dresser, double bed, bench. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, double bed, bench, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, dresser, double bed, bench, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_balkon_1: Photorealistic interior photograph of a balcony in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_banyo_1: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_banyo_2: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_banyo_3: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_cocuk_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, wardrobe, single bed, nightstand, desk. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_cocuk_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, single bed, wardrobe, desk. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_cocuk_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, single bed, wardrobe, office chair, desk. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, double bed, desk, office chair, nightstand, wardrobe. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, double bed, wardrobe, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, double bed, nightstand, desk, office chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, console table, shoe cabinet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, console table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, shoe cabinet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, double bed, wardrobe, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, one white smooth painted accent wall, polished concrete floor, wardrobe, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.

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
