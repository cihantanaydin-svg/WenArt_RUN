"""Milestone 12 track S (docs/milestone12.md §4.7 D13, B3; contract §13.2): decor in its host's frame and
``decor.sync_to_hosts``: the decor follows its host after a move, a turn, a resize or a model swap, and is dropped
(``decor_dropped``) when its host is gone, not built or retyped; rugs and pendants follow their first anchor, wall
art slides along its wall. Checked on hand-made pieces and on the committed real02 / real03 decor."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA

ROOT = Path(__file__).resolve().parents[1]


def piece(pid, ftype, center, size, rot=0.0, **extra):
    return dict({"id": pid, "type": ftype, "level_id": "L0", "room_id": "r1", "status": "verified",
                 "source": "from_documents", "footprint": {"center": list(center), "size": list(size),
                                                           "rotation_deg": rot}}, **extra)


def item(did, dtype, center, size, rot=0.0, host=None, **extra):
    return dict({"id": did, "kind": "decor", "type": dtype, "level_id": "L0", "room_id": "r1", "center": list(center),
                 "rotation_deg": rot, "size": list(size), "host_id": host, "source": "added_by_ai",
                 "method": "rule"}, **extra)


def local_of(it, host):
    fp = host["footprint"]
    p = G.rotate_point(tuple(it["center"][:2]), -float(fp["rotation_deg"]), tuple(fp["center"]))
    return (p[0] - fp["center"][0], p[1] - fp["center"][1])


def sofa_building():
    sofa = piece("s", "sofa", (2.0, 3.0), (2.0, 0.9), 90.0)
    cushions = [dict(c, id=f"c{i}", kind="decor", level_id="L0", room_id="r1", host_id="s", source="added_by_ai",
                     method="rule") for i, c in enumerate(D.host_decor(sofa))]
    return {"furniture": [sofa], "decor": cushions}


def test_host_frame_holds_support_shares_turn_and_lean():
    b = D.attach_host_frames(sofa_building())
    frames = [d["host_frame"] for d in b["decor"]]
    assert all(f["support"] == "back" and f["lean_deg"] == D.LEAN_DEG and f["turn_deg"] == 0.0 for f in frames)
    assert sorted(f["u"] for f in frames) == [-0.25, 0.25]
    assert all(f["v"] == pytest.approx((0.45 - 0.075 - 0.1) / 0.9, abs=1e-4) for f in frames)
    assert D.support_of("throw", "bed_double") == "mattress" and D.support_of("cushion", "bed_single") == "headboard"
    assert D.support_of("book_set", "bookshelf") == "shelf" and D.support_of("vase", "nightstand") == "top"
    assert D.support_of("rug", None) == "floor" and D.support_of("curtain", None) == "wall"
    assert D.support_of("pendant_light", None) == "ceiling" and D.support_of("cushion", "ottoman") == "seat"


@pytest.mark.parametrize("edit", ["move", "turn", "resize", "swap"])
def test_decor_follows_its_host_after_every_edit(edit):
    b = D.attach_host_frames(sofa_building())
    before = {d["id"]: local_of(d, b["furniture"][0]) for d in b["decor"]}
    edited = copy.deepcopy(b)
    fp = edited["furniture"][0]["footprint"]
    if edit == "move":
        fp["center"] = [fp["center"][0] + 1.3, fp["center"][1] - 0.7]
    elif edit == "turn":
        fp["rotation_deg"] = 180.0
    elif edit == "resize":
        fp["size"] = [1.6, 0.8]
    else:
        edited["furniture"][0]["asset"] = {"method": "library", "asset_id": "abo_other", "licence": "CC-BY-4.0"}
    out = D.sync_to_hosts(edited)
    host = out["furniture"][0]
    assert len(out["decor"]) == 2 and "decor_dropped" not in out
    sx = 1.6 / 2.0 if edit == "resize" else 1.0
    sy = 0.8 / 0.9 if edit == "resize" else 1.0
    for d in out["decor"]:
        lx, ly = local_of(d, host)
        bx, by = before[d["id"]]
        assert lx == pytest.approx(bx * (sx if edit == "resize" else 1.0), abs=2e-3)
        assert ly == pytest.approx(by * sy, abs=2e-3)
        assert d["rotation_deg"] == pytest.approx(G.normalise_angle(host["footprint"]["rotation_deg"]))
    # the old code (no sync) left the cushions where they were: off the moved or turned sofa
    if edit in ("move", "turn"):
        stale = edited["decor"]
        assert any(abs(local_of(d, host)[1] - before[d["id"]][1]) > 0.1 or
                   abs(local_of(d, host)[0] - before[d["id"]][0]) > 0.1 for d in stale)


def test_sync_is_idempotent_and_keeps_an_unedited_building():
    b = D.attach_host_frames(sofa_building())
    once = D.sync_to_hosts(b)
    twice = D.sync_to_hosts(once)
    assert json.dumps(once, sort_keys=True) == json.dumps(twice, sort_keys=True)
    for a, c in zip(b["decor"], once["decor"]):
        assert math.dist(a["center"], c["center"]) < 1.5e-3


@pytest.mark.parametrize("change, reason", [("remove", "is gone"), ("unbuilt", "is not built"),
                                            ("unknown", "is not built"), ("gap", "is not built"),
                                            ("retype", "without a back")])
def test_decor_of_a_gone_unbuilt_or_retyped_host_is_dropped(change, reason):
    b = D.attach_host_frames(sofa_building())
    if change == "remove":
        b["furniture"] = []
    elif change == "unbuilt":
        b["furniture"][0]["build"] = False
    elif change == "unknown":
        b["furniture"][0]["type"] = "unknown"
    elif change == "gap":
        b["furniture"][0]["asset"] = {"method": "none", "fallback_reason": "library gap"}
    else:
        b["furniture"][0]["type"] = "table_coffee"
    out = D.sync_to_hosts(b)
    assert out["decor"] == [] and len(out["decor_dropped"]) == 2
    assert all(reason in d["reason"] and d["host_id"] == "s" for d in out["decor_dropped"])


def test_rug_and_pendant_follow_their_piece_wall_art_slides_along_its_wall():
    sofa = piece("s", "sofa", (2.0, 0.55), (2.0, 0.9), 0.0)          # back to the wall y = 1.0 ... facing -Y
    table = piece("t", "table_dining", (6.0, 3.0), (1.6, 0.9), 0.0)
    rug = item("rug1", "rug", (2.0, -0.4), (2.6, 1.8), anchor_ids=["s"])
    art = item("art1", "wall_art", (2.0, 0.98), (1.2, 0.04), anchor_ids=["s"], wall_point=[2.0, 1.0])
    pend = item("p1", "pendant_light", (6.0, 3.0, 2.0), (0.45, 0.45, 0.7), anchor_ids=["t"])
    b = D.attach_host_frames({"furniture": [sofa, table], "decor": [rug, art, pend]})
    assert b["decor"][1]["host_frame"]["support"] == "wall" and b["decor"][1]["host_frame"]["anchor_id"] == "s"
    edited = copy.deepcopy(b)
    edited["furniture"][0]["footprint"]["center"] = [2.8, 0.55]       # the sofa slides 0.8 m along its wall
    edited["furniture"][1]["footprint"]["center"] = [5.5, 3.2]
    out = D.sync_to_hosts(edited)
    r, a, p = out["decor"]
    assert r["center"] == pytest.approx([2.8, -0.4]) and a["wall_point"] == pytest.approx([2.8, 1.0])
    assert a["center"] == pytest.approx([2.8, 0.98]) and p["center"] == pytest.approx([5.5, 3.2, 2.0])
    # the sofa leaves the wall: its picture is dropped, the rug still follows
    edited["furniture"][0]["footprint"]["center"] = [2.8, -0.5]
    out = D.sync_to_hosts(edited)
    assert [d["id"] for d in out["decor"]] == ["rug1", "p1"]
    assert out["decor_dropped"][0]["id"] == "art1" and "from the wall" in out["decor_dropped"][0]["reason"]


def test_throw_takes_the_resized_bed_width_and_tops_never_overhang():
    bed = piece("b", "bed_double", (0.0, 0.0), (1.6, 2.0))
    throw = item("th", "throw", (0.0, -0.72), (1.52, 0.5, 0.05), host="b")
    vase = item("v", "vase", (5.0, 5.0), (0.3, 0.3, 0.4), host="n")
    night = piece("n", "nightstand", (5.0, 5.0), (0.45, 0.4))
    b = D.attach_host_frames({"furniture": [bed, night], "decor": [throw, vase]})
    b["furniture"][0]["footprint"]["size"] = [1.4, 2.0]
    b["furniture"][1]["footprint"]["size"] = [0.25, 0.25]
    out = D.sync_to_hosts(b)
    assert out["decor"][0]["size"][0] == pytest.approx(0.95 * 1.4) and out["decor"][1]["size"][:2] == [0.25, 0.25]


def test_no_decor_cushions_on_models_with_their_own():
    sofa = piece("s", "sofa", (0, 0), (2.0, 0.9), asset={"method": "library", "has_cushions": True})
    bed = piece("b", "bed_double", (5, 0), (1.6, 2.0), asset={"method": "library", "has_bedding": True})
    bare = piece("c", "bed_double", (9, 0), (1.6, 2.0), asset={"method": "library", "has_mattress": True})
    assert not D.takes_cushions(sofa) and not D.takes_cushions(bed) and D.takes_cushions(bare)
    assert DA._cushions(sofa) == [] and DA._cushions(bed) == [] and len(DA._cushions(bare)) == 2
    building = {"rooms": [], "furniture": [sofa, bed, bare]}
    items, row = D.rule_decor_room(building, {"id": "r1", "label": "x", "level_id": "L0", "room_type": "other",
                                              "status": "unverified"}, [sofa, bed, bare], lambda lv: "d")
    assert [i["host_id"] for i in items] == ["c", "c"] and row["cushions"] == 2


def committed(project):
    path = ROOT / "results" / "furniture" / project / "building_final.json"
    if not path.is_file():
        pytest.skip(f"no committed {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def hosted_inside(b, margin=0.05):
    """{decor id: its centre inside its host's footprint (+ margin)} of the hosted items."""
    pieces = {p["id"]: p for p in b["furniture"]}
    out = {}
    for d in b["decor"]:
        host = pieces.get(d.get("host_id"))
        if host is None:
            continue
        lx, ly = local_of(d, host)
        w, dd = host["footprint"]["size"]
        out[d["id"]] = abs(lx) <= w / 2.0 + margin and abs(ly) <= dd / 2.0 + margin
    return out


@pytest.mark.parametrize("project", ["real02", "real03"])
def test_committed_decor_follows_simulated_agent_edits(project):
    """B3 on the committed results: move every host 0.6 m and turn it 90 degrees (an agent's edits): with the sync
    every hosted item keeps its place on its host; without it (the replay of Milestone 11) most are left behind."""
    b = D.attach_host_frames(committed(project))
    start = hosted_inside(b)
    edited = copy.deepcopy(b)
    for p in edited["furniture"]:
        fp = p["footprint"]
        fp["center"] = [fp["center"][0] + 0.6, fp["center"][1] - 0.4]
        fp["rotation_deg"] = G.normalise_angle(float(fp["rotation_deg"]) + 90.0)
    stale = hosted_inside(edited)
    synced = D.sync_to_hosts(edited)
    after = hosted_inside(synced)
    assert len(start) >= 40 and sum(stale.values()) < len(stale) * 0.5
    assert after and all(after[i] == start[i] for i in after)               # every kept item as on its host before
    assert sum(after.values()) >= 0.85 * sum(start.values())
    dropped = synced.get("decor_dropped") or []
    # dropped: decor of unbuilt pieces, and pictures whose piece turned its back away from their wall
    assert all("not built" in d["reason"] or "gone" in d["reason"] or
               (d["type"] in ("wall_art", "mirror", "clock") and "wall" in d["reason"]) for d in dropped)
    assert not any(d.get("host_id") and "wall" in d["reason"] for d in dropped)
