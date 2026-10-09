"""Build the Blender scene from a building JSON (run inside Blender).

    blender -b --python wenart/blender/build.py -- --building outputs/<p>/building.json \
        --style outputs/<p>/style.json --assets assets --out outputs/<p>/scene \
        [--level L0] [--no-textures] [--preview-samples 16] [--proxies] [--camera-policy m5|search]

Writes into ``--out``: ``scene.blend``, ``scene.glb``, ``scene_manifest.json``
(every object with its wenart id, kind, status, the element evidence copied
from the JSON, material, textured/flat, assumed defaults; furniture pieces
with ``asset``, ``fit_scale``, ``method``, ``bbox_m`` and ``decor``; cameras
with the ids in their frustum; the pass-index table; door ray checks) and one
top-down orthographic PNG per level at 100 px/m (``level_<id>_top.png``).

Furniture (docs/milestone4.md §2): fitted library glTF assets from
``--assets`` on the drawn footprints, the parametric mesh when a piece has
no usable asset (``method: parametric (fallback: <reason>)``), the Milestone
3 proxy box for ``unknown`` pieces and for every piece with ``--proxies``;
decor items (``building.decor``) on their host pieces.

Nothing is added, moved or removed relative to the JSON: walls, openings,
rooms, furniture and decor come from the building file one to one; cameras
and lights are the only objects that are not elements and they carry
``wenart_status = assumed``.

Milestone 5 additions (docs/milestone5.md §2.7):

- ``build_fingerprint``: sha256 over the building file, the style file, the
  asset-manifest entries this build uses (without fetch times), the code
  that shapes the scene (``wenart/blender/*.py``, ``wenart/style/vocabulary.py``,
  ``wenart/geometry.py``, ``wenart/furniture/catalog.json``) and the build
  arguments. It is pure Python (no bpy) so ``cli build --reuse`` can check it
  without starting Blender, and it is written to the manifest.
- the scene property ``wenart_mood`` (the style's light mood; render.py
  picks the white-balance residual from it);
- ``preview_maps``: per level the top-down PNG with the area it covers
  (pixel ``u = (x - x0) / m``, ``v = (y1 - y) / m``);
- ``room_ids`` on every door, window and plain-opening entry (the rooms
  whose polygon edge carries the opening) and ``box3d`` (``{center, size,
  rotation_deg}``, the world box of the mesh as built) on every furniture,
  proxy and decor entry;
- one light portal per window (lighting.py) and camera-only window glass
  (materials.py).

Milestone 6 (docs/milestone6.md §4.2, §5):

- ``--camera-policy m5|search`` (default ``m5``, the Milestone 3-5 rules;
  ``search`` is the ray-cast camera search of ``cameras.plan_cameras``),
  part of the fingerprint and recorded as ``camera_policy``;
- the building and the style file enter the fingerprint as
  ``wenart.canonical.canonical_sha256`` (no volatile keys such as
  ``created_utc``), so a re-run pipeline that only changed a time stamp
  never rebuilds the scene; the furniture texture ids
  (``vocabulary.furniture_textures``) are referenced assets;
- the look package of §5: wall faces split at room corners, procedural wet
  tiles, soft bedding, veneer, bevel, door handles, skirting (shell.py),
  dim-room lights at the pole of inaccessibility (lighting.py); every new
  design-detail object or light has an ``assumed`` entry with ``parent``,
  ``kind`` and ``reason``.

Milestone 7 (docs/milestone7.md §6.4):

- stairs are fixed equipment: ``shell.plan_stairs`` / ``shell.build_stairs``
  build them (steps from the drawn lines, landing, rails, the ceiling
  opening and its capped shaft) and furniture.py never sees them
  (``furniture_building``); they count as parametric pieces in the
  ``furniture`` summary and are listed under ``stairs``;
- pieces with ``build: false`` are not built (furniture.py and
  ``build_stairs``); the summary lists them under ``not_built``;
- the building's ``site`` (plot walls, exterior areas, site decor) is never
  built; the manifest's ``site`` records what was left out
  (``site_summary``);
- virtual separators and doorless openings: see shell.py;
- §6.2: the rooms the camera policy gives no view (``search``: empty rooms
  below 2.5 m2, ``cameras.rooms_without_view``) are listed in the
  manifest's ``rooms_without_view`` with the reason and in ``warnings``;
- ``load_style`` never fills the profile's ``family`` from the default (only
  refit's library style filter reads it).

Milestone 8 (docs/milestone8.md §5): ``--lens-mm L`` (the brief's
``render.lens_mm``, 14-35; the orchestrator passes it when the brief sets a
number) gives every searched camera that lens; without it each room gets
``cameras.room_lens`` (18 mm, 16 mm in rooms narrower than 2.2 m). Part of
the fingerprint and recorded as ``lens_mm`` (null = the automatic rule);
every camera plan carries its own ``lens_mm`` and ``lens_rule``. The ``m5``
policy refuses it (its cameras keep the M5 24 mm lens).

Milestone 10 (docs/milestone10.md §1.6, §3.2, §3.3): the whole building.

- ``--variant <id>`` (default ``base``, part of the fingerprint): only the
  variant's levels are built (``views.variant_building``: an alternative
  level replaces its base level; slabs, roof and facade faces follow);
  cameras only for the rooms ``views.views_for`` renders (the base: every
  room but a second twin with ``render.twin_rooms: one``; an alternative:
  its ``rooms_changed``), the others listed in ``rooms_without_view`` with
  the reason; the manifest's ``variant`` holds ``rooms_changed`` /
  ``exterior_changed`` (the building's, else computed) and ``variants`` the
  same for every variant. ``--out`` stays explicit (the scheduler picks
  ``outputs/<p>/variants/<id>/scene`` for an alternative, §1.6b row 9).
- ``--brief <file>`` (a ``wenart.brief.load_brief`` result as JSON, or a
  values dict; ``cli build --brief`` writes it from ``brief.yaml``): the
  brief keys the build reads (``views.BUILD_BRIEF_KEYS``: ``site``,
  ``slab_thickness``, ``exterior``, ``render.exterior_views``,
  ``render.twin_rooms``); without it the building's stored brief and
  ``views.BRIEF_DEFAULTS`` (assumed). Their values (``brief_args``) are part
  of the fingerprint, and ``FINGERPRINT_CODE`` covers the build's import
  closure (tests/test_blender_build.py checks it).
- A building with ``slabs``, ``roof`` or ``variants`` (``is_whole_building``)
  is built whole: slab objects (``shell.slab_plan`` / ``build_slabs``:
  outline minus the stair openings, the brief's ``slab_thickness`` where
  none is given, assumed), walls running to the next floor, the floors above
  a stair cut so the stair arrives (no capped shaft), the roof
  (``roof.roof_model`` / ``build_roof``: the drawn planes, else
  ``roof.planes_for``; ``roof: null`` = ``roof.flat_roof``, assumed;
  terraces cut out, their walls ending at the parapet, ``roof.parapet_cuts``),
  the walls under it cut by its underside (knee walls, gable ends) and the
  ceilings there sloped, the outside looks (``exterior.resolve_looks``:
  documents > brief ``exterior:`` words > style > ``style.exterior_fallback``;
  the manifest's ``exterior_looks``), the drawn facade parts on the walls of
  their side (``facade_faces``), sills and balcony railings
  (``shell.build_outside_details``), the site (``site.site_plan`` /
  ``build_site``, brief ``site: full`` / ``ground``; the basement-door
  terrain and the light wells in the manifest's ``site``), the sun turned by
  the building's north and the exterior cameras ``ext_<n>``
  (``exterior.plan_exterior``; kind ``exterior`` in the manifest's camera
  list, the dropped ones in ``cameras_dropped`` with their
  ``dropped_reason``) when ``views_for`` says so. Every camera record has
  ``kind``, ``variant``, ``view``, ``sides``, ``region_id`` and
  ``dropped_reason`` (§1.6b row 11). Every value no drawing gives is in
  ``assumed``. The top-down previews hide the roof, the site and the
  exterior cameras. Other buildings keep the M3-M9 scene.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path


def _repo_root() -> Path:
    env = os.environ.get("WENART_REPO_ROOT")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


sys.path.insert(0, str(_repo_root()))

PREVIEW_PX_PER_M = 100
PREVIEW_MARGIN_M = 0.5
DEFAULT_PREVIEW_SAMPLES = 16

REPO_ROOT = _repo_root()
# Files whose content shapes scene.blend besides the inputs (docs/milestone5.md §2.7): the build script's import
# closure (tests/test_blender_build.py checks every wenart module it may import is covered) and the data files it
# reads. Milestone 10: the variants and views (views.py), the brief loader and its defaults (the values enter the
# fingerprint through brief_args too), the style package (vocabulary + track C's finishes and colours).
FINGERPRINT_CODE = ("wenart/blender/*.py", "wenart/style/*.py", "wenart/geometry.py", "wenart/canonical.py",
                    "wenart/furniture/catalog.json", "wenart/__init__.py", "wenart/views.py", "wenart/brief.py",
                    "wenart/defaults.yaml")
# Asset-manifest keys that change on every fetch without changing the asset.
FINGERPRINT_VOLATILE_KEYS = ("fetched_utc",)
STYLE_ASSET_SLOTS = ("floor", "walls", "ceiling", "wet_floor", "wet_walls", "trim", "door", "window_frame",
                     "textiles")
# docs/milestone6.md §4.2 (the same names as cameras.CAMERA_POLICIES; repeated here so
# the fingerprint helpers need no camera code).
CAMERA_POLICIES = ("m5", "search")
DEFAULT_CAMERA_POLICY = "m5"


def search_seconds(camera_plans: list[dict], policy: str) -> float | None:
    """The scene manifest's ``search_seconds``: the camera search wall time summed over the
    levels (§4.1 budget), None for the ``m5`` policy (no search)."""
    if policy != "search":
        return None
    from wenart.blender import camsearch  # numpy only; also runs inside Blender's Python
    return round(sum(camsearch.level_search_seconds(camera_plans).values()), 3)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="build.py")
    parser.add_argument("--building", required=True)
    parser.add_argument("--style")
    parser.add_argument("--assets")
    parser.add_argument("--out", required=True)
    parser.add_argument("--level", help="build only this level id")
    parser.add_argument("--no-textures", action="store_true", help="flat colours only")
    parser.add_argument("--preview-samples", type=int, default=DEFAULT_PREVIEW_SAMPLES)
    parser.add_argument("--no-preview", action="store_true")
    parser.add_argument("--no-glb", action="store_true")
    parser.add_argument("--proxies", action="store_true",
                        help="Milestone 3 proxy boxes for every furniture piece instead of assets")
    parser.add_argument("--camera-policy", default=DEFAULT_CAMERA_POLICY, choices=CAMERA_POLICIES,
                        help="m5 = the fixed camera rules of Milestones 3-5 (default); search = ray-cast search")
    parser.add_argument("--lens-mm", type=float, default=None,
                        help="lens of every searched camera (the brief's render.lens_mm, 14-35 mm); default: 18 mm, "
                             "16 mm in rooms narrower than 2.2 m")
    parser.add_argument("--variant", default="base",
                        help="the building variant to build (Milestone 10; base = the M9 scene)")
    parser.add_argument("--brief", default=None,
                        help="JSON of the project brief (a wenart.brief.load_brief result or a values dict; "
                             "Milestone 10); default: the building's stored brief and the defaults")
    parser.add_argument("--markers", action="store_true",
                        help="debug: draw the unverified stripes (Milestone 11 D3: the brief's markers_in_final, "
                             "default false = no stripes in any render)")
    return parser.parse_args(argv)


# --------------------------------------------------------------------------
# Build fingerprint (pure Python: cli.py checks it without Blender)
# --------------------------------------------------------------------------

def fingerprint_args(building: str, style: str | None = None, assets: str | None = None, level: str | None = None,
                     no_textures: bool = False, preview_samples: int | None = None, no_preview: bool = False,
                     no_glb: bool = False, proxies: bool = False, camera_policy: str = DEFAULT_CAMERA_POLICY,
                     lens_mm: float | None = None, variant: str = "base", brief: dict | None = None) -> dict:
    """The build arguments that enter the fingerprint, in one canonical form
    (``--out`` is left out: where the scene is written does not change it).
    ``lens_mm`` None = the automatic lens rule (Milestone 8); ``variant``
    (Milestone 10) the building variant; ``brief`` the brief values the
    build uses (``brief_args``; the file path is not part of it)."""
    return {"building": str(building), "style": str(style) if style else None,
            "assets": str(assets) if assets else None, "level": level, "no_textures": bool(no_textures),
            "preview_samples": DEFAULT_PREVIEW_SAMPLES if preview_samples is None else int(preview_samples),
            "no_preview": bool(no_preview), "no_glb": bool(no_glb), "proxies": bool(proxies),
            "camera_policy": str(camera_policy or DEFAULT_CAMERA_POLICY),
            "lens_mm": None if lens_mm is None else float(lens_mm), "variant": str(variant or "base"),
            "brief": brief or {}}


def load_brief_file(path: str | None) -> dict | None:
    """The ``--brief`` JSON (a ``load_brief`` result or a values dict), None without one."""
    if not path:
        return None
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"--brief {path}: not a JSON object")
    return data


def brief_args(building: dict, brief: dict | None = None) -> dict:
    """``{key: {"value", "assumed"}}`` of the brief keys the build reads (``views.BUILD_BRIEF_KEYS``; pure):
    from ``brief`` (``load_brief_file``), else the building's stored brief, else ``views.BRIEF_DEFAULTS``. The
    fingerprint holds them, so a changed brief rebuilds the scene."""
    from wenart import views as V

    out = {}
    for key in V.BUILD_BRIEF_KEYS:
        value, assumed = V.brief_value(building, brief, key)
        out[key] = {"value": value, "assumed": bool(assumed)}
    # Milestone 11 (docs/milestone11.md §17): the keys of decisions D3, D5 and D6 (wenart/views.py is another
    # track's file, so their defaults live here: M11_BRIEF_DEFAULTS, kept equal to wenart/defaults.yaml by
    # tests/test_m11_exterior.py).
    for key, default in M11_BRIEF_DEFAULTS.items():
        value, assumed = V.brief_value(building, brief, key)
        if value is None:
            value, assumed = default, True
        if key == "site_options.front_court" and isinstance(value, bool):
            value = "yes" if value else "no"                 # YAML reads a bare yes / no as a boolean
        if value not in M11_BRIEF_CHOICES.get(key, (value,)):
            value, assumed = default, True
        out[key] = {"value": value, "assumed": bool(assumed)}
    return out


# Milestone 11 (docs/milestone11.md §17, decisions D3, D5, D6): the brief keys and their defaults (wenart/defaults.yaml).
M11_BRIEF_DEFAULTS = {"markers_in_final": False, "roof_terraces": "auto", "site_options.front_court": "auto"}
M11_BRIEF_CHOICES = {"markers_in_final": (True, False), "roof_terraces": ("auto", "cut", "closed"),
                     "site_options.front_court": ("auto", "yes", "no")}


def _sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _style_for_fingerprint(style_path: str | None) -> dict:
    """The style a build would use (the file, else the default profile), quietly."""
    if style_path and Path(style_path).is_file():
        style = json.loads(Path(style_path).read_text(encoding="utf-8"))
        if isinstance(style, list):
            style = style[0] if style else {}
        return style
    return default_style()


def referenced_asset_ids(building: dict, style: dict) -> list[str]:
    """Asset ids a build of ``building`` with ``style`` reads from the asset
    manifest: the textures named by the style slots, its HDRI, and the
    furniture and decor models of the building."""
    ids: set[str] = set()
    for slot in STYLE_ASSET_SLOTS:
        entry = style.get(slot)
        if isinstance(entry, dict) and entry.get("asset"):
            ids.add(str(entry["asset"]))
    # Milestone 10 (track F): every texture the profile uses (accent wall, outside frames, cabinet and furniture
    # woods, worktops, handles, pots, the exterior looks; wenart.style.profile.assets_in_profile).
    try:
        from wenart.style.profile import assets_in_profile
        ids.update(str(asset_id) for _src, asset_id, _slug in assets_in_profile(style)["textures"])
    except (ImportError, AttributeError, TypeError):
        pass
    hdri = (style.get("lighting") or {}).get("hdri")
    if hdri:
        ids.add(str(hdri))
    items = list(building.get("furniture") or []) + list(building.get("decor") or [])
    for piece in building.get("furniture") or []:
        items.extend(piece.get("decor") or [])
    for item in items:
        asset = item.get("asset") if isinstance(item, dict) else None
        if isinstance(asset, dict) and asset.get("asset_id"):
            ids.add(str(asset["asset_id"]))
    # The furniture texture maps (veneers, linen; Milestone 6): every build may use them.
    try:
        from wenart.style.vocabulary import furniture_textures
        ids.update(asset_id for _, asset_id, _ in furniture_textures())
    except ImportError:
        pass
    return sorted(ids)


def asset_entries_for(assets_dir: str | None, ids: list[str]) -> dict:
    """``{section: {id: entry}}`` of the asset manifest for ``ids``, without fetch times."""
    if not assets_dir:
        return {}
    path = Path(assets_dir) / "manifest.json"
    if not path.is_file():
        return {"manifest": None}
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict = {}
    for section in ("textures", "hdris", "models"):
        for asset_id, entry in (data.get(section) or {}).items():
            if asset_id in ids and isinstance(entry, dict):
                clean = {k: v for k, v in entry.items() if k not in FINGERPRINT_VOLATILE_KEYS}
                out.setdefault(section, {})[asset_id] = clean
    return out


def code_hashes(repo_root: Path | None = None) -> dict[str, str | None]:
    """sha256 per file of ``FINGERPRINT_CODE``, keyed by the repo-relative POSIX path."""
    root = Path(repo_root or REPO_ROOT)
    out: dict[str, str | None] = {}
    for pattern in FINGERPRINT_CODE:
        matches = sorted(root.glob(pattern)) if any(c in pattern for c in "*?[") else [root / pattern]
        for p in matches:
            out[p.relative_to(root).as_posix()] = _sha256_file(p)
    return out


def build_fingerprint(args: dict, repo_root: Path | None = None) -> str:
    """sha256 (hex) of everything that decides what the build writes:
    the building and style files (``canonical_sha256``: without volatile keys
    such as ``created_utc``), their asset entries, the scene code and the
    canonical build arguments (``fingerprint_args``)."""
    from wenart.canonical import canonical_sha256

    building_path = Path(args["building"])
    building = json.loads(building_path.read_text(encoding="utf-8")) if building_path.is_file() else {}
    style = _style_for_fingerprint(args.get("style"))
    ids = referenced_asset_ids(building, style)
    payload = {
        "building_sha256": canonical_sha256(building_path),
        "style_sha256": canonical_sha256(Path(args["style"])) if args.get("style") else None,
        "assets": asset_entries_for(None if args.get("no_textures") else args.get("assets"), ids),
        "code": code_hashes(repo_root),
        "args": args,
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def reusable_build(out: Path, fingerprint: str) -> tuple[bool, str]:
    """``(True, "")`` when ``out`` holds a finished build with this fingerprint,
    else ``(False, why)``. Finished = scene.blend, scene_manifest.json and the
    files and previews the manifest lists all exist."""
    out = Path(out)
    manifest_path = out / "scene_manifest.json"
    if not (out / "scene.blend").is_file():
        return False, "no scene.blend"
    if not manifest_path.is_file():
        return False, "no scene_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return False, f"scene_manifest.json unreadable: {exc}"
    if manifest.get("build_fingerprint") != fingerprint:
        return False, f"fingerprint changed ({manifest.get('build_fingerprint')} -> {fingerprint})"
    names = list((manifest.get("files") or {}).values()) + list((manifest.get("previews") or {}).values())
    missing = [n for n in names if not (out / n).is_file()]
    if missing:
        return False, f"files missing: {', '.join(sorted(missing))}"
    return True, ""


SITE_KEYS = ("boundary_walls", "areas", "decor", "openings")
SITE_REASON = "site elements are recorded in the building JSON and reported, never built (docs/milestone7.md §6.4)"


def site_summary(building: dict) -> dict | None:
    """What the scene leaves out of the building's ``site`` (pure): counts
    per kind and the ids, ``built: false``; None without a site."""
    site = building.get("site")
    if not isinstance(site, dict):
        return None
    out = {"built": False, "reason": SITE_REASON}
    for key in SITE_KEYS:
        items = [i for i in site.get(key) or [] if isinstance(i, dict)]
        out[key] = {"count": len(items), "ids": [str(i["id"]) for i in items if i.get("id") is not None]}
    return out


def furniture_building(building: dict) -> dict:
    """The building furniture.create_furniture gets (pure): every piece but the
    fixed equipment that shell.build_stairs builds (``parametric.SHELL_TYPES``),
    so nothing is built twice."""
    from wenart.blender.parametric import SHELL_TYPES

    return dict(building, furniture=[p for p in building.get("furniture") or [] if p.get("type") not in SHELL_TYPES])


def add_furniture_summary(total: dict, summary: dict) -> None:
    """Add one level's furniture (or stair) summary to the build total (pure):
    counts, methods, fallbacks, ``not_built``, the stair ids and (Milestone 8)
    ``decor_skipped`` (wall art without a library model, or with no room to hang)."""
    for key in ("pieces", "proxies", "decor"):
        total[key] += summary.get(key, 0)
    for method, count in (summary.get("by_method") or {}).items():
        total["by_method"][method] = total["by_method"].get(method, 0) + count
    total["fallbacks"].extend(summary.get("fallbacks") or [])
    total["not_built"].extend(summary.get("not_built") or [])
    if summary.get("decor_skipped"):
        total.setdefault("decor_skipped", []).extend(summary["decor_skipped"])
    if summary.get("ids"):                                  # shell.build_stairs: parametric fixed equipment
        total["by_method"]["parametric"] = total["by_method"].get("parametric", 0) + len(summary["ids"])
        total["stairs"].extend(summary["ids"])


def default_style() -> dict:
    """The default profile of wenart.style (docs/milestone3.md §1): the default
    style text run through the vocabulary, so the asset ids are the ones the
    fetcher downloads. No private copy here, so the two cannot drift."""
    from wenart.style.profile import default_profile

    return default_profile()


def _loud(message: str, warnings: list[str]) -> None:
    """A warning the manifest keeps and the build log shows at a glance."""
    warnings.append(message)
    print(f"WARNING: {message}", file=sys.stderr, flush=True)


def load_style(path: str | None, warnings: list[str], assumed: list[dict] | None = None) -> tuple[dict, str | None]:
    """``(style, path)``: the style file, or the default profile when none is
    given or the file is missing (a loud warning plus an ``assumed`` entry).
    Slots a partial style file leaves out are filled from the default profile
    and each fill is recorded in ``assumed`` and ``warnings``; ``family``
    (Milestone 7) is never filled: a pre-M7 style file has none, and the scene
    does not read it."""
    assumed = assumed if assumed is not None else []
    default = default_style()
    if not path or not Path(path).exists():
        why = "no --style given" if not path else f"style file {path} missing"
        _loud(f"{why}: default style profile assumed ({default['source_text']!r})", warnings)
        assumed.append({"object": "style", "field": "profile", "value": default["source_text"],
                        "reason": f"{why}; default profile of wenart.style used"})
        return default, None
    p = Path(path)
    style = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(style, list):  # profiles_from_brief output: render the first, note the others
        if len(style) > 1:
            warnings.append(f"style file lists {len(style)} profiles; the first is used")
        style = style[0]
    for key, value in default.items():
        if key in style:
            continue
        if key == "family":
            continue  # Milestone 7: only refit's library style filter reads it; never filled from the default
        style[key] = value
        if key in ("matched_terms", "unmatched_terms", "warnings"):
            continue  # bookkeeping lists, not a styling choice
        _loud(f"style file {p} has no {key!r}: default {json.dumps(value)} assumed", warnings)
        assumed.append({"object": "style", "field": key, "value": value,
                        "reason": f"missing in {p}; default profile of wenart.style used"})
    walls = style.get("walls")
    if isinstance(walls, dict) and walls.get("tint") is not None:
        # Milestone 3/4 style files carry walls.tint; the wall colour now comes from
        # the flat albedo mode (docs/milestone5.md §2.2) and a tint would darken twice.
        _loud(f"style file {p}: walls.tint {walls['tint']} ignored (Milestone 5 albedo modes; "
              f"regenerate the style with python -m wenart.style)", warnings)
    return style, str(p)


def load_assets(assets_dir: str | None, no_textures: bool, warnings: list[str]) -> tuple[dict, dict, dict]:
    """``(textures, hdris, refused)`` from ``<assets>/manifest.json`` (empty when absent).

    Every entry must be CC0 from a known source (docs/milestone3.md §2);
    anything else is left out of ``textures`` / ``hdris`` with a warning, so
    it is neither rendered nor recorded as used; ``refused`` maps its id to
    the reason so the material record can say why it is flat."""
    from wenart.blender.materials import licence_problem

    if no_textures or not assets_dir:
        if not no_textures:
            warnings.append("no --assets given: flat colours and sky lighting")
        return {}, {}, {}
    manifest = Path(assets_dir) / "manifest.json"
    if not manifest.exists():
        warnings.append(f"assets manifest {manifest} missing: flat colours and sky lighting")
        return {}, {}, {}
    data = json.loads(manifest.read_text(encoding="utf-8"))
    accepted = {"textures": {}, "hdris": {}}
    refused = {}
    for kind in accepted:
        for asset_id, entry in (data.get(kind) or {}).items():
            problem = licence_problem(entry or {}, asset_id)
            if problem:
                _loud(f"{manifest} {kind}: {problem}", warnings)
                refused[asset_id] = problem
                continue
            accepted[kind][asset_id] = entry
    return accepted["textures"], accepted["hdris"], refused


def hdri_file(hdris: dict, assets_dir: str | None, style: dict) -> str | None:
    wanted = (style.get("lighting") or {}).get("hdri")
    entry = hdris.get(wanted) if wanted else None
    if not entry:
        return None
    path = Path(entry.get("file", ""))
    if not path.is_absolute() and assets_dir:
        path = Path(assets_dir) / path
    return str(path) if path.exists() else None


def is_whole_building(building: dict) -> bool:
    """Milestone 10: a building with slabs, a roof or variants is built whole (slabs, roof, facade, site,
    exterior views); any other keeps the M3-M9 scene."""
    return bool(building.get("slabs") or isinstance(building.get("roof"), dict) or building.get("variants"))


def ground_outline(building: dict, outlines: dict[str, list]) -> list:
    """The outline the ground is cut around: the largest outline of the levels at or below the highest
    drawn ground level (else the lowest level's)."""
    site = building.get("site") if isinstance(building.get("site"), dict) else {}
    zs = [((g.get("z") or {}).get("value")) for g in ((site.get("ground") or {}).get("levels") or [])
          if isinstance(g, dict)]
    top = max([float(z) for z in zs if z is not None] or [0.0])
    levels = sorted(building["levels"], key=lambda lv: float(lv["elevation"]))
    touching = [lv for lv in levels if float(lv["elevation"]) <= top + 0.5 and len(outlines.get(lv["id"]) or []) >= 3]
    if not touching:
        touching = [lv for lv in levels if len(outlines.get(lv["id"]) or []) >= 3][:1]
    if not touching:
        return []
    from wenart import geometry as G

    return max((outlines[lv["id"]] for lv in touching), key=G.polygon_area)


def facade_faces(building: dict, outlines: dict[str, list]) -> tuple[dict[str, list[dict]], list[str]]:
    """``({wall id: [face]}, warnings)``: the drawn facade parts (``facade.faces``, §1.6b row 12) on the walls
    they cover (pure). A face with a ``wall_id`` covers that wall; any other the outer walls of its level (every
    level when it names none) whose outward side (``shell.outward_side`` against the level outline) lies within
    45 degrees of the face's side (``site.side_direction``: compass with the building's north, or drawing-
    relative; ``all`` = every side). Each face gets ``direction`` (its side's unit vector, None for ``all``) so
    only the wall faces turned that way take it; its ``z_range`` (building z) bands it."""
    from wenart import geometry as G
    from wenart.blender import shell
    from wenart.blender import site as S

    north, _ = S.north_deg(building)
    walls = list(building.get("walls") or [])
    level_ids = {lv["id"] for lv in building.get("levels") or []}
    out: dict[str, list[dict]] = {}
    warnings = []
    cos45 = math.cos(math.radians(45.0)) - 1e-9
    for face in (building.get("facade") or {}).get("faces") or []:
        if not isinstance(face, dict) or not face.get("material"):
            continue
        direction = S.side_direction(face.get("side"), north)
        rec = dict(face, direction=list(direction) if direction else None)
        if face.get("wall_id"):
            if any(w["id"] == face["wall_id"] for w in walls):
                out.setdefault(face["wall_id"], []).append(rec)
            continue
        if face.get("level_id") and face["level_id"] not in level_ids:
            continue                                     # a level this variant does not build
        hit = 0
        for w in walls:
            if face.get("level_id") and w.get("level_id") != face["level_id"]:
                continue
            outline = outlines.get(w.get("level_id")) or []
            if len(outline) < 3:
                continue
            side = shell.outward_side(w, outline, G.segment_midpoint(w["start"], w["end"]))
            if side is None or (direction is not None and side[0] * direction[0] + side[1] * direction[1] < cos45):
                continue
            out.setdefault(w["id"], []).append(rec)
            hit += 1
        if not hit:
            warnings.append(f"facade face {face.get('material')} ({face.get('side')}, level {face.get('level_id')}): "
                            f"no outer wall on that side; not used")
    return out, warnings


def prepare(building_all: dict, variant: str = "base", brief: dict | None = None) -> dict:
    """What the build decides before Blender (pure; Milestone 10): the variant's building
    (``views.variant_building``), its ``views_for`` and ``variant_changes``, the brief values
    (``brief_args``), and for a whole building the slab plan, the roof model (``roof: null`` = an assumed flat
    roof; the level under it gets ``ceiling_planes``), the roof terraces, the level outlines, the site plan and
    the drawn facade parts per wall (``facade_faces``). Raises KeyError for an unknown variant.

    Milestone 11 (docs/milestone11.md §1.1 E6-E9, E11, §17): the agent's roof override (``roof.apply_override``),
    the roof terraces by the brief's ``roof_terraces`` (D5, ``roof.terrace_decisions``; the conflicts with the
    section are warnings), the doors and windows of assumed height clipped under the roof (E8,
    ``roof.clip_openings_to_roof``; the building copy gets them), the site options (``overrides.site_options``:
    the brief's ``site_options.front_court``, D6, and the agent's site keys) for the front courts and the inferred
    site. ``overrides_applied`` records what the agent's overrides changed (None without them)."""
    from wenart import views as V
    from wenart.blender import geom2d, shell
    from wenart.blender import overrides as O
    from wenart.blender import roof as R
    from wenart.blender import site as S

    whole = is_whole_building(building_all)
    vb = V.variant_building(building_all, variant)
    out = {"whole": whole, "variant": variant, "building": vb if whole else building_all,
           "views": V.views_for(building_all, variant, brief=brief), "changes": V.variant_changes(building_all, variant),
           "warnings": list(vb["_variant"]["warnings"]), "assumed": [], "slabs": None, "roof": None,
           "open_rooms": set(), "outlines": {}, "ground_outline": [], "site": None, "faces": {},
           "brief": brief_args(building_all, brief), "terraces": [], "clips": [], "site_options": None,
           "overrides_applied": None}
    agent = O.overrides_of(building_all)
    if agent is not None:
        out["overrides_applied"] = {"round": agent.get("round"), "roof": [], "cameras": [], "materials": [],
                                    "sun": None, "site": None}
    if not whole:
        return out
    slab_t, slab_assumed = out["brief"]["slab_thickness"]["value"], out["brief"]["slab_thickness"]["assumed"]
    site_mode, site_assumed = out["brief"]["site"]["value"], out["brief"]["site"]["assumed"]
    if site_assumed:          # (slab_thickness: slab_plan lists it on every slab that uses it)
        out["assumed"].append({"object": "brief", "field": "site", "value": site_mode,
                               "reason": "not in the brief: the default of wenart/defaults.yaml"})
    if building_all.get("slabs"):
        out["slabs"] = shell.slab_plan(vb, vb["levels"], float(slab_t), bool(slab_assumed))
        out["warnings"] += out["slabs"]["warnings"]
        out["assumed"] += out["slabs"]["assumed"]
    roof_in = vb.get("roof") if isinstance(vb.get("roof"), dict) else R.flat_roof(vb)
    if not isinstance(vb.get("roof"), dict):
        out["warnings"].append("roof: null (no roof evidence): a flat roof over the top level, assumed")
    roof_in, changes = R.apply_override(roof_in, O.roof_override(building_all))
    if changes:
        out["overrides_applied"]["roof"] = changes
        out["warnings"] += [f"roof {c['field']}: {c['was']} -> {c['value']} ({c['reason']})" for c in changes]
    roof_in, out["terraces"], warnings = R.terrace_decisions(roof_in, vb, out["brief"]["roof_terraces"]["value"])
    out["warnings"] += warnings
    for d in out["terraces"]:
        out["assumed"].append({"object": "roof", "field": f"terrace:{d['opening_id']}", "value": d["decision"],
                               "reason": d["reason"]})
    roof = R.roof_model(roof_in, vb)
    out["roof"] = roof
    out["warnings"] += roof["warnings"]
    for lv in vb["levels"]:
        if roof["convex"] and roof["equations"] and lv["id"] == roof["over_level_id"]:
            lv["ceiling_planes"] = [list(p) for p in R.ceiling_planes(roof, lv)]
    out["open_rooms"] = {o["room_id"] for o in roof["openings"] if o.get("room_id")}
    over = next((lv for lv in vb["levels"] if lv["id"] == roof.get("over_level_id")), None)
    out["clips"] = R.clip_openings_to_roof(vb, over, roof) if over is not None else []
    if out["clips"]:
        variant_meta = vb.get("_variant")
        vb = R.apply_clips(vb, out["clips"])
        if variant_meta is not None:
            vb["_variant"] = variant_meta
        out["building"] = vb
        for c in out["clips"]:
            out["assumed"].append({"object": c["opening_id"], "field": "height", "value": c["height"],
                                   "reason": c["reason"], "kind": "opening_clipped_by_roof", "parent": c["opening_id"]})
            if not c["fits"]:
                out["warnings"].append(f"{c['opening_id']}: {c['reason']}")
    for lv in vb["levels"]:
        out["outlines"][lv["id"]], method = geom2d.wall_outline([w for w in vb["walls"] if w["level_id"] == lv["id"]])
        if method == "convex_hull":               # review #24: an approximate outline is never silent
            reason = (f"the outline of {lv['id']}'s walls could not be traced: their convex hull stands in for the "
                      f"terrain cut, the light wells, the facade and sill sides and a derived slab or roof outline")
            out["warnings"].append(f"{lv['id']}: {reason}")
            out["assumed"].append({"object": f"level_{lv['id']}", "field": "outline", "value": "convex_hull",
                                   "reason": reason})
    out["ground_outline"] = ground_outline(vb, out["outlines"])
    if out["ground_outline"]:
        mode = site_mode if site_mode in ("full", "ground") else "full"
        if mode != site_mode:
            out["warnings"].append(f"brief site {site_mode!r} unknown: full used")
        out["site_options"] = O.site_options(building_all, out["brief"]["site_options.front_court"]["value"])
        if agent is not None and O.exterior_of(building_all).get("site"):
            out["overrides_applied"]["site"] = {k: v for k, v in out["site_options"]["source"].items() if v == "agent"}
        out["site"] = S.site_plan(vb, vb["levels"], out["ground_outline"], mode, outlines=out["outlines"],
                                  options=out["site_options"])
        out["warnings"] += out["site"]["warnings"]
        out["main_facade"] = S.main_facade(vb, vb["levels"], out["site"]["terrain"], out["ground_outline"],
                                           out["outlines"])
    out["faces"], warnings = facade_faces(vb, out["outlines"])
    out["warnings"] += warnings
    return out


def main(argv: list[str]) -> int:
    import bpy

    from wenart.blender import cameras as cams
    from wenart.blender import common, furniture, lighting, materials, shell
    from wenart.blender import exterior as E
    from wenart.blender import overrides as O
    from wenart.blender import roof as R
    from wenart.blender import site as S
    from wenart.blender.materials import MaterialLibrary
    from wenart.blender.render import configure_device

    args = parse_args(argv)
    t0 = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    if args.lens_mm is not None:
        try:
            cams.check_lens(args.lens_mm)
            if args.camera_policy != "search":
                raise ValueError(f"--lens-mm is for the search policy; the {args.camera_policy} cameras keep "
                                 f"{cams.M5_LENS_MM:g} mm")
        except ValueError as exc:
            print(f"--lens-mm {args.lens_mm:g}: {exc}")
            return 2
    building_all = json.loads(Path(args.building).read_text(encoding="utf-8"))
    try:
        brief = load_brief_file(args.brief)
    except (OSError, ValueError) as exc:
        print(f"--brief {args.brief}: {exc}")
        return 2
    fp_brief = brief_args(building_all, brief)
    if args.markers:                      # M11 D3: the debug flag turns the stripes on whatever the brief says
        fp_brief["markers_in_final"] = {"value": True, "assumed": False, "flag": "--markers"}
    fp_args = fingerprint_args(args.building, args.style, args.assets, args.level, args.no_textures,
                               args.preview_samples, args.no_preview, args.no_glb, args.proxies, args.camera_policy,
                               args.lens_mm, args.variant, fp_brief)
    fingerprint = build_fingerprint(fp_args)
    markers = bool(fp_brief["markers_in_final"]["value"])
    materials.set_markers(markers)
    if building_all.get("status") != "ok":
        print(f"building status is {building_all.get('status')!r}: nothing to build (needs review first)")
        return 2
    try:
        prep = prepare(building_all, args.variant, brief)
    except KeyError as exc:
        print(f"--variant {args.variant}: {exc}")
        return 2
    building = prep["building"]
    whole = prep["whole"]
    views = prep["views"]
    # A build killed half-way must never look finished to `cli build --reuse`:
    # the manifest of the previous build goes first and is written last.
    (out / "scene_manifest.json").unlink(missing_ok=True)
    warnings: list[str] = list(building_all.get("warnings", [])) + prep["warnings"] + list(views["warnings"])
    assumed: list[dict] = list(prep["assumed"])
    if materials.VOCABULARY_IMPORT_ERROR:
        _loud(f"style vocabulary not importable ({materials.VOCABULARY_IMPORT_ERROR}): "
              "flat colours from the local table of materials.py", warnings)
    style, style_path = load_style(args.style, warnings, assumed)
    # Milestone 11 (docs/milestone11.md §17.3): the agent's material slots and sun over the style; the sun of an
    # exterior view from the main facade's side when the north is unknown (§4.1 X7)
    agent_materials = O.materials_of(building_all)
    style, applied = O.apply_style(style, agent_materials)
    style, sun_applied = O.apply_sun(style, building_all)
    if prep["overrides_applied"] is not None:
        prep["overrides_applied"]["materials"] += applied
        prep["overrides_applied"]["sun"] = sun_applied
    if whole and sun_applied is None:
        style, sun_rule = sun_from_main_facade(style, prep.get("main_facade"), building)
        if sun_rule:
            assumed.append({"object": "sun", "field": "azimuth_deg", "value": sun_rule["azimuth_deg"],
                            "reason": sun_rule["reason"]})
    textures, hdris, refused = load_assets(args.assets, args.no_textures, warnings)
    hdri = hdri_file(hdris, args.assets, style)
    if (style.get("lighting") or {}).get("hdri") and hdri is None and not args.no_textures:
        warnings.append(f"HDRI {style['lighting'].get('hdri')} not available: physical sky used")

    levels = [lv for lv in building["levels"] if args.level is None or lv["id"] == args.level]
    if not levels:
        print(f"no level {args.level!r} in {args.building}")
        return 2

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = building["project"]["id"]
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    library = MaterialLibrary(textures, args.assets, use_textures=not args.no_textures, refused=refused)

    manifest_objects: list[dict] = []
    pass_indices: dict[str, int] = {}
    camera_plans: list[dict] = []
    checks: dict = {"door_rays": []}
    level_collections = {}
    furniture_summary = {"pieces": 0, "by_method": {}, "fallbacks": [], "proxies": 0, "decor": 0,
                         "proxies_forced": bool(args.proxies), "not_built": [], "stairs": [], "decor_skipped": []}
    loose_furniture = furniture_building(building)            # stairs are built with the shell
    rooms_without_view: list[dict] = []                       # Milestone 7 §6.2: empty rooms the cameras skip
    cameras_dropped: list[dict] = []                          # Milestone 10: exterior views no place worked for
    looks = E.resolve_looks(building, style, brief) if whole else None
    looks, applied = O.apply_looks(looks, agent_materials)
    if prep["overrides_applied"] is not None:
        prep["overrides_applied"]["materials"] += applied
    for slot, look in (looks or {}).items():
        warnings.extend(look.get("warnings") or [])
        if look.get("assumed") and slot in E.EXTERIOR_SLOTS:
            assumed.append({"object": "exterior", "field": slot, "value": look["material"], "reason": look["reason"]})
    slabs = prep["slabs"]
    roof = prep["roof"]
    render_rooms = set(views["rooms"])
    room_levels = {r["id"]: r["level_id"] for r in building["rooms"]}
    for skip in views["skipped"]:
        if room_levels.get(skip["room_id"]) in {lv["id"] for lv in levels}:
            rooms_without_view.append({"room_id": skip["room_id"], "level_id": room_levels[skip["room_id"]],
                                       "reason": skip["reason"],
                                       **({"same_as": skip["same_as"]} if skip.get("same_as") else {}),
                                       **({"twin_of": skip["twin_of"]} if skip.get("twin_of") else {})})
    outside = {"sills": 0, "railings": 0, "frames_outside": 0}

    for level in levels:
        col = common.get_or_make_collection(f"level_{level['id']}")
        level_collections[level["id"]] = col
        under = slabs["by_level"][level["id"]]["under"] if slabs else None
        above = slabs["by_level"][level["id"]]["above"] if slabs else None
        arrives = bool(above and above["voids"])
        stairs = shell.plan_stairs(building, level, slab_void=arrives)
        wall_whole = None
        if whole:
            roof_cut = R.wall_cut(roof) if roof and roof["over_level_id"] == level["id"] else None
            if roof_cut is not None:          # walls under a roof terrace end at the parapet (§1.6b row 13)
                roof_cut["parapets"] = R.parapet_cuts(roof, building, level)
            wall_whole = {"slab_above": above, "looks": looks, "outline": prep["outlines"].get(level["id"]),
                          "faces": prep["faces"], "open_rooms": prep["open_rooms"], "roof_cut": roof_cut}
            warnings.extend(openings_through_roof(building, level, wall_whole["roof_cut"]))
            warnings.extend(pieces_above_ceiling(building, level))
        shell.build_walls(building, level, col, library, style, manifest_objects, assumed, warnings, whole=wall_whole)
        shell.build_openings(building, level, col, library, style, pass_indices, manifest_objects, assumed, warnings)
        shell.build_skirting(building, level, col, library, style, manifest_objects, assumed)
        floor_whole = None
        if whole:
            floor_whole = {"floor_voids": under["voids"] if under else [],
                           "ceiling_voids": above["voids"] if above else None,
                           "ceiling_planes": level.get("ceiling_planes"), "open_rooms": prep["open_rooms"],
                           "terrace_floor": (looks or {}).get("paving")}
        shell.build_floors_ceilings(building, level, col, library, style, manifest_objects, warnings, stairs=stairs,
                                    whole=floor_whole)
        if whole and prep["outlines"].get(level["id"]):
            counts = shell.build_outside_details(building, level, col, library, looks, prep["outlines"][level["id"]],
                                                 pass_indices, manifest_objects, assumed, style=style)
            for k, v in counts.items():
                outside[k] += v
        level_furniture = loose_furniture
        if whole and level.get("ceiling_planes"):     # decor under the roof stays inside it
            decor, fit_warnings, fit_not_built = decor_under_roof(loose_furniture, level)
            level_furniture = dict(loose_furniture, decor=decor)
            warnings.extend(fit_warnings)
            furniture_summary["not_built"].extend(fit_not_built)
        summary = furniture.create_furniture(level_furniture, level, col, library, style, args.assets, pass_indices,
                                             manifest_objects, assumed, warnings, use_proxies=args.proxies)
        add_furniture_summary(furniture_summary, summary)
        # Milestone 11 (docs/milestone11.md §1.3 M2): the kitchens' tiled splashback behind the counter runs
        splash = shell.build_splashbacks(building, level, col, library, style, manifest_objects, assumed)
        furniture_summary["splashbacks"] = furniture_summary.get("splashbacks", 0) + splash
        add_furniture_summary(furniture_summary, shell.build_stairs(building, level, col, library, style, pass_indices,
                                                                    manifest_objects, assumed, warnings, plans=stairs,
                                                                    shaft=not arrives))
        plans = [p for p in cams.plan_cameras(building, level["id"], policy=args.camera_policy, lens_mm=args.lens_mm)
                 if p.get("room_id") in render_rooms]
        no_view = [r for r in cams.rooms_without_view(building, level["id"], policy=args.camera_policy)
                   if r.get("room_id") in render_rooms]
        rooms_without_view.extend(no_view)
        warnings.extend(f"{r['room_id']}: no view ({r['reason']})" for r in no_view)
        entries = O.camera_entries(building_all, "interior")
        if entries:                                    # Milestone 11 §17.3: the agent's fixed cameras
            level_rooms = {r["id"] for r in building["rooms"] if r["level_id"] == level["id"]}
            plans, applied = O.apply_cameras(plans, entries, level["id"], level_rooms)
            prep["overrides_applied"]["cameras"] += applied
        for plan in plans:
            plan.setdefault("policy", args.camera_policy)
            interior_camera_fields(plan, prep["variant"])
        cams.create_cameras(plans, col, manifest_objects)
        camera_plans.extend(plans)
        for plan in plans:
            if plan.get("warning"):
                warnings.append(f"{plan['name']}: {plan['warning']}")
        bpy.context.view_layer.update()
        rays = shell.door_ray_checks(building, level, scene)
        checks["door_rays"].extend(rays)
        for ray in rays:  # a ray through a door centre must cross the wall unhindered
            if ray["hit"]:
                warnings.append(f"{ray['opening_id']}: door ray hits {ray['hit_object']} ({ray['hit_kind']}); "
                                f"the opening is not cut through its wall")
        if level.get("ceiling_height_source") == "assumed_default":
            assumed.append({"object": f"level_{level['id']}", "field": "ceiling_height",
                            "value": level["ceiling_height"], "reason": "building JSON: assumed_default"})
        add_room_ids(manifest_objects, cams.opening_rooms(building, level["id"]), level["id"])

    whole_info = None
    extra_collections = []
    if whole:
        whole_info = {"slabs": [], "roof": None, "site": None, "outside": outside, "exterior_cameras": None}
        built_ids = {lv["id"] for lv in levels}
        if slabs:
            plan = dict(slabs, slabs=[s for s in slabs["slabs"] if s["above_level_id"] in built_ids])
            shell.build_slabs(plan, level_collections, library, style, manifest_objects, assumed)
            whole_info["slabs"] = [{"id": s["id"], "z_top": s["z_top"], "thickness": s["thickness"],
                                    "source": s["source"], "openings": len(s["voids"]), "stairs": s["stairs"],
                                    "assumed": s["assumed"]} for s in plan["slabs"]]
        if roof is not None and roof["equations"] and roof["over_level_id"] in built_ids:
            roof_col = common.get_or_make_collection("roof")
            extra_collections.append(roof_col)
            ceiling_style = style.get("ceiling") or {"material": "plaster_white"}
            mats = [shell.look_material(library, looks["roof"]),
                    library.get(ceiling_style["material"], ceiling_style.get("asset")),
                    shell.look_material(library, looks["roof"])]
            R.build_roof(roof, roof_col, mats, manifest_objects, assumed)
            over = next(lv for lv in levels if lv["id"] == roof["over_level_id"])
            parapets = R.parapet_cuts(roof, building, over)
            for o in roof["openings"]:
                reason = (f"roof terrace {o['id']}: its walls end at a {o['parapet_height']} m parapet "
                          f"({'drawn' if o['parapet_source'] == 'drawn' else 'height assumed'})")
                walls = sorted(w for w, cuts in parapets.items() if any(c["opening_id"] == o["id"] for c in cuts))
                if not walls:
                    warnings.append(f"roof opening {o['id']}: no outer wall runs under it; no parapet")
                elif o["parapet_source"] != "drawn":
                    assumed.append({"object": ",".join(walls), "field": "parapet", "value": o["parapet_height"],
                                    "reason": reason, "parent": str(o.get("room_id") or o["id"]), "kind": "parapet"})
            whole_info["roof"] = {"type": roof["type"], "planes_source": roof["planes_source"],
                                  "planes": roof["planes"], "derived_check": roof["derived_check"],
                                  "knee_wall_check": roof.get("knee_wall_check"), "profile": roof.get("profile"),
                                  "eaves_z": roof["eaves_z"], "ridge_z": roof["ridge_z"], "thickness": roof["thickness"],
                                  "openings": [o["id"] for o in roof["openings"]], "parapets": parapets,
                                  "flat_assumed": not isinstance(building.get("roof"), dict),
                                  "notes": roof["notes"], "assumed": roof["assumed"]}
        if prep["site"] is not None:
            site_col = common.get_or_make_collection("site")
            extra_collections.append(site_col)
            whole_info["site"] = S.build_site(prep["site"], site_col, looks,
                                              lambda look: shell.look_material(library, look), manifest_objects,
                                              assumed)
        if prep["outlines"]:                           # Milestone 11 E10: plinth, slab bands, coping, surrounds
            from wenart.blender import facade as FA
            fac_col = common.get_or_make_collection("facade_details")
            extra_collections.append(fac_col)
            fplan = FA.articulation_plan(building, levels, prep["outlines"], prep["ground_outline"],
                                         (prep["site"] or {}).get("terrain"), roof, style, looks,
                                         (prep["site"] or {}).get("wells") or [])
            whole_info["facade_details"] = FA.build_articulation(fplan, fac_col,
                                                                 lambda look: shell.look_material(library, look),
                                                                 manifest_objects, assumed)
        whole_info["terraces"] = prep["terraces"]
        whole_info["openings_clipped"] = prep["clips"]
        whole_info["main_facade"] = prep.get("main_facade")
        dropped = []
        if views["exterior"]:
            ext_col = common.get_or_make_collection("exterior")
            extra_collections.append(ext_col)
            model = E.build_model(building, levels, roof, prep["site"])
            ext_plans, dropped = E.plan_exterior(model, building, levels, (prep["site"] or {}).get("plot") or [],
                                                 variant=prep["variant"])
            entries = O.camera_entries(building_all, "exterior")
            if entries:                                # Milestone 11 §17.3: the agent's fixed exterior cameras
                ext_plans, applied = O.apply_cameras(ext_plans, entries)
                for p in ext_plans:
                    if p.get("policy") == "agent":
                        p["index"] = int(p["name"].split("_")[1]) if p["name"].split("_")[-1].isdigit() else 0
                        p["variant"] = prep["variant"]
                        p["visible_openings"] = E.visible_openings(model, building, levels, p["position"],
                                                                   p["target"], p["lens_mm"], 0.0)
                        if not p.get("sides"):          # the facade it looks at (its nearest axis)
                            cx_, cy_ = geom_centre(model.outline)
                            north, src = S.north_deg(building)
                            d = (p["position"][0] - cx_, p["position"][1] - cy_)
                            p["sides"] = [S.side_of(S.AXES[S.nearest_axis(d)], north,
                                                    not src.startswith("assumed"))]
                prep["overrides_applied"]["cameras"] += applied
            E.create_cameras(ext_plans, ext_col, manifest_objects)
            camera_plans.extend(ext_plans)
            for d in dropped:
                warnings.append(f"{d['name']}: exterior view dropped ({d['dropped_reason']})")
            for p in ext_plans:
                if p.get("warning"):
                    warnings.append(f"{p['name']}: {p['warning']}")
        cameras_dropped.extend(dropped)
        whole_info["exterior_cameras"] = {"planned": [p["name"] for p in camera_plans if p.get("kind") == E.KIND],
                                          "dropped": [d["name"] for d in dropped], "reason": views["exterior_reason"],
                                          "from": views["exterior_from"]}

    light_col = common.get_or_make_collection("lighting")
    if whole:
        north, north_source = S.north_deg(building)

        def ceiling_at(level, x, y):
            planes = level.get("ceiling_planes")
            flat = float(level["elevation"]) + float(level["ceiling_height"])
            return min([flat] + [a * x + b * y + c for a, b, c in planes or []])

        light_info = lighting.build_lighting(building, levels, style, hdri, light_col, manifest_objects, assumed,
                                             north_deg=north, north_source=north_source, ceiling_at=ceiling_at,
                                             exterior=bool(views["exterior"]))
        if north_source.startswith("assumed"):
            assumed.append({"object": "sun", "field": "north_deg", "value": north, "reason": north_source})
    else:
        light_info = lighting.build_lighting(building, levels, style, hdri, light_col, manifest_objects, assumed)
    bpy.context.view_layer.update()
    add_box3d(manifest_objects, warnings)
    mood = (style.get("lighting") or {}).get("mood")
    # render.py reads the mood here to pick the white-balance residual (§2.4).
    scene["wenart_mood"] = str(mood or "")

    previews = {}
    preview_maps = {}
    if not args.no_preview:
        configure_device(scene, "cpu" if os.environ.get("WENART_PREVIEW_CPU") else "auto")
        for level in levels:
            png = out / f"level_{level['id']}_top.png"
            mapping = render_top_down(scene, building, level, level_collections, png, args.preview_samples,
                                      hide_collections=extra_collections)
            if mapping is not None:
                previews[level["id"]] = png.name
                preview_maps[level["id"]] = mapping

    if camera_plans:
        scene.camera = bpy.data.objects.get(camera_plans[0]["name"])
    scene.render.resolution_x, scene.render.resolution_y = cams.RESOLUTION
    scene.render.resolution_percentage = 100

    blend = out / "scene.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    files = {"blend": blend.name}
    if not args.no_glb:
        glb = out / "scene.glb"
        try:
            bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", export_apply=True,
                                      export_extras=True, export_cameras=True, export_lights=True,
                                      export_image_format="JPEG", export_yup=True)
            files["glb"] = glb.name
        except Exception as exc:  # noqa: BLE001 - the export must not break the build
            warnings.append(f"glTF export failed: {exc}")

    manifest = {
        "schema_version": "0.1",
        "project": building["project"]["id"],
        "building": str(Path(args.building)),
        "style": style_path,
        "style_profile": style,
        "blender_version": bpy.app.version_string,
        "textures_enabled": not args.no_textures,
        "assets_dir": args.assets,
        "levels": [{"id": lv["id"], "label": lv.get("label"), "elevation": lv["elevation"],
                    "ceiling_height": lv["ceiling_height"], "ceiling_height_source": lv.get("ceiling_height_source")}
                   for lv in levels],
        "objects": manifest_objects,
        "camera_policy": args.camera_policy,
        "lens_mm": args.lens_mm,                              # Milestone 8: the brief's lens, None = automatic
        "search_seconds": search_seconds(camera_plans, args.camera_policy),
        "cameras": camera_plans,
        "rooms_without_view": rooms_without_view,
        "materials": library.records,
        "lighting": light_info,
        "pass_index": pass_indices,
        "assumed": assumed,
        "warnings": warnings,
        "checks": checks,
        "previews": previews,
        "preview_maps": preview_maps,
        "wenart_mood": scene["wenart_mood"],
        "build_fingerprint": fingerprint,
        "build_args": fp_args,
        "files": files,
        "furniture": furniture_summary,
        "site": (whole_info or {}).get("site") or site_summary(building),
        "variant": variant_summary(building_all, prep),
        "variants": variants_summary(building_all),
        "whole_building": whole_info,
        # Milestone 10 (docs/milestone10.md §1.6b rows 9, 11, 12): the exterior cameras no place worked for, the
        # resolved outside looks (never written back to the building) and the brief values used.
        "cameras_dropped": cameras_dropped,
        "exterior_looks": looks,
        "brief": prep["brief"],
        # Milestone 11 (docs/milestone11.md §17): D3 (no stripes in the renders unless asked; the items they would
        # mark, for the report and the debug images) and the agent's overrides as the build applied them.
        "markers_in_final": markers,
        "unverified_items": unverified_items(building),
        "agent_overrides": prep.get("overrides_applied"),
        "seconds": round(time.time() - t0, 1),
    }
    (out / "scene_manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    kinds = {}
    for o in manifest_objects:
        kinds[o["kind"]] = kinds.get(o["kind"], 0) + 1
    print(f"BUILD_DONE {out} objects={kinds} cameras={len(camera_plans)} furniture={furniture_summary['by_method']} "
          f"decor={furniture_summary['decor']} warnings={len(warnings)} seconds={manifest['seconds']}")
    return 0


def geom_centre(outline) -> tuple[float, float]:
    """The centre of an outline's bounding box (pure)."""
    xs, ys = [float(p[0]) for p in outline], [float(p[1]) for p in outline]
    return ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0) if xs else (0.0, 0.0)


SUN_TO_MAIN_FACADE_DEG = 45.0    # Milestone 11 (§7): the sun 45 degrees off the main facade's normal


def sun_from_main_facade(style: dict, main: dict | None, building: dict) -> tuple[dict, dict | None]:
    """``(style, rule)``: with no north arrow (``site.north_deg`` unknown, so the compass means nothing) the sun
    comes from the main (entrance) facade's side, ``SUN_TO_MAIN_FACADE_DEG`` off its normal, at the style's
    elevation (pure; docs/milestone11.md §4.1 X7, §7: the facade the views show is lit, with shadows); with a known
    north the style's sun stays. ``rule``: ``{"azimuth_deg", "reason"}`` or None."""
    from wenart.blender import site as S

    north, source = S.north_deg(building)
    if not main or not source.startswith("assumed"):
        return style, None
    dx, dy = main["direction"]
    facade_az = math.degrees(math.atan2(dx, dy)) % 360.0           # clockwise from +Y (= north, assumed)
    az = round((facade_az + SUN_TO_MAIN_FACADE_DEG) % 360.0, 3)
    lighting = dict(style.get("lighting") or {}, sun_azimuth_deg=az)
    return dict(style, lighting=lighting), {
        "azimuth_deg": az, "reason": f"no north arrow: the sun {SUN_TO_MAIN_FACADE_DEG:g} degrees off the main "
                                     f"({main['axis']}) facade, so the views of it show light and shadows "
                                     f"(docs/milestone11.md §4.1 X7; was {(style.get('lighting') or {}).get('sun_azimuth_deg')})"}


def unverified_items(building: dict) -> list[dict]:
    """The rooms and pieces the unverified stripes mark (pure; Milestone 11 decision D3): ``[{"id", "kind": room |
    furniture, "level_id"}]``. With ``markers_in_final: false`` (the default) the renders show no stripes; the
    scene manifest lists these items so the report and the debug images can name them."""
    out = []
    for room in building.get("rooms") or []:
        if room.get("status") == "unverified":
            out.append({"id": room["id"], "kind": "room", "level_id": room.get("level_id")})
    for piece in building.get("furniture") or []:
        if piece.get("status") == "unverified" and piece.get("build", True) is not False:
            out.append({"id": piece["id"], "kind": "furniture", "level_id": piece.get("level_id")})
    return out


def openings_through_roof(building: dict, level: dict, cut: dict | None) -> list[str]:
    """Warnings for the doors and windows of the level under the roof whose top lies above the roof
    underside at their wall (pure): the drawings disagree (a window drawn higher than the knee wall); the
    opening is built as drawn and shows through the roof."""
    from wenart.blender import geom2d, shell

    if not cut:
        return []
    walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level["id"]}
    out = []
    for o in building["openings"]:
        wall = walls.get(o.get("wall_id"))
        if o["level_id"] != level["id"] or wall is None or o.get("type") not in ("door", "window"):
            continue
        cx, cy, _ = shell.opening_centre_on_wall(o, wall)
        _bottom, top, _ = shell.opening_vertical(o, level, False)
        under = geom2d.surface_z(cut["planes"], cx, cy)
        if top > under + 1e-3:
            out.append(f"{o['id']}: its top ({top:.2f} m) is above the roof underside at its wall ({under:.2f} m); "
                       f"built as drawn, it shows through the roof")
    return out


def pieces_above_ceiling(building: dict, level: dict) -> list[str]:
    """Warnings for the furniture of a level under the roof that is taller than its sloped ceiling at a
    footprint corner (pure; ``level["ceiling_planes"]``): the piece is built as given and shows through the
    ceiling; the layout and fit stages decide sizes."""
    from wenart import geometry as G
    from wenart.blender import geom2d
    from wenart.blender.parametric import piece_bbox

    planes = level.get("ceiling_planes")
    if not planes:
        return []
    out = []
    for piece in building.get("furniture") or []:
        if piece.get("level_id") != level["id"] or piece.get("build", True) is False or piece.get("type") == "stair":
            continue
        fp = piece["footprint"]
        # a wall-hung piece (mount_bottom_m, §1.6b row 15) hangs that high above the floor
        top = float(level["elevation"]) + float(piece.get("mount_bottom_m") or 0.0) + float(piece_bbox(piece)[2])
        corners = G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0))
        low = min(geom2d.surface_z(planes, x, y) for x, y in corners)
        if top > low + 1e-3:
            out.append(f"{piece['id']}: {piece.get('type')} with its top {top - float(level['elevation']):.2f} m "
                       f"above the floor stands where the sloped ceiling is {low - float(level['elevation']):.2f} m "
                       f"high; it shows through the ceiling")
    return out


# Hostless decor that stands on the floor (a piece taller than the sloped ceiling over it would show through the
# roof) and decor hung flush under the ceiling.
FLOOR_DECOR_TYPES = ("plant_large", "plant", "sculpture", "basket")
MIN_LIGHT_BOTTOM_M = 2.0   # M11: a ceiling light under a slope hangs no lower than this above the floor


def decor_under_roof(building: dict, level: dict) -> tuple[list[dict], list[str], list[dict]]:
    """``(decor, warnings, not_built)``: the building's decor list with the hostless decor of a level under the roof
    fitted to its sloped ceiling (pure; ``level["ceiling_planes"]``, ``furniture.ceiling_above``). real02's exterior
    views showed attic decor outside the roof: ceiling lights placed at the flat ceiling height (``center[2]``) hung
    above the roof, and 1.6 m floor plants stood where the sloped ceiling is under 0.9 m high. A ceiling light whose given
    height reaches over the ceiling loses ``center[2]`` (the builder then hangs it flush under the slope); a floor
    piece taller than the ceiling over it is not built (``not_built``, with the reason). Pendants already lower
    themselves (``furniture._create_decor``). The decor placer should respect the slope in the first place."""
    from wenart.blender import furniture as F
    from wenart.blender import parametric as P

    decor = list(building.get("decor") or [])
    if not level.get("ceiling_planes"):
        return decor, [], []
    out, warnings, not_built = [], [], []
    for item in decor:
        dtype = item.get("type")
        center = list(item.get("center") or [])
        if item.get("level_id") != level["id"] or item.get("host_id") is not None or len(center) < 2 \
                or dtype not in ("ceiling_light",) + FLOOR_DECOR_TYPES:
            out.append(item)
            continue
        w, d, h = P.decor_size(dtype, item.get("size") or [0.4, 0.4])
        ceiling, _how = F.ceiling_above(level, center, (w, d), float(item.get("rotation_deg") or 0.0))
        z = float(center[2]) if len(center) > 2 and center[2] is not None else 0.0
        if z + h <= ceiling + 1e-3:
            out.append(item)
            continue
        if dtype == "ceiling_light" and ceiling - h < MIN_LIGHT_BOTTOM_M:
            # M11 pod G2b (real02 attic bathroom, ceiling 1.45 m): a light hung flush under such a low slope hangs
            # at eye height, in front of the camera (depth 0.05 m); it is not built.
            reason = (f"ceiling light: the sloped ceiling over it is {ceiling:.2f} m high, its bottom would be "
                      f"{ceiling - h:.2f} m above the floor (< {MIN_LIGHT_BOTTOM_M} m)")
            warnings.append(f"{item.get('id')}: {reason}; not built")
            not_built.append({"id": item.get("id"), "type": dtype, "reason": reason})
            continue
        if dtype == "ceiling_light":
            out.append(dict(item, center=center[:2]))
            warnings.append(f"{item.get('id')}: ceiling light at {z:.2f} m above the floor, the sloped ceiling over it "
                            f"is {ceiling:.2f} m high: hung flush under the slope instead")
            continue
        reason = (f"{dtype} {z + h:.2f} m high where the sloped ceiling is {ceiling:.2f} m high: it would show "
                  f"through the roof")
        warnings.append(f"{item.get('id')}: {reason}; not built")
        not_built.append({"id": item.get("id"), "type": dtype, "reason": reason})
    return out, warnings, not_built


def interior_camera_fields(plan: dict, variant: str) -> dict:
    """The Milestone 10 camera fields of an interior camera plan (pure; §1.6b row 11): ``kind`` interior,
    ``variant``, ``view`` null, ``sides`` [], ``region_id`` null, ``dropped_reason`` null. Returns ``plan``."""
    plan.setdefault("kind", "interior")
    plan["variant"] = variant
    for key, value in (("view", None), ("sides", []), ("region_id", None), ("dropped_reason", None)):
        plan.setdefault(key, value)
    return plan


def variant_summary(building_all: dict, prep: dict) -> dict:
    """The scene manifest's ``variant`` (pure): the built variant with its ``rooms_changed`` /
    ``exterior_changed`` (filled by the build: the building's, else computed; their source) and what it
    renders (``views_for``)."""
    from wenart import views as V

    rec = V.variant_record(building_all, prep["variant"])
    changes = prep["changes"]
    return {"id": rec["id"], "label": rec.get("label"), "base": V.is_base_variant(rec),
            "levels": list(rec.get("levels") or []), "changes": rec.get("changes") or [],
            "rooms_changed": changes["rooms_changed"], "exterior_changed": changes["exterior_changed"],
            "source": changes["source"], "computed": changes["computed"], "same_as": changes["same_as"],
            "views": prep["views"]}


def variants_summary(building_all: dict) -> list[dict]:
    """Every variant of the building with its ``rooms_changed`` / ``exterior_changed`` (pure)."""
    from wenart import views as V

    out = []
    for rec in V.building_variants(building_all):
        ch = V.variant_changes(building_all, rec["id"])
        out.append({"id": rec["id"], "label": rec.get("label"), "base": V.is_base_variant(rec),
                    "levels": list(rec.get("levels") or []), "rooms_changed": ch["rooms_changed"],
                    "exterior_changed": ch["exterior_changed"], "source": ch["source"]})
    return out


def add_room_ids(manifest_objects: list[dict], rooms_by_opening: dict[str, list[str]], level_id: str) -> None:
    """``room_ids`` on every door, window and plain-opening entry of the level
    (the rooms whose polygon edge carries it, ``cameras.opening_rooms``)."""
    for entry in manifest_objects:
        if entry.get("kind") in ("door", "window", "opening") and entry.get("level_id") == level_id:
            entry["room_ids"] = list(rooms_by_opening.get(entry["wenart_id"], []))


def add_box3d(manifest_objects: list[dict], warnings: list[str]) -> None:
    """``box3d`` on every furniture, proxy and decor entry: the world box of
    the object's mesh as built, in the piece frame (``rotation_deg`` of the
    entry), see ``geom2d.oriented_box``."""
    import bpy

    from wenart.blender import geom2d

    for entry in manifest_objects:
        if entry.get("kind") not in ("furniture", "furniture_proxy", "decor"):
            continue
        ob = bpy.data.objects.get(entry["name"])
        if ob is None or ob.type != "MESH" or not len(ob.data.vertices):
            warnings.append(f"{entry['name']}: no mesh object to measure; box3d left out")
            continue
        mw = ob.matrix_world
        points = [tuple(mw @ v.co) for v in ob.data.vertices]
        entry["box3d"] = geom2d.oriented_box(points, float(entry.get("rotation_deg") or 0.0))


def preview_mapping(x0: float, y0: float, x1: float, y1: float, px_per_m: float = PREVIEW_PX_PER_M) -> dict:
    """Resolution, orthographic scale and covered area of a top-down preview
    of the box ``x0, y0, x1, y1`` (metres) at ``px_per_m`` (pure).

    The resolution rounds the box up to whole pixels and the ortho scale is
    set so a pixel is exactly ``1 / px_per_m`` metres; the covered area is
    centred on the box. Pixel ``u = (x - bx0) / m``, ``v = (by1 - y) / m``
    with ``bbox_m = [bx0, by0, bx1, by1]`` and ``m = m_per_px``."""
    m = 1.0 / float(px_per_m)
    res_x = max(16, int(math.ceil(round((x1 - x0) * px_per_m, 6))))
    res_y = max(16, int(math.ceil(round((y1 - y0) * px_per_m, 6))))
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    half_w, half_h = res_x * m / 2.0, res_y * m / 2.0
    return {"resolution": [res_x, res_y], "m_per_px": m, "ortho_scale": max(res_x, res_y) * m,
            "bbox_m": [round(cx - half_w, 6), round(cy - half_h, 6), round(cx + half_w, 6), round(cy + half_h, 6)]}


def render_top_down(scene, building: dict, level: dict, level_collections: dict, png: Path,
                    samples: int, hide_collections=()) -> dict | None:
    """Orthographic top view of one level at 100 px/m: ceilings and other
    levels hidden for the shot, then restored. Returns the ``preview_maps``
    entry ``{png, bbox_m, m_per_px, resolution}`` (None when the level has
    no geometry). ``hide_collections`` (Milestone 10: roof, site, exterior)
    are hidden for the shot as well."""
    import bpy

    from wenart import geometry as G
    from wenart.blender import common

    walls = [w for w in building["walls"] if w["level_id"] == level["id"]]
    pts = [w["start"] for w in walls] + [w["end"] for w in walls]
    for r in building["rooms"]:
        if r["level_id"] == level["id"]:
            pts.extend(r["polygon"])
    if not pts:
        return None
    x0, y0, x1, y1 = G.bbox(pts)
    x0 -= PREVIEW_MARGIN_M
    y0 -= PREVIEW_MARGIN_M
    x1 += PREVIEW_MARGIN_M
    y1 += PREVIEW_MARGIN_M
    mapping = preview_mapping(x0, y0, x1, y1)
    cam = bpy.data.cameras.new("top_preview")
    cam.type = "ORTHO"
    cam.sensor_fit = "AUTO"     # ortho_scale spans the larger image side
    cam.ortho_scale = mapping["ortho_scale"]
    cam.clip_start = 0.1
    cam.clip_end = 100.0
    ob = bpy.data.objects.new("top_preview", cam)
    top_z = float(level["elevation"]) + float(level["ceiling_height"])
    ob.location = ((x0 + x1) / 2.0, (y0 + y1) / 2.0, top_z + 10.0)
    ob.rotation_euler = (0.0, 0.0, 0.0)  # looking down -Z, image up = +Y (north)
    scene.collection.objects.link(ob)

    hidden = []
    for lid, col in level_collections.items():
        for o in col.objects:
            if lid != level["id"] or o.get("wenart_kind") == "ceiling":
                if not o.hide_render:
                    o.hide_render = True
                    hidden.append(o)
    for col in hide_collections:
        for o in col.objects:
            if not o.hide_render:
                o.hide_render = True
                hidden.append(o)
    old = (scene.camera, scene.render.resolution_x, scene.render.resolution_y, scene.render.filepath,
           scene.cycles.samples, scene.render.image_settings.file_format, scene.render.image_settings.color_mode)
    scene.camera = ob
    scene.render.resolution_x, scene.render.resolution_y = mapping["resolution"]
    scene.render.resolution_percentage = 100
    scene.render.engine = "CYCLES"
    scene.cycles.samples = max(1, samples)
    scene.cycles.use_denoising = samples >= 8
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.filepath = str(png)
    bpy.ops.render.render(write_still=True)
    (scene.camera, scene.render.resolution_x, scene.render.resolution_y, scene.render.filepath,
     scene.cycles.samples, scene.render.image_settings.file_format, scene.render.image_settings.color_mode) = old
    for o in hidden:
        o.hide_render = False
    common.delete_object(ob)
    return {"png": png.name, "bbox_m": mapping["bbox_m"], "m_per_px": mapping["m_per_px"],
            "resolution": mapping["resolution"]}


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    code = main(argv)
    if code:
        sys.exit(code)
