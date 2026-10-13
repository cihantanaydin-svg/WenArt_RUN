#!/usr/bin/env python3
"""Download a local Poly Haven furniture review pack into ``library/review/``.

The next session only has the git checkout, not the RunPod volume. This script
stores the real 1k glTF bundles (the ``.gltf``, the ``.bin`` and the textures
the glTF names) and a JPEG product shot of each model whose Poly Haven
``categories`` include ``furniture``. Licence is CC0
(https://polyhaven.com/license). It does not download 3D-FUTURE, HSSD,
Sketchfab, or any other library.

Idempotent: a file whose md5 already matches the API is not downloaded again,
and an existing JPEG preview is kept. ``selected``, ``use_as`` and ``note``
already written in ``library/review/index.json`` are copied onto the new index
(including rows that failed last time).

A model that fails is recorded under ``failures`` and the process exits 1
when any download failed. Listing the catalogue is required; if that call
fails, nothing is written and the process exits 1.

Usage: ``python scripts/fetch_furniture_review.py``
"""
from __future__ import annotations

import hashlib
import json
import sys
import traceback
import urllib.parse
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from PIL import Image

from wenart.assets import polyhaven, web
from wenart.assets.models import model_gltf
from wenart.furniture.catalog import CATALOG_PATH, FURNITURE_TYPES

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "library" / "review"
INDEX_PATH = REVIEW / "index.json"
GALLERY_PATH = REVIEW / "GALLERY.md"
README_PATH = REVIEW / "README.md"
PREVIEW_DIR = REVIEW / "previews"
MODELS_DIR = REVIEW / "models"

LICENCE = "CC0"
LICENCE_URL = "https://polyhaven.com/license"
SIZE = "1k"
PREVIEW_URL = "https://cdn.polyhaven.com/asset_img/primary/{id}.png?height=720"
MAX_EDGE = 960
JPEG_QUALITY = 82
MAX_FILE_BYTES = 90 * 1024 * 1024  # stay under GitHub's 100 MB file limit
ID_OK = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-")
SELECTION = ("selected", "use_as", "note")
AXES = {
    "dimensions_api_mm": "model-frame millimetres (x, y, z of the Poly Haven source file)",
    "bbox_m": "catalogue piece-frame [width, depth, height] in metres after the front-axis fix",
}


class FetchFailed(RuntimeError):
    """One model could not be stored completely."""


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_furniture(record: dict) -> bool:
    """True when the listing ``categories`` list contains the token ``furniture``."""
    cats = record.get("categories") or []
    return isinstance(cats, list) and "furniture" in cats


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    part = path.with_suffix(path.suffix + ".part")
    part.write_text(text, encoding="utf-8")
    part.replace(path)


def catalogue_by_id(path: Path = CATALOG_PATH) -> dict[str, dict]:
    """Poly Haven rows of ``catalog.json``, keyed by id. Parametric rows have no id."""
    out = {}
    for entry in load_json(path).get("entries", []):
        asset_id = entry.get("id")
        if isinstance(asset_id, str) and asset_id:
            out[asset_id] = entry
    return out


def blank_selection() -> dict:
    return {"selected": None, "use_as": None, "note": None}


def load_selection(path: Path = INDEX_PATH) -> dict[str, dict]:
    """``selected`` / ``use_as`` / ``note`` already chosen, keyed by id.

    Reads both ``assets`` and ``failures``, so a model that failed last run
    keeps a choice made before that failure.
    """
    if not path.is_file():
        return {}
    data = load_json(path)
    found: dict[str, dict] = {}
    for section in ("assets", "failures"):
        for row in data.get(section) or []:
            asset_id = row.get("id")
            if not isinstance(asset_id, str):
                continue
            found[asset_id] = {key: row.get(key) if key in row else None for key in SELECTION}
    return found


def apply_selection(row: dict, previous: dict[str, dict]) -> dict:
    """Copy a prior choice onto ``row``. A new id starts unset."""
    chosen = previous.get(row["id"], blank_selection())
    for key in SELECTION:
        row[key] = chosen.get(key)
    return row


def check_id(asset_id: str) -> None:
    if not asset_id or any(ch not in ID_OK for ch in asset_id):
        raise FetchFailed(f"refusing asset id {asset_id!r}")


def safe_relative(rel: str) -> Path:
    """A glTF include path that stays inside the model folder."""
    path = Path(rel)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise FetchFailed(f"refusing include path {rel!r}")
    return path


def md5_file(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_download(url: str, path: Path, expected_md5: str | None) -> None:
    """Download ``url`` to ``path`` unless the file is already there with the same md5."""
    if path.is_file() and expected_md5 and md5_file(path) == expected_md5:
        _check_size(path)
        return
    web.download(url, path, expected_md5=expected_md5, timeout=180)
    _check_size(path)


def _check_size(path: Path) -> None:
    size = path.stat().st_size
    if size > MAX_FILE_BYTES:
        raise FetchFailed(f"{path.name} is {size} bytes, over the {MAX_FILE_BYTES} byte cap")
    if size <= 0:
        raise FetchFailed(f"{path.name} is empty")


def preview_is_jpeg(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 500:
        return False
    with path.open("rb") as fh:
        return fh.read(3) == b"\xff\xd8\xff"


def save_preview(asset_id: str, dest: Path) -> None:
    """Product shot (not the albedo) as a JPEG, longest edge at most 960 px."""
    if preview_is_jpeg(dest):
        return
    url = PREVIEW_URL.format(id=urllib.parse.quote(asset_id, safe=""))
    raw = web.get_bytes(url, timeout=120)
    image = Image.open(BytesIO(raw))
    image = image.convert("RGBA")
    canvas = Image.new("RGB", image.size, (0, 0, 0))
    canvas.paste(image, mask=image.getchannel("A"))
    longest = max(canvas.size)
    if longest > MAX_EDGE:
        scale = MAX_EDGE / longest
        canvas = canvas.resize((max(1, round(canvas.width * scale)), max(1, round(canvas.height * scale))),
                               Image.Resampling.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(".jpg.part")
    canvas.save(part, "JPEG", quality=JPEG_QUALITY, optimize=True)
    part.replace(dest)
    if not preview_is_jpeg(dest):
        raise FetchFailed(f"preview for {asset_id} is not a JPEG")


def gltf_uris(gltf_path: Path) -> list[str]:
    """Relative URIs named by the glTF buffers and images (data URIs skipped)."""
    doc = json.loads(gltf_path.read_text(encoding="utf-8"))
    uris = []
    for key in ("buffers", "images"):
        for item in doc.get(key) or []:
            uri = item.get("uri") if isinstance(item, dict) else None
            if not isinstance(uri, str) or not uri or uri.startswith("data:"):
                continue
            uris.append(urllib.parse.unquote(uri.split("?", 1)[0]))
    return uris


def fetch_model_bundle(asset_id: str) -> dict:
    """Download the 1k glTF and every include. Returns paths relative to ``REVIEW``."""
    table = polyhaven.files(asset_id)
    try:
        item = model_gltf(table, SIZE)
    except KeyError as exc:
        raise FetchFailed(str(exc)) from exc
    folder = MODELS_DIR / asset_id
    gltf_name = f"{asset_id}_{SIZE}.gltf"
    files: dict[str, str] = {}
    md5s: dict[str, str] = {}
    targets = [("gltf", folder / gltf_name, item)]
    for rel, inc in (item.get("include") or {}).items():
        targets.append((rel, folder / safe_relative(rel), inc))
    for key, target, inc in targets:
        url = inc.get("url")
        if not url:
            raise FetchFailed(f"{asset_id}: {key} has no url")
        ensure_download(url, target, inc.get("md5"))
        files[key] = target.relative_to(REVIEW).as_posix()
        if inc.get("md5"):
            md5s[key] = inc["md5"]
    gltf_path = folder / gltf_name
    for uri in gltf_uris(gltf_path):
        uri_path = folder / safe_relative(uri)
        if not uri_path.is_file():
            raise FetchFailed(f"{asset_id}: glTF references missing file {uri}")
    return {"gltf": files["gltf"], "files": files, "md5": md5s}


def catalogue_fields(entry: dict | None) -> dict:
    if not entry:
        return {}
    out = {
        "catalogue_type": entry.get("type"),
        "catalogue_styles": entry.get("styles"),
        "catalogue_audit": entry.get("audit"),
    }
    if entry.get("bbox_m") is not None:
        out["bbox_m"] = entry["bbox_m"]
    return out


def build_asset(asset_id: str, record: dict, catalogue: dict[str, dict], previous: dict[str, dict]) -> dict:
    check_id(asset_id)
    preview_rel = f"previews/{asset_id}.jpg"
    save_preview(asset_id, REVIEW / preview_rel)
    bundle = fetch_model_bundle(asset_id)
    row = {
        "id": asset_id,
        "name": record.get("name"),
        "selected": None,
        "use_as": None,
        "note": None,
        "authors": record.get("authors") or {},
        "categories": record.get("categories") or [],
        "category": record.get("category"),
        "tags": record.get("tags") or [],
        "description": record.get("description") or "",
        "dimensions_api_mm": record.get("dimensions"),
        "polycount": record.get("polycount"),
        "licence": LICENCE,
        "licence_url": LICENCE_URL,
        "page_url": f"https://polyhaven.com/a/{asset_id}",
        "preview": preview_rel,
        "gltf": bundle["gltf"],
        "files": bundle["files"],
        "md5": bundle["md5"],
        "resolution": SIZE,
    }
    row.update(catalogue_fields(catalogue.get(asset_id)))
    return apply_selection(row, previous)


def author_counts(assets: list[dict]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for asset in assets:
        authors = asset.get("authors") or {}
        names = list(authors) if isinstance(authors, dict) else list(authors)
        if not names:
            names = ["(author not listed)"]
        for name in names:
            counts[str(name)] = counts.get(str(name), 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))


def write_readme(assets: list[dict], failures: list[dict], fetched_utc: str) -> None:
    credits = "\n".join(f"- {name} ({count})" for name, count in author_counts(assets))
    types = ", ".join(f"`{name}`" for name in FURNITURE_TYPES)
    fail_note = ""
    if failures:
        names = "`, `".join(row["id"] for row in failures)
        fail_note = (
            f"\n{len(failures)} model(s) failed and are listed in `index.json` under `failures` "
            f"(`{names}`). Re-run the fetcher to retry them.\n"
        )
    text = f"""# Poly Haven furniture review pack

Local copies of Poly Haven models whose `categories` include `furniture`.
The meshes are the real {SIZE} glTF downloads (the `.gltf`, the `.bin`, and the textures the glTF names).
The JPEGs in `previews/` are product shots on black, not albedo maps.
Nothing in this folder was generated, and no non-commercial library was downloaded.

Fetched {fetched_utc}. {len(assets)} model(s) stored. Licence: **CC0** ({LICENCE_URL}).
Attribution is not required. It is appreciated. Authors below are the names on the Poly Haven listing (`authors` on each row of `index.json`).

{fail_note}
## How to select

1. Open [`GALLERY.md`](GALLERY.md) and look at the previews.
2. Edit [`index.json`](index.json). On each asset set:
   - `selected`: `null`, `"keep"`, or `"skip"`
   - `use_as`: `null`, or one pipeline type: {types}
   - `note`: a short string, or `null`
3. Re-running `python scripts/fetch_furniture_review.py` keeps those three fields.

## Axes

- `dimensions_api_mm`: {AXES["dimensions_api_mm"]}.
- `bbox_m`: {AXES["bbox_m"]}. Copied from `wenart/furniture/catalog.json` when that id is already in the catalogue, together with `catalogue_type`, `catalogue_styles` and `catalogue_audit`.

## Files

- `previews/<id>.jpg` — product shot
- `models/<id>/<id>_1k.gltf` — plus the include-relative textures and `<id>.bin`
- `index.json` — the catalogue the next session edits
- `GALLERY.md` — the same models, one image each

## Credit

CC0 models. Attribution appreciated.

{credits}
"""
    README_PATH.write_text(text, encoding="utf-8")


def write_gallery(assets: list[dict], fetched_utc: str) -> None:
    lines = [
        "# Furniture review gallery",
        "",
        f"Poly Haven CC0 product shots ({len(assets)} models, fetched {fetched_utc}).",
        "These are the primary renders, not albedo textures.",
        f"`dimensions_api_mm` is {AXES['dimensions_api_mm']}.",
        f"`bbox_m`, when present, is {AXES['bbox_m']}.",
        "Set `selected`, `use_as` and `note` in `index.json`.",
        "",
    ]
    for asset in assets:
        authors = asset.get("authors") or {}
        if isinstance(authors, dict):
            credit = ", ".join(f"{name} ({role})" for name, role in authors.items())
        else:
            credit = ", ".join(str(name) for name in authors)
        dims = asset.get("dimensions_api_mm")
        dim_text = "n/a" if not dims else " × ".join(str(round(v)) if isinstance(v, float) else str(v) for v in dims)
        cat = asset.get("catalogue_type") or "not in the pipeline catalogue"
        styles = asset.get("catalogue_styles")
        style_text = ", ".join(styles) if styles else "—"
        lines += [
            f"## {asset['id']}",
            "",
            f"![{asset['id']}]({asset['preview']})",
            "",
            f"- name: {asset.get('name')}",
            f"- author: {credit}",
            f"- catalogue type: {cat}",
            f"- catalogue styles: {style_text}",
            f"- API dimensions (model-frame mm): {dim_text}",
            f"- selected: {json.dumps(asset.get('selected'))}",
            f"- use_as: {json.dumps(asset.get('use_as'))}",
            "",
        ]
    GALLERY_PATH.write_text("\n".join(lines), encoding="utf-8")


def furniture_records(listing: dict) -> list[tuple[str, dict]]:
    rows = [(asset_id, record) for asset_id, record in listing.items() if is_furniture(record)]
    return sorted(rows, key=lambda item: (item[0].lower(), item[0]))


def run() -> int:
    print(f"listing {polyhaven.API}/assets?type=models", flush=True)
    try:
        listing = polyhaven.list_assets("models")
    except (web.HTTPStatusError, web.NetworkError) as exc:
        print(f"failed to list models: {exc}", file=sys.stderr)
        return 1
    chosen = furniture_records(listing)
    print(f"{len(listing)} models, {len(chosen)} with category furniture", flush=True)
    catalogue = catalogue_by_id()
    previous = load_selection()
    assets: list[dict] = []
    failures: list[dict] = []
    for index, (asset_id, record) in enumerate(chosen, start=1):
        print(f"[{index}/{len(chosen)}] {asset_id}", flush=True)
        try:
            assets.append(build_asset(asset_id, record, catalogue, previous))
        except (FetchFailed, web.HTTPStatusError, web.NetworkError, OSError, KeyError, ValueError) as exc:
            message = f"{type(exc).__name__}: {exc}"
            print(f"  FAILED {asset_id}: {message}", file=sys.stderr, flush=True)
            failure = {"id": asset_id, "name": record.get("name"), "error": message}
            apply_selection(failure, previous)
            failures.append(failure)
        except Exception as exc:  # one bad model must not drop the rest
            message = f"{type(exc).__name__}: {exc}"
            print(f"  FAILED {asset_id}: {message}", file=sys.stderr, flush=True)
            traceback.print_exc()
            failure = {"id": asset_id, "name": record.get("name"), "error": message}
            apply_selection(failure, previous)
            failures.append(failure)
    fetched_utc = now_utc()
    index = {
        "source": "polyhaven",
        "licence": LICENCE,
        "licence_url": LICENCE_URL,
        "resolution": SIZE,
        "fetched_utc": fetched_utc,
        "axes": AXES,
        "selection": {
            "selected": 'null | "keep" | "skip"',
            "use_as": "null or a name in wenart.furniture.catalog.FURNITURE_TYPES",
            "note": "null or a short string",
        },
        "count": len(assets),
        "assets": assets,
        "failures": failures,
    }
    write_json(INDEX_PATH, index)
    write_gallery(assets, fetched_utc)
    write_readme(assets, failures, fetched_utc)
    print(f"wrote {len(assets)} assets, {len(failures)} failures -> {INDEX_PATH}", flush=True)
    return 1 if failures else 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
