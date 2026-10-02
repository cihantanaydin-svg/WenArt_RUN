"""Change gate: accept a polished image only when its geometry is unchanged (docs/milestone5.md §4; area C).

``Gate``, ``Reference`` and ``decide`` come from ``wenart.gate.api``, which
does not import torch; the model wrappers (``wenart.gate.models``) import
torch/transformers lazily.
"""
from wenart.gate.api import Gate, Reference, decide

__all__ = ["Gate", "Reference", "decide"]
