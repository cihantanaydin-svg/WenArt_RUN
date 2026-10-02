"""The stage table of a full project run (docs/milestone6.md §2.2) and the A/B stages (§6.3).

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
  render ``render_key``, polish ``attempt_key``, check answers by call key).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Sequence

from wenart.run.projects import PRIVATE_ROOT, ProjectRef

M5_LOOK_COMMIT = "a2adcef58ede7e4f9e92dd6a847e1e4692075131"
CATALOG = "wenart/furniture/catalog.json"
CHECK_YAML = "wenart/vision_check/check.yaml"
STYLE_TEST_PHOTO = "tests/fixtures/style_photo_synthetic-03_salon.jpg"
RENDER_RES = "1920x1080"
SMOKE_RES = "480x270"
SMOKE_SAMPLES = 16
SMOKE_CONTROL_VIEWS = 2          # control renders of stage 11 in the smoke profile
SMOKE_AB_CAMERAS = 2             # A/B cameras in the smoke profile (§2.5: "AB on synthetic-01 (2 cameras)")
PREVIEW_SAMPLES = 32
ALT_LOOK = "AgX - Punchy"
PREVIEW_QUALITY = 85             # the committed M5 previews (§5 row 11)
CONTROL_VIEWS = 8                # §6.2
LOOK_ALT = "look_alt"
REALISM_SETS_FLAG = "--sets"     # realism CLI: the pair sets to ask (contract request to area V)
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

BLENDER_CODE = ("wenart/blender/**", "wenart/canonical.py", "wenart/views.py")
FIT_CODE = ("wenart/furniture/fit.py", "wenart/furniture/catalog.py", CATALOG, "wenart/blender/parametric.py",
            "wenart/assets/models.py", "wenart/assets/fetch.py", "wenart/assets/web.py", "wenart/building.py",
            "wenart/geometry.py", "wenart/schema/**")
VISION_CODE = ("wenart/vision_check/**", "wenart/views.py", "wenart/recognition/vlm_client.py")


@dataclass(frozen=True)
class Stage:
    number: Optional[int]           # 0..17 for project stages (§2.2), None for A/B stages
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
    Stage(1, "pipeline", "cpu", "fingerprint", "failed",
          ("wenart/ingest/**", "wenart/building.py", "wenart/geometry.py", "wenart/schema/**"),
          ("building.json", "report.md")),
    Stage(2, "photos", "vlm", "photos", "warning",
          ("wenart/style/photos.py", "wenart/style/vocabulary.py", "wenart/recognition/vlm_client.py"),
          ("style_photos/passes.json", "style_photos/terms.json"), heavy=True),
    Stage(3, "style", "cpu", "always", "failed", ("wenart/style/**", "wenart/brief.py", "wenart/defaults.yaml"),
          ("style.json",)),
    Stage(4, "assets", "cpu", "always", "warning", ("wenart/assets/**",)),
    Stage(5, "fit", "cpu", "fingerprint", "failed", FIT_CODE, ("building_fitted.json",)),
    Stage(6, "layout", "vlm", "fingerprint", "failed",
          ("wenart/furniture/layout.py", "wenart/furniture/placer.py", "wenart/furniture/prompts.py",
           "wenart/furniture/schemas.py", "wenart/recognition/vlm_client.py", "wenart/building.py",
           "wenart/geometry.py", "wenart/synthetic/blocks.py"),
          ("building_furnished.json", "layout.json"), heavy=True),
    Stage(7, "decor", "cpu", "fingerprint", "failed",
          ("wenart/furniture/decor.py", "wenart/furniture/placer.py", "wenart/furniture/schemas.py",
           "wenart/building.py", "wenart/geometry.py"), ("building_decor.json",)),
    Stage(8, "refit", "cpu", "fingerprint", "failed", FIT_CODE, ("building_final.json",)),
    Stage(9, "build", "blender", "own", "failed", BLENDER_CODE, ("scene/scene.blend", "scene/scene_manifest.json"),
          heavy=True),
    Stage(10, "render", "blender", "own", "failed", BLENDER_CODE, ("renders/render_manifest.json",), heavy=True),
    Stage(11, "controls", "blender", "own", "warning", BLENDER_CODE + VISION_CODE, ("check/controls.json",),
          heavy=True),
    Stage(12, "gate", "gate", "own", "warning", ("wenart/gate/**",),
          ("gate/gate_calibration.json", "gate/gate_validation.json"), heavy=True),
    Stage(13, "polish", "diffusion", "own", "warning", ("wenart/polish/**",), ("polish/polish_manifest.json",),
          heavy=True),
    Stage(14, "expected", "cpu", "always", "failed", VISION_CODE, ("check/expected_views.json",)),
    Stage(15, "check", "vlm", "own", "failed", VISION_CODE, (), heavy=True),
    Stage(16, "combine", "cpu", "always", "failed", VISION_CODE, ("check/check_manifest.json",)),
    Stage(17, "report", "cpu", "always", "failed", ("wenart/report/**",),
          ("final/final_report.md", "final/final_manifest.json")),
    # A/B stages of §6.3 (records under out/run/ab_*.json; they count for the exit code, look_alt excepted).
    Stage(None, "ab_prepare", "cpu", "always", "failed"),
    Stage(None, "ab_m5", "cpu", "always", "failed", ("wenart/run/ab.py",),
          ("ab/m5/building_final.json", "ab/m5/scene_manifest.json", "ab/m5/render_manifest.json",
           "ab/building_m5.json")),
    Stage(None, "ab_render", "blender", "own", "failed", BLENDER_CODE,
          ("ab/renders/render_manifest.json", "ab/cameras_check.json"), heavy=True),
    Stage(None, "ab_controls", "blender", "own", "failed", BLENDER_CODE, (), heavy=True),
    Stage(None, "ab_pairs", "cpu", "always", "failed", VISION_CODE, ("ab/pairs.json",)),
    Stage(None, "ab_realism", "vlm", "own", "failed", VISION_CODE, (), heavy=True),
    Stage(None, "ab_look_alt", "vlm", "own", "failed", VISION_CODE, (), heavy=True),
    Stage(None, "ab_combine", "cpu", "always", "failed", VISION_CODE, ("check/realism/realism_ab.json",)),
)
STAGES = {s.name: s for s in STAGE_LIST}
PROJECT_STAGES = tuple(s.name for s in STAGE_LIST if s.number is not None)
AB_STAGES = tuple(s.name for s in STAGE_LIST if s.number is None)
STAGE_VERSION = {s.name: s.version for s in STAGE_LIST}
# A/B stages that never count for the exit code (§2.1: look_alt excluded).
AB_NOT_COUNTED = ("ab_look_alt",)


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
    return [tools.py, "-m", "wenart.ingest.pipeline", t(ref.project_dir), "--out", _out(ref)]


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
    return [tools.py, "-m", "wenart.furniture.layout", _out(ref, "building_fitted.json"), "--style",
            _out(ref, "style.json"), "--server", url, "--model", tools.model_id("qwen"), "--out",
            _out(ref, "building_furnished.json"), "--debug", _out(ref, "layout_debug"), "--passes", "2"]


def decor(tools: Tools, ref: ProjectRef, furnished: bool) -> list[str]:
    src = "building_furnished.json" if furnished else "building_fitted.json"
    return [tools.py, "-m", "wenart.furniture.decor", _out(ref, src), "--out", _out(ref, "building_decor.json")]


def refit(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.furniture.fit", _out(ref, "building_decor.json"), "--catalog", CATALOG,
            "--out", _out(ref, "building_final.json"), "--assets", t(tools.assets)]


def build(tools: Tools, ref: ProjectRef, force: bool = False) -> list[str]:
    cmd = [tools.py, "-m", "wenart.blender.cli", "build", "--building", _out(ref, "building_final.json"),
           "--style", _out(ref, "style.json"), "--assets", t(tools.assets), "--out", _out(ref, "scene"),
           "--preview-samples", str(PREVIEW_SAMPLES), "--camera-policy", "search"]
    return cmd if force else cmd + ["--reuse"]


def render_quality(tools: Tools, samples: Optional[int] = None) -> list[str]:
    """``--samples N --res WxH`` (+ ``--device cpu`` in the smoke profile)."""
    if tools.smoke:
        return ["--samples", str(samples if samples is not None else SMOKE_SAMPLES), "--res", SMOKE_RES,
                "--device", "cpu"]
    return ["--samples", str(samples if samples is not None else tools.render_samples), "--res", RENDER_RES]


def render(tools: Tools, ref: ProjectRef, force: bool = False) -> list[str]:
    cmd = [tools.py, "-m", "wenart.blender.cli", "render", "--scene", _out(ref, "scene/scene.blend"), "--out",
           _out(ref, "renders"), "--cameras", "all"] + render_quality(tools)[:4] + [
           "--exposure", "auto", "--white-balance", "auto"] + render_quality(tools)[4:]
    return cmd + (["--force"] if force else [])


def select_controls(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "select-controls", "--project-out", _out(ref)]


def control_render(tools: Tools, ref: ProjectRef, hide_sets: str) -> list[str]:
    """The hidden renders of stage 11 (polish.sh: same --hide-sets string, the normal renders' look)."""
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


def expected(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "expected", "--project-out", _out(ref)]


def plan_crops(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "plan-crops", "--project-out", _out(ref)]


def check_run(tools: Tools, ref: ProjectRef, key: str, url: str, seqs: int) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "run", "--project-out", _out(ref), "--model-key", key,
            "--server", url, "--kinds", "cycles,polished", "--workers", str(seqs)]


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
    return [tools.py, "-m", "wenart.report", "final", "--project-out", _out(ref)]


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
           "--preview-samples", str(PREVIEW_SAMPLES), "--camera-policy", "m5"]
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


def realism_pairs(tools: Tools, ref: ProjectRef, controls: bool = False) -> list[str]:
    cmd = [tools.py, "-m", "wenart.vision_check", "realism-pairs", "--project-out", _out(ref)]
    return cmd + (["--controls"] if controls else [])


def realism(tools: Tools, ref: ProjectRef, key: str, url: str, seqs: int,
            sets: Optional[Sequence[str]] = None) -> list[str]:
    cmd = [tools.py, "-m", "wenart.vision_check", "realism", "--project-out", _out(ref), "--model-key", key,
           "--server", url, "--workers", str(seqs)]
    if sets is not None:
        cmd += [REALISM_SETS_FLAG, ",".join(sets)]
    return cmd


def realism_combine(tools: Tools, ref: ProjectRef) -> list[str]:
    return [tools.py, "-m", "wenart.vision_check", "realism-combine", "--project-out", _out(ref)]


def realism_summary(tools: Tools, refs: Sequence[ProjectRef], controls_project: str, out_dir: Path) -> list[str]:
    return ([tools.py, "-m", "wenart.vision_check", "realism-summary", "--project-outs"]
            + [_out(r) for r in refs] + ["--controls-project", controls_project, "--out", t(out_dir)])


# --------------------------------------------------------------------------
# Deadline estimates (§2.3, measured in M5 on the RTX PRO 4500)
# --------------------------------------------------------------------------

EST_BUILD_S = 60.0
EST_RENDER_PER_VIEW_S = 8.0
EST_RENDER_FIXED_S = 60.0
EST_CONTROL_PER_VIEW_S = 8.0
EST_GATE_S = 150.0
EST_POLISH_PER_VIEW_S = 20.0
EST_SERVER_START_S = {"qwen": 300.0, "glm": 150.0}
EST_VLM_CALL_S = 4.4                 # per call, divided by the server's sequences


def est_render(views: int) -> float:
    return EST_RENDER_PER_VIEW_S * max(0, views) + EST_RENDER_FIXED_S


def est_controls(views: int) -> float:
    return EST_CONTROL_PER_VIEW_S * max(0, views)


def est_polish(views: int) -> float:
    return EST_POLISH_PER_VIEW_S * max(0, views)


def est_server(key: str) -> float:
    return EST_SERVER_START_S.get(key, max(EST_SERVER_START_S.values()))


def est_calls(calls: int, seqs: int) -> float:
    return EST_VLM_CALL_S * max(0, calls) / max(1, seqs)
