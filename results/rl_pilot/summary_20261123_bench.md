# RL try 2 (bench data), 23 Nov 2026 (user: "continue")

One variable changed against pilot 1: the training questions come from the dataset bench (real Swiss buildings read by
our own CPU reader at 039f0b8e, truth = the converter's exact geometry) instead of our synthetic plans. Pilot 1's recipe
kept: 8 samples at temperature 0.8 from the FP8 agent model, rejection sampling, rank-16 LoRA on the BF16 base, served
beside it by vLLM 0.30.0 with the same flags and revisions. CPU side wenart/reading_check/rl_bench.py, job
scripts/jobs/rl_bench.sh, set results/rl_bench/set/, results results/rl_bench/pod1/.

## Training set
Close-ups of our reader's bench readings (is this wall / door / window / room of the model right, is a drawn wall /
opening / room missing), the answer from the truth; two images each (drawing, architect-style model, red ring). Split
by building: 53 / 53, none in both. Training: 412 questions from 49 buildings (206 reader errors; walls 42, openings
210, rooms 160). Held out: 246 from 46 buildings (123 errors; walls 50, openings 116, rooms 80). Rejection sampling
(FP8 70.9 % right): 192 all right, 43 all wrong, 177 mixed -> 176 rows (95 of them a reader error). Stairs left out:
draw_arch draws a stair with details.stair but no flights as an empty box (open point).

## Arms (pod c06ymmikyhzz13, same calls, drawing text on, no few-shot; false findings on the user's 25 marks)
| arm | known errors (of 73) | false, all marks | false, fold 0 | right findings | judge (of 62) | failed calls | held-out right (of 246) | errors flagged (of 123) | false alarms (of 123) |
|---|---|---|---|---|---|---|---|---|---|
| (a) FP8 (default) | 65 | 16 | 11 | 104 | 53 | 0 | 174 | 71 | 17 |
| (b) BF16 base | 65 | 16 | 11 | 101 | 52 | 0 | 175 | 68 | 13 |
| (c) BF16 + bench LoRA | 63 | 12 | 10 | 71 | 46 | 18 | 198 | 101 | 24 |

## Ship rule (UL359, UL360): not passed
(c) finds fewer known errors than (a) and (b), none they miss (it misses real09-B07 and real10-B33); 18 of its 91
compare calls broke (whitespace after {"answers":), the judge falls 52 -> 46. The default stays FP8 + drawing text.

## Reading
The bench signal is learnable (held out: 71.1 -> 80.5 %, gains in openings and missing walls, none in rooms) but does
not carry to the RC15 calls. Two tries agree: a LoRA on short close-up answers improves its own format and harms the
exam's long structured calls. Caveat: 28 of 44 training steps (time guard; the pod's own setup took 8 min).

## Pod
c06ymmikyhzz13, RTX PRO 6000, 76 min, $3.42 (setup 5, phase A 15, training 20, phase C 28 min). A first launch found no
stock and created no pod.
