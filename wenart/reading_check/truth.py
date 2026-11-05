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


# --- small pure helpers ---------------------------------------------------------------------------------------------

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


def merge(existing: Optional[dict], new: dict) -> dict:
    """``new`` with every protected element of ``existing`` kept (pure): elements and levels whose ``source`` is
    ``user_correction`` or ``synthetic`` (when the new truth is not synthetic), and every ``absent`` negation; a new
    element with a protected element's id gives way. The applied correction ids are kept too."""
    if not existing:
        return new
    out = json.loads(json.dumps(new))
    protect = tuple(s for s in PROTECTED_SOURCES if s != out.get("source"))
    kept = 0
    per = out.setdefault("per_level", {})
    for lid, lv in (existing.get("per_level") or {}).items():
        for t in ELEMENT_TYPES:
            prot = [e for e in lv.get(t) or [] if e.get("absent") or e.get("source") in protect]
            if not prot:
                continue
            target = per.setdefault(lid, {k: [] for k in ELEMENT_TYPES})
            ids = {e.get("id") for e in prot if e.get("id")}
            target[t] = [e for e in target.get(t) or [] if e.get("id") not in ids] + prot
            kept += len(prot)
        if lid not in {l["id"] for l in out.get("levels") or []}:
            src_level = next((l for l in existing.get("levels") or [] if l["id"] == lid), None)
            if src_level and (src_level.get("source") in protect or lid in per):
                out["levels"].append(src_level)
                per.setdefault(lid, {k: [] for k in ELEMENT_TYPES})
    corrections = sorted(set(existing.get("corrections") or []) | set(out.get("corrections") or []))
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


def add_element(truth: dict, kind: str, level: str, fields: dict, *, source: str = SOURCE_USER,
                correction: Optional[str] = None, date: Optional[str] = None) -> dict:
    """``truth`` with an element (or, ``kind == "level"``, a level) added by the user (pure in the sense that it
    returns the changed dict it was given); the element is returned in ``truth["last_added"]``."""
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
        el = element_from_fields(kind, fields, source=source, correction=correction, date=date)
        if not el.get("id"):
            el["id"] = f"uc_{level}_{kind}_{sum(1 for e in bucket if e.get('source') == SOURCE_USER) + 1:03d}"
        bucket[:] = [e for e in bucket if e.get("id") != el["id"]] + [el]
        truth["last_added"] = el
    if correction:
        truth["corrections"] = sorted(set(truth.get("corrections") or []) | {correction})
    return truth


def remove_element(truth: dict, kind: str, level: str, fields: dict, *, source: str = SOURCE_USER,
                   correction: Optional[str] = None, date: Optional[str] = None) -> dict:
    """``truth`` with an element negated: the element named by ``id`` or found within ``REMOVE_TOL_M`` of the given
    place is marked ``absent: true`` (its geometry kept, so a reading that has it is penalised); when the truth has
    none there, a new absent entry is made from the fields. Returned in ``truth["last_removed"]``."""
    if kind not in KIND_TO_TYPE:
        raise ValueError(f"kind {kind!r}: one of {', '.join(KIND_TO_TYPE)}")
    t = KIND_TO_TYPE[kind]
    _ensure_level(truth, level, source=source)
    bucket = truth["per_level"].setdefault(level, {k: [] for k in ELEMENT_TYPES}).setdefault(t, [])
    target = None
    if fields.get("id"):
        target = next((e for e in bucket if e.get("id") == fields["id"]), None)
    else:
        probe = element_from_fields(kind, fields, source=source, correction=correction, date=date)
        anchor = _anchor(t, probe)
        near = [(d, e) for e in positives(bucket)
                if _anchor(t, e) and (d := _dist(_anchor(t, e), anchor)) <= REMOVE_TOL_M[t]]
        target = min(near, key=lambda de: de[0])[1] if near else None
        if target is None:
            prefix = f"uc_{level}_{kind}_absent_"
            n = sum(1 for e in bucket if str(e.get("id") or "").startswith(prefix)) + 1
            target = dict(probe, id=probe.get("id") or f"{prefix}{n:03d}")
            bucket.append(target)
    if target is None:
        raise ValueError(f"no {kind} {fields.get('id')} on {level} in the truth")
    target.update(absent=True, source=source, correction=correction, removed_on=date or today())
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


def correction_errors(records: list[dict], lesson_ids: Iterable[str], projects: Iterable[str]) -> list[str]:
    """What is wrong with the correction records (pure): a missing field, an unknown element kind, a lesson not in
    the lessons file (null needs a ``note``), a project not in ``projects/``, a place that is neither null nor
    ``{x, y}``, a repeated id."""
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
        truth = load_truth(args.project) or new_truth(args.project)
        fields = {k: getattr(args, k, None) for k in ("id", "label", "room_type", "area", "polygon", "center",
                                                      "width", "wall_id", "start", "end", "thickness", "size",
                                                      "turn", "elevation", "order")}
        fn = add_element if args.action == "add" else remove_element
        try:
            truth = fn(truth, args.kind, args.level, fields, source=args.source or SOURCE_USER,
                       correction=args.correction, date=args.date)
        except (ValueError, KeyError) as exc:
            print(f"reading truth {args.action}: {exc}")
            return 2
        el = truth.pop("last_added", None) or truth.pop("last_removed", None)
        path = write_truth(args.project, truth)
        print(f"{args.project}: {args.kind} {el.get('id')} {'negated (absent)' if args.action == 'remove' else 'added'}"
              f" on {args.level} ({el.get('source')}, correction {args.correction or '-'}) -> {path.relative_to(REPO)}")
        return 0
    print(f"reading truth: unknown action {args.action}")
    return 2
