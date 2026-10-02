"""Polish runner: the attempt ladder, sweep and smoke over the views of one project (docs/milestone5.md §3.6).

What it does for ``kind="run"`` (the milestone result):

1. Loads the project through ``wenart.views.project_paths`` (scene manifest,
   building, rendered style profile, brief) and the M5 views of
   ``renders/`` (stale pre-M5 entries are skipped with a warning).
2. Brief ``polish: false`` -> every view ``final: cycles``, reason
   ``brief``; no model is loaded.
3. Per view: the prompt (``wenart.polish.prompt`` with the own-room furniture
   of ``wenart.vision_check.expected.expected_view``), the control images
   (``<cam>_control_<type>.png``), the gate reference
   (``Gate.prepare(view, cycles_rgb)``).
4. The ladder (``polish.yaml: ladder``) in order: polish (``generate``),
   back to the render size, Cycles window panes pasted back, written as
   ``<cam>_a<k>.png``, gated at once (``Gate.compare``); the first accepted
   attempt is the view's candidate; none -> ``final: cycles``, reason
   ``gate`` (``error`` when an attempt failed). Seed of attempt k =
   ``polish.yaml: seed + k``. The manifest is rewritten after every attempt.
5. Room rule: the candidates of one room must have wall Lab means within
   ΔE76 5 (``wenart.polish.rooms``); otherwise every candidate takes the
   strongest rung all of them accept and whose wall means agree (missing
   rungs are run now), or the Cycles render (reason ``room``).
6. Previews of the final attempts, ``determinism.json`` (the
   ``determinism_view`` polished twice with the same seed), the report.

``sweep`` runs every attempt of a grid on every view, each gated, no early
stop, into ``polish/sweep/`` (``--views auto`` = ``expected.sweep_views(...,
n=4)``); ``smoke`` runs the 4 smoke settings on a few views into
``polish/smoke/`` (timings for run 0).

Resumability: every attempt has an ``attempt_key`` = sha256 over its
settings, seed, steps, sigmas, prompt, control PNG sha256, source PNG
sha256, the model repos/revisions/files (+ the vendored ControlNet config),
``POLISH_CODE_VERSION`` and the torch/diffusers versions. An attempt of the
previous manifest with the same key and an unchanged PNG is reused; its
gate metrics are reused when their ``gate_key`` equals the reference's
current one (else the PNG is gated again), and the decision is always
recomputed from the metrics with the current thresholds (``decide``); the
ladder outcome follows from those decisions. ``--force`` ignores the
previous manifest.

Deadline (``--deadline`` / ``WENART_DEADLINE``, epoch seconds): after it no
new polish, gate reference or gate comparison starts; reuse of stored
results still happens. The manifest gets ``"incomplete": true`` and the
views that could not finish get ``final: cycles``, reason ``deadline``.

Everything the runner needs from other areas comes through ``Deps`` (the
contracts of §1.3/§1.4 plus the backend interface of
``wenart.polish.zimage``), so the CPU tests run it end to end with fakes.
"""
from __future__ import annotations

import copy
import hashlib
import importlib
import json
import os
import re
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np

from wenart import views as V
from wenart.polish import config as PC
from wenart.polish import controls as CT
from wenart.polish import prompt as PR
from wenart.polish import rooms as RM
from wenart.polish import schedule as S
from wenart.polish import sizing as SZ
from wenart.polish.panes import restore_panes

SCHEMA_VERSION = "0.1"
MANIFEST_NAME = "polish_manifest.json"
REPORT_NAME = "polish_report.md"
DETERMINISM_NAME = "determinism.json"
PREVIEW_MAX_BYTES = 300_000
SWEEP_PREVIEW_WIDTH = 960
AUTO_VIEWS = {"sweep": 4, "smoke": 2}
OUT_SUBDIR = {"run": "polish", "sweep": "polish/sweep", "smoke": "polish/smoke"}
FALLBACK_IGNORE_AREA_FRAC = 0.002


class PolishError(Exception):
    """A problem with the inputs (views, grid, project) that stops the run before any GPU work."""


# --------------------------------------------------------------------------
# Dependencies (fakeable)
# --------------------------------------------------------------------------

def find_gate_debug_writer() -> Optional[Callable]:
    """The gate's debug-image writer (§4.4) when area C provides one, else None.

    Called as ``writer(ref=Reference, test_rgb=uint8 H x W x 3, result=compare() dict,
    path=Path)``; looked up as ``wenart.gate.write_debug_image`` or
    ``wenart.gate.debug.write_debug_image``.
    """
    for module, attr in (("wenart.gate", "write_debug_image"), ("wenart.gate.debug", "write_debug_image")):
        try:
            mod = importlib.import_module(module)
        except ImportError:
            continue
        fn = getattr(mod, attr, None)
        if callable(fn):
            return fn
    return None


def _default_backend(cfg: dict, device: str):
    from wenart.polish.zimage import ZImageBackend
    return ZImageBackend(cfg, device=device)


def _default_gate(device: str):
    from wenart.gate import Gate
    return Gate(device=device)


@dataclass
class Deps:
    """What the runner takes from outside; None fields get the real implementations.

    ``backend_factory(cfg, device)`` -> polish backend (interface in
    ``wenart.polish.zimage``); ``gate_factory(device)`` -> object with
    ``thresholds``, ``prepare(view, ref_rgb)`` and ``compare(ref, test_rgb)``
    (§1.3); ``decide(metrics, thresholds)`` (§1.3); ``debug_writer`` (see
    ``find_gate_debug_writer``; None = no gate debug images); ``expected``:
    an object with ``expected_view``, ``expected_views`` and ``sweep_views``
    (§1.4); ``gate_models()`` -> the gate's ``models.yaml`` dict; ``clock``
    (epoch seconds, for the deadline); ``log``.
    """
    backend_factory: Optional[Callable] = None
    gate_factory: Optional[Callable] = None
    decide: Optional[Callable] = None
    debug_writer: Optional[Callable] = None
    expected: Any = None
    gate_models: Optional[Callable] = None
    clock: Callable[[], float] = time.time
    log: Callable[[str], None] = print
    find_debug_writer: bool = True

    def resolved(self) -> "Deps":
        d = copy.copy(self)
        if d.backend_factory is None:
            d.backend_factory = _default_backend
        if d.gate_factory is None:
            d.gate_factory = _default_gate
        if d.decide is None:
            from wenart.gate.api import decide
            d.decide = decide
        if d.debug_writer is None and d.find_debug_writer:
            d.debug_writer = find_gate_debug_writer()
        if d.expected is None:
            from wenart.vision_check import expected
            d.expected = expected
        if d.gate_models is None:
            from wenart.gate.api import load_models_config
            d.gate_models = load_models_config
        return d


# --------------------------------------------------------------------------
# Pure helpers
# --------------------------------------------------------------------------

def sha256_file(path) -> str:
    return CT.sha256_file(path)


def attempt_key(attempt: dict, *, seed: int, steps: int, sigmas: list, prompt: str, control_sha256: Optional[str],
                source_sha256: str, models: dict, versions: dict) -> str:
    """sha256 over everything that decides an attempt's pixels (§3.6)."""
    payload = {
        "strength": attempt["strength"], "control": attempt["control"], "scale": attempt["scale"],
        "size": attempt["size"], "mode": attempt["mode"], "seed": int(seed), "steps": int(steps),
        "sigmas": [round(float(s), 6) for s in sigmas], "prompt": prompt, "control_sha256": control_sha256,
        "source_sha256": source_sha256,
        "models": {k: {kk: models[k].get(kk) for kk in ("repo", "revision", "files", "config_sha256")}
                   for k in ("base", "controlnet")},
        "code": PC.POLISH_CODE_VERSION, "torch": versions.get("torch"), "diffusers": versions.get("diffusers"),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()


def accepted(rec: Optional[dict]) -> bool:
    """True when an attempt record has no error and its gate decision is accept."""
    return bool(rec) and not rec.get("error") and bool(rec.get("gate")) and rec["gate"].get("decision") == "accept"


def ladder_outcome(attempts: list[dict], complete: bool) -> tuple[str, Optional[int], Optional[str]]:
    """``(final, final_attempt, reason)`` of one view's ladder (attempt records in ladder order).

    The first accepted attempt wins. Otherwise ``cycles`` with reason
    ``error`` when an attempt failed, ``deadline`` when the ladder was cut
    short, else ``gate``.
    """
    for rec in attempts:
        if accepted(rec):
            return "polished", int(rec["k"]), None
    if any(rec.get("error") for rec in attempts):
        return "cycles", None, "error"
    if not complete:
        return "cycles", None, "deadline"
    return "cycles", None, "gate"


def relpath(path, start) -> str:
    """POSIX path of ``path`` relative to the folder ``start`` (§1.1)."""
    return Path(os.path.relpath(Path(path).resolve(), Path(start).resolve())).as_posix()


def _json_default(value):
    """numpy scalars/arrays and paths (e.g. inside gate metrics) as plain JSON values."""
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, Path):
        return value.as_posix()
    raise TypeError(f"{type(value).__name__} is not JSON serialisable")


def write_json(path: Path, data: dict) -> Path:
    """JSON (indent 1, UTF-8) written through a temporary file, so a reader never sees half a file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, ensure_ascii=False, default=_json_default), encoding="utf-8")
    os.replace(tmp, path)
    return path


def write_preview(rgb, path, max_bytes: int = PREVIEW_MAX_BYTES, width: Optional[int] = None) -> Path:
    """JPEG preview <= ``max_bytes``: quality steps down, then the size halves until it fits."""
    from PIL import Image
    img = Image.fromarray(np.ascontiguousarray(np.asarray(rgb, dtype=np.uint8)))
    if width and img.width > width:
        img = img.resize((int(width), max(1, round(img.height * width / img.width))), Image.LANCZOS)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    while True:
        for quality in (90, 85, 75, 65, 55, 45):
            img.save(path, "JPEG", quality=quality, optimize=True)
            if path.stat().st_size <= max_bytes:
                return path
        if img.width <= 64:
            return path
        img = img.resize((img.width // 2, max(1, img.height // 2)), Image.LANCZOS)


def fallback_furniture(view: V.View, table: dict, ignore_frac: float = FALLBACK_IGNORE_AREA_FRAC) -> list[str]:
    """Own-room furniture types of a view from the index pass alone (when ``expected_view`` is unavailable)."""
    total = float(view.width * view.height) or 1.0
    rows = []
    for value, stat in view.index_stats.items():
        e = table.get(int(value))
        if not e or e["kind"] != "furniture" or e.get("room_id") != view.room_id:
            continue
        if stat["pixels"] / total < ignore_frac or e.get("type") in (None, "unknown"):
            continue
        if e.get("status") == "unverified":
            continue
        rows.append((stat["pixels"], e["type"]))
    types: list[str] = []
    for _, t in sorted(rows, key=lambda r: -r[0]):
        if t not in types:
            types.append(t)
    return types[:PR.MAX_FURNITURE]


def _room_types(building: dict) -> dict:
    return {r.get("id"): r.get("room_type") for r in (building or {}).get("rooms") or []}


# --------------------------------------------------------------------------
# Per-view state
# --------------------------------------------------------------------------

@dataclass
class ViewJob:
    """One view of the run: inputs (loaded on demand), prompt, controls, gate reference and attempt records."""
    view: V.View
    prompt: str = ""
    prompt_info: dict = field(default_factory=dict)
    expected_source: str = ""
    source_sha256: str = ""
    controls: dict = field(default_factory=dict)          # type -> {"file", "sha256"}
    attempts: list = field(default_factory=list)
    by_k: dict = field(default_factory=dict)               # k -> record (incl. room-rule rungs)
    ref: Any = None
    ref_error: Optional[str] = None
    complete: bool = True
    final: Optional[str] = None
    final_attempt: Optional[int] = None
    reason: Optional[str] = None
    notes: list = field(default_factory=list)
    _arrays: Optional[dict] = None

    def arrays(self) -> dict:
        """rgb, index, depth_mm, normal of the view (read once, dropped by ``release``)."""
        if self._arrays is None:
            self._arrays = {"rgb": self.view.read_rgb(), "index": self.view.read_index(),
                            "depth_mm": self.view.read_depth_mm(), "normal": self.view.read_normal()}
        return self._arrays

    def release(self) -> None:
        """Drop the image arrays (they are read again when the room rule or the determinism check needs them)."""
        self._arrays = None
        for c in self.controls.values():
            c["array"] = None


# --------------------------------------------------------------------------
# The run
# --------------------------------------------------------------------------

class PolishRun:
    """One ``run`` / ``sweep`` / ``smoke`` over the views of a project (see the module docstring)."""

    def __init__(self, project_out, kind: str = "run", *, views=None, out_dir=None, force: bool = False,
                 deadline: Optional[float] = None, grid_name: Optional[str] = None, cfg: Optional[dict] = None,
                 device: str = "cuda", deps: Optional[Deps] = None, previews: Optional[str] = None) -> None:
        if kind not in OUT_SUBDIR:
            raise PolishError(f"unknown kind {kind!r}")
        if previews not in (None, "final", "all", "none"):
            raise PolishError(f"previews must be final, all or none, got {previews!r}")
        self.previews = previews or ("final" if kind == "run" else "all")
        self.kind = kind
        self.project_out = Path(project_out).resolve()
        self.out_dir = Path(out_dir).resolve() if out_dir else self.project_out / OUT_SUBDIR[kind]
        self.force = force
        self.deadline = deadline
        self.device = device
        self.deps = (deps or Deps()).resolved()
        self.log = self.deps.log
        self.cfg = cfg if cfg is not None else PC.load_config()
        self.steps = int(self.cfg.get("steps") or 8)
        self.seed = int(self.cfg.get("seed") or 0)
        try:
            if kind == "run":
                self.attempts = PC.ladder(self.cfg)
            else:
                self.attempts = PC.grid(self.cfg, grid_name or kind)
        except (ValueError, KeyError) as exc:
            raise PolishError(f"attempt list: {exc}") from exc
        self.views_arg = views
        self.warnings: list[str] = []
        self.jobs: list[ViewJob] = []
        self.rooms: dict = {}
        self.incomplete = False
        self.backend = None
        self.versions: dict = {"torch": None, "diffusers": None, "device": None}
        self.gate = None
        self._ready = False
        self._reuse: dict = {}
        self._wall_masks: dict = {}
        self._debug_warned = False
        self.models = PC.models_record(self.cfg, self._gate_models())
        self.started = time.time()

    # -- setup -------------------------------------------------------------

    def _gate_models(self) -> dict:
        try:
            return self.deps.gate_models() or {}
        except (OSError, ValueError) as exc:
            self.warnings.append(f"gate models.yaml not readable: {exc}")
            return {}

    def _warn(self, text: str) -> None:
        if text not in self.warnings:
            self.warnings.append(text)
            self.log(f"WARNING {text}")

    def past_deadline(self) -> bool:
        return self.deadline is not None and self.deps.clock() >= self.deadline

    def _load_project(self) -> None:
        try:
            paths = V.project_paths(self.project_out)
        except FileNotFoundError as exc:
            raise PolishError(f"no scene manifest under {self.project_out}: {exc}") from exc
        self.paths = paths
        self.project = paths["project"]
        for w in paths["warnings"]:
            self._warn(w)
        self.scene = paths["scene_manifest"]
        self.style_profile = paths["style_profile"] or {}
        if not paths["style_profile"]:
            self._warn("scene manifest has no style_profile; prompt words fall back to 'room'")
        self.table = V.index_table(self.scene)
        bpath = paths["building_path"]
        if bpath and Path(bpath).is_file():
            self.building = json.loads(Path(bpath).read_text(encoding="utf-8"))
        else:
            self.building = {}
            self._warn(f"building not found ({bpath}); room types and the expected elements are limited")
        brief = paths["brief"]
        if brief is None:
            self.polish_allowed = True
            self._warn("brief not loaded; polish allowed by the default (brief polish: true)")
        else:
            self.polish_allowed = bool((brief.get("values") or {}).get("polish", True))

    def _camera_names(self) -> Optional[list]:
        arg = self.views_arg
        if isinstance(arg, str):
            arg = arg.strip()
        if self.kind == "run":
            return None if arg in (None, "", "all") else arg
        if arg in (None, "", "auto"):
            n = AUTO_VIEWS[self.kind]
            try:
                exp = self.deps.expected.expected_views(self.project_out)
                return list(self.deps.expected.sweep_views(exp, n))
            except Exception as exc:  # noqa: BLE001 - area D may not be merged yet
                raise PolishError(f"--views auto needs wenart.vision_check.expected ({type(exc).__name__}: {exc}); "
                                  f"pass camera names instead") from exc
        return None if arg == "all" else arg

    def _load_views(self) -> None:
        render_dir = self.paths["render_dir"]
        if not (render_dir / "render_manifest.json").is_file():
            raise PolishError(f"no render manifest in {render_dir}")
        stale: list[str] = []
        try:
            views = V.load_views(render_dir, self._camera_names(), skip_stale=True, warnings=stale)
        except KeyError as exc:
            raise PolishError(str(exc)) from exc
        for w in stale:
            self._warn(w)
        if not views:
            raise PolishError(f"no usable (M5) views in {render_dir}")
        self.jobs = [ViewJob(view=v) for v in views.values()]

    def _expected(self, view: V.View) -> Optional[dict]:
        try:
            return self.deps.expected.expected_view(view, self.scene, self.building)
        except Exception as exc:  # noqa: BLE001 - area D may not be merged yet; never fatal for a prompt
            self._warn(f"expected_view unavailable ({type(exc).__name__}: {exc}); "
                       f"prompt furniture taken from the index pass")
            return None

    def _prepare_job(self, job: ViewJob) -> None:
        view = job.view
        job.source_sha256 = sha256_file(view.png)
        exp = self._expected(view)
        if exp is not None:
            furniture = PR.furniture_types(exp)
            room_type = exp.get("room_type") or _room_types(self.building).get(view.room_id)
            job.expected_source = "expected_view"
        else:
            furniture = fallback_furniture(view, self.table)
            room_type = _room_types(self.building).get(view.room_id)
            job.expected_source = "index_pass"
        job.prompt_info = PR.build_prompt(self.style_profile, room_type, furniture)
        job.prompt = job.prompt_info["prompt"]
        for w in job.prompt_info["warnings"]:
            self._warn(f"{view.camera}: {w}")

    def _write_controls(self, job: ViewJob) -> None:
        """Write ``<cam>_control_<type>.png`` for every control type of the attempt list (once per view)."""
        for kind in sorted({a["control"] for a in self.attempts if a["control"]}):
            self._control(job, kind)

    def _control(self, job: ViewJob, kind: str) -> dict:
        """``{"file", "sha256", "array"}`` of one control image (computed and written when missing)."""
        c = job.controls.get(kind)
        if c is None or c.get("array") is None:
            arr = job.arrays()
            img = CT.make_control(kind, arr["rgb"], arr["index"], arr["depth_mm"], arr["normal"])
            path, sha = CT.write_control(img, self.out_dir / CT.control_filename(job.view.camera, kind))
            c = job.controls[kind] = {"file": path.name, "sha256": sha, "array": img}
        return c

    def _load_previous(self) -> None:
        path = self.out_dir / MANIFEST_NAME
        if self.force or not path.is_file():
            return
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            self._warn(f"previous manifest not readable ({exc}); nothing reused")
            return
        for v in old.get("views") or []:
            for rec in v.get("attempts") or []:
                if rec.get("attempt_key") and rec.get("png") and rec.get("sha256") and not rec.get("error"):
                    self._reuse[(v.get("camera"), rec["attempt_key"])] = rec

    # -- backend and gate --------------------------------------------------

    def _ensure_backend(self) -> None:
        if self.backend is None:
            self.backend = self.deps.backend_factory(self.cfg, self.device)
            self.versions = dict(self.backend.versions())

    def _ensure_ready(self) -> None:
        self._ensure_backend()
        if not self._ready:
            prompts = list(dict.fromkeys(j.prompt for j in self.jobs))
            self.log(f"loading the polish models ({len(prompts)} prompts)")
            self.backend.ensure_ready(prompts)
            self._ready = True

    def _ensure_gate(self):
        if self.gate is None:
            self.gate = self.deps.gate_factory(self.device)
        return self.gate

    def _ensure_ref(self, job: ViewJob) -> bool:
        """Gate reference of the view (once); False when it failed or the deadline stops it."""
        if job.ref is not None:
            return True
        if job.ref_error:
            return False
        if self.past_deadline():
            return False
        gate = self._ensure_gate()
        try:
            if self.backend is not None and self._ready:
                self.backend.free_cache()
            job.ref = gate.prepare(job.view, job.arrays()["rgb"])
        except Exception as exc:  # noqa: BLE001 - recorded, the view falls back to Cycles
            job.ref_error = f"gate prepare: {type(exc).__name__}: {exc}"
            self._warn(f"{job.view.camera}: {job.ref_error}")
            return False
        return True

    def _wall_mask(self, job: ViewJob) -> np.ndarray:
        cam = job.view.camera
        if cam not in self._wall_masks:
            a = job.arrays()
            self._wall_masks[cam] = RM.wall_mask(a["index"], a["depth_mm"], a["normal"], self.table)
        return self._wall_masks[cam]

    # -- one attempt -------------------------------------------------------

    def _png_name(self, job: ViewJob, k: int) -> str:
        return f"{job.view.camera}_a{k}.png"

    def _gate(self, job: ViewJob, rec: dict, test_rgb, stored: Optional[dict]) -> Optional[str]:
        """Fill ``rec["gate"]`` (stored metrics re-decided, or a new comparison); returns an error text or None."""
        gate = self._ensure_gate()
        if stored and stored.get("metrics") is not None and stored.get("gate_key") == job.ref.gate_key:
            decision, reasons, notes = self.deps.decide(stored["metrics"], gate.thresholds)
            rec["gate"] = {"decision": decision, "reasons": reasons, "notes": notes,
                           "metrics": stored["metrics"], "gate_key": stored["gate_key"]}
            rec["gate_reused"] = True
            return None
        if self.past_deadline():
            return "deadline"
        if self.backend is not None and self._ready:
            self.backend.free_cache()
        t0 = time.time()
        try:
            result = gate.compare(job.ref, test_rgb)
        except Exception as exc:  # noqa: BLE001 - recorded on the attempt
            rec["gate"] = None
            rec["error"] = f"gate: {type(exc).__name__}: {exc}"
            return rec["error"]
        rec["gate_seconds"] = round(time.time() - t0, 2)
        rec["gate"] = {"decision": result["decision"], "reasons": list(result.get("reasons") or []),
                       "notes": list(result.get("notes") or []), "metrics": result.get("metrics") or {},
                       "gate_key": result.get("gate_key") or job.ref.gate_key}
        rec["gate_reused"] = False
        self._debug_image(job, rec, test_rgb, result)
        return None

    def _debug_image(self, job: ViewJob, rec: dict, test_rgb, result: dict) -> None:
        writer = self.deps.debug_writer
        if writer is None:
            if not self._debug_warned:
                self._warn("gate debug-image writer not available (wenart.gate.write_debug_image); "
                           "no <cam>_a<k>_gate.jpg written")
                self._debug_warned = True
            return
        path = self.out_dir / f"{job.view.camera}_a{rec['k']}_gate.jpg"
        try:
            writer(ref=job.ref, test_rgb=test_rgb, result=result, path=path)
            rec["debug_jpg"] = path.name
        except Exception as exc:  # noqa: BLE001 - a debug image never fails the attempt
            self._warn(f"{job.view.camera} a{rec['k']}: gate debug image failed ({type(exc).__name__}: {exc})")

    def _base_record(self, job: ViewJob, k: int, attempt: dict) -> dict:
        sched = S.schedule(self.steps, attempt["strength"])
        seed = self.seed + k
        control_sha = self._control(job, attempt["control"])["sha256"] if attempt["control"] else None
        key = attempt_key(attempt, seed=seed, steps=self.steps, sigmas=sched["sigmas"], prompt=job.prompt,
                          control_sha256=control_sha, source_sha256=job.source_sha256, models=self.models,
                          versions=self.versions)
        return {"k": k, "role": attempt["role"], "strength": attempt["strength"], "control": attempt["control"],
                "scale": attempt["scale"], "size": attempt["size"], "mode": attempt["mode"], "seed": seed,
                "steps": self.steps, "sigmas": sched["sigmas"], "sigma0_numpy": sched["sigma0"],
                "forwards": sched["forwards"], "seconds": None, "png": None, "sha256": None,
                "attempt_key": key, "panes_restored": None, "wall_lab": None, "gate": None, "debug_jpg": None,
                "reused": False, "error": None}

    def _reuse_record(self, job: ViewJob, k: int, rec: dict) -> Optional[dict]:
        """The stored attempt of this camera with this key when its PNG is unchanged.

        The PNG is copied to this attempt's name when the stored record used another k.
        """
        old = self._reuse.get((job.view.camera, rec["attempt_key"]))
        if not old:
            return None
        src = self.out_dir / old["png"]
        if not src.is_file() or sha256_file(src) != old["sha256"]:
            return None
        name = self._png_name(job, k)
        if old["png"] != name:
            shutil.copyfile(src, self.out_dir / name)
        for key in ("seconds", "sigma0", "pipeline", "panes_restored", "wall_lab", "debug_jpg", "size_plan"):
            if key in old:
                rec[key] = old[key]
        if rec.get("debug_jpg") and not (self.out_dir / rec["debug_jpg"]).is_file():
            rec["debug_jpg"] = None
        rec.update(png=name, sha256=old["sha256"], reused=True)
        return old

    def run_attempt(self, job: ViewJob, k: int, attempt: dict) -> Optional[dict]:
        """Reuse or make attempt ``k`` of ``job`` and gate it; None when the deadline stops it."""
        self._ensure_backend()
        rec = self._base_record(job, k, attempt)
        if not self._ensure_ref(job):
            if job.ref_error:
                rec["error"] = job.ref_error
                return rec
            return None
        old = self._reuse_record(job, k, rec)
        if old is not None:
            test = V.read_rgb(self.out_dir / rec["png"])
            if rec.get("wall_lab") is None:
                rec["wall_lab"] = RM.wall_lab(test, self._wall_mask(job))
            err = self._gate(job, rec, test, old.get("gate"))
            if err == "deadline":
                return None
            return rec
        if self.past_deadline():
            return None
        arr = job.arrays()
        plan = SZ.plan_size(attempt["size"], job.view.size)
        rec["size_plan"] = plan.to_dict()
        try:
            self._ensure_ready()
            image = SZ.to_model(arr["rgb"], plan)
            control = SZ.to_model(self._control(job, attempt["control"])["array"], plan) if attempt["control"] else None
            t0 = time.time()
            out, meta = self.backend.generate(image, control, strength=attempt["strength"], scale=attempt["scale"],
                                              mode=attempt["mode"], seed=rec["seed"], steps=self.steps,
                                              prompt=job.prompt)
            rec["seconds"] = round(time.time() - t0, 2)
            rec["sigma0"] = meta.get("sigma0")
            rec["pipeline"] = meta.get("pipeline")
            if meta.get("forwards") is not None:
                rec["forwards"] = int(meta["forwards"])
            out = SZ.from_model(out, plan)
            out, n = restore_panes(out, arr["rgb"], arr["index"], self.table)
        except Exception as exc:  # noqa: BLE001 - recorded; the ladder moves on
            rec["error"] = f"{type(exc).__name__}: {exc}"
            self._warn(f"{job.view.camera} a{k}: polish failed ({rec['error']})")
            return rec
        rec["panes_restored"] = n
        path = V.write_png_rgb(self.out_dir / self._png_name(job, k), out)
        rec["png"] = path.name
        rec["sha256"] = sha256_file(path)
        rec["wall_lab"] = RM.wall_lab(out, self._wall_mask(job))
        err = self._gate(job, rec, out, None)
        if err == "deadline":
            rec["gate"] = None
            rec["error"] = None
            job.complete = False
            self.incomplete = True
        self.log(f"{job.view.camera} a{k} s{attempt['strength']} {attempt['control']} -> "
                 f"{(rec.get('gate') or {}).get('decision') or rec.get('error') or 'not gated'}")
        return rec

    # -- views -------------------------------------------------------------

    def _process(self, job: ViewJob) -> None:
        for k, attempt in enumerate(self.attempts, 1):
            rec = self.run_attempt(job, k, attempt)
            if rec is None:
                job.complete = False
                self.incomplete = True
                break
            job.attempts.append(rec)
            job.by_k[k] = rec
            self.write_manifest()
            if self.kind == "run" and accepted(rec):
                break
            if rec.get("error") and job.ref_error:
                break
        if self.kind == "run":
            job.final, job.final_attempt, job.reason = ladder_outcome(job.attempts, job.complete)

    def _room_rule(self) -> None:
        """§3.6 room rule over the run's candidates (runs missing rungs when a room disagrees)."""
        by_room: dict = {}
        for job in self.jobs:
            if job.view.room_id:
                by_room.setdefault(job.view.room_id, []).append(job)
        for room, jobs in by_room.items():
            cands = [j for j in jobs if j.final == "polished"]
            labs = {j.view.camera: j.by_k[j.final_attempt].get("wall_lab") for j in cands}
            de = RM.max_delta_e(labs)
            entry = {"rule": "ok", "rung": None, "views": [j.view.camera for j in jobs],
                     "candidates": [j.view.camera for j in cands], "delta_e_max": de}
            if len(cands) < 2 or RM.labs_agree(labs):
                self.rooms[room] = entry
                continue
            chosen, de_after, cut = self._common_rung(cands)
            entry.update(rule="downgraded", rung=chosen, delta_e_after=de_after)
            if cut:
                entry["incomplete"] = True
            for j in cands:
                before = j.final_attempt
                if chosen is None:
                    j.final, j.final_attempt, j.reason = "cycles", None, ("deadline" if cut else "room")
                    if cut:
                        j.complete = False
                else:
                    j.final, j.final_attempt, j.reason = "polished", chosen, None
                change = (f"keeps a{before}" if chosen == before else
                          f"a{before} -> {'a' + str(chosen) if chosen else 'cycles'}")
                j.notes.append(f"room rule: wall ΔE {de} > {RM.ROOM_MAX_DELTA_E} in {room}; {change}"
                               + (" (deadline before a common rung was found)" if cut else ""))
            self.rooms[room] = entry
            self.write_manifest()

    def _common_rung(self, cands: list[ViewJob]) -> tuple[Optional[int], Optional[float], bool]:
        """``(rung, ΔE at it, cut by the deadline)``: the strongest rung every candidate accepts with
        agreeing wall means (missing rungs are run now); rung None = no such rung."""
        for k in range(1, len(self.attempts) + 1):
            known = [j.by_k.get(k) for j in cands]
            if any(r is not None and not accepted(r) for r in known):
                continue
            ok = True
            for j in cands:
                if j.by_k.get(k) is None:
                    rec = self.run_attempt(j, k, self.attempts[k - 1])
                    if rec is None:
                        self.incomplete = True
                        return None, None, True
                    rec["room_rule"] = True
                    j.by_k[k] = rec
                    j.notes.append(f"room rule ran a{k}")
                    self.write_manifest()
                    if not accepted(rec):
                        ok = False
                        break
            if not ok:
                continue
            labs = {j.view.camera: j.by_k[k].get("wall_lab") for j in cands}
            if RM.labs_agree(labs):
                return k, RM.max_delta_e(labs), False
        return None, None, False

    # -- outputs -----------------------------------------------------------

    def _view_entry(self, job: ViewJob) -> dict:
        ladder_ks = {r["k"] for r in job.attempts}
        extra = [r for k, r in sorted(job.by_k.items()) if k not in ladder_ks]
        attempts = sorted(job.attempts + extra, key=lambda r: r["k"])
        entry = {
            "camera": job.view.camera, "room_id": job.view.room_id, "level_id": job.view.level_id,
            "source_png": relpath(job.view.png, self.out_dir), "source_sha256": job.source_sha256,
            "render_key": job.view.render_key, "prompt": job.prompt or None,
            "prompt_words": {k: v for k, v in job.prompt_info.items() if k not in ("prompt", "warnings")},
            "expected_source": job.expected_source or None,
            "controls": {k: c["file"] for k, c in job.controls.items()},
            "attempts": [{k: v for k, v in r.items()} for r in attempts],
            "final": job.final, "final_attempt": job.final_attempt, "reason": job.reason,
            "complete": job.complete, "notes": list(job.notes),
        }
        if job.ref_error:
            entry["error"] = job.ref_error
        if self.kind != "run":
            entry["accepted"] = [r["k"] for r in attempts if accepted(r)]
        return entry

    def manifest(self) -> dict:
        stats = {}
        if self.backend is not None and self._ready:
            try:
                stats = dict(self.backend.stats())
            except Exception as exc:  # noqa: BLE001
                self._warn(f"backend stats unavailable: {exc}")
        return {
            "schema_version": SCHEMA_VERSION, "kind": self.kind, "project": self.project,
            "incomplete": bool(self.incomplete), "models": self.models, "config": self.cfg,
            "thresholds": getattr(self.gate, "thresholds", None), "device": self.versions.get("device"),
            "torch": self.versions.get("torch"), "diffusers": self.versions.get("diffusers"),
            "memory_mode": stats.get("memory_mode"), "peak_vram_gib": stats.get("peak_vram_gib"),
            "peak_reserved_gib": stats.get("peak_reserved_gib"), "load_seconds": stats.get("load_seconds"),
            "encode_seconds": stats.get("encode_seconds"), "seconds_per_forward": stats.get("seconds_per_forward"),
            "forwards": stats.get("forwards"), "seconds": round(time.time() - self.started, 1),
            "deadline": self.deadline, "polish_allowed": getattr(self, "polish_allowed", True),
            "attempt_list": self.attempts,
            "views": [self._view_entry(j) for j in self.jobs],
            "rooms": self.rooms, "warnings": list(self.warnings),
        }

    def write_manifest(self) -> dict:
        m = self.manifest()
        write_json(self.out_dir / MANIFEST_NAME, m)
        return m

    def _previews(self) -> None:
        """``<cam>_a<k>_preview.jpg`` (<= 300 KB): the final attempt at full size (run), every attempt at
        960 px with ``previews="all"`` (the sweep/smoke default); stale previews of a run are removed."""
        mode = self.previews
        for job in self.jobs:
            cam = job.view.camera
            keep: set = set()
            recs = {r["k"]: r for r in job.attempts}
            recs.update(job.by_k)
            if self.kind == "run" and mode != "none" and job.final == "polished" and job.final_attempt in recs:
                rec = recs[job.final_attempt]
                name = f"{cam}_a{job.final_attempt}_preview.jpg"
                write_preview(V.read_rgb(self.out_dir / rec["png"]), self.out_dir / name)
                rec["preview"] = name
                keep.add(name)
            if mode == "all":
                for rec in recs.values():
                    name = f"{cam}_a{rec['k']}_preview.jpg"
                    if name in keep or not rec.get("png") or not (self.out_dir / rec["png"]).is_file():
                        continue
                    write_preview(V.read_rgb(self.out_dir / rec["png"]), self.out_dir / name,
                                  width=SWEEP_PREVIEW_WIDTH)
                    rec["preview"] = name
                    keep.add(name)
            if self.kind == "run" and mode != "none":
                pattern = re.compile(rf"^{re.escape(cam)}_a\d+_preview\.jpg$")
                for f in self.out_dir.glob(f"{cam}_a*_preview.jpg"):
                    if pattern.match(f.name) and f.name not in keep:
                        f.unlink()

    def _determinism(self) -> Optional[dict]:
        """``determinism.json``: the determinism view's first ladder rung polished twice with one seed."""
        cam = self.cfg.get("determinism_view") or (self.jobs[0].view.camera if self.jobs else None)
        job = next((j for j in self.jobs if j.view.camera == cam), None)
        path = self.out_dir / DETERMINISM_NAME
        if job is None:
            self._warn(f"determinism view {cam} is not in this run; determinism.json not written")
            return None
        attempt = self.attempts[0]
        self._ensure_backend()
        rec = self._base_record(job, 1, attempt)
        data = {"schema_version": SCHEMA_VERSION, "camera": cam, "max_abs_diff": None, "seconds": None,
                "attempt_key": rec["attempt_key"],
                "settings": {k: rec[k] for k in ("strength", "control", "scale", "size", "mode", "seed", "steps")}}
        if path.is_file() and not self.force:
            try:
                old = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                old = {}
            if old.get("attempt_key") == rec["attempt_key"] and old.get("max_abs_diff") is not None:
                return old
        if self.past_deadline():
            data["skipped"] = "deadline"
            write_json(path, data)
            return data
        arr = job.arrays()
        plan = SZ.plan_size(attempt["size"], job.view.size)
        try:
            self._ensure_ready()
            image = SZ.to_model(arr["rgb"], plan)
            control = SZ.to_model(self._control(job, attempt["control"])["array"], plan) if attempt["control"] else None
            outs, secs = [], []
            for _ in range(2):
                t0 = time.time()
                out, _meta = self.backend.generate(image, control, strength=attempt["strength"],
                                                   scale=attempt["scale"], mode=attempt["mode"], seed=rec["seed"],
                                                   steps=self.steps, prompt=job.prompt)
                secs.append(round(time.time() - t0, 2))
                outs.append(SZ.from_model(out, plan).astype(np.int16))
        except Exception as exc:  # noqa: BLE001 - recorded in the file
            data["error"] = f"{type(exc).__name__}: {exc}"
            self._warn(f"determinism check failed: {data['error']}")
            write_json(path, data)
            return data
        data["max_abs_diff"] = int(np.abs(outs[0] - outs[1]).max())
        data["seconds"] = round(sum(secs), 2)
        data["seconds_each"] = secs
        write_json(path, data)
        return data

    # -- main --------------------------------------------------------------

    def execute(self) -> dict:
        """Run everything; returns the final manifest (also written with the report)."""
        from wenart.polish.report import write_report
        from wenart.polish.schema import validate_manifest

        self._load_project()
        self._load_views()
        self.out_dir.mkdir(parents=True, exist_ok=True)
        if not self.polish_allowed:
            for job in self.jobs:
                job.source_sha256 = sha256_file(job.view.png)
                job.final, job.final_attempt, job.reason = "cycles", None, "brief"
                job.notes.append("brief polish: false")
            m = self.write_manifest()
            write_report(m, self.out_dir / REPORT_NAME)
            self.log(f"brief polish: false -> {len(self.jobs)} views keep the Cycles render")
            return m
        self._load_previous()
        for job in self.jobs:
            self._prepare_job(job)
        try:
            for job in self.jobs:
                if self.past_deadline():
                    # No gate reference can be made any more, so nothing of this view can be gated.
                    job.complete = False
                    self.incomplete = True
                    if self.kind == "run":
                        job.final, job.final_attempt, job.reason = "cycles", None, "deadline"
                    continue
                self._write_controls(job)
                self._process(job)
                job.release()
                self.write_manifest()
            if self.kind == "run":
                self._room_rule()
            self._previews()
            if self.kind == "run":
                self._determinism()
        except BaseException as exc:
            self._warn(f"aborted: {type(exc).__name__}: {exc}")
            self.incomplete = True
            self.write_manifest()
            raise
        for job in self.jobs:
            job.release()
        m = self.write_manifest()
        errors = validate_manifest(m)
        for e in errors:
            self._warn(f"manifest schema: {e}")
        if errors:
            m = self.write_manifest()
        write_report(m, self.out_dir / REPORT_NAME)
        return m


def run_polish(project_out, kind: str = "run", **kwargs) -> dict:
    """Convenience wrapper: ``PolishRun(project_out, kind, **kwargs).execute()``."""
    return PolishRun(project_out, kind, **kwargs).execute()
