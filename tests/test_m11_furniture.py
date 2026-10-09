"""Milestone 11 furniture-stage changes (docs/milestone11.md §1.1 E2, §1.2 U10, U13, §3.2 swap_model): seats get a
front clearance, an unverified table asks for no chairs, a rug outline is no obstacle, the fit honours the agent's
pinned model, and the decor placer keeps floor items under the sloped attic ceiling (real02's committed building)."""
import json
from pathlib import Path

import pytest

import _m11_room as M
from test_furniture_fit_v2 import FakeCatalog, model, piece
from wenart.furniture import complete as C
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import fit as F
from wenart.furniture import placer as P
from wenart.furniture import schemas

REAL02 = Path(__file__).resolve().parents[1] / "results" / "furniture" / "real02" / "building_final.json"


def test_an_armchair_needs_a_front_clearance_but_a_coffee_table_may_stand_there():
    # U13: an added armchair stood 1 cm behind a sofa back, facing it (no seat had a front clearance).
    b = M.building(room_type="living")
    ctx = P.room_context(b, b["rooms"][0])
    sofa = P.Piece("sofa", (2.5, 2.0), 0.0, (2.2, 0.9), False)            # back at y = 2.45
    chair = P.Piece("armchair", (2.5, 1.0), 180.0, (0.9, 0.9), False)     # faces +Y: its zone overlaps the sofa
    checks = P.check_all([sofa, chair], ctx)
    assert checks[1]["clearance_ok"] is False
    table = P.Piece("table_coffee", (2.5, 1.85), 0.0, (1.0, 0.6), False)
    chair2 = P.Piece("armchair", (2.5, 1.0), 180.0, (0.9, 0.9), False)
    assert P.check_all([table, chair2], ctx)[1]["clearance_ok"] is True
    assert chair.front_zone().bounds[3] == pytest.approx(1.45 + schemas.CLEARANCE_DEPTH_M["armchair"])


def test_an_unverified_table_asks_for_no_chairs():
    sure = schemas.completion_plan("living", None, [("sofa", (2.2, 0.9)), ("table_dining", (1.6, 0.9), False)])
    assert sure["missing"].get("chair") == 6
    unsure = schemas.completion_plan("living", None, [("sofa", (2.2, 0.9)), ("table_dining", (3.35, 1.57), True)])
    assert "chair" not in unsure["missing"] and "chair" not in unsure["addable"]
    dining = schemas.completion_plan("dining", None, [("table_dining", (3.35, 1.57), True)])
    assert "chair" not in dining["missing"]
    # The two-value form of earlier callers still works.
    assert schemas.completion_plan("living", None, [("table_dining", (1.6, 0.9))])["missing"]["chair"] == 6


def test_a_rug_outline_is_no_obstacle_of_the_completion_and_no_rug_blocker():
    outline = M.fp("u1", "unknown", (2.5, 2.0), (3.0, 2.2), front=None, status="unverified", build=False,
                   inferred=True, inferred_as="rug")
    sofa = M.fp("s1", "sofa", (2.5, 0.47), (2.2, 0.9), rotation=180.0, front=90.0)
    b = M.building(room_type="living", furniture=[outline, sofa])
    kinds = {d.id: d.kind for d in C.classify_drawn(b["rooms"][0], b)}
    assert kinds == {"u1": "outline", "s1": "changeable"}
    ctx = P.room_context(b, b["rooms"][0])
    zone = D._rug_forbidden(ctx, b["furniture"], [])
    assert zone is None or zone.intersection(P.piece_from_furniture(outline).polygon()).area < 0.5


def test_the_fit_takes_the_agents_pinned_model_when_it_passes_the_rules():
    cat = FakeCatalog([model("exact", "sofa", 2.0, 0.9, 0.8, quality=2.0),
                       model("other", "sofa", 2.05, 0.92, 0.8, quality=5.0)])
    assert F.fit_piece(piece("sofa", 2.0, 0.9), cat)["asset_id"] == "abo_other"
    pinned = dict(piece("sofa", 2.0, 0.9), asset_pin="abo_exact")
    fit = F.fit_piece(pinned, cat)
    assert fit["asset_id"] == "abo_exact" and fit["pinned"] == "abo_exact"
    wrong = dict(piece("sofa", 2.0, 0.9), asset_pin="abo_missing")
    fit = F.fit_piece(wrong, cat)
    assert fit["asset_id"] == "abo_other" and "not a sofa model" in fit["pin_refused"]


@pytest.mark.skipif(not REAL02.is_file(), reason="results/furniture/real02 not committed")
def test_the_decor_placer_respects_the_sloped_attic_ceiling():
    # E2: real02's attic plants were placed where the slope leaves 0.87 m (1.6 m plants through the roof).
    b = json.loads(REAL02.read_text(encoding="utf-8"))
    planes = D.ceiling_planes(b, "L1")
    assert planes and not D.ceiling_planes(b, "L0")
    assert D.ceiling_over(b, "L1", (2.151, 0.551), (0.6, 0.6), planes=planes) < 1.0
    assert D.ceiling_over(b, "L0", (2.0, 2.0), (0.6, 0.6)) == pytest.approx(3.0)
    room = next(r for r in b["rooms"] if r["id"] == "r_L1_oyun_aktivite_ve_dinlenme_odasi")
    pieces = [f for f in b["furniture"] if f.get("room_id") == room["id"]]
    ctx = P.room_context(b, room)
    assert DA.free_corners(room, pieces, b, ctx)                       # free corners exist, under the slope
    for _sid, made in DA.floor_items(room, pieces, b, ctx, {"plant", "plant_large"}, 3.4):
        for item in made.values():
            w, d = item["size"][:2]
            h = DA.FLOOR_ITEM_SIZES[item["type"]][2]
            assert D.ceiling_over(b, "L1", item["center"], (w, d), planes=planes) >= h + DA.CEILING_CLEAR_M
    center, why = D.plant_position(room, pieces, b)
    if center is not None:
        assert D.ceiling_over(b, "L1", center, D.PLANT_SIZE, planes=planes) >= D.PLANT_HEIGHT_M
