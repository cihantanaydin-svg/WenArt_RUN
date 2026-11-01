"""1 Nov 2026 (lesson UL235, user on a sloped-site house, the stacked stone on one wall of its lowest floor: "this was
nice wall it can be used all around the same floor"). A cladding the facade puts on some outside walls of a floor (an
inferred face, or the plinth's raised base rising from the low ground to the floor above) goes on every outside wall of
that floor; the floors above keep their own look; a wall the documents give a face keeps it. Pure CPU tests; real04 is
only the test case (``test_real04_lowest_floor_takes_the_stone_all_round`` skips when its baseline is missing)."""
import json
from pathlib import Path

import pytest

from wenart.blender import build as B
from wenart.blender import facade as FA

STONE = "stone_wall_ledgestone"
PLINTH_LOOK = {"material": STONE, "colour": None, "source": "build", "assumed": True}
AGENT_RENDER = {"material": "render", "colour": None, "source": "agent"}
# the outer wall faces of a 10 x 8 m house whose front and back walls run past the side walls (as the walls' outline
# comes out of real drawings: a 0.1 m jog at each corner)
OUTLINE = [(-0.1, 0.0), (10.1, 0.0), (10.1, 0.2), (10.0, 0.2), (10.0, 7.8), (10.1, 7.8), (10.1, 8.0), (-0.1, 8.0),
           (-0.1, 7.8), (0.0, 7.8), (0.0, 0.2), (-0.1, 0.2)]


def _ring(lid: str) -> list[dict]:
    """The four outside walls of a level (0.2 m thick, on ``OUTLINE``)."""
    return [{"id": f"w_{lid}_s", "level_id": lid, "start": [-0.1, 0.1], "end": [10.1, 0.1], "thickness": 0.2},
            {"id": f"w_{lid}_e", "level_id": lid, "start": [9.9, 0.2], "end": [9.9, 7.8], "thickness": 0.2},
            {"id": f"w_{lid}_n", "level_id": lid, "start": [10.1, 7.9], "end": [-0.1, 7.9], "thickness": 0.2},
            {"id": f"w_{lid}_w", "level_id": lid, "start": [0.1, 7.8], "end": [0.1, 0.2], "thickness": 0.2}]


def _house() -> dict:
    """A basement at -3 m, a ground floor at 0 m and a first floor at 3 m on the same ring; an inner wall in the
    basement; the pipeline's plinth rule (the raised base up to the lowest floor at or above the ground)."""
    levels = [{"id": "L-1", "kind": "basement", "elevation": -3.0, "ceiling_height": 2.8},
              {"id": "L0", "kind": "floor", "elevation": 0.0, "ceiling_height": 2.8},
              {"id": "L1", "kind": "floor", "elevation": 3.0, "ceiling_height": 2.8}]
    walls = _ring("L-1") + _ring("L0") + _ring("L1")
    walls.append({"id": "w_L-1_in", "level_id": "L-1", "start": [5.0, 0.2], "end": [5.0, 7.8], "thickness": 0.1})
    return {"levels": levels, "walls": walls, "openings": [],
            "site": {"plinth": {"top_z": 0.0, "floors": [-3.0, 0.0], "min_height": 0.15}}}


def _terrain(east: float = -2.6, rest: float = -0.3) -> dict:
    """The ground at ``rest`` around the house, and at ``east`` along its east wall only (a stand: the low side by a
    sunken terrace; the corners keep ``rest``, so only the east edge of the outline lies low)."""
    return {"kind": "flat", "z": {"+x": rest, "-x": rest, "+y": rest, "-y": rest},
            "stand": [([(9.95, 0.15), (10.05, 0.15), (10.05, 7.85), (9.95, 7.85)], east)]}


def _outlines() -> dict:
    return {"L-1": OUTLINE, "L0": OUTLINE, "L1": OUTLINE}


def _ids(faces) -> list[str]:
    return sorted(f["wall_id"] for f in faces)


def test_is_cladding_is_any_finish_that_is_not_a_render():
    assert all(FA.is_cladding(s) for s in (STONE, "stone_wall_slate", "brick_red", "wood_cladding", "fibre_cement"))
    assert not any(FA.is_cladding(s) for s in ("render", "paint", "lime_plaster", "plaster_exterior", None, "no_such"))


def test_the_plinth_clads_the_lowest_floor_only_where_the_ground_lies_low():
    b = _house()
    got = FA.plinth_storeys(b, b["levels"], _outlines(), OUTLINE, _terrain())
    assert list(got) == ["L-1"] and len(got["L-1"]) == 1             # the east edge only; no floor above
    s = got["L-1"][0]
    assert s["p"][0] == pytest.approx(10.0) and s["q"][0] == pytest.approx(10.0)
    assert s["height_m"] == pytest.approx(2.6) and s["length_m"] == pytest.approx(7.6)
    # a low plinth (0.3 m over the ground everywhere) is a base band, never a storey cladding
    assert FA.plinth_storeys(b, b["levels"], _outlines(), OUTLINE, _terrain(east=-0.3)) == {}
    # the Milestone 11 band (no plinth rule) never clads a storey
    old = dict(b, site={})
    assert FA.plinth_storeys(old, old["levels"], _outlines(), OUTLINE, _terrain()) == {}
    # glazing across the low stretch: less than STOREY["min_length_m"] of stone shows, the wall stays as it is
    glazed = dict(b, openings=[{"id": "win_e", "type": "window", "wall_id": "w_L-1_e", "level_id": "L-1",
                                "center": [9.9, 4.0], "width": 7.0, "sill_height": 0.3, "height": 2.4}])
    assert FA.plinth_storeys(glazed, glazed["levels"], _outlines(), OUTLINE, _terrain()) == {}


def test_one_clad_wall_of_a_floor_clads_every_outside_wall_of_that_floor():
    b = _house()
    stretches = FA.plinth_storeys(b, b["levels"], _outlines(), OUTLINE, _terrain())
    faces, records = FA.storey_claddings(b, b["levels"], _outlines(), {}, stretches, PLINTH_LOOK, AGENT_RENDER)
    assert _ids(faces) == ["w_L-1_e", "w_L-1_n", "w_L-1_s", "w_L-1_w"]   # around the corners, never the inner wall
    assert all(f["material"] == STONE and f["level_id"] == "L-1" and f["inferred"] and f["source"] == "inferred"
               and f["storey_cladding"] and f["side"] == "all" for f in faces)
    assert not [f for f in faces if f["level_id"] != "L-1"]               # the floors above keep their look
    assert [(r["level_id"], r["from"], r["seen_on"]) for r in records] == [("L-1", "plinth", ["w_L-1_e"])]
    assert "UL235" in records[0]["reason"] and "w_L-1_e" in records[0]["reason"]
    # the build maps them onto the same walls (build.facade_faces: a face with its wall_id)
    mapped, warnings = B.facade_faces(dict(b, facade={"faces": faces}), _outlines())
    assert sorted(mapped) == ["w_L-1_e", "w_L-1_n", "w_L-1_s", "w_L-1_w"] and warnings == []


def test_a_wall_with_a_drawn_face_keeps_it_and_a_clad_floor_takes_nothing_more():
    b = _house()
    stretches = FA.plinth_storeys(b, b["levels"], _outlines(), OUTLINE, _terrain())
    drawn = {"w_L-1_w": [{"material": "render", "colour": "white", "side": "west", "source": "documents",
                          "direction": [-1.0, 0.0]}]}
    faces, _ = FA.storey_claddings(b, b["levels"], _outlines(), drawn, stretches, PLINTH_LOOK, AGENT_RENDER)
    assert _ids(faces) == ["w_L-1_e", "w_L-1_n", "w_L-1_s"]              # the documents' wall keeps its own face
    # the scheme's base already on every basement wall: nothing to add (one cladding, not a second one)
    base = {w["id"]: [{"material": "stone_wall_slate", "colour": None, "side": "all", "level_id": "L-1",
                       "source": "inferred", "inferred": True, "direction": None}]
            for w in b["walls"] if w["level_id"] == "L-1"}
    assert FA.storey_claddings(b, b["levels"], _outlines(), base, stretches, PLINTH_LOOK, AGENT_RENDER) == ([], [])


def test_an_inferred_face_on_part_of_a_floor_goes_all_round_but_an_accent_band_stays_a_band():
    b = _house()
    part = {"w_L0_s": [{"material": "brick_red", "colour": None, "side": "all", "wall_id": "w_L0_s",
                        "source": "inferred", "inferred": True, "direction": None}]}
    faces, records = FA.storey_claddings(b, b["levels"], _outlines(), part, {}, PLINTH_LOOK, AGENT_RENDER)
    assert _ids(faces) == ["w_L0_e", "w_L0_n", "w_L0_w"] and {f["material"] for f in faces} == {"brick_red"}
    assert [(r["level_id"], r["from"], r["seen_on"]) for r in records] == [("L0", "facade", ["w_L0_s"])]
    # the scheme's accent framing the entrance (a span and a height band) and a render face spread nowhere
    accent = {"w_L0_s": [{"material": "wood_cladding", "colour": None, "side": "all", "wall_id": "w_L0_s",
                          "span": [[3.0, 0.0], [6.0, 0.0]], "z_range": [-0.5, 3.0], "source": "inferred",
                          "inferred": True, "direction": None}],
              "w_L1_n": [{"material": "render", "colour": "cream", "side": "all", "wall_id": "w_L1_n",
                          "source": "inferred", "inferred": True, "direction": None}]}
    assert FA.storey_claddings(b, b["levels"], _outlines(), accent, {}, PLINTH_LOOK, AGENT_RENDER) == ([], [])


def test_a_named_facade_keeps_the_plinth_a_base_and_a_clad_facade_takes_nothing():
    b = _house()
    stretches = FA.plinth_storeys(b, b["levels"], _outlines(), OUTLINE, _terrain())
    for source in FA.NAMED_SOURCES:                                    # the documents, the brief or the style
        look = {"material": "render", "colour": "white", "source": source}
        assert FA.storey_claddings(b, b["levels"], _outlines(), {}, stretches, PLINTH_LOOK, look) == ([], [])
    for source in ("fallback", "agent"):                               # the scheme's default or the agent's render
        look = {"material": "render", "colour": "off white", "source": source}
        assert len(FA.storey_claddings(b, b["levels"], _outlines(), {}, stretches, PLINTH_LOOK, look)[0]) == 4
    clad = {"material": "wood_cladding", "colour": None, "source": "agent"}
    assert FA.storey_claddings(b, b["levels"], _outlines(), {}, stretches, PLINTH_LOOK, clad) == ([], [])
    render_plinth = {"material": "render", "colour": "grey"}
    assert FA.storey_claddings(b, b["levels"], _outlines(), {}, stretches, render_plinth, AGENT_RENDER) == ([], [])


# ----------------------------------------------------------------------------------------------- the real04 case

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "baseline" / "latest" / "furniture" / "real04" / "building_final.json"
RUNS = ROOT / "results" / "baseline" / "latest" / "runs.json"


def test_real04_lowest_floor_takes_the_stone_all_round():
    """real04 (run 20261031-194116-full): the agent set the facade slot to render, so the scheme's basement stone was
    not built; the plinth rose 2.6 m from the low ground by the pool to the ground floor on the east wall of L-1 only.
    Now every outside wall of L-1 takes that stone; L0 and L1 keep their render."""
    if not REAL04.is_file():
        pytest.skip(f"{REAL04} not on this machine")
    from wenart.blender import exterior as E
    from wenart.blender import overrides as O

    building_all = json.loads(REAL04.read_text(encoding="utf-8"))
    style = {"family": "modern"}
    prep = B.prepare(building_all, "base", None, style_family="modern")
    b = prep["building"]
    levels = sorted(b["levels"], key=lambda lv: float(lv["elevation"]))
    looks, _ = O.apply_looks(E.resolve_looks(b, style, None), O.materials_of(building_all))
    site = prep["site"] or {}
    stretches = FA.plinth_storeys(b, levels, prep["outlines"], prep["ground_outline"], site.get("terrain"),
                                  site.get("wells") or [])
    faces, records = FA.storey_claddings(b, levels, prep["outlines"], prep["faces"], stretches,
                                         FA.plinth_look(style, looks), looks.get("facade"))
    lowest = levels[0]["id"]
    for rec in records:                       # a clad floor is clad on every outside wall
        outer = {w["id"] for w in FA.outer_walls(b, next(lv for lv in levels if lv["id"] == rec["level_id"]),
                                                    prep["outlines"][rec["level_id"]])}
        assert set(rec["walls"]) == outer
    assert not [f for f in faces if f["level_id"] != lowest]           # the floors above keep their own look
    job = json.loads(RUNS.read_text(encoding="utf-8")).get("real04", {}).get("job") if RUNS.is_file() else None
    if job != "20261031-194116-full":
        return                                # another baseline: the general checks above hold
    assert looks["facade"]["source"] == "agent" and lowest == "L-1"
    assert [(r["level_id"], r["material"], r["from"], r["seen_on"]) for r in records] == \
        [("L-1", STONE, "plinth", ["w_L-1_015"])]
    assert _ids(faces) == ["w_L-1_001", "w_L-1_006", "w_L-1_007", "w_L-1_015"]
