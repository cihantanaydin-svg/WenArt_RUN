"""Bake-off CLI: OCR engines and vision-language models on the synthetic raster pages.

    python -m wenart.recognition.bakeoff --projects projects --out results/bakeoff \
        --models Qwen/Qwen3-VL-8B-Instruct zai-org/GLM-4.6V-Flash

For every raster page (``kind`` scan or photo in ``<project>/truth/pages.json``):

- ``<out>/<project>_<page>_ocr.json``: PaddleOCR and Tesseract items with scores.
- ``<out>/<project>_<page>_<model>.json``: the page-class, room-label and symbol
  answers of one model with scores and latency (``<model>`` = last part of the
  Hugging Face ID).
- ``<out>/<project>_<page>_<model>_tiled.json`` (``--stage vlm --tiled``): the
  symbol answer of the tiled pass (``wenart.recognition.tiles``: crop to the
  drawing, one call per tile at full resolution, boxes mapped back to page
  pixels, duplicates merged across tiles), scored like the plain symbol task.
- ``<out>/<project>_<page>_twopass.json``: two-pass agreement of the first two
  models, computed from the saved answers (no extra calls). A page where one
  model's symbol answer failed (``data`` null) gets a record with
  ``not_computed`` and no scores: a pass that never happened is not
  "zero proposals"; the summary counts these pages as not computed.
- ``<out>/<project>_<page>_<who>.jpg``: small debug images (truth green, model
  symbols orange, OCR blue), each <= 300 KB.
- ``<out>/summary.json`` and ``<out>/summary.md``.

Resumable: a page whose result JSON exists is skipped (``--retry-errors`` re-runs
the ones that recorded an error). The vLLM server serves one model at a time;
``scripts/jobs/bakeoff.sh`` starts and stops it per model and calls this CLI
with ``--stage vlm --models <that model>``. Models that are not served are
reported and skipped, never guessed.

``--stage dwg`` runs the LibreDWG round trip (``dxf2dwg`` then ``dwg2dxf``) on the
synthetic DXFs and compares entity counts (``<out>/dwg_roundtrip.json``).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

from wenart.recognition import detect, metrics, ocr, tiles, vlm_client
from wenart.recognition.schemas import TASKS

RASTER_KINDS = ("scan", "photo")
MODEL_TASKS = ("page_class", "room_labels", "symbols")
DEBUG_WIDTH = 1200
DEBUG_MAX_BYTES = 300 * 1024
DEFAULT_MODELS = ("Qwen/Qwen3-VL-8B-Instruct", "zai-org/GLM-4.6V-Flash")
STAGES = ("all", "dwg", "ocr", "vlm", "twopass", "summary")


# --------------------------------------------------------------------------
# Pages and truth
# --------------------------------------------------------------------------

@dataclass
class RasterPage:
    project: str
    file: str
    page: int
    kind: str
    image_path: Path
    truth: dict

    @property
    def slug(self) -> str:
        """``synthetic-02_plan_scan`` (plus ``_p<n>`` for a page > 1 of a multi-page file)."""
        stem = Path(self.file).stem
        suffix = f"_p{self.page}" if self.page > 1 else ""
        return f"{self.project}_{stem}{suffix}"

    def truth_texts(self, role: Optional[str] = None) -> list[str]:
        return [t["text"] for t in self.truth.get("texts", []) if role is None or t.get("role") == role]

    def truth_symbols(self) -> list[dict]:
        return [{"type": s["type"], "box": s["box"], "id": s.get("id")} for s in self.truth.get("symbols", [])]


def model_slug(model: str) -> str:
    """``Qwen/Qwen3-VL-8B-Instruct`` -> ``Qwen3-VL-8B-Instruct`` (file-name safe)."""
    return model.rstrip("/").split("/")[-1].replace(" ", "_")


def raster_pages(projects_dir: str | Path, kinds: Sequence[str] = RASTER_KINDS) -> list[RasterPage]:
    """All scan/photo pages of every project folder that has ``truth/pages.json``."""
    pages = []
    for project_dir in sorted(Path(projects_dir).iterdir()):
        pages_json = project_dir / "truth" / "pages.json"
        if not pages_json.is_file():
            continue
        for rec in json.loads(pages_json.read_text(encoding="utf-8"))["pages"]:
            if rec.get("kind") not in kinds:
                continue
            image = project_dir / rec["file"]
            if not image.is_file():
                continue
            pages.append(RasterPage(project_dir.name, rec["file"], int(rec.get("page", 1)), rec["kind"], image, rec))
    return pages


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def has_result(path: Path, retry_errors: bool) -> bool:
    """True when the page can be skipped: the JSON exists (and has no error, with --retry-errors)."""
    if not path.is_file():
        return False
    if not retry_errors:
        return True
    data = read_json(path)
    return not data.get("has_errors")


# --------------------------------------------------------------------------
# Debug images
# --------------------------------------------------------------------------

def draw_debug(image_path: Path, out_jpg: Path, layers: Sequence[tuple[str, Sequence[dict], str]],
               width: int = DEBUG_WIDTH, max_bytes: int = DEBUG_MAX_BYTES) -> Path:
    """Draw boxes over a downscaled page and save a JPEG under ``max_bytes``.

    ``layers`` = ``[(name, items, colour)]``; each item has ``box`` and ``type``/``text``.
    """
    from PIL import Image, ImageDraw
    img = Image.open(image_path).convert("RGB")
    scale = width / img.width if img.width > width else 1.0
    if scale != 1.0:
        img = img.resize((width, max(1, round(img.height * scale))), Image.LANCZOS)
    draw = ImageDraw.Draw(img)
    for name, items, colour in layers:
        for item in items:
            x0, y0, x1, y1 = (v * scale for v in item["box"])
            draw.rectangle([x0, y0, x1, y1], outline=colour, width=2)
            label = item.get("type") or item.get("text") or item.get("label_raw") or ""
            if label:
                draw.text((x0 + 2, max(0, y0 - 11)), str(label)[:24], fill=colour)
    legend_y = 4
    for name, _, colour in layers:
        draw.text((4, legend_y), name, fill=colour)
        legend_y += 12
    out_jpg.parent.mkdir(parents=True, exist_ok=True)
    quality = 85
    while True:
        img.save(out_jpg, format="JPEG", quality=quality, optimize=True)
        if out_jpg.stat().st_size <= max_bytes or quality <= 30:
            break
        quality -= 10
    return out_jpg


# --------------------------------------------------------------------------
# OCR stage
# --------------------------------------------------------------------------

def score_texts(items: Sequence[dict], page: RasterPage) -> dict:
    texts = [it["text"] for it in items]
    return {
        "all_texts": metrics.text_scores(texts, page.truth_texts()),
        "room_labels": metrics.text_scores(texts, page.truth_texts("room_label")),
    }


def run_ocr_page(page: RasterPage, out_dir: Path, *, use_paddle: bool, use_tesseract: bool,
                 device: Optional[str], retry_errors: bool) -> dict:
    """OCR one page with both engines, score, write JSON + debug image. Skips existing results."""
    out_json = out_dir / f"{page.slug}_ocr.json"
    if has_result(out_json, retry_errors):
        print(f"  skip (exists): {out_json.name}")
        return read_json(out_json)
    record = {"project": page.project, "file": page.file, "page": page.page, "kind": page.kind,
              "engines": {}, "errors": {}, "has_errors": False}
    if use_paddle:
        t0 = time.monotonic()
        try:
            items = ocr.ocr_paddle(page.image_path, device=device)
            record["engines"]["paddleocr"] = {"items": items, "latency_s": round(time.monotonic() - t0, 2),
                                              "scores": score_texts(items, page)}
        except Exception as exc:  # noqa: BLE001 - recorded in the result
            record["errors"]["paddleocr"] = f"{type(exc).__name__}: {exc}"
    if use_tesseract:
        t0 = time.monotonic()
        try:
            items = ocr.ocr_tesseract(page.image_path)
            record["engines"]["tesseract"] = {"items": items, "latency_s": round(time.monotonic() - t0, 2),
                                              "scores": score_texts(items, page)}
        except Exception as exc:  # noqa: BLE001
            record["errors"]["tesseract"] = f"{type(exc).__name__}: {exc}"
    paddle_items = record["engines"].get("paddleocr", {}).get("items", [])
    tess_items = record["engines"].get("tesseract", {}).get("items", [])
    if paddle_items and tess_items:
        checked = ocr.cross_check(paddle_items, tess_items)
        record["cross_check"] = {"agree": sum(1 for c in checked if c["agrees"]), "n_primary": len(checked)}
    record["has_errors"] = bool(record["errors"])
    write_json(out_json, record)
    layers = [("truth texts", [{"box": t["box"], "text": t["text"]} for t in page.truth.get("texts", [])], "#00a000")]
    if paddle_items:
        layers.append(("paddleocr", paddle_items, "#0050ff"))
    elif tess_items:
        layers.append(("tesseract", tess_items, "#0050ff"))
    draw_debug(page.image_path, out_dir / f"{page.slug}_ocr.jpg", layers)
    for engine, data in record["engines"].items():
        rl = data["scores"]["room_labels"]
        print(f"  {engine}: room labels {rl['tp']}/{rl['tp'] + rl['fn']}, {data['latency_s']} s")
    for engine, err in record["errors"].items():
        print(f"  {engine}: ERROR {err}")
    return record


# --------------------------------------------------------------------------
# VLM stage
# --------------------------------------------------------------------------

def score_model_tasks(results: dict[str, vlm_client.VLMResult], page: RasterPage) -> dict:
    """Scores of the three tasks against the truth of ``page`` (missing answers score 0)."""
    scores: dict = {"latency_s": {}, "errors": {}}
    for task, res in results.items():
        scores["latency_s"][task] = round(res.latency_s, 2)
        if res.error:
            scores["errors"][task] = res.error
    pc = results.get("page_class")
    scores["page_class"] = metrics.page_class_scores(pc.data if pc and pc.data else None, page.truth)
    rl = results.get("room_labels")
    labels = [it["label_raw"] for it in rl.data["items"]] if rl and rl.data else []
    scores["room_labels"] = metrics.text_scores(labels, page.truth_texts("room_label"))
    sy = results.get("symbols")
    symbols = sy.data["items"] if sy and sy.data else []
    scores["symbols"] = metrics.symbol_scores(symbols, page.truth_symbols())
    return scores


def run_model_page(page: RasterPage, model: str, client: vlm_client.VLMClient, out_dir: Path, *,
                   tasks: Sequence[str] = MODEL_TASKS, retry_errors: bool) -> dict:
    """Run the tasks of one model on one page, score, write JSON + debug image."""
    out_json = out_dir / f"{page.slug}_{model_slug(model)}.json"
    if has_result(out_json, retry_errors):
        print(f"  skip (exists): {out_json.name}")
        return read_json(out_json)
    results: dict[str, vlm_client.VLMResult] = {}
    for task in tasks:
        res = client.run_task(task, page.image_path)
        results[task] = res
        status = "ok" if res.data is not None else f"ERROR {res.error}"
        print(f"  {model_slug(model)} {task}: {res.latency_s:.1f} s, {status}")
    scores = score_model_tasks(results, page)
    record = {"project": page.project, "file": page.file, "page": page.page, "kind": page.kind, "model": model,
              "tasks": {task: res.to_dict() for task, res in results.items()},
              "scores": scores, "has_errors": bool(scores["errors"])}
    write_json(out_json, record)
    sy = results.get("symbols")
    rl = results.get("room_labels")
    layers = [("truth symbols", page.truth_symbols(), "#00a000")]
    if sy and sy.data:
        layers.append((f"{model_slug(model)} symbols", sy.data["items"], "#ff7f00"))
    if rl and rl.data:
        layers.append((f"{model_slug(model)} labels", rl.data["items"], "#0050ff"))
    draw_debug(page.image_path, out_dir / f"{page.slug}_{model_slug(model)}.jpg", layers)
    return record


# --------------------------------------------------------------------------
# Tiled symbol pass (crop to the drawing, one call per tile)
# --------------------------------------------------------------------------

def tiled_symbol_items(image_path: Path, client, *, tile_px: int = tiles.DEFAULT_TILE_PX,
                       overlap: float = tiles.DEFAULT_OVERLAP) -> dict:
    """Run the ``symbols`` task on every tile of the drawing area and merge the answers.

    The client receives each tile as a PIL crop, so it maps the model's 0..1000
    grid to the CROP size (``VLMResult.page_size`` is the crop size); the boxes
    are then shifted by the tile's top-left corner into page pixels. The crop is
    not downscaled as long as the tile side is <= the client's ``max_side``
    (1024 px tiles against the default 1600 px). Nothing is dropped: a tile
    whose call failed is recorded with its error and contributes no items. A
    proposal whose box touches an inner tile edge (the tile cut the symbol) is
    marked ``edge_clipped`` so the merge can fold it into the whole view from
    the neighbouring tile.

    Returns ``{"extent", "extent_info" (dropped page frames and the ink share
    of the box), "tile_px", "overlap", "tiles": [per-tile records], "items":
    merged items in page pixels, "merge": stats, "latency_s", "errors"}``.
    """
    img = vlm_client.load_image(image_path)
    extent_info = tiles.drawing_extent_info(img)
    extent = extent_info.pop("extent")
    boxes = tiles.tiles(extent, tile_px, overlap)
    raw_items: list[dict] = []
    tile_records: list[dict] = []
    errors: dict[str, str] = {}
    latency = 0.0
    for index, tile in enumerate(boxes):
        crop = img.crop(tuple(int(v) for v in tile))
        res = client.run_task("symbols", crop)
        latency += res.latency_s
        n_items = n_clipped = 0
        if res.data is not None:
            for item in res.data.get("items", []):
                moved = dict(item)
                moved["box"] = tiles.offset_box(item["box"], tile[0], tile[1])
                moved["tile"] = index
                moved["edge_clipped"] = tiles.touches_inner_edge(item["box"], tile, extent)
                n_clipped += moved["edge_clipped"]
                raw_items.append(moved)
                n_items += 1
        else:
            errors[f"tile_{index}"] = res.error or "no answer"
        tile_records.append({"index": index, "box": [int(v) for v in tile], "n_items": n_items,
                             "n_clipped": n_clipped, "latency_s": round(res.latency_s, 3), "error": res.error,
                             "sent_size": list(res.image_size), "crop_size": list(res.page_size)})
    merged, stats = tiles.merge_tile_items(raw_items)
    return {"extent": [int(v) for v in extent], "extent_info": extent_info, "tile_px": tile_px, "overlap": overlap,
            "tiles": tile_records, "items": merged, "merge": stats, "latency_s": round(latency, 3), "errors": errors}


def run_symbols_tiled(page: RasterPage, model: str, client, out_dir: Path, *,
                      tile_px: int = tiles.DEFAULT_TILE_PX, overlap: float = tiles.DEFAULT_OVERLAP,
                      retry_errors: bool = False) -> dict:
    """The tiled symbol pass of one model on one page: JSON + debug image, resumable.

    Writes ``<slug>_<model>_tiled.json`` with the per-tile records, the merged
    symbols (page pixels, each with the ``tiles`` that saw it) and the symbol
    scores against the truth, plus ``<slug>_<model>_tiled.jpg`` (truth green,
    tiles grey, merged symbols orange).
    """
    out_json = out_dir / f"{page.slug}_{model_slug(model)}_tiled.json"
    if has_result(out_json, retry_errors):
        print(f"  skip (exists): {out_json.name}")
        return read_json(out_json)
    run = tiled_symbol_items(page.image_path, client, tile_px=tile_px, overlap=overlap)
    truth = page.truth_symbols()
    scores = {"symbols": metrics.symbol_scores(run["items"], truth),
              "latency_s": {"symbols_tiled": run["latency_s"]},
              "errors": run["errors"], "n_tiles": len(run["tiles"]), "merge": run["merge"]}
    record = {"project": page.project, "file": page.file, "page": page.page, "kind": page.kind, "model": model,
              "tiled": True, "extent": run["extent"], "extent_info": run["extent_info"],
              "tile_px": run["tile_px"], "overlap": run["overlap"],
              "tiles": run["tiles"], "symbols": {"items": run["items"], "merge": run["merge"]},
              "scores": scores, "has_errors": bool(run["errors"])}
    write_json(out_json, record)
    draw_debug(page.image_path, out_dir / f"{page.slug}_{model_slug(model)}_tiled.jpg", [
        ("tiles", [{"box": t["box"], "type": f"tile {t['index']}"} for t in run["tiles"]], "#909090"),
        ("truth symbols", truth, "#00a000"),
        (f"{model_slug(model)} symbols (tiled)", run["items"], "#ff7f00"),
    ])
    ov = scores["symbols"]["overall"]
    print(f"  {model_slug(model)} symbols (tiled): {len(run['tiles'])} tiles, {run['merge']['n_input']} proposals -> "
          f"{run['merge']['n_merged']} symbols, recall {ov['recall']:.2f} precision {ov['precision']:.2f}, "
          f"{run['latency_s']:.1f} s, {len(run['errors'])} tile errors")
    return record


# --------------------------------------------------------------------------
# Two-pass stage (from saved answers)
# --------------------------------------------------------------------------

def run_two_pass_page(page: RasterPage, model_a: str, model_b: str, out_dir: Path) -> Optional[dict]:
    """Combine the saved symbol answers of two models; None when one of them is missing.

    When a model's symbol answer failed (``data`` null: call error or schema
    rejection), the record only says ``not_computed`` (which model, which error)
    and carries no agreement scores, so the summary cannot mistake a failed pass
    for a pass that proposed nothing.
    """
    paths = [out_dir / f"{page.slug}_{model_slug(m)}.json" for m in (model_a, model_b)]
    if not all(p.is_file() for p in paths):
        print(f"  two-pass: missing model results for {page.slug}")
        return None
    answers = []
    failed = []
    for model, path in zip((model_a, model_b), paths):
        symbols_task = read_json(path).get("tasks", {}).get("symbols") or {}
        data = symbols_task.get("data")
        if data is None:
            failed.append(f"{model} symbols: {symbols_task.get('error') or 'no answer'}")
        answers.append(data["items"] if data else [])
    base = {"project": page.project, "file": page.file, "page": page.page, "kind": page.kind,
            "models": [model_a, model_b]}
    if failed:
        reason = "; ".join(failed)
        record = dict(base, symbols=[], not_computed=reason)
        write_json(out_dir / f"{page.slug}_twopass.json", record)
        print(f"  two-pass: not computed for {page.slug} ({reason})")
        return record
    symbols = detect.combine(answers[0], answers[1], model_a, model_b, page.file)
    verified = [s for s in symbols if s["status"] == "verified"]
    truth = page.truth_symbols()
    record = dict(base, symbols=symbols, n_verified=len(verified), n_unverified=len(symbols) - len(verified),
                  verified=metrics.symbol_scores(verified, truth), all=metrics.symbol_scores(symbols, truth))
    write_json(out_dir / f"{page.slug}_twopass.json", record)
    draw_debug(page.image_path, out_dir / f"{page.slug}_twopass.jpg", [
        ("truth symbols", truth, "#00a000"),
        ("verified", verified, "#ff7f00"),
        ("unverified", [s for s in symbols if s["status"] != "verified"], "#d00000"),
    ])
    print(f"  two-pass: {len(verified)} verified, {len(symbols) - len(verified)} unverified; "
          f"verified recall {record['verified']['overall']['recall']:.2f}")
    return record


# --------------------------------------------------------------------------
# Summary stage (from every JSON in the output folder)
# --------------------------------------------------------------------------

def collect_page_results(pages: Sequence[RasterPage], out_dir: Path) -> list[dict]:
    """Per-page records for ``metrics.aggregate`` from the JSON files in ``out_dir``.

    ``two_pass`` is None for pages without a computed two-pass record;
    ``two_pass_not_computed`` then names the reason when a record says so.
    ``tiled`` holds the scores of the tiled symbol pass per model
    (``*_tiled.json``), separate from the plain ``models`` scores.
    """
    page_results = []
    for page in pages:
        entry: dict = {"project": page.project, "file": page.file, "page": page.page, "kind": page.kind,
                       "ocr": {}, "models": {}, "tiled": {}, "two_pass": None, "two_pass_not_computed": None}
        ocr_json = out_dir / f"{page.slug}_ocr.json"
        if ocr_json.is_file():
            for engine, data in read_json(ocr_json).get("engines", {}).items():
                entry["ocr"][engine] = dict(data["scores"], latency_s=data.get("latency_s"))
        for path in sorted(out_dir.glob(f"{page.slug}_*.json")):
            if path.name.endswith(("_ocr.json", "_twopass.json")):
                continue
            data = read_json(path)
            if "model" not in data:
                continue
            if data.get("tiled"):
                entry["tiled"][data["model"]] = data["scores"]
            else:
                entry["models"][data["model"]] = data["scores"]
        two = out_dir / f"{page.slug}_twopass.json"
        if two.is_file():
            data = read_json(two)
            if data.get("not_computed"):
                entry["two_pass_not_computed"] = data["not_computed"]
            else:
                entry["two_pass"] = {k: data[k] for k in ("verified", "all", "n_verified", "n_unverified")}
        page_results.append(entry)
    return page_results


def two_pass_not_computed(page_results: Sequence[dict]) -> dict:
    """``{"pages": n, "reasons": [{"project", "file", "page", "reason"}, ...]}`` for the summary."""
    reasons = [{"project": p.get("project"), "file": p.get("file"), "page": p.get("page"), "reason": p["two_pass_not_computed"]}
               for p in page_results if p.get("two_pass_not_computed")]
    return {"pages": len(reasons), "reasons": reasons}


def summarise_not_computed(not_computed: dict) -> str:
    """Markdown lines listing the pages whose two-pass agreement could not be computed."""
    if not not_computed["pages"]:
        return ""
    lines = ["", "## Two-pass agreement not computed", "",
             f"{not_computed['pages']} page(s) excluded from the two-pass table because one model's symbol "
             "answer failed (a pass that did not happen is not 'zero proposals'):", "",
             "| Project | File | Page | Reason |", "|---|---|---|---|"]
    for r in not_computed["reasons"]:
        lines.append(f"| {r['project']} | {r['file']} | {r['page']} | {r['reason']} |")
    return "\n".join(lines) + "\n"


def write_summary(pages: Sequence[RasterPage], out_dir: Path) -> dict:
    page_results = collect_page_results(pages, out_dir)
    agg = metrics.aggregate(page_results)
    not_computed = two_pass_not_computed(page_results)
    agg["two_pass_not_computed"] = not_computed
    write_json(out_dir / "summary.json", {"aggregate": agg, "pages": page_results})
    text = metrics.summarise(page_results) + summarise_not_computed(not_computed)
    (out_dir / "summary.md").write_text(text, encoding="utf-8")
    print(f"summary: {out_dir / 'summary.md'}")
    return agg


# --------------------------------------------------------------------------
# DWG round trip (LibreDWG)
# --------------------------------------------------------------------------

def entity_counts(dxf_path: Path) -> tuple[dict[str, int], int]:
    """Model-space entity counts per ``type@layer`` plus the number of audit errors (ezdxf recover)."""
    from ezdxf import recover
    doc, auditor = recover.readfile(str(dxf_path))
    counts = Counter(f"{e.dxftype()}@{e.dxf.layer}" for e in doc.modelspace())
    return dict(sorted(counts.items())), len(auditor.errors)


def tool_version(binary: str | Path) -> str:
    try:
        proc = subprocess.run([str(binary), "--version"], capture_output=True, text=True, timeout=30)
        return (proc.stdout or proc.stderr).strip().splitlines()[0] if (proc.stdout or proc.stderr).strip() else "?"
    except (OSError, subprocess.SubprocessError) as exc:
        return f"error: {exc}"


def dwg_roundtrip(dxf_paths: Sequence[Path], out_json: Path, bin_dir: Optional[Path] = None,
                  work_dir: Optional[Path] = None) -> dict:
    """``dxf2dwg`` then ``dwg2dxf`` for every DXF; compare entity counts; write ``out_json``.

    LibreDWG 0.13.3 (programs/dxf2dwg.1, dwg2dxf.1): ``-y`` overwrites, ``-o`` names
    the output, ``--as rNNNN`` picks the version; dxf2dwg writes r2000 by default
    ("Encoding currently only works for R13-R2000"), so the round trip is R2010
    DXF -> R2000 DWG -> DXF.
    """
    dxf2dwg = str(bin_dir / "dxf2dwg") if bin_dir else (shutil.which("dxf2dwg") or "dxf2dwg")
    dwg2dxf = str(bin_dir / "dwg2dxf") if bin_dir else (shutil.which("dwg2dxf") or "dwg2dxf")
    work = work_dir or out_json.parent / "dwg_roundtrip"
    work.mkdir(parents=True, exist_ok=True)
    report = {"dxf2dwg": tool_version(dxf2dwg), "dwg2dxf": tool_version(dwg2dxf), "files": []}
    for dxf in dxf_paths:
        dxf = Path(dxf)
        entry: dict = {"dxf": str(dxf), "ok": False}
        dwg = work / (dxf.stem + ".dwg")
        back = work / (dxf.stem + "_back.dxf")
        try:
            counts_in, audit_in = entity_counts(dxf)
            entry["counts_in"], entry["audit_errors_in"] = counts_in, audit_in
            t0 = time.monotonic()
            p1 = subprocess.run([dxf2dwg, "-y", "-o", str(dwg), str(dxf)], capture_output=True, text=True, timeout=600)
            entry["dxf2dwg_rc"], entry["dxf2dwg_stderr"] = p1.returncode, p1.stderr[-1000:]
            if p1.returncode != 0 or not dwg.is_file():
                raise RuntimeError(f"dxf2dwg failed (rc {p1.returncode})")
            entry["dwg_bytes"] = dwg.stat().st_size
            p2 = subprocess.run([dwg2dxf, "-y", "-o", str(back), str(dwg)], capture_output=True, text=True, timeout=600)
            entry["dwg2dxf_rc"], entry["dwg2dxf_stderr"] = p2.returncode, p2.stderr[-1000:]
            if p2.returncode != 0 or not back.is_file():
                raise RuntimeError(f"dwg2dxf failed (rc {p2.returncode})")
            entry["seconds"] = round(time.monotonic() - t0, 2)
            counts_back, audit_back = entity_counts(back)
            entry["counts_back"], entry["audit_errors_back"] = counts_back, audit_back
            missing = {k: v - counts_back.get(k, 0) for k, v in counts_in.items() if counts_back.get(k, 0) != v}
            extra = {k: v for k, v in counts_back.items() if k not in counts_in}
            entry["missing"], entry["extra"] = missing, extra
            entry["ok"] = not missing and not extra
        except Exception as exc:  # noqa: BLE001 - every failure is reported in the JSON
            entry["error"] = f"{type(exc).__name__}: {exc}"
        report["files"].append(entry)
        print(f"  {dxf.name}: {'ok' if entry['ok'] else 'DIFF/ERROR'} {entry.get('error', '')} "
              f"missing={entry.get('missing', {})} extra={entry.get('extra', {})}")
    report["all_ok"] = all(f["ok"] for f in report["files"]) if report["files"] else False
    write_json(out_json, report)
    return report


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--projects", default="projects", help="folder with the synthetic projects")
    ap.add_argument("--out", default="results/bakeoff", help="output folder")
    ap.add_argument("--models", nargs="*", default=list(DEFAULT_MODELS), help="Hugging Face model IDs")
    ap.add_argument("--server", default=vlm_client.DEFAULT_BASE_URL, help="vLLM OpenAI-compatible base URL")
    ap.add_argument("--stage", choices=STAGES, default="all")
    ap.add_argument("--tasks", nargs="*", default=list(MODEL_TASKS), choices=TASKS, help="model tasks to run")
    ap.add_argument("--no-paddle", action="store_true", help="skip PaddleOCR")
    ap.add_argument("--no-tesseract", action="store_true", help="skip Tesseract")
    ap.add_argument("--ocr-device", default=None, help="PaddleOCR device, e.g. gpu:0 or cpu (default: auto)")
    ap.add_argument("--max-side", type=int, default=vlm_client.DEFAULT_MAX_SIDE, help="longest image side sent to the model (0 = full)")
    ap.add_argument("--tiled", action="store_true",
                    help="vlm stage: also run the tiled symbol pass (crop to the drawing, one call per tile)")
    ap.add_argument("--tile-px", type=int, default=tiles.DEFAULT_TILE_PX, help="tile side in page pixels")
    ap.add_argument("--tile-overlap", type=float, default=tiles.DEFAULT_OVERLAP, help="tile overlap as a share of the side")
    ap.add_argument("--timeout", type=float, default=600.0, help="seconds per model call")
    ap.add_argument("--retry-errors", action="store_true", help="re-run pages whose result recorded an error")
    ap.add_argument("--libredwg-bin", default=None, help="folder with dxf2dwg/dwg2dxf (default: PATH)")
    return ap.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    a = parse_args(argv)
    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    projects_dir = Path(a.projects)
    pages = raster_pages(projects_dir)
    print(f"{len(pages)} raster pages under {projects_dir}")
    failures = 0

    if a.stage == "dwg":
        dxfs = sorted(projects_dir.glob("*/*.dxf"))
        report = dwg_roundtrip(dxfs, out_dir / "dwg_roundtrip.json", Path(a.libredwg_bin) if a.libredwg_bin else None)
        return 0 if report["all_ok"] else 1

    if a.stage in ("all", "ocr"):
        for page in pages:
            print(f"OCR {page.slug}")
            rec = run_ocr_page(page, out_dir, use_paddle=not a.no_paddle, use_tesseract=not a.no_tesseract,
                               device=a.ocr_device, retry_errors=a.retry_errors)
            failures += int(bool(rec.get("has_errors")))

    if a.stage in ("all", "vlm"):
        served = vlm_client.served_models(a.server)
        if not served:
            print(f"no vLLM server at {a.server}; skipping model tasks")
        for model in a.models:
            if model not in served:
                print(f"model {model} is not served at {a.server} (served: {served}); skipping")
                continue
            client = vlm_client.VLMClient(a.server, model=model, timeout_s=a.timeout, max_side=a.max_side)
            for page in pages:
                print(f"VLM {page.slug} {model}")
                rec = run_model_page(page, model, client, out_dir, tasks=a.tasks, retry_errors=a.retry_errors)
                failures += int(bool(rec.get("has_errors")))
                if a.tiled:
                    rec = run_symbols_tiled(page, model, client, out_dir, tile_px=a.tile_px, overlap=a.tile_overlap,
                                            retry_errors=a.retry_errors)
                    failures += int(bool(rec.get("has_errors")))

    if a.stage in ("all", "twopass") and len(a.models) >= 2:
        for page in pages:
            run_two_pass_page(page, a.models[0], a.models[1], out_dir)

    if a.stage in ("all", "twopass", "summary"):
        write_summary(pages, out_dir)

    if failures:
        print(f"{failures} page results with errors (see the JSON files)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
