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

Milestone 7 (docs/milestone7.md §6.3, user decision 7):

- Beds: a bed model without a mattress (``has_mattress`` not true) is never
  a candidate (reason ``no <type> model with a mattress`` when none is left).
- Style filter: ``fit_piece(..., style_family=F)`` takes only candidates
  whose ``styles`` contain ``F`` or ``neutral`` (every candidate when ``F``
  is None); none left -> parametric with the reason ``no model for style F``.
  Excluded candidates are listed under ``excluded`` with the reason. Only
  ``refit`` gets ``--style <out>/style.json`` (it runs after the final
  style); ``fit`` stays style-free, so its fits are provisional (layout and
  decor only read the footprints).
- Objaverse models (``source: objaverse``, CC0 or CC BY 4.0) are fitted like
  the Poly Haven ones; the asset dict carries ``glb``, ``sha256_glb``,
  ``uid`` and the credit fields (``title``, ``author``, ``source_url``,
  ``licence_url``, ``via``, ``attribution``) and ``unit_scale`` (raw GLB
  units -> metres, 1.0 when the entry has none; the scene builder applies
  it before ``fit_scale``); the report lists every CC BY credit line. Downloading an Objaverse model reads only the prep pod's
  cache (``wenart.assets.models.fetch_model``); a miss is a parametric
  fallback like any failed download.

Milestone 8 (docs/milestone8.md §1, §4): fit v2.

- Sources ``abo``, ``polyhaven``, ``objaverse``, ``generated``. After the
  style filter and the bed rule the candidates are tried in **rank order**
  (``rank_key``), the first one within the caps (non-uniform <= 15 %, mean
  scale in ``UNIFORM_RANGE``) wins:
  0. ``generated`` models last (used only when no other library model passes);
  1. real size: models whose box is in real metres (``units_known``: ABO and
     Poly Haven; Objaverse unless a ``unit_note`` says it was normalised by
     type; generated never) before the normalised ones, and among them the
     smallest mean ``|scale - 1|`` over the three fit scales, in
     ``SIZE_BUCKET`` (5 %) steps so that the judge quality decides between
     models whose real size fits about equally well;
  2. judge ``quality`` (mean photoreal quality 1-5, higher first; missing = 3);
  3. aspect error; 4. source order ``SOURCE_ORDER``; 5. the id.
  Every tried candidate records its rank inputs (``size_error``,
  ``size_bucket``, ``units_known``, ``quality``, ``source``, ``rank``) and
  the asset ``ranking`` says why the chosen model won; the report lists it.
- Beds: a bed model without a mattress is a candidate when it is a bed frame
  (``bed_frame: true`` with a positive ``deck_height_m``, metres in the Z-up
  model frame above the model's lowest point, after its unit scale); the
  asset carries ``bed_frame``, ``deck_height_m`` and ``bedding`` (mattress
  top = ``deck_height_m`` x the z fit scale + 0.20 m, the inner box) and
  ``bbox_m`` covers the bedding the scene builder adds
  (``wenart.blender.parametric.frame_bedding``).
- Library models from a GLB (every source but Poly Haven) carry ``glb``,
  ``sha256_glb``, ``uid``, the credit fields, ``unit_scale`` and the
  catalogue's ``licence_flag`` / ``generated`` record.
- Decor (``fit_decor_item``): cushion, plant, rug and wall art take a library
  decor model of the project's style family or ``neutral`` (a decor model
  without ``styles`` counts as neutral) from ``catalog.decor_candidates(type)``
  when the catalogue has the method (duck typing; else the ``kind: decor``
  entries of ``catalog.decor`` / ``catalog.entries``, plus the Poly Haven
  ``decor_plant`` models for plants), picked deterministically by the host id
  (``pick_index``); rugs are scaled to the rug size and kept flat, wall art
  to its width keeping the model's aspect, cushions and plants to the item
  box (refused above ``DECOR_NON_UNIFORM_CAP``). No model -> parametric
  (cushion, plant, book set, rug) or nothing (wall art).

Milestone 10 (docs/milestone10.md §4.5, §4.6, §1.6b rows 15, 16; track F):

- The piece's look (``furniture.design``, written by the layout stage, else ``style.json`` through
  ``wenart.blender.looks.design_for``; only with ``--style``) decides between the library models after the style
  filter: ``material_tags`` ("glass coffee table") keep only models whose judged ``material_tags`` hold every
  asked tag; an upholstered piece's ``fabric_colour`` (a non-upholstered piece's ``colour``) keeps models that can
  take it: ``recolourable_fabric`` models (their separable fabric slots get the colour: ``asset.recolour``, applied
  by the scene builder) or models whose judged fabric slots are already that colour (``colour_rgb`` within
  ``COLOUR_MATCH_DE`` in CIELAB, ``asset.colour_match``); models without the judged fields are skipped for such a
  brief (§4.5: "the fit picks another"), and with none left the parametric piece takes the look. The furniture
  wood (``design.wood``) is recoloured on ``recolourable_wood`` models and preferred, never a reason to skip one.
  Every skipped model is listed under ``excluded`` with the reason.
- The judged fields (``material_slots``, ``material_tags``, ``recolourable_fabric``, ``recolourable_wood``) and a
  plant's ``species`` and ``pot`` travel with the asset (``GLB_ASSET_FIELDS``).
- Decor: the 12 new types take library models like the Milestone 9 ones (tabletop pieces within their box, a clock
  like wall art, curtains, blinds, throws and large plants scaled to their box); a large plant prefers models of
  its ``species``.
- Refit: ``--source building.json [--completion completion.json]`` runs ``wenart.furniture.locked.check`` (mode
  and kept rooms from ``completion.json``) on the fitted building and exits 1 on a violation (the report lists
  them, the fitted building is not written).
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

from wenart.furniture import catalog as C

NON_UNIFORM_CAP = 1.15
PARAMETRIC_LIBRARY = "parametric"
PARAMETRIC_LICENCE = "n/a"
FROZEN_KEYS = ("id", "level_id", "room_id", "type", "type_raw", "source", "footprint", "front_deg", "height",
               "status", "evidence", "build")
# The fields an Objaverse fit carries over from its catalogue entry (the file and the credit line).
OBJAVERSE_ASSET_FIELDS = ("glb", "sha256_glb", "uid", "title", "author", "source_url", "licence_url", "via",
                          "attribution")
# Milestone 8: what any GLB model (ABO, Objaverse, generated) carries over when its entry has it.
GLB_ASSET_FIELDS = OBJAVERSE_ASSET_FIELDS + ("licence_flag", "generated", "style_hint", "name",
                                             # Milestone 10 (track D's judged fields, docs/milestone10.md §4.5, §4.6)
                                             "material_slots", "material_tags", "recolourable_fabric",
                                             "recolourable_wood", "species", "pot",
                                             # Milestone 10 review (track D): the corner sofa's chaise side as the
                                             # viewer facing the front sees it, and a generated plant's attributes
                                             "chaise_side", "chaise_note", "attributes_status")
# Milestone 10: a judged fabric slot whose colour is within this CIELAB distance (Delta E 1976) of the brief's colour
# counts as that colour (designer value, assumed; about the difference between two named greys).
COLOUR_MATCH_DE = 15.0
RECOLOUR_MIN_SHARE = 0.05        # recolour only separable slots covering at least this share of the model
UPHOLSTERED_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bench", "bed_single",
                                      "bed_double")

# Fit v2 ranking (docs/milestone8.md §1).
SOURCE_ORDER: tuple[str, ...] = ("abo", "polyhaven", "objaverse", "generated")
GENERATED = "generated"
DEFAULT_QUALITY = 3.0
SIZE_BUCKET = 0.05           # real-size error steps: models within the same 5 % step are ranked by quality
RANKING_RULE = ("style -> bed rule -> generated last -> real size (known units first, mean |scale - 1| in "
                f"{round(SIZE_BUCKET * 100)} % steps) -> quality (missing = {DEFAULT_QUALITY:g}) -> aspect error -> "
                f"source ({', '.join(SOURCE_ORDER)})")


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


def parametric_box(piece: dict) -> list[float]:
    """The box Blender's parametric mesh will occupy: the piece's ``height`` when
    the JSON has one, else the proxy table height (the same rule as the scene
    builder), measured on the built parts when the type has a builder."""
    from wenart.blender import parametric as P   # pure Python (no bpy)

    width, depth = (float(v) for v in piece["footprint"]["size"])
    height, _ = P.proxy_height(piece["type"], piece.get("height"))
    if piece["type"] in P._BUILDERS:
        height = P.parametric_bbox(piece["type"], width, depth, height)[2]   # a headboard rises above the type height
    return [round(width, 4), round(depth, 4), round(height, 4)]


def parametric_fit(piece: dict, reason: str, candidates: Optional[list[dict]] = None,
                   excluded: Optional[list[dict]] = None, style_family: Optional[str] = None) -> dict:
    ftype = piece["type"]
    return {
        "library": PARAMETRIC_LIBRARY, "asset_id": f"parametric:{ftype}", "licence": PARAMETRIC_LICENCE,
        "license": PARAMETRIC_LICENCE, "method": "parametric", "fit_scale": [1.0, 1.0, 1.0],
        "bbox_m": parametric_box(piece), "aspect_error": None,
        "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0],
        "candidates": candidates or [], "fallback_reason": reason, "cap": NON_UNIFORM_CAP,
        "style_family": style_family, "excluded": list(excluded or []),
    }


def is_bed_frame(entry: dict) -> bool:
    """A bed model without a mattress that the scene builder can make up (docs/milestone8.md §2, §4):
    ``bed_frame: true`` with a positive, finite ``deck_height_m``."""
    deck = entry.get("deck_height_m")
    return (entry.get("type") in C.BED_TYPES and entry.get("bed_frame") is True
            and isinstance(deck, (int, float)) and not isinstance(deck, bool) and math.isfinite(deck) and deck > 0)


def bed_usable(entry: dict) -> bool:
    """The bed rule of fit v2: a model with a mattress (M7) or a bed frame with a deck (M8); other types always."""
    return C.has_mattress(entry) or is_bed_frame(entry)


def units_known(entry: dict) -> bool:
    """True when the entry's box is in real metres (docs/milestone8.md §2): an explicit ``units_known`` wins;
    generated models never are; a ``unit_note`` (a model normalised by type) means unknown; ABO, Poly Haven
    and the other Objaverse models are real metres."""
    if isinstance(entry.get("units_known"), bool):
        return entry["units_known"]
    if entry.get("source") == GENERATED:
        return False
    return not entry.get("unit_note")


def quality_of(entry: dict) -> float:
    """The judge's mean photoreal quality (1-5); ``DEFAULT_QUALITY`` when missing or not a number."""
    q = entry.get("quality")
    if isinstance(q, bool) or not isinstance(q, (int, float)) or not math.isfinite(q):
        return DEFAULT_QUALITY
    return float(q)


def source_rank(entry: dict) -> int:
    source = entry.get("source")
    return SOURCE_ORDER.index(source) if source in SOURCE_ORDER else len(SOURCE_ORDER)


def size_error(scales) -> float:
    """Mean ``|scale - 1|`` over the fit scales: 0 when the model's real size is the footprint."""
    return sum(abs(float(s) - 1.0) for s in scales) / len(scales)


def rank_key(entry: dict, width: float, depth: float) -> tuple:
    """The fit v2 order of a candidate on a ``width x depth`` footprint (lower first, docs/milestone8.md §1):
    generated last, then known units before normalised ones, the real-size step, quality (higher first),
    aspect error, source order and the id."""
    scales, _ = scale_for(entry, width, depth)
    known = units_known(entry)
    bucket = int(size_error(scales) / SIZE_BUCKET + 1e-9) if known else 0
    return (1 if entry.get("source") == GENERATED else 0, 0 if known else 1, bucket, -quality_of(entry),
            round(C.aspect_error(entry, width, depth), 6), source_rank(entry), entry["id"])


def rank_candidates(candidates: list[dict], width: float, depth: float) -> list[dict]:
    return sorted(candidates, key=lambda e: rank_key(e, width, depth))


def ranking_reasons(tried: list[dict], chosen: dict) -> dict:
    """Why the chosen candidate won (the asset's ``ranking`` record)."""
    i = next(n for n, t in enumerate(tried) if t["id"] == chosen["id"])
    size = (f"real size: mean |scale - 1| {chosen['size_error']:.3f} (step {chosen['size_bucket']})"
            if chosen["units_known"] else "units not known (normalised by type): ranked after the real-size models")
    why = [size, f"quality {chosen['quality']:g}", f"aspect error {chosen['aspect_error']:.3f}",
           f"source {chosen['source']}"]
    if chosen["source"] == GENERATED:
        why.insert(0, "generated: no other library model passed the caps")
    passed_over = [{"id": t["id"], "why": "outside the caps (non-uniform {:.1f} %, mean scale {})".format(
        (t["non_uniform"] - 1) * 100, t["mean_scale"])} for t in tried[:i]]
    return {"rule": RANKING_RULE, "rank": chosen["rank"], "tried": len(tried), "reasons": why,
            "passed_over": passed_over}


def usable_candidates(ftype: str, candidates: list[dict], style_family: Optional[str]) -> tuple[list, list, Optional[str]]:
    """``(usable, excluded, reason)`` of the catalogue candidates of a type (docs/milestone7.md §6.3): beds
    without a mattress are dropped unless they are bed frames with a deck (docs/milestone8.md §4), then models
    whose ``styles`` hold neither ``style_family`` nor ``neutral`` (none when the family is None).
    ``excluded`` rows are ``{"id", "reason"}``; ``reason`` is the parametric fallback reason when nothing is
    usable, else None."""
    excluded = [{"id": e["id"], "reason": "bed model without a mattress"} for e in candidates if not bed_usable(e)]
    with_mattress = [e for e in candidates if bed_usable(e)]
    if not with_mattress:
        return [], excluded, f"no {ftype} model with a mattress"
    usable = []
    for e in with_mattress:
        if C.styles_match(e, style_family):
            usable.append(e)
        else:
            excluded.append({"id": e["id"], "reason": f"styles {e.get('styles') or []} include neither "
                                                      f"{style_family} nor {C.NEUTRAL}"})
    if not usable:
        return [], excluded, f"no model for style {style_family}"
    return usable, excluded, None


UNIFORM_RANGE = (0.75, 1.30)   # a model stretched more than this looks wrong (a 1.1 m tall sofa)


def _srgb_to_lab(rgb) -> tuple[float, float, float]:
    from wenart.style import colours as CL

    return CL.linear_to_lab(tuple(CL.srgb_to_linear(float(c) / 255.0) for c in rgb[:3]))


def colour_distance(srgb_255, colour: str) -> Optional[float]:
    """CIELAB Delta E (1976) between a judged slot colour (``colour_rgb``, sRGB 0-255) and a colour phrase of
    ``wenart/style/colours.py``; None when either is unknown."""
    from wenart.style import colours as CL

    if not srgb_255 or len(srgb_255) < 3:
        return None
    try:
        target = CL.linear_to_lab(CL.linear_rgb(colour))
    except (KeyError, ValueError):
        return None
    lab = _srgb_to_lab(srgb_255)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab, target)))


def _slots(entry: dict, material: str, separable: bool) -> list[dict]:
    return [s for s in entry.get("material_slots") or [] if isinstance(s, dict) and s.get("material") == material
            and (not separable or s.get("separable")) and float(s.get("share") or 0.0) >= RECOLOUR_MIN_SHARE]


def look_of(entry: dict, ftype: str, design: dict) -> tuple[Optional[dict], Optional[str]]:
    """``(look, why not)`` of one library model for a piece's design (pure, Milestone 10): ``look`` holds what the
    asset gets (``recolour`` of its fabric / wood slots, ``colour_match``, ``tags``), or None and the reason the
    model cannot show the design (asked material tags missing; the fabric colour neither recolourable nor
    matching; a model nobody judged)."""
    look: dict = {}
    tags = [t for t in design.get("material_tags") or [] if isinstance(t, str)]
    if tags:
        have = entry.get("material_tags")
        if have is None:
            return None, f"no judged material tags (the design asks for {', '.join(tags)})"
        missing = [t for t in tags if t not in have]
        if missing:
            return None, f"material tags {have} lack {', '.join(missing)}"
        look["tags"] = tags
    colour = design.get("fabric_colour") if ftype in UPHOLSTERED_TYPES else design.get("colour")
    if ftype in UPHOLSTERED_TYPES and not colour:
        colour = design.get("colour")
    if colour:
        material = "fabric" if ftype in UPHOLSTERED_TYPES else None
        if material and entry.get("recolourable_fabric") is True and _slots(entry, "fabric", True):
            look["recolour"] = {"fabric": {"colour": colour, "slots": [{"index": s["index"], "name": s.get("name")}
                                                                       for s in _slots(entry, "fabric", True)]}}
        else:
            judged = [s for s in entry.get("material_slots") or [] if isinstance(s, dict)
                      and (material is None or s.get("material") == material) and s.get("colour_rgb")]
            if not judged:
                return None, (f"cannot take the colour {colour}: no recolourable {material or 'judged'} slot and no "
                              "judged slot colour")
            dist = [d for d in (colour_distance(s["colour_rgb"], colour) for s in judged) if d is not None]
            if not dist or min(dist) > COLOUR_MATCH_DE:
                return None, (f"cannot take the colour {colour}: not recolourable and its "
                              f"{material or 'slot'} colour is {min(dist) if dist else float('nan'):.1f} Delta E away "
                              f"(> {COLOUR_MATCH_DE:g})")
            look["colour_match"] = {"colour": colour, "delta_e": round(min(dist), 2)}
    wood = design.get("wood")
    if wood and entry.get("recolourable_wood") is True and _slots(entry, "wood", True):
        from wenart.style import vocabulary as V

        flat = (V.FURNITURE_MATERIALS.get(wood) or {}).get("flat")
        if flat:
            look.setdefault("recolour", {})["wood"] = {
                "colour": wood, "rgb": [float(v) for v in flat],
                "slots": [{"index": s["index"], "name": s.get("name")} for s in _slots(entry, "wood", True)]}
    return look, None


def chaise_side_candidates(candidates: list[dict], side: Optional[str]) -> tuple[list[dict], list[dict], str]:
    """``(kept, excluded, side)`` for an L-shaped piece (``shape: L``; review finding 40): only models whose
    ``chaise_side`` (track D: left / right as a viewer facing the front sees it, measured from the footprint) is the
    piece's ``chaise_side`` (``right`` when the piece has none, as the scene builder assumes); a model without a
    side is excluded as "chaise side unknown", one with the other side too. Library models are never mirrored."""
    want = side if side in C.CHAISE_SIDES else "right"
    kept, excluded = [], []
    for e in candidates:
        has = e.get("chaise_side")
        if has is None:
            excluded.append({"id": e["id"], "reason": "chaise side unknown"})
        elif has != want:
            excluded.append({"id": e["id"], "reason": f"chaise on the {has}, the piece's on the {want} "
                                                      "(no mirroring)"})
        else:
            kept.append(e)
    return kept, excluded, want


class _OneModel:
    """A catalogue view with one library model (the agent's pinned ``asset_pin``, Milestone 11)."""

    def __init__(self, catalog, entry: dict):
        self._catalog = catalog
        self._entry = entry

    def candidates(self, ftype: str) -> list[dict]:
        return [self._entry] if self._entry.get("type") == ftype else []

    @property
    def parametric_types(self) -> list[str]:
        return self._catalog.parametric_types


def fit_piece(piece: dict, catalog: C.Catalog, cap: float = NON_UNIFORM_CAP,
              uniform_range: tuple[float, float] = UNIFORM_RANGE, style_family: Optional[str] = None,
              design: Optional[dict] = None) -> dict:
    """The ``asset`` dict for one piece (pure: the piece is not modified).

    A candidate is accepted when its non-uniform scale (max/min of sx, sy, sz) is
    within ``cap`` and its mean scale within ``uniform_range``; otherwise the next
    candidate in rank order (``rank_key``, Milestone 8) is tried, then the
    parametric fallback. Beds without a mattress (unless bed frames with a deck)
    and, with ``style_family``, models of another style are no candidates
    (``usable_candidates``). Milestone 10: ``design`` (the piece's look) keeps only the models that can show it
    (``look_of``); none left -> parametric with the reason. An L-shaped piece keeps only the models with its
    chaise side (``chaise_side_candidates``); none left -> the parametric L, which builds the drawn side."""
    ftype = piece["type"]
    width, depth = piece["footprint"]["size"]
    if not (width > 0 and depth > 0):
        return parametric_fit(piece, f"footprint size {piece['footprint']['size']} is not positive",
                              style_family=style_family)
    pin = piece.get("asset_pin")
    if pin:
        # Milestone 11 (edit_ops swap_model): the agent's model is tried alone first, through the same rules; when
        # it fails them the normal ranking decides and the asset says so.
        entry = next((e for e in catalog.candidates(ftype) if e.get("id") == pin), None)
        if entry is not None:
            pinned = fit_piece(dict(piece, asset_pin=None), _OneModel(catalog, entry), cap, uniform_range,
                               style_family, design)
            if pinned.get("method") == "library":
                pinned["pinned"] = pin
                return pinned
        asset = fit_piece(dict(piece, asset_pin=None), catalog, cap, uniform_range, style_family, design)
        asset["pin_refused"] = (f"{pin}: not a {ftype} model of the catalogue" if entry is None
                                else f"{pin}: fails the fit rules (style, caps, look)")
        return asset
    candidates = catalog.candidates(ftype)
    if not candidates:
        if ftype in catalog.parametric_types:
            reason = f"type {ftype} is parametric in the catalogue"
        else:
            reason = f"no catalogue entry for type {ftype}"
        return parametric_fit(piece, reason, style_family=style_family)
    candidates, excluded, reason = usable_candidates(ftype, candidates, style_family)
    if not candidates:
        return parametric_fit(piece, reason, excluded=excluded, style_family=style_family)
    if piece.get("shape") == "L":
        candidates, side_excluded, side = chaise_side_candidates(candidates, piece.get("chaise_side"))
        excluded += side_excluded
        if not candidates:
            return parametric_fit(piece, f"no {ftype} model with its chaise on the {side} (library models are not "
                                         "mirrored); the parametric L takes the drawn side",
                                  excluded=excluded, style_family=style_family)
    looks: dict[str, dict] = {}
    if design:
        kept = []
        for e in candidates:
            look, why = look_of(e, ftype, design)
            if look is None:
                excluded.append({"id": e["id"], "reason": why})
            else:
                kept.append(e)
                looks[e["id"]] = look
        if not kept:
            asked = {k: design[k] for k in ("material_tags", "fabric_colour", "colour") if design.get(k)}
            return parametric_fit(piece, f"no {ftype} model can show the design {asked} (recolour, colour or "
                                         "material tags); the parametric piece takes it",
                                  excluded=excluded, style_family=style_family)
        candidates = kept
        # Recolourable wood first among equals: a stable sort keeps the fit v2 order otherwise.
    ordered = rank_candidates(candidates, width, depth)
    if design and design.get("wood"):
        ordered = sorted(ordered, key=lambda e: 0 if "wood" in (looks.get(e["id"], {}).get("recolour") or {}) else 1)
    tried = []
    for rank, entry in enumerate(ordered, start=1):
        scales, non_uniform = scale_for(entry, width, depth)
        err = round(C.aspect_error(entry, width, depth), 4)
        mean_scale = round(sum(scales) / 3.0, 4)
        accepted = non_uniform <= cap + 1e-9 and uniform_range[0] <= mean_scale <= uniform_range[1]
        known = units_known(entry)
        size_err = round(size_error(scales), 4)
        tried.append({"id": entry["id"], "aspect_error": err, "scale": scales, "non_uniform": non_uniform,
                      "mean_scale": mean_scale, "accepted": accepted, "rank": rank, "source": entry.get("source"),
                      "units_known": known, "size_error": size_err,
                      "size_bucket": rank_key(entry, width, depth)[2] if known else None,
                      "quality": quality_of(entry)})
        if accepted:
            asset = {
                "library": entry["source"], "asset_id": entry["id"], "licence": entry["licence"],
                "license": entry["licence"], "method": "library", "fit_scale": scales,
                "bbox_m": [round(width, 4), round(depth, 4), round(entry["bbox_m"][2] * scales[2], 4)],
                "aspect_error": err, "front_axis": entry["front_axis"],
                "up_axis": entry["up_axis"], "origin_offset": list(entry["origin_offset"]),
                "rotation_fix_deg": C.reorient_rotation_deg(entry),
                "front_axis_confidence": entry["front_axis_confidence"], "candidates": tried, "cap": cap, "uniform_range": list(uniform_range),
                "styles": list(entry.get("styles") or []), "style_family": style_family, "excluded": excluded,
                "quality": entry.get("quality"), "units_known": known, "ranking": ranking_reasons(tried, tried[-1]),
            }
            if entry["source"] != "polyhaven" and entry.get("glb"):
                asset.update({k: entry[k] for k in GLB_ASSET_FIELDS if k in entry})
                # Catalogue boxes are metres = raw GLB box x unit_scale (the prep pod's unit guess); the
                # scene builder scales the imported mesh by it before fit_scale (blender/furniture.fit_vertices).
                asset["unit_scale"] = float(entry.get("unit_scale") or 1.0)
            else:
                asset["gltf"] = entry["gltf"]
            if "licence_flag" in entry:
                asset["licence_flag"] = entry["licence_flag"]
            if piece["type"] in C.BED_TYPES and not C.has_mattress(entry) and is_bed_frame(entry):
                asset.update(bed_frame_record(entry, width, depth, scales[2]))
                asset["bbox_m"][2] = max(asset["bbox_m"][2], asset["bedding"]["top_m"])
            look = looks.get(entry["id"]) or {}
            for key in ("recolour", "colour_match"):
                if look.get(key):
                    asset[key] = look[key]
            if look.get("tags"):
                asset["material_tags_asked"] = look["tags"]
            return asset
    best = min(tried, key=lambda t: t["non_uniform"])
    reason = (f"no {ftype} candidate within {round((cap - 1) * 100)} % non-uniform scale and "
              f"{uniform_range[0]}..{uniform_range[1]} mean scale (closest: {best['id']} at "
              f"{round((best['non_uniform'] - 1) * 100, 1)} % non-uniform, mean scale {best['mean_scale']})")
    return parametric_fit(piece, reason, tried, excluded=excluded, style_family=style_family)


def bed_frame_record(entry: dict, width: float, depth: float, z_scale: float) -> dict:
    """The bed-frame fields of a fitted asset (docs/milestone8.md §4): ``bed_frame``, the catalogue
    ``deck_height_m`` and ``bedding`` (``wenart.blender.parametric.frame_bedding_info``: deck and mattress
    top in the piece frame, deck = ``deck_height_m`` x the z fit scale, the inner box, the bedding top)."""
    from wenart.blender import parametric as P   # pure Python (no bpy)

    deck = float(entry["deck_height_m"])
    return {"bed_frame": True, "deck_height_m": deck,
            "bedding": P.frame_bedding_info(width, depth, deck * float(z_scale))}


# Decor (docs/milestone8.md §4): types that may use a library decor model; book sets stay parametric.
DECOR_LIBRARY_TYPES: tuple[str, ...] = ("cushion", "plant", "rug", "wall_art",
                                        "vase", "bowl", "plant_small", "table_lamp", "mirror",   # Milestone 9
                                        # Milestone 10 (docs/milestone10.md §4.6)
                                        "curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock",
                                        "sculpture", "plant_large", "pendant_light", "ceiling_light")
# Milestone 9 (docs/milestone9.md §3, §5): wall decor hangs like wall art (its width, the model's aspect); tabletop
# decor keeps the model's proportions and real size, scaled down (never up) to fit the item's box ("within").
WALL_DECOR_TYPES: tuple[str, ...] = ("wall_art", "mirror", "clock")
SURFACE_DECOR_TYPES: tuple[str, ...] = ("vase", "bowl", "plant_small", "table_lamp",
                                        # Milestone 10: tabletop and hanging pieces keep their real proportions
                                        "candle", "tray", "books", "sculpture", "basket", "pendant_light",
                                        "ceiling_light")
# Furniture models that serve a decor type too (the same object): a floor plant may be a potted_plant model.
DECOR_FROM_FURNITURE: dict[str, tuple[str, ...]] = {"plant": ("potted_plant",)}
# Decor models of catalog.json (Poly Haven, M4) by their old ``type``: the potted plants. The pillow model
# (``decor_cushion``: two loose pillows lying flat) stays out: squashed to a standing cushion it looks wrong.
LEGACY_DECOR_TYPES: dict[str, str] = {"decor_plant": "plant"}
DECOR_NON_UNIFORM_CAP = 1.5      # cushion / plant / rug footprint stretch (max/min of the x, y scales) above: refused
RUG_MAX_THICKNESS_M = 0.03       # a rug model is kept flat: its height is capped here
SURFACE_DECOR_MIN_M = 0.04       # a tabletop model scaled below this footprint side is refused (Milestone 9)
WALL_ART_MIN_WIDTH_M = 0.3       # a wall art model that would end narrower (ceiling room) is refused
_TURN_90 = {"-Y": "-X", "-X": "+Y", "+Y": "+X", "+X": "-Y"}   # the claimed front that turns a model by +90 degrees


def decor_type_of(entry: dict) -> Optional[str]:
    """The decor type of a catalogue entry: ``decor_type`` of a ``kind: decor`` entry (Milestone 8), or the
    Poly Haven ``decor_plant`` models of catalog.json; None for anything else."""
    if entry.get("kind") == "decor" and entry.get("decor_type"):
        return str(entry["decor_type"])
    return LEGACY_DECOR_TYPES.get(str(entry.get("type")))


def decor_entries(catalog, dtype: str) -> list[dict]:
    """The catalogue's decor models of ``dtype``, sorted by id: ``catalog.decor_candidates(dtype)`` when the
    catalogue has that method (Milestone 8 library), plus the decor entries of ``catalog.decor`` and
    ``catalog.entries`` of that type (``decor_type_of``); duplicates by id once."""
    found: list[dict] = []
    method = getattr(catalog, "decor_candidates", None)
    if callable(method):
        found += [e for e in (method(dtype) or []) if isinstance(e, dict)]
    for e in list(getattr(catalog, "decor", None) or []) + list(getattr(catalog, "entries", None) or []):
        if isinstance(e, dict) and decor_type_of(e) == dtype:
            found.append(e)
    furniture_types = DECOR_FROM_FURNITURE.get(dtype, ())
    for e in list(getattr(catalog, "entries", None) or []):    # Milestone 9: e.g. potted_plant models as plants
        if isinstance(e, dict) and e.get("type") in furniture_types and e.get("source") in C.LIBRARY_SOURCES:
            found.append(e)
    out: dict[str, dict] = {}
    for e in found:
        if e.get("id") and not e.get("parametric") and (e.get("gltf") or e.get("glb")) and e.get("bbox_m"):
            out.setdefault(str(e["id"]), e)
    return [out[k] for k in sorted(out)]


def decor_styles_match(entry: dict, family: Optional[str]) -> bool:
    """The M7 style rule for decor; a decor model without ``styles`` (the Poly Haven plants) is neutral."""
    return not entry.get("styles") or C.styles_match(entry, family)


def pick_index(key: str, n: int) -> int:
    """Deterministic pick of one of ``n`` models by a host id (the same host always gets the same model,
    different hosts spread over the models)."""
    return int(hashlib.sha256(str(key).encode("utf-8")).hexdigest()[:12], 16) % n if n else 0


def decor_pick_key(item: dict) -> str:
    """The id the library pick hangs on: the host piece, else the first anchor piece (rug, wall art), else the
    item itself (a floor plant)."""
    anchors = item.get("anchor_ids") or []
    return str(item.get("host_id") or (anchors[0] if anchors else None) or item.get("id") or item.get("type"))


def _decor_fit(entry: dict, item: dict, dtype: str) -> Optional[dict]:
    """Scale, box and orientation of one decor model on ``item``, or None when it does not fit
    (``DECOR_NON_UNIFORM_CAP``, a wall art that would be narrower than ``WALL_ART_MIN_WIDTH_M``)."""
    width, depth = (float(v) for v in item["size"][:2])
    bw, bd, bh = (float(v) for v in entry["bbox_m"][:3])
    front = entry["front_axis"]
    if dtype in SURFACE_DECOR_TYPES:              # Milestone 9: real size, scaled down to the item box, never up
        height = float(item["size"][2]) if len(item["size"]) > 2 and item["size"][2] else None
        limits = [width / bw, depth / bd] + ([height / bh] if height else [])
        s = min([1.0] + limits)
        if min(bw * s, bd * s) < SURFACE_DECOR_MIN_M - 1e-9:
            return None
        return {"fit_scale": [round(s, 4)] * 3, "bbox_m": [round(bw * s, 4), round(bd * s, 4), round(bh * s, 4)],
                "front_axis": front, "turned_deg": 0.0, "target": "within", "non_uniform": 1.0}
    if dtype in WALL_DECOR_TYPES:                 # its width, the model's aspect; the height the wall allows
        s = width / bw
        max_h = item.get("max_height_m")
        if isinstance(max_h, (int, float)) and max_h > 0 and bh * s > float(max_h):
            s = float(max_h) / bh
        if bw * s < WALL_ART_MIN_WIDTH_M - 1e-9:
            return None
        return {"fit_scale": [round(s, 4)] * 3, "bbox_m": [round(bw * s, 4), round(bd * s, 4), round(bh * s, 4)],
                "front_axis": front, "turned_deg": 0.0, "target": "wall_art", "non_uniform": 1.0}
    turned = 0.0
    if dtype == "rug" and C.aspect_error({"bbox_m": [bd, bw, bh]}, width, depth) < C.aspect_error(entry, width, depth):
        bw, bd, front, turned = bd, bw, _TURN_90[front], 90.0      # a rug has no front: turn it to its long side
    sx, sy = width / bw, depth / bd
    non_uniform = max(sx, sy) / min(sx, sy)
    if non_uniform > DECOR_NON_UNIFORM_CAP + 1e-9:
        return None
    if dtype == "rug":                            # flat: scaled to the rug size, its thickness kept (capped)
        h = min(bh, RUG_MAX_THICKNESS_M)
        return {"fit_scale": [round(sx, 4), round(sy, 4), round(h / bh, 4)],
                "bbox_m": [round(width, 4), round(depth, 4), round(h, 4)], "front_axis": front,
                "turned_deg": turned, "target": "rug", "non_uniform": round(non_uniform, 4)}
    sz = (sx + sy) / 2.0                          # cushion, plant: the item box, height by the mean scale
    return {"fit_scale": [round(sx, 4), round(sy, 4), round(sz, 4)],
            "bbox_m": [round(width, 4), round(depth, 4), round(bh * sz, 4)], "front_axis": front,
            "turned_deg": 0.0, "target": "size", "non_uniform": round(non_uniform, 4)}


def fit_decor_item(item: dict, catalog, style_family: Optional[str] = None) -> Optional[dict]:
    """``asset`` for a decor item (docs/milestone8.md §4): one of the catalogue's decor models of its type
    and of the style family or neutral (``decor_entries``, ``decor_styles_match``) that fits the item
    (``_decor_fit``), picked deterministically by the host id (``pick_index`` of ``decor_pick_key``); None
    (parametric decor; no wall art) when there is none. Blender scales the model to ``bbox_m``."""
    dtype = item.get("type", "")
    if dtype not in DECOR_LIBRARY_TYPES or not item.get("size") or len(item["size"]) < 2:
        return None
    styled = [e for e in decor_entries(catalog, dtype) if decor_styles_match(e, style_family)]
    fits = [(e, f) for e in styled for f in [_decor_fit(e, item, dtype)] if f is not None]
    if not fits:
        return None
    # Milestone 10: a large plant of the brief's species takes models of that species first.
    species = item.get("species")
    if dtype == "plant_large" and species:
        same = [(e, f) for e, f in fits if e.get("species") == species]
        fits = same or fits
    # Milestone 9: an AI decor item names a colour; models whose name holds it come first (the pick stays
    # deterministic by the host id inside the chosen group).
    colour = str(item.get("colour") or "").strip().casefold()
    coloured = [(e, f) for e, f in fits if colour and colour in str(e.get("name") or e.get("title") or "").casefold()]
    pool = coloured or fits
    key = decor_pick_key(item)
    i = pick_index(key, len(pool))
    entry, f = pool[i]
    width, depth = (float(v) for v in item["size"][:2])
    asset = {
        "library": entry.get("source") or "polyhaven", "asset_id": entry["id"], "licence": entry.get("licence"),
        "license": entry.get("licence"), "method": "library", "decor_type": dtype, "fit_scale": f["fit_scale"],
        "bbox_m": f["bbox_m"], "aspect_error": round(C.aspect_error(entry, width, depth), 4),
        "front_axis": f["front_axis"], "up_axis": entry.get("up_axis", "+Z"),
        "origin_offset": list(entry.get("origin_offset") or [0.0, 0.0, 0.0]),
        "front_axis_confidence": entry.get("front_axis_confidence"), "target": f["target"],
        "turned_deg": f["turned_deg"], "styles": list(entry.get("styles") or []), "style_family": style_family,
        "quality": entry.get("quality"),
        "pick": {"key": key, "index": i, "of": len(pool), "ids": [e["id"] for e, _f in pool],
                 "colour": colour or None, "colour_matches": len(coloured),
                 "not_fitting": [e["id"] for e in styled if e["id"] not in {x["id"] for x, _f in fits}],
                 "other_style": len(decor_entries(catalog, dtype)) - len(styled)},
    }
    if asset["library"] != "polyhaven" and entry.get("glb"):
        asset.update({k: entry[k] for k in GLB_ASSET_FIELDS if k in entry})
        asset["unit_scale"] = float(entry.get("unit_scale") or 1.0)
    else:
        asset["gltf"] = entry["gltf"]
    if "licence_flag" in entry:
        asset["licence_flag"] = entry["licence_flag"]
    return asset


def design_of(piece: dict, style: Optional[dict]) -> dict:
    """The look the fit honours for a piece (Milestone 10): its ``furniture.design`` (layout stage), else the
    ``style.json`` fallback of ``wenart.blender.looks.design_for``; {} without a style."""
    if style is None and not isinstance(piece.get("design"), dict):
        return {}
    from wenart.blender import looks as LK

    return LK.design_for(piece, style or {})[0]


def fit_building(building: dict, catalog: C.Catalog, cap: float = NON_UNIFORM_CAP,
                 style_family: Optional[str] = None, style: Optional[dict] = None) -> dict:
    """A deep copy of ``building`` with ``asset`` set on every furniture piece
    and on every decor item (a library decor model, or None: parametric decor,
    no wall art), nothing else changed. ``style_family`` (refit only): the
    library style filter of ``fit_piece`` and ``fit_decor_item``; ``style`` (refit only, Milestone 10): the
    profile whose looks the fit honours (``design_of``)."""
    fitted = copy.deepcopy(building)
    for original, piece in zip(building.get("furniture", []), fitted.get("furniture", [])):
        design = design_of(piece, style) if (style is not None or piece.get("design")) else None
        piece["asset"] = fit_piece(piece, catalog, cap=cap, style_family=style_family, design=design or None)
        for key in FROZEN_KEYS:
            if original.get(key) != piece.get(key):  # cannot happen; guards future edits
                raise RuntimeError(f"fit changed {key} of {piece['id']}")
    for item in fitted.get("decor") or []:
        item["asset"] = fit_decor_item(item, catalog, style_family=style_family)
    return fitted


def assert_only_assets_changed(before: dict, after: dict) -> None:
    """Raise AssertionError unless ``after`` equals ``before`` except for
    ``furniture[].asset`` and ``decor[].asset``."""
    a, b = copy.deepcopy(before), copy.deepcopy(after)
    for doc in (a, b):
        for piece in doc.get("furniture", []):
            piece.pop("asset", None)
        for item in doc.get("decor") or []:
            item.pop("asset", None)
    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
        raise AssertionError("fit changed something other than furniture[].asset and decor[].asset")


def style_family_of(profile) -> tuple[Optional[str], str]:
    """``(family, how)`` of a style profile (``style.json``; a list of profiles -> the first, as the scene
    builder renders): its ``family`` field (Milestone 7, None allowed), or for an older profile without the
    field the family keyword of its ``source_text`` (``wenart.style.profile.match_text``, the same rule)."""
    if isinstance(profile, list):
        profile = profile[0] if profile else {}
    profile = profile if isinstance(profile, dict) else {}
    if "family" in profile:
        return profile["family"], "the profile's family"
    from wenart.style.profile import match_text

    text = profile.get("source_text")
    family = match_text(text)["family"] if isinstance(text, str) and text.strip() else None
    return family, "no family field: matched in source_text"


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def _fmt_scale(scales) -> str:
    return " / ".join(f"{s:.3f}" for s in scales)


def fit_report(building: dict, title: Optional[str] = None, style_note: Optional[str] = None) -> str:
    """Markdown: one row per piece (asset, licence, scale, aspect error, method), fallbacks, licences,
    the style filter (``style_note``: the family and where it came from), the fit v2 ranking of every library
    fit (Milestone 8), bed frames and their bedding, licence flags and the CC BY credit lines."""
    pieces = building.get("furniture", [])
    rows = []
    fallbacks, licences, missing = [], Counter(), []
    credits: dict[str, str] = {}
    excluded: list[tuple[str, str, str]] = []
    ranking: list[str] = []
    frames: list[str] = []
    flags: dict[str, str] = {}
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
            if str(asset["licence"]).upper().startswith("CC-BY"):
                credits[asset["asset_id"]] = asset.get("attribution") or "(no attribution recorded)"
            if asset.get("licence_flag"):
                flags[asset["asset_id"]] = f"{asset['licence']} ({asset['licence_flag']})"
            rank = asset.get("ranking")
            if rank:
                ranking.append(f"- {piece['id']} ({piece['type']}): {asset['asset_id']} ({asset['library']}), rank "
                               f"{rank['rank']} of {rank['tried']} tried: {'; '.join(rank['reasons'])}"
                               + (f"; passed over {', '.join(x['id'] for x in rank['passed_over'])} (caps)"
                                  if rank.get("passed_over") else ""))
            if asset.get("bed_frame"):
                bed = asset["bedding"]
                frames.append(f"- {piece['id']}: {asset['asset_id']} is a bed frame (deck {asset['deck_height_m']:.3f} m "
                              f"in the model, {bed['deck_z_m']:.3f} m fitted): parametric mattress top "
                              f"{bed['mattress_top_m']:.3f} m, inner box {bed['inner_box_m'][0]:.2f} x "
                              f"{bed['inner_box_m'][1]:.2f} m, duvet and pillows")
        excluded += [(piece["id"], x["id"], x["reason"]) for x in asset.get("excluded") or []]
    lines = [f"# Furniture fit report{': ' + title if title else ''}", ""]
    project = building.get("project")
    project_id = project.get("id", "?") if isinstance(project, dict) else str(project or "?")
    lines.append(f"Project: {project_id}; {len(pieces)} pieces, "
                 f"{len(pieces) - len(fallbacks) - len(missing)} library fits, {len(fallbacks)} parametric fallbacks"
                 f"{', ' + str(len(missing)) + ' without fit' if missing else ''}. "
                 f"Non-uniform scale cap {round((NON_UNIFORM_CAP - 1) * 100)} %. Footprints, types, rotations, rooms "
                 f"and statuses are as in the building JSON (fitting never changes them).")
    if style_note:
        lines += ["", f"Library style filter: {style_note}"]
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
    if ranking:
        lines += ["", "## Ranking (fit v2)", "", f"Rule: {RANKING_RULE}.", ""] + ranking
    if frames:
        lines += ["", "## Bed frames with bedding", ""] + frames
    looks = [(p["id"], p["asset"]) for p in pieces if (p.get("asset") or {}).get("recolour")
             or (p.get("asset") or {}).get("colour_match")]
    if looks:
        lines += ["", "## Recolour and colour matches (Milestone 10)", ""]
        for pid, asset in looks:
            for part, spec in sorted((asset.get("recolour") or {}).items()):
                lines.append(f"- {pid}: {asset['asset_id']} {part} slots "
                             f"{[s.get('index') for s in spec.get('slots') or []]} recoloured {spec.get('colour')}")
            if asset.get("colour_match"):
                cm = asset["colour_match"]
                lines.append(f"- {pid}: {asset['asset_id']} already {cm['colour']} (Delta E {cm['delta_e']})")
    if excluded:
        lines += ["", "## Models not taken (mattress rule, style filter, design)", ""]
        lines += [f"- {pid}: {aid}: {why}" for pid, aid, why in excluded]
    for item in building.get("decor") or []:              # Milestone 8: library decor models credit too
        asset = item.get("asset") or {}
        if asset.get("method") != "library":
            continue
        if str(asset.get("licence") or "").upper().startswith("CC-BY"):
            credits[asset["asset_id"]] = asset.get("attribution") or "(no attribution recorded)"
        if asset.get("licence_flag"):
            flags[asset["asset_id"]] = f"{asset['licence']} ({asset['licence_flag']})"
    if flags:
        lines += ["", "## Licence flags (recorded, not filtered: docs/milestone8.md §2)", ""]
        lines += [f"- {aid}: {text}" for aid, text in sorted(flags.items())]
    if credits:
        lines += ["", "## Attribution (CC BY 4.0)", ""] + [f"- {aid}: {text}" for aid, text in sorted(credits.items())]
    if missing:
        lines += ["", "## Pieces without a fit", ""] + [f"- {pid}" for pid in missing]
    decor = building.get("decor") or []
    if decor:
        by_kind = Counter((d["type"], (d.get("asset") or {}).get("asset_id")
                           or ("none (not built)" if d["type"] == "wall_art" else "parametric")) for d in decor)
        lines += ["", "## Decor", ""]
        lines += [f"- {kind}: {aid} x {n}" for (kind, aid), n in sorted(by_kind.items())]
        lines.append("- books are parametric by design; cushions, plants and rugs without a library decor model of "
                     "the style family (or neutral) are parametric, wall art without one is not built")
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
    for piece in list(building.get("furniture", [])) + list(building.get("decor") or []):
        asset = piece.get("asset") or {}
        if asset.get("method") != "library":
            continue
        asset_id = asset["asset_id"]
        if asset_id not in cache:
            # Objaverse (and, Milestone 8, ABO and generated) models come only from the prep pod's cache,
            # checked against the catalogue sha256: the fetcher gets the fit's asset dict.
            extra = {"meta": asset} if asset["library"] != "polyhaven" else {}
            try:
                M.fetch_model(asset_id, assets_dir, size="1k", source=asset["library"], licence=asset["licence"],
                              **extra)
                cache[asset_id] = None
                result["fetched"].append(asset_id)
                log(f"model {asset_id:<28} ok")
            except (web.NetworkError, web.HTTPStatusError, fetch.AssetNotFound, fetch.LicenceError, KeyError,
                    RuntimeError) as exc:
                cache[asset_id] = f"{type(exc).__name__}: {exc}"
                result["failed"][asset_id] = cache[asset_id]
                log(f"model {asset_id:<28} FAILED: {exc}")
        if cache[asset_id] is not None:
            if piece.get("kind") == "decor":
                piece["asset"] = None            # decor: the parametric mesh, reason in the log above
            else:
                piece["asset"] = parametric_fit(
                    piece, f"download of {asset_id} failed ({cache[asset_id]}); parametric fallback",
                    candidates=asset.get("candidates"), excluded=asset.get("excluded"),
                    style_family=asset.get("style_family"))
    return result


def locked_check(source_path: Path, fitted: dict, completion_path: Optional[Path] = None) -> tuple[list[str], str]:
    """``(violations, how)``: ``wenart.furniture.locked.check`` of the drawn furniture of ``source_path`` (the
    building before the layout) against the fitted building, mode and kept rooms from ``completion.json``
    (``complete`` and none when it is not given)."""
    from wenart import building as B
    from wenart.furniture import locked

    completion = json.loads(completion_path.read_text(encoding="utf-8")) if completion_path else None
    mode, keep = locked.mode_of(completion), locked.keep_rooms_of(completion)
    problems = locked.check(B.load(source_path), fitted, mode, keep_rooms=keep)
    how = (f"source {source_path}, mode {mode}" + (f", kept rooms {', '.join(keep)}" if keep else "")
           + (f" (from {completion_path})" if completion_path else " (no completion.json: complete)"))
    return problems, how


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="fit catalogue assets to the furniture of a building JSON")
    parser.add_argument("building", help="building.json from the ingest pipeline (or the layout step)")
    parser.add_argument("--catalog", default=str(C.CATALOG_PATH), help="catalog.json (default: the package one)")
    parser.add_argument("--out", required=True, help="where to write the fitted building JSON")
    parser.add_argument("--assets", default=None, help="assets folder; when given, the fitted models are downloaded")
    parser.add_argument("--report", default=None, help="markdown report path (default: <out stem>_report.md)")
    parser.add_argument("--no-download", action="store_true", help="do not download even when --assets is given")
    parser.add_argument("--style", default=None,
                        help="style.json (refit only): library models only of its style family or neutral")
    parser.add_argument("--source", default=None,
                        help="building.json before the layout (refit only): run the locked check of the drawn "
                             "furniture; a violation exits 1 (docs/milestone10.md §2.7)")
    parser.add_argument("--completion", default=None,
                        help="completion.json of the layout stage (the check's mode and kept rooms)")
    args = parser.parse_args(argv)

    from wenart import building as B

    building = B.load(args.building)
    catalog = C.load(Path(args.catalog))
    family, style_note, profile = None, None, None
    if args.style:
        profile = json.loads(Path(args.style).read_text(encoding="utf-8"))
        family, how = style_family_of(profile)
        style_note = (f"family {family!r} ({how}, {args.style}): library models only when their styles hold "
                      f"{family!r} or {C.NEUTRAL!r}" if family else
                      f"no style family ({how}, {args.style}): every library model may be used")
        print(f"style filter: {style_note}")
    if isinstance(profile, list):
        profile = profile[0] if profile else None
    fitted = fit_building(building, catalog, style_family=family, style=profile if isinstance(profile, dict) else None)
    if args.assets and not args.no_download:
        result = download_fitted(fitted, Path(args.assets))
        if result["failed"]:
            print(f"{len(result['failed'])} model download(s) failed; those pieces use the parametric fallback")
    assert_only_assets_changed(building, fitted)
    out = Path(args.out)
    report_path = Path(args.report) if args.report else out.with_name(out.stem + "_report.md")
    report = fit_report(fitted, title=out.stem, style_note=style_note)
    if args.source:
        problems, how = locked_check(Path(args.source), fitted, Path(args.completion) if args.completion else None)
        report += "\n## Locked check (docs/milestone10.md §2.7)\n\n" + how + "\n\n" + (
            "\n".join(f"- {p}" for p in problems) if problems else "- pass") + "\n"
        if problems:
            report_path.write_text(report, encoding="utf-8")
            print(f"locked check: {len(problems)} violation(s); {out} not written (report {report_path})",
                  file=sys.stderr)
            for line in problems:
                print(f"  {line}", file=sys.stderr)
            return 1
    B.save(fitted, out)
    report_path.write_text(report, encoding="utf-8")
    methods = Counter(p["asset"]["method"] for p in fitted.get("furniture", []))
    print(f"{len(fitted.get('furniture', []))} pieces: {methods.get('library', 0)} library, "
          f"{methods.get('parametric', 0)} parametric -> {out} (report {report_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
