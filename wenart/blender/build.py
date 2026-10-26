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

Milestone 13 (docs/milestone13.md §13.2 build.py, K8 camera replay; the camera policy itself stays, D8):

- ``--cameras-from <scene_manifest.json>`` recreates the cameras of that manifest (``cameras.replay_cameras``:
  name, room, level, position, target or rotation, lens, sensor, shift, clip) with ``source: "replayed"`` in the
  scene manifest's ``cameras``; the search runs only for the rooms (and the exterior set) that have no camera in
  the file. ``--cameras-extra`` runs the search for every room as well and adds those cameras with the suffix
  ``_s`` (``cam_<room>_<n>_s``, ``ext_<n>_s``), so a build carries the baseline views and the searched set
  together. The environment variable ``WENART_CAMERAS_FROM`` (the orchestrated run; ``{name}`` = the project id,
  e.g. ``results/renders/{name}/scene_manifest.json``) stands in for the flag, ``WENART_CAMERAS_EXTRA=1`` for
  ``--cameras-extra``. A file without camera records (real04's run committed none) falls back to the search with
  a log line and the manifest's ``cameras_from.reason``. The file's content (sha256) and the extra flag are part
  of the build fingerprint, so a changed camera file rebuilds the scene.
- The scene manifest's ``lighting`` block carries the light variant and the levers (``lighting.build_lighting``);
  the material library gets the style and the levers for the shell material table (``materials.MaterialLibrary``).

Fix round part 2 (17 Oct 2026; the lead's decision on the review of part 1: the CLAUDE.md rule "the sky, the sun and
the horizon are always in the image" wins over the frozen Milestone 11 view): a replayed exterior record of view
``aerial`` (not the site view) whose horizon lies at or above the top of its frame (``copies.horizon_fraction`` >= 1;
real02's M11 ext_5: 30 degrees down at 28.54 mm, the horizon at 1.31 of the frame height, no sky) is re-pitched
about its target at the same distance (``repitch_replayed_aerials``): the pitch of the planner's aerial,
``copies.pitch_for_horizon(exterior.AERIAL_HORIZON_FRAC, min(lens, exterior.AERIAL_LENS_MM),
exterior.AERIAL_PITCH_DEG)``, and its lens at most ``AERIAL_LENS_MM``. The camera record says ``replay: {"status":
"repitched", ...}`` with the old and new pitch, lens, horizon and position and the reason, the build log has a
warning line and ``cameras_from.repitched`` names the cameras.

Fix round after P4a (17 Oct 2026; pod P4a, real02 with the M11 cameras replayed): the agent's camera entries are
applied after the replayed and the planned cameras are merged (``merge_agent_cameras``), inside and outside. P4a
applied its three ``set ext_6`` to the empty planned exterior set (the replayed set stands in for it), so ``ext_6``
was added a second time; Blender named the object ``ext_6.001``, the agent's move never reached the view it judged,
and two GPU tests failed on the unknown name. Now a ``set`` on a replayed name replaces that record: the camera has
``policy: agent`` and ``source: searched`` (the frozen ``CAMERA_SOURCES``) and keeps the replaced record in
``replaced_replayed``; ``cameras_from`` lists ``agent`` and ``agent_replaced``; a ``remove`` of a replayed camera is
listed in ``cameras_from.dropped`` with the agent's reason. An agent exterior camera keeps the view it took over
only while its pose still is that view (``agent_exterior_view``: P4a's corner pose was recorded as the frontal view
of the back facade, which hid X6's "no frontal view of the entrance"); else its view is ``agent`` with the side of
its nearest axis, and the build log says so. Never two cameras with one name: a clash is renamed ``<name>_dup<k>``
with a log line (``dedupe_camera_names``), and the build stops when Blender renames a camera object
(``check_camera_objects``). Each exterior camera object carries ``wenart_camera_source``, as the interior ones.

Fix round after P4b (17 Oct 2026): an agent exterior camera whose view is not aerial / site after
``agent_exterior_view`` loses the ``aerial_allowed`` and ``site_view`` flags it copied from the camera it replaced,
and its ``horizon_frac`` is measured from its own pose (``plan_horizon_fraction``; review of the P4a fix round: an
eye-level pose kept "the aerial view the policy allows, not a finding" for the vision critic). A flat_cut roof's slab
edge and parapet (roof slot 2) take the facade look, not the roof covering (``roof_slot_looks``; P4b's real03 parapet
read as a tiled mansard on a flat roof). The lead's decisions of 17 Oct 2026 recorded here: replayed cameras (set 1)
are frozen and the frontal view X6 asks for is never turned into a non-frontal pose by the agent (both are rules of
the agent's camera tool, wenart/agent/tools.py; the build's view check stays the record of what a pose is).
Integration of the fix round after P4b: an agent pose on an ``entrance`` view keeps ``entrance`` while it still
frames its door (``exterior_checks.entrance_view_problem``: at most 14 m from the door face, within 30 degrees
of its axis, the door in the frame; ``site.entrances``), else it becomes ``agent`` with ``view_was`` (``agent_exterior_view``; the
door id is kept through ``overrides.CAMERA_KEEP_KEYS``). The sun from the main facade (no north arrow) also applies
when the agent's sun override gives no ``azimuth_deg`` (``facade_sun_applies``: an elevation-only override skipped it
and the style's 210 degrees lit real02's back).

Fix round after P6b (23 Oct 2026; pod P6b, real03 with the M11 cameras replayed; docs/milestone13.md §7 "a frozen
camera that ends up inside a newly built piece is moved by the free-floor rule and marked"): every build moves the
replayed interior cameras of a level that a piece of this build blocks or contains (``replayed_moves``,
``camsearch.move_blocked_replayed``, on ``camera_building``) before the search and ``merge_agent_cameras``: same yaw,
pitch, height, lens, shift and name, ``source: replayed`` (frozen for the agent), ``replay: {"status": "moved", ...}``,
a warning line and ``cameras_from.moved``. P6b's yasama_2_2, 3_2, 5_2 and 6_1 stood inside or against the 2.02 m
fridges the reading typed at the end of the kitchen runs; they move 0.66-0.88 m.
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
                    "wenart/defaults.yaml",
                    # Milestone 12 (track L): the terrain surface of site.ground (wenart.levels.terrain); track S: the
                    # catalogue rule and the size table the furniture build imports (lead note of 10 Oct 2026)
                    "wenart/levels/__init__.py", "wenart/levels/terrain.py", "wenart/furniture/__init__.py",
                    "wenart/furniture/catalog.py", "wenart/furniture/sizes.py", "wenart/recognition/size_table.yaml")
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
    parser.add_argument("--cameras-from", default=None,
                        help="Milestone 13: a scene_manifest.json whose cameras are recreated (source: replayed); the "
                             "search runs only for rooms without a camera in it (env WENART_CAMERAS_FROM)")
    parser.add_argument("--cameras-extra", action="store_true",
                        help="Milestone 13: with --cameras-from also run the search for every room and add those "
                             "cameras with the suffix _s (env WENART_CAMERAS_EXTRA=1)")
    return parser.parse_args(argv)


# --------------------------------------------------------------------------
# Milestone 13: the camera file of --cameras-from (pure)
# --------------------------------------------------------------------------

CAMERAS_FROM_ENV = "WENART_CAMERAS_FROM"
CAMERAS_EXTRA_ENV = "WENART_CAMERAS_EXTRA"
EXTRA_CAMERA_SUFFIX = "_s"
_ENV = object()                      # "resolve from the environment" (fingerprint_args, build.main)


def cameras_from_spec(value, project_id: str | None = None, env=None) -> str | None:
    """The camera file of a build (pure): ``value`` (the flag), else ``env[CAMERAS_FROM_ENV]`` (``os.environ``
    when None); ``{name}`` in it is the project id. None without either, or for an empty value."""
    text = value if value not in (None, "") else (os.environ if env is None else env).get(CAMERAS_FROM_ENV)
    if text in (None, ""):
        return None
    text = str(text)
    if "{name}" in text:
        if not project_id:
            return text
        text = text.replace("{name}", str(project_id))
    return text


def cameras_extra_flag(value=None, env=None) -> bool:
    """``--cameras-extra`` (pure): the flag, else ``env[CAMERAS_EXTRA_ENV]`` in ``1 / true / yes / on``."""
    if value:
        return True
    text = str((os.environ if env is None else env).get(CAMERAS_EXTRA_ENV) or "").strip().lower()
    return text in ("1", "true", "yes", "on")


def camera_file_record(path: str | None) -> dict | None:
    """What the fingerprint and the manifest keep of the camera file (pure): ``{"path", "sha256", "cameras",
    "build_fingerprint"}``; ``{"path", "missing": True}`` when it does not exist or is not JSON; None without a
    path. ``cameras`` counts the records ``cameras.replay_cameras`` would take."""
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return {"path": str(path), "missing": True}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except ValueError:
        return {"path": str(path), "missing": True, "reason": "not a JSON file"}
    from wenart.blender.cameras import replay_cameras
    replay = replay_cameras(data if isinstance(data, dict) else {})
    return {"path": str(path), "sha256": _sha256_file(p), "cameras": len(replay["plans"]),
            "build_fingerprint": replay["fingerprint"], "camera_policy": replay["policy"]}


def _project_id_of(building_path: str) -> str | None:
    try:
        data = json.loads(Path(building_path).read_text(encoding="utf-8"))
        return str((data.get("project") or {}).get("id") or "") or None
    except (OSError, ValueError, AttributeError):
        return None


# --------------------------------------------------------------------------
# Build fingerprint (pure Python: cli.py checks it without Blender)
# --------------------------------------------------------------------------

def fingerprint_args(building: str, style: str | None = None, assets: str | None = None, level: str | None = None,
                     no_textures: bool = False, preview_samples: int | None = None, no_preview: bool = False,
                     no_glb: bool = False, proxies: bool = False, camera_policy: str = DEFAULT_CAMERA_POLICY,
                     lens_mm: float | None = None, variant: str = "base", brief: dict | None = None,
                     cameras_from=_ENV, cameras_extra=_ENV) -> dict:
    """The build arguments that enter the fingerprint, in one canonical form
    (``--out`` is left out: where the scene is written does not change it).
    ``lens_mm`` None = the automatic lens rule (Milestone 8); ``variant``
    (Milestone 10) the building variant; ``brief`` the brief values the
    build uses (``brief_args``; the file path is not part of it).

    Milestone 13: ``cameras_from`` (the camera file of ``--cameras-from``; left out = the environment's
    ``WENART_CAMERAS_FROM``, ``{name}`` = the building's project id) enters as ``camera_file_record`` (its sha256,
    so a changed file rebuilds), ``cameras_extra`` as a flag; the light variant (``WENART_LIGHT_VARIANT``) enters
    too, so an A/B build of another variant never reuses this one."""
    path = cameras_from_spec(None if cameras_from is _ENV else cameras_from,
                             _project_id_of(building) if cameras_from is _ENV or "{name}" in str(cameras_from or "")
                             else None, env=None if cameras_from is _ENV else {})
    extra = cameras_extra_flag(None if cameras_extra is _ENV else cameras_extra,
                               env=None if cameras_extra is _ENV else {})
    record = camera_file_record(path)
    if record is not None and record.get("missing"):
        record = {"path": record["path"], "missing": True}
    try:
        from wenart.blender.lighting import light_levers
        variant_name = light_levers()["variant"]
    except Exception:  # noqa: BLE001 - the fingerprint must not die over the lever table
        variant_name = None
    return {"building": str(building), "style": str(style) if style else None,
            "assets": str(assets) if assets else None, "level": level, "no_textures": bool(no_textures),
            "preview_samples": DEFAULT_PREVIEW_SAMPLES if preview_samples is None else int(preview_samples),
            "no_preview": bool(no_preview), "no_glb": bool(no_glb), "proxies": bool(proxies),
            "camera_policy": str(camera_policy or DEFAULT_CAMERA_POLICY),
            "lens_mm": None if lens_mm is None else float(lens_mm), "variant": str(variant or "base"),
            "brief": brief or {},
            "cameras_from": None if record is None else {k: record[k] for k in ("path", "sha256", "missing") if k in record},
            "cameras_extra": bool(extra) if record is not None else False,
            "light_variant": variant_name}


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
    # 25 Oct 2026: the user's answers to the architect's questions (the brief's ``architect_answers``, else the
    # project's ``architect_answers.json``): in the fingerprint, so a new answer rebuilds the scene
    from wenart.blender import architect_actions as AA
    given = (brief or {}).get("architect_answers") if isinstance(brief, dict) else None
    out["architect_answers"] = {"value": given if isinstance(given, dict) else AA.project_answers(building),
                                "assumed": False}
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
    furniture and decor models of the building; since Milestone 13 the shell
    slots' sets and (fix round after P3) the sets of the outside finishes the
    build puts on by itself (``exterior.build_finish_slugs``)."""
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
    # Milestone 13 (round 4 review, 16 Oct 2026): the shell slots' texture sets (worktop marble_01, handles Metal032,
    # ...): a build cached before a set reached the volume must be redone once it is there, so the fingerprint follows
    # them. The ids are read from the slot table itself, as the assets stage's wenart.assets.fetch.shell_texture_rows
    # does (that module is outside the build's import closure, FINGERPRINT_CODE).
    try:
        from wenart.blender import materials as M
        for slot in M.SHELL_SLOT_NAMES:
            for asset_id in (M.SHELL_SLOTS[slot].get("asset"), M.shell_slot_spec(slot, style).get("asset")):
                if asset_id:
                    ids.add(str(asset_id))
    except (ImportError, AttributeError, KeyError, TypeError):
        pass
    # Fix round after P3 (16-17 Oct 2026): the sets of the finishes the outside build puts on by itself (retaining
    # walls and kerbs concrete_exposed -> concrete_wall_001, the family's plinth, the site fallbacks), the same ids the
    # assets stage fetches (wenart.assets.fetch.site_texture_rows reads the same exterior.build_finish_slugs): a build
    # cached before concrete_wall_001 reached the volume (P3) is redone once it is there.
    try:
        from wenart.blender import exterior as E
        from wenart.style import vocabulary as V
        for slug, _part in E.build_finish_slugs(style):
            entry = V.MATERIALS.get(slug) or V.FURNITURE_MATERIALS.get(slug) or {}
            if entry.get("asset"):
                ids.add(str(entry["asset"]))
    except (ImportError, AttributeError, KeyError, TypeError):
        pass
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


def assets_dir_record(env_value: str | None, arg_value: str | None, resolved) -> dict:
    """Where the vegetation module found the assets folder (pure; Milestone 13 T6): ``{"path", "source"}`` with
    ``source`` ``env`` (``WENART_ASSETS``, read first by ``vegetation.assets_dir``), ``build --assets`` (the build's
    own flag, handed over as the scene property ``wenart_assets_dir``), ``default`` (``vegetation.ASSET_CANDIDATES``)
    or None when no folder with a manifest was found (the leaf atlases, hero models and grass clumps then fall back
    to procedural cards)."""
    if resolved is None:
        return {"path": None, "source": None}
    path = Path(str(resolved))
    if env_value and Path(env_value) == path:
        source = "env"
    elif arg_value and Path(arg_value) == path:
        source = "build --assets"
    else:
        source = "default"
    return {"path": str(path), "source": source}


def site_manifest_block(site: dict | None, assets: dict | None = None, realized: dict | None = None) -> dict | None:
    """The manifest's ``site`` block with the Milestone 13 records (pure): ``assets`` (``assets_dir_record``) and
    ``realized_instances`` (``site.realize_site_instances`` before the scene.glb export; None when the glb was not
    written). A building without a site (``site`` None) keeps None. A site that is not built (``built: false``,
    ``site_summary``: an interior-only build) keeps its block as it is: no vegetation is built then, and the
    scene-manifest schema (``schemas.SITE_LEFT_OUT``) allows only ``{count, ids}`` objects next to ``built`` and
    ``reason`` (round-2 review, 15 Oct 2026: the two records broke ``validate_scene_manifest`` there)."""
    if not isinstance(site, dict) or not site.get("built"):
        return site
    out = dict(site)
    if assets is not None:
        out["assets"] = assets
    out["realized_instances"] = realized
    return out


def recolour_parts_of(manifest_objects: list) -> int:
    """Milestone 13 (T8 metric 10): every scene object's ``recolour`` record gets its per-part keys
    (``materials.recolour_parts``: ``fabric``, ``wood``, ...) in place; returns how many records changed."""
    from wenart.blender.materials import recolour_parts

    n = 0
    for o in manifest_objects:
        rec = o.get("recolour")
        if isinstance(rec, dict) and isinstance(rec.get("applied"), list):
            new = recolour_parts(rec)
            if new != rec:
                o["recolour"] = new
                n += 1
    return n


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


LIBRARY_OPENINGS_ENV = "WENART_LIBRARY_OPENINGS"      # "off": the parametric doors and windows (A/B)


def library_openings(building: dict, levels: list, prep: dict, brief, warnings: list, assets_dir=None,
                     style=None, assumed: Optional[list] = None) -> dict:
    """``opening_models.plan`` for the outer doors and windows of a whole-building build (24 Oct 2026), in the
    run's licence mode; {} when ``WENART_LIBRARY_OPENINGS=off`` or the catalogue has no extras."""
    from wenart.blender import opening_models as OM
    from wenart.blender import site as S

    if str(os.environ.get(LIBRARY_OPENINGS_ENV) or "").strip().lower() in ("off", "0", "no", "false"):
        return {}
    try:
        from wenart.furniture.catalog import licence_mode_from
        mode = licence_mode_from(brief)[0]
    except Exception:  # the Blender Python without the fit's dependencies
        mode = str(os.environ.get("WENART_LICENCE_MODE") or "relaxed").strip().lower()
    extras = OM.load_extras(REPO_ROOT / "wenart" / "furniture" / "catalog_library.json")
    if not extras:
        return {}
    outer = S.outer_openings(building, levels, prep.get("ground_outline") or [], prep.get("outlines"))
    # 25 Oct 2026 (architect A3): the doors to terrace and balcony rooms are outside doors too
    from wenart.blender import architect as AR
    ids = {lv["id"] for lv in levels}
    taken = {r["opening"]["id"] for r in outer}
    outer = list(outer) + [r for r in AR.open_air_doors(building) if r["level"]["id"] in ids
                           and r["opening"]["id"] not in taken and r["opening"].get("outside_door")]
    # 26 Oct 2026 (user: "the house ... needs to look very stylish"): the style picks the look, one door and window
    # language per building; what was left out and what stays parametric is listed (opening_models.plan's notes)
    notes: list = []
    plan = OM.plan(building, outer, extras, mode, assets_dir=assets_dir, style=style, notes=notes)
    for n in notes:
        if n.get("kind") == "parametric":
            warnings.append(f"opening {n.get('id')}: parametric in the style's finish ({n.get('reason')})")
            if assumed is not None:
                assumed.append({"object": n.get("id"), "field": "opening_model", "value": "parametric",
                                "reason": str(n.get("reason") or "no model of the building's family fits")})
        elif n.get("kind") == "left_out" and assumed is not None:
            assumed.append({"object": "openings", "field": f"left_out:{n.get('category')}",
                            "value": len(n.get("models") or {}), "reason": "models out of the style's look: "
                            + "; ".join(f"{k}: {v}" for k, v in list((n.get("models") or {}).items())[:8])})
    cats: dict = {}
    for v in plan.values():
        cats.setdefault(v["category"], set()).add(v["asset"]["asset_id"])
    print(f"LIBRARY_OPENINGS {len(plan)} of {len(outer)} outer openings ({mode}): "
          + ", ".join(f"{k} {sorted(v)}" for k, v in sorted(cats.items())))
    return plan


def style_family_of(style_path) -> Optional[str]:
    """The ``family`` of a style file (pure; None when there is none or it cannot be read): the architect's
    balustrade kind follows it (``details.balustrade_kind``)."""
    try:
        data = json.loads(Path(style_path).read_text(encoding="utf-8")) if style_path else None
    except (OSError, ValueError):
        return None
    if isinstance(data, list):
        data = data[0] if data else None
    return str(data.get("family")) if isinstance(data, dict) and data.get("family") else None


def prepare(building_all: dict, variant: str = "base", brief: dict | None = None,
            style_family: Optional[str] = None) -> dict:
    """``prepare_once`` with the architect's defaults carried out (26 Oct 2026, user: "I need ai models to see
    understand and fix everything before even I look at it"): the review's open points that have a safe default
    (``architect.defaults_of``) are answered ``by: architect`` and the plan is made again, at most
    ``architect.DEFAULT_ROUNDS`` times; the AI architect's and the user's answers win over a default
    (``architect_actions.answers_of``). ``out["architect_defaults"]`` lists them.

    26 Oct 2026 (user: "make the AI architect a lot more smart and let it take decisions more"): a point whose choice
    could not be carried out gets the next choice of its chain (``architect.chain_of``) the next round; a default
    that opens a major point that was not open before is refused (tried alone when several came in one round) and
    the next choice is tried instead (``out["architect_refused_defaults"]``: key -> the choice and the points it
    opened)."""
    out = prepare_once(building_all, variant, brief, style_family)
    if not out.get("whole") or out.get("architect") is None:
        return out
    from wenart.blender import architect as AR

    def again(defs: dict) -> dict:
        return prepare_once(dict(building_all, architect_defaults=defs), variant, brief, style_family)

    defaults = dict(building_all.get("architect_defaults") or {})
    tried: dict = {}
    refused: dict = {}
    for _ in range(AR.DEFAULT_ROUNDS):
        new = {k: v for k, v in AR.defaults_of(out["architect"], out.get("architect_answers") or {}, tried).items()
               if (defaults.get(k) or {}).get("choice") != v.get("choice")}
        if not new:
            break
        for k, v in new.items():
            tried.setdefault(k, []).append(v.get("choice"))
        majors = AR.open_keys(out["architect"], "major")
        got = again(dict(defaults, **new))
        if AR.open_keys(got["architect"], "major") - majors - set(new):
            keep = {}
            for k, v in sorted(new.items()):
                more = AR.open_keys(again(dict(defaults, **{k: v}))["architect"], "major") - majors - {k}
                if more:
                    refused[k] = {"choice": v.get("choice"), "opened": sorted(more)}
                else:
                    keep[k] = v
            if not keep:
                continue
            new = keep
            got = again(dict(defaults, **new))
        defaults.update(new)
        out = got
    out["architect_defaults"] = defaults
    out["architect_refused_defaults"] = refused
    return out


def prepare_once(building_all: dict, variant: str = "base", brief: dict | None = None,
                 style_family: Optional[str] = None) -> dict:
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
    site. ``overrides_applied`` records what the agent's overrides changed (None without them).

    Fix round after P5 (22 Oct 2026): every level of a whole building gets ``open_rooms`` (its rooms in
    ``open_rooms``, sorted), so the camera search leaves the sloped ceiling out of the roof terraces open to the sky
    (``camsearch.sloped_level``; P5's real04 terraces got one view each, framed on the parapet corner)."""
    from wenart import views as V
    from wenart.blender import geom2d, shell
    from wenart.blender import overrides as O
    from wenart.blender import roof as R
    from wenart.blender import site as S

    whole = is_whole_building(building_all)
    vb = V.variant_building(building_all, variant)
    # 25 Oct 2026: the architect's answers and the clash resolver change rooms, openings, furniture and decor: the
    # plan works on its own copies (the variant's lists share their items with the caller's building)
    import copy as _copy
    vb = dict(vb, **{k: _copy.deepcopy(vb[k]) for k in ("rooms", "openings", "furniture", "decor") if k in vb})
    own = building_all if whole else dict(building_all, **{k: _copy.deepcopy(building_all[k])
                                                           for k in ("furniture", "decor") if k in building_all})
    out = {"whole": whole, "variant": variant, "building": vb if whole else own,
           "views": V.views_for(building_all, variant, brief=brief), "changes": V.variant_changes(building_all, variant),
           "warnings": list(vb["_variant"]["warnings"]), "assumed": [], "slabs": None, "roof": None,
           "open_rooms": set(), "outlines": {}, "ground_outline": [], "site": None, "faces": {},
           "brief": brief_args(building_all, brief), "terraces": [], "clips": [], "site_options": None,
           "overrides_applied": None}
    agent = O.overrides_of(building_all)
    if agent is not None:
        out["overrides_applied"] = {"round": agent.get("round"), "roof": [], "cameras": [], "materials": [],
                                    "sun": None, "site": None}
    # 25 Oct 2026 (user: "it's unacceptable to see clashing furniture at this stage"): every clash of two pieces is
    # planned apart before the build, for a whole building and a variant alike (wenart/blender/clashes.py; the
    # architect reports it as F5)
    from wenart.blender import clashes as CL
    out["clashes"] = CL.resolve(out["building"])
    out["warnings"] += [f"furniture clash left: {c['id']} and {c['other']} overlap {c['depth_m']:.2f} m"
                        for c in out["clashes"]["left"]]
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
    for c in (roof_in or {}).get("override_refused") or []:
        out["warnings"].append(f"roof {c['field']}: agent value {c['value']} not applied ({c['reason']})")
        if out["overrides_applied"] is not None:
            out["overrides_applied"].setdefault("roof_refused", []).append(c)
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
    # 25 Oct 2026 (user: "ai on the pod needs to be clever and able to answer the questions and make modifications
    # accordingly"): the answers to the architect's questions (the user's project file through the brief, the AI
    # architect's through the agent overrides) are carried out before the openings are clipped and anything else
    # is planned; a window is sized under the roof as the clip will cut it (``roof.opening_head_limit``)
    from wenart.blender import architect_actions as AA
    walls_by_id = {w["id"]: w for w in vb["walls"]}

    def head_limit(o):
        wall = walls_by_id.get(o.get("wall_id"))
        if over is None or wall is None or o.get("level_id") != over["id"]:
            return None
        return R.opening_head_limit(roof, over, wall, o)
    out["architect_answers"] = AA.answers_of(vb, out["brief"]["architect_answers"]["value"])
    out["architect_applied"] = AA.apply_answers(vb, out["architect_answers"], head_limit=head_limit)
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
    # fix round after P5 (22 Oct 2026): each level lists its rooms open to the sky (the decided roof openings, as the
    # shell leaves their ceiling out) for the camera search (camsearch.sloped_level); a list, not a set (JSON)
    for lv in vb["levels"]:
        lv["open_rooms"] = sorted(r["id"] for r in vb["rooms"]
                                  if r["level_id"] == lv["id"] and r["id"] in out["open_rooms"])
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
    if out["whole"]:
        # 25 Oct 2026: the architect's review (wenart/blender/architect.py) asks its questions and fixes the plan
        from wenart.blender import architect as AR
        out["style_family"] = style_family
        out["architect"] = AR.review(vb, out)
        # the openings the answers moved, resized or added, as built (the top-down labels draw them there)
        out["architect"]["openings_changed"] = [
            o for o in vb.get("openings") or []
            if any(k in o for k in ("corrected_by_ai", "adjusted_by_ai", "added_by_ai")) and isinstance(
                o.get("corrected_by_ai") or o.get("adjusted_by_ai") or o.get("added_by_ai"), dict)
            and (o.get("corrected_by_ai") or o.get("adjusted_by_ai") or o.get("added_by_ai")).get("by") == "architect"]
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
    # Milestone 13: the camera file (the flag, else the environment) and the light levers of this build.
    cameras_from = cameras_from_spec(args.cameras_from, str((building_all.get("project") or {}).get("id") or ""))
    cameras_extra = cameras_extra_flag(args.cameras_extra)
    try:
        levers = lighting.light_levers()
    except ValueError as exc:
        print(f"usage error: {exc}")
        return 2
    fp_args = fingerprint_args(args.building, args.style, args.assets, args.level, args.no_textures,
                               args.preview_samples, args.no_preview, args.no_glb, args.proxies, args.camera_policy,
                               args.lens_mm, args.variant, fp_brief, cameras_from=cameras_from,
                               cameras_extra=cameras_extra)
    fingerprint = build_fingerprint(fp_args)
    markers = bool(fp_brief["markers_in_final"]["value"])
    materials.set_markers(markers)
    if building_all.get("status") != "ok":
        print(f"building status is {building_all.get('status')!r}: nothing to build (needs review first)")
        return 2
    camera_file = camera_file_record(cameras_from)
    replay = {"plans": [], "dropped": [], "fingerprint": None, "policy": None}
    if camera_file is not None:
        if camera_file.get("missing"):
            print(f"--cameras-from {cameras_from}: no such file; the camera search runs for every room")
        else:
            replay = cams.replay_cameras(json.loads(Path(cameras_from).read_text(encoding="utf-8")))
            if not replay["plans"]:
                print(f"--cameras-from {cameras_from}: no camera records in the file; the camera search runs for "
                      f"every room")
            else:
                print(f"--cameras-from {cameras_from}: {len(replay['plans'])} cameras replayed "
                      f"({len(replay['dropped'])} records dropped); the search runs for the rooms without one"
                      + (" and for every room as extra cameras (--cameras-extra)" if cameras_extra else ""))
    print(f"LIGHT_VARIANT build={levers['variant'] or 'none'} sun_wm2={levers['sun_wm2']} ev_cap={levers['ev_cap']} "
          f"rig={levers['rig']} shell={levers['shell']}")
    try:
        prep = prepare(building_all, args.variant, brief, style_family=style_family_of(args.style))
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
    if whole and facade_sun_applies(sun_applied):
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
    # Milestone 13 (T6): the vegetation module (leaf atlases, Poly Haven hero models, grass clumps) finds the assets
    # folder through WENART_ASSETS first, then this scene property: the build's own --assets stands in for a job
    # that exports no WENART_ASSETS (scripts/jobs/full.sh does). Recorded in the manifest's site block (assets).
    from wenart.blender import vegetation as VG
    if args.assets:
        scene["wenart_assets_dir"] = str(args.assets)
    assets_record = assets_dir_record(os.environ.get("WENART_ASSETS"), args.assets, VG.assets_dir())
    library = MaterialLibrary(textures, args.assets, use_textures=not args.no_textures, refused=refused, style=style,
                              levers=levers)

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
    if whole and looks and (looks.get("facade") or {}).get("scheme"):
        # The facade scheme of the style family (user request of 24 Oct 2026): base and accent claddings where no
        # drawing and no brief name the facade, after the drawn parts.
        from wenart.blender import facade as FA

        scheme = FA.scheme_faces(building, style, levels)
        mapped, scheme_warnings = facade_faces(dict(building, facade={"faces": scheme}), prep["outlines"])
        warnings.extend(scheme_warnings)
        for wid, faces in mapped.items():
            prep["faces"].setdefault(wid, []).extend(faces)
        for face in scheme:
            assumed.append({"object": face.get("wall_id") or face.get("level_id"), "field": "facade_scheme",
                            "value": face["material"], "reason": face["reason"]})
    lib_openings = library_openings(building, levels, prep, brief, warnings, assets_dir=args.assets, style=style,
                                    assumed=assumed) if whole else {}
    geo_cache: dict = {}
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

    # pod P8 (11 Oct 2026): real03's build took 446 s, P5's 232 s, and the manifest could not say where: the time of
    # each phase (summed over the levels) goes to ``phase_seconds``
    phases: dict = {}
    mark = [t0]                                    # "setup": reading, assets, styles, scene reset

    def lap(name: str) -> None:
        now = time.time()
        phases[name] = round(phases.get(name, 0.0) + now - mark[0], 2)
        mark[0] = now

    lap("setup")
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
        lap("setup")
        shell.build_walls(building, level, col, library, style, manifest_objects, assumed, warnings, whole=wall_whole)
        lap("walls")
        shell.build_openings(building, level, col, library, style, pass_indices, manifest_objects, assumed, warnings,
                             library_openings=lib_openings, assets_dir=args.assets, geo_cache=geo_cache)
        shell.build_skirting(building, level, col, library, style, manifest_objects, assumed)
        floor_whole = None
        if whole:
            floor_whole = {"floor_voids": under["voids"] if under else [],
                           "ceiling_voids": above["voids"] if above else None,
                           "ceiling_planes": level.get("ceiling_planes"), "open_rooms": prep["open_rooms"],
                           "terrace_floor": (looks or {}).get("paving")}
        shell.build_floors_ceilings(building, level, col, library, style, manifest_objects, warnings, stairs=stairs,
                                    whole=floor_whole, assumed=assumed)
        if whole and prep["outlines"].get(level["id"]):
            counts = shell.build_outside_details(building, level, col, library, looks, prep["outlines"][level["id"]],
                                                 pass_indices, manifest_objects, assumed, style=style)
            for k, v in counts.items():
                outside[k] += v
        lap("openings_floors_outside")
        level_furniture = loose_furniture
        fit_not_built: list[dict] = []
        if whole and level.get("ceiling_planes"):     # decor under the roof stays inside it
            decor, fit_warnings, fit_not_built = decor_under_roof(loose_furniture, level)
            level_furniture = dict(loose_furniture, decor=decor)
            warnings.extend(fit_warnings)
            furniture_summary["not_built"].extend(fit_not_built)
        summary = furniture.create_furniture(level_furniture, level, col, library, style, args.assets, pass_indices,
                                             manifest_objects, assumed, warnings, use_proxies=args.proxies)
        add_furniture_summary(furniture_summary, summary)
        lap("furniture")
        # Milestone 12 (docs/milestone12.md §4.6-§4.7, contract §13.3; hook owned by track S): the scene checks S1-S6
        # of this level's built furniture and decor (``summary["objects"]``: {piece or decor id: object}).
        from wenart.blender import scene_checks as SC
        scene_report = SC.run_scene_checks(level_furniture, summary.get("objects") or {},
                                           out / "checks" / f"scene_{level['id']}.json")
        furniture_summary.setdefault("scene_checks", {})[level["id"]] = scene_report.get("counts") or {}
        # decor not built (S5 twice), dressed beds; fix round after P3 (16-17 Oct 2026): the pieces built into a
        # kitchen run (a drawn sink in its counter: furniture.built_in_ids), [{id, type, host, reason}]
        for key in ("decor_not_rested", "dressed_beds", "built_in"):
            furniture_summary.setdefault(key, []).extend(summary.get(key) or [])
        if (scene_report.get("counts") or {}).get("failed_build"):
            # a built item failing S5 cannot happen by construction (rest.plan_decor checks it); recorded as a failed
            # build (critical violations in checks/scene_<level>.json, read by the critic), the render goes on
            furniture_summary["scene_checks_failed"] = True
            warnings.append(f"level {level['id']}: scene check S5 failed for a built decor item; see "
                            f"checks/scene_{level['id']}.json")
        lap("scene_checks")
        # Milestone 11 (docs/milestone11.md §1.3 M2): the kitchens' tiled splashback behind the counter runs
        splash = shell.build_splashbacks(building, level, col, library, style, manifest_objects, assumed)
        furniture_summary["splashbacks"] = furniture_summary.get("splashbacks", 0) + splash
        add_furniture_summary(furniture_summary, shell.build_stairs(building, level, col, library, style, pass_indices,
                                                                    manifest_objects, assumed, warnings, plans=stairs,
                                                                    shaft=not arrives))
        lap("splashbacks_stairs")
        # Milestone 13 (K8): the replayed cameras of this level first; the search for the rooms without one (every
        # room with --cameras-extra, those cameras renamed with the suffix EXTRA_CAMERA_SUFFIX).
        level_room_ids = {r["id"] for r in building["rooms"] if r["level_id"] == level["id"]}
        replayed = [p for p in replay["plans"] if p["kind"] == "interior" and p.get("level_id") == level["id"]
                    and p.get("room_id") in render_rooms and p.get("room_id") in level_room_ids]
        covered = cams.replayed_rooms(replayed)
        # fix round after P6b (23 Oct 2026; docs/milestone13.md §7): a replayed camera a piece of this build blocks or
        # contains moves to the nearest free point with the same frame (camsearch.move_blocked_replayed); every build
        # (the agent's previews too), so a piece the agent moves onto a frozen camera is caught by the next build
        for line in replayed_moves(replayed, camera_building(building, fit_not_built)):
            print(f"camera replay: {line}")
        # fix round after P5 (22 Oct 2026): the search sees the decor that is built (camera_building)
        plans = [p for p in cams.plan_cameras(camera_building(building, fit_not_built), level["id"],
                                              policy=args.camera_policy, lens_mm=args.lens_mm)
                 if p.get("room_id") in render_rooms]
        if covered and not cameras_extra:
            plans = [p for p in plans if p.get("room_id") not in covered]
        elif covered:
            for p in plans:
                if p.get("room_id") in covered:
                    p["name"] = p["name"] + EXTRA_CAMERA_SUFFIX
                    p["extra"] = True
        no_view = [r for r in cams.rooms_without_view(building, level["id"], policy=args.camera_policy)
                   if r.get("room_id") in render_rooms and r.get("room_id") not in covered]
        rooms_without_view.extend(no_view)
        warnings.extend(f"{r['room_id']}: no view ({r['reason']})" for r in no_view)
        for plan in plans:
            plan.setdefault("policy", args.camera_policy)
            plan.setdefault("source", "searched")
        # Milestone 11 §17.3: the agent's fixed cameras. Fix round after P4a (17 Oct 2026): applied to the replayed
        # and the searched cameras together (merge_agent_cameras), so a set on a replayed name replaces it
        entries = O.camera_entries(building_all, "interior")
        plans, applied = merge_agent_cameras(replayed, plans, entries, level["id"], level_room_ids, replay)
        if entries:
            prep["overrides_applied"]["cameras"] += applied
        for plan in plans:
            interior_camera_fields(plan, prep["variant"])
        for line in dedupe_camera_names(plans, {p["name"] for p in camera_plans}):
            print(f"camera name: {line}")
            warnings.append(line)
        # fix round after P3 (16-17 Oct 2026): every room camera, replayed ones included, carries its room type
        # (wenart_room_type), so render.py puts the views of open-air rooms (terraces) under the exterior world
        check_camera_objects(cams.create_cameras(plans, col, manifest_objects,
                                                 room_types={r["id"]: r.get("room_type") for r in building["rooms"]}),
                             plans)
        camera_plans.extend(plans)
        for plan in plans:
            if plan.get("warning"):
                warnings.append(f"{plan['name']}: {plan['warning']}")
        lap("cameras")
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
        lap("door_rays")

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
            # fix round after P4b (17 Oct 2026): a flat_cut roof's slab edge and parapet carry the facade look
            covering, fascia, fascia_note = roof_slot_looks(roof, looks)
            mats = [shell.look_material(library, covering),
                    library.get(ceiling_style["material"], ceiling_style.get("asset")),
                    shell.look_material(library, fascia)]
            if fascia_note is not None:
                assumed.append(fascia_note)
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
            from wenart.blender import details as DT
            terrace_railings(roof, building, over, parapets, roof_col, library, manifest_objects, assumed,
                             kind=DT.balustrade_kind(style))
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
            from wenart.blender import details as DT
            prep["site"]["balustrade"] = DT.balustrade_kind(style)
            whole_info["site"] = S.build_site(prep["site"], site_col, looks,
                                              lambda look: shell.look_material(library, look), manifest_objects,
                                              assumed, glass=library.thin_glass())
        if prep["outlines"]:                           # Milestone 11 E10: plinth, slab bands, coping, surrounds
            from wenart.blender import facade as FA
            fac_col = common.get_or_make_collection("facade_details")
            extra_collections.append(fac_col)
            fplan = FA.articulation_plan(building, levels, prep["outlines"], prep["ground_outline"],
                                         (prep["site"] or {}).get("terrain"), roof, style, looks,
                                         (prep["site"] or {}).get("wells") or [])
            whole_info["facade_details"] = FA.build_articulation(fplan, fac_col,
                                                                 lambda look: library.thin_glass()
                                                                 if look.get("material") == "glass_guard"
                                                                 else shell.look_material(library, look),
                                                                 manifest_objects, assumed)
            if prep.get("architect") is not None:          # 25 Oct 2026: the architect's question about the rain
                from wenart.blender import architect as AR
                changed = prep["architect"].get("openings_changed")
                prep["architect"] = AR.summary([q for q in prep["architect"]["questions"] if q["id"] != "A1"]
                                               + [AR.drainage_answer(fplan.get("kit"), fplan.get("boxes") or [])],
                                               prep["architect"].get("applied"))
                prep["architect"]["openings_changed"] = changed
        # 11 Oct 2026 (real04): every other building on the plot, an instance of this one (wenart/blender/copies.py)
        from wenart.blender import copies as CP
        if CP.copies_of(building):
            copy_col = common.get_or_make_collection("building_copies")
            extra_collections.append(copy_col)            # hidden in the top-down previews like the roof
            built_cols = list(level_collections.values()) + [c for c in extra_collections
                                                              if c.name in ("roof", "facade_details")]
            whole_info["copies"] = CP.place_copies(building, built_cols, copy_col, manifest_objects, assumed)
        whole_info["terraces"] = prep["terraces"]
        whole_info["openings_clipped"] = prep["clips"]
        whole_info["main_facade"] = prep.get("main_facade")
        dropped = []
        if views["exterior"]:
            ext_col = common.get_or_make_collection("exterior")
            extra_collections.append(ext_col)
            model = E.build_model(building, levels, roof, prep["site"])
            # Milestone 13 (K8): the replayed exterior cameras stand in for the planned set (both with --cameras-extra)
            ext_replayed = [p for p in replay["plans"] if p["kind"] == "exterior"]
            # T5 review (15 Oct 2026): E.create_cameras aims an exterior camera at its target (exterior.py, T6);
            # a rotation-only record cannot be replayed there and is dropped with the reason (none in the M11 runs).
            for p in [p for p in ext_replayed if p.get("target") is None]:
                replay["dropped"].append({"name": p["name"], "reason": "exterior record without a target: the "
                                                                         "exterior camera needs one"})
                warnings.append(f"{p['name']}: replayed exterior camera dropped (no target in the record)")
            ext_replayed = [p for p in ext_replayed if p.get("target") is not None]
            # fix round part 2 (17 Oct 2026): a replayed aerial without sky keeps its target and distance, re-pitched
            # so the horizon is in its frame (CLAUDE.md: the sky, the sun and the horizon are always in the image)
            for name in repitch_replayed_aerials(ext_replayed):
                rp = next(p for p in ext_replayed if p["name"] == name)["replay"]
                warnings.append(f"{name}: replayed aerial re-pitched from {-rp['pitch_deg_old']:.1f} to "
                                f"{-rp['pitch_deg']:.1f} degrees down at {rp['lens_mm']:g} mm (its horizon lay at "
                                f"{rp['horizon_frac_old']:.2f} of the frame height, now {rp['horizon_frac']:.2f})")
            for p in ext_replayed:
                p.setdefault("view", None)
                p.setdefault("variant", prep["variant"])
                p.setdefault("sides", [])
                p.setdefault("region_id", None)
                p.setdefault("dropped_reason", None)
            if ext_replayed and not cameras_extra:
                ext_plans, dropped = [], []
            else:
                ext_plans, dropped = E.plan_exterior(model, building, levels, (prep["site"] or {}).get("plot") or [],
                                                     variant=prep["variant"])
                if ext_replayed:
                    for p in ext_plans:
                        p["name"] = p["name"] + EXTRA_CAMERA_SUFFIX
                        p["extra"] = True
            for p in ext_plans:
                p.setdefault("source", "searched")
            # Milestone 11 §17.3: the agent's fixed exterior cameras. Fix round after P4a (17 Oct 2026): applied to the
            # replayed and the planned set together (merge_agent_cameras): P4a's three "set ext_6" went to an empty
            # planned set, added a second ext_6 and Blender rendered the agent's pose as ext_6.001
            entries = O.camera_entries(building_all, "exterior")
            ext_plans, applied = merge_agent_cameras(ext_replayed, ext_plans, entries, replay=replay)
            if entries:
                north, src = S.north_deg(building)
                ext_points = E.building_points(model)        # fix round after P6a: the agent plans' frame
                lines = finish_agent_exterior_plans(
                    ext_plans, prep["variant"], geom_centre(model.outline), north, not src.startswith("assumed"),
                    visible=lambda p: E.visible_openings(model, building, levels, p["position"], p["target"],
                                                         p["lens_mm"], 0.0),
                    entrances=(building.get("site") or {}).get("entrances"),
                    frame=lambda p: E.frame_check(model, p["position"], p["target"], float(p["lens_mm"]), ext_points,
                                                  float(p.get("shift_y") or 0.0)))
                for line in lines:
                    print(f"agent camera: {line}")
                    warnings.append(line)
                prep["overrides_applied"]["cameras"] += applied
            for line in dedupe_camera_names(ext_plans, {p["name"] for p in camera_plans}):
                print(f"camera name: {line}")
                warnings.append(line)
            created = E.create_cameras(ext_plans, ext_col, manifest_objects)
            check_camera_objects(created, ext_plans)
            for p, ob in zip(ext_plans, created):      # each camera's source, as for the interior cameras
                ob["wenart_camera_source"] = p.get("source") or "searched"
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

    # pre-flight of pod P3: a camera record the build did not replay (its room is not a rendered room of this
    # building or level, or the build has no exterior views) is listed with the reason, never lost silently
    unused = unused_replayed(replay["plans"], camera_plans, replay["dropped"])
    replay["dropped"].extend(unused)
    warnings.extend(f"{u['name']}: replayed camera not used ({u['reason']})" for u in unused)
    lap("exterior")
    light_col = common.get_or_make_collection("lighting")
    if whole:
        north, north_source = S.north_deg(building)

        def ceiling_at(level, x, y):
            planes = level.get("ceiling_planes")
            flat = float(level["elevation"]) + float(level["ceiling_height"])
            return min([flat] + [a * x + b * y + c for a, b, c in planes or []])

        light_info = lighting.build_lighting(building, levels, style, hdri, light_col, manifest_objects, assumed,
                                             north_deg=north, north_source=north_source, ceiling_at=ceiling_at,
                                             exterior=bool(views["exterior"]), ceiling_voids=ceiling_voids(slabs))
        if north_source.startswith("assumed"):
            assumed.append({"object": "sun", "field": "north_deg", "value": north, "reason": north_source})
    else:
        light_info = lighting.build_lighting(building, levels, style, hdri, light_col, manifest_objects, assumed)
    bpy.context.view_layer.update()
    add_box3d(manifest_objects, warnings)
    # fix round after P5 (22 Oct 2026): a searched interior camera whose lens touches a built box (decor, the rig's
    # meshes, furniture) is named with the object; warning only, no camera moves (camsearch.lens_clearance)
    from wenart.blender import camsearch
    warnings.extend(hit["warning"] for hit in camsearch.lens_clearance(camera_plans, manifest_objects))
    mood = (style.get("lighting") or {}).get("mood")
    # render.py reads the mood here to pick the white-balance residual (§2.4).
    scene["wenart_mood"] = str(mood or "")

    lap("lighting")
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

    lap("previews")
    blend = out / "scene.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend), compress=True)
    lap("save")
    files = {"blend": blend.name}
    realized = None
    if not args.no_glb:
        glb = out / "scene.glb"
        # Milestone 13 (T6): the vegetation instances (leaf cards, grass clumps) reach the .glb only when realized;
        # after the .blend save, so the renders keep the light instances (site.realize_site_instances, polygon cap).
        try:
            realized = S.realize_site_instances()
        except Exception as exc:  # noqa: BLE001 - the glb is still written, with the cores and cards only
            warnings.append(f"vegetation instances not realized for scene.glb: {type(exc).__name__}: {exc}")
        try:
            bpy.ops.export_scene.gltf(filepath=str(glb), export_format="GLB", export_apply=True,
                                      export_extras=True, export_cameras=True, export_lights=True,
                                      export_image_format="JPEG", export_yup=True)
            files["glb"] = glb.name
        except Exception as exc:  # noqa: BLE001 - the export must not break the build
            warnings.append(f"glTF export failed: {exc}")
    lap("glb")
    recolour_parts_of(manifest_objects)          # Milestone 13 (T8 metric 10): recolour.fabric per object

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
        # Milestone 13 (K8): the camera file of the replay and what came of it
        "cameras_from": cameras_from_summary(camera_file, replay, camera_plans, cameras_extra),
        "light_variant": levers["variant"],
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
        "site": site_manifest_block((whole_info or {}).get("site") or site_summary(building), assets_record, realized),
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
        "phase_seconds": phases,
        "architect": architect_compact(prep.get("architect")),
        # 25 Oct 2026: the building as built (the architect's answers and the clash moves carried out): the checks
        # and reports that compare with the scene read it (views.scene_building_path)
        "building_built": str(out / BUILT_BUILDING),
    }
    (out / BUILT_BUILDING).write_text(json.dumps(prep["building"], indent=1, ensure_ascii=False,
                                                 default=lambda v: sorted(v) if isinstance(v, set) else str(v)),
                                      encoding="utf-8")
    (out / "scene_manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    if prep.get("architect") is not None:          # 25 Oct 2026: the architect's review as the architect hands it over
        from wenart.blender import architect as AR
        (out / "architect.md").write_text(AR.report_md(prep["architect"], Path(args.building).parent.name),
                                          encoding="utf-8")
        (out / "architect.json").write_text(json.dumps(prep["architect"], indent=1, ensure_ascii=False),
                                            encoding="utf-8")
    if whole:
        # 26 Oct 2026 (user: "reviewing the 3d model itself could be better ... than individual renders"): every
        # element of the model as built, measured (wenart/blender/model_review.py); the agent's code critic reads
        # the same review each round, the inspector's report lists it
        from wenart.blender import model_review as MR
        try:
            review = MR.review(prep["building"], manifest, prep)
            (out / MR.REVIEW_JSON).write_text(json.dumps(review, indent=1, ensure_ascii=False), encoding="utf-8")
            (out / MR.REVIEW_MD).write_text(MR.report_md(review, Path(args.building).parent.name), encoding="utf-8")
            print(f"MODEL_REVIEW {sum(1 for f in review['findings'] if f['severity'] == 'critical')} critical, "
                  f"{sum(1 for f in review['findings'] if f['severity'] == 'major')} major")
        except Exception as exc:  # noqa: BLE001 - the review is a record; it never stops a build
            warnings.append(f"model review failed: {type(exc).__name__}: {exc}")
    kinds = {}
    for o in manifest_objects:
        kinds[o["kind"]] = kinds.get(o["kind"], 0) + 1
    print(f"BUILD_DONE {out} objects={kinds} cameras={len(camera_plans)} furniture={furniture_summary['by_method']} "
          f"decor={furniture_summary['decor']} warnings={len(warnings)} seconds={manifest['seconds']}")
    return 0


BUILT_BUILDING = "building_built.json"


def architect_compact(rec: dict | None) -> dict | None:
    """The architect's review for the scene manifest: without the answers that passed (``architect.json`` keeps
    every answer; a big building has thousands)."""
    if rec is None:
        return None
    from wenart.blender import architect as AR
    return AR.compact(rec)


PITCHED_FASCIA_TYPES = ("gable", "hip", "mansard", "gambrel", "shed")
PITCHED_FASCIA_REASON = ("pitched roof: the eaves and verge edges are a fascia board in the gutter's {material} (not "
                         "drawn; the roof covering stretched over a 0.2 m edge read as a paper-thin sheet)")
FLAT_CUT_FASCIA_REASON = ("flat_cut roof: the slab edge and the {h:.2f} m parapet are walling finished like the "
                          "facade ({material}), with the coping on top, not the roof covering ({covering})")


def terrace_railing_runs(roof: dict, building: dict, level: dict, parapets: dict) -> list[dict]:
    """The railings on the lowered parapets of the roof terraces (pure; 24 Oct 2026): per parapet stretch of an
    opening with a ``guard_height`` over its ``parapet_height`` ``{"opening_id", "p", "q", "z", "height"}`` (the wall's
    centre line, standing on the parapet top, up to the guard height over the terrace floor)."""
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"]}
    guards = {o["id"]: o for o in roof.get("openings") or [] if o.get("guard_height")}
    out = []
    for wid, cuts in sorted(parapets.items()):
        w = walls.get(wid)
        for c in cuts:
            o = guards.get(c["opening_id"])
            if w is None or o is None:
                continue
            (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
            p = (x0 + (x1 - x0) * c["t0"], y0 + (y1 - y0) * c["t0"])
            q = (x0 + (x1 - x0) * c["t1"], y0 + (y1 - y0) * c["t1"])
            h = float(o["guard_height"]) - float(o["parapet_height"])
            if math.dist(p, q) > 0.3 and h > 0.05:
                out.append({"opening_id": o["id"], "wall_id": wid, "p": p, "q": q, "z": c["z_top"], "height": h})
    return out


def terrace_railings(roof: dict, building: dict, level: dict, parapets: dict, collection, library,
                     manifest_objects: list, assumed: list, kind: str = "glass_channel") -> list:
    """The railing objects of ``terrace_railing_runs`` (bpy): a stone coping on the parapet and a balustrade on it
    (``details.balustrade`` of ``kind``: 25 Oct 2026, user: "better finishes in the fences on top of the parapets"),
    one object per opening (kind ``railing``, assumed; slots metal, glass, coping)."""
    from wenart.blender import common
    from wenart.blender import details as D

    runs = terrace_railing_runs(roof, building, level, parapets)
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"]}
    made = []
    for oid in sorted({r["opening_id"] for r in runs}):
        parts, slots = [], []
        for r in (x for x in runs if x["opening_id"] == oid):
            width = float((walls.get(r["wall_id"]) or {}).get("thickness") or 0.2)
            cap = D.coping(r["p"], r["q"], r["z"], width)
            z = r["z"] + D.DIMS["coping_t"]
            metal, panes = D.balustrade(r["p"], r["q"], z, max(0.3, r["height"] - D.DIMS["coping_t"]), kind)
            parts += metal + panes + [cap]
            slots += [0] * sum(len(f) for _v, f in metal) + [1] * sum(len(f) for _v, f in panes) + [2] * len(cap[1])
        verts, faces = [], []
        for v, f in parts:
            base = len(verts)
            verts += list(v)
            faces += [[base + i for i in face] for face in f]
        name = f"roof_terrace_railing_{oid}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="railing",
                                    status="assumed", materials=[library.get("steel_brushed"), library.thin_glass(),
                                                                 library.get("concrete_polished")],
                                    face_material_indices=slots)
        reason = (f"roof terrace {oid}: the parapet stops at the eaves line; a {D.DIMS['coping_t']:.2f} m coping on it "
                  f"and a {kind.replace('_', ' ')} balustrade reach the guard height (not drawn; the kind follows the "
                  f"style)")
        manifest_objects.append({"name": ob.name, "wenart_id": name, "kind": "railing", "status": "assumed",
                                 "level_id": level["id"], "element_id": oid, "evidence": [], "material": None,
                                 "textured": False, "pass_index": None, "assumed": {"detail": "terrace_railing",
                                                                                    "reason": reason}})
        assumed.append({"object": ob.name, "field": "terrace_railing", "value": oid, "reason": reason,
                        "parent": str(oid), "kind": "railing"})
        made.append(ob)
    return made


def roof_slot_looks(roof: dict, looks: dict) -> tuple[dict, dict, dict | None]:
    """``(covering, fascia, assumed entry or None)``: the looks of the roof's slot 0 (``roof.SLOT_COVERING``) and slot
    2 (``roof.SLOT_FASCIA``: the eaves fascia, the edges of roof terraces and, on a ``flat_cut`` roof, the slab edge and
    the parapet ring; pure; fix round after P4b, 17 Oct 2026). Pod P4b (real03, a single drawn ground floor): the
    0.30 m parapet and the slab edge under it carried the roof covering (``concrete_tiles``), so the 0.6 m band read
    as a tiled mansard on a flat roof. A ``flat_cut`` roof's fascia slot now takes ``looks["facade"]`` (the parapet is
    a wall; ``facade.py`` adds the coping on top) and the build lists it as assumed with the reason; every other roof
    (real02 pitched, real04 mansard) keeps the roof look on both slots."""
    covering = looks["roof"]
    if roof.get("kind") == "flat_cut" and isinstance(looks.get("facade"), dict):
        facade = looks["facade"]
        note = {"object": "roof", "field": "parapet_material", "value": facade.get("material"),
                "reason": FLAT_CUT_FASCIA_REASON.format(h=float(roof.get("parapet") or 0.0),
                                                        material=facade.get("material"),
                                                        covering=covering.get("material"))}
        return covering, facade, note
    if roof.get("type") in PITCHED_FASCIA_TYPES:
        # 24 Oct 2026 (real04): the 0.2 m roof edge carried the tile texture stretched over it and read as a paper-thin
        # sheet; a pitched roof's eaves and verges get a fascia board in the gutter's look (facade.KIT_LOOKS)
        from wenart.blender import facade as FA
        material, colour, _why = FA.KIT_LOOKS["gutter"]
        fascia = {"material": material, "colour": colour, "rgb": None, "asset": None, "source": "build",
                  "assumed": True, "reason": PITCHED_FASCIA_REASON.format(material=material), "evidence": []}
        note = {"object": "roof", "field": "fascia_material", "value": material,
                "reason": PITCHED_FASCIA_REASON.format(material=material)}
        return covering, fascia, note
    return covering, covering, None


def unused_replayed(plans: list[dict], camera_plans: list[dict], dropped: list[dict] | None = None) -> list[dict]:
    """The replayed camera plans the build did not create (pure; pre-flight of pod P3): ``[{"name", "reason"}]`` for
    every plan of ``plans`` (``cameras.replay_cameras``) whose name is not among ``camera_plans`` and not already in
    ``dropped``: an interior camera whose room is not a rendered room of this build (another room id after a new
    ingest, a twin, a level left out by ``--level``, another variant), an exterior camera of a build without exterior
    views."""
    made = {p.get("name") for p in camera_plans}
    gone = {d.get("name") for d in dropped or []}
    out = []
    for p in plans or []:
        name = p.get("name")
        if name in made or name in gone:
            continue
        if p.get("kind") == "exterior":
            reason = "the build has no exterior views to replay it into"
        else:
            reason = (f"room {p.get('room_id')} on level {p.get('level_id')} is not a rendered room of this build "
                      f"(not in the building, a twin, another level or variant); the search covers this build's "
                      f"rendered rooms without a replayed camera")
        out.append({"name": name, "reason": reason})
    return out


REPITCH_REASON = ("CLAUDE.md: the sky, the sun and the horizon are always in the image; the replayed aerial's horizon "
                  "lay at {old:.2f} of the frame height (at or above its top: no sky), so it is re-pitched about its "
                  "target at the same distance to the planner's aerial pitch (exterior.AERIAL_HORIZON_FRAC, lens at "
                  "most exterior.AERIAL_LENS_MM); the lead's decision of 17 Oct 2026 (fix round part 2)")


def _down_pitch_deg(position, target) -> float:
    """The downward pitch of a camera at ``position`` aimed at ``target`` in degrees (pure; positive = down)."""
    dx, dy, dz = (float(target[k]) - float(position[k]) for k in range(3))
    return math.degrees(math.atan2(-dz, math.hypot(dx, dy)))


def repitch_replayed_aerials(plans: list[dict]) -> list[str]:
    """Re-pitch the replayed aerials without sky (pure; fix round part 2, 17 Oct 2026; the lead's decision): every
    exterior plan of view ``aerial`` with a target that is not the site view (``site_view``) and whose horizon lies
    at or above the top of its frame (``copies.horizon_fraction`` of its downward pitch, lens, sensor and aspect, less
    its vertical shift, >= 1) keeps its target and its distance to it and its compass direction; its pitch becomes
    ``copies.pitch_for_horizon(exterior.AERIAL_HORIZON_FRAC, min(lens, exterior.AERIAL_LENS_MM),
    exterior.AERIAL_PITCH_DEG)``, its lens at most ``AERIAL_LENS_MM``, its vertical shift 0. The plan gets
    ``position``, ``lens_mm``, ``shift_y``, ``pitch_deg`` (negative = down, as the planner's), ``horizon_frac`` and
    ``replay``: ``{"status": "repitched", "pitch_deg_old", "pitch_deg", "lens_mm_old", "lens_mm", "horizon_frac_old",
    "horizon_frac", "shift_y_old", "position_old", "distance_m", "reason"}``. Returns the names re-pitched."""
    from wenart.blender import copies as CP
    from wenart.blender import exterior as E

    done = []
    for p in plans or []:
        if p.get("kind") != "exterior" or p.get("view") != "aerial" or p.get("site_view"):
            continue
        pos, tgt = p.get("position"), p.get("target")
        if pos is None or tgt is None:
            continue
        pos, tgt = [float(v) for v in pos], [float(v) for v in tgt]
        dist = math.dist(pos, tgt)
        if dist <= 1e-6:
            continue
        sensor = float(p.get("sensor_mm") or CP.SENSOR_MM)
        res = p.get("resolution") or [1920, 1080]
        aspect = float(res[1]) / float(res[0]) if res and float(res[0]) > 0 else CP.ASPECT
        lens = float(p["lens_mm"])
        shift = float(p.get("shift_y") or 0.0)
        down = _down_pitch_deg(pos, tgt)
        frac = CP.horizon_fraction(down, lens, sensor, aspect) - shift / aspect
        if frac < 1.0:
            continue
        new_lens = min(lens, E.AERIAL_LENS_MM)
        new_down = CP.pitch_for_horizon(E.AERIAL_HORIZON_FRAC, new_lens, E.AERIAL_PITCH_DEG)
        hx, hy = pos[0] - tgt[0], pos[1] - tgt[1]
        h = math.hypot(hx, hy)
        ux, uy = (hx / h, hy / h) if h > 1e-9 else (1.0, 0.0)       # from the target to the camera, in plan
        a = math.radians(new_down)
        new_pos = [round(tgt[0] + ux * dist * math.cos(a), 4), round(tgt[1] + uy * dist * math.cos(a), 4),
                   round(tgt[2] + dist * math.sin(a), 4)]
        new_frac = CP.horizon_fraction(new_down, new_lens, sensor, aspect)
        p["replay"] = {"status": "repitched", "pitch_deg_old": round(-down, 3), "pitch_deg": round(-new_down, 3),
                       "lens_mm_old": lens, "lens_mm": new_lens, "horizon_frac_old": round(frac, 4),
                       "horizon_frac": round(new_frac, 4), "shift_y_old": shift, "position_old": pos,
                       "distance_m": round(dist, 4), "reason": REPITCH_REASON.format(old=frac)}
        p.update(position=new_pos, lens_mm=new_lens, shift_y=0.0, pitch_deg=round(-new_down, 3),
                 horizon_frac=round(new_frac, 4))
        done.append(p["name"])
    return done


def replayed_moves(plans: list[dict], building: dict) -> list[str]:
    """Fix round after P6b (23 Oct 2026; docs/milestone13.md §7, "a frozen camera that ends up inside a newly built
    piece is moved by the free-floor rule and marked"): ``camsearch.move_blocked_replayed`` on a level's replayed
    interior plans against ``building`` (the build passes ``camera_building``: what the search sees), run before the
    search and ``merge_agent_cameras``. A moved plan keeps ``source: replayed`` (frozen for the agent) with
    ``replay: {"status": "moved", ...}`` and its warning (the build's warning list takes it from the plan, as every
    camera warning); a camera with no free point keeps its pose with ``camsearch.BLOCKED_WARNING``. Returns one log
    line per camera the rule fired on. P6b's real03: yasama_2_2, 3_2, 5_2, 6_1 stood inside or against the 2.02 m
    fridges the reading typed at the end of the kitchen runs (3 black finals)."""
    from wenart.blender import camsearch

    return [f"{hit['name']}: {hit['warning']}" for hit in camsearch.move_blocked_replayed(plans, building)]


def cameras_from_summary(camera_file: dict | None, replay: dict, camera_plans: list[dict], extra: bool) -> dict | None:
    """The scene manifest's ``cameras_from`` (pure): the file record, the counts of replayed and searched cameras
    of the build, the dropped records and a ``reason`` when the search ran for everything (no file, a missing file,
    a file without camera records, real04's case). Fix round part 2 (17 Oct 2026): ``repitched``, the replayed
    aerials ``repitch_replayed_aerials`` re-pitched (none: an empty list). Fix round after P4a (17 Oct 2026):
    ``agent``, this build's agent cameras (``policy: agent``, source ``searched``: counted in ``searched``), and
    ``agent_replaced``, those that replace a replayed record (``replaced_replayed``). Fix round after P6b (23 Oct
    2026): ``moved``, the replayed interior cameras the build moved off a piece of this build (``replayed_moves``)."""
    if camera_file is None:
        return None
    replayed = [p["name"] for p in camera_plans if p.get("source") == "replayed"]
    searched = [p["name"] for p in camera_plans if p.get("source") != "replayed"]
    out = dict(camera_file, replayed=len(replayed), searched=len(searched), extra=bool(extra),
               dropped=list(replay.get("dropped") or []),
               repitched=[p["name"] for p in camera_plans
                          if (p.get("replay") or {}).get("status") == "repitched"],
               # fix round after P6b (23 Oct 2026): the replayed cameras moved off a piece of this build (§7)
               moved=[p["name"] for p in camera_plans if p.get("source") == "replayed"
                      and (p.get("replay") or {}).get("status") == "moved"],
               # fix round after P4a (17 Oct 2026): this build's agent cameras (counted with the searched ones) and
               # those of them that replace a replayed record (``replaced_replayed``: the baseline pose is gone)
               agent=[p["name"] for p in camera_plans if p.get("policy") == "agent" and p.get("source") != "replayed"],
               agent_replaced=[p["name"] for p in camera_plans if isinstance(p.get("replaced_replayed"), dict)])
    if camera_file.get("missing"):
        out["reason"] = "the camera file does not exist: the camera search ran for every room"
    elif not replay.get("plans"):
        out["reason"] = "no camera records in the file: the camera search ran for every room"
    elif not replayed:
        out["reason"] = "no replayed camera matched a rendered room of this variant: the camera search ran"
    return out


# Fix round after P4a (17 Oct 2026): the agent's cameras over the replayed ones (module docstring).
AGENT_REMOVED_REASON = "removed by the agent{seq}: {reason}"
AGENT_FRONTAL_MAX_DEG = 30.0       # a frontal / elevation view looks square at its facade (exterior_checks._faces)
AGENT_CORNER_MAX_DEG = 80.0        # a corner view looks at each of its two facades less than this off its normal
AGENT_AERIAL_MIN_DOWN_DEG = 5.0    # an aerial / site view looks down at least this much (eye-level views are level)
AGENT_AERIAL_VIEWS = ("aerial", "site")
AGENT_AERIAL_FLAGS = ("aerial_allowed", "site_view")   # fix round after P4b: only on a plan of an aerial / site view
DUPLICATE_CAMERA_SUFFIX = "_dup"


def merge_agent_cameras(replayed: list[dict], planned: list[dict], entries, level_id: str | None = None,
                        rooms: set | None = None, replay: dict | None = None) -> tuple[list[dict], list[dict]]:
    """``(plans, applied)`` (pure; fix round after P4a, 17 Oct 2026): the replayed cameras and the planned ones
    merged first (``replayed + planned``: the order the build creates them in), then the agent's camera ``entries``
    applied to the merged list (``overrides.apply_cameras``), so a ``set`` on a replayed name replaces that record
    instead of adding a second camera of that name (P4a: ``ext_6`` twice, Blender's ``ext_6.001``). Every agent
    plan gets ``source: searched`` (the frozen ``CAMERA_SOURCES``: searched | replayed; an agent camera is told by
    ``policy: agent``, the replaced record is kept in ``replaced_replayed``). A ``remove`` of a replayed camera goes
    to ``replay["dropped"]`` with the agent's reason (``AGENT_REMOVED_REASON``), so ``unused_replayed`` gives no
    false reason for it. Without entries the result is the merged list itself."""
    from wenart.blender import overrides as O

    plans = list(replayed) + list(planned)
    if not entries:
        return plans, []
    plans, applied = O.apply_cameras(plans, entries, level_id, rooms)
    for p in plans:
        if p.get("policy") == "agent" and p.get("source") != "replayed":
            p["source"] = "searched"
    if replay is not None:
        for rec in applied:
            if rec.get("result") == "removed" and rec.get("replayed"):
                seq = f" (overrides seq {rec['seq']})" if rec.get("seq") is not None else ""
                replay.setdefault("dropped", []).append(
                    {"name": rec["view_id"], "reason": AGENT_REMOVED_REASON.format(
                        seq=seq, reason=rec.get("reason") or "no reason given")})
    return plans, applied


def _look_dir(plan: dict) -> tuple[float, float] | None:
    """The plan's horizontal view direction (unit; pure), None without a target or when it looks straight down."""
    pos, tgt = plan.get("position"), plan.get("target")
    if pos is None or tgt is None:
        return None
    dx, dy = float(tgt[0]) - float(pos[0]), float(tgt[1]) - float(pos[1])
    n = math.hypot(dx, dy)
    return (dx / n, dy / n) if n > 1e-9 else None


def agent_exterior_view(plan: dict, centre, north: float = 0.0, north_known: bool = False,
                        entrances=None) -> dict | None:
    """Check an agent exterior plan's ``view`` and ``sides`` against its own pose (pure; fix round after P4a, 17 Oct
    2026). ``overrides.fixed_plan`` copies them from the camera the agent replaces, so P4a's corner pose for ext_6
    stayed "frontal, back", which hid the code finding X6 "no frontal view of the entrance". The copied view stays
    when the pose still is one: ``frontal`` / ``elevation`` look square (within ``AGENT_FRONTAL_MAX_DEG``) at the
    facade of their side, ``corner`` looks at each of its sides within ``AGENT_CORNER_MAX_DEG`` of its normal,
    ``aerial`` / ``site`` look down at least ``AGENT_AERIAL_MIN_DOWN_DEG``. Otherwise the view becomes ``agent``
    (exterior_checks then judges the frontal view by the pose itself) and the sides are re-derived; the plan's
    ``agent`` record keeps ``view_was`` and ``sides_was``. A plan without sides gets the side of its nearest axis
    from ``centre`` (as the build did for an added agent camera). Returns ``{"view_was", "sides_was", "view",
    "sides"}`` when the view changed, else None.

    Fix round after P4b (17 Oct 2026; review of the P4a fix round): ``fixed_plan`` also copies ``aerial_allowed``,
    ``site_view`` and ``horizon_frac`` (``overrides.CAMERA_KEEP_KEYS``) from the camera it replaces. A plan whose view
    is not ``aerial`` / ``site`` after the check (an aerial or site pose the agent brought to eye level, real04's
    ext_5 / ext_7) loses ``aerial_allowed`` and ``site_view`` (kept in the ``agent`` record as ``flags_was``, and in
    the returned dict as ``flags_dropped``): the vision critic was told "the aerial view the policy allows, not a
    finding" for an eye-level camera. ``horizon_frac`` is measured again from the plan's own pose
    (``plan_horizon_fraction``; the copied value was the replaced camera's, e.g. 0.78 for a level pose at 0.5); the
    old value is kept as ``horizon_frac_was``. The lead's decisions of 17 Oct 2026: (1) a replayed camera (set 1) is
    frozen and (2) the one frontal view X6 asks for is never turned into a non-frontal pose by the agent; both are
    rules of the agent's camera tool (wenart/agent/tools.py), this check stays the build's record of what a pose
    really is.

    Integration of the fix round after P4b: an ``entrance`` view stays ``entrance`` while the pose still frames its
    door (``entrances``: the ``site.entrances`` records; ``exterior_checks.entrance_view_problem``: at most 14 m from
    the door face, within 30 degrees of its axis, the door in the frame), else it becomes ``agent`` with
    ``view_was``. Without
    entrance records nothing can be judged and the view stays."""
    from wenart.blender import site as S

    view, sides = plan.get("view"), list(plan.get("sides") or [])
    look = _look_dir(plan)
    keep = True
    if view in ("frontal", "elevation", "corner") and look is not None:
        limit = AGENT_FRONTAL_MAX_DEG if view != "corner" else AGENT_CORNER_MAX_DEG
        wanted = sides[:1] if view != "corner" else sides
        normals = [S.side_direction(side, north) for side in wanted]
        keep = bool(normals) and all(
            n is not None and -(look[0] * n[0] + look[1] * n[1]) > math.cos(math.radians(limit)) for n in normals)
    elif view in ("aerial", "site") and plan.get("target") is not None:
        keep = _down_pitch_deg(plan["position"], plan["target"]) >= AGENT_AERIAL_MIN_DOWN_DEG
    elif view == "entrance" and look is not None and entrances:
        from wenart.blender import exterior_checks as X        # integration after P4b (docstring)

        rec = X.entrance_record({"site": {"entrances": list(entrances)}}, plan)
        keep = X.entrance_view_problem(rec, plan["position"], plan["target"], plan.get("lens_mm")) is None
    change = None
    if not keep:
        change = {"view_was": view, "sides_was": sides}
        plan["view"], plan["sides"] = "agent", []
    if not plan.get("sides"):
        d = (float(plan["position"][0]) - float(centre[0]), float(plan["position"][1]) - float(centre[1]))
        plan["sides"] = [S.side_of(S.AXES[S.nearest_axis(d)], north, north_known)]
    # fix round after P4b (docstring): the aerial / site flags only on an aerial / site pose, the horizon of this pose
    flags = {}
    if plan.get("view") not in AGENT_AERIAL_VIEWS:
        flags = {k: plan.pop(k) for k in AGENT_AERIAL_FLAGS if k in plan}
    frac_was = plan.get("horizon_frac")
    if frac_was is not None:
        frac = plan_horizon_fraction(plan)
        if frac is None:
            plan.pop("horizon_frac")
        else:
            plan["horizon_frac"] = frac
    if flags or (frac_was is not None and plan.get("horizon_frac") != frac_was):
        plan["agent"] = dict(plan.get("agent") or {})
        if flags:
            plan["agent"]["flags_was"] = flags
        if frac_was is not None and plan.get("horizon_frac") != frac_was:
            plan["agent"]["horizon_frac_was"] = frac_was
    if change is not None:
        change.update(view=plan["view"], sides=list(plan["sides"]))
        if flags:
            change["flags_dropped"] = sorted(flags)
        plan["agent"] = dict(plan.get("agent") or {}, view_was=change["view_was"], sides_was=change["sides_was"])
    return change


def plan_horizon_fraction(plan: dict) -> float | None:
    """Where the horizon lies in the frame of ``plan``'s own pose (pure; fix round after P4b, 17 Oct 2026):
    ``copies.horizon_fraction`` of the downward pitch from ``position`` to ``target``, the lens, the sensor and the
    aspect of the resolution, less the vertical shift (as ``repitch_replayed_aerials``), rounded to 4 places. None
    without a target or with the target on the camera."""
    from wenart.blender import copies as CP

    pos, tgt = plan.get("position"), plan.get("target")
    if pos is None or tgt is None or math.dist([float(v) for v in pos], [float(v) for v in tgt]) <= 1e-6:
        return None
    res = plan.get("resolution") or [1920, 1080]
    aspect = float(res[1]) / float(res[0]) if res and float(res[0]) > 0 else CP.ASPECT
    sensor = float(plan.get("sensor_mm") or CP.SENSOR_MM)
    frac = CP.horizon_fraction(_down_pitch_deg(pos, tgt), float(plan["lens_mm"]), sensor, aspect)
    return round(frac - float(plan.get("shift_y") or 0.0) / aspect, 4)


def finish_agent_exterior_plans(plans: list[dict], variant, centre, north: float = 0.0, north_known: bool = False,
                                visible=None, entrances=None, frame=None) -> list[str]:
    """The build's fields of this build's agent exterior plans (``policy: agent``, not replayed; pure but for
    ``visible``, ``plan -> visible opening ids``): ``index`` from the name's number (else the plan's own, at least
    1: ``ext_6_s`` gave 0 before, under the schema's minimum), ``variant``, ``visible_openings`` and the view check
    of ``agent_exterior_view`` (``entrances``: the ``site.entrances`` records, integration after P4b). Returns the
    log lines of the views it changed (fix round after P4a).

    Fix round after P6a (22 Oct 2026; pod P6a, real04): ``frame`` (``plan -> {"fill", "fits", "frame_target",
    "sky_share"}``, the build passes ``exterior.frame_check`` on its exterior model) records the plan's frame
    (``FRAME_KEYS`` of ``exterior_checks`` and the re-centred ``frame_target``): code X6, the vision critic's camera
    role and the report read what the agent's camera frames instead of its pose alone (P6a's ext_front_entrance: fill
    2.34, fits False, sky_share 0.0, counted as the frontal view). A frame that cannot be measured (``frame`` returns
    None or raises a ValueError, ZeroDivisionError, FloatingPointError or IndexError) is not recorded."""
    from wenart.blender import exterior_checks as X

    lines = []
    for p in plans:
        if p.get("policy") != "agent" or p.get("source") == "replayed":
            continue
        tail = str(p["name"]).rsplit("_", 1)[-1]
        p["index"] = int(tail) if tail.isdigit() and int(tail) >= 1 else max(1, int(p.get("index") or 1))
        p["variant"] = variant
        if visible is not None:
            p["visible_openings"] = visible(p)
        if frame is not None and p.get("position") and p.get("target"):
            try:
                rec = frame(p)
            except (ValueError, ZeroDivisionError, FloatingPointError, IndexError):
                rec = None                      # a measure only: the camera is built without it
            if isinstance(rec, dict) and all(k in rec for k in X.FRAME_KEYS):
                p.update(fill=round(float(rec["fill"]), 4), fits=bool(rec["fits"]),
                         sky_share=round(float(rec["sky_share"]), 4))
                if rec.get("frame_target") is not None:
                    p["frame_target"] = [round(float(v), 4) for v in rec["frame_target"]]
        change = agent_exterior_view(p, centre, north, north_known, entrances)
        if change is not None:
            lines.append(f"{p['name']}: the agent's pose is no longer the {change['view_was']} view of "
                         f"{', '.join(change['sides_was']) or 'no side'}; recorded as view agent "
                         f"({', '.join(change['sides'])})"
                         + (f"; {', '.join(change['flags_dropped'])} dropped" if change.get("flags_dropped") else ""))
    return lines


def dedupe_camera_names(plans: list[dict], taken=()) -> list[str]:
    """Never two cameras with one name (pure; fix round after P4a, 17 Oct 2026): Blender renames a second object of
    a name silently (``ext_6.001``) while the scene manifest keeps the name twice, so the render, the tests and the
    report lose the camera. Every plan whose name an earlier camera of the build (``taken``) or an earlier plan of
    ``plans`` already holds is renamed ``<name>_dup<k>`` (the first free k from 2) with ``renamed_from``; returns
    one log line per rename (the build's warnings)."""
    seen = set(taken or ())
    lines = []
    for p in plans:
        name = str(p["name"])
        if name in seen:
            k = 2
            while f"{name}{DUPLICATE_CAMERA_SUFFIX}{k}" in seen or any(
                    q.get("name") == f"{name}{DUPLICATE_CAMERA_SUFFIX}{k}" for q in plans):
                k += 1
            new = f"{name}{DUPLICATE_CAMERA_SUFFIX}{k}"
            p["renamed_from"], p["name"] = name, new
            lines.append(f"{name}: a second camera of this name ({p.get('policy') or p.get('source') or 'planned'}) "
                         f"renamed {new}; never two cameras with one name")
        seen.add(p["name"])
    return lines


def check_camera_objects(created, plans: list[dict]) -> None:
    """Every camera object carries its plan's name (fix round after P4a): raises RuntimeError naming the plans
    whose object Blender renamed (an object of that name existed: ``ext_6`` became ``ext_6.001`` in P4a), so the
    build stops before any render instead of writing a manifest the render cannot follow."""
    created = list(created or [])
    bad = [(p["name"], getattr(ob, "name", None)) for p, ob in zip(plans, created) if getattr(ob, "name", None)
           != p["name"]]
    if len(created) != len(plans):
        bad.append((f"{len(plans)} plans", f"{len(created)} camera objects"))
    if bad:
        raise RuntimeError("camera objects not named as their plans (plan, object): "
                           + ", ".join(f"{a} -> {b}" for a, b in bad))


def geom_centre(outline) -> tuple[float, float]:
    """The centre of an outline's bounding box (pure)."""
    xs, ys = [float(p[0]) for p in outline], [float(p[1]) for p in outline]
    return ((min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0) if xs else (0.0, 0.0)


SUN_TO_MAIN_FACADE_DEG = 45.0    # Milestone 11 (§7): the sun 45 degrees off the main facade's normal


def facade_sun_applies(sun_applied: dict | None) -> bool:
    """True when the build turns the sun to the main facade (``sun_from_main_facade``; pure; integration after
    P4b): no agent sun override, or one without ``azimuth_deg`` (an elevation-only override keeps the facade rule;
    it skipped it before and the style's azimuth lit real02's back)."""
    return sun_applied is None or "azimuth_deg" not in sun_applied


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
    from wenart.blender.shell import piece_built     # M12: unknown / no-model pieces are not built either

    for piece in building.get("furniture") or []:
        if piece.get("status") == "unverified" and piece_built(piece):
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
    from wenart.blender import shell as SH
    from wenart.blender.parametric import piece_bbox

    planes = level.get("ceiling_planes")
    if not planes:
        return []
    out = []
    for piece in building.get("furniture") or []:
        if piece.get("level_id") != level["id"] or not SH.piece_built(piece) or piece.get("type") == "stair":
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
# M11: a ceiling light under a slope hangs no lower than this above the floor. Fix round after P5: the copy of
# wenart.furniture.decor.MIN_LIGHT_BOTTOM_M (that module imports shapely, which Blender's Python has not; pinned equal
# in tests/test_m13_p5_fixround.py), checked for every hostless ceiling light under the roof, flush or not.
MIN_LIGHT_BOTTOM_M = 2.0
# Fix round after P6a, part I2 (22-23 Oct 2026; D_decor's ask, verify:look:1 step 5): curtains and blinds under the
# roof stay under the slope. The copies of wenart.furniture.decor.WINDOW_DECOR_TYPES and WINDOW_DECOR_CEILING_CLEAR_M
# (pinned equal in tests/test_m13_p6a_sky.py) and the decor stage's smallest curtain (decor_ai: a curtain 0.3 m tall
# or less is left out).
WINDOW_DECOR_TYPES = ("curtain", "blind")
WINDOW_DECOR_CEILING_CLEAR_M = 0.02
WINDOW_DECOR_MIN_H_M = 0.3
# Fix round after P6a (23 Oct 2026), review: the decor stage's rounding (decor_ai.window_items writes center[2] and
# size[2] to the millimetre from a ceiling read to 0.1 mm), so a curtain or blind it sized under the slope may stand up
# to 1 mm over the bound; such an item is kept as placed (P6a's dec_L1_005 / 014: size 1.009 against 1.0086).
WINDOW_DECOR_ROUND_TOL_M = 1e-3


def camera_building(building: dict, not_built) -> dict:
    """The building the camera search of a level sees (pure; fix round after P5, 22 Oct 2026): ``building`` without
    the decor ``decor_under_roof`` left out (``not_built``: [{id, ...}], a ceiling light under a low slope, a floor
    plant taller than the slope), so a fallback camera does not keep away from a light that is not built
    (``camsearch.floor_decor_rects``). P5's committed building still lists ``dec_L1_011`` (bottom 1.155 m): searched
    with it, ``cam_r_L1_banyo_1`` would stand at (7.02, 10.43) instead of (7.02, 10.63). ``building`` itself when
    nothing was left out."""
    ids = {n.get("id") for n in not_built or () if n.get("id") is not None}
    if not ids:
        return building
    return dict(building, decor=[d for d in building.get("decor") or [] if d.get("id") not in ids])


def ceiling_voids(slabs: dict | None) -> dict:
    """``{level id: [polygons]}``: the openings of the slab above each level of the slab plan (pure; fix round after
    P5, 22 Oct 2026), the ceiling openings the shell cuts (``shell.build_floors_ceilings``' ``ceiling_voids``), for
    the light rig's ceiling fixtures (``lighting.build_lighting``). P5's open stair core r_L0_merdiven had its
    ceiling fixture in the slab's opening, under no ceiling. ``{}`` without a slab plan."""
    out: dict = {}
    for level_id, entry in ((slabs or {}).get("by_level") or {}).items():
        above = (entry or {}).get("above")
        out[level_id] = [[list(p[:2]) for p in v] for v in (above or {}).get("voids") or [] if len(v) >= 3]
    return out


def decor_under_roof(building: dict, level: dict) -> tuple[list[dict], list[str], list[dict]]:
    """``(decor, warnings, not_built)``: the building's decor list with the hostless decor of a level under the roof
    fitted to its sloped ceiling (pure; ``level["ceiling_planes"]``, ``furniture.ceiling_above``). real02's exterior
    views showed attic decor outside the roof: ceiling lights placed at the flat ceiling height (``center[2]``) hung
    above the roof, and 1.6 m floor plants stood where the sloped ceiling is under 0.9 m high. A ceiling light whose given
    height reaches over the ceiling loses ``center[2]`` (the builder then hangs it flush under the slope); a floor
    piece taller than the ceiling over it is not built (``not_built``, with the reason). Pendants already lower
    themselves (``furniture._create_decor``). The decor placer should respect the slope in the first place.

    Fix round after P5 (22 Oct 2026): every hostless ceiling light is held to ``MIN_LIGHT_BOTTOM_M`` before it is
    kept, not only one that reaches over the ceiling: its bottom is its given height when it fits under the slope,
    else the flush height (the ceiling over it minus its height). A light with no height counts as flush (the
    builder hangs it flush), never as 0. Since the fix round after P4a the decor stage hangs its lights flush under
    the slope, so P5's ``dec_L1_011`` (1.155 m above the floor, 1.5 cm under the lens of ``cam_r_L1_banyo_1``),
    ``dec_L1_009`` (1.716 m) and ``dec_L1_013`` (1.155 m) passed the old "fits" keep and were built.

    Fix round after P6a, part I2 (22-23 Oct 2026; verify:look:1 step 5): a hostless curtain or blind
    (``WINDOW_DECOR_TYPES``) with its bottom given (``center[2]``) keeps its top ``WINDOW_DECOR_CEILING_CLEAR_M`` under
    the sloped ceiling over its footprint: a taller one is made shorter from the top (``size[2]``, its bottom kept;
    a warning), and one with ``WINDOW_DECOR_MIN_H_M`` or less left is not built (``not_built``, with the reason). The
    decor stage sizes them under the slope since this round (``wenart.furniture.decor_ai.window_items``); this is the
    builder's bound for any other source, e.g. an agent roof override applied after the decor stage (the committed
    real04 building carries a 45 degree one). P6a hung dec_L1_005 / dec_L1_014 (top 2.25 m) under a 1.83 m slope:
    both showed 0.4 m through the mansard roof."""
    from wenart.blender import furniture as F
    from wenart.blender import parametric as P

    decor = list(building.get("decor") or [])
    if not level.get("ceiling_planes"):
        return decor, [], []
    out, warnings, not_built = [], [], []
    for item in decor:
        dtype = item.get("type")
        center = list(item.get("center") or [])
        if item.get("level_id") == level["id"] and item.get("host_id") is None and dtype in WINDOW_DECOR_TYPES \
                and len(center) > 2 and center[2] is not None:
            kept, warning, dropped = _window_decor_under_roof(item, level, F, P)
            if kept is not None:
                out.append(kept)
            if warning:
                warnings.append(warning)
            if dropped is not None:
                not_built.append(dropped)
            continue
        if item.get("level_id") != level["id"] or item.get("host_id") is not None or len(center) < 2 \
                or dtype not in ("ceiling_light",) + FLOOR_DECOR_TYPES:
            out.append(item)
            continue
        w, d, h = P.decor_size(dtype, item.get("size") or [0.4, 0.4])
        ceiling, _how = F.ceiling_above(level, center, (w, d), float(item.get("rotation_deg") or 0.0))
        has_z = len(center) > 2 and center[2] is not None
        z = float(center[2]) if has_z else 0.0
        fits = z + h <= ceiling + 1e-3
        if dtype == "ceiling_light":
            # M11 pod G2b (real02 attic bathroom, ceiling 1.45 m) and P5 (real04 L1 bathroom, 1.27 m): a light hung
            # under such a low slope hangs at eye height, in front of the camera (depth 0.05 m); it is not built.
            # Fix round after P5: checked before the "fits" keep; a light with no height hangs flush.
            bottom = z if (has_z and fits) else ceiling - h
            if bottom < MIN_LIGHT_BOTTOM_M - 1e-9:
                reason = (f"ceiling light: the sloped ceiling over it is {ceiling:.2f} m high, its bottom "
                          f"{'is' if has_z and fits else 'would be'} {bottom:.2f} m above the floor "
                          f"(< {MIN_LIGHT_BOTTOM_M} m)")
                warnings.append(f"{item.get('id')}: {reason}; not built")
                not_built.append({"id": item.get("id"), "type": dtype, "reason": reason})
                continue
        if fits:
            out.append(item)
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


def _window_decor_under_roof(item: dict, level: dict, F, P) -> tuple[dict | None, str | None, dict | None]:
    """``(item to build or None, warning or None, not_built record or None)`` of one hostless curtain or blind under
    the roof (``decor_under_roof``, fix round after P6a part I2; pure): its top at most ``WINDOW_DECOR_CEILING_CLEAR_M``
    under the lowest ceiling over its footprint (``furniture.ceiling_above``), its bottom (``center[2]``) kept. Fix
    round after P6a (23 Oct 2026), review: an item at most ``WINDOW_DECOR_ROUND_TOL_M`` over that bound (the decor
    stage's millimetre rounding) is kept as placed, with no warning: with the old 1e-6 every attic curtain the decor
    stage sized under the slope (real04 P6a dec_L1_005 / 014, real02 P4a dec_L1_005 / 018) was "made 0.00 m shorter",
    and a roller blind of 0.3 m or less sized right would not have been built."""
    dtype = item.get("type")
    w, d, h = P.decor_size(dtype, item.get("size") or [0.4, 0.4])
    center = list(item["center"])
    ceiling, _how = F.ceiling_above(level, center, (w, d), float(item.get("rotation_deg") or 0.0))
    bottom = float(center[2])
    room = ceiling - WINDOW_DECOR_CEILING_CLEAR_M - bottom
    if bottom + h <= ceiling - WINDOW_DECOR_CEILING_CLEAR_M + WINDOW_DECOR_ROUND_TOL_M + 1e-9:
        return item, None, None
    if room <= WINDOW_DECOR_MIN_H_M + 1e-9:
        reason = (f"{dtype}: the sloped ceiling over it is {ceiling:.2f} m high; from its bottom at {bottom:.2f} m "
                  f"only {max(0.0, room):.2f} m are left {WINDOW_DECOR_CEILING_CLEAR_M} m under the slope "
                  f"(<= {WINDOW_DECOR_MIN_H_M} m)")
        return None, f"{item.get('id')}: {reason}; not built", {"id": item.get("id"), "type": dtype, "reason": reason}
    size = list(item.get("size") or [w, d])[:2] + [round(room, 4)]
    warning = (f"{item.get('id')}: {dtype} top {bottom + h:.2f} m above the floor, the sloped ceiling over it is "
               f"{ceiling:.2f} m high: made {h - room:.2f} m shorter from the top ({room:.2f} m tall, its bottom kept)")
    return dict(item, size=size), warning, None


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
