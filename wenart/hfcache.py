"""Local folders of the pinned Hugging Face snapshots (docs/milestone5.md §1.6).

What: ``local_snapshot(repo, revision, allow_patterns)`` returns the folder of a
pinned snapshot in the Hugging Face cache (``HF_HOME``, on the pod
``/opt/wenart/hf``), so the model loaders read local paths only.

Why: with ``HF_HUB_OFFLINE=1`` a ``from_pretrained(repo_id, subfolder=...,
revision=...)`` call can fail although every file is cached. transformers
5.18's ``AutoTokenizer`` first asks ``AutoConfig`` for
``<subfolder>/config.json``; the Z-Image tokenizer folder has none, and offline
a missing file cannot be told apart from a network error, so the load died with
"We couldn't connect to 'https://huggingface.co' ..." (pod run 0, 2 Oct 2026;
reproduced in the session with the cached tokenizer files). A local folder needs
no hub lookup at all.

How: ``huggingface_hub.snapshot_download(..., local_files_only=True)`` (the
snapshot ``scripts/pod_setup_polish.sh`` downloaded with the same revision and
allow patterns); when the snapshot is not cached and the hub is not offline it
is downloaded. huggingface_hub is imported lazily (the CPU session has none).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def hub_offline() -> bool:
    """True when ``HF_HUB_OFFLINE`` is set to a true value (as huggingface_hub reads it)."""
    return os.environ.get("HF_HUB_OFFLINE", "").strip().upper() in ("1", "ON", "YES", "TRUE")


def local_snapshot(repo: str, revision: str, allow_patterns: Optional[list[str]] = None) -> Path:
    """Folder of ``repo`` at ``revision`` in the HF cache; downloads it only when online and missing."""
    from huggingface_hub import snapshot_download

    kwargs = {"revision": revision}
    if allow_patterns:
        kwargs["allow_patterns"] = list(allow_patterns)
    try:
        return Path(snapshot_download(repo, local_files_only=True, **kwargs))
    except Exception as exc:  # noqa: BLE001 - LocalEntryNotFoundError and friends
        if hub_offline():
            raise FileNotFoundError(f"{repo}@{revision} is not in the Hugging Face cache "
                                    f"(HF_HUB_OFFLINE=1): {exc}") from exc
    return Path(snapshot_download(repo, **kwargs))
