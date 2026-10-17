"""Milestone 12 track S (docs/milestone12.md §4.8 D14, §6.4, B1, B7; CLAUDE.md library rules): the fit takes only
usable (audited, no NC/SA/ND) models, ranks them by the judges' quality list (B1), keeps real proportions (10 %,
0.85-1.20), falls back along the style chain (``style_fallback``), uses a related type only for a piece its group
needs, builds parametric pieces only by design (counters, wall cabinets, stairs, the kitchen and bath fixtures);
throws, curtains and blinds are procedural. Milestone 13 (docs/milestone13.md §12 D4, §13.2; track T1): a sofa, bed
or table without a model is no longer left out: the fallback ladder builds it (a module builder when
``wenart.blender.modules`` knows the type, else the parametric family) and ``library_gap`` names the step."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.furniture import catalog as C
from wenart.furniture import fit as F

from test_furniture_fit_v2 import FakeCatalog, decor_model, model, piece

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def _no_licence_mode_env(monkeypatch):
    """Milestone 13 review (15 Oct 2026): these tests rely on the fit's default licence mode (commercial); the pod
    jobs export WENART_LICENCE_MODE (relaxed, docs/milestone13.md §13.3), which must not reach them."""
    monkeypatch.delenv("WENART_LICENCE_MODE", raising=False)


def no_modules(monkeypatch):
    """Ladder step 2 answers "no module builder" (track T2's module is mocked away): step 3 is the parametric family."""
    monkeypatch.setattr(F, "module_plan_for", lambda piece, style=None: (None, "mocked: no module builder"))


def test_quality_list_ranks_the_models_again_b1():
    """B1: the catalogue stores ``quality`` as the two judges' answers; the old ``quality_of`` read 3.0 for a list."""
    assert F.quality_of({"quality": [5, 4]}) == 4.5 and F.quality_of({"quality": [2, 3]}) == 2.5
    assert F.quality_of({"quality": []}) == F.DEFAULT_QUALITY and F.quality_of({"quality": [True, "x"]}) == 3.0
    low = model("low", "sofa", 2.0 / 1.02, 0.9 / 1.02, 0.8, quality=[2, 2])
    high = model("high", "sofa", 2.0 / 1.03, 0.9 / 1.03, 0.8, quality=[5, 4])     # same 5 % size step
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([low, high]))
    assert fit["asset_id"] == "abo_high" and [c["quality"] for c in fit["candidates"]] == [4.5]


@pytest.mark.parametrize("extra, why", [({"licence": "CC-BY-NC-4.0", "licence_flag": "non_commercial"}, "licence"),
                                        ({"licence": "CC-BY-SA-4.0", "licence_flag": "share_alike"}, "licence"),
                                        ({"licence": "CC-BY-ND-4.0", "licence_flag": "no_derivatives"}, "licence"),
                                        ({"audit": {"status": "removed", "reasons": ["air bed"]}}, "audit")])
def test_only_usable_models_are_fitted(extra, why):
    bad = model("bad", "sofa", 2.0, 0.9, 0.8, quality=[5, 5], **extra)
    good = model("good", "sofa", 2.0, 0.9, 0.8, quality=[3, 3])
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([bad, good]))
    assert fit["asset_id"] == "abo_good"
    assert fit["excluded"][0]["id"] == "abo_bad" and why in fit["excluded"][0]["reason"]
    gap = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([bad]))
    assert gap["method"] == "parametric" and "no usable sofa model" in gap["fallback_reason"]   # M13: the ladder
    assert gap["library_gap"]["step"] == "parametric" and gap["excluded"][0]["id"] == "abo_bad"


def test_an_audit_fix_is_used_as_the_writer_left_it():
    """Track B's writer applies a fix to the catalogue fields (``fixes`` = the new values, ``before`` the old): the fit
    reads the fields and carries the audit record and flags."""
    fixed = model("fixed", "sofa", 2.0, 0.9, 0.8, real_product=True, has_cushions=True,
                  audit={"status": "fix", "reasons": ["front turned"], "fixes": {"front_quarter_turns": 1},
                         "before": {"bbox_m": [0.9, 2.0, 0.8]}, "version": "m12"})
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([fixed]))
    assert fit["method"] == "library" and fit["fit_scale"] == [1.0, 1.0, 1.0] and fit["audit"]["status"] == "fix"
    assert fit["real_product"] is True and fit["has_cushions"] is True and "front_quarter_turns" not in fit
    assert C.usable({"licence": "CC0", "audit": {"status": "keep"}}) and C.audit_status(fixed) == "fix"
    assert C.audit_status({"id": "x"}) is None


def test_real_products_first_within_their_size_step():
    other = model("other", "sofa", 2.0, 0.9, 0.8, quality=[5, 5])
    real = model("real", "sofa", 2.0 / 1.02, 0.9 / 1.02, 0.8, quality=[3, 3], real_product=True)
    assert F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([other, real]))["asset_id"] == "abo_real"
    assert F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([other, dict(real, real_product=False)]))[
        "asset_id"] == "abo_other"                                                  # without the flag: quality


def test_fitted_height_inside_the_real_size_table(monkeypatch):
    """D23 (one size table, ``wenart.furniture.sizes``): a model whose fitted height is outside the type's real
    height range (+-15 %) is refused (the diagnosis: bathtubs built 0.89 m high, stoves 0.54 m)."""
    from wenart.furniture import sizes

    real = sizes.real_range

    def with_heights(ftype):
        r = real(ftype)
        return dict(r, height=(0.40, 0.72)) if ftype == "bathtub" and r else r

    monkeypatch.setattr(sizes, "real_range", with_heights)
    tall = model("tall", "bathtub", 1.7, 0.75, 0.89)
    ok = model("ok", "bathtub", 1.7, 0.75, 0.58, quality=[2, 2])
    fit = F.fit_piece(piece("bathtub", 1.7, 0.75), FakeCatalog([tall, ok]))
    assert fit["asset_id"] == "abo_ok" and [t["height_ok"] for t in fit["candidates"]] == [False, True]
    alone = F.fit_piece(piece("bathtub", 1.7, 0.75), FakeCatalog([tall]))
    assert alone["method"] == "parametric" and "outside the real height 0.4-0.72 m" in alone["fallback_reason"]
    assert F.height_fits(0.82, (0.40, 0.72)) and not F.height_fits(0.84, (0.40, 0.72))
    assert F.height_fits(9.0, None)


def test_decor_models_rest_as_their_type_needs():
    hanging = decor_model("hanging", "table_lamp", 0.3, 0.3, 0.5, contact="hangs")
    standing = decor_model("standing", "table_lamp", 0.3, 0.3, 0.5, contact="flat_bottom")
    it = {"id": "d", "type": "table_lamp", "size": [0.35, 0.35, 0.6], "host_id": "f"}
    assert F.fit_decor_item(it, FakeCatalog(decor=[hanging])) is None
    assert F.fit_decor_item(it, FakeCatalog(decor=[hanging, standing]))["asset_id"] == "abo_standing"
    assert C.contact_fits({"contact": None}, "vase") and C.contact_fits({"contact": "hangs"}, "mirror")


def test_style_family_falls_back_along_its_chain():
    rustic = model("rustic", "sofa", 2.0, 0.9, 0.8, styles=("rustic",))
    classic = model("classic", "sofa", 2.0, 0.9, 0.8, styles=("classic",))
    modern = model("modern", "sofa", 2.0, 0.9, 0.8, styles=("modern",))
    cat = FakeCatalog([rustic, classic, modern])
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), cat, style_family="mediterranean")
    assert fit["asset_id"] == "abo_rustic" and fit["style_family"] == "rustic"
    assert fit["style_fallback"] == {"wanted": "mediterranean", "used": "rustic",
                                     "chain": ["mediterranean", "rustic", "classic"],
                                     "why": "mediterranean: no model for style mediterranean"}
    assert F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([classic, modern]),
                       style_family="mediterranean")["asset_id"] == "abo_classic"
    fit = F.fit_piece(piece("sofa", 2.0, 0.9), FakeCatalog([modern]), style_family="industrial")
    assert fit["asset_id"] == "abo_modern" and fit["style_fallback"]["used"] == "modern"
    assert "style_fallback" not in F.fit_piece(piece("sofa", 2.0, 0.9), cat, style_family="classic")
    assert F.style_chain(None) == [None] and F.style_chain("industrial") == ["industrial", "modern"]
    for family, chain in F.STYLE_FALLBACK.items():
        assert family not in chain and set(chain) <= {f for f, _ in __import__(
            "wenart.style.vocabulary", fromlist=["x"]).STYLE_FAMILIES}


def test_a_sofa_bed_or_table_without_a_model_goes_down_the_ladder(monkeypatch):
    """Milestone 12 left them out (``none``); Milestone 13 (D4) builds them: a module builder when one exists for
    the type (the long table), else the parametric family; the gap names the step so it can be closed later."""
    real_step_2 = F.module_plan_for
    no_modules(monkeypatch)
    for ftype, size in (("sofa", (2.0, 0.9)), ("bed_double", (1.6, 2.0)), ("table_dining", (1.6, 0.9)),
                        ("table_coffee", (1.0, 0.6))):
        odd = model("odd", ftype, size[0] * 1.5, size[1], 0.8)               # 50 % wider: outside the caps
        fit = F.fit_piece(piece(ftype, *size), FakeCatalog([odd]))
        assert fit["method"] == "parametric" and fit["library_gap"]["used"].startswith("parametric family")
        assert fit["library_gap"]["type"] == ftype and "10 % non-uniform" in fit["library_gap"]["reason"]
        assert fit["library_gap"]["step"] == "parametric" and fit["asset_id"] == f"parametric:{ftype}"
        assert [(s["step"], s["result"]) for s in fit["ladder"]] == [
            ("library", "no model"), ("module", "no module builder"), ("parametric", "used")]
        assert fit["ladder"][1]["reason"] == "mocked: no module builder"
    # step 2: a module plan (track T2's wenart.blender.modules.module_plan) wins over the family
    plan = {"builder": "table_long", "modules": [{"kind": "top", "size_m": [2.4, 1.0, 0.04], "pos_m": [0, 0],
                                                  "rot_deg": 0, "material": "wood"}],
            "footprint_m": [2.4, 1.0], "height_m": 0.75, "products": ["dining table 2.40 x 1.00 m"]}
    monkeypatch.setattr(F, "module_plan_for", lambda piece, style=None: (plan, ""))
    odd = model("odd", "table_dining", 3.6, 1.0, 0.75)
    fit = F.fit_piece(piece("table_dining", 2.4, 1.0), FakeCatalog([odd]))
    assert fit["method"] == "module" and fit["asset_id"] == "module:table_dining:table_long"
    assert fit["module_plan"] == plan and fit["bbox_m"] == [2.4, 1.0, 0.75] and fit["library"] == "module"
    assert fit["library_gap"]["step"] == "module" and fit["library_gap"]["used"].startswith("module builder table_long")
    assert [s["step"] for s in fit["ladder"]] == ["library", "module"] and fit["licence"] == "n/a"
    assert fit["commercial_safe"] is True and fit["licence_flag"] == "none" and "by_design" not in fit
    # a builder that raises is logged, never fatal: step 3 follows
    def boom(piece, style=None):
        raise RuntimeError("builder bug")
    monkeypatch.setattr(F, "module_plan_for", real_step_2)
    monkeypatch.setattr("wenart.blender.modules.module_plan", boom)
    fit = F.fit_piece(piece("table_dining", 2.4, 1.0), FakeCatalog([odd]))
    assert fit["method"] == "parametric" and "module_plan failed: RuntimeError: builder bug" in fit["ladder"][1]["reason"]


def test_related_type_only_when_the_group_needs_it(monkeypatch):
    no_modules(monkeypatch)
    chair = model("chair", "chair", 0.8, 0.8, 0.8)
    odd = model("wide", "armchair", 1.4, 0.8, 0.8)
    cat = FakeCatalog([odd, chair])
    added = piece("armchair", 0.8, 0.8, source="added_by_ai")
    fit = F.fit_piece(added, cat)
    assert fit["method"] == "parametric" and "related_type" not in fit         # nobody needs it: the family (M13)
    assert fit["library_gap"]["step"] == "parametric"
    grouped = dict(added, group={"group_id": "g1", "group": "seating", "role": "partner"})
    for p in (grouped, piece("armchair", 0.8, 0.8)):                           # a group member, a drawn piece
        fit = F.fit_piece(p, cat)
        assert fit["method"] == "library" and fit["asset_id"] == "abo_chair" and fit["related_type"] == "chair"
        assert fit["library_gap"]["used"] == "related type chair: abo_chair" and fit["library_gap"]["type"] == \
            "armchair"
        assert fit["library_gap"]["step"] == "library" and fit["ladder"][-1]["result"] == "related type chair: abo_chair"
    assert "sofa" not in F.RELATED_TYPES and "bed_double" not in F.RELATED_TYPES
    assert not set(F.RELATED_TYPES) & set(C.PARAMETRIC_FIXTURE_TYPES)


def test_parametric_only_by_design(monkeypatch):
    assert set(C.BY_DESIGN_PARAMETRIC_TYPES) == {"kitchen_counter", "kitchen_island", "wall_cabinet", "stair",
                                                 "shower", "washing_machine", "fridge", "toilet", "washbasin",
                                                 "bathtub", "sink_kitchen", "stove"}
    assert C.by_design_parametric({"type": "washbasin"}) and C.by_design_parametric(
        {"type": "wardrobe", "design": {"built_in": True}}) and not C.by_design_parametric({"type": "wardrobe"})
    odd = model("odd", "shower", 2.0, 0.9, 2.0)
    no_modules(monkeypatch)
    fit = F.fit_piece(piece("shower", 0.9, 0.9), FakeCatalog([odd]))
    assert fit["method"] == "parametric" and fit["by_design"] and "our parametric shower" in fit["fallback_reason"]
    assert fit["library_gap"]["used"] == "our parametric fixture (by design)" and fit["library_gap"]["step"] == "parametric"
    assert fit["ladder"][-1] == {"step": "parametric", "result": "used (by design)",
                                 "reason": "docs/milestone12.md §6.4: made to the drawing"}
    # Milestone 13: with a module builder for the type (T2's bath set) the fixture is a module, still by design
    plan = {"builder": "bath_set", "modules": [{"kind": "tray", "size_m": [0.9, 0.9, 0.04], "pos_m": [0, 0],
                                                "rot_deg": 0, "material": "ceramic"}],
            "footprint_m": [0.9, 0.9], "height_m": 2.0, "products": ["shower tray 90 x 90"]}
    monkeypatch.setattr(F, "module_plan_for", lambda piece, style=None: (plan, ""))
    fit = F.fit_piece(piece("shower", 0.9, 0.9), FakeCatalog([odd]))
    assert fit["method"] == "module" and fit["by_design"] and fit["library_gap"]["step"] == "module"
    assert fit["library_gap"]["used"].endswith("(by design)")
    # a counter run is made to the drawing: by design and no gap at all (nothing to close)
    counter = F.fit_piece(piece("kitchen_counter", 2.4, 0.6), FakeCatalog([]))
    assert counter["method"] == "module" and counter["by_design"] and "library_gap" not in counter


def test_fit_building_writes_the_gap_on_the_piece_and_changes_nothing_else(monkeypatch):
    no_modules(monkeypatch)
    cat = FakeCatalog([model("odd", "sofa", 3.0, 0.9, 0.8), model("ok", "nightstand", 0.5, 0.4, 0.5)])
    building = {"project": {"id": "t"}, "furniture": [piece("sofa", 2.0, 0.9),
                                                      piece("nightstand", 0.5, 0.4, pid="f_L0_002")]}
    before = copy.deepcopy(building)
    fitted = F.fit_building(building, cat)
    assert building == before
    F.assert_only_assets_changed(building, fitted)
    sofa, night = fitted["furniture"]
    assert sofa["library_gap"]["type"] == "sofa" and "library_gap" not in night
    assert sofa["asset"]["method"] == "parametric" and sofa["library_gap"]["step"] == "parametric"   # M13 ladder
    report = F.fit_report(fitted)
    assert "1 parametric fallbacks" in report and "## Library gaps" in report
    assert "- f_L0_001 (sofa, style None): parametric family (built below the library level)" in report
    assert "## Built below the library level" in report and "- f_L0_001 (sofa): parametric:" in report
    assert "commercial-safe: yes" in report and "Licence mode (Milestone 13): commercial" in report
    refit = F.fit_building(dict(fitted, furniture=[dict(sofa, footprint=dict(sofa["footprint"], size=[3.0, 0.9]))]),
                           cat)
    assert "library_gap" not in refit["furniture"][0]                     # a later fit clears a stale gap
    # a piece that is not built (not furniture, removed) keeps ``none``: the ladder stops at the library step
    gone = F.fit_building({"furniture": [dict(piece("sofa", 2.0, 0.9), build=False)]}, cat)["furniture"][0]
    assert gone["asset"]["method"] == "none" and gone["library_gap"]["used"] == "nothing (not built)"
    # Milestone 13 (16 Oct 2026): a not-built piece no longer searches the library at all (with the HSSD layer a
    # model happened to fit one and was credited although nothing is built), so every step reads "not tried".
    assert [s["result"] for s in gone["asset"]["ladder"]] == ["not tried", "not tried", "not tried"]


def test_throws_curtains_and_blinds_are_procedural_b7():
    """B7: Milestone 11 fitted any 'throw' model (a juice machine, a bench) squashed to 5 cm; now never a model."""
    cat = FakeCatalog(decor=[decor_model("juice", "throw", 0.6, 0.4, 0.3), decor_model("c", "curtain", 1.4, 0.1, 2.4),
                             decor_model("b", "blind", 1.2, 0.05, 1.2)])
    for dtype, size in (("throw", (1.5, 0.5, 0.05)), ("curtain", (1.4, 0.08, 2.4)), ("blind", (1.2, 0.06, 1.0))):
        it = {"id": "d", "type": dtype, "size": list(size), "host_id": "f"}
        assert F.fit_decor_item(it, cat) is None
    assert set(F.PROCEDURAL_DECOR_TYPES) == {"throw", "curtain", "blind"}
    assert not set(F.PROCEDURAL_DECOR_TYPES) & set(F.DECOR_LIBRARY_TYPES)


def test_decor_models_must_be_usable():
    nc = decor_model("nc", "vase", 0.18, 0.18, 0.4, licence="CC-BY-NC-4.0", licence_flag="non_commercial")
    ok = decor_model("ok", "vase", 0.18, 0.18, 0.4)
    it = {"id": "d", "type": "vase", "size": [0.18, 0.18, 0.4], "host_id": "f"}
    assert F.fit_decor_item(it, FakeCatalog(decor=[nc])) is None
    assert F.fit_decor_item(it, FakeCatalog(decor=[nc, ok]))["asset_id"] == "abo_ok"


@pytest.mark.parametrize("project", ["real02", "real03"])
def test_committed_buildings_parametric_only_by_design_gaps_listed(project):
    path = ROOT / "results" / "furniture" / project / "building_final.json"
    if not path.is_file():
        pytest.skip("no committed building")
    building = json.loads(path.read_text(encoding="utf-8"))
    for p in building["furniture"]:
        p.pop("library_gap", None)
    fitted = F.fit_building(building, C.load(), style_family="modern", mode="commercial")
    built = [p for p in fitted["furniture"] if p.get("build", True) is not False and p["type"] != "unknown"]
    for p in built:
        a = p["asset"]
        # Milestone 13 (D4): a built piece is never ``none``; below the library level it is a module or the family
        assert a["method"] in ("library", "module", "parametric"), p["id"]
        if a["method"] in ("parametric", "module") and not a.get("by_design"):
            assert p["library_gap"]["step"] == a["method"], p["id"]
        if a["method"] == "parametric" and C.by_design_parametric(p):
            assert a["by_design"]
        if a["method"] == "library":
            assert C.usable(a, "commercial") and a["commercial_safe"] is True and a["licence_flag"] == "none"
            sx, sy, sz = a["fit_scale"]
            assert sx == sy == sz                                           # Milestone 13: uniform
            cap, (lo, hi) = (F.RELAXED_CAP, F.RELAXED_RANGE) if a.get("caps_relaxed") else (1.10, (0.85, 1.20))
            drawn, got = p["footprint"]["size"][1], a["bbox_m"][1]
            assert max(drawn, got) / min(drawn, got) <= cap + 1e-6 and lo - 1e-6 <= sx <= hi + 1e-6, p["id"]
    below = sum(1 for p in built if p["asset"]["method"] != "library" and not p["asset"].get("by_design"))
    assert below < 0.25 * len(built)


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026): S2 no longer lets a sink or stove stand buried inside a kitchen run
# --------------------------------------------------------------------------

def _k_piece(pid, ftype, center, size, rot=0.0, **extra):
    return dict({"id": pid, "type": ftype, "level_id": "L0", "room_id": "r_k", "status": "verified",
                 "source": "from_documents", "front_deg": (270.0 + rot) % 360.0,
                 "footprint": {"center": list(center), "size": list(size), "rotation_deg": rot},
                 "asset": {"method": "parametric", "asset_id": f"parametric:{ftype}"}}, **extra)


def _k_mesh(p, plan=None, base=0.0):
    from wenart.blender import modules as MOD
    from wenart.blender import parametric as PM

    fp = p["footprint"]
    if plan is not None:
        parts = MOD.module_parts(plan)
    else:
        parts = PM.build_parts(p["type"], *fp["size"], PM.proxy_height(p["type"], p.get("height"))[0], piece=p)
    v, f, _k = PM.world_mesh(parts, fp["center"], fp["rotation_deg"], base)
    return {"verts": v, "faces": f}


def _k_building(furniture):
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
            "rooms": [{"id": "r_k", "level_id": "L0"}], "walls": [], "furniture": list(furniture), "decor": []}


def test_s2_finds_a_sink_or_stove_buried_in_a_kitchen_run_and_not_one_built_in_or_in_its_gap():
    from wenart.blender import modules as MOD
    from wenart.blender import scene_checks as SC

    run = _k_piece("k_run", "kitchen_counter", (2.0, 1.0), (2.4, 0.6), height=0.9)
    sink = _k_piece("k_sink", "sink_kitchen", (1.2, 1.0), (0.8, 0.5))
    stove = _k_piece("k_stove", "stove", (2.75, 1.0), (0.6, 0.6))
    plain = MOD.module_plan(run)                                        # P3: full base units, an uncut worktop
    meshes = {"k_run": _k_mesh(run, plain), "k_sink": _k_mesh(sink), "k_stove": _k_mesh(stove)}
    report = SC.measure_pure(meshes, _k_building([run, sink, stove]))
    s2 = {v["target"]: v for v in report["violations"] if v["check"] == "S2"}
    assert set(s2) == {"k_sink", "k_stove"}                             # the old exemption said nothing
    assert s2["k_sink"]["metrics"]["other"] == "k_run" and s2["k_sink"]["metrics"]["inside_share"] > 0.4
    assert "buried in the kitchen_counter k_run" in s2["k_stove"]["message"]
    # fix round after P3, part 2: the buried member's depth (inside_share x its smaller drawn side), so metrics13's
    # "S2 > 3 cm" and the agent's causes count it as a deep cut
    for pid, side in (("k_sink", 0.5), ("k_stove", 0.6)):
        m = s2[pid]["metrics"]
        assert m["depth_m"] == pytest.approx(m["inside_share"] * side, abs=1e-3) and m["depth_m"] > 0.03
        assert report["measured"][pid]["kitchen_run"]["depth_m"] == pytest.approx(m["depth_m"])
    # the fix: the sink is built into the run (no object of its own), the stove stands in its gap
    hints = {"sink_pos_m": [1.2, 1.0], "sink_w_m": 0.8, "sink_piece": "k_sink",
             "ranges": [dict(MOD.member_in_run(run, stove), id="k_stove", type="stove")]}
    fixed = MOD.module_plan(dict(run, module_hints=hints))
    assert fixed["built_ins"][0]["id"] == "k_sink" and fixed["gaps"][0]["id"] == "k_stove"
    meshes = {"k_run": _k_mesh(run, fixed), "k_stove": _k_mesh(stove)}
    report = SC.measure_pure(meshes, _k_building([run, sink, stove]))
    assert not [v for v in report["violations"] if v["check"] == "S2"]
    assert report["measured"]["k_stove"]["kitchen_run"]["inside_share"] < 0.05


def test_s2_keeps_the_allowance_for_kitchen_pieces_that_only_meet_the_run():
    from wenart.blender import modules as MOD
    from wenart.blender import scene_checks as SC

    run = _k_piece("k_run", "kitchen_counter", (2.0, 1.0), (2.4, 0.6), height=0.9)
    fridge = _k_piece("k_fridge", "fridge", (3.45, 1.0), (0.6, 0.6))   # 5 cm into the run's end (a drawing slip)
    wall = _k_piece("k_wall", "wall_cabinet", (2.0, 1.125), (1.2, 0.35), mount_bottom_m=1.4)
    other = _k_piece("k_run2", "kitchen_counter", (0.5, 1.9), (0.6, 1.8), height=0.9)        # an L corner overlap
    meshes = {"k_run": _k_mesh(run, MOD.module_plan(run)), "k_fridge": _k_mesh(fridge),
              "k_wall": _k_mesh(wall, base=1.4), "k_run2": _k_mesh(other, MOD.module_plan(other))}
    report = SC.measure_pure(meshes, _k_building([run, fridge, wall, other]))
    assert not [v for v in report["violations"] if v["check"] == "S2"]
    assert report["measured"]["k_fridge"]["kitchen_run"]["inside_share"] < SC.TOLERANCES["kitchen_buried_share"]
    assert "kitchen_run" not in report["measured"]["k_wall"]
    assert SC.kitchen_host_member(run, wall) == (None, None) and SC.kitchen_host_member(run, other) == (None, None)
    assert SC.kitchen_host_member(fridge, run) == (run, fridge)


def test_part2_the_buried_s2_depth_counts_in_metrics13_and_in_the_agent_causes():
    """Fix round after P3, part 2 (17 Oct 2026): the review's case. The 'buried in the run' S2 violation had no
    ``depth_m``, so metrics13's metric 6 counted it only under S2_all, never under "S2 > 3 cm"; now it counts, and
    the agent's cause is a collision (never within tolerance)."""
    from types import SimpleNamespace

    from wenart.agent import causes as CA
    from wenart.blender import modules as MOD
    from wenart.blender import scene_checks as SC
    from wenart.report import metrics13 as M13

    run = _k_piece("k_run", "kitchen_counter", (2.0, 1.0), (2.4, 0.6), height=0.9)
    sink = _k_piece("k_sink", "sink_kitchen", (1.2, 1.0), (0.8, 0.5))
    report = SC.measure_pure({"k_run": _k_mesh(run, MOD.module_plan(run)), "k_sink": _k_mesh(sink)},
                             _k_building([run, sink]))
    (v,) = [v for v in report["violations"] if v["check"] == "S2"]
    events = [{"kind": "finding", "round": 1, "checklist": "S2", "target": v["target"],
               "evidence": {"metrics": v["metrics"]}}]
    m6 = M13.metric_6(SimpleNamespace(log={"events": events}, log_first_seq=0))
    assert m6["parts"]["S2"] == 1 and m6["parts"]["S2_all"] == 1
    assert CA.cause_of(v) == "collision"
    assert SC.buried_depth(sink, 0.5) == pytest.approx(0.25) and SC.buried_depth(sink, 0.0) == 0.0
    assert SC.buried_depth({"id": "x"}, 0.9) == 0.0
