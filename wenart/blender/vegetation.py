"""Vegetation of the site: trees, hedges and grass (Milestone 13, docs/milestone13.md §13.2, track T6; CLAUDE.md
vegetation and site rules, user OK of 12 Oct 2026).

What: ``tree_object(species, height_m, seed, near_camera)`` makes one tree of a species at a height: the library's
model of the species when one fits (``library_plant``, ``site_models.plant_model``; 24 Oct 2026), else near the
cameras a Poly Haven CC0 photoscanned model (``POLYHAVEN_MODELS``) instanced from one import (a collection
instance per tree: the mesh is loaded once), elsewhere a species-look tree from the Sapling Tree Gen add-on
(``bpy.ops.curve.tree_add`` with the add-on's own preset and our size, shape and leaf settings: its ``rect`` leaf quads
in its ``leaves`` mesh object take our leaf-card material; the add-on is GPL and runs as an installed program,
nothing of it is copied here), and when neither is available a trunk with a
leaf-card crown from geometry nodes (``crown_plan``) or, for a palm, a trunk with frond cards. ``hedge_object(hedge)``
fills the hedge volume (its box core following the ground) with leaf cards by geometry nodes (Distribute Points on
Faces, Instance on Points). ``grass_patch(polygon, density)`` scatters grass clumps over the lawn near the cameras
(the Poly Haven clump when the assets hold it, else crossed grass cards) and ``lawn_relief`` gives the far lawn a
gentle displacement. ``SPECIES`` names every species the site may infer (``site.species_for``) with its sources,
crown shape and colour. Never a primitive sphere or cone: every tree, shrub, hedge and lawn is a real model or
generated geometry with a leaf texture.

Why: real04's 101 drawn tree symbols (r 0.36 m) were built as 100 four-metre ellipsoid "lollipops" and real02's
inferred trees as 5.6 m spheres (docs/milestone13.md §1.7). The user's rule (12 Oct 2026): every tree, shrub,
hedge and lawn is a real model or generated geometry with leaf textures, never a primitive; species not named in the
documents are inferred (``site.climate_of`` / ``site.species_for``) and named in the report.

How: the pure parts (``species_record``, ``hero_model``, ``sapling_overrides``, ``hedge_plan``, ``crown_plan``,
``palm_plan``, ``leaf_mask_points``) run without Blender and are tested on the CPU (tests/test_m13_site.py); the
``bpy`` parts build the objects (tests/gpu/test_m13_site.py on the pod; verified in the bpy 5.2.2 LTS module during
the build, 15 Oct 2026). Node and property names come from the Blender 5.2 LTS manual and the 5.2.2 Python API:
``GeometryNodeDistributePointsOnFaces`` (Density, Seed; Points, Normal, Rotation), ``GeometryNodeInstanceOnPoints``
(Points, Instance, Rotation, Scale), ``GeometryNodeObjectInfo`` (As Instance), ``FunctionNodeRandomValue``,
``FunctionNodeEulerToRotation`` / ``FunctionNodeRotateRotation``, ``GeometryNodeJoinGeometry``; the Principled BSDF's
``Thin Wall`` input ("useful for modeling thin structures, such as papers, leaves, and window sheets", 5.2 manual)
and ``Alpha``; the Displace modifier with a Clouds texture. Assets: the Poly Haven models and the ambientCG leaf
atlases are read from the assets folder (``WENART_ASSETS``, the scene's ``wenart_assets_dir`` or the default
folders) through the manifest ``wenart.assets`` writes (``python -m wenart.assets models fetch --ids ...`` and
``fetch.fetch_texture``; ``scripts/pod_setup_vegetation.sh`` runs them); nothing is downloaded here. Every object
records ``wenart_veg_method`` (``library`` | ``polyhaven`` | ``sapling`` | ``cards`` | ``palm``), ``wenart_species``,
``wenart_asset`` and the licence for the scene manifest and ATTRIBUTION.md.
"""
from __future__ import annotations

import ast
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Callable, Optional, Sequence

NEAR_CAMERA_M = 25.0                 # a tree this close to the building (the cameras stand around it) is a hero
GRASS_DENSITY_NEAR = 4.0             # grass clumps per m² on the lawn near the cameras
# Leaf cards (round 3, pod P1 of 15 Oct 2026, docs/milestone13.md §14.3 rows 'hedge' and 'sapling'): real02 ext_1
# 'hedge' and real04 ext_1 'hedge' showed the hedges as boxes of yellow-green dots. The round-1 numbers behind that:
# 60 cards/m² of 0.16 x 0.22 m cards times the species' card_scale (boxwood 0.45: a 0.07 x 0.10 m card; cherry laurel
# 0.9) put 0.17 (boxwood) to 0.68 (cherry laurel) expected opaque layers over the box core, when a leaf-atlas card is
# opaque over about 40 % of its area (LEAF_ATLAS_OPAQUE): 16-50 % of the core was covered, the rest showed as the
# dark core between pale cards (real02 boundary hedges: 1,260 cards on 12 m of boxwood; real04 hedge_001: 4,880 cards
# on 25.5 m of cherry laurel). The density now follows a cover target: HEDGE_COVER_LAYERS expected opaque layers over
# the hull for every species (``hedge_density``: LEAF_CARDS_PER_M2 / card_scale²), 87 % covered, the dark core as
# the shadow in the gaps (real02 boxwood 12 m: 10,888 cards; real04 hedge_001: 10,534 cards; 1 quad each, instanced).
LEAF_CARD_M = (0.20, 0.24)           # a leaf card: width, height (the whole atlas tile: a cluster of leaves)
LEAF_ATLAS_OPAQUE = 0.40             # the opaque share of a leaf-atlas card (assumed for the ambientCG LeafSets)
HEDGE_COVER_LAYERS = 2.0             # expected opaque layers over a hedge hull (1 - e^-2 = 87 % covered)
CROWN_COVER_LAYERS = 1.2             # per crown shell (two shells: 2.4 layers in projection)
LEAF_CARDS_PER_M2 = 105.0            # = HEDGE_COVER_LAYERS / (0.20 x 0.24 m² x LEAF_ATLAS_OPAQUE) at card_scale 1
CROWN_CARDS_PER_M2 = 62.0            # = CROWN_COVER_LAYERS / (0.20 x 0.24 m² x LEAF_ATLAS_OPAQUE); round 1: 35
HEDGE_CARD_TILT_DEG = 45.0           # random tilt of a hedge card off the hull normal (round 1: 35°)
HEDGE_CARD_SCALE = (0.75, 1.25)      # random uniform scale of a hedge card
# The leaf material's colour (P1 'hedge' and 'base' rows: pale yellow-green cards): the atlas colour is multiplied by
# the species colour x LEAF_TINT_GAIN at full factor (round 1: factor 0.5 with gain 2.2 kept the atlas' own pale
# tone); the translucent share of a backlit card drops from 0.25 to LEAF_TRANSLUCENT.
LEAF_TINT_FACTOR = 1.0
LEAF_TINT_GAIN = 1.6
LEAF_TRANSLUCENT = 0.15
# Sapling trees (P1 real02 ext_1 'sapling': bare branches). Round 1 asked the add-on for 'dFace' leaves (our card
# instanced on 0.017 m faces, scaled by the face size x 10: 3 cm leaves, invisible) and parked the card 1 m under the
# leaves object (a face instance keeps the child's offset). Round 3 asks for 'rect' leaves: the add-on's own leaf
# quads (leafScale metres tall, leafScaleX wide, UV layer 'leafUV' 0..1 over the quad; utils.genLeafMesh and addTree
# of sapling_tree_gen 0.3.7) in its 'leaves' mesh object, parented to the tree, which then takes the leaf-card
# material (the atlas colour and opacity). SAPLING_LEAF_M is the leaf quad's size: an atlas tile is a cluster of
# leaves, so 0.22 m (x the species' card_scale) stands for a leaf cluster, not one leaf.
SAPLING_LEAF_M = 0.22
SAPLING_LEAF_SCALE_V = 0.25          # random size variation of the leaf quads (the add-on's leafScaleV, 0..1)
SAPLING_LEAVES_DEFAULT = 25          # the add-on's own default of 'leaves' per branch (a preset without one)
GRASS_CARD_M = (0.30, 0.28)
HERO_MAX_PER_SPECIES = 12            # collection instances share one mesh; this caps the render memory per species
ASSET_CANDIDATES = ("/workspace/assets", "assets")
SAPLING_DIR_ENV = "WENART_SAPLING_DIR"
SAPLING_MODULES = ("bl_ext.user_default.sapling_tree_gen", "bl_ext.blender_org.sapling_tree_gen",
                   "sapling_tree_gen", "add_curve_sapling")
# The nine presets of the Sapling Tree Gen add-on (its presets folder; 0.3.5 bundled source and the 0.3.7
# extension, checked 12 Oct 2026).
SAPLING_PRESETS = ("callistemon", "douglas_fir", "japanese_maple", "quaking_aspen", "small_maple", "small_pine",
                   "weeping_willow", "white_birch", "willow")
# The top of each preset's tree over its ``scale`` (leaves included) and its width over the scale, measured in bpy
# 5.2.2 LTS with the 0.3.7 extension at scale 10, seeds 0 and 1 (15 Oct 2026, scratchpad verify): the first guess
# of ``sapling_overrides``; the built tree is then measured and scaled to the drawn height exactly (``_tree_sapling``).
SAPLING_TOP_PER_SCALE = {"callistemon": 1.04, "douglas_fir": 1.04, "japanese_maple": 1.33, "quaking_aspen": 1.16,
                         "small_maple": 1.26, "small_pine": 1.09, "weeping_willow": 1.03, "white_birch": 1.27,
                         "willow": 1.04}
SAPLING_WIDTH_PER_SCALE = {"callistemon": 0.80, "douglas_fir": 0.52, "japanese_maple": 1.41, "quaking_aspen": 0.51,
                           "small_maple": 1.13, "small_pine": 0.77, "weeping_willow": 0.78, "white_birch": 1.01,
                           "willow": 0.71}
# The add-on's crown shapes (its ``shapeList3`` enum: the value is the string the operator takes).
SAPLING_SHAPES = {"conical": "0", "spherical": "1", "hemispherical": "2", "cylindrical": "3",
                  "tapered_cylindrical": "4", "flame": "5", "inverse_conical": "6", "tend_flame": "7"}

# Poly Haven CC0 models (https://polyhaven.com/license: "You can use our assets for any purpose"); every id, name,
# height (the API's dimensions z, mm -> m) and polycount read from https://api.polyhaven.com/info/<id> on
# 15 Oct 2026. Downloaded by ``python -m wenart.assets models fetch --ids <id> --size 2k`` into
# ``<assets>/models/<id>/<id>_2k.gltf`` (wenart/assets/models.py).
POLYHAVEN_MODELS = {
    "island_tree_01": {"name": "Island Tree 01", "height_m": 5.03, "polycount": 3729692, "kind": "tree"},
    "island_tree_02": {"name": "Island Tree 02", "height_m": 3.41, "polycount": 1762064, "kind": "tree"},
    "island_tree_03": {"name": "Island Tree 03", "height_m": 2.62, "polycount": 4760490, "kind": "tree"},
    "tree_small_02": {"name": "Tree Small 02", "height_m": 4.65, "polycount": 4652585, "kind": "tree"},
    "jacaranda_tree": {"name": "Jacaranda Tree", "height_m": 19.83, "polycount": 312356, "kind": "tree"},
    "fir_sapling_medium": {"name": "Fir Sapling Medium", "height_m": 9.16, "polycount": 2308249, "kind": "tree"},
    "searsia_lucida": {"name": "Searsia Lucida", "height_m": 2.34, "polycount": 841648, "kind": "shrub"},
    "searsia_burchellii": {"name": "Searsia Burchellii", "height_m": 3.25, "polycount": 1427042, "kind": "shrub"},
    "othonna_cerarioides": {"name": "Othonna Cerarioides", "height_m": 1.97, "polycount": 651641, "kind": "shrub"},
    "grass_medium_02": {"name": "Grass Medium 02", "height_m": 1.45, "polycount": 1043926, "kind": "grass"},
    "grass_bermuda_01": {"name": "Grass Bermuda 01", "height_m": 1.06, "polycount": 223596, "kind": "grass"},
}
POLYHAVEN_LICENCE = "CC0"
POLYHAVEN_LICENCE_URL = "https://polyhaven.com/license"
# ambientCG CC0 leaf atlases (https://ambientcg.com: "All assets are released under the Creative Commons CC0
# license"); ids checked on the API v2 on 15 Oct 2026. Fetched by ``wenart.assets.fetch.fetch_texture`` (Color,
# NormalGL, Roughness; the Opacity map is not extracted by that fetcher yet, so the cards use a procedural leaf mask).
LEAF_ATLASES = {"broadleaf": "LeafSet027", "oak": "LeafSet012", "maple": "LeafSet016"}
LEAF_LICENCE = "CC0"

# Species the site infers (site.SPECIES_BY_CLIMATE) and the documents may name. source.polyhaven: the hero model
# near the cameras (an inferred look when the species has no CC0 scan: no CC0 olive, cypress, plane, citrus or palm
# exists, docs/milestone13.md §2.2); source.sapling: the add-on preset for the species-look tree elsewhere, with
# the crown shape and our overrides; crown: round | spreading | columnar | umbrella | conical | palm | shrub |
# hedge; colour: linear RGB of the foliage; overshoot: the preset's crown height over its trunk scale (1.15-1.66 per
# preset, measured in bpy 5.2.2 on 12 Oct 2026; used to hit the drawn height).
SPECIES = {
    "olive": {"source": {"polyhaven": "island_tree_02", "sapling": "small_maple"}, "crown": "round",
              "shape": "hemispherical", "colour": (0.30, 0.38, 0.26), "overshoot": 1.35, "leaf": "broadleaf",
              "levels": 3, "width_factor": 0.9, "note": "no CC0 olive scan: a round broadleaf stands in (inferred look)"},
    "stone_pine": {"source": {"polyhaven": None, "sapling": "small_pine"}, "crown": "umbrella",
                   "shape": "inverse_conical", "colour": (0.07, 0.16, 0.06), "overshoot": 1.2, "leaf": "broadleaf",
                   "levels": 3, "width_factor": 0.8, "trunk_share": 0.5, "note": "umbrella crown on a tall trunk"},
    "plane": {"source": {"polyhaven": "jacaranda_tree", "sapling": "quaking_aspen"}, "crown": "spreading",
              "shape": "spherical", "colour": (0.22, 0.40, 0.14), "overshoot": 1.45, "leaf": "maple",
              "levels": 3, "width_factor": 0.8, "note": "no CC0 plane scan: a large broadleaf stands in (inferred look)"},
    "cypress": {"source": {"polyhaven": None, "sapling": "small_pine"}, "crown": "columnar",
                "shape": "tapered_cylindrical", "colour": (0.06, 0.14, 0.06), "overshoot": 1.15, "leaf": "broadleaf",
                "levels": 2, "width_factor": 0.22, "note": "columnar: a narrow tapered crown"},
    "palm": {"source": {"polyhaven": None, "sapling": None}, "crown": "palm", "shape": None,
             "colour": (0.18, 0.36, 0.12), "overshoot": 1.0, "leaf": "broadleaf", "levels": 1, "width_factor": 0.6,
             "note": "no CC0 palm and no Sapling palm: a trunk with frond cards"},
    "oleander": {"source": {"polyhaven": "searsia_lucida", "sapling": None}, "crown": "shrub", "shape": None,
                 "colour": (0.16, 0.30, 0.12), "overshoot": 1.0, "leaf": "broadleaf", "levels": 1, "width_factor": 1.0,
                 "note": "shrub: a leaf-card ball, the Poly Haven shrub near the cameras (inferred look)"},
    "birch": {"source": {"polyhaven": "island_tree_03", "sapling": "white_birch"}, "crown": "round",
              "shape": "spherical", "colour": (0.30, 0.48, 0.16), "overshoot": 1.4, "leaf": "broadleaf",
              "levels": 3, "width_factor": 0.7, "note": "white birch preset"},
    "maple": {"source": {"polyhaven": "island_tree_02", "sapling": "small_maple"}, "crown": "round",
              "shape": "spherical", "colour": (0.20, 0.38, 0.12), "overshoot": 1.35, "leaf": "maple",
              "levels": 3, "width_factor": 0.9, "note": "small maple preset"},
    "oak": {"source": {"polyhaven": "island_tree_01", "sapling": "small_maple"}, "crown": "spreading",
            "shape": "hemispherical", "colour": (0.17, 0.33, 0.11), "overshoot": 1.35, "leaf": "oak",
            "levels": 3, "width_factor": 1.0, "note": "no oak preset: the maple preset with a broad crown (inferred look)"},
    "conifer": {"source": {"polyhaven": "fir_sapling_medium", "sapling": "douglas_fir"}, "crown": "conical",
                "shape": "conical", "colour": (0.08, 0.18, 0.08), "overshoot": 1.25, "leaf": "broadleaf",
                "levels": 3, "width_factor": 0.5, "note": "douglas fir preset"},
    "jacaranda": {"source": {"polyhaven": "jacaranda_tree", "sapling": "quaking_aspen"}, "crown": "spreading",
                  "shape": "spherical", "colour": (0.25, 0.42, 0.16), "overshoot": 1.45, "leaf": "broadleaf",
                  "levels": 3, "width_factor": 0.9, "note": "the Poly Haven jacaranda scan"},
    "generic_broadleaf": {"source": {"polyhaven": "island_tree_02", "sapling": "small_maple"}, "crown": "round",
                          "shape": "spherical", "colour": (0.20, 0.36, 0.12), "overshoot": 1.35, "leaf": "broadleaf",
                          "levels": 3, "width_factor": 0.9, "note": "a broadleaf tree of no named species"},
    "privet_shrub": {"source": {"polyhaven": "searsia_burchellii", "sapling": None}, "crown": "shrub", "shape": None,
                     "colour": (0.14, 0.28, 0.10), "overshoot": 1.0, "leaf": "broadleaf", "levels": 1,
                     "width_factor": 1.0, "note": "shrub: a leaf-card ball, the Poly Haven bush near the cameras"},
    # hedges (leaf-card volumes; the Poly Haven library has no hedge model)
    "boxwood": {"source": {"polyhaven": None, "sapling": None}, "crown": "hedge", "shape": None,
                "colour": (0.14, 0.30, 0.10), "overshoot": 1.0, "leaf": "broadleaf", "levels": 0, "width_factor": 1.0,
                "card_scale": 0.45, "note": "small dense leaves"},
    "cherry_laurel": {"source": {"polyhaven": None, "sapling": None}, "crown": "hedge", "shape": None,
                      "colour": (0.10, 0.26, 0.08), "overshoot": 1.0, "leaf": "broadleaf", "levels": 0,
                      "width_factor": 1.0, "card_scale": 0.9, "note": "large glossy leaves (Turkish 'taflan')"},
    "privet": {"source": {"polyhaven": None, "sapling": None}, "crown": "hedge", "shape": None,
               "colour": (0.16, 0.32, 0.12), "overshoot": 1.0, "leaf": "broadleaf", "levels": 0, "width_factor": 1.0,
               "card_scale": 0.6, "note": "a common clipped hedge"},
    "hornbeam": {"source": {"polyhaven": None, "sapling": None}, "crown": "hedge", "shape": None,
                 "colour": (0.22, 0.40, 0.14), "overshoot": 1.0, "leaf": "broadleaf", "levels": 0,
                 "width_factor": 1.0, "card_scale": 0.7, "note": "a tall clipped hedge"},
    "cypress_hedge": {"source": {"polyhaven": None, "sapling": None}, "crown": "hedge", "shape": None,
                      "colour": (0.07, 0.15, 0.07), "overshoot": 1.0, "leaf": "broadleaf", "levels": 0,
                      "width_factor": 1.0, "card_scale": 0.5, "note": "a tall dark conifer hedge"},
}
TREE_SPECIES = tuple(k for k, v in SPECIES.items() if v["crown"] != "hedge")
HEDGE_SPECIES = tuple(k for k, v in SPECIES.items() if v["crown"] == "hedge")


# --------------------------------------------------------------------------
# Pure parts
# --------------------------------------------------------------------------

# Milestone 13 (T6): a row of tree symbols is a hedge (CLAUDE.md vegetation rules, user OK of 12 Oct 2026).
HEDGE_MIN_COUNT = 5                   # at least this many symbols in a row
HEDGE_MAX_RADIUS_M = 0.6              # symbols larger than this are trees, never a hedge
HEDGE_PITCH_FACTOR = 1.5              # the pitch between neighbours is at most this x the diameter
HEDGE_RADIUS_TOL_M = 0.01             # "equal" radii
HEDGE_MAX_TURN_DEG = 60.0             # a gentle polyline: the row may turn this much between two steps
HEDGE_SIMPLIFY_M = 0.15               # the polyline keeps the symbol centres within this of the drawn row
# The height class by the symbol radius (a trimmed hedge: the drawn width says how it is kept); the heights are
# assumed (no section draws a hedge) and listed as inferred.
HEDGE_HEIGHT_M = {"low": 0.6, "mid": 1.2, "high": 1.8}
HEDGE_CLASS_RADIUS_M = ((0.30, "low"), (0.45, "mid"), (HEDGE_MAX_RADIUS_M, "high"))


def hedge_height_class(radius_m: float) -> str:
    """The height class of a hedge from its symbol radius: ``low`` (r <= 0.30 m), ``mid`` (<= 0.45 m), ``high``."""
    for limit, cls in HEDGE_CLASS_RADIUS_M:
        if radius_m <= limit + 1e-9:
            return cls
    return "high"


def _circle_record(c, k: int) -> Optional[dict]:
    """``{"id", "centre", "radius"}`` of a tree symbol in the sheets format (``points`` / ``radius_m``, the
    evidence entity as the id), the building format (``center`` / ``size``, its ``id``) or a plain
    ``{"center", "radius_m"}``; None when it has no centre or radius."""
    if not isinstance(c, dict):
        return None
    centre = c.get("center") or c.get("centre") or ((c.get("points") or [None])[0])
    if not centre or len(centre) < 2:
        return None
    r = c.get("radius_m")
    if r is None and c.get("size"):
        r = float(max(c["size"][:2])) / 2.0
    if r is None or float(r) <= 0:
        return None
    cid = c.get("id")
    if cid is None:
        ev = c.get("evidence") or []
        cid = (ev[0].get("entity") if ev and isinstance(ev[0], dict) else None) or f"symbol_{k}"
    return {"id": str(cid), "centre": (float(centre[0]), float(centre[1])), "radius": float(r), "index": k}


def _simplify(points: list, tol: float) -> list:
    """Douglas-Peucker on a polyline (pure)."""
    if len(points) <= 2:
        return list(points)
    a, b = points[0], points[-1]
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    length = math.hypot(bx - ax, by - ay)
    best, best_d = 0, -1.0
    for i in range(1, len(points) - 1):
        px, py = points[i]
        if length < 1e-9:
            d = math.hypot(px - ax, py - ay)
        else:
            d = abs((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / length
        if d > best_d:
            best, best_d = i, d
    if best_d > tol:
        left = _simplify(points[:best + 1], tol)
        right = _simplify(points[best:], tol)
        return left[:-1] + right
    return [a, b]


def hedge_rows(circles) -> list[dict]:
    """Rows of tree symbols that are hedges (pure; Milestone 13 T6, docs/milestone13.md §13.2): ``[{"polyline",
    "radius_m", "pitch_m", "count", "height_class", "height_m", "width_m", "length_m", "symbol_ids",
    "symbol_indices"}]``.

    ``circles``: tree symbols as the sheets reader lists them (``points`` / ``radius_m`` / ``evidence``), as the
    building's site decor (``center`` / ``size`` / ``id``) or as ``{"center", "radius_m"}``. A hedge is a chain of
    >= ``HEDGE_MIN_COUNT`` symbols of equal radius (``HEDGE_RADIUS_TOL_M``) <= ``HEDGE_MAX_RADIUS_M`` in which
    every step to the next symbol is at most ``HEDGE_PITCH_FACTOR`` x the diameter and turns at most
    ``HEDGE_MAX_TURN_DEG`` from the step before (a line or a gentle polyline; an L-corner starts a new hedge).
    Chains are walked from their ends (the symbols with one neighbour) to the nearest unvisited neighbour; a symbol
    belongs to one hedge. The polyline runs through the symbol centres, simplified within ``HEDGE_SIMPLIFY_M``;
    ``width_m`` is the diameter, ``height_m`` / ``height_class`` by ``hedge_height_class`` (assumed)."""
    recs = [r for r in (_circle_record(c, k) for k, c in enumerate(circles or [])) if r is not None
            and r["radius"] <= HEDGE_MAX_RADIUS_M + 1e-9]
    if len(recs) < HEDGE_MIN_COUNT:
        return []
    # groups of equal radius
    recs.sort(key=lambda r: r["radius"])
    groups: list[list[dict]] = []
    for r in recs:
        if groups and abs(groups[-1][0]["radius"] - r["radius"]) <= HEDGE_RADIUS_TOL_M:
            groups[-1].append(r)
        else:
            groups.append([r])
    out = []
    for group in groups:
        if len(group) < HEDGE_MIN_COUNT:
            continue
        radius = sum(r["radius"] for r in group) / len(group)
        reach = HEDGE_PITCH_FACTOR * 2.0 * radius
        n = len(group)
        neigh: list[list[tuple[float, int]]] = [[] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                d = math.dist(group[i]["centre"], group[j]["centre"])
                if 1e-6 < d <= reach + 1e-9:
                    neigh[i].append((d, j))
                    neigh[j].append((d, i))
        for lst in neigh:
            lst.sort()
        used = [False] * n
        # ends first (one neighbour), then the rest by neighbour count: a row is walked from its end
        order = sorted(range(n), key=lambda i: (len(neigh[i]) != 1, len(neigh[i]), i))
        for start in order:
            if used[start] or not neigh[start]:
                continue
            chain = [start]
            used[start] = True
            prev_dir = None
            cur = start
            while True:
                nxt = None
                for d, j in neigh[cur]:
                    if used[j]:
                        continue
                    a, b = group[cur]["centre"], group[j]["centre"]
                    step = ((b[0] - a[0]) / d, (b[1] - a[1]) / d)
                    if prev_dir is not None:
                        cos = max(-1.0, min(1.0, step[0] * prev_dir[0] + step[1] * prev_dir[1]))
                        if math.degrees(math.acos(cos)) > HEDGE_MAX_TURN_DEG + 1e-9:
                            continue
                    nxt = (j, step)
                    break
                if nxt is None:
                    break
                cur, prev_dir = nxt
                used[cur] = True
                chain.append(cur)
            if len(chain) < HEDGE_MIN_COUNT:
                for i in chain:                       # a short run stays trees (another chain may still take them)
                    used[i] = False
                used[start] = True                    # ... but never walk from this start again
                continue
            pts = [group[i]["centre"] for i in chain]
            steps = [math.dist(pts[k], pts[k + 1]) for k in range(len(pts) - 1)]
            poly = _simplify(pts, HEDGE_SIMPLIFY_M)
            cls = hedge_height_class(radius)
            out.append({"polyline": [[round(x, 4), round(y, 4)] for x, y in poly],
                        "radius_m": round(radius, 4), "width_m": round(2.0 * radius, 4),
                        "pitch_m": round(sum(steps) / len(steps), 4), "count": len(chain),
                        "length_m": round(sum(steps), 3), "height_class": cls, "height_m": HEDGE_HEIGHT_M[cls],
                        "symbol_ids": [group[i]["id"] for i in chain],
                        "symbol_indices": [group[i]["index"] for i in chain]})
    out.sort(key=lambda h: (-h["count"], h["polyline"][0]))
    return out



def species_record(name: Optional[str]) -> dict:
    """The ``SPECIES`` entry of ``name`` (a generic broadleaf for an unknown name), with its ``name``."""
    key = str(name or "").strip().lower().replace(" ", "_")
    rec = SPECIES.get(key)
    if rec is None:
        rec = SPECIES["generic_broadleaf"]
        key = "generic_broadleaf"
    return dict(rec, name=key)


def assets_dir() -> Optional[Path]:
    """The assets folder: ``WENART_ASSETS``, the scene's ``wenart_assets_dir`` (when bpy runs), else the first of
    ``ASSET_CANDIDATES`` that holds a manifest; None when none does."""
    cands = []
    env = os.environ.get("WENART_ASSETS")
    if env:
        cands.append(env)
    try:
        import bpy
        prop = bpy.context.scene.get("wenart_assets_dir") if bpy.context.scene is not None else None
        if prop:
            cands.append(str(prop))
    except Exception:          # no bpy, or no scene yet
        pass
    cands += list(ASSET_CANDIDATES)
    for c in cands:
        if (Path(c) / "manifest.json").is_file():
            return Path(c)
    return None


def assets_manifest(folder: Optional[Path] = None) -> dict:
    """The assets manifest (``{"textures", "hdris", "models"}``) of the folder, ``{}`` without one."""
    folder = folder or assets_dir()
    if folder is None:
        return {}
    try:
        return json.loads((Path(folder) / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def hero_model(species: str, manifest: Optional[dict] = None, folder: Optional[Path] = None) -> Optional[dict]:
    """The Poly Haven model of a species when the assets hold it (pure): ``{"id", "path", "height_m",
    "polycount", "licence", "name"}``, else None. The path is the glTF the manifest records (``models/<id>/
    <id>_<size>.gltf``), the height the manifest's measured box (``bbox_m[2]``), else the API's."""
    rec = species_record(species)
    return scan_model((rec.get("source") or {}).get("polyhaven"), manifest, folder)


def scan_model(asset: Optional[str], manifest: Optional[dict] = None, folder: Optional[Path] = None) -> Optional[dict]:
    """The Poly Haven model ``asset`` (an id of ``POLYHAVEN_MODELS``) when the assets hold it (pure; ``hero_model``
    by asset id, 27 Oct 2026: the horizon context's trees): the same record, else None."""
    if not asset or asset not in POLYHAVEN_MODELS:
        return None
    folder = folder or assets_dir()
    manifest = manifest if manifest is not None else assets_manifest(folder)
    entry = (manifest.get("models") or {}).get(asset)
    if not isinstance(entry, dict) or folder is None:
        return None
    rel = (entry.get("files") or {}).get("gltf")
    if not rel:
        return None
    path = Path(folder) / rel
    if not path.is_file():
        return None
    bbox = entry.get("bbox_m") or []
    height = float(bbox[2]) if len(bbox) >= 3 and float(bbox[2]) > 0 else POLYHAVEN_MODELS[asset]["height_m"]
    z0 = float((entry.get("bbox_min_m") or [0, 0, 0])[2])
    return {"id": asset, "path": str(path), "height_m": height, "base_z": z0, "licence": POLYHAVEN_LICENCE,
            "licence_url": POLYHAVEN_LICENCE_URL, "polycount": entry.get("polycount") or POLYHAVEN_MODELS[asset]["polycount"],
            "name": entry.get("name") or POLYHAVEN_MODELS[asset]["name"]}


def leaf_atlas(species: str, manifest: Optional[dict] = None, folder: Optional[Path] = None) -> Optional[dict]:
    """The leaf atlas texture of a species when the assets hold it (pure): ``{"id", "files": {albedo, normal,
    roughness[, opacity]}, "size_m", "licence"}`` with absolute paths, else None."""
    rec = species_record(species)
    asset = LEAF_ATLASES.get(rec.get("leaf") or "broadleaf")
    folder = folder or assets_dir()
    manifest = manifest if manifest is not None else assets_manifest(folder)
    entry = (manifest.get("textures") or {}).get(asset) if asset else None
    if not isinstance(entry, dict) or folder is None:
        return None
    files = {}
    for key, rel in (entry.get("files") or {}).items():
        p = Path(folder) / rel
        if p.is_file():
            files[key] = str(p)
    if "albedo" not in files:
        return None
    return {"id": asset, "files": files, "size_m": entry.get("size_m") or [1.0, 1.0], "licence": LEAF_LICENCE}


def sapling_overrides(species: str, height_m: float, seed: int, preset: Optional[dict] = None) -> dict:
    """The operator settings laid over the preset (pure): ``scale`` = ``height_m`` / the preset's measured top per
    scale (``SAPLING_TOP_PER_SCALE``; the built tree is measured and corrected afterwards), ``scaleV`` 0 (the drawn
    height is kept), ``levels``, ``shape``, ``seed``, ``bevel``, ``bevelRes`` 1, and the leaves (round 3, P1 'sapling'
    row): ``showLeaves`` on whatever the preset says (douglas_fir, quaking_aspen and the willows ship with it off),
    ``leafShape`` ``rect`` (the add-on's own leaf quads with UVs; ``dFace`` instanced our card at 3 cm), ``leaves``
    the preset's count per branch (else ``SAPLING_LEAVES_DEFAULT``), ``leafScale`` ``SAPLING_LEAF_M`` x the species'
    card scale (metres, the quad's height), ``leafScaleX`` 1 (a square atlas tile), ``leafScaleV`` a size variation,
    ``bend`` 0; ``do_update``. The property names are those of sapling_tree_gen 0.3.7's ``AddTree`` operator."""
    rec = species_record(species)
    preset_name = (rec.get("source") or {}).get("sapling") or ""
    top = SAPLING_TOP_PER_SCALE.get(preset_name) or float(rec.get("overshoot") or 1.2)
    scale = max(0.3, float(height_m) / top)
    leaves = (preset or {}).get("leaves")
    leaves = int(leaves) if isinstance(leaves, (int, float)) and int(leaves) != 0 else SAPLING_LEAVES_DEFAULT
    cs = float(rec.get("card_scale") or 1.0)
    out = {"do_update": True, "scale": round(scale, 4), "scaleV": 0.0, "levels": int(rec.get("levels") or 3),
           "seed": int(seed) % 100000, "bevel": True, "bevelRes": 1, "showLeaves": True, "leafShape": "rect",
           "leaves": leaves, "leafScale": round(SAPLING_LEAF_M * cs, 4), "leafScaleX": 1.0, "leafScaleT": 0.0,
           "leafScaleV": SAPLING_LEAF_SCALE_V, "bend": 0.0, "useArm": False, "armAnim": False,
           "makeMesh": False, "prune": False}
    shape = rec.get("shape")
    if shape in SAPLING_SHAPES:
        out["shape"] = SAPLING_SHAPES[shape]
    if rec.get("crown") == "columnar":
        out["attractUp"] = (0.0, 0.8, 0.8, 0.8)
    return out


def hedge_density(card_scale: float = 1.0) -> float:
    """Leaf cards per m² of hedge hull for a species' card scale (pure; round 3): ``LEAF_CARDS_PER_M2 /
    card_scale²``, so every species gets the same expected cover (``HEDGE_COVER_LAYERS``) whatever its leaf size:
    boxwood (0.45) 518.5/m², privet (0.6) 291.7/m², cherry laurel (0.9) 129.6/m²."""
    cs = max(0.2, float(card_scale or 1.0))
    return round(LEAF_CARDS_PER_M2 / (cs * cs), 1)


def cover_layers(density: float, card_m: Sequence[float], opaque: float = LEAF_ATLAS_OPAQUE) -> float:
    """The expected opaque layers of cards over a surface (pure): density x card area x the opaque share."""
    return round(float(density) * float(card_m[0]) * float(card_m[1]) * float(opaque), 3)


def hedge_plan(hedge: dict) -> dict:
    """The plan of a leaf-card hedge (pure): ``{"length_m", "surface_m2" (top and two sides), "cards",
    "density" (per species, ``hedge_density``), "card_m": [w, h], "cover_layers", "core": "hull", "top_round_m",
    "tilt_deg", "species", "colour"}``. ``hedge``: ``polyline``, ``width_m``, ``height_m``, ``species``."""
    from wenart.blender.site import HEDGE_TOP_ROUND_M

    pts = [(float(x), float(y)) for x, y in hedge["polyline"]]
    length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
    w, h = float(hedge["width_m"]), float(hedge["height_m"])
    surface = length * (w + 2.0 * h) + 2.0 * w * h
    rec = species_record(hedge.get("species"))
    cs = float(rec.get("card_scale") or 1.0)
    density = hedge_density(cs)
    card_m = [round(LEAF_CARD_M[0] * cs, 4), round(LEAF_CARD_M[1] * cs, 4)]
    return {"length_m": round(length, 3), "surface_m2": round(surface, 3), "density": density,
            "cards": int(round(surface * density)), "card_m": card_m, "cover_layers": cover_layers(density, card_m),
            "core": "hull", "top_round_m": round(max(0.0, min(HEDGE_TOP_ROUND_M, w / 2.0, h / 2.0)), 3),
            "tilt_deg": HEDGE_CARD_TILT_DEG, "species": rec["name"], "colour": list(rec["colour"])}


def crown_plan(species: str, height_m: float, crown_m: Optional[float] = None) -> dict:
    """The plan of a leaf-card tree (pure): the trunk (height, radius), the crown ellipsoid (rx, ry, rz, centre z)
    from the species' crown shape and the drawn crown diameter (else ``width_factor`` x the height), the card
    count of its two shells (``CROWN_CARDS_PER_M2``). Shrubs: a leaf-card ball on the ground without a trunk."""
    rec = species_record(species)
    h = max(0.3, float(height_m))
    crown = rec.get("crown")
    width = float(crown_m) if crown_m else h * float(rec.get("width_factor") or 0.8)
    if crown in ("shrub", "hedge"):
        rz = h / 2.0
        rx = width / 2.0
        trunk_h, trunk_r, cz = 0.0, 0.0, rz
    else:
        share = float(rec.get("trunk_share") or {"columnar": 0.12, "conical": 0.1, "umbrella": 0.5}.get(crown, 0.3))
        trunk_h = h * share
        crown_h = h - trunk_h
        rz = crown_h / 2.0
        rx = width / 2.0
        trunk_r = max(0.04, min(0.35, 0.02 * h))
        cz = trunk_h + rz
        if crown == "umbrella":
            cz = trunk_h + crown_h * 0.6
            rz = crown_h * 0.45
    ry = rx * (0.85 if crown == "spreading" else 1.0)
    area = 4.0 * math.pi * ((rx * ry) ** 1.6 + (rx * rz) ** 1.6 + (ry * rz) ** 1.6) ** (1.0 / 1.6) / 3.0 ** (1.0 / 1.6)
    shells = 2 if crown not in ("shrub", "hedge") else 1
    cards = int(round(area * CROWN_CARDS_PER_M2 * shells))
    card = float(rec.get("card_scale") or 1.0) * (1.4 if h > 6.0 else 1.0)
    return {"species": rec["name"], "crown": crown, "height_m": round(h, 3), "trunk_h": round(trunk_h, 3),
            "trunk_r": round(trunk_r, 3), "crown_rx": round(rx, 3), "crown_ry": round(ry, 3), "crown_rz": round(rz, 3),
            "crown_cz": round(cz, 3), "surface_m2": round(area, 3), "shells": shells, "cards": cards,
            "card_m": [round(LEAF_CARD_M[0] * card, 4), round(LEAF_CARD_M[1] * card, 4)], "colour": list(rec["colour"])}


def palm_plan(height_m: float, seed: int = 0, fronds: int = 14) -> dict:
    """A palm (pure): a leaning trunk of ``height_m`` and ``fronds`` frond cards fanned around its top (yaw, pitch
    and length per frond, deterministic by ``seed``)."""
    rng = random.Random(seed)
    h = max(2.0, float(height_m))
    length = max(1.2, 0.35 * h)
    out = []
    for i in range(fronds):
        yaw = 360.0 * i / fronds + rng.uniform(-8.0, 8.0)
        pitch = rng.uniform(-35.0, 25.0)                      # droop under the horizontal to a little up
        out.append({"yaw_deg": round(yaw, 2), "pitch_deg": round(pitch, 2), "length_m": round(length * rng.uniform(0.8, 1.1), 3),
                    "width_m": round(0.22 * length, 3)})
    return {"height_m": round(h, 3), "trunk_r": round(max(0.12, 0.03 * h), 3), "lean_deg": round(rng.uniform(2.0, 8.0), 2),
            "fronds": out}


def leaf_mask_points(n: int = 16) -> list:
    """The outline of the procedural leaf mask (pure): an ellipse in card UV space (0..1), for the tests and the
    alpha node (a Spherical gradient of the centred UV: inside where the gradient is over ``LEAF_MASK_EDGE``)."""
    return [(0.5 + 0.5 * math.cos(2 * math.pi * k / n), 0.5 + 0.5 * math.sin(2 * math.pi * k / n)) for k in range(n)]


LEAF_MASK_EDGE = 0.12


def tree_source(species: str, near_camera: bool, levers: Optional[dict] = None, hero: Optional[dict] = None,
                sapling_ok: bool = False) -> str:
    """Which source builds a tree (pure): ``polyhaven`` near the cameras with the ``instances`` lever and a model
    in the assets, else ``sapling`` with the ``sapling`` lever and the add-on registered (and a preset for the
    species), else ``palm`` for a palm, else ``cards``."""
    rec = species_record(species)
    lv = levers or {"instances": True, "sapling": True}
    if near_camera and lv.get("instances", True) and hero is not None:
        return "polyhaven"
    if lv.get("sapling", True) and sapling_ok and (rec.get("source") or {}).get("sapling") in SAPLING_PRESETS \
            and rec.get("crown") not in ("shrub", "hedge", "palm"):
        return "sapling"
    if rec.get("crown") == "palm":
        return "palm"
    return "cards"


def missing_source(species: str, near_camera: bool, levers: Optional[dict] = None, hero: Optional[dict] = None,
                   sapling: Optional[dict] = None) -> dict:
    """Why a tree is not built from the source it is meant to have (pure; pre-flight of pod P3): ``{}`` when that
    source is there, else ``{"fallback_from": "polyhaven" | "sapling", "fallback_reason"}``. Near a camera a tree is
    meant to be the species' Poly Haven instance (``instances`` lever; ``hero`` is what ``hero_model`` found, None
    when the model is not in the assets); elsewhere a species with a Sapling preset (not a shrub, hedge or palm) is
    meant to be a Sapling tree (``sapling`` lever; ``sapling`` is ``ensure_sapling()``'s record)."""
    rec = species_record(species)
    lv = levers or {"instances": True, "sapling": True}
    src = rec.get("source") or {}
    model = src.get("polyhaven")
    if near_camera and lv.get("instances", True) and model in POLYHAVEN_MODELS and hero is None:
        return {"fallback_from": "polyhaven",
                "fallback_reason": f"the Poly Haven model {model} of {rec['name']} is not in the assets "
                                   f"({assets_dir() or 'no assets folder'}; scripts/pod_setup_vegetation.sh fetches it)"}
    if lv.get("sapling", True) and src.get("sapling") in SAPLING_PRESETS \
            and rec.get("crown") not in ("shrub", "hedge", "palm") and not (sapling or {}).get("ok"):
        return {"fallback_from": "sapling",
                "fallback_reason": f"the Sapling add-on is not usable ({(sapling or {}).get('how') or 'not checked'})"}
    return {}


# --------------------------------------------------------------------------
# Sapling Tree Gen (the installed GPL add-on, called through bpy.ops)
# --------------------------------------------------------------------------

def sapling_module():
    """The registered Sapling module (its ``AddTree`` operator and ``getPresetpaths``), or None."""
    for name, mod in list(sys.modules.items()):
        if mod is not None and hasattr(mod, "AddTree") and hasattr(mod, "getPresetpaths") \
                and getattr(getattr(mod, "AddTree", None), "bl_idname", "") == "curve.tree_add":
            return mod
    return None


def sapling_available() -> bool:
    """True when ``curve.tree_add`` is a registered operator."""
    try:
        import bpy
        return hasattr(bpy.types, "CURVE_OT_tree_add")
    except Exception:
        return False


def ensure_sapling() -> dict:
    """Make the Sapling add-on usable (bpy): already registered, else enabled from the installed extension
    (``bpy.ops.preferences.addon_enable`` over ``SAPLING_MODULES``), else imported from ``WENART_SAPLING_DIR`` (a
    folder holding the add-on package; the pod setup and the tests). ``{"ok", "how", "module"}``."""
    if sapling_available():
        return {"ok": True, "how": "registered", "module": getattr(sapling_module(), "__name__", None)}
    try:
        import bpy
    except Exception:
        return {"ok": False, "how": "no bpy", "module": None}
    folder = os.environ.get(SAPLING_DIR_ENV)
    if not (folder and Path(folder).is_dir()):
        for name in SAPLING_MODULES:
            try:
                bpy.ops.preferences.addon_enable(module=name)
            except Exception:
                continue
            if sapling_available():
                return {"ok": True, "how": "addon_enable", "module": name}
    if folder and Path(folder).is_dir():
        import importlib
        parent = str(Path(folder).resolve())
        if parent not in sys.path:
            sys.path.insert(0, parent)
        for pkg in ("sapling_tree_gen", "add_curve_sapling"):
            if not (Path(parent) / pkg / "__init__.py").is_file():
                continue
            try:
                mod = importlib.import_module(pkg)
                try:
                    mod.register()
                except Exception as exc:                # already registered
                    if "already registered" not in str(exc):
                        raise
            except Exception:
                continue
            if sapling_available():
                return {"ok": True, "how": f"{SAPLING_DIR_ENV}", "module": pkg}
    return {"ok": False, "how": "not installed (scripts/pod_setup_vegetation.sh)", "module": None}


def sapling_operator_keys() -> set:
    """The property names ``bpy.ops.curve.tree_add`` accepts (bpy; empty without the add-on). A preset file may
    carry keys of older add-on versions (``windGust`` ...) that the operator refuses: they are dropped."""
    try:
        import bpy
        return set(bpy.ops.curve.tree_add.get_rna_type().properties.keys())
    except Exception:
        return set()


def sapling_args(species: str, height_m: float, seed: int, preset: Optional[dict] = None) -> dict:
    """The full operator call of a species-look tree (pure given ``preset``): the preset's settings, the overrides
    of ``sapling_overrides`` on top, the preset-menu keys dropped, and (with bpy) only the keys the operator knows."""
    rec = species_record(species)
    preset = preset if preset is not None else (sapling_preset((rec.get("source") or {}).get("sapling") or "") or {})
    args = dict(preset)
    args.update(sapling_overrides(species, height_m, seed, preset))
    for key in ("chooseSet", "presetName", "limitImport", "overwrite", "leafDupliObj"):
        args.pop(key, None)
    known = sapling_operator_keys()
    if known:
        args = {k: v for k, v in args.items() if k in known}
    return args


def sapling_preset(name: str) -> Optional[dict]:
    """The settings of a Sapling preset read from the add-on's own presets folder (the first non-comment line of
    ``<name>.py``, a Python literal, as the add-on's Import Preset reads it); None when unavailable."""
    if name not in SAPLING_PRESETS:
        return None
    mod = sapling_module()
    paths = []
    if mod is not None:
        try:
            paths += list(mod.getPresetpaths())
        except Exception:
            pass
    folder = os.environ.get(SAPLING_DIR_ENV)
    if folder:
        for pkg in ("sapling_tree_gen", "add_curve_sapling"):
            paths.append(str(Path(folder) / pkg / "presets"))
    for p in paths:
        f = Path(p) / f"{name}.py"
        if not f.is_file():
            continue
        try:
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip() and not line.lstrip().startswith("#"):
                    data = ast.literal_eval(line.strip())
                    if isinstance(data, dict):
                        if isinstance(data.get("attractUp"), (int, float)):
                            data["attractUp"] = [0, 0, data["attractUp"], data["attractUp"]]
                        return data
        except (OSError, ValueError, SyntaxError):
            continue
    return None


# --------------------------------------------------------------------------
# bpy: materials, cards, the library collection
# --------------------------------------------------------------------------

LIBRARY_COLLECTION = "vegetation_library"
_HEROES: dict = {}            # asset id -> {"collection", "height_m", "base_z", "count"}


def library_collection():
    """The collection that holds the imported models and the card objects (bpy; never linked to the scene)."""
    import bpy
    col = bpy.data.collections.get(LIBRARY_COLLECTION)
    if col is None:
        col = bpy.data.collections.new(LIBRARY_COLLECTION)
    return col


def _unlink_everywhere(ob) -> None:
    for col in list(ob.users_collection):
        col.objects.unlink(ob)


def _node(tree, idname: str, **props):
    n = tree.nodes.new(idname)
    for k, v in props.items():
        setattr(n, k, v)
    return n


def leaf_material(name: str, colour: Sequence[float], atlas: Optional[dict] = None):
    """A leaf card material (bpy): Principled BSDF with ``Thin Wall`` on, the atlas Color map (CC0) else the
    species colour, the Opacity map when the atlas has one else the procedural leaf mask (a Spherical gradient of
    the centred UV over ``LEAF_MASK_EDGE`` -> Alpha), a little translucency for backlit leaves. Cached by name."""
    import bpy
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    for n in list(tree.nodes):
        tree.nodes.remove(n)
    out = _node(tree, "ShaderNodeOutputMaterial")
    bsdf = _node(tree, "ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*colour, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.55
    if "Thin Wall" in bsdf.inputs:
        bsdf.inputs["Thin Wall"].default_value = True
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.0
    uv = _node(tree, "ShaderNodeTexCoord")
    if atlas and atlas.get("files", {}).get("albedo"):
        img = bpy.data.images.load(atlas["files"]["albedo"], check_existing=True)
        tex = _node(tree, "ShaderNodeTexImage", image=img)
        tree.links.new(uv.outputs["UV"], tex.inputs["Vector"])
        # round 3: the atlas colour x the species colour x LEAF_TINT_GAIN at LEAF_TINT_FACTOR (a darker green under
        # the atlas; P1 'hedge' row: pale yellow-green dots at factor 0.5 and gain 2.2)
        tint = _node(tree, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
        tint.inputs["Factor"].default_value = LEAF_TINT_FACTOR
        tree.links.new(tex.outputs["Color"], tint.inputs[6])
        tint.inputs[7].default_value = (*[min(1.0, c * LEAF_TINT_GAIN) for c in colour], 1.0)
        tree.links.new(tint.outputs[2], bsdf.inputs["Base Color"])
        if atlas["files"].get("normal"):
            nimg = bpy.data.images.load(atlas["files"]["normal"], check_existing=True)
            nimg.colorspace_settings.name = "Non-Color"
            ntex = _node(tree, "ShaderNodeTexImage", image=nimg)
            tree.links.new(uv.outputs["UV"], ntex.inputs["Vector"])
            nmap = _node(tree, "ShaderNodeNormalMap")
            tree.links.new(ntex.outputs["Color"], nmap.inputs["Color"])
            tree.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    # the alpha: the atlas opacity map when the fetcher kept one, else the procedural leaf mask
    if atlas and atlas.get("files", {}).get("opacity"):
        oimg = bpy.data.images.load(atlas["files"]["opacity"], check_existing=True)
        oimg.colorspace_settings.name = "Non-Color"
        otex = _node(tree, "ShaderNodeTexImage", image=oimg)
        tree.links.new(uv.outputs["UV"], otex.inputs["Vector"])
        tree.links.new(otex.outputs["Color"], bsdf.inputs["Alpha"])
        mask = "opacity_map"
    else:
        centre = _node(tree, "ShaderNodeVectorMath", operation="SUBTRACT")
        centre.inputs[1].default_value = (0.5, 0.5, 0.0)
        tree.links.new(uv.outputs["UV"], centre.inputs[0])
        scale = _node(tree, "ShaderNodeVectorMath", operation="SCALE")
        scale.inputs["Scale"].default_value = 2.0
        tree.links.new(centre.outputs["Vector"], scale.inputs[0])
        grad = _node(tree, "ShaderNodeTexGradient", gradient_type="SPHERICAL")
        tree.links.new(scale.outputs["Vector"], grad.inputs["Vector"])
        edge = _node(tree, "ShaderNodeMath", operation="GREATER_THAN")
        edge.inputs[1].default_value = LEAF_MASK_EDGE
        tree.links.new(grad.outputs["Fac"], edge.inputs[0])
        tree.links.new(edge.outputs["Value"], bsdf.inputs["Alpha"])
        mask = "procedural_ellipse"
    trans = _node(tree, "ShaderNodeBsdfTranslucent")
    trans.inputs["Color"].default_value = (*[min(1.0, c) for c in colour], 1.0)
    mix = _node(tree, "ShaderNodeMixShader")
    mix.inputs["Factor"].default_value = LEAF_TRANSLUCENT
    tree.links.new(bsdf.outputs["BSDF"], mix.inputs[1])
    tree.links.new(trans.outputs["BSDF"], mix.inputs[2])
    tree.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    mat["wenart_leaf"] = True
    mat["wenart_leaf_mask"] = mask
    mat["wenart_atlas"] = atlas["id"] if atlas else ""
    mat["wenart_licence"] = atlas["licence"] if atlas else ""
    mat["wenart_tint"] = f"factor {LEAF_TINT_FACTOR}, gain {LEAF_TINT_GAIN}, translucent {LEAF_TRANSLUCENT}"
    return mat


def bark_material(name: str = "veg_bark"):
    """The trunk material (bpy): a dark brown Principled BSDF with a noise-driven roughness and bump (no bark scan
    in the assets yet). Cached by name."""
    import bpy
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (0.11, 0.08, 0.06, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
        coord = _node(tree, "ShaderNodeTexCoord")
        noise = _node(tree, "ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 18.0
        noise.inputs["Detail"].default_value = 6.0
        tree.links.new(coord.outputs["Object"], noise.inputs["Vector"])
        bump = _node(tree, "ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.4
        tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


# 26 Oct 2026 (real06, site.horizon_context): the leaf texture of the distant context crowns. An atlas tile covers
# CONTEXT_LEAF["tile_m"] of the crown (seen from 50-400 m: a leafy grain, not single leaves); a Voronoi of the object
# coordinates (``clump_per_m``) darkens the gaps between the leaf clumps from ``light`` to ``dark`` x the species colour
# and gives them a bump, so a crown reads as foliage in the sun and in the shade.
CONTEXT_LEAF = {"tile_m": 0.6, "clump_per_m": 0.9, "light": 1.15, "dark": 0.45, "bump": 0.6, "roughness": 0.8,
                # 27 Oct 2026 (pod run 224516: the judge saw "lollipop" crowns with a dotted texture in 20 of 28 views;
                # the atlas tile of 0.6 m reads as a regular dot grid from 50 m): the atlas is off by default; a fine
                # noise gives the leafy grain and a coarse one (``tree_var_per_m``) varies the green between trees
                "atlas": False, "grain_per_m": 2.5, "grain": 0.35, "tree_var_per_m": 0.04, "tree_var": 0.35}


def context_material(species: str):
    """The material of a species' distant context crowns (bpy; 26 Oct 2026, ``site.build_context``): an opaque
    Principled BSDF whose Base Color is a Voronoi clump ramp on the species colour, times a fine leafy grain and a
    coarse variation between trees (27 Oct 2026: a procedural leaf texture), with a bump from the clumps; with
    ``CONTEXT_LEAF["atlas"]`` the species' leaf atlas (``leaf_atlas``, CC0; the box UVs in metres of
    ``common.assign_box_uvs`` at ``CONTEXT_LEAF["tile_m"]`` a tile) tinted by it x ``LEAF_TINT_GAIN``. Cached by name
    ``veg_context_<species>``; records ``wenart_atlas``."""
    import bpy
    rec = species_record(species)
    name = f"veg_context_{rec['name']}"
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    for n in list(tree.nodes):
        tree.nodes.remove(n)
    colour = [float(c) for c in rec["colour"]]
    cfg = CONTEXT_LEAF
    out = _node(tree, "ShaderNodeOutputMaterial")
    bsdf = _node(tree, "ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = cfg["roughness"]
    coord = _node(tree, "ShaderNodeTexCoord")
    clumps = _node(tree, "ShaderNodeTexVoronoi")
    clumps.inputs["Scale"].default_value = cfg["clump_per_m"]
    tree.links.new(coord.outputs["Object"], clumps.inputs["Vector"])
    ramp = _node(tree, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*[min(1.0, c * cfg["light"]) for c in colour], 1.0)
    ramp.color_ramp.elements[1].color = (*[c * cfg["dark"] for c in colour], 1.0)
    tree.links.new(clumps.outputs["Distance"], ramp.inputs["Fac"])
    atlas = leaf_atlas(rec["name"]) if cfg.get("atlas") else None
    base = ramp.outputs["Color"]
    # 27 Oct 2026: the leafy grain (a fine noise darkening up to ``grain``) and the variation between trees (a coarse
    # noise of the object coordinates brightening or darkening up to ``tree_var``)
    for scale, amount in ((cfg.get("grain_per_m"), cfg.get("grain")), (cfg.get("tree_var_per_m"), cfg.get("tree_var"))):
        if not scale or not amount:
            continue
        noise = _node(tree, "ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = float(scale)
        noise.inputs["Detail"].default_value = 4.0
        tree.links.new(coord.outputs["Object"], noise.inputs["Vector"])
        shade = _node(tree, "ShaderNodeMapRange")
        shade.inputs["To Min"].default_value = 1.0 - float(amount)
        shade.inputs["To Max"].default_value = 1.0 + (float(amount) * 0.5 if scale == cfg.get("tree_var_per_m")
                                                      else 0.0)
        tree.links.new(noise.outputs["Fac"], shade.inputs["Value"])
        mix = _node(tree, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
        mix.inputs["Factor"].default_value = 1.0
        tree.links.new(base, mix.inputs[6])
        tree.links.new(shade.outputs["Result"], mix.inputs[7])
        base = mix.outputs[2]
    if atlas and atlas.get("files", {}).get("albedo"):
        img = bpy.data.images.load(atlas["files"]["albedo"], check_existing=True)
        mapping = _node(tree, "ShaderNodeMapping")
        mapping.inputs["Scale"].default_value = (1.0 / cfg["tile_m"], 1.0 / cfg["tile_m"], 1.0)
        tree.links.new(coord.outputs["UV"], mapping.inputs["Vector"])
        tex = _node(tree, "ShaderNodeTexImage", image=img)
        tree.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
        tint = _node(tree, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
        tint.inputs["Factor"].default_value = 1.0
        tree.links.new(tex.outputs["Color"], tint.inputs[6])
        tree.links.new(ramp.outputs["Color"], tint.inputs[7])
        gain = _node(tree, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
        gain.inputs["Factor"].default_value = 1.0
        tree.links.new(tint.outputs[2], gain.inputs[6])
        gain.inputs[7].default_value = (LEAF_TINT_GAIN, LEAF_TINT_GAIN, LEAF_TINT_GAIN, 1.0)
        base = gain.outputs[2]
    tree.links.new(base, bsdf.inputs["Base Color"])
    bump = _node(tree, "ShaderNodeBump")
    bump.inputs["Strength"].default_value = cfg["bump"]
    tree.links.new(clumps.outputs["Distance"], bump.inputs["Height"])
    tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    mat["wenart_context"] = True
    mat["wenart_atlas"] = atlas["id"] if atlas else ""
    mat["wenart_licence"] = atlas["licence"] if atlas else ""
    mat["wenart_leaf_texture"] = "atlas" if atlas else "procedural"
    return mat


def _card_mesh(name: str, w: float, h: float, standing: bool = False):
    """A card mesh ``w`` x ``h`` with UVs 0..1 (lying in XY with its normal +Z, or standing in XZ)."""
    import bpy
    me = bpy.data.meshes.new(name)
    if standing:
        verts = [(-w / 2, 0.0, 0.0), (w / 2, 0.0, 0.0), (w / 2, 0.0, h), (-w / 2, 0.0, h)]
    else:
        verts = [(-w / 2, -h / 2, 0.0), (w / 2, -h / 2, 0.0), (w / 2, h / 2, 0.0), (-w / 2, h / 2, 0.0)]
    me.from_pydata(verts, [], [(0, 1, 2, 3)])
    me.update()
    layer = me.uv_layers.new(name="UVMap")
    for loop, uvc in zip(me.loops, ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))):
        layer.data[loop.index].uv = uvc
    return me


def leaf_card(species: str, card_m: Sequence[float], atlas: Optional[dict] = None):
    """The leaf card object of a species (bpy; one per species, in the library collection): a plane with the leaf
    material, lying flat (its normal +Z: Instance on Points aligns it to the surface normal)."""
    import bpy
    rec = species_record(species)
    name = f"veg_leaf_{rec['name']}"
    ob = bpy.data.objects.get(name)
    if ob is not None:
        return ob
    mat = leaf_material(f"veg_leaf_{rec['name']}", rec["colour"], atlas)
    me = _card_mesh(name, float(card_m[0]), float(card_m[1]))
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    library_collection().objects.link(ob)
    ob["wenart_kind"] = "vegetation_card"
    return ob


def grass_card_object(name: str = "veg_grass_clump"):
    """A grass clump of three crossed standing cards (bpy; the library collection) with a green gradient material
    (dark base to light tip) and a tapering alpha; the fallback when the Poly Haven clump is not in the assets."""
    import bpy
    ob = bpy.data.objects.get(name)
    if ob is not None:
        return ob
    w, h = GRASS_CARD_M
    me = bpy.data.meshes.new(name)
    verts, faces = [], []
    for k in range(3):
        a = math.radians(60.0 * k)
        dx, dy = math.cos(a) * w / 2, math.sin(a) * w / 2
        base = len(verts)
        verts += [(-dx, -dy, 0.0), (dx, dy, 0.0), (dx, dy, h), (-dx, -dy, h)]
        faces.append((base, base + 1, base + 2, base + 3))
    me.from_pydata(verts, [], faces)
    me.update()
    layer = me.uv_layers.new(name="UVMap")
    uvs = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    for poly in me.polygons:
        for li, uvc in zip(poly.loop_indices, uvs):
            layer.data[li].uv = uvc
    mat = bpy.data.materials.get("veg_grass_card")
    if mat is None:
        mat = bpy.data.materials.new("veg_grass_card")
        mat.use_nodes = True
        tree = mat.node_tree
        for n in list(tree.nodes):
            tree.nodes.remove(n)
        out = _node(tree, "ShaderNodeOutputMaterial")
        bsdf = _node(tree, "ShaderNodeBsdfPrincipled")
        bsdf.inputs["Roughness"].default_value = 0.6
        if "Thin Wall" in bsdf.inputs:
            bsdf.inputs["Thin Wall"].default_value = True
        uv = _node(tree, "ShaderNodeTexCoord")
        sep = _node(tree, "ShaderNodeSeparateXYZ")
        tree.links.new(uv.outputs["UV"], sep.inputs["Vector"])
        ramp = _node(tree, "ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.05, 0.12, 0.02, 1.0)
        ramp.color_ramp.elements[1].color = (0.35, 0.52, 0.14, 1.0)
        tree.links.new(sep.outputs["Y"], ramp.inputs["Fac"])
        tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
        # taper: |u - 0.5| * 2 < 1 - v
        cu = _node(tree, "ShaderNodeMath", operation="SUBTRACT")
        cu.inputs[1].default_value = 0.5
        tree.links.new(sep.outputs["X"], cu.inputs[0])
        au = _node(tree, "ShaderNodeMath", operation="ABSOLUTE")
        tree.links.new(cu.outputs["Value"], au.inputs[0])
        du = _node(tree, "ShaderNodeMath", operation="MULTIPLY")
        du.inputs[1].default_value = 2.0
        tree.links.new(au.outputs["Value"], du.inputs[0])
        iv = _node(tree, "ShaderNodeMath", operation="SUBTRACT")
        iv.inputs[0].default_value = 1.0
        tree.links.new(sep.outputs["Y"], iv.inputs[1])
        lt = _node(tree, "ShaderNodeMath", operation="LESS_THAN")
        tree.links.new(du.outputs["Value"], lt.inputs[0])
        tree.links.new(iv.outputs["Value"], lt.inputs[1])
        tree.links.new(lt.outputs["Value"], bsdf.inputs["Alpha"])
        tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    library_collection().objects.link(ob)
    ob["wenart_kind"] = "vegetation_card"
    return ob


# --------------------------------------------------------------------------
# bpy: geometry-nodes scatter
# --------------------------------------------------------------------------

def scatter_group(name: str, instance_ob, density: float, seed: int, scale_range=(0.8, 1.3), tilt_deg: float = 25.0,
                  keep_surface: bool = True, align_normal: bool = True):
    """A geometry-nodes group that scatters ``instance_ob`` over the faces of the input mesh (bpy): Distribute
    Points on Faces (``density`` per m², ``seed``) -> Instance on Points with the points' rotation (the instance Z
    along the face normal) turned by a random tilt and yaw (Random Value -> Euler To Rotation -> Rotate Rotation),
    a random uniform scale in ``scale_range``; the surface itself is kept (``keep_surface``) and joined."""
    import bpy
    ng = bpy.data.node_groups.get(name)
    if ng is not None:
        return ng
    ng = bpy.data.node_groups.new(name, "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gi = ng.nodes.new("NodeGroupInput")
    go = ng.nodes.new("NodeGroupOutput")
    dist = ng.nodes.new("GeometryNodeDistributePointsOnFaces")
    dist.distribute_method = "RANDOM"
    dist.inputs["Density"].default_value = float(density)
    dist.inputs["Seed"].default_value = int(seed) % 10000
    info = ng.nodes.new("GeometryNodeObjectInfo")
    info.inputs["Object"].default_value = instance_ob
    info.inputs["As Instance"].default_value = True
    inst = ng.nodes.new("GeometryNodeInstanceOnPoints")
    rnd_rot = ng.nodes.new("FunctionNodeRandomValue")
    rnd_rot.data_type = "FLOAT_VECTOR"
    t = math.radians(tilt_deg)
    vmin = [x for x in rnd_rot.inputs if x.name == "Min" and x.type == "VECTOR"][0]
    vmax = [x for x in rnd_rot.inputs if x.name == "Max" and x.type == "VECTOR"][0]
    vmin.default_value = (-t, -t, 0.0)
    vmax.default_value = (t, t, 2.0 * math.pi)
    [x for x in rnd_rot.inputs if x.name == "Seed"][0].default_value = int(seed) % 10000 + 1
    euler = ng.nodes.new("FunctionNodeEulerToRotation")
    rot = ng.nodes.new("FunctionNodeRotateRotation")
    rot.rotation_space = "LOCAL"
    rnd_s = ng.nodes.new("FunctionNodeRandomValue")
    rnd_s.data_type = "FLOAT"
    smin = [x for x in rnd_s.inputs if x.name == "Min" and x.type == "VALUE"][0]
    smax = [x for x in rnd_s.inputs if x.name == "Max" and x.type == "VALUE"][0]
    smin.default_value, smax.default_value = float(scale_range[0]), float(scale_range[1])
    [x for x in rnd_s.inputs if x.name == "Seed"][0].default_value = int(seed) % 10000 + 2
    join = ng.nodes.new("GeometryNodeJoinGeometry")
    L = ng.links
    L.new(gi.outputs[0], dist.inputs["Mesh"])
    L.new(dist.outputs["Points"], inst.inputs["Points"])
    L.new(info.outputs["Geometry"], inst.inputs["Instance"])
    vout = [x for x in rnd_rot.outputs if x.type == "VECTOR"][0]
    L.new(vout, euler.inputs["Euler"])
    if align_normal:
        L.new(dist.outputs["Rotation"], rot.inputs["Rotation"])
        L.new(euler.outputs["Rotation"], rot.inputs["Rotate By"])
        L.new(rot.outputs["Rotation"], inst.inputs["Rotation"])
    else:
        L.new(euler.outputs["Rotation"], inst.inputs["Rotation"])
    sout = [x for x in rnd_s.outputs if x.type == "VALUE"][0]
    L.new(sout, inst.inputs["Scale"])
    L.new(inst.outputs["Instances"], join.inputs["Geometry"])
    if keep_surface:
        L.new(gi.outputs[0], join.inputs["Geometry"])
    L.new(join.outputs["Geometry"], go.inputs[0])
    return ng


def _mesh_object(name: str, verts, faces, collection, materials=()):
    import bpy
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [list(f) for f in faces])
    me.update()
    for m in materials:
        if m is not None:
            me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    return ob


def _manifest_kind(kind: str) -> str:
    """The object kind the scene manifest knows (``common.KINDS`` is a closed list): a site part's name as
    ``site.site_kind`` writes it into the manifest entry (its own name when ``common.KINDS`` and the scene-manifest
    schema both know it, else the Milestone 10-12 fallback of ``site.SITE_KINDS``), so the object property and the
    manifest entry agree; any other kind as it is when the list knows it, else ``site_decor``."""
    from wenart.blender.site import SITE_KINDS, site_kind
    for part, (own, _fallback) in SITE_KINDS.items():
        if own == kind:
            return site_kind(part)
    from wenart.blender import common
    if kind in common.KINDS:
        return kind
    return "site_decor"


def _tag(ob, kind: str, species: str, method: str, asset: Optional[str], licence: Optional[str], height_m: float):
    ob["wenart_id"] = ob.name
    ob["wenart_kind"] = _manifest_kind(kind)
    ob["wenart_site_part"] = kind
    ob["wenart_status"] = "assumed"
    ob["wenart_species"] = species
    ob["wenart_veg_method"] = method
    ob["wenart_asset"] = asset or ""
    ob["wenart_licence"] = licence or ""
    ob["wenart_height_m"] = float(height_m)


def hedge_object(hedge: dict, collection=None, name: Optional[str] = None) -> tuple:
    """The leaf-card hedge of one ``site.hedges`` record (bpy; Milestone 13 T6): its solid core (``core_verts`` /
    ``core_faces`` when given, else ``site.hedge_parts`` on a flat ground: the hull with rounded shoulders since
    round 3) with a dark core material (opaque from every side), and a geometry-nodes modifier scattering the
    species' leaf card over the hull's faces at the species' density (``hedge_plan``: ``hedge_density``, tilt
    ``HEDGE_CARD_TILT_DEG``, scale ``HEDGE_CARD_SCALE``). Returns ``(object, record)``; the record names the method
    ``cards``, the card count, density, card size and cover of ``hedge_plan``, the material and the atlas (CC0)
    when the assets hold one."""
    import bpy
    plan = hedge_plan(hedge)
    rec = species_record(hedge.get("species"))
    if hedge.get("core_verts") is not None and hedge.get("core_faces") is not None:
        verts, faces = hedge["core_verts"], hedge["core_faces"]
    else:
        from wenart.blender import site as S
        terrain = {"kind": "flat", "z": {k: float(hedge.get("ground_z") or 0.0) for k in S.AXES}}
        verts, faces, _info = S.hedge_parts(hedge, terrain)
    core = bpy.data.materials.get("veg_hedge_core")
    if core is None:
        core = bpy.data.materials.new("veg_hedge_core")
        core.use_nodes = True
        b = core.node_tree.nodes.get("Principled BSDF")
        if b is not None:
            b.inputs["Base Color"].default_value = (rec["colour"][0] * 0.35, rec["colour"][1] * 0.35, rec["colour"][2] * 0.35, 1.0)
            b.inputs["Roughness"].default_value = 0.9
    name = name or f"hedge_{hedge.get('id') or 'x'}"
    ob = _mesh_object(name, verts, faces, collection, [core])
    atlas = leaf_atlas(rec["name"])
    card = leaf_card(rec["name"], plan["card_m"], atlas)
    seed = sum(ord(c) for c in name)
    ng = scatter_group(f"veg_scatter_{rec['name']}_{int(plan['density'])}", card, plan["density"], seed,
                       scale_range=HEDGE_CARD_SCALE, tilt_deg=HEDGE_CARD_TILT_DEG)
    mod = ob.modifiers.new("leaf_cards", "NODES")
    mod.node_group = ng
    _tag(ob, "site_hedge", rec["name"], "cards", atlas["id"] if atlas else None, atlas["licence"] if atlas else None,
         float(hedge.get("height_m") or 0.0))
    ob["wenart_cards"] = int(plan["cards"])
    return ob, {"method": "cards", "cards": plan["cards"], "density": plan["density"], "card_m": plan["card_m"],
                "cover_layers": plan["cover_layers"], "core": plan["core"], "top_round_m": plan["top_round_m"],
                "tilt_deg": plan["tilt_deg"], "material": card.data.materials[0].name,
                "atlas": atlas["id"] if atlas else None, "licence": atlas["licence"] if atlas else None,
                "leaf_mask": card.data.materials[0].get("wenart_leaf_mask"), "species": rec["name"]}


def _import_hero(hero: dict) -> Optional[dict]:
    """Import a Poly Haven glTF once into the library collection (bpy): ``{"collection", "height_m", "base_z"}``."""
    import bpy
    cached = _HEROES.get(hero["id"])
    if cached is not None and bpy.data.collections.get(cached["collection"]) is not None:
        return cached
    before = set(bpy.data.objects)
    try:
        bpy.ops.import_scene.gltf(filepath=hero["path"], import_shading="NORMALS", import_scene_as_collection=False)
    except Exception:
        return None
    new = [o for o in bpy.data.objects if o not in before]
    if not new:
        return None
    col = bpy.data.collections.get(f"veg_{hero['id']}") or bpy.data.collections.new(f"veg_{hero['id']}")
    if col.name not in library_collection().children:
        library_collection().children.link(col)
    from mathutils import Vector
    pts = []
    for o in new:
        _unlink_everywhere(o)
        col.objects.link(o)
        if o.type == "MESH":
            for v in o.bound_box:
                pts.append(o.matrix_world @ Vector(v))
    zs = [p.z for p in pts]
    height = (max(zs) - min(zs)) if zs else hero["height_m"]
    base_z = min(zs) if zs else hero.get("base_z", 0.0)
    # 27 Oct 2026: the crown's width too (the larger of its x and y extents; the context trees scale to their width)
    width = max(max(p.x for p in pts) - min(p.x for p in pts), max(p.y for p in pts) - min(p.y for p in pts)) \
        if pts else 0.6 * hero["height_m"]
    _HEROES[hero["id"]] = {"collection": col.name, "height_m": max(0.3, height), "base_z": base_z,
                           "width_m": max(0.3, width), "count": 0}
    return _HEROES[hero["id"]]


def _tree_cards(name: str, species: str, height_m: float, seed: int, collection, crown_m: Optional[float]):
    """A trunk mesh and a leaf-card crown by geometry nodes (bpy)."""
    plan = crown_plan(species, height_m, crown_m)
    rec = species_record(species)
    from wenart.blender import site as S
    parts = []
    if plan["trunk_h"] > 0:
        parts.append(S._cylinder((0.0, 0.0), plan["trunk_r"], -0.05, plan["crown_cz"], segments=10))
    verts, faces = (parts[0] if parts else ([], []))
    trunk = _mesh_object(name, verts, faces, collection, [bark_material()])
    shells = [(1.0, "crown"), (0.7, "inner")] if plan["shells"] > 1 else [(1.0, "crown")]
    atlas = leaf_atlas(species)
    card = leaf_card(species, plan["card_m"], atlas)
    import bpy
    core = bpy.data.materials.get("veg_hedge_core")
    for k, (f, label) in enumerate(shells):
        sv, sf = S._sphere((0.0, 0.0, plan["crown_cz"]), plan["crown_rx"] * f, plan["crown_ry"] * f, plan["crown_rz"] * f,
                           segments=14, rings=8)
        shell = _mesh_object(f"{name}_{label}", sv, sf, collection, [core] if core is not None else [])
        shell.parent = trunk
        ng = scatter_group(f"veg_scatter_{rec['name']}_{int(CROWN_CARDS_PER_M2)}", card, CROWN_CARDS_PER_M2,
                           seed + k, scale_range=(0.8, 1.4), tilt_deg=40.0, keep_surface=(label == "inner"))
        mod = shell.modifiers.new("leaf_cards", "NODES")
        mod.node_group = ng
        shell["wenart_kind"] = "site_decor_part"
    _tag(trunk, "site_decor", rec["name"], "cards", atlas["id"] if atlas else None, atlas["licence"] if atlas else None,
         height_m)
    return trunk, {"method": "cards", "cards": plan["cards"], "material": card.data.materials[0].name,
                   "atlas": atlas["id"] if atlas else None, "licence": atlas["licence"] if atlas else None}


def _tree_palm(name: str, height_m: float, seed: int, collection):
    """A palm (bpy): a leaning trunk and frond cards (standing leaf cards fanned around the top)."""
    plan = palm_plan(height_m, seed)
    from wenart.blender import site as S
    h, r = plan["height_m"], plan["trunk_r"]
    lean = math.radians(plan["lean_deg"])
    verts, faces = S._cylinder((0.0, 0.0), r, -0.05, h, segments=10)
    verts = [(x + z * math.sin(lean), y, z * math.cos(lean)) for x, y, z in verts]
    trunk = _mesh_object(name, verts, faces, collection, [bark_material()])
    top = (h * math.sin(lean), 0.0, h * math.cos(lean))
    fv, ff = [], []
    for fr in plan["fronds"]:
        yaw, pitch = math.radians(fr["yaw_deg"]), math.radians(fr["pitch_deg"])
        L_, W_ = fr["length_m"], fr["width_m"]
        d = (math.cos(yaw) * math.cos(pitch), math.sin(yaw) * math.cos(pitch), math.sin(pitch))
        side = (-math.sin(yaw) * W_ / 2, math.cos(yaw) * W_ / 2, 0.0)
        base = len(fv)
        a = (top[0] - side[0] * 0.3, top[1] - side[1] * 0.3, top[2])
        b = (top[0] + side[0] * 0.3, top[1] + side[1] * 0.3, top[2])
        c = (top[0] + d[0] * L_ + side[0], top[1] + d[1] * L_ + side[1], top[2] + d[2] * L_)
        e = (top[0] + d[0] * L_ - side[0], top[1] + d[1] * L_ - side[1], top[2] + d[2] * L_)
        fv += [a, b, c, e]
        ff.append((base, base + 1, base + 2, base + 3))
    fronds = _mesh_object(f"{name}_fronds", fv, ff, collection, [leaf_material("veg_leaf_palm", SPECIES["palm"]["colour"])])
    me = fronds.data
    layer = me.uv_layers.new(name="UVMap")
    uvs = ((0.35, 0.0), (0.65, 0.0), (1.0, 1.0), (0.0, 1.0))
    for poly in me.polygons:
        for li, uvc in zip(poly.loop_indices, uvs):
            layer.data[li].uv = uvc
    fronds.parent = trunk
    fronds["wenart_kind"] = "site_decor_part"
    _tag(trunk, "site_decor", "palm", "palm", None, None, height_m)
    return trunk, {"method": "palm", "cards": len(plan["fronds"]), "material": "veg_leaf_palm", "atlas": None,
                   "licence": None}


def _tree_sapling(name: str, species: str, height_m: float, seed: int, collection, crown_m: Optional[float]):
    """A Sapling Tree Gen tree (bpy; the installed add-on through ``bpy.ops.curve.tree_add``): the species' preset
    read from the add-on's presets folder, our overrides on top (``sapling_overrides``: ``rect`` leaves), the bark
    on the curve, and the add-on's ``leaves`` mesh object (``utils.addTree`` of sapling_tree_gen 0.3.7 makes
    ``bpy.data.objects.new('leaves', mesh)``, links it to the scene collection and parents it to the tree curve;
    ``rect`` leaves are one quad each with the UV layer ``leafUV``) given the species' leaf-card material (the atlas
    colour and opacity, ``leaf_material``). A tree whose leaves mesh has no faces is removed again and raises
    RuntimeError (``tree_object`` then builds the leaf-card crown and records why): a Sapling tree is never bare
    (P1 real02 ext_1 'sapling')."""
    import bpy
    rec = species_record(species)
    preset_name = (rec.get("source") or {}).get("sapling")
    preset = sapling_preset(preset_name) or {}
    args = sapling_args(species, height_m, seed, preset)
    args.pop("leafDupliObj", None)                     # rect leaves are the add-on's own quads: no instanced object
    plan = crown_plan(species, height_m, crown_m)
    atlas = leaf_atlas(species)
    card = leaf_card(species, plan["card_m"], atlas)   # the same material as the leaf cards (one per species)
    leaf_mat = card.data.materials[0]
    before = set(bpy.data.objects)
    bpy.ops.curve.tree_add(**args)
    new = [o for o in bpy.data.objects if o not in before]
    tree_ob = next((o for o in new if o.type == "CURVE"), None)
    if tree_ob is None:
        for o in new:
            bpy.data.objects.remove(o)
        raise RuntimeError("Sapling made no curve object")
    leaves = next((o for o in new if o.type == "MESH" and o.parent == tree_ob), None)
    leaf_faces = len(leaves.data.polygons) if leaves is not None else 0
    if leaf_faces == 0:
        for o in new:
            bpy.data.objects.remove(o)
        raise RuntimeError(f"Sapling made 0 leaf faces (preset {preset_name}, leaves {args.get('leaves')}, "
                           f"showLeaves {args.get('showLeaves')}): leaf-card crown instead")
    for o in new:
        _unlink_everywhere(o)
        if o is card:
            continue
        (collection or bpy.context.scene.collection).objects.link(o)
    tree_ob.name = name
    tree_ob.data.materials.append(bark_material())
    # the drawn height exactly: measure the generated top (curve points and leaves) and scale the tree to it
    zs = [p.co.z for sp in tree_ob.data.splines for p in sp.bezier_points]
    zs += [v.co.z for v in leaves.data.vertices]
    top = max(zs) if zs else 0.0
    post = float(height_m) / top if top > 0.1 else 1.0
    tree_ob.scale = (post, post, post)
    leaves.name = f"{name}_leaves"
    leaves["wenart_kind"] = "site_decor_part"
    leaves.data.materials.clear()
    leaves.data.materials.append(leaf_mat)
    leaves["wenart_leaf_faces"] = leaf_faces
    _tag(tree_ob, "site_decor", rec["name"], "sapling", preset_name, "GPL add-on output (ours)", height_m)
    tree_ob["wenart_leaf_faces"] = leaf_faces
    return tree_ob, {"method": "sapling", "preset": preset_name, "scale": args.get("scale"),
                     "generated_top_m": round(top, 3), "post_scale": round(post, 4), "material": leaf_mat.name,
                     "atlas": atlas["id"] if atlas else None, "licence": atlas["licence"] if atlas else None,
                     "leaves": True, "leaf_faces": leaf_faces, "leaf_shape": args.get("leafShape"),
                     "leaf_m": args.get("leafScale"), "leaves_per_branch": args.get("leaves")}


def _tree_hero(name: str, species: str, height_m: float, seed: int, collection, hero: dict):
    """A collection instance of an imported Poly Haven tree (bpy), scaled to ``height_m``, turned by the seed."""
    import bpy
    lib = _import_hero(hero)
    if lib is None:
        raise RuntimeError(f"{hero['id']}: glTF import failed")
    if lib["count"] >= HERO_MAX_PER_SPECIES:
        raise RuntimeError(f"{hero['id']}: {HERO_MAX_PER_SPECIES} instances already (HERO_MAX_PER_SPECIES)")
    col = bpy.data.collections[lib["collection"]]
    ob = bpy.data.objects.new(name, None)
    ob.instance_type = "COLLECTION"
    ob.instance_collection = col
    s = float(height_m) / float(lib["height_m"])
    ob.scale = (s, s, s)
    ob.rotation_euler = (0.0, 0.0, random.Random(seed).uniform(0.0, 2 * math.pi))
    (collection or bpy.context.scene.collection).objects.link(ob)
    lib["count"] += 1
    _tag(ob, "site_decor", species_record(species)["name"], "polyhaven", hero["id"], hero["licence"], height_m)
    ob["wenart_base_offset"] = -float(lib["base_z"]) * s
    return ob, {"method": "polyhaven", "asset": hero["id"], "licence": hero["licence"], "licence_url": hero["licence_url"],
                "model_height_m": lib["height_m"], "scale": round(s, 4), "polycount": hero.get("polycount"),
                "material": None, "name": hero.get("name")}


def scan_library(hero: dict) -> Optional[dict]:
    """The imported Poly Haven model of ``hero`` (bpy; imported once, shared with the hero trees near the cameras):
    ``{"collection", "height_m", "width_m", "base_z", "count"}``, else None when the import failed."""
    return _import_hero(hero)


def context_instance(name: str, lib: dict, position, scale, yaw: float, parent, collection,
                     hidden_rays: Sequence[str] = ()):
    """One horizon-context tree (bpy; 27 Oct 2026): a collection instance of the imported scan ``lib``
    (``scan_library``), its base on ``position``, scaled by ``scale`` (x, y, z), turned by ``yaw``, a child of
    ``parent``, hidden from ``hidden_rays`` (Cycles takes an instance's ray visibility as its own AND its
    instancer's, so the scan near the cameras keeps its own). No ``HERO_MAX_PER_SPECIES`` cap: instances share the
    one mesh."""
    import bpy
    ob = bpy.data.objects.new(name, None)
    ob.instance_type = "COLLECTION"
    ob.instance_collection = bpy.data.collections[lib["collection"]]
    sx, sy, sz = (float(v) for v in scale)
    ob.scale = (sx, sy, sz)
    ob.rotation_euler = (0.0, 0.0, float(yaw))
    ob.location = (float(position[0]), float(position[1]), float(position[2]) - float(lib["base_z"]) * sz)
    (collection or bpy.context.scene.collection).objects.link(ob)
    if parent is not None:
        ob.parent = parent
    for attr in hidden_rays:
        if hasattr(ob, attr):
            setattr(ob, attr, False)
    ob["wenart_kind"] = "site_decor_part"
    return ob


_LIBRARY: dict = {}


def library_plant(species: str, levers: Optional[dict] = None) -> Optional[dict]:
    """The library model of a species (``site_models.plant_model`` over the catalogue's extras, in the run's licence
    mode) with its file in the assets folder: ``{"id", "path", "height_m", "licence", ...}``, else None (24 Oct 2026:
    the library's trees, palms and bushes before the scans and the generated trees). The lever ``library`` False
    (or ``WENART_SITE_LIBRARY=off``) turns it off."""
    if (levers or {}).get("library") is False or \
            str(os.environ.get("WENART_SITE_LIBRARY") or "").strip().lower() in ("off", "0", "no", "false"):
        return None
    from wenart.blender import site_models as SM
    if "extras" not in _LIBRARY:
        try:
            data = json.loads((Path(__file__).resolve().parents[1] / "furniture" / "catalog_library.json")
                              .read_text(encoding="utf-8"))
            _LIBRARY["extras"] = list(data.get("extras") or [])
        except (OSError, ValueError):
            _LIBRARY["extras"] = []
    rec = species_record(species)
    mode = str(os.environ.get("WENART_LICENCE_MODE") or "relaxed").strip().lower()
    key = (rec["name"], mode)
    if key not in _LIBRARY:
        _LIBRARY[key] = SM.plant_model(rec, _LIBRARY["extras"], mode)
    pick = _LIBRARY[key]
    folder = assets_dir()
    if pick is None or folder is None:
        return None
    path = Path(folder) / pick["asset"]["glb"]
    if not path.is_file():
        return None
    box = pick["asset"].get("bbox_m") or [1.0, 1.0, 1.0]
    return {"id": pick["asset"]["asset_id"], "path": str(path), "height_m": float(box[2]),
            "base_z": float((pick["asset"].get("bbox_min_m") or [0, 0, 0])[2]),
            "licence": pick["asset"].get("licence"), "licence_url": pick["asset"].get("licence_url"),
            "licence_flag": pick["asset"].get("licence_flag"), "attribution": pick["asset"].get("attribution"),
            "polycount": pick["asset"].get("polycount"), "name": pick["asset"].get("title"),
            "match": pick["match"], "reason": pick["reason"]}


PLANT_PALE = {"saturation": 0.12, "value": 0.5}     # an untextured leaf material this pale is the importer's white
BARK_WORDS = ("trunk", "bark", "wood", "stem", "branch", "stamm", "tronco")


def _image_has_cutout(image) -> bool:
    """Whether an image carries transparent texels (alpha under 0.5 somewhere; sampled)."""
    try:
        if image is None or int(image.channels) < 4 or image.alpha_mode == "NONE":
            return False
        n = len(image.pixels)
        if n == 0:
            return False
        step = max(4, (n // 4 // 4096) * 4)            # about 4,096 texels
        px = image.pixels[:]
        return any(px[i] < 0.5 for i in range(3, n, step))
    except Exception:                                 # an unloaded or broken image: leave it
        return False


KEY_BACKGROUND = {"spread": 0.06, "bright": 0.85, "dark": 0.06, "saturation": 0.12, "border": 24,
                  "from": 0.08, "to": 0.2}


def image_background(image) -> Optional[tuple]:
    """27 Oct 2026: the flat background colour of a leaf texture exported without alpha (``KEY_BACKGROUND``: the
    texels sampled along its border all within ``spread`` of their mean, which is near white or near black and grey),
    else None (a texture that fills its frame: bark, a photo of foliage)."""
    import colorsys
    try:
        w, h = (int(v) for v in image.size)
        ch = int(image.channels)
        if w < 4 or h < 4 or ch < 3:
            return None
        px = image.pixels[:]
        n = int(KEY_BACKGROUND["border"])
        pts = [(int(round(i * (w - 1) / n)), y) for i in range(n + 1) for y in (0, h - 1)]
        pts += [(x, int(round(i * (h - 1) / n))) for i in range(1, n) for x in (0, w - 1)]
        cols = [tuple(px[(y * w + x) * ch + k] for k in range(3)) for x, y in pts]
    except Exception:  # noqa: BLE001 - an unloaded or broken image: no key
        return None
    mean = tuple(sum(c[k] for c in cols) / len(cols) for k in range(3))
    if max(max(abs(c[k] - mean[k]) for k in range(3)) for c in cols) > KEY_BACKGROUND["spread"]:
        return None
    _hh, sat, val = colorsys.rgb_to_hsv(*mean)
    if sat > KEY_BACKGROUND["saturation"] or KEY_BACKGROUND["dark"] < val < KEY_BACKGROUND["bright"]:
        return None
    return mean


def _key_alpha(tree, tex, bsdf, colour) -> None:
    """Alpha = the texel's distance from the background ``colour``, mapped from ``KEY_BACKGROUND["from"]`` (0) to
    ``["to"]`` (1)."""
    dist = tree.nodes.new("ShaderNodeVectorMath")
    dist.operation = "DISTANCE"
    tree.links.new(tex.outputs["Color"], dist.inputs[0])
    dist.inputs[1].default_value = tuple(float(c) for c in colour)
    ramp = tree.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value = KEY_BACKGROUND["from"]
    ramp.inputs["From Max"].default_value = KEY_BACKGROUND["to"]
    tree.links.new(dist.outputs["Value"], ramp.inputs["Value"])
    tree.links.new(ramp.outputs["Result"], bsdf.inputs["Alpha"])


def fix_plant_materials(objects, species: str) -> dict:
    """Make a library plant's materials read as foliage (bpy; 24 Oct 2026: real04's 21 library bushes rendered white).
    3D Warehouse plants are leaf cards whose texture has a transparent background, often exported opaque: the image's
    alpha is wired to the Principled BSDF's Alpha where nothing drives it; a texture with no alpha on a flat white or
    black background (``image_background``) gets that background keyed out (27 Oct 2026). An untextured material as pale as the
    importer's white (``PLANT_PALE``) takes the species' foliage colour (its bark colour when the name says trunk /
    bark / wood). Returns ``{"cutout": [...], "tinted": [...], "keyed": [...]}``; each material is changed once
    (``wenart_plant_fix``)."""
    import colorsys
    rec = species_record(species)
    out = {"cutout": [], "tinted": [], "keyed": [], "textured": [], "flat": []}
    seen = set()
    for ob in objects:
        if getattr(ob, "type", None) != "MESH":
            continue
        for slot in ob.material_slots:
            mat = slot.material
            if mat is None or mat.name in seen or getattr(mat, "node_tree", None) is None:
                continue
            seen.add(mat.name)
            if mat.get("wenart_plant_fix"):
                continue
            mat["wenart_plant_fix"] = 1
            nodes, links = mat.node_tree.nodes, mat.node_tree.links
            bsdf = next((n for n in nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
            if bsdf is None:
                continue
            texs = [n for n in nodes if n.bl_idname == "ShaderNodeTexImage" and n.image is not None]
            out["textured" if texs else "flat"].append(mat.name)
            if texs:
                tex = next((t for t in texs if _image_has_cutout(t.image)), None)
                if tex is not None and not bsdf.inputs["Alpha"].links:
                    links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
                    out["cutout"].append(mat.name)
                elif tex is None and not bsdf.inputs["Alpha"].links \
                        and not any(w in mat.name.lower() for w in BARK_WORDS):
                    # 27 Oct 2026: a leaf card exported without alpha on a flat white or black background (a dotted
                    # disc in the render): the background is keyed out
                    for t in texs:
                        bg = image_background(t.image)
                        if bg is not None:
                            _key_alpha(mat.node_tree, t, bsdf, bg)
                            out["keyed"].append(mat.name)
                            break
                continue
            if bsdf.inputs["Base Color"].links:
                continue
            r, g, b, _a = bsdf.inputs["Base Color"].default_value
            _h, sat, val = colorsys.rgb_to_hsv(r, g, b)
            if sat < PLANT_PALE["saturation"] and val > PLANT_PALE["value"]:
                bark = any(w in mat.name.lower() for w in BARK_WORDS)
                col = (0.10, 0.07, 0.05) if bark else tuple(rec["colour"])
                bsdf.inputs["Base Color"].default_value = (*col, 1.0)
                out["tinted"].append(mat.name)
    return out


def scan_first(model: dict, near_camera: bool, levers: Optional[dict], species: str,
               hero_of: Callable = None) -> bool:
    """27 Oct 2026 (pod run 224516: the inferred olives near the cameras were a 3D Warehouse model titled "tree", a flat
    dotted disc on a stick in the window views): near the cameras, a library plant matched only by its crown or its
    kind (``site_models.plant_model``'s ``match`` not ``species``) gives way to the species' Poly Haven scan when the
    assets hold it (``hero_model``) and the ``instances`` lever is on; a library model of the species itself (a real
    olive) stays first (pure but for the assets lookup)."""
    if not near_camera or model.get("match") == "species" or (levers or {}).get("instances", True) is False:
        return False
    return (hero_of or hero_model)(species) is not None


def flat_near_camera(near_camera: bool, material_fix: Optional[dict]) -> Optional[str]:
    """27 Oct 2026 (pod run 091638: the judge saw "lollipop" trees in the windows; the near "parasol pines" were a 3D
    Warehouse model of flat-coloured discs): why a library plant may not stand near the cameras (none of its materials
    holds an image texture: CLAUDE.md wants leaf textures), else None (pure)."""
    fix = material_fix or {}
    if not near_camera or fix.get("textured") or not fix.get("flat"):
        return None
    return (f"no leaf texture: its {len(fix['flat'])} material(s) are flat colours, a stylised model near the "
            f"cameras")


def _tree_library(name: str, species: str, height_m: float, seed: int, collection, model: dict):
    """A collection instance of a library plant (bpy), scaled to ``height_m``, turned by the seed."""
    import bpy
    lib = _import_hero(model)
    if lib is None:
        raise RuntimeError(f"{model['id']}: glTF import failed")
    if "plant_fix" not in lib:
        lib["plant_fix"] = fix_plant_materials(bpy.data.collections[lib["collection"]].all_objects, species)
    ob = bpy.data.objects.new(name, None)
    ob.instance_type = "COLLECTION"
    ob.instance_collection = bpy.data.collections[lib["collection"]]
    s = float(height_m) / float(lib["height_m"])
    ob.scale = (s, s, s)
    ob.rotation_euler = (0.0, 0.0, random.Random(seed).uniform(0.0, 2 * math.pi))
    (collection or bpy.context.scene.collection).objects.link(ob)
    lib["count"] += 1
    _tag(ob, "site_decor", species_record(species)["name"], "library", model["id"], model["licence"], height_m)
    ob["wenart_base_offset"] = -float(lib["base_z"]) * s
    return ob, {"method": "library", "asset": model["id"], "licence": model["licence"],
                "licence_url": model.get("licence_url"), "licence_flag": model.get("licence_flag"),
                "attribution": model.get("attribution"), "model_height_m": lib["height_m"], "scale": round(s, 4),
                "polycount": model.get("polycount"), "material": None, "name": model.get("name"),
                "match": model.get("match"), "inferred": True, "reason": model.get("reason"),
                "material_fix": lib.get("plant_fix")}


def tree_object(species: str, height_m: float, seed: int, near_camera: bool, *, collection=None,
                name: Optional[str] = None, position=(0.0, 0.0, 0.0), levers: Optional[dict] = None,
                crown_m: Optional[float] = None) -> tuple:
    """One tree of ``species`` at ``height_m`` (bpy; Milestone 13 T6): the source by ``tree_source`` (a Poly Haven
    instance near the cameras, a Sapling tree elsewhere, a leaf-card tree or a palm as the fallback; never a
    primitive). ``position`` is the ground point (x, y, z); ``levers`` the site levers (``instances``,
    ``sapling``). Returns ``(object, record)``: the record names ``method``, ``asset``, ``licence`` and the
    numbers of the build; the object carries ``wenart_species`` / ``wenart_veg_method`` / ``wenart_asset``."""
    rec = species_record(species)
    name = name or f"tree_{rec['name']}_{int(seed)}"
    model = library_plant(rec["name"], levers)
    if model is not None and scan_first(model, near_camera, levers, rec["name"]):
        model = None              # 27 Oct 2026: the photoscan near the cameras before a generic library tree
    flat_why = None
    if model is not None:
        try:
            ob, out = _tree_library(name, rec["name"], height_m, seed, collection, model)
            flat_why = flat_near_camera(near_camera, out.get("material_fix"))
            if flat_why is None:
                ob.location = (float(position[0]), float(position[1]),
                               float(position[2]) + float(ob.get("wenart_base_offset") or 0.0))
                return ob, out
            import bpy                                # 27 Oct 2026: a flat-coloured model near a camera: the next
            bpy.data.objects.remove(ob, do_unlink=True)   # source (the scan, Sapling, cards)
            print(f"{name}: library plant {model['id']}: {flat_why}; the next source")
        except Exception as exc:                      # a broken file: the earlier sources
            print(f"{name}: library plant {model['id']} failed ({type(exc).__name__}: {exc}); the next source")
    hero = hero_model(rec["name"])
    sap = levers is None or levers.get("sapling", True)
    sapling_rec = ensure_sapling() if sap else None
    sapling_ok = bool(sap and sapling_rec and sapling_rec["ok"])
    src = tree_source(rec["name"], near_camera, levers, hero, sapling_ok)
    # pre-flight of pod P3: a planned source that is missing (no Poly Haven model in the assets, no Sapling add-on)
    # is recorded with the reason; the 20 real04 shrubs near the cameras became leaf cards with no word of why
    extra: dict = missing_source(rec["name"], near_camera, levers, hero, sapling_rec)
    if flat_why is not None:
        extra = dict(extra, fallback_from="library", fallback_reason=f"{model['id']}: {flat_why}")
    sapling_possible = sapling_ok and (rec.get("source") or {}).get("sapling") in SAPLING_PRESETS \
        and rec.get("crown") not in ("shrub", "hedge", "palm")
    if src == "polyhaven":
        try:
            ob, out = _tree_hero(name, rec["name"], height_m, seed, collection, hero)
            ob.location = (float(position[0]), float(position[1]),
                           float(position[2]) + float(ob.get("wenart_base_offset") or 0.0))
            return ob, out
        except RuntimeError as exc:                   # the cap or a failed import: the next source
            extra = {"fallback_from": "polyhaven", "fallback_reason": str(exc)}
            src = "sapling" if sapling_possible else ("palm" if rec.get("crown") == "palm" else "cards")
    if src == "sapling":
        try:
            ob, out = _tree_sapling(name, rec["name"], height_m, seed, collection, crown_m)
            ob.location = (float(position[0]), float(position[1]), float(position[2]))
            return ob, dict(out, **extra)
        except Exception as exc:
            extra = {"fallback_from": "sapling", "fallback_reason": f"{type(exc).__name__}: {exc}"}
            src = "palm" if rec.get("crown") == "palm" else "cards"
    if src == "palm":
        ob, out = _tree_palm(name, height_m, seed, collection)
    else:
        ob, out = _tree_cards(name, rec["name"], height_m, seed, collection, crown_m)
    ob.location = (float(position[0]), float(position[1]), float(position[2]))
    return ob, dict(out, **extra)


def grass_patch(polygon: Sequence, density: float, *, collection=None, terrain: Optional[dict] = None,
                holes: Sequence = (), name: str = "grass_near", seed: int = 7, relief: bool = False,
                keep: Sequence = (), step: Optional[float] = None, reach: Optional[float] = None) -> tuple:
    """Grass clumps over ``polygon`` (bpy; Milestone 13 T6): a draped surface of the polygon minus ``holes``
    (``site.draped_faces``) carrying a geometry-nodes scatter of ``density`` clumps per m²: the Poly Haven clump
    (``grass_medium_02`` / ``grass_bermuda_01``, CC0) when the assets hold it, else the crossed grass cards. The
    surface itself is hidden from the render (the ground shows through). ``relief`` (fix round after P3): the
    surface gets the lawn's relief first (``lawn_relief``), so the clumps follow the lowered lawn. Fix round part 2
    (17 Oct 2026): ``keep`` and ``reach`` (the ground's keep polygons, ``site.relief_keep``, and its
    ``relief_reach``) leave the same places at their level and ``step`` (the ground's grid, ``site.grid_step`` of the
    ground's extent) puts the surface's vertices on the ground's, so the clumps follow the ground's own relief
    (measured in bpy 5.2.2: within -0.5 / +0.8 cm of it, 0.02 cm on average; 0.08 cm and down to -2.9 cm before);
    ``site.build_site`` asks for ``relief`` only when the ground got one. Returns ``(object, record)``."""
    import bpy
    from wenart.blender import site as S
    terrain = terrain or {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
    verts, faces = S.draped_faces(polygon, list(holes), terrain, lift=0.02, step=step)
    if not faces:
        raise ValueError("grass_patch: an empty lawn polygon")
    ob = _mesh_object(name, verts, faces, collection, [])
    ob.visible_camera = False
    ob.visible_shadow = False
    ob.visible_diffuse = False
    ob.visible_glossy = False
    ob.visible_transmission = False
    clump, asset, licence, method = None, None, None, "cards"
    manifest = assets_manifest()
    for aid in ("grass_medium_02", "grass_bermuda_01"):
        entry = (manifest.get("models") or {}).get(aid)
        folder = assets_dir()
        if isinstance(entry, dict) and folder is not None and (entry.get("files") or {}).get("gltf") \
                and (folder / entry["files"]["gltf"]).is_file():
            lib = _import_hero({"id": aid, "path": str(folder / entry["files"]["gltf"]),
                                "height_m": POLYHAVEN_MODELS[aid]["height_m"], "base_z": 0.0,
                                "licence": POLYHAVEN_LICENCE, "licence_url": POLYHAVEN_LICENCE_URL})
            if lib is not None:
                col = bpy.data.collections[lib["collection"]]
                clump = next((o for o in col.objects if o.type == "MESH"), None)
                asset, licence, method = aid, POLYHAVEN_LICENCE, "polyhaven"
                break
    if clump is None:
        clump = grass_card_object()
    scale = (0.6, 1.1) if method == "cards" else (0.25, 0.45)
    ng = scatter_group(f"veg_grass_{method}_{int(density)}", clump, float(density), seed, scale_range=scale,
                       tilt_deg=8.0, keep_surface=False, align_normal=True)
    relief_rec = None
    if relief:                                       # before the scatter: the clumps stand on the displaced surface
        relief_rec = lawn_relief(ob, pin_edges=False, keep=keep, reach=reach)
    mod = ob.modifiers.new("grass", "NODES")
    mod.node_group = ng
    from wenart import geometry as G
    area = G.polygon_area(polygon) - sum(G.polygon_area(h) for h in holes if len(h) >= 3 and all(
        G.point_in_polygon(q, polygon) for q in h))
    count = int(max(0.0, area) * float(density))
    _tag(ob, "site_grass", "lawn", method, asset, licence, 0.3)
    return ob, {"method": method, "asset": asset, "licence": licence, "density": float(density), "count": count,
                "area_m2": round(max(0.0, area), 2), "relief": bool(relief and (relief_rec or {}).get("applied")),
                "relief_weighted": (relief_rec or {}).get("weighted"), "keep_polygons": len(keep or ())}


# The lawn's look (round 3, P1 §14.3: every exterior view of real02 and real04 rendered the lawn as a flat saturated
# green). The committed real02 scene manifest records the ground material grass__Grass004 as textured (the ambientCG
# photo, size_m 1.4, albedo gain 0.585; review of round 3: the ground *object* entry's ``textured: false`` is the
# constant ``build_site`` writes for every site object, not the material's state): a 1.4 m tile of a uniform photo
# averages to one flat green a few metres from the camera, with nothing at the scale of metres to break it up.
# ``lawn_material`` gives the ground material a visible tiling of
# LAWN_TILE_M (the texture's Mapping scale clamped to 1-2 m), a mild albedo variation (a large Noise mixed into the
# base colour as a multiplier between ``dark`` and ``light``, with or without a texture) and a fine bump where no
# normal map is linked. Two noise nodes: no measurable cost (P1 exteriors 2-4 s, <= 13.4 GB).
LAWN_TILE_M = (1.0, 2.0)
LAWN_VARIATION = {"scale_per_m": 0.12, "detail": 3.0, "dark": (0.78, 0.84, 0.66), "light": (1.12, 1.06, 0.92),
                  "bump": 0.12, "bump_scale_per_m": 6.0}


def lawn_tile_m(size_m) -> float:
    """The tile size the lawn texture repeats at (pure): the texture set's longer side clamped to ``LAWN_TILE_M``
    (a 4 m photo repeats every 2 m, a 0.5 m one every metre); 1.5 m when no size is known."""
    try:
        side = max(float(v) for v in (size_m or []) if v is not None)
    except (TypeError, ValueError):
        side = 0.0
    if side <= 0:
        return 1.5
    return round(min(LAWN_TILE_M[1], max(LAWN_TILE_M[0], side)), 3)


# 27 Oct 2026 (pod run 130756: "a flat, untextured green plane" in the judge's findings of nearly every view): the 1-2 m
# texture and the 8 m variation average to one green beyond 30 m. The ground beyond ``near_m`` from the building
# (fading in to ``far_m``) gets field-scale patches (a noise of ``scale_per_m``: patches of about 80 m) tinted by the
# climate's ``tint`` (a dry meadow in a Mediterranean climate, a lusher, darker one in a temperate one) through a ramp
# from ``lo`` (no tint) to ``hi`` (the full tint): the fields read as fields, the lawn by the house stays a lawn.
LAWN_FIELDS = {"scale_per_m": 0.012, "detail": 2.0, "lo": 0.46, "hi": 0.62, "near_m": 25.0, "far_m": 60.0,
               "tint": {"mediterranean": (1.20, 1.06, 0.60), "temperate": (0.84, 0.96, 0.78)}}
LAWN_BOUNCE_DESAT = 0.75            # share of the lawn's bounced light turned grey (the camera sees the lawn as is)
# 26 Oct 2026 (real06): the Light Path output that tells a bounced ray (Blender 5.2 manual, Light Path node: "Diffuse
# Depth: how many times the ray has undergone diffuse reflection or transmission"): 0 for the camera's own paths,
# through a window pane and in a mirror too (``lawn_material``)
LAWN_OWN_COLOUR_RAYS = "Diffuse Depth"


def lawn_material(mat, fields_centre: Optional[Sequence[float]] = None, climate: str = "temperate") -> dict:
    """Give the ground's grass material its lawn look (bpy; round 3; idempotent): the texture's Mapping node scaled
    to ``lawn_tile_m`` of its current tile, a Noise texture (Object coordinates, ``LAWN_VARIATION``) through a
    ColorRamp from ``dark`` to ``light`` multiplied into whatever feeds the Principled BSDF's Base Color (the texture
    or the flat colour), and a fine Bump where the Normal input is free. With ``fields_centre`` (the building's centre,
    27 Oct 2026) the field-scale patches of ``LAWN_FIELDS`` in the ``climate``'s tint beyond ``near_m`` from it.
    Returns the record for the manifest: ``{"tile_m", "textured", "variation", "bump", "fields", "applied"}``;
    ``applied`` False with the reason when the material has no node tree or no Principled BSDF."""
    import json as _json
    # the node tree alone decides: Material.use_nodes is deprecated in Blender 5.x (always on) and goes in 6.0
    if mat is None or getattr(mat, "node_tree", None) is None:
        return {"applied": False, "reason": "no node tree"}
    if mat.get("wenart_lawn"):
        try:
            return dict(_json.loads(mat["wenart_lawn"]), applied=True)
        except (TypeError, ValueError):
            return {"applied": True}
    tree = mat.node_tree
    nodes, links = tree.nodes, tree.links
    bsdf = next((n for n in nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    if bsdf is None:
        return {"applied": False, "reason": "no Principled BSDF"}
    mapping = next((n for n in nodes if n.bl_idname == "ShaderNodeMapping"), None)
    tile = None
    if mapping is not None:
        sx, sy = float(mapping.inputs["Scale"].default_value[0]), float(mapping.inputs["Scale"].default_value[1])
        tile = lawn_tile_m([1.0 / sx if sx > 1e-9 else 0.0, 1.0 / sy if sy > 1e-9 else 0.0])
        mapping.inputs["Scale"].default_value = (1.0 / tile, 1.0 / tile, 1.0)
    cfg = LAWN_VARIATION
    coord = _node(tree, "ShaderNodeTexCoord")
    noise = _node(tree, "ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = float(cfg["scale_per_m"])
    noise.inputs["Detail"].default_value = float(cfg["detail"])
    links.new(coord.outputs["Object"], noise.inputs["Vector"])
    ramp = _node(tree, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*cfg["dark"], 1.0)
    ramp.color_ramp.elements[1].color = (*cfg["light"], 1.0)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    mix = _node(tree, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
    mix.inputs["Factor"].default_value = 1.0
    base = bsdf.inputs["Base Color"]
    if base.links:
        src = base.links[0].from_socket
        links.remove(base.links[0])
        links.new(src, mix.inputs[6])
    else:
        mix.inputs[6].default_value = tuple(base.default_value)
    links.new(ramp.outputs["Color"], mix.inputs[7])
    colour = mix.outputs[2]
    fields = None
    if fields_centre is not None:
        f = LAWN_FIELDS
        tint = f["tint"].get(climate) or f["tint"]["temperate"]
        fnoise = _node(tree, "ShaderNodeTexNoise")
        fnoise.inputs["Scale"].default_value = float(f["scale_per_m"])
        fnoise.inputs["Detail"].default_value = float(f["detail"])
        links.new(coord.outputs["Object"], fnoise.inputs["Vector"])
        framp = _node(tree, "ShaderNodeValToRGB")
        lo, hi = framp.color_ramp.elements[0], framp.color_ramp.elements[1]
        lo.position, lo.color = float(f["lo"]), (1.0, 1.0, 1.0, 1.0)
        hi.position, hi.color = float(f["hi"]), (*tint, 1.0)
        links.new(fnoise.outputs["Fac"], framp.inputs["Fac"])
        off = _node(tree, "ShaderNodeVectorMath", operation="SUBTRACT")
        links.new(coord.outputs["Object"], off.inputs[0])
        off.inputs[1].default_value = (float(fields_centre[0]), float(fields_centre[1]), 0.0)
        dist = _node(tree, "ShaderNodeVectorMath", operation="LENGTH")
        links.new(off.outputs["Vector"], dist.inputs[0])
        fade = _node(tree, "ShaderNodeMapRange")
        links.new(dist.outputs["Value"], fade.inputs["Value"])
        fade.inputs["From Min"].default_value = float(f["near_m"])
        fade.inputs["From Max"].default_value = float(f["far_m"])
        fade.inputs["To Min"].default_value = 0.0
        fade.inputs["To Max"].default_value = 1.0
        fmix = _node(tree, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY")
        links.new(fade.outputs["Result"], fmix.inputs["Factor"])
        links.new(colour, fmix.inputs[6])
        links.new(framp.outputs["Color"], fmix.inputs[7])
        colour = fmix.outputs[2]
        fields = {"centre": [round(float(fields_centre[0]), 3), round(float(fields_centre[1]), 3)],
                  "climate": climate if climate in f["tint"] else "temperate", "tint": list(tint),
                  "patch_m": round(1.0 / float(f["scale_per_m"]), 1), "from_m": [f["near_m"], f["far_m"]]}
    # 24 Oct 2026 (real04: the walls under the eaves read yellow-olive, lit mostly by the sunlit lawn): the light
    # the lawn bounces is desaturated by LAWN_BOUNCE_DESAT; the camera sees the lawn's own colour.
    # 26 Oct 2026 (real06, "the view out the window is a flat grey void"): the factor was 1 - Is Camera Ray, but the
    # camera's ray through a window pane is a transmission ray after the glass, so every window showed the lawn 75 %
    # grey. LAWN_OWN_COLOUR_RAYS: the lawn keeps its colour on every path without a diffuse bounce (Light Path
    # 'Diffuse Depth' 0: the camera, the view through a pane, a mirror or a glossy reflection) and is grey only for
    # the light it bounces onto a diffuse surface (the walls, the rooms): factor = LAWN_BOUNCE_DESAT x min(Diffuse
    # Depth, 1).
    path = _node(tree, "ShaderNodeLightPath")
    grey = _node(tree, "ShaderNodeRGBToBW")
    links.new(colour, grey.inputs["Color"])
    bounced = _node(tree, "ShaderNodeMath", operation="MINIMUM")
    links.new(path.outputs[LAWN_OWN_COLOUR_RAYS], bounced.inputs[0])
    bounced.inputs[1].default_value = 1.0
    fac = _node(tree, "ShaderNodeMath", operation="MULTIPLY")
    links.new(bounced.outputs[0], fac.inputs[0])
    fac.inputs[1].default_value = LAWN_BOUNCE_DESAT
    bounce = _node(tree, "ShaderNodeMix", data_type="RGBA", blend_type="MIX")
    links.new(fac.outputs[0], bounce.inputs["Factor"])
    links.new(colour, bounce.inputs[6])
    links.new(grey.outputs["Val"], bounce.inputs[7])
    links.new(bounce.outputs[2], base)
    bump = False
    if not bsdf.inputs["Normal"].links:
        fine = _node(tree, "ShaderNodeTexNoise")
        fine.inputs["Scale"].default_value = float(cfg["bump_scale_per_m"])
        fine.inputs["Detail"].default_value = 2.0
        links.new(coord.outputs["Object"], fine.inputs["Vector"])
        bnode = _node(tree, "ShaderNodeBump")
        bnode.inputs["Strength"].default_value = float(cfg["bump"])
        links.new(fine.outputs["Fac"], bnode.inputs["Height"])
        links.new(bnode.outputs["Normal"], bsdf.inputs["Normal"])
        bump = True
    rec = {"tile_m": tile, "textured": mapping is not None, "variation": [list(cfg["dark"]), list(cfg["light"])],
           "noise_scale_per_m": cfg["scale_per_m"], "bump": bump, "bounce_desaturation": LAWN_BOUNCE_DESAT,
           "own_colour_rays": f"{LAWN_OWN_COLOUR_RAYS} 0", "fields": fields}
    mat["wenart_lawn"] = _json.dumps(rec)
    return dict(rec, applied=True)


# Fix round after P3 (16-17 Oct 2026; P3's real04 ext_3 / ext_7: green lawn blobs poked through the paved paths).
# What: the far lawn's relief only goes down (Displace mid level 1: offset = (texture - 1) x strength, 0 .. -strength)
# and the ground's edges keep their level (a vertex group without the boundary vertices: the edges along the building,
# the platforms, the light wells, the pools and the ground's rim). Why: the Milestone 13 relief (strength 0.06 m, mid
# level 0.5) lifted the lawn up to 3 cm, over the draped paths and parking (site.PAVING_LIFT = 1.2 cm) and the grass
# areas (0.4 cm). How: ``relief_range`` and ``relief_weights`` are pure (tests/test_m13_site.py); the grass clumps'
# surface gets the same relief (``grass_patch(..., relief=True)``), so the clumps stay on the lowered lawn.
#
# Fix round part 2 (17 Oct 2026; review of part 1). What: the relief also leaves the ground at its level under and
# around every object that stands on the terrain (``keep``: the polygons ``site.relief_keep`` collects: the ground's
# holes, the draped areas, the sloped platforms, the inferred entrance steps, every tree, shrub and hedge footprint):
# every ground vertex inside a keep polygon or within ``relief_reach`` of it (``RELIEF_KEEP["margin_m"]`` plus a grid
# cell's diagonal: every face that comes within the margin stays level as a whole) gets weight 0. The grass surface
# gets the same keep polygons and reach on the ground's grid (``grass_patch(..., keep=, step=, reach=)``: its vertices
# are the ground's, with the same weights), and the relief only where the ground got one (``site.build_site``: a flat
# ground of convex pieces has no inner vertex, so no relief, and its grass gets none either). Why: measured in
# the bpy 5.2.2 module on a sloped synthetic site, the down-only relief (mean -1.8 cm, up to -3.4 cm, 92 % of the
# vertices moved) left a draped path and a sloped parking 2.1 / 2.0 cm (up to 3.0 cm) over the lawn with no edge under
# them and a shrub's and a tree's base 2.6 / 2.8 cm in the air; on a flat site the grass clumps sat 2.1 cm in the
# lawn. How: ``relief_weights(..., verts=, keep=, reach=)`` is pure (the vertices in buckets, each keep polygon
# tested against the vertices near it); ``lawn_relief`` returns its record (``weighted``: the vertices that move; no
# modifier when none does).
LAWN_RELIEF = {"strength_m": 0.04, "mid_level": 1.0, "scale": 2.5}
LAWN_RELIEF_GROUP = "lawn_relief"
RELIEF_KEEP = {"margin_m": 0.3, "bucket_m": 4.0}


def relief_range(strength_m: float = LAWN_RELIEF["strength_m"], mid_level: float = LAWN_RELIEF["mid_level"]
                 ) -> tuple[float, float]:
    """``(lowest, highest)`` offset of the lawn relief in metres (pure): Blender's Displace modifier moves a vertex
    by ``(texture value - mid level) x strength`` along Z, the Clouds texture's value lies in 0..1."""
    lo, hi = (0.0 - float(mid_level)) * float(strength_m), (1.0 - float(mid_level)) * float(strength_m)
    return round(min(lo, hi), 6), round(max(lo, hi), 6)


def _point_segment_distance(p, a, b) -> float:
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = dx * dx + dy * dy
    t = 0.0 if n <= 1e-18 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / n))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def _inside(p, poly) -> bool:
    """Even-odd point in polygon (pure; a point on an edge may go either way, the reach catches it)."""
    x, y = p
    inside = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def near_polygon(p, poly, reach: float) -> bool:
    """True when the point ``p`` lies inside the polygon or within ``reach`` of its edges (pure)."""
    if len(poly) >= 3 and _inside(p, poly):
        return True
    n = len(poly)
    return any(_point_segment_distance(p, poly[i], poly[(i + 1) % n]) <= reach for i in range(n))


def relief_reach(step_m: float, margin_m: Optional[float] = None) -> float:
    """How far from a keep polygon the ground's vertices stay level (pure; fix round part 2): ``margin_m``
    (``RELIEF_KEEP["margin_m"]``) plus the diagonal of a ground cell of ``step_m`` (``site.grid_step``), so every
    vertex of a ground face that comes within the margin of the polygon stays level, and with it every point of the
    face. The grass surface uses the same reach on the same grid (``grass_patch``), so its clumps follow the lawn."""
    m = float(RELIEF_KEEP["margin_m"] if margin_m is None else margin_m)
    return round(m + math.sqrt(2.0) * max(0.0, float(step_m)), 6)


def relief_weights(n_verts: int, faces: Sequence[Sequence[int]], verts: Optional[Sequence] = None,
                   keep: Sequence = (), reach: Optional[float] = None, pin_edges: bool = True) -> list[float]:
    """The relief's vertex weights (pure): 0 on a boundary vertex with ``pin_edges`` (one end of an edge only one face
    uses: the ground's rim and every hole's edge), so the ground meets the building, the platforms, the wells, the
    pools and the skirt at its own level; fix round part 2 (17 Oct 2026): 0 on every vertex (``verts``: x, y) inside
    a ``keep`` polygon or within ``reach`` of one (default ``RELIEF_KEEP["margin_m"]``; ``relief_reach`` for a ground
    mesh), so the ground under a draped path, a sloped platform, entrance steps, a tree, a shrub or a hedge keeps its
    level; 1 elsewhere."""
    n_verts = int(n_verts)
    zero: set = set()
    if pin_edges:
        count: dict = {}
        for f in faces:
            n = len(f)
            for k in range(n):
                a, b = int(f[k]), int(f[(k + 1) % n])
                key = (a, b) if a < b else (b, a)
                count[key] = count.get(key, 0) + 1
        zero = {v for key, c in count.items() if c == 1 for v in key}
    polys = [[(float(q[0]), float(q[1])) for q in poly] for poly in keep or () if len(poly) >= 3]
    if polys and verts is not None:
        r = float(RELIEF_KEEP["margin_m"] if reach is None else reach)
        cell = max(float(RELIEF_KEEP["bucket_m"]), r)
        buckets: dict = {}
        for i in range(n_verts):
            if i in zero:
                continue
            x, y = float(verts[i][0]), float(verts[i][1])
            buckets.setdefault((math.floor(x / cell), math.floor(y / cell)), []).append(i)
        for poly in polys:
            px, py = [q[0] for q in poly], [q[1] for q in poly]
            x0, y0, x1, y1 = min(px) - r, min(py) - r, max(px) + r, max(py) + r
            for bi in range(math.floor(x0 / cell), math.floor(x1 / cell) + 1):
                for bj in range(math.floor(y0 / cell), math.floor(y1 / cell) + 1):
                    for i in buckets.get((bi, bj), ()):
                        if i in zero:
                            continue
                        x, y = float(verts[i][0]), float(verts[i][1])
                        if x0 <= x <= x1 and y0 <= y <= y1 and near_polygon((x, y), poly, r):
                            zero.add(i)
    return [0.0 if i in zero else 1.0 for i in range(n_verts)]


def lawn_relief(ground_ob, strength: Optional[float] = None, scale: Optional[float] = None,
                pin_edges: bool = True, keep: Sequence = (), reach: Optional[float] = None) -> dict:
    """The far lawn's gentle relief (bpy): a Displace modifier with a Clouds texture on the ground mesh (no blades
    far from the cameras; the grass texture stays). Fix round after P3: down only (``LAWN_RELIEF``: mid level 1) and,
    with ``pin_edges``, only on the vertices of ``relief_weights`` (the vertex group ``LAWN_RELIEF_GROUP``). Fix round
    part 2 (17 Oct 2026): ``keep`` (``site.relief_keep``) leaves the vertices in and within ``reach`` of those
    polygons at their level too (the group then also holds without ``pin_edges``); no modifier when no vertex would
    move (a flat ground of convex pieces). Returns ``{"applied", "weighted", "vertices", "edges_kept",
    "keep_polygons", "reach_m"}`` (the object's ``wenart_lawn_relief``). Idempotent."""
    import bpy
    if ground_ob is None or ground_ob.type != "MESH":
        return {"applied": False, "weighted": 0, "reason": "no mesh"}
    if "lawn_relief" in ground_ob.modifiers or ground_ob.get("wenart_lawn_relief"):
        try:
            return json.loads(ground_ob["wenart_lawn_relief"])
        except (KeyError, TypeError, ValueError):
            return {"applied": "lawn_relief" in ground_ob.modifiers, "weighted": None}
    me = ground_ob.data
    keep = [p for p in keep or () if len(p) >= 3]
    grouped = bool(pin_edges or keep)
    if grouped:
        weights = relief_weights(len(me.vertices), [list(p.vertices) for p in me.polygons],
                                 verts=[(v.co.x, v.co.y) for v in me.vertices], keep=keep, reach=reach,
                                 pin_edges=pin_edges)
        inner = [i for i, w in enumerate(weights) if w > 0.0]
    else:
        inner = list(range(len(me.vertices)))
    rec = {"applied": bool(inner), "weighted": len(inner), "vertices": len(me.vertices), "edges_kept": bool(pin_edges),
           "keep_polygons": len(keep), "reach_m": float(RELIEF_KEEP["margin_m"] if reach is None else reach)}
    if not inner:
        rec["reason"] = "no vertex away from the ground's edges and the keep polygons (a flat ground of convex pieces)"
        ground_ob["wenart_lawn_relief"] = json.dumps(rec)
        return rec
    tex = bpy.data.textures.get("veg_lawn_relief") or bpy.data.textures.new("veg_lawn_relief", type="CLOUDS")
    tex.noise_scale = float(LAWN_RELIEF["scale"] if scale is None else scale)
    tex.noise_depth = 2
    mod = ground_ob.modifiers.new("lawn_relief", "DISPLACE")
    mod.texture = tex
    mod.strength = float(LAWN_RELIEF["strength_m"] if strength is None else strength)
    mod.mid_level = float(LAWN_RELIEF["mid_level"])
    mod.direction = "Z"
    if grouped:
        group = ground_ob.vertex_groups.get(LAWN_RELIEF_GROUP) or ground_ob.vertex_groups.new(name=LAWN_RELIEF_GROUP)
        group.add(inner, 1.0, "REPLACE")
        mod.vertex_group = group.name
    ground_ob["wenart_lawn_relief"] = json.dumps(rec)
    return rec
