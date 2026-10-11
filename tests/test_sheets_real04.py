"""real04 (``projects/real04/deneme1.dwg``, the user's DWG of 11 Oct 2026): the real02 twin villa on its plot,
"4 ADET VİLLA". Needs LibreDWG ``dwg2dxf``; the DWG is converted once per session (about two minutes).

The site plan r14 (PARSEL SINIRI, YAPI YAKLAŞMA SINIRI, pools, level marks 37-46 m) holds two twin-villa blocks,
each drawn as two inserts of the block ``bina``; ``wenart/sheets/buildings.py`` finds both, b2 18.6 m beside b1 and
3 m higher (entrance marks 43 and 46), ±0.00 = 43.00; the pools and the sun terraces name their own outlines."""
from __future__ import annotations

import pytest
from shapely.geometry import Polygon

import wenart.sheets as SH
from conftest import PROJECTS
from wenart.ingest import dwg

pytestmark = pytest.mark.skipif(not dwg.available_converters() or not (PROJECTS / "real04").is_dir(),
                                reason="LibreDWG dwg2dxf not installed")


@pytest.fixture(scope="session")
def real04(tmp_path_factory):
    out = tmp_path_factory.mktemp("real04")
    return SH.run(PROJECTS / "real04", out, no_ai=True).doc


def test_the_site_plan_holds_two_twin_blocks(real04):
    assert SH.validation_errors(real04) == []
    r14 = next(r for r in real04["regions"] if r["id"] == "r14")
    assert r14["class"] == "site_plan" and r14["use"] == "exterior"
    assert r14["registration"]["method"] == "site_buildings"
    site = real04["exterior"]["site"]
    assert site["region"] == "r14"
    b1, b2 = site["buildings"]
    assert b1["reference"] and not b2["reference"]
    assert b1["orientation"] == b2["orientation"] == "entrances"
    assert b1["entrance_ground"] == 43.0 and b2["entrance_ground"] == 46.0 and b2["dz"] == 3.0
    assert b2["rotation_deg"] == pytest.approx(0.0, abs=0.5)
    assert b2["translate"] == pytest.approx([0.0, 18.57], abs=0.1)
    assert all(len(b["entities"]) == 2 for b in (b1, b2))         # two ``bina`` inserts each (one villa each)
    assert site["datum"]["value"] == 43.0


def test_pools_terraces_parking_trees_and_marks(real04):
    site = real04["exterior"]["site"]
    assert sorted(round(Polygon(p["polygon"]).area) for p in site["pools"]) == [24, 24, 24, 24]
    assert all(Polygon(p["polygon"]).area < 40 for p in site["paving"])         # the sun terraces, never the setback
    assert len(site["paving"]) == 4 and round(Polygon(site["parking"][0]["polygon"]).area) == 287
    assert len(site["trees"]) == 101 and len(site["marks"]) == 16
    assert Polygon(site["plot"]).area == pytest.approx(1165.9, abs=1.0)        # the title: 1165 M2 (621 + 544)
