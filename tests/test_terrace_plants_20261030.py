"""A terrace gets plants, never a table and chairs the rules add (30 Oct 2026, lesson UL130, user on real04 run
20261029-201533-full: "Terras does not need table and chairs maybe only some plants and decor for outside would be
enough")."""
from wenart.furniture import groups as GR
from wenart.furniture import program as PR


def test_the_terrace_group_is_plants_in_big_pots():
    g = GR.load_groups()["balcony"]
    assert g["anchor"]["types"] == ["potted_plant"]
    types = {p["type"] for p in g.get("partners") or []}
    assert types == {"potted_plant"} and "table" not in g["what"].split(";")[0]
    assert set(g["options"]) >= {"planters", "planters_2", "planters_3"}


def test_the_terrace_program_offers_the_planters():
    from shapely.geometry import Polygon

    room = {"id": "r_t", "room_type": "balcony", "polygon": [[0, 0], [3, 0], [3, 2], [0, 2]]}
    rows = PR._core_rows("balcony", 6.0, Polygon(room["polygon"]), {"rooms": [room], "furniture": []}, room, None)
    # 30 Oct 2026 (UL152, the P15 terrace): a 2 m wide terrace also takes the pair of armchairs; never a table
    assert rows == [("balcony", False, ["planters"]), ("terrace_pair", False, ["lounge_pair"])]
