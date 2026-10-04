"""Two models, one verdict per element, extras, counts and the polish decision (docs/milestone5.md §5.4, §5.5).

Per element (passes A = qwen, B = glm, independent):

| A / B | result |
|---|---|
| present + present | ok |
| absent + absent | missing |
| different + different | changed |
| absent + different | missing_or_changed |
| present + absent/different | disputed |
| unsure + X | unverified (``single`` = X) |
| a failed or stale call | not_computed (never absent) |

- A pass that answers the sentinel decoy ``present`` is ``unreliable`` for
  that image: its element answers count as ``unsure`` and its extras and
  counts confirm nothing.
- Type-unverified pieces: only present/absent counts; ``different`` is
  read as ``present`` and noted.
- One model only (``CHECK_MODELS`` with one key): every result is
  ``unverified``, every verdict ``info``, ``single_pass: true``.
- Extras: those >= 50 % covered by one indexed element's mask of the list's
  render are dropped (they are listed elements; for an insertion call the
  normal render without the target, the image actually shown); A/B extras
  with IoU >= 0.3 and the same class are ``confirmed``; decor extras are info.
- Counts: expected range ``[required, required + optional + ignored]`` of
  that kind; a mismatch needs every pass outside it on the same side.
- Verdict per image: ``not_computed`` (a pass missing), ``info`` (single
  pass), ``mismatch`` (a required element confirmed missing/changed, a
  confirmed non-decor extra or a count mismatch), ``info`` (disputed,
  unverified, unreliable, unconfirmed extras), else ``ok``.
- added_by_ai elements with a mismatch carry the note "added_by_ai:
  render/polish issue, not a document conflict".

Polish decision (differential, active even when the check is advisory):
the polished candidate is rejected (``vision_check``) when an element ok or
unverified on the Cycles render is confirmed missing/changed on the polished
one, or a confirmed furniture/fixture/door/window extra appears that no
confirmed Cycles extra matches (``added_by_polish``); a polished or Cycles
image with a not-computed or unreliable pass gives ``check_incomplete``. A
mismatch confirmed on the Cycles render itself, or a JSON cross-check
finding, marks the view ``needs_review`` (never fixed).

Added-object detector (docs/milestone7.md §8.1, ``wenart.gate.detect``),
read from ``detect/<cam>.json`` when ``check.yaml`` has a ``detector:`` block
(``t_det``, ``t_strong``; the detection must be of the very images checked,
by sha256):

- candidates = polished boxes >= ``t_det`` with no Cycles box of the same
  group at IoU >= 0.3 and not covered >= 50 % by one element of a compatible
  type in the view's pass-index map;
- ``combine_extras``: an extra of one reliable pass that a candidate of the
  same family (decor or not) overlaps at IoU >= 0.3 is confirmed
  (``confirmed_by: detector``), so it counts like an extra both passes saw;
- a candidate is confirmed by its score (>= ``t_strong``) or by a polished
  extra of either reliable pass at IoU >= 0.3; a confirmed non-decor one
  rejects the polished image (``what: added_by_polish``, ``source:
  detector``) and sets the view's ``added_by_polish``; the report then uses
  the Cycles image. A polished view without a current detection is
  ``check_incomplete`` (the added-object check did not run on it);
- insertion controls (``insertion:<id>``, the normal render against the
  hidden one) get ``detector_control`` (hit score, flagged, confirmed) so
  ``calibrate`` records the detector's insertion rate of every run (info,
  never a target).
Without the block the detector is advisory: each polished view lists its
unmatched boxes under ``detector``, nothing is confirmed or rejected.
"""
from __future__ import annotations

import os
from typing import Optional

import numpy as np

from wenart.gate import detect as D
from wenart.recognition.vlm_client import norm1000_to_pixels
from wenart.vision_check import calls as C
from wenart.vision_check import preference as R
from wenart.vision_check import schemas as S
from wenart.vision_check.project import Project, rel

MISMATCH_RESULTS = ("missing", "changed", "missing_or_changed")
CONFIRMED_GONE = MISMATCH_RESULTS
ADDED_BY_AI_NOTE = "added_by_ai: render/polish issue, not a document conflict"
UNVERIFIED_TYPE_NOTE = "type unverified: 'different' counted as present (info)"
DEFAULT_MODELS = ("qwen", "glm")


def model_keys(arg: Optional[str] = None) -> list[str]:
    """Model keys from ``--models``, else ``CHECK_MODELS`` (space or comma separated), else qwen glm."""
    text = arg if arg else os.environ.get("CHECK_MODELS", "")
    keys = [k for k in text.replace(",", " ").split() if k]
    return keys or list(DEFAULT_MODELS)


# --------------------------------------------------------------------------
# Per element
# --------------------------------------------------------------------------

def element_result(statuses: list, single_pass: bool) -> tuple[str, Optional[str]]:
    """``(result, single)`` of one element from the pass statuses (None = not computed), §5.4."""
    if not statuses or any(s is None for s in statuses):
        return "not_computed", None
    if single_pass:
        return "unverified", statuses[0]
    known = [s for s in statuses if s != "unsure"]
    if len(known) < len(statuses):
        if not known:
            return "unverified", None
        if len(known) == 1:
            return "unverified", known[0]
    if all(s == "present" for s in known):
        return "ok", None
    if all(s == "absent" for s in known):
        return "missing", None
    if all(s == "different" for s in known):
        return "changed", None
    if all(s in ("absent", "different") for s in known):
        return "missing_or_changed", None
    return "disputed", None


def _pass_data(rec: Optional[dict]) -> Optional[dict]:
    return None if rec is None else rec.get("data")


# --------------------------------------------------------------------------
# Extras and counts
# --------------------------------------------------------------------------

def box_iou(a, b) -> float:
    ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / union if union > 0 else 0.0


def covered_frac(box_px, index_map: Optional[np.ndarray]) -> float:
    """Largest share of the box's pixels covered by one indexed element's mask (one pass index > 0)."""
    if index_map is None:
        return 0.0
    H, W = index_map.shape
    x0, y0 = max(0, int(np.floor(box_px[0]))), max(0, int(np.floor(box_px[1])))
    x1, y1 = min(W, int(np.ceil(box_px[2]))), min(H, int(np.ceil(box_px[3])))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    patch = index_map[y0:y1, x0:x1].ravel()
    counts = np.bincount(patch.astype(np.int64))
    counts[0] = 0
    return float(counts.max()) / float(patch.size)


def box_cover(box, target) -> float:
    """Share of ``target`` covered by ``box`` (both pixel boxes)."""
    ix = max(0.0, min(box[2], target[2]) - max(box[0], target[0]))
    iy = max(0.0, min(box[3], target[3]) - max(box[1], target[1]))
    area = (target[2] - target[0]) * (target[3] - target[1])
    return ix * iy / area if area > 0 else 0.0


def parse_extras(data: dict, size, index_map, cfg: dict) -> tuple[list, int]:
    """``(kept extras, dropped count)`` of one pass; boxes to pixels, class, coverage by indexed pixels."""
    W, H = size
    kept, dropped = [], 0
    for ex in data.get("extras") or []:
        box_px = norm1000_to_pixels(ex["box"], W, H)
        if box_px[2] - box_px[0] <= 0 or box_px[3] - box_px[1] <= 0:
            dropped += 1
            continue
        cov = covered_frac(box_px, index_map)
        if cov >= float(cfg["extras"]["covered_frac"]):
            dropped += 1
            continue
        kept.append({"category": ex["category"], "class": S.category_class(ex["category"], ex["box"]),
                     "box_1000": [float(v) for v in ex["box"]], "box_px": box_px,
                     "confidence": ex.get("confidence"), "covered": round(cov, 3)})
    return kept, dropped


def _family(cls: Optional[str]) -> str:
    return "decor" if cls == "decor" else "object"


def combine_extras(per_pass: dict, keys: list, reliable: list, single_pass: bool, cfg: dict,
                   detector: Optional[list] = None) -> list[dict]:
    """Confirmed extras (A/B matched by IoU and class) and the unconfirmed rest, one list.

    ``detector``: added-object candidates of this image (``detect.added_candidates`` at ``t_det``); an extra
    of one reliable pass that a candidate of the same family (decor or not) overlaps at IoU >= 0.3 counts as
    confirmed (``confirmed_by: "detector"``, M7 §8.1). Never in single-pass mode.
    """
    out = []
    used = {k: set() for k in keys}
    if not single_pass and len(reliable) == 2:
        a, b = reliable
        pairs = []
        for i, ea in enumerate(per_pass.get(a) or []):
            for j, eb in enumerate(per_pass.get(b) or []):
                if ea["class"] == eb["class"]:
                    iou = box_iou(ea["box_px"], eb["box_px"])
                    if iou >= float(cfg["extras"]["match_iou"]):
                        pairs.append((iou, i, j))
        for iou, i, j in sorted(pairs, key=lambda p: (-p[0], p[1], p[2])):
            if i in used[a] or j in used[b]:
                continue
            used[a].add(i)
            used[b].add(j)
            ea, eb = per_pass[a][i], per_pass[b][j]
            box = [min(ea["box_px"][0], eb["box_px"][0]), min(ea["box_px"][1], eb["box_px"][1]),
                   max(ea["box_px"][2], eb["box_px"][2]), max(ea["box_px"][3], eb["box_px"][3])]
            out.append({"class": ea["class"], "categories": {a: ea["category"], b: eb["category"]},
                        "boxes_1000": {a: ea["box_1000"], b: eb["box_1000"]}, "box_px": box,
                        "iou": round(iou, 3), "confirmed": True, "passes": [a, b],
                        "info": ea["class"] == "decor"})
    match_iou = float(cfg["extras"]["match_iou"])
    for k in keys:
        for i, e in enumerate(per_pass.get(k) or []):
            if i in used[k]:
                continue
            x = {"class": e["class"], "categories": {k: e["category"]}, "boxes_1000": {k: e["box_1000"]},
                 "box_px": e["box_px"], "iou": None, "confirmed": False, "passes": [k],
                 "info": True, "unreliable": k not in reliable}
            if detector and not single_pass and k in reliable:
                hits = [c for c in detector if _family(c.get("class")) == _family(e["class"])
                        and box_iou(c["box_px"], e["box_px"]) >= match_iou]
                if hits:
                    best = max(hits, key=lambda c: (float(c["score"]), box_iou(c["box_px"], e["box_px"])))
                    x.update(confirmed=True, confirmed_by="detector", info=e["class"] == "decor",
                             detector={"group": best["group"], "score": best["score"], "box_px": best["box_px"],
                                       "iou": round(box_iou(best["box_px"], e["box_px"]), 3)})
            out.append(x)
    return out


def combine_counts(datas: dict, keys: list, reliable: list, single_pass: bool, expected: dict) -> dict:
    """Door and window counts against the expected range of the list's render."""
    out = {}
    elements = expected.get("elements") or []
    for kind, field_name in (("door", "door_count"), ("window", "window_count")):
        els = [e for e in elements if e.get("kind") == kind]
        lo = sum(1 for e in els if e.get("role") == "required")
        hi = len(els)
        vals = {k: (None if datas.get(k) is None else int(datas[k][field_name])) for k in keys}
        sides = {k: (None if v is None else ("fewer" if v < lo else "more" if v > hi else "ok"))
                 for k, v in vals.items()}
        if any(v is None for v in vals.values()):
            result = "not_computed"
        elif single_pass:
            result = "unverified" if sides[keys[0]] != "ok" else "ok"
        else:
            used = [sides[k] for k in keys if k in reliable]
            if len(used) < len(keys):
                result = "unverified"
            elif len(set(used)) == 1:
                result = used[0]
            else:
                result = "unverified"
        out[kind] = {"expected": [lo, hi], "passes": vals, "sides": sides, "result": result}
    return out


# --------------------------------------------------------------------------
# One image
# --------------------------------------------------------------------------

def combine_check(spec: "C.CallSpec", recs: dict, keys: list, cfg: dict, index_map=None,
                  detector: Optional[list] = None) -> dict:
    """The check-manifest entry of one image kind from the pass records ``{key: rec | None}`` (§5.4);
    ``detector``: the image's added-object candidates (M7 §8.1, see ``combine_extras``)."""
    single = len(keys) == 1
    datas = {k: _pass_data(recs.get(k)) for k in keys}
    not_computed = [k for k in keys if datas[k] is None]
    by_label = {it["label"]: it for it in spec.items}

    # Decoy: a pass that sees it is unreliable for this image.
    decoy_item = next((it for it in spec.items if it["decoy"]), None)
    unreliable: list[str] = []
    decoy_entry = None
    if decoy_item is not None:
        statuses = {}
        for k in keys:
            ans = None if datas[k] is None else datas[k]["elements"].get(decoy_item["label"])
            statuses[k] = None if ans is None else ans.get("status")
            if statuses[k] == "present":
                unreliable.append(k)
        decoy_entry = {"label": decoy_item["label"], "type": decoy_item["type"], "box_1000": decoy_item["box_1000"],
                       "passes": statuses, "accepted_by": list(unreliable)}
    reliable = [k for k in keys if datas[k] is not None and k not in unreliable]

    elements: dict[str, dict] = {}
    for label, it in by_label.items():
        if it["decoy"]:
            continue
        passes, statuses, notes = {}, [], []
        for k in keys:
            ans = None if datas[k] is None else datas[k]["elements"].get(label)
            if ans is None:
                passes[k] = None
                statuses.append(None)
                continue
            norm, changed = S.normalise_answer(ans, it["category"], it["type_unverified"])
            status = norm["status"]
            if it["type_unverified"] and status == "different":
                status = "present"
                if UNVERIFIED_TYPE_NOTE not in notes:
                    notes.append(UNVERIFIED_TYPE_NOTE)
            passes[k] = {"status": status, "seen_as": norm.get("seen_as"), "confidence": norm.get("confidence"),
                         "normalised": changed, "unreliable": k in unreliable}
            statuses.append("unsure" if k in unreliable else status)
        result, single_status = element_result(statuses, single)
        entry = {"label": label, "role": it["role"], "kind": it["kind"], "type": it["type"],
                 "type_unverified": it["type_unverified"], "source": it["source"], "box_1000": it["box_1000"],
                 "passes": passes, "result": result, "single": single_status}
        if it.get("swapped_from"):
            entry["swapped_from"] = it["swapped_from"]
        if it["source"] == "added_by_ai" and result in MISMATCH_RESULTS:
            notes.append(ADDED_BY_AI_NOTE)
        if notes:
            entry["notes"] = notes
        elements[it["wenart_id"]] = entry

    size = spec.size
    per_pass, dropped = {}, {}
    for k in keys:
        if datas[k] is not None:
            per_pass[k], dropped[k] = parse_extras(datas[k], size, index_map, cfg)
    extras = combine_extras(per_pass, keys, reliable, single, cfg, detector)
    counts = combine_counts({k: datas[k] for k in keys}, keys, reliable, single, spec.expected or {})

    mismatch = (any(e["role"] == "required" and e["result"] in MISMATCH_RESULTS for e in elements.values())
                or any(x["confirmed"] and x["class"] in S.NON_DECOR_CLASSES for x in extras)
                or any(c["result"] in ("fewer", "more") for c in counts.values()))
    info = (bool(unreliable)
            or any(e["result"] in ("disputed", "unverified") or e["result"] in MISMATCH_RESULTS
                   for e in elements.values())
            or bool(extras) or any(c["result"] == "unverified" for c in counts.values()))
    if not_computed:
        verdict = "not_computed"
    elif single:
        verdict = "info"
    elif mismatch:
        verdict = "mismatch"
    elif info:
        verdict = "info"
    else:
        verdict = "ok"
    entry = {"verdict": verdict, "prompt_kind": spec.prompt_kind, "elements": elements, "extras": extras,
             "extras_dropped": dropped, "counts": counts, "unreliable": unreliable,
             "not_computed": not_computed, "decoy": decoy_entry,
             "images": [os.path.basename(str(p)) for p in spec.images]}
    base_kind = spec.image_kind[len("plan_ab:"):] if spec.image_kind.startswith("plan_ab:") else spec.image_kind
    if spec.target and base_kind.startswith(("removal:", "swap:")):
        entry["control"] = _gone_control(spec, elements, keys)
    elif spec.target and base_kind.startswith("insertion:"):
        entry["control"] = _insertion_control(spec, per_pass, extras, keys)
    return entry


def _gone_control(spec, elements: dict, keys: list) -> dict:
    """Removal / type swap: the target must come back absent or different."""
    e = elements.get(spec.target)
    if e is None:
        return {"target": spec.target, "testable": False}
    statuses = [None if e["passes"].get(k) is None else e["passes"][k]["status"] for k in keys]
    gone = [s in ("absent", "different") for s in statuses if s is not None]
    return {"target": spec.target, "testable": True, "label": e["label"], "statuses": dict(zip(keys, statuses)),
            "computed": all(s is not None for s in statuses),
            "flagged": any(gone), "confirmed": len(gone) == len(keys) and all(gone) and len(keys) > 1,
            "result": e["result"]}


def _insertion_control(spec, per_pass: dict, extras: list, keys: list) -> dict:
    """Insertion: an extra must cover >= 50 % of the element's box in the normal render."""
    box = spec.target_box_px
    if box is None:
        return {"target": spec.target, "testable": False}
    need = 0.5
    flagged = any(box_cover(x["box_px"], box) >= need for k in keys for x in per_pass.get(k) or [])
    confirmed = any(x["confirmed"] and box_cover(x["box_px"], box) >= need for x in extras)
    return {"target": spec.target, "testable": True, "box_px": box,
            "computed": all(k in per_pass for k in keys), "flagged": flagged, "confirmed": confirmed}


# --------------------------------------------------------------------------
# Polish decision
# --------------------------------------------------------------------------

def polish_decision(cycles: Optional[dict], polished: Optional[dict], single_pass: bool) -> dict:
    """``{"polished_rejected", "polished_reason", "polished_reasons"}`` (§5.5, differential)."""
    out = {"polished_rejected": False, "polished_reason": None, "polished_reasons": []}
    if polished is None:
        return out
    incomplete = []
    for name, entry in (("polished", polished), ("cycles", cycles)):
        if entry is None:
            incomplete.append({"reason": "check_incomplete", "image": name, "detail": "not checked"})
            continue
        if entry["not_computed"]:
            incomplete.append({"reason": "check_incomplete", "image": name,
                               "detail": f"not computed: {', '.join(entry['not_computed'])}"})
        if entry["unreliable"]:
            incomplete.append({"reason": "check_incomplete", "image": name,
                               "detail": f"unreliable (decoy seen): {', '.join(entry['unreliable'])}"})
    if incomplete:
        out.update(polished_rejected=True, polished_reason="check_incomplete", polished_reasons=incomplete)
        return out
    reasons = []
    for eid, e in polished["elements"].items():
        before = (cycles["elements"].get(eid) or {}).get("result")
        if e["result"] in CONFIRMED_GONE and before in ("ok", "unverified"):
            reasons.append({"reason": "vision_check", "what": "element", "id": eid, "type": e["type"],
                            "source": e["source"], "cycles": before, "polished": e["result"]})
    cyc_confirmed = [x for x in cycles["extras"] if x["confirmed"]]
    for x in polished["extras"]:
        if not x["confirmed"] or x["class"] not in S.NON_DECOR_CLASSES:
            continue
        matched = any(c["class"] == x["class"] and box_iou(c["box_px"], x["box_px"]) >= 0.3 for c in cyc_confirmed)
        if not matched:
            reasons.append({"reason": "vision_check", "what": "added_by_polish", "class": x["class"],
                            "categories": x["categories"], "box_px": x["box_px"]})
    if reasons and not single_pass:
        out.update(polished_rejected=True, polished_reason="vision_check", polished_reasons=reasons)
    return out


def review_reasons(cycles: Optional[dict], crosscheck: dict) -> list[str]:
    """Why a view needs review: a confirmed mismatch on the Cycles render or a JSON cross-check finding."""
    reasons = []
    if cycles and cycles["verdict"] == "mismatch":
        for eid, e in cycles["elements"].items():
            if e["role"] == "required" and e["result"] in MISMATCH_RESULTS:
                reasons.append(f"{eid} ({e['type']}, {e['source']}): {e['result']}")
        for x in cycles["extras"]:
            if x["confirmed"] and x["class"] in S.NON_DECOR_CLASSES:
                reasons.append(f"confirmed extra {x['class']} at {[round(v) for v in x['box_px']]}")
        for kind, c in cycles["counts"].items():
            if c["result"] in ("fewer", "more"):
                reasons.append(f"{kind} count {c['result']} than expected {c['expected']}: {c['passes']}")
    for key in ("in_json_not_rendered", "misplaced", "rendered_not_in_json"):
        for item in (crosscheck or {}).get(key) or []:
            reasons.append(f"json cross-check {key}: {item.get('id')}")
    return reasons


# --------------------------------------------------------------------------
# Project
# --------------------------------------------------------------------------

def _stores(project: Project, keys: list) -> dict:
    models = project.cfg["models"]
    out = {}
    for k in keys:
        if k not in models:
            raise C.UsageError(f"model key {k!r} not in check.yaml (known: {', '.join(models)})")
        out[k] = C.AnswerStore(C.answers_path(project.check_dir, models[k]["slug"]), k, models[k]["slug"])
    return out


def _answered_kinds(stores: dict) -> set:
    found = set()
    for store in stores.values():
        for rec in store.calls.values():
            found.add((rec.get("prompt_kind"), rec.get("camera"), rec.get("image_kind")))
    return found


def coverage_map(project: Project, spec: "C.CallSpec") -> Optional[np.ndarray]:
    """Index map of the listed elements as the image shown has them (for dropping listed extras).

    Insertion calls show the normal render but list the control render's
    elements: the map is the normal render's index without the target, so
    an extra where the target stands is never "covered" by what the control
    render shows behind it (another piece, a door). Other kinds: the index of
    the render the list came from.
    """
    if spec.base_view is None:
        return None
    kind = spec.image_kind[len("plan_ab:"):] if spec.image_kind.startswith("plan_ab:") else spec.image_kind
    if kind.startswith("insertion:") and spec.camera in project.views():
        index = project.maps(project.views()[spec.camera])[0].copy()
        target = [i for i, e in project.table.items() if e["wenart_id"] == spec.target]
        index[np.isin(index, target)] = 0
        return index
    return project.maps(spec.base_view)[0]


# --------------------------------------------------------------------------
# Added-object detector (M7 §8.1)
# --------------------------------------------------------------------------

DETECTOR_ADVISORY = "no detector: block in check.yaml (thresholds not calibrated): advisory, never rejects"


class DetectorViews:
    """The detection files of one project as the decision reads them (stale files are not used)."""

    def __init__(self, project: Project, det_cfg: Optional[dict]) -> None:
        self.project = project
        self.cfg = det_cfg
        self.dir = project.out / D.DETECT_DIR
        self.ran = self.dir.is_dir()
        self.warnings: list[str] = []
        self._docs: dict = {}

    def doc(self, camera: str) -> Optional[dict]:
        if camera not in self._docs:
            self._docs[camera] = D.load_view(self.dir, camera) if self.ran else None
        return self._docs[camera]

    def boxes(self, camera: str, name: str, png) -> Optional[list]:
        """Boxes of image ``name`` of ``camera`` when its recorded sha256 is that of ``png``, else None."""
        doc = self.doc(camera)
        if doc is None or png is None:
            return None
        found = D.image_boxes(doc, name)
        if found is None:
            return None
        current = D.image_boxes(doc, name, self.project.file_sha(png))
        if current is None:
            msg = f"{camera}: detect/{camera}.json {name} was made from another image (sha256); not used"
            if msg not in self.warnings:
                self.warnings.append(msg)
        return current

    def candidates(self, camera: str, threshold: float, polished_png) -> Optional[list]:
        """Added-object candidates of a polished view at ``threshold`` (None without a current detection)."""
        view = self.project.views().get(camera)
        if view is None:
            return None
        cyc = self.boxes(camera, "cycles", view.png)
        pol = self.boxes(camera, "polished", polished_png)
        if cyc is None or pol is None:
            return None
        c = self.cfg or {}
        return D.added_candidates(pol, cyc, threshold, self.project.maps(view)[0], self.project.table,
                                  match_iou=c.get("match_iou", D.MATCH_IOU),
                                  cover_frac=c.get("cover_frac", D.COVER_FRAC))


def detector_view(dv: DetectorViews, camera: str, polished: Optional[dict]) -> Optional[dict]:
    """The ``detector`` record of one polished camera: candidates confirmed (calibrated) or listed (advisory);
    None for a camera without a polished check, and in advisory mode when the detector never ran."""
    pol = dv.project.polished().get(camera)
    if polished is None or pol is None or (dv.cfg is None and not dv.ran):
        return None
    file = f"../{D.DETECT_DIR}/{camera}.json"
    if dv.cfg is None:
        listed = dv.candidates(camera, 0.0, pol["png"])
        if listed is None:
            return {"status": "advisory", "reason": DETECTOR_ADVISORY, "computed": False, "file": None}
        return {"status": "advisory", "reason": DETECTOR_ADVISORY, "computed": True, "file": file,
                "unmatched": listed[:D.ADVISORY_LIST]}
    cands = dv.candidates(camera, dv.cfg["t_det"], pol["png"])
    if cands is None:
        return {"status": "calibrated", "computed": False, "file": None, "thresholds": _thresholds(dv.cfg)}
    confirmed = D.confirm(cands, dv.cfg["t_strong"], polished.get("extras") or [], dv.cfg.get("confirm_iou",
                                                                                            D.CONFIRM_IOU))
    return {"status": "calibrated", "computed": True, "file": file, "thresholds": _thresholds(dv.cfg),
            "candidates": confirmed,
            "added": [c for c in confirmed if c["confirmed"] and D.non_decor(c.get("class"))]}


def _thresholds(det_cfg: dict) -> dict:
    return {k: det_cfg[k] for k in ("t_det", "t_strong", "match_iou", "cover_frac", "confirm_iou") if k in det_cfg}


def detector_reasons(det: Optional[dict], vlm_reasons: list) -> list[dict]:
    """Rejection reasons of the confirmed added non-decor objects; an object a VLM ``added_by_polish`` reason
    already names (IoU >= 0.3) only gets the detector box added to that reason."""
    out = []
    for c in (det or {}).get("added") or []:
        same = next((r for r in vlm_reasons if r.get("what") == "added_by_polish"
                     and box_iou(r["box_px"], c["box_px"]) >= 0.3), None)
        box = {"group": c["group"], "score": c["score"], "box_px": c["box_px"], "confirmed_by": c["confirmed_by"]}
        if same is not None:
            same.setdefault("detector", []).append(box)
            continue
        out.append({"reason": "vision_check", "what": "added_by_polish", "source": "detector", "class": c["class"],
                    "categories": {"detector": c["group"]}, "box_px": c["box_px"], "score": c["score"],
                    "confirmed_by": c["confirmed_by"]})
    return out


def detector_control(dv: DetectorViews, spec: "C.CallSpec", entry: dict) -> Optional[dict]:
    """Insertion control seen by the detector: the normal render as "polished", the hidden render as "Cycles"."""
    if not dv.ran or not spec.target or spec.target_box_px is None:
        return None
    view = dv.project.views().get(spec.camera)
    control = next((c for c in dv.project.controls() if c["id"] == spec.target and c["camera"] == spec.camera), None)
    hidden = dv.project.control_view(control) if control else None
    if view is None or hidden is None:
        return None
    normal = dv.boxes(spec.camera, "cycles", view.png)
    before = dv.boxes(spec.camera, f"control:{spec.target}", hidden.png)
    out = {"target": spec.target, "advisory": dv.cfg is None, "computed": normal is not None and before is not None}
    if not out["computed"]:
        return out
    index = dv.project.maps(view)[0].copy()
    target = [i for i, e in dv.project.table.items() if e["wenart_id"] == spec.target]
    index[np.isin(index, target)] = 0
    cands = D.added_candidates(normal, before, 0.0, index, dv.project.table)
    hit = D.target_hit(cands, spec.target_box_px)
    out.update(hit_score=None if hit is None else hit["score"], hit_group=None if hit is None else hit["group"])
    if dv.cfg is not None:
        flagged = hit is not None and float(hit["score"]) >= dv.cfg["t_det"]
        confirmed = flagged and bool(D.confirm([hit], dv.cfg["t_strong"], entry.get("extras") or [])[0]["confirmed"])
        out.update(flagged=flagged, confirmed=confirmed)
    return out


def combine_project(project: Project, keys: list) -> dict:
    """The ``check_manifest.json`` content of a project from every answers file (§5.7)."""
    cfg = project.cfg
    single = len(keys) == 1
    stores = _stores(project, keys)
    answered = _answered_kinds(stores)
    warnings: list[str] = []
    det_cfg = D.detector_cfg(cfg)
    dv = DetectorViews(project, det_cfg)

    wanted = C.check_kinds(project, ["cycles", "polished"])
    for cam, kind in C.check_kinds(project, ["controls", "plan_ab"], warn=False):
        pk = "plan_ab" if kind.startswith("plan_ab:") else "check"
        if (pk, cam, kind) in answered:
            wanted.append((cam, kind))
    prefs = [(cam, kind, order) for cam, kind, order in C.preference_kinds(project, ["polished", "sweep"])
             if ("preference", cam, kind) in answered]

    views_out: dict[str, dict] = {cam: {} for cam in project.views()}
    for cam, kind in wanted:
        recs, spec = {}, None
        for k in keys:
            spec_k = C.check_spec(project, cam, kind, stores[k].data.get("model") or "")
            if spec_k is None:
                break
            spec = spec_k
            rec = stores[k].valid(spec_k)
            if rec is None and stores[k].get(spec_k.key) is not None:
                stale = stores[k].get(spec_k.key)
                if stale.get("input_sha256") != spec_k.input_sha256:
                    warnings.append(f"{k}: stale answer for {spec_k.key} (inputs changed); not used")
            recs[k] = rec
        if spec is None:
            continue
        cands = None
        if kind == "polished" and det_cfg is not None and cam in project.polished():
            cands = dv.candidates(cam, det_cfg["t_det"], project.polished()[cam]["png"])
        views_out[cam][kind] = combine_check(spec, recs, keys, cfg, coverage_map(project, spec), detector=cands)
        if kind.startswith("insertion:"):
            dc = detector_control(dv, spec, views_out[cam][kind])
            if dc is not None:
                views_out[cam][kind]["detector_control"] = dc
        views_out[cam][kind]["images"] = [rel(p, project.check_dir) for p in spec.images]
        # The bytes the answers are about (the same hashes their input_sha256 holds): the final report
        # accepts a polished image only when it is these very pixels, never by file name alone.
        views_out[cam][kind]["image_sha256"] = [project.file_sha(p) for p in spec.images]
    pref_groups: dict = {}
    for cam, kind, order in prefs:
        for k in keys:
            spec = C.preference_spec(project, cam, kind, order, stores[k].data.get("model") or "")
            if spec is None:
                continue
            rec = stores[k].valid(spec)
            pref_groups.setdefault((cam, kind), {}).setdefault(order, {})[k] = None if rec is None else rec["data"]
    min_votes = int((cfg.get("preference") or {}).get("min_votes", 3))
    for (cam, kind), by_order in pref_groups.items():
        entry = views_out[cam].setdefault(kind, {"verdict": "info", "preference_only": True, "elements": {},
                                                 "extras": [], "counts": {}, "unreliable": [], "not_computed": []})
        entry["preference"] = R.votes(by_order, keys, min_votes)

    cameras: dict[str, dict] = {}
    for cam, kinds in views_out.items():
        exp = project.expected(cam)
        crosscheck = exp.get("json_crosscheck") or {}
        decision = polish_decision(kinds.get("cycles"), kinds.get("polished"), single)
        det = detector_view(dv, cam, kinds.get("polished"))
        if det is not None and det_cfg is not None:
            if not det["computed"]:
                decision["polished_reasons"].append({"reason": "check_incomplete", "image": "polished",
                                                     "detail": "detector: no current detection of this image"})
                decision["polished_rejected"] = True
                decision["polished_reason"] = decision["polished_reason"] or "check_incomplete"
            extra = detector_reasons(det, decision["polished_reasons"])
            if extra:
                decision["polished_reasons"] += extra
                decision["polished_rejected"] = True
                decision["polished_reason"] = decision["polished_reason"] or "vision_check"
        reasons = review_reasons(kinds.get("cycles"), crosscheck)
        cameras[cam] = dict(kinds)
        added = decision["polished_rejected"] and any(r.get("what") == "added_by_polish"
                                                      for r in decision["polished_reasons"])
        cameras[cam].update({"room_id": exp.get("room_id"), "json_crosscheck": crosscheck, **decision,
                             "added_by_polish": added, "needs_review": bool(reasons),
                             "needs_review_reasons": reasons})
        if det is not None:
            cameras[cam]["detector"] = det
    models = {k: {"id": cfg["models"][k]["id"], "slug": cfg["models"][k]["slug"],
                  "revision": cfg["models"][k].get("revision"), "licence": cfg["models"][k].get("licence"),
                  "served": stores[k].data.get("model") or None, "incomplete": bool(stores[k].data.get("incomplete"))}
              for k in keys}
    advisory_reason = "single pass" if single else "calibrate has not run on this manifest"
    det_manifest = D.read_json(dv.dir / D.DETECT_MANIFEST) if dv.ran else None
    detector = {"status": "not_run" if not dv.ran else "advisory" if det_cfg is None else "calibrated",
                "advisory": det_cfg is None, "reason": DETECTOR_ADVISORY if det_cfg is None else None,
                "thresholds": None if det_cfg is None else _thresholds(det_cfg),
                "calibration": None if det_cfg is None else det_cfg.get("calibration"),
                "model": (det_manifest or {}).get("model"),
                "views": sorted(cam for cam, v in cameras.items() if (v.get("detector") or {}).get("computed")),
                "not_computed": sorted(cam for cam, v in cameras.items()
                                       if v.get("detector") is not None and not v["detector"]["computed"])}
    return {"schema_version": "0.1", "project": project.project, "advisory": True,
            "advisory_reason": advisory_reason, "single_pass": single, "model_keys": list(keys), "models": models,
            "detector": detector, "views": cameras, "warnings": list(project.warnings) + warnings + dv.warnings}
