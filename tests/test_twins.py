"""Mirror twins of a semi-detached pair and the rooms an alternative level shares with its base
(``wenart.ingest.twins``, docs/milestone10.md §1.1, §3.2 items 6-7)."""
from __future__ import annotations

from wenart.ingest import twins as TW


def room(rid, level, label, x0, y0, x1, y1):
    return {"id": rid, "level_id": level, "label": label, "label_raw": label.upper(),
            "polygon": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]}


def door(oid, level, x, y, width=0.9):
    return {"id": oid, "level_id": level, "type": "door", "center": [x, y], "width": width}


def piece(fid, level, room_id, ptype, x, y):
    return {"id": fid, "level_id": level, "room_id": room_id, "type": ptype, "source": "from_documents",
            "footprint": {"center": [x, y], "size": [1.6, 2.0], "rotation_deg": 0.0}}


def pair():
    """Two dwellings mirrored about x = 7.585 (real02's party wall), each a bedroom and a hall."""
    rooms = [room("r_L0_yatak", "L0", "Yatak Odası", 0.2, 0.2, 4.0, 4.5),
             room("r_L0_yatak_2", "L0", "Yatak Odası", 11.17, 0.2, 14.97, 4.5),
             room("r_L0_hol", "L0", "Hol", 4.1, 0.2, 7.4, 3.0),
             room("r_L0_hol_2", "L0", "Hol", 7.77, 0.2, 11.07, 3.0)]
    openings = [door("d_L0_001", "L0", 2.0, 4.5), door("d_L0_002", "L0", 13.17, 4.5)]
    furniture = [piece("f_L0_001", "L0", "r_L0_yatak", "bed_double", 1.5, 2.0),
                 piece("f_L0_002", "L0", "r_L0_yatak_2", "bed_double", 13.67, 2.0)]
    return rooms, openings, furniture


def test_mirrored_pair_is_found_and_the_second_twin_points_at_the_first():
    rooms, openings, furniture = pair()
    assert TW.mirror_twins(rooms, openings, furniture) == {"r_L0_yatak_2": "r_L0_yatak", "r_L0_hol_2": "r_L0_hol"}


def test_a_moved_door_or_piece_breaks_the_twin():
    rooms, openings, furniture = pair()
    openings[1]["center"] = [13.0, 4.5]
    assert "r_L0_yatak_2" not in TW.mirror_twins(rooms, openings, furniture)
    rooms, openings, furniture = pair()
    furniture[1]["type"] = "bed_single"
    assert "r_L0_yatak_2" not in TW.mirror_twins(rooms, openings, furniture)
    rooms, openings, furniture = pair()
    rooms[1]["polygon"][1][0] += 0.05                       # 5 cm wider: no twin
    assert "r_L0_yatak_2" not in TW.mirror_twins(rooms, openings, furniture)


def test_twins_are_deterministic_and_per_level():
    rooms, openings, furniture = pair()
    first = TW.mirror_twins(rooms, openings, furniture)
    assert TW.mirror_twins(list(reversed(rooms)), openings, furniture) == first
    other = [dict(r, level_id="L1", id=r["id"].replace("L0", "L1")) for r in rooms[:1]]
    assert TW.mirror_twins(rooms[:1] + other, [], []) == {}


def test_same_as_on_an_alternative_level():
    base, openings, furniture = pair()
    alt = [dict(r, id=r["id"].replace("L0", "L0b"), level_id="L0b") for r in base]
    alt_openings = [dict(o, id=o["id"].replace("L0", "L0b"), level_id="L0b") for o in openings]
    alt_furniture = [dict(f, id=f["id"].replace("L0", "L0b"), level_id="L0b",
                          room_id=f["room_id"].replace("L0", "L0b")) for f in furniture]
    alt[2]["polygon"] = [[4.1, 0.2], [7.4, 0.2], [7.4, 3.5], [4.1, 3.5]]        # the hall changed
    got = TW.same_as(alt, base, openings + alt_openings, furniture + alt_furniture)
    assert got == {"r_L0b_yatak": "r_L0_yatak", "r_L0b_yatak_2": "r_L0_yatak_2", "r_L0b_hol_2": "r_L0_hol_2"}
