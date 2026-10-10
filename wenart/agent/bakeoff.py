"""The Milestone 12 model bake-off of the agent (docs/milestone12.md §5.1, pod P1).

What: five tasks on our own data, the same for every candidate model of ``check.yaml models.bakeoff``:

- T1 (40 items): type a drawn piece from its plan crop (the room's committed debug plan, the piece outlined in
  blue); truth: hand labels with one-line reasons (``tests/fixtures/m12_bakeoff/tasks.json``).
- T2 (30 rooms): find planted layout errors in a room's top-down image (a bed turned 180 deg, a TV unit away from
  the sofa, a nightstand at the bed foot, a piece in a door swing, a chair turned away from its table; 0-2 per
  room); truth: what the code checks of ``problems_of`` measure on the planted building (a room is used only when
  they find nothing before planting).
- T3 (20 rooms): pick the best of three layouts of a room (one clean, two with planted errors).
- T4 (20 views): floating or sunk decor and wrong objects in committed render views; truth: hand labels.
- T5 (20 briefs): the room session of the agent: a plan (``prompts.PLAN_SCHEMA``, checked by ``loop.check_plan``)
  and the first tool calls on the brief of a planted room; scored: the call is valid (known tool, arguments pass
  its schema), allowed for its target (the brief's lock state) and, for an edit, in the checked plan.

Measured per model and variant (thinking off / on; Muse Glimmer: reasoning strength low / high): accuracy per
task, false findings (T2, T4), valid / allowed / in-plan calls (T5), seconds per call, tokens, the VRAM of the
server and its peak with a Cycles render of a committed scene next to it on the same GPU.

Why: the M11 agent (Qwen3.8-27B-FP8, thinking off) accepted 5 of 78 edits on real03; the bake-off picks the model
on the tasks the agent really does, not on public benchmarks (§5.1).

How:
    python -m wenart.agent.bakeoff build            # CPU, deterministic: items.json + images/ from tasks.json
    python -m wenart.agent.bakeoff models           # the job reads "name key id revision gpus size_gb variants"
    python -m wenart.agent.bakeoff run --key bakeoff.fp8 --device 0 --port 8001 --out results/bakeoff_m12
    python -m wenart.agent.bakeoff summary --out results/bakeoff_m12

The decision rule (``decide``): a model needing 2 GPUs (tensor parallel 2) is picked only when its T1-T4 score
(the mean of the four task accuracies, in points) is at least ``TWO_GPU_MARGIN`` (10) points above the best
single-GPU model; a model must answer >= 90 % of the items and make >= 80 % valid tool calls (T5) to be picked.
Ties (within 1 point): fewer seconds per call.

Contract notes: items are built once on the CPU and committed (the pod runs exactly what was reviewed); every
image path in ``items.json`` is relative to the items folder, or ``repo:<path>`` relative to the repo root (the
committed renders of T4). The answers of every model and variant go to ``<out>/<name>-<variant>.json`` as soon as
a variant ends, the server facts to ``<out>/<name>.json``; ``summary`` reads them all. Temperature 0, strict JSON
schemas (``model.AgentModel.structured``), tools with ``tool_choice: auto`` (``chat``).
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
import random
import statistics
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "m12_bakeoff"
SPEC_PATH = FIXTURE / "tasks.json"
ITEMS_NAME = "items.json"
OUT = REPO_ROOT / "results" / "bakeoff_m12"
TASKS = ("T1", "T2", "T3", "T4", "T5")
SCORED = ("T1", "T2", "T3", "T4")            # the decision rule's tasks
PROJECTS = ("real01", "real02", "real03") + tuple(f"synthetic-0{i}" for i in range(1, 8))
TWO_GPU_MARGIN = 10.0                         # points (§5.1)
TIE_POINTS = 1.0
MIN_ANSWERED = 0.9
MIN_T5_VALID = 0.8
VARIANT_CAP_S = 720.0                         # one variant's time cap (items not started by then are skipped)
WORKERS = 8                                   # = max_seqs of the bake-off servers
CYCLES_SAMPLES = 128
CYCLES_RES = "1920x1080"

# The planted layout problems: problem -> (the check id of its code finding, what the model is told).
PROBLEMS: dict[str, tuple[str, str]] = {
    "bed_reversed": ("G5", "a bed turned the wrong way: its foot end against a wall, its head end in the room"),
    "tv_away": ("G1", "a TV unit whose front does not face the sofa"),
    "nightstand_at_foot": ("G4", "a nightstand at the foot end of the bed instead of beside its head"),
    "door_blocked": ("F7", "a piece standing in the swing or the approach of a door"),
    "chair_away": ("G6", "a chair turned away from its table or desk"),
}
BED_TYPES = ("bed_single", "bed_double")
SOFA_TYPES = ("sofa", "sofa_corner")
TABLE_TYPES = ("table_dining", "desk")
CHAIR_TYPES = ("chair", "office_chair")
MOVABLE_TYPES = ("chair", "armchair", "side_table", "ottoman", "potted_plant", "floor_lamp", "office_chair", "bench")
WALL_GAP_M = 0.30          # an end of a bed within this of a wall is "against the wall"
NEAR_BED_M = 1.0           # a nightstand within this of a bed belongs to it
NEAR_TABLE_M = 1.2         # a chair within this of a table or desk belongs to it
DOOR_OVERLAP_M2 = 0.10     # a piece covering more of a door swing (or its approach strip) blocks it
FOOT_M = 0.30              # a nightstand this far past the bed centre towards the foot is "at the foot"
OVERLAP_M2 = 0.02          # a planted move may not overlap another piece more than this


# --------------------------------------------------------------------------
# Small IO helpers
# --------------------------------------------------------------------------

def read_json(path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)
    return path


def building_of(project: str, root: Path = REPO_ROOT) -> dict:
    return read_json(Path(root) / "results" / "furniture" / project / "building_final.json")


def image_path(ref: str, items_dir: Path, root: Path = REPO_ROOT) -> Path:
    """An image of an item: ``repo:<path>`` from the repo root, else relative to the items folder."""
    return Path(root) / ref[5:] if ref.startswith("repo:") else Path(items_dir) / ref


def t1_choices() -> tuple[str, ...]:
    from wenart.recognition.schemas import FURNITURE_TYPES
    return tuple(t for t in FURNITURE_TYPES if t != "unknown") + ("not_furniture",)


# --------------------------------------------------------------------------
# Geometry and the code checks of the five problems (pure)
# --------------------------------------------------------------------------

def _room(building: dict, room_id: str) -> dict:
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id}")
    return room


def room_polygon(room: dict):
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient
    poly = orient(Polygon(room["polygon"]), 1.0)
    return poly if poly.is_valid else poly.buffer(0)


def center(piece: dict) -> tuple[float, float]:
    fp = piece.get("footprint") or {}
    c = fp.get("center") or (0.0, 0.0)
    return float(c[0]), float(c[1])


def depth(piece: dict) -> float:
    return float(((piece.get("footprint") or {}).get("size") or (0.4, 0.4))[1])


def front(piece: dict) -> tuple[float, float]:
    from wenart.agent import topdown as TD
    a = math.radians(TD.piece_front_deg(piece))
    return math.cos(a), math.sin(a)


def end_gaps(piece: dict, poly) -> tuple[float, float]:
    """``(back gap, front gap)``: the distances of the back and the front edge midpoints to the room outline."""
    from shapely.geometry import Point
    (cx, cy), (fx, fy), d = center(piece), front(piece), depth(piece) / 2.0
    back = Point(cx - fx * d, cy - fy * d)
    head = Point(cx + fx * d, cy + fy * d)
    return poly.exterior.distance(back), poly.exterior.distance(head)


def facing_deg(piece: dict, target: tuple[float, float]) -> float:
    """The angle (0-180) between the piece's front and the direction from its centre to ``target``."""
    (cx, cy), (fx, fy) = center(piece), front(piece)
    vx, vy = target[0] - cx, target[1] - cy
    n = math.hypot(vx, vy)
    if n < 1e-9:
        return 0.0
    cos = max(-1.0, min(1.0, (fx * vx + fy * vy) / n))
    return math.degrees(math.acos(cos))


def along(piece: dict, point: tuple[float, float]) -> float:
    """The signed distance of ``point`` from the piece centre along its front (> 0: towards the front)."""
    (cx, cy), (fx, fy) = center(piece), front(piece)
    return (point[0] - cx) * fx + (point[1] - cy) * fy


def _shape(piece: dict):
    from wenart.agent import topdown as TD
    return TD.piece_polygon(piece)


def _nearest(piece: dict, others: list[dict], within: float) -> Optional[dict]:
    best, best_d = None, None
    shape = _shape(piece)
    for o in others:
        d = shape.distance(_shape(o))
        if d <= within and (best_d is None or d < best_d or (d == best_d and str(o["id"]) < str(best["id"]))):
            best, best_d = o, d
    return best


def door_areas(building: dict, room: dict) -> list[tuple[str, object]]:
    """``(door id, area)`` of every door of the room: its swing when it opens into the room (the half disc the
    top-down draws), else its 0.6 m approach strip; cut to the room."""
    from wenart.furniture import placer
    try:
        ctx = placer.room_context(building, room)
    except Exception:  # noqa: BLE001 - an odd polygon: no door checks for that room
        return []
    out = []
    for door in ctx.doors:
        area = door.swing if door.swing is not None and not door.swing.is_empty else door.zone
        if area is not None and not area.is_empty:
            out.append((door.id, area.intersection(ctx.polygon)))
    return out


def problems_of(building: dict, room_id: str) -> list[tuple[str, str]]:
    """The five problems the code measures in a room, as sorted ``(problem, piece id)`` pairs: the T2 truth."""
    from wenart.agent import topdown as TD
    room = _room(building, room_id)
    poly = room_polygon(room)
    pieces = TD.built_pieces(building, room_id)
    of = lambda types: [p for p in pieces if p.get("type") in types]  # noqa: E731
    out: set = set()
    beds = of(BED_TYPES)
    reversed_beds = set()
    for b in beds:
        back, head = end_gaps(b, poly)
        if back > WALL_GAP_M and head <= WALL_GAP_M:
            out.add(("bed_reversed", b["id"]))
            reversed_beds.add(b["id"])
    sofas = of(SOFA_TYPES)
    for tv in of(("tv_unit",)):
        if sofas:
            s = min(sofas, key=lambda s: (math.dist(center(s), center(tv)), str(s["id"])))
            if facing_deg(tv, center(s)) > 90.0:
                out.add(("tv_away", tv["id"]))
    for n in of(("nightstand",)):
        b = _nearest(n, beds, NEAR_BED_M)
        # A reversed bed is the error, not its nightstands at the wall end: measured from the wall end then.
        sign = -1.0 if b is not None and b["id"] in reversed_beds else 1.0
        if b is not None and sign * along(b, center(n)) > FOOT_M:
            out.add(("nightstand_at_foot", n["id"]))
    tables = of(TABLE_TYPES)
    for ch in of(CHAIR_TYPES):
        t = _nearest(ch, tables, NEAR_TABLE_M)
        if t is not None and facing_deg(ch, center(t)) > 90.0:
            out.add(("chair_away", ch["id"]))
    for _door, area in door_areas(building, room):
        for p in pieces:
            if p.get("type") in ("stair",):
                continue
            try:
                if _shape(p).intersection(area).area > DOOR_OVERLAP_M2:
                    out.add(("door_blocked", p["id"]))
            except Exception:  # noqa: BLE001 - a broken footprint is not a finding here
                continue
    return sorted(out)


# --------------------------------------------------------------------------
# Planting (pure, deterministic)
# --------------------------------------------------------------------------

def turned(piece: dict) -> dict:
    """The piece turned by 180 deg (same footprint, front reversed)."""
    q = copy.deepcopy(piece)
    fp = q.setdefault("footprint", {})
    fp["rotation_deg"] = round((float(fp.get("rotation_deg") or 0.0) + 180.0) % 360.0, 4)
    if q.get("front_deg") is not None:
        q["front_deg"] = round((float(q["front_deg"]) + 180.0) % 360.0, 4)
    return q


def moved(piece: dict, xy: tuple[float, float]) -> dict:
    q = copy.deepcopy(piece)
    q.setdefault("footprint", {})["center"] = [round(float(xy[0]), 4), round(float(xy[1]), 4)]
    return q


def with_piece(building: dict, piece: dict) -> dict:
    b = copy.deepcopy(building)
    b["furniture"] = [piece if f.get("id") == piece.get("id") else f for f in b.get("furniture") or []]
    return b


def fits(building: dict, room_id: str, piece: dict) -> bool:
    """Inside the room (2 cm tolerance) and overlapping no other built piece by more than ``OVERLAP_M2``."""
    from wenart.agent import topdown as TD
    poly = room_polygon(_room(building, room_id))
    shape = _shape(piece)
    if not shape.within(poly.buffer(0.02)):
        return False
    return all(_shape(o).intersection(shape).area <= OVERLAP_M2 for o in TD.built_pieces(building, room_id)
               if o.get("id") != piece.get("id"))


def _candidates(building: dict, room_id: str) -> list[tuple[str, dict]]:
    """Every edit that may plant one problem: ``(problem, new piece)``, in a fixed order."""
    from wenart.agent import topdown as TD
    room = _room(building, room_id)
    pieces = sorted(TD.built_pieces(building, room_id), key=lambda p: str(p.get("id")))
    of = lambda types: [p for p in pieces if p.get("type") in types]  # noqa: E731
    out: list = []
    for b in of(BED_TYPES):
        out.append(("bed_reversed", turned(b)))
    for tv in of(("tv_unit",)):
        out.append(("tv_away", turned(tv)))
    beds = of(BED_TYPES)
    for n in of(("nightstand",)):
        b = _nearest(n, beds, NEAR_BED_M)
        if b is None:
            continue
        (nx, ny), (fx, fy) = center(n), front(b)
        t = along(b, (nx, ny))
        out.append(("nightstand_at_foot", moved(n, (nx - 2.0 * t * fx, ny - 2.0 * t * fy))))
        shift = depth(b) / 2.0 - depth(n) / 2.0 - 0.05 - t
        out.append(("nightstand_at_foot", moved(n, (nx + shift * fx, ny + shift * fy))))
    for ch in of(CHAIR_TYPES):
        out.append(("chair_away", turned(ch)))
    for _door, area in door_areas(building, room):
        if area.is_empty:
            continue
        c = area.centroid
        for p in of(MOVABLE_TYPES):
            out.append(("door_blocked", moved(p, (c.x, c.y))))
    return out


def plant_options(building: dict, room_id: str) -> list[tuple[str, str, dict]]:
    """``(problem, piece id, new piece)`` for every edit that adds exactly that one problem to the room (the code
    checks before and after differ by just it) and keeps the piece inside the room and off the others."""
    base = set(problems_of(building, room_id))
    out = []
    seen = set()
    for problem, piece in _candidates(building, room_id):
        key = (problem, piece["id"])
        if key in base or key in seen:
            continue
        b2 = with_piece(building, piece)
        if set(problems_of(b2, room_id)) != base | {key}:
            continue
        if not fits(building, room_id, piece):
            continue
        seen.add(key)
        out.append((problem, piece["id"], piece))
    return out


def plant(building: dict, room_id: str, n: int, rng: random.Random,
          counts: Optional[dict] = None) -> tuple[dict, list[tuple[str, str]]]:
    """Plant up to ``n`` problems on different pieces; the least used problem kind first (``counts``, updated),
    ties by ``rng``. ``(planted building, planted pairs)``."""
    counts = counts if counts is not None else {}
    b = building
    planted: list = []
    for _ in range(n):
        used = {pid for _p, pid in planted}
        opts = [o for o in plant_options(b, room_id) if o[1] not in used]
        if not opts:
            break
        low = min(counts.get(o[0], 0) for o in opts)
        pool = [o for o in opts if counts.get(o[0], 0) == low]
        problem, pid, piece = pool[rng.randrange(len(pool))]
        b = with_piece(b, piece)
        planted.append((problem, pid))
        counts[problem] = counts.get(problem, 0) + 1
    return b, planted


def room_pool(buildings: dict, clean: bool = False) -> list[tuple[str, str]]:
    """``(project, room id)`` of every room with at least one plant option (``clean``: and no problem before
    planting). A problem the committed layout already has is part of the truth: the code measures it on the image
    the model gets (T2), and every layout of a T3 room has it (the clean one has the fewest)."""
    out = []
    for project in sorted(buildings):
        b = buildings[project]
        for room in sorted(b.get("rooms") or [], key=lambda r: str(r.get("id"))):
            rid = room.get("id")
            try:
                if (clean and problems_of(b, rid)) or not plant_options(b, rid):
                    continue
            except Exception:  # noqa: BLE001 - a room with broken geometry is not used
                continue
            out.append((project, rid))
    return out


def pick_rooms(pool: list, n: int, seed: int, per_project: int, avoid: tuple = ()) -> list[tuple[str, str]]:
    """``n`` rooms of the pool in a seeded order, at most ``per_project`` per project, the ``avoid`` ones last."""
    order = list(pool)
    random.Random(seed).shuffle(order)
    order = [r for r in order if r not in avoid] + [r for r in order if r in avoid]
    out, per = [], {}
    for project, rid in order:
        if per.get(project, 0) >= per_project:
            continue
        out.append((project, rid))
        per[project] = per.get(project, 0) + 1
        if len(out) == n:
            break
    return out


# --------------------------------------------------------------------------
# Building the items (CPU, deterministic)
# --------------------------------------------------------------------------

def plan_image(project: str, room_id: str, root: Path = REPO_ROOT) -> Optional[Path]:
    """The room's committed debug plan (``results/final/<p>/cam_<room>_<n>_plan.jpg``, the lowest n)."""
    folder = Path(root) / "results" / "final" / project
    prefix = f"cam_{room_id}_"
    cams = [c for c in sorted(folder.glob(f"{prefix}*_plan.jpg"))
            if c.name[len(prefix):].split("_")[0].isdigit()]
    return cams[0] if cams else None


def t1_crop(building: dict, project: str, piece_id: str, room_id: str, out: Path, root: Path = REPO_ROOT,
            margin_m: float = 1.2, max_side: int = 512) -> Path:
    """The plan crop of T1: the room's debug plan (its polygon box +- 0.5 m scaled to the image), the piece's
    footprint outlined in blue, cut to the piece +- ``margin_m``."""
    from PIL import Image, ImageDraw
    room = _room(building, room_id)
    xs = [float(p[0]) for p in room["polygon"]]
    ys = [float(p[1]) for p in room["polygon"]]
    x0, x1, y0, y1 = min(xs) - 0.5, max(xs) + 0.5, min(ys) - 0.5, max(ys) + 0.5
    plan = plan_image(project, room_id, root)
    if plan is None:
        raise FileNotFoundError(f"no plan image of {project} {room_id}")
    im = Image.open(plan).convert("RGB")
    W, H = im.size
    sx, sy = W / (x1 - x0), H / (y1 - y0)
    piece = next(f for f in building["furniture"] if f.get("id") == piece_id)
    pts = [((x - x0) * sx, (y1 - y) * sy) for x, y in list(_shape(piece).exterior.coords)[:-1]]
    ImageDraw.Draw(im).polygon(pts, outline=(0, 90, 255), width=4)
    box = (max(0, min(p[0] for p in pts) - margin_m * sx), max(0, min(p[1] for p in pts) - margin_m * sy),
           min(W, max(p[0] for p in pts) + margin_m * sx), min(H, max(p[1] for p in pts) + margin_m * sy))
    crop = im.crop(tuple(int(round(v)) for v in box))
    s = max_side / max(crop.size)                  # the plans are small: most crops are scaled up
    crop = crop.resize((max(1, int(crop.width * s)), max(1, int(crop.height * s))), Image.LANCZOS)
    out.parent.mkdir(parents=True, exist_ok=True)
    crop.save(out, quality=90)
    return out


def topdown_jpg(building: dict, room_id: str, out: Path) -> Path:
    """The agent's top-down image of the room (``topdown.draw_room``) as a JPEG (smaller to commit)."""
    from PIL import Image
    from wenart.agent import topdown as TD
    png = out.with_suffix(".png")
    TD.draw_room(building, room_id, png, title=f"{_room(building, room_id).get('label')} "
                                              f"({_room(building, room_id).get('room_type')})")
    Image.open(png).convert("RGB").save(out, quality=88)
    png.unlink()
    return out


def code_findings(building: dict, room_id: str) -> list[dict]:
    """The planted problems as the code critic's findings (T5's input)."""
    out = []
    for problem, pid in problems_of(building, room_id):
        check, words = PROBLEMS[problem]
        piece = next(f for f in building["furniture"] if f.get("id") == pid)
        out.append({"id": f"c:{check}:{pid}", "check": check, "severity": "major", "target": pid,
                    "room_id": room_id, "source": "code",
                    "message": f"{piece.get('type')} {pid}: {words}"})
    return out


def build(spec_path: Path = SPEC_PATH, out_dir: Path = FIXTURE, root: Path = REPO_ROOT,
          tasks: tuple = TASKS) -> dict:
    """``items.json`` and ``images/`` in ``out_dir`` from the spec (module docstring); returns the items file."""
    from wenart.agent import brief as BR
    from wenart.agent import loop as LP
    from wenart.agent import tools as TL
    spec = read_json(spec_path)
    out_dir = Path(out_dir)
    img = out_dir / "images"
    items: list = []
    buildings = {p: building_of(p, root) for p in PROJECTS
                 if (Path(root) / "results" / "furniture" / p / "building_final.json").is_file()}
    room_of = lambda p, rid: _room(buildings[p], rid)  # noqa: E731
    if "T1" in tasks:
        for i, it in enumerate(spec["T1"]["items"], 1):
            b = buildings[it["project"]]
            piece = next(f for f in b["furniture"] if f.get("id") == it["piece_id"])
            name = f"t1_{i:02d}_{it['project']}_{it['piece_id']}.jpg"
            t1_crop(b, it["project"], it["piece_id"], it["room_id"], img / name, root)
            room = room_of(it["project"], it["room_id"])
            size = [round(float(v), 2) for v in (piece.get("footprint") or {}).get("size") or (0, 0)][:2]
            items.append({"id": f"T1-{i:02d}", "task": "T1", "project": it["project"], "piece_id": it["piece_id"],
                          "room_id": it["room_id"], "room_label": room.get("label"),
                          "room_type": room.get("room_type"), "size_m": size, "images": [f"images/{name}"],
                          "truth": list(it["truth"]), "why": it["why"]})
    pool = room_pool(buildings) if {"T2", "T3", "T5"} & set(tasks) else []
    t2_rooms: list = []
    planted_t2: list = []
    if {"T2", "T5"} & set(tasks):
        s2 = spec["T2"]
        rooms = pick_rooms(pool, int(s2["rooms"]), int(s2["seed"]), int(s2["max_rooms_per_project"]))
        rng = random.Random(int(s2["seed"]))
        counts: dict = {}
        pattern = list(s2["pattern"])
        for i, (project, rid) in enumerate(rooms, 1):
            want = pattern[(i - 1) % len(pattern)]
            b2, planted = plant(buildings[project], rid, want, rng, counts)
            planted_t2.append((project, rid, b2, planted))
            t2_rooms.append((project, rid))
            if "T2" not in tasks:
                continue
            name = f"t2_{i:02d}_{project}_{rid}.jpg"
            topdown_jpg(b2, rid, img / name)
            room = room_of(project, rid)
            items.append({"id": f"T2-{i:02d}", "task": "T2", "project": project, "room_id": rid,
                          "room_label": room.get("label"), "room_type": room.get("room_type"),
                          "images": [f"images/{name}"],
                          "truth": [list(x) for x in problems_of(b2, rid)],
                          "planted": [list(x) for x in planted]})
    if "T3" in tasks:
        s3 = spec["T3"]
        rooms3 = [r for r in pick_rooms(pool, len(pool), int(s3["seed"]), int(s3["max_rooms_per_project"]),
                                        avoid=tuple(t2_rooms))]
        rng = random.Random(int(s3["seed"]))
        counts3: dict = {}
        k = 0
        for project, rid in rooms3:
            if k == int(s3["rooms"]):
                break
            base = buildings[project]
            if len(plant_options(base, rid)) < 2:
                continue
            bad_a, pa = plant(base, rid, 1, rng, counts3)
            bad_b, pb = plant(base, rid, 2, rng, counts3)
            if not pa or not pb or set(pa) == set(pb):
                continue
            k += 1
            order = [("clean", base, []), ("a", bad_a, pa), ("b", bad_b, pb)]
            rng.shuffle(order)
            names = []
            for j, (_tag, bj, _pj) in enumerate(order, 1):
                name = f"t3_{k:02d}_{project}_{rid}_{j}.jpg"
                topdown_jpg(bj, rid, img / name)
                names.append(f"images/{name}")
            room = room_of(project, rid)
            items.append({"id": f"T3-{k:02d}", "task": "T3", "project": project, "room_id": rid,
                          "room_label": room.get("label"), "room_type": room.get("room_type"), "images": names,
                          "truth": 1 + [t for t, _b, _p in order].index("clean"),
                          "layouts": [{"layout": j, "planted": [list(x) for x in pj]}
                                      for j, (_t, _b, pj) in enumerate(order, 1)]})
    if "T4" in tasks:
        for i, it in enumerate(spec["T4"]["items"], 1):
            ref = f"repo:results/final/{it['project']}/{it['camera']}_final_preview.jpg"
            if not image_path(ref, out_dir, root).is_file():
                raise FileNotFoundError(ref)
            items.append({"id": f"T4-{i:02d}", "task": "T4", "project": it["project"], "camera": it["camera"],
                          "images": [ref], "truth": {k: it[k] for k in ("floating_or_sunk_decor", "wrong_object")},
                          "why": it["why"]})
    if "T5" in tasks:
        registry = TL.build_registry()
        n5 = int(spec["T5"]["rooms"])
        k = 0
        for project, rid, b2, planted in planted_t2:
            if k == n5:
                break
            if not planted:
                continue
            k += 1
            brief = BR.room_brief(b2, rid, findings=code_findings(b2, rid))
            offered = LP.offered_tools(registry, brief)
            items.append({"id": f"T5-{k:02d}", "task": "T5", "project": project, "room_id": rid, "images": [],
                          "brief": brief, "offered": offered, "truth": [list(x) for x in planted],
                          "default_checklist": LP.default_checklist(brief)})
    old = out_dir / ITEMS_NAME
    if set(tasks) != set(TASKS) and old.is_file():          # a partial rebuild keeps the other tasks' items
        kept = [i for i in read_json(old).get("items") or [] if i.get("task") not in tasks]
        items = sorted(kept + items, key=lambda i: (TASKS.index(i["task"]), i["id"]))
    data = {"version": 1, "spec": spec_path.name if Path(spec_path).parent == out_dir else str(spec_path),
            "counts": {t: sum(1 for i in items if i["task"] == t) for t in TASKS}, "items": items}
    return {"path": str(write_json(out_dir / ITEMS_NAME, data)), "counts": data["counts"]}


def load_items(items_path: Optional[Path] = None) -> tuple[list[dict], Path]:
    path = Path(items_path) if items_path else FIXTURE / ITEMS_NAME
    return read_json(path)["items"], path.parent


# --------------------------------------------------------------------------
# Prompts and schemas
# --------------------------------------------------------------------------

SYSTEM = ("You check architectural drawings, room layouts and interior renders for an automatic design pipeline. "
          "Answer only with the JSON the schema asks for. Be exact: say what the image shows, not what is usual.")
TOPDOWN_KEY = ("The top-down image: the black outline is the room; each piece is a filled shape with its id and type; "
               "the black arrow from the piece's centre points to its front (a bed's foot end, a chair's seat front, "
               "a TV unit's screen side, a sofa's seat side); the light orange shapes are door swings and door "
               "approach strips; the light blue bands are windows. The grid is 1 m.")


def schema_of(task: str) -> dict:
    if task == "T1":
        return {"type": "object", "additionalProperties": False, "required": ["type", "why"],
                "properties": {"type": {"enum": list(t1_choices())}, "why": {"type": "string", "maxLength": 200}}}
    if task == "T2":
        pair = {"type": "object", "additionalProperties": False, "required": ["problem", "piece_id"],
                "properties": {"problem": {"enum": list(PROBLEMS)}, "piece_id": {"type": "string"}}}
        return {"type": "object", "additionalProperties": False, "required": ["errors"],
                "properties": {"errors": {"type": "array", "maxItems": 8, "items": pair}}}
    if task == "T3":
        return {"type": "object", "additionalProperties": False, "required": ["best", "why"],
                "properties": {"best": {"enum": [1, 2, 3]}, "why": {"type": "string", "maxLength": 300}}}
    if task == "T4":
        return {"type": "object", "additionalProperties": False,
                "required": ["floating_or_sunk_decor", "wrong_object", "notes"],
                "properties": {"floating_or_sunk_decor": {"type": "boolean"}, "wrong_object": {"type": "boolean"},
                               "notes": {"type": "string", "maxLength": 300}}}
    raise KeyError(task)


def problem_lines() -> str:
    return "\n".join(f"- {k}: {v[1]}" for k, v in PROBLEMS.items())


def prompt_of(item: dict) -> str:
    task = item["task"]
    if task == "T1":
        w, d = (item.get("size_m") or [0, 0])[:2]
        return (f"The image is a crop of a floor plan. One drawn item is outlined in blue. Room: "
                f"{item.get('room_label')} ({item.get('room_type')}). The item's drawn outline is {w:.2f} m x "
                f"{d:.2f} m. Coloured texts and boxes in the image are the pipeline's earlier guesses and can be "
                f"wrong; judge the black drawing inside the blue outline. What is the outlined item? Pick one type. "
                f"Pick not_furniture when the outline holds no piece of furniture or fixed equipment (for example "
                f"a door swing, a text, a number, a symbol or a sign). In why, name what you see in one line.")
    if task == "T2":
        return (f"{TOPDOWN_KEY}\nRoom: {item.get('room_label')} ({item.get('room_type')}). Find only these layout "
                f"errors:\n{problem_lines()}\nList each error with the id of the piece that is wrong (for "
                f"door_blocked the piece in the door's way). An empty list when the room has none of them.")
    if task == "T3":
        return (f"{TOPDOWN_KEY}\nImages 1, 2 and 3 are three layouts of the same room: {item.get('room_label')} "
                f"({item.get('room_type')}). Which layout is best, with the fewest of these errors?\n"
                f"{problem_lines()}\nAnswer with its number and one line why.")
    if task == "T4":
        return ("The image is a render of a furnished room. Answer two questions about it.\n"
                "floating_or_sunk_decor: does any decor item (cushion, pillow, throw, vase, lamp, books, plant) "
                "hang in the air above the surface it should rest on, or sink into or cut through another object?\n"
                "wrong_object: is any object clearly not what it should be or visibly faulty (for example a "
                "shapeless blob or a bench used as a blanket, a desk with a drawer left pulled out, an outdoor "
                "object indoors)? Plain untextured boxes do not count.\nIn notes, name what you saw in one line.")
    raise KeyError(task)


def messages_of(item: dict, items_dir: Path, root: Path = REPO_ROOT) -> list[dict]:
    from wenart.agent import model as M
    images = [image_path(ref, items_dir, root) for ref in item.get("images") or []]
    labels = [f"Image {i}" for i in range(1, len(images) + 1)] if len(images) > 1 else None
    return [{"role": "system", "content": SYSTEM},
            M.user_message(prompt_of(item), images, labels)]


# --------------------------------------------------------------------------
# Scoring (pure)
# --------------------------------------------------------------------------

def score_item(item: dict, answer: Optional[dict]) -> dict:
    """The score of one answer (None: no valid answer: wrong, every label missed)."""
    task = item["task"]
    if task == "T1":
        ok = answer is not None and answer.get("type") in item["truth"]
        return {"score": 1.0 if ok else 0.0, "correct": ok}
    if task == "T2":
        truth = {tuple(x) for x in item["truth"]}
        pred = {(e.get("problem"), e.get("piece_id")) for e in (answer or {}).get("errors") or []}
        hit = truth & pred
        union = truth | pred
        score = 1.0 if not union and answer is not None else (len(hit) / len(union) if union else 0.0)
        return {"score": round(score, 4), "hit": len(hit), "missed": len(truth - pred),
                "false": len(pred - truth), "truth": len(truth)}
    if task == "T3":
        ok = answer is not None and answer.get("best") == item["truth"]
        return {"score": 1.0 if ok else 0.0, "correct": ok}
    if task == "T4":
        scored = correct = false = 0
        for k, want in item["truth"].items():
            if want is None:
                continue
            scored += 1
            got = None if answer is None else answer.get(k)
            correct += int(got is want)
            false += int(got is True and want is False)
        return {"score": round(correct / scored, 4) if scored else 0.0, "correct": correct, "scored": scored,
                "false": false}
    if task == "T5":
        calls = (answer or {}).get("calls") or []
        n = len(calls)
        good = sum(1 for c in calls if c["valid"] and c["allowed"] and (not c["edit"] or c["in_plan"]))
        return {"score": round(good / n, 4) if n else 0.0, "calls": n,
                "valid": sum(c["valid"] for c in calls), "allowed": sum(c["allowed"] for c in calls),
                "edits": sum(c["edit"] for c in calls), "in_plan": sum(c["in_plan"] for c in calls if c["edit"]),
                "plan_ok": bool((answer or {}).get("plan_ok"))}
    raise KeyError(task)


def judge_call(name: str, args: Optional[dict], error: Optional[str], item: dict, checklist: list[dict],
               registry) -> dict:
    """One T5 tool call: valid (an offered tool, arguments that pass its schema), allowed (the brief's lock state
    for its target, ``loop.check_plan``'s rules), and for an edit: in the checked plan (``loop.step_done``)."""
    from wenart.agent import brief as BR
    from wenart.agent import loop as LP
    from wenart.agent import tools as TL
    from wenart.recognition.vlm_client import schema_errors
    tool = registry.tools.get(name)
    offered = item.get("offered") or []
    errors = [error] if error else (["not offered"] if tool is None or name not in offered else
                                    schema_errors(tool.parameters, args or {}))
    valid = not errors
    edit = tool is not None and tool.kind in TL.EDIT_KINDS
    brief = item["brief"]
    allowed = valid
    if valid and edit:
        args = args or {}
        target = TL._target(name, args)
        pieces = {p["id"]: p for p in brief.get("pieces") or []}
        if name in BR.PIECE_TOOLS:
            p = pieces.get(target)
            allowed = p is not None and BR.is_allowed(p, name)
        elif name in BR.GROUP_TOOLS:
            groups = {g.get("group_id") for g in brief.get("groups") or []}
            allowed = target in groups or bool((pieces.get(target) or {}).get("group")) or not groups
        elif name in BR.ROOM_TOOLS:
            allowed = args.get("room_id") in (None, brief["room"]["id"])
    in_plan = bool(valid and edit and any(LP.step_done(s, name, args or {}, {}) for s in checklist))
    return {"name": name, "arguments": args, "errors": errors[:3], "valid": valid, "edit": edit,
            "allowed": bool(allowed), "in_plan": in_plan}


def aggregate(items: list[dict], results: dict) -> dict:
    """Per task: accuracy (mean score), answered share, false findings (T2, T4), T5 call rates; seconds and
    tokens per call."""
    out: dict = {}
    for task in TASKS:
        rows = [(it, results.get(it["id"])) for it in items if it["task"] == task]
        if not rows:
            continue
        done = [r for _it, r in rows if r is not None and r.get("status") != "skipped"]
        scores = [(r or {}).get("score", {}).get("score", 0.0) if r else 0.0 for _it, r in rows]
        agg = {"items": len(rows), "run": len(done), "answered": sum(1 for r in done if r.get("error") is None),
               "accuracy": round(sum(scores) / len(rows), 4)}
        if task in ("T2", "T4"):
            agg["false_findings"] = sum((r.get("score") or {}).get("false", 0) for r in done)
        if task == "T2":
            truth = sum((r.get("score") or {}).get("truth", 0) for r in done)
            agg["recall"] = round(sum((r.get("score") or {}).get("hit", 0) for r in done) / truth, 4) if truth \
                else None
        if task == "T5":
            calls = sum((r.get("score") or {}).get("calls", 0) for r in done)
            edits = sum((r.get("score") or {}).get("edits", 0) for r in done)
            agg.update({"calls": calls,
                        "valid_rate": round(sum((r.get("score") or {}).get("valid", 0) for r in done) / calls, 4)
                        if calls else 0.0,
                        "allowed_rate": round(sum((r.get("score") or {}).get("allowed", 0) for r in done) / calls,
                                              4) if calls else 0.0,
                        "in_plan_rate": round(sum((r.get("score") or {}).get("in_plan", 0) for r in done) / edits,
                                              4) if edits else 0.0,
                        "no_call_briefs": sum(1 for r in done if not (r.get("score") or {}).get("calls")),
                        "plans_ok": sum(1 for r in done if (r.get("score") or {}).get("plan_ok"))})
        out[task] = agg
    secs = [c for r in results.values() if r for c in r.get("call_seconds") or []]
    toks = [r.get("completion_tokens") for r in results.values() if r and r.get("completion_tokens") is not None]
    calls = sum(len(r.get("call_seconds") or []) for r in results.values() if r)
    out["calls"] = calls
    out["s_per_call"] = round(statistics.mean(secs), 2) if secs else None
    out["s_per_call_p50"] = round(statistics.median(secs), 2) if secs else None
    out["completion_tokens_per_call"] = round(sum(toks) / calls, 1) if calls and toks else None
    scored = [out[t]["accuracy"] for t in SCORED if t in out]
    out["combined"] = round(100.0 * sum(scored) / len(scored), 1) if len(scored) == len(SCORED) else None
    return out


# --------------------------------------------------------------------------
# Running one model (pod)
# --------------------------------------------------------------------------

def answer_item(model, item: dict, items_dir: Path, registry=None, root: Path = REPO_ROOT) -> dict:
    """One item through the model: ``{"answer", "error", "call_seconds", "prompt_tokens", "completion_tokens"}``."""
    from wenart.agent import model as M
    t0 = time.time()
    out: dict = {"id": item["id"], "task": item["task"], "answer": None, "error": None, "call_seconds": [],
                 "prompt_tokens": 0, "completion_tokens": 0}

    def used(reply):
        out["call_seconds"].append(reply.seconds)
        out["prompt_tokens"] += int((reply.usage or {}).get("prompt_tokens") or 0)
        out["completion_tokens"] += int((reply.usage or {}).get("completion_tokens") or 0)

    try:
        if item["task"] == "T5":
            out["answer"], out["error"] = _session(model, item, registry, used)
        else:
            reply = model.structured(messages_of(item, items_dir, root), schema_of(item["task"]),
                                     call_id=item["id"], name=item["task"].lower(), kind="task",
                                     thinking=model.critic_thinking)
            used(reply)
            out["answer"] = reply.data
            out["error"] = "; ".join(reply.errors[:2]) or None
    except M.ModelError as exc:
        out["error"] = f"model: {exc}"[:400]
    out["seconds"] = round(time.time() - t0, 2)
    out["score"] = score_item(item, out["answer"] if out["error"] is None or item["task"] == "T5" else None)
    return out


def _session(model, item: dict, registry, used: Callable) -> tuple[dict, Optional[str]]:
    """T5: the plan call, ``loop.check_plan``, then one session reply with the offered tools."""
    from wenart.agent import loop as LP
    from wenart.agent import prompts as P
    brief, offered = item["brief"], list(item.get("offered") or [])
    messages = [{"role": "system", "content": P.PLANNER_SYSTEM_M12},
                {"role": "user", "content": P.plan_prompt(1, brief, offered, False)}]
    plan_reply = model.structured(messages, P.PLAN_SCHEMA, call_id=f"{item['id']}-plan", name="plan", kind="plan",
                                  thinking=model.planner_thinking)
    used(plan_reply)
    steps, problems = LP.check_plan(plan_reply.data, brief, offered)
    plan_ok = plan_reply.data is not None and bool(steps) and not problems
    checklist = steps or LP.default_checklist(brief)
    messages = [{"role": "system", "content": P.PLANNER_SYSTEM_M12},
                {"role": "user", "content": P.session_task(1, brief, checklist, problems, LP.MAX_CALLS_PER_ROOM,
                                                           False)}]
    reply = model.chat(messages, registry.specs(offered), call_id=f"{item['id']}-p1")
    used(reply)
    calls = [judge_call(tc.name, tc.parsed, tc.error, item, checklist, registry) for tc in reply.tool_calls]
    return ({"plan": plan_reply.data, "plan_errors": plan_reply.errors[:3], "plan_problems": problems[:6],
             "plan_ok": plan_ok, "checklist": [{k: s.get(k) for k in ("tool", "target", "finding_ids")}
                                                for s in checklist],
             "calls": calls, "content": (reply.content or "")[:400]}, None)


def run_order(items: list[dict]) -> list[dict]:
    """The long T5 sessions first, then T1-T4 taken in turn (one of each task, then the next), so a time cap cuts
    every task about the same."""
    first = [it for it in items if it["task"] == "T5"]
    queues = [[it for it in items if it["task"] == t] for t in TASKS if t != "T5"]
    rest = []
    for k in range(max((len(q) for q in queues), default=0)):
        rest += [q[k] for q in queues if k < len(q)]
    return first + rest


def run_variant(model, items: list[dict], items_dir: Path, *, workers: int = WORKERS,
                cap_s: float = VARIANT_CAP_S, deadline: Optional[float] = None, clock: Callable = time.time,
                registry=None, root: Path = REPO_ROOT, on_done: Optional[Callable[[dict], None]] = None) -> dict:
    """Every item, ``workers`` at a time; an item not started before the cap or the deadline is ``skipped``."""
    from wenart.agent import tools as TL
    registry = registry or TL.build_registry()
    stop_at = clock() + cap_s
    if deadline is not None:
        stop_at = min(stop_at, deadline)
    results: dict = {}
    lock = threading.Lock()

    def one(item):
        if clock() > stop_at:
            res = {"id": item["id"], "task": item["task"], "status": "skipped", "error": "time cap",
                   "score": score_item(item, None), "call_seconds": []}
        else:
            res = answer_item(model, item, items_dir, registry, root)
        with lock:
            results[item["id"]] = res
        if on_done is not None:
            on_done(res)
        return res

    t0 = clock()
    order = run_order(items)
    if workers <= 1:
        for it in order:
            one(it)
    else:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            list(ex.map(one, order))
    return {"results": results, "wall_s": round(clock() - t0, 1), "metrics": aggregate(items, results)}


def gpu_memory() -> list[dict]:
    """``[{"index", "used_mib", "total_mib"}]`` of every GPU (nvidia-smi); [] without one."""
    try:
        text = subprocess.run(["nvidia-smi", "--query-gpu=index,memory.used,memory.total",
                               "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout
    except (OSError, subprocess.SubprocessError):
        return []
    out = []
    for line in text.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 3 and all(p.isdigit() for p in parts):
            out.append({"index": int(parts[0]), "used_mib": int(parts[1]), "total_mib": int(parts[2])})
    return out


class PeakSampler:
    """The peak VRAM per GPU, sampled every ``every_s`` in a thread (``with PeakSampler() as s: ...; s.peak``)."""

    def __init__(self, every_s: float = 2.0, read: Callable[[], list] = gpu_memory):
        self.every_s, self.read = every_s, read
        self.peak: dict = {}
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def sample(self) -> None:
        for g in self.read():
            self.peak[g["index"]] = max(self.peak.get(g["index"], 0), g["used_mib"])

    def __enter__(self):
        self.sample()

        def loop():
            while not self._stop.wait(self.every_s):
                self.sample()
        self._thread = threading.Thread(target=loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=10)
        self.sample()
        return False


def render_command(py: str, scene: Path, out_dir: Path, camera: str) -> list[str]:
    return [py, "-m", "wenart.blender.cli", "render", "--scene", str(scene), "--out", str(out_dir), "--cameras",
            camera, "--samples", str(CYCLES_SAMPLES), "--res", CYCLES_RES, "--force"]


def start_render(scene: Optional[Path], device: str, out_dir: Path, py: str) -> tuple[Optional[subprocess.Popen],
                                                                                         dict]:
    """A Cycles render of one interior camera of ``scene`` on GPU ``device`` (next to the model server)."""
    if scene is None or not Path(scene).is_file():
        return None, {"skipped": f"no scene {scene}"}
    try:
        manifest = read_json(Path(scene).parent / "scene_manifest.json")
    except (OSError, ValueError) as exc:
        return None, {"skipped": f"no scene manifest: {exc}"}
    cam = next((c["name"] for c in manifest.get("cameras") or [] if c.get("room_id")), None)
    if cam is None:
        return None, {"skipped": "no interior camera"}
    env = dict(os.environ, CUDA_VISIBLE_DEVICES=str(device).split(",")[0])
    out_dir.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(render_command(py, Path(scene), out_dir, cam), cwd=str(REPO_ROOT), env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return proc, {"camera": cam, "device": str(device).split(",")[0], "started": time.time()}


def finish_render(proc: Optional[subprocess.Popen], info: dict, timeout_s: float = 900.0) -> dict:
    if proc is None:
        return info
    try:
        rc = proc.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        rc = "timeout"
    return dict({k: v for k, v in info.items() if k != "started"}, render_rc=rc,
                render_seconds=round(time.time() - info["started"], 1))


def model_name(key: str) -> str:
    return key.split(".")[-1]


def run_model(key: str, out_dir: Path, *, url: Optional[str] = None, variants: Optional[list] = None,
              device: Optional[str] = None, port: int = 8001, items_path: Optional[Path] = None,
              deadline: Optional[float] = None, cap_s: float = VARIANT_CAP_S, workers: int = WORKERS,
              scene: Optional[Path] = None, gpu_tests: bool = False, tasks: tuple = TASKS) -> dict:
    """Serve ``check.yaml models.<key>`` (unless ``url``), run every variant, write ``<out>/<name>.json`` and
    ``<out>/<name>-<variant>.json`` (module docstring)."""
    from wenart.agent import model as M
    from wenart.run import servers as SV
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = model_name(key)
    entry = SV.model_entry(SV.check_models(), key) or {}
    variants = variants or list((entry.get("variants") or {"default": {}}).keys())
    items, items_dir = load_items(items_path)
    items = [it for it in items if it["task"] in tasks]
    facts: dict = {"key": key, "name": name, "model": entry.get("id"), "revision": entry.get("revision"),
                   "gpus": int(entry.get("gpus") or 1), "device": device, "variants": {}, "started": time.time(),
                   "vram_before": gpu_memory(), "vllm": SV.default_vllm()}
    facts_path = out_dir / f"{name}.json"
    write_json(facts_path, facts)
    stats: list = []
    py = os.environ.get("WENART_PY") or "/workspace/venv/bin/python"
    logs = Path(os.environ.get("WENART_LOGS", "/workspace/logs"))
    work = Path(os.environ.get("WENART_JOB_DIR", str(out_dir)))
    job_dir = work / f"server-{name}"
    render_dir = work                       # the Cycles render (large files) stays out of the results
    try:
        if url:
            ctx = SV.external_server(url, key, stats=stats)
        else:
            ctx = SV.server(key, deadline, stats=stats, seqs=int(entry.get("max_seqs") or workers), port=port,
                            logs_dir=logs, job_dir=job_dir, devices=device,
                            mem_mib=max((g["total_mib"] for g in gpu_memory()), default=None))
        with ctx as served:
            facts["server"] = dict(stats[-1]) if stats else {}
            facts["vram_server"] = gpu_memory()
            write_json(facts_path, facts)
            for k, variant in enumerate(variants):
                if deadline is not None and time.time() > deadline:
                    facts["variants"][variant] = {"skipped": "deadline"}
                    break
                model = M.from_check_yaml(served, key, variant=None if variant == "default" else variant,
                                          timeout_s=600.0)
                proc, render = (start_render(scene, device or "0", render_dir / f"render-{name}", py)
                                if k == 0 else (None, {"skipped": "first variant only"}))
                with PeakSampler() as sampler:
                    res = run_variant(model, items, items_dir, workers=workers, cap_s=cap_s, deadline=deadline)
                    render = finish_render(proc, render)
                record = {"key": key, "name": name, "variant": variant, "model": entry.get("id"),
                          "revision": entry.get("revision"), "gpus": facts["gpus"], "wall_s": res["wall_s"],
                          "metrics": res["metrics"], "vram_peak": sampler.peak, "cycles": render,
                          "results": res["results"]}
                write_json(out_dir / f"{name}-{variant}.json", record)
                facts["variants"][variant] = {"wall_s": res["wall_s"], "combined": res["metrics"].get("combined"),
                                              "cycles": render, "vram_peak": sampler.peak}
                write_json(facts_path, facts)
            if gpu_tests:
                facts["gpu_tests"] = run_gpu_tests(served, key, out_dir)
    except SV.ServerError as exc:
        facts["server"] = {"error": str(exc), "reason": exc.reason, "stats": stats}
    facts["finished"] = time.time()
    write_json(facts_path, facts)
    return facts


def run_gpu_tests(url: str, key: str, out_dir: Path) -> dict:
    """``pytest -m gpu tests/gpu/test_agent.py`` against this server (``WENART_AGENT_URL``)."""
    env = dict(os.environ, WENART_AGENT_URL=url, AGENT_TEST_MODEL=key)
    cmd = [os.environ.get("WENART_PY") or "python3", "-m", "pytest", "-m", "gpu", "tests/gpu/test_agent.py", "-q",
           "-ra", f"--junitxml={out_dir / f'junit-agent-{model_name(key)}.xml'}"]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=1800)
    return {"rc": proc.returncode, "tail": proc.stdout.strip().splitlines()[-5:]}


# --------------------------------------------------------------------------
# Summary and the decision rule
# --------------------------------------------------------------------------

def row_of(record: dict) -> dict:
    m = record.get("metrics") or {}
    t = lambda task, k="accuracy": (m.get(task) or {}).get(k)  # noqa: E731
    items = sum((m.get(x) or {}).get("items", 0) for x in TASKS)
    answered = sum((m.get(x) or {}).get("answered", 0) for x in TASKS)
    peak = record.get("vram_peak") or {}
    cycles = record.get("cycles") or {}
    return {"name": record.get("name"), "variant": record.get("variant"), "model": record.get("model"),
            "gpus": int(record.get("gpus") or 1),
            **{task: (round(100 * t(task), 1) if t(task) is not None else None) for task in SCORED},
            "combined": m.get("combined"), "T2_false": t("T2", "false_findings"), "T2_recall": t("T2", "recall"),
            "T4_false": t("T4", "false_findings"), "T5": round(100 * t("T5"), 1) if t("T5") is not None else None,
            "T5_valid": t("T5", "valid_rate"), "T5_allowed": t("T5", "allowed_rate"),
            "T5_in_plan": t("T5", "in_plan_rate"), "T5_plans_ok": t("T5", "plans_ok"),
            "answered": round(answered / items, 3) if items else 0.0, "s_per_call": m.get("s_per_call"),
            "tokens_per_call": m.get("completion_tokens_per_call"), "wall_s": record.get("wall_s"),
            "vram_peak_mib": max(peak.values()) if peak else None,
            "cycles_rc": cycles.get("render_rc"), "cycles_s": cycles.get("render_seconds"),
            "cycles_note": cycles.get("skipped")}


def eligible(row: dict) -> bool:
    return row.get("combined") is not None and row["answered"] >= MIN_ANSWERED and \
        (row.get("T5_valid") or 0.0) >= MIN_T5_VALID


def _best(rows: list[dict]) -> Optional[dict]:
    if not rows:
        return None
    top = max(r["combined"] for r in rows)
    near = [r for r in rows if r["combined"] >= top - TIE_POINTS]
    return min(near, key=lambda r: (r.get("s_per_call") or 1e9, -r["combined"], str(r["name"]), str(r["variant"])))


def decide(rows: list[dict]) -> dict:
    """The pick (module docstring): the best single-GPU row, or the best 2-GPU row when it is >= 10 points better
    on T1-T4."""
    ok = [r for r in rows if eligible(r)]
    single = _best([r for r in ok if r["gpus"] == 1])
    double = _best([r for r in ok if r["gpus"] >= 2])
    pick, why = single, "the best single-GPU model"
    if double is not None and (single is None or double["combined"] >= single["combined"] + TWO_GPU_MARGIN):
        pick = double
        why = ("the 2-GPU model is >= 10 points better on T1-T4" if single else "no single-GPU model qualified")
    elif double is not None:
        why = (f"the best 2-GPU model ({double['name']} {double['variant']}, {double['combined']}) is less than "
               f"{TWO_GPU_MARGIN:.0f} points above the best single-GPU model ({single['combined']})")
    if pick is None:
        why = "no model qualified (answered >= 90 % of the items and >= 80 % valid tool calls)"
    return {"pick": None if pick is None else {k: pick[k] for k in ("name", "variant", "model", "gpus", "combined")},
            "why": why, "best_single": single and {k: single[k] for k in ("name", "variant", "combined")},
            "best_two_gpu": double and {k: double[k] for k in ("name", "variant", "combined")},
            "not_eligible": [f"{r['name']} {r['variant']}" for r in rows if not eligible(r)]}


COLUMNS = (("name", "model"), ("variant", "variant"), ("gpus", "GPUs"), ("T1", "T1 %"), ("T2", "T2 %"),
           ("T3", "T3 %"), ("T4", "T4 %"), ("combined", "T1-T4"), ("T2_false", "T2 false"),
           ("T4_false", "T4 false"), ("T5", "T5 %"), ("T5_valid", "T5 valid"), ("T5_allowed", "T5 allowed"),
           ("T5_in_plan", "T5 in plan"), ("answered", "answered"), ("s_per_call", "s/call"),
           ("tokens_per_call", "tokens/call"), ("vram_peak_mib", "VRAM peak MiB"), ("cycles_rc", "Cycles rc"))


def summary(out_dir: Path = OUT) -> dict:
    """``summary.json`` and ``summary.md`` from every ``<name>-<variant>.json`` and ``<name>.json`` of ``out_dir``."""
    out_dir = Path(out_dir)
    rows, servers = [], {}
    for p in sorted(out_dir.glob("*.json")):
        if p.name in ("summary.json",):
            continue
        try:
            data = read_json(p)
        except (OSError, ValueError):
            continue
        if "variant" in data and "metrics" in data:
            rows.append(row_of(data))
        elif "variants" in data and "key" in data:
            servers[data["name"]] = {"model": data.get("model"), "server": data.get("server"),
                                     "vram_server": data.get("vram_server"), "gpu_tests": data.get("gpu_tests")}
    rows.sort(key=lambda r: (str(r["name"]), str(r["variant"])))
    decision = decide(rows)
    data = {"rows": rows, "servers": servers, "decision": decision,
            "rule": f"2-GPU only when >= {TWO_GPU_MARGIN:.0f} points better on T1-T4; answered >= "
                    f"{MIN_ANSWERED:.0%}, T5 valid calls >= {MIN_T5_VALID:.0%}"}
    write_json(out_dir / "summary.json", data)
    lines = ["# Milestone 12 P1: agent model bake-off", "",
             "Tasks: T1 plan-crop typing (40), T2 planted layout errors (30 rooms), T3 best of 3 layouts (20), "
             "T4 decor and wrong objects in renders (20), T5 plan + tool calls on room briefs (20). "
             "T1-T4 = the mean of the four accuracies (points).", "",
             "| " + " | ".join(h for _k, h in COLUMNS) + " |", "|" + "---|" * len(COLUMNS)]
    for r in rows:
        lines.append("| " + " | ".join("" if r.get(k) is None else str(r.get(k)) for k, _h in COLUMNS) + " |")
    lines += ["", f"Rule: {data['rule']}.", ""]
    pick = decision["pick"]
    lines.append(f"**Pick: {pick['name']} {pick['variant']} ({pick['model']}, {pick['combined']} points)** - "
                 f"{decision['why']}." if pick else f"**No pick**: {decision['why']}.")
    for name, s in sorted(servers.items()):
        err = (s.get("server") or {}).get("error")
        if err:
            lines.append(f"- {name}: server failed: {err}")
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return data


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def started(out_dir: Path, name: str) -> bool:
    """The server of bake-off model ``name`` started (no server error) and at least one variant ran."""
    try:
        facts = read_json(Path(out_dir) / f"{name}.json")
    except (OSError, ValueError):
        return False
    ran = any(isinstance(v, dict) and "wall_s" in v for v in (facts.get("variants") or {}).values())
    return not (facts.get("server") or {}).get("error") and ran


def models_lines() -> list[str]:
    """``name key id revision gpus size_gb variants`` of every bake-off model (the job script reads them)."""
    from wenart.run import servers as SV
    table = SV.check_models().get("bakeoff") or {}
    out = []
    for name, m in table.items():
        if isinstance(m, dict) and m.get("id"):
            out.append(f"{name} bakeoff.{name} {m['id']} {m.get('revision') or '-'} {int(m.get('gpus') or 1)} "
                       f"{m.get('size_gb') or 0} {','.join((m.get('variants') or {'default': {}}).keys())}")
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m wenart.agent.bakeoff", description="M12 P1 agent model bake-off")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="items.json + images from tasks.json (CPU)")
    b.add_argument("--spec", default=str(SPEC_PATH))
    b.add_argument("--out", default=str(FIXTURE))
    b.add_argument("--tasks", default=",".join(TASKS))
    sub.add_parser("models", help="the bake-off models of check.yaml, one per line")
    r = sub.add_parser("run", help="serve one model and run every variant (pod)")
    r.add_argument("--key", required=True, help="check.yaml key, e.g. bakeoff.fp8")
    r.add_argument("--variants", default="", help="comma list; default: every variant of the key")
    r.add_argument("--device", default=None, help="CUDA_VISIBLE_DEVICES of the server (0, 1 or 0,1)")
    r.add_argument("--port", type=int, default=8001)
    r.add_argument("--url", default=None, help="a server that is already up")
    r.add_argument("--out", default=str(OUT))
    r.add_argument("--items", default=None)
    r.add_argument("--cap-s", type=float, default=VARIANT_CAP_S)
    r.add_argument("--workers", type=int, default=WORKERS)
    r.add_argument("--scene", default=None, help="scene.blend for the Cycles render next to the server")
    r.add_argument("--gpu-tests", action="store_true", help="pytest -m gpu tests/gpu/test_agent.py on this server")
    r.add_argument("--tasks", default=",".join(TASKS))
    s = sub.add_parser("summary", help="summary.json / summary.md and the pick")
    s.add_argument("--out", default=str(OUT))
    st = sub.add_parser("started", help="exit 0 when the model's server started and a variant ran (the job)")
    st.add_argument("--out", default=str(OUT))
    st.add_argument("--name", required=True)
    a = p.parse_args(argv)
    if a.cmd == "build":
        res = build(Path(a.spec), Path(a.out), tasks=tuple(t for t in a.tasks.split(",") if t))
        print(f"bake-off items: {res['counts']} -> {res['path']}")
        return 0
    if a.cmd == "models":
        print("\n".join(models_lines()))
        return 0
    if a.cmd == "run":
        deadline = float(os.environ["WENART_DEADLINE"]) if os.environ.get("WENART_DEADLINE", "").strip() else None
        facts = run_model(a.key, Path(a.out), url=a.url, variants=[v for v in a.variants.split(",") if v] or None,
                          device=a.device, port=a.port, items_path=Path(a.items) if a.items else None,
                          deadline=deadline, cap_s=a.cap_s, workers=a.workers,
                          scene=Path(a.scene) if a.scene else None, gpu_tests=a.gpu_tests,
                          tasks=tuple(t for t in a.tasks.split(",") if t))
        err = (facts.get("server") or {}).get("error")
        print(f"bake-off {a.key}: " + (f"server FAILED: {err}" if err else
                                        ", ".join(f"{v}={d.get('combined')}" for v, d in facts["variants"].items())))
        return 1 if err else 0
    if a.cmd == "started":
        return 0 if started(Path(a.out), a.name) else 1
    if a.cmd == "summary":
        data = summary(Path(a.out))
        pick = data["decision"]["pick"]
        print(f"bake-off summary: {len(data['rows'])} rows; pick: "
              + (f"{pick['name']} {pick['variant']} ({pick['combined']})" if pick else "none")
              + f" - {data['decision']['why']}")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
