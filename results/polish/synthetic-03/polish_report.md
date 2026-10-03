# Polish report: synthetic-03 (run)

50 views, 84 attempts (84 polished now, 0 reused). Device NVIDIA RTX PRO 4500 Blackwell, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 4.2 s, prompt encoding 3.9 s, 2.86 s per forward, run 845 s.

Final images: 36 polished, 14 Cycles (gate 2, room 12). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6 | 0 |
| cam_r_L-1_banyo_2 | r_L-1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.2 | 0 |
| cam_r_L-1_hol_1 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L-1_hol_2 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L-1_hol_3 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L-1_kiler_1 | r_L-1_kiler | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.22 | 0 |
| cam_r_L-1_kiler_2 | r_L-1_kiler | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 0 |
| cam_r_L-1_kiler_2_2 | r_L-1_kiler_2 | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L-1_kiler_2_3 | r_L-1_kiler_2 | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L-1_kiler_3 | r_L-1_kiler | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L-1_wc_1 | r_L-1_wc | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L-1_008 0.148 (needs <= 0.14) | 3.78 | 0 |
| cam_r_L-1_wc_2 | r_L-1_wc | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 3.8 | 0 |
| cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 1 |
| cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 1 |
| cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 1 |
| cam_r_L0_antre_1 | r_L0_antre | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:d_L0_003 0.144 (needs <= 0.14) | 3.76 | 0 |
| cam_r_L0_antre_2 | r_L0_antre | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L0_hol_1 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L0_hol_2 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L0_hol_3 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L0_kiler_1 | r_L0_kiler | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.26 | 1 |
| cam_r_L0_mutfak_1 | r_L0_mutfak | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.01 | 1 |
| cam_r_L0_mutfak_2 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.26 | 1 |
| cam_r_L0_mutfak_3 | r_L0_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.27 | 1 |
| cam_r_L0_salon_1 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 1 |
| cam_r_L0_salon_2 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 0 |
| cam_r_L0_salon_3 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 0 |
| cam_r_L0_wc_1 | r_L0_wc | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.04 | 0 |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.03 | 0 |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 1 |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_balkon_1 | r_L1_balkon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 1 |
| cam_r_L1_balkon_2 | r_L1_balkon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 1 |
| cam_r_L1_balkon_3 | r_L1_balkon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_banyo_1 | r_L1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 0 |
| cam_r_L1_banyo_2 | r_L1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.02 | 0 |
| cam_r_L1_banyo_3 | r_L1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 1 |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.26 | 2 |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.26 | 1 |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.27 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.04 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 2 |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.27 | 2 |
| cam_r_L1_hol_1 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.76 | 0 |
| cam_r_L1_hol_2 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L1_hol_3 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.76 | 0 |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.76 | 1 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L-1_banyo | ok | - | 0.598 | - | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_hol | downgraded | cycles | 9.25 | - | cam_r_L-1_hol_1, cam_r_L-1_hol_2, cam_r_L-1_hol_3 |
| r_L-1_kiler | ok | - | 0.705 | - | cam_r_L-1_kiler_1, cam_r_L-1_kiler_2, cam_r_L-1_kiler_3 |
| r_L-1_kiler_2 | ok | - | 1.78 | - | cam_r_L-1_kiler_2_1, cam_r_L-1_kiler_2_2, cam_r_L-1_kiler_2_3 |
| r_L-1_wc | ok | - | - | - | cam_r_L-1_wc_2 |
| r_L-1_yatak_odasi | ok | - | 0.803 | - | cam_r_L-1_yatak_odasi_1, cam_r_L-1_yatak_odasi_2, cam_r_L-1_yatak_odasi_3 |
| r_L0_antre | ok | - | - | - | cam_r_L0_antre_2 |
| r_L0_hol | downgraded | cycles | 9.36 | - | cam_r_L0_hol_1, cam_r_L0_hol_2, cam_r_L0_hol_3 |
| r_L0_kiler | ok | - | - | - | cam_r_L0_kiler_1 |
| r_L0_mutfak | ok | - | 4.88 | - | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | ok | - | 2.91 | - | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_wc | ok | - | - | - | cam_r_L0_wc_1 |
| r_L0_yatak_odasi | ok | - | 2.91 | - | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_balkon | ok | - | 2.35 | - | cam_r_L1_balkon_1, cam_r_L1_balkon_2, cam_r_L1_balkon_3 |
| r_L1_banyo | ok | - | 2.79 | - | cam_r_L1_banyo_1, cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | ok | - | 2.59 | - | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | ok | - | 2.11 | - | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | downgraded | cycles | 5.43 | - | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | downgraded | cycles | 5.27 | - | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.42 | reject | depth:global 0.092 (needs <= 0.05) | - |
| cam_r_L-1_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L-1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.2 | accept | - | - |
| cam_r_L-1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.22 | reject | neutral:struct:ceiling 2.17 (needs <= 2) | - |
| cam_r_L-1_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L-1_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L-1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L-1_hol_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L-1_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_kiler_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.22 | accept | - | - |
| cam_r_L-1_kiler_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_kiler_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L-1_kiler_2_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_kiler_2_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_kiler_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_wc_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.085 (needs <= 0.05); depth:f_L-1_008 0.244 (needs <= 0.14) | - |
| cam_r_L-1_wc_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.02 | reject | depth:global 0.0698 (needs <= 0.05); depth:f_L-1_008 0.202 (needs <= 0.14) | - |
| cam_r_L-1_wc_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.78 | reject | depth:f_L-1_008 0.148 (needs <= 0.14) | - |
| cam_r_L-1_wc_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:f_L-1_008 0.324 (needs <= 0.14) | - |
| cam_r_L-1_wc_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | reject | depth:f_L-1_008 0.226 (needs <= 0.14) | - |
| cam_r_L-1_wc_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.8 | accept | - | - |
| cam_r_L-1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L-1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L-1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_antre_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.06 (needs <= 0.05) | - |
| cam_r_L0_antre_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | reject | depth:global 0.0645 (needs <= 0.05); depth:d_L0_003 0.233 (needs <= 0.14) | - |
| cam_r_L0_antre_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | reject | depth:d_L0_003 0.144 (needs <= 0.14) | - |
| cam_r_L0_antre_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | neutral:struct:ceiling 2.08 (needs <= 2) | - |
| cam_r_L0_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | accept | - | - |
| cam_r_L0_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L0_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | reject | neutral:struct:ceiling 2.01 (needs <= 2) | - |
| cam_r_L0_hol_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L0_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L0_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | reject | neutral:struct:ceiling 2.19 (needs <= 2) | - |
| cam_r_L0_hol_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.02 | accept | - | - |
| cam_r_L0_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L0_kiler_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L0_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | reject | edges:f_L0_009 0.865 (needs >= 0.87) | - |
| cam_r_L0_mutfak_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |
| cam_r_L0_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L0_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.27 | accept | - | - |
| cam_r_L0_salon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_salon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_salon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_wc_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | reject | edges:global 0.889 (needs >= 0.935); edges:f_L0_020 0.0048 (needs >= 0.87); depth:f_L0_020 0.185 (needs <= 0.14) | - |
| cam_r_L0_wc_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | reject | edges:global 0.934 (needs >= 0.935) | - |
| cam_r_L0_yatak_odasi_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_balkon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_balkon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_balkon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | edges:global 0.933 (needs >= 0.935) | - |
| cam_r_L1_banyo_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.02 | accept | - | - |
| cam_r_L1_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.27 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | reject | edges:f_L1_004 0.781 (needs >= 0.87) | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.27 | accept | - | - |
| cam_r_L1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | reject | neutral:struct:ceiling 2.19 (needs <= 2) | - |
| cam_r_L1_hol_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | reject | edges:d_L1_002 0.836 (needs >= 0.87) | - |
| cam_r_L1_hol_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | accept | - | - |
| cam_r_L1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_hol_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L1_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |
| cam_r_L1_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.28 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L1_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | accept | - | - |

## Notes

- cam_r_L-1_hol_1: room rule ran a3
- cam_r_L-1_hol_1: room rule: wall ΔE 9.251 > 5.0 in r_L-1_hol; a2 -> cycles
- cam_r_L-1_hol_2: room rule ran a2
- cam_r_L-1_hol_2: room rule ran a3
- cam_r_L-1_hol_2: room rule: wall ΔE 9.251 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L-1_hol_3: room rule ran a2
- cam_r_L-1_hol_3: room rule ran a3
- cam_r_L-1_hol_3: room rule: wall ΔE 9.251 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L0_hol_1: room rule ran a3
- cam_r_L0_hol_1: room rule: wall ΔE 9.363 > 5.0 in r_L0_hol; a2 -> cycles
- cam_r_L0_hol_2: room rule ran a3
- cam_r_L0_hol_2: room rule: wall ΔE 9.363 > 5.0 in r_L0_hol; a2 -> cycles
- cam_r_L0_hol_3: room rule ran a3
- cam_r_L0_hol_3: room rule: wall ΔE 9.363 > 5.0 in r_L0_hol; a2 -> cycles
- cam_r_L1_hol_1: room rule: wall ΔE 5.432 > 5.0 in r_L1_hol; a3 -> cycles
- cam_r_L1_hol_2: room rule ran a3
- cam_r_L1_hol_2: room rule: wall ΔE 5.432 > 5.0 in r_L1_hol; a1 -> cycles
- cam_r_L1_hol_3: room rule ran a3
- cam_r_L1_hol_3: room rule: wall ΔE 5.432 > 5.0 in r_L1_hol; a1 -> cycles
- cam_r_L1_yatak_odasi_1: room rule ran a2
- cam_r_L1_yatak_odasi_1: room rule ran a3
- cam_r_L1_yatak_odasi_1: room rule: wall ΔE 5.271 > 5.0 in r_L1_yatak_odasi; a1 -> cycles
- cam_r_L1_yatak_odasi_2: room rule ran a2
- cam_r_L1_yatak_odasi_2: room rule ran a3
- cam_r_L1_yatak_odasi_2: room rule: wall ΔE 5.271 > 5.0 in r_L1_yatak_odasi; a1 -> cycles
- cam_r_L1_yatak_odasi_3: room rule ran a2
- cam_r_L1_yatak_odasi_3: room rule ran a3
- cam_r_L1_yatak_odasi_3: room rule: wall ΔE 5.271 > 5.0 in r_L1_yatak_odasi; a1 -> cycles

## Prompts

- cam_r_L-1_banyo_1: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, toilet, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_banyo_2: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, washbasin, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_2: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_2_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_2_2: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_2_3: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_3: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_wc_1: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_wc_2: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, desk. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_antre_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_antre_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kiler_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_1: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, kitchen counter, dining table, fridge, stove, kitchen sink. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_2: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, fridge, dining table, kitchen counter, stove, kitchen sink. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_3: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, stove, kitchen counter, dining table, kitchen sink. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_1: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, sofa, armchair, coffee table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_2: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, sofa, armchair, coffee table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_3: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, armchair, bookshelf, sofa. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_wc_1: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, washbasin, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, dresser, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, nightstand, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_balkon_1: Photorealistic interior photograph of a balcony in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_balkon_2: Photorealistic interior photograph of a balcony in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_balkon_3: Photorealistic interior photograph of a balcony in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_1: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, toilet, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_2: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, washbasin, shower. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_3: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, single bed, desk, nightstand, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, single bed, desk, chair, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, single bed, desk, nightstand, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, wardrobe, desk, chair, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, nightstand, desk, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, desk, chair, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, wardrobe, double bed, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, wardrobe, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
