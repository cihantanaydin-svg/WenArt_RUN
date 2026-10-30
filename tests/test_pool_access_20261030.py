"""UL188 (30 Oct 2026, real04 run 20261030-112241-full): "Stairs here not making sense you can give access from the other
side of the pool for both of the houses": the sunken pool terraces' flights climbed out onto the drive, set into the
terrace beside the basement windows (UL162). A sunken terrace's flight never lands on a road; with no path or terrace to
land on it leaves from the side away from the roads. The real04 replay reads the committed latest baseline."""
import json
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results" / "baseline" / "latest" / "furniture" / "real04" / "building_final.json"


def test_real04_pool_terraces_leave_away_from_the_drive():
    if not BASE.is_file():
        pytest.skip("the latest real04 baseline is not in this checkout")
    from wenart.blender import build as B

    site = B.prepare(json.loads(BASE.read_text(encoding="utf-8")))["site"]
    roads = [p for p in site["platforms"] if p.get("kind") in S.ROAD_KINDS]
    ups = [p for p in site["platforms"] if p.get("steps_dir") == "up" and p.get("flight")]
    assert ups and roads
    for pf in ups:
        lands = next((q for q in site["platforms"] if q.get("id") == pf.get("flight_lands_on")), None)
        assert lands is None or lands.get("kind") not in S.ROAD_KINDS, pf["id"]
        assert not pf.get("flight_inward"), pf["id"]
        pt = pf["flight"]["landing"]
        assert all(not G.point_in_polygon(pt, r["polygon"]) for r in roads), pf["id"]
    assert S.ROAD_CLEAR_M >= 3.0
