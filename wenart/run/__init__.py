"""One-command full project run (docs/milestone6.md §2).

``python -m wenart.run plan|pod|copy``. Stdlib + yaml only at import time (no
torch, no bpy): the orchestrator starts every heavy step as a subprocess of the
existing command lines, each in its own venv.
"""
