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

Milestone 13 (docs/milestone13.md §3.0 K1, K2, K7, §12 D1, D3, D4, D5, §13.2, §13.3; track T1):

- What: (1) a licence mode: ``fit_piece(..., mode="commercial")`` and ``fit_building(..., mode=None)`` (None =
  ``project.licence_mode`` of the building, else ``catalog.licence_mode(brief)``: env ``WENART_LICENCE_MODE`` > brief
  ``library.licence_mode`` > ``commercial``); the fit writes ``project.licence_mode`` (and where it came from) and
  every asset carries ``licence``, ``licence_flag``, ``commercial_safe``, ``licence_mode``. (2) The ranking without
  the wood re-sort: real size (uniform scale to the drawn width), real product, known units, the design as a
  preference (material tags, fabric colour: models that show it first, the others still tried, ``design_not_shown``
  when one wins), the audit's vision quality, the texture maps, the judges' quality, the face count (tie-breaks, never
  gates: decision 1a of 11 Oct 2026), aspect error, source, id; a diversity penalty per room and per project
  (``ROOM_REUSE_MAX``, ``ROOM_REUSE_STEPS``, ``PROJECT_REUSE_STEP``: the n-th use of a model costs size steps; a
  matched set, ``SET_TYPES``, is never split within its room). (3)
  Uniform scaling: a model is scaled by the drawn width only (``scale_for``: sx = sy = sz); its depth may differ from
  the drawn depth by ``NON_UNIFORM_CAP`` (10 %; the layout absorbs the difference, ``asset.depth_abs_m``), its mean
  scale lies in ``UNIFORM_RANGE``, its height within 15 % of the real range; no mesh is stretched any more. (4) Pins
  skip the style filter (the agent's choice is the decision; the caps still apply). (5) The fabric colour of the brief
  reaches the asset (``asset.fabric_colour``, from ``design.fabric_colour`` or the style's ``furniture.by_type`` /
  ``furniture.fabric_colour``; B1 of §1.8). (6) The size snap before the fit (``apply_size_snap``,
  ``wenart.furniture.sizes.snap_size``): a drawn furniture size outside its type's product range becomes the nearest
  real product (``piece.size_snap``, ``adjusted_by_ai``, ``drawn_footprint`` kept; the back edge stays where it was
  when the depth changes); off with ``furnished_rooms: keep`` or ``furnished_rooms_keep_size``; fixed equipment is
  not snapped here (the ingest's fixed rule and the agent's ``fix_fixture`` do that). (7) The fallback ladder (D4): a
  piece with no library model within the caps tries, in order, step 1 the nearest audited model (the caps, then the
  relaxed M11 caps ``RELAXED_CAP`` / ``RELAXED_RANGE`` only while the fitted box stays inside the type's documented
  ranges; a related type for a piece its group needs), step 2 a module builder (``wenart.blender.modules.module_plan``,
  track T2; import guarded: absent or None means step 3), step 3 the parametric family (``method: parametric``).
  ``asset.ladder`` logs every step with its result and reason; ``piece.library_gap`` names the step used (``step``);
  ``method: none`` only for a piece that is not built (``build: false``: not furniture, removed). A drawn anchor is
  never left out.
- Why: §1.2-1.3 of the milestone: the wood re-sort put an Objaverse chair of unknown units in front of the real ABO
  chair 82 times; 43 drawn pieces of real04 (20 of 33 drawn anchors) were not built at all; half of the built library
  pieces were stretched by more than 5 %; the brief's fabric colour never arrived.
- How: ``fit_building`` snaps, resolves the mode, keeps the use counters and passes them into ``fit_piece``;
  ``fit_piece`` runs the library search (``_fit_family`` per style family with the preference order), the relaxed
  caps, then ``_no_model`` (related type, module, parametric); every result goes through ``_finish`` (licence
  fields, the ladder). ``fit_report`` lists the mode, the flagged assets, the snaps and the pieces built below the
  library level.
- Build round 2 (15 Oct 2026): ``SOURCE_ORDER`` ranks the HSSD layer (``hssd``, CC BY-NC 4.0, relaxed mode only) after
  Poly Haven and before GSO (real products at real size, declared by the publisher; the licence mode decides whether
  they are candidates at all, ``catalog.usable``). A module plan with a ``split`` (``wenart.blender.modules``: a drawn
  table footprint that includes its chairs, CLAUDE.md "a table footprint that includes its chairs") labels the piece
  ``adjusted_by_ai`` with the reason (``split_label`` on the asset, ``apply_split_label`` on the piece in
  ``fit_building``): the footprint stays as drawn (the modules sit inside it), ``drawn_footprint`` and the other
  ``drawn_*`` keys are kept, and the label names the table and the chairs built in it.
- Build round 3 (lead decision): the split decides BEFORE the size snap. ``fit_building`` asks the module plan first
  (``split_plan_first``: a ``table_dining`` footprint deeper than ``modules.TABLE_DEPTH_MAX_M``, 1.20 m, is a table
  with its chairs); such a piece is labelled ``module_split`` with ``drawn_footprint`` kept and only its table part
  is judged by the snap (``apply_split_then_snap`` -> ``apply_size_snap(part=...)``: the width and the height may
  take a real product, the drawn depth stays because it holds the chairs; ``size_snap.part``; the label keeps
  ``rule: module_split`` with ``rules = [module_split, size_snap]`` and a reason that names the built table and
  chairs, ``split_snap_reason``). Before, the snap ran first and took the drawn 1.8 m depth to a 1.0 m product
  depth, which erased the chairs (``project.size_snap.split_first`` lists the ids). No drawn table of the committed
  real02 / real03 / real04 buildings is deeper than 1.20 m (real04's 10-seat tables are drawn 3.35 x 1.00 m with
  their ten chairs as separate pieces), so their fit does not change. Review of round 3: a piece split first is
  built by its module plan even when a library table would fit the full footprint (``split_module_fit``: the split
  decides, the library pick is logged as ``split_over``); a footprint drawn with its long side as the depth is not
  split first (``plan_table_long`` has no orientation check); ``assert_only_assets_changed`` accepts the snap of a
  split table's part (the width only).
- Fix round after P3 (16-17 Oct 2026), kitchen runs. What: ``kitchen_built_ins`` (pure, before the per-piece fit)
  finds, per built kitchen counter or island, the built drawn sinks and stoves of its level and room with at least
  ``BUILT_IN_SHARE`` of their footprint inside it (``modules.member_in_run``). The largest sink is built into the run:
  the run's plan gets ``sink_pos_m`` / ``sink_w_m`` / ``sink_piece`` (a sink unit with the bowl and tap at its
  cutout, ``plan["built_ins"]``) and the sink's asset says ``built_in: <run id>`` (``method: module``, the run's
  ``asset_id``, by design; build, type and evidence unchanged, so the group checks and the metrics still see a
  sink); the scene does not build it again (``furniture.built_in_ids``). Each stove becomes a gap of the run
  (``ranges``: no base unit, plinth or worktop at its drawn span); the stove keeps its own model. Why: pod P3 built
  every drawn sink and stove inside full-depth base units under an uncut worktop (only a tap and a stove front
  showed). How: the hints reach the plan on a copy of the run (``dict(piece, module_hints=...)``) and are stored as
  ``asset.module_hints`` beside ``asset.module_plan``: the building piece itself never gets ``module_hints``, so
  ``FROZEN_KEYS`` and ``assert_only_assets_changed`` hold. A sink is made a built-in only when the run's plan holds
  it; otherwise it is fitted as before. A pinned sink (``asset_pin``, the agent's model) is never a built-in.
- Fix round after P3, part 2 (17 Oct 2026), kitchen runs. What: a pinned sink inside a run gets a gap of the run
  (``ranges`` entry ``type: sink_kitchen`` with its reason; it keeps its pinned model and stands as drawn); a sink the
  run's plan does not build in because its sink unit would stand more than ``modules.KITCHEN_END_SHIFT_MAX_M`` from
  the drawn centre gets a gap from the plan itself (``modules.plan_kitchen_run``); a built-in records the unit's
  ``shift_m`` from the drawn centre, which the sink's asset reason and the fit report's "Kitchen runs" section name.
  Why: a pinned sink inside a run was neither built in nor given a gap, so it stood buried in full-depth base units
  under an uncut worktop again (the P3 defect; only S2 reported it, and no agent tool clears that); a drawn sink
  overhanging the run's end was built in up to 0.4 of its width from where it is drawn, with no record (the CLAUDE.md
  fixed-equipment rule: as drawn). How: the gap goes through the run's hints like a stove's; nothing on the piece
  changes (``assert_only_assets_changed``).
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

# Milestone 12 (docs/milestone12.md §4.8 D14): real proportions: a model is stretched by at most 10 % between its
# axes (was 15 %) and scaled by 0.85-1.20 on average (was 0.75-1.30); outside -> the next model.
# Milestone 13 (K2): the model is scaled uniformly by the drawn width; NON_UNIFORM_CAP is now the depth mismatch the
# layout absorbs (fitted depth / drawn depth, either way), UNIFORM_RANGE the range of that one scale.
NON_UNIFORM_CAP = 1.10
PARAMETRIC_LIBRARY = "parametric"
PARAMETRIC_LICENCE = "n/a"
# Milestone 13 (D4, ladder step 1b): the Milestone 11 caps, accepted only while the fitted box stays inside the type's
# documented ranges (wenart.furniture.sizes), so a near miss of the M12 caps is a real product and not a gap.
RELAXED_CAP = 1.15
RELAXED_RANGE = (0.75, 1.30)
# Milestone 13 (K2): the diversity penalty, in SIZE_BUCKET steps of the rank (a penalty, never a gate: the model is
# still taken when nothing else fits).
ROOM_REUSE_MAX = 2               # a model may be used this often in a room before the room penalty
ROOM_REUSE_STEPS = 4             # ... then it ranks as if its real-size error were 4 steps (20 %) larger
PROJECT_REUSE_STEP = 1           # every earlier use in another room of the project adds one step (5 %)
# Types a room holds as a matched set (the dining chairs round one table, the two nightstands of a bed, the stools
# at a counter): the room penalty does not split a set; the project penalty (other rooms) still varies the sets.
SET_TYPES: tuple[str, ...] = ("chair", "bar_stool", "office_chair", "nightstand", "side_table")
# Milestone 13 (K2): tie-breaks after the audit's vision quality (never gates, decision 1a of 11 Oct 2026).
FACES_LOW = 3000                 # below: low-poly (the audit's own threshold)
VISION_QUALITY_DEFAULT = 3.0     # an entry without an audited vision quality ranks as "plain" (the audit's 3)
MODULE_METHOD = "module"
METHODS: tuple[str, ...] = ("library", MODULE_METHOD, "parametric", "none")
LADDER_STEPS: tuple[str, ...] = ("library", MODULE_METHOD, "parametric")
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

# Fit v2 ranking (docs/milestone8.md §1); Milestone 13 (K2): the design preference, the audit's vision quality, the
# texture maps, the face count and the diversity penalty join it; the wood re-sort is gone.
# gso: M12 pod P4 scans; hssd: M13 pod P2 (docs/milestone13.md §12 D2; CC BY-NC 4.0, candidates in relaxed mode only)
SOURCE_ORDER: tuple[str, ...] = ("abo", "polyhaven", "hssd", "gso", "objaverse", "generated")
GENERATED = "generated"
DEFAULT_QUALITY = 3.0
SIZE_BUCKET = 0.05           # real-size error steps: models within the same 5 % step are ranked by quality
RANKING_RULE = ("style -> bed rule -> generated last -> real size (known units first, mean |scale - 1| of the "
                f"uniform scale to the drawn width in {round(SIZE_BUCKET * 100)} % steps, plus the diversity penalty: "
                f"{PROJECT_REUSE_STEP} step per earlier use in another room of the project, {ROOM_REUSE_STEPS} steps "
                f"from the {ROOM_REUSE_MAX + 1}. use in a room except for a matched set of "
                f"{', '.join(SET_TYPES)}) -> real product -> design shown (tags, fabric colour) -> audit vision "
                f"quality (missing = {VISION_QUALITY_DEFAULT:g}) -> texture maps -> judge quality (missing = "
                f"{DEFAULT_QUALITY:g}) -> faces (< {FACES_LOW} last) -> aspect error -> source "
                f"({', '.join(SOURCE_ORDER)}) -> id")


# --------------------------------------------------------------------------
# Pure fitting
# --------------------------------------------------------------------------

def scale_for(entry: dict, width: float, depth: float) -> tuple[list[float], float]:
    """``([s, s, s], depth_ratio)`` for an entry on a ``width x depth`` footprint (Milestone 13, K2): one uniform
    scale ``s = width / model width`` (the model keeps its proportions), and the mismatch of its scaled depth against
    the drawn depth as a ratio >= 1 (the layout absorbs it up to ``NON_UNIFORM_CAP``)."""
    s = width / entry["bbox_m"][0]
    fitted_depth = entry["bbox_m"][1] * s
    ratio = max(fitted_depth, depth) / min(fitted_depth, depth) if depth > 0 and fitted_depth > 0 else math.inf
    return [round(s, 4)] * 3, round(ratio, 4)


def fitted_depth(entry: dict, width: float) -> float:
    """The depth a model has after the uniform scale to ``width``."""
    return round(entry["bbox_m"][1] * (width / entry["bbox_m"][0]), 4)


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
    """The judges' mean photoreal quality (1-5); ``DEFAULT_QUALITY`` when missing or not a number. Milestone 12
    (B1): the catalogue stores the two judges' answers as a list ``[q1, q2]``: its mean (the old code read only a
    number, so every model ranked at 3.0)."""
    q = entry.get("quality")
    if isinstance(q, (list, tuple)):
        vals = [float(v) for v in q if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)]
        return sum(vals) / len(vals) if vals else DEFAULT_QUALITY
    if isinstance(q, bool) or not isinstance(q, (int, float)) or not math.isfinite(q):
        return DEFAULT_QUALITY
    return float(q)


def source_rank(entry: dict) -> int:
    source = entry.get("source")
    return SOURCE_ORDER.index(source) if source in SOURCE_ORDER else len(SOURCE_ORDER)


def size_error(scales) -> float:
    """Mean ``|scale - 1|`` over the fit scales: 0 when the model's real size is the footprint."""
    return sum(abs(float(s) - 1.0) for s in scales) / len(scales)


def vision_quality_of(entry: dict) -> Optional[float]:
    """The audit's single-pass vision quality (1-5) when the catalogue records it (``audit.vision.quality`` or
    ``audit.vision_quality``; track T7 writes it for the new entries), else None."""
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    value = audit.get("vision_quality")
    if value is None and isinstance(audit.get("vision"), dict):
        value = audit["vision"].get("quality")
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value)


def faces_of(entry: dict) -> Optional[int]:
    """The model's face count (``polycount``) when known."""
    n = entry.get("polycount")
    return int(n) if isinstance(n, (int, float)) and not isinstance(n, bool) and n > 0 else None


def faces_rank(entry: dict) -> int:
    """0 for a model with enough faces, 1 when the count is not known, 2 for a low-poly model (< ``FACES_LOW``)."""
    n = faces_of(entry)
    if n is None:
        return 1
    return 2 if n < FACES_LOW else 0


def texture_maps_of(entry: dict) -> Optional[dict]:
    """What the catalogue knows about a model's texture maps (Milestone 13: recorded per model, track T7 adds the PBR
    maps as ``texture_maps``): the entry's ``texture_maps`` record, else ``{"base_colour": bool}`` from the Milestone 8
    ``textured`` flag and the judged slots (``material_slots[].textured``); None when nothing is recorded."""
    maps = entry.get("texture_maps")
    if isinstance(maps, dict):
        return dict(maps)
    slots = [s for s in entry.get("material_slots") or [] if isinstance(s, dict)]
    textured = entry.get("textured")
    if not isinstance(textured, bool) and not slots:
        return None
    out: dict = {}
    if isinstance(textured, bool):
        out["base_colour"] = textured
    if slots:
        out["slots_textured"] = sum(1 for s in slots if s.get("textured") is True)
        out["slots"] = len(slots)
        out.setdefault("base_colour", out["slots_textured"] > 0)
    return out


def maps_rank(entry: dict) -> int:
    """0 for a model with normal or roughness maps recorded, 1 for base colour only (or unknown), 2 for flat colours."""
    maps = texture_maps_of(entry)
    if not maps:
        return 1
    if maps.get("normal") or maps.get("roughness") or maps.get("metallic_roughness"):
        return 0
    return 2 if maps.get("base_colour") is False else 1


def diversity_steps(asset_id: str, used: Optional[dict]) -> int:
    """The rank penalty (in ``SIZE_BUCKET`` steps) of using ``asset_id`` once more (Milestone 13, K2):
    ``PROJECT_REUSE_STEP`` per earlier use in another room of the project (``used["project"]`` minus
    ``used["room"]``: the n-th use in the project ranks n - 1 steps worse, so the next room gets another model when
    one of the same size step exists) plus ``ROOM_REUSE_STEPS`` once the room (``used["room"]``) holds it
    ``ROOM_REUSE_MAX`` times already, unless the piece's type (``used["type"]``) is a matched set (``SET_TYPES``: six
    dining chairs are one set, never three models). A penalty, never a gate: with nothing else in reach the model is
    used again."""
    if not used:
        return 0
    project = used.get("project") or {}
    room = used.get("room") or {}
    in_room = int(room.get(asset_id, 0) or 0)
    elsewhere = max(0, int(project.get(asset_id, 0) or 0) - in_room)
    steps = PROJECT_REUSE_STEP * elsewhere
    if in_room >= ROOM_REUSE_MAX and used.get("type") not in SET_TYPES:
        steps += ROOM_REUSE_STEPS
    return steps


def rank_key(entry: dict, width: float, depth: float, used: Optional[dict] = None,
             prefs: Optional[dict] = None) -> tuple:
    """The order of a candidate on a ``width x depth`` footprint (lower first, docs/milestone8.md §1; Milestone 13
    K2): generated last, known units before normalised ones, the real-size step of the uniform scale plus the
    diversity penalty (``diversity_steps``), an audited real product (``real_product: true``) before the others of its
    step, the design preference (``prefs``: 0 shows the design, 1 does not), the audit's vision quality, the texture
    maps, the judges' quality, the face count, aspect error, source order and the id. The first three keys keep their
    Milestone 8 places (tests read ``rank_key(...)[2]`` as the size step)."""
    scales, _ = scale_for(entry, width, depth)
    known = units_known(entry)
    bucket = int(size_error(scales) / SIZE_BUCKET + 1e-9) if known else 0
    bucket += diversity_steps(entry["id"], used)
    real = 0 if entry.get("real_product") is True else 1
    pref = int((prefs or {}).get(entry["id"], 0) or 0)
    vq = vision_quality_of(entry)
    return (1 if entry.get("source") == GENERATED else 0, 0 if known else 1, bucket, real, pref,
            -(vq if vq is not None else VISION_QUALITY_DEFAULT), maps_rank(entry), -quality_of(entry),
            faces_rank(entry), round(C.aspect_error(entry, width, depth), 6), source_rank(entry), entry["id"])


def rank_candidates(candidates: list[dict], width: float, depth: float, used: Optional[dict] = None,
                    prefs: Optional[dict] = None) -> list[dict]:
    return sorted(candidates, key=lambda e: rank_key(e, width, depth, used, prefs))


def ranking_reasons(tried: list[dict], chosen: dict) -> dict:
    """Why the chosen candidate won (the asset's ``ranking`` record)."""
    i = next(n for n, t in enumerate(tried) if t["id"] == chosen["id"])
    size = (f"real size: mean |scale - 1| {chosen['size_error']:.3f} (step {chosen['size_bucket']})"
            if chosen["units_known"] else "units not known (normalised by type): ranked after the real-size models")
    why = [size, f"quality {chosen['quality']:g}", f"aspect error {chosen['aspect_error']:.3f}",
           f"source {chosen['source']}"]
    if chosen.get("diversity_steps"):
        why.insert(1, f"diversity penalty {chosen['diversity_steps']} step(s) (used before in the room or project)")
    if chosen.get("design_pref"):
        why.insert(1, "does not show the design (every model that shows it failed the caps)")
    if chosen.get("vision_quality") is not None:
        why.insert(2, f"audit vision quality {chosen['vision_quality']:g}")
    if chosen.get("faces") is not None:
        why.append(f"faces {chosen['faces']}")
    if chosen["source"] == GENERATED:
        why.insert(0, "generated: no other library model passed the caps")
    passed_over = [{"id": t["id"], "why": "outside the caps (non-uniform {:.1f} %, mean scale {}{})".format(
        (t["non_uniform"] - 1) * 100, t["mean_scale"], "" if t.get("height_ok", True) else ", height outside the range")}
        for t in tried[:i]]
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


UNIFORM_RANGE = (0.85, 1.20)   # a model stretched more than this looks wrong (a 1.1 m tall sofa); M12: was 0.75-1.30


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
              design: Optional[dict] = None, *, mode: str = "commercial", used: Optional[dict] = None,
              style: Optional[dict] = None) -> dict:
    """The ``asset`` dict for one piece (pure: the piece is not modified).

    A candidate is accepted when its uniform scale to the drawn width leaves its depth within ``cap`` of the drawn
    depth (Milestone 13: the layout absorbs the difference) and the scale within ``uniform_range``; otherwise the
    next candidate in rank order (``rank_key``) is tried, then the fallback ladder. Beds without a mattress (unless
    bed frames with a deck) and, with ``style_family``, models of another style are no candidates
    (``usable_candidates``). Milestone 10 / 13: ``design`` (the piece's look) is a preference: the models that show it
    (``look_of``) rank first, the others are still tried and a win of theirs records ``design_not_shown``. An L-shaped
    piece keeps only the models with its chaise side (``chaise_side_candidates``); none left -> the ladder (the
    parametric L builds the drawn side).

    Milestone 12 (docs/milestone12.md §4.8 D14, §6.4; track S) and Milestone 13 (docs/milestone13.md §13.2; track
    T1), in this order:

    1. only usable models in licence ``mode`` (``catalog.usable``: no audit ``removed`` / ``pending``; in
       ``commercial`` mode only commercial-safe entries, in ``relaxed`` mode everything but no-derivatives);
       refused ones are listed under ``excluded``;
    2. the style family, then its fallback chain (``STYLE_FALLBACK``, e.g. mediterranean -> rustic -> classic;
       ``neutral`` models count for every family); a model of a fallback family records ``style_fallback``; a pinned
       model (``asset_pin``, the agent's ``swap_model``) skips the style filter;
    3. the caps, then the relaxed caps (``RELAXED_CAP``, ``RELAXED_RANGE``) while the fitted box stays inside the
       type's documented ranges (``caps_relaxed`` on the asset);
    4. the by-design parametric types (``catalog.BY_DESIGN_PARAMETRIC_TYPES``) go parametric by design; a piece its
       group needs (``group_needs``) takes a model of the nearest related type (``RELATED_TYPES``) first;
    5. else the ladder's step 2, a module builder (``module_plan_for``, track T2: ``method: module``), then step 3,
       the parametric family (``method: parametric``); ``method: none`` only for a piece with ``build: false``.
    Every asset carries ``ladder``, ``licence``, ``licence_flag``, ``commercial_safe`` and ``licence_mode``
    (``_finish``); ``used`` (``{"project": Counter, "room": Counter}`` of asset ids) feeds the diversity penalty.
    """
    mode = C.check_mode(mode)
    ftype = piece["type"]
    if piece.get("build") is False and ftype != "unknown":
        # (an unknown piece keeps its parametric record below: no library search either.)
        # Milestone 13 (16 Oct 2026, found with the HSSD layer): a piece that is not built (not furniture, removed)
        # gets no model at all, not even one that fits: a library asset on it would be credited and counted although
        # nothing is built. Before the HSSD layer no model happened to fit the not-built pieces of the tests.
        why = "the piece is not built (build false): no model is searched"
        return _finish(gap_fit(piece, why, [], [], style_family), mode,
                       [_step("library", "not tried", why), _step(MODULE_METHOD, "not tried", why),
                        _step("parametric", "not tried", why)])
    width, depth = piece["footprint"]["size"]
    if not (width > 0 and depth > 0):
        asset = parametric_fit(piece, f"footprint size {piece['footprint']['size']} is not positive",
                               style_family=style_family)
        return _finish(asset, mode, [_step("parametric", "used", asset["fallback_reason"])])
    pin = piece.get("asset_pin")
    if pin:
        # Milestone 11 (edit_ops swap_model): the agent's model is tried alone first; Milestone 13: without the style
        # filter (the agent's choice is the decision), the caps and the licence mode still apply; when it fails them
        # the normal ranking decides and the asset says so.
        entry = next((e for e in catalog.candidates(ftype) if e.get("id") == pin), None)
        if entry is not None and C.usable(entry, mode):
            pinned = fit_piece(dict(piece, asset_pin=None), _OneModel(catalog, entry), cap, uniform_range, None,
                               design, mode=mode, used=used, style=style)
            if pinned.get("method") == "library":
                pinned["pinned"] = pin
                pinned["style_family"] = style_family
                pinned["pin_skips_style"] = True
                return pinned
        asset = fit_piece(dict(piece, asset_pin=None), catalog, cap, uniform_range, style_family, design, mode=mode,
                          used=used, style=style)
        asset["pin_refused"] = (f"{pin}: not a {ftype} model of the catalogue" if entry is None
                                else f"{pin}: {C.unusable_reason(entry, mode)}" if not C.usable(entry, mode)
                                else f"{pin}: fails the fit rules (caps, height)")
        return asset
    candidates = catalog.candidates(ftype)
    if not candidates:
        if ftype == "unknown":
            asset = parametric_fit(piece, f"type {ftype} is parametric in the catalogue", style_family=style_family)
            return _finish(asset, mode, [_step("parametric", "used", "an unknown piece: the parametric box (not built "
                                                                      "unless typed)")])
        if ftype in catalog.parametric_types:              # Milestone 12: parametric only by design (D14)
            reason = f"type {ftype} is parametric in the catalogue"
        else:
            reason = f"no catalogue entry for type {ftype}"
        return _no_model(piece, catalog, reason, [], [], cap, uniform_range, style_family, mode=mode, used=used,
                         style=style)
    usable, refused = split_usable(candidates, mode)
    if not usable:
        return _no_model(piece, catalog, f"no usable {ftype} model (audit or licence, {mode} mode)", [], refused, cap,
                         uniform_range, style_family, mode=mode, used=used, style=style)
    chain = style_chain(style_family)
    tried, excluded, reasons = [], list(refused), []
    used = dict(used, type=ftype) if used else used            # the diversity penalty knows the piece's type (sets)
    relaxed_caps = _relaxed_caps(cap, uniform_range)
    for relaxed in (False, True):
        if relaxed and (relaxed_caps is None or not tried):
            break               # the caller's caps hold (tightened, or already as loose); or no candidate was tried
        caps = relaxed_caps if relaxed else (cap, uniform_range)
        for fam in chain:
            got = _fit_family(piece, usable, fam, caps[0], caps[1], design, used=used, within_table=relaxed)
            if got.get("method") == "library":
                got["excluded"] = excluded + got.get("excluded", [])
                if fam != style_family:
                    got["style_fallback"] = {"wanted": style_family, "used": fam, "chain": list(chain),
                                             "why": "; ".join(reasons)}
                if relaxed:
                    got["caps_relaxed"] = {"cap": caps[0], "uniform_range": list(caps[1]),
                                           "why": "no model within the caps; the relaxed caps hold inside the type's "
                                                  "documented ranges (docs/milestone13.md §13.2, ladder step 1)"}
                return _finish(got, mode, [_step("library", f"used {got['asset_id']}",
                                                 "relaxed caps inside the documented ranges" if relaxed else None)])
            if relaxed:          # the strict pass said it all: one short line for the relaxed pass
                why = (f"relaxed caps ({round((caps[0] - 1) * 100)} % non-uniform, {caps[1][0]}..{caps[1][1]} mean "
                       f"scale, inside the documented ranges): no {ftype} candidate either")
            else:
                why = got["fallback_reason"]
            reasons.append(why if fam is None else f"{fam}: {why}")
            seen = {t["id"] for t in tried}
            tried += [t for t in got.get("candidates") or [] if t["id"] not in seen]
            known = {x["id"] for x in excluded}
            excluded += [x for x in got.get("excluded") or [] if x["id"] not in known]
    return _no_model(piece, catalog, "; ".join(reasons) or f"no {ftype} model fits", tried, excluded, cap,
                     uniform_range, style_family, mode=mode, used=used, style=style)


def _relaxed_caps(cap: float, uniform_range: tuple[float, float]) -> Optional[tuple[float, tuple[float, float]]]:
    """Ladder step 1b (docs/milestone13.md §13.2): the relaxed caps a call may fall back to, ``(cap, range)`` from
    ``RELAXED_CAP`` / ``RELAXED_RANGE`` widened to the caller's where those are looser; None when the caller
    tightened a cap below the module defaults (its limit holds: a test or a tool asked for exactly that) or when the
    caller's caps are already as loose as the relaxed ones."""
    if (cap < NON_UNIFORM_CAP - 1e-9 or uniform_range[0] > UNIFORM_RANGE[0] + 1e-9
            or uniform_range[1] < UNIFORM_RANGE[1] - 1e-9):
        return None
    r_cap = max(cap, RELAXED_CAP)
    r_range = (min(uniform_range[0], RELAXED_RANGE[0]), max(uniform_range[1], RELAXED_RANGE[1]))
    if r_cap <= cap + 1e-9 and r_range[0] >= uniform_range[0] - 1e-9 and r_range[1] <= uniform_range[1] + 1e-9:
        return None
    return r_cap, r_range


def _fit_family(piece: dict, candidates: list[dict], style_family: Optional[str], cap: float,
                uniform_range: tuple[float, float], design: Optional[dict], *, used: Optional[dict] = None,
                within_table: bool = False) -> dict:
    """The fit of one style family on the usable candidates: the bed rule, the style filter, the chaise side, the
    design as a preference (Milestone 13: models that cannot show it are listed under ``excluded`` with the reason
    and still tried after the ones that can), the rank order (``rank_key`` with the diversity penalty ``used``) and
    the caps: the uniform scale to the drawn width within ``uniform_range``, the depth mismatch within ``cap``, the
    height within the real range; with ``within_table`` the fitted box must also lie inside the type's documented
    ranges (the relaxed caps of the ladder). Returns the library ``asset`` or a parametric record whose
    ``fallback_reason`` says why none fitted."""
    ftype = piece["type"]
    width, depth = piece["footprint"]["size"]
    candidates, excluded, reason = usable_candidates(ftype, candidates, style_family)
    if not candidates:
        return parametric_fit(piece, reason, excluded=excluded, style_family=style_family)
    if piece.get("shape") == "L":
        candidates, side_excluded, side = chaise_side_candidates(candidates, piece.get("chaise_side"))
        excluded += side_excluded
        if not candidates:
            return parametric_fit(piece, f"no {ftype} model with its chaise on the {side} (library models are not "
                                         "mirrored)", excluded=excluded, style_family=style_family)
    looks: dict[str, dict] = {}
    prefs: dict[str, int] = {}
    if design:
        for e in candidates:
            look, why = look_of(e, ftype, design)
            if look is None:
                excluded.append({"id": e["id"], "reason": why, "preference": True})
                prefs[e["id"]] = 1
            else:
                looks[e["id"]] = look
    ordered = rank_candidates(candidates, width, depth, used, prefs)
    tried = []
    heights = real_height_range(ftype)
    for rank, entry in enumerate(ordered, start=1):
        scales, depth_ratio = scale_for(entry, width, depth)
        err = round(C.aspect_error(entry, width, depth), 4)
        mean_scale = round(sum(scales) / 3.0, 4)
        height = round(float(entry["bbox_m"][2]) * scales[2], 4)
        fdepth = fitted_depth(entry, width)
        height_ok = height_fits(height, heights) and working_height_ok(ftype, height)
        accepted = (depth_ratio <= cap + 1e-9 and uniform_range[0] <= mean_scale <= uniform_range[1] and height_ok)
        if accepted and within_table:
            from wenart.furniture import sizes as SZ

            accepted = SZ.real_range(ftype) is not None and SZ.oriented_fits(ftype, [width, fdepth, height], 0.0)
        known = units_known(entry)
        size_err = round(size_error(scales), 4)
        tried.append({"id": entry["id"], "aspect_error": err, "scale": scales, "non_uniform": depth_ratio,
                      "depth_m": fdepth, "mean_scale": mean_scale, "accepted": accepted, "rank": rank,
                      "source": entry.get("source"), "units_known": known, "size_error": size_err,
                      "size_bucket": int(size_err / SIZE_BUCKET + 1e-9) if known else None,
                      "diversity_steps": diversity_steps(entry["id"], used), "design_pref": prefs.get(entry["id"], 0),
                      "quality": quality_of(entry), "vision_quality": vision_quality_of(entry),
                      "faces": faces_of(entry), "height_m": height, "height_ok": height_ok})
        if accepted:
            asset = {
                "library": entry["source"], "asset_id": entry["id"], "licence": entry["licence"],
                "license": entry["licence"], "method": "library", "fit_scale": scales, "scaling": "uniform",
                "bbox_m": [round(width, 4), fdepth, round(entry["bbox_m"][2] * scales[2], 4)],
                "depth_abs_m": round(fdepth - depth, 4),
                "aspect_error": err, "front_axis": entry["front_axis"],
                "up_axis": entry["up_axis"], "origin_offset": list(entry["origin_offset"]),
                "rotation_fix_deg": C.reorient_rotation_deg(entry),
                "front_axis_confidence": entry["front_axis_confidence"], "candidates": tried, "cap": cap,
                "uniform_range": list(uniform_range),
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
            asset["licence_flag"] = C.licence_flag_of(entry)          # Milestone 13: the flag of the entry
            maps = texture_maps_of(entry)
            if maps is not None:
                asset["texture_maps"] = maps
            if faces_of(entry) is not None:
                asset["faces"] = faces_of(entry)
            for key in AUDIT_ASSET_FIELDS:                      # Milestone 12: the audit and its dressing flags
                if key in entry:
                    asset[key] = entry[key]
            if piece["type"] in C.BED_TYPES and not C.has_mattress(entry) and is_bed_frame(entry):
                asset.update(bed_frame_record(entry, width, depth, scales[2]))
                asset["bbox_m"][2] = max(asset["bbox_m"][2], asset["bedding"]["top_m"])
            look = looks.get(entry["id"]) or {}
            for key in ("recolour", "colour_match"):
                if look.get(key):
                    asset[key] = look[key]
            if look.get("tags"):
                asset["material_tags_asked"] = look["tags"]
            if design and prefs.get(entry["id"]):
                asset["design_not_shown"] = {k: design[k] for k in ("material_tags", "fabric_colour", "colour")
                                             if design.get(k)}
                asset["design_not_shown_why"] = next((x["reason"] for x in excluded if x["id"] == entry["id"]), None)
            return asset
    best = min(tried, key=lambda t: t["non_uniform"])
    reason = (f"no {ftype} candidate within {round((cap - 1) * 100)} % non-uniform scale (Milestone 13: the depth "
              f"mismatch of the uniform scale to the drawn width) and {uniform_range[0]}..{uniform_range[1]} mean "
              f"scale (closest: {best['id']} at {round((best['non_uniform'] - 1) * 100, 1)} % non-uniform, mean "
              f"scale {best['mean_scale']})")
    too_tall = [t["id"] for t in tried if not t["height_ok"]]
    if too_tall and heights:
        reason += (f"; {len(too_tall)} fitted outside the real height {heights[0]:g}-{heights[1]:g} m "
                   f"(+-{round(HEIGHT_TOLERANCE * 100)} %, wenart.furniture.sizes)")
        if ftype in WORKING_HEIGHT_TYPES:
            reason += f" or the working height (+-{round(WORKING_HEIGHT_TOL * 100)} % of the product height)"
    if within_table:
        reason += "; the relaxed caps hold only inside the documented ranges"
    return parametric_fit(piece, reason, tried, excluded=excluded, style_family=style_family)


def _step(step: str, result: str, reason: Optional[str] = None) -> dict:
    """One entry of ``asset.ladder`` (docs/milestone13.md §13.2): ``{step, result, reason}``."""
    return {"step": step, "result": result, "reason": reason}


def _finish(asset: dict, mode: str, ladder: list[dict]) -> dict:
    """Milestone 13: the licence fields and the ladder every asset carries (``asset.licence_flag``,
    ``commercial_safe``, ``licence_mode``, ``ladder``); a module or parametric piece is ours (licence ``n/a``, flag
    ``none``), a piece that is not built has nothing to flag."""
    asset["licence_mode"] = mode
    asset["ladder"] = list(asset.get("ladder") or []) + list(ladder)
    if asset.get("method") == "library":
        asset.setdefault("licence_flag", C.licence_flag_of(asset))
        asset["commercial_safe"] = C.commercial_safe(asset)
    else:
        asset.setdefault("licence", PARAMETRIC_LICENCE)
        asset.setdefault("license", PARAMETRIC_LICENCE)
        asset["licence_flag"] = C.NO_FLAG
        asset["commercial_safe"] = True
    return asset


def module_plan_for(piece: dict, style: Optional[dict] = None) -> tuple[Optional[dict], str]:
    """Ladder step 2 (docs/milestone13.md §13.2): ``wenart.blender.modules.module_plan(piece, style)`` (track T2,
    pure) when that module exists and knows a builder for the piece's type; ``(plan, "")`` or ``(None, why)``. The
    import is guarded (the module is built in parallel; a missing one means step 3), and so is a builder error (it
    must not stop the fit: the parametric family follows and the reason is logged)."""
    try:
        from wenart.blender import modules as MOD
    except ImportError as exc:
        return None, f"no module builder (wenart.blender.modules not importable: {exc})"
    fn = getattr(MOD, "module_plan", None)
    if not callable(fn):
        return None, "no module builder (wenart.blender.modules.module_plan missing)"
    try:
        plan = fn(piece, style) if style is not None else fn(piece)
    except Exception as exc:          # noqa: BLE001 - a builder bug is logged, never fatal for the fit
        return None, f"module_plan failed: {type(exc).__name__}: {exc}"
    if not isinstance(plan, dict) or not plan.get("builder"):
        return None, f"no module builder for {piece['type']} (module_plan returned None)"
    return plan, ""


# Fix round after P3 (16-17 Oct 2026, module docstring): the drawn kitchen pieces a kitchen run takes in.
KITCHEN_RUN_HOSTS: tuple[str, ...] = ("kitchen_counter", "kitchen_island")
BUILT_IN_SHARE = 0.60            # a drawn sink or stove with at least this share of its footprint inside a run
BUILT_IN_SINK_TYPES: tuple[str, ...] = ("sink_kitchen",)
RANGE_TYPES: tuple[str, ...] = ("stove",)
PINNED_SINK_GAP_REASON = ("the agent pinned a library model (asset_pin): it stands as drawn in a gap of the run, not "
                          "built in")                   # fix round after P3, part 2


def _usable_footprint(piece: dict) -> bool:
    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else {}
    try:
        return float(fp["size"][0]) > 0 and float(fp["size"][1]) > 0 and len(fp["center"]) >= 2
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def kitchen_built_ins(building: dict) -> dict:
    """The kitchen pre-pass of ``fit_building`` (pure; fix round after P3, module docstring): ``{"hints": {run id:
    module hints}, "sinks": {sink id: run id}}``.

    For every kitchen counter or island with ``build`` not false, the pieces of its level and room with ``build``
    not false and at least ``BUILT_IN_SHARE`` of their footprint inside it (``modules.member_in_run``): the largest
    sink (``BUILT_IN_SINK_TYPES``; not one the agent pinned a model to) gives ``sink_pos_m`` (its centre),
    ``sink_w_m`` (its drawn width along the run) and ``sink_piece``; the stoves (``RANGE_TYPES``) give ``ranges``
    (``{id, type, x0_m, x1_m}``: their drawn span along the run). A piece belongs to one run at most. Without the
    module builders (import guarded, as ``module_plan_for``) nothing is found. Fix round after P3, part 2 (17 Oct
    2026): a pinned sink (``asset_pin``) gives a ``ranges`` entry too (``type: sink_kitchen``, ``reason``): the run
    leaves a gap at its drawn span, where its pinned model stands (it is never in ``sinks``)."""
    out: dict = {"hints": {}, "sinks": {}}
    try:
        from wenart.blender import modules as MOD
    except ImportError:
        return out
    pieces = [p for p in building.get("furniture") or [] if isinstance(p, dict)]
    runs = [p for p in pieces if p.get("type") in KITCHEN_RUN_HOSTS and p.get("build", True) is not False
            and _usable_footprint(p)]
    members = [p for p in pieces if p.get("type") in BUILT_IN_SINK_TYPES + RANGE_TYPES
               and p.get("build", True) is not False and _usable_footprint(p)]
    claimed: set = set()
    for run in runs:
        sinks, ranges = [], []
        for m in members:
            if m.get("id") in claimed or m.get("level_id") != run.get("level_id") \
                    or m.get("room_id") != run.get("room_id"):
                continue
            got = MOD.member_in_run(run, m)
            if got is None or got["share"] < BUILT_IN_SHARE - 1e-9:
                continue
            if m["type"] in BUILT_IN_SINK_TYPES and not m.get("asset_pin"):
                sinks.append((m, got))
            else:
                ranges.append((m, got))         # a stove, or a pinned sink (part 2): a gap, its own model in it
        hints: dict = {}
        if sinks:
            sink, got = max(sinks, key=lambda mg: (float(mg[0]["footprint"]["size"][0])
                                                   * float(mg[0]["footprint"]["size"][1]), str(mg[0]["id"])))
            hints.update(sink_pos_m=[round(float(v), 4) for v in sink["footprint"]["center"][:2]],
                         sink_w_m=got["w_m"], sink_piece=sink["id"])
            out["sinks"][sink["id"]] = run["id"]
            claimed.add(sink["id"])
        if ranges:
            hints["ranges"] = [dict({"id": m["id"], "type": m["type"], "x0_m": got["x0_m"], "x1_m": got["x1_m"]},
                                    **({"reason": PINNED_SINK_GAP_REASON} if m["type"] in BUILT_IN_SINK_TYPES else {}))
                               for m, got in sorted(ranges, key=lambda mg: (mg[1]["x0_m"], str(mg[0]["id"])))]
            claimed.update(m["id"] for m, _got in ranges)
        if hints:
            out["hints"][run["id"]] = hints
    return out


def holds_built_in(run: Optional[dict], piece_id: str) -> bool:
    """True when ``run``'s fitted module plan builds ``piece_id`` into it (``plan["built_ins"]``)."""
    plan = ((run or {}).get("asset") or {}).get("module_plan") or {}
    return any(b.get("id") == piece_id for b in plan.get("built_ins") or [] if isinstance(b, dict))


def built_in_fit(piece: dict, run: dict, mode: str, style_family: Optional[str] = None) -> dict:
    """The asset of a drawn sink built into a kitchen run (fix round after P3): ``method: module``, the run's
    ``asset_id`` (``module:<run type>:kitchen_run``), ``built_in: <run id>``, ours (licence ``n/a``, flag ``none``,
    commercial-safe), by design; ``module_plan`` is only the reference ``{builder, built_into, kind, x_m, w_m}`` (no
    modules: the run's plan builds it, ``parametric.piece_bbox`` keeps the sink's own box); the ladder ends at the
    module step. No library model is searched (none would be built)."""
    plan = (run.get("asset") or {}).get("module_plan") or {}
    record = next((b for b in plan.get("built_ins") or [] if b.get("id") == piece["id"]), {})
    builder = plan.get("builder") or "kitchen_run"
    shift = float(record.get("shift_m") or 0.0)
    why = (f"built into the kitchen run {run['id']}: a {float(record.get('w_m') or 0.0):.2f} m sink unit with the "
           "bowl and the tap at its cutout (the drawn sink lies inside the drawn run)"
           # fix round after P3, part 2: a unit off the drawn centre (at most modules.KITCHEN_END_SHIFT_MAX_M) is named
           + (f"; the unit stands {abs(shift):.2f} m from the drawn sink centre (unit width, run end)"
              if abs(shift) > 0.005 else ""))
    asset = parametric_fit(piece, why, style_family=style_family)
    asset.update({"library": MODULE_METHOD, "method": MODULE_METHOD, "asset_id": f"module:{run['type']}:{builder}",
                  "built_in": run["id"], "by_design": True,
                  "module_plan": {"builder": builder, "built_into": run["id"], "kind": "sink",
                                  "x_m": record.get("x_m"), "w_m": record.get("w_m"),
                                  "shift_m": round(shift, 4)}})
    return _finish(asset, mode, [_step("library", "not tried", why),
                                 _step(MODULE_METHOD, f"built into {run['id']} (sink unit and cutout)", None)])


def module_fit(piece: dict, plan: dict, reason: str, candidates: Optional[list] = None,
               excluded: Optional[list] = None, style_family: Optional[str] = None) -> dict:
    """Ladder step 2: the asset of a piece built from modules (``method: module``, ``module_plan`` for the scene
    builder's ``build_module``; the box from the plan's ``footprint_m`` / ``height_m``). A by-design type (a kitchen
    run, a vanity: ``catalog.BY_DESIGN_PARAMETRIC_TYPES``) is ``by_design`` and, as its parametric twin, a
    ``library_gap`` only when it is a fixture type or models were tried (a counter run is made to the drawing, never
    a gap); every other type is a gap at the module step (listed as built below the library level)."""
    ftype = piece["type"]
    base = parametric_fit(piece, reason, candidates, excluded, style_family)
    fp = plan.get("footprint_m") or piece["footprint"]["size"][:2]
    height = plan.get("height_m") or base["bbox_m"][2]
    products = [str(p) for p in plan.get("products") or []]
    base.update({"library": MODULE_METHOD, "asset_id": f"module:{ftype}:{plan['builder']}", "method": MODULE_METHOD,
                 "bbox_m": [round(float(fp[0]), 4), round(float(fp[1]), 4), round(float(height), 4)],
                 "module_plan": plan})
    by_design = ftype in C.BY_DESIGN_PARAMETRIC_TYPES
    if by_design:
        base["by_design"] = True
    label = split_label(piece, plan)
    if label is not None:
        base["adjusted_by_ai"] = label
    if not by_design or ftype in C.PARAMETRIC_FIXTURE_TYPES or candidates or excluded:
        base["library_gap"] = {"type": ftype, "style": style_family, "step": MODULE_METHOD,
                               "used": f"module builder {plan['builder']} ({len(plan.get('modules') or [])} "
                                       f"module(s){': ' + ', '.join(products) if products else ''})"
                                       + (" (by design)" if by_design else ""),
                               "reason": reason}
    return base


SPLIT_RULE = "module_split"


def split_label(piece: dict, plan: dict) -> Optional[dict]:
    """The ``adjusted_by_ai`` label of a module plan with a ``split`` (``wenart.blender.modules.plan_table_long``: a
    drawn footprint deeper than a real table includes its chairs; pure, None without a split): the reason names the
    drawing error, the table and the chairs built inside the drawn box; ``drawn_footprint`` holds the footprint as
    drawn (the piece's footprint is not changed: the modules sit inside it), ``changed`` is empty for that reason.
    ``fit_building`` copies it onto the piece (``apply_split_label``; CLAUDE.md furniture rules: every change keeps
    the ``drawn_*`` keys and is labelled ``adjusted_by_ai`` with the reason)."""
    split = plan.get("split") if isinstance(plan, dict) else None
    if not isinstance(split, dict):
        return None
    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else {}
    size = [float(v) for v in (fp.get("size") or [])[:2]]
    table = [float(v) for v in (split.get("table_m") or size)[:2]]
    chairs = int(split.get("chairs") or 0)
    why = str(split.get("reason") or "the drawn footprint is deeper than a real table")
    reason = (f"module split: {why}; built as a {table[0]:.2f} x {table[1]:.2f} m table"
              + (f" with {chairs} chairs" if chairs else "")
              + f" inside the drawn {size[0]:.2f} x {size[1]:.2f} m footprint ({plan.get('builder')}); the footprint "
                "stays as drawn, drawn_footprint kept (CLAUDE.md: a table footprint that includes its chairs is a "
                "clear drawing error the AI may fix)")
    return {"reason": reason, "rule": SPLIT_RULE, "changed": {}, "drawn_footprint": copy.deepcopy(fp),
            "split": copy.deepcopy(split)}


def apply_split_label(piece: dict, asset: Optional[dict] = None) -> bool:
    """Label a piece whose fitted ``asset`` (default ``piece["asset"]``) carries a split (``split_label``) in place:
    ``adjusted_by_ai`` with the reason (an earlier label's reason is kept in front, its ``changed`` and bookkeeping
    keys stay), and the ``drawn_*`` keys of ``DRAWN_KEYS`` set where missing. Returns True when the piece was
    labelled. ``wenart.furniture.edit_ops`` may call it after a refit through ``fit_piece``."""
    asset = piece.get("asset") if asset is None else asset
    label = asset.get("adjusted_by_ai") if isinstance(asset, dict) else None
    if not isinstance(label, dict) or label.get("rule") != SPLIT_RULE:
        return False
    old = piece.get("adjusted_by_ai") if isinstance(piece.get("adjusted_by_ai"), dict) else {}
    if old.get("rule") == SPLIT_RULE or SPLIT_RULE in str(old.get("rules") or ""):
        return False                                   # labelled by an earlier fit of the same plan
    for drawn_key, key in DRAWN_KEYS:
        if key in piece:
            piece.setdefault(drawn_key, copy.deepcopy(piece[key]))
    new = {"reason": label["reason"] if not old.get("reason") else f"{old['reason']}; {label['reason']}",
           "changed": dict(old.get("changed") or {}), "rule": SPLIT_RULE, "split": copy.deepcopy(label.get("split"))}
    if old.get("rule") and old["rule"] != SPLIT_RULE:
        new["rules"] = [old["rule"], SPLIT_RULE]       # e.g. a size snap and then the split
    for k in ("round", "log_seq", "model", "snapped_wall", "fix_fixture"):
        if old.get(k) is not None:
            new[k] = old[k]
    piece["adjusted_by_ai"] = new
    return True


HEIGHT_TOLERANCE = 0.15          # = sizes.fits' tolerance: a fitted height this far outside the real range refuses
# Milestone 13 (16 Oct 2026, found by the CPU fit of real04 on the HSSD layer): a uniform scale to the drawn width
# also scales the height. The size table's dining-table range is 0.65-0.92 m (widened by counter-height ABO tables)
# and HEIGHT_TOLERANCE widens it again, so a 2.9 m HSSD table scaled 1.155 to the drawn 3.35 m stood 0.88 m high
# (bar height) and passed. A dining table or a desk is used with chairs, so its working height is fixed: the fitted
# height must stay within WORKING_HEIGHT_TOL of the size table's product height (0.75 m / 0.76 m: 0.69-0.81 m /
# 0.70-0.82 m; common dining and desk heights are 0.72-0.78 m, ABO medians 0.76 / 0.78 m in size_table.yaml).
WORKING_HEIGHT_TYPES: tuple[str, ...] = ("table_dining", "desk")
WORKING_HEIGHT_TOL = 0.08


def working_height_ok(ftype: str, height: float, tol: float = WORKING_HEIGHT_TOL) -> bool:
    """True unless ``ftype`` has a fixed working height (``WORKING_HEIGHT_TYPES``) and ``height`` is more than ``tol``
    away from the size table's product height (always true without a product height)."""
    if ftype not in WORKING_HEIGHT_TYPES:
        return True
    from wenart.furniture import sizes as SZ

    product = (SZ.real_range(ftype) or {}).get("product")
    if not product or len(product) < 3 or not product[2]:
        return True
    return abs(float(height) / float(product[2]) - 1.0) <= tol + 1e-9


def real_height_range(ftype: str) -> Optional[tuple[float, float]]:
    """The type's real height range of the one size table (``wenart.furniture.sizes.real_range``, D23); None when the
    table has no height for it."""
    from wenart.furniture import sizes as SZ

    rng = SZ.real_range(ftype)
    h = (rng or {}).get("height")
    return (float(h[0]), float(h[1])) if h else None


def height_fits(height: float, heights: Optional[tuple[float, float]], tol: float = HEIGHT_TOLERANCE) -> bool:
    """Milestone 12 (§4.8, §6.3): the fitted model's height inside the type's real range (+- ``tol``); always true
    without a range (a bathtub fitted 0.89 m high, a stove 0.54 m: refused, the next model is tried)."""
    if not heights:
        return True
    return heights[0] / (1.0 + tol) - 1e-9 <= float(height) <= heights[1] * (1.0 + tol) + 1e-9


# Milestone 12 (docs/milestone12.md §4.8 D14): the style family fallback chain (each step also takes ``neutral``
# models: ``catalog.styles_match``); logged as ``style_fallback`` on the asset.
STYLE_FALLBACK: dict[str, tuple[str, ...]] = {
    "mediterranean": ("rustic", "classic"), "rustic": ("classic", "mediterranean"), "classic": ("rustic",),
    "industrial": ("modern",), "japandi": ("scandinavian", "minimal"), "scandinavian": ("minimal", "modern"),
    "modern minimal": ("minimal", "modern"), "minimal": ("modern minimal", "modern"),
    "modern": ("modern minimal", "minimal"),
}
# The nearest related type a group may use when its own type has no usable model (§4.8: "a lounge chair for a
# missing armchair"); never for sofas, beds, tables and the bath and kitchen fixtures (a gap instead).
RELATED_TYPES: dict[str, tuple[str, ...]] = {
    "armchair": ("chair",), "chaise": ("armchair",), "ottoman": ("bench",), "bench": ("ottoman",),
    "side_table": ("nightstand",), "nightstand": ("side_table",), "tv_unit": ("sideboard", "dresser"),
    "sideboard": ("tv_unit", "dresser"), "dresser": ("sideboard", "tv_unit"), "console_table": ("sideboard",),
    "shoe_cabinet": ("sideboard", "dresser"), "bookshelf": ("display_cabinet", "tall_cabinet"),
    "display_cabinet": ("bookshelf", "tall_cabinet"), "tall_cabinet": ("wardrobe", "display_cabinet"),
    "wardrobe": ("tall_cabinet",), "bar_stool": ("chair",), "office_chair": ("chair",), "desk": ("console_table",),
    "bunk_bed": ("bed_single",),
}
# Audit fields (track B, contract §13.3) a fitted asset carries: the S6 check and the scene builder read them.
AUDIT_ASSET_FIELDS: tuple[str, ...] = ("audit", "real_product", "has_bedding", "has_cushions", "has_pillows",
                                       "has_mattress", "contact")
NOT_BUILT_METHOD = "none"


def style_chain(style_family: Optional[str]) -> list[Optional[str]]:
    """The families the fit tries in order: the project's, then its ``STYLE_FALLBACK`` chain ([None] without a
    family: every model)."""
    if style_family is None:
        return [None]
    return [style_family] + [f for f in STYLE_FALLBACK.get(style_family, ()) if f != style_family]


def split_usable(candidates: list[dict], mode: str = "commercial") -> tuple[list[dict], list[dict]]:
    """``(usable entries with their audit fixes applied, excluded rows)`` (``catalog.usable`` in licence ``mode``)."""
    usable, refused = [], []
    for e in candidates:
        if C.usable(e, mode):
            usable.append(e)                       # an audit fix is in the fields already
        else:
            refused.append({"id": e["id"], "reason": C.unusable_reason(e, mode)})
    return usable, refused


def group_needs(piece: dict) -> bool:
    """A piece its group needs (§4.8): a member of a functional group (``furniture[].group``, track G) or a piece
    drawn in the documents (CLAUDE.md: drawn furniture is kept)."""
    return bool(isinstance(piece.get("group"), dict) and piece["group"].get("group_id")) or \
        piece.get("source") == "from_documents"


def gap_fit(piece: dict, reason: str, candidates: Optional[list] = None, excluded: Optional[list] = None,
            style_family: Optional[str] = None) -> dict:
    """A piece that is not built (Milestone 13: only one with ``build: false``, not furniture or removed) and has no
    model: ``method: "none"`` and ``library_gap`` (copied onto the piece by ``fit_building``); the parametric box
    stays as ``bbox_m`` for the planners."""
    asset = parametric_fit(piece, reason, candidates, excluded, style_family)
    asset.update({"library": NOT_BUILT_METHOD, "asset_id": f"none:{piece['type']}", "method": NOT_BUILT_METHOD,
                  "library_gap": {"type": piece["type"], "style": style_family, "step": NOT_BUILT_METHOD,
                                  "used": "nothing (not built)", "reason": reason}})
    return asset


def _no_model(piece: dict, catalog, reason: str, tried: list, excluded: list, cap: float,
              uniform_range: tuple[float, float], style_family: Optional[str], *, mode: str = "commercial",
              used: Optional[dict] = None, style: Optional[dict] = None) -> dict:
    """The fallback ladder (docs/milestone13.md §12 D4, §13.2) when no usable model of the piece's type fits:
    step 1 a model of the nearest related type for a piece its group needs (``RELATED_TYPES``); a piece that is not
    built (``build: false``) stops here with ``method: none``; step 2 a module builder (``module_plan_for``, track
    T2); step 3 the parametric family (our parametric fixture for the by-design types, docs/milestone12.md §6.4).
    ``asset.ladder`` logs every step; ``library_gap.step`` names the one used. A drawn anchor is never left out."""
    ftype = piece["type"]
    ladder = [_step("library", "no model", reason)]
    if group_needs(piece):
        for rt in RELATED_TYPES.get(ftype, ()):
            usable, _refused = split_usable(catalog.candidates(rt), mode)
            for fam in style_chain(style_family):
                got = _fit_family(dict(piece, type=rt), usable, fam, cap, uniform_range, None, used=used)
                if got.get("method") == "library":
                    got["related_type"] = rt
                    got["excluded"] = list(excluded) + got.get("excluded", [])
                    got["library_gap"] = {"type": ftype, "style": style_family, "step": "library",
                                          "used": f"related type {rt}: {got['asset_id']}"
                                                  + (f" ({fam} style)" if fam != style_family else ""),
                                          "reason": reason}
                    ladder[-1] = _step("library", f"related type {rt}: {got['asset_id']}", reason)
                    return _finish(got, mode, ladder)
    if piece.get("build") is False:
        asset = gap_fit(piece, reason, tried, excluded, style_family)
        ladder.append(_step(MODULE_METHOD, "not tried", "the piece is not built (build false)"))
        ladder.append(_step("parametric", "not tried", "the piece is not built (build false)"))
        return _finish(asset, mode, ladder)
    plan, why = module_plan_for(piece, style)
    if plan is not None:
        asset = module_fit(piece, plan, reason, tried, excluded, style_family)
        ladder.append(_step(MODULE_METHOD, f"used {plan['builder']}", None))
        return _finish(asset, mode, ladder)
    ladder.append(_step(MODULE_METHOD, "no module builder", why))
    by_design = ftype in C.BY_DESIGN_PARAMETRIC_TYPES
    if by_design:
        fixture = ftype in C.PARAMETRIC_FIXTURE_TYPES or bool(tried or excluded)
        why = (f"{reason}; our parametric {ftype.replace('_', ' ')} (by design, docs/milestone12.md §6.4)"
               if fixture else reason)                        # a counter, island, wall cabinet or stair: as always
        asset = parametric_fit(piece, why, tried, excluded, style_family)
        asset["by_design"] = True
        if fixture:
            asset["library_gap"] = {"type": ftype, "style": style_family, "step": "parametric",
                                    "used": "our parametric fixture (by design)", "reason": reason}
        ladder.append(_step("parametric", "used (by design)", "docs/milestone12.md §6.4: made to the drawing"))
        return _finish(asset, mode, ladder)
    asset = parametric_fit(piece, f"{reason}; the parametric family (ladder step 3, docs/milestone13.md §13.2)",
                           tried, excluded, style_family)
    asset["library_gap"] = {"type": ftype, "style": style_family, "step": "parametric",
                            "used": "parametric family (built below the library level)", "reason": reason}
    ladder.append(_step("parametric", "used", "no library model within the caps and no module builder"))
    return _finish(asset, mode, ladder)


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
                                        # Milestone 10 (docs/milestone10.md §4.6); Milestone 12 (§4.7, §6.4, B7):
                                        # throws, curtains and blinds are our procedural textiles, never a model
                                        "books", "candle", "basket", "tray", "clock",
                                        "sculpture", "plant_large", "pendant_light", "ceiling_light")
PROCEDURAL_DECOR_TYPES: tuple[str, ...] = ("throw", "curtain", "blind")   # wenart.blender.textiles
# Milestone 12 (§4.7, B7): a cushion model keeps its real proportions: scaled uniformly to the cushion's width and
# height (their scales may differ by at most this), its thickness then in CUSHION_THICKNESS_M.
CUSHION_PROPORTION_CAP = 1.10
CUSHION_THICKNESS_M = (0.06, 0.28)
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


def decor_entries(catalog, dtype: str, mode: str = "commercial") -> list[dict]:
    """The catalogue's decor models of ``dtype``, sorted by id: ``catalog.decor_candidates(dtype)`` when the
    catalogue has that method (Milestone 8 library), plus the decor entries of ``catalog.decor`` and
    ``catalog.entries`` of that type (``decor_type_of``); duplicates by id once; only the ones usable in licence
    ``mode`` (Milestone 13)."""
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
        if e.get("id") and not e.get("parametric") and (e.get("gltf") or e.get("glb")) and e.get("bbox_m") \
                and C.usable(e, mode):                            # Milestone 12 / 13: audited, usable in the mode
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
    if dtype == "cushion":                        # Milestone 12 (B7): real proportions, never stretched
        if len(item["size"]) < 3 or not item["size"][2]:
            return None                           # a lying cushion (ottoman, bench): the procedural one
        height = float(item["size"][2])
        sw, sh = width / bw, height / bh
        if max(sw, sh) / min(sw, sh) > CUSHION_PROPORTION_CAP + 1e-9:
            return None
        s = (sw + sh) / 2.0
        if not CUSHION_THICKNESS_M[0] - 1e-9 <= bd * s <= CUSHION_THICKNESS_M[1] + 1e-9:
            return None
        return {"fit_scale": [round(s, 4)] * 3, "bbox_m": [round(bw * s, 4), round(bd * s, 4), round(bh * s, 4)],
                "front_axis": front, "turned_deg": 0.0, "target": "within", "non_uniform": round(max(sw, sh)
                                                                                                 / min(sw, sh), 4)}
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


def fit_decor_item(item: dict, catalog, style_family: Optional[str] = None, *,
                   mode: str = "commercial") -> Optional[dict]:
    """``asset`` for a decor item (docs/milestone8.md §4): one of the catalogue's decor models of its type
    and of the style family or neutral (``decor_entries``, ``decor_styles_match``) that fits the item
    (``_decor_fit``), picked deterministically by the host id (``pick_index`` of ``decor_pick_key``); None
    (parametric decor; no wall art) when there is none. Blender scales the model to ``bbox_m``. Milestone 13:
    only models usable in licence ``mode``; the asset carries the licence fields (``_finish``)."""
    mode = C.check_mode(mode)
    dtype = item.get("type", "")
    if dtype not in DECOR_LIBRARY_TYPES or not item.get("size") or len(item["size"]) < 2:
        return None
    styled = [e for e in decor_entries(catalog, dtype, mode) if decor_styles_match(e, style_family)
              and C.contact_fits(e, dtype)]               # Milestone 12: the audited contact suits the type
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
                 "other_style": len(decor_entries(catalog, dtype, mode)) - len(styled)},
    }
    if asset["library"] != "polyhaven" and entry.get("glb"):
        asset.update({k: entry[k] for k in GLB_ASSET_FIELDS if k in entry})
        asset["unit_scale"] = float(entry.get("unit_scale") or 1.0)
    else:
        asset["gltf"] = entry["gltf"]
    asset["licence_flag"] = C.licence_flag_of(entry)
    return _finish(asset, mode, [_step("library", f"used {entry['id']}", None)])


def fabric_colour_of(piece: dict, style: Optional[dict]) -> tuple[Optional[str], Optional[str]]:
    """``(colour, where it came from)`` of an upholstered piece (Milestone 13, B1 of docs/milestone13.md §1.8): its
    ``design.fabric_colour`` (layout stage), else the style's ``furniture.by_type[type].fabric_colour``, else
    ``furniture.fabric_colour``; ``(None, None)`` for other types or without a colour. The completion stage writes
    ``design.material_tags`` only, so the brief's "light grey fabric sofa" reaches the fit through this."""
    if piece.get("type") not in UPHOLSTERED_TYPES:
        return None, None
    design = piece.get("design") if isinstance(piece.get("design"), dict) else {}
    if design.get("fabric_colour"):
        return str(design["fabric_colour"]), "furniture.design (layout stage)"
    profile = style[0] if isinstance(style, list) and style else style
    furniture = (profile or {}).get("furniture") if isinstance(profile, dict) else None
    furniture = furniture if isinstance(furniture, dict) else {}
    by_type = (furniture.get("by_type") or {}).get(piece.get("type")) or {}
    if isinstance(by_type, dict) and by_type.get("fabric_colour"):
        return str(by_type["fabric_colour"]), f"style.json furniture.by_type.{piece.get('type')}"
    if furniture.get("fabric_colour"):
        return str(furniture["fabric_colour"]), "style.json furniture.fabric_colour"
    return None, None


def design_of(piece: dict, style: Optional[dict]) -> dict:
    """The look the fit honours for a piece (Milestone 10): its ``furniture.design`` (layout stage), else the
    ``style.json`` fallback of ``wenart.blender.looks.design_for``; {} without a style. Milestone 13: an upholstered
    piece whose design lacks the fabric colour gets the style's (``fabric_colour_of``), so the brief's colour is a
    preference of the fit and travels to the asset."""
    if style is None and not isinstance(piece.get("design"), dict):
        return {}
    from wenart.blender import looks as LK

    design = dict(LK.design_for(piece, style or {})[0])
    colour, source = fabric_colour_of(piece, style)
    if colour and not design.get("fabric_colour"):
        design["fabric_colour"] = colour
        design["fabric_colour_source"] = source
    return design


# --------------------------------------------------------------------------
# Milestone 13 (K1, D5): the size snap before the fit
# --------------------------------------------------------------------------

SNAP_RULE = "size_snap"
DRAWN_KEYS = (("drawn_type", "type"), ("drawn_footprint", "footprint"), ("drawn_front_deg", "front_deg"),
              ("drawn_height", "height"))


def snap_allowed(settings) -> tuple[bool, str]:
    """Whether the size snap runs under the brief's furnished-room settings (``wenart.furniture.complete.Settings``
    or a dict with ``furnished_rooms`` / ``furnished_rooms_keep_size``): off with ``keep`` or ``keep_size`` (user OK
    D5 of 12 Oct 2026); on without settings (the defaults: complete)."""
    if settings is None:
        return True, "no brief: furnished_rooms complete (default), size snap on"
    mode = getattr(settings, "mode", None)
    keep_size = getattr(settings, "keep_size", None)
    if isinstance(settings, dict):
        mode = settings.get("furnished_rooms", mode)
        keep_size = settings.get("furnished_rooms_keep_size", keep_size)
    if str(mode or "complete") == "keep":
        return False, "furnished_rooms: keep: drawn sizes stay as drawn (size snap off)"
    if keep_size:
        return False, "furnished_rooms_keep_size: drawn sizes stay as drawn (size snap off)"
    return True, f"furnished_rooms: {mode or 'complete'}, size snap on"


def snap_candidate(piece: dict) -> Optional[str]:
    """Why a piece is not snapped (None when it is): only drawn furniture that is built, with a type the size table
    knows, and no fixed equipment (the ingest's fixed rule and the agent's ``fix_fixture`` resize those)."""
    if piece.get("source") != "from_documents":
        return "not drawn"
    if piece.get("build") is False:
        return "not built"
    ftype = piece.get("type")
    if ftype in (None, "unknown"):
        return "no type"
    if C.by_design_parametric(piece):
        return "fixed equipment or a by-design type (the ingest rule and fix_fixture resize those)"
    from wenart.furniture import sizes as SZ

    if SZ.real_range(ftype) is None:
        return f"no size row for {ftype}"
    return None


def apply_size_snap(piece: dict, part: Optional[tuple] = None) -> Optional[dict]:
    """Snap a drawn piece's footprint to the nearest real product when it lies outside its type's product range
    (``wenart.furniture.sizes.snap_size``), in place; returns the ``size_snap`` record or None when nothing changed.
    The width change keeps the centre; a depth change keeps the back edge where it was (the piece stays against its
    wall; without a front the centre stays). The piece keeps ``drawn_type``, ``drawn_footprint``, ``drawn_front_deg``,
    ``drawn_height`` and is labelled ``adjusted_by_ai`` with the reason (CLAUDE.md furniture rules).

    ``part`` (build round 3, the split before the snap): the ``(w, d)`` the snap judges instead of the footprint,
    the table part of a drawn footprint that includes its chairs (``split_plan_first``); then only the width and
    the height of the piece may change, the drawn depth stays (it holds the chairs) and the record says ``part``."""
    from wenart.furniture import sizes as SZ

    if snap_candidate(piece) is not None:
        return None
    fp = piece["footprint"]
    w, d = (float(v) for v in fp["size"][:2])
    height = piece.get("height") if isinstance(piece.get("height"), (int, float)) else None
    judged = (w, d) if part is None else (float(part[0]), float(part[1]))
    snap = SZ.snap_size(piece["type"], judged, height)
    if not snap["changed"]:
        return None
    before = copy.deepcopy(fp)
    nw, nd = (round(float(v), 4) for v in snap["footprint"])
    if part is not None:
        nd = round(d, 4)                     # the drawn depth stays: the chairs are in it (the split's business)
    cx, cy = (float(v) for v in fp["center"])
    front = piece.get("front_deg")
    if abs(nd - d) > 1e-9 and isinstance(front, (int, float)):
        shift = (nd - d) / 2.0
        cx += shift * math.cos(math.radians(float(front)))
        cy += shift * math.sin(math.radians(float(front)))
    piece["footprint"] = dict(fp, center=[round(cx, 4), round(cy, 4)], size=[nw, nd])
    changed = {"footprint": before}
    if snap["height"] is not None and height is not None and abs(float(snap["height"]) - height) > 1e-9:
        changed["height"] = piece.get("height")
        piece["height"] = round(float(snap["height"]), 4)
    for drawn_key, key in DRAWN_KEYS:
        # the values before the snap (review fix of 15 Oct 2026: the footprint and the height were replaced above, so
        # the drawn height must come from ``changed``, not from the piece, or it would hold the product height)
        value = before if key == "footprint" else changed["height"] if key == "height" and "height" in changed \
            else piece.get(key)
        piece.setdefault(drawn_key, copy.deepcopy(value))
    old = piece.get("adjusted_by_ai") if isinstance(piece.get("adjusted_by_ai"), dict) else {}
    merged_changed = dict(old.get("changed") or {})
    for k, v in changed.items():
        merged_changed.setdefault(k, v)
    if part is None:
        reason = (f"size snap: the drawn {piece['type']} {w:.2f} x {d:.2f} m is outside its product range "
                  f"({snap['reason']}); nearest real product {snap['product']} (CLAUDE.md: a drawn size outside its "
                  "type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct "
                  "2026)")
    else:
        reason = (f"size snap of the table part: the {piece['type']} {judged[0]:.2f} x {judged[1]:.2f} m inside the "
                  f"drawn {w:.2f} x {d:.2f} m footprint is outside its product range ({snap['reason']}); nearest real "
                  f"product {snap['product']}; the drawn depth stays, it holds the chairs (CLAUDE.md: a drawn size "
                  "outside its type's product range is snapped to the nearest real product before the fit; user OK "
                  "D5 of 12 Oct 2026; the split decides first, build round 3)")
    label = {"reason": reason if not old.get("reason") else f"{old['reason']}; {reason}", "changed": merged_changed,
             "rule": SNAP_RULE}
    if old.get("rule") and old["rule"] != SNAP_RULE:
        label["rules"] = list(old.get("rules") or [old["rule"]]) + [SNAP_RULE]   # e.g. the split, then the snap
    for k in ("round", "log_seq", "model", "snapped_wall", "fix_fixture", "split"):
        if old.get(k) is not None:
            label[k] = copy.deepcopy(old[k])
    piece["adjusted_by_ai"] = label
    record = {"drawn": [w, d] + ([height] if height is not None else []),
              "snapped": [nw, nd] + ([piece["height"]] if "height" in changed else ([height] if height is not None
                                                                                     else [])),
              "product": snap["product"], "reason": snap["reason"]}
    if part is not None:
        record["part"] = [round(judged[0], 4), round(judged[1], 4)]
    piece["size_snap"] = record
    return record


def split_plan_first(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """Build round 3 (lead decision on the K1 / T2 leftover): the module plan with a ``split`` of a drawn table whose
    footprint is deeper than a real table (``wenart.blender.modules.plan_table_long``: deeper than
    ``TABLE_DEPTH_MAX_M``, 1.20 m, the footprint includes its chairs), decided BEFORE the size snap; None for every
    other piece (no snap candidate, no module builder, no split). The size snap must not snap such a footprint to a
    product depth first: that would erase the chairs.

    A footprint whose depth is its long side (``size[1] > size[0]``) is not split first: ``plan_table_long`` reads
    ``size[1]`` as the depth with no orientation check (``wenart.blender.modules``, owner T2), so a long table drawn
    turned would be taken for a short table with its chairs; such a piece keeps the round-2 order (the snap, then
    the ladder). None of the 131 dining tables of the committed buildings is drawn so (checked 16 Oct 2026)."""
    if snap_candidate(piece) is not None:
        return None
    size = (piece.get("footprint") or {}).get("size") or []
    if len(size) < 2 or float(size[1]) > float(size[0]) + 1e-9:
        return None
    plan, _why = module_plan_for(piece, style)
    if not isinstance(plan, dict) or not isinstance(plan.get("split"), dict):
        return None
    return plan


def apply_split_then_snap(piece: dict, style: Optional[dict] = None) -> Optional[tuple[dict, Optional[dict]]]:
    """The split-before-snap order of build round 3 for one drawn piece, in place: when ``split_plan_first`` finds a
    split, the piece is labelled ``adjusted_by_ai`` (rule ``module_split``, ``drawn_footprint`` and the other
    ``drawn_*`` keys kept, the footprint unchanged) and only then the table part is judged by the size snap
    (``apply_size_snap(part=...)``: the width and the height may take a real product, the depth stays as drawn).
    After such a snap the plan is made again on the snapped piece; the label keeps ``rule: module_split`` (the
    split is why the piece changed) with ``rules = [module_split, size_snap]``, its ``split`` is the new plan's and
    its reason says what is built (``split_snap_reason``), after any earlier label's reason. Returns ``(plan,
    size_snap record or None)``, or None when the piece has no split (the caller snaps as usual)."""
    plan = split_plan_first(piece, style)
    if plan is None:
        return None
    prior = copy.deepcopy(piece.get("adjusted_by_ai")) if isinstance(piece.get("adjusted_by_ai"), dict) else {}
    apply_split_label(piece, {"adjusted_by_ai": split_label(piece, plan)})
    table = plan["split"].get("table_m") or piece["footprint"]["size"][:2]
    drawn_fp = copy.deepcopy(piece["footprint"])
    record = apply_size_snap(piece, part=(float(table[0]), float(table[1])))
    if record is None:
        return plan, None
    again, _why = module_plan_for(piece, style)
    if isinstance(again, dict) and isinstance(again.get("split"), dict):
        plan = again
    label = piece["adjusted_by_ai"]
    label["rule"] = SPLIT_RULE
    label["rules"] = [r for r in (prior.get("rules") or ([prior["rule"]] if prior.get("rule") else []))
                      if r not in (SPLIT_RULE, SNAP_RULE)] + [SPLIT_RULE, SNAP_RULE]
    label["split"] = copy.deepcopy(plan["split"])
    text = split_snap_reason(drawn_fp, piece, plan, record)
    label["reason"] = text if not prior.get("reason") else f"{prior['reason']}; {text}"
    return plan, record


def split_module_fit(piece: dict, fitted: dict, style: Optional[dict], style_family: Optional[str],
                     mode: str) -> dict:
    """Build round 3 (review of item 2): the asset of a piece the split labelled first (``apply_split_then_snap``)
    when the fit picked something other than its module plan with the split. Why: the label says the module builder
    makes the table and its chairs inside the drawn footprint, and the lead decision is that the split decides; a
    library table at the full footprint depth (a square table model scaled to a deep square footprint, a deep
    model from a later catalogue) would build the table alone, erase the chairs and contradict the label (the fit
    CLI's ``assert_only_assets_changed`` refuses a split label without the plan's split). Today's catalogue never
    gets here (no library table reaches a footprint deeper than 1.35 m within the caps, checked on 16 Oct 2026 over
    1.2-3.6 m widths and 1.25-2.2 m depths); the guard keeps it so when the catalogue grows. Returns ``fitted``
    unchanged when it already carries the split or when the module plan no longer splits."""
    if ((fitted.get("module_plan") or {}).get("split")) or fitted.get("method") == "none":
        return fitted
    plan, _why = module_plan_for(piece, style)
    if not isinstance(plan, dict) or not isinstance(plan.get("split"), dict):
        return fitted
    picked = fitted.get("asset_id") or fitted.get("method") or "the fit"
    reason = (f"the drawn footprint holds the table and its chairs (module split, decided before the size snap, "
              f"build round 3): {picked} would build the table alone at the full footprint depth")
    asset = module_fit(piece, plan, reason, fitted.get("candidates") or [], fitted.get("excluded") or [],
                       style_family)
    asset["split_over"] = picked
    return _finish(asset, mode, [_step("library", f"not used: {picked}", reason),
                                 _step(MODULE_METHOD, f"used {plan['builder']}", "the module split decides")])


def split_snap_reason(drawn_fp: dict, piece: dict, plan: dict, record: dict) -> str:
    """The ``adjusted_by_ai`` reason of a drawn table split first and then snapped (``apply_split_then_snap``): the
    drawing error (the footprint holds the chairs), the table part outside the product range and the product it
    took, the footprint that results (the drawn depth kept) and what the module builder makes in it."""
    split = plan.get("split") or {}
    dw, dd = (float(v) for v in drawn_fp["size"][:2])
    nw, nd = (float(v) for v in piece["footprint"]["size"][:2])
    part = record.get("part") or [dw, dd]
    table = [float(v) for v in (split.get("table_m") or [nw, nd])[:2]]
    chairs = int(split.get("chairs") or 0)
    why = str(split.get("reason") or "the drawn footprint is deeper than a real table")
    return (f"module split, then the size snap of the table part: {why}; the table part {part[0]:.2f} x "
            f"{part[1]:.2f} m is outside its product range ({record['reason']}; the product: "
            f"{record['product']}), so the footprint is {nw:.2f} x {nd:.2f} m (drawn {dw:.2f} x {dd:.2f} m; the depth "
            f"stays, it holds the chairs); built as a {table[0]:.2f} x {table[1]:.2f} m table"
            + (f" with {chairs} chairs" if chairs else "")
            + f" inside it ({plan.get('builder')}); drawn_footprint kept (CLAUDE.md: a table footprint that includes "
              "its chairs is a clear drawing error the AI may fix, and a drawn size outside its type's product range "
              "is snapped to the nearest real product; user OK D5 of 12 Oct 2026; the split decides first, build "
              "round 3)")


def resolve_mode(building: dict, brief: Optional[dict], mode: Optional[str]) -> tuple[str, str]:
    """``(mode, source)`` of a fit run: the given ``mode``, else the building's ``project.licence_mode`` (a later
    stage never reads the brief), else ``catalog.licence_mode_from(brief)`` (env > brief > commercial)."""
    if mode is not None:
        return C.check_mode(mode), "given to the fit"
    project = building.get("project") if isinstance(building.get("project"), dict) else {}
    if project.get("licence_mode") in C.LICENCE_MODES:
        return str(project["licence_mode"]), "building project.licence_mode"
    return C.licence_mode_from(brief)


def fit_building(building: dict, catalog: C.Catalog, cap: float = NON_UNIFORM_CAP,
                 style_family: Optional[str] = None, style: Optional[dict] = None, *, mode: Optional[str] = None,
                 brief: Optional[dict] = None, settings=None, snap: Optional[bool] = None) -> dict:
    """A deep copy of ``building`` with ``asset`` set on every furniture piece and on every decor item (a library
    decor model, or None: parametric decor, no wall art). ``style_family`` (refit only): the library style filter of
    ``fit_piece`` and ``fit_decor_item``; ``style`` (refit only, Milestone 10): the profile whose looks the fit
    honours (``design_of``).

    Milestone 13: ``mode`` None = ``project.licence_mode`` of the building, else the brief's (``resolve_mode``); the
    fit writes ``project.licence_mode`` and ``project.licence_mode_source``. Before the fit the drawn sizes outside
    their product range are snapped (``apply_size_snap``; ``snap`` None = by the brief's furnished-room settings,
    ``settings`` a ``complete.Settings`` or the ``brief``'s values; off with keep / keep_size). The use counters of
    the diversity penalty run over the pieces in file order (per room and per project). Nothing else changes
    (``assert_only_assets_changed``)."""
    mode, mode_source = resolve_mode(building, brief, mode)
    fitted = copy.deepcopy(building)
    project = fitted.get("project") if isinstance(fitted.get("project"), dict) else None
    if project is None:
        project = fitted["project"] = {}
    project["licence_mode"] = mode
    project["licence_mode_source"] = mode_source
    if settings is None and brief is not None and "values" in brief:
        # the two keys of wenart.furniture.complete.Settings the snap needs, read from the brief here so that the fit
        # stage's import closure stays free of the layout code (wenart/run/stages.py FIT_CODE)
        from wenart import brief as BR

        settings = {"furnished_rooms": BR.value(brief, "furnished_rooms", "complete"),
                    "furnished_rooms_keep_size": BR.value(brief, "furnished_rooms_keep_size", False)}
    snap_on, snap_why = (snap, "given to the fit") if snap is not None else snap_allowed(settings)
    project["size_snap"] = {"on": bool(snap_on), "why": snap_why}
    snapped = []
    split_first = []
    if snap_on:
        for piece in fitted.get("furniture", []):
            # Build round 3 (lead decision): a drawn table footprint deeper than a real table is a table with its
            # chairs (the module plan's split decides, ``split_plan_first``); it is labelled first and only its
            # table part is judged by the snap, so the snap never erases the chairs.
            split = apply_split_then_snap(piece, style)
            if split is not None:
                split_first.append(piece["id"])
                record = split[1]
            else:
                record = apply_size_snap(piece)
            if record is not None:
                snapped.append(piece["id"])
        if split_first:
            project["size_snap"]["split_first"] = split_first
    used_project: Counter = Counter()
    used_rooms: dict[str, Counter] = {}
    # fix round after P3 (module docstring): the drawn sinks and stoves inside the kitchen runs
    kitchen = kitchen_built_ins(fitted)
    by_id = {p.get("id"): p for p in fitted.get("furniture", [])}

    def fit_one(piece: dict, built_into: Optional[dict] = None) -> None:
        frozen = {k: copy.deepcopy(piece.get(k)) for k in FROZEN_KEYS}
        room = str(piece.get("room_id") or "")
        used = {"project": used_project, "room": used_rooms.setdefault(room, Counter())}
        if built_into is not None:
            asset = built_in_fit(piece, built_into, mode, style_family)
        else:
            design = design_of(piece, style) if (style is not None or piece.get("design")) else None
            hints = kitchen["hints"].get(piece.get("id"))
            # the run's hints reach its plan on a copy: the building piece never gets module_hints (FROZEN_KEYS,
            # assert_only_assets_changed); the asset keeps them beside the plan (furniture.module_plan_of)
            target = dict(piece, module_hints={**(piece.get("module_hints") or {}), **hints}) if hints else piece
            asset = fit_piece(target, catalog, cap=cap, style_family=style_family, design=design or None, mode=mode,
                              used=used, style=style)
            if hints and asset.get("method") == MODULE_METHOD:
                asset["module_hints"] = copy.deepcopy(hints)
            if piece.get("id") in split_first:
                # review of build round 3 item 2: a piece the split labelled is built by its module plan (the split
                # decides; a library table at the full depth would erase the chairs the label names)
                asset = split_module_fit(piece, asset, style, style_family, mode)
            colour, source = fabric_colour_of(piece, style)
            if colour:
                asset["fabric_colour"] = colour
                asset["fabric_colour_source"] = source
        piece["asset"] = asset
        apply_split_label(piece, asset)                 # a table footprint split into table + chairs (modules)
        if asset.get("method") == "library":
            used_project[asset["asset_id"]] += 1
            used["room"][asset["asset_id"]] += 1
        # Milestone 12 (§4.8, §6.4): the library gap (type, style, what was used instead) is a finding on the piece
        if asset.get("library_gap"):
            piece["library_gap"] = dict(asset["library_gap"])
        else:
            piece.pop("library_gap", None)
        for key in FROZEN_KEYS:
            if frozen.get(key) != piece.get(key):  # cannot happen; guards future edits
                raise RuntimeError(f"fit changed {key} of {piece['id']}")

    deferred = []
    for piece in fitted.get("furniture", []):
        if piece.get("id") in kitchen["sinks"]:
            deferred.append(piece)             # after its run: built in only when the run's plan holds it
            continue
        fit_one(piece)
    for piece in deferred:
        run = by_id.get(kitchen["sinks"][piece["id"]])
        fit_one(piece, run if holds_built_in(run, piece["id"]) else None)
    for item in fitted.get("decor") or []:
        item["asset"] = fit_decor_item(item, catalog, style_family=style_family, mode=mode)
    return fitted


PROJECT_FIT_KEYS = ("licence_mode", "licence_mode_source", "size_snap")
SNAP_PIECE_KEYS = ("size_snap", "adjusted_by_ai", "footprint", "height") + tuple(k for k, _ in DRAWN_KEYS)


def assert_only_assets_changed(before: dict, after: dict) -> None:
    """Raise AssertionError unless ``after`` equals ``before`` except for ``furniture[].asset`` and
    ``decor[].asset`` (Milestone 12: and ``furniture[].library_gap``; Milestone 13: the fit's ``project`` keys and,
    on a piece with a ``size_snap``, the snapped footprint and height with their labels, checked here: the snapped
    size is the footprint's, the drawn footprint is the one before; a module split keeps the footprint, and, split
    first in build round 3, the snap of its table part changes the width only)."""
    a, b = copy.deepcopy(before), copy.deepcopy(after)
    for piece_a, piece_b in zip(a.get("furniture", []), b.get("furniture", [])):
        label = piece_b.get("adjusted_by_ai") if isinstance(piece_b.get("adjusted_by_ai"), dict) else {}
        split = label.get("rule") == SPLIT_RULE and label != piece_a.get("adjusted_by_ai")
        snap = piece_b.get("size_snap")
        new_snap = bool(snap) and snap != piece_a.get("size_snap")
        if split:
            # a module split (build round 2): the footprint is unchanged, the label and the drawn_* keys are new.
            # Build round 3 (split before the snap): the snap of the table part (``size_snap.part``) may change the
            # width only; the drawn depth (it holds the chairs), the centre and the rotation stay.
            fa, fb = piece_a.get("footprint") or {}, piece_b.get("footprint") or {}
            if new_snap and snap.get("part"):
                if (round(float(fb["size"][1]), 4) != round(float(fa["size"][1]), 4)
                        or fb.get("center") != fa.get("center") or fb.get("rotation_deg") != fa.get("rotation_deg")):
                    raise AssertionError(f"{piece_b.get('id')}: the snap of a split table's part may change its "
                                         "width only (the drawn depth holds the chairs)")
            elif fb != fa:
                raise AssertionError(f"{piece_b.get('id')}: a module split must not change the footprint")
            if piece_b.get("drawn_footprint") != piece_a.get("drawn_footprint", piece_a.get("footprint")):
                raise AssertionError(f"{piece_b.get('id')}: drawn_footprint does not hold the drawn footprint")
            if not label.get("reason") or not ((piece_b.get("asset") or {}).get("module_plan") or {}).get("split"):
                raise AssertionError(f"{piece_b.get('id')}: a split piece needs adjusted_by_ai with a reason and the "
                                     "plan's split")
        if split and not new_snap:
            for key in ("adjusted_by_ai",) + tuple(k for k, _ in DRAWN_KEYS):
                piece_a.pop(key, None)
                piece_b.pop(key, None)
        if new_snap:
            if [round(float(v), 4) for v in piece_b["footprint"]["size"][:2]] != [round(float(v), 4)
                                                                                 for v in snap["snapped"][:2]]:
                raise AssertionError(f"{piece_b.get('id')}: size_snap.snapped is not the footprint size")
            if piece_b.get("drawn_footprint") != piece_a.get("drawn_footprint", piece_a.get("footprint")):
                raise AssertionError(f"{piece_b.get('id')}: drawn_footprint does not hold the footprint before the snap")
            if not (piece_b.get("adjusted_by_ai") or {}).get("reason"):
                raise AssertionError(f"{piece_b.get('id')}: a snapped piece needs adjusted_by_ai with a reason")
            for key in SNAP_PIECE_KEYS:
                piece_a.pop(key, None)
                piece_b.pop(key, None)
    for doc in (a, b):
        for piece in doc.get("furniture", []):
            piece.pop("asset", None)
            piece.pop("library_gap", None)
        for item in doc.get("decor") or []:
            item.pop("asset", None)
        project = doc.get("project")
        if isinstance(project, dict):
            for key in PROJECT_FIT_KEYS:
                project.pop(key, None)
            if not project and "project" not in before:
                doc.pop("project")
    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
        raise AssertionError("fit changed something other than furniture[].asset, decor[].asset, the size snaps and "
                             "project.licence_mode")


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
    gaps: list[str] = []
    style_fallbacks: list[str] = []
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
        if asset.get("library_gap"):                                  # Milestone 12 (§6.4)
            gaps.append(f"- {piece['id']} ({piece['type']}, style {asset['library_gap'].get('style')}): "
                        f"{asset['library_gap'].get('used')}; {asset['library_gap'].get('reason')}")
        if asset.get("style_fallback"):
            sf = asset["style_fallback"]
            style_fallbacks.append(f"- {piece['id']} ({piece['type']}): {asset['asset_id']} of style {sf['used']} "
                                   f"(wanted {sf['wanted']}; chain {' -> '.join(str(f) for f in sf['chain'])})")
        if asset["method"] == NOT_BUILT_METHOD:
            pass
        elif asset["method"] in ("parametric", MODULE_METHOD):
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
    not_built = sum(1 for p in pieces if (p.get("asset") or {}).get("method") == NOT_BUILT_METHOD)
    lines.append(f"Project: {project_id}; {len(pieces)} pieces, "
                 f"{len(pieces) - len(fallbacks) - len(missing) - not_built} library fits, {len(fallbacks)} parametric "
                 f"fallbacks" + (f", {not_built} library gaps (not built)" if not_built else "") +
                 f"{', ' + str(len(missing)) + ' without fit' if missing else ''}. "
                 f"Non-uniform scale cap {round((NON_UNIFORM_CAP - 1) * 100)} %. Footprints, types, rotations, rooms "
                 f"and statuses are as in the building JSON (fitting never changes them).")
    if style_note:
        lines += ["", f"Library style filter: {style_note}"]
    if isinstance(project, dict) and project.get("licence_mode"):
        lines += ["", f"Licence mode (Milestone 13): {project['licence_mode']} "
                      f"({project.get('licence_mode_source') or 'source not recorded'}); "
                      f"{'commercial-safe entries only' if project['licence_mode'] == 'commercial' else 'non-commercial, share-alike, research-only, regional and tool_nc entries allowed (no-derivatives never)'}"]
    flagged_assets = sorted({(p["asset"]["asset_id"], p["asset"].get("licence_flag"))
                             for p in pieces if p.get("asset") and p["asset"].get("method") == "library"
                             and p["asset"].get("commercial_safe") is False}
                            | {(d["asset"]["asset_id"], d["asset"].get("licence_flag"))
                               for d in building.get("decor") or [] if d.get("asset")
                               and d["asset"].get("commercial_safe") is False})
    lines += ["", f"commercial-safe: {'yes' if not flagged_assets else 'no (flagged assets: ' + ', '.join(f'{a} [{f}]' for a, f in flagged_assets) + ')'}"]
    lines += ["", "| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | "
              "scale x / y / z | aspect err | height (m) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"] + rows
    snaps = [p for p in pieces if p.get("size_snap")]
    if snaps:
        lines += ["", "## Size snaps (Milestone 13: drawn sizes outside the product range, adjusted_by_ai)", ""]
        lines += [f"- {p['id']} ({p['type']}): {' x '.join(f'{v:.2f}' for v in p['size_snap']['drawn'][:2])} -> "
                  f"{' x '.join(f'{v:.2f}' for v in p['size_snap']['snapped'][:2])} m, {p['size_snap']['product']}; "
                  + (f"the table part {' x '.join(f'{v:.2f}' for v in p['size_snap']['part'])} m of a footprint "
                     "split into table + chairs (the depth stays); " if p['size_snap'].get('part') else "")
                  + f"{p['size_snap']['reason']}" for p in snaps]
    below = [(p["id"], p["type"], p["asset"]["method"], (p.get("library_gap") or {}).get("used"))
             for p in pieces if p.get("asset") and p["asset"].get("method") in (MODULE_METHOD, "parametric")
             and p["type"] not in C.BY_DESIGN_PARAMETRIC_TYPES + ("unknown",) and not p["asset"].get("by_design")]
    if below:
        lines += ["", "## Built below the library level (Milestone 13 ladder: module or parametric family; close "
                      "the gap with a real model)", ""]
        lines += [f"- {pid} ({ftype}): {method}: {used}" for pid, ftype, method, used in below]
    built_ins = [(p["id"], p["type"], p["asset"]["built_in"], float((p["asset"].get("module_plan") or {}).get("shift_m")
                                                                     or 0.0))
                 for p in pieces if (p.get("asset") or {}).get("built_in")]
    run_gaps = [(p["id"], g) for p in pieces for g in ((p.get("asset") or {}).get("module_plan") or {}).get("gaps") or []]
    if built_ins or run_gaps:                         # fix round after P3 (module docstring; part 2: shifts, reasons)
        lines += ["", "## Kitchen runs (drawn sinks built in, gaps for drawn stoves and sinks)", ""]
        lines += [f"- {pid} ({ftype}): built into the kitchen run {rid} (its sink unit, bowl and tap; not built "
                  "again)" + (f"; the sink unit stands {abs(shift):.2f} m from the drawn centre" if abs(shift) > 0.005
                              else "") for pid, ftype, rid, shift in built_ins]
        lines += [f"- {rid}: a {float(g.get('w_m') or 0.0):.2f} m gap for the drawn {g.get('type') or 'stove'} "
                  f"{g.get('id')} (no base unit, plinth or worktop there"
                  + (f"; {g['reason']}" if g.get("reason") else "") + ")" for rid, g in run_gaps]
    lines += ["", "## Parametric fallbacks", "", "(Milestone 13: the module builders of the ladder's step 2 are "
              "listed here too; the method column says which)"]
    if fallbacks:
        lines += [f"- {pid} ({ftype}): {reason}" for pid, ftype, reason in fallbacks]
    else:
        lines.append("- none")
    if gaps:
        lines += ["", "## Library gaps (docs/milestone12.md §6.4: no audited model; what was used instead)", ""] + gaps
    if style_fallbacks:
        lines += ["", "## Style fallbacks (§4.8)", ""] + style_fallbacks
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

def polyhaven_size_of(asset: dict, default: str = "1k") -> str:
    """The Poly Haven file size a fitted asset needs (Milestone 13 round 3, A1's ask): the size of the ``.gltf`` the
    scene builder loads (``asset["gltf"]`` = the catalogue entry's ``models/<id>/<id>_<size>.gltf``; pod P2 relinked
    87 entries to ``2k``), else the asset's ``resolution``, else ``default`` (the Milestone 4-12 ``1k``). A fetch at
    any other size would rewrite the asset manifest entry away from the file the build loads."""
    name = Path(str(asset.get("gltf") or "")).name
    stem = name[:-len(".gltf")] if name.endswith(".gltf") else ""
    size = stem.rsplit("_", 1)[-1] if "_" in stem else ""
    if size[:-1].isdigit() and size.endswith("k"):
        return size
    return str(asset.get("resolution") or default)


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
                size = polyhaven_size_of(asset) if asset["library"] == "polyhaven" else "1k"
                M.fetch_model(asset_id, assets_dir, size=size, source=asset["library"], licence=asset["licence"],
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


def project_dir_of(building: dict, given: Optional[str] = None) -> Optional[Path]:
    """The project folder whose ``brief.yaml`` the fit reads: ``given`` (``--project``), else the building's
    ``project.source_folder`` when that folder exists (relative to the working directory, as the jobs run), else
    None (no brief: the defaults)."""
    if given:
        return Path(given)
    project = building.get("project") if isinstance(building.get("project"), dict) else {}
    folder = project.get("source_folder")
    if isinstance(folder, str) and folder.strip() and Path(folder).is_dir():
        return Path(folder)
    return None


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
    parser.add_argument("--licence-mode", default=None, choices=list(C.LICENCE_MODES),
                        help="Milestone 13: the library licence mode (default: the building's project.licence_mode, "
                             "else env WENART_LICENCE_MODE, else the brief's library.licence_mode, else commercial)")
    parser.add_argument("--project", default=None,
                        help="the project folder with brief.yaml (default: the building's project.source_folder when "
                             "it exists): the licence mode and the furnished_rooms settings of the size snap")
    args = parser.parse_args(argv)

    from wenart import brief as BR
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
    project_dir = project_dir_of(building, args.project)
    brief = BR.load_brief(project_dir) if project_dir is not None else None
    fitted = fit_building(building, catalog, style_family=family, style=profile if isinstance(profile, dict) else None,
                          mode=args.licence_mode, brief=brief)
    project = fitted.get("project") or {}
    print(f"licence mode: {project.get('licence_mode')} ({project.get('licence_mode_source')}); size snap "
          f"{'on' if (project.get('size_snap') or {}).get('on') else 'off'} ({(project.get('size_snap') or {}).get('why')}"
          f"{'; brief ' + str(project_dir) if project_dir is not None else '; no brief'})")
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
