"""Calibration of the vision check: false alarms, decoys, controls, plan A/B (docs/milestone5.md §5.5).

From ``check_manifest.json`` (written by ``combine``):

- baseline on every Cycles view: combined ``fa_missing`` (required elements
  confirmed missing/changed on a render that shows them), ``fa_extra`` (views
  with a confirmed non-decor extra), ``count_error`` (views with a confirmed
  door/window count mismatch); per model the single-pass false "missing"
  rate and the decoy acceptance;
- controls: ``removal_flagged`` (a pass says absent/different on the
  render without the element), ``removal_confirmed`` (every pass does),
  ``insertion`` (a confirmed extra covers >= 50 % of the element's box),
  ``swap_flagged`` / ``swap_confirmed`` (info);
- ``detector_insertion`` (docs/milestone7.md §8.1, info, never a target):
  the same insertion controls seen by the added-object detector
  (``detector_control`` of combine): the share where a candidate covers the
  element at all (``found``), at ``t_det`` (``flagged``) and confirmed
  (``confirmed``; None while the detector is advisory);
- targets of ``check.yaml``; a missed target (or one without data, or a
  single-pass check) makes the check ``advisory``: an open item that needs
  the user's OK before the milestone is called done. The differential
  decision on polished images stays active either way;
- plan A/B: the same metrics with the source-plan crop as Image 2 on the A/B
  cameras; it favours the crop only when removal detection rises and false
  alarms do not. That is reported as a proposal ("set plan_image: true to
  adopt"); the crop goes into the element checks only with ``check.yaml:
  plan_image: true``, set by hand.
"""
from __future__ import annotations

from typing import Optional

from wenart.vision_check import schemas as S
from wenart.vision_check.combine import MISMATCH_RESULTS

NOT_ADOPTED_TEXT = ("source plan compared through the evidence chain, the projected cross-check and the "
                    "side-by-side crop")
FAVOURS_TEXT = "A/B favours the plan crop: set plan_image: true to adopt"
USED_TEXT = "source-plan crop used as Image 2 of every element check (check.yaml plan_image: true)"

# (target key in check.yaml, metric, op)
TARGETS = (
    ("fa_missing_max", "fa_missing", "<="),
    ("fa_extra_max", "fa_extra", "<="),
    ("removal_flagged_min", "removal_flagged", ">="),
    ("removal_confirmed_min", "removal_confirmed", ">="),
    ("insertion_min", "insertion", ">="),
)


def ratio(num: int, den: int) -> Optional[float]:
    return None if den == 0 else round(num / den, 4)


def _computed(entry: dict) -> bool:
    return entry is not None and entry.get("verdict") != "not_computed" and not entry.get("preference_only")


def _required(entry: dict) -> list[dict]:
    return [e for e in entry["elements"].values() if e["role"] == "required"]


def baseline(entries: list[dict], single_pass: bool) -> dict:
    """Combined false-alarm rates over computed check entries (None in single-pass mode)."""
    done = [e for e in entries if _computed(e)]
    req = [el for e in done for el in _required(e)]
    out = {"views": len(entries), "views_computed": len(done), "required_elements": len(req)}
    if single_pass:
        out.update(fa_missing=None, fa_extra=None, count_error=None)
        return out
    out["fa_missing"] = ratio(sum(el["result"] in MISMATCH_RESULTS for el in req), len(req))
    out["fa_extra"] = ratio(sum(any(x["confirmed"] and x["class"] in S.NON_DECOR_CLASSES for x in e["extras"])
                                for e in done), len(done))
    out["count_error"] = ratio(sum(any(c["result"] in ("fewer", "more") for c in e["counts"].values())
                                   for e in done), len(done))
    out["disputed"] = ratio(sum(el["result"] == "disputed" for el in req), len(req))
    return out


def per_model(entries: list[dict], keys: list) -> dict:
    """Answer rate, decoy acceptance and single-pass false "missing" rate per model on the Cycles views."""
    out = {}
    for k in keys:
        answered = [e for e in entries if e and k not in (e.get("not_computed") or [])]
        with_decoy = [e for e in answered if e.get("decoy") and (e["decoy"]["passes"].get(k) is not None)]
        accepted = sum(1 for e in with_decoy if e["decoy"]["passes"][k] == "present")
        req = [el for e in answered for el in _required(e) if el["passes"].get(k)]
        gone = sum(1 for el in req if el["passes"][k]["status"] in ("absent", "different"))
        out[k] = {"calls": len(entries), "answered": len(answered), "answer_rate": ratio(len(answered), len(entries)),
                  "decoys": len(with_decoy), "decoy_accept": ratio(accepted, len(with_decoy)),
                  "fa_missing_single": ratio(gone, len(req))}
    return out


def control_rates(views_out: dict, prefix: str) -> dict:
    """Flagged/confirmed rates of the control entries whose image kind starts with ``prefix``."""
    rows = []
    for cam, kinds in views_out.items():
        for kind, entry in kinds.items():
            if not isinstance(entry, dict) or not kind.startswith(prefix):
                continue
            c = entry.get("control") or {}
            if c.get("testable") and c.get("computed"):
                rows.append({"camera": cam, "kind": kind, "flagged": bool(c["flagged"]),
                             "confirmed": bool(c["confirmed"])})
    return {"n": len(rows), "flagged": ratio(sum(r["flagged"] for r in rows), len(rows)),
            "confirmed": ratio(sum(r["confirmed"] for r in rows), len(rows)), "rows": rows}


def detector_insertion(views_out: dict) -> dict:
    """The detector's insertion rates over the computed ``detector_control`` records of the insertion controls."""
    rows = []
    advisory = None
    for cam, kinds in views_out.items():
        for kind, entry in kinds.items():
            if not isinstance(entry, dict) or not kind.startswith("insertion:"):
                continue
            dc = entry.get("detector_control") or {}
            if not dc.get("computed"):
                continue
            advisory = bool(dc.get("advisory")) if advisory is None else advisory or bool(dc.get("advisory"))
            rows.append({"camera": cam, "kind": kind, "hit_score": dc.get("hit_score"),
                         "hit_group": dc.get("hit_group"),
                         "flagged": dc.get("flagged"), "confirmed": dc.get("confirmed")})
    n = len(rows)
    calibrated = n > 0 and not advisory
    return {"n": n, "advisory": advisory, "found": ratio(sum(r["hit_score"] is not None for r in rows), n),
            "flagged": ratio(sum(bool(r["flagged"]) for r in rows), n) if calibrated else None,
            "confirmed": ratio(sum(bool(r["confirmed"]) for r in rows), n) if calibrated else None, "rows": rows}


def plan_ab(views_out: dict, single_pass: bool, plan_image: bool = False) -> dict:
    """The plan A/B: false alarms and removal detection without and with the plan crop.

    ``favours_plan``: removal detection rises and false alarms do not. That
    is a proposal: the crop is sent with the element checks only when
    ``check.yaml: plan_image`` is true (``used``; ``adopted`` = ``used``).
    """
    cams = sorted(cam for cam, kinds in views_out.items() if f"plan_ab:{cam}" in kinds)
    pairs = [(kinds.get("cycles"), kinds.get(f"plan_ab:{cam}")) for cam, kinds in views_out.items() if cam in cams]
    pairs = [(a, b) for a, b in pairs if _computed(a) and _computed(b)]
    without = baseline([a for a, _ in pairs], single_pass)
    with_plan = baseline([b for _, b in pairs], single_pass)
    rem_without, rem_with = [], []
    for cam, kinds in views_out.items():
        for kind, entry in kinds.items():
            if not isinstance(entry, dict) or not kind.startswith("plan_ab:removal:"):
                continue
            base = kinds.get(kind[len("plan_ab:"):])
            c_with, c_without = entry.get("control") or {}, (base or {}).get("control") or {}
            if c_with.get("computed") and c_without.get("computed"):
                rem_with.append(bool(c_with["confirmed"]))
                rem_without.append(bool(c_without["confirmed"]))
    out = {"cameras": cams, "pairs": len(pairs), "removal_pairs": len(rem_with),
           "fa_missing_without": without.get("fa_missing"), "fa_missing_with": with_plan.get("fa_missing"),
           "fa_extra_without": without.get("fa_extra"), "fa_extra_with": with_plan.get("fa_extra"),
           "removal_confirmed_without": ratio(sum(rem_without), len(rem_without)),
           "removal_confirmed_with": ratio(sum(rem_with), len(rem_with))}
    vals = [out[k] for k in ("fa_missing_without", "fa_missing_with", "fa_extra_without", "fa_extra_with",
                             "removal_confirmed_without", "removal_confirmed_with")]
    favours = (all(v is not None for v in vals)
               and out["removal_confirmed_with"] > out["removal_confirmed_without"]
               and out["fa_missing_with"] <= out["fa_missing_without"]
               and out["fa_extra_with"] <= out["fa_extra_without"])
    out["favours_plan"] = bool(favours)
    out["used"] = out["adopted"] = bool(plan_image)
    out["text"] = USED_TEXT if plan_image else FAVOURS_TEXT if favours else NOT_ADOPTED_TEXT
    if not all(v is not None for v in vals):
        out["note"] = "not enough plan A/B answers to compare"
    return out


def calibrate(manifest: dict, cfg: dict) -> dict:
    """``check_calibration.json``: ``{metrics, targets, missed, advisory, advisory_reasons, plan_ab}``."""
    keys = list(manifest.get("model_keys") or [])
    single = bool(manifest.get("single_pass"))
    views_out = manifest.get("views") or {}
    cycles = [kinds.get("cycles") for kinds in views_out.values() if kinds.get("cycles")]
    base = baseline(cycles, single)
    models = per_model(cycles, keys)
    removal = control_rates(views_out, "removal:")
    insertion = control_rates(views_out, "insertion:")
    swap = control_rates(views_out, "swap:")
    metrics = {"baseline": base, "models": models,
               "fa_missing": base.get("fa_missing"), "fa_extra": base.get("fa_extra"),
               "count_error": base.get("count_error"),
               "removal_flagged": None if single else removal["flagged"],
               "removal_confirmed": None if single else removal["confirmed"],
               "insertion": None if single else insertion["confirmed"],
               "insertion_flagged": insertion["flagged"],
               "swap_flagged": swap["flagged"], "swap_confirmed": None if single else swap["confirmed"],
               "detector_insertion": detector_insertion(views_out),
               "controls": {"removal": removal, "insertion": insertion, "swap": swap}}
    targets = dict(cfg["targets"])
    missed = []
    for tkey, metric, op in TARGETS:
        value, limit = metrics[metric], float(targets[tkey])
        if value is None:
            missed.append({"target": tkey, "metric": metric, "value": None, "threshold": limit, "op": op,
                           "reason": "single pass" if single else "no data"})
        elif (op == "<=" and value > limit) or (op == ">=" and value < limit):
            missed.append({"target": tkey, "metric": metric, "value": value, "threshold": limit, "op": op})
    limit = float(targets["decoy_accept_max"])
    for k, m in models.items():
        value = m["decoy_accept"]
        if value is None:
            missed.append({"target": "decoy_accept_max", "metric": f"decoy_accept[{k}]", "value": None,
                           "threshold": limit, "op": "<=", "reason": "no data"})
        elif value > limit:
            missed.append({"target": "decoy_accept_max", "metric": f"decoy_accept[{k}]", "value": value,
                           "threshold": limit, "op": "<="})
    reasons = []
    if single:
        reasons.append("single pass: no two-model agreement")
    for m in missed:
        why = f" ({m['reason']})" if m.get("reason") else ""
        reasons.append(f"{m['metric']} {m['value']} misses {m['op']} {m['threshold']}{why}")
    return {"schema_version": "0.1", "project": manifest.get("project"), "model_keys": keys, "single_pass": single,
            "metrics": metrics, "targets": targets, "missed": missed, "advisory": bool(missed) or single,
            "advisory_reasons": reasons, "plan_ab": plan_ab(views_out, single, bool(cfg.get("plan_image")))}
