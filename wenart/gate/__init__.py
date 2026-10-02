"""Change gate: accept a polished image only when its geometry is unchanged (docs/milestone5.md §4; area C).

``Gate``, ``Reference`` and ``decide`` come from ``wenart.gate.api``, which
imports neither torch, transformers, OpenCV nor Pillow at import time; the
check modules (``edges``, ``lines``, ``depth``, ``colour``, ``masks``,
``features``, ``debug``, ``controls``) are numpy/OpenCV, the model wrappers
(``wenart.gate.models``) import torch/transformers lazily, and
``python -m wenart.gate calibrate`` runs the §4.3 calibration.
"""
from wenart.gate.api import GATE_CODE_VERSION, Gate, Reference, decide

__all__ = ["GATE_CODE_VERSION", "Gate", "Reference", "decide"]
