"""Verandas and terraces furnished like the ones in good photos (27 Oct 2026, lesson UL42; user: "veranda is not like
a veranda"): ``outdoor_sets.plan_space`` / ``furnish`` on a toy veranda and on real06's run building."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
from shapely.geometry import Point

from wenart.furniture import outdoor_sets as O

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "runs" / "20261027-091638-full" / "results" / "furniture" / "real06" / "building_final.json"


def toy(doors=((3.0, 4.1),), steps=True, columns=()):
    """A house 8 x 4 m (rooms y 0.1..4) with a 6 x 3.5 m veranda in front of it (y -3.5..0)."""
    b = {"rooms": [{"id": "r1", "level_id": "L0", "room_type": "living",
                    "polygon": [[0, 0.25], [8, 0.25], [8, 4], [0, 4]]}],
         "openings": [{"id": f"d{i}", "center": [x, 0.1]} for i, (x, _y) in enumerate(doors)],
         "furniture": [], "decor": [],
         "site": {"outdoor_spaces": [{"id": "os_v", "kind": "veranda", "label": "VERANDA", "level_id": "L0",
                                      "polygon": [[1, -3.5], [7, -3.5], [7, 0], [1, 0]],
                                      "doors": [f"d{i}" for i in range(len(doors))],
                                      "columns": [{"id": f"c{i}", "center": list(c), "size_m": 0.3}
                                                  for i, c in enumerate(columns)],
                                      "roof": {"polygon": [[1, -3.5], [7, -3.5], [7, 0], [1, 0]]}}]}}
    if steps:
        b["site"]["outdoor_spaces"][0]["steps"] = {"edge": [[2.0, -3.5], [3.0, -3.5]]}
    return b


def test_a_lounge_backs_onto_the_house_clear_of_doors_steps_and_the_walkway():
    b = toy()
    space = b["site"]["outdoor_spaces"][0]
    plan = O.plan_space(space, b)
    assert plan["set"] in ("lounge", "lounge_side") and [p["type"] for p in plan["pieces"]][:2] == ["sofa",
                                                                                                    "table_coffee"]
    sofa = plan["pieces"][0]
    assert sofa["center"][1] > -1.0                                    # its back to the house wall (y = 0)
    assert sofa["front_deg"] == pytest.approx(270.0)                   # facing the garden (-y)
    assert (sofa["rotation_deg"] + 270.0) % 360.0 == pytest.approx(sofa["front_deg"])
    door = Point(3.0, 0.1)
    for p in plan["pieces"]:
        assert Point(p["center"]).distance(door) > O.DOOR_CLEAR_M
    # 28 Oct 2026 (user on real04's roof terrace: "makes no sense to have that table with the carpet outside"): no rug
    assert plan["rug"] is None and plan["planters"] and plan["covered"] == 1.0
    assert any(n.startswith("no rug") for n in plan["notes"])


def test_furnish_adds_pieces_and_decor_once():
    out, notes = O.furnish(toy())
    pieces = [f for f in out["furniture"] if f.get("outdoor_space") == "os_v"]
    assert {f["type"] for f in pieces} >= {"sofa", "table_coffee"} and all(f["open_air"] for f in pieces)
    assert all(f["source"] == "added_by_ai" and f["evidence"][0]["method"] == "inferred" for f in pieces)
    decor = [d for d in out["decor"] if d.get("outdoor_space") == "os_v"]
    assert {"plant_large", "candle"} <= {d["type"] for d in decor} and "lounge set" in notes[0]
    assert "rug" not in {d["type"] for d in decor} and "no rug" in notes[0]          # 28 Oct 2026: no rug outside
    again, notes2 = O.furnish(out)
    assert len(again["furniture"]) == len(out["furniture"]) and not notes2      # furnished already


def test_too_small_or_blocked_spaces_get_no_set():
    b = toy()
    b["site"]["outdoor_spaces"][0]["polygon"] = [[1, -1.5], [2.5, -1.5], [2.5, 0], [1, 0]]
    assert O.plan_space(b["site"]["outdoor_spaces"][0], b)["pieces"] == []
    b = toy(doors=[(x + 0.5, 0) for x in range(1, 7)])                 # a door every metre: no wall is free
    plan = O.plan_space(b["site"]["outdoor_spaces"][0], b)
    assert plan["set"] != "lounge" or plan["pieces"][0]["center"][1] < -1.0


@pytest.mark.skipif(not REAL06.is_file(), reason="no real06 run building")
def test_real06_veranda_gets_a_lounge_and_planters():
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    out, notes = O.furnish(b)
    pieces = [f for f in out["furniture"] if f.get("outdoor_space") == "os_L0_veranda"]
    assert len(pieces) == 4 and any("os_L0_veranda: lounge set" in n for n in notes)
    space = b["site"]["outdoor_spaces"][0]
    poly = O._poly(space["polygon"])
    for f in pieces:
        fp = f["footprint"]
        rect = O._rect(fp["center"][0], fp["center"][1], fp["size"][0], fp["size"][1],
                       math.radians(fp["rotation_deg"]))
        assert poly.contains(rect)


def test_the_decor_debug_draws_an_outdoor_space(tmp_path):
    """Pod run 123917: ``decor_ai apply --debug`` stopped on the veranda's record (no room of that id)."""
    from wenart.furniture import decor_ai as DA

    out, notes = O.furnish(toy())
    rec = DA.RoomDecor("os_v", "VERANDA", "veranda")
    rec.items = [d for d in out["decor"] if d.get("outdoor_space") == "os_v"]
    DA.write_room_debug(rec, out, tmp_path)
    assert (tmp_path / "os_v.json").is_file() and (tmp_path / "os_v.png").is_file()
    DA.write_room_debug(DA.RoomDecor("nowhere", "x", "other"), out, tmp_path)      # no polygon: JSON only
    assert (tmp_path / "nowhere.json").is_file() and not (tmp_path / "nowhere.png").exists()
