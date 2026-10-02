"""CPU test of the Z-Image backend's plumbing with fake torch/diffusers/transformers (docs/milestone5.md §3.1, §3.2).

torch is not installed here, so ``wenart.polish.zimage`` is run against
stand-in modules. The fake pipelines' ``__call__`` signatures copy diffusers
0.40.0 (``ZImageControlNetPipeline``, ``ZImageControlNetInpaintPipeline``,
``ZImageImg2ImgPipeline``: keyword names and order, no ``**kwargs``), so a
misspelt keyword fails here instead of on the pod. What is checked:

- loading: text encoder first (bf16, ``device_map``), prompts encoded in
  batches with ``do_classifier_free_guidance=False`` and kept on the CPU, the
  encoder dropped before the transformer is loaded; every ``from_pretrained``
  with the pinned revision and subfolder; the ControlNet from the HF-cache
  file with the vendored ``config=``; the pipeline built as
  ``ZImageControlNetPipeline(scheduler, vae, None, tokenizer, transformer,
  controlnet)``;
- one polish: ``set_timesteps(sigmas=tail)`` before reading sigma0,
  latents = sigma0 * noise + (1 - sigma0) * x0 with the VAE mode, explicit
  height/width, ``prompt=None`` + ``prompt_embeds=[emb]``, guidance 0;
- anchor (inpaint, all-black mask) and presumed_bad (img2img with strength)
  through ``from_pipe(..., dtype=bfloat16)``;
- VAE tiling above 1.5 MP; one OOM retry with CPU offload when RAM allows.

The real numerics run on the pod (``tests/gpu/test_polish.py``).
"""
import sys
import types

import numpy as np
import pytest

from wenart.polish import config as PC
from wenart.polish import schedule as S
from wenart.polish import zimage as ZI


# --------------------------------------------------------------------------
# Fake torch
# --------------------------------------------------------------------------

class FT:
    """A numpy-backed stand-in for a torch tensor (only what zimage.py uses)."""

    def __init__(self, a, device="cpu", dtype="float32"):
        self.a = np.asarray(a, dtype=np.float64)
        self.device = device
        self.dtype = dtype

    @property
    def shape(self):
        return self.a.shape

    def to(self, *args, device=None, dtype=None):
        for arg in args:
            if isinstance(arg, str):
                device = arg
            else:
                dtype = arg
        return FT(self.a, device or self.device, dtype or self.dtype)

    def detach(self):
        return self

    def _v(self, other):
        return other.a if isinstance(other, FT) else other

    def __add__(self, o):
        return FT(self.a + self._v(o), self.device, self.dtype)

    __radd__ = __add__

    def __sub__(self, o):
        return FT(self.a - self._v(o), self.device, self.dtype)

    def __rsub__(self, o):
        return FT(self._v(o) - self.a, self.device, self.dtype)

    def __mul__(self, o):
        return FT(self.a * self._v(o), self.device, self.dtype)

    __rmul__ = __mul__


class OOM(RuntimeError):
    pass


class Generator:
    def __init__(self, device="cpu"):
        self.device_type = device
        self.seed = None

    def manual_seed(self, seed):
        self.seed = int(seed)
        return self


class NoGrad:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def fake_torch():
    t = types.ModuleType("torch")
    t.__version__ = "2.9.1+fake"
    t.bfloat16 = "bfloat16"
    t.float32 = "float32"
    t.Generator = Generator
    t.no_grad = NoGrad

    def randn(shape, generator=None, dtype=None):
        rng = np.random.default_rng(generator.seed)
        return FT(rng.standard_normal(shape), "cpu", dtype or "float32")

    t.randn = randn
    cuda = types.SimpleNamespace(is_available=lambda: False, OutOfMemoryError=OOM, empty_cache=lambda: None,
                                 synchronize=lambda: None, get_device_name=lambda i=0: "fake",
                                 max_memory_allocated=lambda: 0, max_memory_reserved=lambda: 0)
    t.cuda = cuda
    return t


# --------------------------------------------------------------------------
# Fake diffusers pieces
# --------------------------------------------------------------------------

LOG: dict = {}


class Config(dict):
    __getattr__ = dict.get


class FakeScheduler:
    def __init__(self):
        self.config = Config(shift=3.0)
        self.sigmas = None
        self.calls = []

    def set_timesteps(self, num_inference_steps=None, device=None, sigmas=None, mu=None, timesteps=None):
        self.calls.append({"sigmas": list(sigmas), "device": device})
        self.sigmas = S.scheduler_sigmas(sigmas, self.config.shift)


class FakeVAE:
    dtype = "bfloat16"

    def __init__(self):
        self.config = Config(shift_factor=0.1159, scaling_factor=0.3611)
        self.tiling = None
        self.device = "cpu"

    def to(self, device):
        self.device = device
        return self

    def enable_tiling(self):
        self.tiling = True

    def disable_tiling(self):
        self.tiling = False

    def encode(self, x):
        n, c, h, w = x.shape
        mode = FT(np.full((n, 16, h // 8, w // 8), 0.5), x.device, self.dtype)
        return types.SimpleNamespace(latent_dist=types.SimpleNamespace(mode=lambda: mode))


class FakeImageProcessor:
    def preprocess(self, image, height=None, width=None, resize_mode="default", crops_coords=None):
        assert (image.width, image.height) == (width, height)
        return FT(np.zeros((1, 3, height, width)))


def _result(height, width):
    return types.SimpleNamespace(images=np.full((1, height, width, 3), 0.5))


class FakePipeBase:
    _execution_device = "cuda"

    def __init__(self):
        self.scheduler = FakeScheduler()
        self.vae = FakeVAE()
        self.image_processor = FakeImageProcessor()
        self.calls = []
        self.offloaded = 0
        self.fail_next = 0

    def set_progress_bar_config(self, **kwargs):
        self.progress = kwargs

    def enable_model_cpu_offload(self, gpu_id=None, device=None):
        self.offloaded += 1

    def _record(self, kwargs):
        if self.fail_next:
            self.fail_next -= 1
            raise OOM("CUDA out of memory")
        self.calls.append(kwargs)
        return _result(kwargs["height"], kwargs["width"])


class FakeControlNetPipeline(FakePipeBase):
    """``ZImageControlNetPipeline`` of diffusers 0.40.0 (pipeline_z_image_controlnet.py)."""

    def __init__(self, scheduler, vae, text_encoder, tokenizer, transformer, controlnet):
        super().__init__()
        LOG["pipeline_init"] = (scheduler, vae, text_encoder, tokenizer, transformer, controlnet)
        self.scheduler, self.vae = scheduler, vae

    def __call__(self, prompt=None, height=None, width=None, num_inference_steps=50, sigmas=None,
                 guidance_scale=5.0, control_image=None, controlnet_conditioning_scale=0.75,
                 cfg_normalization=False, cfg_truncation=1.0, negative_prompt=None, num_images_per_prompt=1,
                 generator=None, latents=None, prompt_embeds=None, negative_prompt_embeds=None, output_type="pil",
                 return_dict=True, joint_attention_kwargs=None, callback_on_step_end=None,
                 callback_on_step_end_tensor_inputs=["latents"], max_sequence_length=512):
        kwargs = dict(locals())
        kwargs.pop("self")
        kwargs["pipeline"] = "controlnet"
        return self._record(kwargs)


class FakeInpaintPipeline(FakePipeBase):
    """``ZImageControlNetInpaintPipeline`` of diffusers 0.40.0 (pipeline_z_image_controlnet_inpaint.py)."""

    @classmethod
    def from_pipe(cls, pipeline, **kwargs):
        LOG.setdefault("from_pipe", []).append((cls.__name__, kwargs))
        p = cls()
        p.scheduler, p.vae = pipeline.scheduler, pipeline.vae
        return p

    def __call__(self, prompt=None, height=None, width=None, num_inference_steps=50, sigmas=None,
                 guidance_scale=5.0, image=None, mask_image=None, control_image=None,
                 controlnet_conditioning_scale=0.75, cfg_normalization=False, cfg_truncation=1.0,
                 negative_prompt=None, num_images_per_prompt=1, generator=None, latents=None, prompt_embeds=None,
                 negative_prompt_embeds=None, output_type="pil", return_dict=True, joint_attention_kwargs=None,
                 callback_on_step_end=None, callback_on_step_end_tensor_inputs=["latents"],
                 max_sequence_length=512):
        kwargs = dict(locals())
        kwargs.pop("self")
        kwargs["pipeline"] = "inpaint"
        return self._record(kwargs)


class FakeImg2ImgPipeline(FakePipeBase):
    """``ZImageImg2ImgPipeline`` of diffusers 0.40.0 (pipeline_z_image_img2img.py)."""

    @classmethod
    def from_pipe(cls, pipeline, **kwargs):
        LOG.setdefault("from_pipe", []).append((cls.__name__, kwargs))
        p = cls()
        p.scheduler, p.vae = pipeline.scheduler, pipeline.vae
        return p

    def __call__(self, prompt=None, image=None, strength=0.6, height=None, width=None, num_inference_steps=50,
                 sigmas=None, guidance_scale=5.0, cfg_normalization=False, cfg_truncation=1.0, negative_prompt=None,
                 num_images_per_prompt=1, generator=None, latents=None, prompt_embeds=None,
                 negative_prompt_embeds=None, output_type="pil", return_dict=True, joint_attention_kwargs=None,
                 callback_on_step_end=None, callback_on_step_end_tensor_inputs=["latents"], max_sequence_length=512):
        kwargs = dict(locals())
        kwargs.pop("self")
        kwargs["pipeline"] = "img2img"
        return self._record(kwargs)


class FakeShell:
    """``ZImagePipeline`` used only for ``encode_prompt`` (pipeline_z_image.py)."""

    def __init__(self, scheduler, vae, text_encoder, tokenizer, transformer):
        LOG["shell_init"] = dict(scheduler=scheduler, vae=vae, text_encoder=text_encoder, tokenizer=tokenizer,
                                 transformer=transformer)

    def encode_prompt(self, prompt, device=None, do_classifier_free_guidance=True, negative_prompt=None,
                      prompt_embeds=None, negative_prompt_embeds=None, max_sequence_length=512):
        LOG.setdefault("encode", []).append({"n": len(prompt), "device": device,
                                             "cfg": do_classifier_free_guidance})
        out = [FT(np.full((len(p), 4), float(len(p))), device, "bfloat16") for p in prompt]
        prompt[:] = ["<chat>" + p for p in prompt]           # diffusers rewrites the list in place
        return out, []


def loader(name):
    class M:
        @classmethod
        def from_pretrained(cls, repo, **kwargs):
            LOG.setdefault("from_pretrained", []).append((name, repo, kwargs))
            return FakeVAE() if name == "vae" else (FakeScheduler() if name == "scheduler" else
                                                    types.SimpleNamespace(name=name, to=lambda d: d))

        @classmethod
        def from_single_file(cls, path, **kwargs):
            LOG["single_file"] = (path, kwargs)
            return types.SimpleNamespace(name="controlnet", to=lambda d: ("controlnet on", d))
    M.__name__ = name
    return M


@pytest.fixture
def fakes(monkeypatch):
    LOG.clear()
    torch = fake_torch()
    diffusers = types.ModuleType("diffusers")
    diffusers.__version__ = "0.40.0"
    diffusers.ZImagePipeline = FakeShell
    diffusers.ZImageControlNetPipeline = FakeControlNetPipeline
    diffusers.ZImageControlNetInpaintPipeline = FakeInpaintPipeline
    diffusers.ZImageImg2ImgPipeline = FakeImg2ImgPipeline
    diffusers.ZImageTransformer2DModel = loader("transformer")
    diffusers.ZImageControlNetModel = loader("controlnet")
    diffusers.AutoencoderKL = loader("vae")
    diffusers.FlowMatchEulerDiscreteScheduler = loader("scheduler")
    cn_mod = types.ModuleType("diffusers.pipelines.z_image.pipeline_z_image_controlnet")
    cn_mod.get_default_z_image_sigmas = S.default_sigmas

    def retrieve_latents(encoder_output, generator=None, sample_mode="sample"):
        assert sample_mode == "argmax"
        return encoder_output.latent_dist.mode()

    cn_mod.retrieve_latents = retrieve_latents
    transformers = types.ModuleType("transformers")
    transformers.AutoTokenizer = loader("tokenizer")
    transformers.Qwen3Model = loader("text_encoder")
    hub = types.ModuleType("huggingface_hub")

    def hf_hub_download(repo_id, filename, *, revision=None, **kwargs):
        LOG["download"] = (repo_id, filename, revision)
        return f"/opt/wenart/hf/{filename}"

    hub.hf_hub_download = hf_hub_download
    for name, mod in (("torch", torch), ("diffusers", diffusers), ("transformers", transformers),
                      ("huggingface_hub", hub), ("diffusers.pipelines", types.ModuleType("diffusers.pipelines")),
                      ("diffusers.pipelines.z_image", types.ModuleType("diffusers.pipelines.z_image")),
                      ("diffusers.pipelines.z_image.pipeline_z_image_controlnet", cn_mod)):
        monkeypatch.setitem(sys.modules, name, mod)
    return torch


def ready_backend():
    backend = ZI.ZImageBackend(PC.load_config(), device="cuda")
    backend.ensure_ready(["prompt one", "prompt two", "prompt one"])
    return backend


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

def test_loading_follows_the_memory_plan(fakes):
    cfg = PC.load_config()
    base, cn = cfg["models"]["base"], cfg["models"]["controlnet"]
    backend = ready_backend()
    loads = LOG["from_pretrained"]
    names = [n for n, _, _ in loads]
    assert names == ["tokenizer", "text_encoder", "transformer", "vae", "scheduler"]   # encoder first
    for name, repo, kwargs in loads:
        assert repo == base["repo"] and kwargs["revision"] == base["revision"]
        assert kwargs["subfolder"] == name
    kw = {n: k for n, _, k in loads}
    assert kw["text_encoder"]["dtype"] == "bfloat16" and kw["text_encoder"]["device_map"] == "cuda"
    assert kw["transformer"]["dtype"] == "bfloat16" and kw["transformer"]["device_map"] == "cuda"
    assert kw["vae"]["dtype"] == "bfloat16"
    assert LOG["download"] == (cn["repo"], cn["files"][0], cn["revision"])
    path, single = LOG["single_file"]
    assert path.endswith(cn["files"][0]) and single == {"config": str(PC.config_dir(cfg)), "dtype": "bfloat16"}
    scheduler, vae, text_encoder, tokenizer, transformer, controlnet = LOG["pipeline_init"]
    assert text_encoder is None and controlnet == ("controlnet on", "cuda") and transformer.name == "transformer"
    assert tokenizer.name == "tokenizer" and isinstance(vae, FakeVAE)
    shell = LOG["shell_init"]
    assert shell["transformer"] is None and shell["vae"] is None and shell["text_encoder"].name == "text_encoder"
    assert LOG["encode"] == [{"n": 2, "device": "cuda", "cfg": False}]      # deduplicated, no CFG
    assert set(backend.embeddings) == {"prompt one", "prompt two"}             # the caller's texts, not chat text
    assert all(e.device == "cpu" for e in backend.embeddings.values())
    assert backend.pipe.progress == {"disable": True} and backend.memory_mode == "resident"
    assert not any(isinstance(v, types.SimpleNamespace) and getattr(v, "name", "") == "text_encoder"
                   for v in vars(backend).values())                         # the encoder was dropped
    backend.ensure_ready(["prompt two"])                                       # no second load
    with pytest.raises(RuntimeError):
        backend.ensure_ready(["a new prompt"])
    assert backend.versions() == {"torch": "2.9.1+fake", "diffusers": "0.40.0", "device": "cpu"}


def test_prompts_are_encoded_in_batches_of_8(fakes):
    backend = ZI.ZImageBackend(PC.load_config())
    backend.ensure_ready([f"prompt {i}" for i in range(19)])
    assert [e["n"] for e in LOG["encode"]] == [8, 8, 3]


def test_plain_polish_call(fakes):
    backend = ready_backend()
    img = np.full((48, 64, 3), 100, np.uint8)
    ctrl = np.full((48, 64, 3), 200, np.uint8)
    out, meta = backend.generate(img, ctrl, strength=0.375, scale=0.8, mode="plain", seed=7, steps=8,
                                 prompt="prompt one")
    assert out.shape == (48, 64, 3) and out.dtype == np.uint8 and (out == 128).all()
    pipe = backend.pipe
    assert pipe.scheduler.calls[0]["sigmas"] == [0.375, 0.25, 0.125]          # set_timesteps(sigmas=tail) first
    call = pipe.calls[0]
    assert call["prompt"] is None and call["prompt_embeds"][0].device == "cuda"
    assert call["prompt_embeds"][0].a is not None and len(call["prompt_embeds"]) == 1
    assert (call["height"], call["width"]) == (48, 64) and call["guidance_scale"] == 0.0
    assert call["sigmas"] == [0.375, 0.25, 0.125] and call["num_inference_steps"] == 3
    assert call["controlnet_conditioning_scale"] == 0.8 and call["output_type"] == "np"
    assert call["control_image"].size == (64, 48) and call["generator"].seed == 7
    # latents = sigma0 * noise + (1 - sigma0) * x0, x0 = (VAE mode - shift) * scale, noise from the CPU generator.
    s0 = S.sigma0([0.375])
    x0 = (0.5 - 0.1159) * 0.3611
    noise = np.random.default_rng(7).standard_normal((1, 16, 6, 8))
    assert call["latents"].shape == (1, 16, 6, 8) and call["latents"].device == "cuda"
    assert np.allclose(call["latents"].a, s0 * noise + (1 - s0) * x0)
    assert meta["pipeline"] == "controlnet" and meta["forwards"] == 3
    assert meta["sigma0"] == pytest.approx(0.642857, abs=1e-6) and meta["sigma0_numpy"] == meta["sigma0"]
    assert backend.pipe.vae.tiling is False                                   # small image: no tiling
    assert backend.stats()["forwards"] == 3


def test_anchor_and_presumed_bad_use_from_pipe_in_bf16(fakes):
    backend = ready_backend()
    img = np.full((48, 64, 3), 100, np.uint8)
    _, meta = backend.generate(img, img, strength=0.375, scale=0.8, mode="anchor", seed=1, steps=8,
                               prompt="prompt one")
    inpaint = backend._derived["anchor"]
    call = inpaint.calls[0]
    assert meta["pipeline"] == "controlnet_inpaint" and call["image"].size == (64, 48)
    mask = np.asarray(call["mask_image"])
    assert call["mask_image"].mode == "L" and mask.shape == (48, 64) and mask.max() == 0      # black = keep
    assert call["sigmas"] == [0.375, 0.25, 0.125] and call["latents"] is not None
    _, meta = backend.generate(img, None, strength=0.75, scale=None, mode="plain", seed=2, steps=8,
                               prompt="prompt two")
    img2img = backend._derived["img2img"]
    call = img2img.calls[0]
    assert meta["pipeline"] == "img2img" and meta["forwards"] == 6 and meta["sigma0_numpy"] == pytest.approx(0.9)
    assert call["strength"] == 0.75 and call["num_inference_steps"] == 8 and call["latents"] is None
    assert call["image"].size == (64, 48) and (call["height"], call["width"]) == (48, 64)
    assert LOG["from_pipe"] == [("FakeInpaintPipeline", {"dtype": "bfloat16"}),
                                ("FakeImg2ImgPipeline", {"dtype": "bfloat16"})]
    backend.generate(img, img, strength=0.25, scale=0.8, mode="anchor", seed=3, steps=8, prompt="prompt one")
    assert len(LOG["from_pipe"]) == 2                                          # derived pipelines are kept


def test_vae_tiling_above_1_5_megapixels(fakes):
    backend = ready_backend()
    big = np.zeros((1088, 1920, 3), np.uint8)
    backend.generate(big, big, strength=0.125, scale=0.8, mode="plain", seed=0, steps=8, prompt="prompt one")
    assert backend.pipe.vae.tiling is True


def test_oom_retries_once_with_cpu_offload(fakes, monkeypatch):
    backend = ready_backend()
    img = np.zeros((48, 64, 3), np.uint8)
    monkeypatch.setattr(ZI, "mem_available_gb", lambda path="/proc/meminfo": 64.0)
    backend.pipe.fail_next = 1
    out, _ = backend.generate(img, img, strength=0.25, scale=0.8, mode="plain", seed=0, steps=8,
                              prompt="prompt one")
    assert backend.memory_mode == "offload" and backend.pipe.offloaded == 1 and out.shape == (48, 64, 3)
    assert backend.stats()["memory_mode"] == "offload"
    # Offload mode: a derived pipeline gets its own offload hooks before it runs.
    backend.generate(img, img, strength=0.25, scale=0.8, mode="anchor", seed=0, steps=8, prompt="prompt one")
    assert backend._derived["anchor"].offloaded == 1
    # A second OOM, or one without enough RAM, is raised.
    backend.pipe.fail_next = 1
    with pytest.raises(OOM):
        backend.generate(img, img, strength=0.25, scale=0.8, mode="plain", seed=0, steps=8, prompt="prompt one")
    other = ready_backend()
    monkeypatch.setattr(ZI, "mem_available_gb", lambda path="/proc/meminfo": 20.0)
    other.pipe.fail_next = 1
    with pytest.raises(OOM):
        other.generate(img, img, strength=0.25, scale=0.8, mode="plain", seed=0, steps=8, prompt="prompt one")
    assert other.memory_mode == "resident"


def test_generate_needs_ensure_ready_and_known_prompts(fakes):
    backend = ZI.ZImageBackend(PC.load_config())
    img = np.zeros((48, 64, 3), np.uint8)
    with pytest.raises(RuntimeError):
        backend.generate(img, img, strength=0.25, scale=0.8, mode="plain", seed=0, steps=8, prompt="x")
    backend = ready_backend()
    with pytest.raises(RuntimeError):
        backend.generate(img, img, strength=0.25, scale=0.8, mode="plain", seed=0, steps=8, prompt="unknown")
