"""The reading truth: the accepted reading plus a replay of the user's corrections (Milestone 14 track R1; user, 4 Nov
2026: "I want structure recognition to be cumulatively better with the feedbacks I am giving"; derived truth of 6 Nov
2026, decided by the session organizer after four rounds of review).

What: ``results/reading_truth/<project>.json`` holds, per project, the elements the truth knows in building metres:
the levels (id, label, elevation, order) and, per level, the rooms (label, type, area, centroid, polygon), the doors,
the windows, the other openings (width, centre, wall), the walls (centre line, thickness) and the stairs (centre,
size, turn, flights). Every element carries its ``source`` (``accepted_reading``, ``synthetic`` or
``user_correction``), its confidence and method where the reading gave them, and the flags that mark a code-added
element (``inferred``, ``lift_door``, ``parapet``, ``virtual``; ``label_source`` on a level), so the ranker can weight
them. A negated element is an entry with ``absent: true``: a reading that has it there is penalised (``score.py``).

The truth is DERIVED, never merged and never edited by hand::

    truth(project) = the accepted reading's elements + a replay of the project's applicable correction records,
                     in record order, each applied by place

- The accepted reading is stored: ``results/reading_accepted/<project>.json`` (``truth accept``) is the reading the
  user accepted, in the truth's shape (``extract``), with the reader's ids, the commit it was read at, the
  acceptance and the drift check (``truth_of``). It is stored rather than read again at its commit, so a build is
  pure (no reading, no LibreDWG, seconds) and byte-identical from the same inputs; ``truth accept`` replaces it only
  after the user accepted a new reading (``accepted_by_user: true`` in the baseline). A synthetic project's accepted
  reading is its exact truth (``projects/<p>/truth/``).
- The correction store ``results/reading_corrections.jsonl`` is the memory. A record is replayed when
  ``correction_applicable`` allows it (accepted, the user's own words, not held, not placed below
  ``PLACE_CONFIDENCE_MIN`` by the machine) and it carries a ``truth_action``: one element operation, or several under
  ``elements``, each naming its ``level``, ``kind`` and place (``center``; a room's ``polygon``; a wall's ``start``
  and ``end``). Records name places; ``reader_ids`` are hints of the reading the record was located on, and nothing
  joins on an id.
- ``build_truth`` (pure): the accepted entries first, numbered in a deterministic order (``t_<level>_<kind>_<nnnn>``
  by level, kind, then x and y rounded to 1 cm), then the operations in record order, by place with the score's
  tolerances (``score.OPENING_CENTER_M``, ``STAIR_CENTER_M``, the room rule, the wall rules):

  - ``add`` (door, window, opening, stair): the element of the class (door, window and opening are one class) nearest
    the place, within the tolerance, is replaced: the user's type, width, place (a stair's size and turn) win; with
    none there, or with a negation nearer than every element (the record removed the element at its place first: a
    retype), the element is added (``u_<record>_<n>``). A room: the room at the place (the score's room rule; a room
    given by its centre alone: the room holding the centre) takes the user's label and type and keeps its drawn
    polygon; else a room with a polygon is added. A wall: the wall at the place (the score's wall rule) is confirmed
    as drawn; else the wall is added. An add drops a negation of its own kind at its place (the newer record wins).
  - ``confirm``: the element of the record's kind at the place keeps its geometry and becomes ``user_correction``;
    with none there the operation is listed ``unmatched`` in the build report, and nothing is invented.
  - ``retype`` (a room, an opening): the element at the place changes its type (label) and keeps its geometry.
  - ``remove``: the element of the record's kind nearest the place (and its double reads within ``DUPLICATE_M``) is
    removed and an absent entry is written at the record's place, so a reading that builds it again counts as an
    absent hit. A wall span (start, end) cuts the walls on its line: the pieces outside the span stay, the part inside
    is removed (a piece shorter than its own thickness is a joint and goes too), and an absent span is written. A long
    wall is never removed whole for a short span.
  - several records on one element compose in record order; the element's ``corrections`` lists them all.
  - an operation on a level the truth lacks (left out, not accepted) is ``unmatched``: no level comes back through a
    correction; a room given by its centre with no room there is ``unmatched`` (it could never match a reading).

  The result is a snapshot: ``built_from`` names the accepted reading, its commit and the replayed record ids;
  ``build_report`` lists every operation's result (``applied``), the ``unmatched`` ones with the reason, and the
  project's records that were not replayed with the reason (``not_replayed``).
- ``truth add`` / ``truth remove`` append a record (with the user's words, ``--text``) or add the operation to the
  record named by ``--correction`` (accepted, the user's words, the same project), then rebuild; they never edit the
  truth file. A place on an existing element means replace or confirm, never a duplicate. A reader's id needs the
  reading it was taken from (``--reading``) and becomes that element's place; a truth id (informational) names the
  place of that element in the current truth file.

Ids are informational only: the score, the ranker's labels and the remark crops all work by place.

Why: four rounds of merging a new reading into a stored truth (by id, then by place) still undid or blurred user
corrections in 18 verified cases (a negated span read again took the long wall's id, a user element missing from a
reading took its neighbour, a double read at a negation became a new positive, ...). A truth derived from fixed inputs
cannot drift: the accepted reading does not change when the reader does, and the replay decides on the accepted
reading, never on a later one.

How: pure functions over the dicts (no AI, no pod); the fields come from ``building.json`` as the pipeline writes it
(rooms: ``polygon``, ``label``, ``room_type``, ``area_computed``; openings: ``type``, ``center``, ``width``,
``wall_id``; walls: ``start``, ``end``, ``thickness``; stairs: the furniture pieces of ``type == "stair"`` with their
``stair`` rule result). Labels are folded with ``wenart.textfold.fold_ascii``.

``python -m wenart.reading_check truth accept --projects p [--work DIR] [--fresh] [--allow-drift]`` stores the
accepted reading (the user's acceptance in the baseline and the drift check are required); ``truth build
[--projects a,b]`` derives and writes the truths; ``truth add|remove --project p --level L --kind door --center x,y
[--width w] (--correction C0012 | --text "the user's words")`` records a correction and rebuilds.
"""
from __future__ import annotations

import copy
import datetime as _dt
import json
import math
import subprocess
from pathlib import Path
from typing import Iterable, Optional

from wenart.textfold import fold_ascii

REPO = Path(__file__).resolve().parents[2]
TRUTH_DIR = REPO / "results" / "reading_truth"
ACCEPTED_DIR = REPO / "results" / "reading_accepted"
BASELINE_DIR = REPO / "results" / "reading_baseline"
PROJECTS_DIR = REPO / "projects"
CORRECTIONS_PATH = REPO / "results" / "reading_corrections.jsonl"
SOURCE_ACCEPTED = "accepted_reading"
SOURCE_SYNTHETIC = "synthetic"
SOURCE_USER = "user_correction"
ELEMENT_TYPES = ("rooms", "doors", "windows", "openings", "walls", "stairs")
KIND_TO_TYPE = {"room": "rooms", "door": "doors", "window": "windows", "opening": "openings", "wall": "walls",
                "stair": "stairs"}
TYPE_KIND = {t: k for k, t in KIND_TO_TYPE.items()}
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
TRUTH_ID_PREFIX = "t_"                      # an accepted entry's id (informational: nothing joins on it)
USER_ID_PREFIX = "u_"                       # an entry a record made: u_<record id>_<n>
OPENING_TYPES = ("doors", "windows", "openings")
OPS = ("add", "remove", "confirm", "retype")
DUPLICATE_M = 0.01           # a second element of one kind this close to a removed one is the same element read twice
ROOM_DUPLICATE_IOU = 0.95    # ... a second room this alike
NEAR_EPS_M = 0.01            # a negation must be this much nearer than every element to mark the place as negated
WALL_ANGLE_DEG = 2.0         # a negated wall span cuts walls this parallel to it ...
WALL_PIECE_MIN_M = 0.10      # ... and a piece left shorter than this (or than its own thickness) is a joint
PLACE_CONFIDENCE_MIN = 0.6   # a record the machine located with less confidence waits for the user


# --- small pure helpers ---------------------------------------------------------------------------------------------

def is_truth_id(value) -> bool:
    """True for an id the truth gave (an accepted entry ``t_...`` or an entry of a record ``u_...``)."""
    return isinstance(value, str) and (value.startswith(TRUTH_ID_PREFIX) or value.startswith(USER_ID_PREFIX))


def same_place_pairs(t: str, a: list, b: list) -> list:
    """The ``(i, j)`` pairs of elements of ``a`` and ``b`` (one level, one type) that are the same element by place:
    the score's own rules (``score.match_kind``), one to one."""
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


# --- the truth shape of one building --------------------------------------------------------------------------------

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
    """The truth-shaped dict of a building dict (pure; the reader's ids stay as ``id``). ``leave_out`` names the
    levels (by label) that stay out, as the baseline's ``levels_left_out`` lists them; ``source`` is stamped on every
    element."""
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
    """The accepted reading of a project in the truth's shape (pure): ``(accepted, messages)``. None without the
    user's acceptance in the baseline; ``status: "drifted"`` with ``drift`` when the reading's numbers differ from the
    accepted ones; the levels limited to the accepted ones (a partial acceptance) and without the baseline's
    ``levels_left_out``. ``truth accept`` stores it; ``build_truth`` derives the truth from it."""
    acc = acceptance(baseline)
    if acc is None:
        return None, [f"{project}: not accepted by the user: the baseline has no accepted_by_user: true "
                      f"(after the user accepts: regress --update, set the acceptance fields, then truth accept)"]
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


# --- geometry of the replay -----------------------------------------------------------------------------------------

def _parse_xy(text) -> Optional[list]:
    if text is None or text == "":
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


def _inside(pt, polygon) -> bool:
    """True when the point lies inside the polygon (even-odd rule)."""
    x, y = float(pt[0]), float(pt[1])
    inside = False
    pts = polygon or []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / ((y1 - y0) or 1e-12) + x0:
            inside = not inside
    return inside


def _cut(wall: dict, start, end) -> Optional[list]:
    """The pieces ``[(start, end)]`` of ``wall`` left outside the span ``start``-``end`` (pure), None when the span is
    not on the wall's line (parallel within ``WALL_ANGLE_DEG``, both span ends within ``score.WALL_LATERAL_M`` of the
    line) or does not overlap it. A piece shorter than ``WALL_PIECE_MIN_M`` or than the wall's thickness is a joint
    and is dropped."""
    from wenart.reading_check import score as SC

    ws, we = wall.get("start"), wall.get("end")
    lw, ls = _dist(ws, we), _dist(start, end)
    if lw < 1e-6 or ls < 1e-6:
        return None
    ux, uy = (float(we[0]) - float(ws[0])) / lw, (float(we[1]) - float(ws[1])) / lw
    vx, vy = (float(end[0]) - float(start[0])) / ls, (float(end[1]) - float(start[1])) / ls
    if abs(ux * vy - uy * vx) > math.sin(math.radians(WALL_ANGLE_DEG)):
        return None
    along = []
    for q in (start, end):
        dx, dy = float(q[0]) - float(ws[0]), float(q[1]) - float(ws[1])
        if abs(dx * uy - dy * ux) > SC.WALL_LATERAL_M:
            return None
        along.append(dx * ux + dy * uy)
    lo, hi = max(0.0, min(along)), min(lw, max(along))
    if hi - lo <= 1e-6:
        return None
    least = max(WALL_PIECE_MIN_M, float(wall.get("thickness") or 0.0))
    pieces = [(a, b) for a, b in ((0.0, lo), (hi, lw)) if b - a >= least - 1e-9]
    return [(_pt((float(ws[0]) + ux * a, float(ws[1]) + uy * a)), _pt((float(ws[0]) + ux * b, float(ws[1]) + uy * b)))
            for a, b in pieces]


def _sort_key(t: str, e: dict) -> tuple:
    """The deterministic order of a level's elements of one type: x and y of the anchor rounded to 1 cm, then the
    element itself (its canonical JSON)."""
    a = _anchor(t, e)
    head = (0, round(float(a[0]), 2), round(float(a[1]), 2)) if a else (1, 0.0, 0.0)
    return head + (json.dumps(e, sort_keys=True, ensure_ascii=False),)


# --- the accepted entries and the replay ----------------------------------------------------------------------------

def accepted_entries(accepted: dict) -> dict:
    """The truth's skeleton from an accepted reading (pure): every element keeps its fields, the reader's id becomes
    ``reader_id`` (a hint) and the element gets a truth id from the deterministic order (``_sort_key``):
    ``t_<level>_<kind>_<nnnn>``. The stored reading's own notes (``note``, ``removed``) stay out."""
    out = {k: copy.deepcopy(v) for k, v in accepted.items() if k not in ("per_level", "note", "removed")}
    out["per_level"] = {}
    for lid, lv in (accepted.get("per_level") or {}).items():
        out["per_level"][lid] = {}
        for t in ELEMENT_TYPES:
            els = sorted((copy.deepcopy(e) for e in lv.get(t) or []), key=lambda e: _sort_key(t, e))
            for n, e in enumerate(els, 1):
                rid = e.get("reader_id") or e.get("id")
                e["id"] = f"{TRUTH_ID_PREFIX}{lid}_{TYPE_KIND[t]}_{n:04d}"
                if rid is not None and not is_truth_id(rid):
                    e["reader_id"] = rid
            out["per_level"][lid][t] = els
    return out


def element_from_fields(kind: str, fields: dict, *, source: str, correction: Optional[str],
                        date: Optional[str] = None) -> dict:
    """A truth element of ``kind`` (``KIND_TO_TYPE`` key) from an operation's fields (pure): ``id``, ``label``,
    ``room_type``, ``area``, ``polygon`` (``x,y;x,y;...`` or a list), ``center`` (``x,y``), ``width``, ``wall_id``,
    ``start``, ``end``, ``thickness``, ``size`` (``w,d``), ``turn``. Raises ValueError when the place is missing."""
    t = KIND_TO_TYPE[kind]
    el: dict = {"id": fields.get("id")}
    if t == "rooms":
        poly = _parse_poly(fields.get("polygon"))
        el.update(label=fields.get("label"), room_type=fields.get("room_type"),
                  area=round(float(fields["area"]), ROUND) if fields.get("area") is not None else None,
                  centroid=_parse_xy(fields.get("center")) or centroid(poly), polygon=poly)
        if not el["centroid"]:
            raise ValueError("a room needs --polygon or --center")
    elif t == "walls":
        s, e = _parse_xy(fields.get("start")), _parse_xy(fields.get("end"))
        if not s or not e:
            raise ValueError("a wall needs --start and --end")
        el.update(start=s, end=e, thickness=round(float(fields["thickness"]), ROUND)
                  if fields.get("thickness") is not None else None)
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
        el.update(type=kind, width=round(float(fields["width"]), ROUND) if fields.get("width") is not None else None,
                  center=c, wall_id=fields.get("wall_id"))
    el.update(source=source, confidence=None, method="user", correction=correction, added_on=date or today())
    return el


def record_ops(rec: dict) -> list[dict]:
    """The element operations of a record's ``truth_action`` (pure): the ``elements`` list, or the action itself;
    each with its level (the record's when it names none) and kind (the record's element kind when it names none)."""
    act = rec.get("truth_action")
    if not isinstance(act, dict):
        return []
    els = act["elements"] if isinstance(act.get("elements"), list) else [act]
    out = []
    for el in els:
        if not isinstance(el, dict):
            continue
        op = dict(el)
        if op.get("level") is None:
            op["level"] = rec.get("level")
        if op.get("kind") is None:
            op["kind"] = rec.get("element_kind")
        out.append(op)
    return out


def _record_key(rid) -> tuple:
    s = str(rid or "")
    return (len(s), s)


class _Replay:
    """The replay of one record's operations on a truth (in place); ``report`` collects one entry per operation."""

    def __init__(self, truth: dict):
        self.truth = truth
        self.count: dict = {}

    # -- the element bookkeeping
    def _new_id(self, rid: str) -> str:
        self.count[rid] = self.count.get(rid, 0) + 1
        return f"{USER_ID_PREFIX}{rid}_{self.count[rid]}"

    def _touch(self, el: dict, rec: dict, op: dict, changed=(), when: str = "confirmed_on") -> dict:
        rid = rec["id"]
        ids = list(el.get("corrections") or [])
        if rid not in ids:
            ids.append(rid)
        el["corrections"] = ids
        el["correction"] = rid
        el["source"] = SOURCE_USER
        if changed:
            el["changed"] = sorted(set(el.get("changed") or []) | set(changed))
            el["method"] = "user"
            el["confidence"] = None
        if op.get("note"):
            el["note"] = str(op["note"])
        if op.get("evidence"):
            el["evidence"] = list(op["evidence"])
        el[when] = rec.get("date")
        return el

    def _new(self, rec: dict, op: dict, kind: str, absent: bool = False, base: Optional[dict] = None) -> dict:
        if base is not None:                          # a negated element keeps what the reading said of it
            el = copy.deepcopy(base)
        else:
            el = element_from_fields(kind, op, source=SOURCE_USER, correction=rec["id"], date=rec.get("date"))
        hint = op.get("id")
        el["id"] = self._new_id(rec["id"])
        if hint and not is_truth_id(hint):
            el["reader_id"] = hint
        elif base is None:
            el.pop("reader_id", None)
        if absent:
            el["absent"] = True
            el.pop("added_on", None)
            return self._touch(el, rec, op, when="removed_on")
        return self._touch(el, rec, op, when="added_on")

    # -- one operation
    def apply(self, rec: dict, op: dict) -> dict:
        what, kind, lid = op.get("op"), op.get("kind"), op.get("level")
        entry = {"record": rec["id"], "op": what, "kind": kind, "level": lid}
        place = op.get("center") or op.get("start") or (centroid(op.get("polygon")) if op.get("polygon") else None)
        if place is not None:
            try:
                entry["place"] = _parse_xy(place)
            except (TypeError, ValueError):
                entry["place"] = None

        def unmatched(why):
            return dict(entry, state="unmatched", why=why)

        if what not in OPS:
            return unmatched(f"operation {what!r}: one of {', '.join(OPS)}")
        if kind == "level":
            return self._level(rec, op, entry, unmatched)
        if kind not in KIND_TO_TYPE:
            return unmatched(f"kind {kind!r} is no element type of the truth")
        lv = (self.truth.get("per_level") or {}).get(lid)
        if lv is None:
            return unmatched(f"level {lid!r} is not in the truth (left out, not accepted, or unknown): no level comes "
                             f"back through a correction")
        for t in ELEMENT_TYPES:
            lv.setdefault(t, [])
        t = KIND_TO_TYPE[kind]
        try:
            if t in OPENING_TYPES or t == "stairs":
                return self._point(rec, op, entry, unmatched, lv, kind, t)
            if t == "rooms":
                return self._room(rec, op, entry, unmatched, lv, kind)
            return self._wall(rec, op, entry, unmatched, lv, kind)
        except (TypeError, ValueError) as exc:
            return unmatched(f"the operation's place cannot be read: {exc}")

    def _level(self, rec, op, entry, unmatched):
        if op.get("op") != "add":
            return unmatched("a level can only be added (a level the user negates is no element of the truth)")
        lid = op.get("level")
        levels = self.truth.setdefault("levels", [])
        lv = next((x for x in levels if x["id"] == lid), None)
        if lv is None:
            lv = {"id": lid, "label": op.get("label"),
                  "elevation": float(op["elevation"]) if op.get("elevation") is not None else None,
                  "order": int(op["order"]) if op.get("order") is not None else None, "source": SOURCE_USER}
            levels.append(lv)
            self.truth.setdefault("per_level", {})[lid] = {t: [] for t in ELEMENT_TYPES}
            state = "added"
        else:
            state = "confirmed"
            for k in ("label", "elevation", "order"):
                if op.get(k) is not None and lv.get(k) != op[k]:
                    lv[k] = op[k]
                    state = "changed"
            lv["source"] = SOURCE_USER
        ids = list(lv.get("corrections") or [])
        if rec["id"] not in ids:
            ids.append(rec["id"])
        lv["corrections"], lv["correction"] = ids, rec["id"]
        return dict(entry, state=state, ids=[lid])

    @staticmethod
    def _near(lv, lists, center, tol, absent=False) -> list:
        out = []
        for t in lists:
            for e in lv.get(t) or []:
                if bool(e.get("absent")) != absent or not e.get("center"):
                    continue
                d = _dist(e["center"], center)
                if d <= tol + 1e-9:
                    out.append((d, t, e))
        return sorted(out, key=lambda x: (round(x[0], 6), x[1], str(x[2].get("id"))))

    def _point(self, rec, op, entry, unmatched, lv, kind, t):
        from wenart.reading_check import score as SC

        what = op["op"]
        center = _parse_xy(op.get("center"))
        if not center:
            return unmatched(f"a {kind} needs its centre")
        tol = SC.STAIR_CENTER_M if t == "stairs" else SC.OPENING_CENTER_M
        klass = ("stairs",) if t == "stairs" else OPENING_TYPES
        if what == "remove":
            near = self._near(lv, (t,), center, tol)
            removed = []
            if near:
                first = near[0][2]
                for _d, _t, e in near:
                    if e is first or _dist(e["center"], first["center"]) <= DUPLICATE_M:
                        lv[t].remove(e)
                        removed.append(e)
            old = self._near(lv, (t,), center, tol, absent=True)
            if old:                                              # a negation already there: the records compose
                el = self._touch(old[0][2], rec, op, when="removed_on")
                state = "negated again"
            else:
                base = None
                if removed:
                    base = dict(removed[0], center=center)
                    if op.get("width") is not None and t != "stairs":
                        base["width"] = round(float(op["width"]), ROUND)
                    if op.get("size") and t == "stairs":
                        base["size"] = _parse_xy(op["size"])
                el = self._new(rec, op, kind, absent=True, base=base)
                lv[t].append(el)
                state = "removed" if removed else "negated"
            out = dict(entry, state=state, ids=[el["id"]])
            if removed:
                out["removed"] = [e["id"] for e in removed]
                el["removed_elements"] = sorted(set(el.get("removed_elements") or []) | set(out["removed"]))
            return out
        if what == "confirm":
            near = self._near(lv, (t,), center, tol)
            if not near:
                return unmatched(f"no {kind} at the place to confirm: nothing invented")
            el = self._touch(near[0][2], rec, op)
            return dict(entry, state="confirmed", ids=[el["id"]])
        if what == "retype":
            if t == "stairs":
                return unmatched("a stair has no type to change")
            near = self._near(lv, klass, center, tol)
            if not near:
                return unmatched(f"nothing of the opening class at the place to retype: nothing invented")
            _d, src, el = near[0]
            changed = []
            if src != t:
                lv[src].remove(el)
                lv[t].append(el)
                changed.append("type")
            el["type"] = kind
            self._touch(el, rec, op, changed)
            return dict(entry, state="retyped" if changed else "confirmed", ids=[el["id"]])
        # add
        near = self._near(lv, klass, center, tol)
        neg = self._near(lv, klass, center, tol, absent=True)
        if near and not (neg and neg[0][0] + NEAR_EPS_M < near[0][0]):
            _d, src, el = near[0]
            changed = []
            if src != t:
                lv[src].remove(el)
                lv[t].append(el)
                changed.append("type")
            if t != "stairs":
                el["type"] = kind
                keys = (("center", center), ("width", round(float(op["width"]), ROUND)
                                             if op.get("width") is not None else None))
            else:
                keys = (("center", center), ("size", _parse_xy(op.get("size")) if op.get("size") else None),
                        ("turn", op.get("turn")))
            for key, value in keys:
                if value is not None and el.get(key) != value:
                    el[key] = value
                    changed.append(key)
            self._touch(el, rec, op, changed)
            state = "replaced" if changed else "confirmed"
        else:
            el = self._new(rec, op, kind)
            lv[t].append(el)
            state = "added"
        out = dict(entry, state=state, ids=[el["id"]])
        if state == "replaced":
            out["changed"] = sorted(set(changed))
        dropped = [e for _d, _t, e in self._near(lv, (t,), el["center"], tol, absent=True)]
        for e in dropped:                                        # the newer record wins over its own kind's negation
            lv[t].remove(e)
        if dropped:
            out["dropped_negations"] = [e["id"] for e in dropped]
        return out

    @staticmethod
    def _room_probe(op) -> dict:
        poly = _parse_poly(op.get("polygon"))
        return {"label": op.get("label"), "polygon": poly,
                "centroid": centroid(poly) if len(poly) >= 3 else _parse_xy(op.get("center"))}

    @staticmethod
    def _room_at(cands: list, probe: dict) -> Optional[dict]:
        """The room of ``cands`` at the probe's place: the score's room rule when the probe has a polygon; else the
        room holding the probe's centre (the same label first), or the same label within the room rule's distance."""
        from wenart.reading_check import score as SC

        if len(probe["polygon"]) >= 3:
            pairs = SC.match_rooms([probe], cands)
            return cands[pairs[0][1]] if pairs else None
        c = probe.get("centroid")
        if not c:
            return None
        holding = [e for e in cands if len(e.get("polygon") or []) >= 3 and _inside(c, e["polygon"])]
        lbl = norm_label(probe.get("label"))
        same = [e for e in holding if lbl and norm_label(e.get("label")) == lbl]
        if same or holding:
            return (same or holding)[0]
        if lbl:
            near = sorted((_dist(e["centroid"], c), str(e.get("id")), e) for e in cands
                          if e.get("centroid") and norm_label(e.get("label")) == lbl
                          and _dist(e["centroid"], c) <= SC.ROOM_CENTROID_M)
            return near[0][2] if near else None
        return None

    def _room(self, rec, op, entry, unmatched, lv, kind):
        from wenart.reading_check import score as SC

        what = op["op"]
        probe = self._room_probe(op)
        if not probe["centroid"]:
            return unmatched("a room needs its polygon or its centre")
        has_poly = len(probe["polygon"]) >= 3
        pos = positives(lv["rooms"])
        hit = self._room_at(pos, probe)
        if what == "remove":
            removed = []
            if hit is not None:
                removed = [hit] + [e for e in pos if e is not hit
                                   and SC.polygon_iou(e.get("polygon"), hit.get("polygon")) >= ROOM_DUPLICATE_IOU]
                for e in removed:
                    lv["rooms"].remove(e)
            elif not has_poly:
                return unmatched("a room given by its centre alone, with no room there, could never match a reading: "
                                 "give its polygon")
            old = self._room_at([e for e in lv["rooms"] if e.get("absent")],
                                probe if has_poly else dict(probe, polygon=removed[0].get("polygon") or []))
            if old is not None:
                el = self._touch(old, rec, op, when="removed_on")
                out = dict(entry, state="negated again", ids=[el["id"]])
            else:
                base = None
                if removed:
                    base = copy.deepcopy(removed[0])
                    if has_poly:
                        base.update(polygon=probe["polygon"], centroid=probe["centroid"])
                    for k in ("label", "room_type"):
                        if op.get(k) is not None:
                            base[k] = op[k]
                el = self._new(rec, op, kind, absent=True, base=base)
                lv["rooms"].append(el)
                out = dict(entry, state="removed" if removed else "negated", ids=[el["id"]])
            if removed:
                out["removed"] = [e["id"] for e in removed]
                el["removed_elements"] = sorted(set(el.get("removed_elements") or []) | set(out["removed"]))
            return out
        if hit is None:
            if what in ("confirm", "retype"):
                return unmatched(f"no room at the place to {what}: nothing invented")
            if not has_poly:
                return unmatched("a room given by its centre alone, with no room there, could never match a reading: "
                                 "give its polygon")
            el = self._new(rec, op, kind)
            lv["rooms"].append(el)
            out = dict(entry, state="added", ids=[el["id"]])
        else:
            changed = []
            if what != "confirm":
                for k in ("label", "room_type"):
                    if op.get(k) is not None and hit.get(k) != op[k]:
                        hit[k] = op[k]
                        changed.append(k)
            el = self._touch(hit, rec, op, changed)
            out = dict(entry, state=("retyped" if what == "retype" else "replaced") if changed else "confirmed",
                       ids=[el["id"]])
            if changed:
                out["changed"] = changed
        negs = [e for e in lv["rooms"] if e.get("absent")]
        gone = [negs[i] for i, _j in SC.match_rooms(negs, [el])] if negs else []
        for e in gone:
            lv["rooms"].remove(e)
        if gone:
            out["dropped_negations"] = [e["id"] for e in gone]
        return out

    def _wall(self, rec, op, entry, unmatched, lv, kind):
        from wenart.reading_check import score as SC

        what = op["op"]
        s, e = _parse_xy(op.get("start")), _parse_xy(op.get("end"))
        if not s or not e:
            return unmatched("a wall needs its start and end")
        probe = {"start": s, "end": e, "thickness": round(float(op["thickness"]), ROUND)
                 if op.get("thickness") is not None else None}
        if what == "retype":
            return unmatched("a wall has no type to change")
        if what == "remove":
            cut, kept = [], []
            for w in list(lv["walls"]):
                if w.get("absent"):
                    continue
                pieces = _cut(w, s, e)
                if pieces is None:
                    continue
                at = lv["walls"].index(w)
                lv["walls"].remove(w)
                cut.append(w["id"])
                for n, (ps, pe) in enumerate(pieces, 1):
                    piece = dict(copy.deepcopy(w), id=f"{w['id']}.{n}", start=ps, end=pe)
                    piece["cut_by"] = list(w.get("cut_by") or []) + [rec["id"]]
                    lv["walls"].insert(at + n - 1, piece)
                    kept.append(piece["id"])
            old = [x for x in lv["walls"] if x.get("absent") and SC.wall_overlap(x, probe) is not None]
            if old:
                el = self._touch(old[0], rec, op, when="removed_on")
                out = dict(entry, state="negated again", ids=[el["id"]])
            else:
                el = self._new(rec, op, kind, absent=True)
                lv["walls"].append(el)
                out = dict(entry, state="cut" if cut else "negated", ids=[el["id"]])
            if cut:
                out["cut"], out["pieces"] = cut, kept
                el["cut_walls"] = sorted(set(el.get("cut_walls") or []) | set(cut))
            return out
        pos = positives(lv["walls"])
        pairs = SC.match_walls([probe], pos)
        if pairs:
            el = self._touch(pos[pairs[0][1]], rec, op)
            out = dict(entry, state="confirmed", ids=[el["id"]])
        elif what == "confirm":
            return unmatched("no wall at the place to confirm: nothing invented")
        else:
            el = self._new(rec, op, kind)
            lv["walls"].append(el)
            out = dict(entry, state="added", ids=[el["id"]])
        gone = [x for x in lv["walls"] if x.get("absent") and SC.wall_overlap(x, el) is not None]
        for x in gone:
            lv["walls"].remove(x)
        if gone:
            out["dropped_negations"] = [x["id"] for x in gone]
        return out


def build_truth(project: str, accepted: dict, records: Iterable[dict]) -> dict:
    """The truth of a project (pure): the accepted reading's entries (``accepted_entries``) and the replay of the
    project's applicable records in id order (the module docstring). Every list is in the deterministic order
    (``_sort_key``); the snapshot names what it was built from (``built_from``) and what each operation did
    (``build_report``). The same inputs give the same bytes."""
    truth = accepted_entries(accepted)
    replay = _Replay(truth)
    applied, unmatched, not_replayed, replayed = [], [], [], []
    mine = sorted((r for r in records if r.get("project") == project), key=lambda r: _record_key(r.get("id")))
    for rec in mine:
        why = correction_applicable(rec)
        if why is None and not record_ops(rec):
            why = "no truth action (nothing placeable to replay)"
        if why:
            not_replayed.append({"record": rec.get("id"), "why": why})
            continue
        replayed.append(rec["id"])
        for op in record_ops(rec):
            res = replay.apply(rec, op)
            (unmatched if res.get("state") == "unmatched" else applied).append(res)
    for lid, lv in (truth.get("per_level") or {}).items():
        for t in ELEMENT_TYPES:
            lv[t] = sorted(lv.get(t) or [], key=lambda e: _sort_key(t, e))
    touched = sorted({res["record"] for res in applied}, key=_record_key)
    truth.pop("corrections", None)
    if touched:
        truth["corrections"] = touched
    truth["built_from"] = {"reading": accepted.get("stored_as") or accepted.get("truth_file"),
                           "reading_commit": accepted.get("commit"), "records": replayed}
    truth.pop("stored_as", None)
    truth["build_report"] = {"applied": applied, "unmatched": unmatched, "not_replayed": not_replayed}
    return truth


# --- files ----------------------------------------------------------------------------------------------------------

def load_baseline(project: str, baseline_dir: Path = BASELINE_DIR) -> Optional[dict]:
    path = Path(baseline_dir) / f"{project}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def load_truth(project: str, truth_dir: Path = TRUTH_DIR) -> Optional[dict]:
    path = Path(truth_dir) / f"{project}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def dumps(data: dict) -> str:
    """The files' text form (one form for the truth and the stored accepted reading, so a rebuild is byte-equal)."""
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def write_truth(project: str, truth: dict, truth_dir: Path = TRUTH_DIR) -> Path:
    Path(truth_dir).mkdir(parents=True, exist_ok=True)
    path = Path(truth_dir) / f"{project}.json"
    path.write_text(dumps(truth), encoding="utf-8")
    return path


def load_accepted(project: str, accepted_dir: Path = ACCEPTED_DIR) -> Optional[dict]:
    """The stored accepted reading of a real project (``results/reading_accepted/<p>.json``), None without one."""
    path = Path(accepted_dir) / f"{project}.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def write_accepted(project: str, accepted: dict, accepted_dir: Path = ACCEPTED_DIR) -> Path:
    Path(accepted_dir).mkdir(parents=True, exist_ok=True)
    path = Path(accepted_dir) / f"{project}.json"
    path.write_text(dumps(accepted), encoding="utf-8")
    return path


def truth_projects(truth_dir: Path = TRUTH_DIR) -> list[str]:
    return sorted(p.stem for p in Path(truth_dir).glob("*.json"))


def default_projects(baseline_dir: Path = BASELINE_DIR, projects_dir: Path = PROJECTS_DIR) -> list[str]:
    """What ``truth build`` builds without ``--projects``: the accepted projects and the synthetic ones."""
    return sorted(set(accepted_projects(baseline_dir)) | set(synthetic_projects(projects_dir)))


def accepted_of(project: str, *, accepted_dir: Path = ACCEPTED_DIR, baseline_dir: Path = BASELINE_DIR,
                projects_dir: Path = PROJECTS_DIR) -> tuple[Optional[dict], Optional[str]]:
    """``(accepted reading, None)`` of a project, or ``(None, why)``: a synthetic project's exact truth; a real
    project's stored accepted reading, while its baseline still says ``accepted_by_user: true``."""
    synth = synthetic_truth_file(project, projects_dir)
    if synth is not None:
        acc = synthetic_truth(project, synth)
        acc["date"] = None                               # no clock in a derived file
        return acc, None
    if acceptance(load_baseline(project, baseline_dir)) is None:
        return None, (f"{project}: the baseline has no accepted_by_user: true: the truth waits for the user's "
                      f"acceptance")
    acc = load_accepted(project, accepted_dir)
    if acc is None:
        return None, (f"{project}: no stored accepted reading ({Path(accepted_dir).name}/{project}.json): run "
                      f"`truth accept --projects {project}` after the user accepted the reading")
    try:
        rel = str((Path(accepted_dir) / f"{project}.json").resolve().relative_to(REPO))
    except ValueError:
        rel = str(Path(accepted_dir) / f"{project}.json")
    acc["stored_as"] = rel
    return acc, None


def build(projects: list[str], *, truth_dir: Path = TRUTH_DIR, accepted_dir: Path = ACCEPTED_DIR,
          baseline_dir: Path = BASELINE_DIR, projects_dir: Path = PROJECTS_DIR,
          corrections: Path = CORRECTIONS_PATH) -> dict:
    """Derive and write the truth of each project (``build_truth`` from ``accepted_of`` and the correction store);
    returns ``{project: truth}`` of the ones written; a project without an accepted reading is printed and skipped."""
    records = load_corrections(corrections)
    out = {}
    for p in projects:
        acc, why = accepted_of(p, accepted_dir=accepted_dir, baseline_dir=baseline_dir, projects_dir=projects_dir)
        if acc is None:
            print(why)
            continue
        truth = build_truth(p, acc, records)
        write_truth(p, truth, truth_dir)
        c = counts(truth)
        rep = truth["build_report"]
        print(f"{p}: truth written ({truth['source']}, {truth['status']}, reading commit "
              f"{(truth.get('commit') or '-')[:12]}; " + ", ".join(f"{k} {v}" for k, v in c.items())
              + f"; records replayed {len(truth['built_from']['records'])}, operations applied {len(rep['applied'])}"
              + f", unmatched {len(rep['unmatched'])})")
        for u in rep["unmatched"]:
            print(f"  unmatched {u['record']} {u['op']} {u['kind']} {u['level']}: {u['why']}")
        out[p] = truth
    return out


def accept(projects: list[str], work: Path, *, fresh: bool = False, allow_drift: bool = False,
           accepted_dir: Path = ACCEPTED_DIR, baseline_dir: Path = BASELINE_DIR,
           projects_dir: Path = PROJECTS_DIR) -> dict:
    """Store the accepted reading of each real project (``truth_of`` on a CPU reading: the user's acceptance in the
    baseline, the drift check, the commit the reading was made at); returns ``{project: accepted}``. A drifted reading
    is stored only with ``allow_drift`` (status ``drifted``). Run ``build`` afterwards."""
    out = {}
    for p in projects:
        if synthetic_truth_file(p, projects_dir) is not None:
            print(f"{p}: synthetic: its exact truth is its accepted reading, nothing to store")
            continue
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
        acc, msgs = truth_of(p, b, base, numbers=nums, commit=read_commit(folder))
        for m in msgs:
            print(m)
        if acc["status"] == "drifted" and not allow_drift:
            print(f"{p}: not stored (--allow-drift stores it with status drifted)")
            continue
        path = write_accepted(p, acc, accepted_dir)
        print(f"{p}: accepted reading stored ({acc['status']}, commit {acc['commit'][:12]}) -> {path.name}; "
              f"run `truth build --projects {p}`")
        out[p] = acc
    return out


# --- the correction store -------------------------------------------------------------------------------------------

def load_corrections(path: Path = CORRECTIONS_PATH) -> list[dict]:
    """The correction records (one JSON object per non-empty line)."""
    path = Path(path)
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_corrections(records: list[dict], path: Path = CORRECTIONS_PATH) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    return path


PLACEABLE_KINDS = ("wall", "door", "window", "opening", "room", "stair")    # an element with one place on a level
SOURCE_REVIEW = "user_review"                                              # a remark captured by `remark add`


def correction_applicable(rec: Optional[dict]) -> Optional[str]:
    """Why a correction record may not go into the truth, None when it may (pure). The truth holds what the user said
    (review of 5 Nov 2026): a record goes in only when it is ``accepted`` (a machine proposal waits for the user) and
    carries the user's words (``user_words``; a remark of the user's review, ``source: user_review``, is the user's
    words itself). 6 Nov 2026 (derived truth): a record a review ``hold``s waits, and a place the machine located
    below ``PLACE_CONFIDENCE_MIN`` waits for the user to check its crop."""
    if rec is None:
        return "no such record in the correction store"
    if rec.get("status") != "accepted":
        return f"status {rec.get('status')!r}: waits for the user's confirmation"
    if rec.get("source") != SOURCE_REVIEW and not str(rec.get("user_words") or "").strip():
        return "no user words: the record states the session's own note, not the user's"
    hold = rec.get("hold")
    if hold:
        return "held: " + str(hold.get("why") if isinstance(hold, dict) else hold)
    conf = rec.get("place_confidence")
    if rec.get("place_source") == "located_by_machine" and conf is not None and float(conf) < PLACE_CONFIDENCE_MIN:
        return f"place confidence {float(conf):.2f} under {PLACE_CONFIDENCE_MIN}: waits for the user to check the place"
    return None


def correction_errors(records: list[dict], lesson_ids: Iterable[str], projects: Iterable[str]) -> list[str]:
    """What is wrong with the correction records (pure): a missing field, an unknown element kind, a lesson not in
    the lessons file (null needs a ``note``), a project not in ``projects/``, a place that is neither null nor
    ``{x, y}``, a repeated id, a truth action that is no list of operations of ``OPS`` on the truth's kinds.

    5 Nov 2026 (Milestone 14, user: "I want structure recognition to be cumulatively better with the feedbacks I am
    giving"): a correction joins the truth and the ranker's labels only through its place. Two rules keep the store
    placeable: an accepted remark of the user's review (``source: user_review``, ``status: accepted``) about a
    placeable element (``PLACEABLE_KINDS``) needs a ``place`` or an explicit ``place_note`` (why it has none); and a
    record that says ``placeable: true`` needs the same, while ``placeable: false`` needs its ``why``. A record marked
    applied (``truth_applied.status``: ``applied`` or ``replayed``) must be one ``correction_applicable`` allows."""
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
        if (rec.get("truth_applied") or {}).get("status") in ("applied", "replayed") and why:
            out.append(f"{rid}: applied to the truth but {why}")
        if rec.get("truth_action") is not None:
            for op in record_ops(rec) or [None]:
                if op is None or op.get("op") not in OPS or op.get("kind") not in tuple(KIND_TO_TYPE) + ("level",):
                    out.append(f"{rid}: truth_action operation {op!r} is not one of {', '.join(OPS)} on a kind of "
                               f"the truth")
                    break
    return out


# --- the command line -----------------------------------------------------------------------------------------------

FIELD_ARGS = ("label", "room_type", "area", "polygon", "center", "width", "wall_id", "start", "end", "thickness",
              "size", "turn", "elevation", "order")


def op_from_args(action: str, kind: str, level: str, fields: dict, *, confirm: bool = False, retype: bool = False,
                 hint: Optional[str] = None) -> dict:
    """The element operation of ``truth add|remove`` (pure): the place in the store's form (points as lists, numbers
    as numbers), the reader's id as a hint. Raises ValueError when the place is missing."""
    what = "remove" if action == "remove" else ("confirm" if confirm else ("retype" if retype else "add"))
    op: dict = {"op": what, "kind": kind, "level": level}
    for k in FIELD_ARGS:
        v = fields.get(k)
        if v in (None, ""):
            continue
        if k in ("center", "start", "end", "size"):
            v = _parse_xy(v)
        elif k == "polygon":
            v = _parse_poly(v)
        elif k in ("area", "width", "thickness", "elevation"):
            v = round(float(v), ROUND)
        elif k == "order":
            v = int(v)
        op[k] = v
    if hint:
        op["id"] = hint
    if kind == "level":
        return op
    t = KIND_TO_TYPE[kind]
    if t == "walls" and not (op.get("start") and op.get("end")):
        raise ValueError("a wall needs --start and --end (or --id of a wall in --reading)")
    if t == "rooms" and not (op.get("polygon") or op.get("center")):
        raise ValueError("a room needs --polygon (or --center of a room the truth holds, or --id in --reading)")
    if t not in ("walls", "rooms") and not op.get("center"):
        raise ValueError(f"a {kind} needs --center (or --id of a {kind} in --reading)")
    return op


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


def place_fields(t: str, el: dict) -> dict:
    """The place and size fields of a truth-shaped element, as ``truth add|remove`` fields."""
    keys = {"rooms": ("label", "room_type", "area", "polygon"), "walls": ("start", "end", "thickness"),
            "stairs": ("center", "size", "turn")}.get(t, ("center", "width", "wall_id"))
    return {k: el.get(k) for k in keys if el.get(k) is not None}


def resolve_id(element_id: str, kind: str, level: str, action: str, *, truth: Optional[dict],
               building: Optional[dict]) -> dict:
    """The place fields ``--id`` names (pure): a truth id in the current truth file, or a reader's id in the reading
    it was taken from (``building``). Refused (ValueError, with what to give instead): a reader's id without its
    reading, an id the reading or the truth lacks, an element of another kind (a door, window or opening may be added
    as another of the three: a retype)."""
    t = KIND_TO_TYPE[kind]
    if is_truth_id(element_id):
        lv = ((truth or {}).get("per_level") or {}).get(level) or {}
        for tt in ELEMENT_TYPES:
            for e in lv.get(tt) or []:
                if e.get("id") == element_id:
                    if tt != t and not (action == "add" and tt in OPENING_TYPES and t in OPENING_TYPES):
                        raise ValueError(f"{element_id} is a {TYPE_KIND[tt]} in the truth, not a {kind}: give "
                                         f"--kind {TYPE_KIND[tt]}")
                    return place_fields(tt, e)
        raise ValueError(f"{element_id}: no such truth id on {level} (truth ids change with every build: give the "
                         f"place, --center / --polygon / --start --end)")
    if building is None:
        raise ValueError(f"{element_id} is a reader's id: give the reading it was taken from (--reading), or the "
                         f"place (--center / --polygon / --start --end)")
    found = reading_element(building, element_id, level)
    if found is None:
        raise ValueError(f"{element_id}: the given reading has no such element on {level}")
    tt, el = found
    if tt != t and not (action == "add" and tt in OPENING_TYPES and t in OPENING_TYPES):
        raise ValueError(f"{element_id} is a {TYPE_KIND[tt]} in the given reading, not a {kind}: give --kind "
                         f"{TYPE_KIND[tt]}" + (" (or add it as a door, window or opening to retype it)"
                                               if tt in OPENING_TYPES else ""))
    return place_fields(tt, el)


def _next_record_id(records: list[dict]) -> str:
    top = 0
    for r in records:
        rid = str(r.get("id", ""))
        if rid[:1] == "C" and rid[1:].isdigit():
            top = max(top, int(rid[1:]))
    return f"C{top + 1:04d}"


def correct(args, *, corrections: Optional[Path] = None, truth_dir: Optional[Path] = None,
            accepted_dir: Optional[Path] = None, baseline_dir: Optional[Path] = None,
            projects_dir: Optional[Path] = None) -> tuple[int, str]:
    """``truth add|remove``: ``(exit code, message)``. The operation goes into a record (a new one with the user's
    words, ``--text``; or the one ``--correction`` names: accepted, with the user's words, of the same project), the
    project's truth is rebuilt with it, and only when the replay applied the operation are the store and the truth
    written. The folders default to the repository's (read when called). A refusal or an unreadable input is an
    answer (exit code 2 and the reason), never a traceback."""
    try:
        return _correct(args, corrections=corrections, truth_dir=truth_dir, accepted_dir=accepted_dir,
                        baseline_dir=baseline_dir, projects_dir=projects_dir)
    except (ValueError, KeyError, TypeError, AttributeError, OSError, json.JSONDecodeError) as exc:
        return 2, str(exc) if type(exc) is ValueError else f"{type(exc).__name__}: {exc}"


def _correct(args, *, corrections, truth_dir, accepted_dir, baseline_dir, projects_dir) -> tuple[int, str]:
    corrections = Path(corrections or CORRECTIONS_PATH)
    truth_dir, accepted_dir = Path(truth_dir or TRUTH_DIR), Path(accepted_dir or ACCEPTED_DIR)
    baseline_dir, projects_dir = Path(baseline_dir or BASELINE_DIR), Path(projects_dir or PROJECTS_DIR)
    g = lambda k: getattr(args, k, None)                 # noqa: E731 - a namespace may lack the optional fields
    project, level, kind, action = g("project"), g("level"), g("kind"), g("action")
    if not project or not kind or not level:
        return 2, "--project, --level and --kind are needed"
    if kind not in tuple(KIND_TO_TYPE) + ("level",):
        return 2, f"--kind {kind!r}: one of {', '.join(KIND_TO_TYPE)} or level"
    if kind == "level" and action == "remove":
        return 2, "a level cannot be negated: correct its elements, or leave it out in the baseline"
    if g("source") not in (None, SOURCE_USER):
        return 2, (f"--source {g('source')}: only the user's corrections enter a truth through add/remove (a "
                   f"synthetic project's truth is its exact truth file)")
    records = load_corrections(corrections)
    rec = None
    if g("correction"):
        rec = next((r for r in records if r.get("id") == g("correction")), None)
        why = correction_applicable(rec)
        if why:
            return 2, f"correction {g('correction')} is not applied: {why}"
        if rec.get("project") != project:
            return 2, f"correction {rec['id']} is a record of {rec.get('project')}, not of {project}"
    elif not str(g("text") or "").strip():
        return 2, "a correction needs the user's words: --text \"...\" (a new record) or --correction <record id>"
    acc, why = accepted_of(project, accepted_dir=accepted_dir, baseline_dir=baseline_dir, projects_dir=projects_dir)
    if acc is None:
        return 2, why
    fields = {k: g(k) for k in FIELD_ARGS}
    hint = None
    if g("id") and kind != "level":
        building = None
        if g("reading"):
            rp = Path(g("reading"))
            rp = rp / "building.json" if rp.is_dir() else rp
            if not rp.is_file():
                return 2, f"--reading {g('reading')}: no building.json there"
            building = json.loads(rp.read_text(encoding="utf-8"))
        given = resolve_id(g("id"), kind, level, action, truth=load_truth(project, truth_dir), building=building)
        fields = dict(given, **{k: v for k, v in fields.items() if v not in (None, "")})
        hint = None if is_truth_id(g("id")) else g("id")
    op = op_from_args(action, kind, level, fields, confirm=bool(g("confirm")), retype=bool(g("retype")), hint=hint)
    date = g("date") or today()
    new_records = copy.deepcopy(records)
    if rec is not None:
        target = next(r for r in new_records if r.get("id") == rec["id"])
        act = target.get("truth_action")
        ops = record_ops(target)
        if any({k: v for k, v in o.items() if k != "note"} == op for o in ops):
            pass                                          # the record holds the operation already: rebuild only
        else:
            if not isinstance(act, dict):
                target["truth_action"] = {"op": op["op"], "kind": kind, "elements": [op]}
            elif isinstance(act.get("elements"), list):
                act["elements"].append(op)
            else:
                target["truth_action"] = {"op": act.get("op"), "kind": act.get("kind"), "elements": [act, op]}
            target.setdefault("history", []).append({"date": date, "truth_op_added": op, "by": "truth " + action})
            if target.get("place") is None and kind != "level":
                p = op.get("center") or op.get("start") or centroid(op.get("polygon") or [])
                if p:
                    target["place"] = {"x": p[0], "y": p[1]}
    else:
        p = None if kind == "level" else (op.get("center") or op.get("start") or centroid(op.get("polygon") or []))
        target = {"id": _next_record_id(new_records), "date": date, "project": project, "level": level,
                  "place": {"x": p[0], "y": p[1]} if p else None, "element_kind": kind,
                  "reader_answer": g("reader_answer") or "", "right_answer": g("right_answer") or "",
                  "user_words": str(g("text")).strip(), "lesson": g("lesson"), "source": SOURCE_REVIEW,
                  "status": "accepted", "placeable": kind != "level"}
        if kind == "level":
            target["why"] = "a level of the truth"
        else:
            target.update(place_source="given_by_user", place_confidence=1.0,
                          place_note=f"given with `truth {action}`")
        if hint:
            target["reader_ids"] = [hint]
        if not g("lesson"):
            target["note"] = "no lesson yet: the general rule for this correction is still to be written"
        target["truth_action"] = {"op": op["op"], "kind": kind, "elements": [op]}
        new_records.append(target)
    truth = build_truth(project, acc, new_records)
    mine = [r for r in truth["build_report"]["applied"] + truth["build_report"]["unmatched"]
            if r["record"] == target["id"]]
    last = mine[-1] if mine else {"state": "unmatched", "why": "not replayed"}
    if last.get("state") == "unmatched":
        return 2, f"nothing written: the operation is unmatched: {last.get('why')}"
    save_corrections(new_records, corrections)
    path = write_truth(project, truth, truth_dir)
    try:
        shown = path.relative_to(REPO)
    except ValueError:
        shown = path
    return 0, (f"{project}: {last['op']} {kind} on {level}: {last['state']} ({', '.join(last.get('ids') or [])}), "
               f"record {target['id']}; truth rebuilt -> {shown}")


def main(args) -> int:
    action = getattr(args, "action", None)
    if action == "build":
        projects = [p.strip() for p in (getattr(args, "projects", None) or "").split(",") if p.strip()] \
            or default_projects()
        if not projects:
            print("reading truth: no accepted baseline (accepted_by_user: true) in results/reading_baseline/, no "
                  "synthetic project with a truth and no --projects")
            return 2
        done = build(projects)
        return 0 if len(done) == len(projects) else 1
    if action == "accept":
        projects = [p.strip() for p in (getattr(args, "projects", None) or "").split(",") if p.strip()]
        if not projects:
            print("reading truth accept: name the projects the user accepted (--projects a,b)")
            return 2
        import tempfile
        work = Path(args.work) if getattr(args, "work", None) else Path(tempfile.mkdtemp(prefix="reading_accept_"))
        done = accept(projects, work, fresh=bool(getattr(args, "fresh", False)),
                      allow_drift=bool(getattr(args, "allow_drift", False)))
        return 0 if len(done) == len(projects) else 1
    if action in ("add", "remove"):
        code, msg = correct(args)
        print(f"reading truth {action}: {msg}" if code else msg)
        return code
    print(f"reading truth: unknown action {action}")
    return 2
