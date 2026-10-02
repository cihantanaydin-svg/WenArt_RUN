"""AI polish of the Cycles renders (docs/milestone5.md §3; area B).

Z-Image-Turbo + Fun ControlNet Union 2.1, img2img with one control image,
attempt ladder gated by ``wenart.gate``; settings in ``polish.yaml``.
torch/diffusers are imported lazily inside functions so the package imports
on a CPU-only machine.

Modules:

- ``config``: ``polish.yaml``, ladder and grids as checked attempt lists;
- ``schedule``: the sigma tail and sigma0 of an attempt (pure numpy);
- ``sizing``: native reflect-pad / WxH Lanczos to the model size and back;
- ``controls``: depth / canny / geometry control images;
- ``prompt``: the prompt of a view (slug -> words tables);
- ``panes``: Cycles window panes pasted back after every attempt;
- ``rooms``: the room rule (wall Lab means within ΔE 5);
- ``zimage``: the diffusers backend (the only module that imports torch);
- ``runner``: ladder, sweep, smoke, resumability, deadline, manifest;
- ``schema``: JSON schema of ``polish_manifest.json`` / ``determinism.json``;
- ``report``: ``polish_report.md``;
- ``__main__``: ``python -m wenart.polish run|sweep|smoke|report``.
"""
