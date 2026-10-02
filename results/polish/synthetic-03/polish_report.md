# Polish report: synthetic-03 (run)

57 views, 135 attempts (135 polished now, 0 reused). Device NVIDIA RTX PRO 4500 Blackwell, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 4.3 s, prompt encoding 3.7 s, 2.94 s per forward, run 1.22e+03 s.

Final images: 21 polished, 36 Cycles (gate 10, room 26). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.02 | 0 |
| cam_r_L-1_banyo_2 | r_L-1_banyo | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L-1_011 0.236 (needs <= 0.14) | 3.79 | 0 |
| cam_r_L-1_banyo_3 | r_L-1_banyo | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.0677 (needs <= 0.05) | 3.77 | 0 |
| cam_r_L-1_hol_1 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.74 | 0 |
| cam_r_L-1_hol_2 | r_L-1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.74 | 0 |
| cam_r_L-1_hol_3 | r_L-1_hol | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.117 (needs <= 0.05) | 3.76 | 0 |
| cam_r_L-1_kiler_1 | r_L-1_kiler | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L-1_kiler_2 | r_L-1_kiler | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L-1_kiler_2_2 | r_L-1_kiler_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L-1_kiler_2_3 | r_L-1_kiler_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L-1_kiler_3 | r_L-1_kiler | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L-1_wc_1 | r_L-1_wc | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.03 | 0 |
| cam_r_L-1_wc_2 | r_L-1_wc | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 0 |
| cam_r_L-1_wc_3 | r_L-1_wc | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 0 |
| cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L-1_003 0.217 (needs <= 0.14) | 3.75 | 0 |
| cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | cycles (room) | - | 0.25 / canny / 0.8 / native / plain | accept | - | 6 | 0 |
| cam_r_L0_antre_1 | r_L0_antre | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L0_antre_2 | r_L0_antre | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L0_antre_3 | r_L0_antre | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.74 | 0 |
| cam_r_L0_hol_1 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L0_hol_2 | r_L0_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L0_023 0.169 (needs <= 0.14) | 3.75 | 0 |
| cam_r_L0_hol_3 | r_L0_hol | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.0756 (needs <= 0.05) | 3.76 | 0 |
| cam_r_L0_kiler_1 | r_L0_kiler | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.04 | 0 |
| cam_r_L0_kiler_2 | r_L0_kiler | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L0_kiler_3 | r_L0_kiler | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L0_021 0.15 (needs <= 0.14) | 3.8 | 0 |
| cam_r_L0_mutfak_1 | r_L0_mutfak | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.74 | 0 |
| cam_r_L0_mutfak_2 | r_L0_mutfak | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L0_mutfak_3 | r_L0_mutfak | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.74 | 0 |
| cam_r_L0_salon_1 | r_L0_salon | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 3.79 | 1 |
| cam_r_L0_salon_2 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.28 | 1 |
| cam_r_L0_salon_3 | r_L0_salon | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 1 |
| cam_r_L0_wc_1 | r_L0_wc | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.74 | 0 |
| cam_r_L0_wc_2 | r_L0_wc | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.78 | 0 |
| cam_r_L0_wc_3 | r_L0_wc | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.0505 (needs <= 0.05) | 3.78 | 0 |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.25 | 1 |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.26 | 1 |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_balkon_1 | r_L1_balkon | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L1_balkon_2 | r_L1_balkon | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 1 |
| cam_r_L1_balkon_3 | r_L1_balkon | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.74 | 0 |
| cam_r_L1_banyo_1 | r_L1_banyo | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.133 (needs <= 0.05) | 3.76 | 0 |
| cam_r_L1_banyo_2 | r_L1_banyo | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.0993 (needs <= 0.05) | 3.75 | 0 |
| cam_r_L1_banyo_3 | r_L1_banyo | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6 | 0 |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.26 | 1 |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.01 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.23 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 1 |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 1 |
| cam_r_L1_hol_1 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L1_hol_2 | r_L1_hol | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 3.75 | 0 |
| cam_r_L1_hol_3 | r_L1_hol | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | edges:global 0.44 (needs >= 0.935); depth:global 0.144 (needs <= 0.05); depth:struct:walls 0.145 (needs <= 0.14) | 3.76 | 0 |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L1_007 0.28 (needs <= 0.14) | 3.77 | 1 |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 8.24 | 0 |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 6.01 | 0 |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L-1_banyo | ok | - | - | - | cam_r_L-1_banyo_1 |
| r_L-1_hol | downgraded | cycles | 7.14 | - | cam_r_L-1_hol_1, cam_r_L-1_hol_2 |
| r_L-1_kiler | downgraded | cycles | 16.8 | - | cam_r_L-1_kiler_1, cam_r_L-1_kiler_2, cam_r_L-1_kiler_3 |
| r_L-1_kiler_2 | downgraded | cycles | 13.2 | - | cam_r_L-1_kiler_2_1, cam_r_L-1_kiler_2_2, cam_r_L-1_kiler_2_3 |
| r_L-1_wc | ok | - | 3.22 | - | cam_r_L-1_wc_1, cam_r_L-1_wc_2, cam_r_L-1_wc_3 |
| r_L-1_yatak_odasi | downgraded | cycles | 6.71 | - | cam_r_L-1_yatak_odasi_1, cam_r_L-1_yatak_odasi_2, cam_r_L-1_yatak_odasi_3 |
| r_L0_antre | downgraded | cycles | 25 | - | cam_r_L0_antre_1, cam_r_L0_antre_2, cam_r_L0_antre_3 |
| r_L0_hol | downgraded | cycles | 8.35 | - | cam_r_L0_hol_1, cam_r_L0_hol_2 |
| r_L0_kiler | ok | - | 3.85 | - | cam_r_L0_kiler_1, cam_r_L0_kiler_2 |
| r_L0_mutfak | downgraded | cycles | 32.8 | - | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | ok | - | 2.92 | - | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_wc | downgraded | cycles | 11.5 | - | cam_r_L0_wc_1, cam_r_L0_wc_2 |
| r_L0_yatak_odasi | ok | - | 1.84 | - | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_balkon | downgraded | cycles | 6.52 | - | cam_r_L1_balkon_1, cam_r_L1_balkon_2, cam_r_L1_balkon_3 |
| r_L1_banyo | ok | - | - | - | cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | ok | - | 1.93 | - | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | ok | - | 1.65 | - | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | downgraded | cycles | 9.74 | - | cam_r_L1_hol_1, cam_r_L1_hol_2 |
| r_L1_yatak_odasi | ok | - | 2.21 | - | cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.41 | reject | edges:global 0.934 (needs >= 0.935); depth:global 0.0702 (needs <= 0.05) | - |
| cam_r_L-1_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.02 | accept | - | - |
| cam_r_L-1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | reject | depth:global 0.0614 (needs <= 0.05) | - |
| cam_r_L-1_banyo_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | reject | depth:global 0.0717 (needs <= 0.05); depth:f_L-1_011 0.284 (needs <= 0.14) | - |
| cam_r_L-1_banyo_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.79 | reject | depth:f_L-1_011 0.236 (needs <= 0.14) | - |
| cam_r_L-1_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | reject | depth:global 0.123 (needs <= 0.05); depth:struct:walls 0.149 (needs <= 0.14) | - |
| cam_r_L-1_banyo_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | reject | depth:global 0.0675 (needs <= 0.05) | - |
| cam_r_L-1_banyo_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.77 | reject | depth:global 0.0677 (needs <= 0.05) | - |
| cam_r_L-1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L-1_hol_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L-1_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.74 | accept | - | - |
| cam_r_L-1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L-1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.74 | accept | - | - |
| cam_r_L-1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | reject | depth:global 0.144 (needs <= 0.05); depth:struct:walls 0.143 (needs <= 0.14) | - |
| cam_r_L-1_hol_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | reject | depth:global 0.153 (needs <= 0.05); depth:struct:walls 0.154 (needs <= 0.14) | - |
| cam_r_L-1_hol_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | reject | depth:global 0.117 (needs <= 0.05) | - |
| cam_r_L-1_kiler_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L-1_kiler_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L-1_kiler_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_kiler_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_kiler_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L-1_kiler_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_kiler_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_kiler_2_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L-1_kiler_2_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_kiler_2_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L-1_kiler_2_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L-1_kiler_2_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_kiler_2_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L-1_kiler_2_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L-1_kiler_2_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_kiler_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_kiler_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L-1_kiler_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_wc_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.0622 (needs <= 0.05) | - |
| cam_r_L-1_wc_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L-1_wc_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L-1_wc_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L-1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L-1_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L-1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L-1_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | reject | depth:f_L-1_003 0.217 (needs <= 0.14) | - |
| cam_r_L-1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L-1_yatak_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L0_antre_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L0_antre_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L0_antre_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L0_antre_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | reject | edges:global 0.927 (needs >= 0.935) | - |
| cam_r_L0_antre_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L0_antre_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L0_antre_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.0785 (needs <= 0.05) | - |
| cam_r_L0_antre_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | accept | - | - |
| cam_r_L0_antre_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.74 | accept | - | - |
| cam_r_L0_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_hol_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L0_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L0_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L0_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | reject | depth:f_L0_023 0.169 (needs <= 0.14) | - |
| cam_r_L0_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.0836 (needs <= 0.05) | - |
| cam_r_L0_hol_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.02 | reject | depth:global 0.112 (needs <= 0.05) | - |
| cam_r_L0_hol_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | reject | depth:global 0.0756 (needs <= 0.05) | - |
| cam_r_L0_kiler_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | edges:global 0.928 (needs >= 0.935) | - |
| cam_r_L0_kiler_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | accept | - | - |
| cam_r_L0_kiler_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_kiler_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | reject | depth:f_L0_021 0.18 (needs <= 0.14) | - |
| cam_r_L0_kiler_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.04 | reject | depth:f_L0_021 0.169 (needs <= 0.14) | - |
| cam_r_L0_kiler_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.8 | reject | depth:f_L0_021 0.15 (needs <= 0.14) | - |
| cam_r_L0_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:f_L0_011 0.194 (needs <= 0.14) | - |
| cam_r_L0_mutfak_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.05 | accept | - | - |
| cam_r_L0_mutfak_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.74 | accept | - | - |
| cam_r_L0_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L0_mutfak_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L0_mutfak_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L0_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_mutfak_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L0_mutfak_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.74 | accept | - | - |
| cam_r_L0_salon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:f_L0_006 0.193 (needs <= 0.14) | - |
| cam_r_L0_salon_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.02 | reject | depth:f_L0_006 0.197 (needs <= 0.14) | - |
| cam_r_L0_salon_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.79 | accept | - | - |
| cam_r_L0_salon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.28 | accept | - | - |
| cam_r_L0_salon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_wc_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L0_wc_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.74 | accept | - | - |
| cam_r_L0_wc_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.164 (needs <= 0.05); depth:struct:walls 0.218 (needs <= 0.14) | - |
| cam_r_L0_wc_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | reject | depth:global 0.124 (needs <= 0.05); depth:struct:walls 0.191 (needs <= 0.14) | - |
| cam_r_L0_wc_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.78 | accept | - | - |
| cam_r_L0_wc_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.0801 (needs <= 0.05); depth:struct:walls 0.165 (needs <= 0.14) | - |
| cam_r_L0_wc_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.03 | reject | depth:global 0.132 (needs <= 0.05); depth:struct:walls 0.165 (needs <= 0.14) | - |
| cam_r_L0_wc_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.78 | reject | depth:global 0.0505 (needs <= 0.05) | - |
| cam_r_L0_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_balkon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.28 | accept | - | - |
| cam_r_L1_balkon_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L1_balkon_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L1_balkon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_balkon_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L1_balkon_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L1_balkon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_balkon_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L1_balkon_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.74 | accept | - | - |
| cam_r_L1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | depth:global 0.174 (needs <= 0.05); depth:f_L1_016 0.186 (needs <= 0.14); depth:struct:walls 0.17 (needs <= 0.14) | - |
| cam_r_L1_banyo_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | reject | depth:global 0.152 (needs <= 0.05); depth:f_L1_016 0.162 (needs <= 0.14); depth:struct:walls 0.149 (needs <= 0.14) | - |
| cam_r_L1_banyo_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | reject | depth:global 0.133 (needs <= 0.05) | - |
| cam_r_L1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | reject | depth:global 0.0733 (needs <= 0.05); depth:f_L1_016 0.151 (needs <= 0.14) | - |
| cam_r_L1_banyo_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | reject | depth:global 0.174 (needs <= 0.05); depth:f_L1_016 0.164 (needs <= 0.14); depth:struct:walls 0.178 (needs <= 0.14) | - |
| cam_r_L1_banyo_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | reject | depth:global 0.0993 (needs <= 0.05) | - |
| cam_r_L1_banyo_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | edges:global 0.927 (needs >= 0.935) | - |
| cam_r_L1_banyo_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6 | accept | - | - |
| cam_r_L1_cocuk_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_cocuk_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.26 | accept | - | - |
| cam_r_L1_cocuk_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | added_lines:struct:ceiling 0.0717 (needs <= 0.04) | - |
| cam_r_L1_cocuk_odasi_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.23 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_hol_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | accept | - | - |
| cam_r_L1_hol_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L1_hol_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L1_hol_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_hol_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | accept | - | - |
| cam_r_L1_hol_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.75 | accept | - | - |
| cam_r_L1_hol_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | edges:global 0.92 (needs >= 0.935); depth:global 0.18 (needs <= 0.05); depth:struct:walls 0.181 (needs <= 0.14) | - |
| cam_r_L1_hol_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 5.99 | reject | depth:global 0.19 (needs <= 0.05); depth:struct:walls 0.19 (needs <= 0.14) | - |
| cam_r_L1_hol_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.76 | reject | edges:global 0.44 (needs >= 0.935); depth:global 0.144 (needs <= 0.05); depth:struct:walls 0.145 (needs <= 0.14) | - |
| cam_r_L1_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | reject | edges:f_L1_010 0.864 (needs >= 0.87); depth:f_L1_010 0.219 (needs <= 0.14) | - |
| cam_r_L1_yatak_odasi_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | reject | depth:f_L1_007 0.158 (needs <= 0.14) | - |
| cam_r_L1_yatak_odasi_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.77 | reject | depth:f_L1_007 0.28 (needs <= 0.14) | - |
| cam_r_L1_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.24 | accept | - | - |
| cam_r_L1_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 8.25 | reject | depth:f_L1_007 0.928 (needs <= 0.14) | - |
| cam_r_L1_yatak_odasi_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 6.01 | accept | - | - |

## Notes

- cam_r_L-1_hol_1: room rule ran a2
- cam_r_L-1_hol_1: room rule ran a3
- cam_r_L-1_hol_1: room rule: wall ΔE 7.141 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L-1_hol_2: room rule ran a2
- cam_r_L-1_hol_2: room rule ran a3
- cam_r_L-1_hol_2: room rule: wall ΔE 7.141 > 5.0 in r_L-1_hol; a1 -> cycles
- cam_r_L-1_kiler_1: room rule ran a2
- cam_r_L-1_kiler_1: room rule ran a3
- cam_r_L-1_kiler_1: room rule: wall ΔE 16.822 > 5.0 in r_L-1_kiler; a1 -> cycles
- cam_r_L-1_kiler_2: room rule ran a2
- cam_r_L-1_kiler_2: room rule ran a3
- cam_r_L-1_kiler_2: room rule: wall ΔE 16.822 > 5.0 in r_L-1_kiler; a1 -> cycles
- cam_r_L-1_kiler_2_1: room rule ran a2
- cam_r_L-1_kiler_2_1: room rule ran a3
- cam_r_L-1_kiler_2_1: room rule: wall ΔE 13.202 > 5.0 in r_L-1_kiler_2; a1 -> cycles
- cam_r_L-1_kiler_2_2: room rule ran a2
- cam_r_L-1_kiler_2_2: room rule ran a3
- cam_r_L-1_kiler_2_2: room rule: wall ΔE 13.202 > 5.0 in r_L-1_kiler_2; a1 -> cycles
- cam_r_L-1_kiler_2_3: room rule ran a2
- cam_r_L-1_kiler_2_3: room rule ran a3
- cam_r_L-1_kiler_2_3: room rule: wall ΔE 13.202 > 5.0 in r_L-1_kiler_2; a1 -> cycles
- cam_r_L-1_kiler_3: room rule ran a2
- cam_r_L-1_kiler_3: room rule ran a3
- cam_r_L-1_kiler_3: room rule: wall ΔE 16.822 > 5.0 in r_L-1_kiler; a1 -> cycles
- cam_r_L-1_yatak_odasi_1: room rule ran a2
- cam_r_L-1_yatak_odasi_1: room rule ran a3
- cam_r_L-1_yatak_odasi_1: room rule: wall ΔE 6.71 > 5.0 in r_L-1_yatak_odasi; a1 -> cycles
- cam_r_L-1_yatak_odasi_2: room rule ran a2
- cam_r_L-1_yatak_odasi_2: room rule ran a3
- cam_r_L-1_yatak_odasi_2: room rule: wall ΔE 6.71 > 5.0 in r_L-1_yatak_odasi; a1 -> cycles
- cam_r_L-1_yatak_odasi_3: room rule ran a2
- cam_r_L-1_yatak_odasi_3: room rule: wall ΔE 6.71 > 5.0 in r_L-1_yatak_odasi; a1 -> cycles
- cam_r_L0_antre_1: room rule ran a2
- cam_r_L0_antre_1: room rule ran a3
- cam_r_L0_antre_1: room rule: wall ΔE 24.98 > 5.0 in r_L0_antre; a1 -> cycles
- cam_r_L0_antre_2: room rule ran a3
- cam_r_L0_antre_2: room rule: wall ΔE 24.98 > 5.0 in r_L0_antre; a2 -> cycles
- cam_r_L0_antre_3: room rule ran a3
- cam_r_L0_antre_3: room rule: wall ΔE 24.98 > 5.0 in r_L0_antre; a2 -> cycles
- cam_r_L0_hol_1: room rule ran a2
- cam_r_L0_hol_1: room rule ran a3
- cam_r_L0_hol_1: room rule: wall ΔE 8.351 > 5.0 in r_L0_hol; a1 -> cycles
- cam_r_L0_hol_2: room rule ran a2
- cam_r_L0_hol_2: room rule ran a3
- cam_r_L0_hol_2: room rule: wall ΔE 8.351 > 5.0 in r_L0_hol; a1 -> cycles
- cam_r_L0_mutfak_1: room rule ran a3
- cam_r_L0_mutfak_1: room rule: wall ΔE 32.824 > 5.0 in r_L0_mutfak; a2 -> cycles
- cam_r_L0_mutfak_2: room rule ran a2
- cam_r_L0_mutfak_2: room rule ran a3
- cam_r_L0_mutfak_2: room rule: wall ΔE 32.824 > 5.0 in r_L0_mutfak; a1 -> cycles
- cam_r_L0_mutfak_3: room rule ran a2
- cam_r_L0_mutfak_3: room rule ran a3
- cam_r_L0_mutfak_3: room rule: wall ΔE 32.824 > 5.0 in r_L0_mutfak; a1 -> cycles
- cam_r_L0_wc_1: room rule ran a3
- cam_r_L0_wc_1: room rule: wall ΔE 11.506 > 5.0 in r_L0_wc; a1 -> cycles
- cam_r_L0_wc_2: room rule: wall ΔE 11.506 > 5.0 in r_L0_wc; a3 -> cycles
- cam_r_L1_balkon_1: room rule ran a2
- cam_r_L1_balkon_1: room rule ran a3
- cam_r_L1_balkon_1: room rule: wall ΔE 6.523 > 5.0 in r_L1_balkon; a1 -> cycles
- cam_r_L1_balkon_2: room rule ran a2
- cam_r_L1_balkon_2: room rule ran a3
- cam_r_L1_balkon_2: room rule: wall ΔE 6.523 > 5.0 in r_L1_balkon; a1 -> cycles
- cam_r_L1_balkon_3: room rule ran a2
- cam_r_L1_balkon_3: room rule ran a3
- cam_r_L1_balkon_3: room rule: wall ΔE 6.523 > 5.0 in r_L1_balkon; a1 -> cycles
- cam_r_L1_hol_1: room rule ran a2
- cam_r_L1_hol_1: room rule ran a3
- cam_r_L1_hol_1: room rule: wall ΔE 9.741 > 5.0 in r_L1_hol; a1 -> cycles
- cam_r_L1_hol_2: room rule ran a2
- cam_r_L1_hol_2: room rule ran a3
- cam_r_L1_hol_2: room rule: wall ΔE 9.741 > 5.0 in r_L1_hol; a1 -> cycles

## Prompts

- cam_r_L-1_banyo_1: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_banyo_2: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_banyo_3: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_2: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_2_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_2_2: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_2_3: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_kiler_3: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_wc_1: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_wc_2: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_wc_3: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, desk, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, desk, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L-1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_antre_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_antre_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_antre_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kiler_1: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kiler_2: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_kiler_3: Photorealistic interior photograph of a storage room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_1: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, dining table, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_2: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, dining table, kitchen counter, stove, chair, kitchen sink. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_mutfak_3: Photorealistic interior photograph of a kitchen in modern minimalist style. Light ceramic tile walls, polished concrete floor, chair, dining table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_1: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, bookshelf, TV unit. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_2: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, sofa, armchair, coffee table, TV unit. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_salon_3: Photorealistic interior photograph of a living room in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, sofa, armchair, coffee table. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_wc_1: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, toilet. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_wc_2: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_wc_3: Photorealistic interior photograph of a small toilet room in modern minimalist style. Light ceramic tile walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, dresser, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L0_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_balkon_1: Photorealistic interior photograph of a balcony in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_balkon_2: Photorealistic interior photograph of a balcony in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_balkon_3: Photorealistic interior photograph of a balcony in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_1: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_2: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_banyo_3: Photorealistic interior photograph of a bathroom in modern minimalist style. Light ceramic tile walls, polished concrete floor, shower, washbasin. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, desk, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, single bed, desk, nightstand, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_cocuk_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, wardrobe, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, nightstand, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, nightstand, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_ebeveyn_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed, nightstand. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_1: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair, dresser. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_2: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, chair. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_hol_3: Photorealistic interior photograph of a hallway in modern minimalist style. Charcoal grey plaster walls, polished concrete floor. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, wardrobe, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.
- cam_r_L1_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern minimalist style. Charcoal grey plaster walls, polished concrete floor, wardrobe, double bed. Cool daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens.

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
