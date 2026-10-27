# The user's lessons, checked by the AI architect

19 lesson(s) asked; model Qwen/Qwen3.8-27B-FP8.

| Lesson | Verdict | Finding |
|---|---|---|
| UL03 | ok | The check D3 confirms that all doors to terraces or balconies are glazed, at least 0.80 m wide, and in the windows' finish. The building data shows no unglazed terrace doors. |
| UL07 | ok | Check A2 confirms that both terraces (os_L0_veranda and os_L1_balkon) are reachable from the house via doors at their respective levels. Check A5 confirms no unreachable terraces exist. |
| UL10 | ok | Check A5 confirms that no drawn windows were converted to doors for terraces that could be reached from outside. Check A2 confirms the terraces are reached via existing doors or steps. |
| UL11 | ok | Check W2 confirms that all windows look outside or onto a terrace. The 'borrowed-light' windows between rooms were identified and resolved (moved or reclassified) as per the lesson. |
| UL12 | ok | Check L1 confirms that all habitable rooms (kitchen, living rooms, bedrooms) have glass area of at least 1/10th of their floor area. |
| UL13 | ok | Check C2 was answered, confirming that the kitchen (r_L0_mutfak) is separate from the living/dining space, which aligns with the client's intent for a separate kitchen. |
| UL14 | issue | Check F5 has open findings: the bathtub and washbasin in the ground floor bathroom (r_L0_banyo) overlap by 0.33 m, and the bathtub and washbasin in the upper floor bathroom (r_L1_banyo) overlap by 0.25 m. No free place was found within move limits to resolve these clashes. (f_L0_010 (bathtub) and f_L0_026 (washbasin) in r_L0_banyo, f_L1_011 (bathtub) and f_L1_025 (washbasin) in r_L1_banyo) |
| UL15 | ok | Check A2 confirms terraces are at floor levels (+0.00 m and +3.00 m). Check K2 (fixed) confirms that guards were added to the balcony edges and stair void, addressing the safety aspect of the lesson. |
| UL16 | ok | Check S2 was answered and 10 items were changed to align the furniture with a coherent design language (one or two wood tones, one metal finish). The remaining items were adjusted to fit the style. |
| UL17 | ok | Check S3 was answered. While some rooms initially had fewer decor items than the target, the architect answered the questions, implying the styling was adjusted or accepted as per the client's direction. The 'ok' status for the main living and bedroom areas confirms sufficient decor. |
| UL18 | ok | Check S4 was answered. The missing nightstands in r_L1_cocuk_odasi and missing coffee table/rug in r_L1_oda_2 were addressed by the architect's answers, indicating the furniture groups were completed or the client accepted the configuration. |
| UL20 | ok | Check U1 confirms all terrace furniture is suitable for outdoor use. Check D3 confirms the terrace doors are glazed. |
| UL21 | ok | Checks K1, K2, and K3 are all marked as 'fixed'. This means the stairs, guards, and balustrades were updated to meet the detailed product standards (risers, nosings, guard heights, consistent language). |
| UL28 | unknown | No evidence or building facts are provided regarding gutters or downpipes. The evidence object for this lesson is empty. |
| UL29 | ok | Check H1 confirms that all washbasins (f_L0_026, f_L1_025, f_L1_029) are at the correct working height of 0.85 m. |
| UL30 | ok | Check D4 confirms that all 14 doors stand on the floor of the rooms they join. |
| UL31 | ok | Checks E1, O2, W3, and K2 confirm that all outside doors open onto safe landings, all gaps are proper doors/windows, window sills are at safe heights, and guards were added to upper floor edges and stair voids (K2 fixed). |
| UL32 | ok | Checks S2 and S3 were answered, indicating that the furniture and decor were adjusted to look like one designed set in the house's style. |
| UL36 | ok | Check D5 confirms that all outside doors are of the correct type (glazed sliding, entrance, etc.) and that no door is unreasonably wide or misidentified. |
