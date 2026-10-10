# Decor: real03

AI decor (docs/milestone9.md §4): 14 items chosen by the AI (model Qwen/Qwen3-VL-8B-Instruct, both passes agreeing, confidence 0.9) in 5 rooms; 0 items by the rules (M4/M8) in 0 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Rüzgarlık (r_L0_ruzgarlik) | other | 7 | 4 / 4 | 3 | plant, table_lamp | plant (the corner is no longer free next to the other plant) | - |
| Kat Holü (r_L0_kat_holu) | hall | 5 | 3 / 3 | 2 | plant_large, vase | - | - |
| Güvenlik Holü (r_L0_guvenlik_holu) | hall | 6 | 4 / 3 | 2 | mirror, plant_small | - | - |
| Yangın Merdiveni (r_L0_yangin_merdiveni) | other | 8 | 5 / 5 | 5 | cushion, pendant_light, plant_large, plant_large, plant_small | - | - |
| Kat Merdiveni (r_L0_kat_merdiveni) | other | 8 | 5 / 5 | 3 | cushion, plant_large, plant_large | - | - |

Items only one pass chose (not built):

- r_L0_ruzgarlik: pendant_light in ceiling:centre_r_L0_ruzgarlik (pass 1)
- r_L0_ruzgarlik: wall_art in f_L0_004.wall (pass 2)
- r_L0_kat_holu: pendant_light in ceiling:centre_r_L0_kat_holu (pass 1)
- r_L0_kat_holu: ceiling_light in ceiling:centre_r_L0_kat_holu (pass 2)
- r_L0_guvenlik_holu: pendant_light in ceiling:centre_r_L0_guvenlik_holu (pass 1)
- r_L0_guvenlik_holu: vase in f_L0_007.centre (pass 1)
- r_L0_guvenlik_holu: ceiling_light in ceiling:centre_r_L0_guvenlik_holu (pass 2)
- r_L0_kat_merdiveni: pendant_light in ceiling:over_f_L0_017 (pass 1)
- r_L0_kat_merdiveni: rug in r_L0_kat_merdiveni.rug1 (pass 1)
- r_L0_kat_merdiveni: pendant_light in ceiling:centre_r_L0_kat_merdiveni (pass 2)
- r_L0_kat_merdiveni: plant_small in f_L0_017.centre (pass 2)

Places left out:

- r_L0_kat_holu: f_L0_010 wall: mirror: f_L0_010 has no wall behind it; wall_art: f_L0_010 has no wall behind it
- r_L0_guvenlik_holu: no free corner for a floor plant
