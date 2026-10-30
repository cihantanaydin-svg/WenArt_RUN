"""UL180 (30 Oct 2026, real04 run 20261030-112241-full, r_L-1_salon): "put some pillows and sheet on to the white sofa
also another carpet could be good here". The white library L-sofa stood bare: the reading had typed its L outline a
corner sofa by rule but left it unverified (larger than the type's size table), so the decor took it for no host; the
audit's has_cushions ("loose or scatter cushions") would have kept its cushions off too; the AI's throw went to an
armchair and the room's one rug lay under the dining table. Pure tests: the rules are general, real04 is only the test
case."""
from __future__ import annotations

from wenart.assets.audit import ask as A
from wenart.assets.audit import decide as DC
from wenart.blender import rest as R
from wenart.furniture import catalog as C
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import room_use as RU

from test_decor_m8 import room_building

STYLE = "modern, light oak, white walls"


def _living(sofa_status: str = "verified", sofa_asset=None):
    """An 8 x 6 m living-dining room: a 2.4 m sofa on the north wall facing south, its coffee table, an armchair facing
    it, a dining table in the south-east."""
    b = room_building(width=8.0, depth=6.0, furniture=[
        ("sofa", (3.0, 5.45), 0.0, (2.4, 0.9), sofa_status), ("table_coffee", (3.0, 4.25), 0.0, (1.1, 0.6)),
        ("armchair", (1.0, 3.4), 90.0, (0.8, 0.8)), ("table_dining", (6.3, 1.5), 0.0, (1.6, 0.9))])
    if sofa_asset is not None:
        b["furniture"][0]["asset"] = sofa_asset
    return b


def _ids():
    n = [0]

    def new_id(level):
        n[0] += 1
        return f"dec_{level}_{n[0]:03d}"
    return new_id


def test_a_built_unverified_piece_hosts_decor_a_proposal_or_an_unbuilt_one_not():
    sofa = {"id": "s", "type": "sofa_corner", "status": "unverified", "evidence": [{"method": "vector"}],
            "type_method": "rule"}
    assert not D.trusted_host(sofa)                                   # the reading's doubt, nothing built yet
    assert D.trusted_host(dict(sofa, asset={"method": "library"}))    # built as a corner sofa: dressed as one
    assert D.trusted_host(dict(sofa, asset={"method": "parametric"}))
    assert not D.trusted_host(dict(sofa, asset={"method": "none"}))
    assert not D.trusted_host(dict(sofa, asset={"method": "library"}, type_proposal=True))
    assert not D.trusted_host(dict(sofa, status="needs_review", asset={"method": "library"}))


def test_loose_seat_cushions_are_not_scatter_cushions():
    assert not C.has_scatter_cushions({"title": "sectional sofa L", "has_cushions": True})
    assert C.has_scatter_cushions({"title": "Modern Sofa with 2 Throw Pillows"})
    assert C.has_scatter_cushions({"title": "Sofa", "has_scatter_cushions": True})
    assert not C.has_scatter_cushions({"title": "Sofa with pillows", "has_scatter_cushions": False})   # the audit says
    loose = {"type": "sofa_corner", "asset": {"method": "library", "has_cushions": True}}
    assert not R.own_cushions(loose) and D.takes_cushions(loose)
    assert R.own_cushions({"type": "sofa", "asset": {"has_scatter_cushions": True}})
    assert R.own_cushions({"type": "bed_double", "asset": {"has_cushions": True}})       # beds as before (UL163)
    assert not C.has_own_cushions({"has_cushions": True}) and C.has_own_cushions({"has_scatter_cushions": True})


def test_the_fit_tells_the_build_whether_a_seat_has_its_own_pillows():
    from test_furniture_fit_v2 import FakeCatalog, model, piece

    from wenart.furniture import fit as F

    loose = model("loose", "sofa", 2.0, 0.9, 0.8, real_product=True, has_cushions=True)
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([loose]))
    assert fit["method"] == "library" and fit["has_cushions"] is True and fit["has_scatter_cushions"] is False
    assert not R.own_cushions({"type": "sofa", "asset": fit})
    pillows = model("pillows", "sofa", 2.0, 0.9, 0.8, real_product=True, has_cushions=True,
                    title="Modern Sofa with 2 Throw Pillows")
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([pillows]))
    assert fit["has_scatter_cushions"] is True and R.own_cushions({"type": "sofa", "asset": fit})


def test_a_corner_sofa_takes_two_to_four_cushions():
    def corner(w):
        return {"id": "c", "type": "sofa_corner", "footprint": {"center": [0.0, 0.0], "size": [w, 1.9],
                                                               "rotation_deg": 0.0}}
    counts = [len([i for i in D.host_decor(corner(w)) if i["type"] == "cushion"]) for w in (1.2, 2.6, 4.4)]
    assert counts == [2, 4, D.CORNER_SOFA_CUSHIONS_MAX] and D.CORNER_SOFA_CUSHIONS_MAX == 4


def test_the_main_sofa_gets_cushions_and_the_throw_and_its_group_a_rug():
    b = _living(sofa_status="unverified", sofa_asset={"method": "library", "has_cushions": True})
    q = {q.room["id"]: q for q in DA.room_questions(b, STYLE)}[b["rooms"][0]["id"]]
    slots = {s.id: s for s in q.slots}
    assert {"f_L0_001.cushions", "f_L0_001.throw"} <= set(slots)        # the built sofa is a host now
    rugs = [s for s in q.slots if s.kind == "rug"]
    seating = [s for s in rugs if s.host_id == "f_L0_001"]
    dining = [s for s in rugs if s.host_id == "f_L0_004"]
    assert seating and dining
    # the AI's own choice in real04: the dining rug, a cushion and the throw on the armchair
    new_id = _ids()
    ai = [{"slot": dining[0].id, "type": "rug", "colour": "beige", "reasons": ["ai"] * 2},
          {"slot": "f_L0_003.cushions", "type": "cushion", "colour": "mustard", "reasons": ["ai"] * 2},
          {"slot": "f_L0_003.throw", "type": "throw", "colour": "cream", "reasons": ["ai"] * 2}]
    items, refused = DA.build_items(q, ai, "m", b, new_id)
    assert not refused and len(items) == 3
    b["decor"] = list(items)
    found, checked = DA.dressing_review(b)
    assert checked == 1 and found and set(found[0]["metrics"]["missing"]) == {"scatter cushions", "throw",
                                                                               "rug under its seating group"}
    dressed, replaced = DA.living_dressing(q, items, b, new_id)
    kinds = sorted(i["type"] for i in dressed)
    assert kinds == ["cushion", "cushion", "rug", "throw"]
    assert all(i["host_id"] == "f_L0_001" for i in dressed if i["type"] != "rug")
    assert all(i["method"] == "rule" and "user: '" in i["reason"] for i in dressed)
    throw = next(i for i in dressed if i["type"] == "throw")
    old = next(i for i in items if i["type"] == "throw")
    assert replaced == {old["id"]} and throw["colour"] == "cream"     # the throw moves, its colour kept
    rug = next(i for i in dressed if i["type"] == "rug")
    assert rug["slot"] == seating[0].id
    b["decor"] = [i for i in items if i["id"] not in replaced] + dressed
    assert DA.dressing_review(b) == ([], 1)
    again, none = DA.living_dressing(q, b["decor"], b, new_id)        # nothing twice
    assert again == [] and none == set()


def test_other_rooms_and_an_already_dressed_sofa_are_left_alone():
    b = _living()
    b["rooms"][0]["room_type"] = "bedroom"
    q = DA.room_questions(b, STYLE)[0]
    assert DA.living_dressing(q, [], b, _ids()) == ([], set())
    b = _living()
    q = DA.room_questions(b, STYLE)[0]
    new_id = _ids()
    ai = [{"slot": "f_L0_001.cushions", "type": "cushion", "colour": None, "reasons": ["ai"] * 2},
          {"slot": "f_L0_001.throw", "type": "throw", "colour": None, "reasons": ["ai"] * 2}]
    items, _ = DA.build_items(q, ai, "m", b, new_id)
    dressed, replaced = DA.living_dressing(q, items, b, new_id)
    assert [i["type"] for i in dressed] == ["rug"] and replaced == set()


def test_the_review_is_part_of_m21():
    b = _living()
    found, _n = RU.review(b)
    assert not [f for f in found if f["metrics"].get("lesson") == "UL180"]     # no decor yet: not judged
    b["decor"] = [{"id": "dec_L0_001", "type": "vase", "room_id": b["rooms"][0]["id"], "host_id": "f_L0_002"}]
    found, _n = RU.review(b)
    mine = [f for f in found if f["metrics"].get("lesson") == "UL180"]
    assert len(mine) == 1 and mine[0]["check"] == "M21" and mine[0]["severity"] == "minor"


def test_the_audit_asks_scatter_cushions_apart_from_m13_4():
    sofa = {"id": "x", "type": "sofa", "kind": "furniture", "source": "abo", "title": "Sofa", "bbox_m": [2, 0.9, 0.8]}
    assert "has_scatter_cushions" not in A.schema("furniture", "m13.3")["properties"]
    assert "has_scatter_cushions" in A.schema("furniture", "m13.4")["properties"]
    old, new = A.prompt(sofa, sofa["bbox_m"], "m13.3"), A.prompt(sofa, sofa["bbox_m"], "m13.4")
    assert "loose or scatter cushions" in old and "has_scatter_cushions" not in old
    assert "loose seat or back cushions" in new and "has_scatter_cushions: true when" in new
    assert A.version_for(sofa, {"version": "m12.1", "version_seats": "m13.4"}) == "m13.4"
    assert A.version_for(dict(sofa, material_tags=["fabric"]), {"version": "m12.1"}) == "m12.1"   # opt-in
    flags = DC.answer_flags(sofa, {"has_cushions": True, "has_scatter_cushions": False})
    assert flags["has_cushions"] is True and flags["has_scatter_cushions"] is False
