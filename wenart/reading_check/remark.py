"""Capture of the user's review remarks as correction records, each with a small crop image of the place.

What: ``python -m wenart.reading_check.remark add|list|show|redo``. ``add`` appends one record to
``results/reading_corrections.jsonl`` (the format of ``truth.py`` is kept; only the optional fields
``element_ids``, ``truth_action``, ``place_note`` and ``history`` are new) and, when the reading folder is given,
draws a crop ``results/reading_corrections/crops/<id>.png`` of the place from ``building.json`` (``--drawing``: with
the drawing's own strokes over it). A wall, door, window, opening, room or stair remark needs ``--place``,
``--element`` or ``--place-note`` (review of 5 Nov 2026).

Why (5 Nov 2026, Milestone 14, R9): the user keeps reviewing the reading sheets in detail ("possibly I may need
to continue detailed reviews for some time more"). His free words ("This wall do not exist") used to end as text in
docs/progress.md. Now every remark becomes a record at once, and the crop shown back in the reply lets him catch a
misplaced record in the same exchange.

How: pure functions (``next_id``, ``build_record``, ``element_place``, ``draw_crop``) and thin file code around
them. Every path is a parameter, so tests never touch the real corrections file.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import json
import sys
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[2]
CORRECTIONS_PATH = REPO / "results" / "reading_corrections.jsonl"
CROP_DIR = REPO / "results" / "reading_corrections" / "crops"
PROJECTS_DIR = REPO / "projects"
SOURCE_USER = "user_review"
STATUS_ACCEPTED = "accepted"
NO_LESSON_NOTE = "no lesson yet: the general rule for this remark is still to be written"   # truth.correction_errors needs a note when lesson is null
ELEMENT_KINDS = ("wall", "opening", "door", "window", "room", "stair", "level", "label", "region", "roof", "site",
                 "other")
PLACEABLE_KINDS = ("wall", "door", "window", "opening", "room", "stair")   # as truth.PLACEABLE_KINDS
TRUTH_OPS = ("add", "remove", "retype", "move")
ELEMENT_LISTS = ("walls", "openings", "rooms", "furniture")
CROP_SIZE_M = 6.0                 # side of the window around the place, building metres
CROP_PX = 600
CROP_MARGIN_M = 0.5               # margin around the whole level when there is no place
NEAREST_IDS = 8
COLOURS = {"wall": "#9a9a9a", "door": "#2e9e4f", "window": "#2b6fd6", "mark": "#d62020", "room": "#444444"}


def today() -> str:
    return _dt.date.today().isoformat()


def next_id(records: Iterable[dict]) -> str:
    """The next free id C0001, C0002, ... (pure)."""
    top = 0
    for r in records:
        rid = str(r.get("id", ""))
        if rid[:1] == "C" and rid[1:].isdigit():
            top = max(top, int(rid[1:]))
    return f"C{top + 1:04d}"


def parse_place(text: str) -> dict:
    x, y = (float(v) for v in text.split(","))
    return {"x": round(x, 3), "y": round(y, 3)}


def find_element(building: dict, element_id: str):
    for lst in ELEMENT_LISTS:
        for el in building.get(lst) or []:
            if el.get("id") == element_id:
                return lst, el
    return None


def nearest_ids(building: dict, element_id: str, level: str | None) -> list[str]:
    """Ids of the same level that look most like the wrong one (pure; for the refusal message)."""
    pool = [el["id"] for lst in ELEMENT_LISTS for el in building.get(lst) or []
            if el.get("id") and (level is None or el.get("level_id") == level)]
    return difflib.get_close_matches(element_id, pool, n=NEAREST_IDS, cutoff=0.0)


def element_place(kind: str, el: dict) -> dict | None:
    """The place of an element (pure): a wall's midpoint, an opening's centre, a room's centroid, a piece's centre."""
    pt = None
    if kind == "walls" and el.get("start") and el.get("end"):
        pt = [(el["start"][0] + el["end"][0]) / 2, (el["start"][1] + el["end"][1]) / 2]
    elif kind == "openings" and el.get("center"):
        pt = el["center"]
    elif kind == "rooms" and el.get("polygon"):
        pts = el["polygon"]
        pt = [sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)]
        a = c = d = 0.0                       # area centroid when the polygon allows it
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            cr = x0 * y1 - x1 * y0
            a += cr
            c += (x0 + x1) * cr
            d += (y0 + y1) * cr
        if abs(a) > 1e-9:
            pt = [c / (3 * a), d / (3 * a)]
    elif kind == "furniture" and (el.get("footprint") or {}).get("center"):
        pt = el["footprint"]["center"]
    return None if pt is None else {"x": round(pt[0], 3), "y": round(pt[1], 3)}


def validate_truth_action(action) -> str | None:
    """None when fine, else the reason (pure)."""
    if not isinstance(action, dict):
        return "truth_action must be a JSON object"
    if action.get("op") not in TRUTH_OPS:
        return f"truth_action needs an 'op' of {', '.join(TRUTH_OPS)}"
    return None


def build_record(records: list[dict], *, project: str, text: str, level: str | None = None,
                 place: dict | None = None, element_ids: list[str] | None = None, kind: str = "other",
                 reader_answer: str = "", right_answer: str = "", lesson: str | None = None, note: str | None = None,
                 truth_action: dict | None = None, building: dict | None = None,
                 projects: Iterable[str] | None = None, lesson_ids: Iterable[str] | None = None,
                 date: str | None = None, place_note: str | None = None) -> dict:
    """One correction record (pure). Raises ValueError with the reason when something is wrong. 5 Nov 2026 (review):
    a remark about a placeable element (``PLACEABLE_KINDS``: wall, door, window, opening, room, stair) is refused
    without a place (``--place``, or ``--element`` whose place is taken) or a ``place_note`` saying why it has none,
    so every remark joins the truth and the ranker's labels at capture (``truth.correction_errors`` checks the
    same)."""
    if projects is not None and project not in set(projects):
        raise ValueError(f"project {project!r} not in projects/")
    if kind not in ELEMENT_KINDS:
        raise ValueError(f"kind {kind!r} is not one of {', '.join(ELEMENT_KINDS)}")
    if lesson is not None and lesson_ids is not None and lesson not in set(lesson_ids):
        raise ValueError(f"lesson {lesson} not in the lessons file")
    if truth_action is not None:
        why = validate_truth_action(truth_action)
        if why:
            raise ValueError(why)
    if not text.strip():
        raise ValueError("the user's words are empty")
    ids = list(element_ids or [])
    if ids and building is not None:
        for eid in ids:
            hit = find_element(building, eid)
            if hit is None:
                raise ValueError(f"element {eid} not in building.json; nearest on {level or 'all levels'}: "
                                 + ", ".join(nearest_ids(building, eid, level)))
            if place is None:
                place = element_place(*hit)
            if level is None:
                level = hit[1].get("level_id")
    note_place = (place_note or "").strip()
    if kind in PLACEABLE_KINDS and place is None and not note_place:
        raise ValueError(f"a {kind} remark needs its place: give --place x,y (building metres) or --element <id> "
                         f"(its place is taken), or --place-note saying why it has none")
    rec = {"id": next_id(records), "date": date or today(), "project": project, "level": level, "place": place,
           "element_kind": kind, "reader_answer": reader_answer, "right_answer": right_answer,
           "user_words": text, "lesson": lesson, "source": SOURCE_USER, "status": STATUS_ACCEPTED}
    if note_place:
        rec["place_note"] = note_place
    if ids:
        rec["element_ids"] = ids
    if truth_action is not None:
        rec["truth_action"] = truth_action
    if note or lesson is None:
        rec["note"] = note or NO_LESSON_NOTE
    return rec


def draw_crop(building: dict, level_id: str | None, place: dict | None, element_ids: list[str], path: Path,
              lines: list | None = None) -> Path:
    """Draw the crop (matplotlib, headless): walls grey, doors green, windows blue, room labels, the named
    elements red, the place a red cross, a 1 m scale bar. 6 x 6 m around the place, else the whole level.
    ``lines`` (``drawing_lines``): the drawing's own strokes in building metres, drawn thin black over the model,
    so the user sees the jambs, swings and frames the place was taken from."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    named = set(element_ids or [])
    on = lambda lst: [e for e in building.get(lst) or [] if level_id is None or e.get("level_id") == level_id]
    walls, openings, rooms = on("walls"), on("openings"), on("rooms")
    if place:
        h = CROP_SIZE_M / 2
        x0, x1, y0, y1 = place["x"] - h, place["x"] + h, place["y"] - h, place["y"] + h
    else:
        xs = [p for w in walls for p in (w["start"][0], w["end"][0])] + [q[0] for r in rooms for q in r.get("polygon", [])]
        ys = [p for w in walls for p in (w["start"][1], w["end"][1])] + [q[1] for r in rooms for q in r.get("polygon", [])]
        if not xs:
            xs, ys = [0.0, CROP_SIZE_M], [0.0, CROP_SIZE_M]
        x0, x1 = min(xs) - CROP_MARGIN_M, max(xs) + CROP_MARGIN_M
        y0, y1 = min(ys) - CROP_MARGIN_M, max(ys) + CROP_MARGIN_M
    span = max(x1 - x0, y1 - y0)
    fig, ax = plt.subplots(figsize=(CROP_PX / 100, CROP_PX / 100), dpi=100)
    ax.set_xlim(x0, x0 + span)
    ax.set_ylim(y0, y0 + span)
    ax.set_aspect("equal")
    px_per_m = CROP_PX * 0.80 / span                       # the axes fill about 80 % of the figure
    lw = lambda m: max(1.0, m * px_per_m * 72 / 100)       # a width in metres as line points
    for w in walls:
        red = w.get("id") in named
        ax.plot([w["start"][0], w["end"][0]], [w["start"][1], w["end"][1]], solid_capstyle="butt",
                color=COLOURS["mark"] if red else COLOURS["wall"], lw=lw(w.get("thickness") or 0.2),
                zorder=3 if red else 2)
    for o in openings:
        c, half = o.get("center"), (o.get("width") or 0.9) / 2
        if not c:
            continue
        w_ = next((w for w in walls if w.get("id") == o.get("wall_id")), None)
        dx, dy = 1.0, 0.0
        if w_:
            ex, ey = w_["end"][0] - w_["start"][0], w_["end"][1] - w_["start"][1]
            n = (ex * ex + ey * ey) ** 0.5 or 1.0
            dx, dy = ex / n, ey / n
        is_win = o.get("type") == "window"
        col = COLOURS["mark"] if o.get("id") in named else (COLOURS["window"] if is_win else COLOURS["door"])
        ax.plot([c[0] - dx * half, c[0] + dx * half], [c[1] - dy * half, c[1] + dy * half], solid_capstyle="butt",
                color=col, lw=lw(0.12 if is_win else 0.08) + 1, zorder=4)
    for r in rooms:
        c = element_place("rooms", r)
        if c:
            ax.text(c["x"], c["y"], str(r.get("label") or r.get("id")), fontsize=7, ha="center", va="center",
                    color=COLOURS["mark"] if r.get("id") in named else COLOURS["room"], zorder=5, clip_on=True)
    for (ax0, ay0), (ax1, ay1) in lines or []:
        ax.plot([ax0, ax1], [ay0, ay1], color="black", lw=0.6, zorder=5.5)
    if place:
        ax.plot([place["x"]], [place["y"]], marker="+", ms=26, mew=5, color="white", zorder=6)   # shows on red
        ax.plot([place["x"]], [place["y"]], marker="+", ms=22, mew=2, color=COLOURS["mark"], zorder=7)
    bx, by = x0 + 0.05 * span, y0 + 0.05 * span                # 1 m scale bar
    ax.plot([bx, bx + 1], [by, by], color="black", lw=3, zorder=6)
    ax.text(bx + 0.5, by + 0.03 * span, "1 m", ha="center", fontsize=8, zorder=6)
    ax.set_title(f"{Path(path).stem} {(building.get('project') or {}).get('id', '')} {level_id or 'all levels'}",
                 fontsize=10)
    ax.tick_params(labelsize=7)
    ax.grid(True, lw=0.3, alpha=0.4)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


NOTATION_LAYER_WORDS = ("OLCU", "OLÇÜ", "DIM", "AKS", "AXIS", "GRID")


def drawing_lines(out, building: dict, level_id: str | None, place: dict | None, size: float = CROP_SIZE_M) -> list:
    """The drawing's strokes around ``place`` on ``level_id`` in building metres: the LINE, LWPOLYLINE and ARC
    entities of the reading's converted DXF (``<out>/converted/*.dxf``) mapped by the level's page transform
    (``building["documents"][*]["pages"]``, the one the model used), dimensions and grid layers left out. Empty when
    the reading has no DXF or the level no page transform."""
    import math
    out = Path(out)
    tf = next((pg.get("transform_to_building") for d in building.get("documents") or []
               for pg in d.get("pages") or [] if pg.get("level_id") == level_id and pg.get("transform_to_building")),
              None)
    dxfs = sorted((out / "converted").glob("*.dxf")) if (out / "converted").is_dir() else []
    if not tf or not dxfs or not place:
        return []
    import ezdxf
    a, b, c, d, e, f = tf
    to_b = lambda x, y: (a * x + b * y + c, d * x + e * y + f)
    h = size / 2 + 0.5
    near = lambda q: abs(q[0] - place["x"]) <= h and abs(q[1] - place["y"]) <= h
    segs = []
    for ent in ezdxf.readfile(str(dxfs[0])).modelspace():
        t = ent.dxftype()
        layer = (ent.dxf.get("layer") or "").upper()
        if t.endswith("DIMENSION") or any(w in layer for w in NOTATION_LAYER_WORDS):
            continue
        try:
            if t == "LINE":
                pts = [to_b(ent.dxf.start.x, ent.dxf.start.y), to_b(ent.dxf.end.x, ent.dxf.end.y)]
            elif t == "LWPOLYLINE":
                pts = [to_b(x, y) for x, y in ent.get_points("xy")]
            elif t == "ARC":
                r, a0, a1 = ent.dxf.radius, ent.dxf.start_angle, ent.dxf.end_angle
                a1 = a1 + 360 if a1 < a0 else a1
                pts = [to_b(ent.dxf.center.x + r * math.cos(math.radians(a0 + (a1 - a0) * i / 12)),
                            ent.dxf.center.y + r * math.sin(math.radians(a0 + (a1 - a0) * i / 12)))
                       for i in range(13)]
            else:
                continue
        except Exception:  # noqa: BLE001 - an entity without points: left out
            continue
        if any(near(q) for q in pts):
            segs += list(zip(pts, pts[1:]))
    return segs


# ---- file code -------------------------------------------------------------------------------------------------
def load(path: Path) -> list[dict]:
    path = Path(path)
    if not path.is_file():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def save(path: Path, records: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")


def load_building(out) -> dict:
    out = Path(out)
    f = out / "building.json" if out.is_dir() else out
    return json.loads(f.read_text(encoding="utf-8"))


def lesson_ids() -> list[str]:
    f = REPO / "wenart" / "blender" / "architect_lessons.json"
    return [l["id"] for l in json.loads(f.read_text(encoding="utf-8")).get("lessons", [])]


def project_names() -> list[str]:
    return sorted(p.name for p in PROJECTS_DIR.iterdir() if p.is_dir()) if PROJECTS_DIR.is_dir() else []


def add(args, corrections: Path = CORRECTIONS_PATH, crop_dir: Path = CROP_DIR):
    records = load(corrections)
    building = load_building(args.out) if args.out else None
    action = json.loads(args.truth_action) if args.truth_action else None
    rec = build_record(records, project=args.project, text=args.text, level=args.level,
                       place=parse_place(args.place) if args.place else None, element_ids=args.element or [],
                       kind=args.kind, reader_answer=args.reader_answer, right_answer=args.right_answer,
                       lesson=args.lesson, note=getattr(args, "note", None), truth_action=action, building=building, projects=project_names(),
                       lesson_ids=lesson_ids(), place_note=getattr(args, "place_note", None))
    crop = None
    if building is not None:
        lines = (drawing_lines(args.out, building, rec["level"], rec["place"])
                 if getattr(args, "drawing", False) else None)
        crop = draw_crop(building, rec["level"], rec["place"], rec.get("reader_ids") or rec.get("element_ids", []),
                         Path(crop_dir) / f"{rec['id']}.png", lines=lines)
    save(corrections, records + [rec])
    return rec, crop


def redo(rid: str, place: dict, corrections: Path = CORRECTIONS_PATH, crop_dir: Path = CROP_DIR,
         building: dict | None = None, date: str | None = None, lines: list | None = None):
    records = load(corrections)
    rec = next((r for r in records if r.get("id") == rid), None)
    if rec is None:
        raise ValueError(f"no record {rid}")
    rec.setdefault("history", []).append({"date": date or today(), "old_place": rec.get("place")})
    rec["place"] = place
    crop = None
    if building is not None:
        # the reading's ids (``reader_ids``, 5 Nov 2026) name its elements; ``element_ids`` may be the truth's ids
        crop = draw_crop(building, rec.get("level"), place, rec.get("reader_ids") or rec.get("element_ids", []),
                         Path(crop_dir) / f"{rid}.png", lines=lines)
    save(corrections, records)
    return rec, crop


def select(records: list[dict], project: str | None = None, since: str | None = None) -> list[dict]:
    return [r for r in records
            if (not project or r.get("project") == project) and (not since or r.get("date", "") >= since)]


def table(records: list[dict]) -> str:
    rows = [f"{r['id']}  {r.get('date')}  {r.get('project')}  {r.get('level') or '-'}  {r.get('element_kind')}  "
            f"{r.get('lesson') or '-'}  {(r.get('user_words') or '')[:60]}" for r in records]
    return "\n".join(["id     date        project  level  kind  lesson  words"] + rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="wenart.reading_check.remark")
    sub = ap.add_subparsers(dest="action", required=True)
    a = sub.add_parser("add")
    a.add_argument("--project", required=True)
    a.add_argument("--text", required=True)
    a.add_argument("--level")
    a.add_argument("--place")
    a.add_argument("--element", action="append")
    a.add_argument("--kind", default="other", choices=ELEMENT_KINDS)
    a.add_argument("--reader-answer", default="")
    a.add_argument("--right-answer", default="")
    a.add_argument("--lesson")
    a.add_argument("--note", help="why there is no lesson, or what the record needs")
    a.add_argument("--place-note", help="how the place was found, or why a wall/door/window/opening/room/stair "
                                        "remark has none (needed when there is neither --place nor --element)")
    a.add_argument("--out")
    a.add_argument("--drawing", action="store_true", help="draw the drawing's own strokes in the crop (with --out)")
    a.add_argument("--truth-action")
    ls = sub.add_parser("list")
    ls.add_argument("--project")
    ls.add_argument("--since")
    sh = sub.add_parser("show")
    sh.add_argument("id")
    rd = sub.add_parser("redo")
    rd.add_argument("id")
    rd.add_argument("--place", required=True)
    rd.add_argument("--out")
    rd.add_argument("--drawing", action="store_true", help="draw the drawing's own strokes in the crop (with --out)")
    args = ap.parse_args(argv)
    try:
        if args.action == "add":
            rec, crop = add(args)
            print(json.dumps(rec, ensure_ascii=False))
            print(f"crop: {crop}" if crop else "crop: none (no --out)")
        elif args.action == "list":
            print(table(select(load(CORRECTIONS_PATH), args.project, args.since)))
        elif args.action == "show":
            rec = next((r for r in load(CORRECTIONS_PATH) if r["id"] == args.id), None)
            if rec is None:
                raise ValueError(f"no record {args.id}")
            c = CROP_DIR / f"{args.id}.png"
            print(json.dumps(rec, ensure_ascii=False))
            print(f"crop: {c}" if c.is_file() else "crop: none")
        else:
            building = load_building(args.out) if args.out else None
            lines = None
            if building is not None and args.drawing:
                level = next((r.get("level") for r in load(CORRECTIONS_PATH) if r.get("id") == args.id), None)
                lines = drawing_lines(args.out, building, level, parse_place(args.place))
            rec, crop = redo(args.id, parse_place(args.place), building=building, lines=lines)
            print(json.dumps(rec, ensure_ascii=False))
            print(f"crop: {crop}" if crop else "crop: not redrawn (no --out)")
    except (ValueError, json.JSONDecodeError) as e:
        print(f"remark: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
