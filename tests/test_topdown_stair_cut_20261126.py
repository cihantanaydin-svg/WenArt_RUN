"""26 Nov 2026 (real17 re-render, pod 23367e58pfhcq9): the top-down views cut a stair at ``STAIR_CUT_M`` over the
level's floor with a cutter of its own, so its rails no longer hang over the hall."""
from __future__ import annotations

import inspect

from wenart.blender import topdown as TD


def test_stairs_are_cut_like_a_plan():
    assert TD.STAIR_TYPES >= {"stair"}
    assert 0.9 <= TD.STAIR_CUT_M <= 1.5            # an architect's plan cut: above the walls' cut, under a landing
    assert TD.STAIR_CUT_M > TD.WALL_CUT_M


def test_section_cut_takes_types_and_its_own_cutter():
    sig = inspect.signature(TD.section_cut)
    assert "types" in sig.parameters and "cutter_name" in sig.parameters
    assert sig.parameters["cutter_name"].default == "topdown_cutter"
    src = inspect.getsource(TD.render_level)
    assert "STAIR_TYPES" in src and "topdown_stair_cutter" in src
