# Polish report: real02 (run)

47 views, 88 attempts (88 polished now, 0 reused). Device NVIDIA RTX PRO 6000 Blackwell Workstation Edition, torch 2.9.1+cu128, diffusers 0.40.0; memory resident, peak VRAM 22.5 GiB, model load 2.8 s, prompt encoding 3.5 s, 1.4 s per forward, run 572 s.

Final images: 20 polished, 27 Cycles (gate 7, room 20). A polished image is used only when the change gate accepted it (and, later, the vision check does not reject it).

## Views

| camera | room | final | attempt | strength / control / scale / size / mode | gate | failed checks | seconds | panes |
|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.76 | 0 |
| cam_r_L-1_banyo_2 | r_L-1_banyo | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 0 |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.75 | 1 |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:f_L-1_065 0.215 (needs <= 0.14) | 1.78 | 0 |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.75 | 1 |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.71 | 1 |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.71 | 1 |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.73 | 0 |
| cam_r_L-1_salon_1 | r_L-1_salon | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 1 |
| cam_r_L-1_salon_2 | r_L-1_salon | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.77 | 1 |
| cam_r_L-1_salon_3 | r_L-1_salon | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.78 | 1 |
| cam_r_L0_banyo_1 | r_L0_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.73 | 0 |
| cam_r_L0_banyo_2 | r_L0_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.73 | 0 |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.8 | 0 |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.72 | 0 |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 1 |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 0 |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 0 |
| cam_r_L0_koridor_1 | r_L0_koridor | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.79 | 0 |
| cam_r_L0_koridor_2 | r_L0_koridor | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 0 |
| cam_r_L0_koridor_3 | r_L0_koridor | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.75 | 0 |
| cam_r_L0_oda_1 | r_L0_oda | polished | a3 | 0.125 / depth / 0.8 / native / plain | accept | - | 1.77 | 0 |
| cam_r_L0_oda_2 | r_L0_oda | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.7 | 0 |
| cam_r_L0_oda_2_1 | r_L0_oda_2 | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.7 | 0 |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 1 |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 0 |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 1 |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 3.45 | 0 |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.73 | 0 |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.68 | 0 |
| cam_r_L1_banyo_1 | r_L1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.68 | 0 |
| cam_r_L1_banyo_2 | r_L1_banyo | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.73 | 0 |
| cam_r_L1_koridor_1 | r_L1_koridor | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 0 |
| cam_r_L1_koridor_2 | r_L1_koridor | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 0 |
| cam_r_L1_koridor_2_1 | r_L1_koridor_2 | polished | a2 | 0.25 / canny / 0.8 / native / plain | accept | - | 3.52 | 0 |
| cam_r_L1_koridor_2_2 | r_L1_koridor_2 | cycles (gate) | - | 0.125 / depth / 0.8 / native / plain | reject | depth:global 0.0889 (needs <= 0.05) | 3.16 | 0 |
| cam_r_L1_koridor_2_3 | r_L1_koridor_2 | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 3.68 | 0 |
| cam_r_L1_koridor_3 | r_L1_koridor | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.77 | 0 |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 0 |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 1 |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cycles (room) | - | 0.125 / depth / 0.8 / native / plain | accept | - | 1.76 | 0 |
| cam_r_L1_teras_1 | r_L1_teras | polished | a1 | 0.375 / geometry / 0.8 / native / plain | accept | - | 5.08 | 1 |
| ext_1 | - | cycles (gate) | - | - | - | - | - | - |
| ext_2 | - | cycles (gate) | - | - | - | - | - | - |
| ext_3 | - | cycles (gate) | - | - | - | - | - | - |
| ext_4 | - | cycles (gate) | - | - | - | - | - | - |
| ext_5 | - | cycles (gate) | - | - | - | - | - | - |

## Room rule

Candidates of one room must have wall Lab means within ΔE 5; otherwise they take the strongest rung all of them accept (with agreeing walls) or the Cycles render.

| room | rule | rung | ΔE max | ΔE after | candidates |
|---|---|---|---|---|---|
| r_L-1_banyo | ok | - | 0.442 | - | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_koridor_2 | downgraded | cycles | 19 | - | cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_3 |
| r_L-1_mutfak | ok | - | 2.86 | - | cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3 |
| r_L-1_salon | downgraded | cycles | 15 | - | cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3 |
| r_L0_banyo | ok | - | 2.29 | - | cam_r_L0_banyo_1, cam_r_L0_banyo_2 |
| r_L0_e_banyo | ok | - | 1.26 | - | cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2 |
| r_L0_e_yatak_odasi | downgraded | cycles | 12.5 | - | cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3 |
| r_L0_koridor | downgraded | cycles | 11.9 | - | cam_r_L0_koridor_1, cam_r_L0_koridor_2, cam_r_L0_koridor_3 |
| r_L0_oda | ok | - | 2.83 | - | cam_r_L0_oda_1, cam_r_L0_oda_2 |
| r_L0_oda_2 | ok | - | - | - | cam_r_L0_oda_2_1 |
| r_L0_yatak_odasi | downgraded | cycles | 7.13 | - | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L0_yatak_odasi_3 | ok | - | 3.59 | - | cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3 |
| r_L1_banyo | ok | - | 3.58 | - | cam_r_L1_banyo_1, cam_r_L1_banyo_2 |
| r_L1_koridor | downgraded | cycles | 5.22 | - | cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_3 |
| r_L1_koridor_2 | ok | - | 1.21 | - | cam_r_L1_koridor_2_1, cam_r_L1_koridor_2_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | downgraded | cycles | 5.66 | - | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |
| r_L1_teras | ok | - | - | - | cam_r_L1_teras_1 |

## Attempts

| camera | k | role | strength / control / scale / size / mode | seed | sigma0 | forwards | seconds | decision | failed checks | reused |
|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.76 | accept | - | - |
| cam_r_L-1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.66 | reject | depth:f_L-1_020 0.231 (needs <= 0.14) | - |
| cam_r_L-1_banyo_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.73 | reject | depth:f_L-1_020 0.159 (needs <= 0.14) | - |
| cam_r_L-1_banyo_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L-1_koridor_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.68 | reject | edges:f_L-1_044 0.805 (needs >= 0.87) | - |
| cam_r_L-1_koridor_2_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.75 | accept | - | - |
| cam_r_L-1_koridor_2_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.75 | accept | - | - |
| cam_r_L-1_koridor_2_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.69 | reject | depth:f_L-1_065 0.334 (needs <= 0.14) | - |
| cam_r_L-1_koridor_2_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.75 | reject | depth:f_L-1_065 0.325 (needs <= 0.14) | - |
| cam_r_L-1_koridor_2_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | reject | depth:f_L-1_065 0.215 (needs <= 0.14) | - |
| cam_r_L-1_koridor_2_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.7 | reject | edges:win_L-1_001 0.866 (needs >= 0.87); edges:f_L-1_017 0.804 (needs >= 0.87); edges:f_L-1_027 0.788 (needs >= 0.87) | - |
| cam_r_L-1_koridor_2_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L-1_koridor_2_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.75 | accept | - | - |
| cam_r_L-1_mutfak_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.71 | accept | - | - |
| cam_r_L-1_mutfak_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.71 | accept | - | - |
| cam_r_L-1_mutfak_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | accept | - | - |
| cam_r_L-1_salon_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | accept | - | - |
| cam_r_L-1_salon_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L-1_salon_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | reject | edges:f_L-1_058 0.429 (needs >= 0.87) | - |
| cam_r_L-1_salon_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L-1_salon_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.77 | accept | - | - |
| cam_r_L-1_salon_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | reject | edges:f_L-1_063 0.771 (needs >= 0.87); neutral:struct:walls 2.16 (needs <= 2) | - |
| cam_r_L-1_salon_3 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | reject | edges:f_L-1_063 0.866 (needs >= 0.87) | - |
| cam_r_L-1_salon_3 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.78 | accept | - | - |
| cam_r_L0_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | accept | - | - |
| cam_r_L0_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | accept | - | - |
| cam_r_L0_e_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.8 | accept | - | - |
| cam_r_L0_e_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | accept | - | - |
| cam_r_L0_e_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.76 | accept | - | - |
| cam_r_L0_e_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.74 | accept | - | - |
| cam_r_L0_e_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L0_e_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 5.46 | accept | - | - |
| cam_r_L0_e_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.74 | accept | - | - |
| cam_r_L0_e_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L0_e_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 5.54 | accept | - | - |
| cam_r_L0_e_yatak_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.77 | accept | - | - |
| cam_r_L0_e_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L0_koridor_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.7 | reject | depth:f_L0_038 0.236 (needs <= 0.14) | - |
| cam_r_L0_koridor_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.94 | reject | depth:global 0.0539 (needs <= 0.05) | - |
| cam_r_L0_koridor_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.79 | accept | - | - |
| cam_r_L0_koridor_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.71 | accept | - | - |
| cam_r_L0_koridor_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L0_koridor_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.69 | accept | - | - |
| cam_r_L0_koridor_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.75 | accept | - | - |
| cam_r_L0_oda_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 5.15 | reject | depth:f_L0_001 0.173 (needs <= 0.14) | - |
| cam_r_L0_oda_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | reject | depth:f_L0_001 0.183 (needs <= 0.14) | - |
| cam_r_L0_oda_1 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.77 | accept | - | - |
| cam_r_L0_oda_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.7 | accept | - | - |
| cam_r_L0_oda_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.7 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.7 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.73 | accept | - | - |
| cam_r_L0_yatak_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.72 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.74 | accept | - | - |
| cam_r_L0_yatak_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.67 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.74 | accept | - | - |
| cam_r_L0_yatak_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L0_yatak_odasi_3_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.24 | reject | edges:d_L0_006 0.846 (needs >= 0.87) | - |
| cam_r_L0_yatak_odasi_3_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.45 | accept | - | - |
| cam_r_L0_yatak_odasi_3_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | accept | - | - |
| cam_r_L0_yatak_odasi_3_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.68 | accept | - | - |
| cam_r_L1_banyo_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.68 | accept | - | - |
| cam_r_L1_banyo_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.73 | accept | - | - |
| cam_r_L1_koridor_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.69 | accept | - | - |
| cam_r_L1_koridor_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.74 | accept | - | - |
| cam_r_L1_koridor_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L1_koridor_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.69 | reject | masks:f_L0_001 0.567 (needs >= 0.62) | - |
| cam_r_L1_koridor_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.76 | accept | - | - |
| cam_r_L1_koridor_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L1_koridor_2_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.62 | reject | neutral:struct:ceiling 2.05 (needs <= 2) | - |
| cam_r_L1_koridor_2_1 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 3.52 | accept | - | - |
| cam_r_L1_koridor_2_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 4.99 | reject | depth:global 0.069 (needs <= 0.05) | - |
| cam_r_L1_koridor_2_2 | a2 | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 4.84 | reject | depth:global 0.103 (needs <= 0.05) | - |
| cam_r_L1_koridor_2_2 | a3 | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 3.16 | reject | depth:global 0.0889 (needs <= 0.05) | - |
| cam_r_L1_koridor_2_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.68 | accept | - | - |
| cam_r_L1_koridor_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.68 | accept | - | - |
| cam_r_L1_koridor_3 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.74 | accept | - | - |
| cam_r_L1_koridor_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.77 | accept | - | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.68 | accept | - | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.74 | accept | - | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 3.67 | accept | - | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | a2 (room rule) | ladder | 0.25 / canny / 0.8 / native / plain | 2 | 0.5 | 2 | 2.74 | reject | masks:f_L1_015 0.225 (needs >= 0.62) | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 5.06 | accept | - | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | a3 (room rule) | ladder | 0.125 / depth / 0.8 / native / plain | 3 | 0.3 | 1 | 1.76 | accept | - | - |
| cam_r_L1_teras_1 | a1 | ladder | 0.375 / geometry / 0.8 / native / plain | 1 | 0.643 | 3 | 5.08 | accept | - | - |

## Notes

- cam_r_L-1_koridor_2_1: room rule ran a3
- cam_r_L-1_koridor_2_1: room rule: wall ΔE 19.041 > 5.0 in r_L-1_koridor_2; a2 -> cycles
- cam_r_L-1_koridor_2_3: room rule ran a3
- cam_r_L-1_koridor_2_3: room rule: wall ΔE 19.041 > 5.0 in r_L-1_koridor_2; a2 -> cycles
- cam_r_L-1_salon_1: room rule ran a3
- cam_r_L-1_salon_1: room rule: wall ΔE 14.951 > 5.0 in r_L-1_salon; a1 -> cycles
- cam_r_L-1_salon_2: room rule ran a3
- cam_r_L-1_salon_2: room rule: wall ΔE 14.951 > 5.0 in r_L-1_salon; a2 -> cycles
- cam_r_L-1_salon_3: room rule: wall ΔE 14.951 > 5.0 in r_L-1_salon; a3 -> cycles
- cam_r_L0_e_yatak_odasi_1: room rule ran a2
- cam_r_L0_e_yatak_odasi_1: room rule ran a3
- cam_r_L0_e_yatak_odasi_1: room rule: wall ΔE 12.5 > 5.0 in r_L0_e_yatak_odasi; a1 -> cycles
- cam_r_L0_e_yatak_odasi_2: room rule ran a2
- cam_r_L0_e_yatak_odasi_2: room rule ran a3
- cam_r_L0_e_yatak_odasi_2: room rule: wall ΔE 12.5 > 5.0 in r_L0_e_yatak_odasi; a1 -> cycles
- cam_r_L0_e_yatak_odasi_3: room rule ran a2
- cam_r_L0_e_yatak_odasi_3: room rule ran a3
- cam_r_L0_e_yatak_odasi_3: room rule: wall ΔE 12.5 > 5.0 in r_L0_e_yatak_odasi; a1 -> cycles
- cam_r_L0_koridor_1: room rule: wall ΔE 11.898 > 5.0 in r_L0_koridor; a3 -> cycles
- cam_r_L0_koridor_2: room rule ran a3
- cam_r_L0_koridor_2: room rule: wall ΔE 11.898 > 5.0 in r_L0_koridor; a1 -> cycles
- cam_r_L0_koridor_3: room rule ran a3
- cam_r_L0_koridor_3: room rule: wall ΔE 11.898 > 5.0 in r_L0_koridor; a1 -> cycles
- cam_r_L0_yatak_odasi_1: room rule ran a2
- cam_r_L0_yatak_odasi_1: room rule ran a3
- cam_r_L0_yatak_odasi_1: room rule: wall ΔE 7.126 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L0_yatak_odasi_2: room rule ran a2
- cam_r_L0_yatak_odasi_2: room rule ran a3
- cam_r_L0_yatak_odasi_2: room rule: wall ΔE 7.126 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L0_yatak_odasi_3: room rule ran a2
- cam_r_L0_yatak_odasi_3: room rule ran a3
- cam_r_L0_yatak_odasi_3: room rule: wall ΔE 7.126 > 5.0 in r_L0_yatak_odasi; a1 -> cycles
- cam_r_L1_koridor_1: room rule ran a2
- cam_r_L1_koridor_1: room rule ran a3
- cam_r_L1_koridor_1: room rule: wall ΔE 5.219 > 5.0 in r_L1_koridor; a1 -> cycles
- cam_r_L1_koridor_2: room rule ran a3
- cam_r_L1_koridor_2: room rule: wall ΔE 5.219 > 5.0 in r_L1_koridor; a2 -> cycles
- cam_r_L1_koridor_3: room rule ran a2
- cam_r_L1_koridor_3: room rule ran a3
- cam_r_L1_koridor_3: room rule: wall ΔE 5.219 > 5.0 in r_L1_koridor; a1 -> cycles
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: room rule ran a2
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: room rule ran a3
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: room rule: wall ΔE 5.655 > 5.0 in r_L1_oyun_aktivite_ve_dinlenme_odasi; a1 -> cycles
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room rule ran a2
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room rule ran a3
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room rule: wall ΔE 5.655 > 5.0 in r_L1_oyun_aktivite_ve_dinlenme_odasi; a1 -> cycles
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: room rule ran a3
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: room rule: wall ΔE 5.655 > 5.0 in r_L1_oyun_aktivite_ve_dinlenme_odasi; a1 -> cycles
- ext_1: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_2: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_3: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_4: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_5: exterior gate polish_disabled: the exterior views keep the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)

## Prompts

- cam_r_L-1_banyo_1: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor, washbasin, toilet, bathtub. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1_banyo_2: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor, washbasin, toilet, bathtub. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L-1_koridor_2_1: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_koridor_2_2: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_koridor_2_3: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, console table, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_mutfak_1: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor, fridge. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_mutfak_2: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_mutfak_3: Photorealistic interior photograph of a kitchen in modern style. Light ceramic tile walls, light ceramic tile floor. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_salon_1: Photorealistic interior photograph of a living room in modern style. Warm greige smooth painted walls, light oak wood floor, sofa, corner sofa, floor lamp. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_salon_2: Photorealistic interior photograph of a living room in modern style. Warm greige smooth painted walls, light oak wood floor, corner sofa, sofa, chair, floor lamp, sideboard, ottoman, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L-1_salon_3: Photorealistic interior photograph of a living room in modern style. Warm greige smooth painted walls, light oak wood floor, corner sofa, wardrobe, sofa, floor lamp, sideboard, chair, ottoman. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_banyo_1: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor, washbasin, toilet, bathtub. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_banyo_2: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor, washbasin, toilet, bathtub. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_e_banyo_1: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor, toilet, washbasin. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_e_banyo_2: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor, washbasin, toilet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_e_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern style. Warm greige smooth painted walls, light oak wood floor, double bed, wardrobe, bench, floor lamp, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_e_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern style. Warm greige smooth painted walls, light oak wood floor, double bed, wardrobe, floor lamp. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_e_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern style. Warm greige smooth painted walls, light oak wood floor, double bed, wardrobe, floor lamp, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_koridor_1: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, shoe cabinet, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_koridor_2: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, console table, shoe cabinet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_koridor_3: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, shoe cabinet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_oda_1: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_oda_2: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_oda_2_1: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L0_yatak_odasi_1: Photorealistic interior photograph of a bedroom in modern style. Warm greige smooth painted walls, light oak wood floor, double bed, bench. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_2: Photorealistic interior photograph of a bedroom in modern style. Warm greige smooth painted walls, light oak wood floor, wardrobe. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_3: Photorealistic interior photograph of a bedroom in modern style. Warm greige smooth painted walls, light oak wood floor, double bed, bench. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_3_1: Photorealistic interior photograph of a bedroom in modern style. Warm greige smooth painted walls, light oak wood floor, double bed, wardrobe. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_3_2: Photorealistic interior photograph of a bedroom in modern style. Warm greige smooth painted walls, light oak wood floor, wardrobe, double bed. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L0_yatak_odasi_3_3: Photorealistic interior photograph of a bedroom in modern style. Warm greige smooth painted walls, light oak wood floor, double bed, nightstand. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_banyo_1: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor, washbasin, toilet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_banyo_2: Photorealistic interior photograph of a bathroom in modern style. Light ceramic tile walls, light ceramic tile floor, bathtub, washbasin, toilet. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- cam_r_L1_koridor_1: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_koridor_2: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_koridor_2_1: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, console table, bench. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_koridor_2_2: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, staircase, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_koridor_2_3: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, console table, bench. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_koridor_3: Photorealistic interior photograph of a hallway in modern style. Warm greige smooth painted walls, light oak wood floor, console table. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: Photorealistic interior photograph of a room in modern style. Warm greige smooth painted walls, light oak wood floor, bookshelf, sofa. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: Photorealistic interior photograph of a room in modern style. Warm greige smooth painted walls, light oak wood floor, sofa, armchair, chair. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: Photorealistic interior photograph of a room in modern style. Warm greige smooth painted walls, light oak wood floor, bookshelf. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 18 mm lens.
- cam_r_L1_teras_1: Photorealistic interior photograph of a balcony in modern style. Warm greige smooth painted walls, light oak wood floor. Warm daytime light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 16 mm lens.
- ext_1: Photorealistic architectural photograph of a house exterior in modern style, seen from a corner of the plot at eye level, two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 32.46 mm lens.
- ext_2: Photorealistic architectural photograph of a house exterior in modern style, seen from a corner of the plot at eye level, two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 32.46 mm lens.
- ext_3: Photorealistic architectural photograph of a house exterior in modern style, seen from a corner of the plot at eye level, two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 32.46 mm lens.
- ext_4: Photorealistic architectural photograph of a house exterior in modern style, seen from a corner of the plot at eye level, two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 32.46 mm lens.
- ext_5: Photorealistic architectural photograph of a house exterior in modern style, seen in a three-quarter aerial view from above, roof and two facades in view. Warm greige smooth rendered facade, anthracite concrete tile roof, dark bronze window frames. Light oak wood front door, grey concrete paver paving, lawn garden. Warm daytime sunlight under a clear sky, soft natural shadows, realistic materials and textures, sharp focus, 28.54 mm lens.

## Models

| role | repo | revision | licence | files |
|---|---|---|---|---|
| polish base | Tongyi-MAI/Z-Image-Turbo | `f332072aa78b` | Apache-2.0 | model_index.json, scheduler/*, text_encoder/*, tokenizer/*, transformer/*, vae/* |
| polish controlnet | alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1 | `5155fc56d178` | Apache-2.0 | Z-Image-Turbo-Fun-Controlnet-Union-2.1-2602-8steps.safetensors |
| gate depth | depth-anything/Depth-Anything-V2-Small-hf | `5426e4f0f365` | Apache-2.0 | - |
| gate dino | facebook/dinov2-base | `f9e44c814b77` | Apache-2.0 | - |
| gate sam | facebook/sam2.1-hiera-large | `665f8e2ad61c` | Apache-2.0 | - |

## Warnings

- exterior gate polish_disabled: 5 exterior views keep the Cycles render
