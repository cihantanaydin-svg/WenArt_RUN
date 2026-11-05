#!/usr/bin/env python3
"""Rename the element ids the user's corrections name after a change of the reader's id numbering.

Why: the truth (``results/reading_truth/<p>.json``) keeps the user's corrections as ``user_correction`` entries and the
correction records (``results/reading_corrections.jsonl``) name elements by id; when the reader numbers its elements
differently (5 Nov 2026: mirror copies got their own numbers ``d_L0_m001``, so the separators after them moved, real10
C0043's doors o_Lk_033/034 -> o_Lk_030/031), those ids must follow the elements, or a truth rebuild by id holds the
element twice. The meaning of every correction stays the same: only its id changes.

What: maps every opening and room id of the old reading to the id of the same element in the new reading (same level,
same type, same source lines and evidence rule, centre within ``TOL_M``; rooms: same label and centroid within
``TOL_M``) and renames, for ``--project``, the ``user_correction`` entries of the truth and the ``element_ids`` of its
correction records (also the ids in their ``truth_action`` and ``truth_applied``); each changed record gets a
``history`` entry ``{"date", "old_element_ids", "reason"}``. Prints every rename (old id, new id, place). Dry run
unless ``--write``.

How:
    python scripts/migrate_reading_ids.py --old <old reading>/building.json --new <new reading>/building.json \
        --project real10 --reason "stable mirror-copy ids, 5 Nov 2026" [--write]
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOL_M = 0.05


def _centre(e: dict):
    c = e.get("center") or e.get("centroid")
    if c is None and e.get("polygon"):
        from shapely.geometry import Polygon
        q = Polygon(e["polygon"]).centroid
        c = [q.x, q.y]
    return c


def _ev(e: dict) -> tuple:
    ev = (e.get("evidence") or [{}])[0]
    return str(ev.get("entity")), ev.get("rule")


def id_map(old: dict, new: dict) -> dict:
    """``{old id: (new id, place)}`` for the openings and rooms whose id changed."""
    out = {}
    for o in old.get("openings") or []:
        same = [q for q in new.get("openings") or [] if q["level_id"] == o["level_id"] and q["type"] == o["type"]
                and _ev(q) == _ev(o) and math.dist(q["center"], o["center"]) <= TOL_M]
        if same and same[0]["id"] != o["id"]:
            out[o["id"]] = (same[0]["id"], o["center"])
    for r in old.get("rooms") or []:
        same = [q for q in new.get("rooms") or [] if q["level_id"] == r["level_id"] and q.get("label") == r.get("label")
                and math.dist(_centre(q), _centre(r)) <= TOL_M]
        if same and same[0]["id"] != r["id"]:
            out[r["id"]] = (same[0]["id"], _centre(r))
    return out


def _rename_ids(node, ids: dict):
    """``node`` with every ``"id"`` value found in ``ids`` renamed (nested dicts and lists)."""
    if isinstance(node, dict):
        return {k: (ids[v][0] if k == "id" and isinstance(v, str) and v in ids else _rename_ids(v, ids))
                for k, v in node.items()}
    if isinstance(node, list):
        return [_rename_ids(v, ids) for v in node]
    return node


def migrate(project: str, old: dict, new: dict, reason: str, write: bool, repo: Path = REPO) -> list[tuple]:
    """The renames ``[(where, old id, new id, place)]``; written when ``write``."""
    ids = id_map(old, new)
    renames = []
    truth_p = repo / "results" / "reading_truth" / f"{project}.json"
    truth = json.loads(truth_p.read_text(encoding="utf-8"))
    for lid, lv in truth["per_level"].items():
        for kind, items in lv.items():
            for e in items if isinstance(items, list) else []:
                if e.get("source") == "user_correction" and e["id"] in ids:
                    new_id, place = ids[e["id"]]
                    renames.append((f"truth {lid} {kind} {e.get('correction')}", e["id"], new_id, place))
                    e["id"] = new_id
    corr_p = repo / "results" / "reading_corrections.jsonl"
    lines = corr_p.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines:
        rec = json.loads(line) if line.strip() else None
        if rec and rec.get("project") == project and any(e in ids for e in rec.get("element_ids") or []):
            olds = list(rec["element_ids"])
            for e in olds:
                if e in ids:
                    renames.append((f"record {rec['id']}", e, ids[e][0], ids[e][1]))
            rec["element_ids"] = [ids[e][0] if e in ids else e for e in olds]
            for part in ("truth_action", "truth_applied"):            # the ids the applied action wrote
                if rec.get(part) is not None:
                    rec[part] = _rename_ids(rec[part], ids)
            rec.setdefault("history", []).append({"date": date.today().isoformat(), "old_element_ids": olds,
                                                  "reason": reason})
            line = json.dumps(rec, ensure_ascii=False)
        out.append(line)
    if write:
        truth_p.write_text(json.dumps(truth, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        corr_p.write_text("\n".join(out) + "\n", encoding="utf-8")
    return renames


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--old", required=True, help="the old reading's building.json")
    ap.add_argument("--new", required=True, help="the new reading's building.json")
    ap.add_argument("--project", required=True)
    ap.add_argument("--reason", required=True)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    old = json.loads(Path(a.old).read_text(encoding="utf-8"))
    new = json.loads(Path(a.new).read_text(encoding="utf-8"))
    renames = migrate(a.project, old, new, a.reason, a.write)
    for where, o, n, place in renames:
        print(f"{where}: {o} -> {n} at ({place[0]:.3f}, {place[1]:.3f})")
    print(f"{len(renames)} renames" + ("" if a.write else " (dry run: --write applies them)"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
