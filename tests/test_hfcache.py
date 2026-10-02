"""Local snapshot folders for the pod's model loaders (wenart/hfcache.py).

Pod run 0 (2 Oct 2026) died on ``AutoTokenizer.from_pretrained(repo,
subfolder="tokenizer", revision=...)`` with ``HF_HUB_OFFLINE=1`` although every
file was cached; the loaders now read the snapshot's local folder. These tests
pin the resolution rules with a fake ``huggingface_hub``.
"""
import sys
import types

import pytest

from wenart import hfcache


@pytest.fixture
def hub(monkeypatch):
    calls = []
    mod = types.ModuleType("huggingface_hub")
    state = {"cached": True}

    def snapshot_download(repo, *, revision=None, allow_patterns=None, local_files_only=False):
        calls.append((repo, revision, allow_patterns, local_files_only))
        if local_files_only and not state["cached"]:
            raise OSError("not in the cache")
        return f"/hf/{repo}/{revision}"

    mod.snapshot_download = snapshot_download
    monkeypatch.setitem(sys.modules, "huggingface_hub", mod)
    return calls, state


def test_a_cached_snapshot_never_touches_the_hub(hub, monkeypatch):
    calls, _ = hub
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    path = hfcache.local_snapshot("org/model", "abc123", ["*.json"])
    assert str(path) == "/hf/org/model/abc123"
    assert calls == [("org/model", "abc123", ["*.json"], True)]


def test_offline_and_missing_is_a_clear_error(hub, monkeypatch):
    _, state = hub
    state["cached"] = False
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    with pytest.raises(FileNotFoundError, match="org/model@abc123 is not in the Hugging Face cache"):
        hfcache.local_snapshot("org/model", "abc123")


def test_online_and_missing_downloads_the_pinned_revision(hub, monkeypatch):
    calls, state = hub
    state["cached"] = False
    monkeypatch.delenv("HF_HUB_OFFLINE", raising=False)
    assert str(hfcache.local_snapshot("org/model", "abc123")) == "/hf/org/model/abc123"
    assert calls == [("org/model", "abc123", None, True), ("org/model", "abc123", None, False)]


@pytest.mark.parametrize("value,offline", [("1", True), ("true", True), ("ON", True), ("0", False), ("", False)])
def test_offline_flag_values(monkeypatch, value, offline):
    monkeypatch.setenv("HF_HUB_OFFLINE", value)
    assert hfcache.hub_offline() is offline
