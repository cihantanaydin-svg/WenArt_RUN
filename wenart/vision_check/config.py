"""Load ``check.yaml`` (docs/milestone5.md §5) and make the default VLM client (§1.5).

The default path resolves relative to this package (§1.1). ``client_factory``
is the default of every ``main(argv=None, client_factory=None)`` that talks to
a vLLM server: model key (``qwen``/``glm``) -> a ``VLMClient`` for that
model's id at ``base_url``. Fakes implement only ``.model`` and
``.run_schema``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

CHECK_DIR = Path(__file__).resolve().parent
CONFIG_PATH = CHECK_DIR / "check.yaml"


def load_config(path: Optional[str | Path] = None) -> dict:
    """The vision-check config as a dict (this package's ``check.yaml`` when ``path`` is None)."""
    import yaml
    with open(CONFIG_PATH if path is None else path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def client_factory(model_key: str, base_url: str, cfg: Optional[dict] = None):
    """A ``VLMClient`` for ``check.yaml: models.<model_key>.id`` served at ``base_url`` (KeyError for an unknown key)."""
    from wenart.recognition.vlm_client import VLMClient
    models = (cfg or load_config())["models"]
    return VLMClient(base_url, model=models[model_key]["id"])
