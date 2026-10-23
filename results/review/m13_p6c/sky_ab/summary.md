# Milestone 13 interior sky A/B, view set 'skywin' (scripts/jobs/m13_p6.sh)

The interior world (the HDRI that lights the interior views) raised by 2^stops; the exterior world, the sun, the rig and every other lever as in production. Pull k = the window pull in stops; panes p50 / p90 after it (display values, 1.0 = white); day green = the view's daylight G/sqrt(RB); tint = the gain on the white point's G.

A windows-only level (skywin*) raises the world only on the camera's paths (through the panes, in sharp reflections): its world strength is the room's, with the strength the camera sees in brackets.

| Project | Variant | View | World strength | Stops | EV used | EV metered | Pull k | Panes p50 / p90 | WB K (view / project) | Day green | Tint | Seconds |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| real02 | base | cam_r_L-1_salon_1 | 1.0 | 0.0 | -0.5 | -0.4223 | 0 | - / - | 5605.6 / 5611.6 | 0.975632 | 0.987746 | 6.89 |
| real02 | base | cam_r_L-1_mutfak_1 | 1.0 | 0.0 | 1.333333 | 1.3709 | 2 | 0.642 / 0.8987 | 3202.8 / 5611.6 | 1.005005 | 1.001493 | 7.46 |
| real02 | base | cam_r_L0_yatak_odasi_1 | 1.0 | 0.0 | -0.666667 | -0.6384 | 0 | - / - | 5514.4 / 5611.6 | 1.004108 | 1.006245 | 6.35 |
| real02 | base | cam_r_L0_e_yatak_odasi_3 | 1.0 | 0.0 | 3.0 | 3.1052 | 3 | 0.633 / 0.9237 | 5638.0 / 5611.6 | 1.08302 | 1.057117 | 6.94 |
| real02 | base | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | 1.0 | 0.0 | 0.166667 | 0.1614 | 1 | 0.5569 / 0.8879 | 5615.0 / 5611.6 | 1.004988 | 1.006964 | 6.95 |
| real02 | base | cam_r_L-1_koridor_2_1 | 1.0 | 0.0 | 1.5 | 1.4283 | 1 | 0.6647 / 0.6779 | 5234.5 / 5611.6 | 0.974923 | 0.990213 | 7.08 |
| real02 | skywin35 | cam_r_L-1_salon_1 | 1.0 (camera paths 11.313708) | 3.5 | -0.5 | -0.4223 | 0 | - / - | 5605.7 / 5611.7 | 0.975632 | 0.987794 | 6.95 |
| real02 | skywin35 | cam_r_L-1_mutfak_1 | 1.0 (camera paths 11.313708) | 3.5 | 1.333333 | 1.3709 | 2 | 0.642 / 0.8987 | 3202.8 / 5611.7 | 1.005005 | 1.001503 | 7.62 |
| real02 | skywin35 | cam_r_L0_yatak_odasi_1 | 1.0 (camera paths 11.313708) | 3.5 | -0.666667 | -0.6384 | 1 | 0.7987 / 0.8376 | 5514.4 / 5611.7 | 1.004108 | 1.006293 | 6.45 |
| real02 | skywin35 | cam_r_L0_e_yatak_odasi_3 | 1.0 (camera paths 11.313708) | 3.5 | 3.0 | 3.1052 | 5 | 0.736 / 0.8012 | 5638.1 / 5611.7 | 1.08302 | 1.057169 | 7.13 |
| real02 | skywin35 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | 1.0 (camera paths 11.313708) | 3.5 | 0.166667 | 0.1614 | 2 | 0.7935 / 0.8226 | 5615.1 / 5611.7 | 1.004988 | 1.007013 | 6.8 |
| real02 | skywin35 | cam_r_L-1_koridor_2_1 | 1.0 (camera paths 11.313708) | 3.5 | 1.5 | 1.4283 | 1 | 0.6647 / 0.6779 | 5234.6 / 5611.7 | 0.974923 | 0.990249 | 7.01 |
| real02 | sky35 | cam_r_L-1_salon_1 | 11.313708498984761 | 3.5 | -0.5 | -0.5028 | 1 | 0.4443 / 0.4678 | 5752.8 / 5757.0 | 0.966246 | 0.987601 | 7.11 |
| real02 | sky35 | cam_r_L-1_mutfak_1 | 11.313708498984761 | 3.5 | 1.333333 | 1.301 | 3 | 0.5401 / 0.8181 | 3262.5 / 5757.0 | 0.964923 | 0.996659 | 7.55 |
| real02 | sky35 | cam_r_L0_yatak_odasi_1 | 11.313708498984761 | 3.5 | -0.666667 | -0.6707 | 1 | 0.7987 / 0.8376 | 5657.5 / 5757.0 | 1.001289 | 1.010502 | 6.41 |
| real02 | sky35 | cam_r_L0_e_yatak_odasi_3 | 11.313708498984761 | 3.5 | 2.5 | 2.5644 | 4 | 0.7849 / 0.841 | 5767.5 / 5757.0 | 1.033868 | 1.031993 | 6.9 |
| real02 | sky35 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | 11.313708498984761 | 3.5 | 0.0 | 0.063 | 2 | 0.7786 / 0.809 | 5759.1 / 5757.0 | 0.994369 | 1.006191 | 6.85 |
| real02 | sky35 | cam_r_L-1_koridor_2_1 | 11.313708498984761 | 3.5 | 1.5 | 1.4561 | 1 | 0.7213 / 0.7334 | 5326.6 / 5757.0 | 0.969012 | 0.991848 | 6.93 |
