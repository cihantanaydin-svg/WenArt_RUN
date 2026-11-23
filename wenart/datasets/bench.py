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


# --- the bench's fair wall scoring (23 Nov 2026) ----------------------------------------------------------------------
#
# The bench scores walls with its own one-to-one matching (``bench_match_walls``) and verdicts (``wall_verdicts``), not
# with the gate's ``score.match_walls`` (the gate stays as it is). Faults of the first scorer, each fixed so that one
# error counts once and a correct reading is never counted wrong, while real errors still count:
# 1. pairs were ranked by the share of the shorter wall first, so a 4 cm piece (share 1.0) took the truth wall from the
#    2.67 m wall that reads it (share 0.9985): pairs are now ranked by the overlap length (metres) first;
# 2. a piece of a few cm counted as the reading of a long truth wall: a match must cover ``MATCH_MIN_TRUTH_SHARE`` of the
#    truth wall's length;
# 3. a thickness misread counted twice (the read wall a 'split', the truth wall 'read with another thickness'): the
#    unmatched truth and read walls on one line are paired one to one (``bench_match_walls`` ignoring the thickness);
#    the pair is one error, on the truth side;
# 4. the truth lists no piece shorter than 0.30 m or 1.5 x its thickness and no column (``swiss_dwellings.
#    is_listed_wall``: "a reader may fairly fold them into their neighbours"), so a kept junction block or column
#    counted as invented: an unmatched read piece of that size lying on the drawing's wall material (the wall and column
#    hatches, ``truth_material``) is neither a match nor an error; on no material it stays invented;
# 5. overlapping truth walls (two railings drawn over each other, b3431) are one solid in the drawing: a read wall
#    inside their overlap, and a truth wall whose length the walls read on the pair's band cover, are not counted.

MATCH_MIN_TRUTH_SHARE = 0.3   # a match covers at least this share of the truth wall's length (fault 2) ...
PIECES_MIN_SHARE = 0.5        # ... unless the read walls of its thickness on its line cover this share of it together
UNLISTED_MIN_M = 0.30         # a read piece shorter than this, or than ``UNLISTED_RATIO`` x its thickness, is a block
UNLISTED_RATIO = 1.5          # ... (the truth's own ``is_listed_wall`` sizes)
MATERIAL_SHARE = 0.75         # a block lies on wall material when this share of its footprint does ...
MATERIAL_TOL_M = 0.02         # ... the material grown by this much (drawing rounding)
TWIN_COVER_SHARE = 0.8        # an overlapping truth wall counts as read when walls on the pair's band cover this share
TWIN_ANGLE_DEG = 3.0


def _wlen(w: dict) -> float:
    return SC._dist(w["start"], w["end"])


def _overlap_m(t: dict, r: dict, ignore_thickness: bool = False, pieces_share: float = 0.0) -> Optional[tuple]:
    """``(overlap_m, lateral_m)`` of a truth wall and a read wall that pass ``score.wall_overlap`` (the thickness of the
    truth wall lent to the read one when ``ignore_thickness``) and whose overlap covers ``MATCH_MIN_TRUTH_SHARE`` of the
    truth wall, or any part of it when the read walls of its thickness on its line cover ``PIECES_MIN_SHARE`` of it
    together (``pieces_share``: a wall read in short pieces is read; its longest piece is the match); else None."""
    ov = SC.wall_overlap(t, dict(r, thickness=t.get("thickness")) if ignore_thickness else r)
    if ov is None:
        return None
    lt, lr = _wlen(t), _wlen(r)
    over = ov[0] * min(lt, lr)
    if over < MATCH_MIN_TRUTH_SHARE * lt - 1e-9 and pieces_share < PIECES_MIN_SHARE:
        return None
    return round(over, 4), ov[1]


def bench_match_walls(truth: list, read: list, ignore_thickness: bool = False) -> list:
    """The bench's matched ``(truth index, read index)`` pairs of one level's walls: candidates by ``_overlap_m``, ranked
    by the overlap weighed by the thickness agreement (``overlap x (1 - |dt| / 0.1)``: of two read walls over one truth
    wall the one of its thickness), the overlap, the smaller lateral offset, then the places (never the order of the
    lists); then each unmatched truth wall takes a candidate whose truth wall can move to a free candidate of its own
    (one swap, repeated: a wall read twice on one line never leaves a neighbour unmatched that one of the two reads)."""
    cand: dict = collections.defaultdict(dict)
    pairs = []
    for i, t in enumerate(truth):
        lt = _wlen(t)
        near = [r if not ignore_thickness else dict(r, thickness=t.get("thickness")) for r in read]
        share = covered_length(t, near) / lt if lt > 1e-6 else 0.0
        for j, r in enumerate(read):
            ov = _overlap_m(t, r, ignore_thickness, share)
            if ov is None:
                continue
            dt = 0.0 if ignore_thickness else abs(float(t.get("thickness") or 0) - float(r.get("thickness") or 0))
            key = (-round(ov[0] * max(0.0, 1.0 - dt / 0.1), 4), -ov[0], ov[1], SC._at(t, "start", "end", "thickness"),
                   SC._at(r, "start", "end", "thickness"))
            cand[i][j] = key
            pairs.append((key, i, j))
    chosen = dict(SC._greedy(pairs))
    for _round in range(len(truth)):
        taken = {j: i for i, j in chosen.items()}
        moved = False
        for i in sorted(cand):
            if i in chosen:
                continue
            options = []
            for j, key in cand[i].items():
                i2 = taken.get(j)
                if i2 is None:
                    options.append((key, (), j, None, None))
                    continue
                free = [q for q in cand[i2] if q not in taken]
                if free:
                    j2 = min(free, key=lambda q: cand[i2][q])
                    options.append((key, cand[i2][j2], j, i2, j2))
            if not options:
                continue
            _k, _k2, j, i2, j2 = min(options)
            if i2 is not None:
                chosen[i2] = j2
                taken[j2] = i2
            chosen[i] = j
            taken[j] = i
            moved = True
        if not moved:
            break
    return sorted(chosen.items())


def unlisted_size(w: dict) -> bool:
    """A piece the truth would not list by its size (``swiss_dwellings.is_listed_wall``)."""
    length = _wlen(w)
    return length < UNLISTED_MIN_M or length < UNLISTED_RATIO * float(w.get("thickness") or 0.0)


def _footprint(w: dict):
    from shapely.geometry import LineString
    t = max(float(w.get("thickness") or 0.0), 0.01)
    return LineString([w["start"][:2], w["end"][:2]]).buffer(t / 2.0, cap_style=2)


def truth_material(project_dir: Path, truth: dict) -> dict:
    """``{level id: shapely geometry}``: the wall material the bench drawing shows on each level, in the truth frame:
    the HATCH entities of ``plan.dxf`` on the wall, hatch and column layers of the project's style (the converter
    hatches the union of every wall, parapet and column, listed or not, less the openings: ``swiss_convert.
    wall_prims``), moved by each plan's origin (``truth.drawing``). Empty when the drawing or its plans are missing."""
    from shapely.geometry import Point, Polygon, box
    from shapely.ops import unary_union

    drawing = truth.get("drawing") or {}
    path = Path(project_dir) / (drawing.get("file") or "plan.dxf")
    upm = float(drawing.get("units_per_metre") or 0.0)
    plans = drawing.get("plans") or []
    if not path.is_file() or upm <= 0 or not plans:
        return {}
    try:
        import ezdxf
        doc = ezdxf.readfile(str(path))
    except Exception:                                   # noqa: BLE001 - no material, the scorer falls back
        return {}
    layers = (truth.get("style") or {}).get("layers") or {}
    want = {layers.get(k) for k in ("wall", "hatch", "structure")} - {None}
    frames = []
    for pl in plans:
        for lid in pl.get("levels") or []:
            tl = (truth.get("per_level") or {}).get(lid) or {}
            pts = [q for w in tl.get("walls") or [] for q in (w["start"], w["end"])]
            pts += [q for rm in tl.get("rooms") or [] for q in rm.get("polygon") or []]
            if pts:
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                frames.append((lid, pl["origin_m"], box(min(xs) - 1.0, min(ys) - 1.0, max(xs) + 1.0, max(ys) + 1.0)))
    parts: dict = collections.defaultdict(list)
    for h in doc.modelspace().query("HATCH"):
        if want and h.dxf.layer not in want:
            continue
        shells, holes = [], []
        for path_ in h.paths:
            verts = getattr(path_, "vertices", None)
            if not verts or len(verts) < 3:
                continue
            poly = Polygon([(float(v[0]) / upm, float(v[1]) / upm) for v in verts]).buffer(0)
            (shells if path_.path_type_flags & ezdxf.const.BOUNDARY_PATH_EXTERNAL else holes).append(poly)
        if not shells:
            continue
        geom = unary_union(shells)
        if holes:
            geom = geom.difference(unary_union(holes))
        c = geom.representative_point()
        for lid, (ox, oy), frame in frames:
            if frame.contains(Point(c.x - ox, c.y - oy)):
                from shapely import affinity
                parts[lid].append(affinity.translate(geom, -ox, -oy))
                break
    return {lid: unary_union(g).buffer(0) for lid, g in parts.items()}


def _on_material(w: dict, material) -> bool:
    if material is None or material.is_empty:
        return False
    fp = _footprint(w)
    return fp.area > 0 and fp.intersection(material.buffer(MATERIAL_TOL_M, join_style=2)).area >= \
        MATERIAL_SHARE * fp.area


def _twin_truth(tt: list) -> list:
    """Pairs of truth walls that overlap each other (one solid in the drawing, fault 5): parallel within
    ``TWIN_ANGLE_DEG``, the centre lines no further apart than half their thicknesses together (the bands touch or
    overlap) and overlapping along their axes by a listed wall's length (``UNLISTED_MIN_M``, ``UNLISTED_RATIO`` x the
    thicker; an end-to-end junction overlap is none): ``[(i, j, band)]``, ``band`` the union of the two footprints over
    their common span."""
    from shapely.geometry import LineString
    out = []
    for i, a in enumerate(tt):
        la = _wlen(a)
        if la < 1e-6:
            continue
        ux, uy = (a["end"][0] - a["start"][0]) / la, (a["end"][1] - a["start"][1]) / la
        for j in range(i + 1, len(tt)):
            b = tt[j]
            lb = _wlen(b)
            if lb < 1e-6:
                continue
            vx, vy = (b["end"][0] - b["start"][0]) / lb, (b["end"][1] - b["start"][1]) / lb
            if abs(ux * vy - uy * vx) > math.sin(math.radians(TWIN_ANGLE_DEG)):
                continue
            ss, ds = [], []
            for p in (b["start"], b["end"]):
                dx, dy = p[0] - a["start"][0], p[1] - a["start"][1]
                ss.append(dx * ux + dy * uy)
                ds.append(dx * uy - dy * ux)
            lo, hi = max(0.0, min(ss)), min(la, max(ss))
            ta, tb = float(a.get("thickness") or 0), float(b.get("thickness") or 0)
            if hi - lo < max(UNLISTED_MIN_M, UNLISTED_RATIO * max(ta, tb)) or \
                    max(abs(d) for d in ds) > (ta + tb) / 2.0 + 0.01:
                continue                       # an end-to-end junction overlap is no twin (a block there: fault 4)
            seg_a = LineString([(a["start"][0] + ux * lo, a["start"][1] + uy * lo),
                                (a["start"][0] + ux * hi, a["start"][1] + uy * hi)])
            band = _footprint({"start": list(seg_a.coords[0]), "end": list(seg_a.coords[1]),
                               "thickness": a.get("thickness")}).union(_footprint(b).intersection(
                                   seg_a.buffer(10.0, cap_style=2)))
            out.append((i, j, band))
    return out


def _read_with_twin(t: dict, rr: list, band) -> bool:
    """Truth wall ``t`` (one of two overlapping truth walls, ``band`` their common span) is read with its twin: read
    walls on its line cover ``TWIN_COVER_SHARE`` of its length (``covered_length``: of its thickness, any thickness for
    a read wall lying in the band, the solid the drawing shows there) and half of its footprint (grown by
    ``MATERIAL_TOL_M``: a leaf of two touching leaves read alone leaves the other one's material empty, a missed wall)."""
    from shapely.ops import unary_union
    lt = _wlen(t)
    if lt < 1e-6:
        return False
    grown = band.buffer(SC.WALL_LATERAL_M, cap_style=2)
    lent = []
    for r in rr:
        fp = _footprint(r)
        lent.append(dict(r, thickness=t.get("thickness")) if fp.area > 0 and fp.intersection(grown).area >=
                    0.5 * fp.area else r)
    if covered_length(dict(t), lent) < TWIN_COVER_SHARE * lt:
        return False
    tf = _footprint(t)
    near = [fp for fp in (_footprint(r) for r in rr) if fp.intersects(tf)]
    if not near:
        return False
    got = unary_union(near).buffer(MATERIAL_TOL_M, join_style=2)
    return tf.area > 0 and tf.intersection(got).area >= 0.5 * tf.area


def wall_verdicts(tt: list, rr: list, material=None) -> dict:
    """The bench's verdict on one level's walls (the faults above): ``pairs`` (matched, ``bench_match_walls``),
    ``thick`` (an unmatched truth wall and an unmatched read wall on one line with other thicknesses: one error),
    ``truth_skip`` / ``read_skip`` (``{index: reason}``: not counted either way), ``truth_class`` / ``read_class``
    (``{index: error class}`` of the rest)."""
    pairs = bench_match_walls(tt, rr)
    mt, mr = {i for i, _ in pairs}, {j for _, j in pairs}
    out = {"pairs": pairs, "thick": [], "truth_skip": {}, "read_skip": {}, "truth_class": {}, "read_class": {}}
    twins = _twin_truth(tt)
    for i, j, band in twins:                                     # fault 5: the truth lists one solid twice
        for k in (i, j):
            if k not in mt and k not in out["truth_skip"] and _read_with_twin(tt[k], rr, band):
                out["truth_skip"][k] = "overlaps another truth wall, read with it"
    for j, r in enumerate(rr):
        if j in mr:
            continue
        fp = _footprint(r)
        for i, k, band in twins:
            if fp.area > 0 and fp.intersection(band.buffer(MATERIAL_TOL_M, cap_style=2)).area >= \
                    MATERIAL_SHARE * fp.area:
                out["read_skip"][j] = "inside two overlapping truth walls"
                break
    left_t = [i for i in range(len(tt)) if i not in mt and i not in out["truth_skip"]]
    left_r = [j for j in range(len(rr)) if j not in mr and j not in out["read_skip"]]
    for a, b in bench_match_walls([tt[i] for i in left_t], [rr[j] for j in left_r], ignore_thickness=True):
        out["thick"].append((left_t[a], left_r[b]))               # fault 3: one error for the pair
    paired_t, paired_r = {i for i, _ in out["thick"]}, {j for _, j in out["thick"]}
    for j in left_r:
        if j in paired_r:
            continue
        if unlisted_size(rr[j]) and _on_material(rr[j], material):
            out["read_skip"][j] = "a block on drawn wall material (the truth lists no block)"   # fault 4
            continue
        out["read_class"][j] = _extra_wall_class(rr[j], tt)
    for i in left_t:
        if i in paired_t:
            out["truth_class"][i] = "wall read with another thickness"
        elif any(_overlap_m(tt[i], r) is not None for j, r in enumerate(rr) if j in mr):
            out["truth_class"][i] = "walls merged (read as part of a neighbouring wall on its line)"
        elif tt[i].get("parapet"):
            out["truth_class"][i] = "parapet wall missed"
        elif any(_overlap_m(tt[i], r, ignore_thickness=True) is not None for r in rr):
            out["truth_class"][i] = "wall read with another thickness"
        elif _off_axes(tt[i]):
            out["truth_class"][i] = "angled wall missed"
        else:
            out["truth_class"][i] = ("thin wall (< 10 cm) missed" if float(tt[i].get("thickness") or 0) < 0.10
                                     else "wall missed")
    return out


def bench_wall_stats(truth: dict, read: dict, material: Optional[dict] = None) -> tuple[dict, dict]:
    """The bench's wall numbers (``score._stats``: the skipped walls of ``wall_verdicts`` counted on neither side;
    walls on levels the truth has not are read and unmatched, as in ``score.match``) and the verdicts per level."""
    material = material or {}
    nt = nr = nm = 0
    verdicts = {}
    t_levels = [lv["id"] for lv in truth.get("levels") or []]
    for lid in t_levels:
        tt = TR.positives(((truth.get("per_level") or {}).get(lid) or {}).get("walls") or [])
        rr = ((read.get("per_level") or {}).get(lid) or {}).get("walls") or []
        v = wall_verdicts(tt, rr, material.get(lid))
        verdicts[lid] = v
        nt += len(tt) - len(v["truth_skip"])
        nr += len(rr) - len(v["read_skip"])
        nm += len(v["pairs"])
    if truth.get("status") != "partial":
        nr += sum(len((rl or {}).get("walls") or []) for lid, rl in (read.get("per_level") or {}).items()
                  if lid not in t_levels)
    return SC._stats(nt, nr, nm), verdicts


def errors(project: str, truth: dict, read: dict, material: Optional[dict] = None,
           verdicts: Optional[dict] = None) -> list[dict]:
    """The error instances of one reading: ``{class, kind, level, example}`` (the module docstring); walls by the
    bench's verdicts (``wall_verdicts``; ``material`` the drawing's wall material per level, ``truth_material``)."""
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
    # walls (the bench's own verdicts, ``wall_verdicts``) and stairs
    if verdicts is None:
        verdicts = bench_wall_stats(truth, read, material)[1]
    for lid, v in verdicts.items():
        if lid not in r_levels:
            continue
        tt = TR.positives(((truth.get("per_level") or {}).get(lid) or {}).get("walls") or [])
        rr = ((read.get("per_level") or {}).get(lid) or {}).get("walls") or []
        for i, cls in sorted(v["truth_class"].items()):
            t = tt[i]
            ex = f"{t.get('id')} {t.get('start')}-{t.get('end')} t={t.get('thickness')}"
            if cls == "wall read with another thickness":
                r = next((rr[j] for a, j in v["thick"] if a == i), None)
                if r is not None:
                    ex += f", read t={r.get('thickness')}"
            out.append({"class": cls, "kind": "walls", "level": lid, "example": ex})
        for j, cls in sorted(v["read_class"].items()):
            r = rr[j]
            out.append({"class": cls, "kind": "walls", "level": lid,
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


LINE_SHIFT_WALLS = 12         # align: the longest walls of each side whose lines vote for a shift
LINE_SHIFT_TOP = 6            # ... the shifts with the most votes are tried


def _line_shifts(tl: dict, rl: dict, rot: float) -> list[tuple]:
    """21 Nov 2026 (bench: four plans read right but scored 0, their min corners off by a parapet or a step): shifts that
    lay the reading's long wall lines on the truth's. Every pair of a truth wall and a read wall (after the turn) of
    the same direction (2 degrees) and thickness (5 cm) gives one line equation n . s = d (n the wall's normal, d the
    lines' offset); two equations of directions >= 30 degrees apart give a shift; the shifts are rounded to 2 cm and the
    ``LINE_SHIFT_TOP`` most voted returned as ``(dx, dy, rot)``."""
    def longest(ws):
        ws = [w for w in ws if w.get("start") and w.get("end") and SC._dist(w["start"], w["end"]) > 0.5]
        return sorted(ws, key=lambda w: -SC._dist(w["start"], w["end"]))[:LINE_SHIFT_WALLS]

    tt = longest(TR.positives(tl.get("walls") or []))
    rr = longest(_shift_level(rl, 0.0, 0.0, rot).get("walls") or [])
    eqs = []
    for t in tt:
        lt = SC._dist(t["start"], t["end"])
        ux, uy = (t["end"][0] - t["start"][0]) / lt, (t["end"][1] - t["start"][1]) / lt
        nx, ny = -uy, ux
        mt = ((t["start"][0] + t["end"][0]) / 2, (t["start"][1] + t["end"][1]) / 2)
        for r in rr:
            lr = SC._dist(r["start"], r["end"])
            vx, vy = (r["end"][0] - r["start"][0]) / lr, (r["end"][1] - r["start"][1]) / lr
            if abs(ux * vy - uy * vx) > math.sin(math.radians(2.0)):
                continue
            if abs(float(t.get("thickness") or 0) - float(r.get("thickness") or 0)) > SC.WALL_THICKNESS_M:
                continue
            mr = ((r["start"][0] + r["end"][0]) / 2, (r["start"][1] + r["end"][1]) / 2)
            eqs.append((nx, ny, nx * (mr[0] - mt[0]) + ny * (mr[1] - mt[1])))
    votes: collections.Counter = collections.Counter()
    for i, (ax, ay, ad) in enumerate(eqs):
        for bx, by, bd in eqs[i + 1:]:
            det = ax * by - ay * bx
            if abs(det) < math.sin(math.radians(30.0)):
                continue
            sx, sy = (ad * by - ay * bd) / det, (ax * bd - ad * bx) / det
            if math.hypot(sx, sy) <= 5.0:
                votes[(round(sx / 0.02) * 0.02, round(sy / 0.02) * 0.02)] += 1
    return [(sx, sy, rot) for (sx, sy), _n in votes.most_common(LINE_SHIFT_TOP)]


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
            cands += _line_shifts(tl, rl, rot)
        best = max(cands, key=lambda m: (_matches(tl, _shift_level(rl, *m)), -abs(m[2]), -math.hypot(m[0], m[1])))
        moved = math.hypot(best[0], best[1]) > 0.05 or abs(best[2]) > 0.5
        if moved and _matches(tl, _shift_level(rl, *best)) > _matches(tl, rl):
            out["per_level"][lid] = _shift_level(rl, *best)
            moves[lid] = {"shift_m": [round(best[0], 3), round(best[1], 3)], "rot_deg": best[2]}
            first = first or best
        else:
            first = first or (0.0, 0.0, 0.0)
    return out, moves


COVER_ANGLE_DEG = 3.0         # wall coverage: a wall covers another within this angle ...


def covered_length(a: dict, others: list) -> float:
    """The length of wall ``a``'s centre line that walls of ``others`` cover: the union of their spans along ``a``'s axis,
    each from a wall within ``COVER_ANGLE_DEG`` of ``a``, its centre line within ``score.WALL_LATERAL_M`` of ``a``'s
    over the shared span and its thickness within ``score.WALL_THICKNESS_M`` (the same solid on the same line)."""
    la = SC._dist(a["start"], a["end"])
    if la < 1e-6:
        return 0.0
    ox, oy = float(a["start"][0]), float(a["start"][1])
    ux, uy = (float(a["end"][0]) - ox) / la, (float(a["end"][1]) - oy) / la
    ta = a.get("thickness")
    spans = []
    for b in others:
        tb = b.get("thickness")
        if ta is not None and tb is not None and abs(float(ta) - float(tb)) > SC.WALL_THICKNESS_M:
            continue
        lb = SC._dist(b["start"], b["end"])
        if lb < 1e-6:
            continue
        cross = abs(((float(b["end"][0]) - float(b["start"][0])) * uy - (float(b["end"][1]) - float(b["start"][1])) * ux)
                    / lb)
        if cross > math.sin(math.radians(COVER_ANGLE_DEG)):
            continue
        pts = []
        for p in (b["start"], b["end"]):
            dx, dy = float(p[0]) - ox, float(p[1]) - oy
            pts.append((dx * ux + dy * uy, dx * uy - dy * ux))
        (s0, d0), (s1, d1) = sorted(pts)
        lo, hi = max(0.0, s0), min(la, s1)
        if hi - lo <= 1e-6:
            continue
        at = (lambda s: d0 + (d1 - d0) * (s - s0) / (s1 - s0)) if s1 - s0 > 1e-9 else (lambda s: d0)
        if max(abs(at(lo)), abs(at(hi))) > SC.WALL_LATERAL_M:
            continue
        spans.append((lo, hi))
    total, end = 0.0, -1.0
    for lo, hi in sorted(spans):
        if hi <= end:
            continue
        total += hi - max(lo, end)
        end = hi
    return total


def wall_coverage(truth: dict, read: dict) -> dict:
    """The length-weighted wall score (21 Nov 2026, next to the one-to-one ``match_walls``): pieces of one drawn wall
    that build the same solid on the same line count as that wall. ``truth_m``: the truth's wall length, ``covered_m``:
    of it covered by read walls; ``read_m``: the read wall length, ``on_truth_m``: of it on truth walls (``covered_length``
    both ways)."""
    out = {"truth_m": 0.0, "covered_m": 0.0, "read_m": 0.0, "on_truth_m": 0.0}
    for lid, tl in (truth.get("per_level") or {}).items():
        tt = [w for w in TR.positives(tl.get("walls") or []) if w.get("start") and w.get("end")]
        rr = [w for w in ((read.get("per_level") or {}).get(lid) or {}).get("walls") or []
              if w.get("start") and w.get("end")]
        for t in tt:
            out["truth_m"] += SC._dist(t["start"], t["end"])
            out["covered_m"] += covered_length(t, rr)
        for r in rr:
            out["read_m"] += SC._dist(r["start"], r["end"])
            out["on_truth_m"] += covered_length(r, tt)
    return {k: round(v, 3) for k, v in out.items()}


def _coverage_stats(c: dict) -> dict:
    rec = c["covered_m"] / c["truth_m"] if c["truth_m"] else 0.0
    prec = c["on_truth_m"] / c["read_m"] if c["read_m"] else 0.0
    return {**{k: round(v, 1) for k, v in c.items()}, "recall": round(rec, 4), "precision": round(prec, 4),
            "f1": round(2 * rec * prec / (rec + prec), 4) if rec + prec else 0.0}


def score_one(project_dir: Path, read_dir: Path) -> dict:
    """The numbers of one reading against its truth: ``reading_check.score.match`` per kind after ``align`` (the
    unaligned total kept), the room types, the errors."""
    name = Path(project_dir).name
    path = Path(project_dir) / "truth" / "reading_truth.json"
    truth = TR.synthetic_truth(name, path)
    meta = json.loads(path.read_text(encoding="utf-8"))          # the dataset and style fields synthetic_truth drops
    truth["dataset"], truth["style"] = meta.get("dataset") or {}, meta.get("style") or {}
    truth["drawing"] = meta.get("drawing") or {}
    b = json.loads((Path(read_dir) / "building.json").read_text(encoding="utf-8"))
    raw = TR.extract(b, project=name)
    read, shifts = align(truth, raw)
    res = SC.match(truth, read, b)
    res["total_unaligned"] = SC.match(truth, raw, b)["total"]
    # 23 Nov 2026: walls by the bench's fair scoring (``wall_verdicts``), the total with them; the gate's numbers kept
    material = truth_material(Path(project_dir), truth)
    res["walls_gate"] = res["walls"]
    res["total_gate"] = res["total"]
    res["walls"], verdicts = bench_wall_stats(truth, read, material)
    res["walls"]["skipped"] = {"truth": sum(len(v["truth_skip"]) for v in verdicts.values()),
                               "read": sum(len(v["read_skip"]) for v in verdicts.values())}
    res["total"] = SC.total({k: res[k] for k in SC.WEIGHTS if isinstance(res.get(k), dict)})
    res["scorer"] = "bench_s2"
    res["frame_moves"] = shifts
    res["walls_coverage"] = wall_coverage(truth, read)
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
        res["errors"] = errors(name, truth, read, material, verdicts) + [
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
    cover = {"truth_m": 0.0, "covered_m": 0.0, "read_m": 0.0, "on_truth_m": 0.0}
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
        for k, v in (res.get("walls_coverage") or {}).items():
            cover[k] += v
        for e in res.get("errors") or []:
            errs[e["class"]] += 1
            if e["class"] not in examples or (examples[e["class"]].get("bench_class") == "angled"
                                              and e.get("bench_class") != "angled"):
                examples[e["class"]] = e              # an orthogonal example where the class has one
    per_kind = {k: SC._stats(nt, nr, nm) for k, (nt, nr, nm) in sums.items()}
    per_kind["room_types"] = {"matched": types[0], "right": types[1],
                              "share": round(types[1] / types[0], 4) if types[0] else None}
    per_kind["walls_coverage"] = _coverage_stats(cover)
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
    wc, wc2 = agg["per_kind"]["walls_coverage"], read["per_kind"]["walls_coverage"]
    lines.append(f"| walls, length-weighted (m) | {wc['truth_m']:.0f} | {wc['read_m']:.0f} | {wc['covered_m']:.0f} | "
                 f"{wc['recall']:.3f} | {wc['precision']:.3f} | {wc['f1']:.3f} | {wc2['f1']:.3f} | "
                 f"{co['per_kind']['walls_coverage']['f1']:.3f} | {ca['per_kind']['walls_coverage']['f1']:.3f} |")
    rt, rt2 = agg["per_kind"]["room_types"], read["per_kind"]["room_types"]
    lines += [f"| room types (of matched rooms) | {rt['matched']} | | {rt['right']} | | | {rt['share']} | "
              f"{rt2['share']} | {co['per_kind']['room_types']['share']} | {ca['per_kind']['room_types']['share']} |",
              "", "The class columns count the projects whose drawing scale was read (a floor not read says "
              "nothing about walls at an angle). Walls are scored twice: one to one (the bench's own "
              "`bench_match_walls` and `wall_verdicts` since 23 Nov 2026: the longest overlap first, a match covers "
              "30 % of the truth wall, a thickness misread is one error, a block on the drawing's wall material and "
              "a wall inside two overlapping truth walls are not counted; a drawn wall read in pieces counts one "
              "piece) and length-weighted (`wall_coverage`: the length of the truth's walls that read walls of the "
              "same thickness cover on their line, and of the read walls on truth walls; pieces that build the same "
              "solid count as the wall).", "",
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
        # 23 Nov 2026: ``--out <dir>`` writes ``<dir>/<project>/bench_score.json`` and leaves the stored scores alone
        out_dir = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
        for f in sorted(Path(argv[2]).glob("*/bench_score.json")):
            old = json.loads(f.read_text(encoding="utf-8"))
            dest = (out_dir / f.parent.name / "bench_score.json") if out_dir else f
            if "error" in old or not (f.parent / "building.json").is_file():
                if out_dir:                             # a failed reading stays failed in the new scores
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(json.dumps(old, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                continue
            res = score_one(Path(argv[1]) / f.parent.name, f.parent)
            res["seconds"] = old.get("seconds")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    elif cmd == "report":
        agg = report(Path(argv[1]), Path(argv[2]), Path(argv[3]))
        print(json.dumps({k: agg[k] for k in ("projects", "floors", "mean_total")}))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
