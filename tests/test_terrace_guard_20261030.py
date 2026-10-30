"""Terrace guards read as real guards (30 Oct 2026, lesson UL145, user on real04 run 20261029-201533-full: "better
handrails in the terras is needed": the roof terrace's 28 mm cap over clear thin glass read as a thin bare tube)."""
from pathlib import Path

from wenart.blender import details as D

REPO = Path(__file__).resolve().parents[1]


def test_the_glass_channel_cap_is_a_real_handrail():
    assert D.DIMS["cap_w"] >= 0.045 and D.DIMS["cap_h"] >= 0.04


def test_outdoor_guard_glass_is_tinted_not_clear():
    r, g, b = D.GUARD_GLASS_RGB
    assert all(0.6 <= c < 1.0 for c in (r, g, b))


def _body(text: str, name: str) -> str:
    body = text[text.index(f"def {name}("):]
    end = body.find("\ndef ", 1)
    return body if end < 0 else body[:end]


def test_every_outdoor_guard_uses_the_guard_glass():
    build = (REPO / "wenart/blender/build.py").read_text(encoding="utf-8")
    shell = (REPO / "wenart/blender/shell.py").read_text(encoding="utf-8")
    rail = _body(build, "terrace_railings")
    assert "library.guard_glass()" in rail and "library.thin_glass()" not in rail
    outside = _body(shell, "build_outside_details")
    assert "library.guard_glass()" in outside and "library.thin_glass()" not in outside
