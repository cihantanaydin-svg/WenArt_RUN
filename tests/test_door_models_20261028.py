"""Better doors and windows, inside and outside, with variation in one language per house (28 Oct 2026, user: "I want
better doors inside the house and the outside, I am not liking that much the models used at the moment, some
variation is needed", then "find the best models"; lesson UL65). CPU, pure.

- the HSSD doors and windows as a library source (``wenart.assets.hssd_openings``), their growth list and approval,
  their catalogue entries, the opening question of the audit and its fields in the catalogue;
- the choice (``wenart.blender.opening_models``): the audit's structured fields before the title, a statement
  entrance, service doors of their own family, the house's seed among equal families, each opening a member that
  opens its way;
- the inside doors (``inside_records``, ``inside_role``, ``plan_inside``, ``opening_build`` centred / mirrored /
  handles) and Argus' door checks (``door_variety_problems``)."""
import json
import math
from argparse import Namespace
from pathlib import Path

import pytest

from wenart.assets import hssd as H
from wenart.assets import hssd_openings as HO
from wenart.assets import warehouse as WH
from wenart.assets.audit import ask as A
from wenart.assets.audit import checks as CK
from wenart.assets.audit import growth as G
from wenart.assets.audit import growth_entries as GE
from wenart.assets.audit import growth_run as GR
from wenart.blender import opening_build as OB
from wenart.blender import opening_models as OM

ROOT = Path(__file__).resolve().parents[1]
GROWTH = ROOT / "results" / "library" / "growth"


def _row(hid, synset, w, h, d=0.08, name=""):
    return {"id": hid, "name": name, "wnsynsetkey": synset, "aligned.dims": f"{w},{h},{d}",
            "main_category": "window" if synset == "window.n.01" else ("door" if "door" in synset else "")}


# --------------------------------------------------------------------------
# the source: HSSD doors and windows
# --------------------------------------------------------------------------

def test_hssd_openings_are_typed_by_their_synset_and_size():
    t = HO.typed_opening(_row("200-19", "door.n.01", 0.82, 2.2, 0.23))
    assert t["type"] == "door" and t["kind"] == "single" and t["operation"] == "hinged"
    assert t["series"] == "200" and t["variant"] == 19 and t["title"] == "HSSD door 200-19 (0.82 x 2.20 m)"
    assert set(t["categories"]) == {"entrance", "door", "terrace_door", "inside_door"} and "left_out" not in t
    s = HO.typed_opening(_row("211-11", "sliding_door.n.01", 1.79, 2.1, 0.15))
    assert s["kind"] == "sliding" and s["operation"] == "sliding" and s["categories"] == ["glazed_door"]
    assert "sliding door" in s["title"]                     # the opening choice reads the kind's words
    w = HO.typed_opening(_row("218-10", "window.n.01", 1.15, 0.95))
    assert w["type"] == "window" and w["operation"] is None and w["categories"] == ["window"]
    wide = HO.typed_opening(_row("cbadc2e21f27", "door.n.01", 1.75, 2.61, 0.05, "Door Restoration Hardware"))
    assert wide["kind"] == "double" and "more than one leaf" in wide["kind_note"] and wide["title"] == \
        "Door Restoration Hardware"
    assert "garage" in HO.typed_opening(_row("212-0", "garage_door.n.01", 2.6, 2.2))["left_out"]
    assert "mirror" in HO.typed_opening(_row("99bd", "window.n.01", 0.88, 1.49, name="Mirror"))["left_out"].lower()
    assert "fits no window" in HO.typed_opening(_row("218-95", "window.n.01", 5.4, 1.15))["left_out"]
    assert HO.typed_opening(_row("c1", "window_curtain.n.01", 1.2, 2.4)) is None       # a curtain: no opening
    assert HO.series_of("3752-28") == ("3752", 28) and HO.series_of("a" * 40) == ("a" * 12, None)


def test_the_pick_spreads_each_series_over_its_proportions_and_keeps_the_named_products():
    rows = [_row(f"218-{i}", "window.n.01", 0.5 + 0.1 * i, 1.4) for i in range(25)]
    rows += [_row("ef9b08bbb966", "door.n.01", 0.82, 2.3, 0.1, "YOO OH single panel door, EARTH"),
             _row("hab_only", "door.n.01", 0.9, 2.2), _row("212-0", "garage_door.n.01", 2.6, 2.2)]
    listing = {r["id"]: {"path": f"objects/openings/{r['id']}.glb", "size": 40000} for r in rows
               if r["id"] != "hab_only"}
    cands, left = HO.pick(rows, listing)
    series = [c for c in cands if c["opening"]["series"] == "hssd:218"]
    assert 1 < len(series) <= HO.MAX_PER_SERIES["window"]
    steps = [round(math.log(c["aspect"]) / HO.PROPORTION_STEP) for c in series]
    assert len(set(steps)) == len(steps)                                    # one variant per proportion step
    named = next(c for c in cands if c["hssd_id"] == "ef9b08bbb966")
    assert named["title"] == "YOO OH single panel door, EARTH" and named["id"] == "hssd_ef9b08bbb966"
    assert named["licence_flag"] == H.LICENCE_FLAG and named["kind"] == "opening" and named["pick"]
    assert not any(c["hssd_id"] == "hab_only" for c in cands)               # not in hssd-models: nothing to fetch
    reasons = {r["id"]: r["reason"] for r in left}
    assert "garage" in reasons["212-0"] and any(r.startswith("series 218") for r in reasons.values())
    doc = HO.list_doc(cands, left, "2026-10-28T13:00:00Z")
    assert doc["count"] == len(cands) and doc["by_type"]["window"] == len(series) and doc["list"] == "hssd_openings"


def test_the_committed_openings_list_and_its_approval_pass_the_ingest_gate():
    doc = json.loads((GROWTH / "candidates_hssd_openings.json").read_text(encoding="utf-8"))
    assert doc["source"] == "hssd" and doc["list"] == "hssd_openings" and doc["query"]["revision"] == H.REVISION
    cands = doc["candidates"]
    assert 150 <= len(cands) <= 300 and len({c["id"] for c in cands}) == len(cands)
    for c in cands:
        assert c["id"] == "hssd_" + c["hssd_id"] and c["type"] in ("door", "window") and c["opening"]["categories"]
        assert c["path"].startswith("objects/") and c["path"].endswith(f"{c['hssd_id']}.glb")
        assert c["licence"] == "CC-BY-NC-4.0" and c["size_mb"] and c["size_mb"] < 3.0
    cats = doc["by_category"]
    for cat in ("entrance", "door", "terrace_door", "glazed_door", "inside_door", "window"):
        assert cats.get(cat, 0) >= 10, cats                    # a spread across the categories
    approval = G.approved("hssd_openings", ROOT / "results" / "library")
    assert approval["ids"] == [c["id"] for c in cands] and approval["licence_mode"] == "relaxed only"
    assert "find the best models" in approval["approved_by"]


def test_an_hssd_opening_entry_is_an_extra_with_its_series_and_synset():
    cand = HO.candidate(HO.typed_opening(_row("200-19", "door.n.01", 0.82, 2.2, 0.23)),
                        {"200-19": {"path": "objects/openings/200-19.glb", "size": 41804}}, 5)
    m = {"bbox_model_m": [0.82, 0.23, 2.2], "bbox_min_m": [-0.41, -0.115, 0.0], "bbox_max_m": [0.41, 0.115, 2.2],
         "triangles": 900, "vertices": 600, "info": {"textured": False, "vertex_colours": False}, "stats": None,
         "pbr": {"base_colour": False}}
    e = GE.hssd_opening_entry(cand, m, "0" * 64, "2026-10-28T13:00:00Z")
    WH.validate_extra(e)
    assert e["kind"] == "opening" and e["type"] == "door" and GE.section_of(e) == "extras"
    assert e["series"] == "hssd:200" and e["hssd"]["synset"] == "door.n.01" and e["opening"]["kind"] == "single"
    assert e["licence_flag"] == "non_commercial" and e["commercial_safe"] is False
    assert "CC BY-NC 4.0" in e["attribution"]
    assert e["glb"] == "models/hssd/hssd_200-19.glb" and e["audit"]["status"] == "pending"
    assert OM.family_key(e) == "door:series:hssd:200"
    # the HSSD table's synset is the type evidence of the audit's title check (no second vision pass)
    rec = CK.extra_title_check({"kind": "opening", "type": "door", "title": e["title"], "hssd": e["hssd"]})
    assert rec[0]["status"] == "ok" and rec[0]["metrics"]["verdict"] == "match"
    assert CK.extra_title_check({"kind": "opening", "type": "window", "title": "x", "hssd": e["hssd"]})[0][
        "status"] == "review"


def test_the_growth_steps_know_the_openings_source():
    assert GR.list_names("hssd_openings") == ("candidates_hssd_openings.json", "hssd_openings")
    assert "hssd_openings" in GR.ONLY_SOURCES
    args = GR.parser().parse_args(["ingest", "--source", "hssd_openings", "--token-env", "HF_TOKEN"])
    assert args.source == "hssd_openings"
    assert GR.ingest_name(Namespace(source="hssd_openings", m13=False)) == "ingest_hssd_openings.json"


def test_the_catalogue_step_builds_the_opening_entries_alone(tmp_path):
    import struct
    lists, g, assets = tmp_path / "lists", tmp_path / "g", tmp_path / "assets"
    (lists / "growth").mkdir(parents=True)
    (g / "report").mkdir(parents=True)
    cand = HO.candidate(HO.typed_opening(_row("218-10", "window.n.01", 1.15, 0.95)),
                        {"218-10": {"path": "objects/openings/218-10.glb", "size": 37000}}, 10)
    (lists / "growth" / "candidates_hssd_openings.json").write_text(json.dumps({"candidates": [cand]}))
    # a 1.15 x 0.08 x 0.95 m box (glTF Y-up: x width, y up, z depth)
    pos = [(x, y, z) for x in (-0.575, 0.575) for y in (0.0, 0.95) for z in (-0.04, 0.04)]
    tris = [0, 1, 3, 0, 3, 2, 4, 6, 7, 4, 7, 5, 0, 4, 5, 0, 5, 1, 2, 3, 7, 2, 7, 6, 0, 2, 6, 0, 6, 4, 1, 5, 7, 1, 7, 3]
    pb = b"".join(struct.pack("<3f", *p) for p in pos)
    ib = b"".join(struct.pack("<H", i) for i in tris)
    doc = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0}],
           "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "material": 0}]}],
           "materials": [{"name": "glass", "pbrMetallicRoughness": {}}], "buffers": [{"byteLength": len(pb + ib)}],
           "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(pb)},
                           {"buffer": 0, "byteOffset": len(pb), "byteLength": len(ib)}],
           "accessors": [{"bufferView": 0, "componentType": 5126, "count": 8, "type": "VEC3",
                          "min": [-0.575, 0.0, -0.04], "max": [0.575, 0.95, 0.04]},
                         {"bufferView": 1, "componentType": 5123, "count": len(tris), "type": "SCALAR"}]}
    js = json.dumps(doc).encode()
    js += b" " * (-len(js) % 4)
    blob = pb + ib
    blob += b"\0" * (-len(blob) % 4)
    data = struct.pack("<III", 0x46546C67, 2, 28 + len(js) + len(blob)) + struct.pack("<II", len(js), 0x4E4F534A) \
        + js + struct.pack("<II", len(blob), 0x004E4942) + blob
    glb = assets / "models" / "hssd" / "hssd_218-10.glb"
    glb.parent.mkdir(parents=True)
    glb.write_bytes(data)
    (g / "report" / "ingest_hssd_openings.json").write_text(json.dumps({"records": [
        {"id": "hssd_218-10", "hssd_id": "218-10", "ok": True, "glb": "models/hssd/hssd_218-10.glb",
         "sha256": GR.sha256_file(glb)},
        {"id": "hssd_218-11", "hssd_id": "218-11", "ok": False, "error": "not downloaded"}]}))
    a = Namespace(growth=str(g), report=None, p4=str(tmp_path / "p4"), p3=str(tmp_path / "p3"), assets=str(assets),
                  lists=str(lists), only="hssd_openings", checked_utc="2026-10-28T13:00:00Z", m13=False)
    assert GR.cmd_catalogue(a) == 0
    lib = json.loads((tmp_path / "p4" / "audit" / "catalogue" / "catalog_library.json").read_text())
    e = next(x for x in lib["extras"] if x["id"] == "hssd_218-10")
    assert e["kind"] == "opening" and e["type"] == "window" and e["series"] == "hssd:218"
    assert [round(v, 3) for v in e["bbox_m"]] == [1.15, 0.08, 0.95]
    nid = json.loads((tmp_path / "p4" / "audit" / "new_ids.json").read_text())
    assert nid["ids"] == ["hssd_218-10"] and nid["only"] == ["hssd_openings"]
    rep = json.loads((g / "report" / "catalogue.json").read_text())
    assert rep["by_list"] == {"hssd_openings": 1}
    assert any(d["id"] == "hssd_218-11" and d["source"] == "hssd_openings" for d in rep["dropped"])
    # the growth report has a row for the openings layer
    ing = json.loads((g / "report" / "ingest_hssd_openings.json").read_text())
    (g / "report" / "ingest_hssd_openings.json").write_text(json.dumps(dict(ing, approved=2, ok=1)))
    assert GR.cmd_report(Namespace(**{**vars(a), "steps": None})) == 0
    row = next(r for r in json.loads((g / "report" / "growth.json").read_text())["sources"]
               if r["source"] == "hssd_openings")
    assert row["approved"] == 2 and row["downloaded_or_generated"] == 1 and row["catalogued"] == 1
    assert row["dropped"] == 1


def test_the_same_pod_gives_the_doubted_models_their_second_look(tmp_path):
    """Coordinator, 28 Oct 2026: the pending models whose own audit doubted their type or size (model_title
    ``audit_doubt``) are audited with the new doors and windows: the growth ones join the audit ids, the P3 ones go
    to the pending step, the ones pending for another reason (a front off its detail side) stay."""
    def pend(iid, rules, growth=True):
        e = {"id": iid, "type": "fridge", "audit": {"status": "pending", "title_rules": {
            "findings": [{"rule": r, "status": "review"} for r in rules]}}}
        if growth:
            e["growth"] = {"pod": "P2"}
        return e
    lib = {"entries": [pend("hssd_a", ["audit_doubt"]), pend("abo_old", ["audit_doubt"], growth=False),
                       pend("3dwh_f", ["front_side"]), pend("3dwh_b", ["audit_doubt", "front_side"]),
                       {"id": "ok_1", "audit": {"status": "keep"}}],
           "decor": [pend("3dwh_d", ["audit_doubt"])], "extras": [{"id": "hssd_200-19", "audit": {"status": "pending"}}]}
    sel = GR.second_look_ids(lib, {"entries": []})
    assert sel == {"p4": ["3dwh_d", "hssd_a"], "p3": ["abo_old"], "other": ["3dwh_b", "3dwh_f", "hssd_200-19"]}
    # the step: the audit ids are the new ones plus the doubted growth models; --summary records their status after
    p4 = tmp_path / "p4" / "audit"
    (p4 / "catalogue").mkdir(parents=True)
    (p4 / "catalogue" / "catalog_library.json").write_text(json.dumps(lib))
    (p4 / "catalogue" / "catalog.json").write_text(json.dumps({"entries": []}))
    (p4 / "new_ids.json").write_text(json.dumps({"ids": ["hssd_200-19"]}))
    a = Namespace(growth=str(tmp_path / "g"), report=None, p4=str(tmp_path / "p4"), summary=False)
    assert GR.cmd_second_look(a) == 0
    ids = json.loads((p4 / GR.AUDIT_IDS).read_text())
    assert ids["ids"] == ["hssd_200-19", "3dwh_d", "hssd_a"] and ids["p3"] == ["abo_old"]
    lib["entries"][0]["audit"] = {"status": "keep"}
    (p4 / "catalogue" / "catalog_library.json").write_text(json.dumps(lib))
    assert GR.cmd_second_look(Namespace(**{**vars(a), "summary": True})) == 0
    rep = json.loads((tmp_path / "g" / "report" / "second_look.json").read_text())
    assert rep["growth"] == 2 and rep["after"]["None:keep"] == 1 and rep["after"]["None:pending"] == 2
    assert "second-look" in GR.STEPS and GR.parser().parse_args(["second-look", "--summary"]).summary


def test_the_doubted_models_get_the_type_question_and_their_decision_follows_it():
    from wenart.assets.audit import cli as CLI
    from wenart.assets.audit import decide as D
    item = {"id": "3dwh_w", "type": "wardrobe", "kind": "furniture", "title": "WARDROBE", "source": "3dwh"}
    first = {"3dwh_w": {"is_type": False, "type_guess": "other", "size_plausible": False}}
    assert CLI.second_pass_ids([item], first) == {"3dwh_w"}
    reasons, notes, doubts, pending = [], [], [], []
    D.second_look("the vision check says it is not a wardrobe", item, {"type_guess": "wardrobe"}, reasons, notes,
                  doubts, pending)
    assert not reasons and not pending and "confirmed" in notes[0]
    reasons, notes, doubts, pending = [], [], [], []
    D.second_look("the vision check says it is not a wardrobe", item, None, reasons, notes, doubts, pending)
    assert pending and doubts


# --------------------------------------------------------------------------
# the opening question of the audit and its fields in the catalogue
# --------------------------------------------------------------------------

def test_hssd_doors_and_windows_get_the_opening_question():
    cfg = {"version": "m12.1", "version_materials": "m13.1", "version_logo": "m13.2", "version_openings": "m13.3"}
    item = {"id": "hssd_200-19", "type": "door", "kind": "opening", "source": "hssd", "title": "HSSD door 200-19"}
    assert A.version_for(item, cfg) == "m13.3"
    assert A.version_for(dict(item, source="3dwh"), cfg) == "m13.2"           # the 3D Warehouse answers stay valid
    assert A.version_for(dict(item, kind="furniture", type="sofa"), cfg) == "m13.1"
    sch = A.schema("opening", "m13.3")
    assert set(A.OPENING_FIELDS) <= set(sch["required"]) and "brand_logo" in sch["required"]
    assert not set(A.OPENING_FIELDS) & set(A.schema("furniture", "m13.3")["required"])
    text = A.prompt(item, [0.82, 0.23, 2.2], "m13.3")
    assert "- glazing:" in text and "- role:" in text and "- handle_side:" in text
    assert "- glazing:" not in A.prompt(item, [0.82, 0.23, 2.2], "m13.2")
    answer = {"is_type": True, "type_guess": "door", "single_object": True, "real_product": True, "indoor": "both",
              "upright": True, "size_plausible": True, "parts_open": False, "styles": ["modern"], "quality": 4,
              "front_shown": "front", "has_bedding": None, "has_pillows": None, "has_cushions": None, "contact": None,
              "materials": ["wood"], "brand_logo": False, "text_print": False, "role": "inside",
              "operation": "hinged", "leaves": 1, "glazing": "none", "leaf": "flush", "handle_side": "right"}
    assert A.answer_version(answer) == "m13.3" and A.valid(answer, "opening")
    assert not A.valid(dict(answer, glazing="tinted"), "opening")
    assert A.server_schema({"context": {"kind": "opening", "version": "m13.3"}}) == sch


def test_the_vision_fields_step_writes_the_quality_and_the_opening_answer():
    doc = {"extras": [{"id": "hssd_200-19", "kind": "opening", "type": "door", "styles": ["neutral"]},
                      {"id": "3dwh_x", "kind": "vegetation", "type": "tree", "styles": ["neutral"]}]}
    answers = {"hssd_200-19": {"styles": ["scandinavian"], "quality": 4, "role": "inside", "glazing": "none",
                               "leaf": "flush", "operation": "hinged", "leaves": 1, "handle_side": "left"},
               "3dwh_x": {"styles": [], "quality": 3}}
    got = GE.apply_vision_fields(doc, answers, {"hssd_200-19", "3dwh_x"})
    door, tree = doc["extras"]
    assert got["openings"] == 1 and door["audit_quality"] == 4 and door["opening_vision"]["role"] == "inside"
    assert door["opening_vision"]["handle_side"] == "left" and "audit_quality" not in tree
    assert OM.model_role(door) == "inside" and OM.model_glazing(door) == "none" and OM.model_handle_side(door) == "left"


def test_the_pods_new_doors_are_adopted_without_overwriting_the_repo_catalogue():
    repo = {"entries": [{"id": "sofa_1", "v": "repo"}], "extras": [{"id": "3dwh_a", "v": "repo"}], "sources": ["abo"]}
    copy = {"entries": [{"id": "sofa_1", "v": "pod"}],
            "extras": [{"id": "3dwh_a", "v": "pod"}, {"id": "hssd_200-19", "kind": "opening", "v": "pod"}],
            "sources": ["abo", "hssd"], "datasets": {"hssd": {"name": "HSSD"}}, "notes": ["n1"]}
    got = GE.adopt_entries(repo, copy, ["hssd_200-19", "hssd_9-9"])
    assert got["added"] == 1 and got["missing"] == ["hssd_9-9"]
    assert repo["entries"][0]["v"] == "repo" and repo["extras"][0]["v"] == "repo"      # the rest stays the repo's
    assert repo["extras"][1]["id"] == "hssd_200-19" and repo["sources"] == ["abo", "hssd"]
    assert repo["datasets"]["hssd"]["name"] == "HSSD" and repo["notes"] == ["n1"]


def test_load_extras_reads_the_openings_audit(tmp_path):
    cat = tmp_path / "catalog_library.json"
    cat.write_text(json.dumps({"extras": [{"id": "hssd_1-1", "type": "door", "kind": "opening", "styles": ["neutral"],
                                           "bbox_m": [0.9, 0.2, 2.2]}]}))
    audit = tmp_path / "audit.json"
    audit.write_text(json.dumps({"items": [{"id": "hssd_1-1", "vision": {"quality": 4, "styles": ["modern"],
                                                                         "role": "entrance", "glazing": "clear"}}]}))
    e = OM.load_extras(cat, audits=[audit])[0]
    assert e["audit_quality"] == 4 and e["opening_vision"]["role"] == "entrance" and e["styles"] == ["modern"]
    assert "results/library/audit/openings/audit.json" in OM.AUDIT_FILES


# --------------------------------------------------------------------------
# the choice: structured fields, a statement entrance, service doors of their own family, variation
# --------------------------------------------------------------------------

def _model(i, title, w=0.95, h=2.1, kind="door", styles=("modern",), q=3, **extra):
    e = {"id": f"m{i}", "type": kind, "kind": "opening", "title": title, "glb": f"m{i}.glb", "bbox_m": [w, 0.1, h],
         "styles": list(styles), "audit": {"status": "keep"}, "licence_flag": "non_commercial", "textured": True,
         "audit_quality": q}
    e.update(extra)
    return e


def _outer(oid, width, top=2.1, kind="door", **o):
    return {"opening": dict({"id": oid, "type": kind, "width": width}, **o), "bottom": 0.0, "top": top,
            "outward": [0, -1]}


def test_the_audit_fields_come_before_the_title_words():
    inside = _model(1, "HSSD door 200-19", opening_vision={"role": "inside", "glazing": "none"})
    assert OM.structured_problem(inside, "entrance") and OM.structured_problem(inside, "door")
    assert OM.structured_problem(inside, "inside_door") is None
    front = _model(2, "HSSD door 201-2", opening_vision={"role": "entrance"})
    assert OM.structured_problem(front, "inside_door") and OM.is_statement(front)
    pair = _model(3, "HSSD double door 208-11", w=1.66, opening={"kind": "double", "operation": "hinged"})
    assert OM.model_leaves(pair) == 2 and OM.structured_problem(pair, "terrace_door")
    solid = _model(4, "Glass door", opening_vision={"glazing": "none"})
    assert "no glass" in OM.structured_problem(solid, "glazed_door")
    slide = _model(5, "HSSD sliding door 211-11", w=1.8, opening={"kind": "sliding", "operation": "sliding"})
    assert OM.model_operation(slide) == "sliding"
    assert OM.model_operation(dict(slide, opening_vision={"operation": "folding"})) == "folding"   # the audit first
    assert OM.model_operation({"title": "Lift Slide Patio Door"}) == "sliding"                    # else the title
    ids = [e["id"] for e in OM.candidates([inside, front, pair, solid], "entrance", "relaxed")]
    assert ids == ["m2"]                                    # no inside door, no pair on the entrance
    assert [e["id"] for e in OM.candidates([inside, front], "inside_door", "relaxed")] == ["m1"]
    clear = _model(6, "HSSD door 204-3", opening_vision={"glazing": "clear"})
    assert [e["id"] for e in OM.candidates([clear, solid], "terrace_door", "relaxed")] == ["m6"]
    # the light look: the audit's panelled leaf and glazing bars are out
    look = OM.look_of("scandinavian")
    assert OM.look_fit(_model(7, "HSSD door 1-1", opening_vision={"leaf": "panelled"}), look)[0] is None
    assert OM.look_fit(_model(8, "HSSD window 1-1", kind="window", opening_vision={"glazing": "bars"}), look,
                       None, "window")[0] is None


def test_the_entrance_takes_a_statement_door_and_the_service_doors_another_family():
    extras = [_model(1, "Modern Front Door", q=4), _model(2, "Plain Door", q=4), _model(3, "Other Door", q=3)]
    b = {"site": {"entrances": [{"door_id": "e", "main": True}]}}
    outer = [_outer("e", 0.95), _outer("d1", 0.9), _outer("d2", 0.9)]
    notes: list = []
    plan = OM.plan(b, outer, extras, style={"family": "modern"}, notes=notes)
    assert plan["e"]["asset"]["asset_id"] == "m1" and plan["e"]["statement"] is True
    assert plan["d1"]["asset"]["asset_id"] == "m2" and plan["d1"]["family"] != plan["e"]["family"]
    assert "another family than the entrance's" in plan["d1"]["reason"]
    assert OM.door_variety_problems(plan) == []
    # only an off-look model left for the service doors: they share the entrance's family (one language first)
    extras = [_model(1, "Modern Front Door", q=4), _model(2, "Victorian Door", q=4, styles=("classic",))]
    notes = []
    plan = OM.plan(b, outer, extras, style={"family": "modern"}, notes=notes)
    assert plan["d1"]["family"] == plan["e"]["family"]
    assert any(n["kind"] == "shared_family" for n in notes)


def test_two_houses_of_one_style_get_different_products_among_equal_families():
    extras = [_model(i, f"Window Type {chr(65 + i)}", w=1.2, h=1.3, kind="window", q=4) for i in range(4)]
    outer = [_outer(f"w{i}", 1.2, top=2.2, kind="window") for i in range(3)]
    for rec in outer:
        rec["bottom"] = 0.9
    picks = {}
    for project in ("house_a", "house_b", "house_c", "house_d", "house_e"):
        plan = OM.plan({"project": {"id": project}}, outer, extras, style={"family": "modern"})
        assert len({v["asset"]["asset_id"] for v in plan.values()}) == 1      # one window family per house
        picks[project] = plan["w0"]["asset"]["asset_id"]
        again = OM.plan({"project": {"id": project}}, outer, extras, style={"family": "modern"})
        assert again["w0"]["asset"]["asset_id"] == picks[project]            # stable for one house
    assert len(set(picks.values())) >= 2
    assert OM.plan({}, outer, extras)["w0"]["asset"]["asset_id"] == "m0"     # no seed: the ranked order
    # a better model is never traded for variety
    best = dict(extras[3], audit_quality=5)
    for project in ("house_a", "house_b", "house_c"):
        plan = OM.plan({"project": {"id": project}}, outer, extras[:3] + [best], style={"family": "modern"})
        assert plan["w0"]["asset"]["asset_id"] == "m3"


def test_each_glazed_door_takes_a_member_that_opens_its_way():
    """A French and a sliding glazed door in one house: a series whose audit or table states the operation of each
    member serves both (the old rule kept only the models naming no operation: no HSSD model)."""
    hinged = _model(1, "HSSD double door 208-11", w=1.66, h=2.2, series="hssd:208",
                    opening={"kind": "double", "operation": "hinged"}, opening_vision={"glazing": "clear"})
    sliding = _model(2, "HSSD sliding door 208-12", w=2.4, h=2.2, series="hssd:208",
                     opening={"kind": "sliding", "operation": "sliding"}, opening_vision={"glazing": "clear"})
    outer = [_outer("f", 1.6, top=2.2, door_type="french"), _outer("s", 2.4, top=2.2, door_type="glazed_sliding")]
    plan = OM.plan({}, outer, [hinged, sliding], style={"family": "modern"})
    assert plan["f"]["asset"]["asset_id"] == "m1" and plan["s"]["asset"]["asset_id"] == "m2"
    assert plan["f"]["family"] == plan["s"]["family"] == "door:series:hssd:208"
    assert OM.op_ok(hinged, "sliding") is False and OM.op_ok(hinged, None) and OM.op_ok({"title": "Glass door"}, "x")


# --------------------------------------------------------------------------
# inside doors
# --------------------------------------------------------------------------

def _house():
    """Living | hall | bedroom on one level, an outside door into the living room; the inner walls at x = 5 and 7."""
    rooms = [{"id": "r_liv", "level_id": "L0", "room_type": "living", "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]},
             {"id": "r_hall", "level_id": "L0", "room_type": "hall", "polygon": [[5, 0], [7, 0], [7, 4], [5, 4]]},
             {"id": "r_bed", "level_id": "L0", "room_type": "bedroom", "polygon": [[7, 0], [11, 0], [11, 4], [7, 4]]}]
    walls = [{"id": "w5", "level_id": "L0", "start": [5, 0], "end": [5, 4], "thickness": 0.1},
             {"id": "w7", "level_id": "L0", "start": [7, 0], "end": [7, 4], "thickness": 0.1},
             {"id": "ws", "level_id": "L0", "start": [0, 0], "end": [11, 0], "thickness": 0.3}]
    openings = [{"id": "d_liv", "type": "door", "level_id": "L0", "wall_id": "w5", "center": [5, 2], "width": 0.9,
                 "height": 2.1, "swing_side": "r_liv"},
                {"id": "d_bed", "type": "door", "level_id": "L0", "wall_id": "w7", "center": [7, 2], "width": 0.8,
                 "height": 2.1, "swing_side": "r_bed", "hinge_side": "left"},
                {"id": "d_out", "type": "door", "level_id": "L0", "wall_id": "ws", "center": [2, 0], "width": 1.0,
                 "height": 2.1}]
    levels = [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}]
    return {"project": {"id": "house_t"}, "levels": levels, "walls": walls, "rooms": rooms, "openings": openings}


def test_inside_records_face_the_room_each_door_opens_into():
    b = _house()
    recs = {r["opening"]["id"]: r for r in OM.inside_records(b, b["levels"])}
    assert set(recs) == {"d_liv", "d_bed"}                        # the outside door is the facade plan's
    liv, bed = recs["d_liv"], recs["d_bed"]
    assert sorted(liv["joins"]) == ["hall", "living"] and liv["swing_room"] == "r_liv"
    assert liv["outward"] == [-1.0, 0.0] and bed["outward"] == [1.0, 0.0]   # into the living room / the bedroom
    assert liv["top"] == pytest.approx(2.1) and liv["thickness"] == 0.1
    assert OM.inside_records(b, b["levels"], skip={"d_liv"})[0]["opening"]["id"] == "d_bed"


def test_the_inside_role_is_the_door_style_of_its_rooms():
    style = {"family": "scandinavian", "door": {"material": "wood_oak_light"}}
    b = _house()
    recs = {r["opening"]["id"]: r for r in OM.inside_records(b, b["levels"])}
    assert OM.inside_role(recs["d_liv"], style)[0] == "glazed"          # = looks.role_door_style
    assert OM.inside_role(recs["d_bed"], style)[0] == "solid"
    slide = dict(recs["d_bed"], opening=dict(recs["d_bed"]["opening"], operation="sliding"))
    assert OM.inside_role(slide, style)[0] == "sliding"
    pocket = dict(recs["d_bed"], opening=dict(recs["d_bed"]["opening"], operation="pocket"))
    assert OM.inside_role(pocket, style)[0] is None
    pair = dict(recs["d_bed"], opening=dict(recs["d_bed"]["opening"], door_type="double"))
    # 29 Oct 2026 (UL89): a pair takes its rooms' role (two leaves of the role's model); a sliding pair stays parametric
    assert OM.inside_role(pair, style)[0] == "solid"
    slide_pair = dict(recs["d_bed"], opening=dict(recs["d_bed"]["opening"], door_type="sliding_pair"))
    assert OM.inside_role(slide_pair, style)[0] is None


def test_inside_doors_take_one_family_per_role_never_a_facade_family():
    style = {"family": "scandinavian", "door": {"material": "wood_oak_light"}}
    b = _house()
    recs = OM.inside_records(b, b["levels"])
    solid = _model(1, "HSSD door 201-2", w=0.9, h=2.2, series="hssd:201", q=4,
                   opening_vision={"role": "inside", "glazing": "none", "leaf": "flush", "handle_side": "right"})
    glazed_same = _model(2, "HSSD door 201-9", w=0.9, h=2.2, series="hssd:201", q=3,
                         opening_vision={"role": "inside", "glazing": "clear", "leaf": "glazed",
                                         "handle_side": "none"})
    glazed_other = _model(3, "HSSD door 204-3", w=0.9, h=2.2, series="hssd:204", q=4,
                          opening_vision={"role": "inside", "glazing": "clear", "leaf": "glazed"})
    front = _model(4, "HSSD door 3262-0", w=0.9, h=2.2, series="hssd:3262", q=5,
                   opening_vision={"role": "entrance", "glazing": "none"})
    notes: list = []
    plan = OM.plan_inside(b, recs, [solid, glazed_same, glazed_other, front], style=style, notes=notes)
    bed, liv = plan["d_bed"], plan["d_liv"]
    assert bed["asset"]["asset_id"] == "m1" and bed["role"] == "solid" and bed["inside"] is True
    assert liv["asset"]["asset_id"] == "m2" and liv["role"] == "glazed"        # the solid doors' series first
    assert "the solid doors' series" in liv["reason"] and liv["add_handles"] is True
    assert bed["outward"] == [1.0, 0.0] and bed["category"] == "inside_door"
    # d_bed: drawn hinge on the left -> the handle on the right: m1's handle is on the right, kept as modelled
    assert bed["mirror"] is False and "hinged on the drawn left" in bed["hinge"]
    flipped = dict(solid, opening_vision=dict(solid["opening_vision"], handle_side="left"))
    plan2 = OM.plan_inside(b, recs, [flipped, glazed_other], style=style)
    assert plan2["d_bed"]["mirror"] is True and "mirrored" in plan2["d_bed"]["hinge"]
    assert plan2["d_liv"]["asset"]["asset_id"] == "m3"                          # no glazed m1 series: its own
    # a facade family is never an inside door; nothing left -> the parametric door, logged with the reason
    notes = []
    plan3 = OM.plan_inside(b, recs, [solid], style=style, notes=notes, exclude_families={"door:series:hssd:201"})
    assert plan3 == {} and {n["id"] for n in notes if n["kind"] == "parametric"} == {"d_bed", "d_liv"}


def test_a_period_house_gives_its_private_rooms_panelled_doors():
    b = _house()
    recs = [r for r in OM.inside_records(b, b["levels"]) if r["opening"]["id"] == "d_bed"]
    flush = _model(1, "HSSD door 201-2", w=0.9, h=2.2, q=4, styles=("classic",),
                   opening_vision={"role": "inside", "glazing": "none", "leaf": "flush"})
    panel = _model(2, "HSSD door 204-3", w=0.9, h=2.2, q=4, styles=("classic",),
                   opening_vision={"role": "inside", "glazing": "none", "leaf": "panelled"})
    classic = OM.plan_inside(b, recs, [flush, panel], style={"family": "classic"})
    assert classic["d_bed"]["asset"]["asset_id"] == "m2"                 # = looks.role_door_style: shaker_panel
    light = OM.plan_inside(b, recs, [flush, panel], style={"family": "scandinavian"})
    assert light.get("d_bed", {}).get("asset", {}).get("asset_id") != "m2"   # a panelled leaf is out of the light look


def test_a_drawn_sliding_inside_door_takes_a_sliding_model_and_a_barn_door_only_in_its_styles():
    b = _house()
    for o in b["openings"]:
        if o["id"] == "d_bed":
            o["operation"] = "sliding"
    recs = [r for r in OM.inside_records(b, b["levels"]) if r["opening"]["id"] == "d_bed"]
    barn = _model(1, "Barn door - Loft", w=0.9, h=2.2, opening={"kind": "barn", "operation": "sliding"})
    slide = _model(2, "HSSD sliding door 211-7", w=1.0, h=2.2, opening={"kind": "sliding", "operation": "sliding"})
    swing = _model(3, "HSSD door 201-2", w=0.9, h=2.2)
    light = OM.plan_inside(b, recs, [barn, slide, swing], style={"family": "scandinavian"})
    assert light["d_bed"]["asset"]["asset_id"] == "m2" and light["d_bed"]["role"] == "sliding"
    rustic = OM.plan_inside(b, recs, [barn, swing], style={"family": "rustic"})
    assert rustic["d_bed"]["asset"]["asset_id"] == "m1"


def test_an_inside_door_is_centred_in_its_wall_and_can_be_mirrored():
    wall = {"start": [0, 0], "end": [4, 0], "thickness": 0.1}
    outer = OB.panel_layout((2.0, 0.0), wall, 0.9, 1, (0.0, -1.0), 0.3, 0.06)
    inner = OB.panel_layout((2.0, 0.0), wall, 0.9, 1, (0.0, -1.0), 0.3, 0.06, centred=True)
    assert outer[0][1] < 0 and inner[0] == pytest.approx((2.0, 0.0))
    verts = [(2.1, 0.0, 0.0), (2.4, 0.0, 0.0), (2.4, 0.0, 2.0)]
    v2, f2, uv2 = OB.mirror_across(verts, [[0, 1, 2]], [[(0, 0), (1, 0), (1, 1)]], (2.0, 0.0), (4.0, 0.0))
    assert [round(v[0], 6) for v in v2] == [1.9, 1.6, 1.6] and f2 == [[2, 1, 0]]
    assert uv2 == [[(1, 1), (1, 0), (0, 0)]]
    assert OB.mirror_across(verts, [[0, 1, 2]], None, (2.0, 0.0), (1.0, 0.0))[2] is None


def test_a_door_to_an_open_air_room_is_no_inside_door():
    from wenart.blender import architect as AR
    assert OM.OPEN_AIR_TYPES == AR.OPEN_AIR_TYPES
    b = _house()
    b["rooms"][2]["room_type"] = "terrace"
    assert [r["opening"]["id"] for r in OM.inside_records(b, b["levels"])] == ["d_liv"]


def test_the_build_plans_the_inside_doors_beside_the_facade(monkeypatch):
    from wenart.blender import build as BB
    b = _house()
    b["site"] = {"entrances": [{"door_id": "d_out", "main": True}]}
    models = [_model(1, "HSSD door 201-2", w=0.9, h=2.2, series="hssd:201", q=4,
                     opening_vision={"role": "inside", "glazing": "none", "leaf": "flush", "handle_side": "right"}),
              _model(2, "HSSD door 204-3", w=0.9, h=2.2, series="hssd:204", q=4,
                     opening_vision={"role": "inside", "glazing": "clear", "leaf": "glazed", "handle_side": "left"}),
              _model(3, "Modern Front Door", w=1.0, h=2.1, q=4, opening_vision={"role": "entrance"})]
    monkeypatch.setattr(OM, "load_extras", lambda *a, **k: [dict(m) for m in models])
    outline = [[0, 0], [11, 0], [11, 4], [0, 4]]
    prep = {"ground_outline": outline, "outlines": {"L0": outline}}
    style = {"family": "modern", "door": {"material": "wood_oak_light"}}
    warnings, assumed = [], []
    monkeypatch.delenv(BB.LIBRARY_INSIDE_DOORS_ENV, raising=False)
    monkeypatch.delenv(BB.LIBRARY_OPENINGS_ENV, raising=False)
    plan = BB.library_openings(b, b["levels"], prep, None, warnings, style=style, assumed=assumed)
    assert plan["d_out"]["category"] == "entrance" and plan["d_out"]["asset"]["asset_id"] == "m3"
    assert plan["d_bed"]["asset"]["asset_id"] == "m1" and plan["d_bed"]["role"] == "solid"
    assert plan["d_liv"]["asset"]["asset_id"] == "m2" and plan["d_liv"]["role"] == "glazed"
    assert OM.door_variety_problems(plan) == []
    monkeypatch.setenv(BB.LIBRARY_INSIDE_DOORS_ENV, "off")
    plan = BB.library_openings(b, b["levels"], prep, None, [], style=style)
    assert set(plan) == {"d_out"}


# --------------------------------------------------------------------------
# Argus: door variety
# --------------------------------------------------------------------------

def test_door_variety_problems_find_one_model_an_inside_model_outside_and_no_statement_entrance():
    def entry(cat, fam, title, role=None, statement=None):
        return {"category": cat, "family": fam, "asset": {"asset_id": fam, "title": title}, "model_role": role,
                "statement": statement}
    same = {"e": entry("entrance", "f1", "Front Door", statement=True), "d": entry("door", "f1", "Front Door"),
            "i1": entry("inside_door", "f1", "Front Door"), "i2": entry("inside_door", "f1", "Front Door")}
    kinds = {p["kind"] for p in OM.door_variety_problems(same)}
    assert {"one_door_model", "no_statement_entrance"} <= kinds
    facade = {"e": entry("entrance", "f1", "Modern Front Door", statement=True),
              "d": entry("door", "f2", "Bathroom Door"), "t": entry("terrace_door", "f3", "HSSD door 1-1", "inside")}
    found = OM.door_variety_problems(facade)
    assert sorted(p["target"] for p in found if p["kind"] == "inside_door_on_facade") == ["d", "t"]
    assert all({"target", "message", "severity"} <= set(p) for p in found)
    assert OM.door_variety_problems({"d": entry("door", "f2", "Plain Door")})[0]["kind"] == "no_statement_entrance"
    ok = {"e": entry("entrance", "f1", "Pivot Front Door", statement=True), "d": entry("door", "f2", "Plain Door"),
          "i": entry("inside_door", "f3", "HSSD door 201-2"), "w": entry("window", "f4", "Window")}
    assert OM.door_variety_problems(ok) == []
    # a manifest: library doors (library_model) and parametric doors (door record)
    manifest = {"objects": [
        {"kind": "door", "wenart_id": "e", "library_model": {"category": "entrance", "family": "f1",
                                                             "asset_id": "a1", "title": "Front Door",
                                                             "statement": True}},
        {"kind": "door", "wenart_id": "x", "door": {"door_style": "flush"}},
        {"kind": "door", "wenart_id": "y", "door": {"door_style": "flush"}},
        {"kind": "window", "wenart_id": "w", "library_model": {"category": "window", "family": "f9"}}]}
    assert OM.door_variety_problems(manifest) == []
    flat = {"objects": [{"kind": "door", "wenart_id": k, "door": {"door_style": "flush"}} for k in "abc"]}
    assert [p["kind"] for p in OM.door_variety_problems(flat)] == ["one_door_model"]
