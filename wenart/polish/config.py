"""Load ``polish.yaml`` (docs/milestone5.md §1.6, §3).

Default paths resolve relative to this package, never to the cwd (§1.1).
``models.controlnet.config_dir`` is relative to ``wenart/polish``;
``config_dir(cfg)`` gives the absolute folder.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

POLISH_DIR = Path(__file__).resolve().parent
CONFIG_PATH = POLISH_DIR / "polish.yaml"


def load_config(path: Optional[str | Path] = None) -> dict:
    """The polish config as a dict (``polish.yaml`` of this package when ``path`` is None)."""
    import yaml
    with open(CONFIG_PATH if path is None else path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def config_dir(cfg: dict) -> Path:
    """Absolute folder of the vendored ControlNet config (``models.controlnet.config_dir``)."""
    rel = Path(cfg["models"]["controlnet"]["config_dir"])
    return rel if rel.is_absolute() else POLISH_DIR / rel
