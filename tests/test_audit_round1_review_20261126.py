"""Review of audit fix round 1 (26 Nov 2026): the five defects an independent reviewer found in the merged round.

1. A roof terrace's parapet wall partly under the roof (``sheets.to_building``) keeps the roof cut: only the guards
   ``ingest.edge_guards`` made (``guard_of``) skip it.
2. An elevated outdoor space whose edge runs along its guard wall gets no second railing there (``site.guarded_edges``).
3. A typical copy that keeps only the fixed equipment carries no decor or built-in record of pieces it lacks.
4. A bare 'Havalandırma' names a void only on a room typed shaft ('Havalandırma Odası' is a plant room).
5. An open-air room is a landing only when its own floor lies within the tolerance of the door's floor.
"""
from __future__ import annotations

import inspect

from wenart.blender import outdoor as OD
from wenart.blender import shell
from wenart.blender import site as S
from wenart.blender import typical_copies as TC


def test_only_edge_guards_skip_the_roof_cut():
    src = inspect.getsource(shell.build_walls)
    assert 'guard_wall = bool(wall.get("parapet") and wall.get("guard_of"))' in src
    # the under-roof manifest entry keeps its z range
    assert src.count('entry["z_range"] = [round(wz, 4), round(wz + height, 4)]') == 2


def test_a_guard_wall_takes_the_railing_off_its_platform_edge():
    square = [[5.0456, 9.35], [6.5, 9.35], [6.5, 11.0], [5.0456, 11.0]]
    wall = {"id": "w_L1_042", "start": [5.0206, 8.3], "end": [5.0206, 11.0], "thickness": 0.05,
            "guard_of": "os_L1_balkon_1"}
    assert S.guarded_edges(square, [wall]) == [3]               # the west edge (from point 3 back to point 0)
    far = dict(wall, start=[4.5, 8.3], end=[4.5, 11.0])
    assert S.guarded_edges(square, [far]) == []
    crossing = dict(wall, start=[4.0, 10.0], end=[7.0, 10.0])   # not parallel to the west edge
    assert 3 not in S.guarded_edges(square, [crossing])
    assert "guard_walls" in inspect.signature(S.platforms).parameters


def test_a_fixed_only_copy_carries_no_foreign_decor_or_built_ins():
    summary = {"pieces": 9, "decor": 4, "decor_not_rested": [{"id": "dec_L1_007", "host": "f_L1_050"}],
               "built_in": [{"id": "f_L1_012", "host": "f_L1_011"}, {"id": "f_L1_060", "host": "f_L1_050"}],
               "fallbacks": [], "not_built": []}
    s = TC.copy_summary(summary, "L1", "L2", {}, only=["f_L1_012"])
    assert s["decor_not_rested"] == []
    assert [x["id"] for x in s["built_in"]] == ["f_L2_012"]


def test_ventilation_words():
    assert not OD.is_void({"room_type": "other", "label": "Havalandırma Odası"})
    assert not OD.is_void({"room_type": "shaft", "label": "Havalandırma Odası"})
    assert OD.is_void({"room_type": "shaft", "label": "Havalandırma"})
    assert OD.is_void({"room_type": "other", "label": "Havalandırma Boşluğu"})
    assert OD.is_void({"room_type": "shaft", "label": "H.B 50X50"})
    assert not OD.is_void({"room_type": "shaft", "label": "Asansör"})


def test_an_open_air_room_lands_a_door_only_at_its_floor():
    b = {"levels": [{"id": "L0", "elevation": 0.0}],
         "rooms": [{"id": "r_L0_teras", "level_id": "L0", "room_type": "terrace",
                    "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]], "floor_offset_m": 0.0}]}
    got = S.landing_at(b, "L0", (2.0, 1.0), 0.1)
    assert got is not None and got["id"] == "r_L0_teras" and got["z"] == 0.0
    assert S.landing_at(b, "L0", (2.0, 1.0), 0.6) is None      # a door 0.6 m up: the terrace is a full step below
