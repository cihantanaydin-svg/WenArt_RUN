"""Gate calibration with benign and negative controls (docs/milestone5.md §4.3).

What: for the calibration views of a project (``sweep_views(n=8)``: the 4
sweep views + 4 more, at most one per room) the gate compares the Cycles
render with

- benign edits (must be accepted): ``controls.benign_controls``;
- CPU negatives (must be rejected) on ``largest_required`` and one more
  required object of the view (shift, scale, rotation, erase), a window/door
  crop of another view pasted on a wall, and three colour edits;
- GPU negatives from the ``--hide`` control renders listed in
  ``check/controls.json`` (``controls/hide_<id>/render_manifest.json``):
  removal (reference = normal render, test = hidden render) and insertion
  (reference = hidden render with its own passes, test = normal render);
- presumed-bad polish attempts (reported only): ``role: presumed_bad`` in
  ``polish/sweep/polish_manifest.json``.

Then, per check and limit: the worst benign value, the best (closest to
passing) small and overall negative among the controls the check is meant
to catch (``TARGETS``), whether one threshold separates them, and the
proposal = worst benign value + 25 % of the gap to the best small negative
(never midway to the gross ones; when the check has no small negative the
gross ones are the basis and the entry says so). Proposals are applied to
``thresholds.yaml`` by hand after review; a proposal looser than the current
value is flagged (it needs the user's OK).

One control that no single limit can see (a 2 degree rotation inside the
3 px radius) would hide everything else a limit separates, so each entry
also lists the value closest to passing per control (``per_control``), the
controls the limit alone separates (``caught``) and the rest (``missed``);
``proposed_partial`` applies the 25 % rule to the caught small negatives
only. It is review material, never a proposal.

Milestone 10 (docs/milestone10.md §3.3 item 5): the calibration views also hold up to
``EXTERIOR_CALIBRATION_VIEWS`` exterior views (``expected.sweep_exterior_views``: one of each view kind first). They
get the same controls (benign edits; shift, scale, rotation and erase of their largest windows or doors; a window
crop pasted on a wall, preferably a donor of another exterior view; three colour edits), and every record carries
its ``view_kind``. The top-level ``rates`` and ``per_metric`` count the interior comparisons only (an exterior
failure must not switch the polish of the rooms off); ``exterior`` holds the exterior rates, and
``exterior_validation`` / ``exterior_polish`` turn them into the decision for the exterior views with the same limits
as the project (``validation.yaml``): a failed or missing exterior validation keeps the exterior views Cycles
only.

Files: ``<out>/gate_calibration.json`` (rewritten after every view, so a
stopped run keeps its numbers) and ``gate_calibration.md``.

CLI: ``python -m wenart.gate calibrate --project-out outputs/<p> [--out DIR]
[--views N|cam,...] [--deadline S] [--device cuda]``; after the deadline
(default env ``WENART_DEADLINE``, epoch seconds) no new comparison starts,
the JSON says ``"incomplete": true`` and the exit code is 0.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np

from wenart.gate import controls as K
from wenart.gate.api import GATE_CODE_VERSION, NOT_THRESHOLDS, limits_of

CALIBRATION_VIEWS = 8
EXTERIOR_CALIBRATION_VIEWS = 3
EXTERIOR = "exterior"
INTERIOR = "interior"
PROPOSAL_GAP_SHARE = 0.25
OBJECT_CONTROLS = {"shift", "scale", "rotate", "erase", "removal", "insertion"}
COLOUR_CONTROLS = {"white_balance_strong", "wall_b", "floor_L"}
# Which negatives each check is meant to catch (the basis of its proposal).
TARGETS = {
    "edges": OBJECT_CONTROLS,
    "added_lines": {"paste", "insertion"},
    "depth": OBJECT_CONTROLS | {"paste"},
    "masks": OBJECT_CONTROLS,
    "colour": COLOUR_CONTROLS,
    "neutral": {"white_balance_strong", "wall_b"},
    "features": OBJECT_CONTROLS | {"paste"},
}
FAMILY = {**{c: "object" for c in ("shift", "scale", "rotate", "erase")}, "paste": "paste",
          "removal": "hide", "insertion": "hide", **{c: "colour" for c in COLOUR_CONTROLS}}
REQUIRED_KINDS = ("door", "window", "furniture")
FALLBACK_REQUIRED_FRAC = 0.03


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def _dump(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False, default=_json_default), encoding="utf-8")
    tmp.replace(path)


def _json_default(value):
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return value.as_posix()
    raise TypeError(f"not JSON serialisable: {type(value).__name__}")


def _magnitude_key(control: str, magnitude) -> str:
    return control if magnitude is None else f"{control}:{magnitude}"


def proposal(worst_benign: float, best_negative: float, share: float = PROPOSAL_GAP_SHARE) -> float:
    """Worst benign value moved ``share`` (25 %) of the gap towards the best negative (§4.3).

    The same formula serves ``*_min`` limits (the negative lies below) and
    ``*_max`` limits (the negative lies above).
    """
    gap = float(best_negative) - float(worst_benign)
    return round(float(worst_benign) + share * gap, 4)


def worst_value(record: dict, check: str, scope: str, op: str) -> Optional[float]:
    """The value of one comparison closest to failing: the global value, or the worst region value."""
    m = (record.get("metrics") or {}).get(check)
    if not isinstance(m, dict) or m.get("error"):
        return None
    if scope == "global":
        v = m.get("global")
        return None if v is None else float(v)
    values = [float(v) for v in (m.get("regions") or {}).values() if v is not None]
    if not values:
        return None
    return min(values) if op == ">=" else max(values)


def _passes(value: float, limit: float, op: str) -> bool:
    return value >= limit if op == ">=" else value <= limit


# --------------------------------------------------------------------------
# Expected elements (area D) with a clearly labelled fallback
# --------------------------------------------------------------------------

def index_elements(view, table: dict) -> list[dict]:
    """Fallback element list from the index pass: required = door/window/furniture with area >= 3 %.

    Used only when ``wenart.vision_check.expected`` is not available; the
    own-room and visibility rules of §5.1 are not applied (the calibration
    warns about it).
    """
    total = float(view.width * view.height)
    out = []
    for idx, st in sorted(view.index_stats.items(), key=lambda kv: (-kv[1]["pixels"], kv[0])):
        entry = table.get(int(idx)) or {}
        kind = entry.get("kind", "unknown")
        frac = st["pixels"] / total
        role = "required" if kind in REQUIRED_KINDS and frac >= FALLBACK_REQUIRED_FRAC else "optional"
        out.append({"index": int(idx), "wenart_id": entry.get("wenart_id") or f"index:{idx}", "kind": kind,
                    "type": entry.get("type"), "room_id": entry.get("room_id"), "pixels": st["pixels"],
                    "area_frac": round(frac, 5), "box_px": st["box"], "role": role})
    return out


def fallback_sweep(expected: dict, n: int) -> list[str]:
    """Up to ``n`` cameras with the most required elements, one per room, ties by camera name."""
    order = sorted(expected, key=lambda cam: (-sum(e["role"] == "required" for e in expected[cam]["elements"]), cam))
    rooms, out = set(), []
    for cam in order:
        room = expected[cam].get("room_id")
        if room in rooms:
            continue
        rooms.add(room)
        out.append(cam)
        if len(out) >= n:
            break
    return out


def calibration_targets(project_out: Path, views: dict, scene: dict, n: int, expected_api=None,
                        warnings: Optional[list] = None,
                        cameras: Optional[list[str]] = None,
                        n_exterior: int = 0) -> tuple[list[str], dict]:
    """``(cameras, {camera: [object elements]})``: the calibration views and the objects of their negatives.

    Cameras = ``sweep_views(expected_views, n)`` (or the ``cameras`` asked) and, with ``n_exterior`` and no
    ``cameras`` asked, up to ``n_exterior`` exterior views (``sweep_exterior_views``; none when the expected API
    has no such function); objects = ``largest_required`` + the next required element by pixels.
    """
    from wenart import views as V
    warnings = warnings if warnings is not None else []
    api = expected_api
    if api is None:
        from wenart.vision_check import expected as api
    try:
        ev = api.expected_views(project_out)
        ev = {cam: e for cam, e in ev.items() if cam in views}
        cams = list(cameras) if cameras else [c for c in api.sweep_views(ev, n) if c in views]
        pick_exterior = getattr(api, "sweep_exterior_views", None)
        if n_exterior and not cameras and callable(pick_exterior):
            cams += [c for c in pick_exterior(ev, n_exterior) if c in views and c not in cams]
        largest = {cam: api.largest_required(ev[cam]) if cam in ev else None for cam in cams}
    except NotImplementedError:
        warnings.append("wenart.vision_check.expected is not implemented: calibration views and objects from "
                        "the index pass (required = door/window/furniture >= 3 % of the frame; own-room and "
                        "visibility rules not applied)")
        table = V.index_table(scene or {})
        ev = {cam: {"camera": cam, "room_id": v.room_id, "elements": index_elements(v, table)}
              for cam, v in views.items()}
        cams = list(cameras) if cameras else fallback_sweep(ev, n)
        largest = {cam: next((e for e in ev[cam]["elements"] if e["role"] == "required"), None) for cam in cams}
    objects: dict[str, list] = {}
    for cam in cams:
        first = largest.get(cam)
        if first is None:
            objects[cam] = []
            warnings.append(f"{cam}: no required element; no object negatives")
            continue
        rest = sorted((e for e in ev[cam]["elements"] if e.get("role") == "required" and e["index"] != first["index"]),
                      key=lambda e: (-e["pixels"], e["index"]))
        objects[cam] = [first] + rest[:1]
    return cams, objects


# --------------------------------------------------------------------------
# Donor crops for the paste negative
# --------------------------------------------------------------------------

def _touches_border(box, width: int, height: int) -> bool:
    x0, y0, x1, y1 = box
    return x0 <= 0 or y0 <= 0 or x1 >= width or y1 >= height


def donor_crops(views: dict, cams: list[str], table: dict) -> list[dict]:
    """The largest window/door crop of each calibration view (preferring ones that do not touch the border)."""
    donors = []
    for cam in cams:
        view = views[cam]
        cands = []
        for idx, st in view.index_stats.items():
            kind = (table.get(int(idx)) or {}).get("kind")
            if kind in ("window", "door"):
                cands.append((_touches_border(st["box"], view.width, view.height), -st["pixels"], int(idx), kind))
        if not cands:
            continue
        cands.sort()
        _border, _neg, idx, kind = cands[0]
        crop_rgb, crop_mask = K.crop_of(view.read_rgb(), view.read_index(), idx)
        donors.append({"camera": cam, "index": idx, "kind": kind,
                       "object": (table.get(idx) or {}).get("wenart_id") or f"index:{idx}",
                       "rgb": crop_rgb, "mask": crop_mask})
    return donors


def donor_for(donors: list[dict], camera: str, kinds: Optional[dict] = None) -> Optional[dict]:
    """The first donor of another view (the views' order is fixed, so the choice is deterministic); with ``kinds``
    (``{camera: interior | exterior}``) a donor of another view of the same kind first (a facade window pasted on
    a facade wall), else any other view's."""
    others = [d for d in donors if d["camera"] != camera]
    if kinds:
        same = [d for d in others if kinds.get(d["camera"]) == kinds.get(camera)]
        if same:
            return same[0]
    return others[0] if others else None


# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------

def _record(camera: str, control: str, magnitude, obj, result: dict, **extra) -> dict:
    family = "polish" if control == "presumed_bad" else FAMILY.get(control, "benign")
    rec = {"camera": camera, "view_kind": INTERIOR, "control": control, "magnitude": magnitude, "object": obj,
           "family": family,
           "small": K.is_small(control, magnitude), "decision": result["decision"],
           "reasons": result["reasons"], "notes": result["notes"], "metrics": result["metrics"],
           "gate_key": result.get("gate_key")}
    rec.update(extra)
    return rec


def _resolve_dir(value: str, base: Path) -> Path:
    """A folder named in an M5 JSON, relative to ``base`` (absolute paths are kept)."""
    p = Path(value)
    return p if p.is_absolute() else base / p


def controls_base(data: dict, json_dir: Path, project_out: Path) -> Path:
    """The folder the ``dir`` entries of ``check/controls.json`` are relative to.

    The vision check writes ``dir_relative_to: project_out`` (§5.5 writes
    ``controls/hide_<id>``); without that key the §1.1 rule holds (the JSON's
    own folder).
    """
    return project_out if data.get("dir_relative_to") == "project_out" else json_dir


def run_calibration(project_out, *, gate=None, expected_api=None, out_dir=None, n_views: int = CALIBRATION_VIEWS,
                    cameras: Optional[list[str]] = None, deadline: Optional[float] = None,
                    log: Callable[[str], Any] = print, n_exterior: int = EXTERIOR_CALIBRATION_VIEWS) -> dict:
    """Run every control of §4.3 for one project, write the JSON + markdown, return the calibration dict."""
    from wenart import views as V
    from wenart.gate.api import Gate

    project_out = Path(project_out).resolve()
    out_dir = Path(out_dir) if out_dir else project_out / "gate"
    json_path = out_dir / "gate_calibration.json"
    md_path = out_dir / "gate_calibration.md"
    start = time.time()
    warnings: list[str] = []
    paths = V.project_paths(project_out)
    scene = paths["scene_manifest"]
    project = paths["project"]
    views = V.load_views(paths["render_dir"], skip_stale=True, warnings=warnings)
    gate = gate if gate is not None else Gate()
    if getattr(gate, "scene_manifest", None) is None:
        gate.scene_manifest = scene
    table = V.index_table(scene)

    cal: dict[str, Any] = {
        "schema_version": "0.1", "kind": "gate_calibration", "project": project, "incomplete": False,
        "gate_code": GATE_CODE_VERSION, "models": gate.model_info(), "thresholds": gate.thresholds,
        "views": [], "objects": {}, "benign": [], "negative": [], "presumed_bad": [], "skipped": [],
        "exterior_incomplete": False, "warnings": warnings, "seconds": 0.0,
    }

    def expired(exterior: bool = False) -> bool:
        """The deadline has passed. A cut in the exterior comparisons (the last CPU phase) sets only
        ``exterior_incomplete``: the rooms' controls are complete and their validation stands (Milestone 10)."""
        if deadline is not None and time.time() >= float(deadline):
            if exterior and not cal["incomplete"]:
                if not cal["exterior_incomplete"]:
                    warnings.append("deadline reached: the exterior comparisons were not started")
                cal["exterior_incomplete"] = True
                return True
            if not cal["incomplete"]:
                warnings.append("deadline reached: the remaining comparisons were not started")
            cal["incomplete"] = True
            return True
        return False

    def save() -> None:
        cal["seconds"] = round(time.time() - start, 1)
        cal.update(summarise(cal, gate.thresholds))
        cal["exterior"] = exterior_block(cal, gate.thresholds, [c for c in views if kinds.get(c) == EXTERIOR])
        _dump(json_path, cal)
        md_path.write_text(report_md(cal), encoding="utf-8")

    if cameras:
        unknown = [c for c in cameras if c not in views]
        if unknown:
            raise KeyError(f"cameras not rendered (or stale): {', '.join(unknown)}")
    cams, objects = calibration_targets(project_out, views, scene, n_views, expected_api, warnings, cameras,
                                        n_exterior=n_exterior)
    from wenart.gate import colour as GC
    kinds = {c: (EXTERIOR if GC.is_exterior(scene, c, views[c].room_id) else INTERIOR) for c in views}
    cal["views"] = cams
    cal["objects"] = {c: [{"index": e["index"], "wenart_id": e["wenart_id"], "kind": e.get("kind"),
                           "pixels": e.get("pixels")} for e in objs] for c, objs in objects.items()}
    donors = donor_crops(views, cams, table)
    log(f"{project}: {len(cams)} calibration views, {len(donors)} donor crops")

    # CPU controls per view. The room views come first, the exterior views after the GPU controls of the rooms
    # (below): a deadline that cuts the exterior comparisons must not make the rooms' calibration incomplete.
    def cpu_controls(cam_list: list, exterior: bool = False) -> None:
        for cam in cam_list:
            if expired(exterior):
                break
            view = views[cam]
            rgb = view.read_rgb()
            ref = gate.prepare(view, rgb)
            index = view.read_index()
            depth_mm = view.read_depth_mm()
            for ctl in K.benign_controls(rgb, seed=K.seed_for(project, cam, "noise")):
                if expired(exterior):
                    break
                res = gate.compare(ref, ctl["image"])
                cal["benign"].append(_record(cam, ctl["control"], ctl["magnitude"], None, res, view_kind=kinds[cam]))
            for element in objects.get(cam, []):
                for ctl in K.object_negatives(rgb, index, depth_mm, element["index"], element["wenart_id"]):
                    if expired(exterior):
                        break
                    res = gate.compare(ref, ctl["image"])
                    cal["negative"].append(_record(cam, ctl["control"], ctl["magnitude"], ctl["object"], res,
                                                   view_kind=kinds[cam]))
            for ctl in K.view_negatives(rgb, ref.regions.masks, donor_for(donors, cam, kinds)):
                if expired(exterior):
                    break
                if ctl["image"] is None:
                    cal["skipped"].append({"camera": cam, "control": ctl["control"], "reason": ctl["skipped"]})
                    continue
                res = gate.compare(ref, ctl["image"])
                cal["negative"].append(_record(cam, ctl["control"], ctl["magnitude"], ctl["object"], res,
                                               view_kind=kinds[cam],
                                               **({"info": ctl["info"]} if ctl.get("info") else {})))
            log(f"  {cam}: {sum(r['camera'] == cam for r in cal['benign'])} benign, "
                f"{sum(r['camera'] == cam for r in cal['negative'])} negative comparisons")
            save()

    cpu_controls([c for c in cams if kinds[c] != EXTERIOR])

    # GPU controls: removal and insertion from the --hide renders.
    controls_path = project_out / "check" / "controls.json"
    if controls_path.is_file():
        controls_data = json.loads(controls_path.read_text(encoding="utf-8"))
        controls = controls_data.get("controls") or []
        base = controls_base(controls_data, controls_path.parent, project_out)
        for c in controls:
            if expired():
                break
            cam, cid = c.get("camera"), c.get("id")
            hide_dir = _resolve_dir(c.get("dir") or f"controls/hide_{cid}", base)
            reason = None
            hidden = None
            if cam not in views:
                reason = "normal render missing or stale"
            elif not (hide_dir / "render_manifest.json").is_file():
                reason = f"control render missing ({hide_dir.name})"
            else:
                try:
                    hidden = V.load_views(hide_dir, [cam])[cam]
                except (KeyError, V.StaleRender) as exc:
                    reason = f"control render unusable: {exc}"
            if hidden is not None and c.get("index") is not None and int(c["index"]) in hidden.index_stats:
                reason = "control render still contains the index"
            if reason:
                cal["skipped"].append({"camera": cam, "control": f"hide:{cid}", "reason": reason})
                continue
            normal_rgb = views[cam].read_rgb()
            hidden_rgb = hidden.read_rgb()
            try:
                res = gate.compare(gate.prepare(views[cam], normal_rgb), hidden_rgb)
            except ValueError as exc:            # e.g. the control was rendered at another size
                cal["skipped"].append({"camera": cam, "control": f"hide:{cid}", "reason": str(exc)})
                continue
            cal["negative"].append(_record(cam, "removal", None, cid, res, kind=c.get("kind"),
                                           view_kind=kinds.get(cam, INTERIOR)))
            if expired():
                break
            res = gate.compare(gate.prepare(hidden, hidden_rgb), normal_rgb)
            cal["negative"].append(_record(cam, "insertion", None, cid, res, kind=c.get("kind"),
                                           view_kind=kinds.get(cam, INTERIOR)))
        save()
    else:
        warnings.append("check/controls.json not found: no removal/insertion controls")

    cpu_controls([c for c in cams if kinds[c] == EXTERIOR], exterior=True)
    save()

    # Presumed-bad polish attempts (reported only).
    sweep_path = project_out / "polish" / "sweep" / "polish_manifest.json"
    if sweep_path.is_file():
        sweep = json.loads(sweep_path.read_text(encoding="utf-8"))
        for entry in sweep.get("views") or []:
            cam = entry.get("camera")
            for att in entry.get("attempts") or []:
                if att.get("role") != "presumed_bad":
                    continue
                if expired():
                    break
                png = sweep_path.parent / (att.get("png") or "")
                if cam not in views or not att.get("png") or not png.is_file():
                    cal["skipped"].append({"camera": cam, "control": "presumed_bad",
                                           "reason": "attempt PNG or view missing"})
                    continue
                rgb = views[cam].read_rgb()
                try:
                    res = gate.compare(gate.prepare(views[cam], rgb), V.read_rgb(png))
                except ValueError as exc:
                    cal["skipped"].append({"camera": cam, "control": "presumed_bad", "reason": str(exc)})
                    continue
                rel = Path(os.path.relpath(png.resolve(), out_dir.resolve())).as_posix()
                cal["presumed_bad"].append(_record(cam, "presumed_bad", att.get("strength"), None, res,
                                                   attempt=att.get("k"), png=rel, view_kind=kinds.get(cam, INTERIOR)))
        save()
    else:
        warnings.append("polish/sweep/polish_manifest.json not found: no presumed-bad attempts")
    save()
    return cal


# --------------------------------------------------------------------------
# Summary
# --------------------------------------------------------------------------

def _rate(n: int, k: int) -> Optional[float]:
    return None if n == 0 else round(k / n, 4)


def of_kind(records, kind: str = INTERIOR) -> list[dict]:
    """The comparisons of one view kind (a record without ``view_kind`` is an interior one: calibrations before
    Milestone 10)."""
    return [r for r in records or [] if (r.get("view_kind") or INTERIOR) == kind]


def summarise(cal: dict, thresholds: dict, kind: str = INTERIOR) -> dict:
    """``{"rates", "per_metric", "smallest_detected", "explanations"}`` from the recorded comparisons of one
    view kind (the interior ones by default: an exterior failure must not decide the rooms' polish)."""
    benign, negative = of_kind(cal.get("benign"), kind), of_kind(cal.get("negative"), kind)
    small = [r for r in negative if r.get("small")]
    by_control: dict[str, dict] = {}
    for kind_, records in (("benign", benign), ("negative", negative),
                           ("presumed_bad", of_kind(cal.get("presumed_bad"), kind))):
        for r in records:
            key = f"{kind_}:{_magnitude_key(r['control'], r['magnitude'])}"
            e = by_control.setdefault(key, {"kind": kind_, "control": r["control"], "magnitude": r["magnitude"],
                                            "n": 0, "accepted": 0, "rejected": 0})
            e["n"] += 1
            e["accepted" if r["decision"] == "accept" else "rejected"] += 1
    for e in by_control.values():
        e["rate"] = _rate(e["n"], e["accepted"] if e["kind"] == "benign" else e["rejected"])
    rates = {"benign_accept": _rate(len(benign), sum(r["decision"] == "accept" for r in benign)),
             "negative_reject": _rate(len(negative), sum(r["decision"] == "reject" for r in negative)),
             "small_negative_reject": _rate(len(small), sum(r["decision"] == "reject" for r in small)),
             "by_control": dict(sorted(by_control.items()))}

    per_metric: dict[str, dict] = {}
    explanations: list[str] = []
    for check, th in thresholds.items():
        if check in NOT_THRESHOLDS or not isinstance(th, dict):
            continue
        targets = TARGETS.get(check)
        for scope, key, op in limits_of(check, th):
            limit = float(th[key])
            bvals = [v for v in (worst_value(r, check, scope, op) for r in benign) if v is not None]
            negs = [r for r in negative if targets is None or r["control"] in targets]
            nvals = [(v, bool(r.get("small")), _magnitude_key(r["control"], r["magnitude"]))
                     for v, r in ((worst_value(r, check, scope, op), r) for r in negs) if v is not None]
            pick_worst = min if op == ">=" else max       # the benign value closest to failing
            pick_best = max if op == ">=" else min        # the negative value closest to passing

            def beyond(value, ref, op=op):                # strictly on the failing side of ref
                return value < ref if op == ">=" else value > ref

            worst_benign = pick_worst(bvals) if bvals else None
            best_negative = pick_best(v for v, _s, _k in nvals) if nvals else None
            small_vals = [v for v, s, _k in nvals if s]
            best_small = pick_best(small_vals) if small_vals else None
            basis_val, basis = (best_small, "small") if small_vals else (best_negative, "gross" if nvals else None)
            separates = worst_benign is not None and basis_val is not None and beyond(basis_val, worst_benign)
            proposed = proposal(worst_benign, basis_val) if separates else None
            looser = None if proposed is None else (proposed < limit if op == ">=" else proposed > limit)
            # Per control: the value closest to passing; which controls this limit alone separates.
            per_control: dict[str, float] = {}
            small_keys = set()
            for v, s, k in nvals:
                per_control[k] = v if k not in per_control else pick_best(per_control[k], v)
                if s:
                    small_keys.add(k)
            caught = sorted(k for k, v in per_control.items() if worst_benign is not None and beyond(v, worst_benign))
            missed = sorted(set(per_control) - set(caught))
            caught_small = [per_control[k] for k in caught if k in small_keys]
            partial = None
            if not separates and caught_small and worst_benign is not None:
                partial = proposal(worst_benign, pick_best(caught_small))
            entry = {"op": op, "scope": scope, "current": th[key], "hard": bool(th.get("hard", True)),
                     "worst_benign": worst_benign, "best_small_negative": best_small, "best_negative": best_negative,
                     "basis": basis, "separates": bool(separates), "proposed": proposed,
                     "looser_than_current": looser, "n_benign": len(bvals), "n_negative": len(nvals),
                     "benign_pass_current": _rate(len(bvals), sum(_passes(v, limit, op) for v in bvals)),
                     "negative_fail_current": _rate(len(nvals), sum(not _passes(v, limit, op) for v, _s, _k in nvals)),
                     "targets": sorted(targets) if targets else None,
                     "per_control": dict(sorted(per_control.items())), "caught": caught, "missed": missed,
                     "proposed_partial": partial}
            per_metric.setdefault(check, {})[key] = entry
            name = f"{check}.{key}"
            if worst_benign is None or basis_val is None:
                explanations.append(f"{name}: not enough values (benign {len(bvals)}, negative {len(nvals)})")
            elif separates:
                explanations.append(
                    f"{name} separates: worst benign {worst_benign:.4g} vs best {basis} negative {basis_val:.4g}; "
                    f"proposed {proposed:.4g} (current {limit:.4g}{', LOOSER: needs the user OK' if looser else ''})")
            else:
                text = (f"{name} does not separate every {basis} negative: worst benign {worst_benign:.4g} vs best "
                        f"{basis} negative {basis_val:.4g}; no proposal; misses {', '.join(missed) or '-'}")
                if partial is not None:
                    text += (f"; on the small negatives it catches ({', '.join(k for k in caught if k in small_keys)})"
                             f" a threshold of {partial:.4g} would sit 25 % into the gap (proposed_partial)")
                explanations.append(text)

    smallest: dict[str, Any] = {"shift_px": None, "scale": None, "by_magnitude": {}}
    for control, key in (("shift", "shift_px"), ("scale", "scale")):
        mags: dict = {}
        for r in negative:
            if r["control"] == control:
                n, k = mags.get(r["magnitude"], (0, 0))
                mags[r["magnitude"]] = (n + 1, k + (r["decision"] == "reject"))
        ordered = sorted(mags)
        smallest["by_magnitude"][control] = {str(m): _rate(*mags[m]) for m in ordered}
        for i, m in enumerate(ordered):
            if all(mags[x][0] == mags[x][1] for x in ordered[i:]):
                smallest[key] = m
                break

    for r in benign:
        if r["decision"] != "accept":
            why = "; ".join(f"{x['check']} {x['region']} {x['value']} (limit {x['op']} {x['threshold']})"
                            for x in r["reasons"][:3])
            explanations.append(f"benign {_magnitude_key(r['control'], r['magnitude'])} on {r['camera']} "
                                f"rejected: {why}")
    for r in negative:
        if r["decision"] == "accept":
            explanations.append(f"negative {_magnitude_key(r['control'], r['magnitude'])} on "
                                f"{r.get('object') or 'view'} ({r['camera']}) accepted")
    return {"rates": rates, "per_metric": per_metric, "smallest_detected": smallest, "explanations": explanations}


# --------------------------------------------------------------------------
# Exterior views (Milestone 10)
# --------------------------------------------------------------------------

def exterior_block(cal: dict, thresholds: dict, rendered: list[str]) -> dict:
    """The ``exterior`` record of a calibration: the exterior views rendered and used, the exterior comparisons'
    rates and what separates them (``summarise`` over the exterior records), the numbers of comparisons."""
    used = sorted({r["camera"] for key in ("benign", "negative") for r in of_kind(cal.get(key), EXTERIOR)})
    summary = summarise(cal, thresholds, kind=EXTERIOR)
    return {"cameras_rendered": len(rendered), "cameras": list(rendered), "views": used,
            "n_benign": len(of_kind(cal.get("benign"), EXTERIOR)),
            "n_negative": len(of_kind(cal.get("negative"), EXTERIOR)), **summary}


def exterior_validation(cal: Optional[dict], limits: dict, thresholds: Optional[dict] = None) -> dict:
    """The validation of the exterior views of one calibration (pure): ``wenart.gate.validate.decide_validation`` on
    the exterior comparisons with the project's limits, plus ``polish_allowed``.

    ``decision``: ``ok`` / ``flagged`` allow the exterior polish; ``polish_disabled`` (too many exterior geometry
    changes get through) and ``not_validated`` (no calibration, or no exterior benign or negative comparison, or cut
    by the deadline, or other thresholds) keep the exterior views Cycles only; ``not_applicable`` when the project
    rendered no exterior view (nothing to polish or validate)."""
    from wenart.gate import validate as VAL

    if not isinstance(cal, dict):
        out = VAL.decide_validation(None, limits, thresholds)
        return dict(out, polish_allowed=False, exterior_cameras=None)
    ext = cal.get("exterior") if isinstance(cal.get("exterior"), dict) else {}
    rendered = int(ext.get("cameras_rendered") or 0)
    if not rendered and cal.get("exterior") is not None:
        return {"decision": "not_applicable", "polish_allowed": False, "benign_accept": None, "negative_reject": None,
                "n_benign": 0, "n_negative": 0, "pass_benign": False, "pass_negative": False,
                "reasons": ["the project rendered no exterior view"], "thresholds_match": None,
                "exterior_cameras": 0}
    sub = {"benign": of_kind(cal.get("benign"), EXTERIOR), "negative": of_kind(cal.get("negative"), EXTERIOR),
           "rates": ext.get("rates") or {}, "thresholds": cal.get("thresholds"),
           "incomplete": bool(cal.get("incomplete") or cal.get("exterior_incomplete"))}
    out = VAL.decide_validation(sub, limits, thresholds, kind=EXTERIOR)
    if cal.get("exterior") is None:
        out["reasons"].insert(0, "the calibration has no exterior block (made before Milestone 10, or the exterior "
                                 "views were not calibrated)")
        out["decision"] = "not_validated"
    out["polish_allowed"] = out["decision"] in VAL.POLISH_DECISIONS
    out["exterior_cameras"] = rendered
    return out


def exterior_polish(project_out, gate_dir=None, thresholds=None) -> dict:
    """The exterior polish decision of a project output from ``gate/gate_calibration.json`` (``exterior_validation``
    with the limits of ``validation.yaml`` and the current thresholds). The polish and the final report ask this
    for every exterior view, next to the project's own ``gate_validation.json`` (both must allow)."""
    from wenart.gate import validate as VAL
    from wenart.gate.api import load_thresholds

    folder = Path(gate_dir) if gate_dir else Path(project_out) / "gate"
    path = folder / VAL.CALIBRATION_NAME
    if not path.is_file() and not gate_dir and Path(project_out).resolve().parent.name == "variants":
        # An alternative's sub-output (outputs/<p>/variants/<id>) reuses the base project's calibration
        # (docs/milestone10.md §1.6b row 9).
        base = Path(project_out).resolve().parent.parent / "gate" / VAL.CALIBRATION_NAME
        if base.is_file():
            path = base
    cal = None
    if path.is_file():
        try:
            cal = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            cal = None
    current = thresholds if isinstance(thresholds, dict) else load_thresholds(thresholds)
    out = exterior_validation(cal, VAL.load_validation_config(), current)
    out["limits"] = VAL.load_validation_config()
    out["source"] = VAL.CALIBRATION_NAME if path.is_file() else None
    out["from_base_project"] = bool(path.is_file() and path.parent != folder)
    return out


# --------------------------------------------------------------------------
# Markdown report
# --------------------------------------------------------------------------

def _fmt(v) -> str:
    if v is None:
        return "-"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def exterior_md(cal: dict, ext: dict) -> list[str]:
    """The "Exterior views" section of the report: the exterior comparisons apart from the rooms' (Milestone 10)."""
    if not ext.get("cameras_rendered"):
        return ["", "## Exterior views", "", "The project rendered no exterior view."]
    er = ext.get("rates") or {}
    benign, negative = of_kind(cal.get("benign"), EXTERIOR), of_kind(cal.get("negative"), EXTERIOR)
    lines = ["", "## Exterior views", "",
             f"{ext['cameras_rendered']} exterior view(s) rendered, {len(ext.get('views') or [])} calibrated "
             f"({', '.join(ext.get('views') or []) or '-'}): benign {sum(r['decision'] == 'accept' for r in benign)}"
             f"/{len(benign)} accepted (rate {_fmt(er.get('benign_accept'))}); negatives "
             f"{sum(r['decision'] == 'reject' for r in negative)}/{len(negative)} rejected (rate "
             f"{_fmt(er.get('negative_reject'))}, small negatives {_fmt(er.get('small_negative_reject'))}). They "
             "do not count in the rates above: the exterior views are validated apart, with the same limits "
             "(`validation.yaml`), and a failed exterior validation keeps them Cycles only."]
    if cal.get("exterior_incomplete"):
        lines += ["", "**Incomplete**: the deadline cut the exterior comparisons. The rooms' calibration is complete; "
                      "the exterior views are not validated and stay the Cycles render."]
    lines += [f"- accepted negative: {r['camera']} {_magnitude_key(r['control'], r['magnitude'])} on "
              f"{r.get('object') or 'view'}" for r in negative if r["decision"] == "accept"]
    lines += [f"- rejected benign: {r['camera']} {_magnitude_key(r['control'], r['magnitude'])}: "
              + "; ".join(f"{x['check']} {x['region']} {_fmt(x['value'])} {x['op']} {_fmt(x['threshold'])}"
                          for x in r["reasons"][:4]) for r in benign if r["decision"] != "accept"]
    return lines


def report_md(cal: dict) -> str:
    """Markdown report of a calibration (summary, rates, per-metric proposals, failures, skips)."""
    rates = cal.get("rates") or {}
    benign, negative = of_kind(cal.get("benign")), of_kind(cal.get("negative"))       # the rooms (interior views)
    ext = cal.get("exterior") if isinstance(cal.get("exterior"), dict) else {}
    lines = [f"# Change-gate calibration: {cal.get('project', '?')}", ""]
    lines.append(
        f"{len(cal.get('views') or []) - len(ext.get('views') or [])} calibration views (rooms); benign {sum(r['decision'] == 'accept' for r in benign)}"
        f"/{len(benign)} accepted (rate {_fmt(rates.get('benign_accept'))}); negatives "
        f"{sum(r['decision'] == 'reject' for r in negative)}/{len(negative)} rejected (rate "
        f"{_fmt(rates.get('negative_reject'))}, small negatives {_fmt(rates.get('small_negative_reject'))}); "
        f"{len(cal.get('presumed_bad') or [])} presumed-bad polish attempts (reported only). Gate code "
        f"{cal.get('gate_code')}; {'INCOMPLETE (deadline)' if cal.get('incomplete') else 'complete'}; "
        f"{cal.get('seconds', 0)} s. Proposals = worst benign value + 25 % of the gap to the best small "
        f"negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the "
        f"user's OK.")
    lines += exterior_md(cal, ext)
    lines += ["", "## Rates by control", "", "| set | control | magnitude | n | accepted | rejected | rate |",
              "|---|---|---|---|---|---|---|"]
    for e in (rates.get("by_control") or {}).values():
        lines.append(f"| {e['kind']} | {e['control']} | {_fmt(e['magnitude'])} | {e['n']} | {e['accepted']} | "
                     f"{e['rejected']} | {_fmt(e['rate'])} |")
    lines += ["", "## Per metric", "",
              "| check | limit | op | hard | current | worst benign | best small negative | best negative | "
              "separates | proposed | looser | benign pass now | negatives fail now |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for check, entries in (cal.get("per_metric") or {}).items():
        for key, e in entries.items():
            lines.append(f"| {check} | {key} | {e['op']} | {_fmt(e['hard'])} | {_fmt(e['current'])} | "
                         f"{_fmt(e['worst_benign'])} | {_fmt(e['best_small_negative'])} | "
                         f"{_fmt(e['best_negative'])} | {_fmt(e['separates'])} | {_fmt(e['proposed'])} | "
                         f"{_fmt(e['looser_than_current'])} | {_fmt(e['benign_pass_current'])} | "
                         f"{_fmt(e['negative_fail_current'])} |")
    lines += ["", "## What each limit separates on its own", "",
              "A control is caught when its value closest to passing is beyond the worst benign value. "
              "proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).",
              ""]
    for check, entries in (cal.get("per_metric") or {}).items():
        for key, e in entries.items():
            lines.append(f"- {check}.{key}: caught {', '.join(e.get('caught') or []) or '-'}; missed "
                         f"{', '.join(e.get('missed') or []) or '-'}"
                         + (f"; proposed_partial {_fmt(e['proposed_partial'])}"
                            if e.get("proposed_partial") is not None else ""))
    sd = cal.get("smallest_detected") or {}
    lines += ["", "## Smallest detected change", "",
              f"- shift: {_fmt(sd.get('shift_px'))} px (rejection rate by px: "
              f"{json.dumps((sd.get('by_magnitude') or {}).get('shift', {}))})",
              f"- scale: x{_fmt(sd.get('scale'))} (rejection rate by factor: "
              f"{json.dumps((sd.get('by_magnitude') or {}).get('scale', {}))})"]
    lines += ["", "## Benign controls rejected", ""]
    bad = [r for r in benign if r["decision"] != "accept"]
    lines += [f"- {r['camera']} {_magnitude_key(r['control'], r['magnitude'])}: "
              + "; ".join(f"{x['check']} {x['region']} {_fmt(x['value'])} {x['op']} {_fmt(x['threshold'])}"
                          for x in r["reasons"][:4]) for r in bad] or ["- none"]
    lines += ["", "## Negative controls accepted", ""]
    missed = [r for r in negative if r["decision"] == "accept"]
    lines += [f"- {r['camera']} {_magnitude_key(r['control'], r['magnitude'])} on {r.get('object') or 'view'}"
              for r in missed] or ["- none"]
    lines += ["", "## Presumed-bad polish attempts (reported only)", ""]
    pb = cal.get("presumed_bad") or []
    if pb:
        lines += ["| camera | attempt | strength | decision | failed checks |", "|---|---|---|---|---|"]
        for r in pb:
            checks = ", ".join(sorted({x["check"] for x in r["reasons"]})) or "-"
            lines.append(f"| {r['camera']} | {_fmt(r.get('attempt'))} | {_fmt(r['magnitude'])} | {r['decision']} | "
                         f"{checks} |")
    else:
        lines.append("None.")
    lines += ["", "## Skipped controls", ""]
    lines += [f"- {s.get('camera')} {s['control']}: {s['reason']}" for s in cal.get("skipped") or []] or ["- none"]
    lines += ["", "## Explanations", ""]
    lines += [f"- {e}" for e in cal.get("explanations") or []] or ["- none"]
    lines += ["", "## Warnings", ""]
    lines += [f"- {w}" for w in cal.get("warnings") or []] or ["- none"]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _deadline(value: Optional[str]) -> Optional[float]:
    raw = value if value not in (None, "") else os.environ.get("WENART_DEADLINE")
    if raw in (None, ""):
        return None
    return float(raw)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--project-out", required=True, help="outputs/<p> (renders/, scene/, check/, polish/)")
    parser.add_argument("--out", default=None, help="output folder (default <project-out>/gate)")
    parser.add_argument("--views", default=None,
                        help=f"number of calibration views (default {CALIBRATION_VIEWS}) or a comma list of cameras")
    parser.add_argument("--exterior-views", type=int, default=EXTERIOR_CALIBRATION_VIEWS,
                        help=f"exterior views to calibrate as well (default {EXTERIOR_CALIBRATION_VIEWS}; 0 = none)")
    parser.add_argument("--deadline", default=None, help="epoch seconds; default env WENART_DEADLINE")
    parser.add_argument("--device", default="cuda", help="torch device of the gate models (default cuda)")
    parser.add_argument("--thresholds", default=None, help="thresholds.yaml (default: the package one)")


def run_from_args(args, gate=None, expected_api=None) -> int:
    """Run ``calibrate`` from parsed arguments (``gate``/``expected_api`` are fakes in tests)."""
    from wenart.gate.api import Gate
    if gate is None:
        gate = Gate(thresholds=args.thresholds, device=args.device)
    n_views, cameras = CALIBRATION_VIEWS, None
    if args.views:
        if args.views.strip().isdigit():
            n_views = int(args.views)
        else:
            cameras = [c.strip() for c in args.views.split(",") if c.strip()]
    cal = run_calibration(args.project_out, gate=gate, expected_api=expected_api, out_dir=args.out,
                          n_views=n_views, cameras=cameras, deadline=_deadline(args.deadline),
                          n_exterior=getattr(args, "exterior_views", EXTERIOR_CALIBRATION_VIEWS))
    rates = cal["rates"]
    print(f"CALIBRATION {cal['project']}: benign accept {_fmt(rates['benign_accept'])}, negative reject "
          f"{_fmt(rates['negative_reject'])}{' (incomplete)' if cal['incomplete'] else ''}")
    return 0


def main(argv=None, gate=None, expected_api=None) -> int:
    parser = argparse.ArgumentParser(description="calibrate the change gate with benign and negative controls")
    add_arguments(parser)
    return run_from_args(parser.parse_args(argv), gate=gate, expected_api=expected_api)


if __name__ == "__main__":
    raise SystemExit(main())
