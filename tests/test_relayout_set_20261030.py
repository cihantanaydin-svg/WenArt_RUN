"""30 Oct 2026 (real04 run 20261030-112241-full, review): two Argus ``relayout_room`` edits took the TV unit out of
r_L-1_salon_2 and the play room (metric 5: living rooms with their set 3/5 -> 1/5). They were accepted because they
removed collision findings. The relayout replaced the room's added pieces with the solver's alone; the TV unit of the
media wall and the sideboard of the room fill came from the layout stage's rules after the solver. Now a relayout
runs those rules again in its room (``edit_ops.room_rules``), and a group edit that still loses a member of the room
type's set (``schemas.ROOM_SETS``) is refused (check ``set``). Pure tests; real04 is only the test case."""
import copy

import _m11_room as M
from wenart.furniture import edit_ops as E
from wenart.furniture import schemas
from wenart.report import metrics13 as MX

META = {"reason": "test", "round": 2, "log_seq": 3, "model": "mock"}
ROOM = M.ROOM_ID


def edit(op, **args):
    return dict({"op": op}, **META, **args)


def _sofa():
    """A drawn 2.2 m sofa, back on the west wall, facing east."""
    return M.fp("s1", "sofa", (0.55, 2.5), (2.2, 0.9), rotation=90.0, front=0.0)


def _living():
    return M.building(w=6.0, h=5.0, room_type="living", furniture=[_sofa()])


def test_one_set_table_for_the_metric_and_the_edits():
    assert MX.ROOM_SETS is schemas.ROOM_SETS
    assert schemas.room_set_missing("living", ["sofa", "table_coffee", "tv_unit", "rug"]) == []
    assert schemas.room_set_missing("living", ["sofa_corner", "table_coffee"]) == ["tv unit", "rug"]
    assert schemas.room_set_missing("bedroom", ["bed_double", "nightstand", "wardrobe"]) == ["nightstands"]
    assert schemas.room_set_missing("hall", []) == [] and schemas.room_set_missing(None, []) == []


def test_set_losses_names_only_what_the_room_had():
    b = _living()
    b["furniture"].append(M.fp("t1", "tv_unit", (5.75, 2.5), (1.6, 0.45), rotation=90.0, source="added_by_ai"))
    after = copy.deepcopy(b)
    after["furniture"] = [f for f in after["furniture"] if f["id"] != "t1"]
    assert E.set_losses(b, after, ROOM) == ["tv unit"]
    assert E.set_losses(after, after, ROOM) == []                    # never had one: not a loss
    unbuilt = copy.deepcopy(b)
    next(f for f in unbuilt["furniture"] if f["id"] == "t1")["build"] = False
    assert E.set_losses(b, unbuilt, ROOM) == ["tv unit"]             # a piece that is not built does not count


def test_a_group_edit_that_loses_the_tv_unit_is_refused(monkeypatch):
    laid = E.apply_edit(_living(), edit("relayout_room", room_id=ROOM))
    assert laid["accepted"], laid["failed_checks"]
    b = laid["building"]
    assert any(f["type"] == "tv_unit" for f in b["furniture"])

    def without_tv(bb, args):
        gone = [f["id"] for f in bb["furniture"] if f["type"] == "tv_unit"]
        bb["furniture"] = [f for f in bb["furniture"] if f["id"] not in gone]
        return gone

    monkeypatch.setattr(E, "_relayout_m12", without_tv)
    res = E.apply_edit(b, edit("relayout_room", room_id=ROOM))
    assert not res["accepted"] and res["building"] is None
    assert any(f.startswith("set: ") and "tv unit" in f for f in res["failed_checks"])


def test_relayout_runs_the_layout_rules_again_in_its_room(monkeypatch):
    b = _living()
    added = E.room_rules(b, ROOM)                                    # the media wall finds the TV wall the sofa faces
    tv = [f for f in b["furniture"] if f["id"] in added and f["type"] == "tv_unit"]
    assert len(tv) == 1 and tv[0]["source"] == "added_by_ai"
    again = E.room_rules(b, ROOM)                                    # the room keeps the TV unit it has
    assert not [f for f in b["furniture"] if f["id"] in again and f["type"] == "tv_unit"]
    seen = []
    real = E.room_rules
    monkeypatch.setattr(E, "room_rules", lambda bb, rid: seen.append(rid) or real(bb, rid))
    res = E.apply_edit(_living(), edit("relayout_room", room_id=ROOM))
    assert res["accepted"] and seen == [ROOM]
    assert len([f for f in res["building"]["furniture"] if f["type"] == "tv_unit"]) == 1     # never a second one
