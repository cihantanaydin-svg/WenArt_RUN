"""Sigma schedule of the img2img-with-control polish, in pure numpy (docs/milestone5.md §3.2).

What: the few formulas the Z-Image polish needs to start from the Cycles
render instead of pure noise:

- ``default_sigmas(n)``: ``get_default_z_image_sigmas(n)`` of diffusers
  0.40.0 (``torch.linspace(1.0, 1 / n, n).tolist()`` in
  ``pipelines/z_image/pipeline_z_image_controlnet.py``), computed the way
  torch's float32 linspace does it;
- ``t_start(n, strength)``: ``ZImageImg2ImgPipeline.get_timesteps``
  (``int(max(n - min(n * strength, n), 0))``);
- ``sigma_tail(n, strength)``: ``default_sigmas(n)[t_start:]``, the sigmas
  the pipeline is called with (``sigmas=tail``); an empty tail is an error;
- ``shift_sigmas(sigmas, shift)``: what
  ``FlowMatchEulerDiscreteScheduler.set_timesteps(sigmas=...)`` does with a
  static shift (``shift * s / (1 + (shift - 1) * s)`` in float32;
  ``use_dynamic_shifting`` is false in the Z-Image-Turbo scheduler config, so
  the ``mu`` the pipeline passes is ignored);
- ``scheduler_sigmas(tail, shift)``: the shifted tail plus the terminal sigma
  0 that ``set_timesteps`` appends (it is a target, not a forward);
- ``sigma0(tail, shift)``: the first shifted sigma, the noise level the
  render's latents are mixed with (``sigma0 * noise + (1 - sigma0) * x0``,
  the ``scale_noise`` of the scheduler).

Why pure: torch is not installed on the CPU machines. ``wenart.polish.zimage``
reads sigma0 from the real scheduler (``scheduler.sigmas[0]``) and logs it
next to this replication, so a drift between the two is visible in the
manifest; the CPU tests check the §3.2 numbers (shift 3: strength 0.125 -> 1
step from 0.30, 0.25 -> 2 from 0.50, 0.375 -> 3 from 0.643, 0.5 -> 4 from 0.75).
"""
from __future__ import annotations

import numpy as np

ZIMAGE_SHIFT = 3.0          # Tongyi-MAI/Z-Image-Turbo scheduler/scheduler_config.json: shift 3.0


def default_sigmas(n: int) -> list[float]:
    """``torch.linspace(1.0, 1 / n, n).tolist()`` in float32 (diffusers ``get_default_z_image_sigmas``).

    torch fills the first half as ``start + i * step`` and the second half as
    ``end - (n - 1 - i) * step``; both are done here in float32 so the values
    match torch to the last bit for the step counts used (8 gives exactly
    1.0, 0.875, ..., 0.125).
    """
    n = int(n)
    if n < 1:
        raise ValueError(f"number of steps must be >= 1, got {n}")
    start = np.float32(1.0)
    end = np.float32(1.0 / n)
    if n == 1:
        return [float(start)]
    step = np.float32((end - start) / np.float32(n - 1))
    out = []
    half = n // 2
    for i in range(n):
        if i < half:
            v = np.float32(start + step * np.float32(i))
        else:
            v = np.float32(end - step * np.float32(n - 1 - i))
        out.append(float(v))
    return out


def t_start(n: int, strength: float) -> int:
    """First kept index of the default sigmas for ``strength`` (``ZImageImg2ImgPipeline.get_timesteps``)."""
    strength = float(strength)
    if not 0.0 <= strength <= 1.0:
        raise ValueError(f"strength must be in [0, 1], got {strength}")
    init = min(int(n) * strength, int(n))
    return int(max(int(n) - init, 0))


def sigma_tail(n: int, strength: float) -> list[float]:
    """The unshifted sigmas the polish runs (``default_sigmas(n)[t_start:]``); ValueError when empty."""
    tail = default_sigmas(n)[t_start(n, strength):]
    if not tail:
        raise ValueError(f"strength {strength} with {n} steps leaves no denoising step")
    return tail


def shift_sigmas(sigmas, shift: float = ZIMAGE_SHIFT) -> list[float]:
    """Static time shift of ``set_timesteps``: ``shift * s / (1 + (shift - 1) * s)`` in float32."""
    s = np.asarray(sigmas, dtype=np.float32)
    sh = np.float32(shift)
    out = (sh * s / (np.float32(1.0) + (sh - np.float32(1.0)) * s)).astype(np.float32)
    return [float(v) for v in out]


def scheduler_sigmas(tail, shift: float = ZIMAGE_SHIFT) -> list[float]:
    """``scheduler.sigmas`` after ``set_timesteps(sigmas=tail)``: the shifted tail plus the terminal 0."""
    return shift_sigmas(tail, shift) + [0.0]


def sigma0(tail, shift: float = ZIMAGE_SHIFT) -> float:
    """The first shifted sigma of ``tail``: the noise level the render's latents start from."""
    if not len(tail):
        raise ValueError("empty sigma tail")
    return shift_sigmas([tail[0]], shift)[0]


def schedule(n: int, strength: float, shift: float = ZIMAGE_SHIFT) -> dict:
    """Everything the manifest records about one attempt's schedule.

    ``{"steps": n, "t_start", "forwards": len(tail), "sigmas": tail (unshifted, as passed to the
    pipeline), "shifted": the scheduler sigmas without the terminal 0, "sigma0", "shift"}``.
    """
    tail = sigma_tail(n, strength)
    shifted = shift_sigmas(tail, shift)
    return {"steps": int(n), "t_start": t_start(n, strength), "forwards": len(tail),
            "sigmas": [round(v, 6) for v in tail], "shifted": [round(v, 6) for v in shifted],
            "sigma0": round(shifted[0], 6), "shift": float(shift)}
