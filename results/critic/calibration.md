# RC15 the vision critic: calibration of the first pod (6 Nov 2026)

Pod jz5j09w4dlvmgm (RTX PRO 6000 WK, 28.6 min, $1.24): `Qwen/Qwen3.8-27B-FP8` at 017b9c7a, served by `wenart.run.servers`
with 0.90 of the VRAM and 16k context, 8 sequences; setup 181 s, server ready after 190 s, then 1,218 s of asking. 58 levels
(set a 26, set b 13, set c 19): all 58 differences calls answered, 33 of 58 question-bank calls answered, 25 skipped at
the deadline (set c's and 7 of set b's); qwen skipped (-131 s left). Mean call 101 s (prompt 5.3k tokens, answer 1.1k),
every answer valid against its schema at the first try. Raw answers: `runs/20261106-104159-critic/results/critic/agent/
answers.json`; mapped findings `results/critic/findings_agent.json`; the full tables `results/critic/calibration.json`;
the judgements from the drawings `results/critic/judged_by_eye.json`; the trust file
`wenart/reading_check/models/critic_trust.json`.

## What the model did

570 differences on 58 levels, **9.8 a level, never zero, mean confidence 93**: 370 `missing_opening`, 87 `wrong_label`,
51 `missing_wall`, 20 `missing_stair`, 15 `extra_opening`, 10 `extra_wall`, 8 `split_room`, 7 `false_stair`, 1 merged,
1 other. The mapping is right (the points sit on the drawn doors and labels they describe; the dot test gives 2 mm).
The model is **blind to image 2's legend**: it calls a door or window "missing from the model" where the model panel
draws a green or blue bar at that very place (synthetic-16: six "missing doors", every one of them a green bar; set c's
clean readings get 6 to 28 such findings each); and it reports the model's label spelling as `wrong_label` ("'Salon
(living)' but the drawing says 'salon'", "the kitchen is mislabeled as a kitchen"). The prompt now states both rules
(the legend, the spelling) and that most levels have zero to three real differences; this is measured only by another pod.

## Precision on set a (the accepted projects' current readings, 271 findings)

A finding is right when the truth disagrees with the reading within 1.5 m in the way its kind says; 13 findings the
truth calls false are right by the drawing (the accepted truth carries the reading's own error: real21's six AYDINLIK
light wells read as bedrooms or unknown rooms, five of real15's unbuilt left-block walls, real06's dining room merged
into the salon) and are counted right (`judged_by_eye.json`).

| kind | findings | right | precision | by truth alone | note |
|---|---|---|---|---|---|
| missing_opening | 165 | 0 | 0.00 | 0.00 | the green and blue bars not read as openings |
| wrong_label | 45 | 6 | 0.13 | 0.00 | the 6: real21's light wells; the rest spelling and translation |
| missing_wall | 29 | 6 | 0.21 | 0.00 | real15 x5, real06 x1 by eye |
| extra_opening | 12 | 3 | 0.25 | 0.25 | real10 L-1's door in a solid wall, synthetic-07's two terrace doors |
| missing_stair | 6 | 0 | 0.00 | 0.00 | |
| split_room | 5 | 3 | 0.60 | 0.60 | synthetic-06's lobby and living room, synthetic-07's hall (small sample) |
| extra_wall | 4 | 2 | 0.50 | 0.50 | synthetic-06's two separator walls (small sample) |
| false_stair | 4 | 0 | 0.00 | 0.00 | real02 and real04's U stair read as two flights (false) |
| merged_rooms | 1 | 1 | 1.00 | 0.00 | real06's dining room (by eye; one finding) |
| all | 271 | 21 | **0.08** | 0.03 | random points with the same counts and kinds: 0.008 |

Three kinds pass the 0.5 threshold on 1 to 5 findings each; `small_sample: true` in the trust file. Every other kind
writes info.

## Recall of the user's corrections on set b (RC14's 24 records), next to RC14's 15 of 24

By the mechanical rule (a finding on the record's level within 1.5 m of its place, or of its element kind for a record
without a place): **11 of 24**; random points with the critic's own density: 5.0 of 24. By meaning (the nearest
finding names the record's problem, judged record by record in `judged_by_eye.json`): **2 of 24**.

| record | project | the correction | RC14 (round 2) | critic by place | nearest finding | critic by meaning |
|---|---|---|---|---|---|---|
| C0001 | real09 | glazed facade closed along its frames | no | yes | a missing door swing on the kitchen wall, 1.43 m | no |
| C0003 | real09 | the recess mouth is open air | yes | yes | 'Banyo' label remark, 0.48 m | no |
| C0004 | real09 | both halves alike | yes | yes (by kind) | a gallery label remark | no |
| C0006 | real09 | the stair core room | no | no | 2.68 m | no |
| C0007 | real09 | tile grids are no stair | yes | yes | the tiled room's label, 1.23 m | no |
| C0009 | real09 | the attic over its core | yes | no | - | no |
| C0013 | real09 | four winder stairs | no | no | a missing wall, 1.08 m | no |
| C0002 | real07 | no walls outside the facade | no | no | - | no |
| C0010 | real07 | fixtures are no anchors | no | no | - | no |
| C0051 | real07 | an open passage, no wall | no | no | a bathroom window, 1.68 m | no |
| C0053 | real07 | no wall over the stair's edge | yes | yes | a hall window, 0.79 m | no |
| C0054 | real07 | the curved stair 1-18 is the stair | yes | yes | "the central staircase is completely missing from the model", 0.45 m | **yes** |
| C0016 | real10 | no wall between stair and landing | yes | yes | Oda/antre label remark, 1.07 m | no |
| C0017 | real10 | Merdiven + Kat Holü one room | no | yes | Oda/antre label remark, 0.41 m | no |
| C0018 | real10 | the inside hall is a room | yes | no | 3.19 m | no |
| C0020 | real10 | the closets are Depo | no | yes | the central bathroom split, 1.42 m | no |
| C0023 | real10 | the recess is open air | yes | no | 3.33 m | no |
| C0027 | real10 | the central hall and the right flat apart | yes | no | a missing curved stair, 2.39 m | no |
| C0028 | real10 | the kitchen door in its gap | yes | no | 3.41 m | no |
| C0035 | real10 | the fire stair | yes | yes | Oda/antre label remark, 0.46 m | no |
| C0037 | real10 | open air, not two rooms | yes | no | 1.85 m | no |
| C0029 | real17 | a hatch's text island is no hole | yes | yes (by kind) | "the entire perimeter wall of the building is missing" | yes (the same symptom) |
| C0030 | real17 | a title listing floors | no | no | - | no |
| C0038 | real17 | walls joined at their columns | yes | no | missing windows, 2.82 m | no |

Corrections only the critic raised: by place C0001, C0017, C0020 (all three by an unrelated finding that happens to
lie within 1.5 m); by meaning none. Of the other 21 placed records of these projects (outside RC14's set) 7 are raised
by place, none checked by meaning.

## Out of sample on set c (synthetic-08 to -22), next to RC14's 1 of 11

9 of the 15 classes read with an error against their exact truth (the same 9 for both reviewers: 08, 09, 10, 12, 14,
16, 17, 20, 22); 6 read clean.

| class | reading errors | findings | by place | what the findings say | by meaning |
|---|---|---|---|---|---|
| 08 spaced labels | 2 label errors | 6 | missed | doors missing | no |
| 09 jamb stubs | 5 extra wall stubs | 6 | caught (5) | doors missing at the jambs | no |
| 10 glazed facade | 8 | 6 | missed | doors and windows missing | no |
| 12 mirrored halves | 13 (labels, doors) | 10 | caught (7) | the right half's rooms labelled 'Oda', split rooms, extra walls | **yes** (the labels) |
| 14 elevation title | 66 (L1 unread) | 6 | caught (13) | doors missing | no |
| 16 open recess | 1 extra opening | 6 | caught (1) | the door there "missing" (the opposite claim) | no |
| 17 garage, lift | 4 | 6 | missed | doors missing | no |
| 20 glazed corner | 11 | 7 | caught (2) | openings missing | no |
| 22 curved stair | 1 missing stair | 7 | caught (1) | "the curved staircase is missing" | **yes** |
| 11, 13, 15, 18, 19, 21 (clean) | 0 | 6-28 each | 6 false alarms | doors and windows missing | - |

By place 6 of 9 caught, against 5.6 of 9 for random points of the same density; by meaning **2 of 9** (RC14: 1 of 11)
with **6 false alarms on the 6 clean classes** (RC14: 0).

## The question bank

42 questions (the reading and plan lessons) on 33 levels: **0 problems**, 909 ok, 477 cannot_see. Questions about
layers, units, sections and other floors come back cannot_see (14-15 of 33 for UL260, UL264, UL278, UL282, UL286,
UL308, UL316); every question the images could answer comes back ok on every level, also on the 7 set-b levels whose
errors the user corrected. The question bank told us nothing; the 25 skipped calls would not change that.

## Verdict

As prompted, the critic is not better than chance: its precision is 0.08 (random points 0.008, but 165 of its 271
findings are the legend misread), its recall by place (11 of 24) is twice chance (5) and by meaning 2 of 24 against
RC14's 15, its out-of-sample catches are at chance by place and 2 of 9 by meaning with false alarms on every clean
reading. The two things it did see that RC14 could not (real07's curved stair, synthetic-22's) are both missing stairs,
and real21's light wells are an error the accepted truth carries. Nothing it raised is a correction only it found.

The trust file leaves every kind at info except `extra_wall` (2 of 4), `split_room` (3 of 5) and `merged_rooms` (1 of
1), each a small sample. A second pod is worth it only with the corrected prompt (the legend, the spelling, zero to
three differences a level) and the differences call alone, with qwen beside it for comparison: about 30 min, about
$1.30 at the RTX PRO 6000's price; finishing the 25 question-bank calls is not.
