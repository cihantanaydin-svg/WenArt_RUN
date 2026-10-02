"""Z-Image-Turbo + Fun ControlNet Union 2.1 backend of the polish (docs/milestone5.md §3.1, §3.2).

What: the only module that touches torch, transformers and diffusers (all
imported inside the methods, so ``wenart.polish`` imports on a CPU machine).
The runner talks to it through the backend interface below; the CPU tests use
a fake with the same interface.

Backend interface (``wenart.polish.runner`` uses only this):

- ``versions() -> {"torch", "diffusers", "device"}`` (part of every attempt key);
- ``ensure_ready(prompts)``: encode every prompt of the run, then load the
  diffusion models (called once, before the first generation; nothing is
  loaded when every attempt is reused);
- ``generate(image, control, *, strength, scale, mode, seed, steps, prompt)
  -> (uint8 H x W x 3 at the model size, meta)``: one polish; ``control``
  None = the ``presumed_bad`` img2img control without ControlNet; ``meta`` =
  ``{"pipeline", "forwards", "sigma0", "sigma0_numpy", "seconds"}``;
- ``free_cache()``: release cached GPU memory before a gate call (§1.3);
- ``release_hook``: attribute, None or a callable the backend calls after a
  CUDA OOM, before its retry (the runner sets it to move the gate's models
  off the GPU);
- ``stats() -> {"memory_mode", "peak_vram_gib", "peak_reserved_gib",
  "load_seconds", "encode_seconds", "seconds_per_forward", "forwards",
  "oom_retries"}``.

Memory plan (§3.1, no CPU offload; it would move ~19 GB per call):

1. Prompts first: tokenizer + text encoder (``Qwen3Model``, bf16, cuda) in a
   ``ZImagePipeline`` shell with no transformer/VAE; ``encode_prompt(prompts,
   device="cuda", do_classifier_free_guidance=False)`` in batches of 8 under
   ``torch.no_grad()`` (``encode_prompt`` itself has no no_grad); the
   embeddings (a list of [tokens, 2560] tensors, one per prompt) are kept on
   the CPU; the encoder is deleted, ``gc.collect()``,
   ``torch.cuda.empty_cache()``.
2. ``ZImageTransformer2DModel.from_pretrained(subfolder="transformer",
   dtype=bf16, device_map="cuda")`` (the repo's FP32 shards are cast per
   tensor while loading), ``ZImageControlNetModel.from_single_file(<file in
   the HF cache>, config=<vendored config dir>, dtype=bf16).to("cuda")``,
   ``AutoencoderKL`` (bf16, cuda; ``enable_tiling()`` above 1.5 MP),
   ``FlowMatchEulerDiscreteScheduler`` from the repo, all from the local
   folder of the pinned snapshot (``wenart.hfcache.local_snapshot``: no hub
   lookups, so ``HF_HUB_OFFLINE=1`` works); ``ZImageControlNetPipeline(scheduler, vae, None, tokenizer,
   transformer, controlnet)`` (its ``__init__`` shares the transformer's
   embedders with the ControlNet via ``ZImageControlNetModel.from_transformer``).
3. ``PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`` (set before torch is
   imported unless the job set it). On a CUDA OOM: one retry, still
   resident, after the ``except`` block (so the failed call's frames and the
   CUDA tensors they hold are released first), the ``release_hook`` and
   ``gc.collect()`` + ``torch.cuda.empty_cache()``; counted in
   ``oom_retries``. A retry that runs out of memory again is raised, and
   later OOMs of the run are raised at once. No accelerate
   ``enable_model_cpu_offload()``: ``from_transformer`` makes the ControlNet
   share the transformer's embedders, refiners and first parameter
   (``x_pad_token``), so the transformer's offload hook sees that parameter
   already on cuda and leaves its blocks on the CPU (every later ControlNet
   call fails with a device mismatch); with the text encoder gone the hooks
   would also keep transformer and ControlNet resident together for the
   whole loop, so offload saves nothing. ``memory_mode`` is always
   ``resident``.

img2img with one control image (§3.2; diffusers 0.40.0 has no pipeline that
takes both ``strength`` and ``control_image``):

- ``full = get_default_z_image_sigmas(steps)``, ``tail =
  full[t_start:]`` with ``t_start = int(max(steps - min(steps * strength,
  steps), 0))`` (as ``ZImageImg2ImgPipeline.get_timesteps``);
  ``scheduler.set_timesteps(sigmas=tail)`` shifts them (static shift 3, the
  ``mu`` is ignored because ``use_dynamic_shifting`` is false) and appends the
  terminal 0; sigma0 = ``scheduler.sigmas[0]``, logged next to the pure
  numpy replication of ``wenart.polish.schedule``.
- latents: ``retrieve_latents(vae.encode(render), sample_mode="argmax")``,
  ``(x - shift_factor) * scaling_factor``, then ``sigma0 * noise + (1 -
  sigma0) * x0`` (the scheduler's ``scale_noise``) with float32 noise from a
  CPU ``torch.Generator`` seeded per attempt (the same noise on every GPU).
- ``pipe(prompt=None, prompt_embeds=[emb.to("cuda")], control_image=...,
  controlnet_conditioning_scale=s, height=H, width=W, sigmas=tail,
  num_inference_steps=len(tail), latents=latents, guidance_scale=0.0,
  generator=g)``. H and W are always passed: the pipeline defaults to
  1024x1024 and would stretch the control image. Given latents are only
  shape-checked, never re-noised; the pipeline re-runs ``set_timesteps`` with
  the same tail, so the schedule is the one sigma0 was read from.
- ``mode: anchor``: ``ZImageControlNetInpaintPipeline.from_pipe(pipe,
  dtype=bf16)`` with ``image=render`` and an all-black ``mask_image`` (black =
  keep: the ControlNet sees the whole render as known), same tail and
  latents. ``from_pipe`` casts every module to ``dtype`` (float32 when not
  given, which would double the transformer), hence ``dtype=bf16``.
- ``presumed_bad`` (control None): ``ZImageImg2ImgPipeline.from_pipe(pipe,
  dtype=bf16)`` with ``strength`` and ``num_inference_steps=steps`` (its own
  ``get_timesteps`` gives the same tail).
"""
from __future__ import annotations

import gc
import json
import os
import time
from pathlib import Path
from typing import Callable, Optional

import numpy as np

from wenart.hfcache import local_snapshot
from wenart.polish import schedule as S
from wenart.polish.config import config_dir

VAE_TILING_MIN_PIXELS = 1_500_000
PROMPT_BATCH = 8
ALLOC_CONF = "expandable_segments:True"


def to_uint8(image) -> np.ndarray:
    """Pipeline ``output_type="np"`` image (float 0..1, H x W x 3) -> uint8, rounded as diffusers' numpy_to_pil."""
    a = np.asarray(image, dtype=np.float32)
    return np.clip(np.rint(a * 255.0), 0, 255).astype(np.uint8)


def text_classes(base_dir: Path) -> tuple[str, str]:
    """transformers class names of the tokenizer and the text encoder from the snapshot's
    ``model_index.json`` (``["transformers", "Qwen2Tokenizer"]``, ``["transformers", "Qwen3Model"]``)."""
    index = json.loads((Path(base_dir) / "model_index.json").read_text(encoding="utf-8"))
    tok, enc = index["tokenizer"], index["text_encoder"]
    if tok[0] != "transformers" or enc[0] != "transformers":
        raise ValueError(f"unexpected tokenizer/text encoder libraries in model_index.json: {tok}, {enc}")
    return tok[1], enc[1]


class ZImageBackend:
    """Z-Image-Turbo + ControlNet Union 2.1 on one CUDA device (see the module docstring)."""

    def __init__(self, cfg: dict, device: str = "cuda") -> None:
        os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", ALLOC_CONF)
        self.cfg = cfg
        self.device = device
        self.embeddings: dict[str, object] = {}
        self.tokenizer = None
        self.pipe = None
        self._derived: dict[str, object] = {}
        self.memory_mode = "resident"        # always: no CPU offload (see the module docstring)
        self.release_hook: Optional[Callable[[], None]] = None
        self.oom_retries = 0
        self._retry_after_oom = True         # False once a retry ran out of memory again
        self.load_seconds: Optional[float] = None
        self.encode_seconds: Optional[float] = None
        self._calls: list[tuple[float, int]] = []

    # -- interface ---------------------------------------------------------

    def versions(self) -> dict:
        import diffusers
        import torch
        name = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu"
        return {"torch": torch.__version__, "diffusers": diffusers.__version__, "device": name}

    def ensure_ready(self, prompts) -> None:
        """Encode all prompts (text encoder loaded, used, freed), then load the diffusion models once."""
        if self.pipe is None:
            self._encode_prompts(list(prompts))
            self._load()
            return
        missing = [p for p in prompts if p not in self.embeddings]
        if missing:
            raise RuntimeError(f"{len(missing)} prompt(s) were not encoded before the text encoder was freed")

    def free_cache(self) -> None:
        import torch
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def stats(self) -> dict:
        import torch
        peak = reserved = None
        if torch.cuda.is_available():
            peak = round(torch.cuda.max_memory_allocated() / 2 ** 30, 2)
            reserved = round(torch.cuda.max_memory_reserved() / 2 ** 30, 2)
        forwards = sum(n for _, n in self._calls)
        spf = round(sum(s for s, _ in self._calls) / forwards, 3) if forwards else None
        return {"memory_mode": self.memory_mode, "peak_vram_gib": peak, "peak_reserved_gib": reserved,
                "load_seconds": self.load_seconds, "encode_seconds": self.encode_seconds,
                "seconds_per_forward": spf, "forwards": forwards, "oom_retries": self.oom_retries}

    def generate(self, image, control, *, strength: float, scale, mode: str, seed: int, steps: int,
                 prompt: str) -> tuple[np.ndarray, dict]:
        """One polish at the model size (see the module docstring); after a CUDA OOM one resident retry."""
        import torch
        if self.pipe is None:
            raise RuntimeError("ensure_ready() was not called")
        if prompt not in self.embeddings:
            raise RuntimeError("prompt was not encoded")
        args = (image, control, strength, scale, mode, seed, steps, prompt)
        try:
            return self._generate(*args)
        except torch.cuda.OutOfMemoryError:
            if not self._retry_after_oom:
                raise
        # The retry runs here, after the handler: the exception, its traceback and with them the failed
        # call's frames (latents, activations) are released before anything is allocated again.
        self.oom_retries += 1
        if self.release_hook is not None:
            self.release_hook()
        self.free_cache()
        try:
            return self._generate(*args)
        except torch.cuda.OutOfMemoryError:
            self._retry_after_oom = False    # freeing did not help: later OOMs are raised at once
            raise

    # -- loading -----------------------------------------------------------

    def _encode_prompts(self, prompts: list[str]) -> None:
        import torch
        from diffusers import ZImagePipeline
        import transformers

        t0 = time.time()
        base_dir = self._base_dir()
        tok_cls, enc_cls = text_classes(base_dir)
        # Local folders only: AutoTokenizer(repo, subfolder=...) asks AutoConfig for a
        # tokenizer/config.json that does not exist and fails offline (wenart/hfcache.py).
        self.tokenizer = getattr(transformers, tok_cls).from_pretrained(str(base_dir / "tokenizer"))
        encoder = getattr(transformers, enc_cls).from_pretrained(str(base_dir / "text_encoder"),
                                                                 dtype=torch.bfloat16, device_map=self.device)
        shell = ZImagePipeline(scheduler=None, vae=None, text_encoder=encoder, tokenizer=self.tokenizer,
                               transformer=None)
        todo = [p for p in dict.fromkeys(prompts) if p not in self.embeddings]
        with torch.no_grad():
            for i in range(0, len(todo), PROMPT_BATCH):
                chunk = todo[i:i + PROMPT_BATCH]
                # encode_prompt rewrites the list it is given (chat template), so it gets a copy.
                embeds, _ = shell.encode_prompt(prompt=list(chunk), device=self.device,
                                                do_classifier_free_guidance=False)
                for text, emb in zip(chunk, embeds):
                    self.embeddings[text] = emb.detach().to("cpu")
        del shell, encoder
        self.free_cache()
        self.encode_seconds = round(time.time() - t0, 1)

    def _base_dir(self) -> Path:
        """Local folder of the pinned Z-Image-Turbo snapshot (wenart/hfcache.py)."""
        base = self.cfg["models"]["base"]
        return local_snapshot(base["repo"], base["revision"], base.get("allow_patterns"))

    def _load(self) -> None:
        import torch
        from diffusers import (AutoencoderKL, FlowMatchEulerDiscreteScheduler, ZImageControlNetModel,
                               ZImageControlNetPipeline, ZImageTransformer2DModel)
        cn = self.cfg["models"]["controlnet"]
        t0 = time.time()
        base_dir = str(self._base_dir())
        transformer = ZImageTransformer2DModel.from_pretrained(
            base_dir, subfolder="transformer", dtype=torch.bfloat16, device_map=self.device)
        cn_dir = local_snapshot(cn["repo"], cn["revision"], cn.get("allow_patterns") or list(cn["files"]))
        weights = str(cn_dir / cn["files"][0])
        controlnet = ZImageControlNetModel.from_single_file(
            weights, config=str(config_dir(self.cfg)), dtype=torch.bfloat16).to(self.device)
        vae = AutoencoderKL.from_pretrained(base_dir, subfolder="vae", dtype=torch.bfloat16).to(self.device)
        scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(base_dir, subfolder="scheduler")
        self.pipe = ZImageControlNetPipeline(scheduler, vae, None, self.tokenizer, transformer, controlnet)
        self.pipe.set_progress_bar_config(disable=True)
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        self.load_seconds = round(time.time() - t0, 1)

    def _pipeline(self, name: str):
        """The pipeline for ``plain`` (the ControlNet pipeline), ``anchor`` (inpaint) or ``img2img``."""
        import torch
        if name == "plain":
            pipe = self.pipe
        else:
            pipe = self._derived.get(name)
            if pipe is None:
                if name == "anchor":
                    from diffusers import ZImageControlNetInpaintPipeline as cls
                elif name == "img2img":
                    from diffusers import ZImageImg2ImgPipeline as cls
                else:
                    raise ValueError(f"unknown pipeline {name!r}")
                pipe = cls.from_pipe(self.pipe, dtype=torch.bfloat16)
                pipe.set_progress_bar_config(disable=True)
                self._derived[name] = pipe
        return pipe

    # -- generation --------------------------------------------------------

    def _tiling(self, pixels: int) -> None:
        vae = self.pipe.vae
        if pixels > VAE_TILING_MIN_PIXELS:
            vae.enable_tiling()
        else:
            vae.disable_tiling()

    def _generate(self, image, control, strength, scale, mode, seed, steps, prompt) -> tuple[np.ndarray, dict]:
        import torch
        from PIL import Image

        img = np.ascontiguousarray(np.asarray(image, dtype=np.uint8)[:, :, :3])
        H, W = img.shape[:2]
        self._tiling(W * H)
        pil = Image.fromarray(img)
        g = torch.Generator("cpu").manual_seed(int(seed))
        tail_numpy = S.sigma_tail(int(steps), float(strength))
        if control is None:
            pipe = self._pipeline("img2img")
            dev = pipe._execution_device
            t0 = time.time()
            out = pipe(prompt=None, prompt_embeds=[self.embeddings[prompt].to(dev)], image=pil,
                       strength=float(strength), height=H, width=W, num_inference_steps=int(steps),
                       guidance_scale=0.0, generator=g, output_type="np")
            seconds = self._timed(t0)
            forwards = len(tail_numpy)
            meta = {"pipeline": "img2img", "forwards": forwards, "sigma0": None,
                    "sigma0_numpy": S.sigma0(tail_numpy, float(pipe.scheduler.config.shift))}
        else:
            from diffusers.pipelines.z_image.pipeline_z_image_controlnet import (get_default_z_image_sigmas,
                                                                                 retrieve_latents)
            pipe = self._pipeline("anchor" if mode == "anchor" else "plain")
            dev = pipe._execution_device
            full = get_default_z_image_sigmas(int(steps))
            tail = full[S.t_start(int(steps), float(strength)):]
            if not tail:
                raise ValueError(f"strength {strength} with {steps} steps leaves no denoising step")
            sched = pipe.scheduler
            sched.set_timesteps(sigmas=tail, device=dev)
            s0 = float(sched.sigmas[0])
            t0 = time.time()
            with torch.no_grad():
                x = pipe.image_processor.preprocess(pil, height=H, width=W).to(device=dev, dtype=pipe.vae.dtype)
                x0 = retrieve_latents(pipe.vae.encode(x), sample_mode="argmax")
                x0 = (x0 - pipe.vae.config.shift_factor) * pipe.vae.config.scaling_factor
                noise = torch.randn(tuple(x0.shape), generator=g, dtype=torch.float32)
                latents = s0 * noise.to(dev) + (1.0 - s0) * x0.to(torch.float32)
            kwargs = dict(prompt=None, prompt_embeds=[self.embeddings[prompt].to(dev)],
                          control_image=Image.fromarray(np.ascontiguousarray(np.asarray(control, dtype=np.uint8))),
                          controlnet_conditioning_scale=float(scale), height=H, width=W, sigmas=tail,
                          num_inference_steps=len(tail), latents=latents, guidance_scale=0.0, generator=g,
                          output_type="np")
            if mode == "anchor":
                kwargs.update(image=pil, mask_image=Image.new("L", (W, H), 0))
            out = pipe(**kwargs)
            seconds = self._timed(t0)
            forwards = len(tail)
            meta = {"pipeline": "controlnet_inpaint" if mode == "anchor" else "controlnet", "forwards": forwards,
                    "sigma0": round(s0, 6),
                    "sigma0_numpy": S.sigma0(tail_numpy, float(sched.config.shift))}
        self._calls.append((seconds, forwards))
        meta["sigma0_numpy"] = round(meta["sigma0_numpy"], 6)
        meta["seconds"] = round(seconds, 3)
        result = to_uint8(out.images[0])
        if result.shape != (H, W, 3):
            raise RuntimeError(f"pipeline returned {result.shape}, expected {(H, W, 3)}")
        return result, meta

    @staticmethod
    def _timed(t0: float) -> float:
        import torch
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        return time.time() - t0
