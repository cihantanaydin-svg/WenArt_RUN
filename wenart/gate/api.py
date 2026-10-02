"""Change-gate API (docs/milestone5.md §1.3, §4): the binding signatures.

What: ``Gate`` compares a polished image with its Cycles reference and
accepts it only when the geometry is unchanged (edges lost and added,
monocular depth, SAM 2.1 masks, colour, neutral walls, DINOv2 features).
``decide`` turns stored metrics into a decision with the current thresholds,
so a reused polish attempt is re-decided without running any model.

Why a separate module: the polish ladder, the calibration and the GPU tests
all import ``Gate``/``decide``; this module imports neither torch nor
transformers (the model wrappers in ``gate/models.py`` import them lazily),
so it loads on a CPU-only machine. Written as a skeleton by F0; area C fills
the bodies.

Contract (§1.3):

- ``Gate(thresholds=None, models=None, device="cuda")``: ``thresholds`` a
  dict or a YAML path (None = this package's ``thresholds.yaml``); ``models``
  a ``wenart.gate.models.Models`` (None = loaded lazily on first use; tests
  pass a fake).
- ``Gate.prepare(view, ref_rgb) -> Reference``: regions, reference edges, Lab
  means and the model outputs on the reference, computed once per view and
  cached.
- ``Gate.compare(ref, test_rgb) -> {"decision": "accept"|"reject", "reasons",
  "notes", "metrics", "gate_key"}``; ValueError when ``test_rgb`` is not the
  view size.
- ``decide(metrics, thresholds) -> (decision, reasons, notes)``: pure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

GATE_DIR = Path(__file__).resolve().parent
THRESHOLDS_PATH = GATE_DIR / "thresholds.yaml"
MODELS_PATH = GATE_DIR / "models.yaml"


def _load_yaml(path) -> dict:
    import yaml
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_thresholds(path: Optional[str | Path] = None) -> dict:
    """The gate thresholds (this package's ``thresholds.yaml`` when ``path`` is None)."""
    return _load_yaml(THRESHOLDS_PATH if path is None else path)


def load_models_config(path: Optional[str | Path] = None) -> dict:
    """The gate model list ``{"models": {"depth"|"sam"|"dino": {repo, revision, licence, allow_patterns}}}``."""
    return _load_yaml(MODELS_PATH if path is None else path)


@dataclass
class Reference:
    """What ``Gate.prepare`` computes once per view (placeholder; area C owns the fields).

    ``gate_key`` is the key ``compare`` will report for this reference
    (GATE_CODE_VERSION, gate model revisions, reference sha256), so the polish
    can tell whether stored gate metrics are still valid before comparing.
    """
    view: Any
    rgb: Any
    sha256: str = ""
    gate_key: str = ""
    regions: Any = None
    edges: Any = None
    lab_means: dict = field(default_factory=dict)
    model_outputs: dict = field(default_factory=dict)


class Gate:
    """Geometry change gate for one device; see the module docstring for the contract."""

    def __init__(self, thresholds: Optional[dict | str | Path] = None, models: Any = None,
                 device: str = "cuda") -> None:
        if thresholds is None or isinstance(thresholds, (str, Path)):
            thresholds = load_thresholds(thresholds)
        self.thresholds = thresholds
        self.models = models
        self.device = device

    def prepare(self, view, ref_rgb) -> Reference:
        """Regions, reference edges, Lab means and model outputs of the reference image (cached per view)."""
        raise NotImplementedError("wenart.gate.api.Gate.prepare: area C")

    def compare(self, ref: Reference, test_rgb) -> dict:
        """``{"decision", "reasons", "notes", "metrics", "gate_key"}`` for ``test_rgb`` against ``ref``."""
        raise NotImplementedError("wenart.gate.api.Gate.compare: area C")


def decide(metrics: dict, thresholds: dict) -> tuple[str, list, list]:
    """``("accept"|"reject", reasons, notes)`` from stored metrics and thresholds (pure).

    ``reasons`` are the failed hard checks, ``notes`` the failed soft ones,
    each ``{check, region: "global"|<id>, value, threshold, op: ">="|"<="}``;
    accept iff every hard check passes (§4.2).
    """
    raise NotImplementedError("wenart.gate.api.decide: area C")
