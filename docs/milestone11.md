# Milestone 11 – an AI orchestrator that checks and fixes the whole pipeline inside the pod

Goal (user, 9 Oct 2026): the real02 results are bad. The exterior does not look like a real building on a real
site, and furniture placement is not logical (wrong facing, pieces floating in the middle of rooms, blocked
walkways, odd combinations). Today the pipeline is a fixed chain of stages (`wenart/run/stages.py`) with strict
rules and small AI calls (Qwen3-VL-8B, two passes, temperature 0). Nothing looks at the result as a whole, and
nothing sends a bad result back to the stage that caused it.

Milestone 11 adds an **agent**: a large open-weight vision-language model on the pod that runs the stages as typed
tools, checks every output against common sense, fixes what it finds through validated edits, and loops until the
critic is satisfied or the budget ends. The old fixed chain stays as `--no-orchestrator`.

Note on the file name: the user asked for the design in `docs/milestone10.md`, but that file is the Milestone 10
spec (815 lines, done). This design is `docs/milestone11.md`.

Status: **design, waiting for the user's OK** (step 1). Only plain bug fixes (§1) are built before the OK.

<!-- DIAGNOSIS -->

<!-- DESIGN -->
