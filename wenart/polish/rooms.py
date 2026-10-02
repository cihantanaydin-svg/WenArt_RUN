"""Room rule of the polish ladder: one room, one wall colour (docs/milestone5.md §3.6).

What: after the ladder, the polished candidates of one room must agree on the
colour of their walls: the CIELAB means (D65, sRGB) of the wall regions
(``struct:walls`` of ``wenart.views.regions``, window panes left out) must be
within ΔE76 5 of each other. Otherwise the room is downgraded: every
candidate takes the strongest rung that all of them accept and whose wall
means agree, or the Cycles render when there is none. The runner
(``wenart.polish.runner``) runs any rung that is still missing; this module
holds the pure parts:

- ``srgb_to_lab``: sRGB uint8 -> CIELAB (D65), the same formula as the gate's
  colour check;
- ``wall_mask`` / ``wall_lab``: the wall region of a view and its Lab mean;
- ``max_delta_e``: the largest pairwise ΔE76 of a set of Lab means (views
  without a wall region are left out);
- ``common_rungs``: the rungs every candidate accepts, strongest first.
"""
from __future__ import annotations

from itertools import combinations
from typing import Optional

import numpy as np

from wenart import views as V

ROOM_MAX_DELTA_E = 5.0

_M_RGB_TO_XYZ = np.array([[0.4124564, 0.3575761, 0.1804375],
                          [0.2126729, 0.7151522, 0.0721750],
                          [0.0193339, 0.1191920, 0.9503041]])
_WHITE_D65 = np.array([0.95047, 1.0, 1.08883])


def srgb_to_lab(rgb) -> np.ndarray:
    """uint8 sRGB (... x 3) -> float64 CIELAB (... x 3), D65 white."""
    c = np.asarray(rgb, dtype=np.float64)[..., :3] / 255.0
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    xyz = lin @ _M_RGB_TO_XYZ.T / _WHITE_D65
    eps = (6.0 / 29.0) ** 3
    f = np.where(xyz > eps, np.cbrt(xyz), xyz / (3.0 * (6.0 / 29.0) ** 2) + 4.0 / 29.0)
    L = 116.0 * f[..., 1] - 16.0
    a = 500.0 * (f[..., 0] - f[..., 1])
    b = 200.0 * (f[..., 1] - f[..., 2])
    return np.stack([L, a, b], axis=-1)


def wall_mask(index, depth_mm, normal, table: dict) -> np.ndarray:
    """bool H x W: the view's wall structure region without window panes."""
    reg = V.regions(index, depth_mm, normal, table)
    walls = reg.masks.get(V.STRUCT_WALLS)
    if walls is None:
        return np.zeros(np.asarray(index).shape, dtype=bool)
    return walls & ~reg.panes


def wall_lab(rgb, mask) -> Optional[list[float]]:
    """Mean CIELAB of ``rgb`` over ``mask`` (rounded to 0.01), None for an empty mask."""
    m = np.asarray(mask, dtype=bool)
    if not m.any():
        return None
    lab = srgb_to_lab(np.asarray(rgb)[m])
    return [round(float(v), 2) for v in lab.mean(axis=0)]


def delta_e(lab1, lab2) -> float:
    """ΔE76 between two Lab triples."""
    return float(np.linalg.norm(np.asarray(lab1, dtype=np.float64) - np.asarray(lab2, dtype=np.float64)))


def max_delta_e(labs) -> Optional[float]:
    """Largest pairwise ΔE76 of the non-None Lab means (a dict's values or a list); None for fewer than two."""
    values = [v for v in (labs.values() if isinstance(labs, dict) else labs) if v is not None]
    if len(values) < 2:
        return None
    return round(max(delta_e(a, b) for a, b in combinations(values, 2)), 3)


def labs_agree(labs, max_de: float = ROOM_MAX_DELTA_E) -> bool:
    """True when every pair of wall Lab means is within ``max_de`` (or fewer than two are known)."""
    de = max_delta_e(labs)
    return de is None or de <= max_de


def common_rungs(accepted: dict, n_rungs: int) -> list[int]:
    """Rungs (1-based) accepted by every camera of ``accepted`` = {camera: set of accepted rungs}, strongest first."""
    if not accepted:
        return []
    return [k for k in range(1, int(n_rungs) + 1) if all(k in s for s in accepted.values())]
