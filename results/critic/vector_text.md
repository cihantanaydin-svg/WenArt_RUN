# RC15 with the drawing's vector data as text: offline measure and pod plan (21 Nov 2026)

Milestone 14 queue item 3. The AI checks (inventory, compare, plausibility, second look) saw only rendered crops; round
2 found 71 of the known errors. Now each question can carry a short text of the drawing file's own items and the
reading's, in metres in the image's frame, with the same ids drawn on the images. Off by default
(`CRITIC_VECTOR_TEXT=0`) until a pod has measured it. No pod was started.

## What was built

| part | where |
|---|---|
| serializer: drawing items (wall line pairs with thickness, arcs / door swings, window symbols, stair lines, room labels with their area, area texts, size tags, dimensions, level marks, other texts) and reading items (rooms with label, type, area, size; doors, windows, openings with width and the spaces they join; walls exterior / inferred; stairs, lifts), frame = metres from the image's top-left corner, y down, so rotated and mirrored page transforms land on the drawn lines | `wenart/reading_check/vector_text.py` |
| token cap per question: 2400, and never more than the 16384 context less images, prompt and answer; tokens by a rule fitted on round 2's own server counts (never under, mean +10 %; chars / 3.5 was under on all 56 text calls, by 25 %) | `vector_text.cap_for`, `estimate_tokens` |
| the four prompts with the text behind the switch (`0` as round 2, `1` text and blue id tags, `text` text only); one ask runs both arms on the same server, the two arms of one call one after the other, temperature 0, seed 0 | `critic._check_messages`, `critic.ask(arms=)`, `critic ask --arms 0,1`, `CRITIC_ARMS` in `scripts/jobs/critic.sh` |
| the judge question: each RC18 finding as `real_breach`, `reading_error` or `unclear` from two close-ups and the text; RC17 and RC14 findings queued in the same shape | `wenart/reading_check/critic_judge.py`, `critic judge-prep` |
| CPU side: vector files of an input set already made, the offline measure, the scorer per arm | `wenart/reading_check/vector_measure.py`, `critic vector`, `critic vt-measure`, `critic vt-score` |
| inputs for the pod: vector files of the 42 round-2 level entries (before, after, synth; model walls from readings at the right commits) and 44 judge level entries; 208 judge items (RC18 71, RC17 30, RC14 107), 62 labelled: 14 of the 15 eye-judged RC18 findings (real17's salon no longer fires after the facade-offset fix) and 48 RC14 judgements of `models/sense_trust.json` | `results/critic/inputs/` |

## Prompt sizes (every call of round 2, plus the 153 second looks and the 208 judge calls the next pod asks)

Tokens estimated; the A arm's estimate is +1 % to +15 % over the server's own counts of round 2 (mean +6 %).

| call | calls | A median / max | B median / max | text median / max | cut by the cap | B + answer, max |
|---|---|---|---|---|---|---|
| inventory | 42 | 2432 / 3166 | 3802 / 5489 | 1426 / 2354 | 15 | 8561 |
| compare | 91 | 4492 / 5989 | 6720 / 8321 | 2343 / 2369 | 69 | 9857 |
| plausibility | 56 | 1904 / 5935 | 2840 / 8285 | 1097 / 2363 | 16 | 10333 |
| second look | 153 | 789 / 817 | 2887 / 3161 | 2129 / 2378 | 64 | 3225 |
| judge | 208 | 2111 / 2162 | 4425 / 4504 | 2358 / 2383 | 141 | 4888 |

Every B prompt with its answer stays under 10.4k of the 16k context.

## What the text alone answers (a lower bound: fixed rules on the listed items, no images)

| question | answered by the text alone |
|---|---|
| compare marks | 810 of 1072 (room 310/415, opening type 445/520, balcony 28/78, angled wall 27/46, window 0/13) |
| round-2 compare findings judged right | the text agrees on 19 of 19 |
| round-2 compare findings judged wrong | the text refutes 2 of 4 |
| marks with no round-2 finding where the text differs from the reading | 14 (unverified: candidate catches) |
| known errors of the before readings | 33 of 74 shown by a listed drawing item: angled walls 8/8, opening types 18/19, kitchen windows 7/14; doors into the air 0/23 and real09's missing rooms and balconies 0/8 (its left flat is unlabelled: only the mirror shows them); the storey count is no drawing item |
| RC18 judge, 14 labelled | 9 decided, 5 right (the area rule cannot see the two narrow-side bathroom breaches; two light-air reading errors have their windows drawn without a window layer) |

The 3 errors round 2 missed: real10-B33 (a window read as an opening) had no compare question at that opening (the
opening cap) and no window-layer symbol there, so the text does not decide it; real03-B01 (the storey count) is in the
storey texts the inventory already gets; real09's roof is targeted by no check.

## C0008

The score is right: C0008 (real09's left balcony on L0) holds on the after reading, which has `os_L0_balkon_mirror_1`
at its place (`score --gate` holds; real09 has every correction satisfied). The critic's known errors were wrong:
`critic_checks.sparse_known` matched the user's corrections on `truth.extract` without the sparse fields, so no outdoor
space was ever seen. Both now read the reading through `score.reading_for`; `real09-UA01` is a fixed place in
`known_errors.json`. Round 2 re-scored: 71 of 74 known errors found (73 targeted), the same 71 as before.

## Pod plan (not started: the user decides)

```
scripts/gpu_run.py run --job scripts/jobs/critic.sh --max-minutes 45 --env CRITIC_MODELS=agent \
  --env CRITIC_SETS=before,after,synth,judge --env CRITIC_WHICH=plausibility,inventory,compare,judge,second \
  --env CRITIC_ARMS=0,1 --purpose "M14 RC15 vector text A/B and the RC18 judge"
```

| item | value |
|---|---|
| calls | per arm 189 (round 2's) + 208 judge + up to 160 second looks; at most 1114 in all |
| GPU | first in stock of `GPU_PRIORITY` with 48 GB or more (`JOB_MIN_VRAM_GB`): RTX PRO 6000, about $2.5/h (price read live from `/v2/catalog/gpus` at the start) |
| minutes | setup about 3, server about 3, asking about 22 (round 2: 189 calls in 342 s; B prompts about 1.5 times longer); expected 30, cut at 45 (the deadline stops new calls; the arms of a call go together, so a cut leaves both arms on the same questions) |
| cost | expected about $1.25; worst case 45 min x $2.5/h = $1.88; at the $5/h cap on any allowed card $3.75: under the $5 action limit (no `--over-5-ok`), the $30 day cap (nothing spent on 21 Nov) and the project total ($462.75 of $1000 spent) |
| before the pod | commit and push this branch (the pod clones the repository: the vector files and the judge set must be in it) |
| after the pod | `python -m wenart.reading_check critic vt-score --answers runs/<job>/results/critic/agent/answers.json` (recall, false findings, judge accuracy per arm); `critic calibrate --arm 0` / `--arm 1` for the review sheets; switch the default only when the B arm finds more known errors with no more false findings |

Measure files: `results/critic/vector_text_measure.json` (every call's sizes and the lower-bound rows).

## Pod result (21 Nov 2026, pod mry4qa3n8jaduh, RTX PRO 6000, 24 min, $1.06)

| arm | answered | findings | known errors found | false findings | right | judge RC18 | judge all labelled |
|---|---|---|---|---|---|---|---|
| A: images only | 543 | 609 | 54 / 73 | 11 | 71 | 8 / 14 | 51 / 62 |
| B: images + vector text | 529 | 725 | 66 / 73 | 11 | 103 | 7 / 14 | 39 / 62 |

B found 13 known errors A missed (real09-B07, real10-B03..B14) and missed 1 A found (real09-UB01); false findings
equal. Decision: the checks take the vector text by default (`scripts/jobs/critic.sh`, `CRITIC_VECTOR_TEXT=1`); the
judge asks with images only unless `CRITIC_JUDGE_TEXT=1` (it was worse with the text). Scores in
`vector_text_pod_score.json`.
