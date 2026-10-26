# The user's lessons, checked by the AI architect

18 lesson(s) asked; model Qwen/Qwen3.8-27B-FP8.

| Lesson | Verdict | Finding |
|---|---|---|
| UL03 | ok | The code check D3 (terrace doors) is ok. The building facts do not list any terraces or outer doors/windows to contradict the lesson, and no open findings exist for this lesson. |
| UL07 | ok | The code checks A2 and A5 are ok. The building facts do not list any terraces or pool decks, so there are no elements to reach. |
| UL10 | ok | The code checks A5 and A2 are ok. No terraces are listed in the building facts, so the condition is vacuously satisfied. |
| UL11 | issue | The code check W2 is open with 4 findings. The windows win_L0_001 (between kitchen and living), win_L1_004 and win_L1_005 (between dressing and bathroom), and win_L1_008 (between living and hall) are located in internal walls between rooms, not looking outside. (win_L0_001, win_L1_004, win_L1_005, win_L1_008) |
| UL12 | ok | The code check L1 is ok. All habitable rooms (kitchen, living, bedrooms) have sufficient glass area relative to their floor area. |
| UL13 | ok | The code check C2 is ok. The kitchen (r_L0_mutfak) opens onto the living room (r_L0_salon), satisfying the requirement for a separate kitchen to be adjacent to the living/dining space. |
| UL14 | ok | The code check F5 is fixed. All furniture clashes were identified and resolved (changed). |
| UL15 | ok | The code checks A2 and K2 are ok/fixed. No terraces are listed in the building facts. The stair void guard was fixed. |
| UL16 | ok | The code check S2 is answered. The furniture coherence issues (loud colors, wood/metal tones) were addressed by the architect's answers and changes. |
| UL17 | ok | The code check S3 is answered. The decor shortages in the hall, bathroom, and living room were addressed by the architect's answers. |
| UL18 | ok | The code check S4 is answered. The missing furniture items in the living rooms and bedroom were addressed by the architect's answers. |
| UL20 | ok | The code checks U1 and D3 are ok. No terraces are listed in the building facts, so there is no outdoor furniture to check. |
| UL21 | ok | The code checks K1, K2, and K3 are fixed. The stair treads, void guard, and balustrade language were corrected. |
| UL28 | unknown | There is no evidence provided for this lesson (evidence object is empty), and the building facts do not contain specific details about gutters or downpipes. |
| UL29 | ok | The code check H1 is ok. All washbasins are at the correct working height (0.85 m). |
| UL30 | ok | The code check D4 is ok. All doors stand on the floor of the rooms they join. |
| UL31 | ok | The code checks E1, O2, W3, and K2 are ok/fixed. All upper floor openings have appropriate guards or sills, and the stair void is guarded. |
| UL32 | ok | The code checks S2 and S3 are answered. The design coherence and decor issues were addressed by the architect's answers and changes. |
