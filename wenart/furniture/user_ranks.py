"""The user's ranks of the library models (31 Oct 2026, lesson UL217; user: "Is it possible to do furniture ranking
system? we render the furnitures and I ranked them from 10 to 0 based purely on the look?", then "page with score
buttons, start with beds sofas armchairs").

What: ``results/library/user_ranks.json`` holds ``{"ranks": {model id: {"rank": 0-10, "type", "date", "sheet",
"letter"}}}``, written from the scoring page (``merge``). The fit reads it:

- ``out_reason(entry)``: a model ranked ``OUT_AT_OR_BELOW`` (2) or lower is never used, in any licence mode
  (``catalog.usable``), like a model the user rejected;
- ``rank_steps(entry)``: the rank as size steps of the fit's order (``fit.rank_key``): ``STEPS_PER_POINT`` per point
  away from ``UNRANKED`` (5: a model the user has not ranked keeps its place), so of the models that fit the drawn
  piece the best-looking one wins (rank 10 vs rank 7: 6 steps, more than the whole size range of the caps); the
  user's rank stands in for our own upholstery grade (``fit.soft_steps``);
- ``better_than_procedural(entry)``: a ranked model of a type we also build ourselves (UL215's library-first decor) is
  better than our build from ``GOOD_FROM`` (6) up and worse below; None when unranked (the audit's vision quality
  decides, as before).

Why: the vision models judged the library's look (the audit's quality 1-5) and the user still disliked models in the
renders (UL94, UL131, UL216); the user's own eye ranks them on one studio sheet (``wenart.assets.audit.studio``).

How: pure; the file is read once per path (cached; ``reset()`` for tests); a missing or broken file means no ranks.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

USER_RANKS_PATH = Path(__file__).resolve().parents[2] / "results" / "library" / "user_ranks.json"
RANK_MIN, RANK_MAX = 0, 10
UNRANKED = 5
OUT_AT_OR_BELOW = 2
GOOD_FROM = 6
STEPS_PER_POINT = 2
RULE = "user_rank (UL217)"
_CACHE: dict = {}


def reset() -> None:
    _CACHE.clear()


def valid_rank(value) -> Optional[int]:
    """An integer rank 0-10, else None (a bool, a fraction or a value outside the scale is no rank)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return value if isinstance(value, int) and RANK_MIN <= value <= RANK_MAX else None


def ranks(path: Optional[Path] = None) -> dict[str, dict]:
    """``{model id: record}`` with a valid ``rank`` (cached per path)."""
    p = Path(path) if path is not None else USER_RANKS_PATH
    key = str(p)
    if key not in _CACHE:
        rows: dict[str, dict] = {}
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            for iid, rec in (data.get("ranks") or {}).items():
                if isinstance(rec, dict) and valid_rank(rec.get("rank")) is not None:
                    rows[str(iid)] = rec
        except (OSError, ValueError, AttributeError):
            rows = {}
        _CACHE[key] = rows
    return _CACHE[key]


def rank_of(entry: dict, path: Optional[Path] = None) -> Optional[int]:
    """The user's rank of a catalogue entry or a fitted asset (by ``id``, ``asset_id`` or ``uid``), None unranked."""
    rows = ranks(path)
    if not rows or not isinstance(entry, dict):
        return None
    for key in ("id", "asset_id", "uid"):
        value = entry.get(key)
        if value and str(value) in rows:
            return valid_rank(rows[str(value)].get("rank"))
    return None


def out_reason(entry: dict, path: Optional[Path] = None) -> Optional[str]:
    """Why a model the user ranked low is never used, None otherwise."""
    rank = rank_of(entry, path)
    if rank is None or rank > OUT_AT_OR_BELOW:
        return None
    rec = ranks(path).get(str(entry.get("id") or entry.get("asset_id") or entry.get("uid")), {})
    return (f"the user ranked this model {rank}/10 on {rec.get('date') or '?'} (sheet {rec.get('sheet') or '?'} "
            f"{rec.get('letter') or ''}; {OUT_AT_OR_BELOW} or lower: never used, {RULE}, "
            "results/library/user_ranks.json)").replace(" )", ")")


def rank_steps(entry: dict, path: Optional[Path] = None) -> int:
    """The rank's size steps in the fit's order (negative for a rank above ``UNRANKED``); 0 unranked."""
    rank = rank_of(entry, path)
    return 0 if rank is None else STEPS_PER_POINT * (UNRANKED - rank)


def better_than_procedural(entry: dict, path: Optional[Path] = None) -> Optional[bool]:
    rank = rank_of(entry, path)
    return None if rank is None else rank >= GOOD_FROM


def merge(current: Optional[dict], scores: dict, index: dict, date: str, where: str = "the scoring page") -> dict:
    """The new ``user_ranks.json`` document: ``current`` plus ``scores`` (``{model id: rank}``; a valid rank only, a
    model of ``index["models"]`` only), each with its type, sheet, letter, the date and where it was given. A later
    score of a model replaces the earlier one."""
    doc = dict(current or {})
    doc.setdefault("schema_version", 1)
    doc["kind"] = "user_ranks"
    doc["what"] = ("the user's ranks (0-10, purely on the look) of the library models on the ranking studio's sheets "
                   f"(lesson UL217): 0-{OUT_AT_OR_BELOW} never used; the fit prefers the higher rank; "
                   f"unranked = {UNRANKED}")
    rows = dict(doc.get("ranks") or {})
    models = index.get("models") or {}
    for iid, value in sorted(scores.items()):
        rank = valid_rank(value)
        if rank is None or iid not in models:
            continue
        m = models[iid]
        rows[iid] = {"rank": rank, "type": m.get("type"), "sheet": m.get("sheet"), "letter": m.get("letter"),
                     "title": m.get("title"), "date": date, "where": where}
    doc["ranks"] = dict(sorted(rows.items()))
    return doc


def parse_text(text: str, index: dict) -> tuple[str, dict[str, int]]:
    """``(name, {model id: rank})`` of the text the survey page copies ("Name: ..." then one line per sheet:
    ``bed_double-01: A7 B3 T10``), the letters read against ``index`` (the sheets the rater saw:
    ``results/library/ranking/second_opinion_index.json``). Unknown sheets, letters and ranks outside 0-10 are skipped."""
    import re
    name, out = "", {}
    letters = {s["sheet"]: s["letters"] for s in index.get("sheets") or []}
    for line in str(text or "").splitlines():
        line = line.strip()
        if line.lower().startswith("name:"):
            name = line[5:].strip()
            continue
        head, sep, rest = line.partition(":")
        if not sep or head.strip() not in letters:
            continue
        for letter, value in re.findall(r"\b([A-Z])(\d{1,2})\b", rest):
            iid = letters[head.strip()].get(letter)
            rank = valid_rank(int(value))
            if iid and rank is not None:
                out[iid] = rank
    return name, out


def main(argv: Optional[list[str]] = None) -> int:
    """``python -m wenart.furniture.user_ranks merge --scores scores.json [--index ...] [--date ...]``: the scoring
    page's scores (``{model id: rank}`` or the page's rows ``[{"id", "rank"}]``) into ``user_ranks.json``."""
    import argparse
    import datetime
    ap = argparse.ArgumentParser(prog="python -m wenart.furniture.user_ranks")
    ap.add_argument("action", choices=("merge", "show"))
    ap.add_argument("--scores")
    ap.add_argument("--index", default=str(USER_RANKS_PATH.parent / "ranking" / "ranking_index.json"))
    ap.add_argument("--out", default=str(USER_RANKS_PATH))
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args(argv)
    out = Path(a.out)
    current = json.loads(out.read_text(encoding="utf-8")) if out.is_file() else None
    if a.action == "merge":
        raw = json.loads(Path(a.scores).read_text(encoding="utf-8"))
        scores = raw if isinstance(raw, dict) else {str(r.get("id")): r.get("rank") for r in raw if isinstance(r, dict)}
        index = json.loads(Path(a.index).read_text(encoding="utf-8"))
        doc = merge(current, scores, index, a.date)
        out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        current = doc
        reset()
    rows = (current or {}).get("ranks") or {}
    by_type: dict = {}
    for rec in rows.values():
        t = by_type.setdefault(rec.get("type") or "?", {"ranked": 0, "out": 0, "good": 0})
        t["ranked"] += 1
        t["out"] += int(rec["rank"] <= OUT_AT_OR_BELOW)
        t["good"] += int(rec["rank"] >= GOOD_FROM)
    for t, c in sorted(by_type.items()):
        print(f"{t}: {c['ranked']} ranked, {c['out']} out (0-{OUT_AT_OR_BELOW}), {c['good']} at {GOOD_FROM}+")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
