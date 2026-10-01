"""Two-pass symbol detection: two independent models, keep what agrees.

Rule (docs/milestone2.md, section 3 and CLAUDE.md): a symbol proposed by both
models with box IoU >= 0.5 and the same type is ``verified`` with
``confidence = min(both)``; everything else is ``unverified`` and keeps every
proposal in its evidence, tagged ``pass`` 1 (model A) or 2 (model B). Nothing
is dropped silently: an unverified symbol still appears, so the report can list it.

Rotation is part of the agreement too (CLAUDE.md: "keep only what agrees",
orientation is part of the furniture contract): when both passes give a
rotation and they differ by more than ``ROTATION_TOL_DEG``, the type and box
stay agreed (``agreement: "type_box"``) but ``rotation_deg`` is null, the symbol
is ``unverified`` and both values are kept in ``rotation_candidates`` and in the
evidence entries.

Matching is greedy by descending IoU over pairs of equal type. Pairs that
overlap (IoU >= threshold) but disagree on the type are joined into one
unverified item with ``type_candidates`` listing both types, because that is
exactly the "type unclear, footprint clear" case of the furniture rules.

``two_pass`` takes a ``run`` callable so the logic is testable without a GPU:
``run(model, image) -> list[{"type", "box", "rotation_deg", "confidence"}]``
(boxes in page pixels). The default ``run`` calls the vLLM client.
"""
from __future__ import annotations

from typing import Callable, Optional, Sequence

from wenart import building as B
from wenart import geometry as G
from wenart.recognition import vlm_client

IOU_THRESHOLD = 0.5
ROTATION_TOL_DEG = 15.0   # two passes agree on the rotation within this (symbol rotations are coarse)

Runner = Callable[[str, object], list[dict]]


def _mean_box(a: Sequence[float], b: Sequence[float]) -> list[float]:
    return [round((a[i] + b[i]) / 2.0, 1) for i in range(4)]


def match_proposals(a_items: list[dict], b_items: list[dict], iou_thresh: float = IOU_THRESHOLD
                    ) -> tuple[list[tuple[int, int, float]], list[tuple[int, int, float]], list[int], list[int]]:
    """Greedy one-to-one matching of two proposal lists by IoU.

    Returns ``(agreed, type_clashes, unmatched_a, unmatched_b)`` where ``agreed``
    and ``type_clashes`` are ``(index_a, index_b, iou)`` triples: ``agreed`` pairs
    share the type, ``type_clashes`` overlap but differ in type.
    """
    pairs = []
    for i, a in enumerate(a_items):
        for j, b in enumerate(b_items):
            iou = G.box_iou(a["box"], b["box"])
            if iou >= iou_thresh:
                # Same type wins over a type clash at equal IoU.
                pairs.append((iou, a["type"] == b["type"], i, j))
    pairs.sort(key=lambda p: (p[0], p[1]), reverse=True)
    used_a: set[int] = set()
    used_b: set[int] = set()
    agreed, clashes = [], []
    for iou, same_type, i, j in pairs:
        if i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        (agreed if same_type else clashes).append((i, j, iou))
    unmatched_a = [i for i in range(len(a_items)) if i not in used_a]
    unmatched_b = [j for j in range(len(b_items)) if j not in used_b]
    return agreed, clashes, unmatched_a, unmatched_b


def _evidence(file: str, model: str, pass_no: int, item: dict) -> dict:
    """Evidence entry for one proposal; ``text`` keeps the type the model answered.

    The rotation the model answered is kept as well (``rotation_deg``), so a
    rotation disagreement stays traceable to the pass that said it.
    """
    ev = B.evidence(file, "ai", float(item.get("confidence", 0.0)), model=model, pass_=pass_no,
                    pixel_box=[float(v) for v in item["box"]], text=item["type"])
    if item.get("rotation_deg") is not None:
        ev["rotation_deg"] = item["rotation_deg"]
    return ev


def agreed_rotation(a_rot, b_rot, tol_deg: float = ROTATION_TOL_DEG) -> tuple:
    """Rotation of a type/box-agreed pair: ``(rotation_deg, agrees)``.

    Both given and within ``tol_deg``: pass 1's value, agrees. Only one given:
    that value (the other pass did not contradict it). Both given but apart by
    more than ``tol_deg``: ``None`` and ``agrees = False``.
    """
    if a_rot is None:
        return b_rot, True
    if b_rot is None:
        return a_rot, True
    if G.angle_difference_deg(float(a_rot), float(b_rot)) <= tol_deg:
        return a_rot, True
    return None, False


def combine(a_items: list[dict], b_items: list[dict], model_a: str, model_b: str, file: str,
            iou_thresh: float = IOU_THRESHOLD, rotation_tol: float = ROTATION_TOL_DEG) -> list[dict]:
    """Merge the proposals of two models into verified / unverified symbols (pure).

    Each result: ``{"type", "box", "rotation_deg", "confidence", "status",
    "type_candidates", "evidence": [...]}``. Verified symbols use the mean box
    and the rotation of pass 1 (pass 2's rotation when pass 1 has none). Type/box
    pairs whose rotations differ by more than ``rotation_tol`` are ``unverified``
    with ``rotation_deg`` null, ``agreement: "type_box"`` and
    ``rotation_candidates: [pass 1, pass 2]``; fully agreed symbols carry
    ``agreement: "type_box_rotation"``.
    """
    agreed, clashes, rest_a, rest_b = match_proposals(a_items, b_items, iou_thresh)
    out = []
    for i, j, iou in agreed:
        a, b = a_items[i], b_items[j]
        rotation, rotation_agrees = agreed_rotation(a.get("rotation_deg"), b.get("rotation_deg"), rotation_tol)
        symbol = {
            "type": a["type"],
            "box": _mean_box(a["box"], b["box"]),
            "rotation_deg": rotation,
            "confidence": round(min(float(a["confidence"]), float(b["confidence"])), 4),
            "status": "verified" if rotation_agrees else "unverified",
            "agreement": "type_box_rotation" if rotation_agrees else "type_box",
            "type_candidates": [a["type"]],
            "iou": round(iou, 3),
            "evidence": [_evidence(file, model_a, 1, a), _evidence(file, model_b, 2, b)],
        }
        if not rotation_agrees:
            symbol["rotation_candidates"] = [a["rotation_deg"], b["rotation_deg"]]
        out.append(symbol)
    for i, j, iou in clashes:
        a, b = a_items[i], b_items[j]
        out.append({
            "type": a["type"],
            "box": _mean_box(a["box"], b["box"]),
            "rotation_deg": a.get("rotation_deg"),
            "confidence": round(min(float(a["confidence"]), float(b["confidence"])), 4),
            "status": "unverified",
            "type_candidates": [a["type"], b["type"]],
            "iou": round(iou, 3),
            "evidence": [_evidence(file, model_a, 1, a), _evidence(file, model_b, 2, b)],
        })
    for items, model, pass_no, indices in ((a_items, model_a, 1, rest_a), (b_items, model_b, 2, rest_b)):
        for k in indices:
            item = items[k]
            out.append({
                "type": item["type"],
                "box": [round(float(v), 1) for v in item["box"]],
                "rotation_deg": item.get("rotation_deg"),
                "confidence": round(float(item["confidence"]), 4),
                "status": "unverified",
                "type_candidates": [item["type"]],
                "iou": 0.0,
                "evidence": [_evidence(file, model, pass_no, item)],
            })
    return out


def default_runner(base_url: str = vlm_client.DEFAULT_BASE_URL, **client_kwargs) -> Runner:
    """A ``run(model, image)`` that asks the vLLM server at ``base_url`` for symbols.

    The server serves one model at a time (see scripts/jobs/bakeoff.sh), so the
    caller must make sure ``model`` is the one being served.
    """
    def run(model: str, image) -> list[dict]:
        client = vlm_client.VLMClient(base_url, model=model, **client_kwargs)
        result = client.run_task("symbols", image)
        if result.data is None:
            raise RuntimeError(f"{model}: {result.error}")
        return result.data["items"]
    return run


def two_pass(page, model_a: str, model_b: str, run: Optional[Runner] = None, *,
             file: Optional[str] = None, iou_thresh: float = IOU_THRESHOLD) -> dict:
    """Run the symbol task with both models on ``page`` (an image path) and combine.

    Returns ``{"symbols": [...], "pass1": [...], "pass2": [...], "models": [a, b]}``.
    """
    runner = run or default_runner()
    pass1 = runner(model_a, page)
    pass2 = runner(model_b, page)
    evidence_file = file if file is not None else str(page)
    symbols = combine(pass1, pass2, model_a, model_b, evidence_file, iou_thresh)
    return {"symbols": symbols, "pass1": pass1, "pass2": pass2, "models": [model_a, model_b]}
