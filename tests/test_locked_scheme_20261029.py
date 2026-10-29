"""A room's design scheme is no drawn data (29 Oct 2026: real04 run 20261029-185352-full stopped at the refit's locked
check: the decor stage's room schemes, ``room["scheme"]``, made every room "changed")."""
import copy

from wenart.furniture import locked as L

ROOM = {"id": "r1", "level_id": "L0", "label": "SALON", "room_type": "living",
        "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]], "evidence": [{"file": "plan.dxf", "method": "vector"}]}


def test_a_scheme_written_into_a_room_keeps_it_as_drawn():
    source = {"rooms": [ROOM], "walls": [], "openings": []}
    final = copy.deepcopy(source)
    final["rooms"][0]["scheme"] = {"name": "gallery", "colour": "pale muted sage"}
    assert L._block_problems(source, final) == []


def test_a_drawn_room_change_is_still_found():
    source = {"rooms": [ROOM], "walls": [], "openings": []}
    final = copy.deepcopy(source)
    final["rooms"][0]["scheme"] = {"name": "gallery"}
    final["rooms"][0]["polygon"] = [[0, 0], [5, 0], [5, 3], [0, 3]]
    assert L._block_problems(source, final) == ["rooms: must stay as drawn (byte-equal): changed r1"]
