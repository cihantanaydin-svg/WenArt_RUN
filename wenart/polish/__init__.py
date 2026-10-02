"""AI polish of the Cycles renders (docs/milestone5.md §3; area B).

Z-Image-Turbo + Fun ControlNet Union 2.1, img2img with one control image,
attempt ladder gated by ``wenart.gate``; settings in ``polish.yaml``.
torch/diffusers are imported lazily inside functions so the package imports
on a CPU-only machine.
"""
