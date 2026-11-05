"""The reading truth corpus and the correction store (4 Nov 2026, Milestone 14 track R1; user: "I want structure
recognition to be cumulatively better with the feedbacks I am giving").

What: ``results/reading_truth/<project>.json`` holds, per project the user accepted, the elements of its accepted
reading in building metres: the levels (id, label, elevation, order) and, per level, the rooms (label, type, area,
centroid, polygon), the doors, the windows, the other openings (width, centre, wall), the walls (centre line,
thickness) and the stairs (the drawn stair pieces: centre, size, turn, flights). Every element carries
``source: "accepted_reading"`` and the confidence of its primary evidence. ``status`` is ``accepted`` when the
baseline's reading check was ``ready``, else ``partial`` (the user accepted the levels that were read). The levels the
baseline lists as left out stay out.

``python -m wenart.reading_check truth build [--projects a,b] [--work DIR] [--fresh]`` reads every accepted project of
``results/reading_baseline/`` with the CPU pipeline (``regress.read_project``; a reading already in ``--work`` is used
again unless ``--fresh``) and writes the truth files. ``extract(building, ...)`` is the pure part: a building dict in,
the truth dict out; ``wenart.reading_check.score`` runs it on the new reading too and matches the two.

``results/reading_corrections.jsonl`` holds one record per correction of the user (``load_corrections``): project,
level, place (building metres, or null when the text gives none), element kind, the reader's answer, the right answer,
the user's words, the lesson id, the date, the source (``backfill_progress`` for the 3 and 4 Nov 2026 reviews, lessons
UL274 to UL328) and the status (the user's own words count as accepted).

Why: a correction of the user used to become one hand-written rule, and nothing measured whether the rule helped or
hurt the other projects. With the truth of every accepted reading the score (``score.py``) says per commit how far
each reading is from the truth; with the correction store each correction is a labelled example the ranker (R3) and
the reviewers (R4 to R6) learn from, instead of a line in a review table.

How: pure functions over the building dict (no AI, no pod); the fields come from ``building.json`` as the pipeline
writes it (rooms: ``polygon``, ``label``, ``room_type``, ``area_computed``; openings: ``type``, ``center``, ``width``,
``wall_id``; walls: ``start``, ``end``, ``thickness``; stairs: the furniture pieces of ``type == "stair"`` with their
``stair`` rule result). Labels are folded with ``wenart.textfold.fold_ascii`` (Turkish letters, letter-spaced words).
"""
from __future__ import annotations

import datetime as _dt
import json
import subprocess
from pathlib import Path
from typing import Iterable, Optional

from wenart.textfold import fold_ascii

REPO = Path(__file__).resolve().parents[2]
TRUTH_DIR = REPO / "results" / "reading_truth"
BASELINE_DIR = REPO / "results" / "reading_baseline"
CORRECTIONS_PATH = REPO / "results" / "reading_corrections.jsonl"
SOURCE_ACCEPTED = "accepted_reading"
ELEMENT_TYPES = ("rooms", "doors", "windows", "openings", "walls", "stairs")
ELEMENT_KINDS = ("wall", "opening", "door", "window", "room", "stair", "level", "label", "region", "roof", "site",
                 "other")
CORRECTION_FIELDS = ("id", "date", "project", "level", "place", "element_kind", "reader_answer", "right_answer",
                     "user_words", "lesson", "source", "status")
ROUND = 3                                   # millimetres: enough for the matching tolerances, keeps the files small


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


def confidence_of(element: dict) -> Optional[float]:
    """The confidence of an element's primary evidence (the first evidence entry that carries one), else None."""
    for ev in element.get("evidence") or []:
        if isinstance(ev, dict) and ev.get("confidence") is not None:
            try:
                return round(float(ev["confidence"]), 3)
            except (TypeError, ValueError):
                return None
    return None


def git_head(repo: Path = REPO) -> Optional[str]:
    """The commit the reading was made at (``git rev-parse HEAD``), None outside a repository."""
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(repo), capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() or None if out.returncode == 0 else None


# --- the truth of one building --------------------------------------------------------------------------------------

def _room(r: dict) -> dict:
    area = r.get("area_computed")
    return {"id": r.get("id"), "label": r.get("label"), "room_type": r.get("room_type"),
            "area": round(float(area), ROUND) if area is not None else None,
            "centroid": centroid(r.get("polygon") or []), "polygon": _poly(r.get("polygon")),
            "source": SOURCE_ACCEPTED, "confidence": confidence_of(r)}


def _opening(o: dict) -> dict:
    out = {"id": o.get("id"), "type": o.get("type"), "width": round(float(o["width"]), ROUND) if o.get("width")
           is not None else None, "center": _pt(o["center"]) if o.get("center") else None, "wall_id": o.get("wall_id"),
           "source": SOURCE_ACCEPTED, "confidence": confidence_of(o)}
    if o.get("virtual"):
        out["virtual"] = True
    return out


def _wall(w: dict) -> dict:
    return {"id": w.get("id"), "start": _pt(w["start"]), "end": _pt(w["end"]),
            "thickness": round(float(w["thickness"]), ROUND) if w.get("thickness") is not None else None,
            "status": w.get("status"), "source": SOURCE_ACCEPTED, "confidence": confidence_of(w)}


def _stair(f: dict) -> dict:
    fp = f.get("footprint") or {}
    st = f.get("stair") or {}
    flights = [{"start": _pt(fl["start"]), "end": _pt(fl["end"]), "width": fl.get("width"), "lines": fl.get("lines")}
               for fl in (st.get("flights") or []) if fl.get("start") and fl.get("end")]
    return {"id": f.get("id"), "center": _pt(fp["center"]) if fp.get("center") else None,
            "size": [round(float(s), ROUND) for s in fp["size"]] if fp.get("size") else None,
            "rotation_deg": fp.get("rotation_deg"), "room_id": f.get("room_id"), "turn": st.get("turn"),
            "flights": flights, "source": SOURCE_ACCEPTED, "confidence": confidence_of(f)}


def stairs_of(building: dict) -> list:
    """The drawn stair pieces of a building: the furniture of ``type == "stair"`` (where the pipeline records them)."""
    return [f for f in building.get("furniture") or [] if f.get("type") == "stair"]


def extract(building: dict, *, project: Optional[str] = None, status: str = "accepted", commit: Optional[str] = None,
            date: Optional[str] = None, leave_out: Iterable[str] = ()) -> dict:
    """The truth dict of a building dict (pure). ``leave_out`` names the levels (by label) that stay out, as the
    baseline's ``levels_left_out`` lists them."""
    skip = {norm_label(lbl) for lbl in leave_out}
    levels = [lv for lv in building.get("levels") or [] if norm_label(lv.get("label")) not in skip]
    ids = [lv["id"] for lv in levels]
    per = {lid: {t: [] for t in ELEMENT_TYPES} for lid in ids}
    for r in building.get("rooms") or []:
        if r.get("level_id") in per:
            per[r["level_id"]]["rooms"].append(_room(r))
    for o in building.get("openings") or []:
        if o.get("level_id") not in per:
            continue
        kind = {"door": "doors", "window": "windows"}.get(o.get("type"), "openings")
        per[o["level_id"]][kind].append(_opening(o))
    for w in building.get("walls") or []:
        if w.get("level_id") in per and w.get("start") and w.get("end"):
            per[w["level_id"]]["walls"].append(_wall(w))
    for f in stairs_of(building):
        if f.get("level_id") in per:
            per[f["level_id"]]["stairs"].append(_stair(f))
    return {"project": project or (building.get("project") or {}).get("id"), "source": SOURCE_ACCEPTED,
            "status": status, "commit": commit, "date": date or _dt.date.today().isoformat(),
            "levels": [{"id": lv["id"], "label": lv.get("label"), "elevation": lv.get("elevation"),
                        "order": lv.get("order")} for lv in levels],
            "levels_left_out": sorted(leave_out), "per_level": per}


def counts(truth: dict) -> dict:
    """``{"levels": n, "rooms": n, ...}`` of a truth dict (the report's table)."""
    out = {"levels": len(truth.get("levels") or [])}
    for t in ELEMENT_TYPES:
        out[t] = sum(len(lv.get(t) or []) for lv in (truth.get("per_level") or {}).values())
    return out


# --- files ----------------------------------------------------------------------------------------------------------

def accepted_projects(baseline_dir: Path = BASELINE_DIR) -> list[str]:
    """The projects whose baseline reading has ``status: ok`` (the user accepted the reading)."""
    out = []
    for path in sorted(baseline_dir.glob("*.json")):
        try:
            if json.loads(path.read_text(encoding="utf-8")).get("status") == "ok":
                out.append(path.stem)
        except (OSError, ValueError):
            continue
    return out


def baseline_status(baseline: Optional[dict]) -> str:
    """``accepted`` when the baseline's reading check was ready, else ``partial``."""
    return "accepted" if ((baseline or {}).get("check") or {}).get("verdict") == "ready" else "partial"


def load_truth(project: str, truth_dir: Path = TRUTH_DIR) -> Optional[dict]:
    path = Path(truth_dir) / f"{project}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def truth_projects(truth_dir: Path = TRUTH_DIR) -> list[str]:
    return sorted(p.stem for p in Path(truth_dir).glob("*.json"))


def reading(project: str, work: Path, fresh: bool = False) -> Path:
    """``work/<project>`` with its ``building.json``: the reading already there, or a new CPU reading."""
    out = Path(work) / project
    if fresh or not (out / "building.json").is_file():
        from wenart.reading_check import regress as RG
        out = RG.read_project(project, Path(work))
    return out


def build(projects: list[str], work: Path, *, fresh: bool = False, truth_dir: Path = TRUTH_DIR,
          baseline_dir: Path = BASELINE_DIR) -> dict:
    """Read the projects and write their truth files; returns ``{project: truth}`` (a failed reading is reported,
    the others are still written)."""
    out = {}
    commit = git_head()
    for p in projects:
        path = Path(baseline_dir) / f"{p}.json"
        base = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
        try:
            folder = reading(p, work, fresh)
            b = json.loads((folder / "building.json").read_text(encoding="utf-8"))
        except Exception as exc:                                 # a failed reading must not stop the other projects
            print(f"{p}: reading failed: {exc}")
            continue
        truth = extract(b, project=p, status=baseline_status(base), commit=commit,
                        leave_out=(base or {}).get("levels_left_out") or [])
        Path(truth_dir).mkdir(parents=True, exist_ok=True)
        (Path(truth_dir) / f"{p}.json").write_text(json.dumps(truth, ensure_ascii=False, indent=1) + "\n",
                                                   encoding="utf-8")
        c = counts(truth)
        print(f"{p}: truth written ({truth['status']}; " + ", ".join(f"{k} {v}" for k, v in c.items()) + ")")
        out[p] = truth
    return out


def load_corrections(path: Path = CORRECTIONS_PATH) -> list[dict]:
    """The correction records (one JSON object per non-empty line)."""
    path = Path(path)
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def correction_errors(records: list[dict], lesson_ids: Iterable[str], projects: Iterable[str]) -> list[str]:
    """What is wrong with the correction records (pure): a missing field, an unknown element kind, a lesson not in
    the lessons file, a project not in ``projects/``, a place that is neither null nor ``{x, y}``, a repeated id."""
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
        if rec.get("lesson") is not None and rec["lesson"] not in lessons:
            out.append(f"{rid}: lesson {rec['lesson']} not in the lessons file")
        if rec.get("project") not in known:
            out.append(f"{rid}: project {rec.get('project')!r} not in projects/")
        place = rec.get("place")
        if place is not None and not (isinstance(place, dict) and set(place) >= {"x", "y"}
                                      and all(isinstance(place[k], (int, float)) for k in ("x", "y"))):
            out.append(f"{rid}: place {place!r} is neither null nor {{x, y}}")
    return out


def main(args) -> int:
    if args.action != "build":
        print(f"reading truth: unknown action {args.action}")
        return 2
    projects = [p.strip() for p in (args.projects or "").split(",") if p.strip()] or accepted_projects()
    if not projects:
        print("reading truth: no accepted baseline in results/reading_baseline/ and no --projects")
        return 2
    import tempfile
    work = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="reading_truth_"))
    done = build(projects, work, fresh=bool(getattr(args, "fresh", False)))
    return 0 if len(done) == len(projects) else 1
