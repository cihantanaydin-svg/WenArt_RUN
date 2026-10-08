"""Change-gate API (docs/milestone5.md §1.3, §4): accept a polished image only when its geometry is unchanged.

What: ``Gate`` compares a polished image with its Cycles reference and
accepts it only when every hard check passes (edges lost and added,
monocular depth, SAM 2.1 masks, colour, neutral walls; DINOv2 features are
soft until the calibration separates them). ``decide`` turns stored
metrics into a decision with the current thresholds, so a reused polish
attempt is re-decided without running any model.

Why a separate module: the polish ladder, the calibration and the GPU tests
all import ``Gate``/``decide``; this module imports neither torch,
transformers, OpenCV nor Pillow at import time (the check modules are
imported inside the methods, the model wrappers in ``gate/models.py``
import torch/transformers lazily), so ``import wenart.gate`` works on a
CPU-only machine.

Contract (§1.3):

- ``Gate(thresholds=None, models=None, device="cuda")``: ``thresholds`` a
  dict or a YAML path (None = this package's ``thresholds.yaml``); ``models``
  a ``wenart.gate.models.Models`` (None = created on first model use; tests
  pass a fake with ``depth(rgb)``, ``sam_masks(rgb, boxes)``,
  ``dino_tokens(rgb)`` and optionally ``info()``/``settle()``).
- ``Gate.prepare(view, ref_rgb) -> Reference``: regions, reference edges, Lab
  means and (on first use, then cached) the model outputs on the reference;
  one cached ``Reference`` per (camera, render key, png, image sha256).
- ``Gate.compare(ref, test_rgb) -> {"decision": "accept"|"reject", "reasons",
  "notes", "metrics", "gate_key"}``; ValueError when ``test_rgb`` is not the
  view size.
- ``Gate.release_gpu() -> bool``: the gate models off the GPU for the rest
  of the run (the polish calls it after a CUDA OOM, before its retry).
- ``decide(metrics, thresholds) -> (decision, reasons, notes)``: pure.

Metrics (§4.2): ``{"<check>": {"global": float|None, "regions": {id: float},
"skipped": {id: reason}, ...}, "regions": {id: {"kind", "pixels"}},
"seconds": {check: s}, "size": [W, H]}``. A check that could not be computed
(a model failed) carries ``"error"``; ``decide`` then fails it (a hard check
that was not computed has not passed).

Cost: ``prepare`` indexes what every comparison reuses (the valid pixels
grouped by region, ``layout.Layout``; the reference edge pixels per object,
``edges.EdgeIndex``; the reference Lab of the valid pixels) and the first
comparison caches what depends on the reference model outputs (depth
samples and range, DINOv2 norms, patch selections). A comparison then makes
no full-image pass per region (pod run 0b: the colour, depth and features
checks took 5-24 s per comparison on a contended pod; at 1920 x 1080 with
15 objects the CPU time per comparison went from 0.76 to 0.30 s on 4 cores).
The numbers are those of the mask-based functions of the check modules
(``edges.edge_metrics``, ``colour.colour_metrics``, ``depth.depth_metrics``,
``features.feature_metrics``) within 1e-4; ``tests/test_gate.py`` checks it.

Milestone 10 (docs/milestone10.md §3.3 item 5): the same gate runs on the exterior views (no room, no level).
``prepare`` takes the walls' albedo of an exterior view from the facade look (``colour.exterior_albedo``);
nothing else depends on the room. The calibration records its comparisons per view kind and the polish decides
per kind (``wenart.gate.calibrate.exterior_polish``).

``gate_key`` = first 16 hex of sha256 over GATE_CODE_VERSION, the gate model
repos/revisions, the reference image sha256 and the threshold entries that
shape the metrics (radius, Canny, minimum region sizes; not the pass/fail
limits, which ``decide`` re-applies).
"""
from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

GATE_DIR = Path(__file__).resolve().parent
THRESHOLDS_PATH = GATE_DIR / "thresholds.yaml"
MODELS_PATH = GATE_DIR / "models.yaml"
GATE_CODE_VERSION = "m5.2"          # m5.2: oriented low-threshold reference edges in added_lines
REFERENCE_CACHE = 2          # references kept in memory (each holds a few full-size arrays)

CHECKS = ("edges", "added_lines", "depth", "masks", "colour", "neutral", "features")
# (scope, threshold key, op) per check: the limits ``decide`` compares.
LIMITS = {
    "edges": (("global", "global_min", ">="), ("region", "region_min", ">=")),
    "added_lines": (("region", "region_max_len_frac", "<="),),
    "depth": (("global", "global_max", "<="), ("region", "region_max", "<=")),
    "masks": (("region", "region_min", ">="),),
    "colour": (("global", "global_max", "<="), ("region", "region_max", "<=")),
    "neutral": (("region", "region_max_dchroma", "<="),),
    "features": (("region", "region_min", ">="),),
}
GENERIC_LIMITS = (("global", "global_min", ">="), ("global", "global_max", "<="),
                  ("region", "region_min", ">="), ("region", "region_max", "<="))
NOT_THRESHOLDS = ("calibration",)


def _load_yaml(path) -> dict:
    import yaml
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def load_thresholds(path: Optional[str | Path] = None) -> dict:
    """The gate thresholds (this package's ``thresholds.yaml`` when ``path`` is None)."""
    return _load_yaml(THRESHOLDS_PATH if path is None else path)


def load_models_config(path: Optional[str | Path] = None) -> dict:
    """The gate model list ``{"models": {"depth"|"sam"|"dino": {repo, revision, licence, allow_patterns}}}``."""
    return _load_yaml(MODELS_PATH if path is None else path)


def limits_of(check: str, th: dict) -> list[tuple[str, str, str]]:
    """The ``(scope, key, op)`` limits of one check that are set in its thresholds."""
    table = LIMITS.get(check, GENERIC_LIMITS)
    return [lim for lim in table if th.get(lim[1]) is not None]


def compute_params(thresholds: dict) -> dict:
    """Threshold entries that shape the metrics (everything except ``hard``, the limits and the calibration)."""
    out = {}
    for check, th in sorted(thresholds.items()):
        if check in NOT_THRESHOLDS or not isinstance(th, dict):
            continue
        limit_keys = {lim[1] for lim in LIMITS.get(check, GENERIC_LIMITS)}
        out[check] = {k: v for k, v in sorted(th.items()) if k != "hard" and k not in limit_keys}
    return out


def image_sha256(rgb) -> str:
    """sha256 of a uint8 image (shape + C-order bytes), independent of the PNG encoder."""
    a = np.ascontiguousarray(np.asarray(rgb, dtype=np.uint8))
    h = hashlib.sha256(json.dumps(list(a.shape)).encode())
    h.update(a.tobytes())
    return h.hexdigest()


def make_gate_key(reference_sha256: str, model_info: dict, thresholds: dict) -> str:
    """First 16 hex of sha256 over the gate code version, model revisions, reference sha and metric parameters."""
    payload = {"code": GATE_CODE_VERSION,
               "models": {k: {"repo": v.get("repo"), "revision": v.get("revision")}
                          for k, v in sorted((model_info or {}).items())},
               "reference": reference_sha256, "params": compute_params(thresholds)}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


@dataclass
class Reference:
    """What ``Gate.prepare`` computes once per view.

    ``gate_key`` is the key ``compare`` reports for this reference, so the
    polish can tell whether stored gate metrics are still valid before
    comparing. ``sha256`` is ``image_sha256(rgb)``. ``regions`` is the
    ``views.Regions`` of the view, ``edges`` the reference edges (bool),
    ``lab_means`` ``{region id: [L, a, b] | None}`` over valid pixels.
    ``model_outputs`` fills on first use: ``depth`` (disparity), ``sam``
    (``{"boxes", "skipped", "masks", "reliability"}``), ``dino`` (tokens).
    ``valid`` = not background and not a window pane; ``match_dist`` =
    distance to the nearest reference Canny or geometry edge (added lines);
    ``ref_angle`` the oriented low-threshold reference edges
    (``edges.edge_angles``, added lines; None when ``ref_factor`` is 0);
    ``layout`` the valid pixels grouped by region (``layout.Layout``);
    ``lab`` the reference Lab of those pixels (float32 3 x N, layout order);
    ``edge_index`` the reference edge pixels per object
    (``edges.EdgeIndex``); ``albedo`` the wall/ceiling albedo modes;
    ``valid_pixels`` per region; ``cache`` values derived from the model
    outputs on the reference (depth samples and range, DINOv2 norms, patch
    selections), filled on first use.
    """
    view: Any
    rgb: Any
    sha256: str = ""
    gate_key: str = ""
    regions: Any = None
    edges: Any = None
    lab_means: dict = field(default_factory=dict)
    model_outputs: dict = field(default_factory=dict)
    valid: Any = None
    geometry: Any = None
    match_dist: Any = None
    ref_angle: Any = None
    layout: Any = None
    lab: Any = None
    edge_index: Any = None
    albedo: dict = field(default_factory=dict)
    valid_pixels: dict = field(default_factory=dict)
    cache: dict = field(default_factory=dict)
    scene_manifest_path: Optional[str] = None
    warnings: list = field(default_factory=list)

    @property
    def size(self) -> tuple[int, int]:
        """(W, H) of the reference image."""
        h, w = np.asarray(self.rgb).shape[:2]
        return int(w), int(h)


def find_scene_manifest(view) -> Optional[Path]:
    """The scene manifest of a view: next to the render manifest's ``scene``, else ``../scene`` or ``../../scene``.

    The same search as ``wenart.views.load_views`` (renders/ and
    controls/hide_<id>/ layouts).
    """
    render_dir = Path(view.png).parent
    candidates = []
    manifest_path = render_dir / "render_manifest.json"
    if manifest_path.is_file():
        try:
            scene = json.loads(manifest_path.read_text(encoding="utf-8")).get("scene")
        except (OSError, ValueError):
            scene = None
        if scene:
            p = Path(scene)
            candidates.append((p if p.is_absolute() else render_dir / p).parent / "scene_manifest.json")
    candidates.append(render_dir.parent / "scene" / "scene_manifest.json")
    candidates.append(render_dir.parent.parent / "scene" / "scene_manifest.json")
    for cand in candidates:
        if cand.is_file():
            return cand
    return None


class Gate:
    """Geometry change gate for one device; see the module docstring for the contract."""

    def __init__(self, thresholds: Optional[dict | str | Path] = None, models: Any = None,
                 device: str = "cuda") -> None:
        if thresholds is None or isinstance(thresholds, (str, Path)):
            thresholds = load_thresholds(thresholds)
        self.thresholds = thresholds
        self.models = models
        self.device = device
        # A caller that already loaded the scene manifest may set it here; else
        # it is found next to the view's render folder.
        self.scene_manifest: Optional[dict] = None
        self._scenes: dict[str, dict] = {}
        self._refs: "OrderedDict[tuple, Reference]" = OrderedDict()
        self._settled = False
        self.last_artifacts: Optional[dict] = None

    # ------------------------------------------------------------- helpers

    def _models(self):
        """The model wrapper (a ``models.Models`` created on first use when none was given)."""
        if self.models is None:
            from wenart.gate.models import Models
            self.models = Models(device=self.device)
        return self.models

    def release_gpu(self) -> bool:
        """Move the gate's models off the GPU for the rest of the run (``Models.release_gpu``).

        The polish runner calls it from the Z-Image backend's release hook after a CUDA OOM, before
        the single retry (§3.1). A no-op (False) when no model wrapper exists yet (none is created),
        the wrapper has no ``release_gpu`` (test fakes) or nothing is on a CUDA device.
        """
        release = getattr(self.models, "release_gpu", None)
        return bool(release()) if callable(release) else False

    def model_info(self) -> dict:
        """``{"depth"|"sam"|"dino": {"repo", "revision", "licence"}}`` of the models in use (models.yaml otherwise)."""
        info = getattr(self.models, "info", None)
        if callable(info):
            return info()
        cfg = load_models_config()["models"]
        return {k: {"repo": v["repo"], "revision": v["revision"], "licence": v.get("licence")}
                for k, v in cfg.items()}

    def _th(self, check: str) -> dict:
        return self.thresholds.get(check) or {}

    def _ref_factor(self) -> float:
        """``added_lines.ref_factor``: Canny thresholds x this for the oriented reference edges (0/None = off)."""
        from wenart.gate import lines
        value = self._th("added_lines").get("ref_factor", lines.REF_FACTOR)
        return float(value or 0.0)

    def _added_lines(self, ref: "Reference", test_canny) -> tuple[dict, list]:
        """The added-lines metrics and segments of one test Canny map against ``ref``."""
        from wenart.gate import lines
        lth = self._th("added_lines")
        return lines.added_lines(
            test_canny, ref.match_dist, ref.regions.masks, ref.regions.structure_ids(), ref.size[0],
            float(lth.get("min_len_frac", 0.04)), float(lth.get("unmatched_frac", 0.7)), exclude=~ref.valid,
            match_px=float(lth.get("match_px", lines.MATCH_PX)), ref_angle=ref.ref_angle,
            angle_tol_deg=float(lth.get("ref_angle_deg", lines.ANGLE_TOL_DEG)))

    def _scene_for(self, view) -> tuple[Optional[dict], Optional[str]]:
        if self.scene_manifest is not None:
            return self.scene_manifest, "given"
        path = find_scene_manifest(view)
        if path is None:
            return None, None
        key = str(path.resolve())
        if key not in self._scenes:
            self._scenes[key] = json.loads(path.read_text(encoding="utf-8"))
        return self._scenes[key], key

    # ------------------------------------------------------------- prepare

    def prepare(self, view, ref_rgb) -> Reference:
        """Regions, reference edges, Lab means of the reference image (cached per view and image)."""
        from wenart import views as V
        from wenart.gate import colour, edges
        from wenart.gate.layout import Layout

        rgb = np.asarray(ref_rgb)
        if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] < 3:
            raise ValueError(f"reference must be a uint8 H x W x 3 image, got {rgb.dtype} {rgb.shape}")
        rgb = np.ascontiguousarray(rgb[:, :, :3])
        width, height = (int(v) for v in view.size)
        if rgb.shape[:2] != (height, width):
            raise ValueError(f"{view.camera}: reference is {rgb.shape[1]}x{rgb.shape[0]}, view is {width}x{height}")
        sha = image_sha256(rgb)
        key = (view.camera, view.render_key, str(view.png), sha)
        if key in self._refs:
            self._refs.move_to_end(key)
            return self._refs[key]

        warnings: list[str] = []
        index = view.read_index()
        depth_mm = view.read_depth_mm()
        normal = view.read_normal()
        scene, scene_path = self._scene_for(view)
        if scene is None:
            warnings.append("scene manifest not found: objects are index:<v> regions, neutral check skipped")
        table = V.index_table(scene) if scene else {}
        regs = V.regions(index, depth_mm, normal, table)
        valid = ~regs.background & ~regs.panes

        eth = self._th("edges")
        canny_cfg = eth.get("canny") or {}
        sigma, low, high = (canny_cfg.get("sigma", 1.5), canny_cfg.get("low", 25), canny_cfg.get("high", 75))
        geometry = V.geometry_edges(index, depth_mm, normal)
        gray = edges.blurred_gray(rgb, sigma)
        ref_canny = edges.canny_blurred(gray, low, high)
        ref_dist = edges.distance_to(ref_canny)
        ref_edges = edges.reference_edges(geometry, ref_dist, float(eth.get("radius_px", 3)), valid)
        match_dist = edges.distance_to(ref_canny | geometry)
        ref_factor = self._ref_factor()
        ref_angle = edges.edge_angles(gray, low * ref_factor, high * ref_factor) if ref_factor > 0 else None

        # Valid pixels grouped by region: every comparison gathers its test pixels once in this order.
        ids = list(regs.masks)
        lay = Layout.build(regs.masks, ids, valid)
        lab = colour.lab_planes(lay.planes(rgb))
        lab_means = colour.layout_means(lab, lay)
        valid_pixels = {rid: int(n) for rid, n in zip(ids, lay.counts())}
        edge_idx = edges.edge_index(ref_edges, regs, regs.object_ids())
        albedo = colour.structure_albedo(scene, view.room_id, exterior=colour.is_exterior(scene, view.camera,
                                                                                         view.room_id)) if scene else {}

        ref = Reference(view=view, rgb=rgb, sha256=sha,
                        gate_key=make_gate_key(sha, self.model_info(), self.thresholds),
                        regions=regs, edges=ref_edges, lab_means=lab_means, model_outputs={}, valid=valid,
                        geometry=geometry, match_dist=match_dist, ref_angle=ref_angle, layout=lay, lab=lab,
                        edge_index=edge_idx, albedo=albedo, valid_pixels=valid_pixels,
                        scene_manifest_path=scene_path, warnings=warnings)
        self._refs[key] = ref
        while len(self._refs) > REFERENCE_CACHE:
            self._refs.popitem(last=False)
        return ref

    def _ref_output(self, ref: Reference, name: str):
        """A model output on the reference, computed on first use and cached in ``ref.model_outputs``."""
        if name in ref.model_outputs:
            return ref.model_outputs[name]
        from wenart.gate import masks as M
        models = self._models()
        if name == "depth":
            value = np.asarray(models.depth(ref.rgb), dtype=np.float32)
        elif name == "dino":
            value = np.asarray(models.dino_tokens(ref.rgb), dtype=np.float32)
        elif name == "sam":
            w, h = ref.size
            th = self._th("masks")
            boxes, skipped = M.sam_objects(ref.regions.masks, ref.regions.object_ids(), w * h,
                                           float(th.get("region_min_frac", 0.0)))
            ids = list(boxes)
            stack = np.asarray(models.sam_masks(ref.rgb, [boxes[i] for i in ids]), dtype=bool)
            sam = {rid: stack[k] for k, rid in enumerate(ids)}
            value = {"boxes": boxes, "skipped": skipped, "masks": sam,
                     "reliability": M.reliability(sam, ref.regions.masks)}
        else:
            raise KeyError(name)
        ref.model_outputs[name] = value
        return value

    def _ref_depth(self, ref: Reference) -> tuple[np.ndarray, float]:
        """``(float64 reference disparity in layout order, its p98 - p2 range)``, cached on the reference."""
        from wenart.gate import depth
        cached = ref.cache.get("depth")
        disp = self._ref_output(ref, "depth")
        if cached is None or cached[0] is not disp:
            _check_map(disp, ref, "reference depth")
            y = ref.layout.gather(disp).astype(np.float64)
            fin = np.isfinite(y)
            rng = depth.reference_range(y[fin]) if fin.any() else None
            cached = (disp, y, rng)
            ref.cache["depth"] = cached
        return cached[1], cached[2]

    def _ref_dino(self, ref: Reference) -> tuple[np.ndarray, np.ndarray]:
        """``(float64 reference tokens, their norms)``, cached on the reference."""
        cached = ref.cache.get("dino")
        tok = self._ref_output(ref, "dino")
        if cached is None or cached[0] is not tok:
            a = np.asarray(tok, dtype=np.float64)
            cached = (tok, a, np.linalg.norm(a, axis=-1))
            ref.cache["dino"] = cached
        return cached[1], cached[2]

    # ------------------------------------------------------------- compare

    def compare(self, ref: Reference, test_rgb) -> dict:
        """``{"decision", "reasons", "notes", "metrics", "gate_key"}`` for ``test_rgb`` against ``ref``."""
        from wenart.gate import colour, depth, edges, features
        from wenart.gate import masks as M

        test = np.asarray(test_rgb)
        width, height = ref.size
        if test.ndim != 3 or test.shape[2] < 3 or test.shape[:2] != (height, width):
            raise ValueError(f"test image is {test.shape}, the view is {width}x{height} (W x H) RGB")
        if test.dtype != np.uint8:
            raise ValueError(f"test image must be uint8, got {test.dtype}")
        test = np.ascontiguousarray(test[:, :, :3])
        regs = ref.regions
        lay = ref.layout
        total = width * height
        all_ids = list(regs.masks)
        seconds: dict[str, float] = {}
        metrics: dict[str, Any] = {}
        artifacts: dict[str, Any] = {"missed": None, "lines": [], "depth_err": None}

        # Lost edges (one blur for both Canny maps; the reference edges per object are indexed once).
        t0 = time.time()
        eth = self._th("edges")
        canny_cfg = eth.get("canny") or {}
        sigma, low, high = canny_cfg.get("sigma", 1.5), canny_cfg.get("low", 25), canny_cfg.get("high", 75)
        factor = float(eth.get("test_factor", edges.TEST_FACTOR))
        gray = edges.blurred_gray(test, sigma)
        test_canny = edges.canny_blurred(gray, low, high)
        test_dist = edges.distance_to(edges.canny_blurred(gray, low * factor, high * factor))
        metrics["edges"], artifacts["missed"] = edges.edge_metrics_indexed(
            ref.edge_index, test_dist, float(eth.get("radius_px", 3)), int(eth.get("region_min_ref_px", 0)))
        seconds["edges"] = round(time.time() - t0, 3)

        # Added straight lines on structure.
        t0 = time.time()
        metrics["added_lines"], artifacts["lines"] = self._added_lines(ref, test_canny)
        seconds["added_lines"] = round(time.time() - t0, 3)

        # Colour and neutral walls.
        t0 = time.time()
        cth = self._th("colour")
        test_lab = colour.lab_planes(lay.planes(test))
        metrics["colour"], test_means = colour.colour_metrics_layout(
            ref.lab, test_lab, ref.lab_means, lay, float(cth.get("region_min_frac", 0.0)))
        del test_lab
        nth = self._th("neutral")
        metrics["neutral"] = colour.neutral_metrics(
            ref.lab_means, test_means, ref.valid_pixels, total, ref.albedo,
            float(nth.get("region_min_frac", cth.get("region_min_frac", 0.0))))
        seconds["colour"] = round(time.time() - t0, 3)

        # Model checks: a failure is recorded and fails the check (never a silent pass).
        t0 = time.time()
        try:
            dth = self._th("depth")
            ref_y, ref_range = self._ref_depth(ref)
            test_disp = np.asarray(self._models().depth(test), dtype=np.float32)
            _check_map(test_disp, ref, "test depth")
            metrics["depth"], err = depth.depth_metrics_layout(
                ref_y, lay.gather(test_disp), lay, float(dth.get("region_min_frac", 0.0)), ref_range=ref_range)
            artifacts["depth_err"] = lay.scatter(err)
        except Exception as exc:  # noqa: BLE001 - recorded, the check then fails
            metrics["depth"] = _error_metric(exc)
        seconds["depth"] = round(time.time() - t0, 3)

        t0 = time.time()
        try:
            mth = self._th("masks")
            sam = self._ref_output(ref, "sam")
            ids = list(sam["boxes"])
            stack = np.asarray(self._models().sam_masks(test, [sam["boxes"][i] for i in ids]), dtype=bool)
            test_sam = {rid: stack[k] for k, rid in enumerate(ids)}
            metrics["masks"] = M.mask_metrics(sam["masks"], test_sam, sam["reliability"], sam["skipped"],
                                              float(mth.get("sam_reliable_min", 0.0)))
        except Exception as exc:  # noqa: BLE001
            metrics["masks"] = _error_metric(exc)
        seconds["masks"] = round(time.time() - t0, 3)

        t0 = time.time()
        try:
            fth = self._th("features")
            ref_tok, ref_norm = self._ref_dino(ref)
            test_tok = np.asarray(self._models().dino_tokens(test), dtype=np.float32)
            metrics["features"], _cos = features.feature_metrics(
                ref_tok, test_tok, regs.masks, regs.object_ids(), total, float(fth.get("region_min_frac", 0.0)),
                cache=ref.cache.setdefault("patches", {}), ref_norm=ref_norm)
        except Exception as exc:  # noqa: BLE001
            metrics["features"] = _error_metric(exc)
        seconds["features"] = round(time.time() - t0, 3)

        # Memory policy (§1.3): decided once, after the first comparison whose model checks all ran.
        if not self._settled and not any(metrics[c].get("error") for c in ("depth", "masks", "features")):
            settle = getattr(self.models, "settle", None)
            if callable(settle):
                settle()
            self._settled = True

        metrics["regions"] = {rid: {"kind": regs.kinds[rid], "pixels": int(regs.pixels[rid])} for rid in all_ids}
        metrics["seconds"] = seconds
        metrics["size"] = [width, height]
        decision, reasons, notes = decide(metrics, self.thresholds)
        self.last_artifacts = dict(artifacts, test_sha256=image_sha256(test), gate_key=ref.gate_key)
        return {"decision": decision, "reasons": reasons, "notes": notes, "metrics": metrics,
                "gate_key": ref.gate_key}

    # ------------------------------------------------------------- debug

    def write_debug(self, ref: Reference, test_rgb, result: dict, path) -> Path:
        """Write the §4.4 debug JPEG (<= 300 KB) for a comparison; returns the path.

        Uses the maps of the last ``compare`` when they belong to this test
        image, else recomputes the edge and line maps (the depth panel then
        stays empty).
        """
        from wenart.gate import debug, edges

        test = np.ascontiguousarray(np.asarray(test_rgb)[:, :, :3])
        art = self.last_artifacts
        if not art or art.get("gate_key") != ref.gate_key or art.get("test_sha256") != image_sha256(test):
            eth = self._th("edges")
            canny_cfg = eth.get("canny") or {}
            sigma, low, high = canny_cfg.get("sigma", 1.5), canny_cfg.get("low", 25), canny_cfg.get("high", 75)
            factor = float(eth.get("test_factor", edges.TEST_FACTOR))
            test_canny = edges.canny(test, sigma, low, high)
            dist = edges.distance_to(edges.canny(test, sigma, low * factor, high * factor))
            _m, found = self._added_lines(ref, test_canny)
            art = {"missed": ref.edges & (dist > float(eth.get("radius_px", 3))), "lines": found, "depth_err": None}
        return debug.write_debug_image(path, ref.rgb, test, art.get("missed"), art.get("lines") or [],
                                       art.get("depth_err"), ref.regions, result,
                                       depth_scale=float(self._th("depth").get("region_max", 0.05)) * 2.0)


def _check_map(arr, ref: Reference, what: str) -> None:
    """ValueError unless a model output map has the view size (H x W)."""
    w, h = ref.size
    if np.asarray(arr).shape != (h, w):
        raise ValueError(f"{what} is {np.asarray(arr).shape}, the view is {h} x {w}")


def _error_metric(exc: Exception) -> dict:
    return {"global": None, "regions": {}, "skipped": {}, "error": f"{type(exc).__name__}: {exc}"}


def decide(metrics: dict, thresholds: dict) -> tuple[str, list, list]:
    """``("accept"|"reject", reasons, notes)`` from stored metrics and thresholds (pure).

    ``reasons`` are the failed hard checks, ``notes`` the failed soft ones,
    each ``{check, region: "global"|<id>, value, threshold, op: ">="|"<="}``;
    accept iff every hard check passes (§4.2). ``*_min``: value >= threshold
    passes, ``*_max``: value <= threshold passes (equal passes). A check with
    limits in ``thresholds`` but no metrics (or an ``error``) fails with
    ``value: None`` and an ``error`` text. A None value (nothing to measure,
    e.g. no reference edge in the view) passes.
    """
    reasons: list = []
    notes: list = []
    for check, th in thresholds.items():
        if check in NOT_THRESHOLDS or not isinstance(th, dict):
            continue
        lims = limits_of(check, th)
        if not lims:
            continue
        target = reasons if th.get("hard", True) else notes
        m = metrics.get(check)
        if not isinstance(m, dict) or m.get("error"):
            scope, key, op = lims[0]
            error = (m or {}).get("error") if isinstance(m, dict) else None
            target.append({"check": check, "region": "global", "value": None, "threshold": th[key], "op": op,
                           "error": error or "not computed"})
            continue
        for scope, key, op in lims:
            limit = float(th[key])
            items = [("global", m.get("global"))] if scope == "global" else list((m.get("regions") or {}).items())
            for region, value in items:
                if value is None:
                    continue
                ok = float(value) >= limit if op == ">=" else float(value) <= limit
                if not ok:
                    target.append({"check": check, "region": region, "value": value, "threshold": th[key], "op": op})
    return ("accept" if not reasons else "reject"), reasons, notes
