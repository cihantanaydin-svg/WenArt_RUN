"""RL try 2 of the AI checks' vision model: training questions from the dataset bench (23 Nov 2026; user: "continue").

Pilot 1 (``rl_pilot.py``, 22 Nov 2026) trained a rejection-sampling LoRA on close-up questions about our synthetic
plans: 105 -> 117 of 117 held-out synthetic questions, but 64 -> 52 of 73 known errors on the real exam against its own
base (UL359, UL360). It learned our synthetic drawings. This try changes one variable, the data source: the questions
are asked about the dataset bench (``wenart/datasets/bench.py``: real Swiss buildings converted to DXF, read by our own
CPU reader, the truth the converter's exact geometry), so every "wrong" item is a real error of our reader on real
plan geometry. The rest is pilot 1's recipe (``rl_pilot``: 8 samples at temperature 0.8 from the FP8 agent model,
rejection sampling, a rank-16 LoRA on the BF16 base for 2 epochs, served beside it by vLLM).

What:
- ``python -m wenart.reading_check rl_bench build [--bench DIR] [--work DIR] [--out DIR]`` (CPU): every bench reading
  aligned on its truth (``bench.align``) and matched per element kind (``score.match_kind``); the close-up questions the
  RC15 checks ask about a reading, each with the answer the truth gives:
  ``wall_right`` (the model's wall at the ring: is it drawn there? matched: yes; on no drawn line: no),
  ``wall_missing`` (does the drawing draw a wall there the model lacks? missed: yes; matched: no),
  ``opening_right`` (the model's door or window at the ring: what does the drawing draw there? door / window / none),
  ``opening_missing`` (a door or window drawn there that the model lacks? yes / no),
  ``room_right`` (the model's room at the ring: the same room in the drawing? yes / no),
  ``room_missing`` (the drawing's room at the ring: does the model lack it, missing or merged? yes / no),
  ``stair_right`` and ``stair_missing`` likewise (generated, not asked: ``KINDS``). Ambiguous items are left out (a split wall piece, a wall of another
  thickness, an opening offset by 0.3-1.0 m, a parapet, an open-air space, a room under 1 m2). Two close-ups per
  question (the drawing and the model drawn as an architect's plan, ``critic.render_level(model_style="arch")``, the
  same crop, a red ring at the place), like the RC15 judge. The split is by building (``train_building``: the bench's
  projects sorted by a sha1 hash, the first half trains, the second half is the held-out bench test); per building and
  class (kind, answer) at most ``CAP_BUILDING``, per class at most ``CAP_CLASS`` (train) / ``CAP_CLASS_HELD``, right and
  wrong items balanced per kind. Writes ``questions.jsonl``, ``crops/`` and ``manifest.json`` (committed: the pod has no
  bench).
- ``filter`` (pod): rejection sampling (``rl_pilot.keep_question``), one row per kept question, at most ``ROWS_MAX``
  rows balanced over the classes (the training time of the pod: 2 epochs of ~4.5 s a row).
- ``phase-sample`` (pod, the FP8 agent model): the training questions 8 times at temperature 0.8, the held-out
  questions once at temperature 0, then exam arm (a) (the RC15 calls with the drawing text, ``rl_pilot._exam`` with
  arm ``1``).
- ``phase-exam`` (pod, the BF16 base with the LoRA beside it): the held-out questions with the LoRA and the base, then
  exam arms (c) (LoRA) and (b) (base) asked side by side (two clients, one server: a deadline cuts both arms alike).
- ``held-score`` (CPU): the held-out bench table per arm: accuracy, the reader's errors flagged, false alarms.

The exam is scored on the CPU with ``critic vt-score`` (known errors of 73, false findings on the user's marks, which
no arm saw, the judge items). Ship rule (UL359, UL360): the LoRA arm ships only when it finds more known errors than
both other arms with no more false findings; the held-out bench is information only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Optional

from wenart.reading_check import rl_pilot as RP

REPO = Path(__file__).resolve().parents[2]
BENCH = Path("/home/user/bench_data/projects")
WORK = Path("/home/user/bench_data/work_lightwell")
SET_DIR = REPO / "results" / "rl_bench" / "set"
SEED = 20261123
N_SAMPLES = RP.N_SAMPLES                  # 8, pilot 1's recipe
TEMPERATURE = RP.TEMPERATURE              # 0.8
MAX_TOKENS = RP.MAX_TOKENS
CROP_M = 6.0                              # a close-up shows this many metres around its ring (rooms: their box + margin)
ROOM_MARGIN_M = 1.5
CROP_PX = 384                             # each close-up's side (two per question)
MIN_WALL_M = 1.0
OPENING_CLEAR_M = 0.5                     # a wall ring this far (plus half the width) from every opening
NONE_CLEAR_M = 1.0                        # "no opening": no drawn door or window this near; "missing": none read
STAIR_CLEAR_M = 2.0
COVER_SHARE = 0.2                         # a wall counted missing / invented only when this little of it is covered
WALL_AWAY_M = 0.4                         # ... and its middle this far from the other side's wall lines (plus half
                                          # their thickness): a tilted or shifted copy of a drawn wall is no clear item
MAX_CROP_M = 14.0                         # a room larger than this (with its margin) is left out (too small at 384 px)
MIN_ROOM_M2 = 1.0
OPEN_AIR = ("balcony", "terrace", "loggia", "deck", "patio", "courtyard", "roof_terrace", "garden")
CAP_BUILDING = 3                          # per building and class (kind, answer)
CAP_CLASS = 40                            # per class, training half
CAP_CLASS_HELD = 20                       # per class, held-out half
ROWS_MAX = 176                            # training rows (2 epochs at ~37 s per 8 rows: ~27 min on the RTX PRO 6000)
# 23 Nov 2026: the stair kinds are generated but not asked: the model image (``critic_checks.draw_arch``) draws a
# reading's stair as a thin empty box with no treads when its record has ``details.stair`` without flights (the S4
# fire-stair flag; seen on swiss-b2486 L1), so image 2 cannot answer them
KINDS = ("wall_right", "wall_missing", "opening_right", "opening_missing", "room_right", "room_missing")
YES_NO = "{\"answer\": \"yes\" | \"no\"}"
BASE = ("Image 1 is a close-up of an architect's floor plan; image 2 is a computer's model of the same place drawn the "
        "same way (black walls, door leaves and swings, window symbols, room labels), in the same frame. The red ring "
        "marks the same place in both. ")
PROMPTS = {
    "wall_right": BASE + "Image 2 has a wall at the ring. Does image 1 draw a wall there, on the same line? Answer only "
                         "JSON: " + YES_NO,
    "wall_missing": BASE + "Does image 1 draw a wall at the ring that image 2 does not have? Answer only JSON: " + YES_NO,
    "opening_right": BASE + "Image 2 has a {model} at the ring. What does image 1 draw there: a door (a leaf with a "
                            "swing arc), a window (thin parallel lines across the wall) or no opening (none)? Answer only "
                            "JSON: {{\"answer\": \"door\" | \"window\" | \"none\"}}",
    "opening_missing": BASE + "Does image 1 draw a door or a window at the ring that image 2 does not have (no door, "
                              "window or gap there in image 2)? Answer only JSON: " + YES_NO,
    "room_right": BASE + "Image 2 has a room at the ring (the space its walls close around the ring). Does image 1 draw "
                         "the same room there, with about the same outline (not a part of a bigger room, not two rooms)? "
                         "Answer only JSON: " + YES_NO,
    "room_missing": BASE + "Image 1 draws a room at the ring. Does image 2 lack it as a room of its own (no room there, "
                           "or that room merged with a neighbouring room into one)? Answer only JSON: " + YES_NO,
    "stair_right": BASE + "Image 2 has a stair at the ring. Does image 1 draw a stair there (treads drawn as parallel "
                          "lines, a flight or a landing)? Answer only JSON: " + YES_NO,
    "stair_missing": BASE + "Image 1 draws a stair at the ring. Does image 2 lack it (no stair there)? Answer only JSON: "
                            + YES_NO,
}
LABELS = ["Image 1 (the drawing):", "Image 2 (the computer's model):"]


def prompt_of(q: dict) -> str:
    text = PROMPTS[q["kind"]]
    return text.format(model=q.get("model_has") or "opening") if q["kind"] == "opening_right" else text


def says_error(q: dict, answer) -> Optional[bool]:
    """Whether ``answer`` says the reading is wrong at the question's place (pure): ``no`` to a ``*_right`` question
    (for ``opening_right``: any type but the model's), ``yes`` to a ``*_missing`` question; None for no answer."""
    if not isinstance(answer, str):
        return None
    a = answer.strip().lower()
    if q["kind"] == "opening_right":
        return a != str(q.get("model_has"))
    if q["kind"].endswith("_right"):
        return a == "no"
    return a == "yes"


def verify(q: dict, text: str) -> Optional[bool]:
    """True / False when the model's answer ``text`` is right / wrong against the truth, None with no answer (pure)."""
    ans = RP.parse_answer(text)
    if ans is None:
        return None
    return isinstance(ans, str) and ans.strip().lower() == str(q["answer"])


# --- the split and the questions (pure) -------------------------------------------------------------------------------

def _h(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()


def split(projects: list) -> dict:
    """``{project: "train" | "held"}`` (pure): the projects sorted by a sha1 hash of their name, the first half trains
    (a building is never in both halves)."""
    order = sorted(projects, key=_h)
    half = (len(order) + 1) // 2
    return {p: ("train" if i < half else "held") for i, p in enumerate(order)}


def _mid(w: dict) -> list:
    return [(float(w["start"][0]) + float(w["end"][0])) / 2.0, (float(w["start"][1]) + float(w["end"][1])) / 2.0]


def _len(w: dict) -> float:
    return math.dist(w["start"], w["end"])


def _inverse(move: Optional[dict]):
    """The map from the truth frame back to the reading's own frame of a level moved by ``bench.align`` (aligned
    p' = R(rot) p - shift, so p = R(-rot) (p' + shift))."""
    if not move:
        return lambda p: [float(p[0]), float(p[1])]
    dx, dy = move["shift_m"]
    c, s = math.cos(math.radians(-move["rot_deg"])), math.sin(math.radians(-move["rot_deg"]))

    def back(p):
        x, y = float(p[0]) + dx, float(p[1]) + dy
        return [c * x - s * y, s * x + c * y]
    return back


def _inner_point(poly: list) -> Optional[list]:
    from shapely.geometry import Polygon
    from shapely.ops import polylabel

    try:
        pg = Polygon(poly).buffer(0)
        if pg.is_empty:
            return None
        if pg.geom_type != "Polygon":
            pg = max(pg.geoms, key=lambda g: g.area)
        p = polylabel(pg, tolerance=0.05)
        return [p.x, p.y]
    except Exception:                                           # noqa: BLE001 - a broken outline gives no question
        return None


def _room_crop(poly: list) -> float:
    xs, ys = [float(p[0]) for p in poly], [float(p[1]) for p in poly]
    return max(CROP_M, max(max(xs) - min(xs), max(ys) - min(ys)) + 2 * ROOM_MARGIN_M)


def _away(p, walls: list) -> bool:
    """Whether point ``p`` lies at least ``WALL_AWAY_M`` plus half the thickness from every wall's centre line."""
    return all(RP._seg_dist(p, w["start"], w["end"]) >= WALL_AWAY_M + float(w.get("thickness") or 0) / 2.0
               for w in walls if w.get("start") and w.get("end"))


def _area(poly: list) -> float:
    from shapely.geometry import Polygon
    try:
        return float(Polygon(poly).buffer(0).area)
    except Exception:                                           # noqa: BLE001
        return 0.0


def level_items(project: str, lid: str, tl: dict, raw: dict, al: dict, move: Optional[dict]) -> list:
    """The candidate questions of one level (pure): ``{id, project, level, kind, answer, error, at, crop_m, model_has,
    why}``, ``at`` in the reading's own frame (the frame of its images). ``tl`` the truth level, ``raw`` / ``al`` the
    reading's level before / after ``bench.align`` (same element order)."""
    from wenart.datasets import bench as BE
    from wenart.reading_check import score as SC
    from wenart.reading_check import truth as TR

    back = _inverse(move)
    out: list = []

    def add(kind, at, answer, error, why, crop_m=CROP_M, model_has=None):
        out.append({"id": f"{project}|{lid}|{kind}|{at[0]:.2f},{at[1]:.2f}", "project": project, "level": lid,
                    "kind": kind, "answer": answer, "error": bool(error), "at": [round(at[0], 3), round(at[1], 3)],
                    "crop_m": round(crop_m, 2), "model_has": model_has, "why": why})

    t_ops = [o for k in ("doors", "windows") for o in TR.positives(tl.get(k) or []) if o.get("center")]
    a_ops = [o for k in ("doors", "windows", "openings") for o in al.get(k) or [] if o.get("center")]

    def clear_of_openings(p) -> bool:
        return all(math.dist(p, o["center"]) >= OPENING_CLEAR_M + float(o.get("width") or 0) / 2.0
                   for o in t_ops + a_ops)

    # walls
    tt = [w for w in TR.positives(tl.get("walls") or []) if w.get("start") and w.get("end")]
    rr_al, rr_raw = al.get("walls") or [], raw.get("walls") or []
    m = SC.match_kind("walls", tt, rr_al)
    mt, mr = {i: j for i, j in m}, {j: i for i, j in m}
    for j, r in enumerate(rr_al):
        if not r.get("start") or not r.get("end") or _len(r) < MIN_WALL_M or not clear_of_openings(_mid(r)):
            continue
        at = _mid(rr_raw[j])
        if j in mr:
            if not tt[mr[j]].get("parapet"):
                add("wall_right", at, "yes", False, "matched")
        elif BE._extra_wall_class(r, tt).startswith("wall invented") and \
                BE.covered_length(r, tt) < COVER_SHARE * _len(r) and _away(_mid(r), tt):
            add("wall_right", at, "no", True, "wall invented (on no drawn wall line)")
    for i, t in enumerate(tt):
        if t.get("parapet") or _len(t) < MIN_WALL_M or not clear_of_openings(_mid(t)):
            continue
        at = back(_mid(t))
        if i in mt:
            add("wall_missing", at, "no", False, "matched")
        else:
            cls = BE._wall_class(t, rr_al)
            if cls != "wall read with another thickness" and BE.covered_length(t, rr_al) < COVER_SHARE * _len(t) \
                    and _away(_mid(t), rr_al):
                add("wall_missing", at, "yes", True, cls)
    # doors and windows
    for kind, other in (("doors", "windows"), ("windows", "doors")):
        tk = [o for o in TR.positives(tl.get(kind) or []) if o.get("center")]
        to = [o for o in TR.positives(tl.get(other) or []) if o.get("center")]
        ra = [o for o in al.get(kind) or [] if o.get("center")]
        rw = raw.get(kind) or []
        rw = [o for o in rw if o.get("center")]
        m = SC.match_kind(kind, tk, ra)
        mt, mr = {i: j for i, j in m}, {j: i for i, j in m}
        mine, theirs = kind[:-1], other[:-1]
        for j, r in enumerate(ra):
            at = rw[j]["center"]
            if j in mr:
                add("opening_right", at, mine, False, "matched", model_has=mine)
                continue
            near_other = [o for o in to if math.dist(o["center"], r["center"]) <= SC.OPENING_CENTER_M]
            near_mine = [o for o in tk if math.dist(o["center"], r["center"]) <= NONE_CLEAR_M]
            if near_other and not near_mine:
                add("opening_right", at, theirs, True, f"{theirs} read as {mine}", model_has=mine)
            elif not near_mine and not any(math.dist(o["center"], r["center"]) <= NONE_CLEAR_M for o in to):
                add("opening_right", at, "none", True, f"{mine} invented", model_has=mine)
        for i, t in enumerate(tk):
            at = back(t["center"])
            if i in mt:
                add("opening_missing", at, "no", False, "matched")
            elif not any(math.dist(o["center"], t["center"]) <= NONE_CLEAR_M for o in a_ops):
                add("opening_missing", at, "yes", True, f"{mine} missed")
    # rooms
    tt = [r for r in TR.positives(tl.get("rooms") or []) if len(r.get("polygon") or []) >= 3]
    ra = [r for r in al.get("rooms") or [] if len(r.get("polygon") or []) >= 3]
    rw = [r for r in raw.get("rooms") or [] if len(r.get("polygon") or []) >= 3]
    m = SC.match_kind("rooms", tt, ra)
    mt, mr = {i: j for i, j in m}, {j: i for i, j in m}

    def open_air(r) -> bool:
        return str(r.get("room_type") or "") in OPEN_AIR

    for j, r in enumerate(ra):
        if open_air(r) or _area(r["polygon"]) < MIN_ROOM_M2 or (j in mr and open_air(tt[mr[j]])) \
                or _room_crop(rw[j]["polygon"]) > MAX_CROP_M:
            continue
        at = _inner_point(rw[j]["polygon"])
        if at is None:
            continue
        if j in mr:
            add("room_right", at, "yes", False, "matched", crop_m=_room_crop(rw[j]["polygon"]))
        else:
            add("room_right", at, "no", True, "room invented or split", crop_m=_room_crop(rw[j]["polygon"]))
    for i, t in enumerate(tt):
        if open_air(t) or _area(t["polygon"]) < MIN_ROOM_M2 or _room_crop(t["polygon"]) > MAX_CROP_M:
            continue
        p = _inner_point(t["polygon"])
        if p is None:
            continue
        poly = [back(q) for q in t["polygon"]]
        if i in mt:
            add("room_missing", back(p), "no", False, "matched", crop_m=_room_crop(poly))
        else:
            add("room_missing", back(p), "yes", True, "room missed or merged", crop_m=_room_crop(poly))
    # stairs
    tt = [s for s in TR.positives(tl.get("stairs") or []) if s.get("center")]
    ra = [s for s in al.get("stairs") or [] if s.get("center")]
    rw = [s for s in raw.get("stairs") or [] if s.get("center")]
    m = SC.match_kind("stairs", tt, ra)
    mt, mr = {i: j for i, j in m}, {j: i for i, j in m}
    for j, r in enumerate(ra):
        if j in mr:
            add("stair_right", rw[j]["center"], "yes", False, "matched")
        elif not any(math.dist(t["center"], r["center"]) <= STAIR_CLEAR_M for t in tt):
            add("stair_right", rw[j]["center"], "no", True, "stair invented")
    for i, t in enumerate(tt):
        if i in mt:
            add("stair_missing", back(t["center"]), "no", False, "matched")
        elif not any(math.dist(r["center"], t["center"]) <= STAIR_CLEAR_M for r in ra):
            add("stair_missing", back(t["center"]), "yes", True, "stair missed")
    return out


def cls_of(q: dict) -> str:
    """The class of a question: its kind and answer (``opening_right`` also the model's type: a door read as a window
    is not a window read right)."""
    if q["kind"] == "opening_right":
        return f"opening_right:{q.get('model_has')}->{q['answer']}"
    return f"{q['kind']}:{q['answer']}"


def select(items: list, cap_class: int, cap_building: int = CAP_BUILDING) -> list:
    """The questions kept (pure, deterministic): items in sha1 order; per building and class at most ``cap_building``;
    per class at most ``cap_class``; per kind as many right as wrong items (the larger side cut to the smaller, the
    ``opening_right`` right items split evenly between door and window)."""
    items = sorted(items, key=lambda q: _h(q["id"]))
    per_b: dict = {}
    per_c: dict = {}
    kept = []
    for q in items:
        kb, kc = (q["project"], cls_of(q)), cls_of(q)
        if per_b.get(kb, 0) >= cap_building or per_c.get(kc, 0) >= cap_class:
            continue
        per_b[kb] = per_b.get(kb, 0) + 1
        per_c[kc] = per_c.get(kc, 0) + 1
        kept.append(q)
    out = []
    for kind in KINDS:
        right = [q for q in kept if q["kind"] == kind and not q["error"]]
        wrong = [q for q in kept if q["kind"] == kind and q["error"]]
        n = min(len(right), len(wrong))
        if kind == "opening_right":
            doors = [q for q in right if q["answer"] == "door"]   # right items: the answer is the model's type
            wins = [q for q in right if q["answer"] == "window"]
            nd = min(len(doors), max(n - len(wins), n // 2 + n % 2))
            right = doors[:nd] + wins[:n - nd]
        out += right[:n] + wrong[:n]
    return sorted(out, key=lambda q: _h(q["id"]))


# --- building the set (CPU, the bench readings) -----------------------------------------------------------------------

def project_candidates(project_dir: Path, read_dir: Path) -> list:
    """Every candidate question of one bench reading (the truth and the reading as ``bench.score_one`` reads them)."""
    from wenart.datasets import bench as BE
    from wenart.reading_check import truth as TR

    name = Path(project_dir).name
    truth = TR.synthetic_truth(name, Path(project_dir) / "truth" / "reading_truth.json")
    b = json.loads((Path(read_dir) / "building.json").read_text(encoding="utf-8"))
    raw = TR.extract(b, project=name)
    al, moves = BE.align(truth, raw)
    out = []
    for lid, tl in (truth.get("per_level") or {}).items():
        rl, ra = (raw.get("per_level") or {}).get(lid), (al.get("per_level") or {}).get(lid)
        if not rl or not ra or not (rl.get("walls") or []):
            continue
        out += level_items(name, lid, tl, rl, ra, moves.get(lid))
    return out


def _render(read_dir: Path, lid: str, dest: Path, cache: dict) -> Optional[dict]:
    from wenart.reading_check import critic as CR

    key = (str(read_dir), lid)
    if key not in cache:
        cache[key] = CR.render_level(read_dir, lid, dest, model_style="arch", building=cache.get(("b", str(read_dir))),
                                     docs=cache.setdefault(("docs", str(read_dir)), {}))
    return cache[key]


def build(out: Path = SET_DIR, bench: Path = BENCH, work: Path = WORK, *, log=print) -> dict:
    """The question set (the module docstring): ``out/questions.jsonl``, ``out/crops/``, ``out/manifest.json``."""
    import shutil
    import tempfile

    from PIL import Image

    from wenart.reading_check import critic as CR
    from wenart.reading_check.critic_checks import _crop

    out = Path(out)
    projects = sorted(p.name for p in Path(bench).iterdir() if (p / "truth" / "reading_truth.json").is_file()
                      and (Path(work) / p.name / "building.json").is_file())
    halves = split(projects)
    cands: dict = {"train": [], "held": []}
    failed = []
    for p in projects:
        try:
            items = project_candidates(Path(bench) / p, Path(work) / p)
        except Exception as exc:                                # noqa: BLE001 - one bad reading never stops the set
            failed.append({"project": p, "error": f"{type(exc).__name__}: {str(exc)[:200]}"})
            continue
        cands[halves[p]] += items
    chosen = {"train": select(cands["train"], CAP_CLASS), "held": select(cands["held"], CAP_CLASS_HELD)}
    if (out / "crops").is_dir():
        shutil.rmtree(out / "crops")
    (out / "crops").mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="rl_bench_"))
    cache: dict = {}
    allq, skipped = [], 0
    try:
        for half in ("train", "held"):
            for q in chosen[half]:
                e = _render(Path(work) / q["project"], q["level"], tmp / q["project"], cache)
                if e is None:
                    skipped += 1
                    continue
                nx, ny = CR.metres_to_norm(q["at"][0], q["at"][1], e["box"], e["tf"])
                if not (0.02 <= nx <= 0.98 and 0.02 <= ny <= 0.98):
                    skipped += 1
                    continue
                w, h = e["size"]
                a = CR.metres_to_norm(0.0, 0.0, e["box"], e["tf"])
                b = CR.metres_to_norm(1.0, 0.0, e["box"], e["tf"])
                ppm = math.hypot((b[0] - a[0]) * w, (b[1] - a[1]) * h)
                side = max(64, int(q["crop_m"] * ppm))
                stem = _h(q["id"])[:16]
                q["images"] = []
                for tag, f in (("d", e["drawing"]), ("m", e["model"])):
                    im = Image.open(tmp / q["project"] / f).convert("RGB")
                    c = _crop(im, (nx, ny), side, CROP_PX)
                    c.save(out / "crops" / f"{stem}_{tag}.jpg", quality=80, optimize=True)
                    q["images"].append(f"crops/{stem}_{tag}.jpg")
                q["held_out"] = half == "held"
                allq.append(q)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    with open(out / "questions.jsonl", "w", encoding="utf-8") as fh:
        for q in allq:
            fh.write(json.dumps(q, ensure_ascii=False) + "\n")

    def counts(qs):
        c: dict = {}
        for q in qs:
            c[cls_of(q)] = c.get(cls_of(q), 0) + 1
        return dict(sorted(c.items()))

    tr = [q for q in allq if not q["held_out"]]
    he = [q for q in allq if q["held_out"]]
    manifest = {"made": "2026-11-23", "bench": str(bench), "readings": str(work), "seed": SEED,
                "projects": len(projects), "projects_train": sorted(p for p in projects if halves[p] == "train"),
                "projects_held": sorted(p for p in projects if halves[p] == "held"),
                "buildings_with_questions": {"train": len({q["project"] for q in tr}),
                                             "held": len({q["project"] for q in he})},
                "candidates": {"train": counts(cands["train"]), "held": counts(cands["held"])},
                "questions": len(allq), "train": len(tr), "held_out": len(he),
                "counts": {"train": counts(tr), "held": counts(he)},
                "errors_share": {"train": round(sum(q["error"] for q in tr) / max(1, len(tr)), 3),
                                 "held": round(sum(q["error"] for q in he) / max(1, len(he)), 3)},
                "skipped_no_image": skipped, "failed": failed,
                "crops_mb": round(sum(f.stat().st_size for f in (out / "crops").glob("*.jpg")) / 1e6, 1),
                "samples_per_question": N_SAMPLES, "calls": len(tr) * N_SAMPLES, "rows_max": ROWS_MAX,
                "caps": {"building": CAP_BUILDING, "class_train": CAP_CLASS, "class_held": CAP_CLASS_HELD}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    log(f"rl_bench: {len(tr)} training and {len(he)} held-out questions, {manifest['crops_mb']} MB of crops")
    return manifest


# --- the pod side -------------------------------------------------------------------------------------------------------

def load_questions(path: Path) -> dict:
    return RP.load_questions(path)


def _image_url(path: Path) -> str:
    import base64
    return "data:image/jpeg;base64," + base64.b64encode(Path(path).read_bytes()).decode("ascii")


def messages_of(q: dict, train_dir: Path) -> list:
    """The OpenAI chat messages of one question: the checks' system text, the two close-ups after their labels, the
    question (the RC15 judge's layout)."""
    from wenart.reading_check.critic_checks import SYSTEM_TEXT

    content: list = []
    for label, img in zip(LABELS, q["images"]):
        content += [{"type": "text", "text": label},
                    {"type": "image_url", "image_url": {"url": _image_url(Path(train_dir) / img)}}]
    content.append({"type": "text", "text": prompt_of(q)})
    return [{"role": "system", "content": SYSTEM_TEXT}, {"role": "user", "content": content}]


def sft_row(q: dict, answer_json: str) -> dict:
    """One TRL prompt-completion row (the images by path, in the order of their ``{"type": "image"}`` parts)."""
    from wenart.reading_check.critic_checks import SYSTEM_TEXT

    content: list = []
    for label in LABELS[:len(q["images"])]:
        content += [{"type": "text", "text": label}, {"type": "image"}]
    content.append({"type": "text", "text": prompt_of(q)})
    return {"id": q["id"], "kind": q["kind"], "images": list(q["images"]),
            "prompt": [{"role": "system", "content": [{"type": "text", "text": SYSTEM_TEXT}]},
                       {"role": "user", "content": content}],
            "completion": [{"role": "assistant", "content": [{"type": "text", "text": answer_json}]}]}


def sample(train_dir: Path, url: str, model: str, out: Path, *, n: int = N_SAMPLES, temperature: float = TEMPERATURE,
           held_out: bool = False, workers: int = 16, deadline: Optional[float] = None) -> dict:
    """Ask every training (or with ``held_out`` every held-out) question ``n`` times; verify; ``out`` (jsonl)."""
    import concurrent.futures as cf
    import time
    import urllib.request

    qs = [q for q in load_questions(Path(train_dir) / "questions.jsonl").values() if bool(q["held_out"]) == held_out]

    def one(q):
        if deadline and time.time() > deadline:
            return {"id": q["id"], "answers": [], "verified": [], "skipped": "deadline"}
        body = {"model": model, "n": n, "temperature": temperature, "max_tokens": MAX_TOKENS, "seed": SEED,
                "messages": messages_of(q, train_dir), "chat_template_kwargs": {"enable_thinking": False}}
        req = urllib.request.Request(RP.chat_url(url), data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                data = json.loads(r.read())
            texts = [c["message"]["content"] or "" for c in data["choices"]]
        except Exception as exc:                                # noqa: BLE001 - a failed call is a result
            return {"id": q["id"], "answers": [], "verified": [], "error": str(exc)[:200]}
        return {"id": q["id"], "kind": q["kind"], "answers": texts, "verified": [verify(q, t) for t in texts]}

    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        res = list(ex.map(one, qs))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        for r in res:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    done = [r for r in res if r.get("verified")]
    right = sum(sum(bool(v) for v in r["verified"]) for r in done)
    total = sum(len(r["verified"]) for r in done)
    return {"questions": len(qs), "answered": len(done), "accuracy": round(right / total, 4) if total else None}


def sft_rows(questions: dict, samples: list, rows_max: int = ROWS_MAX) -> tuple:
    """``(rows, report)`` (pure): rejection sampling (``rl_pilot.keep_question``: neither all right nor all wrong), one
    row per kept training question (its right answer as compact JSON), at most ``rows_max`` rows taken round-robin
    over the classes in sha1 order (the classes balanced)."""
    rep = {"questions": 0, "all_right": 0, "all_wrong": 0, "kept": 0, "rows": 0, "by_class": {}}
    kept: dict = {}
    for s in samples:
        q = questions.get(s.get("id"))
        if q is None or q.get("held_out") or not s.get("verified"):
            continue
        rep["questions"] += 1
        ver = [bool(v) for v in s["verified"]]
        if all(ver):
            rep["all_right"] += 1
            continue
        if not any(ver):
            rep["all_wrong"] += 1
            continue
        rep["kept"] += 1
        kept.setdefault(cls_of(q), []).append(q)
    queues = {c: sorted(v, key=lambda q: _h(q["id"])) for c, v in sorted(kept.items())}
    rows = []
    while len(rows) < rows_max and any(queues.values()):
        for c in list(queues):
            if queues[c] and len(rows) < rows_max:
                q = queues[c].pop(0)
                rows.append(sft_row(q, json.dumps({"answer": q["answer"]})))
                rep["by_class"][c] = rep["by_class"].get(c, 0) + 1
    rep["rows"] = len(rows)
    rep["by_class"] = dict(sorted(rep["by_class"].items()))
    return rows, rep


def _exam_arm(url: str, key: str, out: Path, served: Optional[str], deadline: Optional[float]) -> dict:
    """One exam arm: pilot 1's ``_exam`` with the drawing text (arm ``1``, today's default; the judge with images
    only), no few-shot block."""
    return RP._exam(url, key, out, served=served, fewshot=None, deadline=deadline, arms=("1",))


def phase_sample(train_dir: Path, out: Path, *, key: str = "agent", server_flags: str = "",
                 deadline: Optional[float] = None, exam: bool = True, log=print) -> dict:
    """Pod phase A (the FP8 agent model): the training questions ``N_SAMPLES`` times at ``TEMPERATURE``, the held-out
    questions once at temperature 0, then exam arm (a)."""
    from wenart.run import servers as SV

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rep: dict = {}

    def save():
        (out / "phase_sample.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")

    with SV.server(key, deadline, extra_flags=server_flags) as url:
        model = SV.model_entry(SV.check_models(), key)["id"]
        rep["train"] = sample(train_dir, url, model, out / "samples.jsonl", deadline=deadline)
        log(f"rl_bench: sampled {rep['train']}")
        save()
        rep["held_fp8"] = sample(train_dir, url, model, out / "held_fp8.jsonl", n=1, temperature=0.0, held_out=True,
                                 deadline=deadline)
        log(f"rl_bench: held-out (fp8) {rep['held_fp8']}")
        save()
        if exam:
            rep["exam_fp8"] = _exam_arm(url, key, out / "exam_fp8", None, deadline)
            log(f"rl_bench: exam (a) fp8 {rep['exam_fp8']}")
    save()
    return rep


def phase_exam(train_dir: Path, adapter: Path, out: Path, *, key: str = "bakeoff.bf16", rank: int = 16,
               server_flags: str = "", deadline: Optional[float] = None, log=print) -> dict:
    """Pod phase C: the BF16 base with the LoRA beside it (pilot 1's flags): the held-out questions with the LoRA and
    the base, then exam arms (c) LoRA and (b) base side by side."""
    import concurrent.futures as cf

    from wenart.run import servers as SV

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    flags = f"{server_flags} --enable-lora --max-lora-rank {int(rank)} --lora-modules {RP.LORA_NAME}={adapter}".strip()
    rep: dict = {}

    def save():
        (out / "phase_exam.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")

    with SV.server(key, deadline, extra_flags=flags) as url:
        base = SV.model_entry(SV.check_models(), key)["id"]
        rep["held_lora"] = sample(train_dir, url, RP.LORA_NAME, out / "held_lora.jsonl", n=1, temperature=0.0,
                                  held_out=True, deadline=deadline)
        rep["held_bf16"] = sample(train_dir, url, base, out / "held_bf16.jsonl", n=1, temperature=0.0, held_out=True,
                                  deadline=deadline)
        log(f"rl_bench: held-out lora {rep['held_lora']} base {rep['held_bf16']}")
        save()
        with cf.ThreadPoolExecutor(max_workers=2) as ex:
            fut = {"exam_lora": ex.submit(_exam_arm, url, key, out / "exam_lora", RP.LORA_NAME, deadline),
                   "exam_bf16": ex.submit(_exam_arm, url, key, out / "exam_bf16", None, deadline)}
            for name, f in fut.items():
                try:
                    rep[name] = f.result()
                except Exception as exc:                        # noqa: BLE001 - recorded, the other arm still counts
                    rep[name] = {"error": f"{type(exc).__name__}: {str(exc)[:300]}"}
                log(f"rl_bench: {name} {rep[name]}")
    save()
    return rep


# --- the held-out bench table (CPU) -------------------------------------------------------------------------------------

def held_score(train_dir: Path, answers: dict) -> dict:
    """``{arm: {questions, answered, right, accuracy, errors, errors_flagged, rights, false_alarms, per_kind}}`` (pure
    but for reading): ``answers`` = ``{arm: path of a held-out jsonl}``."""
    qs = load_questions(Path(train_dir) / "questions.jsonl")
    out = {}
    for arm, path in answers.items():
        rows = [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
        st = {"questions": 0, "answered": 0, "right": 0, "errors": 0, "errors_flagged": 0, "rights": 0,
              "false_alarms": 0, "per_kind": {}}
        for r in rows:
            q = qs.get(r["id"])
            if q is None:
                continue
            st["questions"] += 1
            k = st["per_kind"].setdefault(q["kind"], {"questions": 0, "right": 0})
            k["questions"] += 1
            if not r.get("answers"):
                continue
            ans = RP.parse_answer(r["answers"][0])
            st["answered"] += ans is not None
            ok = verify(q, r["answers"][0]) is True
            st["right"] += ok
            k["right"] += ok
            flagged = says_error(q, ans) is True
            if q["error"]:
                st["errors"] += 1
                st["errors_flagged"] += flagged
            else:
                st["rights"] += 1
                st["false_alarms"] += flagged
        st["accuracy"] = round(st["right"] / st["questions"], 4) if st["questions"] else None
        out[arm] = st
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.reading_check rl_bench", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--bench", default=str(BENCH))
    b.add_argument("--work", default=str(WORK))
    b.add_argument("--out", default=str(SET_DIR))
    f = sub.add_parser("filter")
    f.add_argument("--train", required=True)
    f.add_argument("--samples", required=True)
    f.add_argument("--rows-max", type=int, default=ROWS_MAX)
    pa = sub.add_parser("phase-sample")
    pa.add_argument("--train", required=True)
    pa.add_argument("--out", required=True)
    pa.add_argument("--server-flags", default="")
    pa.add_argument("--deadline", type=float, default=None)
    pa.add_argument("--no-exam", action="store_true")
    pc = sub.add_parser("phase-exam")
    pc.add_argument("--train", required=True)
    pc.add_argument("--adapter", required=True)
    pc.add_argument("--out", required=True)
    pc.add_argument("--server-flags", default="")
    pc.add_argument("--deadline", type=float, default=None)
    pc.add_argument("--rank", type=int, default=16)
    hs = sub.add_parser("held-score")
    hs.add_argument("--train", default=str(SET_DIR))
    hs.add_argument("--arm", action="append", default=[], metavar="NAME=JSONL")
    hs.add_argument("--json", default=None)
    args = ap.parse_args(argv)
    if args.cmd == "build":
        print(json.dumps(build(Path(args.out), Path(args.bench), Path(args.work)), indent=1))
        return 0
    if args.cmd == "filter":
        qs = load_questions(Path(args.train) / "questions.jsonl")
        samples = [json.loads(x) for x in Path(args.samples).read_text(encoding="utf-8").splitlines() if x.strip()]
        rows, rep = sft_rows(qs, samples, rows_max=args.rows_max)
        with open(Path(args.train) / "sft.jsonl", "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        (Path(args.train) / "filter.json").write_text(json.dumps(rep, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(rep))
        return 0 if rows else 1
    if args.cmd == "phase-sample":
        print(json.dumps(phase_sample(Path(args.train), Path(args.out), server_flags=args.server_flags,
                                      deadline=args.deadline, exam=not args.no_exam)))
        return 0
    if args.cmd == "phase-exam":
        print(json.dumps(phase_exam(Path(args.train), Path(args.adapter), Path(args.out), rank=args.rank,
                                    server_flags=args.server_flags, deadline=args.deadline)))
        return 0
    res = held_score(Path(args.train), dict(a.split("=", 1) for a in args.arm))
    print(json.dumps(res, indent=1))
    if args.json:
        Path(args.json).write_text(json.dumps(res, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
