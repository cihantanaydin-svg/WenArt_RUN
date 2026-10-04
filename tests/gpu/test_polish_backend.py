"""GPU test of the Z-Image backend's CUDA OOM retry (docs/milestone5.md §3.1, review of 2 Oct 2026).

Run on the pod with the polish venv once the pinned models are in the HF cache:
``/opt/wenart/venv-polish/bin/python -m pytest -m gpu tests/gpu/test_polish_backend.py``. It loads the
polish models once (about 20 GiB of VRAM, 20-40 s) and polishes 512x512 images, so it must not run while
another process holds the GPU. What it checks:

- the first call fills the free VRAM with a tensor that only its own frame holds and then raises
  ``torch.cuda.OutOfMemoryError``: the retry must succeed, which it can only do when it runs after the
  failed call's frames were released (a retry inside the ``except`` block would run out of memory);
- the retry is the same polish (same seed: same image within the determinism limit of 2 grey levels),
  ``memory_mode`` stays ``resident``, ``oom_retries`` is 1, the release hook ran once, and no accelerate
  offload hook sits on the transformer, the ControlNet or the VAE (the old ``enable_model_cpu_offload``
  fallback left the transformer blocks on the CPU and broke every later ControlNet call);
- ControlNet (plain), anchor (inpaint) and img2img polishes still work after the retry.
"""
import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("diffusers")

pytestmark = [pytest.mark.gpu,
              pytest.mark.skipif(not torch.cuda.is_available(), reason="needs a CUDA device")]

PROMPT = "Photorealistic interior photograph of a living room in Scandinavian style."
SIZE = 512
HEADROOM_BYTES = 16 * 2 ** 20          # what the filler leaves free: far less than one 512x512 polish needs
MAX_DIFF = 2


@pytest.fixture(scope="module")
def backend():
    from wenart.polish.config import load_config
    from wenart.polish.zimage import ZImageBackend
    b = ZImageBackend(load_config(), device="cuda")
    b.ensure_ready([PROMPT])
    yield b
    b.pipe = None
    b._derived.clear()
    b.free_cache()


def _images():
    rng = np.random.default_rng(0)
    img = rng.integers(0, 256, (SIZE, SIZE, 3), dtype=np.uint8)
    ctl = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    ctl[:, SIZE // 2:] = 255
    return img, ctl


def _fill_vram():
    """A uint8 CUDA tensor over all but ``HEADROOM_BYTES`` of the free memory."""
    torch.cuda.empty_cache()
    free, _total = torch.cuda.mem_get_info()
    size = free - HEADROOM_BYTES
    for _ in range(8):
        try:
            return torch.empty(max(size, 1), dtype=torch.uint8, device="cuda")
        except torch.cuda.OutOfMemoryError:
            size -= 64 * 2 ** 20
    pytest.fail("could not allocate the VRAM filler")


def test_cuda_oom_is_retried_resident_after_the_failed_call_is_released(backend):
    img, ctl = _images()
    kw = dict(strength=0.25, scale=0.8, mode="plain", seed=1, steps=8, prompt=PROMPT)
    reference, _ = backend.generate(img, ctl, **kw)
    released = []
    backend.release_hook = lambda: released.append(True)
    real = backend._generate
    calls = {"n": 0}

    def fails_first_with_the_vram_full(*args):
        calls["n"] += 1
        if calls["n"] == 1:
            filler = _fill_vram()          # held only by this frame (and so by the OOM's traceback)
            raise torch.cuda.OutOfMemoryError(f"forced OOM with {filler.numel() / 2 ** 30:.1f} GiB held")
        return real(*args)

    backend._generate = fails_first_with_the_vram_full
    try:
        out, meta = backend.generate(img, ctl, **kw)
    finally:
        backend._generate = real
        backend.release_hook = None
    assert calls["n"] == 2 and released == [True]
    assert out.shape == (SIZE, SIZE, 3) and meta["pipeline"] == "controlnet"
    assert int(np.abs(out.astype(np.int16) - reference.astype(np.int16)).max()) <= MAX_DIFF
    stats = backend.stats()
    assert stats["memory_mode"] == "resident" and stats["oom_retries"] == 1
    pipe = backend.pipe
    for name in ("transformer", "controlnet", "vae"):
        assert not hasattr(getattr(pipe, name), "_hf_hook"), f"{name} carries an accelerate offload hook"
    devices = {p.device.type for m in (pipe.transformer, pipe.controlnet, pipe.vae) for p in m.parameters()}
    assert devices == {"cuda"}


def test_every_pipeline_works_after_the_retry(backend):
    img, ctl = _images()
    for control, mode, strength, pipeline in ((ctl, "plain", 0.375, "controlnet"),
                                              (ctl, "anchor", 0.375, "controlnet_inpaint"),
                                              (None, "plain", 0.75, "img2img")):
        out, meta = backend.generate(img, control, strength=strength, scale=0.8 if control is not None else None,
                                     mode=mode, seed=2, steps=8, prompt=PROMPT)
        assert out.shape == (SIZE, SIZE, 3) and out.dtype == np.uint8 and meta["pipeline"] == pipeline
        assert 0 < int(out.std())                         # an image, not a constant
