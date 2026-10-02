"""Model wrappers of the change gate (docs/milestone5.md §1.3, §1.6, §4.2): DAv2-Small, SAM 2.1, DINOv2.

What: ``Models`` loads the three gate models lazily (first use) from the
local folders of the pinned snapshots of ``models.yaml``
(``wenart.hfcache.local_snapshot``: the repo and revision resolve to a folder
of the ``HF_HOME`` cache, so ``HF_HUB_OFFLINE=1`` needs no hub lookup) and
gives numpy results:

- ``depth(rgb) -> float32 H x W`` relative disparity (Depth Anything V2
  Small: ``AutoImageProcessor`` + ``AutoModelForDepthEstimation``, upsampled
  to the image size with ``post_process_depth_estimation(outputs,
  target_sizes=[(H, W)])``);
- ``sam_masks(rgb, boxes) -> bool N x H x W`` (SAM 2.1: ``Sam2Processor(images,
  input_boxes=[boxes])``, one ``Sam2Model.get_image_embeddings`` per image,
  the boxes in one batch (chunks of ``SAM_CHUNK``) with
  ``multimask_output=False``, ``post_process_masks`` to the image size);
- ``dino_tokens(rgb) -> float32 gh x gw x C`` (DINOv2-base ``AutoModel``; the
  processor is told ``size={"height": 518, "width": 924}`` for a 16:9 image
  and ``do_center_crop=False``; the CLS token is dropped).

Every image goes to the device once as a uint8 3 x H x W tensor and the
processors get ``device=`` (an ``ImagesKwargs`` key of the torchvision
backend), so the resize and normalisation run on the GPU; the depth
upsampling and the SAM mask upsampling + threshold run there too, and only
the final float32 disparity / bool masks / tokens are copied back. On the
CPU these steps used every host thread (pod run 0b, 112 visible CPUs) and
competed with the gate's own numpy work.

The APIs were checked against the transformers 5.18.0 wheel source
(``models/sam2/processing_sam2.py`` ``__call__`` and ``post_process_masks``,
``modeling_sam2.py`` ``get_image_embeddings``/``forward``,
``models/dpt/image_processing_dpt.py`` ``post_process_depth_estimation``,
``image_processing_backends.py`` resize with height/width,
``modeling_utils.py`` ``from_pretrained(..., revision=, dtype=)``). They
cannot run here (no torch in the cloud session): the GPU tests on the pod
run them; CPU tests use fakes with the same three methods.

Memory (§1.3): models stay on the GPU when ``torch.cuda.mem_get_info()``
shows at least 4 GiB free after the first comparison (``settle()``),
otherwise each model is moved to the GPU for its call and back to the CPU
afterwards (``torch.cuda.empty_cache()`` after the move). All three run in
float32 (small models; the gate is a measurement).

torch and transformers are imported inside the methods only.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from wenart.gate.api import load_models_config

GIB = 1024 ** 3
RESIDENT_MIN_FREE_GIB = 4.0
SAM_CHUNK = 64                 # boxes per mask-decoder batch (one image encoding is shared)
DINO_HEIGHT = 518              # processor height; width keeps the aspect, multiple of the patch size
MODEL_KEYS = ("depth", "sam", "dino")


def dino_size(width: int, height: int, patch: int = 14, target_h: int = DINO_HEIGHT) -> tuple[int, int]:
    """``(h, w)`` for the DINOv2 processor: height 518, width rounded to a multiple of ``patch`` (1920x1080 -> 518x924)."""
    w = int(round(target_h * float(width) / float(height) / patch)) * patch
    return int(target_h), max(patch, w)


class Models:
    """Lazy DAv2-Small / SAM 2.1 / DINOv2 wrappers for one device (see the module docstring)."""

    def __init__(self, config: Optional[dict] = None, device: str = "cuda") -> None:
        cfg = config if config is not None else load_models_config()
        self.config = cfg.get("models", cfg)
        missing = [k for k in MODEL_KEYS if k not in self.config]
        if missing:
            raise KeyError(f"models.yaml lacks {', '.join(missing)}")
        self.device = device
        self.resident: Optional[bool] = None          # None until settle(): stay on the device
        self._loaded: dict[str, tuple] = {}            # key -> (processor, model)
        self.load_seconds: dict[str, float] = {}

    # ------------------------------------------------------------------ info

    def info(self) -> dict:
        """``{"depth"|"sam"|"dino": {"repo", "revision", "licence"}}`` for manifests and the gate key."""
        return {k: {"repo": v["repo"], "revision": v["revision"], "licence": v.get("licence")}
                for k, v in ((k, self.config[k]) for k in MODEL_KEYS)}

    def memory(self) -> dict:
        """``{"resident", "loaded", "load_seconds"}`` (what the manifests record)."""
        return {"resident": self.resident, "loaded": sorted(self._loaded), "load_seconds": dict(self.load_seconds)}

    # --------------------------------------------------------------- loading

    def _snapshot(self, cfg: dict):
        """Local folder of a model's pinned snapshot (downloaded by scripts/pod_setup_polish.sh)."""
        from wenart.hfcache import local_snapshot
        return local_snapshot(cfg["repo"], cfg["revision"], cfg.get("allow_patterns"))

    def _load(self, key: str) -> tuple:
        import time

        import torch
        start = time.time()
        cfg = self.config[key]
        # The local folder of the pinned snapshot, not the repo id: with HF_HUB_OFFLINE=1 a
        # repo-id load can fail on a missing optional file (wenart/hfcache.py).
        path = str(self._snapshot(cfg))
        if key == "depth":
            from transformers import AutoImageProcessor, AutoModelForDepthEstimation
            proc = AutoImageProcessor.from_pretrained(path)
            model = AutoModelForDepthEstimation.from_pretrained(path, dtype=torch.float32)
        elif key == "sam":
            from transformers import Sam2Model, Sam2Processor
            proc = Sam2Processor.from_pretrained(path)
            model = Sam2Model.from_pretrained(path, dtype=torch.float32)
        elif key == "dino":
            from transformers import AutoImageProcessor, AutoModel
            proc = AutoImageProcessor.from_pretrained(path)
            model = AutoModel.from_pretrained(path, dtype=torch.float32)
        else:
            raise KeyError(key)
        model.eval()
        model.to(self.device)
        self.load_seconds[key] = round(time.time() - start, 2)
        return proc, model

    def _ready(self, key: str) -> tuple:
        """The (processor, model) of ``key`` on the device (loaded on first use)."""
        if key not in self._loaded:
            self._loaded[key] = self._load(key)
        proc, model = self._loaded[key]
        if self.resident is False:
            model.to(self.device)
        return proc, model

    def _release(self, key: str) -> None:
        """Move the model back to the CPU after its call when the models are not resident."""
        if self.resident is not False or key not in self._loaded or not str(self.device).startswith("cuda"):
            return
        import torch
        self._loaded[key][1].to("cpu")
        torch.cuda.empty_cache()

    def settle(self) -> Optional[bool]:
        """Decide once (after the first comparison) whether the models stay on the GPU (>= 4 GiB free)."""
        if self.resident is not None or not self._loaded:
            return self.resident
        if not str(self.device).startswith("cuda"):
            self.resident = True
            return True
        import torch
        free, _total = torch.cuda.mem_get_info()
        self.resident = free / GIB >= RESIDENT_MIN_FREE_GIB
        if not self.resident:
            for key in list(self._loaded):
                self._loaded[key][1].to("cpu")
            torch.cuda.empty_cache()
        return self.resident

    # ----------------------------------------------------------------- calls

    def _image(self, rgb):
        """uint8 3 x H x W tensor of an RGB image, already on the device.

        The image processors (torchvision backend) then resize and normalise
        it on the device (``device=`` below) instead of on the CPU, where
        their resize ran with every host thread (pod run 0b: the gate checks
        took 5-24 s per comparison on a contended pod).
        """
        import torch
        a = np.ascontiguousarray(np.asarray(rgb, dtype=np.uint8)[:, :, :3])
        return torch.from_numpy(a).to(self.device).permute(2, 0, 1).contiguous()

    def depth(self, rgb) -> np.ndarray:
        """float32 H x W relative disparity of an RGB uint8 image (Depth Anything V2 Small)."""
        import torch
        proc, model = self._ready("depth")
        try:
            h, w = np.asarray(rgb).shape[:2]
            inputs = proc(images=self._image(rgb), return_tensors="pt", device=self.device)
            with torch.inference_mode():
                outputs = model(pixel_values=inputs["pixel_values"].to(self.device))
                # Bicubic upsampling to (H, W) runs where the prediction is (the device), in float32.
                post = proc.post_process_depth_estimation(outputs, target_sizes=[(h, w)])
                disp = post[0]["predicted_depth"].float().cpu()
            return np.asarray(disp.numpy(), dtype=np.float32)
        finally:
            self._release("depth")

    def sam_masks(self, rgb, boxes) -> np.ndarray:
        """bool N x H x W SAM 2.1 masks for ``boxes`` (``[x0, y0, x1, y1]`` pixels) on one RGB image."""
        import torch
        h, w = np.asarray(rgb).shape[:2]
        boxes = [[float(v) for v in b] for b in boxes]
        if not boxes:
            return np.zeros((0, h, w), dtype=bool)
        proc, model = self._ready("sam")
        try:
            inputs = proc(images=self._image(rgb), input_boxes=[boxes], return_tensors="pt", device=self.device)
            out = []
            with torch.inference_mode():
                embeddings = model.get_image_embeddings(inputs["pixel_values"].to(self.device))
                all_boxes = inputs["input_boxes"]
                for start in range(0, len(boxes), SAM_CHUNK):
                    chunk = all_boxes[:, start:start + SAM_CHUNK].to(self.device)
                    result = model(image_embeddings=embeddings, input_boxes=chunk, multimask_output=False)
                    # Upsample the low-res logits to (H, W) and threshold on the device; only the bool masks
                    # come back (they used to be upsampled on the CPU in float32, N x H x W).
                    masks = proc.post_process_masks(result.pred_masks, inputs["original_sizes"])[0]
                    out.append(np.asarray(masks[:, 0].cpu().numpy(), dtype=bool))
            return np.concatenate(out, axis=0)
        finally:
            self._release("sam")

    def dino_tokens(self, rgb) -> np.ndarray:
        """float32 gh x gw x C DINOv2 patch tokens (no centre crop; height 518, width by aspect)."""
        import torch
        proc, model = self._ready("dino")
        try:
            h, w = np.asarray(rgb).shape[:2]
            patch = int(getattr(model.config, "patch_size", 14))
            size_h, size_w = dino_size(w, h, patch)
            inputs = proc(images=self._image(rgb), size={"height": size_h, "width": size_w},
                          do_center_crop=False, return_tensors="pt", device=self.device)
            with torch.inference_mode():
                outputs = model(pixel_values=inputs["pixel_values"].to(self.device))
            skip = 1 + int(getattr(model.config, "num_register_tokens", 0) or 0)
            tokens = outputs.last_hidden_state[0, skip:].float().cpu().numpy()
            gh, gw = size_h // patch, size_w // patch
            return np.asarray(tokens, dtype=np.float32).reshape(gh, gw, -1)
        finally:
            self._release("dino")
