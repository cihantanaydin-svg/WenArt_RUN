"""real02 through the whole vector pipeline (``pipeline.run_project``, ``--no-ai``): the sheets stage, the registration
of the four plan regions, the generic core per region, mirror twins, same_as and the variant (docs/milestone10.md
§1.1, §1.6b rows 14-18; track A3 follow-up). Needs LibreDWG (``scripts/cloud-setup.sh``); about three minutes.

What the plans draw, per dwelling (two mirrored dwellings on every plan, the 0.40 m party wall between them):

- L0 (ground floor): Yatak Odası x 2, E.Yatak Odası, E.Banyo, Banyo, Koridor, and the stair face (unlabelled: M11 M8
  names it "Merdiven", a hall: the M7 rule gives a stair its own face when it would share a labelled one). 14 rooms,
  7 twin pairs (Milestone 11: unlabelled faces pair too).
- L1 (attic): Teras, Banyo, Koridor, Oyun Aktivite ve Dinlenme Odası. 8 rooms, 4 twin pairs.
- L-1 (basement): Banyo, Mutfak, Koridor (with the stair), Salon. 8 rooms, 4 twin pairs; 4 doors, 4 windows (two
  7.19 m on the south wall, one 4.16 m in each kitchen's side wall), 2 doorless openings (kitchen to Salon).
- L-1b (basement, alternative "Açık mutfak"): Banyo, Oda, Koridor, and one face for Açık Mutfak + Salon: nothing is
  drawn between them, and no separator of <= 2.4 m reaches across, so the M7 two-labels-in-one-face rule applies:
  the first label (Açık Mutfak) names the room, the room is ``unverified`` and the warnings list the other label
  (SALON). 8 rooms, 4 twin pairs; both Banyo equal the base's (``same_as``). 4 doors, 2 windows (south), 2 doorless
  openings.
- The variant's ``exterior_changed`` is true for a drawn reason: L-1's kitchens have a window in each side wall
  (glass lines on layer 0 between the columns), L-1b's Oda there has plain side walls. Every outer wall and every
  other opening matches the base.

The basement outer face lines lie on their 3-decimal region box (``sheets.model.round_box``):
``dxf_generic.clip_page`` keeps them with its 0.001-unit tolerance (``BOX_TOL``), else the basement outer walls are
read only 0.2-1.9 m and one dwelling's rooms do not close.
"""
from __future__ import annotations

from collections import Counter

import pytest
from shapely.geometry import Polygon

from conftest import PROJECTS
from wenart.ingest import dwg
from wenart.ingest import pipeline as P

pytestmark = pytest.mark.skipif(not dwg.available_converters(), reason="LibreDWG dwg2dxf not installed")
TOL = 0.02


@pytest.fixture(scope="module")
def building(tmp_path_factory):
    out = tmp_path_factory.mktemp("real02_pipeline")
    b, _ = P.run_project(PROJECTS / "real02", out, no_ai=True)
    return b


def _rooms(b: dict, level: str) -> list[dict]:
    return [r for r in b["rooms"] if r["level_id"] == level]


def _twins(b: dict, level: str) -> Counter:
    """Label -> number of twin pairs on the level; every pair mirrors about the party wall (x = const)."""
    rooms = {r["id"]: r for r in _rooms(b, level)}
    out: Counter = Counter()
    for r in rooms.values():
        if r.get("twin_of"):
            first = rooms[r["twin_of"]]
            assert first["label"] == r["label"]
            a, c = Polygon(first["polygon"]).centroid, Polygon(r["polygon"]).centroid
            assert abs(a.y - c.y) <= TOL and abs(a.x - c.x) > 1.0
            out[r["label"]] += 1
    return out


def _openings(b: dict, level: str) -> Counter:
    return Counter(o["type"] for o in b["openings"] if o["level_id"] == level)


def _exterior(b: dict, level: str) -> tuple[list[dict], list[dict]]:
    walls = [w for w in b["walls"] if w["level_id"] == level and w.get("exterior")]
    ids = {w["id"] for w in walls}
    return walls, [o for o in b["openings"] if o["level_id"] == level and o.get("wall_id") in ids]


def _close(p, q) -> bool:
    return max(abs(p[0] - q[0]), abs(p[1] - q[1])) <= TOL


def _same_wall(a: dict, c: dict) -> bool:
    return abs(a["thickness"] - c["thickness"]) <= TOL and (
        (_close(a["start"], c["start"]) and _close(a["end"], c["end"])) or
        (_close(a["start"], c["end"]) and _close(a["end"], c["start"])))


def _same_opening(a: dict, c: dict) -> bool:
    return a["type"] == c["type"] and abs(a["width"] - c["width"]) <= TOL and _close(a["center"], c["center"])


def test_status_levels_and_variants(building):
    assert building["status"] == "ok"
    assert sorted(lv["id"] for lv in building["levels"]) == ["L-1", "L-1b", "L0", "L1"]
    assert [v["id"] for v in building["variants"]] == ["base", "l-1b-acik-mutfak"]


def test_ground_floor_rooms_and_twins(building):
    rooms = _rooms(building, "L0")
    assert Counter(r["label"] for r in rooms) == {"Yatak Odası": 4, "E.yatak Odası": 2, "E.banyo": 2, "Banyo": 2,
                                                  "Koridor": 2, "Merdiven": 2}
    assert all(r.get("label_raw") is None and r["room_type"] == "hall" for r in rooms if r["label"] == "Merdiven")
    assert _twins(building, "L0") == {"Yatak Odası": 2, "E.yatak Odası": 1, "E.banyo": 1, "Banyo": 1, "Koridor": 1,
                                      "Merdiven": 1}


def test_attic_rooms_and_twins(building):
    labels = {"Teras": 2, "Banyo": 2, "Koridor": 2, "Oyun Aktivite Ve Dinlenme Odası": 2}
    assert Counter(r["label"] for r in _rooms(building, "L1")) == labels
    assert _twins(building, "L1") == {k: 1 for k in labels}


def test_basement_rooms_twins_and_openings(building):
    labels = {"Banyo": 2, "Mutfak": 2, "Koridor": 2, "Salon": 2}
    assert Counter(r["label"] for r in _rooms(building, "L-1")) == labels
    assert _twins(building, "L-1") == {k: 1 for k in labels}                  # each dwelling has all four rooms
    assert _openings(building, "L-1") == {"door": 4, "window": 4, "opening": 2}


def test_alternative_basement_rooms_twins_and_same_as(building):
    labels = {"Banyo": 2, "Oda": 2, "Koridor": 2, "Açık Mutfak": 2}
    rooms = _rooms(building, "L-1b")
    assert Counter(r["label"] for r in rooms) == labels
    assert _twins(building, "L-1b") == {k: 1 for k in labels}
    assert _openings(building, "L-1b") == {"door": 4, "window": 2, "opening": 2}
    # Açık Mutfak and Salon share one face (nothing drawn between them): first label kept, unverified, SALON listed.
    assert all(r["status"] == "unverified" for r in rooms if r["label"] == "Açık Mutfak")
    assert any(w.startswith("L-1b: room 'Açık Mutfak' has more labels: SALON") for w in building["warnings"])
    base = {r["id"]: r for r in _rooms(building, "L-1")}
    same = {r["id"]: r["same_as"] for r in rooms if r.get("same_as")}
    assert len(same) == 2 and all(base[b]["label"] == "Banyo" for b in same.values())
    variant = building["variants"][1]
    assert sorted(variant["rooms_changed"]) == sorted(r["id"] for r in rooms if r["id"] not in same)


def test_exterior_changed_only_by_the_kitchen_side_windows(building):
    variant = building["variants"][1]
    alt_w, alt_o = _exterior(building, "L-1b")
    base_w, base_o = _exterior(building, "L-1")
    assert len(alt_w) == len(base_w) == 4                                     # the outer walls, full length
    assert all(any(_same_wall(a, c) for c in base_w) for a in alt_w)
    assert all(any(_same_wall(c, a) for a in alt_w) for c in base_w)
    assert all(any(_same_opening(a, c) for c in base_o) for a in alt_o)
    extra = [c for c in base_o if not any(_same_opening(c, a) for a in alt_o)]
    assert sorted((c["type"], round(c["width"], 2)) for c in extra) == [("window", 4.16), ("window", 4.16)]
    walls = {w["id"]: w for w in base_w}
    assert all(abs(walls[c["wall_id"]]["start"][0] - walls[c["wall_id"]]["end"][0]) < TOL for c in extra)  # side walls
    assert variant["exterior_changed"] is True


def test_m11_groups_are_split_and_no_counter_is_read_in_a_bedroom(building):
    """Milestone 11 (docs/milestone11.md §1.2 U8, U10, U12): each Salon's "masa" block is a 3.35 m table and 10
    chairs facing it; each L-1 kitchen's counter outline gives four counter legs with the hob on them; the wardrobe
    block of the E.yatak Odası is no kitchen counter."""
    f = building["furniture"]
    for salon in ("r_L-1_salon", "r_L-1_salon_2"):
        pieces = [p for p in f if p["room_id"] == salon]
        tables = [p for p in pieces if p["type"] == "table_dining"]
        chairs = [p for p in pieces if p["type"] == "chair" and p["source"] == "from_documents"]
        assert len(tables) == 1 and tables[0]["status"] == "verified" and len(chairs) == 10
        assert all(p["front_deg"] is not None for p in chairs)
    for kitchen in ("r_L-1_mutfak", "r_L-1_mutfak_2"):
        counters = [p for p in f if p["room_id"] == kitchen and p["type"] == "kitchen_counter"]
        assert len(counters) == 4 and all(p["front_deg"] is not None for p in counters)
        assert [p["type"] for p in f if p["room_id"] == kitchen and p["type"] == "stove"] == ["stove"]
    assert not [p for p in f if p["type"] == "kitchen_counter" and "yatak" in (p["room_id"] or "")]
