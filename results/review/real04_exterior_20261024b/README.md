# real04 after the pool-side well and gutter fixes (24 Oct 2026)

User remark of 24 Oct 2026: "Roof still not looking realistic enough there seems to be some gaps and unrealistic,
also there was a bulge from bodrum kat [...] Bulge at the side of the pool".

Pod `37me6g1nvncmu1` (RTX PRO 6000, $2.49/h), job `20261024-153219-full`, code 9502309, 119 min, $4.94; GPU tests
48 passed, 8 skipped, 0 failed. `sheets13/`: before = Milestone 13 (`results/baseline/m13/`), after = this run.

- The bulge beside the pool was an assumed light well (1 m concrete box) in front of the basement window
  `win_L-1_003`, made against the sloped ground while the drawn pool terrace there lies 0.9 m under the sill: gone
  (`site.wells_on_platforms`). The court in front of `win_L-1_004` stays (its terrace is above the sill).
- Gutters ran along the roof-terrace parapets past the end of the roof: now only along real eaves, with downpipes at
  both ends of every run (`facade.eaves_edges`, `downpipe_stations`).
- Still open in this run: the library bushes render white (fixed after it: low-rated library models are not
  picked), the terrace parapets stand 0.4 m over the eaves (fixed after it: parapet at the eaves line with a
  glass railing).
