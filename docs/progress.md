# Progress

## Milestone 0 – plan (done, waiting for your OK)

What works:
- Repo skeleton, `CLAUDE.md` rules, building JSON schema + validated example.
- `docs/plan.md`: reality check, approach choice (3D-first with gated polish), stage diagram,
  option tables with licences and picks, RunPod setup, cost estimate (~$35–45 of $100).
- `docs/setup.md`: step-by-step setup guide for Hugging Face, RunPod and the cloud environment.

What fails / is blocked:
- This cloud environment blocks `api.runpod.io`, `huggingface.co` and others, so no RunPod
  read-only checks could run yet. Hugging Face model cards could not be fetched; licences were
  verified from GitHub LICENSE files instead and marked (S) where only search snippets exist.
- Live GPU prices are from third-party snippets; the runner will read them from the API.

GPU cost so far: $0.00

Next step: you finish `docs/setup.md` steps 1, 2 and 4, start a new session, and give your OK on
`docs/plan.md`. Then Milestone 1: `setup.sh` + `scripts/gpu_run.py` tested on a real pod.
