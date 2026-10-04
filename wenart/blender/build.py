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
# Files whose content shapes scene.blend besides the inputs (docs/milestone5.md §2.7).
FINGERPRINT_CODE = ("wenart/blender/*.py", "wenart/style/vocabulary.py", "wenart/geometry.py",
                    "wenart/furniture/catalog.json")
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
    return parser.parse_args(argv)


# --------------------------------------------------------------------------
# Build fingerprint (pure Python: cli.py checks it without Blender)
# --------------------------------------------------------------------------

def fingerprint_args(building: str, style: str | None = None, assets: str | None = None, level: str | None = None,
                     no_textures: bool = False, preview_samples: int | None = None, no_preview: bool = False,
                     no_glb: bool = False, proxies: bool = False, camera_policy: str = DEFAULT_CAMERA_POLICY,
                     lens_mm: float | None = None) -> dict:
    """The build arguments that enter the fingerprint, in one canonical form
    (``--out`` is left out: where the scene is written does not change it).
    ``lens_mm`` None = the automatic lens rule (Milestone 8)."""
    return {"building": str(building), "style": str(style) if style else None,
            "assets": str(assets) if assets else None, "level": level, "no_textures": bool(no_textures),
            "preview_samples": DEFAULT_PREVIEW_SAMPLES if preview_samples is None else int(preview_samples),
            "no_preview": bool(no_preview), "no_glb": bool(no_glb), "proxies": bool(proxies),
            "camera_policy": str(camera_policy or DEFAULT_CAMERA_POLICY),
            "lens_mm": None if lens_mm is None else float(lens_mm)}


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


def main(argv: list[str]) -> int:
    import bpy

    from wenart.blender import cameras as cams
    from wenart.blender import common, furniture, lighting, materials, shell
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
    fp_args = fingerprint_args(args.building, args.style, args.assets, args.level, args.no_textures,
                               args.preview_samples, args.no_preview, args.no_glb, args.proxies, args.camera_policy,
                               args.lens_mm)
    fingerprint = build_fingerprint(fp_args)
    building = json.loads(Path(args.building).read_text(encoding="utf-8"))
    if building.get("status") != "ok":
        print(f"building status is {building.get('status')!r}: nothing to build (needs review first)")
        return 2
    # A build killed half-way must never look finished to `cli build --reuse`:
    # the manifest of the previous build goes first and is written last.
    (out / "scene_manifest.json").unlink(missing_ok=True)
    warnings: list[str] = list(building.get("warnings", []))
    assumed: list[dict] = []
    if materials.VOCABULARY_IMPORT_ERROR:
        _loud(f"style vocabulary not importable ({materials.VOCABULARY_IMPORT_ERROR}): "
              "flat colours from the local table of materials.py", warnings)
    style, style_path = load_style(args.style, warnings, assumed)
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

    for level in levels:
        col = common.get_or_make_collection(f"level_{level['id']}")
        level_collections[level["id"]] = col
        stairs = shell.plan_stairs(building, level)
        shell.build_walls(building, level, col, library, style, manifest_objects, assumed, warnings)
        shell.build_openings(building, level, col, library, style, pass_indices, manifest_objects, assumed, warnings)
        shell.build_skirting(building, level, col, library, style, manifest_objects, assumed)
        shell.build_floors_ceilings(building, level, col, library, style, manifest_objects, warnings, stairs=stairs)
        summary = furniture.create_furniture(loose_furniture, level, col, library, style, args.assets, pass_indices,
                                             manifest_objects, assumed, warnings, use_proxies=args.proxies)
        add_furniture_summary(furniture_summary, summary)
        add_furniture_summary(furniture_summary, shell.build_stairs(building, level, col, library, style, pass_indices,
                                                                    manifest_objects, assumed, warnings, plans=stairs))
        plans = cams.plan_cameras(building, level["id"], policy=args.camera_policy, lens_mm=args.lens_mm)
        no_view = cams.rooms_without_view(building, level["id"], policy=args.camera_policy)
        rooms_without_view.extend(no_view)
        warnings.extend(f"{r['room_id']}: no view ({r['reason']})" for r in no_view)
        for plan in plans:
            plan.setdefault("policy", args.camera_policy)
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

    light_col = common.get_or_make_collection("lighting")
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
            mapping = render_top_down(scene, building, level, level_collections, png, args.preview_samples)
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
        "site": site_summary(building),
        "seconds": round(time.time() - t0, 1),
    }
    (out / "scene_manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    kinds = {}
    for o in manifest_objects:
        kinds[o["kind"]] = kinds.get(o["kind"], 0) + 1
    print(f"BUILD_DONE {out} objects={kinds} cameras={len(camera_plans)} furniture={furniture_summary['by_method']} "
          f"decor={furniture_summary['decor']} warnings={len(warnings)} seconds={manifest['seconds']}")
    return 0


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
                    samples: int) -> dict | None:
    """Orthographic top view of one level at 100 px/m: ceilings and other
    levels hidden for the shot, then restored. Returns the ``preview_maps``
    entry ``{png, bbox_m, m_per_px, resolution}`` (None when the level has
    no geometry)."""
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
