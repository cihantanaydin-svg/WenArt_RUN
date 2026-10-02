"""End-to-end CPU dry run of Milestone 5 (docs/milestone5.md §1-§8) on synthetic-01.

What: every stage of ``scripts/jobs/polish.sh`` in job order, through the real
CLIs and module entry points, on the committed
``results/furniture/synthetic-01/building_final.json`` (level L0, no assets:
flat colours):

style -> build (and ``--reuse``) -> render of 2 cameras at 192x108, 4 samples,
CPU, auto exposure and white balance -> ``select-controls`` and the hidden
renders with ``--look-from`` -> polish ``run`` and ``sweep`` with a FAKE
diffusion backend (``Deps.backend_factory``) and the REAL gate with FAKE
DAv2/SAM/DINOv2 models -> gate calibration -> vision check ``expected``,
``plan-crops``, ``run``, ``preference``, ``style-photo``, ``combine``,
``calibrate`` with an oracle client for both model keys -> style photo terms
-> report ``final`` and ``sweep``.

Why: each area was built and tested in isolation against fakes of the
others; this test checks that the real modules fit together: the files and
key fields of every manifest exist, every path inside an M5 JSON resolves
relative to that JSON's folder (§1.1), and the final decision of every view
follows §5.5/§7. It also runs the read-only GPU test logic of
``tests/gpu/test_polish.py`` and ``tests/gpu/test_check.py`` on these
outputs (except the calibration-rate test, which needs real models).

Scenario (decided by the fakes, so every branch of the decision is hit):
- salon view: the fake polish erases the largest required piece at strength
  0.375 (the gate rejects a1), and only brightens at 0.25 (a2 accepted); the
  vision check sees every element on a2 -> final polished a2;
- bedroom view: a1 accepted by the gate, but the oracle "model" does not see
  the largest required piece on the polished image -> final cycles, reason
  vision_check (§5.5 differential decision).

The oracle client answers from the object-index pass of the image it is
shown (a fair stand-in for a model that sees what is rendered), never from
the prompt. Skipped without Blender.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import re
import shutil
import time
from pathlib import Path

import numpy as np
import pytest

from wenart import views as V
from wenart.blender import cli as blender_cli
from conftest import START_THRESHOLDS  # the gate start limits the fakes were built for

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "synthetic-01"
CAMS = ("cam_r_L0_salon_1", "cam_r_L0_yatak_odasi_1")
SALON, BEDROOM = CAMS
RES = "192x108"
BLENDER = blender_cli.find_blender()
pytestmark = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, /workspace/tools/"
                                "blender, /opt/wenart/blender, PATH)")
MODEL_IDS = {"qwen": "Qwen/Qwen3-VL-8B-Instruct", "glm": "zai-org/GLM-4.6V-Flash"}
STYLE_TEST_PHOTO = ROOT / "tests" / "fixtures" / "style_photo_synthetic-03_salon.jpg"
LINE = re.compile(r"^- (E\d+): (.+?) \(.*?\); expected inside box \[(\d+), (\d+), (\d+), (\d+)\]", re.M)


# --------------------------------------------------------------------------
# Fakes
# --------------------------------------------------------------------------

class FakeGateModels:
    """Image-driven stand-ins for DAv2-Small / SAM 2.1 / DINOv2 with the ``gate.models.Models`` interface."""

    def info(self):
        return {k: {"repo": f"fake/{k}", "revision": "0", "licence": "test"} for k in ("depth", "sam", "dino")}

    def settle(self):
        return True

    def depth(self, rgb):
        import cv2
        g = cv2.cvtColor(np.ascontiguousarray(rgb), cv2.COLOR_RGB2GRAY).astype(np.float32)
        return cv2.GaussianBlur(g, (0, 0), 3.0) / 255.0

    def sam_masks(self, rgb, boxes):
        a = np.asarray(rgb, np.float32)
        out = np.zeros((len(boxes), a.shape[0], a.shape[1]), bool)
        for k, (x0, y0, x1, y1) in enumerate(boxes):
            x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
            patch = a[y0:y1, x0:x1]
            med = np.median(patch.reshape(-1, 3), axis=0) if patch.size else np.zeros(3)
            out[k, y0:y1, x0:x1] = np.linalg.norm(patch - med, axis=2) < 60
        return out

    def dino_tokens(self, rgb):
        import cv2
        a = np.asarray(rgb, np.float32)
        gh, gw = max(1, a.shape[0] // 14), max(1, a.shape[1] // 14)
        a = cv2.resize(a, (gw * 14, gh * 14), interpolation=cv2.INTER_AREA).reshape(gh, 14, gw, 14, 3)
        return np.concatenate([a.mean(axis=(1, 3)) - 128.0, a.std(axis=(1, 3)) + 1.0], axis=-1)


class FakeBackend:
    """The ``wenart.polish.zimage`` backend interface without a model.

    ``erase``: ``(render height, box)`` -> at strength >= 0.375 the box (in
    render pixels; the "native" size pads the render by equal rows top and
    bottom) is painted with the image's median colour (a lost object the
    gate must reject); otherwise the image is only brightened by 2 levels.
    """

    def __init__(self, erase=None):
        self.erase = erase
        self.calls = []
        self.prompts = []

    def versions(self):
        return {"torch": "fake", "diffusers": "fake", "device": "cpu"}

    def ensure_ready(self, prompts):
        self.prompts = list(prompts)

    def generate(self, image, control, *, strength, scale, mode, seed, steps, prompt):
        self.calls.append({"strength": strength, "control": control is not None, "mode": mode, "seed": seed})
        out = np.clip(image.astype(np.int16) + 2, 0, 255).astype(np.uint8)
        if self.erase and strength >= 0.375:
            render_h, (x0, y0, x1, y1) = self.erase
            dy = (out.shape[0] - render_h) // 2
            out[y0 + dy:y1 + dy, x0:x1] = np.median(image.reshape(-1, 3), axis=0).astype(np.uint8)
        return out, {"pipeline": "fake", "forwards": 1, "sigma0": 0.5, "sigma0_numpy": 0.5, "seconds": 0.0}

    def free_cache(self):
        pass

    def stats(self):
        return {"memory_mode": "resident", "peak_vram_gib": 0.0, "peak_reserved_gib": 0.0, "load_seconds": 0.0,
                "encode_seconds": 0.0, "seconds_per_forward": 0.01, "forwards": len(self.calls)}


class OracleClient:
    """A vision "model" (``.model`` + ``.run_schema``, §1.5) that answers from the index pass of the image.

    An asked element is present when an indexed object of the asked type
    covers its box (IoU >= 0.3 on the 0..1000 grid), else absent; unasked
    indexed doors, windows and furniture are reported as extras; door and
    window counts are the indexed ones. Polished images (``<cam>_a<k>.png``)
    use the index pass of their Cycles render minus ``lost[file name]``
    (wenart ids the polish is pretended to have lost). Style photos get the
    charcoal / polished-concrete answer; the preference picks the polished
    image.
    """

    def __init__(self, model, project_out, lost=None):
        self.model = model
        self.out = Path(project_out)
        self.lost = lost or {}
        self.table = V.index_table(json.loads((self.out / "scene" / "scene_manifest.json").read_text("utf-8")))
        self.calls = []

    def _index_path(self, image: Path) -> tuple[Path, set]:
        m = re.match(r"^(.+)_a\d+$", image.stem)
        if image.parent.name in ("polish", "sweep") and m:
            return self.out / "renders" / f"{m.group(1)}_index.png", set(self.lost.get(image.name, ()))
        return image.with_name(f"{image.stem}_index.png"), set()

    def _objects(self, image: Path) -> list[dict]:
        path, lost = self._index_path(image)
        index = V.read_index(path)
        h, w = index.shape
        objs = []
        for value in np.unique(index):
            e = self.table.get(int(value))
            if not value or e is None or e["wenart_id"] in lost:
                continue
            ys, xs = np.nonzero(index == value)
            box = V.box_to_1000([int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1], w, h)
            objs.append({"id": e["wenart_id"], "kind": e["kind"], "type": e.get("type"), "box": box,
                         "frac": len(xs) / float(w * h)})
        return objs

    @staticmethod
    def _iou(a, b) -> float:
        ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
        iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
        inter = ix * iy
        union = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
        return inter / union if union > 0 else 0.0

    def run_schema(self, images, prompt, schema, *, seed=0, task="custom", max_side=None, labels=None,
                   system_prompt=None):
        from wenart.recognition.vlm_client import VLMResult, schema_errors
        from wenart.vision_check import schemas as S

        self.calls.append({"task": task, "images": [Path(str(i)).name for i in images]})
        if task == "style_photo":
            data = {"floor": "concrete_polished", "walls": "plaster_charcoal", "light": "warm daylight",
                    "family": "industrial"}
        elif task.startswith("preference"):
            first, second = (Path(str(i)).parent.name in ("polish", "sweep") for i in images[:2])
            data = {"choice": "first" if first and not second else "second" if second and not first else "same",
                    "confidence": 0.8}
        else:
            objs = self._objects(Path(str(images[0])))
            used, elements = set(), {}
            for label, what, *box in LINE.findall(prompt):
                box = [int(v) for v in box]
                hit = None
                for o in objs:
                    same = (o["kind"] == "furniture") if what.startswith("furniture piece") else (o["type"] == what)
                    if same and self._iou(o["box"], box) >= 0.3:
                        hit = o
                        break
                if hit is not None:
                    used.add(hit["id"])
                    seen = hit["type"] if hit["type"] in S.CATEGORIES else "other_furniture"
                    elements[label] = {"status": "present", "seen_as": seen, "confidence": 0.9}
                else:
                    elements[label] = {"status": "absent", "seen_as": "nothing", "confidence": 0.9}
            extras = [{"category": o["type"] if o["type"] in S.CATEGORIES else "other_furniture", "box": o["box"],
                       "confidence": 0.9}
                      for o in objs if o["id"] not in used and o["kind"] in ("door", "window", "furniture")
                      and o["frac"] >= 0.01][:S.MAX_EXTRAS]
            data = {"elements": elements, "extras": extras,
                    "door_count": sum(o["kind"] == "door" for o in objs),
                    "window_count": sum(o["kind"] == "window" for o in objs)}
        problems = schema_errors(schema, data)
        return VLMResult(task=task, model=self.model, data=None if problems else data, raw_text=json.dumps(data),
                         latency_s=0.01, attempts=1, error=("schema: " + "; ".join(problems)) if problems else None)


# --------------------------------------------------------------------------
# The run
# --------------------------------------------------------------------------

def _json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_gpu_test(name: str):
    """A tests/gpu module (only its read-only helpers and test functions are used here)."""
    spec = importlib.util.spec_from_file_location(f"m5_e2e_gpu_{name}", ROOT / "tests" / "gpu" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def run(tmp_path_factory):
    """Every stage of the job on synthetic-01 L0; returns paths, exit codes and timings."""
    from wenart.gate import Gate
    from wenart.gate.__main__ import main as gate_main
    from wenart.polish.__main__ import main as polish_main
    from wenart.polish.runner import Deps
    from wenart.report.__main__ import main as report_main
    from wenart.style.__main__ import main as style_main
    from wenart.style.photos import main as photos_main
    from wenart.vision_check.cli import main as vc_main

    t_start = time.time()
    root = tmp_path_factory.mktemp("m5e2e")
    out = root / "outputs" / PROJECT
    out.mkdir(parents=True)
    shutil.copyfile(ROOT / "results" / "furniture" / PROJECT / "building_final.json", out / "building_final.json")
    rc, seconds = {}, {}

    def stage(name, fn):
        """Run one stage; CLIs return their exit code, the Blender helpers a path (exit 0) or raise."""
        t0 = time.time()
        result = fn()
        rc[name] = 0 if isinstance(result, Path) else result
        seconds[name] = round(time.time() - t0, 2)
        return rc[name]

    # look: style (always regenerated), build (+ reuse), render with auto exposure / white balance.
    stage("style", lambda: style_main([str(ROOT / "projects" / PROJECT), "--out", str(out / "style.json")]))
    build_args = dict(style=out / "style.json", level="L0", no_textures=True, preview_samples=4)
    stage("build", lambda: blender_cli.build(out / "building_final.json", out / "scene", **build_args))
    stage("render", lambda: blender_cli.render(out / "scene" / "scene.blend", out / "renders", cameras=",".join(CAMS),
                                               samples=4, res=RES, device="cpu", exposure="auto",
                                               white_balance="auto"))

    # controls: select-controls -> CONTROL lines -> one Blender call with --hide-sets and --look-from.
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        stage("select_controls", lambda: vc_main(["select-controls", "--project-out", str(out)]))
    lines = [ln.split("\t") for ln in buf.getvalue().splitlines() if ln.startswith("CONTROL\t")]
    hide_sets = ";".join(f"{cam}:{cid}{'+plug' if plug == '1' else ''}" for _, cid, cam, plug, _dir in lines)
    if hide_sets:
        stage("controls_render", lambda: blender_cli.render(
            out / "scene" / "scene.blend", out / "controls", samples=4, res=RES, device="cpu", hide_sets=hide_sets,
            look_from=out / "renders" / "render_manifest.json"))

    # expected elements first (the fakes need the boxes), then the polish with the real gate.
    stage("expected", lambda: vc_main(["expected", "--project-out", str(out)]))
    exp = _json(out / "check" / "expected_views.json")["views"]
    # The largest furniture piece of each view, required first (since run 1b's calibration a piece that is
    # mostly out of the frame is optional).
    largest = {cam: sorted((e for e in exp[cam]["elements"] if e["kind"] == "furniture"),
                           key=lambda e: (e["role"] != "required", -e["pixels"]))[0] for cam in CAMS}
    h = int(RES.split("x")[1])
    backend = FakeBackend(erase=(h, largest[SALON]["box_px"]))

    def gate_factory(device):
        return Gate(thresholds=START_THRESHOLDS, models=FakeGateModels(), device="cpu")

    deps = Deps(backend_factory=lambda cfg, device: backend, gate_factory=gate_factory, log=lambda s: None)
    stage("polish_run", lambda: polish_main(["run", "--project-out", str(out), "--device", "cpu"], deps=deps))
    sweep_deps = Deps(backend_factory=lambda cfg, device: FakeBackend(), gate_factory=gate_factory,
                      log=lambda s: None)
    stage("polish_sweep", lambda: polish_main(["sweep", "--project-out", str(out), "--views", "auto", "--grid",
                                               "sweep", "--device", "cpu"], deps=sweep_deps))
    stage("gate_calibrate", lambda: gate_main(["calibrate", "--project-out", str(out), "--device", "cpu"],
                                              gate=gate_factory("cpu")))

    # check: plan crops, both "models" one after the other, then combine and calibrate.
    lost = {f"{BEDROOM}_a1.png": {largest[BEDROOM]["wenart_id"]}}
    clients = {}

    def factory(key, url):
        clients[key] = OracleClient(MODEL_IDS[key], out, lost=lost)
        return clients[key]

    stage("plan_crops", lambda: vc_main(["plan-crops", "--project-out", str(out)]))
    for key in ("qwen", "glm"):
        stage(f"check_run_{key}", lambda: vc_main(["run", "--project-out", str(out), "--model-key", key, "--kinds",
                                                   "cycles,polished,controls,plan_ab"], client_factory=factory))
        stage(f"preference_{key}", lambda: vc_main(["preference", "--project-out", str(out), "--model-key", key,
                                                    "--kinds", "polished,sweep"], client_factory=factory))
        stage(f"style_photo_{key}", lambda: vc_main(["style-photo", "--project-out", str(out), "--model-key", key],
                                                    client_factory=factory))
        stage(f"style_photo_test_{key}", lambda: vc_main(
            ["style-photo", "--project-out", str(out), "--model-key", key, "--photo", str(STYLE_TEST_PHOTO),
             "--out", str(out / "check" / "style_photo_test.json")], client_factory=factory))
    stage("combine", lambda: vc_main(["combine", "--project-out", str(out), "--models", "qwen,glm"]))
    stage("check_calibrate", lambda: vc_main(["calibrate", "--project-out", str(out)]))
    stage("photo_terms", lambda: photos_main(["combine", str(out / "check" / "style_photo_test.json"), "--out",
                                              str(out / "check" / "style_photo_test_terms.json")]))

    # report
    stage("report_final", lambda: report_main(["final", "--project-out", str(out)]))
    stage("report_sweep", lambda: report_main(["sweep", "--project-out", str(out)]))
    return {"out": out, "rc": rc, "seconds": seconds, "total": round(time.time() - t_start, 1), "largest": largest,
            "backend": backend, "clients": clients, "build_args": build_args, "controls": lines}


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

def test_every_stage_exits_0_and_the_run_is_fast(run):
    assert all(v == 0 for v in run["rc"].values()), run["rc"]
    assert run["controls"], "select-controls chose no control"
    assert run["total"] < 120, f"the dry run took {run['total']} s: {run['seconds']}"


def test_build_reuse_skips_blender(run, capsys):
    out = run["out"]
    path = blender_cli.build(out / "building_final.json", out / "scene", reuse=True, **run["build_args"])
    assert path == out / "scene" / "scene_manifest.json"
    assert "BUILD_REUSED" in capsys.readouterr().out


def test_render_and_control_manifests(run):
    out = run["out"]
    views = V.load_views(out / "renders")
    assert set(views) == set(CAMS)
    for cam, view in views.items():
        assert view.size == (192, 108) and view.render_key and view.index_stats
        assert view.exposure["mode"] == "auto" and view.exposure["whitepoint"]
    rm = _json(out / "renders" / "render_manifest.json")
    for _, cid, cam, plug, rel in run["controls"]:
        hidden = _json(out / rel / "render_manifest.json")
        assert hidden["hidden"] == [cid] and hidden["plugged"] == ([cid] if plug == "1" else [])
        (entry,) = [e for e in hidden["renders"] if e["camera"] == cam]
        assert entry["exposure"]["mode"] == "from"
        src = next(e for e in rm["renders"] if e["camera"] == cam)
        assert entry["exposure"]["ev"] == src["exposure"]["ev"]           # controls share the normal look
        assert entry["exposure"]["whitepoint"] == src["exposure"]["whitepoint"]
        index = V.read_index(out / rel / entry["files"]["index"])
        table = V.index_table(_json(out / "scene" / "scene_manifest.json"))
        gone = [v for v, e in table.items() if e["wenart_id"] == cid]
        assert gone and not np.isin(index, gone).any(), f"{cid} still visible in its hidden render"


def test_every_path_in_the_m5_jsons_resolves_relative_to_its_json(run):
    out = run["out"]
    checked = []

    def resolves(json_path: Path, value: str):
        p = Path(value)
        assert not p.is_absolute() and "\\" not in value, f"{json_path.name}: {value} is not a relative POSIX path"
        target = (json_path.parent / p)
        assert target.exists(), f"{json_path.relative_to(out)}: {value} does not resolve"
        checked.append(value)

    rm_path = out / "renders" / "render_manifest.json"
    rm = _json(rm_path)
    resolves(rm_path, rm["scene"])
    for e in rm["renders"]:
        for key in ("png", "exr", "preview"):
            if e.get(key):
                resolves(rm_path, e[key])
        for value in e["files"].values():
            resolves(rm_path, value)
    sm_path = out / "scene" / "scene_manifest.json"
    for level in _json(sm_path)["preview_maps"].values():
        resolves(sm_path, level["png"])
    for hm in (out / "controls").glob("hide_*/render_manifest.json"):
        data = _json(hm)
        resolves(hm, data["scene"])
        resolves(hm, data["look_from"])
    for kind in ("polish", "polish/sweep"):
        pm_path = out / kind / "polish_manifest.json"
        for v in _json(pm_path)["views"]:
            resolves(pm_path, v["source_png"])
            for value in v["controls"].values():
                resolves(pm_path, value)
            for a in v["attempts"]:
                for key in ("png", "preview", "debug_jpg"):
                    if a.get(key):
                        resolves(pm_path, a[key])
    cm_path = out / "check" / "check_manifest.json"
    for cam, cv in _json(cm_path)["views"].items():
        for kind, entry in cv.items():
            if isinstance(entry, dict):
                for value in entry.get("images") or []:
                    resolves(cm_path, value)
    st_path = out / "check" / "style_photo_test.json"
    for call in _json(st_path)["calls"]:
        resolves(st_path, call["file"])
    fm_path = out / "final" / "final_manifest.json"
    fm = _json(fm_path)
    for v in fm["views"]:
        for key in ("image", "preview", "plan"):
            if v.get(key):
                resolves(fm_path, v[key])
    for value in fm["contact_sheets"].values():
        resolves(fm_path, value)
    # controls.json names its base explicitly (§5.5 writes dirs relative to the project output).
    controls = _json(out / "check" / "controls.json")
    assert controls["dir_relative_to"] == "project_out"
    for c in controls["controls"]:
        assert (out / c["dir"] / "render_manifest.json").is_file()
    assert len(checked) > 20


def test_polish_ladder_with_the_real_gate(run):
    out = run["out"]
    from wenart.polish.schema import validate_determinism, validate_manifest

    m = _json(out / "polish" / "polish_manifest.json")
    assert validate_manifest(m) == [] and m["kind"] == "run" and m["incomplete"] is False
    views = {v["camera"]: v for v in m["views"]}
    salon, bedroom = views[SALON], views[BEDROOM]
    # Salon: the erased piece fails the gate at 0.375, the mild change passes at 0.25.
    assert [a["gate"]["decision"] for a in salon["attempts"]] == ["reject", "accept"]
    assert {r["check"] for r in salon["attempts"][0]["gate"]["reasons"]} & {"edges", "colour", "depth", "masks"}
    assert salon["final"] == "polished" and salon["final_attempt"] == 2 and salon["reason"] is None
    assert bedroom["final"] == "polished" and bedroom["final_attempt"] == 1
    for v in m["views"]:
        assert v["source_sha256"] == hashlib.sha256((out / "renders" / f"{v['camera']}.png").read_bytes()).hexdigest()
        assert "control_depth" in v["controls"]["depth"]
        for a in v["attempts"]:
            assert a["debug_jpg"] and (out / "polish" / a["debug_jpg"]).stat().st_size <= 300_000
            assert len(a["gate"]["gate_key"]) == 16 and a["gate"]["metrics"]["size"] == [192, 108]
    # Gate and expected elements are the real modules (prompt words from expected_view).
    assert {v["expected_source"] for v in m["views"]} == {"expected_view"}
    assert m["models"]["gate"] and set(m["models"]["gate"]) == {"depth", "sam", "dino"}
    assert not [w for w in m["warnings"] if "write_debug" in w or "expected_view unavailable" in w]
    det = _json(out / "polish" / "determinism.json")
    assert validate_determinism(det) == [] and det["max_abs_diff"] == 0
    sweep = _json(out / "polish" / "sweep" / "polish_manifest.json")
    assert validate_manifest(sweep) == [] and sweep["kind"] == "sweep"
    assert {v["camera"] for v in sweep["views"]} == set(CAMS)               # sweep_views: one per room
    roles = [a["role"] for a in sweep["views"][0]["attempts"]]
    assert roles.count("presumed_bad") == 1 and roles.count("grid") == 10


def test_polish_rerun_reuses_every_attempt(run):
    from wenart.gate import Gate
    from wenart.polish.runner import Deps, run_polish

    out = run["out"]
    backend = FakeBackend()
    deps = Deps(backend_factory=lambda cfg, device: backend,
                gate_factory=lambda device: Gate(thresholds=START_THRESHOLDS, models=FakeGateModels(), device="cpu"), log=lambda s: None)
    before = _json(out / "polish" / "polish_manifest.json")
    m = run_polish(out, "run", deps=deps, device="cpu")
    assert backend.calls == []                                   # nothing generated again (attempt_key reuse)
    assert [(v["camera"], v["final"], v["final_attempt"]) for v in m["views"]] == \
        [(v["camera"], v["final"], v["final_attempt"]) for v in before["views"]]
    assert all(a["reused"] and a["gate_reused"] for v in m["views"] for a in v["attempts"])
    # No model loaded: the memory/speed numbers are those of the run that made the attempts.
    assert m["stats_source"] == "previous_run" and m["memory_mode"] == before["memory_mode"] == "resident"


def test_gate_calibration_file(run):
    out = run["out"]
    cal = _json(out / "gate" / "gate_calibration.json")
    for key in ("benign", "negative", "presumed_bad", "rates", "per_metric", "smallest_detected", "explanations"):
        assert key in cal, key
    assert cal["benign"] and cal["negative"]
    controls = {r["control"] for r in cal["negative"]}
    assert {"removal", "insertion"} <= controls, controls                   # the --hide renders were used
    assert len(cal["presumed_bad"]) == len(CAMS)                           # the sweep's presumed-bad attempts
    assert (out / "gate" / "gate_calibration.md").is_file()


def test_vision_check_manifest_and_decisions(run):
    out = run["out"]
    cm = _json(out / "check" / "check_manifest.json")
    assert cm["single_pass"] is False and set(cm["models"]) == {"qwen", "glm"}
    salon, bedroom = cm["views"][SALON], cm["views"][BEDROOM]
    for cv in (salon, bedroom):
        assert cv["cycles"]["verdict"] in ("ok", "mismatch") and not cv["cycles"]["unreliable"]
        assert any(k.startswith("removal:") for k in cv) or any(k.startswith("insertion:") for k in cv)
    # The decoy is never seen by the oracle; every asked element of the Cycles image is ok.
    for cv in (salon, bedroom):
        results = {e["result"] for e in cv["cycles"]["elements"].values()}
        assert results <= {"ok"}, results
    lost = run["largest"][BEDROOM]["wenart_id"]
    assert bedroom["polished"]["elements"][lost]["result"] == "missing"
    assert bedroom["polished_rejected"] is True and bedroom["polished_reason"] == "vision_check"
    assert salon["polished_rejected"] is False
    assert Path(salon["polished"]["images"][0]).name == f"{SALON}_a2.png"   # the final attempt was checked
    pref = salon["polished"]["preference"]
    assert pref["preferred"] is True and pref["votes"] >= 3
    cal = _json(out / "check" / "check_calibration.json")
    assert cal["advisory"] == cm["advisory"] == bool(cal["missed"])
    for name in ("debug", "plan"):
        jpgs = list((out / "check").glob(f"*_{'check' if name == 'debug' else 'plan'}.jpg"))
        assert jpgs and all(p.stat().st_size <= 300_000 for p in jpgs)
    terms = _json(out / "check" / "style_photo_test_terms.json")["terms"]
    assert {t["slot"]: t["value"] for t in terms}["walls"] == "plaster_charcoal"


def test_final_decision_follows_the_polish_and_the_vision_check(run):
    """§5.5/§7: polished iff the polish says polished and the vision check did not reject it."""
    out = run["out"]
    from wenart.report.final import validate_final_manifest

    fm = _json(out / "final" / "final_manifest.json")
    assert validate_final_manifest(fm) == []
    pm = {v["camera"]: v for v in _json(out / "polish" / "polish_manifest.json")["views"]}
    cm = _json(out / "check" / "check_manifest.json")["views"]
    finals = {v["camera"]: v for v in fm["views"]}
    assert set(finals) == set(CAMS)
    for cam, v in finals.items():
        want = "polished" if pm[cam]["final"] == "polished" and not cm[cam]["polished_rejected"] else "cycles"
        assert v["final"] == want, (cam, v["final"], v["reason"])
    assert finals[SALON]["final"] == "polished" and finals[SALON]["image"] == f"../polish/{SALON}_a2.png"
    assert finals[BEDROOM]["final"] == "cycles" and finals[BEDROOM]["reason"] == "vision_check"
    assert finals[BEDROOM]["image"] == f"../renders/{BEDROOM}.png"
    assert fm["summary"]["polished"] == 1 and fm["summary"]["cycles_by_reason"] == {"vision_check": 1}
    for name in ("final_report.md", "contact_L0.jpg", f"{SALON}_final_preview.jpg", f"{SALON}_plan.jpg"):
        assert (out / "final" / name).is_file(), name
    assert all(p.stat().st_size <= 300_000 for p in (out / "final").glob("*.jpg"))
    md = (out / "final" / "final_report.md").read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", md)
    assert all("/" not in link and (out / "final" / link).exists() for link in links), links
    assert (out / "final" / "sweep_report.md").is_file()


def test_gpu_test_logic_passes_on_the_dry_run(run, monkeypatch):
    """The read-only GPU tests of the polish and the check accept these (fake-model) outputs."""
    out = run["out"]
    tp = _load_gpu_test("test_polish")
    monkeypatch.setattr(tp, "OUTPUTS", out.parent)
    # The dry run's polish used the gate start limits (its fakes were built for them); the pod tests
    # recompute with the package limits the pod run used.
    monkeypatch.setattr(tp, "current_thresholds", lambda: START_THRESHOLDS)
    project = (PROJECT, _json(out / "polish" / "polish_manifest.json"))
    tp.test_manifest_is_a_complete_run(project)
    tp.test_manifest_records_the_pinned_models(project)
    tp.test_every_view_has_a_final_image_of_render_size(project)
    tp.test_accepted_attempts_pass_every_hard_threshold(project)
    tp.test_rejected_attempts_have_reasons(project)
    tp.test_determinism(project)
    tc = _load_gpu_test("test_check")
    monkeypatch.setattr(tc, "OUTPUTS", out.parent)
    monkeypatch.setattr(tc, "MODEL_KEYS", ["qwen", "glm"])
    from wenart.vision_check.config import load_config
    cfg = load_config()
    tc.test_every_model_answered_its_calls(PROJECT, cfg)
    tc.test_calibration_present(PROJECT, cfg)
    tc.test_advisory_set_exactly_when_a_target_is_missed(PROJECT, cfg)
    tc.test_style_photo_test(PROJECT)
