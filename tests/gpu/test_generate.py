"""GPU test of the generated-furniture step (docs/milestone8.md §3, §7; wenart/assets/generate.py).

Run on the pod in venv-trellis after scripts/pod_setup_trellis.sh (which writes setup_trellis.json and the models
into HF_HOME): ``/opt/wenart/venv-trellis/bin/python -m pytest -m gpu tests/gpu/test_generate.py`` with
``HF_HUB_OFFLINE=1``. It needs the GPU alone: Z-Image-Turbo (about 21 GB) and TRELLIS.2 (about 16 GB resident) are
loaded one after the other. What it checks:

- ``setup_trellis.json`` (``$WENART_RESULTS``, else ``/workspace/logs``) says ``status: ok``: the pinned TRELLIS.2
  commit, an attention backend that passed its GPU check, every model of generate.yaml downloaded, the pinned
  ``pipeline.json`` with the names the code checks; ``trellis_env.json`` of the venv names the same backend;
- one pair end to end through ``wenart.assets.generate.run``: Z-Image-Turbo renders the 1024 x 1024 image, TRELLIS.2
  loads (the DINOv3 and BiRefNet shims in place) and exports a textured GLB with more than 1000 faces; the survey
  record has the generated fields;
- a canned image (a chair drawn with PIL on white, no alpha: TRELLIS.2's background remover runs) gives a textured
  GLB with more than 1000 faces inside the unit box TRELLIS.2 generates in.

The PNGs and a short summary go to ``$WENART_RESULTS/generate_gpu_test/`` when ``WENART_RESULTS`` is set (no GLBs).
"""
import json
import os
import shutil
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("diffusers")

from wenart.assets import generate as G  # noqa: E402
from wenart.assets import objaverse as OV  # noqa: E402

pytestmark = [pytest.mark.gpu, pytest.mark.skipif(not torch.cuda.is_available(), reason="needs a CUDA device")]
CFG = G.load_config()
RESULTS = os.environ.get("WENART_RESULTS")
LOGS = Path(os.environ.get("WENART_LOGS", "/workspace/logs"))
MIN_FACES = 1000


def keep(path: Path, name: str) -> None:
    if RESULTS:
        out = Path(RESULTS) / "generate_gpu_test"
        out.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, out / name)


def setup_doc() -> dict:
    for path in ([Path(RESULTS) / "setup_trellis.json"] if RESULTS else []) + [LOGS / "setup_trellis.json"]:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    pytest.fail("setup_trellis.json not found: run scripts/pod_setup_trellis.sh first")


class LazyTrellis:
    """One TRELLIS.2 backend for the module, loaded on first use (after Z-Image-Turbo was freed)."""

    def __init__(self):
        self.backend = None

    def __call__(self, cfg):              # the run's factory
        return self

    def load(self):
        if self.backend is None:
            self.backend = G.TrellisImageTo3D(CFG)
            self.backend.load()

    def image_to_glb(self, image_path, glb_path, seed):
        return self.backend.image_to_glb(image_path, glb_path, seed)

    def versions(self):
        return self.backend.versions()

    def free(self):
        self.backend.free()

    def close(self):                      # kept for the next test
        pass


@pytest.fixture(scope="module")
def trellis():
    lazy = LazyTrellis()
    yield lazy
    if lazy.backend is not None:
        lazy.backend.close()


def check_glb(path: Path) -> dict:
    info = OV.glb_info(path)
    faces = G.glb_face_count(path)
    assert faces > MIN_FACES, f"{path.name}: {faces} faces"
    assert info["textured"] and info["images"] >= 1, info
    return {"faces": faces, **info}


def test_setup_trellis_status_ok():
    doc = setup_doc()
    assert doc["status"] == "ok", doc.get("reason")
    assert doc["trellis"]["commit"] == CFG["trellis_code"]["commit"]
    assert doc["attn_backend"] in ("flash_attn", "xformers")
    assert {m["key"] for m in doc["models"]} == set(CFG["models"]) and all(m["ok"] for m in doc["models"])
    assert doc["versions"]["attn_backend"] == doc["attn_backend"]
    assert doc["versions"]["pipeline_json"] == "names as checked"
    for name in ("nvdiffrast", "cumesh", "flex_gemm", "o_voxel"):
        assert doc["extensions"][name]["state"] == "ok", name
    assert G.trellis_env().get("ATTN_BACKEND") == doc["attn_backend"]


def test_one_pair_end_to_end(tmp_path, trellis):
    empty = tmp_path / "accepted.json"
    empty.write_text(json.dumps({"accepted": []}), encoding="utf-8")
    out = tmp_path / "lib"
    G.make_plan([empty], ["scandinavian"], out, CFG, types=["chair"], images_per_pair=1)
    code = G.run(out, out / "generate" / "plan.json", cfg=CFG, image_backend=G.ZImageText2Image,
                 mesh_backend=trellis)
    survey = json.loads((out / G.SURVEY_NAME).read_text(encoding="utf-8"))
    assert code == 0, survey.get("errors") or survey.get("refused")
    assert len(survey["candidates"]) == 1
    cand = survey["candidates"][0]
    from PIL import Image
    png = out / cand["generation"]["image"]
    with Image.open(png) as im:
        assert im.size == (CFG["image"]["size"], CFG["image"]["size"]) and im.mode == "RGB"
        pixels = np.asarray(im)
    assert pixels.std() > 5, "the image is flat"
    corners = np.concatenate([pixels[:16, :16].reshape(-1, 3), pixels[-16:, -16:].reshape(-1, 3)])
    assert corners.mean() > 180, "the background is not white (prompt: plain white background)"
    stats = check_glb(Path(cand["glb"]))
    assert cand["face_count"] == stats["faces"] and cand["source"] == "generated"
    assert cand["generated"]["revision"] == CFG["models"]["trellis"]["revision"]
    from trellis2.modules import image_feature_extractor as IFE
    assert IFE.DinoV3FeatureExtractor.extract_features is G._dinov3_extract_features
    assert next(trellis.backend.pipe.rembg_model.model.parameters()).dtype == torch.float32
    keep(png, "chair_scandinavian_1.png")
    if RESULTS:
        meta = json.loads((out / "generate" / "chair__scandinavian" / "model_1.json").read_text(encoding="utf-8"))
        summary = {"candidate": {k: cand[k] for k in ("uid", "face_count", "glb_bytes", "glb_info")},
                   "backend": meta.get("backend"), "versions": meta.get("versions"), "seconds": meta.get("seconds")}
        (Path(RESULTS) / "generate_gpu_test" / "summary.json").write_text(json.dumps(summary, indent=1))


def canned_chair(path: Path) -> Path:
    """A wooden chair in three-quarter view, drawn with flat shading on a white 1024 x 1024 RGB image."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (1024, 1024), (255, 255, 255))
    d = ImageDraw.Draw(img)
    wood, dark, light = (150, 100, 60), (110, 70, 40), (185, 135, 90)
    for x0, y0, x1, y1 in ((330, 560, 360, 840), (560, 600, 590, 880), (450, 520, 475, 760), (660, 550, 685, 790)):
        d.rectangle((x0, y0, x1, y1), fill=dark)                                  # legs
    d.polygon([(320, 560), (600, 600), (700, 540), (440, 510)], fill=light)       # seat top
    d.polygon([(320, 560), (600, 600), (600, 630), (320, 590)], fill=wood)        # seat front edge
    d.polygon([(600, 600), (700, 540), (700, 570), (600, 630)], fill=dark)        # seat side edge
    d.polygon([(440, 510), (700, 540), (700, 230), (450, 200)], fill=wood)        # back rest
    d.polygon([(450, 200), (700, 230), (700, 260), (450, 230)], fill=light)       # top rail
    img.save(path)
    return path


def test_canned_image_to_textured_glb(tmp_path, trellis):
    trellis.load()
    image = canned_chair(tmp_path / "chair.png")
    glb = tmp_path / "chair.glb"
    meta = trellis.image_to_glb(image, glb, seed=1)
    stats = check_glb(glb)
    import trimesh
    mesh = trimesh.load(glb, force="mesh")
    lo, hi = mesh.bounds
    assert np.all(lo >= -0.6) and np.all(hi <= 0.6), (lo, hi)
    assert meta["raw_faces"] > MIN_FACES and meta["peak_vram_gib"] > 0
    keep(image, "canned_chair.png")
    print(f"canned chair: {stats['faces']} faces, {glb.stat().st_size / 1e6:.1f} MB, {meta}")
