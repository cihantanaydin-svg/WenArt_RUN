"""The stage table of a full project run (docs/milestone6.md §2.2, docs/milestone7.md §9.1) and the A/B stages.

What: per stage its number, the GPU holder it needs (``cpu``, ``vlm``,
``blender``, ``gate``, ``diffusion``), its reuse rule, the status a failed
command gives (``failed`` stops the project, ``warning`` lets it go on), the
code files whose hash goes into the fingerprint, the outputs (relative to
the project's out folder) and the exact command lines of the existing CLIs.

Why: the command lines are written once, here; the scheduler only decides
when to run them, and the CPU tests compare them with golden lists.

How: the builders are pure functions of ``Tools`` (interpreters, assets
folder, render samples, profile) and a ``ProjectRef``; every path is passed
as ``views.repo_path_text`` (repo-relative inside the repo, else absolute),
because every CLI runs with cwd = repo root (§1.1). Reuse rules:

- ``fingerprint``: skipped (``reused``) when ``state.reusable`` holds;
- ``photos``: skipped when ``style_photos/passes.json`` already holds a valid
  answer of both check.yaml model ids for every current photo (§2.2 row 2);
- ``always``: deterministic and cheap, always run;
- ``own``: always invoked, the CLI reuses its own work (build ``--reuse``,
  render ``render_key``, polish ``attempt_key``, check answers by call key,
  recognize answers by key and input hash, detect by detection key).

Milestone 7 (§9.1): ``recognize`` (the two VLM passes over the pipeline's
recognition questions, GLM in phase 2 and Qwen in phase 3, seeded from the
committed ``results/recognition/<p>/``), ``pipeline_final`` (the pipeline
again with ``--answers``; ``--no-ai`` when an answer is missing, so it never
exits 4; an exit 4 with complete answers, i.e. new second-round questions,
runs it once more with ``--no-ai`` and is a ``warning``) and ``detect``
(OWLv2 on the Cycles and the polished images, phase 6). The A/B uses the
realism v2 commands (``realism2-*``, M7 §8.2): the control sets from the
control project's M6 ``ab/`` renders (rendered again only when they are
missing), ``look_alt`` from the main renders of the A/B projects, rendered
with ``--alt-look None`` (``ALT_LOOK``).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

from wenart.run.projects import PRIVATE_ROOT, ProjectRef

M5_LOOK_COMMIT = "a2adcef58ede7e4f9e92dd6a847e1e4692075131"
CATALOG = "wenart/furniture/catalog.json"
# The Objaverse library (docs/milestone7.md §6.6, §7): merged by catalog.load() after catalog.json; committed
# between the prep pod and the full runs (absent until then: a missing input hashes to None).
CATALOG_OBJAVERSE = "wenart/furniture/catalog_objaverse.json"
# Milestone 8 (docs/milestone8.md §2): the one library catalogue of every source; catalog.load() merges it instead of
# catalog_objaverse.json when it is committed (both are fit and refit inputs; FIT_CODE's catalog*.json covers both).
CATALOG_LIBRARY = "wenart/furniture/catalog_library.json"
CHECK_YAML = "wenart/vision_check/check.yaml"
RECOGNITION_DIR = "recognition"            # <out>/recognition: requests.json, answers_<slug>.json, crops/
EXIT_QUESTIONS = 4                         # wenart.ingest.pipeline: questions written, answers missing (§1.4)
# pipeline_final exited 4 although its answers were complete (the answers opened new questions, e.g. a raster
# page's second-round symbol questions): it runs once more with --no-ai and the stage is a warning, never failed.
SECOND_ROUND_NOTE = "second-round questions left unanswered (no-ai)"
RECOGNITION_SEEDS = "results/recognition"  # committed answers of earlier runs (--seed-answers <seeds>/<p>/)
STYLE_TEST_PHOTO = "tests/fixtures/style_photo_synthetic-03_salon.jpg"
RENDER_RES = "1920x1080"
SMOKE_RES = "480x270"
SMOKE_SAMPLES = 16
SMOKE_CONTROL_VIEWS = 2          # control renders of the controls stage in the smoke profile
SMOKE_AB_CAMERAS = 2             # A/B cameras in the smoke profile (§2.5: "AB on synthetic-01 (2 cameras)")
PREVIEW_SAMPLES = 32
SMOKE_PREVIEW_SAMPLES = 4        # the builds' top-down previews on the CPU (§2.5; 32 samples took 55 of 66 s)
ALT_LOOK = "None"                # M7 §6.1: the default look is AgX - Punchy, the A/B alternative is look None
PREVIEW_QUALITY = 85             # the committed M5 previews (§5 row 11)
CONTROL_VIEWS = 8                # §6.2
LOOK_ALT = "look_alt"
REALISM_SETS_FLAG = "--sets"     # realism2 CLI: the pair sets to ask
REALISM2_CALLS_PER_PAIR = 8      # 4 aspects x 2 orders (M7 §8.2)
NULL_IDENTICAL = "null_identical"   # asked with one call at a time (check.yaml realism2.null_identical_workers)
CHECK_KINDS = "cycles,polished,controls"   # M7 §8.1: the insertion controls are asked in every full run
CUDA_ALLOC = {"PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"}
# §6.2 control renders: set -> (own scene folder under ab/ or None for ab/scene, extra render flags).
CONTROL_RENDERS = {
    "ctl_flat": ("ctl_flat", []),
    "ctl_proxy": ("ctl_proxy", []),
    "ctl_direct": (None, ["--max-bounces", "0"]),
    "ctl_lowspp": (None, ["--no-denoise"]),
    "nuisance_ev": (None, ["--ev-offset", "0.3"]),
}
CONTROL_BUILD_FLAGS = {"ctl_flat": "--no-textures", "ctl_proxy": "--proxies"}
LOWSPP_SAMPLES = 4

# Code lists (§1.2): the files whose hash goes into a stage's fingerprint. For a stage that is reused by its
# fingerprint (and the gate calibration) the list covers the whole wenart import closure of the stage's CLI,
# function-level imports included (tests/test_run_stages.py computes it with ast), plus the data files it
# reads; the package __init__.py files of every listed module count too (state.code_hash).
BLENDER_CODE = ("wenart/blender/**", "wenart/canonical.py", "wenart/views.py")
# catalog*.json: catalog.json and, once committed, catalog_objaverse.json (catalog.load merges it).
FIT_CODE = ("wenart/furniture/fit.py", "wenart/furniture/catalog.py", CATALOG, "wenart/furniture/catalog*.json",
            "wenart/blender/parametric.py", "wenart/blender/proxies.py", "wenart/blender/geom2d.py",
            "wenart/blender/common.py", "wenart/assets/**", "wenart/style/**", "wenart/building.py", "wenart/units.py",
            "wenart/geometry.py", "wenart/schema/**")
# The pipeline (and pipeline_final): the vector, DXF/DWG and generic cores, the recognition questions and answers
# (crops, size table, the two-pass rule, check.yaml's model ids and slugs) and the room-type table.
PIPELINE_CODE = ("wenart/ingest/**", "wenart/synthetic/**", "wenart/building.py", "wenart/units.py",
                 "wenart/geometry.py", "wenart/schema/**", "wenart/recognition/**", "wenart/furniture/__init__.py",
                 "wenart/furniture/schemas.py", CHECK_YAML)
# wenart/furniture/decor.py: its DECOR_TYPES are the vision check's decor categories (Milestone 8: rug, wall_art).
VISION_CODE = ("wenart/vision_check/**", "wenart/views.py", "wenart/recognition/vlm_client.py",
               "wenart/gate/detect.py", "wenart/furniture/decor.py")
# gate calibrate (polish venv) + validate: the gate package (thresholds.yaml, models.yaml, validation.yaml
# included) and what it imports for the views, the expected objects and the scene geometry.
GATE_CODE = ("wenart/gate/**", "wenart/vision_check/expected.py", "wenart/views.py", "wenart/canonical.py",
             "wenart/hfcache.py", "wenart/brief.py", "wenart/geometry.py", "wenart/style/**",
             "wenart/blender/cameras.py", "wenart/blender/camsearch.py", "wenart/blender/common.py",
             "wenart/blender/geom2d.py", "wenart/blender/lighting.py", "wenart/blender/materials.py",
             "wenart/blender/parametric.py", "wenart/blender/proxies.py", "wenart/blender/shell.py")


# The decor stages (Milestone 9): the rules and the AI decorator (its slots read the placer, the wall art height
# parametric.piece_bbox, its question the layout's style text).
DECOR_CODE = ("wenart/furniture/decor.py", "wenart/furniture/decor_ai.py", "wenart/furniture/placer.py",
              "wenart/furniture/schemas.py", "wenart/furniture/layout.py", "wenart/furniture/prompts.py",
              "wenart/furniture/complete.py", "wenart/furniture/locked.py", "wenart/brief.py",
              "wenart/synthetic/**", "wenart/building.py", "wenart/units.py", "wenart/geometry.py",
              "wenart/schema/**", "wenart/style/**", "wenart/recognition/**", "wenart/blender/**")
DECOR_ANSWERS = "decor_ai_answers.json"


@dataclass(frozen=True)
class Stage:
    number: Optional[int]           # 0..20 for project stages (M7 §9.1), None for A/B stages
    name: str
    holder: str                     # cpu | vlm | blender | gate | diffusion
    reuse: str                      # fingerprint | photos | always | own
    on_failure: str                 # failed | warning
    code: tuple = ()
    outputs: tuple = ()             # relative to out_dir; "{name}" = the project name
    version: str = "1"
    heavy: bool = False             # starts only when now + estimate < deadline (§2.3)


STAGE_LIST = (
    Stage(0, "intake", "cpu", "fingerprint", "failed", ("wenart/intake.py", "wenart/run/projects.py"),
          ("input/{name}", "intake_manifest.json")),
    Stage(1, "pipeline", "cpu", "fingerprint", "failed", PIPELINE_CODE, ("building.json", "report.md")),
    Stage(2, "recognize", "vlm", "own", "warning", ("wenart/recognition/**", CHECK_YAML), (), heavy=True),
    Stage(3, "pipeline_final", "cpu", "fingerprint", "failed", PIPELINE_CODE, ("building.json", "report.md")),
    Stage(4, "photos", "vlm", "photos", "warning",
          ("wenart/style/photos.py", "wenart/style/vocabulary.py", "wenart/recognition/vlm_client.py"),
          ("style_photos/passes.json", "style_photos/terms.json"), heavy=True),
    Stage(5, "style", "cpu", "always", "failed", ("wenart/style/**", "wenart/brief.py", "wenart/defaults.yaml"),
          ("style.json",)),
    Stage(6, "assets", "cpu", "always", "warning", ("wenart/assets/**",)),
    Stage(7, "fit", "cpu", "fingerprint", "failed", FIT_CODE, ("building_fitted.json",)),
    Stage(8, "layout", "vlm", "fingerprint", "failed",
          ("wenart/furniture/layout.py", "wenart/furniture/placer.py", "wenart/furniture/prompts.py",
           "wenart/furniture/schemas.py", "wenart/furniture/complete.py", "wenart/furniture/locked.py",
           "wenart/recognition/**", "wenart/style/**", "wenart/building.py", "wenart/brief.py", "wenart/defaults.yaml",
           "wenart/units.py", "wenart/geometry.py", "wenart/synthetic/blocks.py", "wenart/schema/**",
           "wenart/blender/**"),
          ("building_furnished.json", "layout.json", "completion.json", "completion_report.md"), heavy=True),
    # Milestone 9 (docs/milestone9.md §4): the AI decor's two passes per room, asked in the layout's Qwen session
    # (answers stored by key in decor_ai_answers.json); a failure is a warning: the decor stage then falls back to
    # the rules for the rooms without both answers.
    Stage(9, "decor_ask", "vlm", "fingerprint", "warning", DECOR_CODE + ("wenart/recognition/vlm_client.py",),
          ("decor_ai_answers.json",), heavy=True),
    Stage(10, "decor", "cpu", "fingerprint", "failed", DECOR_CODE, ("building_decor.json",)),
    Stage(11, "refit", "cpu", "fingerprint", "failed", FIT_CODE, ("building_final.json",)),
    Stage(12, "build", "blender", "own", "failed", BLENDER_CODE, ("scene/scene.blend", "scene/scene_manifest.json"),
          heavy=True),
    Stage(13, "render", "blender", "own", "failed", BLENDER_CODE, ("renders/render_manifest.json",), heavy=True),
    # Milestone 9 (user request of 4 Oct 2026): the 3D files that open in Blender (a packed .blend and a .glb).
    Stage(14, "export", "blender", "own", "warning", BLENDER_CODE, ("export/export_manifest.json",), heavy=True),
    Stage(15, "controls", "blender", "own", "warning", BLENDER_CODE + VISION_CODE, ("check/controls.json",),
          heavy=True),
    Stage(16, "gate", "gate", "own", "warning", GATE_CODE,
          ("gate/gate_calibration.json", "gate/gate_validation.json"), heavy=True),
    Stage(17, "polish", "diffusion", "own", "warning", ("wenart/polish/**",), ("polish/polish_manifest.json",),
          heavy=True),
    Stage(18, "detect", "gate", "own", "warning", GATE_CODE + ("wenart/schema/building.schema.json",),
          ("detect/detect_manifest.json",), heavy=True),
    Stage(19, "expected", "cpu", "always", "failed", VISION_CODE, ("check/expected_views.json",)),
    Stage(20, "check", "vlm", "own", "failed", VISION_CODE, (), heavy=True),
    Stage(21, "combine", "cpu", "always", "failed", VISION_CODE, ("check/check_manifest.json",)),
    Stage(22, "report", "cpu", "always", "failed", ("wenart/report/**",),
          ("final/final_report.md", "final/final_manifest.json")),
    # A/B stages (M6 §6.3, realism v2 of M7 §8.2; records under out/run/ab_*.json; they count for the exit code).
    # ab_prepare, ab_m5, ab_render and ab_controls run only for the control project whose control renders are
    # missing on the volume (they are the M6 control renders otherwise).
    Stage(None, "ab_prepare", "cpu", "always", "failed"),
    Stage(None, "ab_m5", "cpu", "always", "failed", ("wenart/run/ab.py",),
          ("ab/m5/building_final.json", "ab/m5/scene_manifest.json", "ab/m5/render_manifest.json",
           "ab/building_m5.json")),
    Stage(None, "ab_render", "blender", "own", "failed", BLENDER_CODE,
          ("ab/renders/render_manifest.json", "ab/cameras_check.json"), heavy=True),
    Stage(None, "ab_controls", "blender", "own", "failed", BLENDER_CODE, (), heavy=True),
    Stage(None, "ab_pairs", "cpu", "always", "failed", VISION_CODE, ("ab/pairs_v2.json",)),
    Stage(None, "ab_realism", "vlm", "own", "failed", VISION_CODE, (), heavy=True),
    Stage(None, "ab_combine", "cpu", "always", "failed", VISION_CODE, ("check/realism/realism2_ab.json",)),
)
STAGES = {s.name: s for s in STAGE_LIST}
PROJECT_STAGES = tuple(s.name for s in STAGE_LIST if s.number is not None)
AB_STAGES = tuple(s.name for s in STAGE_LIST if s.number is None)
STAGE_VERSION = {s.name: s.version for s in STAGE_LIST}
# A/B stages that never count for the exit code: none in M7 (look_alt is the decided set of realism v2, §8.2; in
# M6 the ab_look_alt stage was not counted).
AB_NOT_COUNTED: tuple = ()
# Stages that download the fitted models (``fit --assets``): a failed download is a parametric fallback with
# exit 0, recorded as a warning and never reused (§2.2 rows 5 and 8).
DOWNLOAD_STAGES = ("fit", "refit")
DOWNLOAD_FALLBACK_PREFIX = "download of "     # wenart.furniture.fit.download_fitted's fallback_reason


def outputs_of(stage: str, name: str) -> list[str]:
    return [o.format(name=name) for o in STAGES[stage].outputs]


# --------------------------------------------------------------------------
# Command builders
# --------------------------------------------------------------------------

def t(path) -> str:
    """How a path is passed to a CLI: repo-relative inside the repo, else absolute (§1.1)."""
    from wenart.views import repo_path_text   # lazy: wenart.views imports numpy
    return repo_path_text(path)


@dataclass(frozen=True)
class Tools:
    py: str                                    # /workspace/venv/bin/python
    polish_py: str                             # /opt/wenart/venv-polish/bin/python
    assets: Path                               # /workspace/assets
    render_samples: int = 128
    smoke: bool = False                        # --profile smoke (§2.5)
    check_models: dict = field(default_factory=dict)   # check.yaml models: key -> {id, revision, slug, ...}
    private_root: Path = PRIVATE_ROOT          # uploads of private projects

    def model_id(self, key: str) -> str:
        return str((self.check_models.get(key) or {}).get("id") or "")

    def model_revision(self, key: str) -> str:
        return str((self.check_models.get(key) or {}).get("revision") or "")

    def model_slug(self, key: str) -> str:
        return str((self.check_models.get(key) or {}).get("slug") or key)


def _out(ref: ProjectRef, rel: str = "") -> str:
    return t(ref.out_dir / rel) if rel else t(ref.out_dir)


def intake(tools: Tools, ref: ProjectRef) -> list[str]:
    cmd = [tools.py, "-m", "wenart.intake", "stage", ref.name, "--out", t(ref.out_dir / "input" / ref.name)]
    if Path(tools.private_root) != PRIVATE_ROOT:
        cmd += ["--root", t(tools.private_root)]
    return cmd


def pipeline(tools: Tools, ref: ProjectRef) -> list[str]:
    """The first pipeline run: exit 0 ok, 1 needs_review, 4 recognition questions written (M7 §1.4)."""
    return [tools.py, "-m", "wenart.ingest.pipeline", t(ref.project_dir), "--out", _out(ref)]


def pipeline_final(tools: Tools, ref: ProjectRef, answers: bool = True, no_ai: bool = False) -> list[str]:
    """The pipeline again with the answers of ``<out>/recognition`` (M7 §9.1); ``no_ai`` when an answer is missing
    (the unanswered pieces stay unknown/unverified, so it never exits 4). The smoke profile passes no answers and
    ``--no-ai`` (the fake server's answers would agree)."""
    cmd = [tools.py, "-m", "wenart.ingest.pipeline", t(ref.project_dir), "--out", _out(ref)]
    if answers:
        cmd += ["--answers", _out(ref, RECOGNITION_DIR)]
    return cmd + (["--no-ai"] if no_ai else [])


def recognition_seeds(ref: ProjectRef, repo_root: Optional[Path] = None) -> Optional[Path]:
    """``results/recognition/<p>/`` (the committed answers of earlier runs) of a public project; None for a
    private one (its answers are never committed)."""
    if ref.private:
        return None
    from wenart.run.projects import REPO_ROOT
    return Path(repo_root or REPO_ROOT) / RECOGNITION_SEEDS / ref.name


def recognize(tools: Tools, ref: ProjectRef, key: str, url: Optional[str] = None, seqs: Optional[int] = None,
              seeds: Optional[Path] = None) -> list[str]:
    """``wenart.recognition.answers ask`` for one model (M7 §1.4). Without ``url`` the command only copies the
    stored answers of ``seeds`` (it asks no server when they complete the set: exit 0); the deadline comes from
    ``WENART_DEADLINE`` in the environment."""
    cmd = [tools.py, "-m", "wenart.recognition.answers", "ask", _out(ref, RECOGNITION_DIR), "--model-key", key]
    if url is not None:
        cmd += ["--server", url, "--workers", str(int(seqs or 1))]
    return cmd + (["--seed-answers", t(seeds)] if seeds is not None else [])


def photos_read(tools: Tools, ref: ProjectRef, key: str, url: str, photos: Sequence[Path]) -> list[str]:
    return ([tools.py, "-m", "wenart.style.photos", "read"] + [t(p) for p in photos]
            + ["--model-key", key, "--server", url, "--out", _out(ref, "style_photos/passes.json")])


def photos_combine(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.style.photos", "combine", _out(ref, "style_photos/passes.json"),
            "--out", _out(ref, "style_photos/terms.json")]


def style(tools: Tools, ref: ProjectRef, terms: bool = False) -> list[str]:
    cmd = [tools.py, "-m", "wenart.style", t(ref.project_dir), "--out", _out(ref, "style.json")]
    if terms:
        cmd += ["--photo-terms", _out(ref, "style_photos/terms.json")]
    return cmd


def assets(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.assets", "fetch", "--style", _out(ref, "style.json"), "--assets",
            t(tools.assets), "--size", "2k"]


def fit(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.furniture.fit", _out(ref, "building.json"), "--catalog", CATALOG,
            "--out", _out(ref, "building_fitted.json"), "--assets", t(tools.assets)]


def layout(tools: Tools, ref: ProjectRef, url: str) -> list[str]:
    """The empty-room layout (M4) and the completion of furnished rooms (M10 §2) in one run; ``--project-dir``: the
    brief keys furnished_rooms, furnished_rooms_keep(_size), render.twin_rooms (its brief.yaml is in the
    fingerprint through the project folder)."""
    return [tools.py, "-m", "wenart.furniture.layout", _out(ref, "building_fitted.json"), "--style",
            _out(ref, "style.json"), "--server", url, "--model", tools.model_id("qwen"), "--out",
            _out(ref, "building_furnished.json"), "--debug", _out(ref, "layout_debug"), "--passes", "2",
            "--project-dir", t(ref.project_dir)]


def decor_ask(tools: Tools, ref: ProjectRef, furnished: bool, url: str) -> list[str]:
    """The AI decor's two passes per room (Milestone 9, docs/milestone9.md §4), stored by key in the answers file."""
    src = "building_furnished.json" if furnished else "building_fitted.json"
    return [tools.py, "-m", "wenart.furniture.decor_ai", "ask", _out(ref, src), "--style", _out(ref, "style.json"),
            "--server", url, "--model", tools.model_id("qwen"), "--answers", _out(ref, DECOR_ANSWERS)]


def decor(tools: Tools, ref: ProjectRef, furnished: bool) -> list[str]:
    """Milestone 9: the AI decor's agreement and checks (``decor_ai apply``), the rules per room where it does not
    apply (no answers: no server, ``brief.decor: rules``)."""
    src = "building_furnished.json" if furnished else "building_fitted.json"
    return [tools.py, "-m", "wenart.furniture.decor_ai", "apply", _out(ref, src), "--style", _out(ref, "style.json"),
            "--answers", _out(ref, DECOR_ANSWERS), "--out", _out(ref, "building_decor.json"), "--debug",
            _out(ref, "decor_debug")]


def refit(tools: Tools, ref: ProjectRef) -> list[str]:
    """The fit after layout and decor, with the project's final style (``--style``: the library style filter,
    M7 §6.3; ``fit`` stays style-free)."""
    return [tools.py, "-m", "wenart.furniture.fit", _out(ref, "building_decor.json"), "--catalog", CATALOG,
            "--out", _out(ref, "building_final.json"), "--assets", t(tools.assets), "--style",
            _out(ref, "style.json")]


def preview_samples(tools: Tools) -> str:
    return str(SMOKE_PREVIEW_SAMPLES if tools.smoke else PREVIEW_SAMPLES)


def build(tools: Tools, ref: ProjectRef, force: bool = False, lens_mm: Optional[float] = None) -> list[str]:
    """``lens_mm``: the brief's ``render.lens_mm`` (Milestone 8; ``wenart.brief.lens_mm``), None for the automatic
    18 / 16 mm rule of the camera search."""
    cmd = [tools.py, "-m", "wenart.blender.cli", "build", "--building", _out(ref, "building_final.json"),
           "--style", _out(ref, "style.json"), "--assets", t(tools.assets), "--out", _out(ref, "scene"),
           "--preview-samples", preview_samples(tools), "--camera-policy", "search"]
    if lens_mm is not None:
        cmd += ["--lens-mm", f"{float(lens_mm):g}"]
    return cmd if force else cmd + ["--reuse"]


def render_quality(tools: Tools, samples: Optional[int] = None) -> list[str]:
    """``--samples N --res WxH`` (+ ``--device cpu`` in the smoke profile)."""
    if tools.smoke:
        return ["--samples", str(samples if samples is not None else SMOKE_SAMPLES), "--res", SMOKE_RES,
                "--device", "cpu"]
    return ["--samples", str(samples if samples is not None else tools.render_samples), "--res", RENDER_RES]


def render(tools: Tools, ref: ProjectRef, force: bool = False, alt_look: bool = False) -> list[str]:
    """``alt_look``: a project of the realism A/B also saves ``<cam>_alt_preview.jpg`` with ``ALT_LOOK`` from the
    same render result (the look_alt pairs of M7 §8.2)."""
    cmd = [tools.py, "-m", "wenart.blender.cli", "render", "--scene", _out(ref, "scene/scene.blend"), "--out",
           _out(ref, "renders"), "--cameras", "all"] + render_quality(tools)[:4] + [
           "--exposure", "auto", "--white-balance", "auto"] + render_quality(tools)[4:]
    if alt_look:
        cmd += ["--alt-look", ALT_LOOK]
    return cmd + (["--force"] if force else [])


def export(tools: Tools, ref: ProjectRef) -> list[str]:
    """The 3D files of the final scene (Milestone 9): ``<p>.blend`` (textures packed, cameras with their metered
    exposure) and ``<p>.glb`` in ``<out>/export``."""
    return [tools.py, "-m", "wenart.blender.cli", "export", "--scene", _out(ref, "scene/scene.blend"), "--renders",
            _out(ref, "renders/render_manifest.json"), "--out", _out(ref, "export"), "--name", ref.name]


def select_controls(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "select-controls", "--project-out", _out(ref)]


def control_render(tools: Tools, ref: ProjectRef, hide_sets: str) -> list[str]:
    """The hidden renders of the controls stage (polish.sh: same --hide-sets string, the normal renders' look)."""
    return [tools.py, "-m", "wenart.blender.cli", "render", "--scene", _out(ref, "scene/scene.blend"), "--out",
            _out(ref, "controls"), "--hide-sets", hide_sets, "--look-from",
            _out(ref, "renders/render_manifest.json")] + render_quality(tools)


def limit_hide_sets(hide_sets: str, n: Optional[int]) -> str:
    """The first ``n`` entries of a ``cam:id;cam:id+plug`` string (all for None)."""
    entries = [e for e in str(hide_sets or "").split(";") if e.strip()]
    return ";".join(entries if n is None else entries[:n])


def gate_calibrate(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.polish_py, "-m", "wenart.gate", "calibrate", "--project-out", _out(ref)]


def gate_validate(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.gate", "validate", "--project-out", _out(ref)]


def polish(tools: Tools, ref: ProjectRef, force: bool = False) -> list[str]:
    cmd = [tools.polish_py, "-m", "wenart.polish", "run", "--project-out", _out(ref)]
    return cmd + (["--force"] if force else [])


def detect(tools: Tools, ref: ProjectRef, force: bool = False) -> list[str]:
    """OWLv2 boxes of the Cycles and the chosen polished image of every polished view and of the control renders
    (``wenart.gate detect``, M7 §8.1; venv-polish; the deadline from ``WENART_DEADLINE``)."""
    cmd = [tools.polish_py, "-m", "wenart.gate", "detect", _out(ref), "--manifest",
           _out(ref, "polish/polish_manifest.json"), "--out", _out(ref, "detect")]
    return cmd + (["--force"] if force else [])


def expected(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "expected", "--project-out", _out(ref)]


def plan_crops(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "plan-crops", "--project-out", _out(ref)]


def check_run(tools: Tools, ref: ProjectRef, key: str, url: str, seqs: int) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "run", "--project-out", _out(ref), "--model-key", key,
            "--server", url, "--kinds", CHECK_KINDS, "--workers", str(seqs)]


def preference(tools: Tools, ref: ProjectRef, key: str, url: str, seqs: int) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "preference", "--project-out", _out(ref), "--model-key", key,
            "--server", url, "--kinds", "polished", "--workers", str(seqs)]


def style_photo_test(tools: Tools, ref: ProjectRef, key: str, url: str) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "style-photo", "--project-out", _out(ref), "--model-key", key,
            "--server", url, "--photo", STYLE_TEST_PHOTO, "--out", _out(ref, "check/style_photo_test.json")]


def combine(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "combine", "--project-out", _out(ref)]


def calibrate(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "calibrate", "--project-out", _out(ref)]


def report(tools: Tools, ref: ProjectRef) -> list[str]:
    """``--private`` for a private project: plan crops and debug images are named, never copied (§7.4); the
    report also detects it from the output folder, the flag makes it explicit."""
    cmd = [tools.py, "-m", "wenart.report", "final", "--project-out", _out(ref)]
    return cmd + (["--private"] if ref.private else [])


# --- A/B (§6.3) -----------------------------------------------------------

def ab_m5(tools: Tools, ref: ProjectRef, commit: str = M5_LOOK_COMMIT) -> list[str]:
    """AB prepare part 2: the M5 files of ``commit`` into out/ab/m5/ (``python -m wenart.run ab-m5``)."""
    return [tools.py, "-m", "wenart.run", "ab-m5", "--project", ref.name, "--project-out", _out(ref),
            "--commit", commit]


def ab_build(tools: Tools, ref: ProjectRef, variant: Optional[str] = None) -> list[str]:
    """The M5 building with the M6 look and the M5 cameras: ``out/ab/scene`` or ``out/ab/<ctl>/scene``."""
    scene = "ab/scene" if variant is None else f"ab/{variant}/scene"
    cmd = [tools.py, "-m", "wenart.blender.cli", "build", "--building", _out(ref, "ab/building_m5.json"),
           "--style", _out(ref, "style.json"), "--assets", t(tools.assets), "--out", _out(ref, scene),
           "--preview-samples", preview_samples(tools), "--camera-policy", "m5"]
    if variant is not None:
        cmd.append(CONTROL_BUILD_FLAGS[variant])
    return cmd + ["--reuse"]


def ab_render(tools: Tools, ref: ProjectRef, cameras: Optional[Sequence[str]] = None) -> list[str]:
    q = render_quality(tools)
    return ([tools.py, "-m", "wenart.blender.cli", "render", "--scene", _out(ref, "ab/scene/scene.blend"), "--out",
             _out(ref, "ab/renders"), "--cameras", ",".join(cameras) if cameras else "all"] + q[:4]
            + ["--exposure", "auto", "--white-balance", "auto"] + q[4:]
            + ["--alt-look", ALT_LOOK, "--preview-quality", str(PREVIEW_QUALITY)])


def ab_control_render(tools: Tools, ref: ProjectRef, set_name: str, cameras: Sequence[str]) -> list[str]:
    own_scene, extra = CONTROL_RENDERS[set_name]
    scene = f"ab/{own_scene}/scene/scene.blend" if own_scene else "ab/scene/scene.blend"
    samples = LOWSPP_SAMPLES if set_name == "ctl_lowspp" else None
    return ([tools.py, "-m", "wenart.blender.cli", "render", "--scene", _out(ref, scene), "--out",
             _out(ref, f"ab/{set_name}/renders"), "--cameras", ",".join(cameras)] + render_quality(tools, samples)
            + ["--look-from", _out(ref, "ab/renders/render_manifest.json"), "--preview-quality",
               str(PREVIEW_QUALITY)] + list(extra))


def realism2_pairs(tools: Tools, ref: ProjectRef, controls: bool = False,
                   ab_outs: Sequence[Path] = ()) -> list[str]:
    """``ab/pairs_v2.json`` (M7 §8.2): ``--controls`` for the control project (its M6 ``ab/`` renders);
    ``--project-outs`` = the outputs of every look_alt project of the run (the same list for every project, so
    each takes its share of the same 32-camera selection)."""
    cmd = [tools.py, "-m", "wenart.vision_check", "realism2-pairs", "--project-out", _out(ref)]
    if controls:
        cmd.append("--controls")
    if ab_outs:
        cmd += ["--project-outs"] + [t(o) for o in ab_outs]
    return cmd


def realism2(tools: Tools, ref: ProjectRef, key: str, url: str, seqs: int,
             sets: Optional[Sequence[str]] = None) -> list[str]:
    """Every pair of ``ab/pairs_v2.json`` (or ``sets``), 8 calls per pair, into
    ``check/realism/answers_realism2_<slug>.json``."""
    cmd = [tools.py, "-m", "wenart.vision_check", "realism2", "--project-out", _out(ref), "--model-key", key,
           "--server", url, "--workers", str(seqs)]
    if sets is not None:
        cmd += [REALISM_SETS_FLAG, ",".join(sets)]
    return cmd


def realism2_combine(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "realism2-combine", "--project-out", _out(ref)]


def realism2_summary(tools: Tools, refs: Sequence[ProjectRef], controls_out: Optional[Path],
                     out_dir: Path) -> list[str]:
    """``$RESULTS/realism/realism2_summary.json``: the look_alt decision over ``refs`` with the control project's
    output folder (None: no control project, the summary has no signal)."""
    cmd = ([tools.py, "-m", "wenart.vision_check", "realism2-summary", "--project-outs"]
           + [_out(r) for r in refs])
    if controls_out is not None:
        cmd += ["--controls-project", t(controls_out)]
    return cmd + ["--out", t(out_dir)]


# --------------------------------------------------------------------------
# Deadline estimates (§2.3, measured in M5 on the RTX PRO 4500; the scheduler divides every estimate by the pod's
# GPU speed, wenart.run.plan.GPU_SPEED, M7 §9.3)
# --------------------------------------------------------------------------

EST_BUILD_S = 60.0
EST_EXPORT_S = 120.0                  # Milestone 9: open the scene, pack the textures, save the .blend, write the .glb
EST_RENDER_PER_VIEW_S = 8.0
EST_WINDOW_PULL_PER_VIEW_S = 1.0      # M7 §9.3: the window pull of each view (+ its alt look)
EST_RENDER_FIXED_S = 60.0
EST_CONTROL_PER_VIEW_S = 8.0
EST_GATE_S = 150.0
EST_POLISH_PER_VIEW_S = 20.0
# The detector (M7 §8.1) is not timed by the prep pod: model load plus about two images per view, generous.
EST_DETECT_FIXED_S = 60.0
EST_DETECT_PER_VIEW_S = 3.0
EST_SERVER_START_S = {"qwen": 300.0, "glm": 150.0}
EST_VLM_CALL_S = 4.4                 # per call, divided by the server's sequences


def est_render(views: int) -> float:
    return (EST_RENDER_PER_VIEW_S + EST_WINDOW_PULL_PER_VIEW_S) * max(0, views) + EST_RENDER_FIXED_S


def est_detect(views: int) -> float:
    return EST_DETECT_FIXED_S + EST_DETECT_PER_VIEW_S * max(0, views)


def est_realism2(pairs: int, null_pairs: int, seqs: int) -> float:
    """8 calls per pair at ``seqs`` calls at once; the ``null_identical`` pairs one call at a time (M7 §9.1)."""
    other = max(0, pairs - null_pairs)
    return (est_calls(REALISM2_CALLS_PER_PAIR * other, seqs)
            + est_calls(REALISM2_CALLS_PER_PAIR * max(0, null_pairs), 1))


def est_controls(views: int) -> float:
    return EST_CONTROL_PER_VIEW_S * max(0, views)


def est_polish(views: int) -> float:
    return EST_POLISH_PER_VIEW_S * max(0, views)


def est_server(key: str) -> float:
    return EST_SERVER_START_S.get(key, max(EST_SERVER_START_S.values()))


def est_calls(calls: int, seqs: int) -> float:
    return EST_VLM_CALL_S * max(0, calls) / max(1, seqs)
