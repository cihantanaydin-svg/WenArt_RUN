"""Detection of objects the polish adds: OWLv2 boxes on the Cycles and the polished image (docs/milestone7.md §8.1).

What:

- ``python -m wenart.gate detect <out> --manifest <out>/polish/polish_manifest.json --out <out>/detect/``
  (phase 6, venv-polish): OWLv2 boxes per query group for the Cycles render
  and the **chosen polish attempt** of every view whose polish final is
  ``polished`` (``run_detect``), and for the hidden render of every
  removal/insertion control of ``check/controls.json`` (the per-run
  insertion measurement). One ``detect/<cam>.json`` per camera and
  ``detect/detect_manifest.json``. An image whose detection key (model
  revision, ``DETECT_VERSION``, queries, settings, image sha256) did not
  change is reused, never detected again.
- ``python -m wenart.gate detect-calibrate (--pairs <list.json> | --project-outs OUT ...) --out <dir>``
  (prep pod): positives = the M6 insertion controls (the normal render as
  the "polished" image, the hide render as the "Cycles" image), negatives =
  the M6 accepted polishes against their Cycles images and benign
  perturbations of the Cycles images (JPEG q70, noise sigma 2, blur sigma
  0.6). ``build_pairs`` writes the pair list from the project outputs on
  the volume; ``calibrate_scores`` picks ``t_strong`` (the lowest score with
  false confirmed <= 3 %) and ``t_det`` (the lowest score with false flagged
  <= 10 %, at most ``t_strong``) and reports whether insertion confirmed
  reaches 60 %. Output ``detector_calibration.json``; the integrator copies
  ``check_yaml_block`` into ``check.yaml detector:`` only when ``usable``.
- The decision (pure, used by ``wenart.vision_check.combine`` in phase 10):
  an *added object* is a polished box with score >= ``t_det`` that has no
  Cycles box of the same group at IoU >= 0.3 and is not covered >= 50 % by
  one element of a compatible type in the view's pass-index map
  (``added_candidates``); it is **confirmed** when its score is >=
  ``t_strong`` or a VLM extra of either reliable pass overlaps it at IoU >=
  0.3 (``confirm``). A confirmed non-decor object rejects the polished image
  (``added_by_polish``). Without a ``detector:`` block in ``check.yaml`` the
  detector is advisory: boxes are recorded and the unmatched ones listed,
  nothing is confirmed and nothing is rejected.

Why: user decision 3 (3 Oct 2026). The two VLM passes almost never confirm
an inserted object (M5/M6 insertion controls: 0-14 % confirmed against the
60 % target), so a polish that adds a lamp or a chair could pass. An
open-vocabulary detector compares the same camera before and after the
polish: an object it finds only after the polish, where the building has no
element of that kind, was added by the polish.

How: the query groups are plain words, one per building furniture type
(``FURNITURE_WORDS``, kept equal to the schema's type list by
``tests/test_gate_detect.py``) plus door, window, lamp, picture frame, rug,
vase, cushion, mirror and television. Classes follow the vision check
(``wenart.vision_check.schemas.category_class``, mirrored here so the gate
CLI does not import the vision check): furniture types are
``furniture``; ``potted_plant``, picture frame, rug, vase, cushion, mirror and
television are ``decor`` (never a rejection, as the VLM's plant, textile and
other_object today); a lamp is a ``fixture`` or ``furniture`` by its box.
Milestone 8: the decor ``rug`` and ``wall_art`` of the building are
compatible with the rug and picture frame groups (a box on them is covered,
not added; decor either way, never a rejection).
Images go to the model at 960 px on the long side (``IMAGE_LONG_SIDE``; the
OWLv2 processor pads to a square and works at 960 x 960). Per box and group
the score is the sigmoid of the group's best query logit; boxes below
``MIN_SCORE`` are not recorded, the rest go through a per-group NMS (IoU
0.5, at most 20 per group). Box coordinates are pixels of the original
image: the model's boxes are relative to the padded square, so they scale
by the long side (``boxes_from_raw``; the same rule as transformers 5.18's
``Owlv2ImageProcessor._scale_boxes``, done here in numpy so it is
CPU-tested). The model wrapper is ``wenart.gate.models.Detector``
(``raw(rgb, texts) -> (logits [P, Q], pred_boxes [P, 4])``); tests pass a
fake with the same method. Every function but ``run_detect`` /
``run_calibration`` (which call the model) is pure numpy/Python.
"""
from __future__ import annotations

import hashlib
import io
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Optional

import numpy as np

DETECT_VERSION = "m7.1"
IMAGE_LONG_SIDE = 960            # §8.1: images at 960 px long side
MIN_SCORE = 0.05                 # record floor: boxes below it are not written (the calibration grid starts here)
NMS_IOU = 0.5
MAX_PER_GROUP = 20
MATCH_IOU = 0.3                  # a Cycles box of the same group at IoU >= 0.3: the object was there before
COVER_FRAC = 0.5                 # covered >= 50 % by one element of a compatible type: a drawn element
CONFIRM_IOU = 0.3                # a VLM extra of either pass at IoU >= 0.3 confirms a candidate
TARGET_COVER = 0.5               # insertion: a candidate covering >= 50 % of the hidden element's box finds it
ADVISORY_LIST = 10               # advisory mode: the unmatched polished boxes listed per view

DETECT_DIR = "detect"
DETECT_MANIFEST = "detect_manifest.json"
CALIBRATION_JSON = "detector_calibration.json"
PAIRS_JSON = "detect_pairs.json"
CONTROLS_JSON = Path("check") / "controls.json"

# Calibration (§8.1 targets; FALSE_FLAGGED_MAX is the bound of t_det, the same 10 % as the VLM check's
# fa_extra_max: a candidate only becomes a rejection when a VLM extra or the strong score confirms it).
TARGETS = {"insertion_confirmed_min": 0.60, "false_confirmed_max": 0.03, "false_flagged_max": 0.10}
GRID = tuple(round(0.05 + 0.01 * i, 2) for i in range(91))          # 0.05 .. 0.95
PERTURBATIONS = ("jpeg70", "noise2", "blur0.6")

# The vision check's class rules, mirrored here so that ``python -m wenart.gate`` does not import the vision
# check (its schemas pull in the building and furniture code, which would enter the gate stage's code
# fingerprint); tests/test_gate_detect.py pins them equal to ``wenart.vision_check.schemas``.
SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "building.schema.json"
NON_DECOR_CLASSES = ("door", "window", "furniture", "fixture")
LAMP_FIXTURE_MAX_Y1 = 400            # a lamp box ending above y 400 of 1000 hangs (fixture), else it stands


def furniture_types(path: Path = SCHEMA_PATH) -> tuple[str, ...]:
    """The building schema's furniture types without ``unknown`` (the enum the vision check's categories use)."""
    schema = json.loads(Path(path).read_text(encoding="utf-8"))
    return tuple(t for t in schema["$defs"]["furniture"]["properties"]["type"]["enum"] if t != "unknown")


FURNITURE_TYPES: tuple[str, ...] = furniture_types()

# --------------------------------------------------------------------------
# Query groups
# --------------------------------------------------------------------------

# One plain-word query per building furniture type (the schema enum without "unknown").
FURNITURE_WORDS: dict[str, str] = {
    "bed_single": "single bed", "bed_double": "double bed", "sofa": "sofa", "armchair": "armchair",
    "table_dining": "dining table", "table_coffee": "coffee table", "desk": "desk", "chair": "chair",
    "wardrobe": "wardrobe", "kitchen_counter": "kitchen counter", "kitchen_island": "kitchen island",
    "fridge": "refrigerator", "stove": "stove", "sink_kitchen": "kitchen sink", "washbasin": "washbasin",
    "toilet": "toilet", "shower": "shower", "bathtub": "bathtub", "tv_unit": "tv stand", "bookshelf": "bookshelf",
    "nightstand": "nightstand", "dresser": "chest of drawers", "washing_machine": "washing machine",
    "stair": "staircase", "side_table": "side table", "floor_lamp": "floor lamp", "potted_plant": "potted plant",
}
# Types whose element families a box of that type may lie on without being "added" (§8.1 "compatible type").
FAMILIES: tuple[tuple[str, ...], ...] = (
    ("bed_single", "bed_double"),
    ("sofa", "armchair", "chair"),
    ("table_dining", "table_coffee", "desk", "side_table", "nightstand", "kitchen_island"),
    ("wardrobe", "dresser", "bookshelf", "tv_unit", "nightstand"),
    ("kitchen_counter", "kitchen_island", "stove", "sink_kitchen", "fridge", "washing_machine"),
    ("washbasin", "toilet", "shower", "bathtub", "washing_machine"),
    ("floor_lamp",),
    ("potted_plant", "plant"),
    ("stair",),
)
DECOR_FURNITURE = ("potted_plant",)      # a furniture type the detector treats as decor (as the VLM's "plant")
LAMP = "lamp"                             # class by box: fixture (hangs high) or furniture (stands)


@dataclass(frozen=True)
class Group:
    """One query group: the plain-word texts, the class of its boxes and the element types it may lie on."""
    name: str
    texts: tuple[str, ...]
    cls: str                       # door | window | furniture | fixture | decor | "lamp" (by box)
    compatible: tuple[str, ...]    # element types (furniture/decor ``type``, or door/window ``kind``)


def _family(t: str) -> tuple[str, ...]:
    out = [t]
    for fam in FAMILIES:
        if t in fam:
            out += [x for x in fam if x not in out]
    return tuple(out)


def _groups() -> tuple[Group, ...]:
    groups = []
    for t in FURNITURE_TYPES:
        cls = "decor" if t in DECOR_FURNITURE else "furniture"
        groups.append(Group(t, (FURNITURE_WORDS[t],), cls, _family(t) + ("unknown",)))
    groups += [
        Group("door", ("door",), "door", ("door",)),
        Group("window", ("window",), "window", ("window",)),
        Group("lamp", ("lamp",), LAMP, ("floor_lamp", "table_lamp")),       # Milestone 9: the decor table lamp
        # Milestone 8: a picture frame / rug box lying on the decor wall art / rug of the building is not added.
        Group("picture_frame", ("picture frame",), "decor", ("wall_art",)),
        Group("rug", ("rug",), "decor", ("rug",)),
        Group("vase", ("vase",), "decor", ("vase",)),                       # Milestone 9: the decor vase
        Group("cushion", ("cushion",), "decor", ("cushion", "sofa", "armchair", "bed_single", "bed_double")),
        Group("mirror", ("mirror",), "decor", ("mirror",)),                 # Milestone 9: the decor mirror
        Group("television", ("television",), "decor", ("tv_unit",)),
    ]
    return tuple(groups)


GROUPS: tuple[Group, ...] = _groups()
GROUP_BY_NAME: dict[str, Group] = {g.name: g for g in GROUPS}


def query_texts(groups: Iterable[Group] = GROUPS) -> tuple[list[str], list[str]]:
    """``(texts, group of each text)``: the flat query list the model gets, in group order."""
    texts, owners = [], []
    for g in groups:
        for t in g.texts:
            texts.append(t)
            owners.append(g.name)
    return texts, owners


def queries_record(groups: Iterable[Group] = GROUPS) -> dict:
    """``{group: {"texts", "class", "compatible"}}`` as written into every detection file."""
    return {g.name: {"texts": list(g.texts), "class": g.cls, "compatible": list(g.compatible)} for g in groups}


def box_class(group: str, box_px, size) -> Optional[str]:
    """Class of one box: the group's class; a lamp by its box (``schemas.category_class`` on the 0..1000 grid)."""
    g = GROUP_BY_NAME.get(group)
    if g is None:
        return None
    if g.cls != LAMP:
        return g.cls
    W, H = (float(v) for v in size)
    box_1000 = [box_px[0] * 1000.0 / W, box_px[1] * 1000.0 / H, box_px[2] * 1000.0 / W, box_px[3] * 1000.0 / H]
    return "fixture" if max(box_1000[1], box_1000[3]) <= LAMP_FIXTURE_MAX_Y1 else "furniture"


def non_decor(cls: Optional[str]) -> bool:
    return cls in NON_DECOR_CLASSES


# --------------------------------------------------------------------------
# Boxes
# --------------------------------------------------------------------------

def box_iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def box_cover(box, target) -> float:
    """Share of ``target`` covered by ``box``."""
    ix = max(0.0, min(box[2], target[2]) - max(box[0], target[0]))
    iy = max(0.0, min(box[3], target[3]) - max(box[1], target[1]))
    area = (target[2] - target[0]) * (target[3] - target[1])
    return ix * iy / area if area > 0 else 0.0


def sigmoid(x) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    return 1.0 / (1.0 + np.exp(-x))


def nms(boxes: np.ndarray, scores: np.ndarray, iou: float = NMS_IOU, limit: Optional[int] = None) -> list[int]:
    """Indices kept by a greedy non-maximum suppression (highest score first, ties by index)."""
    order = sorted(range(len(scores)), key=lambda i: (-float(scores[i]), i))
    keep: list[int] = []
    for i in order:
        if limit is not None and len(keep) >= limit:
            break
        if all(box_iou(boxes[i], boxes[j]) < iou for j in keep):
            keep.append(i)
    return keep


def boxes_from_raw(logits, pred_boxes, size, owners: list[str], texts: Optional[list[str]] = None, model_size=None,
                   min_score: float = MIN_SCORE, nms_iou: float = NMS_IOU,
                   max_per_group: int = MAX_PER_GROUP) -> list[dict]:
    """The recorded boxes of one image from the raw OWLv2 outputs.

    ``logits`` [P, Q] and ``pred_boxes`` [P, 4] (centre x, centre y, width,
    height, relative to the processor's padded square) of the image the model
    got, of pixel size ``model_size`` (W, H; default ``size``); ``size`` is the
    original image's (W, H); ``owners`` the group of each of the Q queries
    and ``texts`` their words (recorded with each box).
    Per group the score of a box is the sigmoid of its best query logit; boxes
    >= ``min_score`` go through a per-group NMS. Boxes are original-image
    pixels ``[x0, y0, x1, y1]``, clipped to the image, sorted by group order
    then score. Each box: ``{"group", "text", "score", "box_px", "class"}``.
    """
    logits = np.asarray(logits, dtype=np.float64)
    pred = np.asarray(pred_boxes, dtype=np.float64)
    if logits.ndim != 2 or pred.ndim != 2 or pred.shape[1] != 4 or logits.shape[0] != pred.shape[0]:
        raise ValueError(f"logits {logits.shape} and pred_boxes {pred.shape} do not match")
    if logits.shape[1] != len(owners):
        raise ValueError(f"{logits.shape[1]} query logits for {len(owners)} query texts")
    W, H = (float(v) for v in size)
    mw, mh = (float(v) for v in (model_size or size))
    side = max(mw, mh)                                     # the padded square of the model's image
    sx, sy = side * W / mw, side * H / mh                  # relative -> original pixels per axis
    cx, cy, bw, bh = pred[:, 0], pred[:, 1], pred[:, 2], pred[:, 3]
    corners = np.stack([np.clip((cx - bw / 2) * sx, 0, W), np.clip((cy - bh / 2) * sy, 0, H),
                        np.clip((cx + bw / 2) * sx, 0, W), np.clip((cy + bh / 2) * sy, 0, H)], axis=1)
    probs = sigmoid(logits)
    out: list[dict] = []
    names = list(dict.fromkeys(owners))
    for name in names:
        cols = [q for q, o in enumerate(owners) if o == name]
        best_q = np.asarray(cols)[np.argmax(probs[:, cols], axis=1)]
        scores = probs[np.arange(len(probs)), best_q]
        valid = (scores >= float(min_score)) & (corners[:, 2] > corners[:, 0]) & (corners[:, 3] > corners[:, 1])
        idx = np.flatnonzero(valid)
        if not len(idx):
            continue
        keep = nms(corners[idx], scores[idx], nms_iou, max_per_group)
        for k in keep:
            i = int(idx[k])
            box = [round(float(v), 1) for v in corners[i]]
            q = int(best_q[i])
            out.append({"group": name, "text": None if texts is None else texts[q],
                        "score": round(float(scores[i]), 4), "box_px": box, "class": box_class(name, box, size)})
    return out


def model_image(rgb: np.ndarray, long_side: int = IMAGE_LONG_SIDE) -> np.ndarray:
    """``rgb`` scaled to ``long_side`` on its long side (PIL Lanczos; unchanged when already that size)."""
    from PIL import Image
    a = np.ascontiguousarray(np.asarray(rgb, dtype=np.uint8)[:, :, :3])
    h, w = a.shape[:2]
    scale = float(long_side) / float(max(w, h))
    if abs(scale - 1.0) < 1e-9:
        return a
    size = (max(1, int(round(w * scale))), max(1, int(round(h * scale))))
    return np.asarray(Image.fromarray(a).resize(size, Image.Resampling.LANCZOS), dtype=np.uint8)


def detect_rgb(detector, rgb: np.ndarray, groups: Iterable[Group] = GROUPS, min_score: float = MIN_SCORE) -> dict:
    """``{"size", "model_size", "boxes", "seconds"}`` of one image (the model call)."""
    t0 = time.time()
    rgb = np.asarray(rgb)
    H, W = rgb.shape[:2]
    small = model_image(rgb)
    texts, owners = query_texts(groups)
    logits, pred = detector.raw(small, texts)
    boxes = boxes_from_raw(logits, pred, (W, H), owners, texts, model_size=(small.shape[1], small.shape[0]),
                           min_score=min_score)
    return {"size": [int(W), int(H)], "model_size": [int(small.shape[1]), int(small.shape[0])], "boxes": boxes,
            "seconds": round(time.time() - t0, 3)}


# --------------------------------------------------------------------------
# The decision (pure; combine and the calibration)
# --------------------------------------------------------------------------

def element_matches(group: str, element: Optional[dict]) -> bool:
    """True when ``element`` (an ``views.index_table`` entry) has a type ``group`` may lie on."""
    g = GROUP_BY_NAME.get(group)
    if g is None or not element:
        return False
    kind = element.get("kind")
    if kind in ("door", "window"):
        return kind in g.compatible
    types = {element.get("type")} | set(element.get("host_decor") or [])
    if kind == "furniture" and element.get("status") == "unverified":
        types.add("unknown")
    return bool(types & set(g.compatible))


def compatible_cover(box_px, group: str, index_map: Optional[np.ndarray], table: dict,
                     exclude_ids: Iterable[str] = ()) -> float:
    """Largest share of the box covered by ONE element of a type ``group`` may lie on (0 without a map)."""
    if index_map is None:
        return 0.0
    H, W = index_map.shape
    x0, y0 = max(0, int(np.floor(box_px[0]))), max(0, int(np.floor(box_px[1])))
    x1, y1 = min(W, int(np.ceil(box_px[2]))), min(H, int(np.ceil(box_px[3])))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    patch = index_map[y0:y1, x0:x1].ravel().astype(np.int64)
    counts = np.bincount(patch)
    exclude = set(exclude_ids)
    best = 0
    for pi in np.flatnonzero(counts):
        if pi == 0:
            continue
        el = table.get(int(pi))
        if el is None or el.get("wenart_id") in exclude or not element_matches(group, el):
            continue
        best = max(best, int(counts[pi]))
    return best / float(patch.size)


def added_candidates(polished: list[dict], cycles: list[dict], t_det: float, index_map=None, table=None,
                     exclude_ids: Iterable[str] = (), match_iou: float = MATCH_IOU,
                     cover_frac: float = COVER_FRAC) -> list[dict]:
    """Added-object candidates: polished boxes >= ``t_det`` with no Cycles box of the same group at IoU >=
    ``match_iou`` and not covered >= ``cover_frac`` by one element of a compatible type (§8.1).

    Every recorded Cycles box counts for the match (recorded down to
    ``MIN_SCORE``): an object the detector saw faintly before the polish was
    not added by it. ``exclude_ids``: elements left out of the coverage (an
    insertion control's target). Each candidate: the polished box plus
    ``cycles_iou`` (best same-group IoU) and ``covered``; sorted by score.
    """
    table = table or {}
    out = []
    for b in polished:
        if float(b["score"]) < float(t_det):
            continue
        same = [c for c in cycles if c["group"] == b["group"]]
        best_iou = max((box_iou(b["box_px"], c["box_px"]) for c in same), default=0.0)
        if best_iou >= match_iou:
            continue
        cov = compatible_cover(b["box_px"], b["group"], index_map, table, exclude_ids)
        if cov >= cover_frac:
            continue
        out.append(dict(b, cycles_iou=round(best_iou, 3), covered=round(cov, 3)))
    return sorted(out, key=lambda c: (-float(c["score"]), c["group"], c["box_px"]))


def confirm(candidates: list[dict], t_strong: Optional[float], extras: Iterable[dict] = (),
            iou: float = CONFIRM_IOU) -> list[dict]:
    """``candidates`` with ``confirmed`` and ``confirmed_by``: the strong score, or a VLM extra (any class, either
    reliable pass; ``extras`` are vision-check extras with ``box_px`` and ``passes``) at IoU >= ``iou``."""
    extras = list(extras)
    out = []
    for c in candidates:
        by = []
        if t_strong is not None and float(c["score"]) >= float(t_strong):
            by.append("score")
        for x in extras:
            if x.get("unreliable"):
                continue
            if box_iou(c["box_px"], x["box_px"]) >= iou:
                for k in x.get("passes") or []:
                    tag = f"vlm:{k}"
                    if tag not in by:
                        by.append(tag)
        out.append(dict(c, confirmed=bool(by), confirmed_by=by))
    return out


def target_hit(candidates: list[dict], target_box, need: float = TARGET_COVER) -> Optional[dict]:
    """The best-scoring NON-DECOR candidate covering >= ``need`` of an insertion target's box (None when none does).

    Decor boxes (picture frame, mirror, rug, ...) never count as a hit: the
    decision only rejects on confirmed non-decor candidates, so the insertion
    rate of the calibration and of the per-run controls measures the same
    thing (review vision-1: a "picture frame" box over an inserted window
    counted as found although it can never reject a polish)."""
    hits = [c for c in candidates if non_decor(c.get("class")) and box_cover(c["box_px"], target_box) >= need]
    return max(hits, key=lambda c: (float(c["score"]), c["group"]), default=None)


def unmatched(polished: list[dict], cycles: list[dict], index_map=None, table=None, limit: int = ADVISORY_LIST
              ) -> list[dict]:
    """Advisory listing: the ``limit`` best polished boxes that are added candidates at the record floor."""
    return added_candidates(polished, cycles, 0.0, index_map, table)[:limit]


def detector_cfg(cfg: Optional[dict]) -> Optional[dict]:
    """The ``check.yaml detector:`` block as ``{t_det, t_strong, match_iou, cover_frac, confirm_iou, ...}``, or None
    (advisory) when the block is missing or empty, marked ``advisory: true`` or has no thresholds (both null).
    ValueError for a malformed block (one threshold only, not numbers, not 0 < t_det <= t_strong <= 1)."""
    block = (cfg or {}).get("detector")
    if not block:
        return None
    if not isinstance(block, dict):
        raise ValueError(f"check.yaml detector: must be a mapping, got {type(block).__name__}")
    if block.get("advisory") or (block.get("t_det") is None and block.get("t_strong") is None):
        return None
    try:
        t_det, t_strong = float(block["t_det"]), float(block["t_strong"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"check.yaml detector: needs numbers t_det and t_strong ({exc})") from exc
    if not (0.0 < t_det <= t_strong <= 1.0):
        raise ValueError(f"check.yaml detector: need 0 < t_det <= t_strong <= 1, got {t_det}, {t_strong}")
    out = {"t_det": t_det, "t_strong": t_strong, "match_iou": float(block.get("match_iou", MATCH_IOU)),
           "cover_frac": float(block.get("cover_frac", COVER_FRAC)),
           "confirm_iou": float(block.get("confirm_iou", CONFIRM_IOU))}
    if block.get("calibration") is not None:
        out["calibration"] = block["calibration"]
    return out


# --------------------------------------------------------------------------
# Detection files (run_detect)
# --------------------------------------------------------------------------

def sha256_file(path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def settings_record() -> dict:
    return {"detect_version": DETECT_VERSION, "image_long_side": IMAGE_LONG_SIDE, "min_score": MIN_SCORE,
            "nms_iou": NMS_IOU, "max_per_group": MAX_PER_GROUP}


def detection_key(model: dict, image_sha: str, perturb: Optional[str] = None) -> str:
    """First 16 hex of sha256 over the model revision, the settings, the query table and the image (+ perturbation)."""
    payload = {"model": {"repo": (model or {}).get("repo"), "revision": (model or {}).get("revision")},
               "settings": settings_record(), "queries": queries_record(), "image": image_sha, "perturb": perturb}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def _rel(path: Path, base: Path) -> str:
    import os
    return Path(os.path.relpath(Path(path).resolve(), Path(base).resolve())).as_posix()


def write_json(path: Path, data) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def read_json(path: Path) -> Optional[dict]:
    path = Path(path)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _image_record(detector, png: Path, det_dir: Path, model: dict, old: Optional[dict], extra: Optional[dict] = None
                  ) -> tuple[dict, bool]:
    """``(record, reused)`` of one image: reused when the stored record has the same detection key."""
    from wenart import views as V
    sha = sha256_file(png)
    key = detection_key(model, sha)
    if old and old.get("key") == key and isinstance(old.get("boxes"), list):
        return dict(old, file=_rel(png, det_dir), **(extra or {})), True
    found = detect_rgb(detector, V.read_rgb(png))
    rec = {"file": _rel(png, det_dir), "sha256": sha, "key": key, **found, **(extra or {})}
    return rec, False


def polished_views(manifest: dict, manifest_path: Path) -> tuple[dict, dict]:
    """``({camera: {"png", "k", "source_sha256"}}, {camera: skip reason})`` from a polish manifest."""
    base = Path(manifest_path).parent
    chosen, skipped = {}, {}
    for v in manifest.get("views") or []:
        cam = v.get("camera")
        if not cam:
            continue
        if v.get("final") != "polished" or v.get("final_attempt") is None:
            skipped[cam] = f"final {v.get('final') or '-'}" + (f" ({v['reason']})" if v.get("reason") else "")
            continue
        rec = next((a for a in v.get("attempts") or [] if a.get("k") == v["final_attempt"]), None)
        if not rec or not rec.get("png"):
            skipped[cam] = f"final attempt {v['final_attempt']} has no PNG"
            continue
        png = base / rec["png"]
        if not png.is_file():
            skipped[cam] = f"polished PNG missing ({rec['png']})"
            continue
        chosen[cam] = {"png": png, "k": int(v["final_attempt"]), "source_sha256": v.get("source_sha256")}
    return chosen, skipped


def run_detect(out, manifest_path, det_dir, detector, *, controls: bool = True, deadline: Optional[float] = None,
               force: bool = False, log: Callable = print, clock: Callable[[], float] = time.time) -> dict:
    """Write ``det_dir/<cam>.json`` per camera and ``det_dir/detect_manifest.json`` (see the module docstring).

    Cameras: the views whose polish final is ``polished`` (their Cycles render
    and the chosen attempt) and, with ``controls``, the cameras of the
    controls in ``check/controls.json`` (their Cycles render and each hidden
    render). A polished view made from another Cycles render
    (``source_sha256``) is skipped with a warning. No image starts after
    ``deadline``; the manifest then says ``incomplete``.
    """
    from wenart import views as V
    out = Path(out).resolve()
    det_dir = Path(det_dir).resolve()
    manifest_path = Path(manifest_path)
    t0 = clock()
    warnings: list[str] = []
    pm = read_json(manifest_path)
    if pm is None:
        raise FileNotFoundError(f"no polish manifest at {manifest_path}")
    model = detector.info() if hasattr(detector, "info") else {}
    doc = {"schema_version": "0.1", "kind": "detect_manifest", "project": pm.get("project") or out.name,
           "model": model, "settings": settings_record(), "queries": queries_record(),
           "polish_manifest": _rel(manifest_path, det_dir), "views": {}, "incomplete": False, "warnings": warnings}
    if pm.get("polish_allowed") is False:
        doc["skipped"] = "polish not allowed (gate not validated)"
        write_json(det_dir / DETECT_MANIFEST, doc)
        return doc
    render_dir = out / "renders"
    cycles = V.load_views(render_dir, skip_stale=True, warnings=warnings) \
        if (render_dir / "render_manifest.json").is_file() else {}
    chosen, skipped = polished_views(pm, manifest_path)
    for cam, why in skipped.items():
        doc["views"][cam] = {"status": "skipped", "reason": why}
    control_list = []
    if controls:
        cdoc = read_json(out / CONTROLS_JSON) or {}
        control_list = [c for c in cdoc.get("controls") or [] if c.get("camera") in cycles]
    cams = list(dict.fromkeys([c for c in cycles if c in chosen] + [c["camera"] for c in control_list]))
    for cam in chosen:
        if cam not in cycles:
            doc["views"][cam] = {"status": "skipped", "reason": "no current Cycles render"}
    detected = reused = 0
    for cam in cams:
        view = cycles[cam]
        path = det_dir / f"{cam}.json"
        old = None if force else read_json(path)
        if old is not None and (old.get("model") or {}).get("revision") != model.get("revision"):
            old = None
        old_images = (old or {}).get("images") or {}
        rec = {"schema_version": "0.1", "kind": "detect_view", "camera": cam, "room_id": view.room_id,
               "model": model, "settings": settings_record(), "queries": queries_record(), "images": {},
               "controls": {}}
        pol = chosen.get(cam)
        if pol and pol.get("source_sha256") and sha256_file(view.png) != pol["source_sha256"]:
            warnings.append(f"{cam}: the polished image was made from another Cycles render (source_sha256); "
                            "not detected")
            doc["views"][cam] = {"status": "skipped", "reason": "polish made from another Cycles render"}
            pol = None
        jobs = [("cycles", view.png, {}, old_images.get("cycles"))]
        if pol:
            jobs.append(("polished", pol["png"], {"k": pol["k"]}, old_images.get("polished")))
        for c in control_list:
            if c["camera"] != cam:
                continue
            hdir = out / c.get("dir", f"controls/hide_{c['id']}")
            try:
                hidden = V.load_views(hdir, [cam], skip_stale=True).get(cam) \
                    if (hdir / "render_manifest.json").is_file() else None
            except KeyError:
                hidden = None
            if hidden is None:
                warnings.append(f"control {c['id']}: no render in {_rel(hdir, out)}; not detected")
                continue
            jobs.append((f"control:{c['id']}", hidden.png, {"target": c["id"], "kind": c.get("kind"),
                                                            "type": c.get("type")},
                         ((old or {}).get("controls") or {}).get(c["id"])))
        stop = False
        for name, png, extra, prev in jobs:
            if not stop and deadline is not None and clock() >= deadline:
                doc["incomplete"] = stop = True
            if stop:
                image = prev                       # not reached: the earlier record stays (combine checks its sha256)
                if image is None:
                    continue
            else:
                image, was_reused = _image_record(detector, png, det_dir, model, prev, extra)
                reused += was_reused
                detected += not was_reused
            if name.startswith("control:"):
                rec["controls"][name.split(":", 1)[1]] = image
            else:
                rec["images"][name] = image
        if rec["images"].get("cycles"):
            write_json(path, rec)
            status = "ok" if "polished" in rec["images"] else "controls only"
            doc["views"].setdefault(cam, {"status": status, "file": f"{cam}.json"})
            doc["views"][cam].update(file=f"{cam}.json", polished=bool(rec["images"].get("polished")),
                                     controls=sorted(rec["controls"]))
        if stop:
            warnings.append("deadline reached: detection incomplete")
            break
    doc["detected_images"] = detected
    doc["reused_images"] = reused
    doc["seconds"] = round(clock() - t0, 2)
    write_json(det_dir / DETECT_MANIFEST, doc)
    log(f"gate detect: {len(cams)} camera(s), {detected} image(s) detected, {reused} reused"
        f"{' (deadline: incomplete)' if doc['incomplete'] else ''} -> {det_dir}")
    return doc


# --------------------------------------------------------------------------
# Calibration pairs (detect-calibrate)
# --------------------------------------------------------------------------

def perturb(rgb: np.ndarray, kind: Optional[str]) -> np.ndarray:
    """A benign perturbation of an image (deterministic): ``jpeg70``, ``noise2`` (sigma 2, seed 0), ``blur0.6``."""
    a = np.ascontiguousarray(np.asarray(rgb, dtype=np.uint8)[:, :, :3])
    if not kind:
        return a
    if kind == "jpeg70":
        from PIL import Image
        buf = io.BytesIO()
        Image.fromarray(a).save(buf, format="JPEG", quality=70)
        with Image.open(io.BytesIO(buf.getvalue())) as img:
            return np.asarray(img.convert("RGB"), dtype=np.uint8)
    if kind == "noise2":
        rng = np.random.default_rng(0)
        return np.clip(a.astype(np.float64) + rng.normal(0.0, 2.0, a.shape), 0, 255).round().astype(np.uint8)
    if kind == "blur0.6":
        import cv2
        return cv2.GaussianBlur(a, (0, 0), sigmaX=0.6, sigmaY=0.6, borderType=cv2.BORDER_REFLECT_101)
    raise ValueError(f"unknown perturbation {kind!r}; choose from {', '.join(PERTURBATIONS)}")


def _project_paths(out: Path) -> tuple[Optional[Path], dict]:
    scene_path = out / "scene" / "scene_manifest.json"
    return (scene_path if scene_path.is_file() else None), (read_json(scene_path) or {})


def build_pairs(project_outs: Iterable, perturbations: Iterable[str] = PERTURBATIONS) -> dict:
    """The calibration pair list from project outputs (the M6 outputs on the volume, before any M7 render).

    Positives: every control of ``check/controls.json`` whose hide render
    exists and no longer shows the element: ``cycles`` = the hide render,
    ``polished`` = the normal render, ``target_box_px`` = the element's box in
    the normal render (``index_stats``). Negatives: every view whose polish
    final is ``polished`` (made from the current render): ``cycles`` = the
    render, ``polished`` = the chosen attempt; and per such view one pair per
    perturbation of the Cycles image. Each pair names the index map and scene
    manifest of the normal render for the coverage rule.
    """
    from wenart import views as V
    pairs: list[dict] = []
    warnings: list[str] = []
    for o in dict.fromkeys(Path(p).resolve() for p in project_outs):
        name = o.name
        render_dir = o / "renders"
        if not (render_dir / "render_manifest.json").is_file():
            warnings.append(f"{name}: no renders/render_manifest.json; skipped")
            continue
        scene_path, scene = _project_paths(o)
        table = V.index_table(scene) if scene else {}
        by_id = {e["wenart_id"]: pi for pi, e in table.items()}
        views = V.load_views(render_dir, skip_stale=True, warnings=warnings)
        common = {"project": name, "scene_manifest": str(scene_path) if scene_path else None}
        for c in (read_json(o / CONTROLS_JSON) or {}).get("controls") or []:
            cam, cid = c.get("camera"), c.get("id")
            view = views.get(cam)
            hdir = o / c.get("dir", f"controls/hide_{cid}")
            if view is None or not (hdir / "render_manifest.json").is_file():
                warnings.append(f"{name}: control {cid}: no normal or hide render; skipped")
                continue
            try:
                hidden = V.load_views(hdir, [cam], skip_stale=True).get(cam)
            except KeyError:
                hidden = None
            pi = by_id.get(cid)
            stats = (view.index_stats or {}).get(pi) if pi else None
            if hidden is None or not stats or not stats.get("box"):
                warnings.append(f"{name}: control {cid}: no hide render or no box in the normal render; skipped")
                continue
            if pi in {int(k) for k in (hidden.index_stats or {})}:
                warnings.append(f"{name}: control {cid}: the hide render still shows it; skipped")
                continue
            pairs.append({"id": f"{name}:insertion:{cid}", "kind": "positive", "source": "insertion_control",
                          "camera": cam, "cycles": str(hidden.png), "polished": str(view.png),
                          "index": str(view.index), "target": cid, "target_type": c.get("type"),
                          "target_box_px": [float(v) for v in stats["box"]], "exclude_ids": [cid], **common})
        pm_path = o / "polish" / "polish_manifest.json"
        pm = read_json(pm_path)
        if pm is None:
            continue
        chosen, _ = polished_views(pm, pm_path)
        for cam, pol in chosen.items():
            view = views.get(cam)
            if view is None:
                continue
            if pol.get("source_sha256") and sha256_file(view.png) != pol["source_sha256"]:
                warnings.append(f"{name}: {cam}: polish made from another render; skipped")
                continue
            base = {"camera": cam, "index": str(view.index), "exclude_ids": [], **common}
            pairs.append({"id": f"{name}:polish:{cam}", "kind": "negative", "source": "accepted_polish",
                          "cycles": str(view.png), "polished": str(pol["png"]), **base})
            for p in perturbations:
                pairs.append({"id": f"{name}:{p}:{cam}", "kind": "negative", "source": "perturbation",
                              "perturb": p, "cycles": str(view.png), "polished": str(view.png), **base})
    by = {}
    for p in pairs:
        by[p["source"]] = by.get(p["source"], 0) + 1
    return {"schema_version": "0.1", "kind": "detect_pairs", "projects": [Path(p).name for p in project_outs],
            "pairs": pairs, "counts": by, "warnings": warnings}


def pair_scores(pair: dict, cycles_boxes: list[dict], polished_boxes: list[dict], index_map=None,
                table=None) -> dict:
    """The scores the calibration needs from one pair: ``hit`` (positives: the best non-decor candidate on the
    target, ``target_hit``), ``false`` (negatives: the best non-decor candidate), at the record floor (every
    candidate). Both sides count only what the decision can reject on (non-decor)."""
    cands = added_candidates(polished_boxes, cycles_boxes, 0.0, index_map, table, pair.get("exclude_ids") or ())
    if pair["kind"] == "positive":
        hit = target_hit(cands, pair["target_box_px"])
        return {"hit": None if hit is None else float(hit["score"]), "hit_group": None if hit is None else hit["group"],
                "candidates": len(cands)}
    worst = next((c for c in cands if non_decor(c.get("class"))), None)
    return {"false": None if worst is None else float(worst["score"]),
            "false_group": None if worst is None else worst["group"], "candidates": len(cands)}


def rates_at(t: float, hits: list, falses: list) -> dict:
    """Shares of positives found and of negatives flagged at threshold ``t`` (None without pairs)."""
    def share(values):
        if not values:
            return None
        return round(sum(1 for v in values if v is not None and v >= t) / len(values), 4)
    return {"t": round(float(t), 2), "insertion": share(hits), "false": share(falses)}


def calibrate_scores(hits: list, falses: list, grid: Iterable[float] = GRID, targets: Optional[dict] = None) -> dict:
    """``t_det``, ``t_strong``, their rates, the grid and whether the targets are met (§8.1).

    - ``t_strong``: the lowest grid score whose false share (negatives with
      a non-decor candidate at >= t) is <= ``false_confirmed_max`` (3 %);
    - ``t_det``: the lowest grid score whose false share is <=
      ``false_flagged_max`` (10 %), at most ``t_strong``;
    - ``targets_met``: insertion confirmed (positives with a non-decor
      candidate on the target at >= ``t_strong``) >= 60 % and false
      confirmed <= 3 %;
      ``usable`` = targets met with both thresholds found.
    Without positives or negatives nothing is proposed.
    """
    tg = dict(TARGETS, **(targets or {}))
    rows = [rates_at(t, hits, falses) for t in grid]
    out = {"targets": tg, "grid": rows, "t_det": None, "t_strong": None, "rates": None, "targets_met": False,
           "usable": False, "positives": len(hits), "negatives": len(falses)}
    if not hits or not falses:
        out["note"] = "no positives" if not hits else "no negatives"
        return out
    strong = next((r for r in rows if r["false"] <= tg["false_confirmed_max"]), None)
    if strong is None:
        out["note"] = f"no score keeps false confirmed <= {tg['false_confirmed_max']}"
        return out
    det = next((r for r in rows if r["false"] <= tg["false_flagged_max"] and r["t"] <= strong["t"]), strong)
    out.update(t_det=det["t"], t_strong=strong["t"],
               rates={"insertion_confirmed": strong["insertion"], "false_confirmed": strong["false"],
                      "insertion_flagged": det["insertion"], "false_flagged": det["false"]})
    met = strong["insertion"] >= tg["insertion_confirmed_min"] and strong["false"] <= tg["false_confirmed_max"]
    out["targets_met"] = out["usable"] = bool(met)
    if not met:
        out["note"] = (f"insertion confirmed {strong['insertion']} < {tg['insertion_confirmed_min']} at t_strong "
                       f"{strong['t']}: the detector stays advisory")
    return out


def run_calibration(pairs_doc: dict, out_dir, detector, *, cache_dir=None, log: Callable = print) -> dict:
    """Detect every image of the pair list (cached per detection key in ``cache_dir``, default
    ``<out_dir>/boxes/``), score the pairs and write ``<out_dir>/detector_calibration.json``."""
    from wenart import views as V
    out_dir = Path(out_dir)
    model = detector.info() if hasattr(detector, "info") else {}
    cache_dir = Path(cache_dir) if cache_dir else out_dir / "boxes"
    t0 = time.time()
    maps: dict = {}
    tables: dict = {}
    rows, hits, falses, warnings = [], [], [], list(pairs_doc.get("warnings") or [])
    detected = reused = 0

    def boxes_of(png: str, kind: Optional[str] = None) -> list[dict]:
        nonlocal detected, reused
        sha = sha256_file(png)
        key = detection_key(model, sha, kind)
        cached = read_json(cache_dir / f"{key}.json")
        if cached is not None:
            reused += 1
            return cached["boxes"]
        rgb = perturb(V.read_rgb(png), kind)
        found = detect_rgb(detector, rgb)
        write_json(cache_dir / f"{key}.json", {"key": key, "file": str(png), "perturb": kind, **found})
        detected += 1
        return found["boxes"]

    for pair in pairs_doc.get("pairs") or []:
        try:
            cyc = boxes_of(pair["cycles"])
            pol = boxes_of(pair["polished"], pair.get("perturb"))
        except (OSError, ValueError) as exc:
            warnings.append(f"{pair['id']}: {type(exc).__name__}: {exc}; left out")
            continue
        index_map = None
        if pair.get("index") and Path(pair["index"]).is_file():
            if pair["index"] not in maps:
                maps.clear()                                  # one map at a time (8 MB at 1920 x 1080)
                maps[pair["index"]] = V.read_index(pair["index"])
            index_map = maps[pair["index"]]
        sm = pair.get("scene_manifest")
        if sm not in tables:
            tables[sm] = V.index_table(read_json(sm) or {}) if sm else {}
        sc = pair_scores(pair, cyc, pol, index_map, tables[sm])
        rows.append({"id": pair["id"], "kind": pair["kind"], "source": pair.get("source"), **sc})
        if pair["kind"] == "positive":
            hits.append(sc["hit"])
        else:
            falses.append(sc["false"])
    result = calibrate_scores(hits, falses)
    by_source: dict = {}
    for r in rows:
        s = by_source.setdefault(r["source"] or "-", {"pairs": 0})
        s["pairs"] += 1
    doc = {"schema_version": "0.1", "kind": "detector_calibration", "model": model, "settings": settings_record(),
           "queries": queries_record(), "pairs_by_source": by_source, **result, "per_pair": rows,
           "detected_images": detected, "reused_images": reused, "seconds": round(time.time() - t0, 1),
           "warnings": warnings}
    doc["check_yaml_block"] = None if not result["usable"] else {
        "advisory": False, "t_det": result["t_det"], "t_strong": result["t_strong"], "match_iou": MATCH_IOU,
        "cover_frac": COVER_FRAC, "confirm_iou": CONFIRM_IOU,
        "calibration": {"file": CALIBRATION_JSON, "model_revision": model.get("revision"),
                        "detect_version": DETECT_VERSION, "positives": result["positives"],
                        "negatives": result["negatives"], **result["rates"]}}
    write_json(out_dir / CALIBRATION_JSON, doc)
    log(f"gate detect-calibrate: {result['positives']} positive(s), {result['negatives']} negative(s); t_det "
        f"{result['t_det']}, t_strong {result['t_strong']}, rates {result['rates']}, usable {result['usable']} "
        f"-> {out_dir / CALIBRATION_JSON}")
    return doc


# --------------------------------------------------------------------------
# Reading detection files (combine)
# --------------------------------------------------------------------------

def load_view(det_dir, camera: str) -> Optional[dict]:
    """``detect/<camera>.json`` or None."""
    return read_json(Path(det_dir) / f"{camera}.json")


def image_boxes(doc: Optional[dict], name: str, sha256: Optional[str] = None) -> Optional[list[dict]]:
    """The boxes of image ``name`` (``cycles``, ``polished`` or ``control:<id>``) when its sha256 matches
    ``sha256`` (None: any), else None (missing or stale)."""
    if not doc:
        return None
    if name.startswith("control:"):
        rec = (doc.get("controls") or {}).get(name.split(":", 1)[1])
    else:
        rec = (doc.get("images") or {}).get(name)
    if not rec or not isinstance(rec.get("boxes"), list):
        return None
    if sha256 is not None and rec.get("sha256") != sha256:
        return None
    return rec["boxes"]
