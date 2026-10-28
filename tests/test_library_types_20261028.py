"""28 Oct 2026 (user on real04 run 20261028-005318-full): "what is this miniature table makes no sense" (a 2.4 m high
table with its barstools, read in feet, fitted as a coffee table), "This makes no sense and terrible sink" (a
double-bowl kitchen sink as the washbasin of five bathrooms) and "is this a window? how is this making sense?" (a
"WARDROBE" whose end shows a glazed frame; the vision audit said it is not a wardrobe). The library rules of
``wenart.furniture.model_title``: a stated size against the box with the unit factors, sets of pieces, a title of
another type or use, the audit's own doubts (type, size, a front turned off its detail side); the catalogue gate
(``catalog.usable``), the audit check and decision, the catalogue pass, the swap tool, the fit report, the code critic
(``LT``), the vision checklist (D2) and Argus (``P11``). CPU only.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.assets.audit import checks as CH
from wenart.assets.audit import decide as DE
from wenart.assets.audit import keywords as K
from wenart.assets.audit import write as W
from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from wenart.furniture import model_title as MT

from test_furniture_fit_v2 import FakeCatalog, model, piece

ROOT = Path(__file__).resolve().parents[1]
FACIT = "3dwh_f2d78684d4e41a5b93b167d0"
SINK = "3dwh_9314d5619fde2de825a4a2a1"
INODORO = "3dwh_1bcba362feacb0144ea5a4e1"
WARDROBE = "3dwh_e41345920f4dce2514160e34"
FACIT_TITLE = "Facit High Table W2400 D800 mm NamNam Barstool Low back Metal Leg"


@pytest.fixture(scope="module")
def library():
    return C.load()


def entry(ftype, title, box, source="3dwh", **extra):
    w, d, h = box
    e = model(title.replace(" ", "_")[:20], ftype, w, d, h, source="abo")
    e.update(source=source, title=title, name=title)
    e.update(extra)
    return e


def facit():
    """The user's coffee table as the catalogue held it (box in feet, the 3D Warehouse record)."""
    return entry("table_coffee", FACIT_TITLE, (0.7315, 0.4228, 0.3292),
                 **{"3dwh": {"rel": f"3D Warehouse Furniture/Stools/{FACIT_TITLE} [81f6fb39]/model.glb",
                             "factor": 0.3048, "unit": "feet"},
                    "audit": {"status": "keep", "reasons": [],
                              "vision_doubt": ["the vision check says it is not a table_coffee (a table_dining)",
                                               "the vision check sees more than one object"]}})


def sink(rel="3D Warehouse Furniture/Kitchen/Sink [3dd30a43]/model.glb", title="Sink"):
    return entry("washbasin", title, (0.965, 0.5, 0.3923), **{"3dwh": {"rel": rel, "factor": 1.0},
                                                               "audit": {"status": "keep", "reasons": []}})


def rules(e) -> list[str]:
    return [f["rule"] for f in MT.findings(e)]


# --------------------------------------------------------------------------
# Stated sizes
# --------------------------------------------------------------------------

@pytest.mark.parametrize("title, dims, unit", [
    ("Facit High Table W2400 D800 mm NamNam", [("w", 2.4), ("d", 0.8)], "mm"),
    ("Coffee Table, 120 x 60 x 36cm, Oak", [(None, 1.2), (None, 0.6), (None, 0.36)], "cm"),
    ('Gazette Vanity 34"hx30"w Coffee Brown', [("h", 0.8636), ("w", 0.762)], "in"),
    ('Rug 3\' 9" x 5\' 9", Beige', [(None, 1.143), (None, 1.7526)], "ft"),
    ("Table 1.2 x 0.6 m", [(None, 1.2), (None, 0.6)], "m"),
])
def test_stated_sizes_reads_the_size_a_title_gives(title, dims, unit):
    got = MT.stated_sizes(title)
    assert len(got) == 1 and got[0]["unit_from"] == "title" and got[0]["unit"] == unit
    assert [(lab, pytest.approx(v, abs=1e-3)) for lab, v in got[0]["dims"]] == dims


@pytest.mark.parametrize("title", [
    "AmazonBasics Metal Bed - 14 Inch Height for Under-Bed Storage",   # one number: which side?
    "Lamp 60W 2700K", "Model 2400 by Studio", "Sofa 3M fabric",          # watts, codes, a brand
    'Dining Table, Expandable, 39-57"L, Brown', "Dining Table 160/205 x 90 x 74cm",   # ranges, alternatives
    "Haworth Table-Planes Rect30x60 Y-Leg", "Kids 70's chair",           # a code, a quote that is no unit
])
def test_stated_sizes_never_reads_a_guess(title):
    assert [g for g in MT.stated_sizes(title) if g["dims"]] == []


def test_a_size_without_its_unit_only_confirms():
    g = MT.stated_sizes("Interior Door 80x36 Flat Hollow Core")[0]
    assert g["unit_from"] == "none" and g["dims"] == [] and {u for u, _d in g["unitless"]} >= {"cm", "in"}
    # a door 80" x 36" agrees in inches; a unitless size never refuses
    door = entry("bookshelf", "Shelf 80x36", (0.2, 0.1, 0.1), source="abo")
    assert MT.size_finding(door) is None


def test_the_facit_table_is_refused_for_its_units_and_as_a_set():
    e = facit()
    found = {f["rule"]: f for f in MT.findings(e)}
    size = found["stated_size"]
    assert size["status"] == "refuse"
    assert size["metrics"]["read_as"] == "feet" and size["metrics"]["should_be"] == "metres"
    assert size["metrics"]["factor"] == pytest.approx(1 / 0.3048, rel=1e-4)
    assert size["metrics"]["corrected_box_m"][0] == pytest.approx(2.4, abs=0.001)
    assert found["title_set"]["status"] == "refuse" and "barstool" in found["title_set"]["reason"]
    assert C.usable(e, "relaxed") is False
    assert "its names or its audit refuse it" in C.unusable_reason(e, "relaxed")


def test_a_unit_error_with_a_real_size_behind_it_is_fixed_by_rescale():
    # a dining table 1.8 x 0.9 x 0.75 m whose box was read in feet
    e = entry("table_dining", "Oslo Dining Table 1800 x 900 x 750 mm", (0.5486, 0.2743, 0.2286),
              audit={"status": "keep", "reasons": []})
    f = MT.size_finding(e)
    assert f["status"] == "fix" and f["fix"]["rescale"] == pytest.approx(1 / 0.3048, rel=1e-4)
    assert C.usable(e, "relaxed") is False                 # not used until the catalogue is corrected
    doc = {"entries": [e], "decor": []}
    stats = W.apply_title_rules(doc, "2026-10-28T12:00:00Z")
    assert stats["fixed"] == [e["id"]] and not stats["removed"]
    fixed = doc["entries"][0]
    assert fixed["audit"]["status"] == "fix" and fixed["audit"]["title_rules"]["status_before"] == "keep"
    assert fixed["bbox_m"] == pytest.approx([1.8, 0.9, 0.75], abs=0.002)
    assert fixed["unit_scale"] == pytest.approx(1 / 0.3048, rel=1e-4)
    assert fixed["audit"]["before"]["bbox_m"] == [0.5486, 0.2743, 0.2286]
    assert MT.findings(fixed) == [] and C.usable(fixed, "relaxed")
    again = W.apply_title_rules(doc, "2026-10-28T13:00:00Z")      # idempotent: the corrected entry agrees
    assert not again["fixed"] and not again["removed"] and doc["entries"][0]["bbox_m"] == fixed["bbox_m"]


@pytest.mark.parametrize("ftype, title, box", [
    ("table_coffee", "Coffee Table, 120 x 60 x 40 cm, Oak", (1.2, 0.6, 0.42)),
    ("sofa_corner", "Enan 3-Seater L-Shaped Corner Sofa, 266 x 86 x 73 cm", (2.66, 1.61, 0.73)),   # the chaise
    ("bed_double", "Kolva Double Bed Frame, 144.5 x 194.5 x 31.7cm, Grey", (1.49, 1.95, 0.43)),   # the headboard
    ("shower", "Dusche/douche Setaplano 90 x 90 x 4,5 cm", (0.92, 0.92, 2.0)),                     # the screen
])
def test_a_box_larger_than_the_listing_by_its_parts_agrees(ftype, title, box):
    assert MT.size_finding(entry(ftype, title, box, source="abo")) is None


def test_stated_and_measured_sizes_that_disagree_refuse_the_model():
    e = entry("table_coffee", "Movian Kyyvesi, Coffee Table, 120 x 60 x 40 cm, Oak Effect", (0.8, 0.4, 0.4),
              source="abo")
    f = MT.size_finding(e)
    assert f["status"] == "refuse" and "disagree" in f["reason"] and "no unit explains it" in f["reason"]
    # a rug is sized by the fit: its listing size says nothing
    assert MT.size_finding(entry("rug", "Rug, 8' x 10', Natural", (1.68, 1.08, 0.01), source="abo",
                                 kind="decor", decor_type="rug")) is None


# --------------------------------------------------------------------------
# Sets
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ftype, title", [
    ("chair", "Dining Table and 6 Chairs"),
    ("armchair", "Herman Miller Eames Lounge Chair and Ottoman"),
    ("table_dining", "LÄCKÖ IKEA table 2 chairs"),
    ("table_coffee", "Facit Round Table Dia 1200 mm Sky Chairs 4 Leg"),
    ("sofa", "Traditional classic sofa & armchair"),
    ("table_coffee", "Bistro set for two"),
])
def test_a_title_naming_the_pieces_of_a_group_is_a_set(ftype, title):
    f = MT.set_finding(entry(ftype, title, (1.0, 0.8, 0.75)))
    assert f and f["status"] == "refuse" and "never one" in f["reason"]


@pytest.mark.parametrize("ftype, title", [
    ("office_chair", "AmazonBasics Classic Leather Office Desk Guest Chair"),   # a modifier, no join
    ("bar_stool", "Bar stool for kitchen table"),                              # what it is for
    ("chair", "Dining table chair, oak"),                                       # a compound
    ("nightstand", "Rivet King Street Industrial Floating Side Table Night Stand"),
    ("sofa_corner", "Stuart 3-Piece Sectional"),                                # one L-sofa in pieces
    ("chair", "Set of 2 dining chairs"),                                        # an ABO pack: one chair's mesh
])
def test_modifiers_contexts_and_packs_are_no_set(ftype, title):
    assert MT.set_finding(entry(ftype, title, (1.0, 0.8, 0.75), source="abo")) is None


def test_a_pack_with_the_vision_check_seeing_several_objects_is_a_set():
    e = entry("chair", "Set of 2 dining chairs", (0.5, 0.5, 0.9), source="abo",
              audit={"status": "keep", "vision_doubt": ["the vision check sees more than one object"]})
    assert MT.set_finding(e)["status"] == "refuse"


# --------------------------------------------------------------------------
# Types and use
# --------------------------------------------------------------------------

def test_a_bare_sink_is_a_kitchen_sink_never_a_washbasin():
    f = MT.type_finding(sink())
    assert f["rule"] == "title_type" and "kitchen (source folder)" in f["reason"]
    f2 = MT.type_finding(sink(rel=""))                      # no folder: the bare word decides
    assert "a bare sink is a kitchen sink" in f2["reason"]
    assert C.usable(sink(), "relaxed") is False


@pytest.mark.parametrize("title, extra, ok", [
    ("36 Industrial Vanity with Concrete Rectangle Sink", {}, True),
    ("Cooke & Lewis Lanzo Square Cloackroom Basin", {}, True),
    ("ProCasa Cinque Waschbecken/Lave-main/Lavamano", {}, True),
    ("Regia Juke Box Light 870000-50 nero glass sink", {"hssd": {"found_in": "bathroom"}}, True),
    ("Regia Juke Box Light 870000-50 nero glass sink", {}, False),
    ("Stainless Double Bowl Sink with Drainboard", {}, False),
    ("Sink Kitchen Sink Built-in Sink Einbauspüle Spüle", {}, False),
    ("Mobilya1", {}, True),                                 # no type word: the audit's two vision passes typed it
    ("Mobilya1", {"audit": {"status": "keep", "vision_doubt": ["the two vision passes disagree: a washbasin and a "
                                                               "tray"]}}, False),
])
def test_a_washbasin_needs_bathroom_evidence(title, extra, ok):
    e = entry("washbasin", title, (0.6, 0.45, 0.85), source="hssd", **extra)
    assert (MT.type_finding(e) is None) is ok


def test_a_kitchen_sink_named_for_the_bathroom_is_no_kitchen_sink():
    e = entry("sink_kitchen", "Bathroom Vessel Sink", (0.6, 0.45, 0.9))
    assert "a bathroom basin, not a kitchen sink" in MT.type_finding(e)["reason"]
    assert MT.type_finding(entry("sink_kitchen", "Kitchen sink unit 80 cm", (0.8, 0.6, 0.9))) is None


def test_a_title_of_another_type_is_refused_with_its_suggestion():
    e = entry("tall_cabinet", "Armoire with mirror doors", (1.0, 0.6, 2.0), source="abo")
    f = MT.type_finding(e)
    assert f and "a wardrobe" in f["reason"] and f["metrics"]["suggested_type"] == "wardrobe"


def test_the_title_and_the_vision_check_on_one_other_type_refuse():
    e = entry("washbasin", "INODORO EXCUSADO TOILET LAVABO", (0.84, 0.49, 1.04),
              audit={"status": "fix", "vision_doubt": ["the vision check says it is not a washbasin (a toilet)"]})
    f = MT.type_finding(e)
    assert f and "sees a toilet" in f["reason"]
    # the vision doubt alone keeps the model (decision 1a)
    alone = dict(e, title="Lavabo Roca", name="Lavabo Roca")
    assert MT.type_finding(alone) is None


def test_a_title_review_waives_the_rules_and_generated_titles_are_ours():
    e = sink()
    e["audit"]["title_review"] = {"ok": True, "type": "washbasin", "by": "user", "reason": "a bathroom basin"}
    assert MT.findings(e) == [] and C.usable(e, "relaxed")
    gen = entry("washbasin", "Generated japandi washbasin (1)", (0.6, 0.5, 0.6), source="generated")
    assert MT.findings(gen) == []


# --------------------------------------------------------------------------
# The audit, the catalogue and the fit
# --------------------------------------------------------------------------

def test_the_audit_removes_what_the_names_refuse():
    item = dict(facit(), kind="furniture")
    recs = CH.model_title_check(item)
    assert {r["check"] for r in recs} == {"stated_size", "title_set"} and {r["status"] for r in recs} == {"remove"}
    decision = DE.decide(item, recs + [CH.rec("title", "ok", "", metrics={"verdict": "match"})],
                         answer={"is_type": True, "single_object": True, "upright": True, "quality": 4})
    assert decision["status"] == "removed"
    assert CH.model_title_check(dict(entry("table_coffee", "Ikea LACK", (0.9, 0.55, 0.45)), kind="furniture")) == \
        [CH.rec("model_title", "ok", "the names say nothing against the model")]


def test_the_catalogue_carries_the_two_models_removed_with_the_rule(library):
    raw = json.loads((ROOT / "wenart/furniture/catalog_library.json").read_text(encoding="utf-8"))
    by = {e["id"]: e for s in ("entries", "decor") for e in raw[s]}
    for iid, rule, status in ((FACIT, "stated_size", "removed"), (FACIT, "title_set", "removed"),
                              (SINK, "title_type", "removed"), (INODORO, "title_type", "removed"),
                              (WARDROBE, "audit_doubt", "pending"), (WARDROBE, "front_side", "pending")):
        a = by[iid]["audit"]
        assert a["status"] == status and a["title_rules"]["version"] == MT.VERSION
        assert rule in [f["rule"] for f in a["title_rules"]["findings"]]
        assert a["title_rules"]["status_before"] in ("keep", "fix")
        assert not C.usable(library.entry(iid), "relaxed")
    assert W.TITLE_RULES_NOTE in raw["notes"]


def test_no_usable_catalogue_entry_is_refused_by_the_rules(library):
    """The catalogue pass is complete: every entry the fit may use passes the rules (the pass changed only the audit
    fields of the entries it removed)."""
    bad = [e["id"] for e in library.models + library.decor
           if (e.get("audit") or {}).get("status") in ("keep", "fix") and MT.refusal(e)]
    assert bad == []
    sinks = [e for e in library.candidates("washbasin") if C.usable(e, "relaxed")]
    assert sinks and all(MT.type_finding(e) is None for e in sinks)


def test_the_fit_no_longer_hangs_a_kitchen_sink_as_a_washbasin(library):
    p = dict(piece("washbasin", 1.0, 0.55, pid="f_L-1_026"), room_id="r_L-1_banyo")
    got = F.fit_piece(p, library, style_family="industrial", mode="relaxed")
    assert got["method"] == "library" and got["asset_id"] not in (SINK, INODORO)
    assert MT.type_finding(dict(library.entry(got["asset_id"]))) is None
    pinned = F.fit_piece(dict(p, asset_pin=SINK), library, style_family="industrial", mode="relaxed")
    assert pinned["asset_id"] != SINK and SINK in pinned["pin_refused"]


def test_the_fit_no_longer_builds_the_table_set_as_a_coffee_table(library):
    p = dict(piece("table_coffee", 0.7117, 0.405, pid="f_L-1_087"))
    got = F.fit_piece(p, library, style_family="industrial", mode="relaxed")
    assert got["asset_id"] != FACIT and not MT.findings(MT.asset_entry(dict(p, asset=got)) or {})


def test_a_fake_catalogue_candidate_refused_by_its_names_is_listed_as_excluded():
    good = model("wb1", "washbasin", 0.6, 0.45, 0.85, title="Ceramic washbasin")
    bad = model("wb2", "washbasin", 0.6, 0.45, 0.85, title="Kitchen sink, double bowl")
    got = F.fit_piece(piece("washbasin", 0.6, 0.45), FakeCatalog([bad, good]), mode="relaxed")
    assert got["asset_id"] == good["id"]
    reason = next(x["reason"] for x in got["excluded"] if x["id"] == bad["id"])
    assert "refuse it" in reason and "kitchen" in reason


# --------------------------------------------------------------------------
# The run's checks: fit report, code critic (LT), Argus (P11)
# --------------------------------------------------------------------------

def fitted_building():
    sink_asset = {"asset_id": SINK, "method": "library", "library": "3dwh", "title": "Sink", "name": "Sink",
                  "bbox_m": [1.0004, 0.5183, 0.4067], "fit_scale": [1.0367, 1.0367, 1.0367],
                  "source_url": "https://drive.google.com/file/d/x/view (zip member 3D Warehouse Furniture/Kitchen/"
                                "Sink [3dd30a43]/model.glb)", "audit": {"status": "keep"}}
    table_asset = {"asset_id": FACIT, "method": "library", "library": "3dwh", "title": FACIT_TITLE,
                   "bbox_m": [0.7117, 0.4114, 0.3203], "fit_scale": [0.9729, 0.9729, 0.9729],
                   "audit": {"status": "keep"}}
    lack = {"asset_id": "3dwh_lack", "method": "library", "library": "3dwh", "title": "Ikea LACK coffee table",
            "bbox_m": [0.9, 0.55, 0.45], "fit_scale": [1.0, 1.0, 1.0]}
    for a in (sink_asset, table_asset, lack):
        a.update(licence="3DWH-UNREVIEWED", licence_flag="non_commercial")
    return {"project_id": "t", "furniture": [
        dict(piece("washbasin", 1.0, 0.55, pid="f_L0_006"), room_id="r_L0_e_banyo", asset=sink_asset),
        dict(piece("table_coffee", 0.71, 0.405, pid="f_L-1_087"), room_id="r_L-1_salon", asset=table_asset),
        dict(piece("table_coffee", 0.9, 0.55, pid="f_L0_010"), asset=lack),
        dict(piece("washbasin", 0.6, 0.45, pid="f_L0_011"), asset={
            "asset_id": "parametric:washbasin", "method": "parametric", "library": "parametric", "licence": "n/a",
            "fit_scale": [1.0, 1.0, 1.0], "bbox_m": [0.6, 0.45, 0.85]})]}


def test_fitted_findings_name_the_wrong_models_of_a_run():
    found = {v["target"]: v for v in MT.fitted_findings(fitted_building())}
    assert set(found) == {"f_L0_006", "f_L-1_087"}
    assert found["f_L0_006"]["check"] == "LT" and found["f_L0_006"]["severity"] == "major"
    assert "kitchen" in found["f_L0_006"]["message"] and found["f_L0_006"]["room_id"] == "r_L0_e_banyo"
    assert set(found["f_L-1_087"]["metrics"]["rules"]) == {"stated_size", "title_set"}


def test_the_code_critic_and_the_fit_report_carry_lt():
    from wenart.agent import causes as CA
    from wenart.agent import critic_code as CC
    from wenart.agent.prompts import CHECKLIST
    got = CC.library_titles(fitted_building())
    assert [v["check"] for v in got] == ["LT", "LT"]
    assert CA.CHECK_CAUSE["LT"] == "wrong_model" and "LT" in CHECKLIST and CC.FAMILY_OF["LT"] == "library"
    from wenart.audit import kinds as AK
    assert AK.kind_of({"check": "LT"}) == "misread" == AK.kind_of({"check": "P11", "line": "process"})
    report = F.fit_report(fitted_building())
    assert "## Library models their names or audit refuse (LT" in report
    assert "f_L0_006" in report.split("## Library models their names or audit refuse")[1]


def test_argus_finds_them_in_the_process_line():
    from wenart.audit import process as PR
    from wenart.audit.inputs import Inputs
    b = fitted_building()
    built = copy.deepcopy(b)
    built["furniture"] = built["furniture"][:1]             # the building as built holds one of them again
    inp = Inputs(project="t", layout="collected", root=ROOT, stages=[("final", b), ("build", built)])
    found = PR.library_titles(inp)
    assert sorted(f["target"] for f in found) == ["f_L-1_087", "f_L0_006"]
    assert all(f["check"] == "P11" and f["kind"] == "misread" and f["fix"] == "swap_model" for f in found)


# --------------------------------------------------------------------------
# keywords: the speed change keeps every match
# --------------------------------------------------------------------------

def _old_matches(toks, folded, keyword):
    """The matcher before 28 Oct 2026 (no compiled keywords, no quick test)."""
    if K._CJK.search(keyword):
        out, start = [], folded.find(keyword)
        while start >= 0:
            out.append((-(start + 1) - 10_000, -(start + 1) - 10_000 + len(keyword), len(keyword) * 3))
            start = folded.find(keyword, start + 1)
        return out
    if keyword.startswith("~"):
        stem = K.fold(keyword[1:]).replace(" ", "")
        return [(i, i + 1, len(stem)) for i, t in enumerate(toks) if stem and stem in t]
    words = K.fold(keyword).split()
    n = len(words)
    if not n:
        return []
    return [(i, i + n, len(" ".join(words))) for i in range(len(toks) - n + 1)
            if all(K._token_eq(toks[i + k], words[k]) for k in range(n))]


@pytest.mark.parametrize("title", [FACIT_TITLE, "Dining Tables and Chairs", "Einbauspüle Spüle", "Sofás de esquina",
                                   "Coffee tables", "INODORO EXCUSADO TOILET LAVABO", "沙发 茶几", "Bedside lamps"])
def test_the_compiled_matcher_finds_what_the_old_one_found(title):
    toks, folded = K.tokens(title), K.fold(title)
    for words in list(K.KEYWORDS.values()) + list(K.FLAG_WORDS.values()):
        for w in words:
            assert K._matches(toks, folded, w) == _old_matches(toks, folded, w), (title, w)


# --------------------------------------------------------------------------
# The audit's own doubts: the "WARDROBE" with a window at its end (f_L0_023)
# --------------------------------------------------------------------------

def wardrobe(**audit):
    e = entry("wardrobe", "WARDROBE", (3.145, 0.6387, 2.5875),
              front_axis="+Y", front_axis_note=("geometry: detail_side: 2722 vs 108 vertices in the x slabs: front +X; "
                                                "M12 audit: front turned 90 deg to +Y"))
    e["audit"] = dict({"status": "fix", "fixes": {"front_axis": "+Y"},
                       "notes": ["its front is on the wrong side for a wardrobe (width along the front): turned 90 deg "
                                 "(side unknown: the vision check confirms)"],
                       "vision_doubt": ["the vision check says it is not a wardrobe"]}, **audit)
    return e


def test_a_vision_doubt_of_the_type_or_the_size_waits_for_a_second_pass():
    e = wardrobe()
    found = {f["rule"]: f for f in MT.findings(e)}
    assert found["audit_doubt"]["status"] == "review" and "not a wardrobe" in found["audit_doubt"]["reason"]
    assert not C.usable(e, "relaxed")
    size = entry("sofa", "Sofa", (2.0, 0.9, 0.8), source="abo", audit={
        "status": "keep", "notes": ["the vision check finds the size odd next to the scale reference (code: size ok)"]})
    assert [f["rule"] for f in MT.findings(size)] == ["audit_doubt"]
    # pass 2 confirmed it: decide writes a note of another wording, no doubt; the model is used
    ok = entry("sofa", "Sofa", (2.0, 0.9, 0.8), source="abo", audit={
        "status": "keep", "notes": ["pass 1 says it is not a sofa (a bench); pass 2 names a sofa: the type is "
                                    "confirmed"]})
    assert MT.findings(ok) == [] and C.usable(ok, "relaxed")
    # the extras stay with their own stages
    tree = entry("tree", "Oak tree", (5.0, 5.0, 9.0), kind="vegetation",
                 audit={"status": "keep", "vision_doubt": ["the vision check says it is not a tree"]})
    assert MT.findings(tree) == []


def test_a_front_turned_off_its_detail_side_gets_a_second_look():
    e = wardrobe(vision_doubt=[])
    f = MT.front_finding(e)
    assert f and f["status"] == "review" and f["metrics"] == {"geometric_front": "+X", "front_axis": "+Y"}
    assert "glazed panel or a window" in f["reason"]
    # the detail on the front, or a type whose front is not its long face: nothing
    assert MT.front_finding(dict(e, front_axis_note="geometry: detail_side: 900 vs 80 vertices in the y slabs: "
                                                    "front +Y")) is None
    assert MT.front_finding(dict(e, type="bed_double")) is None


def test_the_catalogue_pass_sets_the_doubtful_models_pending():
    doc = {"entries": [wardrobe(), facit(), entry("table_coffee", "Ikea LACK", (0.9, 0.55, 0.45),
                                                  audit={"status": "keep"})], "decor": []}
    stats = W.apply_title_rules(doc, "2026-10-28T12:00:00Z")
    assert stats["pending"] == [doc["entries"][0]["id"]] and stats["removed"] == [doc["entries"][1]["id"]]
    w = doc["entries"][0]["audit"]
    assert w["status"] == "pending" and w["title_rules"]["status_before"] == "fix"
    assert w["reasons"][0].startswith("28 Oct 2026, audit_doubt") and w["vision_doubt"]      # the evidence kept
    assert doc["entries"][2]["audit"] == {"status": "keep"}
    assert W.apply_title_rules(doc, "2026-10-28T13:00:00Z")["checked"] == 1                  # only the LACK again


def test_the_wardrobe_of_f_l0_023_is_no_longer_fitted(library):
    p = dict(piece("wardrobe", 3.1082, 0.6, pid="f_L0_023"), room_id="r_L0_e_yatak_odasi")
    got = F.fit_piece(p, library, style_family="industrial", mode="relaxed")
    assert got["asset_id"] != WARDROBE and got["method"] in ("library", "module")
    assert not MT.findings(MT.asset_entry(dict(p, asset=got)) or {})


def test_the_swap_tool_refuses_a_model_the_rules_refuse(library):
    from wenart.furniture import edit_ops as EO
    b = {"furniture": [dict(piece("washbasin", 1.0, 0.55, pid="f_L0_006"), room_id="r_L0_e_banyo")]}
    with pytest.raises(EO.EditRejected) as exc:
        EO._swap_model(b, {"piece_id": "f_L0_006", "asset_id": SINK}, library)
    assert exc.value.check == "asset_unusable" and "not used" in exc.value.message


def test_the_vision_checklist_names_a_window_on_furniture():
    from wenart.agent.prompts import CHECKLIST
    assert "a window or a glazed frame on a piece of furniture" in CHECKLIST["D2"]["what"]
    assert CHECKLIST["D2"]["how"] == "V"


def test_argus_lists_the_doubtful_wardrobe_of_a_run():
    from wenart.audit import process as PR
    from wenart.audit.inputs import Inputs
    asset = {"asset_id": WARDROBE, "method": "library", "library": "3dwh", "title": "WARDROBE", "name": "WARDROBE",
             "bbox_m": [3.1082, 0.6312, 2.5572], "fit_scale": [0.9883] * 3, "audit": wardrobe()["audit"]}
    b = {"furniture": [dict(piece("wardrobe", 3.1082, 0.6, pid="f_L0_023"), room_id="r_L0_e_yatak_odasi",
                            asset=asset)]}
    found = PR.library_titles(Inputs(project="t", layout="collected", root=ROOT, stages=[("final", b)]))
    assert [f["target"] for f in found] == ["f_L0_023"] and "not a wardrobe" in found[0]["message"]


def test_the_geometric_front_reading_is_the_audits(library):
    """model_title keeps its own copy of the audit's geometric front reading (its import closure stays small): the two
    read every catalogue note alike."""
    from wenart.assets.audit.checks import geometric_front
    notes = {str(e.get("front_axis_note") or "") for e in library.models + library.decor}
    assert len(notes) > 100
    for n in notes:
        assert MT.geometric_front(n) == geometric_front({"front_axis_note": n}), n


# --------------------------------------------------------------------------
# The bath of real06 ("What kind of a bath is this" / "this bath needs to make sense")
# --------------------------------------------------------------------------

BATH = "3dwh_1fab322fe57d8d05759235ad"


def flat_bath(**extra):
    e = entry("bathtub", "Bathtub", (1.524, 0.7366, 0.3683), real_product=False, audit={
        "status": "keep", "vision_doubt": ["vision quality 2 (<= 2)"],
        "notes": ["85% non-manifold edges",
                  "the vision check finds the size odd next to the scale reference (code: size ok)"]})
    e.update(extra)
    return e


def test_a_low_quality_or_unreal_furniture_model_is_not_used():
    f = MT.quality_finding(flat_bath())
    assert f["status"] == "refuse" and "vision quality 2" in f["reason"] and "no real product" in f["reason"]
    assert {x["rule"] for x in MT.findings(flat_bath())} == {"audit_quality", "audit_doubt"}
    assert not C.usable(flat_bath(), "relaxed")
    # a generated model's real_product comes from its source; decor keeps the doubt
    gen = entry("bathtub", "Generated minimal bathtub (1)", (1.7, 0.75, 0.56), source="generated",
                real_product=False, audit={"status": "keep"})
    assert MT.quality_finding(gen) is None
    vase = entry("vase", "Vase", (0.2, 0.2, 0.3), kind="decor", decor_type="vase",
                 audit={"status": "keep", "vision_doubt": ["vision quality 2 (<= 2)"]})
    assert MT.quality_finding(vase) is None


def test_a_bath_stands_at_its_real_height():
    assert not F.fixture_height_ok("bathtub", 0.3746) and F.fixture_height_ok("bathtub", 0.555)
    assert F.fixture_height_ok("bathtub", 0.79) and not F.fixture_height_ok("bathtub", 0.9)   # a raised-end bath
    assert F.fixture_height_ok("washbasin", 0.4)
    low = model("bath_low", "bathtub", 1.55, 0.75, 0.37, title="Bath")
    good = model("bath_ok", "bathtub", 1.55, 0.75, 0.56, title="Bath")
    got = F.fit_piece(piece("bathtub", 1.55, 0.75), FakeCatalog([low, good]), mode="relaxed")
    assert got["asset_id"] == good["id"]
    tried = {c["id"]: c for c in got["candidates"]}
    assert tried[low["id"]]["height_ok"] is False
    alone = F.fit_piece(piece("bathtub", 1.55, 0.75), FakeCatalog([low]), mode="relaxed")
    assert alone["method"] != "library" and alone.get("by_design")


def test_the_catalogue_drops_the_flat_bath_and_the_fit_takes_a_real_one(library):
    raw = json.loads((ROOT / "wenart/furniture/catalog_library.json").read_text(encoding="utf-8"))
    a = next(e for e in raw["entries"] if e["id"] == BATH)["audit"]
    assert a["status"] == "removed" and {"audit_quality", "audit_doubt"} <= {f["rule"] for f in
                                                                           a["title_rules"]["findings"]}
    p = dict(piece("bathtub", 1.55, 0.75, pid="f_L0_010"), room_id="r_L0_banyo")
    got = F.fit_piece(p, library, style_family="scandinavian", mode="relaxed")
    assert got["asset_id"] != BATH
    if got["method"] == "library":
        assert F.FIXTURE_HEIGHTS["bathtub"][0] <= got["bbox_m"][2] <= F.FIXTURE_HEIGHTS["bathtub"][1]


def test_a_bath_built_from_code_has_a_rim_a_mixer_and_panels_where_no_wall_is():
    from wenart.blender import parametric as P
    from wenart.furniture import fixture_seat as FS
    room = [[0.0, 0.0], [1.6, 0.0], [1.6, 2.2], [0.0, 2.2]]
    bath = dict(piece("bathtub", 1.6, 0.75, pid="f_bath"), room_id="r_b",
                footprint={"center": [0.8, 1.825], "size": [1.6, 0.75], "rotation_deg": 0.0}, front_deg=270.0)
    b = {"rooms": [{"id": "r_b", "polygon": room}], "furniture": [bath]}
    assert FS.bath_walls(b, bath) == [1, 2, 3]                          # a niche: back and both ends on walls
    fitted = F.fit_building(b, FakeCatalog([]), mode="relaxed")
    assert fitted["furniture"][0]["asset"]["bath_walls"] == [1, 2, 3]
    niche = P.build_parts("bathtub", 1.6, 0.75, 0.58, piece=fitted["furniture"][0])
    roles = [p["role"] for p in niche]
    assert roles.count("panel") == 1 and "rim" in roles and roles.count("tap") >= 3 and "drain" in roles
    corner = P.build_parts("bathtub", 1.6, 0.75, 0.58, piece={"asset": {"bath_walls": [1, 2]}})
    assert [p["role"] for p in corner].count("panel") == 2               # the front and the open end
    free = P.build_parts("bathtub", 1.6, 0.75, 0.58, piece=None)
    assert "panel" not in {p["role"] for p in free} and {"basin", "tap"} <= {p["role"] for p in free}
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(niche)
    assert x1 - x0 == pytest.approx(1.6, abs=0.01) and y1 - y0 == pytest.approx(0.75, abs=0.01) and z0 == 0.0
