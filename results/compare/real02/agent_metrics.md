# Agent metrics across runs: real02

One row per orchestrated run (docs/milestone12.md §5.5); written by `python -m wenart.agent metrics`.

| run | model | rounds | edits accepted / rejected | accepted % | rooms visited / fixable | critical before -> after | major before -> after | agent min | calls | tokens (k) | first accepted edit (s) | repeats refused | dry runs | top rejection reasons |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M11 G2d (rx88jd2u31clb6, 10 Oct 2026) | Qwen/Qwen3.8-27B-FP8 | 4 | 20 / 177 | 10 | 10 / 32 | 6 -> 6 | 120 -> 117 | 32.75 | 312 | 3003.8 | 60.0 | 0 | 0 | drawn_lock 83, product_size 21, snap 20 |
