"""The dataset bench: converted dataset floors read by the CPU reader and scored per element kind (21 Nov 2026).

What:
- ``pick <geometries.csv> <pick.json> [--floors N]``: varied buildings of Swiss Dwellings (1-4 flats a floor, 60-700
  entities, rooms, doors and windows; a third of the buildings with stairs), 1-4 floors each, about N floors;
- ``convert <geometries.csv> <pick.json> <bench_dir>``: the picked buildings in the pick's order -> projects
  (``swiss_convert``) until 200 floors, orthogonal and angled alike, and ``manifest.json``;
- ``run <bench_dir> <work_dir> [--timeout S]``: each project read on the CPU (``ingest.pipeline.run_project``, no AI)
  in its own process, one at a time, and scored (``score_one``); the debug images are deleted, ``score.json`` kept;
- ``rescore <bench_dir> <work_dir>``: the stored readings scored again;
- ``report <bench_dir> <work_dir> <out_stem>``: the bench score per element kind (recall, precision, F1 over all
  projects; rooms also the share of matched rooms with the right type; levels by id), the mean project total
  (``reading_check.score.total``), the same where the drawing scale was read, per bench class (``orthogonal``,
  ``angled``: walls at an angle, user, 21 Nov 2026), and the error classes, most frequent first, each with an example
  (``<out_stem>.json`` and ``.md``).

Why: a large real-geometry test bench for the reader (user OK, 21 Nov 2026); not part of the gated synthetic set.

How: the truth is the converter's exact truth (``truth.synthetic_truth``), the matching the score's own
(``reading_check.score``: ``match``, ``match_rooms``, ``match_points``, ``match_walls``) after ``align`` (each level
turned and moved onto the truth frame, on the longest wall direction); an error class is a missed or
invented element of a kind, refined by what stands near it (a door read as a window, two rooms read as one, a thin wall
or a parapet missed ...).
"""
from __future__ import annotations

import collections
import csv
import json
import math
import random
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from wenart.reading_check import score as SC
from wenart.reading_check import truth as TR

KINDS = ("levels", "rooms", "walls", "doors", "windows", "stairs")
MIN_ORTHOGONAL = 0.0          # 21 Nov 2026 (user: "include slanted walls in the bench too"): no building is left out


# --- picking and converting -----------------------------------------------------------------------------------------

def pick(csv_path: Path, n_floors: int = 200, seed: int = 20261121) -> dict:
    """``{building_id: [floor_id, ...]}``: about ``n_floors`` floors of varied buildings (the module docstring)."""
    csv.field_size_limit(10 ** 9)
    floors: dict = {}
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            f = floors.setdefault(row["floor_id"], {"b": row["building_id"], "n": 0, "units": set(),
                                                    "sub": collections.Counter()})
            f["n"] += 1
            f["units"].add(row["unit_id"])
            f["sub"][row["entity_subtype"]] += 1
    ok: dict = collections.defaultdict(list)
    for fid, v in floors.items():
        sub = v["sub"]
        rooms = sum(sub.get(k, 0) for k in ("ROOM", "BEDROOM", "LIVING_ROOM", "LIVING_DINING", "KITCHEN", "BATHROOM"))
        if 1 <= len(v["units"]) <= 4 and 60 <= v["n"] <= 700 and rooms >= 3 and sub.get("DOOR", 0) >= 3 \
                and sub.get("WINDOW", 0) >= 2:
            ok[v["b"]].append((fid, sub.get("STAIRS", 0) > 0))
    rng = random.Random(seed)
    with_stairs = sorted(b for b, fl in ok.items() if any(s for _f, s in fl))
    without = sorted(b for b in ok if b not in set(with_stairs))
    rng.shuffle(with_stairs)
    rng.shuffle(without)
    out, n = {}, 0
    while n < n_floors and (with_stairs or without):
        src = with_stairs if (with_stairs and (rng.random() < 0.33 or not without)) else without
        b = src.pop()
        fids = sorted((f for f, _s in ok[b]), key=lambda x: int(x))[:rng.choice([1, 1, 2, 2, 3, 3, 4])]
        out[b] = fids
        n += len(fids)
    return out


def convert(csv_path: Path, picked: dict, bench_dir: Path, target_floors: int = 200) -> list[str]:
    from wenart.datasets import swiss_convert as SCV
    from wenart.datasets import swiss_dwellings as SD
    from wenart.datasets import turkish_profile as TP

    want = {f for fs in picked.values() for f in fs}
    rows = SD.read_rows(csv_path, want)
    profile = TP.load()
    names, skipped, projects, floors = [], [], [], 0
    for bid in picked:                                  # the pick's own (random) order, until ``target_floors``
        if bid not in rows or floors >= target_floors:
            continue
        name = f"swiss-b{bid}"
        try:
            truth = SCV.convert_building(rows[bid], bench_dir, name, profile, min_orthogonal=MIN_ORTHOGONAL)
        except SCV.NotOrthogonal as exc:
            skipped.append({"building_id": bid, "reason": str(exc)})
            continue
        except Exception as exc:                        # noqa: BLE001 - one bad building never stops the bench
            skipped.append({"building_id": bid, "reason": f"conversion failed: {exc}"})
            continue
        names.append(name)
        floors += len(truth["levels"])
        projects.append({"project": name, "building_id": bid, "floor_ids": truth["dataset"]["floor_ids"],
                         "levels": len(truth["levels"]), "style_unit": truth["style"]["unit"],
                         "counts": TR.counts(truth), "bench_class": truth["dataset"]["bench_class"],
                         "angled_share": truth["dataset"]["angled_share"]})
    manifest = {"dataset": SD.DATASET, "source_file": "geometries.csv", "projects": projects,
                "floors": floors, "skipped": skipped, "min_orthogonal": MIN_ORTHOGONAL}
    (Path(bench_dir) / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
                                                  encoding="utf-8")
    return names


# --- reading and scoring ----------------------------------------------------------------------------------------------

def read_one(project_dir: Path, out: Path) -> None:
    from wenart.ingest import pipeline as PL

    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    PL.run_project(Path(project_dir), out, no_ai=True)


def _pairs_by_level(truth: dict, read: dict, kind: str) -> dict:
    out = {}
    for lid, tl in (truth.get("per_level") or {}).items():
        tt = TR.positives(tl.get(kind) or [])
        rr = ((read.get("per_level") or {}).get(lid) or {}).get(kind) or []
        out[lid] = (tt, rr, SC.match_kind(kind, tt, rr))
    return out


def _wall_class(t: dict, rr: list) -> str:
    if t.get("parapet"):
        return "parapet wall missed"
    if any(SC.wall_overlap(t, dict(r, thickness=t.get("thickness"))) is not None for r in rr):
        return "wall read with another thickness"
    if _off_axes(t):
        return "angled wall missed"
    return "thin wall (< 10 cm) missed" if float(t.get("thickness") or 0) < 0.10 else "wall missed"


def _angle(w: dict) -> float:
    return math.degrees(math.atan2(w["end"][1] - w["start"][1], w["end"][0] - w["start"][0])) % 180.0


def _off_axes(w: dict) -> bool:
    a = _angle(w) % 90.0
    return min(a, 90.0 - a) > 2.0


def _extra_wall_class(r: dict, tt: list) -> str:
    """A read wall that matched none: a piece of a drawn wall (on its line), axis-aligned steps along a drawn wall at
    an angle, or a wall on no drawn line."""
    if any(SC.wall_overlap(dict(t, thickness=r.get("thickness")), r) is not None for t in tt):
        return "wall split (a piece of a drawn wall read as a wall of its own)"
    if not _off_axes(r):
        from shapely.geometry import LineString, Point
        mid = Point((r["start"][0] + r["end"][0]) / 2, (r["start"][1] + r["end"][1]) / 2)
        if any(_off_axes(t) and LineString([t["start"], t["end"]]).distance(mid) <= 0.4 for t in tt):
            return "angled wall read as axis-aligned steps"
    return "wall invented (on no drawn wall line)"


def errors(project: str, truth: dict, read: dict) -> list[dict]:
    """The error instances of one reading: ``{class, kind, level, example}`` (the module docstring)."""
    from shapely.geometry import Polygon

    out = []
    t_levels = [lv["id"] for lv in truth.get("levels") or []]
    r_levels = [lv["id"] for lv in read.get("levels") or []]
    for lid in t_levels:
        if lid not in r_levels:
            out.append({"class": "level missing", "kind": "levels", "level": lid, "example": lid})
    for lid in r_levels:
        if lid not in t_levels:
            out.append({"class": "level invented", "kind": "levels", "level": lid, "example": lid})
    # rooms
    for lid, (tt, rr, m) in _pairs_by_level(truth, read, "rooms").items():
        if lid not in r_levels:
            continue
        mt, mr = {i for i, _ in m}, {j for _, j in m}
        rpolys = [Polygon(r["polygon"]).buffer(0) if len(r.get("polygon") or []) >= 3 else None for r in rr]
        for i, t in enumerate(tt):
            if i in mt:
                continue
            tp = Polygon(t["polygon"]).buffer(0)
            cover = [(j, rp.intersection(tp).area / tp.area) for j, rp in enumerate(rpolys) if rp is not None
                     and tp.area > 0 and rp.intersects(tp)]
            best = max(cover, key=lambda q: q[1], default=(None, 0.0))
            if best[1] >= 0.5:
                cls = "rooms merged (two drawn rooms read as one)"
            else:
                cls = f"room missed ({t.get('room_type') or 'other'}{', unlabelled' if not t.get('label') else ''})"
            out.append({"class": cls, "kind": "rooms", "level": lid,
                        "example": f"{t.get('label') or '-'} {t.get('area')} m2 at {t.get('centroid')}"})
        tpolys = [Polygon(t["polygon"]).buffer(0) for t in tt if len(t.get("polygon") or []) >= 3]
        for j, r in enumerate(rr):
            if j in mr:
                continue
            rp = rpolys[j]
            cls = "room invented"
            if rp is not None and rp.area > 0:
                mrr = rp.minimum_rotated_rectangle
                c = list(mrr.exterior.coords) if mrr.geom_type == "Polygon" else []
                width = min(SC._dist(c[0], c[1]), SC._dist(c[1], c[2])) if len(c) >= 3 else 0.0
                hit = [tp for tp in tpolys if tp.intersects(rp) and tp.intersection(rp).area > 0.2 * rp.area]
                if width < 0.35 or rp.area < 1.0:
                    cls = "room invented in a wall cavity or a narrow gap"
                elif hit:
                    cls = "room split (one drawn room read as several)"
            out.append({"class": cls, "kind": "rooms", "level": lid,
                        "example": f"{r.get('label') or '-'} at {r.get('centroid')}"})
        for i, j in m:
            t, r = tt[i], rr[j]
            if TR.norm_label(t.get("label")) != TR.norm_label(r.get("label")):
                out.append({"class": "room label wrong", "kind": "rooms", "level": lid,
                            "example": f"{t.get('label') or '-'} read {r.get('label') or '-'} at {t.get('centroid')}"})
            elif (t.get("room_type") or "other") != (r.get("room_type") or "other"):
                out.append({"class": f"room type wrong ({t.get('room_type')} read {r.get('room_type')})",
                            "kind": "rooms", "level": lid, "example": f"{t.get('label')} at {t.get('centroid')}"})
    # openings
    for kind, other in (("doors", "windows"), ("windows", "doors")):
        pk = _pairs_by_level(truth, read, kind)
        for lid, (tt, rr, m) in pk.items():
            if lid not in r_levels:
                continue
            mt, mr = {i for i, _ in m}, {j for _, j in m}
            rl = (read.get("per_level") or {}).get(lid) or {}
            alt = (rl.get(other) or []) + (rl.get("openings") or [])
            tl = (truth.get("per_level") or {}).get(lid) or {}
            t_alt = TR.positives(tl.get(other) or [])
            for i, t in enumerate(tt):
                if i in mt:
                    continue
                near = [a for a in alt if a.get("center") and SC._dist(a["center"], t["center"]) <= SC.OPENING_CENTER_M]
                cls = (f"{kind[:-1]} read as {near[0].get('type') or 'opening'}" if near else f"{kind[:-1]} missed")
                out.append({"class": cls, "kind": kind, "level": lid,
                            "example": f"{t.get('id')} {t.get('width')} m at {t.get('center')}"})
            for j, r in enumerate(rr):
                if j in mr or not r.get("center"):
                    continue
                if any(SC._dist(a["center"], r["center"]) <= SC.OPENING_CENTER_M for a in t_alt if a.get("center")):
                    continue                                  # counted on the other kind's side
                out.append({"class": f"{kind[:-1]} invented", "kind": kind, "level": lid,
                            "example": f"{r.get('width')} m at {r.get('center')}"})
    # walls and stairs
    for lid, (tt, rr, m) in _pairs_by_level(truth, read, "walls").items():
        if lid not in r_levels:
            continue
        mt, mr = {i for i, _ in m}, {j for _, j in m}
        for i, t in enumerate(tt):
            if i not in mt:
                out.append({"class": _wall_class(t, rr), "kind": "walls", "level": lid,
                            "example": f"{t.get('id')} {t.get('start')}-{t.get('end')} t={t.get('thickness')}"})
        for j, r in enumerate(rr):
            if j not in mr:
                out.append({"class": _extra_wall_class(r, tt), "kind": "walls", "level": lid,
                            "example": f"{r.get('start')}-{r.get('end')} t={r.get('thickness')}"})
    for lid, (tt, rr, m) in _pairs_by_level(truth, read, "stairs").items():
        if lid not in r_levels:
            continue
        mt, mr = {i for i, _ in m}, {j for _, j in m}
        out += [{"class": "stair missed", "kind": "stairs", "level": lid, "example": f"at {t.get('center')}"}
                for i, t in enumerate(tt) if i not in mt]
        out += [{"class": "stair invented", "kind": "stairs", "level": lid, "example": f"at {r.get('center')}"}
                for j, r in enumerate(rr) if j not in mr]
    for e in out:
        e["project"] = project
    return out


def _shift_level(rl: dict, dx: float, dy: float, rot: float = 0.0) -> dict:
    """A level of a truth-shaped reading turned by ``rot`` degrees about the origin, then moved by (-dx, -dy) (every
    point the matching reads)."""
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def mv(p):
        return [c * p[0] - s_ * p[1] - dx, s_ * p[0] + c * p[1] - dy] if p else p

    out = {}
    for kind, items in rl.items():
        moved = []
        for e in items:
            e = dict(e)
            for key in ("center", "centroid", "start", "end"):
                if e.get(key):
                    e[key] = mv(e[key])
            if e.get("polygon"):
                e["polygon"] = [mv(q) for q in e["polygon"]]
            moved.append(e)
        out[kind] = moved
    return out


def _wall_min(rl: dict) -> Optional[tuple]:
    pts = [(min(w["start"][0], w["end"][0]) - (w.get("thickness") or 0) / 2,
            min(w["start"][1], w["end"][1]) - (w.get("thickness") or 0) / 2) for w in rl.get("walls") or []]
    return (min(p[0] for p in pts), min(p[1] for p in pts)) if pts else None


def _longest_dir(rl: dict) -> Optional[float]:
    """The direction (degrees in [0, 180)) of the longest wall of a level."""
    walls = [w for w in rl.get("walls") or [] if w.get("start") and w.get("end")]
    if not walls:
        return None
    w = max(walls, key=lambda q: SC._dist(q["start"], q["end"]))
    return math.degrees(math.atan2(w["end"][1] - w["start"][1], w["end"][0] - w["start"][0])) % 180.0


def _matches(tl: dict, rl: dict) -> int:
    return sum(len(SC.match_kind(k, TR.positives(tl.get(k) or []), rl.get(k) or []))
               for k in ("walls", "doors", "windows"))


def align(truth: dict, read: dict) -> tuple[dict, dict]:
    """The reading with each level moved onto the truth frame by the turn and shift that match most walls, doors and
    windows, and the moves ``{level: {"shift_m", "rot_deg"}}`` (only those over 5 cm or 0.5 degrees). Turns: none and
    the one that lays the reading's longest wall on the truth's longest wall direction (a reader may straighten a
    non-orthogonal plan on another wall); shifts: none, the walls' min-corner difference of the level after the turn,
    the first level's move. The reader's frame is the min corner of the reference level's outer walls; a missed parapet
    or a level registered elsewhere moves every element of it, which the per-element numbers should not count again
    (``frame offset`` is its own error class)."""
    out = dict(read, per_level=dict(read.get("per_level") or {}))
    moves, first = {}, None
    for lid, tl in (truth.get("per_level") or {}).items():
        rl = out["per_level"].get(lid)
        if not rl:
            continue
        rots = [0.0]
        td, rd = _longest_dir(tl), _longest_dir(rl)
        if td is not None and rd is not None:
            d = (td - rd + 90.0) % 180.0 - 90.0
            if abs(d) > 0.5:
                rots.append(round(d, 3))
        cands = [(0.0, 0.0, 0.0)] + ([first] if first else [])
        tm = _wall_min(tl)
        for rot in rots:
            rm = _wall_min(_shift_level(rl, 0.0, 0.0, rot))
            if tm and rm:
                cands.append((rm[0] - tm[0], rm[1] - tm[1], rot))
            elif rot:
                cands.append((0.0, 0.0, rot))
        best = max(cands, key=lambda m: (_matches(tl, _shift_level(rl, *m)), -abs(m[2]), -math.hypot(m[0], m[1])))
        moved = math.hypot(best[0], best[1]) > 0.05 or abs(best[2]) > 0.5
        if moved and _matches(tl, _shift_level(rl, *best)) > _matches(tl, rl):
            out["per_level"][lid] = _shift_level(rl, *best)
            moves[lid] = {"shift_m": [round(best[0], 3), round(best[1], 3)], "rot_deg": best[2]}
            first = first or best
        else:
            first = first or (0.0, 0.0, 0.0)
    return out, moves


def score_one(project_dir: Path, read_dir: Path) -> dict:
    """The numbers of one reading against its truth: ``reading_check.score.match`` per kind after ``align`` (the
    unaligned total kept), the room types, the errors."""
    name = Path(project_dir).name
    path = Path(project_dir) / "truth" / "reading_truth.json"
    truth = TR.synthetic_truth(name, path)
    meta = json.loads(path.read_text(encoding="utf-8"))          # the dataset and style fields synthetic_truth drops
    truth["dataset"], truth["style"] = meta.get("dataset") or {}, meta.get("style") or {}
    b = json.loads((Path(read_dir) / "building.json").read_text(encoding="utf-8"))
    raw = TR.extract(b, project=name)
    read, shifts = align(truth, raw)
    res = SC.match(truth, read, b)
    res["total_unaligned"] = SC.match(truth, raw, b)["total"]
    res["frame_moves"] = shifts
    res["bench_class"] = (truth.get("dataset") or {}).get("bench_class") or "orthogonal"
    typed = right = 0
    for lid, (tt, rr, m) in _pairs_by_level(truth, read, "rooms").items():
        for i, j in m:
            typed += 1
            right += (tt[i].get("room_type") or "other") == (rr[j].get("room_type") or "other")
    res["room_types"] = {"matched": typed, "right": right, "share": round(right / typed, 4) if typed else None}
    n_walls = sum(len(lv.get("walls") or []) for lv in (read.get("per_level") or {}).values())
    if not n_walls:
        st = truth.get("style") or {}
        res["errors"] = [{"class": "floor not read: drawing scale not found or misread", "kind": "levels",
                          "level": lv["id"], "project": name,
                          "example": f"unit {st.get('unit')}, $INSUNITS {st.get('insunits')}, dimensions "
                                     f"{'as DIMENSION entities' if st.get('dims_as_entities') else 'exploded'}"}
                         for lv in truth.get("levels") or []]
        res["nothing_read"] = True
    else:
        res["errors"] = errors(name, truth, read) + [
            {"class": "frame offset (a level read in another origin or turned)", "kind": "levels", "level": lid,
             "project": name, "example": f"shift {s['shift_m']} m, turn {s['rot_deg']} deg"}
            for lid, s in shifts.items()]
    for e in res["errors"]:
        e["bench_class"] = res["bench_class"]
    res["status"] = (b.get("project") or {}).get("status") or b.get("status")
    return res


def run(bench_dir: Path, work: Path, timeout: int = 900, only: Optional[list] = None) -> None:
    work.mkdir(parents=True, exist_ok=True)
    projects = sorted(p for p in Path(bench_dir).iterdir() if (p / "truth" / "reading_truth.json").is_file())
    for p in projects:
        if only and p.name not in only:
            continue
        out = work / p.name
        if (out / "bench_score.json").is_file():
            continue
        t0 = time.time()
        try:
            subprocess.run([sys.executable, "-m", "wenart.datasets.bench", "read", str(p), str(out)], check=True,
                           timeout=timeout, capture_output=True)
            res = score_one(p, out)
        except (subprocess.SubprocessError, OSError, ValueError, KeyError) as exc:
            out.mkdir(parents=True, exist_ok=True)
            res = {"error": f"{type(exc).__name__}: {str(exc)[-300:]}"}
        res["seconds"] = round(time.time() - t0, 1)
        for sub in ("debug", "sheets_debug"):
            shutil.rmtree(out / sub, ignore_errors=True)
        (out / "bench_score.json").write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(f"{p.name}: {res.get('total', res.get('error'))} ({res['seconds']} s)", flush=True)


# --- the report -------------------------------------------------------------------------------------------------------

def aggregate(results: dict) -> dict:
    sums = {k: [0, 0, 0] for k in KINDS}
    types = [0, 0]
    totals, errs, failed = [], collections.Counter(), []
    examples: dict = {}
    for name, res in sorted(results.items()):
        if "error" in res:
            failed.append({"project": name, "error": res["error"]})
            continue
        totals.append(res["total"])
        for k in KINDS:
            st = res.get(k) or {}
            sums[k][0] += st.get("truth", 0)
            sums[k][1] += st.get("read", 0)
            sums[k][2] += st.get("matched", 0)
        types[0] += res["room_types"]["matched"]
        types[1] += res["room_types"]["right"]
        for e in res.get("errors") or []:
            errs[e["class"]] += 1
            if e["class"] not in examples or (examples[e["class"]].get("bench_class") == "angled"
                                              and e.get("bench_class") != "angled"):
                examples[e["class"]] = e              # an orthogonal example where the class has one
    per_kind = {k: SC._stats(nt, nr, nm) for k, (nt, nr, nm) in sums.items()}
    per_kind["room_types"] = {"matched": types[0], "right": types[1],
                              "share": round(types[1] / types[0], 4) if types[0] else None}
    return {"projects": len(results), "scored": len(totals), "failed": failed,
            "floors": sums["levels"][0], "mean_total": round(sum(totals) / len(totals), 2) if totals else None,
            "per_kind": per_kind,
            "error_classes": [{"class": c, "count": n, "example": examples[c]} for c, n in errs.most_common()]}


def report(bench_dir: Path, work: Path, out_stem: Path) -> dict:
    results = {}
    for p in sorted(Path(work).iterdir()):
        f = p / "bench_score.json"
        if f.is_file():
            results[p.name] = json.loads(f.read_text(encoding="utf-8"))
    agg = aggregate(results)
    ok = {n: r for n, r in results.items() if "error" not in r and not r.get("nothing_read")}
    read = aggregate(ok)
    agg["scale_read"] = {k: read[k] for k in ("projects", "floors", "mean_total", "per_kind")}
    classes = {c: aggregate({n: r for n, r in ok.items() if (r.get("bench_class") or "orthogonal") == c})
               for c in ("orthogonal", "angled")}
    agg["classes_scale_read"] = {c: {k: a[k] for k in ("projects", "floors", "mean_total", "per_kind")}
                                 for c, a in classes.items()}
    agg["classes_all"] = {c: sum(1 for r in results.values() if (r.get("bench_class") or "orthogonal") == c)
                          for c in ("orthogonal", "angled")}
    agg["per_project"] = {n: (r.get("total") if "error" not in r else None) for n, r in results.items()}
    out_stem.parent.mkdir(parents=True, exist_ok=True)
    out_stem.with_suffix(".json").write_text(json.dumps(agg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    co, ca = classes["orthogonal"], classes["angled"]
    lines = ["# Dataset bench: Swiss Dwellings in a Turkish drafting style", "",
             f"{agg['projects']} projects ({agg['classes_all']['orthogonal']} orthogonal, {agg['classes_all']['angled']} "
             f"with angled walls), {agg['floors']} floors, {agg['scored']} scored, {len(agg['failed'])} failed. Mean "
             f"project total {agg['mean_total']} (all); where the drawing scale was read: {read['mean_total']} "
             f"({read['projects']} projects, {read['floors']} floors), orthogonal {co['mean_total']} ({co['projects']} "
             f"projects), angled {ca['mean_total']} ({ca['projects']} projects).", "",
             "| kind | truth | read | matched | recall | precision | F1 all | F1 scale read | F1 orthogonal | "
             "F1 angled |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k in KINDS:
        s, s2 = agg["per_kind"][k], read["per_kind"][k]
        lines.append(f"| {k} | {s['truth']} | {s['read']} | {s['matched']} | {s['recall']:.3f} | "
                     f"{s['precision']:.3f} | {s['f1']:.3f} | {s2['f1']:.3f} | {co['per_kind'][k]['f1']:.3f} | "
                     f"{ca['per_kind'][k]['f1']:.3f} |")
    rt, rt2 = agg["per_kind"]["room_types"], read["per_kind"]["room_types"]
    lines += [f"| room types (of matched rooms) | {rt['matched']} | | {rt['right']} | | | {rt['share']} | "
              f"{rt2['share']} | {co['per_kind']['room_types']['share']} | {ca['per_kind']['room_types']['share']} |",
              "", "The class columns count the projects whose drawing scale was read (a floor not read says "
              "nothing about walls at an angle).", "",
              "## Error classes", "", "| class | count | example |", "|---|---|---|"]
    for e in agg["error_classes"][:25]:
        ex = e["example"]
        lines.append(f"| {e['class']} | {e['count']} | {ex['project']} {ex['level']}: {ex['example']} |")
    out_stem.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return agg


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
    if cmd == "pick":
        n = int(argv[argv.index("--floors") + 1]) if "--floors" in argv else 200
        picked = pick(Path(argv[1]), n)
        Path(argv[2]).write_text(json.dumps(picked, indent=0) + "\n", encoding="utf-8")
        print(f"{len(picked)} buildings, {sum(len(v) for v in picked.values())} floors")
    elif cmd == "convert":
        picked = json.loads(Path(argv[2]).read_text(encoding="utf-8"))
        names = convert(Path(argv[1]), picked, Path(argv[3]))
        print(f"{len(names)} projects")
    elif cmd == "read":
        read_one(Path(argv[1]), Path(argv[2]))
    elif cmd == "run":
        timeout = int(argv[argv.index("--timeout") + 1]) if "--timeout" in argv else 900
        only = argv[argv.index("--only") + 1].split(",") if "--only" in argv else None
        run(Path(argv[1]), Path(argv[2]), timeout, only)
    elif cmd == "rescore":                              # the stored readings scored again (a scoring change)
        for f in sorted(Path(argv[2]).glob("*/bench_score.json")):
            old = json.loads(f.read_text(encoding="utf-8"))
            if "error" in old or not (f.parent / "building.json").is_file():
                continue
            res = score_one(Path(argv[1]) / f.parent.name, f.parent)
            res["seconds"] = old.get("seconds")
            f.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    elif cmd == "report":
        agg = report(Path(argv[1]), Path(argv[2]), Path(argv[3]))
        print(json.dumps({k: agg[k] for k in ("projects", "floors", "mean_total")}))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
