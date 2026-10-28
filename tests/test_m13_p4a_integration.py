"""Integration of the fix round after P4a (17 Oct 2026): the cross-track asks the lead applied.

What: CPU tests of the small changes made for the tracks' asks: the pendant that keeps its shade bottom under a sloped
ceiling and the library mirror's glass (scene builder), the ceiling slots of the decor stage under the slope, the
code-typed drawn bed or table that hosts decor and is checked by G4-G6 (the dining chairs of
``groups._expected_missing`` stay as they were: docs/milestone13.md §14.10), the F9 routing of the agent, the library
gap of a piece parametric by design, the vision quality of a catalogue doubt in the fit, the report CLI lines and the
agent metrics of the reports.
Why: every behaviour change of the integration step gets a test that fails on the code before it (03881bc plus the
tracks' changes) or on the mutation named in its docstring.
How: small hand-made inputs and the committed buildings; no Blender, no model server.
"""
from __future__ import annotations

import pytest

import _m11_room as M
from wenart.blender import furniture as BF
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.furniture import group_checks as GC

ROOM = M.ROOM_ID


def fp(pid, ftype, center, size, front, **kw):
    """A drawn piece whose front is ``front`` (the footprint's local -Y)."""
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def _by(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


# --------------------------------------------------------------------------
# Scene builder (R_rig asks): pendants under a slope, library mirror glass
# --------------------------------------------------------------------------

def test_a_pendant_keeps_its_shade_bottom_and_a_low_slope_leaves_it_out():
    """P4a real02 L1 (ceiling_height 3.433 m, slope 2.05-2.18 m over the slots): the shade bottom stays where the
    decor stage put it and the cord ends at the ceiling; under the 2.047 m slope over dec_L1_009 (bottom 2.0 m) the
    drop is 0.047 m and the pendant is not built. Before, the shade was lowered to fit: dec_L1_006 rested 0.244 m
    above the floor, through table f_L1_045."""
    assert BF.PENDANT_MIN_DROP_M == DA.PENDANT_MIN_DROP_M
    assert BF.pendant_hang(1.5, 2.177) == (0.677, None)                 # dec_L1_006 over the dining table
    assert BF.pendant_hang(2.0, 3.433) == (1.433, None)                 # a flat ceiling: the old cord length
    h, why = BF.pendant_hang(2.0, 2.047)                                # dec_L1_009
    assert h == pytest.approx(0.047) and why.startswith("ceiling 2.05 m over its slot too low")
    assert BF.pendant_hang(2.0, 1.9)[1] is not None                     # a ceiling under the shade bottom
    assert BF.pendant_hang(1.5, 1.8)[1] is None                         # exactly the least drop is built


def test_the_pendant_rule_is_the_one_the_builder_uses():
    """The builder's pendant branch calls ``pendant_hang`` and no longer lowers the shade bottom (the 03881bc line
    ``z_above = round(max(0.0, ceiling - h), 4)`` is gone)."""
    import inspect

    src = inspect.getsource(BF._create_decor)
    assert "pendant_hang(z_above, ceiling)" in src
    assert "max(0.0, ceiling - h)" not in src


def test_a_library_mirror_gets_mirror_glass_and_other_wall_decor_keeps_its_materials(monkeypatch):
    """R_rig's ask: ``_create_wall_art`` builds a library mirror from ``materials.mirror_glass_materials`` and keeps
    the cached geometry's list unchanged (it is shared per file); wall art and clocks keep the model's own list."""
    from wenart.blender import materials as MT

    calls = []

    def fake(mats):
        calls.append(mats)
        return [f"{m}__mirror" for m in mats], {m: "texture" for m in mats}

    monkeypatch.setattr(MT, "mirror_glass_materials", fake)
    cached = ["glass_atlas", "frame"]
    out, record = BF.wall_art_materials("mirror", cached)
    assert out == ["glass_atlas__mirror", "frame__mirror"] and record == {"glass_atlas": "texture", "frame": "texture"}
    assert cached == ["glass_atlas", "frame"] and calls[0] is not cached
    for dtype in ("wall_art", "clock"):
        assert BF.wall_art_materials(dtype, cached) == (cached, None)
    import inspect

    src = inspect.getsource(BF._create_wall_art)
    assert "wall_art_materials(dtype, geo[\"materials\"])" in src and 'entry["mirror_glass"]' in src


# --------------------------------------------------------------------------
# Decor stage (R_rig ask): the ceiling slots hang from the ceiling over them
# --------------------------------------------------------------------------

def _dining_room():
    table = fp("t1", "table_dining", (2.5, 2.0), (1.2, 0.8), 270.0, height=0.75)
    coffee = fp("c1", "table_coffee", (4.2, 3.3), (0.9, 0.5), 270.0, height=0.45)
    return M.building(w=5.0, h=4.0, room_type="living", window=None, furniture=[table, coffee])


def test_ceiling_slots_hang_from_the_sloped_ceiling_over_them(monkeypatch):
    """P4a: the decor stage hung real02's L1 pendants from the flat 3.433 m ceiling height while the attic slope over
    them was 2.05-2.18 m, so the builder lowered them through the table. With the building, a slot's pendant gets
    the drop that is there (a dining pendant keeps its 1.5 m bottom) and where the drop is under 0.3 m only the flush
    ceiling light is offered. Without a slope (or without the building) nothing changes."""
    b = _dining_room()
    room = b["rooms"][0]
    pieces = b["furniture"]
    ceiling = DA._ceiling(b, room)
    flat = dict(DA.ceiling_items(room, pieces, ceiling))
    assert flat["ceiling:over_t1"]["pendant_light"]["size"][2] == pytest.approx(2.7 - 1.5)
    assert dict(DA.ceiling_items(room, pieces, ceiling, building=b)) == flat            # no roof: as before
    # a slope falling to the east: 2.6 m over the floor at x = 0, 2.0 m at x = 5 (z = 2.6 - 0.12 x)
    monkeypatch.setattr(D, "ceiling_planes", lambda building, level_id: [[-0.12, 0.0, 2.6]])
    sloped = dict(DA.ceiling_items(room, pieces, ceiling, building=b))
    pendant = sloped["ceiling:over_t1"]["pendant_light"]
    top = D.ceiling_over(b, "L0", pendant["center"], DA.PENDANT_SIZE, planes=[[-0.12, 0.0, 2.6]])
    assert pendant["center"][2] == pytest.approx(1.5) and pendant["size"][2] == pytest.approx(top - 1.5, abs=1e-3)
    assert top < 2.7 and "sloped ceiling" in pendant["reason"]
    # bottom 2.0 m under a ~2.07 m slope: no pendant. Pin changed on purpose in the fix round after P5: the flush
    # light's bottom would be 1.95 m (< decor.MIN_LIGHT_BOTTOM_M), so the slot is left out with a note
    assert "ceiling:over_c1" not in sloped and "pendant_light" in flat["ceiling:over_c1"]
    notes: list = []
    DA.ceiling_items(room, pieces, ceiling, building=b, notes=notes)
    assert any(n.startswith("ceiling light over table coffee c1: the sloped ceiling over it is 2.07 m high, its "
                            "bottom would be 1.95 m") and n.endswith("left out") for n in notes), notes


# --------------------------------------------------------------------------
# Furniture (F_furniture asks): a code-typed drawn anchor hosts decor and is checked by G4-G6
# --------------------------------------------------------------------------

def _code_typed(ftype, center, size, method="twin", **kw):
    return fp("b1", ftype, center, size, 270.0, status="unverified", type_method=method, inferred=True, **kw)


def test_a_code_typed_drawn_bed_hosts_decor_and_an_unsure_one_does_not():
    """P4a r_L0_yatak_odasi: its bed f_L0_019 was typed by code at reading (status unverified) and hosted nothing:
    2 decor slots against 10 in M11. A vector-drawn piece typed by code is a trusted host now; a piece the reading
    could not agree on, a completion type proposal and any other status are not."""
    bed = _code_typed("bed_double", (2.5, 2.97), (1.6, 2.0))
    assert D.trusted_host(bed) and D._usable_anchor(bed)
    assert not D.trusted_host(dict(bed, type_method="ai_disagreement"))
    assert not D.trusted_host(dict(bed, type_proposal=True))
    assert not D.trusted_host(dict(bed, status="assumed")) and D.trusted_host(dict(bed, status="verified"))
    def hosted(building):
        counter = iter(range(1, 100))
        items, _row = D.rule_decor_room(building, building["rooms"][0], building["furniture"],
                                        lambda level_id: f"dec_{level_id}_{next(counter):03d}")
        return [i for i in items if i.get("host_id") == "b1"]

    b = M.building(w=5.0, h=4.0, room_type="bedroom", window=None, furniture=[bed])
    assert hosted(b), "the code-typed bed gets its cushions"
    unsure = M.building(w=5.0, h=4.0, room_type="bedroom", window=None,
                        furniture=[dict(bed, type_method="ai_disagreement")])
    assert hosted(unsure) == []


def test_g4_g5_check_a_code_typed_bed_and_g6_a_code_typed_table():
    """F_furniture's ask: G4/G5 skipped every ``unverified`` bed, so the nightstands the completion now adds beside a
    code-typed bed were never checked; G6 skipped a code-typed table. A bed the reading could not agree on stays
    skipped."""
    bed = _code_typed("bed_double", (2.5, 2.97), (1.6, 2.0))
    b = M.building(w=5.0, h=4.0, room_type="bedroom", window=None, furniture=[bed])
    found = [v for v in GC.check_view(GC.room_view(b, ROOM)) if v["check"] in ("G4", "G5")]
    assert any(v["check"] == "G4" and v["target"] == "b1" for v in found), found
    unsure = M.building(w=5.0, h=4.0, room_type="bedroom", window=None,
                        furniture=[dict(bed, type_method="ai_disagreement")])
    assert not [v for v in GC.check_view(GC.room_view(unsure, ROOM)) if v["check"] in ("G4", "G5")]
    table = _code_typed("table_dining", (2.5, 2.0), (1.6, 0.9), height=0.75)
    d = M.building(w=5.0, h=4.0, room_type="dining", window=None, furniture=[table])
    g6 = [v for v in GC.check_view(GC.room_view(d, ROOM)) if v["check"] == "G6"]
    assert g6 and "no chairs" in g6[0]["message"], g6
    unsure_t = M.building(w=5.0, h=4.0, room_type="dining", window=None,
                          furniture=[dict(table, type_method="ai_disagreement")])
    assert not [v for v in GC.check_view(GC.room_view(unsure_t, ROOM)) if v["check"] == "G6"]


# --------------------------------------------------------------------------
# Agent (F_furniture asks): F9 through the outline, library gaps by design
# --------------------------------------------------------------------------

def test_an_f9_through_the_room_outline_is_a_cut_never_a_wrong_type():
    """P4a seq 647: the wardrobe f_L-1_024's F9 "reaches 0.05 m² through the room outline" (0.020 m deep, the same as
    its S2) got the cause wrong_type and the tool mark_not_furniture, which deleted the drawn anchor. Below 0.03 m it
    is within tolerance (report only); deeper it is a collision (move the piece); never mark_not_furniture."""
    from wenart.agent import causes as CS

    wardrobe = {"check": "F9", "severity": "major", "target": "f_L-1_024",
                "message": "wardrobe reaches 0.05 m² through the room outline, up to 0.020 m deep",
                "metrics": {"outside_m2": 0.052, "depth_m": 0.02}}
    assert CS.cause_of(wardrobe) == "within_tolerance" and CS.tools_for_finding(wardrobe) == []
    chair = dict(wardrobe, target="f_L1_022", message="chair reaches 0.20 m² through the room outline, up to "
                 "0.150 m deep", metrics={"outside_m2": 0.2, "depth_m": 0.15})
    assert CS.cause_of(chair) == "collision"
    tools = CS.tools_for_finding(chair)
    assert "move_piece" in tools and "mark_not_furniture" not in tools
    older = dict(chair, metrics={})                      # an older log: the text alone, no depth
    assert CS.cause_of(older) == "collision"
    duplicate = {"check": "F9", "target": "f_1", "message": "duplicate outline of a wardrobe", "metrics": {}}
    assert CS.cause_of(duplicate) == "wrong_type"        # the other F9 causes are unchanged


def test_no_library_gap_finding_for_a_piece_parametric_by_design():
    """P4a raised LG for the showers f_L0_013 / f_L0_014, which the final report lists as "no (by design)"; the
    agent now uses the report's rule (``asset.by_design`` or ``catalog.by_design_parametric``)."""
    from wenart.agent import critic_code as CC

    shower = {"id": "s1", "type": "shower", "room_id": "r", "library_gap": {"note": "no model"},
              "asset": {"method": "parametric"}}
    vanity = {"id": "v1", "type": "washbasin", "room_id": "r", "design": {"vanity": True},
              "library_gap": {"note": "no model"}, "asset": {"method": "module"}}
    flagged = {"id": "k1", "type": "wardrobe", "room_id": "r", "library_gap": {"note": "no model"},
               "asset": {"method": "module", "by_design": True}}
    coffee = {"id": "c1", "type": "table_coffee", "room_id": "r", "library_gap": {"note": "no model in the caps"},
              "asset": {"method": "parametric"}}
    found = CC.library_gaps({"furniture": [shower, vanity, flagged, coffee]})
    assert [f["target"] for f in found] == ["c1"]


# --------------------------------------------------------------------------
# Fit (F_furniture ask: the library verifier's better_fix)
# --------------------------------------------------------------------------

def _piece(pid, ftype, size, height=None):
    p = {"id": pid, "type": ftype, "level_id": "L-1", "room_id": "r", "status": "verified", "source": "from_documents",
         "footprint": {"center": [0.0, 0.0], "size": list(size), "rotation_deg": 0.0}, "front_deg": 270.0}
    if height is not None:
        p["height"] = height
    return p


@pytest.fixture(scope="module")
def catalog():
    from wenart.furniture import catalog as C

    return C.load()


def test_the_vision_quality_tie_break_reads_the_audit_doubt_text(catalog):
    """``assets/audit/write.py`` writes only ``vision_doubt`` strings, so the tie-break never fired and the doubtful
    models won exact ties on P4a's wardrobe f_L-1_023 (2.5685 x 0.6) and fridge f_L-1_096 (0.6 x 0.65). Now a
    doubt-free model of the same size step wins; a "not a <type>" doubt is not read."""
    from wenart.furniture import fit as F

    assert F.vision_quality_of({"audit": {"vision_doubt": ["vision quality 2 (<= 2)"]}}) == 2.0
    assert F.vision_quality_of({"audit": {"vision_doubt": "vision quality 1 (<= 2)"}}) == 1.0
    assert F.vision_quality_of({"audit": {"vision_doubt": ["the vision check says it is not a table_dining"]}}) is None
    assert F.vision_quality_of({"audit": {"vision_quality": 4, "vision_doubt": ["vision quality 2"]}}) == 4.0
    by_id = {e["id"]: e for t in ("wardrobe", "fridge") for e in catalog.candidates(t)}
    for pid, ftype, size, height, old in (
            ("f_L-1_023", "wardrobe", (2.5685, 0.6), None, "hssd_7094e30496b2735c235819e99c509769dc30502d"),):
        asset = F.fit_piece(_piece(pid, ftype, size, height), catalog, style_family="modern", mode="relaxed")
        assert asset["method"] == "library" and asset["asset_id"] != old, (pid, asset["asset_id"])
        chosen = by_id[asset["asset_id"]]
        assert not (chosen.get("audit") or {}).get("vision_doubt"), (pid, chosen["id"])
        assert F.rank_key(chosen, *size)[2] == F.rank_key(by_id[old], *size)[2]        # the same size step
    # Pin changed on purpose at the integration of the fix round after P5: the doubt-free fridges that fit f_L-1_096
    # (Smeg FAB28LV and its same-mesh twin FAB28XS6) were removed for a readable logo (audit check render_print), the
    # other doubt-free Smeg fridges fail the caps (17 % non-uniform), so the "vision quality 2" model wins again: the
    # tie-break still passes over no better-ranked model that fits
    # Pin changed again on 23 Oct 2026: the 3D Warehouse layer brought a doubt-free fridge of the same size step
    # (3dwh "Refrigerator", 0.595 x 0.625 x 1.84 m), which now wins the tie over the "vision quality 2" HSSD model
    asset = F.fit_piece(_piece("f_L-1_096", "fridge", (0.6, 0.65), 1.8), catalog, style_family="modern",
                        mode="relaxed")
    doubtful = "hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023"
    fridges = {e["id"]: e for e in catalog.candidates("fridge")}
    assert asset["method"] == "library" and asset["asset_id"] != doubtful
    chosen = fridges[asset["asset_id"]]
    assert not (chosen.get("audit") or {}).get("vision_doubt"), chosen["id"]
    assert F.rank_key(chosen, 0.6, 0.65)[2] == F.rank_key(fridges[doubtful], 0.6, 0.65)[2]
    assert "hssd_404146070e07145" not in str(asset["ranking"])


def test_a_pin_to_a_generated_model_is_refused_while_a_real_product_fits(catalog):
    """P4a seq 709: the agent pinned ``gen_fridge_mediterranean_3`` on the fridge f_L-1_090 (0.6 x 0.65) and it
    rendered as a faceted column; a real HSSD fridge fits the same footprint. The pin is refused with the reason; a
    pin to a real model is kept; the catalog tool labels generated models."""
    from wenart.agent import tools as T
    from wenart.furniture import fit as F

    gen = next(e["id"] for e in catalog.candidates("fridge") if e["id"].startswith("gen_fridge_mediterranean_3"))
    piece = _piece("f_L-1_090", "fridge", (0.6, 0.65), 1.8)
    asset = F.fit_piece(dict(piece, asset_pin=gen), catalog, style_family="modern", mode="relaxed")
    assert asset["asset_id"] != gen and "generated model (units guessed)" in asset["pin_refused"]
    assert not asset.get("pinned")
    real = asset["asset_id"]
    # 28 Oct 2026 (model_title audit_quality: the real 0.6 m fridges rated 2 left the library): another real fridge
    # when one fits the footprint, else a pin to the real model the ranking took
    other = next((e["id"] for e in catalog.candidates("fridge") if e.get("source") != "generated" and e["id"] != real
                  and F.fit_piece(dict(piece, asset_pin=e["id"]), catalog, style_family="modern",
                                  mode="relaxed").get("pinned")), real)
    kept = F.fit_piece(dict(piece, asset_pin=other), catalog, style_family="modern", mode="relaxed")
    assert kept["pinned"] == other and "pin_refused" not in kept
    assert "units guessed" in T.GENERATED_MODEL_NOTE


# --------------------------------------------------------------------------
# Reports (A_agent, P_report, L_render asks)
# --------------------------------------------------------------------------

def _agent_metrics(**memory_extra) -> dict:
    return {"edits": {"accepted": 25, "rejected": 40, "accepted_share": 0.38, "rejected_by_reason": {"memory": 3}},
            "rooms": {"code": 30, "vision": 10, "planner": 8, "planner_rooms": [], "fixable_rooms": [], "fixable": 0},
            "findings": {"before_totals": {"critical": 2, "major": 20}, "after_totals": {"critical": 0, "major": 9}},
            "time": {"agent_minutes": 30, "first_accepted_edit_s": 60},
            "memory": dict({"repeats_refused": 3, "dry_runs": 50, "plans": 12, "plans_valid": 7}, **memory_extra),
            "findings_removed": {"total": 24, "dry_recheck": {"1": 20}, "edits_removing_finding": 17,
                                 "edits_with_target": 24}}


def test_the_agent_report_names_the_edits_removing_their_finding_and_the_plan_statuses():
    """A_agent's ask: the final report's agent table shows P4a's 17 of 24 and why the default checklist ran; a log
    from before the fix round (no such keys) keeps the old rows."""
    from wenart.report import agent as RA

    text = "\n".join(RA.metrics_lines(_agent_metrics(plans_empty=3, plans_refused=1, plans_default=1)))
    assert "| edits removing their finding | 17 of 24 |" in text
    assert "| plans ok / empty / refused / default | 7 / 3 / 1 / 1 |" in text
    old = _agent_metrics()
    old["findings_removed"] = {"total": 24, "dry_recheck": {"1": 20}}
    text = "\n".join(RA.metrics_lines(old))
    assert "removing their finding" not in text and "plans ok" not in text


def test_the_report_cli_names_why_a_metric_has_no_data_and_the_left_out_previews(tmp_path, capsys, monkeypatch):
    """P_report's ask: the metrics13 line named only "no data: m11, m15"; real03 has no tree at all, which read like a
    missing input. Now each one carries its reason. The sheets13 line counts the baseline previews left out."""
    from wenart.report import metrics13 as MX
    from wenart.report import sheets13 as SH
    from wenart.report.__main__ import _no_data_reason
    from wenart.report.__main__ import main as report_main

    assert _no_data_reason({"text": "no drawn tree; no tree in the scene"}, MX.NO_DATA) == \
        " (no drawn tree; no tree in the scene)"
    assert _no_data_reason({"text": "no data"}, MX.NO_DATA) == ""
    assert _no_data_reason({"text": "no data (no scene manifest)"}, MX.NO_DATA) == " (no scene manifest)"
    out, base = tmp_path / "out", tmp_path / "base"
    out.mkdir()
    base.mkdir()

    def fake_write(run, baseline, json_path, md_path):
        return {"project": "p", "views": [], "warnings": [], "metrics": {
            "m11": {"value": MX.NO_DATA, "text": "no drawn tree; no tree in the scene"},
            "m15": MX.metric_15(MX.Run(root=out, name="p", layout="volume")),
            "m1": {"value": 50.0, "text": "1 of 2"}}}

    monkeypatch.setattr(MX, "write", fake_write)
    assert report_main(["metrics13", "--out", str(out), "--json", str(tmp_path / "m.json")]) == 0
    assert "no data: m11 (no drawn tree; no tree in the scene), m15 (no reviewer rubric file)" in capsys.readouterr().out
    monkeypatch.setattr(SH, "sheets", lambda run, baseline, d: {
        "project": "p", "sheets": {"a": "a.jpg"}, "missing_before": ["a"], "missing_after": [], "baseline_only": [],
        "before_left_out": [{"camera": "a", "file": "x.jpg", "reason": "not a view of the baseline report"}],
        "warnings": []})
    assert report_main(["sheets13", "--out", str(out), "--baseline", str(base), "--dir", str(tmp_path / "s")]) == 0
    assert "; baseline previews left out: 1" in capsys.readouterr().out
