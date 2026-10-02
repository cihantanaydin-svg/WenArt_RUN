"""Shared view loader for Milestone 5 (docs/milestone5.md §1.2).

What: one place that knows how a rendered view is stored and what its pixels
mean. Polish, change gate, vision check and report all read views through
this module, so they agree on file formats, regions, edges and boxes.

- Encoders (``encode_depth_mm``, ``encode_normal``, ``encode_index``) turn the
  Cycles passes into the helper PNGs. ``wenart/blender/render.py`` calls them
  inside Blender, which is why this module imports only the standard library
  and numpy at import time (Pillow is imported inside the readers/writers).
- Readers (``read_rgb``, ``read_index``, ``read_depth_mm``, ``read_normal``)
  use Pillow, never plain ``cv2.imread`` (it turns a uint16 PNG into uint8
  BGR). ``write_png16`` / ``write_png_rgb`` write the same formats, so a
  value above 255 survives the round trip.
- ``View`` + ``load_views``: one rendered camera with absolute file paths and
  its index statistics; an entry written before M5 raises ``StaleRender``.
- ``index_table``: pass index -> element (wenart id, kind, type, room, evidence)
  from the scene manifest; ``regions``: per-object and structure masks;
  ``geometry_edges``: the one definition of geometry edges (polish control and
  gate reference); ``box_to_1000``: the box convention; ``project_paths``: where
  a project's building, style profile and brief come from (§1.1).

File formats (written by render.py, one set per camera):

- ``<cam>.png``: display-referred RGB8 (the image every area works on);
- ``<cam>_index.png``: uint16 grey, pixel = pass index (0 = no indexed object);
- ``<cam>_depth_mm.png``: uint16 grey, Cycles Z (planar depth along the view
  axis) in millimetres, 0 = no surface or farther than 65.535 m;
- ``<cam>_normal.png``: RGB8 world normal, ``round((n + 1) * 127.5)``, (0, 0, 0)
  where no surface was hit.

Boxes: every pixel box is ``[x0, y0, x1, y1]`` with x1/y1 exclusive.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]

DEPTH_BACKGROUND = 1e9          # Cycles writes a huge Z where no surface was hit
DEPTH_MAX_M = 65.535            # largest depth a uint16 millimetre value can hold
INDEX_MAX = 65535

# Structure regions on index-0 pixels, split by the world normal's Z.
STRUCT_FLOOR = "struct:floor"
STRUCT_CEILING = "struct:ceiling"
STRUCT_WALLS = "struct:walls"
STRUCTURE_KINDS = {STRUCT_FLOOR: "floor", STRUCT_CEILING: "ceiling", STRUCT_WALLS: "wall"}
FLOOR_NZ_MIN = 0.9              # floor: nz > 0.9
CEILING_NZ_MAX = -0.9           # ceiling: nz < -0.9
WALL_NZ_ABS_MAX = 0.3           # walls: |nz| < 0.3

# Scene-manifest kind -> element kind (furniture_proxy counts as furniture;
# decor here means hostless decor such as plants; hosted decor is folded
# into its host).
KIND_MAP = {"door": "door", "window": "window", "furniture": "furniture",
            "furniture_proxy": "furniture", "decor": "decor"}
OBJECT_KINDS = ("door", "window", "furniture", "decor")
PROXY_PREFIX = "proxy:"


class StaleRender(Exception):
    """A render-manifest entry written before Milestone 5 (no render_key, index_stats or files).

    Callers skip that view with a warning; ``load_views(..., skip_stale=True)``
    does that for them.
    """

    def __init__(self, camera: str, missing: list[str]) -> None:
        self.camera = camera
        self.missing = list(missing)
        super().__init__(f"{camera}: stale render entry (missing {', '.join(self.missing)}); re-render it")


# --------------------------------------------------------------------------
# Encoders (numpy only; used by render.py inside Blender)
# --------------------------------------------------------------------------

def encode_depth_mm(z_m) -> np.ndarray:
    """Cycles Z in metres -> uint16 millimetres (``round(z * 1000)``).

    0 where the value is not finite, not positive, >= 1e9 (no surface hit) or
    beyond 65.535 m (does not fit uint16). A surface closer than 0.5 mm would
    also round to 0; cameras clip far earlier.
    """
    z = np.asarray(z_m, dtype=np.float64)
    with np.errstate(invalid="ignore"):
        valid = np.isfinite(z) & (z > 0.0) & (z < DEPTH_BACKGROUND) & (z <= DEPTH_MAX_M)
    out = np.zeros(z.shape, dtype=np.uint16)
    out[valid] = np.clip(np.rint(z[valid] * 1000.0), 0, INDEX_MAX).astype(np.uint16)
    return out


def encode_normal(n, hit=None) -> np.ndarray:
    """World normals (H x W x 3, components in -1..1) -> uint8 RGB ``round((n + 1) * 127.5)``.

    ``hit`` (bool H x W) marks pixels where a surface was hit; the others are
    written as (0, 0, 0). ``None`` means "every pixel with a finite, non-zero
    normal". A hit pixel never encodes to (0, 0, 0): a unit normal has a
    component above -1 in at least two channels.
    """
    arr = np.asarray(n, dtype=np.float64)
    if arr.ndim != 3 or arr.shape[2] < 3:
        raise ValueError(f"normal array must be H x W x 3, got shape {arr.shape}")
    arr = arr[:, :, :3]
    finite = np.isfinite(arr).all(axis=2)
    if hit is None:
        mask = finite & (np.abs(np.where(np.isfinite(arr), arr, 0.0)).sum(axis=2) > 0)
    else:
        mask = np.asarray(hit, dtype=bool)
        if mask.shape != arr.shape[:2]:
            raise ValueError(f"hit mask shape {mask.shape} does not match normals {arr.shape[:2]}")
        mask = mask & finite
    safe = np.where(np.isfinite(arr), arr, 0.0)
    out = np.clip(np.rint((safe + 1.0) * 127.5), 0, 255).astype(np.uint8)
    out[~mask] = 0
    return out


def encode_index(index_float) -> np.ndarray:
    """Object-index pass (float) -> uint16 (``rint``, clipped to 0..65535; NaN -> 0)."""
    x = np.asarray(index_float, dtype=np.float64)
    x = np.where(np.isfinite(x), x, 0.0)
    return np.clip(np.rint(x), 0, INDEX_MAX).astype(np.uint16)


def decode_normal(encoded) -> np.ndarray:
    """uint8 RGB normal -> float32 H x W x 3 (``v / 127.5 - 1``); not-hit pixels become (0, 0, 0).

    A decoded hit normal never has an exact 0 component (127.5 is not an
    integer), so ``normal_hit`` can tell hit from not hit.
    """
    v = np.asarray(encoded)
    if v.ndim != 3 or v.shape[2] < 3:
        raise ValueError(f"encoded normal must be H x W x 3, got shape {v.shape}")
    v = v[:, :, :3].astype(np.float32)
    hit = (v > 0).any(axis=2)
    out = v / np.float32(127.5) - np.float32(1.0)
    out[~hit] = 0.0
    return out


def normal_hit(normal) -> np.ndarray:
    """bool H x W: pixels with a surface normal (decoded float or encoded uint8 normals)."""
    arr = np.asarray(normal)
    return (arr[:, :, :3] != 0).any(axis=2)


def compute_index_stats(index) -> dict[int, dict]:
    """``{pass_index: {"pixels": int, "box": [x0, y0, x1, y1]}}`` for every index > 0 in the view.

    Boxes are exclusive at x1/y1. render.py writes this as the entry's
    ``index_stats`` (JSON turns the keys into strings; ``load_views`` turns
    them back into ints).
    """
    idx = np.asarray(index)
    values, counts = np.unique(idx, return_counts=True)
    stats: dict[int, dict] = {}
    for value, count in zip(values.tolist(), counts.tolist()):
        if value <= 0:
            continue
        mask = idx == value
        rows = np.flatnonzero(mask.any(axis=1))
        cols = np.flatnonzero(mask.any(axis=0))
        stats[int(value)] = {"pixels": int(count),
                             "box": [int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1]}
    return stats


# --------------------------------------------------------------------------
# Readers and writers (Pillow, imported lazily)
# --------------------------------------------------------------------------

def read_rgb(path) -> np.ndarray:
    """uint8 H x W x 3 RGB (any PNG/JPEG mode is converted to RGB)."""
    from PIL import Image
    with Image.open(path) as img:
        return np.array(img.convert("RGB"), dtype=np.uint8)


def _read_grey16(path) -> np.ndarray:
    """uint16 H x W from a 16-bit grey PNG (Pillow mode ``I;16*`` or ``I``) or an 8-bit grey PNG."""
    from PIL import Image
    with Image.open(path) as img:
        mode = img.mode
        if mode.startswith("I;16") or mode == "L":
            arr = np.array(img)
        elif mode == "I":
            arr = np.array(img)
            if arr.size and (int(arr.min()) < 0 or int(arr.max()) > INDEX_MAX):
                raise ValueError(f"{path}: values outside 0..65535 in a mode-I image")
        else:
            raise ValueError(f"{path}: expected a 16-bit grey PNG, got Pillow mode {mode}")
    return arr.astype(np.uint16)


def read_index(path) -> np.ndarray:
    """uint16 H x W object-index map (pixel = pass index, 0 = no indexed object)."""
    return _read_grey16(path)


def read_depth_mm(path) -> np.ndarray:
    """uint16 H x W planar depth in millimetres (0 = background / no value)."""
    return _read_grey16(path)


def read_normal(path) -> np.ndarray:
    """float32 H x W x 3 world normal (``v / 127.5 - 1``); not-hit pixels are (0, 0, 0).

    ``normal_hit(read_normal(p))`` gives the hit mask (any encoded channel > 0).
    """
    from PIL import Image
    with Image.open(path) as img:
        v = np.array(img.convert("RGB"), dtype=np.uint8)
    return decode_normal(v)


def _as_uint(array, max_value: int, dtype, what: str) -> np.ndarray:
    a = np.asarray(array)
    if a.dtype == dtype:
        return a
    if a.dtype == bool or not np.issubdtype(a.dtype, np.integer):
        raise ValueError(f"{what}: integer array expected, got {a.dtype}")
    if a.size and (int(a.min()) < 0 or int(a.max()) > max_value):
        raise ValueError(f"{what}: values outside 0..{max_value}")
    return a.astype(dtype)


def write_png16(path, array) -> Path:
    """Write a 2-D array as a 16-bit grey PNG (values must fit 0..65535; no silent wrap)."""
    from PIL import Image
    a = _as_uint(array, INDEX_MAX, np.uint16, "write_png16")
    if a.ndim != 2:
        raise ValueError(f"write_png16: H x W array expected, got shape {a.shape}")
    h, w = a.shape
    img = Image.frombytes("I;16", (w, h), np.ascontiguousarray(a, dtype="<u2").tobytes())
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, format="PNG")
    return path


def write_png_rgb(path, array) -> Path:
    """Write a uint8 H x W x 3 array as an RGB PNG."""
    from PIL import Image
    a = _as_uint(array, 255, np.uint8, "write_png_rgb")
    if a.ndim != 3 or a.shape[2] != 3:
        raise ValueError(f"write_png_rgb: H x W x 3 array expected, got shape {a.shape}")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.ascontiguousarray(a)).save(path, format="PNG")
    return path


# --------------------------------------------------------------------------
# Views
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class View:
    """One rendered camera (an entry of ``render_manifest.json``) with absolute file paths.

    ``size`` is (W, H). ``index_stats`` maps pass index -> {"pixels", "box"}.
    ``exposure`` is the entry's exposure record (None when absent);
    ``hidden``/``plugged`` the ids hidden/plugged for a control render;
    ``entry`` the raw manifest entry.
    """
    camera: str
    room_id: Optional[str]
    level_id: Optional[str]
    size: tuple[int, int]
    png: Path
    index: Path
    depth_mm: Path
    normal: Path
    index_stats: dict = field(default_factory=dict)
    exposure: Optional[dict] = None
    hidden: tuple[str, ...] = ()
    plugged: tuple[str, ...] = ()
    render_key: str = ""
    entry: dict = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash((self.camera, self.render_key, str(self.png)))

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    def read_rgb(self) -> np.ndarray:
        return read_rgb(self.png)

    def read_index(self) -> np.ndarray:
        return read_index(self.index)

    def read_depth_mm(self) -> np.ndarray:
        return read_depth_mm(self.depth_mm)

    def read_normal(self) -> np.ndarray:
        return read_normal(self.normal)


def _stale_fields(entry: dict) -> list[str]:
    missing = []
    if not entry.get("render_key"):
        missing.append("render_key")
    if entry.get("index_stats") is None:
        missing.append("index_stats")
    files = entry.get("files") or {}
    for key in ("depth_mm", "normal"):
        if not files.get(key):
            missing.append(f"files.{key}")
    if not (files.get("index") or entry.get("index_png")):
        missing.append("index_png")
    return missing


def view_from_entry(entry: dict, render_dir, level_id: Optional[str] = None) -> View:
    """A ``View`` from one render-manifest entry; file names resolve against ``render_dir``.

    Raises ``StaleRender`` when the entry has no ``render_key``, no
    ``index_stats``, no ``files.depth_mm``/``files.normal`` or no index PNG.
    """
    camera = entry.get("camera", "?")
    missing = _stale_fields(entry)
    if missing:
        raise StaleRender(camera, missing)
    base = Path(render_dir).resolve()
    files = entry.get("files") or {}
    stats = {int(k): {"pixels": int(v["pixels"]), "box": [int(x) for x in v["box"]]}
             for k, v in (entry.get("index_stats") or {}).items()}
    width, height = (int(v) for v in entry["resolution"])
    return View(
        camera=camera,
        room_id=entry.get("room_id"),
        level_id=entry.get("level_id") or level_id,
        size=(width, height),
        png=base / entry["png"],
        index=base / (files.get("index") or entry["index_png"]),
        depth_mm=base / files["depth_mm"],
        normal=base / files["normal"],
        index_stats=stats,
        exposure=entry.get("exposure"),
        hidden=tuple(entry.get("hidden") or ()),
        plugged=tuple(entry.get("plugged") or ()),
        render_key=entry["render_key"],
        entry=entry,
    )


def _find_scene_manifest(render_dir: Path, manifest: dict) -> Optional[Path]:
    """The scene manifest next to the rendered scene.blend (renders/ or controls/hide_<id>/ layouts)."""
    candidates = []
    scene = manifest.get("scene")
    if scene:
        p = Path(scene)
        candidates.append((p if p.is_absolute() else render_dir / p).parent / "scene_manifest.json")
    candidates.append(render_dir.parent / "scene" / "scene_manifest.json")
    candidates.append(render_dir.parent.parent / "scene" / "scene_manifest.json")
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


def load_views(render_dir, cameras: Optional[Iterable[str]] = None, *, skip_stale: bool = False,
               warnings: Optional[list] = None) -> dict[str, View]:
    """``{camera: View}`` from ``<render_dir>/render_manifest.json`` (manifest order, or the order asked).

    ``cameras``: None or "all" for every entry, else names (an iterable or a
    comma string); an unknown name raises KeyError. A stale entry raises
    ``StaleRender``; with ``skip_stale=True`` it is left out and a message is
    appended to ``warnings`` (when given). ``level_id`` comes from the entry,
    else from the scene manifest's camera list (found next to the scene).
    """
    render_dir = Path(render_dir)
    manifest = json.loads((render_dir / "render_manifest.json").read_text(encoding="utf-8"))
    entries = {e["camera"]: e for e in manifest.get("renders", [])}
    if cameras is None or cameras == "all":
        names = list(entries)
    else:
        names = [c.strip() for c in (cameras.split(",") if isinstance(cameras, str) else cameras) if c.strip()]
        unknown = [c for c in names if c not in entries]
        if unknown:
            raise KeyError(f"cameras not in {render_dir / 'render_manifest.json'}: {', '.join(unknown)}")
    scene_cams: Optional[dict] = None
    views: dict[str, View] = {}
    for name in names:
        entry = entries[name]
        level_id = entry.get("level_id")
        if level_id is None:
            if scene_cams is None:
                path = _find_scene_manifest(render_dir, manifest)
                scene = json.loads(path.read_text(encoding="utf-8")) if path else {}
                scene_cams = {c["name"]: c for c in scene.get("cameras", [])}
            level_id = (scene_cams.get(name) or {}).get("level_id")
        try:
            views[name] = view_from_entry(entry, render_dir, level_id=level_id)
        except StaleRender as exc:
            if not skip_stale:
                raise
            if warnings is not None:
                warnings.append(f"skipped view {exc}")
    return views


# --------------------------------------------------------------------------
# Pass-index table
# --------------------------------------------------------------------------

def _box3d(obj: dict) -> Optional[dict]:
    """The element's world box: the manifest's ``box3d`` (M5 builds), else its centre/size/rotation."""
    if obj.get("box3d"):
        return obj["box3d"]
    if obj.get("center") is not None and obj.get("size") is not None:
        return {"center": list(obj["center"]), "size": list(obj["size"]),
                "rotation_deg": float(obj.get("rotation_deg") or 0.0)}
    return None


def _is_hosted_decor(obj: dict) -> bool:
    return obj.get("kind") == "decor" and bool(obj.get("host_id"))


def _table_entry(obj: dict, kind: str) -> dict:
    raw_kind = obj.get("kind")
    wenart_id = str(obj.get("wenart_id") or "")
    if wenart_id.startswith(PROXY_PREFIX):
        wenart_id = wenart_id[len(PROXY_PREFIX):]
    room_id = obj.get("room_id")
    if kind in ("door", "window"):
        room_ids = list(obj.get("room_ids") or [])
        # Openings exist in the building only as read from the documents (the
        # building schema gives openings no ``source``), so this is a fact,
        # not a guess.
        source = obj.get("source") or "from_documents"
        box3d = None
    else:
        room_ids = list(obj.get("room_ids") or ([room_id] if room_id else []))
        source = obj.get("source")
        box3d = _box3d(obj)
    return {
        "wenart_id": wenart_id,
        "kind": kind,
        "type": obj.get("type") or raw_kind,
        "room_id": room_id,
        "room_ids": room_ids,
        "host_decor": [],
        "evidence": list(obj.get("evidence") or []),
        "status": obj.get("status"),
        "source": source,
        "box3d": box3d,
        "level_id": obj.get("level_id"),
        "manifest_kind": raw_kind,
    }


def index_table(scene_manifest: dict) -> dict[int, dict]:
    """``{pass_index: element}`` for every object of the scene manifest with a pass index > 0.

    element = ``{"wenart_id" (``proxy:`` stripped), "kind": door|window|furniture|decor,
    "type", "room_id", "room_ids", "host_decor": [types], "evidence", "status", "source",
    "box3d", "level_id", "manifest_kind"}``.

    - The first object of an index that is not hosted decor is the host
      (a door's frame and leaf, a window's frame and glass share one index).
    - Hosted decor (``kind: decor`` with ``host_id``: cushions, book sets)
      shares its host's index and only adds its type to ``host_decor``
      (unique, manifest order). Hostless decor (plants) is its own element
      with kind ``decor``. An index with only hosted decor falls back to its
      first decor object (kind ``decor``).
    - ``furniture_proxy`` becomes kind ``furniture`` (type ``unknown``,
      status ``unverified``); any other manifest kind with an index keeps its
      own name so nothing is silently re-labelled.
    - ``room_ids``: openings: the manifest's ``room_ids`` (M5 builds; [] for
      older manifests), merged over the element's parts; other elements:
      ``[room_id]``. ``source`` of openings
      is ``from_documents``. ``box3d``: the manifest's ``box3d``, else
      ``{center, size, rotation_deg}`` of the object (pre-M5 manifests); None
      for openings.
    """
    table: dict[int, dict] = {}
    hosted: dict[int, list] = {}
    for obj in scene_manifest.get("objects") or []:
        pi = obj.get("pass_index")
        if not pi:
            continue
        pi = int(pi)
        if _is_hosted_decor(obj):
            hosted.setdefault(pi, []).append(obj)
            continue
        if pi in table:
            # Later parts of the same element (door leaf, window glass) only add room ids.
            for rid in obj.get("room_ids") or []:
                if rid not in table[pi]["room_ids"]:
                    table[pi]["room_ids"].append(rid)
            continue
        table[pi] = _table_entry(obj, KIND_MAP.get(obj.get("kind"), obj.get("kind")))
    for pi, decor in hosted.items():
        if pi not in table:
            table[pi] = _table_entry(decor[0], "decor")
        types: list = []
        for obj in decor:
            t = obj.get("type")
            if t and t not in types:
                types.append(t)
        table[pi]["host_decor"] = types
    return dict(sorted(table.items()))


# --------------------------------------------------------------------------
# Regions and geometry edges
# --------------------------------------------------------------------------

@dataclass
class Regions:
    """Masks of one view (all bool H x W).

    ``masks``/``kinds``/``pixels`` are keyed by region id: the wenart id for
    objects (``index:<v>`` for an index missing from the table, kind
    ``unknown``) and ``struct:floor``/``struct:ceiling``/``struct:walls`` for
    structure (kinds ``floor``/``ceiling``/``wall``). Only non-empty regions
    are listed. ``background`` = depth 0; ``panes`` = union of the window
    masks, each eroded by ``pane_erode_px``. ``indices`` maps object region id
    -> pass index.
    """
    masks: dict[str, np.ndarray]
    kinds: dict[str, str]
    pixels: dict[str, int]
    background: np.ndarray
    panes: np.ndarray
    indices: dict[str, int] = field(default_factory=dict)

    def object_ids(self) -> list[str]:
        return [rid for rid in self.masks if rid not in STRUCTURE_KINDS]

    def structure_ids(self) -> list[str]:
        return [rid for rid in self.masks if rid in STRUCTURE_KINDS]


def _float_normal(normal) -> np.ndarray:
    arr = np.asarray(normal)
    if arr.dtype == np.uint8:
        return decode_normal(arr)
    if arr.ndim != 3 or arr.shape[2] < 3:
        raise ValueError(f"normal must be H x W x 3, got shape {arr.shape}")
    return arr[:, :, :3].astype(np.float32)


def erode(mask, radius_px: int) -> np.ndarray:
    """Binary erosion with a (2r+1) square; the image border does not erode (as ``cv2.erode``'s default)."""
    m = np.asarray(mask, dtype=bool)
    r = int(radius_px)
    if r <= 0 or not m.any():
        return m.copy()
    h, w = m.shape
    rows = np.flatnonzero(m.any(axis=1))
    cols = np.flatnonzero(m.any(axis=0))
    y0, y1 = max(0, rows[0] - r), min(h, rows[-1] + 1 + r)
    x0, x1 = max(0, cols[0] - r), min(w, cols[-1] + 1 + r)
    sub = m[y0:y1, x0:x1]
    sh, sw = sub.shape
    padded = np.pad(sub, ((0, 0), (r, r)), constant_values=True)
    tmp = np.ones_like(sub)
    for s in range(2 * r + 1):
        tmp &= padded[:, s:s + sw]
    padded = np.pad(tmp, ((r, r), (0, 0)), constant_values=True)
    res = np.ones_like(sub)
    for s in range(2 * r + 1):
        res &= padded[s:s + sh, :]
    out = np.zeros_like(m)
    out[y0:y1, x0:x1] = res
    return out


def regions(index, depth_mm, normal, table: dict, pane_erode_px: int = 6) -> Regions:
    """Object and structure regions of a view (§1.2).

    ``index``/``depth_mm`` uint16 H x W, ``normal`` float H x W x 3 (or the
    encoded uint8 PNG array), ``table`` from ``index_table``. Objects: one
    mask per pass index present. Structure: index-0 pixels that are not
    background, split by the world normal: floor nz > 0.9, ceiling nz < -0.9,
    walls |nz| < 0.3 (slanted surfaces belong to none).
    """
    idx = np.asarray(index)
    depth = np.asarray(depth_mm)
    nrm = _float_normal(normal)
    if idx.shape != depth.shape or idx.shape != nrm.shape[:2]:
        raise ValueError(f"shape mismatch: index {idx.shape}, depth {depth.shape}, normal {nrm.shape}")
    background = depth == 0
    masks: dict[str, np.ndarray] = {}
    kinds: dict[str, str] = {}
    indices: dict[str, int] = {}
    panes = np.zeros(idx.shape, dtype=bool)
    for value in np.unique(idx).tolist():
        if value <= 0:
            continue
        mask = idx == value
        entry = table.get(int(value))
        rid = entry["wenart_id"] if entry else f"index:{value}"
        kind = entry["kind"] if entry else "unknown"
        if rid in masks:                 # two indices with one id (stale table): keep one region
            masks[rid] = masks[rid] | mask
        else:
            masks[rid] = mask
            kinds[rid] = kind
            indices[rid] = int(value)
        if kind == "window":
            panes |= erode(mask, pane_erode_px)
    zero = (idx == 0) & ~background & normal_hit(nrm)
    nz = nrm[:, :, 2]
    for rid, sel in ((STRUCT_FLOOR, nz > FLOOR_NZ_MIN), (STRUCT_CEILING, nz < CEILING_NZ_MAX),
                     (STRUCT_WALLS, np.abs(nz) < WALL_NZ_ABS_MAX)):
        mask = zero & sel
        if mask.any():
            masks[rid] = mask
            kinds[rid] = STRUCTURE_KINDS[rid]
    pixels = {rid: int(m.sum()) for rid, m in masks.items()}
    return Regions(masks=masks, kinds=kinds, pixels=pixels, background=background, panes=panes, indices=indices)


def geometry_edges(index, depth_mm, normal, depth_rel: float = 0.03, normal_deg: float = 30.0) -> np.ndarray:
    """bool H x W, 1 px wide: where the geometry of the view changes (§1.2, the only definition).

    Between each pixel and its right and lower neighbour: the index changes,
    the depth jumps by more than ``depth_rel`` of the nearer depth, one side
    is background (depth 0) and the other is not, or the normals turn by more
    than ``normal_deg``. The nearer pixel of the pair is marked (the
    occluding side; the left/upper one on a tie), so each boundary is one
    pixel wide.
    """
    idx = np.asarray(index)
    d = np.asarray(depth_mm).astype(np.float64)
    nrm = _float_normal(normal)
    if idx.shape != d.shape or idx.shape != nrm.shape[:2]:
        raise ValueError(f"shape mismatch: index {idx.shape}, depth {d.shape}, normal {nrm.shape}")
    valid = d > 0
    length = np.linalg.norm(nrm, axis=2)
    hit = length > 0
    unit = nrm / np.where(hit, length, 1.0)[:, :, None]
    cos_max = math.cos(math.radians(normal_deg))
    edges = np.zeros(idx.shape, dtype=bool)
    for a, b in (((slice(None), slice(None, -1)), (slice(None), slice(1, None))),
                 ((slice(None, -1), slice(None)), (slice(1, None), slice(None)))):
        da, db = d[a], d[b]
        va, vb = valid[a], valid[b]
        both = va & vb
        jump = both & (np.abs(da - db) > depth_rel * np.minimum(da, db))
        turn = hit[a] & hit[b] & ((unit[a] * unit[b]).sum(axis=2) < cos_max)
        change = (idx[a] != idx[b]) | jump | (va != vb) | turn
        a_nearer = va & (~vb | (da <= db))
        edges[a] |= change & a_nearer
        edges[b] |= change & ~a_nearer
    return edges


# --------------------------------------------------------------------------
# Boxes and project paths
# --------------------------------------------------------------------------

def box_to_1000(box, width: int, height: int) -> list[int]:
    """Pixel box ``[x0, y0, x1, y1]`` (x1/y1 exclusive) -> 0..1000 grid, rounded outwards.

    ``[floor(x0*1000/W), floor(y0*1000/H), ceil(x1*1000/W), ceil(y1*1000/H)]``,
    clipped to 0..1000. Back to pixels with ``vlm_client.norm1000_to_pixels``.
    Integer boxes use exact integer arithmetic.
    """
    x0, y0, x1, y1 = box
    W, H = int(width), int(height)
    if all(isinstance(v, (int, np.integer)) for v in (x0, y0, x1, y1)):
        out = [(int(x0) * 1000) // W, (int(y0) * 1000) // H, -((-int(x1) * 1000) // W), -((-int(y1) * 1000) // H)]
    else:
        out = [math.floor(float(x0) * 1000.0 / W), math.floor(float(y0) * 1000.0 / H),
               math.ceil(float(x1) * 1000.0 / W), math.ceil(float(y1) * 1000.0 / H)]
    return [min(1000, max(0, int(v))) for v in out]


def _resolve_repo_path(value, project_out: Path) -> Optional[Path]:
    """A path recorded in a manifest: absolute as is, else relative to the repo root (§1.1).

    When that file does not exist (for example a pod path read on another
    machine), the same name in the cwd or in ``project_out`` is used if it exists.
    """
    if not value:
        return None
    p = Path(value)
    first = p if p.is_absolute() else REPO_ROOT / p
    candidates = [first]
    if not p.is_absolute():
        candidates.append(Path.cwd() / p)
    candidates.append(project_out / p.name)
    for cand in candidates:
        if cand.exists():
            return cand.resolve()
    return first


def project_paths(project_out) -> dict:
    """Where a project's inputs come from (§1.1).

    Returns ``{"project", "project_out", "scene_manifest" (dict), "scene_manifest_path",
    "building_path", "style_profile" (dict), "project_dir", "brief_path", "brief",
    "render_dir", "warnings"}``:

    - the scene manifest is ``<project_out>/scene/scene_manifest.json``;
    - the building is ``scene_manifest["building"]`` (relative to the repo
      root), the style is ``scene_manifest["style_profile"]`` (the profile
      that was rendered), never a fresh ``style.json``;
    - the project folder is ``building["project"]["source_folder"]`` when the
      building has one, else ``projects/<p>`` (both under the repo root);
    - ``brief`` is ``wenart.brief.load_brief(project_dir)`` (``{"values",
      "assumed"}``), or None with a warning while that module is missing.
    """
    out = Path(project_out).resolve()
    scene_path = out / "scene" / "scene_manifest.json"
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    project = scene.get("project") or out.name
    warnings: list[str] = []
    building_path = _resolve_repo_path(scene.get("building"), out)
    if building_path is None:
        building_path = out / "building_final.json"
        warnings.append("scene manifest names no building; using building_final.json in the project output")
    source_folder = None
    if building_path.is_file():
        building = json.loads(building_path.read_text(encoding="utf-8"))
        source_folder = (building.get("project") or {}).get("source_folder")
    else:
        warnings.append(f"building file not found: {building_path}")
    if source_folder:
        project_dir = Path(source_folder) if Path(source_folder).is_absolute() else REPO_ROOT / source_folder
    else:
        project_dir = REPO_ROOT / "projects" / project
    brief = None
    try:
        from wenart.brief import load_brief  # area E; imported lazily
    except ImportError:
        warnings.append("wenart.brief is not available: brief not loaded")
    else:
        brief = load_brief(project_dir)
    return {
        "project": project,
        "project_out": out,
        "scene_manifest": scene,
        "scene_manifest_path": scene_path,
        "building_path": building_path,
        "style_profile": scene.get("style_profile"),
        "project_dir": project_dir,
        "brief_path": project_dir / "brief.yaml",
        "brief": brief,
        "render_dir": out / "renders",
        "warnings": warnings,
    }
