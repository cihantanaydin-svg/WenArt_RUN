"""The committed Poly Haven furniture review pack is complete, CC0, and offline.

No network: the test only reads ``library/review`` and the fetcher's pure helpers.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import urllib.parse
from pathlib import Path

from wenart.furniture.catalog import FURNITURE_TYPES

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "library" / "review"
INDEX_PATH = REVIEW / "index.json"


def _fetcher():
    path = ROOT / "scripts" / "fetch_furniture_review.py"
    spec = importlib.util.spec_from_file_location("fetch_furniture_review", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _gltf_uris(path: Path) -> list[str]:
    doc = json.loads(path.read_text(encoding="utf-8"))
    uris = []
    for key in ("buffers", "images"):
        for item in doc.get(key) or []:
            uri = item.get("uri") if isinstance(item, dict) else None
            if isinstance(uri, str) and uri and not uri.startswith("data:"):
                uris.append(urllib.parse.unquote(uri.split("?", 1)[0]))
    return uris


def test_furniture_filter_uses_the_categories_token():
    fetcher = _fetcher()
    assert fetcher.is_furniture({"categories": ["furniture", "seating"]})
    assert fetcher.is_furniture({"categories": ["decorative", "furniture"]})
    # A "Furniture/..." category path is not enough: hand_truck is that path
    # and is not in the furniture category list.
    assert not fetcher.is_furniture({"categories": ["props", "industrial"], "category": "Furniture/Storage Furniture/Carts & Trolleys"})
    assert not fetcher.is_furniture({"categories": "furniture"})


def test_rerun_preserves_selected_use_as_and_note(tmp_path):
    fetcher = _fetcher()
    index = tmp_path / "index.json"
    index.write_text(json.dumps({
        "assets": [{
            "id": "sofa_02",
            "selected": "keep",
            "use_as": "sofa",
            "note": "tufted leather, use for classic living rooms",
        }],
        "failures": [{
            "id": "GothicBed_01",
            "selected": "skip",
            "use_as": None,
            "note": "too ornate",
        }],
    }), encoding="utf-8")
    previous = fetcher.load_selection(index)
    fresh = {"id": "sofa_02", "selected": None, "use_as": None, "note": None, "name": "Sofa 02"}
    failed = {"id": "GothicBed_01", "error": "timeout"}
    newcomer = {"id": "dining_table", "name": "Dining Table"}
    fetcher.apply_selection(fresh, previous)
    fetcher.apply_selection(failed, previous)
    fetcher.apply_selection(newcomer, previous)
    assert fresh["selected"] == "keep"
    assert fresh["use_as"] == "sofa"
    assert fresh["note"] == "tufted leather, use for classic living rooms"
    assert failed["selected"] == "skip" and failed["note"] == "too ornate" and failed["use_as"] is None
    assert newcomer["selected"] is None and newcomer["use_as"] is None and newcomer["note"] is None
    assert "sofa" in FURNITURE_TYPES


def test_committed_review_index_is_valid():
    """Unique ids, CC0, files on disk, selection values. Reads the checkout only."""
    assert INDEX_PATH.is_file(), "library/review/index.json is missing; run scripts/fetch_furniture_review.py"
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    assert index["licence"] == "CC0"
    assert index["licence_url"] == "https://polyhaven.com/license"
    assets = index["assets"]
    assert assets, "the review pack has no assets"
    ids = [asset["id"] for asset in assets]
    assert len(ids) == len(set(ids))
    for asset in assets:
        assert asset["licence"] == "CC0"
        assert asset["licence_url"] == "https://polyhaven.com/license"
        assert asset["selected"] in (None, "keep", "skip")
        assert asset["use_as"] is None or asset["use_as"] in FURNITURE_TYPES
        assert "furniture" in asset["categories"]
        preview = REVIEW / asset["preview"]
        assert preview.is_file(), asset["preview"]
        assert preview.suffix == ".jpg"
        assert preview.read_bytes()[:3] == b"\xff\xd8\xff"
        gltf = REVIEW / asset["gltf"]
        assert gltf.is_file(), asset["gltf"]
        assert gltf.suffix == ".gltf"
        for uri in _gltf_uris(gltf):
            referenced = (gltf.parent / uri).resolve()
            assert str(referenced).startswith(str((REVIEW / "models" / asset["id"]).resolve()))
            assert referenced.is_file(), f"{asset['id']} missing {uri}"
        for rel in asset["files"].values():
            path = REVIEW / rel
            assert path.is_file(), rel
            assert ".." not in Path(rel).parts


def test_review_bins_are_tracked():
    """The global ``*.bin`` gitignore rule must not hide the glTF buffers."""
    index = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    bins = [rel for asset in index["assets"] for rel in asset["files"].values() if rel.endswith(".bin")]
    assert bins, "no .bin files recorded"
    sample = REVIEW / bins[0]
    assert sample.is_file()
    result = subprocess.run(["git", "check-ignore", "-q", "--", str(sample.relative_to(ROOT))], cwd=ROOT)
    assert result.returncode != 0, f"{bins[0]} is gitignored"


def test_setup_allow_list_includes_the_preview_cdn():
    text = (ROOT / "docs" / "setup.md").read_text(encoding="utf-8")
    block = text.split("Allowed domains", 1)[1].split("```", 2)[1]
    assert "cdn.polyhaven.com" in block.splitlines()
    assert "dl.polyhaven.org" in block
    assert "api.polyhaven.com" in block
