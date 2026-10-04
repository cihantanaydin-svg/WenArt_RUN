"""A toy project for the vision-check tests: one room, one camera, a numpy ray caster.

The room is 6 x 4 m (inner faces x = 0..6, y = 0..4, ceiling 2.7 m) with
20 cm walls whose centre lines sit 10 cm outside. A door and a window are in
the south wall (their leaf/glass on the wall centre line, y = -0.1, as the
Blender build makes them); a sofa, a coffee table, an armchair, an
unverified proxy and a plant stand in the room. The camera looks south with
the pinhole of ``wenart/blender/cameras.py``.

``raycast`` renders the index, planar depth and world-normal maps of any
subset of the boxes, so a test can drop or move a piece in the render while
the building JSON keeps it (the JSON cross-check cases), and
``write_toy_project`` lays out ``outputs/toy`` the way the M5 jobs do:
``scene/scene_manifest.json``, ``renders/`` (+ PNGs and helper passes),
``building_final.json``, optional ``polish/`` and ``controls/hide_<id>/``.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from wenart import views as V

SIZE = (160, 90)
CAMERA = {"name": "cam_r_salon_1", "room_id": "r_salon", "level_id": "L0", "index": 1,
          "position": [3.0, 3.8, 1.7], "target": [3.0, 0.0, 1.0], "lens_mm": 24.0, "sensor_mm": 36.0,
          "resolution": list(SIZE)}
ROOM = (0.0, 6.0, 0.0, 4.0, 0.0, 2.7)          # x0 x1 y0 y1 z0 z1 (inner faces)
WALL_Y = -0.1                                   # south wall centre line

EV = [{"file": "plan.png", "page": 1, "method": "vector", "confidence": 1.0, "layer": "MOBILYA"}]

# id -> (kind, type, pass index, centre xy, size wd, height, source, status)
PIECES = {
    "f_sofa": ("furniture", "sofa", 3, (3.0, 0.55), (2.0, 0.9), 0.85, "from_documents", "verified"),
    "f_table": ("furniture", "table_coffee", 4, (3.0, 1.8), (1.0, 0.6), 0.45, "from_documents", "verified"),
    "f_arm": ("furniture", "armchair", 5, (4.2, 1.5), (0.8, 0.8), 0.85, "added_by_ai", "verified"),
    "f_unk": ("furniture_proxy", "unknown", 6, (1.0, 0.5), (0.6, 0.5), 0.8, "from_documents", "unverified"),
    "dec_plant": ("decor", "plant", 7, (5.2, 0.4), (0.4, 0.4), 0.5, "added_by_ai", "assumed"),
}
# id -> (type, pass index, x0, x1, z0, z1) on the south wall
OPENINGS = {
    "d_1": ("door", 2, 0.75, 1.65, 0.0, 2.1),
    "win_1": ("window", 1, 3.9, 5.1, 0.9, 2.1),
}


# --------------------------------------------------------------------------
# Building JSON and scene manifest
# --------------------------------------------------------------------------

def toy_building(project_dir: str | None = None) -> dict:
    walls = [
        {"id": "w_s", "level_id": "L0", "start": [-0.1, -0.1], "end": [6.1, -0.1], "thickness": 0.2,
         "status": "verified", "evidence": EV},
        {"id": "w_e", "level_id": "L0", "start": [6.1, -0.1], "end": [6.1, 4.1], "thickness": 0.2,
         "status": "verified", "evidence": EV},
        {"id": "w_n", "level_id": "L0", "start": [6.1, 4.1], "end": [-0.1, 4.1], "thickness": 0.2,
         "status": "verified", "evidence": EV},
        {"id": "w_w", "level_id": "L0", "start": [-0.1, 4.1], "end": [-0.1, -0.1], "thickness": 0.2,
         "status": "verified", "evidence": EV},
    ]
    openings = []
    for oid, (otype, _, x0, x1, _, _) in OPENINGS.items():
        openings.append({"id": oid, "type": otype, "level_id": "L0", "wall_id": "w_s",
                         "center": [(x0 + x1) / 2.0, WALL_Y], "width": round(x1 - x0, 6), "height": None,
                         "sill_height": None, "status": "verified", "evidence": EV})
    furniture, decor = [], []
    for pid, (kind, ptype, _, c, s, h, source, status) in PIECES.items():
        if kind == "decor":
            decor.append({"id": pid, "kind": "decor", "type": ptype, "level_id": "L0", "room_id": "r_salon",
                          "center": list(c), "rotation_deg": 0.0, "size": list(s) + [h], "host_id": None,
                          "source": source, "method": "rule"})
            continue
        furniture.append({"id": pid, "level_id": "L0", "room_id": "r_salon", "type": ptype, "source": source,
                          "footprint": {"center": list(c), "size": list(s), "rotation_deg": 0.0},
                          "front_deg": 90.0, "height": h,
                          "asset": {"method": "library", "bbox_m": [s[0], s[1], h]},
                          "status": status, "evidence": EV})
    return {
        "schema_version": "0.1", "status": "ok",
        "project": {"id": "toy", "source_folder": project_dir},
        "documents": [{"id": "doc_plan_png", "file": "plan.png", "format": "image", "converter": None,
                       "pages": [{"page": 1, "class": "floor_plan", "kind": "vector", "level_id": "L0",
                                  "transform_to_building": [0.01, 0.0, -1.0, 0.0, -0.01, 6.0],
                                  "confidence": 1.0, "evidence": [], "skip_reason": None}]}],
        "levels": [{"id": "L0", "label": "Zemin Kat", "elevation": 0.0, "ceiling_height": 2.7,
                    "ceiling_height_source": "assumed_default"}],
        "walls": walls, "openings": openings,
        "rooms": [{"id": "r_salon", "level_id": "L0", "label": "Salon", "room_type": "living",
                   "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]], "area_computed": 24.0,
                   "has_documented_furniture": True, "status": "verified", "evidence": EV},
                  {"id": "r_hol", "level_id": "L0", "label": "Hol", "room_type": "hall",
                   "polygon": [[0, -3], [3, -3], [3, -0.2], [0, -0.2]], "area_computed": 8.4,
                   "has_documented_furniture": False, "status": "verified", "evidence": EV}],
        "furniture": furniture, "decor": decor, "conflicts": [], "unverified": [], "warnings": [],
    }


def toy_scene(building_path: str, m5: bool = True, extra_objects=()) -> dict:
    """Scene manifest of the toy build; ``m5=False`` leaves out ``room_ids``/``box3d`` (pre-M5)."""
    objects = []
    for oid, (otype, pi, x0, x1, z0, z1) in OPENINGS.items():
        for part in (("frame", "leaf") if otype == "door" else ("frame", "glass")):
            obj = {"name": f"{oid}_{part}", "wenart_id": oid, "kind": otype, "status": "verified",
                   "level_id": "L0", "element_id": oid, "evidence": EV, "pass_index": pi, "wall_id": "w_s"}
            if m5:
                obj["room_ids"] = ["r_salon", "r_hol"] if otype == "door" else ["r_salon"]
            objects.append(obj)
    for pid, (kind, ptype, pi, c, s, h, source, status) in PIECES.items():
        wid = f"proxy:{pid}" if kind == "furniture_proxy" else pid
        obj = {"name": f"furn_{pid}", "wenart_id": wid, "kind": kind, "status": status, "level_id": "L0",
               "element_id": pid, "room_id": "r_salon", "type": ptype, "source": source, "evidence": EV,
               "pass_index": pi, "center": [c[0], c[1], h / 2.0], "size": [s[0], s[1], h], "rotation_deg": 0.0}
        if kind == "decor":
            obj["host_id"] = None
        if m5:
            obj["box3d"] = {"center": [c[0], c[1], h / 2.0], "size": [s[0], s[1], h], "rotation_deg": 0.0}
        objects.append(obj)
    objects.append({"name": "decor_f_sofa_1", "wenart_id": "f_sofa", "kind": "decor", "host_id": "f_sofa",
                    "type": "cushion", "room_id": "r_salon", "level_id": "L0", "source": "added_by_ai",
                    "status": "assumed", "evidence": [], "pass_index": 3})
    objects += list(extra_objects)
    return {"schema_version": "0.1", "project": "toy", "building": building_path,
            "style_profile": {"walls": {"material": "plaster_white"}},
            "objects": objects, "cameras": [dict(CAMERA)], "pass_index": {}}


# --------------------------------------------------------------------------
# Ray caster
# --------------------------------------------------------------------------

def _basis(camera):
    pos = np.array(camera["position"], float)
    f = np.array(camera["target"], float) - pos
    f /= np.linalg.norm(f)
    r = np.cross(f, [0.0, 0.0, 1.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return pos, f, r, u


def raycast(boxes: dict, openings: dict, size=SIZE, camera=CAMERA):
    """``(index uint16, depth_mm uint16, normal float HxWx3)`` of the room with ``boxes`` and ``openings``.

    ``boxes``: ``{index: (centre xy, size wd, height)}`` (axis-aligned);
    ``openings``: ``{index: (x0, x1, z0, z1)}`` in the south wall (leaf/glass at
    y = -0.1); a hole without an opening shows background (depth 0).
    """
    W, H = size
    pos, f, r, u = _basis(camera)
    fpx = camera["lens_mm"] / camera["sensor_mm"] * W
    us = (np.arange(W) + 0.5 - W / 2.0) / fpx
    vs = -(np.arange(H) + 0.5 - H / 2.0) / fpx
    A, B = np.meshgrid(us, vs)
    d = f[None, None, :] + A[..., None] * r[None, None, :] + B[..., None] * u[None, None, :]
    d = d.reshape(-1, 3)
    n = len(d)
    t_best = np.full(n, np.inf)
    index = np.zeros(n, dtype=np.int64)
    normal = np.zeros((n, 3))
    x0, x1, y0, y1, z0, z1 = ROOM
    eps = 1e-9
    planes = [(0, x0, (1, 0, 0)), (0, x1, (-1, 0, 0)), (1, y0, (0, 1, 0)), (1, y1, (0, -1, 0)),
              (2, z0, (0, 0, 1)), (2, z1, (0, 0, -1))]
    with np.errstate(divide="ignore", invalid="ignore"):
        for axis, value, nrm in planes:
            t = (value - pos[axis]) / d[:, axis]
            p = pos + t[:, None] * d
            ok = (t > 1e-6) & (p[:, 0] >= x0 - 1e-6) & (p[:, 0] <= x1 + 1e-6) & (p[:, 1] >= y0 - 1e-6) \
                & (p[:, 1] <= y1 + 1e-6) & (p[:, 2] >= z0 - 1e-6) & (p[:, 2] <= z1 + 1e-6) & (t < t_best)
            t_best[ok] = t[ok]
            index[ok] = 0
            normal[ok] = nrm
        # Holes in the south wall: through to the leaf/glass plane (or the background).
        south = np.isclose((pos + t_best[:, None] * d)[:, 1], y0, atol=1e-6) & np.isfinite(t_best)
        p = pos + t_best[:, None] * d
        t2 = (WALL_Y - pos[1]) / d[:, 1]
        p2 = pos + t2[:, None] * d
        for oid, (otype, pi, hx0, hx1, hz0, hz1) in OPENINGS.items():
            hole = south & (p[:, 0] > hx0) & (p[:, 0] < hx1) & (p[:, 2] > hz0) & (p[:, 2] < hz1)
            if pi in openings:
                ox0, ox1, oz0, oz1 = openings[pi]
                on = hole & (p2[:, 0] >= ox0) & (p2[:, 0] <= ox1) & (p2[:, 2] >= oz0) & (p2[:, 2] <= oz1)
                t_best[on] = t2[on]
                index[on] = pi
                normal[on] = (0, 1, 0)
                reveal = hole & ~on
                t_best[reveal] = t2[reveal]
                index[reveal] = 0
                normal[reveal] = (1, 0, 0)
            else:
                t_best[hole] = np.inf
                index[hole] = 0
                normal[hole] = 0
        for pi, (c, s, h) in boxes.items():
            lo = np.array([c[0] - s[0] / 2.0, c[1] - s[1] / 2.0, 0.0])
            hi = np.array([c[0] + s[0] / 2.0, c[1] + s[1] / 2.0, h])
            t0 = (lo - pos) / d
            t1 = (hi - pos) / d
            tmin = np.minimum(t0, t1)
            tmax = np.maximum(t0, t1)
            tn = tmin.max(axis=1)
            tf = tmax.min(axis=1)
            hit = (tn <= tf) & (tn > 1e-6) & (tn < t_best)
            axis = tmin.argmax(axis=1)
            t_best[hit] = tn[hit]
            index[hit] = pi
            nn = np.zeros((n, 3))
            nn[np.arange(n), axis] = -np.sign(d[np.arange(n), axis])
            normal[hit] = nn[hit]
    depth_m = np.where(np.isfinite(t_best), t_best, 0.0)          # planar depth (d . f == 1)
    return (index.reshape(H, W).astype(np.uint16), V.encode_depth_mm(depth_m.reshape(H, W)),
            normal.reshape(H, W, 3))


def default_boxes(drop=(), shift=None) -> dict:
    """Boxes of every piece by pass index; ``drop`` ids are left out, ``shift={id: (dx, dy)}`` moves one."""
    out = {}
    for pid, (_, _, pi, c, s, h, _, _) in PIECES.items():
        if pid in drop:
            continue
        dx, dy = (shift or {}).get(pid, (0.0, 0.0))
        out[pi] = ((c[0] + dx, c[1] + dy), s, h)
    return out


def default_openings(drop=()) -> dict:
    return {pi: (x0, x1, z0, z1) for oid, (_, pi, x0, x1, z0, z1) in OPENINGS.items() if oid not in drop}


def colour_image(index: np.ndarray, depth: np.ndarray) -> np.ndarray:
    """A plain RGB picture of the render (index colours, darker with distance)."""
    rng = np.random.default_rng(1)
    lut = rng.integers(40, 230, size=(int(index.max()) + 1, 3)).astype(np.float64)
    lut[0] = (200, 200, 190)
    shade = np.clip(1.2 - depth.astype(np.float64) / 8000.0, 0.3, 1.0)[..., None]
    return np.clip(lut[index] * shade, 0, 255).astype(np.uint8)


# --------------------------------------------------------------------------
# Project layout
# --------------------------------------------------------------------------

def write_render(render_dir: Path, camera: str, index, depth, normal, *, hidden=(), plugged=(), rgb=None,
                 name_suffix: str = "") -> dict:
    """Write the PNGs of one view and return its M5 render-manifest entry."""
    render_dir.mkdir(parents=True, exist_ok=True)
    stem = camera + name_suffix
    rgb = colour_image(index, depth) if rgb is None else rgb
    V.write_png_rgb(render_dir / f"{stem}.png", rgb)
    V.write_png16(render_dir / f"{stem}_index.png", index)
    V.write_png16(render_dir / f"{stem}_depth_mm.png", depth)
    V.write_png_rgb(render_dir / f"{stem}_normal.png", V.encode_normal(normal, V.normal_hit(normal)))
    stats = V.compute_index_stats(index)
    H, W = index.shape
    return {"camera": camera, "png": f"{stem}.png", "exr": f"{stem}_passes.exr", "preview": f"{stem}_preview.jpg",
            "index_png": f"{stem}_index.png", "seconds": 1.0, "samples": 16, "resolution": [W, H],
            "index_values": sorted(stats), "room_id": CAMERA["room_id"], "level_id": "L0",
            "index_stats": {str(k): v for k, v in sorted(stats.items())},
            "files": {"index": f"{stem}_index.png", "depth_mm": f"{stem}_depth_mm.png", "normal": f"{stem}_normal.png"},
            "render_key": "toy0123456789abc", "hidden": list(hidden), "plugged": list(plugged), "scene_sha256": "x"}


def write_manifest(render_dir: Path, entries: list) -> None:
    render_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"schema_version": "0.1", "scene": "../scene/scene.blend", "renders": entries}
    (render_dir / "render_manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")


def write_plan_png(path: Path) -> None:
    """A 'scanned plan' whose page pixels map to the building by [0.01, 0, -1, 0, -0.01, 6]."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (900, 1000), "white")
    draw = ImageDraw.Draw(img)
    # room outline: building (0,0)-(6,4) -> pixels x = (X + 1) * 100, y = (6 - Y) * 100
    draw.rectangle([100, 200, 700, 600], outline=(0, 0, 0), width=3)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def write_toy_project(root: Path, *, drop=(), shift=None, m5: bool = True, extra_objects=(), polished: bool = False,
                      controls=(), size=SIZE) -> Path:
    """``root/outputs/toy`` with a scene manifest, the building, the Cycles render and optional extras.

    ``drop``/``shift``: pieces left out of / moved in the render (the building keeps them as drawn);
    ``polished``: a polish manifest whose final attempt is a copy of the render;
    ``controls``: ids rendered hidden into ``controls/hide_<id>/``.
    """
    out = Path(root) / "outputs" / "toy"
    project_dir = Path(root) / "projects" / "toy"
    write_plan_png(project_dir / "plan.png")
    building = toy_building(str(project_dir))
    (out / "scene").mkdir(parents=True, exist_ok=True)
    bpath = out / "building_final.json"
    bpath.write_text(json.dumps(building, indent=1), encoding="utf-8")
    scene = toy_scene(str(bpath), m5=m5, extra_objects=extra_objects)
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene, indent=1), encoding="utf-8")
    boxes = default_boxes(drop=drop, shift=shift)
    for obj in extra_objects:
        c, s = obj["center"], obj["size"]
        boxes[obj["pass_index"]] = ((c[0], c[1]), (s[0], s[1]), s[2])
    index, depth, normal = raycast(boxes, default_openings(drop=drop), size)
    cam = CAMERA["name"]
    entry = write_render(out / "renders", cam, index, depth, normal)
    write_manifest(out / "renders", [entry])
    if polished:
        rgb = V.read_rgb(out / "renders" / f"{cam}.png")
        pdir = out / "polish"
        V.write_png_rgb(pdir / f"{cam}_a1.png", np.clip(rgb.astype(int) + 5, 0, 255).astype(np.uint8))
        pm = {"schema_version": "0.1", "kind": "run", "project": "toy",
              "views": [{"camera": cam, "room_id": "r_salon", "final": "polished", "final_attempt": 1, "reason": None,
                         "attempts": [{"k": 1, "role": "ladder", "strength": 0.375, "png": f"{cam}_a1.png",
                                       "gate": {"decision": "accept"}}]}]}
        (pdir / "polish_manifest.json").write_text(json.dumps(pm, indent=1), encoding="utf-8")
    for cid in controls:
        write_control(out, cid, drop=drop, shift=shift, size=size)
    return out


def write_control(out: Path, cid: str, drop=(), shift=None, size=SIZE) -> Path:
    """``controls/hide_<cid>/``: the camera rendered without ``cid`` (a window keeps a closed wall: plugged)."""
    piece_drop = (cid,) if cid in PIECES else ()
    oid_drop = (cid,) if cid in OPENINGS else ()
    b = default_boxes(drop=tuple(drop) + piece_drop, shift=shift)
    openings = default_openings(drop=tuple(drop) + oid_drop)
    idx2, dep2, nrm2 = raycast(b, openings, size)
    if cid in OPENINGS and OPENINGS[cid][0] == "window":
        # Plugged: the hole shows the wall plug at the wall face, not the sky.
        hole = dep2 == 0
        idx2[hole] = 0
        dep2[hole] = np.where(hole, 4000, dep2)[hole]
        nrm2[hole] = (0.0, 1.0, 0.0)
    hdir = Path(out) / "controls" / f"hide_{cid}"
    e2 = write_render(hdir, CAMERA["name"], idx2, dep2, nrm2, hidden=[cid],
                      plugged=[cid] if cid in OPENINGS and OPENINGS[cid][0] == "window" else [])
    write_manifest(hdir, [e2])
    return hdir


def fpx(width: int = SIZE[0]) -> float:
    return CAMERA["lens_mm"] / CAMERA["sensor_mm"] * width


def project_point(p) -> tuple[float, float]:
    """Pixel of a world point in the toy camera (independent of the module under test)."""
    pos, f, r, u = _basis(CAMERA)
    d = np.asarray(p, float) - pos
    z = d @ f
    return (SIZE[0] / 2.0 + fpx() * (d @ r) / z, SIZE[1] / 2.0 - fpx() * (d @ u) / z)


def degrees_between(a, b) -> float:
    return math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(a, b))))))


# --------------------------------------------------------------------------
# Fake vision model (the documented client interface: .model and .run_schema)
# --------------------------------------------------------------------------

class FakeClient:
    """A model that answers from a truth table instead of looking.

    Images are named ``<folder>/<file>`` (``renders/cam.png``,
    ``hide_f_arm/cam.png``, ``polish/cam_a1.png``).
    ``truth``: ``{image name: set of types visible}``; an asked element
    whose type is in the set is ``present``, else ``absent`` (so the decoy
    comes back absent unless ``see_all``: then every asked type is present,
    a yes-biased model). Type-unverified pieces are asked as "furniture
    piece" and are present when ``"furniture piece"`` is in the set.
    ``statuses``: ``{(image name, type): (status, seen_as)}`` overrides;
    ``extras``: ``{image name: [extra dicts]}``; ``counts``: ``{image name:
    (doors, windows)}``; ``fail``: image names whose call fails; ``prefer``:
    ``{image name: score}`` for the realism preference (higher wins). Every
    call is recorded in ``calls``.
    """

    def __init__(self, model="fake/model", truth=None, extras=None, counts=None, fail=(), see_all=False,
                 prefer=None, statuses=None):
        self.model = model
        self.truth = truth or {}
        self.extras = extras or {}
        self.counts = counts or {}
        self.fail = set(fail)
        self.see_all = see_all
        self.prefer = prefer or {}
        self.statuses = statuses or {}
        self.calls = []

    def run_schema(self, images, prompt, schema, *, seed=0, task="custom", max_side=None, labels=None,
                   system_prompt=None):
        import re

        from wenart.recognition.vlm_client import VLMResult, schema_errors
        names = [f"{Path(str(i)).parent.name}/{Path(str(i)).name}" for i in images]
        self.calls.append({"images": names, "task": task, "labels": labels, "prompt": prompt})
        if names[0] in self.fail:
            return VLMResult(task=task, model=self.model, data=None, raw_text="", latency_s=0.01, attempts=3,
                             error="cannot reach http://fake: refused")
        if task.startswith("preference"):
            a, b = (self.prefer.get(n, 0) for n in names[:2])
            data = {"choice": "first" if a > b else "second" if b > a else "same", "confidence": 0.8}
        else:
            seen = self.truth.get(names[0], set())
            elements = {}
            for label, what in re.findall(r"^- (E\d+): (.+?) \(", prompt, re.M):
                key = "furniture piece" if what == "furniture piece" else what
                forced = self.statuses.get((names[0], key))
                if forced:
                    status, seen_as = forced
                elif key in seen or self.see_all:
                    status, seen_as = "present", ("other_furniture" if key == "furniture piece" else key)
                else:
                    status, seen_as = "absent", "nothing"
                elements[label] = {"status": status, "seen_as": seen_as, "confidence": 0.9}
            doors, windows = self.counts.get(names[0], (int("door" in seen), int("window" in seen)))
            data = {"elements": elements, "extras": list(self.extras.get(names[0], [])),
                    "door_count": doors, "window_count": windows}
        problems = schema_errors(schema, data)
        if problems:
            return VLMResult(task=task, model=self.model, data=None, raw_text=json.dumps(data), latency_s=0.01,
                             attempts=1, error="schema: " + "; ".join(problems))
        return VLMResult(task=task, model=self.model, data=data, raw_text=json.dumps(data), latency_s=0.01,
                         attempts=1, image_size=(160, 90), page_size=(160, 90))


TOY_TYPES = {"sofa", "armchair", "door", "window", "table_coffee", "furniture piece", "plant"}
