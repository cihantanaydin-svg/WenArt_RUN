"""CPU tests of the polish runner with a fake pipeline and a fake gate (docs/milestone5.md §3.6, §9 "polish").

A toy project (3 cameras, 2 rooms, one window, one sofa) is written to a
temporary ``outputs/toy``; the fake backend brightens the image by
``strength * gain`` (and can paint the outside view, so pane restore shows),
the fake gate measures the mean change and decides with per-camera limits
(with gain 40: a1 ~ 14.3, a2 ~ 9.5, a3 ~ 4.8; with gain 120 three times that). That
is enough to drive the ladder, the room rule, resumability (attempt_key,
gate_key, decision recomputed), the deadline, ``polish: false``, sweep/smoke,
determinism, the CLI and the manifest schema end to end.
"""
import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest

from wenart import views as V
from wenart.gate.api import Reference
from wenart.polish import config as PC
from wenart.polish import schedule as S
from wenart.polish.__main__ import env_deadline, has_errors, main, summary
from wenart.polish.runner import (DETERMINISM_NAME, MANIFEST_NAME, REPORT_NAME, Deps, PolishError, PolishRun,
                                  find_gate_debug_writer, run_polish)
from wenart.polish.schema import validate_determinism, validate_manifest

W, H = 64, 40
GAIN = 40.0           # fake polish: + strength * gain on every channel (room-rule tests use 120)


# --------------------------------------------------------------------------
# Toy project
# --------------------------------------------------------------------------

def _obj(wenart_id, kind, pass_index, **extra):
    base = {"name": f"{kind}_{wenart_id}", "wenart_id": wenart_id, "kind": kind, "status": "verified",
            "level_id": "L0", "evidence": [{"file": "plan.dxf", "method": "vector", "confidence": 1.0}],
            "pass_index": pass_index}
    base.update(extra)
    return base


def scene_manifest() -> dict:
    profile = json.loads((Path(__file__).resolve().parents[1] / "results" / "renders" / "synthetic-01"
                          / "scene_manifest.json").read_text(encoding="utf-8"))["style_profile"]
    return {
        "schema_version": "0.1", "project": "toy", "building": "outputs/toy/building_final.json",
        "style_profile": profile,
        "cameras": [{"name": "cam_a", "room_id": "r_salon", "level_id": "L0", "lens_mm": 18.0},
                    {"name": "cam_b", "room_id": "r_salon", "level_id": "L0", "lens_mm": 18.0},
                    {"name": "cam_c", "room_id": "r_hol", "level_id": "L0", "lens_mm": 16.0}],
        "objects": [
            _obj("w_1", "wall", None),
            _obj("win_1", "window", 2, wall_id="w_1", room_ids=["r_salon"]),
            _obj("f_1", "furniture", 3, room_id="r_salon", type="sofa", source="from_documents",
                 box3d={"center": [1, 1, 0.4], "size": [2, 0.9, 0.8], "rotation_deg": 0}),
            _obj("f_2", "furniture", 4, room_id="r_hol", type="wardrobe", source="added_by_ai", status="assumed",
                 box3d={"center": [3, 3, 1], "size": [1, 0.6, 2], "rotation_deg": 0}),
        ],
    }


def building() -> dict:
    return {"project": {"id": "toy"},
            "rooms": [{"id": "r_salon", "room_type": "living"}, {"id": "r_hol", "room_type": "hall"}]}


def passes(camera: str):
    index = np.zeros((H, W), dtype=np.uint16)
    depth = np.full((H, W), 4000, dtype=np.uint16)
    normal = np.zeros((H, W, 3), dtype=np.float32)
    normal[:8] = [0, 0, -1]               # ceiling
    normal[8:30] = [0, 1, 0]              # wall
    normal[30:] = [0, 0, 1]               # floor
    depth[30:] = np.linspace(3000, 1200, H - 30).astype(np.uint16)[:, None]
    index[6:28, 36:60] = 2                # window (22 x 24)
    if camera == "cam_c":
        index[20:34, 4:20] = 4            # wardrobe
    else:
        index[24:34, 6:26] = 3            # sofa
    obj = index > 0
    depth[obj & (index != 2)] = 1500
    normal[obj & (index != 2)] = [1, 0, 0]
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    rgb[:8] = [210, 210, 205]
    rgb[8:30] = [120, 118, 112]
    rgb[30:] = [110, 80, 50]
    rgb[index == 2] = [90, 140, 220]       # the outside view
    rgb[index == 3] = [60, 60, 70]
    rgb[index == 4] = [70, 50, 40]
    return rgb, index, depth, normal


def make_project(root: Path, cameras=("cam_a", "cam_b", "cam_c")) -> Path:
    out = root / "outputs" / "toy"
    renders = out / "renders"
    renders.mkdir(parents=True)
    (out / "scene").mkdir()
    rooms = {"cam_a": "r_salon", "cam_b": "r_salon", "cam_c": "r_hol"}
    entries = []
    for cam in cameras:
        rgb, index, depth, normal = passes(cam)
        V.write_png_rgb(renders / f"{cam}.png", rgb)
        V.write_png16(renders / f"{cam}_index.png", index)
        V.write_png16(renders / f"{cam}_depth_mm.png", depth)
        V.write_png_rgb(renders / f"{cam}_normal.png", V.encode_normal(normal, V.normal_hit(normal)))
        stats = {str(k): v for k, v in V.compute_index_stats(index).items()}
        entries.append({"camera": cam, "png": f"{cam}.png", "index_png": f"{cam}_index.png",
                        "resolution": [W, H], "room_id": rooms[cam], "index_stats": stats,
                        "files": {"depth_mm": f"{cam}_depth_mm.png", "normal": f"{cam}_normal.png"},
                        "render_key": "0123456789abcdef", "hidden": [], "plugged": []})
    entries.append({"camera": "cam_old", "png": "cam_old.png", "index_png": "cam_old_index.png",
                    "resolution": [W, H], "room_id": "r_hol"})          # pre-M5 entry: skipped
    (renders / "render_manifest.json").write_text(json.dumps({"schema_version": "0.1", "renders": entries}),
                                                  encoding="utf-8")
    scene = scene_manifest()
    (out / "building_final.json").write_text(json.dumps(building()), encoding="utf-8")
    scene["building"] = str(out / "building_final.json")
    (out / "scene" / "scene_manifest.json").write_text(json.dumps(scene), encoding="utf-8")
    return out


# --------------------------------------------------------------------------
# Fakes
# --------------------------------------------------------------------------

class FakeBackend:
    """The backend interface of wenart.polish.zimage, with a predictable effect."""

    def __init__(self, cfg=None, device="cuda", noise=0, fail_strengths=(), versions=None, gain=GAIN,
                 paint_sky=False):
        self.gain = gain
        self.paint_sky = paint_sky
        self.calls = []
        self.ready = []
        self.frees = 0
        self.noise = noise
        self.fail_strengths = set(fail_strengths)
        self._versions = versions or {"torch": "fake-torch", "diffusers": "fake-diffusers", "device": "fake-gpu"}

    def versions(self):
        return dict(self._versions)

    def ensure_ready(self, prompts):
        self.ready.append(list(prompts))

    def generate(self, image, control, *, strength, scale, mode, seed, steps, prompt):
        assert image.dtype == np.uint8 and image.shape[0] % 16 == 0 and image.shape[1] % 16 == 0
        if control is not None:
            assert control.shape == image.shape
        self.calls.append({"shape": image.shape, "control": None if control is None else int(control.max()),
                           "strength": strength, "scale": scale, "mode": mode, "seed": seed, "steps": steps,
                           "prompt": prompt})
        if strength in self.fail_strengths:
            raise RuntimeError("fake failure")
        out = image.astype(np.float32) + strength * self.gain + self.noise * len(self.calls)
        if self.paint_sky:     # paint the outside view (blue pixels) green, so pane restore is visible
            sky = (image[..., 2] > 200) & (image[..., 0] < 100)
            out[sky] = [20, 200, 20]
        tail = S.sigma_tail(steps, strength)
        return np.clip(out, 0, 255).astype(np.uint8), {"pipeline": "fake", "forwards": len(tail),
                                                       "sigma0": S.sigma0(tail)}

    def free_cache(self):
        self.frees += 1

    def stats(self):
        return {"memory_mode": "resident", "peak_vram_gib": 1.5, "peak_reserved_gib": 2.0, "load_seconds": 0.5,
                "encode_seconds": 0.1, "seconds_per_forward": 0.01, "forwards": len(self.calls)}


def fake_decide(metrics, thresholds):
    """Accept when the mean change of the camera lies inside its [lo, hi] window."""
    cam = metrics["camera"]
    lo, hi = thresholds.get("limits", {}).get(cam, thresholds.get("default", [0.0, 1e9]))
    value = metrics["delta"]["global"]
    reasons = []
    if value > hi:
        reasons.append({"check": "delta", "region": "global", "value": value, "threshold": hi, "op": "<="})
    if value < lo:
        reasons.append({"check": "delta", "region": "global", "value": value, "threshold": lo, "op": ">="})
    return ("reject" if reasons else "accept"), reasons, []


class FakeGate:
    """prepare/compare of §1.3 on numpy arrays; decisions through ``fake_decide``."""

    def __init__(self, thresholds=None, key="gate-key-1"):
        self.thresholds = thresholds or {"default": [0.0, 1e9]}
        self.key = key
        self.prepared = []
        self.compared = []

    def prepare(self, view, ref_rgb):
        assert ref_rgb.shape == (view.height, view.width, 3)
        self.prepared.append(view.camera)
        return Reference(view=view, rgb=ref_rgb, sha256="x", gate_key=self.key)

    def compare(self, ref, test_rgb):
        if test_rgb.shape != ref.rgb.shape:
            raise ValueError("test image is not the view size")
        self.compared.append(ref.view.camera)
        delta = float(np.abs(test_rgb.astype(float) - ref.rgb.astype(float)).mean())
        metrics = {"camera": ref.view.camera, "delta": {"global": round(delta, 4), "regions": {}, "skipped": {}}}
        decision, reasons, notes = fake_decide(metrics, self.thresholds)
        return {"decision": decision, "reasons": reasons, "notes": notes, "metrics": metrics, "gate_key": self.key}


class FakeExpected:
    """expected_view / expected_views / sweep_views of §1.4."""

    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def expected_view(self, view, scene_manifest, building, cfg=None):
        self.calls.append(view.camera)
        if self.fail:
            raise NotImplementedError("area D")
        room_type = {r["id"]: r["room_type"] for r in building["rooms"]}[view.room_id]
        elements = [{"kind": "furniture", "type": "sofa" if view.room_id == "r_salon" else "wardrobe",
                     "own_room": True, "role": "required", "pixels": 200, "status": "verified"},
                    {"kind": "furniture", "type": "armchair", "own_room": True, "role": "optional", "pixels": 50,
                     "status": "verified"},
                    {"kind": "window", "type": "window", "own_room": True, "role": "required", "pixels": 500}]
        return {"camera": view.camera, "room_id": view.room_id, "room_type": room_type, "size": [W, H],
                "elements": elements, "json_crosscheck": {}}

    def expected_views(self, project_out, render_dir=None):
        if self.fail:
            raise NotImplementedError("area D")
        return {"cam_a": {"room_id": "r_salon"}, "cam_b": {"room_id": "r_salon"}, "cam_c": {"room_id": "r_hol"}}

    def sweep_views(self, expected_views, n):
        return ["cam_c", "cam_a"][:n]


def gate_models():
    return {"models": {"depth": {"repo": "d/r", "revision": "1" * 40, "licence": "Apache-2.0"}}}


def debug_writer(ref, test_rgb, result, path):
    from PIL import Image
    Image.fromarray(np.concatenate([ref.rgb, test_rgb], axis=1)).save(path, "JPEG", quality=80)
    return path


def make_deps(backend=None, gate=None, expected=None, clock=None, writer=debug_writer, logs=None):
    backend = backend or FakeBackend()
    gate = gate or FakeGate()
    deps = Deps(backend_factory=lambda cfg, device: backend, gate_factory=lambda device: gate, decide=fake_decide,
                debug_writer=writer, expected=expected or FakeExpected(), gate_models=gate_models,
                log=(logs.append if logs is not None else (lambda s: None)), find_debug_writer=False)
    if clock is not None:
        deps.clock = clock
    return deps, backend, gate


def cfg_with(**changes) -> dict:
    cfg = PC.load_config()
    cfg.update(changes)
    return cfg


def view_of(m, cam):
    return next(v for v in m["views"] if v["camera"] == cam)


# --------------------------------------------------------------------------
# The run ladder
# --------------------------------------------------------------------------

def test_run_ladder_first_accepted_attempt_wins(tmp_path):
    out = make_project(tmp_path)
    gate = FakeGate({"limits": {"cam_b": [0, 12], "cam_c": [0, 3]}, "default": [0, 1e9]})
    deps, backend, gate = make_deps(gate=gate)
    m = run_polish(out, "run", deps=deps)
    assert validate_manifest(m) == []
    assert m["kind"] == "run" and m["project"] == "toy" and not m["incomplete"]
    assert [v["camera"] for v in m["views"]] == ["cam_a", "cam_b", "cam_c"]   # cam_old (stale) skipped
    assert any("cam_old" in w for w in m["warnings"])
    a, b, c = (view_of(m, cam) for cam in ("cam_a", "cam_b", "cam_c"))
    assert (a["final"], a["final_attempt"], a["reason"]) == ("polished", 1, None)
    assert [r["k"] for r in a["attempts"]] == [1]                            # stops at the first accept
    assert (b["final"], b["final_attempt"]) == ("polished", 2)
    assert b["attempts"][0]["gate"]["decision"] == "reject" and b["attempts"][0]["gate"]["reasons"][0]["op"] == "<="
    assert (c["final"], c["final_attempt"], c["reason"]) == ("cycles", None, "gate")
    assert len(c["attempts"]) == 3
    # Attempt records.
    r = a["attempts"][0]
    assert (r["strength"], r["control"], r["scale"], r["size"], r["mode"], r["role"]) == (
        0.375, "geometry", 0.8, "native", "plain", "ladder")
    assert r["seed"] == 1 and r["steps"] == 8 and r["sigmas"] == [0.375, 0.25, 0.125]
    assert r["sigma0"] == pytest.approx(0.642857, abs=1e-5) and r["forwards"] == 3
    assert r["png"] == "cam_a_a1.png" and len(r["attempt_key"]) == 64 and r["panes_restored"] == 1
    assert r["gate"]["gate_key"] == "gate-key-1" and r["debug_jpg"] == "cam_a_a1_gate.jpg"
    assert [x["seed"] for x in c["attempts"]] == [1, 2, 3]
    # Files and paths.
    pol = out / "polish"
    # One control image per control type of the ladder, written once per view.
    assert a["source_png"] == "../renders/cam_a.png" and a["controls"] == {
        c: f"cam_a_control_{c}.png" for c in ("geometry", "canny", "depth")}
    for name in ("cam_a_a1.png", "cam_a_control_depth.png", "cam_a_a1_gate.jpg", "cam_a_a1_preview.jpg",
                 "cam_b_a2_preview.jpg", MANIFEST_NAME, REPORT_NAME, DETERMINISM_NAME):
        assert (pol / name).is_file(), name
    assert not (pol / "cam_b_a1_preview.jpg").exists() and not (pol / "cam_c_a1_preview.jpg").exists()
    assert (pol / "cam_a_a1_preview.jpg").stat().st_size <= 300_000
    img = V.read_rgb(pol / "cam_a_a1.png")
    assert img.shape == (H, W, 3)                                              # render size, not 48 rows
    # Backend: padded to 64 x 48, one ensure_ready with every prompt, cache freed before gate calls.
    assert all(call["shape"] == (48, 64, 3) for call in backend.calls)
    assert len(backend.ready) == 1 and len(backend.ready[0]) == 2             # two rooms -> two prompts
    assert backend.frees >= len(gate.compared)
    assert sorted(gate.prepared) == ["cam_a", "cam_b", "cam_c"]               # one reference per view
    assert m["models"]["base"]["repo"] == "Tongyi-MAI/Z-Image-Turbo" and m["models"]["gate"]["depth"]["repo"] == "d/r"
    assert m["torch"] == "fake-torch" and m["memory_mode"] == "resident" and m["thresholds"] == gate.thresholds
    # Prompt from the expected elements and the rendered profile.
    assert a["prompt"].startswith("Photorealistic interior photograph of a living room in Scandinavian style. "
                                  "White plaster walls, light oak wood floor, sofa, armchair.")
    assert c["prompt"].startswith("Photorealistic interior photograph of a hallway")
    # Milestone 8: the lens words are each view camera's own lens_mm (the scene manifest's plan).
    assert a["prompt"].endswith("sharp focus, 18 mm lens.") and c["prompt"].endswith("sharp focus, 16 mm lens.")
    assert a["expected_source"] == "expected_view"
    report = (pol / REPORT_NAME).read_text(encoding="utf-8")
    assert "# Polish report: toy (run)" in report and "cam_c" in report and "delta:global" in report


def _png_zlib_header(path):
    """The first two bytes of the zlib stream in the first IDAT chunk of a PNG file."""
    data = Path(path).read_bytes()
    pos = 8
    while pos < len(data):
        length = int.from_bytes(data[pos:pos + 4], "big")
        if data[pos + 4:pos + 8] == b"IDAT":
            return data[pos + 8:pos + 10]
        pos += 12 + length
    raise AssertionError("no IDAT chunk")


def test_attempt_pngs_are_written_fast_lossless_and_hashed_once(tmp_path):
    """Pod run 0b: the CPU side of an attempt was mostly the PNG encoder at its default zlib level 6."""
    import hashlib
    out = make_project(tmp_path, cameras=("cam_a",))
    deps, backend, gate = make_deps(backend=FakeBackend(noise=1))
    m = run_polish(out, "run", deps=deps)
    rec = view_of(m, "cam_a")["attempts"][0]
    path = out / "polish" / rec["png"]
    assert _png_zlib_header(path)[1] & 0xC0 == 0                     # zlib FLEVEL 0: the fastest level
    assert rec["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    from wenart.polish.runner import write_attempt_png
    rgb = np.random.default_rng(1).integers(0, 256, (H, W, 3), dtype=np.uint8)
    p, sha = write_attempt_png(tmp_path / "x" / "a.png", rgb)
    assert np.array_equal(V.read_rgb(p), rgb) and sha == hashlib.sha256(p.read_bytes()).hexdigest()
    assert not list((tmp_path / "x").glob("*.tmp"))
    with pytest.raises(ValueError):
        write_attempt_png(tmp_path / "x" / "b.png", rgb.astype(np.float32))


def test_attempt_records_split_their_time(tmp_path):
    """Where an attempt's time goes: the pipeline call (``diffusion_seconds``), the rest of ``generate``
    (``seconds`` - ``diffusion_seconds``), the runner's own CPU work (``cpu_seconds``) and the gate."""
    out = make_project(tmp_path, cameras=("cam_a",))

    class TimedBackend(FakeBackend):
        def generate(self, image, control, **kwargs):
            img, meta = super().generate(image, control, **kwargs)
            return img, dict(meta, seconds=1.25)

    deps, backend, gate = make_deps(backend=TimedBackend())
    m = run_polish(out, "run", deps=deps)
    rec = view_of(m, "cam_a")["attempts"][0]
    assert rec["diffusion_seconds"] == 1.25
    assert isinstance(rec["cpu_seconds"], float) and 0 <= rec["cpu_seconds"] < 10
    assert isinstance(rec["gate_seconds"], float) and isinstance(rec["seconds"], float)


def test_pane_restore_keeps_the_cycles_outside_view(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))
    deps, backend, gate = make_deps(backend=FakeBackend(paint_sky=True))
    run_polish(out, "run", deps=deps)
    rgb, index, _, _ = passes("cam_a")
    polished = V.read_rgb(out / "polish" / "cam_a_a1.png")
    core = V.erode(index == 2, 6)
    assert np.array_equal(polished[core], rgb[core])                 # the fake painted it green; restored
    wall = np.zeros_like(core)
    wall[10:20, 2:30] = True
    assert (polished[wall].astype(int) - rgb[wall].astype(int) == 15).all()   # 0.375 * 40 elsewhere
    band = (index == 2) & ~V.erode(index == 2, 3)
    assert (polished[band] == [20, 200, 20]).all()                   # the frame band stays polished


def test_brief_polish_false_keeps_every_cycles_render(tmp_path, monkeypatch):
    out = make_project(tmp_path)
    brief = types.ModuleType("wenart.brief")
    brief.load_brief = lambda project_dir: {"values": {"polish": False}, "assumed": []}
    monkeypatch.setitem(sys.modules, "wenart.brief", brief)
    deps, backend, gate = make_deps()
    m = run_polish(out, "run", deps=deps)
    assert validate_manifest(m) == []
    assert all((v["final"], v["reason"], v["attempts"]) == ("cycles", "brief", []) for v in m["views"])
    assert backend.calls == [] and backend.ready == [] and gate.prepared == []
    assert m["polish_allowed"] is False and m["torch"] is None
    assert "polish: false" in (out / "polish" / REPORT_NAME).read_text(encoding="utf-8")
    brief.load_brief = lambda project_dir: {"values": {"polish": True}, "assumed": ["polish"]}
    m2 = run_polish(out, "run", deps=make_deps()[0])
    assert all(v["reason"] != "brief" for v in m2["views"])


def test_failed_attempt_moves_on_and_is_reported(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))
    deps, backend, gate = make_deps(backend=FakeBackend(fail_strengths={0.375}))
    m = run_polish(out, "run", deps=deps)
    a = view_of(m, "cam_a")
    assert a["attempts"][0]["error"] == "RuntimeError: fake failure" and a["attempts"][0]["gate"] is None
    assert (a["final"], a["final_attempt"]) == ("polished", 2)
    assert has_errors(m) and validate_manifest(m) == []
    deps, backend, gate = make_deps(backend=FakeBackend(fail_strengths={0.375, 0.25, 0.125}))
    m = run_polish(out, "run", deps=deps, force=True)
    assert (view_of(m, "cam_a")["final"], view_of(m, "cam_a")["reason"]) == ("cycles", "error")


class OOMBackend(FakeBackend):
    """A backend whose first polish hits a CUDA OOM: it calls its release hook before its retry (zimage)."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.release_hook = None
        self.released = 0

    def generate(self, image, control, **kwargs):
        if not self.released:
            self.released += 1
            self.release_hook()
        return super().generate(image, control, **kwargs)


class ReleasingGate(FakeGate):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.releases = 0

    def release_gpu(self):
        self.releases += 1


def test_the_backend_release_hook_moves_the_gate_models_off_the_gpu(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))
    deps, backend, gate = make_deps(backend=OOMBackend(), gate=ReleasingGate())
    m = run_polish(out, "run", deps=deps)
    assert backend.released == 1 and gate.releases == 1
    assert view_of(m, "cam_a")["final"] == "polished" and validate_manifest(m) == []
    # A gate without release_gpu (or none loaded yet) is fine: the hook does nothing.
    deps, backend, gate = make_deps(backend=OOMBackend())
    m = run_polish(out, "run", deps=deps, force=True)
    assert backend.released == 1 and view_of(m, "cam_a")["final"] == "polished"
    run = PolishRun(out, "run", deps=make_deps(backend=OOMBackend())[0])
    run._ensure_backend()
    run.backend.release_hook()                                   # no gate yet: nothing to release


def test_oom_retries_of_the_backend_reach_the_manifest(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))

    class RetryingBackend(FakeBackend):
        def stats(self):
            return dict(super().stats(), oom_retries=2)

    deps, backend, gate = make_deps(backend=RetryingBackend())
    m = run_polish(out, "run", deps=deps)
    assert m["oom_retries"] == 2 and m["memory_mode"] == "resident"


class FailingLoadBackend(FakeBackend):
    """A backend whose model load fails (pod run 0: offline tokenizer lookup)."""

    def ensure_ready(self, prompts):
        self.ready.append(list(prompts))
        raise OSError("We couldn't connect to 'https://huggingface.co' to load the files")


def test_a_failed_model_load_is_not_retried_for_every_attempt(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a", "cam_b"))
    backend = FailingLoadBackend()
    deps, backend, gate = make_deps(backend=backend)
    m = run_polish(out, "run", deps=deps)
    assert len(backend.ready) == 1 and backend.calls == []          # one load attempt in the whole run
    for cam in ("cam_a", "cam_b"):
        v = view_of(m, cam)
        assert (v["final"], v["reason"]) == ("cycles", "error")
        assert all("OSError" in a["error"] for a in v["attempts"])
    assert validate_manifest(m) == []


def test_gate_prepare_failure_falls_back_to_cycles(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))

    class BrokenGate(FakeGate):
        def prepare(self, view, ref_rgb):
            raise RuntimeError("no SAM")

    deps, backend, gate = make_deps(gate=BrokenGate())
    m = run_polish(out, "run", deps=deps)
    a = view_of(m, "cam_a")
    assert (a["final"], a["reason"]) == ("cycles", "error") and "no SAM" in a["error"]
    assert len(a["attempts"]) == 1 and a["attempts"][0]["png"] is None
    assert len(backend.calls) == 2                       # only the determinism check (it needs no gate)


# --------------------------------------------------------------------------
# Room rule
# --------------------------------------------------------------------------

def test_room_rule_downgrades_to_the_strongest_common_rung(tmp_path):
    out = make_project(tmp_path)
    # gain 120: cam_a accepts a1 (+45), cam_b only from a2 (+30): walls differ by > ΔE 5 -> both take a2.
    gate = FakeGate({"limits": {"cam_b": [0, 35]}, "default": [0, 1e9]})
    deps, backend, gate = make_deps(gate=gate, backend=FakeBackend(gain=120))
    m = run_polish(out, "run", deps=deps)
    a, b = view_of(m, "cam_a"), view_of(m, "cam_b")
    assert (a["final"], a["final_attempt"]) == ("polished", 2) and (b["final"], b["final_attempt"]) == ("polished", 2)
    room = m["rooms"]["r_salon"]
    assert room["rule"] == "downgraded" and room["rung"] == 2 and room["delta_e_max"] > 5
    assert room["delta_e_after"] == pytest.approx(0.0, abs=0.5) and room["candidates"] == ["cam_a", "cam_b"]
    assert [r["k"] for r in a["attempts"]] == [1, 2] and a["attempts"][1]["room_rule"] is True
    assert any("room rule" in n for n in a["notes"])
    assert m["rooms"]["r_hol"]["rule"] == "ok" and m["rooms"]["r_hol"]["rung"] is None
    assert (out / "polish" / "cam_a_a2_preview.jpg").is_file()
    assert not (out / "polish" / "cam_a_a1_preview.jpg").exists()
    assert validate_manifest(m) == []


def test_room_rule_falls_back_to_cycles_without_a_common_rung(tmp_path):
    out = make_project(tmp_path)
    gate = FakeGate({"limits": {"cam_a": [40, 1e9], "cam_b": [0, 20]}, "default": [0, 1e9]})
    deps, backend, gate = make_deps(gate=gate, backend=FakeBackend(gain=120))
    m = run_polish(out, "run", deps=deps)
    a, b = view_of(m, "cam_a"), view_of(m, "cam_b")
    assert (a["final"], a["reason"]) == ("cycles", "room") and (b["final"], b["reason"]) == ("cycles", "room")
    assert m["rooms"]["r_salon"]["rule"] == "downgraded" and m["rooms"]["r_salon"]["rung"] is None
    report = (out / "polish" / REPORT_NAME).read_text(encoding="utf-8")
    assert "| r_salon | downgraded | cycles |" in report


def test_deadline_during_the_room_rule_keeps_cycles_with_reason_deadline(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a", "cam_b"))
    gate = FakeGate({"limits": {"cam_b": [0, 35]}, "default": [0, 1e9]})
    # The clock passes the deadline after the third gate comparison (cam_a a1, cam_b a1, cam_b a2).
    deps, backend, gate = make_deps(gate=gate, backend=FakeBackend(gain=120),
                                    clock=lambda: 1000.0 + 100.0 * len(gate.compared))
    m = run_polish(out, "run", deps=deps, deadline=1300.0)
    a, b = view_of(m, "cam_a"), view_of(m, "cam_b")
    assert m["incomplete"] and m["rooms"]["r_salon"]["incomplete"] and m["rooms"]["r_salon"]["rung"] is None
    assert (a["final"], a["reason"]) == ("cycles", "deadline") and (b["final"], b["reason"]) == ("cycles", "deadline")
    assert "deadline" in a["notes"][-1] and validate_manifest(m) == []


def test_write_json_accepts_numpy_values(tmp_path):
    from wenart.polish.runner import write_json
    path = write_json(tmp_path / "x.json", {"a": np.float32(0.5), "b": np.int64(3), "c": np.array([1, 2]),
                                            "d": np.bool_(True), "e": tmp_path / "f.png"})
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data == {"a": 0.5, "b": 3, "c": [1, 2], "d": True, "e": (tmp_path / "f.png").as_posix()}
    with pytest.raises(TypeError):
        write_json(tmp_path / "y.json", {"x": object()})


def test_room_rule_ok_when_walls_agree(tmp_path):
    out = make_project(tmp_path)
    deps, backend, gate = make_deps()
    m = run_polish(out, "run", deps=deps)
    assert m["rooms"]["r_salon"] == {"rule": "ok", "rung": None, "views": ["cam_a", "cam_b"],
                                     "candidates": ["cam_a", "cam_b"], "delta_e_max": 0.0}
    assert view_of(m, "cam_a")["final_attempt"] == view_of(m, "cam_b")["final_attempt"] == 1


# --------------------------------------------------------------------------
# Resumability (§3.6)
# --------------------------------------------------------------------------

def test_rerun_reuses_pngs_and_gate_metrics(tmp_path):
    out = make_project(tmp_path)
    limits = {"limits": {"cam_b": [0, 12], "cam_c": [0, 3]}, "default": [0, 1e9]}
    deps, backend, gate = make_deps(gate=FakeGate(limits))
    first = run_polish(out, "run", deps=deps)
    n_calls = len(backend.calls)
    deps2, backend2, gate2 = make_deps(gate=FakeGate(limits))
    second = run_polish(out, "run", deps=deps2)
    assert backend2.calls == [] and backend2.ready == [] and gate2.compared == []
    for v1, v2 in zip(first["views"], second["views"]):
        assert (v1["final"], v1["final_attempt"], v1["reason"]) == (v2["final"], v2["final_attempt"], v2["reason"])
        assert [r["attempt_key"] for r in v1["attempts"]] == [r["attempt_key"] for r in v2["attempts"]]
        assert all(r["reused"] and r["gate_reused"] for r in v2["attempts"])
    assert n_calls > 0 and validate_manifest(second) == []
    assert "png + gate" in (out / "polish" / REPORT_NAME).read_text(encoding="utf-8")


def test_new_gate_key_regates_stored_pngs(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))
    run_polish(out, "run", deps=make_deps()[0])
    deps, backend, gate = make_deps(gate=FakeGate(key="gate-key-2"))
    m = run_polish(out, "run", deps=deps)
    r = view_of(m, "cam_a")["attempts"][0]
    assert backend.calls == [] and gate.compared == ["cam_a"]
    assert r["reused"] and not r["gate_reused"] and r["gate"]["gate_key"] == "gate-key-2"


def decide_with_errors(metrics, thresholds):
    """``fake_decide`` plus the rule of the real ``decide``: a check with an ``error`` fails."""
    errors = [{"check": c, "region": "global", "value": None, "threshold": None, "op": "<=", "error": m["error"]}
              for c, m in metrics.items() if isinstance(m, dict) and m.get("error")]
    decision, reasons, notes = fake_decide(metrics, thresholds)
    return ("reject" if errors else decision), errors + reasons, notes


class ModelErrorGate(FakeGate):
    """A gate whose SAM check failed (CUDA OOM): stored as an error metric, the attempt is rejected."""

    def compare(self, ref, test_rgb):
        result = super().compare(ref, test_rgb)
        result["metrics"]["masks"] = {"global": None, "regions": {}, "skipped": {},
                                      "error": "OutOfMemoryError: CUDA out of memory"}
        result["decision"], result["reasons"], result["notes"] = decide_with_errors(result["metrics"],
                                                                                    self.thresholds)
        return result


def test_stored_gate_metrics_with_a_model_error_are_computed_again(tmp_path):
    """Review finding: a check that could not be computed (SAM out of memory, a missing snapshot) was reused
    with the same gate_key on the next run, so a transient model failure became a permanent reject."""
    out = make_project(tmp_path, cameras=("cam_a",))
    deps, backend, gate = make_deps(gate=ModelErrorGate())
    deps.decide = decide_with_errors
    first = run_polish(out, "run", deps=deps)
    a = view_of(first, "cam_a")
    assert (a["final"], a["reason"]) == ("cycles", "gate") and len(a["attempts"]) == 3
    assert all(r["gate"]["metrics"]["masks"]["error"] for r in a["attempts"])
    # The model works again; the gate key is the same (it covers code, model revisions and the reference only).
    deps, backend, gate = make_deps(gate=FakeGate(key="gate-key-1"))
    deps.decide = decide_with_errors
    m = run_polish(out, "run", deps=deps)
    a = view_of(m, "cam_a")
    r1 = a["attempts"][0]
    assert backend.calls == [] and gate.compared == ["cam_a"]          # the PNG is reused, the gate runs again
    assert r1["reused"] and not r1["gate_reused"] and r1["gate"]["decision"] == "accept"
    assert "masks" not in r1["gate"]["metrics"]
    assert (a["final"], a["final_attempt"]) == ("polished", 1) and validate_manifest(m) == []
    # Complete metrics are reused as before.
    deps, backend, gate = make_deps(gate=FakeGate(key="gate-key-1"))
    deps.decide = decide_with_errors
    m = run_polish(out, "run", deps=deps)
    assert gate.compared == [] and view_of(m, "cam_a")["attempts"][0]["gate_reused"]


def test_gate_metrics_complete():
    from wenart.polish.runner import gate_metrics_complete
    ok = {"camera": "c", "edges": {"global": 0.9, "regions": {"f_1": 0.8}, "skipped": {}},
          "regions": {"f_1": {"kind": "furniture", "pixels": 10}}, "seconds": {"edges": 0.1}, "size": [64, 40]}
    assert gate_metrics_complete(ok)
    assert not gate_metrics_complete(dict(ok, depth={"global": None, "regions": {}, "skipped": {}, "error": "x"}))
    assert not gate_metrics_complete(None) and not gate_metrics_complete({}) and not gate_metrics_complete([1])


def test_decision_is_recomputed_with_the_current_thresholds(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))
    run_polish(out, "run", deps=make_deps()[0])                       # a1 accepted
    deps, backend, gate = make_deps(gate=FakeGate({"default": [0, 12]}))
    m = run_polish(out, "run", deps=deps)
    a = view_of(m, "cam_a")
    r1, r2 = a["attempts"]
    assert r1["reused"] and r1["gate_reused"] and r1["gate"]["decision"] == "reject"
    assert not r2["reused"] and r2["gate"]["decision"] == "accept"
    assert (a["final"], a["final_attempt"]) == ("polished", 2)
    assert [c["strength"] for c in backend.calls if c["strength"] != 0.375] == [0.25]
    assert gate.compared == ["cam_a"]                                  # only the new attempt was compared


def test_changed_inputs_or_tampered_files_are_polished_again(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))
    run_polish(out, "run", deps=make_deps()[0])
    pol = out / "polish"
    # A changed PNG on disk is not trusted.
    V.write_png_rgb(pol / "cam_a_a1.png", np.zeros((H, W, 3), np.uint8))
    deps, backend, _ = make_deps()
    m = run_polish(out, "run", deps=deps)
    assert len([c for c in backend.calls if c["strength"] == 0.375]) == 1
    assert not view_of(m, "cam_a")["attempts"][0]["reused"]
    # A new torch version changes every attempt key (a1, and the determinism pair).
    deps, backend, _ = make_deps(backend=FakeBackend(versions={"torch": "9", "diffusers": "x", "device": "d"}))
    run_polish(out, "run", deps=deps)
    assert len([c for c in backend.calls if c["strength"] == 0.375]) == 3
    # A new render (source PNG) changes the key too.
    rgb = V.read_rgb(out / "renders" / "cam_a.png")
    rgb[0, 0] = [1, 2, 3]
    V.write_png_rgb(out / "renders" / "cam_a.png", rgb)
    deps, backend, _ = make_deps(backend=FakeBackend(versions={"torch": "9", "diffusers": "x", "device": "d"}))
    run_polish(out, "run", deps=deps)
    assert len([c for c in backend.calls if c["strength"] == 0.375]) == 3
    # --force ignores the previous manifest.
    deps, backend, _ = make_deps(backend=FakeBackend(versions={"torch": "9", "diffusers": "x", "device": "d"}))
    run_polish(out, "run", deps=deps, force=True)
    assert len([c for c in backend.calls if c["strength"] == 0.375]) == 3     # a1 + determinism twice


# --------------------------------------------------------------------------
# Deadline
# --------------------------------------------------------------------------

class StepClock:
    """Epoch clock that advances one second per reading."""

    def __init__(self, start=1000.0):
        self.t = start

    def __call__(self):
        self.t += 1.0
        return self.t


def test_deadline_stops_new_attempts_and_marks_the_manifest(tmp_path):
    out = make_project(tmp_path)
    gate = FakeGate({"limits": {"cam_a": [0, 3]}, "default": [0, 1e9]})     # cam_a rejects every rung
    clock = StepClock()
    deps, backend, gate = make_deps(gate=gate, clock=clock)
    m = run_polish(out, "run", deps=deps, deadline=1004.0)
    assert m["incomplete"] is True and validate_manifest(m) == []
    a, b, c = (view_of(m, cam) for cam in ("cam_a", "cam_b", "cam_c"))
    assert 1 <= len(a["attempts"]) < 3 and (a["final"], a["reason"]) == ("cycles", "deadline")
    assert (b["final"], b["reason"]) == (c["final"], c["reason"]) == ("cycles", "deadline")
    assert b["attempts"] == [] and not b["complete"]
    det = json.loads((out / "polish" / DETERMINISM_NAME).read_text(encoding="utf-8"))
    assert det["skipped"] == "deadline" and det["max_abs_diff"] is None
    assert "Incomplete" in (out / "polish" / REPORT_NAME).read_text(encoding="utf-8")
    # The next run (no deadline) continues from the stored attempts.
    deps2, backend2, _ = make_deps(gate=FakeGate({"limits": {"cam_a": [0, 3]}, "default": [0, 1e9]}))
    m2 = run_polish(out, "run", deps=deps2)
    assert not m2["incomplete"] and view_of(m2, "cam_a")["attempts"][0]["reused"]
    assert view_of(m2, "cam_b")["final"] == "polished"


def test_deadline_in_the_past_starts_nothing(tmp_path):
    out = make_project(tmp_path)
    deps, backend, gate = make_deps()
    code = main(["run", "--project-out", str(out), "--deadline", "1"], deps=deps)
    assert code == 0 and backend.calls == [] and gate.prepared == []
    m = json.loads((out / "polish" / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert m["incomplete"] and all(v["reason"] == "deadline" for v in m["views"])


def test_deadline_from_the_environment(monkeypatch):
    assert env_deadline({}) is None and env_deadline({"WENART_DEADLINE": ""}) is None
    assert env_deadline({"WENART_DEADLINE": "1790000000"}) == 1790000000.0
    monkeypatch.setenv("WENART_DEADLINE", "soon")
    assert main(["run", "--project-out", "/nowhere"]) == 2


# --------------------------------------------------------------------------
# Determinism, debug images, expected fallback
# --------------------------------------------------------------------------

def test_determinism_json(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a", "cam_c"))
    deps, backend, gate = make_deps()
    run_polish(out, "run", deps=deps, cfg=cfg_with(determinism_view="cam_c"))
    det = json.loads((out / "polish" / DETERMINISM_NAME).read_text(encoding="utf-8"))
    assert validate_determinism(det) == [] and det["camera"] == "cam_c" and det["max_abs_diff"] == 0
    assert det["settings"]["seed"] == 1 and det["settings"]["strength"] == 0.375 and len(det["seconds_each"]) == 2
    calls = len(backend.calls)
    deps, backend2, _ = make_deps()
    run_polish(out, "run", deps=deps, cfg=cfg_with(determinism_view="cam_c"))
    assert backend2.calls == []                                          # same key: kept
    deps, noisy, _ = make_deps(backend=FakeBackend(noise=3))
    run_polish(out, "run", deps=deps, cfg=cfg_with(determinism_view="cam_c"), force=True)
    det = json.loads((out / "polish" / DETERMINISM_NAME).read_text(encoding="utf-8"))
    assert det["max_abs_diff"] == 3 and calls > 0


def test_missing_debug_writer_and_expected_fallback_are_warned(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))
    deps, backend, gate = make_deps(writer=None, expected=FakeExpected(fail=True))
    m = run_polish(out, "run", deps=deps)
    a = view_of(m, "cam_a")
    assert a["attempts"][0]["debug_jpg"] is None and not (out / "polish" / "cam_a_a1_gate.jpg").exists()
    assert any("write_debug" in w for w in m["warnings"])
    assert any("expected_view unavailable" in w for w in m["warnings"])
    assert a["expected_source"] == "index_pass" and "sofa" in a["prompt"] and "armchair" not in a["prompt"]
    assert validate_manifest(m) == []


def test_find_gate_debug_writer_uses_the_gates_write_debug(tmp_path):
    assert find_gate_debug_writer(FakeGate()) is None                    # no write_debug: no images

    class GateWithDebug(FakeGate):
        def write_debug(self, ref, test_rgb, result, path):
            return debug_writer(ref, test_rgb, result, path)

    out = make_project(tmp_path, cameras=("cam_a",))
    gate = GateWithDebug()
    deps, backend, _ = make_deps(gate=gate, writer=None)
    deps.find_debug_writer = True
    m = run_polish(out, "run", deps=deps)
    a = view_of(m, "cam_a")
    assert a["attempts"][0]["debug_jpg"] == "cam_a_a1_gate.jpg"
    assert (out / "polish" / "cam_a_a1_gate.jpg").is_file()
    assert not any("write_debug" in w for w in m["warnings"])

    from wenart.gate import Gate
    assert callable(find_gate_debug_writer(Gate(thresholds={})))      # the real gate provides one


# --------------------------------------------------------------------------
# Sweep and smoke
# --------------------------------------------------------------------------

def test_sweep_runs_every_setting_on_the_auto_views(tmp_path):
    out = make_project(tmp_path)
    cfg = cfg_with(grids={"sweep": [
        {"role": "grid", "strength": 0.25, "control": "depth", "scale": 0.8, "size": "native", "mode": "plain"},
        {"role": "grid", "strength": 0.25, "control": "canny", "scale": 0.8, "size": "native", "mode": "plain"},
        {"role": "grid", "strength": 0.375, "control": "geometry", "scale": 0.8, "size": "native", "mode": "plain"},
        {"role": "grid", "strength": 0.375, "control": "depth", "scale": 0.8, "size": "64x32", "mode": "plain"},
        {"role": "grid", "strength": 0.375, "control": "depth", "scale": 0.8, "size": "native", "mode": "anchor"},
        {"role": "presumed_bad", "strength": 0.75, "control": None, "scale": None, "size": "native",
         "mode": "plain"}]})
    gate = FakeGate({"default": [0, 25]})
    deps, backend, gate = make_deps(gate=gate)
    m = run_polish(out, "sweep", deps=deps, cfg=cfg)
    assert validate_manifest(m) == [] and m["kind"] == "sweep"
    assert [v["camera"] for v in m["views"]] == ["cam_c", "cam_a"]                 # the order of sweep_views
    for v in m["views"]:
        assert [r["k"] for r in v["attempts"]] == [1, 2, 3, 4, 5, 6]               # no early stop
        assert v["final"] is None and v["accepted"] == [1, 2, 3, 4, 5]             # 0.75 * 40 ~ 28.6 > 25
        assert v["source_png"] == "../../renders/" + v["camera"] + ".png"
        assert set(v["controls"]) == {"depth", "canny", "geometry"}
        assert v["attempts"][5]["role"] == "presumed_bad" and v["attempts"][5]["control"] is None
    sweep = out / "polish" / "sweep"
    assert (sweep / "cam_c_a6.png").is_file() and (sweep / "cam_c_a6_preview.jpg").is_file()
    assert not (out / "polish" / MANIFEST_NAME).exists() and not (sweep / DETERMINISM_NAME).exists()
    shapes = [c["shape"] for c in backend.calls]
    assert (32, 64, 3) in shapes and (48, 64, 3) in shapes
    modes = {(c["mode"], c["control"] is None) for c in backend.calls}
    assert ("anchor", False) in modes and ("plain", True) in modes
    assert [c["seed"] for c in backend.calls[:6]] == [1, 2, 3, 4, 5, 6]
    report = (sweep / REPORT_NAME).read_text(encoding="utf-8")
    assert "## Settings" in report and "| a6 | presumed_bad |" in report
    assert summary(m).startswith("sweep toy: 2 views, 12 attempts")


def test_smoke_cli_with_named_views(tmp_path):
    out = make_project(tmp_path)
    deps, backend, gate = make_deps()
    assert main(["smoke", "--project-out", str(out), "--views", "cam_b"], deps=deps) == 0
    m = json.loads((out / "polish" / "smoke" / MANIFEST_NAME).read_text(encoding="utf-8"))
    assert m["kind"] == "smoke" and [v["camera"] for v in m["views"]] == ["cam_b"]
    assert [(r["strength"], r["control"]) for r in m["views"][0]["attempts"]] == [
        (0.25, "depth"), (0.375, "depth"), (0.375, "canny"), (0.375, "geometry")]
    assert validate_manifest(m) == []


def test_auto_views_need_the_expected_module(tmp_path):
    out = make_project(tmp_path)
    deps, backend, gate = make_deps(expected=FakeExpected(fail=True))
    with pytest.raises(PolishError):
        run_polish(out, "sweep", deps=deps)
    assert main(["sweep", "--project-out", str(out)], deps=deps) == 2


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def test_cli_run_report_and_errors(tmp_path, capsys):
    out = make_project(tmp_path)
    deps, backend, gate = make_deps()
    assert main(["run", "--project-out", str(out), "--views", "cam_a,cam_c"], deps=deps) == 0
    printed = capsys.readouterr().out
    assert "run toy: 2 views" in printed and "2 polished" in printed
    manifest = out / "polish" / MANIFEST_NAME
    (out / "polish" / REPORT_NAME).unlink()
    assert main(["report", str(manifest)]) == 0 and (out / "polish" / REPORT_NAME).is_file()
    assert main(["run", "--project-out", str(out), "--views", "cam_zz"], deps=make_deps()[0]) == 2
    assert main(["run", "--project-out", str(tmp_path / "missing")], deps=make_deps()[0]) == 2
    bad = make_deps(backend=FakeBackend(fail_strengths={0.375, 0.25, 0.125}))[0]
    assert main(["run", "--project-out", str(out), "--views", "cam_a", "--force", "--out",
                 str(tmp_path / "alt")], deps=bad) == 1
    assert (tmp_path / "alt" / MANIFEST_NAME).is_file()
    grid = tmp_path / "grid.yaml"
    grid.write_text("- {strength: 0.3, control: nope, scale: 0.8}\n", encoding="utf-8")
    assert main(["sweep", "--project-out", str(out), "--views", "cam_a", "--grid", str(grid)],
                deps=make_deps()[0]) == 2


def test_polish_run_rejects_unknown_kind_and_previews(tmp_path):
    with pytest.raises(PolishError):
        PolishRun(tmp_path, "final", deps=make_deps()[0])
    with pytest.raises(PolishError):
        PolishRun(tmp_path, "run", deps=make_deps()[0], previews="some")


def test_preview_options(tmp_path):
    out = make_project(tmp_path, cameras=("cam_a",))
    gate = FakeGate({"default": [0, 12]})                    # a1 rejected, a2 accepted
    assert main(["run", "--project-out", str(out), "--previews", "all"], deps=make_deps(gate=gate)[0]) == 0
    pol = out / "polish"
    from PIL import Image
    with Image.open(pol / "cam_a_a2_preview.jpg") as img:
        assert img.size == (W, H)                            # the final attempt at full size
    assert (pol / "cam_a_a1_preview.jpg").is_file()          # the rejected attempt too
    assert main(["run", "--project-out", str(out)], deps=make_deps(gate=FakeGate({"default": [0, 12]}))[0]) == 0
    assert not (pol / "cam_a_a1_preview.jpg").exists() and (pol / "cam_a_a2_preview.jpg").is_file()
    (pol / "cam_a_a2_preview.jpg").unlink()
    assert main(["run", "--project-out", str(out), "--previews", "none"],
                deps=make_deps(gate=FakeGate({"default": [0, 12]}))[0]) == 0
    assert not list(pol.glob("*_preview.jpg"))
