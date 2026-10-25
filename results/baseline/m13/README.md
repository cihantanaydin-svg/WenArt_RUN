# Milestone 13 baseline (before / after rule of 24 Oct 2026)

Your rule of 24 Oct 2026: "from now on every before after must be between ms 13 and other changes implemented".
Replaced by the rule of 25 Oct 2026 ("every run is against its latest run, not according to milestones"): the
default "before" is now the project's latest run (`../latest/README.md`). These Milestone 13 runs are kept and
used with `--baseline m13` when asked, or as the "before" when no later run of the project is known. Layout: the
committed results layout (`furniture/`, `renders/`, `final/`, `agent/`, `run/`).

| Project | Milestone 13 run here | Source |
|---|---|---|
| real04 | yes | pod `udqp9w9972b08f`, job `20261023-135954-full`, code 2799c88 (the Milestone 13 final code: windows-only interior sky, final-pass fixes; before the 3D Warehouse layer, the group options 10x and the r16 ground floor); review in `results/review/real04_rerun_20261023/` |
| real03 | not yet | P6b (`results/review/m13_p6b/`): its full output is on the network volume (`outputs/real03`, `WENART_OUTPUTS` of `scripts/jobs/full.sh`) until a run overwrites it; copy it here before the next real03 run |
| real02 | not yet | P6c (`results/review/m13_p6c/`): its full output is on the network volume (`outputs/real02`, `WENART_OUTPUTS` of `scripts/jobs/full.sh`) until a run overwrites it; copy it here before the next real02 run |

Files per project: `furniture/<p>/building_final.json`, `renders/<p>/scene_manifest.json`, `render_manifest.json`,
`variants/<id>/scene_manifest.json`, `final/<p>/final_manifest.json`, `final_report.md`, `ATTRIBUTION.md`,
`*_final_preview.jpg`, `agent/<p>/log.json`, `run/<p>/*.json` (stage records). Never replaced by a later run.
