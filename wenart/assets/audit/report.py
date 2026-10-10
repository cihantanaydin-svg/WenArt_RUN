"""The audit's tables (docs/milestone12.md §6.1 output): ``audit.json``, ``audit.csv`` and ``audit.md`` (one row per
model: id, type, source, licence, dimensions, checks, vision answers, decision, reasons; summary tables per type,
source and style family).

How: pure text from the records; rows in catalogue order; no clock inside (the caller passes the date).
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter
from pathlib import Path
from typing import Optional

from wenart.assets.audit.decide import expected_status

ORDER = ("keep", "keep?", "fix", "fix?", "vision?", "removed?", "removed", "pending")


def rows_of(items: list[dict], checks: dict, decisions: dict, answers: Optional[dict] = None,
            answers2: Optional[dict] = None) -> list[dict]:
    answers, answers2 = answers or {}, answers2 or {}
    out = []
    for it in items:
        d = decisions[it["id"]]
        out.append({"id": it["id"], "type": it["type"], "kind": it["kind"], "source": it.get("source"),
                    "licence": it.get("licence"), "title": it.get("title"), "dims_m": it.get("bbox_m"),
                    "styles": it.get("styles"), "status": d["status"], "expected": expected_status(d),
                    "reasons": d["reasons"], "fixes": d["fixes"], "pending": d.get("pending") or [],
                    "flags": d.get("flags") or {}, "notes": d.get("notes") or [],
                    "checks": [c for c in checks[it["id"]] if c["status"] not in ("ok", "skip")],
                    "vision": answers.get(it["id"]), "vision2": answers2.get(it["id"])})
    return out


def counts(rows: list[dict], key: str = "expected") -> dict:
    c = Counter(r[key] for r in rows)
    return {k: c[k] for k in ORDER if c.get(k)}


def audit_json(rows: list[dict], mode: str, generated_utc: str, extra: Optional[dict] = None) -> str:
    doc = {"kind": "library_audit", "version": "m12", "mode": mode, "generated_utc": generated_utc,
           "counts": counts(rows), "counts_by_source": {s: counts([r for r in rows if r["source"] == s])
                                                        for s in sorted({r["source"] for r in rows})},
           "items": rows}
    doc.update(extra or {})
    return json.dumps(doc, indent=1, ensure_ascii=False) + "\n"


def audit_csv(rows: list[dict]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["id", "type", "kind", "source", "licence", "w_m", "d_m", "h_m", "status", "expected", "reasons",
                "fixes", "title"])
    for r in rows:
        dims = list(r["dims_m"] or [None, None, None])
        w.writerow([r["id"], r["type"], r["kind"], r["source"], r["licence"]] + dims
                   + [r["status"], r["expected"], " | ".join(r["reasons"]),
                      json.dumps(r["fixes"], sort_keys=True) if r["fixes"] else "", r["title"]])
    return buf.getvalue()


def _table(header: list[str], body: list[list]) -> list[str]:
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + \
        ["| " + " | ".join(str(c) for c in row) + " |" for row in body]


def reason_group(reason: str) -> str:
    """A short class of a reason for the summary (the reason text names the item's numbers)."""
    r = reason.lower()
    for key, label in (("names no type", "no title evidence (two vision passes)"),
                       ("generated: our own title", "generated (two vision passes)"),
                       ("every model needs", "the vision check of every model"),
                       ("triangles", "few faces (crude unless the vision quality is high)"),
                       ("retype if", "retype (title and vision)"), ("licence", "licence not allowed"),
                       ("lies on its side", "lies on its side"),
                       ("proportions", "proportions fit no real piece"), ("known units", "real product off size"),
                       ("title says", "title flag"), ("the title names", "title names another type"),
                       ("duplicate", "duplicate"), ("copy of", "duplicate"), ("same glb", "duplicate"),
                       ("broken", "broken mesh"), ("vision", "vision check"), ("crude", "crude"),
                       ("judges' quality", "M8-M10 quality")):
        if key in r:
            return label
    return reason.split(":")[0][:50]


def audit_markdown(rows: list[dict], title: str, intro: str = "") -> str:
    lines = [f"# {title}", ""]
    if intro:
        lines += [intro, ""]
    cols = [k for k in ORDER if any(r["expected"] == k for r in rows)]
    lines += ["## Totals", ""] + _table(["status"] + ["models"], [[k, sum(1 for r in rows if r["expected"] == k)]
                                                                   for k in cols]) + [""]
    lines += ["## Per source", ""]
    srcs = sorted({r["source"] for r in rows})
    lines += _table(["source"] + cols + ["total"],
                    [[s] + [sum(1 for r in rows if r["source"] == s and r["expected"] == k) for k in cols]
                     + [sum(1 for r in rows if r["source"] == s)] for s in srcs]) + [""]
    lines += ["## Per type", ""]
    types: list = []
    for r in rows:
        if (r["kind"], r["type"]) not in types:
            types.append((r["kind"], r["type"]))
    lines += _table(["kind", "type"] + cols + ["total"],
                    [[k, t] + [sum(1 for r in rows if r["type"] == t and r["kind"] == k and r["expected"] == c)
                               for c in cols] + [sum(1 for r in rows if r["type"] == t and r["kind"] == k)]
                     for k, t in types]) + [""]
    reasons = Counter(reason_group(x) for r in rows for x in r["reasons"])
    lines += ["## Removal reasons (a model may have several)", ""] + _table(
        ["reason", "models"], [[k, v] for k, v in reasons.most_common()]) + [""]
    fixes = Counter(k for r in rows for k in r["fixes"])
    if fixes:
        lines += ["## Fixes (catalogue fields)", ""] + _table(["fix", "models"],
                                                              [[k, v] for k, v in fixes.most_common()]) + [""]
    pend = Counter(p["needs"] + ": " + reason_group(p["why"]) for r in rows for p in r["pending"])
    if pend:
        lines += ["## Waiting for the vision check", ""] + _table(["needs", "models"],
                                                                 [[k, v] for k, v in pend.most_common()]) + [""]
    removed = [r for r in rows if r["expected"] in ("removed", "removed?")]
    if removed:
        lines += ["## Models to remove (catalogue only; the files stay on the volume)", ""] + _table(
            ["id", "type", "source", "status", "reason", "title"],
            [[r["id"], r["type"], r["source"], r["expected"],
              (r["reasons"] or [p["why"] for p in r["pending"]] or [""])[0].replace("|", "/"),
              str(r["title"])[:60].replace("|", "/")] for r in removed]) + [""]
    fixed = [r for r in rows if r["expected"] in ("fix", "fix?")]
    if fixed:
        lines += ["## Models to fix", ""] + _table(
            ["id", "type", "source", "fixes", "why"],
            [[r["id"], r["type"], r["source"], json.dumps(r["fixes"], sort_keys=True).replace("|", "/"),
              ("; ".join(r["notes"][:2]) or "; ".join(p["why"] for p in r["pending"]))[:120].replace("|", "/")]
             for r in fixed]) + [""]
    return "\n".join(lines)


def write_outputs(folder: Path, rows: list[dict], mode: str, generated_utc: str, title: str, intro: str = "",
                  extra: Optional[dict] = None) -> list[Path]:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    paths = [folder / "audit.json", folder / "audit.csv", folder / "audit.md"]
    paths[0].write_text(audit_json(rows, mode, generated_utc, extra), encoding="utf-8")
    paths[1].write_text(audit_csv(rows), encoding="utf-8")
    paths[2].write_text(audit_markdown(rows, title, intro), encoding="utf-8")
    return paths
