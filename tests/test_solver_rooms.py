"""The deterministic group solver (docs/milestone12.md §4.4, contract §13.2; wenart/furniture/solver.py) on hand-made
rooms: a rectangle, an L-shaped room, a room with two doors, drawn anchors kept, completion adding only partners,
determinism, the candidate format and the time per room."""
import json
import statistics
import time

from shapely.geometry import Polygon

import _m11_room as M
from wenart.furniture import group_checks as GC
from wenart.furniture import placer as P
from wenart.furniture import program as PR
from wenart.furniture import solver as SV

ROOM = M.ROOM_ID
KEYS = {"rank", "score", "terms", "pieces", "groups", "hard_failures", "group_violations", "options", "placed",
        "not_placed", "kept_ids", "nodes"}


def fp(pid, ftype, center, size, front, **kw):
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def new_findings(building, cand):
    after = SV.apply_candidate(building, ROOM, cand)
    before = {(v["check"], v["target"], v["message"]) for v in GC.check_room(building, ROOM)}
    return [v for v in GC.check_room(after, ROOM) if (v["check"], v["target"], v["message"]) not in before
            and v["severity"] in ("critical", "major")]


def l_room():
    """An L: 6 x 5 with the 2.5 x 2.0 north-east corner cut out."""
    b = M.building(w=6.0, h=5.0, room_type="bedroom", window=(1.5, 1.2))
    b["rooms"][0]["polygon"] = [[0.0, 0.0], [6.0, 0.0], [6.0, 3.0], [3.5, 3.0], [3.5, 5.0], [0.0, 5.0]]
    b["rooms"][0]["area_computed"] = 25.0
    b["walls"] += [{"id": "w_l1", "level_id": "L0", "start": [6.0, 3.05], "end": [3.5, 3.05], "thickness": 0.1,
                    "status": "verified", "evidence": []},
                   {"id": "w_l2", "level_id": "L0", "start": [3.55, 3.0], "end": [3.55, 5.0], "thickness": 0.1,
                    "status": "verified", "evidence": []}]
    return b


def test_candidates_have_the_contract_keys_and_ranks():
    b = M.building(w=4.0, h=4.5, room_type="bedroom")
    cands = SV.solve_room(b, ROOM, k=3)
    assert [c["rank"] for c in cands] == [1, 2, 3] and all(set(c) >= KEYS for c in cands)
    best = cands[0]
    assert not best["hard_failures"] and best["terms"] and best["nodes"]["generated"] > 0
    types = sorted(p["type"] for p in best["pieces"])
    assert types.count("bed_double") == 1 and types.count("nightstand") == 2 and "wardrobe" in types
    for p in best["pieces"]:
        assert p["source"] == "added_by_ai" and p["method"] == "rule" and p["group"]["group_id"].startswith(ROOM + ".")
        assert p["front_deg"] == round((270.0 + p["footprint"]["rotation_deg"]) % 360.0, 3)
    sigs = {json.dumps(sorted((p["type"], p["footprint"]["center"]) for p in c["pieces"])) for c in cands}
    assert len(sigs) == 3                                                    # three different layouts
    assert not new_findings(b, best)


def test_the_solver_is_deterministic():
    b = M.building(w=5.0, h=4.0, room_type="living")
    a = SV.solve_room(b, ROOM, k=3)
    c = SV.solve_room(json.loads(json.dumps(b)), ROOM, k=3)
    assert json.dumps(a, sort_keys=True) == json.dumps(c, sort_keys=True)


def test_living_room_sofa_faces_its_tv_with_the_coffee_table_between():
    b = M.building(w=5.0, h=4.5, room_type="living", window=(1.0, 1.0))
    best = SV.solve_room(b, ROOM, k=3)[0]
    types = [p["type"] for p in best["pieces"]]
    assert {"sofa", "tv_unit", "table_coffee"} <= set(types) or {"sofa_corner", "tv_unit"} <= set(types)
    after = SV.apply_candidate(b, ROOM, best)
    assert not [v for v in GC.check_room(after, ROOM) if v["check"] in ("G1", "G2", "G3", "G11")
                and v["severity"] != "minor"]


def test_an_l_shaped_room_keeps_every_piece_inside():
    b = l_room()
    cands = SV.solve_room(b, ROOM, k=3)
    assert cands and not cands[0]["hard_failures"]
    poly = Polygon(b["rooms"][0]["polygon"]).buffer(1e-3)
    for c in cands:
        for p in c["pieces"]:
            assert poly.contains(P.drawn_piece(p).polygon()), (c["rank"], p["type"])
    assert not new_findings(b, cands[0])


def test_two_doors_stay_connected():
    b = M.building(w=4.0, h=5.0, room_type="bedroom", door_x=1.0)
    b["openings"].append({"id": "d2", "type": "door", "level_id": "L0", "wall_id": "w_n", "center": [3.0, 5.05],
                          "width": 0.9, "swing_side": ROOM, "status": "verified", "evidence": []})
    b["openings"] = [o for o in b["openings"] if o["type"] == "door"]
    for c in SV.solve_room(b, ROOM, k=3):
        after = SV.apply_candidate(b, ROOM, c)
        assert not [v for v in GC.check_room(after, ROOM) if v["check"] == "G11"], c["rank"]
        ctx = P.room_context(after, after["rooms"][0])
        for f in after["furniture"]:
            poly = P.drawn_piece(f).polygon()
            for d in ctx.doors:
                assert poly.intersection(d.zone).area < P.AREA_EPS and (d.swing is None or poly.intersection(
                    d.swing).area < P.AREA_EPS), (c["rank"], f["type"], d.id)


def test_drawn_anchors_stay_and_get_only_their_partners():
    sofa = fp("s1", "sofa", (0.47, 2.5), (2.2, 0.9), 0.0)
    b = M.building(w=4.5, h=5.0, room_type="living", window=(2.25, 1.2), furniture=[sofa])
    prog = PR.room_program(b, ROOM)
    seat = next(g for g in prog["groups"] if g["group"] == "seating")
    assert seat["drawn"] and seat["anchor_id"] == "s1" and set(seat["missing"]) == {"tv_unit", "table_coffee"}
    for c in SV.solve_room(b, ROOM, prog, k=3):
        assert not {"sofa", "sofa_corner"} & {p["type"] for p in c["pieces"]}
        for p in c["pieces"]:
            if p["group"]["group"] == "seating":
                assert p["group"]["anchor_id"] == "s1" and p["group"]["role"] == "partner"
        after = SV.apply_candidate(b, ROOM, c)
        assert next(f for f in after["furniture"] if f["id"] == "s1") == sofa
    best = SV.solve_room(b, ROOM, prog, k=1)[0]
    assert {"tv_unit", "table_coffee"} <= {p["type"] for p in best["pieces"]}


def test_completion_adds_only_the_partners_a_drawn_group_misses():
    bed = fp("b1", "bed_double", (1.02, 2.5), (1.6, 2.0), 0.0)
    ns = fp("n1", "nightstand", (0.22, 1.47), (0.4, 0.4), 0.0)
    b = M.building(w=4.5, h=5.0, furniture=[bed, ns])
    best = SV.solve_room(b, ROOM, k=1)[0]
    stands = [p for p in best["pieces"] if p["type"] == "nightstand"]
    assert len(stands) == 1 and not [p for p in best["pieces"] if p["type"] in ("bed_double", "bed_single")]
    side = GC.nightstand_place(P.drawn_piece(bed), P.drawn_piece(stands[0]))["side"]
    assert side != GC.nightstand_place(P.drawn_piece(bed), P.drawn_piece(ns))["side"]


def test_fixed_ids_keep_added_pieces_and_apply_candidate_renumbers():
    b = M.building(w=4.0, h=4.5, room_type="bedroom")
    first = SV.apply_candidate(b, ROOM, SV.solve_room(b, ROOM, k=1)[0])
    wardrobe = next(f for f in first["furniture"] if f["type"] == "wardrobe")
    again = SV.solve_room(first, ROOM, k=1, fixed_ids=[wardrobe["id"]])[0]
    assert wardrobe["id"] in again["kept_ids"] and "wardrobe" not in {p["type"] for p in again["pieces"]}
    out = SV.apply_candidate(first, ROOM, again)
    assert [f["id"] for f in out["furniture"]].count(wardrobe["id"]) == 1
    ids = [f["id"] for f in out["furniture"]]
    assert len(ids) == len(set(ids)) and len([f for f in out["furniture"] if f["type"] == "bed_double"]) == 1
    anchors = {f["id"] for f in out["furniture"]}
    assert all(f["group"]["anchor_id"] in anchors for f in out["furniture"] if f["group"]["anchor_id"])


def test_an_empty_kitchen_gets_a_run_in_working_order():
    b = M.building(w=3.5, h=4.0, room_type="kitchen", window=(1.75, 1.0), sill=1.0)
    best = SV.solve_room(b, ROOM, k=3)[0]
    types = {p["type"] for p in best["pieces"]}
    assert {"kitchen_counter", "sink_kitchen", "stove", "fridge"} <= types
    after = SV.apply_candidate(b, ROOM, best)
    assert not [v for v in GC.check_room(after, ROOM) if v["check"] in ("G8", "G9") and v["severity"] != "minor"]


def test_a_typical_room_is_solved_in_about_two_seconds():
    """§4.4: ≤ 2 s per typical room (the median of three runs; the CPU is shared with other jobs, so 3 s here)."""
    b = M.building(w=4.5, h=5.0, room_type="bedroom")
    times = []
    for _ in range(3):
        t0 = time.perf_counter()
        SV.solve_room(b, ROOM, k=3)
        times.append(time.perf_counter() - t0)
    assert statistics.median(times) < 3.0, times
