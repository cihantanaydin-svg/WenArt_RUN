"""One-command full project run (docs/milestone6.md §2, docs/milestone7.md §9).

``python -m wenart.run plan|pod|copy``. Stdlib only at import time (no
numpy, yaml, torch or bpy; the modules that need more import it inside the
function): the orchestrator starts every heavy step as a subprocess of the
existing command lines, each in its own venv.

- ``projects``: where a project's inputs, outputs and results live (§1.1);
- ``state``: stage records, fingerprints, statuses, project states (§1.2);
- ``stages``: the stage table with the exact command lines (§2.2);
- ``servers``: the vLLM server sessions (§1.4);
- ``scheduler``: the phases, deadline, server sharing, A/B steps, GPU tests
  and run manifests (§2.3, §6.3);
- ``copy``: the small result files into the results layout (§2.1);
- ``plan``: stage 1, the time rule (GPU_SPEED, recognition calls) and the pod split (§2.1, §8.1; M7 §9.3);
- ``ab``: the M5 files of the A/B and the camera check (§6.3; in M7 only for a control project whose control
  renders are missing);
- ``prep``: the prep pod's job (M7 §9.2).
"""
