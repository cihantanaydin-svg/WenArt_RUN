"""Fit a catalogue asset (or the parametric fallback) to every furniture piece.

Rule (docs/milestone4.md, conventions, plan section 4.8): among the catalogue
entries of the piece's type, try the candidates in order of aspect
closeness (``|ln(asset width/depth / footprint width/depth)|``); scale X and
Y to the footprint, Z by the mean of the two; a non-uniform scale
(``max(sx, sy, sz) / min(sx, sy, sz)``) above 15 % rejects the candidate;
no candidate within the cap, or no entry for the type, means the parametric
fallback (exact footprint, type height). Every decision is written into the
piece's ``asset`` dict so ``fit_report`` can list it; nothing else of the
piece changes (``footprint``, ``front_deg``, ``room_id``, ``type``,
``status``, ``evidence`` are untouched, checked by ``fit_building``).

``asset`` dict::

    {"library": "polyhaven" | "parametric", "asset_id": "sofa_02" | "parametric:sofa",
     "licence": "CC0" | "n/a", "license": <same>, "method": "library" | "parametric",
     "fit_scale": [sx, sy, sz], "bbox_m": [w, d, h] of the fitted piece, "aspect_error": float | null,
     "gltf": "models/<id>/<id>_1k.gltf" (library only), "front_axis", "up_axis", "origin_offset",
     "rotation_fix_deg" (library only), "candidates": [{"id", "aspect_error", "scale", "non_uniform", "accepted"}],
     "fallback_reason": str (parametric only), "cap": 1.15}

``license`` duplicates ``licence`` because the building schema names the
field ``license`` and the milestone text ``licence``.

CLI: ``python -m wenart.furniture.fit outputs/<p>/building.json --catalog wenart/furniture/catalog.json
--out outputs/<p>/building_fitted.json --assets assets`` downloads the fitted
models into ``assets/models`` (a failed download turns that fit into the
parametric fallback and the report says so).
"""
from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter
from pathlib import Path
from typing import Optional

from wenart.furniture import catalog as C

NON_UNIFORM_CAP = 1.15
PARAMETRIC_LIBRARY = "parametric"
PARAMETRIC_LICENCE = "n/a"
FROZEN_KEYS = ("id", "level_id", "room_id", "type", "type_raw", "source", "footprint", "front_deg", "height",
               "status", "evidence")


# --------------------------------------------------------------------------
# Pure fitting
# --------------------------------------------------------------------------

def scale_for(entry: dict, width: float, depth: float) -> tuple[list[float], float]:
    """``([sx, sy, sz], non_uniform)`` for an entry on a ``width x depth`` footprint."""
    sx = width / entry["bbox_m"][0]
    sy = depth / entry["bbox_m"][1]
    sz = (sx + sy) / 2.0
    scales = [sx, sy, sz]
    return [round(s, 4) for s in scales], round(max(scales) / min(scales), 4)


def parametric_fit(piece: dict, reason: str, candidates: Optional[list[dict]] = None) -> dict:
    width, depth = piece["footprint"]["size"]
    ftype = piece["type"]
    return {
        "library": PARAMETRIC_LIBRARY, "asset_id": f"parametric:{ftype}", "licence": PARAMETRIC_LICENCE,
        "license": PARAMETRIC_LICENCE, "method": "parametric", "fit_scale": [1.0, 1.0, 1.0],
        "bbox_m": [round(width, 4), round(depth, 4), C.parametric_height(ftype)], "aspect_error": None,
        "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0],
        "candidates": candidates or [], "fallback_reason": reason, "cap": NON_UNIFORM_CAP,
    }


UNIFORM_RANGE = (0.75, 1.30)   # a model stretched more than this looks wrong (a 1.1 m tall sofa)


def fit_piece(piece: dict, catalog: C.Catalog, cap: float = NON_UNIFORM_CAP,
              uniform_range: tuple[float, float] = UNIFORM_RANGE) -> dict:
    """The ``asset`` dict for one piece (pure: the piece is not modified).

    A candidate is accepted when its non-uniform scale (max/min of sx, sy, sz) is
    within ``cap`` and its mean scale within ``uniform_range``; otherwise the next
    candidate by aspect error is tried, then the parametric fallback."""
    ftype = piece["type"]
    width, depth = piece["footprint"]["size"]
    if not (width > 0 and depth > 0):
        return parametric_fit(piece, f"footprint size {piece['footprint']['size']} is not positive")
    candidates = catalog.candidates(ftype)
    if not candidates:
        if ftype in catalog.parametric_types:
            reason = f"type {ftype} is parametric in the catalogue"
        else:
            reason = f"no catalogue entry for type {ftype}"
        return parametric_fit(piece, reason)
    ordered = sorted(candidates, key=lambda e: (C.aspect_error(e, width, depth), e["id"]))
    tried = []
    for entry in ordered:
        scales, non_uniform = scale_for(entry, width, depth)
        err = round(C.aspect_error(entry, width, depth), 4)
        mean_scale = round(sum(scales) / 3.0, 4)
        accepted = non_uniform <= cap + 1e-9 and uniform_range[0] <= mean_scale <= uniform_range[1]
        tried.append({"id": entry["id"], "aspect_error": err, "scale": scales, "non_uniform": non_uniform,
                      "mean_scale": mean_scale, "accepted": accepted})
        if accepted:
            return {
                "library": entry["source"], "asset_id": entry["id"], "licence": entry["licence"],
                "license": entry["licence"], "method": "library", "fit_scale": scales,
                "bbox_m": [round(width, 4), round(depth, 4), round(entry["bbox_m"][2] * scales[2], 4)],
                "aspect_error": err, "gltf": entry["gltf"], "front_axis": entry["front_axis"],
                "up_axis": entry["up_axis"], "origin_offset": list(entry["origin_offset"]),
                "rotation_fix_deg": C.reorient_rotation_deg(entry),
                "front_axis_confidence": entry["front_axis_confidence"], "candidates": tried, "cap": cap, "uniform_range": list(uniform_range),
            }
    best = min(tried, key=lambda t: t["non_uniform"])
    reason = (f"no {ftype} candidate within {round((cap - 1) * 100)} % non-uniform scale and "
              f"{uniform_range[0]}..{uniform_range[1]} mean scale (closest: {best['id']} at "
              f"{round((best['non_uniform'] - 1) * 100, 1)} % non-uniform, mean scale {best['mean_scale']})")
    return parametric_fit(piece, reason, tried)


def fit_building(building: dict, catalog: C.Catalog, cap: float = NON_UNIFORM_CAP) -> dict:
    """A deep copy of ``building`` with ``asset`` set on every furniture piece, nothing else changed."""
    fitted = copy.deepcopy(building)
    for original, piece in zip(building.get("furniture", []), fitted.get("furniture", [])):
        piece["asset"] = fit_piece(piece, catalog, cap=cap)
        for key in FROZEN_KEYS:
            if original.get(key) != piece.get(key):  # cannot happen; guards future edits
                raise RuntimeError(f"fit changed {key} of {piece['id']}")
    return fitted


def assert_only_assets_changed(before: dict, after: dict) -> None:
    """Raise AssertionError unless ``after`` equals ``before`` except for ``furniture[].asset``."""
    a, b = copy.deepcopy(before), copy.deepcopy(after)
    for piece in a.get("furniture", []):
        piece.pop("asset", None)
    for piece in b.get("furniture", []):
        piece.pop("asset", None)
    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
        raise AssertionError("fit changed something other than furniture[].asset")


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def _fmt_scale(scales) -> str:
    return " / ".join(f"{s:.3f}" for s in scales)


def fit_report(building: dict, title: Optional[str] = None) -> str:
    """Markdown: one row per piece (asset, licence, scale, aspect error, method), fallbacks, licences."""
    pieces = building.get("furniture", [])
    rows = []
    fallbacks, licences, missing = [], Counter(), []
    for piece in pieces:
        asset = piece.get("asset")
        if not asset:
            missing.append(piece["id"])
            continue
        fp = piece["footprint"]
        err = "-" if asset.get("aspect_error") is None else f"{asset['aspect_error']:.3f}"
        rows.append(f"| {piece['id']} | {piece.get('room_id') or '-'} | {piece['type']} | {piece['source']} | "
                    f"{piece['status']} | {fp['size'][0]:.2f} x {fp['size'][1]:.2f} | {asset['method']} | "
                    f"{asset['asset_id']} | {asset['licence']} | {_fmt_scale(asset['fit_scale'])} | {err} | "
                    f"{asset['bbox_m'][2]:.2f} |")
        if asset["method"] == "parametric":
            fallbacks.append((piece["id"], piece["type"], asset.get("fallback_reason", "")))
        else:
            licences[(asset["library"], asset["asset_id"], asset["licence"])] += 1
    lines = [f"# Furniture fit report{': ' + title if title else ''}", ""]
    project = building.get("project")
    project_id = project.get("id", "?") if isinstance(project, dict) else str(project or "?")
    lines.append(f"Project: {project_id}; {len(pieces)} pieces, "
                 f"{len(pieces) - len(fallbacks) - len(missing)} library fits, {len(fallbacks)} parametric fallbacks"
                 f"{', ' + str(len(missing)) + ' without fit' if missing else ''}. "
                 f"Non-uniform scale cap {round((NON_UNIFORM_CAP - 1) * 100)} %. Footprints, types, rotations, rooms "
                 f"and statuses are as in the building JSON (fitting never changes them).")
    lines += ["", "| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | "
              "scale x / y / z | aspect err | height (m) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"] + rows
    lines += ["", "## Parametric fallbacks", ""]
    if fallbacks:
        lines += [f"- {pid} ({ftype}): {reason}" for pid, ftype, reason in fallbacks]
    else:
        lines.append("- none")
    lines += ["", "## Library assets and licences", ""]
    if licences:
        lines += [f"- {aid} ({lib}, {lic}) x {n}" for (lib, aid, lic), n in sorted(licences.items())]
    else:
        lines.append("- none")
    if missing:
        lines += ["", "## Pieces without a fit", ""] + [f"- {pid}" for pid in missing]
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def download_fitted(building: dict, assets_dir: Path, log=print) -> dict:
    """Fetch every library asset used in ``building`` into ``assets_dir``.

    A piece whose model cannot be downloaded (offline, blocked host, unknown
    id) is re-fitted as parametric with the error in ``fallback_reason``.
    Returns ``{"fetched": [ids], "failed": {id: reason}}``.
    """
    from wenart.assets import models as M
    from wenart.assets import fetch, web

    result = {"fetched": [], "failed": {}}
    cache: dict[str, Optional[str]] = {}
    for piece in building.get("furniture", []):
        asset = piece.get("asset") or {}
        if asset.get("method") != "library":
            continue
        asset_id = asset["asset_id"]
        if asset_id not in cache:
            try:
                M.fetch_model(asset_id, assets_dir, size="1k", source=asset["library"], licence=asset["licence"])
                cache[asset_id] = None
                result["fetched"].append(asset_id)
                log(f"model {asset_id:<28} ok")
            except (web.NetworkError, web.HTTPStatusError, fetch.AssetNotFound, fetch.LicenceError, KeyError,
                    RuntimeError) as exc:
                cache[asset_id] = f"{type(exc).__name__}: {exc}"
                result["failed"][asset_id] = cache[asset_id]
                log(f"model {asset_id:<28} FAILED: {exc}")
        if cache[asset_id] is not None:
            piece["asset"] = parametric_fit(
                piece, f"download of {asset_id} failed ({cache[asset_id]}); parametric fallback",
                candidates=asset.get("candidates"))
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="fit catalogue assets to the furniture of a building JSON")
    parser.add_argument("building", help="building.json from the ingest pipeline (or the layout step)")
    parser.add_argument("--catalog", default=str(C.CATALOG_PATH), help="catalog.json (default: the package one)")
    parser.add_argument("--out", required=True, help="where to write the fitted building JSON")
    parser.add_argument("--assets", default=None, help="assets folder; when given, the fitted models are downloaded")
    parser.add_argument("--report", default=None, help="markdown report path (default: <out stem>_report.md)")
    parser.add_argument("--no-download", action="store_true", help="do not download even when --assets is given")
    args = parser.parse_args(argv)

    from wenart import building as B

    building = B.load(args.building)
    catalog = C.load(Path(args.catalog))
    fitted = fit_building(building, catalog)
    if args.assets and not args.no_download:
        result = download_fitted(fitted, Path(args.assets))
        if result["failed"]:
            print(f"{len(result['failed'])} model download(s) failed; those pieces use the parametric fallback")
    assert_only_assets_changed(building, fitted)
    out = Path(args.out)
    B.save(fitted, out)
    report_path = Path(args.report) if args.report else out.with_name(out.stem + "_report.md")
    report_path.write_text(fit_report(fitted, title=out.stem), encoding="utf-8")
    methods = Counter(p["asset"]["method"] for p in fitted.get("furniture", []))
    print(f"{len(fitted.get('furniture', []))} pieces: {methods.get('library', 0)} library, "
          f"{methods.get('parametric', 0)} parametric -> {out} (report {report_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
