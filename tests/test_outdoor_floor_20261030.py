"""UL159 (30 Oct 2026, real04 run 20261030-043021-full): "I like the new Teras furnitures better but a different
flooring is needed which must be suitable for the outside". The roof terrace had the garden paving (concrete slabs with
grass in the joints). A roof terrace, a balcony or a loggia takes the family's terrace floor, never a garden floor."""
from pathlib import Path

import pytest

from wenart.blender import grading as GR
from wenart.blender import shell as SH

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("family", sorted(GR.FLOOR_SETS) + [None, "unknown family"])
def test_a_raised_outdoor_floor_is_the_familys_terrace_floor_never_garden_paving(family):
    for paving in (None, {"material": "paving", "assumed": True, "source": "fallback"},
                   {"material": "paving", "assumed": False, "source": "style"},
                   {"material": "gravel", "assumed": False, "source": "brief"}):
        lk = GR.raised_floor({"paving": paving} if paving else {}, family)
        assert lk["material"] not in GR.RAISED_NEVER and lk.get("asset"), (family, paving, lk)
        assert "roof terrace or balcony floor" in lk["reason"]
    # a stone the style names for its terraces is kept
    named = GR.raised_floor({"paving": {"material": "travertine", "assumed": False, "source": "style"}}, family)
    assert named["material"] == "travertine"


def test_the_build_gives_open_and_outdoor_rooms_the_raised_floor():
    assert {"balcony", "terrace", "loggia"} <= set(SH.OUTDOOR_FLOOR_ROOMS)
    src = (ROOT / "wenart" / "blender" / "build.py").read_text()
    assert '"terrace_floor": GR.raised_floor(looks' in src and '"terrace_floor": (looks or {}).get("paving")' not in src
    slot, wet = SH.floor_style({"room_type": "balcony"}, {"floor": {"material": "wood_herringbone_mid"}},
                               GR.raised_floor({}, "modern"))
    assert slot["material"] == "paving_stone" and not wet
