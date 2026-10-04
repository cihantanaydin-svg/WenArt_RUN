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
- **Front** (§2.8): a unique deterministic front in the candidate (``front_deg``, or ``front_candidates`` with one
  distinct value) is kept when at least one pass names a side, also when a pass names another side: the drawing
  outranks the AI (CLAUDE.md trust order: vector geometry > AI suggestions), so a disagreeing pass only adds a warning
  and a ``front_conflict`` (listed in the building's conflicts, never resolved silently; pod B: both models named one
  fixed side for every bed, and dropping the drawn front built real01's south bed reversed). With no deterministic
  front, both passes must name the same side; else ``front`` is None. A side of the iso crop (``top``, ``right``,
  ``bottom``, ``left``; the crops are not rotated, page y up) becomes the footprint axis direction nearest to it
  (0 = +x, 90 = +y, as ``front_deg`` everywhere).

  When both passes agree on an accepted type and both answer ``none`` (no pass contradicts it), the unique
  deterministic front is kept, marked assumed (``front_assumed``, ``front_rule`` = the drawing rule that found it
  when the candidate's ``front_candidates`` are the core's ``{front_deg, rule}`` dicts, a warning; review ingest-6). A
  typed piece that still has no front is oriented by its type's width/depth convention (``oriented_size``, applied by
  the core). The size veto tests the sides rounded to 1 mm (``sides_mm``), as the offered choices do.

``answers`` = ``{model_key: answer dict | None}`` as ``answers.load`` gives per key; the pass number and model id of
each key come from ``answers.model_info`` (check.yaml). ``candidate`` carries ``key``, ``footprint {center, size,
rotation_deg}``, ``strokes``, ``bbox`` and, for the evidence, ``file``, ``page``; optional ``element_id`` (put in
the conflict), ``level``, ``room_id``, ``front_deg`` / ``front_candidates``.

**Question facts** (prep pod finding P5, ``question_facts``): what the question tells the models about one item,
derived only from the drawing: the drawn footprint size; ``choices`` = the types whose size range fits it (+15 %,
``choices_for``) plus ``unknown`` and ``not_furniture`` (the geometry restricts the choice; the models pick among
plausible types); for vector pages the room's printed label and type (``room_label``, ``room_type``) and the
neighbours (``neighbours`` from ``neighbour_facts``: how many pieces of about the same size the room holds, the
larger piece within 0.3 m and how many of the similar ones stand around it). Raster pages give neither room nor
neighbours: their room names and clusters can change with the label answers of the same round, and a symbol question
must ask the same in both rounds. The facts are deterministic (rounded to 1 mm / 1 cm), rendered by
``prompts.symbol_type_prompt`` and hashed by ``crops.question_digest``.
"""
from __future__ import annotations

import math
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
# Types without a front (the question: "a round or square table, a plant, a lamp"; synthetic NO_FRONT_TYPES): a
# typed piece of these with no front is not an assumption worth a warning (core._apply_decision).
FRONTLESS_TYPES: tuple[str, ...] = ("table_dining", "table_coffee", "side_table", "floor_lamp", "potted_plant")
NOT_BUILT_NOTE = "drawn symbol, not built"
CONFLICT_RESOLUTION = "unresolved: the drawn footprint is kept as unknown, unverified"
FRONT_CONFLICT_RESOLUTION = "the drawn front is kept (trust order: vector geometry > AI suggestions)"
QUESTION_KINDS: tuple[str, ...] = ("vector", "raster")
SIMILAR_TOLERANCE = 0.15           # neighbours: sides (sorted) within 15 % (at least 3 cm) count as the same size
SIMILAR_MIN_M = 0.03
NEAR_M = 0.3                       # ... a larger piece (area >= 2x) within 0.3 m of the footprint is "next to" it
LARGER_FACTOR = 2.0
LABEL_MAX_CHARS = 60


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


def oriented_size(size, rotation_deg: float, ftype: str, table: Optional[dict] = None):
    """``(size, rotation_deg, swapped)`` of a typed footprint without a front, in its type's convention (review
    ingest-6): ``size[0]`` is the width (across the front: X of the parametric builder), ``size[1]`` the depth.

    The no-front rule of the core makes the longer side the width; for a bed (1.35-2.0 wide, 1.85-2.25 deep) that
    builds it 90 deg off. The orientation that fits the type's ranges without the tolerance wins, else the one closer
    to the ranges' centres; types whose width and depth ranges are equal (chair, side table, ...) and unknown types
    keep the footprint as it is. Swapping the sides turns the footprint by 90 deg, so the drawn rectangle stays put.
    """
    table = normalise_table(table if table is not None else load_size_table())
    a, b = float(size[0]), float(size[1])
    rotation = float(rotation_deg)
    if ftype not in table:
        return (a, b), rotation, False
    (w0, w1), (d0, d1) = table[ftype]
    if (w0, w1) == (d0, d1):
        return (a, b), rotation, False

    def score(w, d):
        strict = (w0 <= w <= w1) and (d0 <= d <= d1)
        off = abs(w - (w0 + w1) / 2.0) / max(w1 - w0, 1e-6) + abs(d - (d0 + d1) / 2.0) / max(d1 - d0, 1e-6)
        return (0 if strict else 1, off)

    if score(b, a) < score(a, b):
        return (b, a), round((rotation + 90.0) % 180.0, 3), True
    return (a, b), rotation, False


# --------------------------------------------------------------------------
# Question facts (prep pod finding P5)
# --------------------------------------------------------------------------

def choices_for(size, table: Optional[dict] = None) -> list[str]:
    """The types offered for a footprint: every schema type whose size range fits it (+15 %, either orientation, in
    the schema's order) plus ``unknown`` and ``not_furniture``; without a size the full list. Sides are rounded to
    1 mm first, so sub-millimetre noise never changes the list (it is hashed)."""
    if size is None or len(size) < 2:
        return list(schemas.SYMBOL_TYPE_CHOICES)
    table = normalise_table(table if table is not None else load_size_table())
    sides = sides_mm(size)
    fitting = [t for t in schemas.FURNITURE_TYPES if t != "unknown" and fits(table, t, sides)]
    return fitting + ["unknown", schemas.NOT_FURNITURE]


def sides_mm(size) -> tuple[float, float]:
    """The footprint sides rounded to 1 mm: what the offered choices and the size veto of ``decide`` both test, so a
    type offered to the models is never vetoed by sub-millimetre noise (and the reverse)."""
    return round(float(size[0]), 3), round(float(size[1]), 3)


def _clean_label(text) -> Optional[str]:
    if text is None:
        return None
    words = " ".join(str(text).replace('"', "'").split())
    return words[:LABEL_MAX_CHARS] or None


def _cm(values) -> list[float]:
    return [round(float(v), 2) for v in values]


def question_facts(candidate: dict, kind: str = "vector", table: Optional[dict] = None) -> dict:
    """The facts of one item's symbol question (see the module docstring): ``{"kind", "choices", "size_m", "room",
    "neighbours"}``. ``room`` = ``{"label", "type"}`` (``type`` only with a printed label; a room type without one
    would be a guess: "an unlabelled room") or None; ``neighbours`` = ``{"similar", "next_to", "around"}`` or None.
    Raster items get no room and no neighbours. ValueError for another ``kind``."""
    if kind not in QUESTION_KINDS:
        raise ValueError(f"symbol question: unknown crop kind {kind!r}")
    size = (candidate.get("footprint") or {}).get("size")
    facts = {"kind": kind, "choices": choices_for(size, table),
             "size_m": _cm(size[:2]) if size is not None and len(size) >= 2 else None, "room": None,
             "neighbours": None}
    if kind == "raster":
        return facts
    label = _clean_label(candidate.get("room_label"))
    if label:
        facts["room"] = {"label": label, "type": candidate.get("room_type") or None}
    elif candidate.get("room_type") or candidate.get("room_index") is not None:
        facts["room"] = {"label": None, "type": None}
    near = candidate.get("neighbours") or {}
    if any(near.get(k) for k in ("similar", "next_to", "around")):
        facts["neighbours"] = {"similar": near.get("similar") or None,
                               "next_to": _cm(near["next_to"]) if near.get("next_to") else None,
                               "around": near.get("around") or None}
    return facts


def _rect(footprint: dict):
    from shapely.geometry import Polygon
    cx, cy = (float(v) for v in footprint["center"])
    w, d = (float(v) for v in footprint["size"][:2])
    t = math.radians(float(footprint.get("rotation_deg") or 0.0))
    c, s = math.cos(t), math.sin(t)
    pts = [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2),
                                                                 (-w / 2, d / 2))]
    poly = Polygon(pts)
    return poly if poly.area > 0 else poly.buffer(1e-4)


def _similar(a, b) -> bool:
    sa, sb = sorted((float(v) for v in a), reverse=True), sorted((float(v) for v in b), reverse=True)
    return all(abs(x - y) <= max(SIMILAR_MIN_M, SIMILAR_TOLERANCE * max(x, y)) for x, y in zip(sa, sb))


def neighbour_facts(cands: list[dict]) -> dict:
    """``{key: {"similar", "next_to", "around"}}`` for candidates ``{key, footprint, room_index}`` of one page.

    ``similar``: how many candidates of the same room (this one included) have about the same size (sorted sides
    within 15 %, at least 3 cm), or None below 2. ``next_to``: the sides (longer first) of the nearest candidate of
    the same room whose footprint area is at least twice this one's and whose footprint lies within 0.3 m (ties: the
    larger, then the key), or None. ``around``: how many of the similar ones (this one included) are next to that
    same piece, or None below 2. Deterministic: the input order does not matter.
    """
    items = sorted(cands, key=lambda c: str(c["key"]))
    rects = {c["key"]: _rect(c["footprint"]) for c in items}
    sizes = {c["key"]: [float(v) for v in c["footprint"]["size"][:2]] for c in items}
    area = {k: v[0] * v[1] for k, v in sizes.items()}
    room = {c["key"]: c.get("room_index") for c in items}
    similar = {k: [o for o in rects if room[o] == room[k] and _similar(sizes[k], sizes[o])] for k in rects}
    nearest = {}
    for k in rects:
        best = None
        for o in rects:
            if o == k or room[o] != room[k] or area[o] < LARGER_FACTOR * max(area[k], 1e-9):
                continue
            d = rects[k].distance(rects[o])
            if d <= NEAR_M:
                rank = (round(d, 4), -area[o], o)
                if best is None or rank < best[0]:
                    best = (rank, o)
        nearest[k] = best[1] if best else None
    out = {}
    for k in rects:
        n_similar = len(similar[k])
        big = nearest[k]
        around = sum(1 for o in similar[k] if nearest[o] == big) if big is not None else 0
        out[k] = {"similar": n_similar if n_similar >= 2 else None,
                  "next_to": sorted((round(v, 2) for v in sizes[big]), reverse=True) if big is not None else None,
                  "around": around if around >= 2 else None}
    return out


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
    """The ``symbol_type`` request item of a candidate (images relative to ``<out>/recognition``).

    ``question`` holds the item's facts (the ones hashed into ``input_sha256``: ``crops["question"]``, else computed
    for the crops' kind); ``answers.call_args`` asks exactly that question."""
    crops = crops if crops is not None else candidate.get("crops")
    if not crops or "input_sha256" not in crops:
        raise ValueError(f"candidate {candidate.get('key')!r}: render its crops first (crops.render_pair)")
    key = candidate["key"]
    facts = crops.get("question")
    if facts is None:
        facts = question_facts(candidate, (crops.get("crop") or {}).get("kind") or "vector")
    context = {
        "file": candidate.get("file"),
        "level": candidate.get("level"),
        "room_id": candidate.get("room_id"),
        "room_type": candidate.get("room_type"),
        "room_label": candidate.get("room_label"),
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
        "question": _jsonable(facts),
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


def _front_rules(candidate: dict) -> list[tuple[float, Optional[str]]]:
    """The candidate's deterministic fronts as distinct ``(angle, rule)`` pairs: ``front_candidates`` holds plain
    angles or the generic core's ``{"front_deg", "rule"}`` dicts; ``front_deg`` is a plain angle."""
    out: list[tuple[float, Optional[str]]] = []
    for c in list(candidate.get("front_candidates") or []) + [candidate.get("front_deg")]:
        v, rule = (c.get("front_deg"), c.get("rule")) if isinstance(c, dict) else (c, None)
        if v is None:
            continue
        v = float(v) % 360.0
        same = next((k for k, (w, _) in enumerate(out) if _same_angle(v, w)), None)
        if same is None:
            out.append((v, rule))
        elif rule and not out[same][1]:
            out[same] = (out[same][0], rule)
    return out


def _deterministic_front(candidate: dict) -> Optional[float]:
    """The unique deterministic front of the candidate (``front_deg`` or a one-valued ``front_candidates``)."""
    values = _front_rules(candidate)
    return values[0][0] if len(values) == 1 else None


def _front(candidate: dict, passes: list[dict], warnings: list[str]) -> tuple[Optional[float], Optional[str]]:
    """``(front, disagreement)``: see the module docstring (**Front**). ``disagreement`` describes AI fronts that
    contradict the kept drawn front (the caller lists it as a conflict)."""
    ai = [p["front_deg"] for p in passes if p["front_deg"] is not None]
    det = _deterministic_front(candidate)
    if det is not None:
        if not ai:
            return None, None            # no pass named a side: the caller may keep the drawn front as assumed
        other = sorted({round(a, 6) for a in ai if not _same_angle(a, det)})
        if not other:
            return det, None
        rule = _front_rules(candidate)[0][1]
        said = ", ".join(f"pass {p['info']['pass']} ({p['info']['id']}) {p['answer']['front']}" for p in passes
                         if p["front_deg"] is not None)
        description = (f"AI front {sorted(set(round(a, 6) for a in ai))} ({said}) disagrees with the drawn front "
                       f"{det:g} deg" + (f" ({rule})" if rule else ""))
        warnings.append(f"{candidate.get('key')}: {description}: the drawn front is kept (vector geometry > AI)")
        return det, description
    if len(passes) == 2 and len(ai) == 2 and _same_angle(ai[0], ai[1]):
        return ai[0], None
    return None, None


def _evidence(candidate: dict, info: dict, ans: dict) -> dict:
    ev = B.evidence(str(candidate.get("file") or ""), "ai", float(ans["confidence"]), page=candidate.get("page"),
                    entity=f"recognition:{candidate.get('key')}", model=info["id"], pass_=info["pass"],
                    text=ans["type"])
    ev["front"] = ans["front"]
    ev["reason"] = ans["reason"]
    return ev


def decide(candidate: dict, answers: Optional[dict], size_table: dict, room_type: Optional[str]) -> dict:
    """The two-pass rule of §3.3 for one candidate; see the module docstring.

    Returns ``{"type", "status", "type_method", "type_candidates", "front", "front_assumed", "front_rule",
    "confidence", "ai_evidence", "conflict", "build", "note", "warnings"}``; ``ai_evidence`` has one evidence dict per
    pass that answered (two when both did), ``conflict`` is ``{"kind", "element_ids", "description", "resolution"}``
    or None.
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
              "front": None, "front_assumed": False, "front_rule": None, "confidence": None, "ai_evidence": evidence,
              "conflict": None, "front_conflict": None, "build": True, "note": None, "warnings": warnings}
    element_ids = [str(candidate["element_id"])] if candidate.get("element_id") else []

    def conflict(description: str) -> dict:
        return {"kind": "symbol_type_disagreement", "element_ids": element_ids, "description": description,
                "resolution": CONFLICT_RESOLUTION}

    types = [p["answer"]["type"] for p in passes]
    if len(passes) == 2 and types[0] == types[1] == schemas.NOT_FURNITURE:
        result.update(build=False, note=NOT_BUILT_NOTE)
        warnings.append(f"{key}: both passes say not_furniture: kept as an obstacle, not built")
        return result
    result["front"], disagreement = _front(candidate, passes, warnings)
    if disagreement is not None:
        result["front_rule"] = _front_rules(candidate)[0][1]
        result["front_conflict"] = {"kind": "symbol_front_disagreement", "element_ids": element_ids,
                                    "description": f"{key}: {disagreement}", "resolution": FRONT_CONFLICT_RESOLUTION}
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
    if not fits(size_table, agreed, sides_mm(size)):
        w, d = (float(v) for v in size)
        result["conflict"] = conflict(f"{key}: both passes say {agreed}, but the drawn footprint {w:.2f} x {d:.2f} m "
                                      f"is outside the {agreed} size range")
        warnings.append(f"{key}: size veto: {agreed} does not fit {w:.2f} x {d:.2f} m")
        return result
    result.update(type=agreed, status="verified", type_method="ai_two_pass",
                  confidence=round(min(min(float(p["answer"]["confidence"]) for p in passes), CONFIDENCE_CAP), 4))
    det = _deterministic_front(candidate)
    if result["front"] is None and det is not None and all(p["front_deg"] is None for p in passes):
        # Both passes answer 'none': nothing contradicts the drawn front (pillows, wall, table), so it stays,
        # marked assumed with the rule that found it (review ingest-6: dropping it built real01's beds 90 deg off).
        rule = _front_rules(candidate)[0][1]
        result.update(front=det, front_assumed=True, front_rule=rule)
        warnings.append(f"{key}: front assumed: both passes answered none; the drawn front {det:g} deg"
                        + (f" ({rule})" if rule else "") + " is kept")
    allowed = allowed_types(room_type)
    if allowed is not None and agreed not in allowed:
        result["status"] = "unverified"
        warnings.append(f"{key}: {agreed} is not a type allowed in a {room_type} room: kept, unverified")
    if agreed in HALL_ONLY_TYPES:
        result["status"] = "unverified"
        warnings.append(f"{key}: stair named by both passes, but the stair rule found no treads there: flights "
                        "unknown, unverified")
    return result

