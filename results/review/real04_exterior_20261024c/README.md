# real04: pool-side bulge gone, roof terraces with railings, green bushes (24 Oct 2026)

User remark of 24 Oct 2026: "Roof still not looking realistic enough there seems to be some gaps and unrealistic,
also there was a bulge from bodrum kat [...] Bulge at the side of the pool".

Pod `xrsf17cw0e6od1` (RTX PRO 6000, $2.49/h), job `20261024-174006-full`, code 7bea23b, 109 min, $4.51; GPU tests
48 passed, 8 skipped, 0 failed. `sheets13/`: before = Milestone 13 (`results/baseline/m13/`), after = this run.

| Seen | Cause | Change (general) |
|---|---|---|
| a box beside the pool under a basement window | an assumed light well made against the sloped ground; the drawn pool terrace lies 0.9 m under the sill | `site.wells_on_platforms`: no well over a lower terrace; under a higher one it opens at the terrace level |
| gutters running past the roof along the terraces | the gutter followed the whole roof outline, roof terraces included | `facade.eaves_edges`: only real eaves; downpipes at both ends of every run |
| white boxes at the roof ends | the assumed 1.0 m terrace parapet rose 0.4 m over the eaves | `roof.roof_model`: the wall stops at the eaves line, `build.terrace_railings` adds a glass railing to 1.0 m |
| white bushes | the library bush the audit rated 2 / 5 | `site_models.vision_quality`: models rated 2 or less are not picked (plants, cars, doors, windows) |
