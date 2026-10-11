"""User decision 1a of 11 Oct 2026 (docs/milestone12.md §14.3): a library model the audit kept with a vision doubt is
looked at in every run: the final check's element line asks about it, the agent's room critic is told about it (D2,
also for a decor model on a piece) and the final report lists it."""
from wenart import views as VW
from wenart.agent import critic_vision as CV
from wenart.agent import prompts as AP
from wenart.furniture import catalog as C
from wenart.report import final as F
from wenart.vision_check import prompts as VP

DOUBT = ["the vision check sees more than one object"]
ASSET = {"asset_id": "abo_x", "method": "library", "audit": {"status": "keep", "vision_doubt": DOUBT}}


def scene():
    return {"objects": [
        {"name": "furn_f_1", "wenart_id": "f_1", "kind": "furniture", "type": "sofa", "room_id": "r_1",
         "pass_index": 5, "asset": ASSET},
        {"name": "decor_f_1_1", "wenart_id": "f_1", "decor_id": "dec_1", "host_id": "f_1", "kind": "decor",
         "type": "cushion", "room_id": "r_1", "pass_index": 5,
         "asset": {"asset_id": "abo_c", "audit": {"status": "keep", "vision_doubt": ["vision quality 2 (<= 2)"]}}},
        {"name": "furn_f_2", "wenart_id": "f_2", "kind": "furniture", "type": "chair", "room_id": "r_1",
         "pass_index": 6, "asset": {"asset_id": "abo_y", "audit": {"status": "keep"}}},
    ]}


def test_the_catalogue_reads_the_doubt_of_an_entry_or_an_asset():
    assert C.vision_doubt(ASSET) == DOUBT
    assert C.vision_doubt({"audit": {"status": "keep"}}) == [] and C.vision_doubt(None) == []


def test_the_element_table_carries_the_doubts():
    table = VW.index_table(scene())
    assert table[5]["vision_doubt"] == DOUBT
    assert table[5]["decor_doubt"] == [{"type": "cushion", "doubt": ["vision quality 2 (<= 2)"]}]
    assert table[6]["vision_doubt"] == [] and table[6]["decor_doubt"] == []


def test_the_final_check_asks_about_a_doubtful_model():
    item = {"label": "E1", "type": "sofa", "box_1000": [1, 2, 3, 4], "vision_doubt": DOUBT}
    assert "may not be a real sofa" in VP.element_line(item)
    assert "may not be" not in VP.element_line(dict(item, vision_doubt=[]))
    expected = {"elements": [{"wenart_id": "f_1", "kind": "furniture", "type": "sofa", "role": "required",
                              "pixels": 900, "index": 5, "box_1000": [1, 2, 3, 4], "vision_doubt": DOUBT}]}
    assert VP.check_items(expected)[0]["vision_doubt"] == DOUBT


def test_the_room_critic_is_told_about_doubtful_models_and_decor():
    building = {"decor": [{"id": "dec_1", "host_id": "f_1", "type": "cushion",
                           "asset": {"audit": {"vision_doubt": ["vision quality 2 (<= 2)"]}}}]}
    pieces = CV.with_decor_doubts([{"id": "f_1", "type": "sofa", "asset": ASSET}, {"id": "f_2", "type": "chair"}],
                                  building)
    room = {"id": "r_1", "label": "Salon", "room_type": "living", "area_computed": 20.0}
    text = AP.room_look_prompt(room, pieces, ["cam_1"], ["render of view cam_1"], [])
    line = next(x for x in text.splitlines() if x.startswith("- f_1:"))
    assert "D2" in line and "more than one object" in line and "the cushion on it is in doubt" in line
    assert next(x for x in text.splitlines() if x.startswith("- f_2:")) == "- f_2: chair"


def test_the_final_report_lists_the_models_in_doubt():
    rows = F.models_in_doubt(scene())
    assert [(r["id"], r["kind"], r["asset_id"]) for r in rows] == [("f_1", "furniture", "abo_x"),
                                                                   ("dec_1", "decor", "abo_c")]
    assert F.models_in_doubt(None) == []
