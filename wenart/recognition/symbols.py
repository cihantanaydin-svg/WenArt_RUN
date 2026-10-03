"""AI typing of one unnamed drawn object: the question and the two-pass rule (docs/milestone7.md §3.2, §3.3).

The generic core (``wenart.ingest.generic``) finds furniture **footprints** in the geometry; a footprint that no
rule and no block name types becomes an AI candidate. This module asks both models about it and decides what the
building may say:

- ``question(candidate, crops=None)``: the ``symbol_type`` request item (``answers.write_requests``) for a
  candidate whose two crops ``crops.render_pair`` drew (``crops`` defaults to ``candidate["crops"]``).
- ``decide(candidate, answers, size_table, room_type)``: the two-pass rule. A type T is accepted
  (``type_method "ai_two_pass"``, ``verified``, confidence = the lower of the two, capped at 0.9) only when both
  passes answer T **and** the drawn footprint fits T's size range (``size_table.yaml``, either orientation, +15 %).
  Otherwise the piece stays ``unknown`` / ``unverified`` with both answers in ``type_candidates``: different types or
  a size veto give a ``symbol_type_disagreement`` conflict; a missing, null or empty answer never counts as
  agreement (warning, no conflict); both ``unknown`` is no conflict either. Both ``not_furniture`` keep the piece in
  the building as ``unknown`` / ``unverified`` with ``build: false`` (an obstacle, not rendered; the room keeps
  ``has_documented_furniture``), noted "drawn symbol, not built". An accepted type that is not allowed in the room
  (``furniture.schemas.ALLOWED_TYPES`` + ``side_table``, ``floor_lamp``, ``potted_plant`` everywhere, ``stair`` in
  halls) is kept, ``unverified``, with a warning. An accepted ``stair`` is always ``unverified``: the stair rule of
  §2.8 found no treads there, so flights and landing are unknown.
- **Front** (§2.8): with a unique deterministic front in the candidate (``front_deg``, or ``front_candidates`` with
  one distinct value) the result keeps it only when at least one pass names that side and none names another; with
  none, both passes must name the same side; else ``front`` is None. A side of the iso crop (``top``, ``right``,
  ``bottom``, ``left``; the crops are not rotated, page y up) becomes the footprint axis direction nearest to it
  (0 = +x, 90 = +y, as ``front_deg`` everywhere).

``answers`` = ``{model_key: answer dict | None}`` as ``answers.load`` gives per key; the pass number and model id of
each key come from ``answers.model_info`` (check.yaml). ``candidate`` carries ``key``, ``footprint {center, size,
rotation_deg}``, ``strokes``, ``bbox`` and, for the evidence, ``file``, ``page``; optional ``element_id`` (put in
the conflict), ``level``, ``room_id``, ``front_deg`` / ``front_candidates``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from wenart import building as B
from wenart.recognition import answers as A
from wenart.recognition import schemas

TASK = "symbol_type"
SIZE_TABLE_PATH = Path(__file__).resolve().parent / "size_table.yaml"
SIZE_TOLERANCE = 0.15
CONFIDENCE_CAP = 0.9
EVERYWHERE_TYPES: tuple[str, ...] = ("side_table", "floor_lamp", "potted_plant")
HALL_ONLY_TYPES: tuple[str, ...] = ("stair",)
# Room types the layout table may not have yet (docs/milestone7.md §6.5 adds dining to ALLOWED_TYPES).
ROOM_TYPE_FALLBACK: dict[str, tuple[str, ...]] = {"dining": ("table_dining", "chair", "dresser", "bookshelf")}
FRONT_SIDE_DEG: dict[str, float] = {"right": 0.0, "top": 90.0, "left": 180.0, "bottom": 270.0}
NOT_BUILT_NOTE = "drawn symbol, not built"
CONFLICT_RESOLUTION = "unresolved: the drawn footprint is kept as unknown, unverified"


# --------------------------------------------------------------------------
# Size table
# --------------------------------------------------------------------------

def load_size_table(path: Optional[Path] = None) -> dict:
    """``size_table.yaml`` as ``{type: ((w_min, w_max), (d_min, d_max))}`` (the shape of the core's table)."""
    import yaml
    data = yaml.safe_load(Path(SIZE_TABLE_PATH if path is None else path).read_text(encoding="utf-8")) or {}
    return normalise_table(data.get("types", data))


def normalise_table(table: dict) -> dict:
    """Accept ``{t: ((w0, w1), (d0, d1))}`` or ``{t: {"width": [w0, w1], "depth": [d0, d1], ...}}``."""
    out = {}
    for name, spec in (table or {}).items():
        if isinstance(spec, dict):
            w, d = spec.get("width", spec.get("width_m")), spec.get("depth", spec.get("depth_m"))
        else:
            w, d = spec
        out[name] = ((float(w[0]), float(w[1])), (float(d[0]), float(d[1])))
    return out


def fits(table: dict, ftype: str, size, tolerance: float = SIZE_TOLERANCE) -> bool:
    """Whether a footprint (a, b) lies in ``ftype``'s ranges in either orientation, ``tolerance`` on top."""
    table = normalise_table(table)
    if ftype not in table:
        return False
    (w0, w1), (d0, d1) = table[ftype]
    a, b = float(size[0]), float(size[1])

    def inside(v, lo, hi):
        return lo / (1.0 + tolerance) <= v <= hi * (1.0 + tolerance)
    return (inside(a, w0, w1) and inside(b, d0, d1)) or (inside(a, d0, d1) and inside(b, w0, w1))


# --------------------------------------------------------------------------
# Question
# --------------------------------------------------------------------------

def _jsonable(value):
    """Tuples, numpy scalars and arrays -> plain JSON values."""
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "tolist"):
        return _jsonable(value.tolist())
    if isinstance(value, float):
        return round(value, 4)
    return value


def question(candidate: dict, crops: Optional[dict] = None) -> dict:
    """The ``symbol_type`` request item of a candidate (images relative to ``<out>/recognition``)."""
    crops = crops if crops is not None else candidate.get("crops")
    if not crops or "input_sha256" not in crops:
        raise ValueError(f"candidate {candidate.get('key')!r}: render its crops first (crops.render_pair)")
    key = candidate["key"]
    context = {
        "file": candidate.get("file"),
        "level": candidate.get("level"),
        "room_id": candidate.get("room_id"),
        "room_type": candidate.get("room_type"),
        "footprint": _jsonable(candidate.get("footprint")),
        "bbox": _jsonable(candidate.get("bbox")),
        "crop": crops.get("crop"),
    }
    return {
        "key": key,
        "task": TASK,
        "page": candidate.get("page"),
        "images": [f"{A.CROPS_DIR}/{Path(crops['ctx_png']).name}", f"{A.CROPS_DIR}/{Path(crops['iso_png']).name}"],
        "context": context,
        "input_sha256": crops["input_sha256"],
    }


# --------------------------------------------------------------------------
# Two-pass rule
# --------------------------------------------------------------------------

def allowed_types(room_type: Optional[str]) -> Optional[set]:
    """The types allowed in a room type (§3.3), or None when the room type is unknown (no veto possible)."""
    if not room_type or room_type == "unknown":
        return None
    from wenart.furniture.schemas import ALLOWED_TYPES
    base = ALLOWED_TYPES.get(room_type)
    if base is None:
        base = ROOM_TYPE_FALLBACK.get(room_type, ())
    allowed = set(base) | set(EVERYWHERE_TYPES)
    if room_type == "hall":
        allowed |= set(HALL_ONLY_TYPES)
    return allowed


def _answer(data) -> Optional[dict]:
    """A usable answer (schema-valid, non-empty type) or None: empty answers never count."""
    if not isinstance(data, dict) or not str(data.get("type") or "").strip():
        return None
    if schemas.validation_errors(TASK, data):
        return None
    return data


def _snap_front(side: str, rotation_deg: float) -> Optional[float]:
    """A side of the (unrotated) iso crop -> the footprint axis direction nearest to it, in [0, 360)."""
    if side not in FRONT_SIDE_DEG:
        return None
    target = FRONT_SIDE_DEG[side]
    axes = [(float(rotation_deg) + 90.0 * k) % 360.0 for k in range(4)]
    best = min(axes, key=lambda a: abs((a - target + 180.0) % 360.0 - 180.0))
    return round(best % 360.0, 6)


def _same_angle(a: float, b: float, tol: float = 1.0) -> bool:
    return abs((a - b + 180.0) % 360.0 - 180.0) <= tol


def _deterministic_front(candidate: dict) -> Optional[float]:
    """The unique deterministic front of the candidate (``front_deg`` or a one-valued ``front_candidates``)."""
    values = []
    for v in list(candidate.get("front_candidates") or []) + [candidate.get("front_deg")]:
        if v is None:
            continue
        v = float(v) % 360.0
        if not any(_same_angle(v, w) for w in values):
            values.append(v)
    return values[0] if len(values) == 1 else None


def _front(candidate: dict, passes: list[dict], warnings: list[str]) -> Optional[float]:
    ai = [p["front_deg"] for p in passes if p["front_deg"] is not None]
    det = _deterministic_front(candidate)
    if det is not None:
        if ai and all(_same_angle(a, det) for a in ai):
            return det
        if any(not _same_angle(a, det) for a in ai):
            warnings.append(f"{candidate.get('key')}: AI front {sorted(set(ai))} disagrees with the drawn front "
                            f"{det:g}: front unknown")
        return None
    if len(passes) == 2 and len(ai) == 2 and _same_angle(ai[0], ai[1]):
        return ai[0]
    return None


def _evidence(candidate: dict, info: dict, ans: dict) -> dict:
    ev = B.evidence(str(candidate.get("file") or ""), "ai", float(ans["confidence"]), page=candidate.get("page"),
                    entity=f"recognition:{candidate.get('key')}", model=info["id"], pass_=info["pass"],
                    text=ans["type"])
    ev["front"] = ans["front"]
    ev["reason"] = ans["reason"]
    return ev


def decide(candidate: dict, answers: Optional[dict], size_table: dict, room_type: Optional[str]) -> dict:
    """The two-pass rule of §3.3 for one candidate; see the module docstring.

    Returns ``{"type", "status", "type_method", "type_candidates", "front", "confidence", "ai_evidence",
    "conflict", "build", "note", "warnings"}``; ``ai_evidence`` has one evidence dict per pass that answered (two
    when both did), ``conflict`` is ``{"kind", "element_ids", "description", "resolution"}`` or None.
    """
    answers = answers or {}
    models = A.load_models()
    key = candidate.get("key")
    size = (candidate.get("footprint") or {}).get("size") or [0.0, 0.0]
    rotation = float((candidate.get("footprint") or {}).get("rotation_deg") or 0.0)
    warnings: list[str] = []
    passes: list[dict] = []
    evidence: list[dict] = []
    candidates: list[dict] = []
    for mk in A.MODEL_KEYS:
        info = A.model_info(mk, models)
        raw = answers.get(mk)
        ans = _answer(raw)
        if ans is None:
            what = "no answer" if raw is None else "an empty or invalid answer"
            warnings.append(f"{key}: pass {info['pass']} ({info['id']}) gave {what}: no agreement possible")
            continue
        front_deg = _snap_front(ans["front"], rotation)
        passes.append({"key": mk, "info": info, "answer": ans, "front_deg": front_deg})
        evidence.append(_evidence(candidate, info, ans))
        candidates.append({"type": ans["type"], "model": info["id"], "model_key": mk, "pass": info["pass"],
                           "confidence": float(ans["confidence"]), "front": ans["front"], "reason": ans["reason"]})
    result = {"type": "unknown", "status": "unverified", "type_method": "none", "type_candidates": candidates,
              "front": None, "confidence": None, "ai_evidence": evidence, "conflict": None, "build": True,
              "note": None, "warnings": warnings}
    element_ids = [str(candidate["element_id"])] if candidate.get("element_id") else []

    def conflict(description: str) -> dict:
        return {"kind": "symbol_type_disagreement", "element_ids": element_ids, "description": description,
                "resolution": CONFLICT_RESOLUTION}

    types = [p["answer"]["type"] for p in passes]
    if len(passes) == 2 and types[0] == types[1] == schemas.NOT_FURNITURE:
        result.update(build=False, note=NOT_BUILT_NOTE)
        warnings.append(f"{key}: both passes say not_furniture: kept as an obstacle, not built")
        return result
    result["front"] = _front(candidate, passes, warnings)
    if len(passes) < 2:
        return result
    if types[0] != types[1]:
        said = ", ".join(f"pass {p['info']['pass']} ({p['info']['id']}) {p['answer']['type']}" for p in passes)
        result["conflict"] = conflict(f"{key}: the passes disagree: {said}")
        return result
    agreed = types[0]
    if agreed == "unknown":
        warnings.append(f"{key}: both passes say unknown: type left open")
        return result
    if not fits(size_table, agreed, size):
        w, d = (float(v) for v in size)
        result["conflict"] = conflict(f"{key}: both passes say {agreed}, but the drawn footprint {w:.2f} x {d:.2f} m "
                                      f"is outside the {agreed} size range")
        warnings.append(f"{key}: size veto: {agreed} does not fit {w:.2f} x {d:.2f} m")
        return result
    result.update(type=agreed, status="verified", type_method="ai_two_pass",
                  confidence=round(min(min(float(p["answer"]["confidence"]) for p in passes), CONFIDENCE_CAP), 4))
    allowed = allowed_types(room_type)
    if allowed is not None and agreed not in allowed:
        result["status"] = "unverified"
        warnings.append(f"{key}: {agreed} is not a type allowed in a {room_type} room: kept, unverified")
    if agreed in HALL_ONLY_TYPES:
        result["status"] = "unverified"
        warnings.append(f"{key}: stair named by both passes, but the stair rule found no treads there: flights "
                        "unknown, unverified")
    return result

