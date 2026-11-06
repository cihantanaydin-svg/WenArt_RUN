"""The reading truth corpus and the correction store (4 Nov 2026, Milestone 14 track R1; user: "I want structure
recognition to be cumulatively better with the feedbacks I am giving"; review findings of 5 Nov 2026 built in).

What: ``results/reading_truth/<project>.json`` holds, per project, the elements the truth knows in building metres:
the levels (id, label, elevation, order) and, per level, the rooms (label, type, area, centroid, polygon), the doors,
the windows, the other openings (width, centre, wall), the walls (centre line, thickness) and the stairs (the drawn
stair pieces: centre, size, turn, flights). Every element carries its ``source`` and, where the reading gave one, the
confidence and the method of its primary evidence, its ``status`` and the flags that mark a code-added element
(``inferred``, ``lift_door``, ``parapet``, ``virtual``; ``label_source`` on a level), so the ranker can weight them.
Three sources:

- ``accepted_reading``: the CPU reading of a project the user accepted. Acceptance is explicit: the project's baseline
  (``results/reading_baseline/<p>.json``) must say ``accepted_by_user: true`` with ``accepted_on``, ``accepted_scope``
  (``all``, or ``partial`` with ``accepted_levels``: the levels the user saw) and ``accepted_note`` (the user's words);
  the pipeline's own ``status: ok`` is no acceptance. ``build`` reads the project again, compares the reading's numbers
  with the accepted baseline (``regress.compare``) and refuses a reading that drifted from them (``--allow-drift``
  writes it with ``status: "drifted"`` and the differences). The truth's ``commit`` is the commit the reading was made
  at (``reading_check/commit.txt``, written by ``reading``; a reused reading without it is ``unknown``), never HEAD.
  ``status`` is ``accepted`` when the truth covers the whole building, ``partial`` when the user accepted some levels
  or the baseline left levels out.
- ``synthetic``: a generated project's exact truth (``projects/<p>/truth/reading_truth.json``, already in this format,
  or ``projects/<p>/truth/building.json``, a building dict). It is used as the truth as it is; the reader's output of
  a synthetic project is never its truth.
- ``user_correction``: an element the user added or negated by hand (``truth add`` / ``truth remove``, each naming its
  correction record); a negated element is stored with ``absent: true`` so a reading is penalised for having it.
  A ``build`` never overwrites a ``user_correction`` or ``synthetic`` element (``merge``).

``python -m wenart.reading_check truth build [--projects a,b] [--work DIR] [--fresh] [--allow-drift]`` builds the
truth of every accepted project and every synthetic project with an exact truth; ``truth add --project p --level L
--kind door --center x,y --width w --source user_correction --correction C0012`` adds an element, ``truth remove``
negates one. ``extract(building, ...)`` is the pure part: a building dict in, the truth dict out;
``wenart.reading_check.score`` runs it on the new reading too and matches the two.

``results/reading_corrections.jsonl`` holds one record per correction of the user (``load_corrections``): project,
level, place (building metres, or null when the text gives none), element kind, the reader's answer, the right answer,
the user's words, the lesson id (null with a ``note`` when no lesson states the rule), the date, the source
(``backfill_progress`` for the 3 and 4 Nov 2026 reviews, lessons UL274 to UL328) and the status (the user's own words
count as accepted).

Why: a correction of the user used to become one hand-written rule, and nothing measured whether the rule helped or
hurt the other projects. With the truth of every accepted reading the score (``score.py``) says per commit how far
each reading is from the truth; with the correction store each correction is a labelled example the ranker (R3) and
the reviewers (R4 to R6) learn from, instead of a line in a review table. The truth must be what the user accepted
(not what the pipeline happened to read at HEAD), so the acceptance, the drift check and the commit stamp are explicit.

How: pure functions over the building dict (no AI, no pod); the fields come from ``building.json`` as the pipeline
writes it (rooms: ``polygon``, ``label``, ``room_type``, ``area_computed``; openings: ``type``, ``center``, ``width``,
``wall_id``; walls: ``start``, ``end``, ``thickness``; stairs: the furniture pieces of ``type == "stair"`` with their
``stair`` rule result). Labels are folded with ``wenart.textfold.fold_ascii`` (Turkish letters, letter-spaced words).
The baseline comparison is the regression set's own (counts within its tolerances): a reading within them counts as
the accepted one.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import subprocess
from pathlib import Path
from typing import Iterable, Optional

from wenart.textfold import fold_ascii

REPO = Path(__file__).resolve().parents[2]
TRUTH_DIR = REPO / "results" / "reading_truth"
BASELINE_DIR = REPO / "results" / "reading_baseline"
PROJECTS_DIR = REPO / "projects"
CORRECTIONS_PATH = REPO / "results" / "reading_corrections.jsonl"
SOURCE_ACCEPTED = "accepted_reading"
SOURCE_SYNTHETIC = "synthetic"
SOURCE_USER = "user_correction"
PROTECTED_SOURCES = (SOURCE_USER, SOURCE_SYNTHETIC)      # a build never overwrites these
ELEMENT_TYPES = ("rooms", "doors", "windows", "openings", "walls", "stairs")
KIND_TO_TYPE = {"room": "rooms", "door": "doors", "window": "windows", "opening": "openings", "wall": "walls",
                "stair": "stairs"}
ELEMENT_KINDS = ("wall", "opening", "door", "window", "room", "stair", "level", "label", "region", "roof", "site",
                 "other")
CORRECTION_FIELDS = ("id", "date", "project", "level", "place", "element_kind", "reader_answer", "right_answer",
                     "user_words", "lesson", "source", "status")
ACCEPT_FIELDS = ("accepted_by_user", "accepted_on", "accepted_scope", "accepted_levels", "accepted_note")
KEEP_FIELDS = ("status", "inferred", "lift_door", "parapet", "virtual", "label_source")   # kept where present
SYNTHETIC_TRUTH_FILES = ("truth/reading_truth.json", "truth/building.json")
COMMIT_FILE = "reading_check/commit.txt"
UNKNOWN_COMMIT = "unknown"
ROUND = 3                                   # millimetres: enough for the matching tolerances, keeps the files small
REMOVE_TOL_M = {"rooms": 1.0, "doors": 0.30, "windows": 0.30, "openings": 0.30, "stairs": 1.0, "walls": 0.30}
# 5 Nov 2026 (review: every reader improvement renumbers the reader's ids; an absent entry o_Lk_029 then negated the
# real opening that inherited that id, and the file held one id for two elements): a truth element's identity is its
# place, as in the score; its ``id`` is a truth id of its own (``t_L0_door_0012``), unique in the file, assigned once
# and never reused (``next_truth_id``); the reader's id stays as a ``reader_id`` hint only.
TRUTH_ID_PREFIX = "t_"
TYPE_KIND = {"rooms": "room", "doors": "door", "windows": "window", "openings": "opening", "walls": "wall",
             "stairs": "stair"}


# --- small pure helpers ---------------------------------------------------------------------------------------------

def is_truth_id(value) -> bool:
    return isinstance(value, str) and value.startswith(TRUTH_ID_PREFIX)


def _truth_id_number(value) -> int:
    try:
        return int(str(value).rsplit("_", 1)[1])
    except (IndexError, ValueError):
        return 0


def next_truth_id(truth: dict, level: str, t: str) -> str:
    """A new truth id for an element of type ``t`` on ``level`` (never one the file used before)."""
    n = max(int(truth.get("next_truth_id") or 1), 1 + max(
        (_truth_id_number(e.get("id")) for lv in (truth.get("per_level") or {}).values()
         for els in lv.values() if isinstance(els, list) for e in els if is_truth_id(e.get("id"))), default=0))
    truth["next_truth_id"] = n + 1
    return f"{TRUTH_ID_PREFIX}{level}_{TYPE_KIND[t]}_{n:04d}"


def ensure_truth_ids(truth: dict) -> dict:
    """``truth`` with a truth id on every element (the elements of an older file keep their id as ``reader_id``, or
    as ``old_id`` when it was an id the truth itself made, ``uc_...``); returns the same dict."""
    for lid, lv in (truth.get("per_level") or {}).items():
        for t in ELEMENT_TYPES:
            for e in lv.get(t) or []:
                if not is_truth_id(e.get("id")):
                    old = e.get("id")
                    if old and str(old).startswith("uc_"):
                        e.setdefault("old_id", old)
                    elif old and not e.get("reader_id"):
                        e["reader_id"] = old
                    e["id"] = next_truth_id(truth, lid, t)
    return truth


def records_to_truth_ids(truth: dict, records: list[dict], project: str, *, date: Optional[str] = None,
                         reason: str = "truth ids by place, 5 Nov 2026") -> list[str]:
    """The project's correction records moved to the truth's own ids (in place; the one-time move of 5 Nov 2026):
    ``element_ids`` name the truth elements (a reader's id that names one becomes its truth id, the others stay as
    they were), ``reader_ids`` keep the reader's ids as hints, ``truth_applied`` results name truth ids; a changed
    record gets a ``history`` entry. A reader's id that names several truth elements (a retype: the negated opening
    and the door) names those that carry the record's correction. Returns one line per change."""
    elems = [(lid, t, e) for lid, lv in (truth.get("per_level") or {}).items() for t in ELEMENT_TYPES
             for e in lv.get(t) or []]

    def named(old_id, rid, level=None, t=None):
        hits = [(lid, tt, e) for lid, tt, e in elems if old_id in (e.get("reader_id"), e.get("old_id"))
                and (level is None or lid == level) and (t is None or tt == t)]
        mine = [h for h in hits if rid in (h[2].get("corrections") or [])]
        return mine or hits

    lines = []
    for rec in records:
        if rec.get("project") != project or not rec.get("element_ids") or rec.get("reader_ids") is not None:
            continue
        old_ids = list(rec["element_ids"])
        new_ids = []
        for x in old_ids:
            hits = named(x, rec.get("id"))
            new_ids.extend(h[2]["id"] for h in hits if h[2]["id"] not in new_ids) if hits else new_ids.append(x)
        applied = rec.get("truth_applied") or {}
        for res in applied.get("results") or []:
            hits = named(res.get("id"), rec.get("id"), res.get("level"), res.get("type"))
            if hits:
                res.setdefault("reader_id", res["id"])
                res["id"] = hits[0][2]["id"]
        rec["element_ids"], rec["reader_ids"] = new_ids, old_ids
        rec.setdefault("history", []).append({"date": date or today(), "old_element_ids": old_ids, "reason": reason})
        lines.append(f"{rec['id']}: {len(old_ids)} element ids -> {len(new_ids)} ids, "
                     f"{sum(1 for i in new_ids if is_truth_id(i))} of them truth ids")
    return lines


def same_place_pairs(t: str, a: list, b: list) -> list:
    """The ``(i, j)`` pairs of elements of ``a`` and ``b`` (one level, one type) that are the same element by place:
    the score's own rules (``score.match_kind``: openings of one class by centre within ``OPENING_CENTER_M``, rooms by
    label and centroid or polygon IoU, walls by centre-line overlap, stairs by centre), one to one."""
    from wenart.reading_check import score as SC

    return SC.match_kind(t, a, b)


def norm_label(label: Optional[str]) -> str:
    """A room or level label normalised for matching: upper case, Turkish diacritics folded, letter-spaced words
    joined, white space collapsed (``'S a l o n'`` -> ``'SALON'``, ``'Çocuk Odası'`` -> ``'COCUK ODASI'``)."""
    if not label:
        return ""
    return " ".join(fold_ascii(str(label)).upper().split())


def _pt(p) -> list:
    return [round(float(p[0]), ROUND), round(float(p[1]), ROUND)]


def _poly(poly) -> list:
    return [_pt(p) for p in (poly or [])]


def centroid(polygon: list) -> Optional[list]:
    """The area centroid of a polygon (shoelace); the mean of the points when the area is zero; None when empty."""
    pts = [(float(p[0]), float(p[1])) for p in (polygon or [])]
    if not pts:
        return None
    if len(pts) < 3:
        return _pt((sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)))
    a2 = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        cross = x0 * y1 - x1 * y0
        a2 += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    if abs(a2) < 1e-9:
        return _pt((sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)))
    return _pt((cx / (3 * a2), cy / (3 * a2)))


def _primary(element: dict) -> dict:
    """The primary evidence of an element: the first evidence entry that is a dict (else empty)."""
    for ev in element.get("evidence") or []:
        if isinstance(ev, dict):
            return ev
    return {}


def confidence_of(element: dict) -> Optional[float]:
    """The confidence of an element's primary evidence (the first evidence entry that carries one), else None."""
    for ev in element.get("evidence") or []:
        if isinstance(ev, dict) and ev.get("confidence") is not None:
            try:
                return round(float(ev["confidence"]), 3)
            except (TypeError, ValueError):
                return None
    return None


def method_of(element: dict) -> Optional[str]:
    """The method of an element's primary evidence (vector / ocr / ai / inferred / raster ...), else None."""
    return _primary(element).get("method")


def _keep(element: dict, out: dict) -> dict:
    """``out`` with the ``KEEP_FIELDS`` of ``element`` that are set (a code-added element stays recognisable)."""
    for k in KEEP_FIELDS:
        v = element.get(k)
        if v not in (None, False):
            out[k] = v
    return out


def git_head(repo: Path = REPO) -> Optional[str]:
    """The current commit (``git rev-parse HEAD``), None outside a repository."""
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


def today() -> str:
    return _dt.date.today().isoformat()


# --- the truth of one building --------------------------------------------------------------------------------------

def _room(r: dict, source: str) -> dict:
    area = r.get("area_computed")
    out = {"id": r.get("id"), "label": r.get("label"), "room_type": r.get("room_type"),
           "area": round(float(area), ROUND) if area is not None else None,
           "centroid": centroid(r.get("polygon") or []), "polygon": _poly(r.get("polygon")),
           "source": source, "confidence": confidence_of(r), "method": method_of(r)}
    return _keep(r, out)


def _opening(o: dict, source: str) -> dict:
    out = {"id": o.get("id"), "type": o.get("type"), "width": round(float(o["width"]), ROUND) if o.get("width")
           is not None else None, "center": _pt(o["center"]) if o.get("center") else None, "wall_id": o.get("wall_id"),
           "source": source, "confidence": confidence_of(o), "method": method_of(o)}
    return _keep(o, out)


def _wall(w: dict, source: str) -> dict:
    out = {"id": w.get("id"), "start": _pt(w["start"]), "end": _pt(w["end"]),
           "thickness": round(float(w["thickness"]), ROUND) if w.get("thickness") is not None else None,
           "source": source, "confidence": confidence_of(w), "method": method_of(w)}
    return _keep(w, out)


def _stair(f: dict, source: str) -> dict:
    fp = f.get("footprint") or {}
    st = f.get("stair") or {}
    flights = [{"start": _pt(fl["start"]), "end": _pt(fl["end"]), "width": fl.get("width"), "lines": fl.get("lines")}
               for fl in (st.get("flights") or []) if fl.get("start") and fl.get("end")]
    out = {"id": f.get("id"), "center": _pt(fp["center"]) if fp.get("center") else None,
           "size": [round(float(s), ROUND) for s in fp["size"]] if fp.get("size") else None,
           "rotation_deg": fp.get("rotation_deg"), "room_id": f.get("room_id"), "turn": st.get("turn"),
           "flights": flights, "source": source, "confidence": confidence_of(f), "method": method_of(f)}
    return _keep(f, out)


def stairs_of(building: dict) -> list:
    """The drawn stair pieces of a building: the furniture of ``type == "stair"`` (where the pipeline records them)."""
    return [f for f in building.get("furniture") or [] if f.get("type") == "stair"]


def extract(building: dict, *, project: Optional[str] = None, status: str = "accepted", commit: Optional[str] = None,
            date: Optional[str] = None, leave_out: Iterable[str] = (), source: str = SOURCE_ACCEPTED) -> dict:
    """The truth dict of a building dict (pure). ``leave_out`` names the levels (by label) that stay out, as the
    baseline's ``levels_left_out`` lists them; ``source`` is stamped on every element."""
    skip = {norm_label(lbl) for lbl in leave_out}
    levels = [lv for lv in building.get("levels") or [] if norm_label(lv.get("label")) not in skip]
    ids = [lv["id"] for lv in levels]
    per = {lid: {t: [] for t in ELEMENT_TYPES} for lid in ids}
    for r in building.get("rooms") or []:
        if r.get("level_id") in per:
            per[r["level_id"]]["rooms"].append(_room(r, source))
    for o in building.get("openings") or []:
        if o.get("level_id") not in per:
            continue
        kind = {"door": "doors", "window": "windows"}.get(o.get("type"), "openings")
        per[o["level_id"]][kind].append(_opening(o, source))
    for w in building.get("walls") or []:
        if w.get("level_id") in per and w.get("start") and w.get("end"):
            per[w["level_id"]]["walls"].append(_wall(w, source))
    for f in stairs_of(building):
        if f.get("level_id") in per:
            per[f["level_id"]]["stairs"].append(_stair(f, source))
    return {"project": project or (building.get("project") or {}).get("id"), "source": source,
            "status": status, "commit": commit, "date": date or today(),
            "levels": [_keep(lv, {"id": lv["id"], "label": lv.get("label"), "elevation": lv.get("elevation"),
                                  "order": lv.get("order"), "source": source}) for lv in levels],
            "levels_left_out": sorted(leave_out), "per_level": per}


def positives(elements: list) -> list:
    """The elements that exist (an ``absent: true`` entry is a negation, not a truth element)."""
    return [e for e in elements or [] if not e.get("absent")]


def counts(truth: dict) -> dict:
    """``{"levels": n, "rooms": n, ...}`` of a truth dict (the report's table; absent entries not counted)."""
    out = {"levels": len(truth.get("levels") or [])}
    for t in ELEMENT_TYPES:
        out[t] = sum(len(positives(lv.get(t))) for lv in (truth.get("per_level") or {}).values())
    return out


# --- acceptance, drift, commit --------------------------------------------------------------------------------------

def acceptance(baseline: Optional[dict]) -> Optional[dict]:
    """``{"scope", "levels", "on", "note"}`` when the baseline says ``accepted_by_user: true`` (the user's explicit
    acceptance), else None. The pipeline's own ``status: ok`` is not an acceptance."""
    if not baseline or baseline.get("accepted_by_user") is not True:
        return None
    scope = baseline.get("accepted_scope") or "all"
    return {"scope": "partial" if scope == "partial" else "all",
            "levels": list(baseline.get("accepted_levels") or []) if scope == "partial" else None,
            "on": baseline.get("accepted_on"), "note": baseline.get("accepted_note")}


def accepted_projects(baseline_dir: Path = BASELINE_DIR) -> list[str]:
    """The projects whose baseline the user accepted (``accepted_by_user: true``)."""
    out = []
    for path in sorted(Path(baseline_dir).glob("*.json")):
        try:
            if acceptance(json.loads(path.read_text(encoding="utf-8"))):
                out.append(path.stem)
        except (OSError, ValueError):
            continue
    return out


def synthetic_truth_file(project: str, projects_dir: Path = PROJECTS_DIR) -> Optional[Path]:
    """The exact truth file of a synthetic project (``SYNTHETIC_TRUTH_FILES``, the first that exists), else None."""
    for rel in SYNTHETIC_TRUTH_FILES:
        path = Path(projects_dir) / project / rel
        if path.is_file():
            return path
    return None


def synthetic_projects(projects_dir: Path = PROJECTS_DIR) -> list[str]:
    """The ``synthetic-*`` projects that carry an exact truth."""
    return sorted(p.name for p in Path(projects_dir).glob("synthetic-*")
                  if p.is_dir() and synthetic_truth_file(p.name, projects_dir))


def synthetic_truth(project: str, path: Path, *, date: Optional[str] = None) -> dict:
    """The truth of a synthetic project from its exact truth file: ``reading_truth.json`` (this format; every element
    stamped ``source: synthetic``) or ``building.json`` (``extract``)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    try:
        rel = str(Path(path).resolve().relative_to(REPO))
    except ValueError:
        rel = str(path)
    if "per_level" in data:
        per = {}
        for lid, lv in (data.get("per_level") or {}).items():
            per[lid] = {}
            for t in ELEMENT_TYPES:
                per[lid][t] = [dict(e, source=SOURCE_SYNTHETIC, confidence=e.get("confidence"),
                                    centroid=e.get("centroid") or (centroid(e.get("polygon")) if t == "rooms"
                                                                   else None))
                               if t == "rooms" else dict(e, source=SOURCE_SYNTHETIC, confidence=e.get("confidence"))
                               for e in (lv.get(t) or [])]
        out = {"project": project, "source": SOURCE_SYNTHETIC, "status": "accepted", "commit": None,
               "date": date or today(),
               "levels": [dict(lv, source=SOURCE_SYNTHETIC) for lv in data.get("levels") or []],
               "levels_left_out": [], "per_level": per}
        for k in ("failure_class", "lesson", "summary"):
            if data.get(k) is not None:
                out[k] = data[k]
    else:
        out = extract(data, project=project, status="accepted", commit=None, date=date, source=SOURCE_SYNTHETIC)
    out["truth_file"] = rel
    return out


def read_commit(folder: Path) -> str:
    """The commit a reading was made at (``reading_check/commit.txt``), ``unknown`` when the reading has none."""
    path = Path(folder) / COMMIT_FILE
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return UNKNOWN_COMMIT
    return text.split()[0] if text else UNKNOWN_COMMIT


def reading(project: str, work: Path, fresh: bool = False) -> Path:
    """``work/<project>`` with its ``building.json``: the reading already there, or a new CPU reading stamped with
    the commit it was made at (``reading_check/commit.txt``)."""
    out = Path(work) / project
    if fresh or not (out / "building.json").is_file():
        from wenart.reading_check import regress as RG
        out = RG.read_project(project, Path(work))
        (out / "reading_check").mkdir(parents=True, exist_ok=True)
        (out / COMMIT_FILE).write_text((git_head() or UNKNOWN_COMMIT) + "\n", encoding="utf-8")
    return out


def drift(baseline: dict, numbers: dict) -> list[str]:
    """The differences of a reading's key numbers from the accepted baseline (``regress.compare``; its count lines
    are symmetric, so a reading with more rooms than the user accepted is a drift too; a better verdict or status is
    no drift of the content). A level the user never saw is caught by ``truth_of`` on the truth's own levels."""
    from wenart.reading_check import regress as RG

    return list(RG.compare(baseline, numbers))


def truth_of(project: str, building: dict, baseline: Optional[dict], *, numbers: Optional[dict] = None,
             commit: Optional[str] = None, date: Optional[str] = None) -> tuple[Optional[dict], list[str]]:
    """The accepted-reading truth of a project (pure): ``(truth, messages)``. None without the user's acceptance in
    the baseline; ``status: "drifted"`` with ``drift`` when the reading's numbers differ from the accepted ones; the
    levels limited to the accepted ones (a partial acceptance) and without the baseline's ``levels_left_out``."""
    acc = acceptance(baseline)
    if acc is None:
        return None, [f"{project}: not accepted by the user: the baseline has no accepted_by_user: true "
                      f"(after the user accepts: regress --update, set the acceptance fields, then truth build)"]
    diffs = drift(baseline, numbers) if numbers is not None else []
    leave_out = (baseline or {}).get("levels_left_out") or []
    truth = extract(building, project=project, commit=commit or UNKNOWN_COMMIT, date=date, leave_out=leave_out)
    if acc["scope"] == "partial":
        keep = set(acc["levels"] or [])
        truth["levels"] = [lv for lv in truth["levels"] if lv["id"] in keep]
        truth["per_level"] = {lid: v for lid, v in truth["per_level"].items() if lid in keep}
    unseen = [lv["id"] for lv in truth["levels"] if lv["id"] not in set((baseline or {}).get("levels") or [])]
    if unseen:                                        # a level the reading has and the user never saw
        diffs.append(f"levels not accepted: {unseen}")
    truth["status"] = "drifted" if diffs else ("partial" if acc["scope"] == "partial" or leave_out else "accepted")
    truth["accepted"] = {"on": acc["on"], "scope": acc["scope"], "levels": acc["levels"], "note": acc["note"]}
    if diffs:
        truth["drift"] = diffs
    msgs = [f"{project}: the reading drifted from the accepted baseline: " + "; ".join(diffs)] if diffs else []
    return truth, msgs


OPENING_TYPES = ("doors", "windows", "openings")
ABSENT_WALL_COVER = 0.8         # a negated wall span suppresses a reading wall it covers this much of


def _absent_wall_pairs(absent: list, walls: list) -> list:
    """``(i, j)`` pairs of negated wall spans and reading walls (5 Nov 2026, review: a short negated span must not
    remove a long wall): the span lies within the reading wall's line (``score.WALL_LATERAL_M``) and covers at least
    ``ABSENT_WALL_COVER`` of the reading wall's length and of its own; one to one, best cover first."""
    from wenart.reading_check import score as SC

    pairs = []
    for i, n in enumerate(absent):
        for j, w in enumerate(walls):
            ln, lw = _dist(n["start"], n["end"]), _dist(w["start"], w["end"])
            if ln < 1e-6 or lw < 1e-6:
                continue
            ox, oy = float(w["start"][0]), float(w["start"][1])
            ux, uy = (float(w["end"][0]) - ox) / lw, (float(w["end"][1]) - oy) / lw
            along, lateral = [], 0.0
            for q in (n["start"], n["end"]):
                dx, dy = float(q[0]) - ox, float(q[1]) - oy
                along.append(dx * ux + dy * uy)
                lateral = max(lateral, abs(dx * uy - dy * ux))
            if lateral > SC.WALL_LATERAL_M:
                continue
            overlap = min(lw, max(along)) - max(0.0, min(along))
            if overlap >= ABSENT_WALL_COVER * lw and overlap >= ABSENT_WALL_COVER * ln:
                pairs.append((-overlap / lw, i, j))
    return SC._greedy(pairs)


def assign_points(a: list, b: list, tol: float, key: str = "center") -> list:
    """``(i, j)`` pairs of elements of ``a`` and ``b`` whose points (``key``) lie within ``tol``, one to one, with the
    least total displacement (the Hungarian method; pure). The score's greedy choice takes the nearest pair first, so
    a reading shifted a few centimetres can swap two elements that stand close together (review of round 3: real10's
    L0 lift openings o_L0_007, o_L0_009, o_L0_010); the merge keeps every element's truth id with this."""
    ia = [i for i, e in enumerate(a) if e.get(key)]
    jb = [j for j, e in enumerate(b) if e.get(key)]
    na, nb = len(ia), len(jb)
    if not na or not nb:
        return []
    n = na + nb
    inf = 1e9
    cost = [[0.0] * n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            if r < na and c < nb:
                d = _dist(a[ia[r]][key], b[jb[c]][key])
                cost[r][c] = d if d <= tol else inf
            elif r < na or c < nb:
                cost[r][c] = tol                         # left unmatched
    # the Hungarian method (potentials, O(n^3)), 1-based
    u, v, p, way = [0.0] * (n + 1), [0.0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0], j0 = i, 0
        minv, used = [inf * 10] * (n + 1), [False] * (n + 1)
        while True:
            used[j0] = True
            i0, delta, j1 = p[j0], inf * 10, 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j], way[j] = cur, j0
                    if minv[j] < delta:
                        delta, j1 = minv[j], j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    out = []
    for j in range(1, n + 1):
        r, c = p[j] - 1, j - 1
        if r < na and c < nb and cost[r][c] < inf:
            out.append((ia[r], jb[c]))
    return sorted(out)


def _group_pairs(t: str, a: list, b: list) -> list:
    """The merge's same-place pairs: points (doors, windows, openings, stairs) by the least total displacement
    (``assign_points``) within the score's tolerances, rooms and walls by the score's rules (``same_place_pairs``);
    ``t == "openings*"``: doors, windows and openings matched across their lists, as the user's correction holds its
    place whatever list the reader put the element in."""
    from wenart.reading_check import score as SC

    if t in ("openings*",) + OPENING_TYPES:
        return assign_points(a, b, SC.OPENING_CENTER_M)
    if t == "stairs":
        return assign_points(a, b, SC.STAIR_CENTER_M)
    return same_place_pairs(t, a, b)


def merge(existing: Optional[dict], new: dict) -> dict:
    """``new`` (a reading's truth, ``extract``: the reader's ids) with every protected element of ``existing`` kept
    (pure): elements and levels whose ``source`` is ``user_correction`` or ``synthetic`` (when the new truth is not
    synthetic), and every ``absent`` negation. Identity is place, never the reader's id. In the score's order (5 Nov
    2026, review: a negation took a reading element before the accepted element at its place could keep it):
    (a) the protected positives take the reading elements at their places (the opening class across its lists: a
    user's door wins its place whatever list the reader put it in), and those reading elements give way;
    (b) the earlier accepted elements take the reading elements at their places (own list), which keep their truth
    ids; (c) only then do the negations take what is left at their places (own list; a negated wall span only a
    reading wall it covers, ``_absent_wall_pairs``), and those give way. Every other reading element gets a new truth
    id; every element keeps the reader's id as ``reader_id``. The applied correction ids and the truth id counter are
    kept too."""
    out = json.loads(json.dumps(new))
    for lv in (out.get("per_level") or {}).values():
        for t in ELEMENT_TYPES:
            for e in lv.get(t) or []:
                if not is_truth_id(e.get("id")):
                    e["reader_id"] = e.get("reader_id") or e.get("id")
                    e["id"] = None
    if not existing:
        out.pop("next_truth_id", None)
        return ensure_truth_ids(out)
    old = ensure_truth_ids(json.loads(json.dumps(existing)))
    out["next_truth_id"] = int(old.get("next_truth_id") or 1)
    protect = tuple(s for s in PROTECTED_SOURCES if s != out.get("source"))
    kept = 0
    per = out.setdefault("per_level", {})
    for lid, lv in (old.get("per_level") or {}).items():
        olds = {t: lv.get(t) or [] for t in ELEMENT_TYPES}
        prot = {t: [e for e in olds[t] if e.get("absent") or e.get("source") in protect] for t in ELEMENT_TYPES}
        if lid not in per and not any(prot.values()):
            continue
        target = per.setdefault(lid, {k: [] for k in ELEMENT_TYPES})
        news = {t: list(target.get(t) or []) for t in ELEMENT_TYPES}
        gone = {t: set() for t in ELEMENT_TYPES}

        def free(t):
            return [(j, e) for j, e in enumerate(news[t]) if j not in gone[t]]

        # (a) the protected positives keep their reading elements: first in their own list, then (the opening
        # class) the ones still without an element take one of another opening list at their place
        held = set()
        for t in ELEMENT_TYPES:
            pos = [e for e in prot[t] if not e.get("absent")]
            cand = free(t)
            for i, k in _group_pairs(t, pos, [e for _j, e in cand]):
                gone[t].add(cand[k][0])
                held.add(id(pos[i]))
        pos = [e for t in OPENING_TYPES for e in prot[t] if not e.get("absent") and id(e) not in held]
        cand = [(t, j, e) for t in OPENING_TYPES for j, e in free(t)]
        for _i, k in _group_pairs("openings*", pos, [e for _t, _j, e in cand]):
            gone[cand[k][0]].add(cand[k][1])
        for t in ELEMENT_TYPES:
            # (b) the accepted elements keep theirs and their truth ids
            rest = [e for e in olds[t] if not (e.get("absent") or e.get("source") in protect)]
            cand = free(t)
            taken = set()
            for i, k in _group_pairs(t, rest, [e for _j, e in cand]):
                news[t][cand[k][0]]["id"] = rest[i]["id"]
                taken.add(cand[k][0])
            # (c) the negations take what is left
            neg = [e for e in prot[t] if e.get("absent")]
            left = [(j, e) for j, e in free(t) if j not in taken]
            pairs = (_absent_wall_pairs(neg, [e for _j, e in left]) if t == "walls"
                     else _group_pairs(t, neg, [e for _j, e in left]))
            for _i, k in pairs:
                gone[t].add(left[k][0])
            target[t] = [e for j, e in enumerate(news[t]) if j not in gone[t]] + prot[t]
            kept += len(prot[t])
        if lid not in {l["id"] for l in out.get("levels") or []}:
            src_level = next((l for l in old.get("levels") or [] if l["id"] == lid), None)
            if src_level and (src_level.get("source") in protect or lid in per):
                out["levels"].append(src_level)
    ensure_truth_ids(out)
    corrections = sorted(set(old.get("corrections") or []) | set(out.get("corrections") or []))
    if corrections:
        out["corrections"] = corrections
    if kept:
        out["kept_from_previous"] = kept
    return out


# --- files ----------------------------------------------------------------------------------------------------------

def load_baseline(project: str, baseline_dir: Path = BASELINE_DIR) -> Optional[dict]:
    path = Path(baseline_dir) / f"{project}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def load_truth(project: str, truth_dir: Path = TRUTH_DIR) -> Optional[dict]:
    path = Path(truth_dir) / f"{project}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def write_truth(project: str, truth: dict, truth_dir: Path = TRUTH_DIR) -> Path:
    Path(truth_dir).mkdir(parents=True, exist_ok=True)
    path = Path(truth_dir) / f"{project}.json"
    path.write_text(json.dumps(truth, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


def truth_projects(truth_dir: Path = TRUTH_DIR) -> list[str]:
    return sorted(p.stem for p in Path(truth_dir).glob("*.json"))


def default_projects(baseline_dir: Path = BASELINE_DIR, projects_dir: Path = PROJECTS_DIR) -> list[str]:
    """What ``truth build`` builds without ``--projects``: the accepted projects and the synthetic ones."""
    return sorted(set(accepted_projects(baseline_dir)) | set(synthetic_projects(projects_dir)))


def build(projects: list[str], work: Path, *, fresh: bool = False, allow_drift: bool = False,
          truth_dir: Path = TRUTH_DIR, baseline_dir: Path = BASELINE_DIR, projects_dir: Path = PROJECTS_DIR) -> dict:
    """Build and write the truth of each project (the module docstring); returns ``{project: truth}`` of the ones
    written. A project without the user's acceptance, a drifted reading (unless ``allow_drift``) or a failed reading
    is printed and skipped; the others are still written."""
    out = {}
    for p in projects:
        synth = synthetic_truth_file(p, projects_dir)
        if synth is not None:
            truth = synthetic_truth(p, synth)
        else:
            base = load_baseline(p, baseline_dir)
            if acceptance(base) is None:
                print(truth_of(p, {}, base)[1][0])
                continue
            try:
                folder = reading(p, work, fresh)
                b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
                from wenart.reading_check import regress as RG
                nums = RG.numbers(folder)
            except Exception as exc:                             # a failed reading must not stop the other projects
                print(f"{p}: reading failed: {exc}")
                continue
            truth, msgs = truth_of(p, b, base, numbers=nums, commit=read_commit(folder))
            for m in msgs:
                print(m)
            if truth is None or (truth["status"] == "drifted" and not allow_drift):
                if truth is not None:
                    print(f"{p}: not written (--allow-drift writes it with status drifted)")
                continue
        truth = merge(load_truth(p, truth_dir), truth)
        write_truth(p, truth, truth_dir)
        c = counts(truth)
        print(f"{p}: truth written ({truth['source']}, {truth['status']}, commit "
              f"{(truth.get('commit') or '-')[:12]}; " + ", ".join(f"{k} {v}" for k, v in c.items())
              + (f"; {truth['kept_from_previous']} protected elements kept" if truth.get("kept_from_previous") else "")
              + ")")
        out[p] = truth
    return out


# --- user corrections into the truth --------------------------------------------------------------------------------

def _parse_xy(text) -> Optional[list]:
    if text is None:
        return None
    if isinstance(text, (list, tuple)):
        return _pt(text)
    x, y = str(text).split(",")
    return _pt((float(x), float(y)))


def _parse_poly(text) -> list:
    if not text:
        return []
    if isinstance(text, (list, tuple)):
        return _poly(text)
    return [_parse_xy(part) for part in str(text).split(";") if part.strip()]


def _dist(a, b) -> float:
    return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def _anchor(kind: str, element: dict) -> Optional[list]:
    """The point an element is found by: a room's centroid, an opening's or stair's centre, a wall's mid point."""
    if kind == "rooms":
        return element.get("centroid") or centroid(element.get("polygon") or [])
    if kind == "walls":
        s, e = element.get("start"), element.get("end")
        return _pt(((s[0] + e[0]) / 2, (s[1] + e[1]) / 2)) if s and e else None
    return element.get("center")


def new_truth(project: str, *, source: str = SOURCE_USER, date: Optional[str] = None) -> dict:
    """An empty truth file for a project that has none yet (``partial``: it holds only what the user confirmed)."""
    return {"project": project, "source": source, "status": "partial", "commit": None, "date": date or today(),
            "levels": [], "levels_left_out": [], "per_level": {}}


def element_from_fields(kind: str, fields: dict, *, source: str, correction: Optional[str],
                        date: Optional[str] = None) -> dict:
    """A truth element of ``kind`` (``KIND_TO_TYPE`` key) from command-line fields (pure): ``id``, ``label``,
    ``room_type``, ``area``, ``polygon`` (``x,y;x,y;...``), ``center`` (``x,y``), ``width``, ``wall_id``, ``start``,
    ``end``, ``thickness``, ``size`` (``w,d``), ``turn``."""
    t = KIND_TO_TYPE[kind]
    el: dict = {"id": fields.get("id")}
    if t == "rooms":
        poly = _parse_poly(fields.get("polygon"))
        el.update(label=fields.get("label"), room_type=fields.get("room_type"),
                  area=float(fields["area"]) if fields.get("area") is not None else None,
                  centroid=_parse_xy(fields.get("center")) or centroid(poly), polygon=poly)
        if not el["centroid"]:
            raise ValueError("a room needs --polygon or --center")
    elif t == "walls":
        s, e = _parse_xy(fields.get("start")), _parse_xy(fields.get("end"))
        if not s or not e:
            raise ValueError("a wall needs --start and --end")
        el.update(start=s, end=e, thickness=float(fields["thickness"]) if fields.get("thickness") is not None
                  else None)
    elif t == "stairs":
        c = _parse_xy(fields.get("center"))
        if not c:
            raise ValueError("a stair needs --center")
        size = _parse_xy(fields.get("size")) if fields.get("size") else None
        el.update(center=c, size=size, rotation_deg=None, room_id=None, turn=fields.get("turn"), flights=[])
    else:
        c = _parse_xy(fields.get("center"))
        if not c:
            raise ValueError(f"a {kind} needs --center")
        el.update(type=kind, width=float(fields["width"]) if fields.get("width") is not None else None, center=c,
                  wall_id=fields.get("wall_id"))
    el.update(source=source, confidence=None, method="user", correction=correction, added_on=date or today())
    return el


def reading_element(building: dict, element_id: str, level: Optional[str] = None) -> Optional[tuple]:
    """``(type, truth-shaped element)`` of the reading's element ``element_id`` (``extract``'s shape: its place and
    kind), or None."""
    if not building or not element_id:
        return None
    tr = extract(building)
    for lid, lv in tr["per_level"].items():
        if level is not None and lid != level:
            continue
        for t in ELEMENT_TYPES:
            for e in lv.get(t) or []:
                if e.get("id") == element_id:
                    return t, e
    return None


def find_element(truth: dict, t: str, level: str, fields: dict, reading: Optional[dict] = None) -> Optional[dict]:
    """The truth element ``fields`` names on ``level``: by its truth id; else the reader's id resolved to its place in
    ``reading`` (the reading the id was taken from) and found there by place (``same_place_pairs``). None when the
    truth holds nothing there. 5 Nov 2026 (review: a stale ``reader_id`` hint named another element after a
    renumbering): a reader's id without its reading, an id the reading lacks, a truth id the file lacks, or an id the
    reading holds as another type, is refused (ValueError naming the truth id to use where the hint finds one)."""
    bucket = ((truth.get("per_level") or {}).get(level) or {}).get(t) or []
    rid = fields.get("id")
    if not rid:
        return None
    hit = next((e for e in bucket if e.get("id") == rid), None)
    if hit is not None:
        return hit
    if is_truth_id(rid):
        raise ValueError(f"{rid}: no such truth id on {level} ({t})")
    hints = [e["id"] for e in bucket if e.get("reader_id") == rid]
    use = f" (the truth id there may be {', '.join(hints)}; check it and give that)" if hints else ""
    if not reading:
        raise ValueError(f"{rid} is a reader's id: give the reading it was taken from (--reading) or a truth id{use}")
    found = reading_element(reading, rid, level)
    if found is None:
        raise ValueError(f"{rid}: the given reading has no such element on {level}{use}")
    if found[0] != t:
        raise ValueError(f"{rid}: the given reading holds it as {found[0]}, not {t}{use}")
    pairs = same_place_pairs(t, bucket, [found[1]])
    return bucket[pairs[0][0]] if pairs else None


def _ensure_level(truth: dict, level: str, *, source: str, label: Optional[str] = None,
                  elevation: Optional[float] = None, order: Optional[int] = None) -> dict:
    """The level entry of ``level`` in ``truth``, created with ``source`` when the truth has none."""
    for lv in truth.setdefault("levels", []):
        if lv["id"] == level:
            return lv
    lv = {"id": level, "label": label, "elevation": elevation, "order": order, "source": source}
    truth["levels"].append(lv)
    truth.setdefault("per_level", {})[level] = {k: [] for k in ELEMENT_TYPES}
    return lv


# 5 Nov 2026 (review of the located corrections): a confirm keeps the reading's element exactly (a stair keeps its
# rotation, room and flights) and changes only its source and correction ids; a field the user gives that differs
# is a change (``changed``, method ``user``); an element touched by several corrections keeps all of their ids.
CONFIRM_FIELDS = ("label", "room_type", "area", "polygon", "center", "width", "wall_id", "start", "end", "thickness",
                  "size", "turn")


def _with_correction(el: dict, correction: Optional[str]) -> dict:
    """``el`` with ``correction`` added to its ``corrections`` (every correction that touched it, in order) and set as
    its ``correction`` (the latest, kept for older readers of the files)."""
    ids = list(el.get("corrections") or ([el["correction"]] if el.get("correction") else []))
    if correction and correction not in ids:
        ids.append(correction)
    if ids:
        el["corrections"] = ids
    if correction:
        el["correction"] = correction
    return el


def _annotate(el: dict, fields: dict) -> dict:
    """The evidence and note a caller gives with a correction (the drawing's entities that prove it), kept on the
    element; the command line does not pass them, Python callers may."""
    if fields.get("evidence"):
        el["evidence"] = list(fields["evidence"])
    if fields.get("note"):
        el["note"] = str(fields["note"])
    return el


def _parsed(t: str, key: str, value):
    if key in ("center", "start", "end", "size"):
        return _parse_xy(value)
    if key == "polygon":
        return _parse_poly(value)
    if key in ("area", "width", "thickness"):
        return round(float(value), ROUND)
    return value


def confirm_element(kind: str, existing: dict, fields: dict, *, source: str = SOURCE_USER,
                    correction: Optional[str] = None, date: Optional[str] = None) -> dict:
    """The user's confirm of an element the truth already holds by its id (pure): a copy of ``existing`` with only
    ``source`` and the correction ids changed; a given field that differs from the element is applied and listed in
    ``changed`` (then ``method`` is ``user`` and the reading's confidence no longer applies). A negated element that
    is confirmed exists again."""
    t = KIND_TO_TYPE[kind]
    el = json.loads(json.dumps(existing))
    changed = []
    for key in CONFIRM_FIELDS:
        if fields.get(key) in (None, ""):
            continue
        value = _parsed(t, key, fields[key])
        slot = "centroid" if t == "rooms" and key == "center" else key       # a room is found by its centroid
        if el.get(slot) != value:
            el[slot] = value
            changed.append(key)
    if t == "rooms" and "polygon" in changed and "center" not in changed:
        el["centroid"] = centroid(el.get("polygon") or [])
    if changed:
        el["changed"] = sorted(set(el.get("changed") or []) | set(changed))
        el.update(method="user", confidence=None)
    for k in ("absent", "removed_on"):
        el.pop(k, None)
    el.update(source=source, confirmed_on=date or today())
    _with_correction(el, correction)
    return _annotate(el, fields)


def add_element(truth: dict, kind: str, level: str, fields: dict, *, source: str = SOURCE_USER,
                correction: Optional[str] = None, date: Optional[str] = None, reading: Optional[dict] = None) -> dict:
    """``truth`` with an element (or, ``kind == "level"``, a level) added by the user (pure in the sense that it
    returns the changed dict it was given); the element is returned in ``truth["last_added"]``. When the truth
    already holds the element the given ``id`` names (``find_element``: a truth id, or the reader's id resolved to
    its place in ``reading``), it is confirmed (``confirm_element``): kept exactly, only its source and correction ids
    change, unless a given field differs. A new element gets a truth id; a reader's id stays as ``reader_id``."""
    if kind == "level":
        lv = _ensure_level(truth, level, source=source, label=fields.get("label"),
                           elevation=float(fields["elevation"]) if fields.get("elevation") is not None else None,
                           order=int(fields["order"]) if fields.get("order") is not None else None)
        lv.update({k: v for k, v in (("label", fields.get("label")),) if v is not None}, correction=correction)
        truth["last_added"] = lv
    else:
        if kind not in KIND_TO_TYPE:
            raise ValueError(f"kind {kind!r}: one of {', '.join(KIND_TO_TYPE)} or level")
        t = KIND_TO_TYPE[kind]
        _ensure_level(truth, level, source=source)
        bucket = truth["per_level"].setdefault(level, {k: [] for k in ELEMENT_TYPES}).setdefault(t, [])
        hit = find_element(truth, t, level, fields, reading)
        existing = next((i for i, e in enumerate(bucket) if e is hit), None)
        if existing is not None:                 # a confirm (or a retype) of the reading's own element: kept exactly
            el = confirm_element(kind, bucket[existing], {k: v for k, v in fields.items() if k != "id"},
                                 source=source, correction=correction, date=date)
            bucket[existing] = el
        else:
            given = dict(fields)
            found = reading_element(reading, fields.get("id"), level) if reading and fields.get("id") else None
            if found is not None and found[0] == t:          # the reading's element: its place and size
                src = found[1]
                for key in ("center", "width", "wall_id", "start", "end", "thickness", "label", "room_type", "area",
                            "polygon"):
                    slot = "centroid" if key == "center" and t == "rooms" else key
                    if given.get(key) in (None, "") and src.get(slot) is not None:
                        given[key] = src[slot]
            el = element_from_fields(kind, given, source=source, correction=correction, date=date)
            if fields.get("id") and not is_truth_id(fields["id"]):
                el["reader_id"] = fields["id"]
            el["id"] = next_truth_id(truth, level, t)
            _with_correction(el, correction)
            _annotate(el, fields)
            bucket.append(el)
        truth["last_added"] = el
    if correction:
        truth["corrections"] = sorted(set(truth.get("corrections") or []) | {correction})
    return truth


def remove_element(truth: dict, kind: str, level: str, fields: dict, *, source: str = SOURCE_USER,
                   correction: Optional[str] = None, date: Optional[str] = None, reading: Optional[dict] = None) -> dict:
    """``truth`` with an element negated: the element ``id`` names (``find_element``: a truth id, or the reader's id
    resolved to its place in ``reading``) or the one found within ``REMOVE_TOL_M`` of the given place is marked
    ``absent: true`` (its geometry kept, so a reading that has it is penalised); when the truth has none there, a new
    absent entry with a truth id is made from the fields. Returned in ``truth["last_removed"]``."""
    if kind not in KIND_TO_TYPE:
        raise ValueError(f"kind {kind!r}: one of {', '.join(KIND_TO_TYPE)}")
    t = KIND_TO_TYPE[kind]
    _ensure_level(truth, level, source=source)
    bucket = truth["per_level"].setdefault(level, {k: [] for k in ELEMENT_TYPES}).setdefault(t, [])
    target = None
    if fields.get("id"):
        target = find_element(truth, t, level, fields, reading)
    else:
        probe = element_from_fields(kind, fields, source=source, correction=correction, date=date)
        anchor = _anchor(t, probe)
        near = [(d, e) for e in positives(bucket)
                if _anchor(t, e) and (d := _dist(_anchor(t, e), anchor)) <= REMOVE_TOL_M[t]]
        target = min(near, key=lambda de: de[0])[1] if near else None
        if target is None:
            target = dict(probe, id=next_truth_id(truth, level, t))
            bucket.append(target)
    if target is None:
        raise ValueError(f"no {kind} {fields.get('id')} on {level} in the truth")
    target.update(absent=True, source=source, removed_on=date or today())
    _with_correction(target, correction)
    _annotate(target, fields)
    truth["last_removed"] = target
    if correction:
        truth["corrections"] = sorted(set(truth.get("corrections") or []) | {correction})
    return truth


def load_corrections(path: Path = CORRECTIONS_PATH) -> list[dict]:
    """The correction records (one JSON object per non-empty line)."""
    path = Path(path)
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


PLACEABLE_KINDS = ("wall", "door", "window", "opening", "room", "stair")    # an element with one place on a level
SOURCE_REVIEW = "user_review"                                              # a remark captured by `remark add`


def correction_applicable(rec: Optional[dict]) -> Optional[str]:
    """Why a correction record may not go into the truth, None when it may (pure). 5 Nov 2026 (review): the truth
    holds what the user said. A record goes in only when it is ``accepted`` (a machine proposal waits for the user)
    and carries the user's words (``user_words``); a remark of the user's review (``source: user_review``) is the
    user's words itself. A backfilled record without words states the session's own note, not the user's."""
    if rec is None:
        return "no such record in the correction store"
    if rec.get("status") != "accepted":
        return f"status {rec.get('status')!r}: waits for the user's confirmation"
    if rec.get("source") != SOURCE_REVIEW and not str(rec.get("user_words") or "").strip():
        return "no user words: the record states the session's own note, not the user's"
    return None


def correction_errors(records: list[dict], lesson_ids: Iterable[str], projects: Iterable[str]) -> list[str]:
    """What is wrong with the correction records (pure): a missing field, an unknown element kind, a lesson not in
    the lessons file (null needs a ``note``), a project not in ``projects/``, a place that is neither null nor
    ``{x, y}``, a repeated id.

    5 Nov 2026 (Milestone 14, user: "I want structure recognition to be cumulatively better with the feedbacks I am
    giving"): a correction joins the truth and the ranker's labels only through its place. 57 of the first 58 records
    had none, so nothing joined them to a gap, a wall or a room. Two rules keep the store placeable from now on:
    an accepted remark of the user's review (``source: user_review``, ``status: accepted``) about a placeable element
    (``PLACEABLE_KINDS``: wall, door, window, opening, room, stair) needs a ``place`` or an explicit ``place_note``
    (why it has none), so every future remark is placed at capture; and a record that says ``placeable: true`` needs
    the same, while ``placeable: false`` needs its ``why``. A record marked applied to the truth
    (``truth_applied.status: applied``) must be one ``correction_applicable`` allows: accepted, with the user's
    words."""
    lessons, known, seen, out = set(lesson_ids), set(projects), set(), []
    for rec in records:
        rid = rec.get("id")
        for f in CORRECTION_FIELDS:
            if f not in rec:
                out.append(f"{rid}: field {f} missing")
        if rid in seen:
            out.append(f"{rid}: repeated id")
        seen.add(rid)
        if rec.get("element_kind") not in ELEMENT_KINDS:
            out.append(f"{rid}: element_kind {rec.get('element_kind')!r}")
        if rec.get("lesson") is None:
            if not rec.get("note"):
                out.append(f"{rid}: lesson null without a note")
        elif rec["lesson"] not in lessons:
            out.append(f"{rid}: lesson {rec['lesson']} not in the lessons file")
        if rec.get("project") not in known:
            out.append(f"{rid}: project {rec.get('project')!r} not in projects/")
        place = rec.get("place")
        if place is not None and not (isinstance(place, dict) and set(place) >= {"x", "y"}
                                      and all(isinstance(place[k], (int, float)) for k in ("x", "y"))):
            out.append(f"{rid}: place {place!r} is neither null nor {{x, y}}")
        unplaced = place is None and not str(rec.get("place_note") or "").strip()
        if (unplaced and rec.get("element_kind") in PLACEABLE_KINDS and rec.get("source") == SOURCE_REVIEW
                and rec.get("status") == "accepted"):
            out.append(f"{rid}: a {rec['element_kind']} remark of the user's review needs a place or a place_note "
                       f"(why it has none)")
        elif unplaced and rec.get("placeable") is True:
            out.append(f"{rid}: placeable but neither a place nor a place_note")
        if rec.get("placeable") is False and not str(rec.get("why") or "").strip():
            out.append(f"{rid}: placeable false without a why")
        why = correction_applicable(rec)
        if (rec.get("truth_applied") or {}).get("status") == "applied" and why:
            out.append(f"{rid}: applied to the truth but {why}")
    return out


def main(args) -> int:
    if args.action == "build":
        projects = [p.strip() for p in (args.projects or "").split(",") if p.strip()] or default_projects()
        if not projects:
            print("reading truth: no accepted baseline (accepted_by_user: true) in results/reading_baseline/, no "
                  "synthetic project with a truth and no --projects")
            return 2
        import tempfile
        work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="reading_truth_"))
        done = build(projects, work, fresh=bool(getattr(args, "fresh", False)),
                     allow_drift=bool(getattr(args, "allow_drift", False)))
        return 0 if len(done) == len(projects) else 1
    if args.action in ("add", "remove"):
        if not args.project or not args.kind or not args.level:
            print("reading truth add/remove: --project, --level and --kind are needed")
            return 2
        if args.correction and (args.source or SOURCE_USER) == SOURCE_USER:
            rec = next((r for r in load_corrections() if r.get("id") == args.correction), None)
            why = correction_applicable(rec)
            if why:
                print(f"reading truth {args.action}: correction {args.correction} is not applied: {why}")
                return 2
        truth = load_truth(args.project) or new_truth(args.project)
        fields = {k: getattr(args, k, None) for k in ("id", "label", "room_type", "area", "polygon", "center",
                                                      "width", "wall_id", "start", "end", "thickness", "size",
                                                      "turn", "elevation", "order")}
        fn = add_element if args.action == "add" else remove_element
        reading_b = None
        if getattr(args, "reading", None):
            rp = Path(args.reading)
            rp = rp / "building.json" if rp.is_dir() else rp
            reading_b = json.loads(rp.read_text(encoding="utf-8"))
        try:
            truth = fn(truth, args.kind, args.level, fields, source=args.source or SOURCE_USER,
                       correction=args.correction, date=args.date, reading=reading_b)
        except (ValueError, KeyError) as exc:
            print(f"reading truth {args.action}: {exc}")
            return 2
        el = truth.pop("last_added", None) or truth.pop("last_removed", None)
        path = write_truth(args.project, truth)
        print(f"{args.project}: {args.kind} {el.get('id')} (reader id {el.get('reader_id') or '-'}) "
              f"{'negated (absent)' if args.action == 'remove' else 'added'}"
              f" on {args.level} ({el.get('source')}, correction {args.correction or '-'}) -> {path.relative_to(REPO)}")
        return 0
    print(f"reading truth: unknown action {args.action}")
    return 2
