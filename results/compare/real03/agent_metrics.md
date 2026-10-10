# Agent metrics across runs: real03

One row per orchestrated run (docs/milestone12.md §5.5); written by `python -m wenart.agent metrics`.

| run | model | rounds | edits accepted / rejected | accepted % | rooms visited / fixable | critical before -> after | major before -> after | agent min | calls | tokens (k) | first accepted edit (s) | repeats refused | dry runs | top rejection reasons |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| M11 run 3 (oesbppzw7hsnmb, 10 Oct 2026) | Qwen/Qwen3.8-27B-FP8 | 2 | 5 / 73 | 6 | 11 / 35 | 18 -> 17 | 186 -> 176 | 10.75 | 144 | 1220.0 | 91.0 | 0 | 0 | drawn_lock 39, max_tries 8, product_size 8 |
