"""CPU tests of the two-model combination, the polish decision, calibration and controls (§5.4-5.6).

Every row of the §5.4 table, the decoy (unreliable pass), failed calls
(not_computed, never absent), single-pass mode, extras (coverage drop,
A/B confirmation, decor as info), counts, the differential decision with
check_incomplete, the calibration metrics and targets, the plan A/B rule,
the preference votes and select-controls.
"""
import copy

import numpy as np
import pytest

from wenart.vision_check import calibrate as CAL
from wenart.vision_check import calls as C
from wenart.vision_check import combine as CB
from wenart.vision_check import controls as CT
from wenart.vision_check import expected as X
from wenart.vision_check import preference as R
from wenart.vision_check import prompts as P

CFG = X.load_cfg()
KEYS = ["qwen", "glm"]


def el(i, wid, kind, typ, px, role="required", box=(100, 100, 300, 300), source="from_documents", unverified=False):
    return {"index": i, "wenart_id": wid, "kind": kind, "type": typ, "pixels": px, "role": role,
            "box_1000": list(box), "box_px": list(box), "touches_border": False, "type_unverified": unverified,
            "source": source, "own_room": True, "area_frac": px / 1e6}


def expected_view() -> dict:
    return {"camera": "cam_r_1", "room_id": "r", "room_type": "living", "elements": [
        el(1, "win_1", "window", "window", 9000, box=(600, 100, 800, 400)),
        el(2, "f_sofa", "furniture", "sofa", 8000, box=(100, 500, 500, 800)),
        el(3, "f_arm", "furniture", "armchair", 7000, box=(550, 550, 750, 800), source="added_by_ai"),
        el(4, "f_unk", "furniture", "unknown", 6000, box=(820, 600, 950, 800), unverified=True),
        el(5, "d_1", "door", "door", 5000, role="optional", box=(10, 100, 90, 700)),
        el(6, "d_2", "door", "door", 100, role="ignore", box=(0, 0, 5, 5)),
    ]}


DECOY = {"type": "tv_unit", "box_px": [300, 100, 480, 350], "box_1000": [300, 100, 480, 350]}


def spec_for(exp=None, kind="cycles", decoy=DECOY, swap=None, target=None, target_box=None) -> C.CallSpec:
    exp = exp or expected_view()
    items = P.check_items(exp, decoy, swap)
    return C.CallSpec(key=f"check|cam_r_1|{kind}", camera="cam_r_1", image_kind=kind, prompt_kind="check", prompt="",
                      schema={}, images=[], image_labels=[], size=(1000, 1000), items=items, decoy=decoy, expected=exp,
                      target=target, target_box_px=target_box)


def labels(spec) -> dict:
    """wenart id (or 'decoy') -> label."""
    return {("decoy" if it["decoy"] else it["wenart_id"]): it["label"] for it in spec.items}


def answer(spec, statuses=None, extras=(), doors=1, windows=1, default="present") -> dict:
    """A schema-shaped answer: every element ``default`` (decoy absent) unless ``statuses`` says otherwise."""
    lab = labels(spec)
    out = {}
    for it in spec.items:
        key = "decoy" if it["decoy"] else it["wenart_id"]
        status, seen = (statuses or {}).get(key, ("absent", "nothing") if it["decoy"] else (default, None))
        if seen is None:
            seen = (it["category"] or "other_furniture") if status == "present" else "nothing"
        out[lab[key]] = {"status": status, "seen_as": seen, "confidence": 0.9}
    return {"data": {"elements": out, "extras": list(extras), "door_count": doors, "window_count": windows}}


def combine(spec, recs, keys=KEYS, index_map=None):
    return CB.combine_check(spec, recs, keys, CFG, index_map)


# --------------------------------------------------------------------------
# §5.4 rows
# --------------------------------------------------------------------------

@pytest.mark.parametrize("a, b, result, single", [
    ("present", "present", "ok", None),
    ("absent", "absent", "missing", None),
    ("different", "different", "changed", None),
    ("absent", "different", "missing_or_changed", None),
    ("different", "absent", "missing_or_changed", None),
    ("present", "absent", "disputed", None),
    ("different", "present", "disputed", None),
    ("unsure", "present", "unverified", "present"),
    ("absent", "unsure", "unverified", "absent"),
    ("unsure", "unsure", "unverified", None),
    (None, "present", "not_computed", None),
    ("absent", None, "not_computed", None),
])
def test_element_result_table(a, b, result, single):
    assert CB.element_result([a, b], single_pass=False) == (result, single)


def test_element_result_single_pass_is_always_unverified():
    assert CB.element_result(["present"], single_pass=True) == ("unverified", "present")
    assert CB.element_result(["absent"], single_pass=True) == ("unverified", "absent")
    assert CB.element_result([None], single_pass=True) == ("not_computed", None)


def _seen(status):
    return {"present": None, "absent": "nothing", "different": "bookshelf", "unsure": "nothing"}[status]


@pytest.mark.parametrize("a, b, result", [
    ("present", "present", "ok"), ("absent", "absent", "missing"), ("different", "different", "changed"),
    ("absent", "different", "missing_or_changed"), ("present", "absent", "disputed"),
    ("present", "different", "disputed"), ("unsure", "absent", "unverified"),
])
def test_every_row_through_combine_check(a, b, result):
    spec = spec_for()
    recs = {"qwen": answer(spec, {"f_sofa": (a, _seen(a))}), "glm": answer(spec, {"f_sofa": (b, _seen(b))})}
    entry = combine(spec, recs)
    sofa = entry["elements"]["f_sofa"]
    assert sofa["result"] == result
    assert sofa["passes"]["qwen"]["status"] == a and sofa["passes"]["glm"]["status"] == b
    others = [e["result"] for k, e in entry["elements"].items() if k != "f_sofa"]
    assert set(others) == {"ok"}
    expected_verdict = {"ok": "ok", "missing": "mismatch", "changed": "mismatch", "missing_or_changed": "mismatch",
                        "disputed": "info", "unverified": "info"}[result]
    assert entry["verdict"] == expected_verdict


def test_failed_call_is_not_computed_never_absent():
    spec = spec_for()
    entry = combine(spec, {"qwen": answer(spec), "glm": None})
    assert entry["verdict"] == "not_computed" and entry["not_computed"] == ["glm"]
    assert {e["result"] for e in entry["elements"].values()} == {"not_computed"}
    assert entry["elements"]["f_sofa"]["passes"]["glm"] is None
    assert entry["counts"]["door"]["result"] == "not_computed"


def test_decoy_seen_makes_the_pass_unreliable():
    spec = spec_for()
    recs = {"qwen": answer(spec, {"decoy": ("present", "tv_unit"), "f_sofa": ("absent", "nothing")}),
            "glm": answer(spec, {"f_sofa": ("absent", "nothing")})}
    entry = combine(spec, recs)
    assert entry["unreliable"] == ["qwen"] and entry["decoy"]["accepted_by"] == ["qwen"]
    assert entry["decoy"]["type"] == "tv_unit" and entry["decoy"]["passes"] == {"qwen": "present", "glm": "absent"}
    # The unreliable pass counts as unsure: nothing is confirmed by it.
    assert entry["elements"]["f_sofa"]["result"] == "unverified"
    assert entry["elements"]["f_sofa"]["passes"]["qwen"]["unreliable"]
    assert entry["verdict"] == "info"


def test_single_pass_results_are_unverified_and_the_verdict_info():
    spec = spec_for()
    entry = combine(spec, {"qwen": answer(spec, {"f_sofa": ("absent", "nothing")})}, keys=["qwen"])
    assert {e["result"] for e in entry["elements"].values()} == {"unverified"}
    assert entry["verdict"] == "info" and entry["elements"]["f_sofa"]["single"] == "absent"


def test_type_unverified_piece_only_present_or_absent_counts():
    spec = spec_for()
    recs = {k: answer(spec, {"f_unk": ("different", "wardrobe")}) for k in KEYS}
    entry = combine(spec, recs)
    unk = entry["elements"]["f_unk"]
    assert unk["result"] == "ok" and unk["type_unverified"] and "type unverified" in unk["notes"][0]
    recs = {k: answer(spec, {"f_unk": ("absent", "nothing")}) for k in KEYS}
    assert combine(spec, recs)["elements"]["f_unk"]["result"] == "missing"


def test_inconsistent_answers_are_normalised_to_unsure():
    spec = spec_for()
    recs = {"qwen": answer(spec, {"f_sofa": ("present", "armchair")}), "glm": answer(spec)}
    sofa = combine(spec, recs)["elements"]["f_sofa"]
    assert sofa["passes"]["qwen"]["status"] == "unsure" and sofa["passes"]["qwen"]["normalised"]
    assert sofa["result"] == "unverified"


def test_added_by_ai_mismatch_is_labelled_as_a_render_issue():
    spec = spec_for()
    recs = {k: answer(spec, {"f_arm": ("absent", "nothing")}) for k in KEYS}
    arm = combine(spec, recs)["elements"]["f_arm"]
    assert arm["result"] == "missing" and arm["source"] == "added_by_ai"
    assert CB.ADDED_BY_AI_NOTE in arm["notes"]
    assert CB.ADDED_BY_AI_NOTE == "added_by_ai: render/polish issue, not a document conflict"


def test_optional_element_missing_is_info_not_mismatch():
    spec = spec_for()
    recs = {k: answer(spec, {"d_1": ("absent", "nothing")}) for k in KEYS}
    entry = combine(spec, recs)
    assert entry["elements"]["d_1"]["result"] == "missing" and entry["elements"]["d_1"]["role"] == "optional"
    assert entry["verdict"] == "info"
    assert "d_2" not in entry["elements"]                     # ignore-role elements are not asked


# --------------------------------------------------------------------------
# Extras and counts
# --------------------------------------------------------------------------

def extra(cat, box, conf=0.8):
    return {"category": cat, "box": list(box), "confidence": conf}


def test_extras_coverage_drop_confirmation_and_classes():
    spec = spec_for()
    index = np.zeros((1000, 1000), dtype=np.uint16)
    index[500:800, 100:500] = 2                                   # the sofa's mask
    recs = {"qwen": answer(spec, extras=[extra("sofa", (110, 510, 490, 790)),       # on the sofa: dropped
                                         extra("lamp", (510, 400, 545, 900)),        # floor lamp
                                         extra("plant", (900, 850, 980, 990)),
                                         extra("chair", (20, 850, 80, 990))]),
            "glm": answer(spec, extras=[extra("other_furniture", (512, 410, 548, 880)),   # same class, IoU high
                                        extra("cushion", (905, 860, 975, 985)),
                                        extra("window", (20, 850, 80, 990))])}        # same box, other class
    entry = combine(spec, recs, index_map=index)
    assert entry["extras_dropped"] == {"qwen": 1, "glm": 0}
    confirmed = [x for x in entry["extras"] if x["confirmed"]]
    assert {(x["class"], x["info"]) for x in confirmed} == {("furniture", False), ("decor", True)}
    lamp = next(x for x in confirmed if x["class"] == "furniture")
    assert lamp["categories"] == {"qwen": "lamp", "glm": "other_furniture"} and lamp["iou"] >= 0.3
    unconfirmed = [x for x in entry["extras"] if not x["confirmed"]]
    assert {x["class"] for x in unconfirmed} == {"furniture", "window"}
    assert entry["verdict"] == "mismatch"                         # a confirmed furniture extra


def test_decor_only_extras_do_not_make_a_mismatch():
    spec = spec_for()
    recs = {k: answer(spec, extras=[extra("plant", (900, 850, 980, 990))]) for k in KEYS}
    entry = combine(spec, recs)
    assert [x["class"] for x in entry["extras"] if x["confirmed"]] == ["decor"] and entry["verdict"] == "info"


def test_low_iou_extras_are_not_confirmed():
    spec = spec_for()
    recs = {"qwen": answer(spec, extras=[extra("chair", (0, 800, 100, 900))]),
            "glm": answer(spec, extras=[extra("chair", (80, 880, 180, 980))])}
    assert not any(x["confirmed"] for x in combine(spec, recs)["extras"])


def test_counts_range_and_agreement():
    spec = spec_for()                                    # doors: 0 required (d_1 optional, d_2 ignore) .. 2 total
    entry = combine(spec, {k: answer(spec, doors=1, windows=1) for k in KEYS})
    assert entry["counts"]["door"]["expected"] == [0, 2] and entry["counts"]["window"]["expected"] == [1, 1]
    assert entry["counts"]["door"]["result"] == "ok" and entry["verdict"] == "ok"
    entry = combine(spec, {k: answer(spec, windows=3) for k in KEYS})
    assert entry["counts"]["window"]["result"] == "more" and entry["verdict"] == "mismatch"
    entry = combine(spec, {k: answer(spec, windows=0) for k in KEYS})
    assert entry["counts"]["window"]["result"] == "fewer"
    entry = combine(spec, {"qwen": answer(spec, windows=3), "glm": answer(spec, windows=1)})
    assert entry["counts"]["window"]["result"] == "unverified" and entry["verdict"] == "info"
    entry = combine(spec, {"qwen": answer(spec, windows=3), "glm": answer(spec, windows=0)})
    assert entry["counts"]["window"]["result"] == "unverified"


# --------------------------------------------------------------------------
# Controls inside combine
# --------------------------------------------------------------------------

def test_removal_and_swap_controls_flagged_and_confirmed():
    spec = spec_for(kind="removal:f_sofa", target="f_sofa")
    recs = {"qwen": answer(spec, {"f_sofa": ("absent", "nothing")}), "glm": answer(spec)}
    c = combine(spec, recs)["control"]
    assert c["flagged"] and not c["confirmed"] and c["computed"]
    recs["glm"] = answer(spec, {"f_sofa": ("different", "bed_double")})
    c = combine(spec, recs)["control"]
    assert c["flagged"] and c["confirmed"] and c["result"] == "missing_or_changed"
    swap = spec_for(kind="swap:f_sofa", swap={"id": "f_sofa", "type": "bed_double"}, target="f_sofa")
    recs = {k: answer(swap, {"f_sofa": ("different", "sofa")}) for k in KEYS}
    entry = combine(swap, recs)
    assert entry["elements"]["f_sofa"]["swapped_from"] == "sofa" and entry["elements"]["f_sofa"]["type"] == "bed_double"
    assert entry["control"]["confirmed"]


def test_insertion_control_needs_a_confirmed_extra_over_the_box():
    spec = spec_for(kind="insertion:f_sofa", target="f_sofa", target_box=[100, 500, 500, 800])
    over = extra("sofa", (120, 520, 480, 790))
    recs = {"qwen": answer(spec, extras=[over]), "glm": answer(spec)}
    c = combine(spec, recs)["control"]
    assert c["flagged"] and not c["confirmed"]
    recs["glm"] = answer(spec, extras=[extra("armchair", (110, 500, 450, 800))])
    c = combine(spec, recs)["control"]
    assert c["flagged"] and c["confirmed"]


# --------------------------------------------------------------------------
# Differential decision
# --------------------------------------------------------------------------

def _pair(cycles_status=None, polished_status=None, cycles_extras=(), polished_extras=(), polished_rec=True,
          decoy_seen=False):
    spec = spec_for()
    cyc = combine(spec, {k: answer(spec, cycles_status, extras=cycles_extras) for k in KEYS})
    precs = {k: answer(spec, polished_status, extras=polished_extras) for k in KEYS}
    if not polished_rec:
        precs["glm"] = None
    if decoy_seen:
        precs["qwen"] = answer(spec, dict(polished_status or {}, decoy=("present", "tv_unit")), extras=polished_extras)
    pol = combine(spec, precs)
    return cyc, pol


def test_polished_missing_element_rejects():
    cyc, pol = _pair(polished_status={"f_sofa": ("absent", "nothing")})
    d = CB.polish_decision(cyc, pol, single_pass=False)
    assert d["polished_rejected"] and d["polished_reason"] == "vision_check"
    assert d["polished_reasons"][0]["id"] == "f_sofa" and d["polished_reasons"][0]["polished"] == "missing"


def test_a_miss_already_on_the_cycles_render_does_not_reject_the_polish():
    gone = {"f_sofa": ("absent", "nothing")}
    cyc, pol = _pair(cycles_status=gone, polished_status=gone)
    assert not CB.polish_decision(cyc, pol, False)["polished_rejected"]
    # ... but it marks the view for review.
    assert CB.review_reasons(cyc, {}) and "f_sofa" in CB.review_reasons(cyc, {})[0]


def test_unverified_on_cycles_then_confirmed_changed_rejects():
    cyc, pol = _pair(cycles_status={"f_sofa": ("unsure", "nothing")},
                     polished_status={"f_sofa": ("different", "bed_double")})
    assert cyc["elements"]["f_sofa"]["result"] == "unverified"
    assert CB.polish_decision(cyc, pol, False)["polished_reason"] == "vision_check"


def test_disputed_on_polished_does_not_reject():
    spec = spec_for()
    cyc = combine(spec, {k: answer(spec) for k in KEYS})
    pol = combine(spec, {"qwen": answer(spec, {"f_sofa": ("absent", "nothing")}), "glm": answer(spec)})
    assert pol["elements"]["f_sofa"]["result"] == "disputed"
    assert not CB.polish_decision(cyc, pol, False)["polished_rejected"]


def test_added_by_polish_extra_rejects_unless_cycles_had_it():
    lamp = extra("lamp", (300, 400, 360, 900))
    cyc, pol = _pair(polished_extras=[lamp])
    d = CB.polish_decision(cyc, pol, False)
    assert d["polished_rejected"] and d["polished_reasons"][0]["what"] == "added_by_polish"
    cyc, pol = _pair(cycles_extras=[lamp], polished_extras=[lamp])
    assert not CB.polish_decision(cyc, pol, False)["polished_rejected"]
    plant = extra("plant", (900, 850, 980, 990))                   # decor: info, never a rejection
    cyc, pol = _pair(polished_extras=[plant])
    assert not CB.polish_decision(cyc, pol, False)["polished_rejected"]


def test_check_incomplete_for_a_failed_or_unreliable_pass():
    cyc, pol = _pair(polished_rec=False)
    d = CB.polish_decision(cyc, pol, False)
    assert d["polished_rejected"] and d["polished_reason"] == "check_incomplete"
    cyc, pol = _pair(decoy_seen=True)
    d = CB.polish_decision(cyc, pol, False)
    assert d["polished_reason"] == "check_incomplete" and "unreliable" in d["polished_reasons"][0]["detail"]
    cyc, pol = _pair()
    assert CB.polish_decision(cyc, pol, False) == {"polished_rejected": False, "polished_reason": None,
                                                   "polished_reasons": []}
    assert CB.polish_decision(cyc, None, False)["polished_rejected"] is False


def test_single_pass_never_confirms_a_rejection():
    spec = spec_for()
    cyc = combine(spec, {"qwen": answer(spec)}, keys=["qwen"])
    pol = combine(spec, {"qwen": answer(spec, {"f_sofa": ("absent", "nothing")})}, keys=["qwen"])
    assert not CB.polish_decision(cyc, pol, single_pass=True)["polished_rejected"]


def test_review_reasons_include_the_json_crosscheck():
    reasons = CB.review_reasons(None, {"in_json_not_rendered": [{"id": "f_x"}], "misplaced": [{"id": "f_y"}]})
    assert len(reasons) == 2 and "f_x" in reasons[0]


def test_model_keys_from_arg_env_or_default(monkeypatch):
    monkeypatch.delenv("CHECK_MODELS", raising=False)
    assert CB.model_keys() == ["qwen", "glm"]
    monkeypatch.setenv("CHECK_MODELS", "glm")
    assert CB.model_keys() == ["glm"]
    assert CB.model_keys("qwen,glm") == ["qwen", "glm"]


# --------------------------------------------------------------------------
# Preference
# --------------------------------------------------------------------------

def test_preference_votes_three_of_four():
    answers = {"pc": {"qwen": {"choice": "first"}, "glm": {"choice": "first"}},
               "cp": {"qwen": {"choice": "second"}, "glm": {"choice": "same"}}}
    v = R.votes(answers, KEYS, 3)
    assert v["votes"] == 3 and v["answers"] == 4 and v["preferred"]
    answers["cp"]["qwen"] = {"choice": "first"}
    assert not R.votes(answers, KEYS, 3)["preferred"]
    answers["pc"]["glm"] = None
    v = R.votes(answers, KEYS, 3)
    assert v["answers"] == 3 and v["calls"]["glm"]["pc"] is None


# --------------------------------------------------------------------------
# Calibration
# --------------------------------------------------------------------------

def manifest_with(n_views=10, fa_views=0, extra_views=0, decoy_qwen=0, removal=(5, 5, 5), insertion=(5, 4),
                  single=False, plan=None) -> dict:
    """A check manifest of ``n_views`` Cycles views (2 required elements each)."""
    spec = spec_for()
    keys = ["qwen"] if single else KEYS
    views = {}
    for i in range(n_views):
        recs = {}
        for k in keys:
            st = {"f_sofa": ("absent", "nothing")} if i < fa_views else {}
            if k == "qwen" and i >= n_views - decoy_qwen:
                st = dict(st, decoy=("present", "tv_unit"))
            ex = [extra("chair", (20, 850, 80, 990))] if i < extra_views else []
            recs[k] = answer(spec, st, extras=ex)
        views[f"cam_{i}"] = {"cycles": combine(spec, recs, keys)}
    n_rem, flagged, confirmed = removal
    for j in range(n_rem):
        rs = spec_for(kind=f"removal:f_sofa", target="f_sofa")
        st_q = {"f_sofa": ("absent", "nothing")} if j < flagged else {}
        st_g = {"f_sofa": ("absent", "nothing")} if j < confirmed else {}
        views[f"cam_{j}"][f"removal:f_sofa"] = combine(rs, {"qwen": answer(rs, st_q), "glm": answer(rs, st_g)})
    n_ins, ok = insertion
    for j in range(n_ins):
        ins = spec_for(kind="insertion:f_sofa", target="f_sofa", target_box=[100, 500, 500, 800])
        ex = [extra("sofa", (120, 520, 480, 790))] if j < ok else []
        views[f"cam_{j}"]["insertion:f_sofa"] = combine(ins, {k: answer(ins, extras=ex) for k in KEYS})
    if plan:
        for j, (with_conf) in enumerate(plan):
            cam = f"cam_{j}"
            views[cam][f"plan_ab:{cam}"] = copy.deepcopy(views[cam]["cycles"])
            rs = spec_for(kind="plan_ab:removal:f_sofa", target="f_sofa")
            st = {"f_sofa": ("absent", "nothing")} if with_conf else {}
            views[cam]["plan_ab:removal:f_sofa"] = combine(rs, {k: answer(rs, st) for k in KEYS})
    return {"project": "toy", "model_keys": keys, "single_pass": single, "views": views}


def test_calibration_metrics_and_targets_met():
    cal = CAL.calibrate(manifest_with(), CFG)
    m = cal["metrics"]
    assert m["fa_missing"] == 0.0 and m["fa_extra"] == 0.0 and m["count_error"] == 0.0
    assert m["removal_flagged"] == 1.0 and m["removal_confirmed"] == 1.0 and m["insertion"] == 0.8
    assert m["models"]["qwen"]["decoy_accept"] == 0.0 and m["models"]["glm"]["answer_rate"] == 1.0
    assert cal["missed"] == [] and cal["advisory"] is False


def test_calibration_missed_targets_make_the_check_advisory():
    cal = CAL.calibrate(manifest_with(fa_views=3, extra_views=3, decoy_qwen=2, removal=(5, 4, 2), insertion=(5, 2)),
                        CFG)
    m = cal["metrics"]
    assert m["fa_missing"] == pytest.approx(3 / 40, abs=1e-3)          # 4 required elements per view
    assert m["fa_extra"] == 0.3                                          # both passes see the chair: confirmed
    assert m["removal_flagged"] == 0.8 and m["removal_confirmed"] == 0.4 and m["insertion"] == 0.4
    assert m["models"]["qwen"]["decoy_accept"] == 0.2 and m["models"]["glm"]["decoy_accept"] == 0.0
    missed = {r["metric"] for r in cal["missed"]}
    assert missed == {"fa_missing", "fa_extra", "removal_confirmed", "insertion", "decoy_accept[qwen]"}
    assert cal["advisory"] and len(cal["advisory_reasons"]) == 5


def test_calibration_without_controls_or_single_pass_is_advisory():
    cal = CAL.calibrate(manifest_with(removal=(0, 0, 0), insertion=(0, 0)), CFG)
    assert {r["metric"] for r in cal["missed"]} == {"removal_flagged", "removal_confirmed", "insertion"}
    assert all(r["reason"] == "no data" for r in cal["missed"]) and cal["advisory"]
    cal = CAL.calibrate(manifest_with(single=True, removal=(0, 0, 0), insertion=(0, 0)), CFG)
    assert cal["advisory"] and cal["single_pass"] and cal["metrics"]["fa_missing"] is None
    assert cal["advisory_reasons"][0].startswith("single pass")


def test_plan_ab_adopted_only_when_removal_detection_rises_without_more_false_alarms():
    # Without the plan the removals are confirmed for cam_0..cam_4 (removal=(5, 5, 5)).
    cal = CAL.calibrate(manifest_with(removal=(3, 3, 0), plan=[True, True, True]), CFG)
    ab = cal["plan_ab"]
    assert ab["removal_confirmed_without"] == 0.0 and ab["removal_confirmed_with"] == 1.0
    assert ab["fa_missing_with"] == ab["fa_missing_without"] and ab["adopted"] and ab["text"] == CAL.ADOPTED_TEXT
    cal = CAL.calibrate(manifest_with(removal=(3, 3, 3), plan=[True, True, True]), CFG)
    assert not cal["plan_ab"]["adopted"] and cal["plan_ab"]["text"] == CAL.NOT_ADOPTED_TEXT
    cal = CAL.calibrate(manifest_with(), CFG)
    assert not cal["plan_ab"]["adopted"] and cal["plan_ab"]["text"].startswith("source plan compared through")


# --------------------------------------------------------------------------
# select-controls
# --------------------------------------------------------------------------

def ctl_el(wid, kind, typ, area, room_ok=True, border=False, role="required", source="from_documents",
           unverified=False):
    return {"wenart_id": wid, "index": hash(wid) % 1000, "kind": kind, "type": typ, "area_frac": area,
            "role": role, "own_room": room_ok, "touches_border": border, "source": source,
            "type_unverified": unverified}


def test_select_controls_rules():
    views = {
        "cam_a_1": {"room_id": "a", "elements": [
            ctl_el("f_big_ai", "furniture", "sofa", 0.20, source="added_by_ai"),
            ctl_el("f_a2", "furniture", "armchair", 0.10, source="added_by_ai"),
            ctl_el("w_a", "window", "window", 0.08), ctl_el("d_a", "door", "door", 0.05),
            ctl_el("f_edge", "furniture", "desk", 0.30, border=True),
            ctl_el("f_small", "furniture", "chair", 0.02),
            ctl_el("f_unk", "furniture", "unknown", 0.40, unverified=True)]},
        "cam_a_2": {"room_id": "a", "elements": [ctl_el("f_big_ai", "furniture", "sofa", 0.25, source="added_by_ai")]},
        "cam_b_1": {"room_id": "b", "elements": [
            ctl_el("f_doc", "furniture", "bed_double", 0.06), ctl_el("w_b", "window", "window", 0.09),
            ctl_el("w_b2", "window", "window", 0.12), ctl_el("d_other", "door", "door", 0.2, room_ok=False)]},
        "cam_c_1": {"room_id": "c", "elements": [
            ctl_el("f_c", "furniture", "wardrobe", 0.15, source="added_by_ai"), ctl_el("w_c", "window", "window", 0.04),
            ctl_el("d_c", "door", "door", 0.04), ctl_el("f_opt", "furniture", "desk", 0.5, role="optional")]},
    }
    sel = CT.select_controls(views, CFG)
    by_kind = {}
    for c in sel["controls"]:
        by_kind.setdefault(c["kind"], []).append(c)
    furn = by_kind["furniture"]
    # One per room, at least one from the documents, largest first, the best view per id.
    assert [c["id"] for c in furn] == ["f_big_ai", "f_c", "f_doc"]
    assert next(c for c in furn if c["id"] == "f_big_ai")["camera"] == "cam_a_2"
    assert any(c["source"] == "from_documents" for c in furn)
    assert [c["id"] for c in by_kind["window"]] == ["w_b2", "w_a", "w_c"]          # w_b loses to w_b2 (room b)
    assert [c["id"] for c in by_kind["door"]] == ["d_a", "d_c"]                   # d_other: another room
    for c in sel["controls"]:
        assert c["plug"] == (c["kind"] == "window") and c["dir"] == f"controls/hide_{c['id']}"
        assert set(c) >= {"id", "index", "kind", "camera", "room_id", "plug", "area_frac", "source", "dir"}
    lines = CT.control_lines(sel)
    assert lines[0] == "CONTROL\tf_big_ai\tcam_a_2\t0\tcontrols/hide_f_big_ai"
    assert "CONTROL\tw_b2\tcam_b_1\t1\tcontrols/hide_w_b2" in lines
    assert CT.hide_sets(sel).startswith("cam_a_2:f_big_ai;") and "cam_b_1:w_b2+plug" in CT.hide_sets(sel)
    swaps = {s["id"]: s["swap_to"] for s in sel["swaps"]}
    assert swaps == {"f_big_ai": "bed_double", "f_doc": "sofa"}


def test_coverage_is_per_indexed_mask():
    index = np.zeros((100, 100), dtype=np.uint16)
    index[0:100, 0:40] = 3                         # two different elements, 40 % of the box each
    index[0:100, 60:100] = 4
    assert CB.covered_frac([0, 0, 100, 100], index) == pytest.approx(0.4)
    index[0:100, 40:60] = 3
    assert CB.covered_frac([0, 0, 100, 100], index) == pytest.approx(0.6)
    assert CB.covered_frac([0, 0, 100, 100], None) == 0.0 and CB.covered_frac([50, 50, 50, 60], index) == 0.0


def test_fa_extra_counts_only_confirmed_extras():
    spec = spec_for()
    views = {}
    for i in range(4):
        recs = {"qwen": answer(spec, extras=[extra("chair", (20, 850, 80, 990))]), "glm": answer(spec)}
        views[f"cam_{i}"] = {"cycles": combine(spec, recs)}
    cal = CAL.calibrate({"model_keys": KEYS, "single_pass": False, "views": views}, CFG)
    assert cal["metrics"]["fa_extra"] == 0.0 and cal["metrics"]["fa_missing"] == 0.0


def test_select_controls_furniture_without_any_document_piece():
    views = {"cam_a_1": {"room_id": "a", "elements": [ctl_el("f1", "furniture", "sofa", 0.2, source="added_by_ai")]}}
    sel = CT.select_controls(views, CFG)
    assert [c["id"] for c in sel["controls"]] == ["f1"]
