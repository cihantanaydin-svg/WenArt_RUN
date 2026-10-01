"""Scores of OCR and model answers against the synthetic ground truth.

Inputs are plain dicts/lists (what ``bakeoff.py`` writes), so the functions
run on hand-made data in the CPU tests.

- Text: recall / precision of normalised texts (``ocr.normalise_text``: case-
  insensitive with Turkish rules, decimal comma -> dot), multiset matching, no
  boxes needed.
- Symbols: precision / recall per type at box IoU >= 0.5 with greedy matching;
  truth boxes come from ``truth/pages.json`` (pixel boxes) or are mapped from
  the building frame with the page transform (``map_building_boxes``).
- Page class and level label accuracy, per-page latency.
- ``aggregate`` sums the per-page scores per model / OCR engine, ``summarise``
  renders the markdown tables for ``results/bakeoff/summary.md``.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean, median
from typing import Iterable, Optional, Sequence

from wenart import building as B
from wenart import geometry as G
from wenart.recognition.ocr import normalise_text

IOU_THRESHOLD = 0.5


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def precision_recall(tp: int, fp: int, fn: int) -> dict:
    """tp/fp/fn -> precision, recall and F1 (0.0 when undefined)."""
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": round(precision, 4),
            "recall": round(recall, 4), "f1": round(f1, 4)}


def latency_stats(values: Iterable[float]) -> dict:
    """mean / median / max / n of latencies in seconds (zeros when empty)."""
    vals = [float(v) for v in values]
    if not vals:
        return {"n": 0, "mean_s": 0.0, "median_s": 0.0, "max_s": 0.0}
    return {"n": len(vals), "mean_s": round(mean(vals), 2), "median_s": round(median(vals), 2),
            "max_s": round(max(vals), 2)}


# --------------------------------------------------------------------------
# Text
# --------------------------------------------------------------------------

def text_scores(pred_texts: Sequence[str], truth_texts: Sequence[str]) -> dict:
    """Multiset recall / precision of normalised texts.

    A prediction counts when its normalised form equals a not-yet-used truth text.
    Empty predictions are ignored. Also returns the missed truth texts, for the report.
    """
    truth_counter = Counter(normalise_text(t) for t in truth_texts if normalise_text(t))
    remaining = Counter(truth_counter)
    tp = fp = 0
    for text in pred_texts:
        norm = normalise_text(text)
        if not norm:
            continue
        if remaining[norm] > 0:
            remaining[norm] -= 1
            tp += 1
        else:
            fp += 1
    fn = sum(remaining.values())
    scores = precision_recall(tp, fp, fn)
    scores["missed"] = sorted(remaining.elements())
    return scores


# --------------------------------------------------------------------------
# Symbols
# --------------------------------------------------------------------------

def map_building_boxes(polygons: Iterable[Sequence[G.Point]], transform) -> list[list[float]]:
    """Polygons in the building frame -> axis-aligned pixel boxes through the page transform.

    ``transform`` is the ``transform.building_to_page`` of ``truth/pages.json``
    (6-number affine or 9-number homography).
    """
    return [[round(v, 1) for v in G.bbox(G.transform_points(transform, poly))] for poly in polygons]


def furniture_boxes_from_building(building: dict, level_id: str, transform) -> list[dict]:
    """Truth symbols ``{"type", "box", "id"}`` for the furniture of one level, mapped to pixels."""
    pieces = [f for f in building["furniture"] if f["level_id"] == level_id]
    polys = [G.rotated_rectangle(f["footprint"]["center"], f["footprint"]["size"], f["footprint"]["rotation_deg"])
             for f in pieces]
    boxes = map_building_boxes(polys, transform)
    return [{"type": f["type"], "box": box, "id": f["id"]} for f, box in zip(pieces, boxes)]


def match_symbols(pred: Sequence[dict], truth: Sequence[dict], iou_thresh: float = IOU_THRESHOLD
                  ) -> list[tuple[int, int, float]]:
    """Greedy (pred, truth, iou) matches with equal type and IoU >= threshold."""
    pairs = []
    for i, p in enumerate(pred):
        for j, t in enumerate(truth):
            if p["type"] != t["type"]:
                continue
            iou = G.box_iou(p["box"], t["box"])
            if iou >= iou_thresh:
                pairs.append((iou, i, j))
    pairs.sort(reverse=True)
    used_p: set[int] = set()
    used_t: set[int] = set()
    matches = []
    for iou, i, j in pairs:
        if i in used_p or j in used_t:
            continue
        used_p.add(i)
        used_t.add(j)
        matches.append((i, j, iou))
    return matches


def symbol_scores(pred: Sequence[dict], truth: Sequence[dict], iou_thresh: float = IOU_THRESHOLD) -> dict:
    """Precision / recall per type and overall at IoU >= ``iou_thresh``.

    ``pred`` and ``truth`` are lists of ``{"type", "box"}`` in the same pixel frame.
    """
    matches = match_symbols(pred, truth, iou_thresh)
    matched_p = {i for i, _, _ in matches}
    matched_t = {j for _, j, _ in matches}
    counts: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    for i, p in enumerate(pred):
        counts[p["type"]]["tp" if i in matched_p else "fp"] += 1
    for j, t in enumerate(truth):
        if j not in matched_t:
            counts[t["type"]]["fn"] += 1
    per_type = {name: precision_recall(c["tp"], c["fp"], c["fn"]) for name, c in sorted(counts.items())}
    overall = precision_recall(sum(c["tp"] for c in counts.values()), sum(c["fp"] for c in counts.values()),
                               sum(c["fn"] for c in counts.values()))
    return {"per_type": per_type, "overall": overall, "n_pred": len(pred), "n_truth": len(truth)}


# --------------------------------------------------------------------------
# Page class and level label
# --------------------------------------------------------------------------

def level_label_matches(pred: Optional[str], truth: Optional[str]) -> bool:
    """Compare level titles after normalisation (``ZEMİN KAT PLANI`` == ``Zemin Kat Planı``)."""
    if not pred and not truth:
        return True
    if not pred or not truth:
        return False
    p, t = B.normalise_level_label(pred), B.normalise_level_label(truth)
    if p is not None or t is not None:
        return p == t
    return normalise_text(pred) == normalise_text(truth)


def page_class_scores(pred: Optional[dict], truth_page: dict) -> dict:
    """``{"class_correct", "level_label_correct", "scale_text_correct", "pred_class", "truth_class"}``."""
    truth_class = truth_page.get("class")
    truth_label = truth_page.get("level_label_raw")
    truth_scale = next((t["text"] for t in truth_page.get("texts", []) if t.get("role") == "scale"), None)
    if not pred:
        return {"class_correct": False, "level_label_correct": False, "scale_text_correct": False,
                "pred_class": None, "truth_class": truth_class}
    scale_ok = (not truth_scale and not pred.get("scale_text")) or (
        bool(truth_scale) and bool(pred.get("scale_text")) and normalise_text(pred["scale_text"]) == normalise_text(truth_scale))
    return {
        "class_correct": pred.get("class") == truth_class,
        "level_label_correct": level_label_matches(pred.get("level_label_raw"), truth_label),
        "scale_text_correct": bool(scale_ok),
        "pred_class": pred.get("class"),
        "truth_class": truth_class,
    }


# --------------------------------------------------------------------------
# Aggregation over pages and the markdown summary
# --------------------------------------------------------------------------

def _sum_pr(parts: Iterable[dict]) -> dict:
    tp = fp = fn = 0
    for p in parts:
        tp += p.get("tp", 0)
        fp += p.get("fp", 0)
        fn += p.get("fn", 0)
    return precision_recall(tp, fp, fn)


def aggregate(page_results: Sequence[dict]) -> dict:
    """Totals per model and per OCR engine over per-page results.

    Each page result (see ``bakeoff.py``) looks like::

        {"project", "file", "page", "kind",
         "ocr": {engine: {"all_texts": text_scores, "room_labels": text_scores, "latency_s": float}},
         "models": {model: {"page_class": page_class_scores, "room_labels": text_scores,
                            "symbols": symbol_scores, "latency_s": {task: float}, "errors": {task: str}}},
         "two_pass": {"verified": symbol_scores, "all": symbol_scores, "n_verified", "n_unverified"} | None}
    """
    models: dict[str, dict] = {}
    engines: dict[str, dict] = {}
    for page in page_results:
        for engine, scores in (page.get("ocr") or {}).items():
            e = engines.setdefault(engine, {"all_texts": [], "room_labels": [], "latency": [], "pages": 0})
            e["pages"] += 1
            e["all_texts"].append(scores.get("all_texts", {}))
            e["room_labels"].append(scores.get("room_labels", {}))
            if scores.get("latency_s") is not None:
                e["latency"].append(scores["latency_s"])
        for model, scores in (page.get("models") or {}).items():
            m = models.setdefault(model, {"pages": 0, "class_ok": 0, "label_ok": 0, "scale_ok": 0,
                                          "room_labels": [], "symbols_overall": [], "symbols_per_type": defaultdict(list),
                                          "latency": [], "errors": 0})
            m["pages"] += 1
            pc = scores.get("page_class") or {}
            m["class_ok"] += int(bool(pc.get("class_correct")))
            m["label_ok"] += int(bool(pc.get("level_label_correct")))
            m["scale_ok"] += int(bool(pc.get("scale_text_correct")))
            if scores.get("room_labels"):
                m["room_labels"].append(scores["room_labels"])
            sym = scores.get("symbols") or {}
            if sym:
                m["symbols_overall"].append(sym.get("overall", {}))
                for name, pr in sym.get("per_type", {}).items():
                    m["symbols_per_type"][name].append(pr)
            m["latency"].extend(v for v in (scores.get("latency_s") or {}).values() if v is not None)
            m["errors"] += len(scores.get("errors") or {})
    out_models = {}
    for model, m in models.items():
        out_models[model] = {
            "pages": m["pages"],
            "page_class_accuracy": round(m["class_ok"] / m["pages"], 4) if m["pages"] else 0.0,
            "level_label_accuracy": round(m["label_ok"] / m["pages"], 4) if m["pages"] else 0.0,
            "scale_text_accuracy": round(m["scale_ok"] / m["pages"], 4) if m["pages"] else 0.0,
            "room_labels": _sum_pr(m["room_labels"]),
            "symbols": _sum_pr(m["symbols_overall"]),
            "symbols_per_type": {name: _sum_pr(parts) for name, parts in sorted(m["symbols_per_type"].items())},
            "latency": latency_stats(m["latency"]),
            "errors": m["errors"],
        }
    out_engines = {}
    for engine, e in engines.items():
        out_engines[engine] = {
            "pages": e["pages"],
            "all_texts": _sum_pr(e["all_texts"]),
            "room_labels": _sum_pr(e["room_labels"]),
            "latency": latency_stats(e["latency"]),
        }
    two_pass = [p["two_pass"] for p in page_results if p.get("two_pass")]
    out_two_pass = None
    if two_pass:
        out_two_pass = {
            "pages": len(two_pass),
            "verified": _sum_pr(t.get("verified", {}).get("overall", {}) for t in two_pass),
            "all": _sum_pr(t.get("all", {}).get("overall", {}) for t in two_pass),
            "n_verified": sum(t.get("n_verified", 0) for t in two_pass),
            "n_unverified": sum(t.get("n_unverified", 0) for t in two_pass),
        }
    return {"models": out_models, "ocr": out_engines, "two_pass": out_two_pass, "pages": len(page_results)}


def _pct(value: float) -> str:
    return f"{100.0 * value:.0f} %"


def summarise(page_results: Sequence[dict]) -> str:
    """Markdown summary (tables) of the bake-off results."""
    agg = aggregate(page_results)
    lines = ["# Recognition bake-off summary", "",
             f"Pages: {agg['pages']} (synthetic scans and photos). IoU threshold {IOU_THRESHOLD} for symbols; "
             "texts compared after normalisation (case-insensitive, decimal comma -> dot).", ""]

    lines += ["## OCR engines", "", "| Engine | Pages | Texts recall | Texts precision | Room labels recall | Room labels precision | Mean latency |",
              "|---|---|---|---|---|---|---|"]
    for engine, e in sorted(agg["ocr"].items()):
        lines.append(f"| {engine} | {e['pages']} | {_pct(e['all_texts']['recall'])} | {_pct(e['all_texts']['precision'])} | "
                     f"{_pct(e['room_labels']['recall'])} | {_pct(e['room_labels']['precision'])} | {e['latency']['mean_s']} s |")
    if not agg["ocr"]:
        lines.append("| (no OCR results) | | | | | | |")

    lines += ["", "## Vision-language models", "",
              "| Model | Pages | Page class | Level label | Scale text | Room labels R / P | Symbols R / P | Mean latency / call | Errors |",
              "|---|---|---|---|---|---|---|---|---|"]
    for model, m in sorted(agg["models"].items()):
        lines.append(f"| {model} | {m['pages']} | {_pct(m['page_class_accuracy'])} | {_pct(m['level_label_accuracy'])} | "
                     f"{_pct(m['scale_text_accuracy'])} | {_pct(m['room_labels']['recall'])} / {_pct(m['room_labels']['precision'])} | "
                     f"{_pct(m['symbols']['recall'])} / {_pct(m['symbols']['precision'])} | {m['latency']['mean_s']} s | {m['errors']} |")
    if not agg["models"]:
        lines.append("| (no model results) | | | | | | | | |")

    types = sorted({name for m in agg["models"].values() for name in m["symbols_per_type"]})
    if types:
        models = sorted(agg["models"])
        lines += ["", "## Symbols per type (recall / precision)", "",
                  "| Type | " + " | ".join(models) + " |", "|---|" + "---|" * len(models)]
        for name in types:
            cells = []
            for model in models:
                pr = agg["models"][model]["symbols_per_type"].get(name)
                cells.append(f"{_pct(pr['recall'])} / {_pct(pr['precision'])} (n={pr['tp'] + pr['fn']})" if pr else "-")
            lines.append(f"| {name} | " + " | ".join(cells) + " |")

    if agg["two_pass"]:
        t = agg["two_pass"]
        lines += ["", "## Two-pass agreement", "",
                  "| Set | Symbols | Recall | Precision |", "|---|---|---|---|",
                  f"| verified (both models agree) | {t['n_verified']} | {_pct(t['verified']['recall'])} | {_pct(t['verified']['precision'])} |",
                  f"| all proposals (verified + unverified) | {t['n_verified'] + t['n_unverified']} | {_pct(t['all']['recall'])} | {_pct(t['all']['precision'])} |"]

    lines += ["", "## Per page", "", "| Project | File | Kind | Who | Room labels R / P | Symbols R / P | Page class | Latency |",
              "|---|---|---|---|---|---|---|---|"]
    for page in page_results:
        where = f"| {page.get('project')} | {page.get('file')} | {page.get('kind')} |"
        for engine, s in sorted((page.get("ocr") or {}).items()):
            rl = s.get("room_labels", {})
            lines.append(f"{where} {engine} | {_pct(rl.get('recall', 0))} / {_pct(rl.get('precision', 0))} | - | - | {s.get('latency_s', 0)} s |")
        for model, s in sorted((page.get("models") or {}).items()):
            rl = s.get("room_labels") or {}
            sy = (s.get("symbols") or {}).get("overall", {})
            pc = s.get("page_class") or {}
            lat = sum(v for v in (s.get("latency_s") or {}).values() if v)
            klass = f"{pc.get('pred_class')} ({'ok' if pc.get('class_correct') else 'wrong'})"
            lines.append(f"{where} {model} | {_pct(rl.get('recall', 0))} / {_pct(rl.get('precision', 0))} | "
                         f"{_pct(sy.get('recall', 0))} / {_pct(sy.get('precision', 0))} | {klass} | {lat:.1f} s |")
    return "\n".join(lines) + "\n"
