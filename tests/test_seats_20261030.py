"""30 Oct 2026, the user's review of real04 run 20261030-112241-full. UL193 "I did not like the chair" (a bedroom desk's
black mesh "Physio Approved Ergonomic 2 Lever Office Chair"); UL194 "I did not like this sofa" (the open-kitchen
salons' drawn 2.13 x 0.90 m sofas took a front along their length, so no library sofa fitted and the parametric box was
built). Pure tests; real04 is only the test case."""
import _m11_room as M
from wenart.furniture import fit as F
from wenart.furniture import infer as I


def _chair(title):
    return {"id": "c", "type": "office_chair", "title": title}


def test_a_home_desk_takes_a_residential_chair_first():
    for title in ("Office Hippo Physio Approved Ergonomic 2 Lever Office Chair", "AmazonBasics Mesh Fabric Executive "
                  "Mid-Back Office Desk Chair", "UMI. Essentials Gaming High Back Office Desk Racing Chair"):
        assert F.desk_chair_misfit(_chair(title), "office_chair"), title
    for title in ("Amazon Brand - Rivet Bertha Mid-Century Velvet-Upholstered Swivel Office Chair",
                  "Herman Miller Eames Executive Chair from Smart Furniture", "Phoebe Office Chair, Blue"):
        assert F.desk_chair_misfit(_chair(title), "office_chair") is None, title
    assert F.desk_chair_misfit(_chair("Mesh chair"), "chair") is None            # only desk chairs
    flags = F.taste_flags([_chair("Ergonomic Mesh Office Chair")], "office_chair", False, "modern")
    assert flags["c"]["misfit"]


def test_an_elongated_piece_without_a_front_faces_from_a_long_side():
    sofa = M.fp("s1", "sofa", (2.5, 2.0), (2.13, 0.9), rotation=90.0, front=None)
    chair = M.fp("a1", "armchair", (2.5, 3.6), (0.8, 0.8), rotation=0.0, front=None)
    b = M.building(w=5.0, h=6.0, room_type="living", furniture=[sofa, chair], window=None)
    I.missing_fronts(b)
    s = next(f for f in b["furniture"] if f["id"] == "s1")
    w, d = s["footprint"]["size"]
    assert w > d and s["front_deg"] is not None and s["adjusted_by_ai"]["rule"] == "missing_front"
    assert s["drawn_footprint"]["size"] == [2.13, 0.9]
    long_piece = I.placer.drawn_piece(dict(sofa, front_deg=0.0))
    assert I._long_side_turns(long_piece) == (0, 2) and I._long_side_turns(I.placer.drawn_piece(chair)) == (0, 1, 2, 3)
