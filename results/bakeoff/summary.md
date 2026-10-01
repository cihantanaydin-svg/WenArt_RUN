# Recognition bake-off summary

Pages: 3 (synthetic scans and photos). IoU threshold 0.5 for symbols; texts compared after normalisation (case-insensitive, decimal comma -> dot).

## OCR engines

| Engine | Pages | Texts recall | Texts precision | Room labels recall | Room labels precision | Mean latency |
|---|---|---|---|---|---|---|
| paddleocr | 3 | 65 % | 63 % | 73 % | 27 % | 18.52 s |
| tesseract | 3 | 48 % | 35 % | 20 % | 6 % | 0.39 s |

## Vision-language models

Symbols (tiled): the symbol task on the drawing area cut into full-resolution tiles (`--tiled`, wenart/recognition/tiles.py); `-` when that pass was not run.

| Model | Pages | Page class | Level label | Scale text | Room labels R / P | Symbols R / P | Symbols (tiled) R / P | Mean latency / call | Errors |
|---|---|---|---|---|---|---|---|---|---|
| Qwen/Qwen3-VL-8B-Instruct | 3 | 100 % | 100 % | 100 % | 100 % / 100 % | 0 % / 0 % | 0 % / 0 % (3 p, 75.08 s / page) | 5.08 s | 1 |
| zai-org/GLM-4.6V-Flash | 3 | 100 % | 100 % | 100 % | 100 % / 100 % | 1 % / 3 % | 4 % / 10 % (3 p, 9.53 s / page) | 5.59 s | 0 |

## Symbols per type (recall / precision)

| Type | Qwen/Qwen3-VL-8B-Instruct | zai-org/GLM-4.6V-Flash |
|---|---|---|
| armchair | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| bathtub | - | 0 % / 0 % (n=0) |
| bed_double | 0 % / 0 % (n=2) | 50 % / 100 % (n=2) |
| bookshelf | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| chair | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| desk | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| door | 0 % / 0 % (n=14) | 0 % / 0 % (n=14) |
| fridge | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| kitchen_counter | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| kitchen_island | - | 0 % / 0 % (n=0) |
| nightstand | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| shower | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| sink_kitchen | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| sofa | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| stove | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| table_coffee | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| table_dining | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| toilet | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| tv_unit | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| unknown | 0 % / 0 % (n=0) | 0 % / 0 % (n=0) |
| wardrobe | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| washbasin | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| washing_machine | 0 % / 0 % (n=2) | 0 % / 0 % (n=2) |
| window | 0 % / 0 % (n=16) | 0 % / 0 % (n=16) |

## Two-pass agreement

| Set | Symbols | Recall | Precision |
|---|---|---|---|
| verified (both models agree) | 0 | 0 % | 0 % |
| all proposals (verified + unverified) | 71 | 1 % | 1 % |

## Per page

| Project | File | Kind | Who | Room labels R / P | Symbols R / P | Symbols (tiled) R / P | Page class | Latency |
|---|---|---|---|---|---|---|---|---|
| synthetic-01 | 1_kat_scan.png | scan | paddleocr | 100 % / 36 % | - | - | - | 54.67 s |
| synthetic-01 | 1_kat_scan.png | scan | tesseract | 40 % / 13 % | - | - | - | 0.36 s |
| synthetic-01 | 1_kat_scan.png | scan | Qwen/Qwen3-VL-8B-Instruct | 100 % / 100 % | 0 % / 0 % | 0 % / 0 % (1 tiles) | floor_plan (ok) | 14.1 s |
| synthetic-01 | 1_kat_scan.png | scan | zai-org/GLM-4.6V-Flash | 100 % / 100 % | 0 % / 0 % | 0 % / 0 % (1 tiles) | floor_plan (ok) | 18.5 s |
| synthetic-02 | plan_scan.png | scan | paddleocr | 60 % / 23 % | - | - | - | 0.44 s |
| synthetic-02 | plan_scan.png | scan | tesseract | 0 % / 0 % | - | - | - | 0.41 s |
| synthetic-02 | plan_scan.png | scan | Qwen/Qwen3-VL-8B-Instruct | 100 % / 100 % | 0 % / 0 % | 0 % / 0 % (1 tiles) | floor_plan (ok) | 24.4 s |
| synthetic-02 | plan_scan.png | scan | zai-org/GLM-4.6V-Flash | 100 % / 100 % | 3 % / 8 % | 7 % / 18 % (1 tiles) | floor_plan (ok) | 27.1 s |
| synthetic-02 | plan_photo.jpg | photo | paddleocr | 60 % / 21 % | - | - | - | 0.45 s |
| synthetic-02 | plan_photo.jpg | photo | tesseract | 20 % / 6 % | - | - | - | 0.39 s |
| synthetic-02 | plan_photo.jpg | photo | Qwen/Qwen3-VL-8B-Instruct | 100 % / 100 % | 0 % / 0 % | 0 % / 0 % (1 tiles) | floor_plan (ok) | 232.4 s |
| synthetic-02 | plan_photo.jpg | photo | zai-org/GLM-4.6V-Flash | 100 % / 100 % | 0 % / 0 % | 3 % / 9 % (1 tiles) | floor_plan (ok) | 33.3 s |
