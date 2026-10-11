# Milestone 12 P1: agent model bake-off

Tasks: T1 plan-crop typing (40), T2 planted layout errors (30 rooms), T3 best of 3 layouts (20), T4 decor and wrong objects in renders (20), T5 plan + tool calls on room briefs (20). T1-T4 = the mean of the four accuracies (points).

| model | variant | GPUs | T1 % | T2 % | T3 % | T4 % | T1-T4 | T2 false | T4 false | T5 % | T5 valid | T5 allowed | T5 in plan | answered | s/call | tokens/call | VRAM peak MiB | Cycles rc |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bf16 | off | 1 | 47.5 | 10.6 | 35.0 | 70.0 | 40.8 | 61 | 0 | 100.0 | 1.0 | 1.0 | 1.0 | 1.0 | 4.88 | 69.5 | 71033 |  |
| bf16 | on | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 10.0 | 1.0 | 1.0 | 0.0 | 0.077 | 380.65 | 5758.0 | 71592 |  |
| flash_next | off | 2 | 57.5 | 27.2 | 35.0 | 65.0 | 46.2 | 48 | 0 | 100.0 | 1.0 | 1.0 | 1.0 | 1.0 | 2.81 | 103.8 | 84913 |  |
| flash_next | on | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 90.0 | 1.0 | 1.0 | 0.0 | 0.146 | 98.41 | 4355.8 | 85472 |  |
| fp8 | off | 1 | 50.0 | 12.2 | 35.0 | 65.0 | 40.6 | 52 | 0 | 100.0 | 1.0 | 1.0 | 1.0 | 1.0 | 3.18 | 67.7 | 73697 |  |
| fp8 | on | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 15.0 | 1.0 | 1.0 | 0.0 | 0.131 | 243.49 | 5809.1 | 74011 |  |
| muse | high | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0 | 0 | 80.0 | 1.0 | 1.0 | 0.0 | 0.131 | 227.76 | 2834.6 | 74011 |  |
| muse | low | 1 | 15.0 | 0.0 | 0.0 | 65.0 | 20.0 | 0 | 0 | 95.0 | 1.0 | 1.0 | 0.0 | 0.362 | 49.67 | 622.3 | 74258 |  |

Rule: 2-GPU only when >= 10 points better on T1-T4; answered >= 90%, T5 valid calls >= 80%.

**Pick: fp8 off (Qwen/Qwen3.8-27B-FP8, 40.6 points)** - the best 2-GPU model (flash_next off, 46.2) is less than 10 points above the best single-GPU model (40.6).
