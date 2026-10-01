# WenArt_RUN

Proof of concept: an automated pipeline that turns an architectural project folder
(PDF / DWG / photos + a style prompt) into photoreal, textured renders of the
furnished rooms, using open-weight AI models and open-source tools only.

- Plan and research: `docs/plan.md`
- Setup guide (Hugging Face, RunPod, Claude Code cloud environment): `docs/setup.md`
- Progress and next steps: `docs/progress.md`
- GPU spending log: `docs/gpu-log.md`
- Rules for every Claude session: `CLAUDE.md`
- Building JSON schema: `wenart/schema/building.schema.json`

Layout:

```
projects/<name>/      one folder per project (documents + optional brief.yaml)
results/<name>/       small JPG previews committed for viewing on GitHub
scripts/              setup.sh, gpu_run.py (RunPod runner), helpers
wenart/               pipeline code (Python package)
tests/                CPU tests here, GPU tests on RunPod (pytest -m gpu)
docs/                 plan, progress, logs, examples
```
