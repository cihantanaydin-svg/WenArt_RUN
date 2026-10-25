# Latest run of each project (before / after rule of 25 Oct 2026)

Your rule of 25 Oct 2026: "From now on every run is against its latest run compare not according to milestones".
Every before / after (`python -m wenart.report sheets13` / `metrics13`) compares a new run (after) with the
project's latest run before it (before), found by `wenart.report.latest`: the runner's local copies
(`runs/<job>/results/final/<p>`), this folder, and the Milestone 13 copies (`../m13`, kept) when nothing newer is
known. After the report the new run is copied here
(`python -m wenart.report latest --out runs/<job>/results/final/<p> --promote`), so the next session finds it.

`runs.json` names the run of each project here. Files per project (the set the reports read):
`furniture/<p>/building_final.json`, `renders/<p>/scene_manifest.json`, `render_manifest.json`,
`variants/<id>/scene_manifest.json`, `final/<p>/final_manifest.json`, `final_report.md`, `ATTRIBUTION.md`,
`*_final_preview.jpg`, `agent/<p>/log.json`, `run/<p>/*.json`. A project's copy is replaced by its next run; git
keeps the earlier ones.
