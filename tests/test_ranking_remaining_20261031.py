"""31 Oct 2026, lesson UL217 (user: "include all remaining library models for ranking after the real04 run"): the
ranking studio's remaining batch (wenart.assets.audit.studio: the decor models, the extras the fit takes first, the
small items' models, any other furniture type), each on the stage of its kind; the sheets by type under new names (the
committed sheets keep theirs); the scoring page's groups of tabs; the user's rank in the normal decor pick and the
textile library pick. CPU only."""
import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path

import pytest

from wenart.assets.audit import studio as S
from wenart.blender import furniture as BF
from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from wenart.furniture import small_items as SI
from wenart.furniture import user_ranks as UR

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def cat():
    return C.load()


@pytest.fixture(scope="module")
def rows(cat):
    return S.remaining_entries(catalog=cat)


@pytest.fixture
def ranks_file(tmp_path, monkeypatch):
    path = tmp_path / "user_ranks.json"

    def write(rows: dict) -> Path:
        path.write_text(json.dumps({"ranks": {k: {"rank": v, "date": "2026-10-31", "sheet": "vase-01", "letter": "A"}
                                              for k, v in rows.items()}}), encoding="utf-8")
        UR.reset()
        return path
    monkeypatch.setattr(UR, "USER_RANKS_PATH", path)
    write({})
    yield write
    UR.reset()


class _Cat:
    def __init__(self, decor=(), extras=(), entries=()):
        self.decor, self.extras, self.entries = list(decor), list(extras), list(entries)


def _decor(iid, dtype="vase", bbox=(0.2, 0.2, 0.3), **kw):
    e = {"id": iid, "kind": "decor", "decor_type": dtype, "type": f"decor_{dtype}", "glb": f"models/3dwh/{iid}.glb",
         "bbox_m": list(bbox), "source": "3dwh", "licence": "CC-BY-4.0", "licence_flag": "none",
         "commercial_safe": True, "audit": {"status": "keep"}, "styles": ["neutral"], "real_product": True,
         "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0], "title": f"model {iid}"}
    e.update(kw)
    return e


def _one(rows, rtype, **want):
    return next(e for e in rows if e["type"] == rtype and all(e.get(k) == v for k, v in want.items()))


# --------------------------------------------------------------------------
# The models of the batch
# --------------------------------------------------------------------------

def test_the_remaining_batch_is_every_usable_model_not_on_the_sheets(cat, rows):
    done = S.committed_ids()
    assert len(done) >= 2453 and rows
    ids = [e["id"] for e in rows]
    assert len(ids) == len(set(ids)) and not set(ids) & done
    order = S.remaining_types()
    types = [e["type"] for e in rows if e["type"] in order]
    assert types == sorted(types, key=order.index)                     # page order, then by id
    for t in set(types):
        got = [e["id"] for e in rows if e["type"] == t]
        assert got == sorted(got)
    seen = set(done)
    for t in order:                                                    # = the fit's own pools, minus the sheets
        if t in F.LIBRARY_FIRST:
            want = sorted(e["id"] for e in cat.extras if e.get("type") == F.LIBRARY_FIRST[t][0] and e.get("glb")
                          and e.get("bbox_m") and C.usable(e, "relaxed"))
        else:
            want = [e["id"] for e in F.decor_entries(cat, t, "relaxed")]
        want = [i for i in want if i not in seen]
        seen.update(want)
        assert [e["id"] for e in rows if e["type"] == t] == want, t
    for kind in SI.ITEMS:                                              # every small item's model is on a sheet
        assert {e["id"] for e in SI.candidates(kind, cat, "relaxed")} <= seen | {e["id"] for e in rows}
    assert {"cushion", "rug", "curtain", "blind", "throw", "pendant_light", "wall_art", "tv", "laptop"} <= set(types)
    assert all(C.usable(e, "relaxed") for e in rows)
    assert {e["studio"] for e in rows if e["type"] == "tv"} == {"extra"}
    assert all(e["catalog_type"] for e in rows if S.is_decor_row(e))


def test_small_items_and_other_furniture_types_join_the_batch():
    """A small item's model no decor type lists (a soap dispenser of the extras) goes on its own small_<kind> sheet; a
    furniture type outside ALL_TYPES on the furniture stage; a model on a committed sheet never again."""
    soap = _decor("soap1", "vase", (0.07, 0.07, 0.19), type="bathroom_set", kind=None, decor_type=None,
                  title="Glass soap dispenser", audit={"status": "keep", "vision_quality": 5})
    vase = _decor("vase1")
    rack = dict(_decor("rack1", "vase", (0.5, 0.5, 1.8)), type="coat_rack", kind=None, decor_type=None)
    old = _decor("vase0")
    got = S.remaining_entries(catalog=_Cat(decor=[vase, old], extras=[soap], entries=[rack]), done={"vase0"})
    assert [(e["id"], e["type"], e.get("studio")) for e in got] == [
        ("vase1", "vase", "decor"), ("soap1", "small_pump_bottle", "small"), ("rack1", "coat_rack", None)]
    assert got[1]["build_type"] == S.SMALL_BUILD_TYPE and S.tab_group("small_pump_bottle") == S.GROUP_SMALL
    assert S.remaining_entries(catalog=_Cat(decor=[vase], extras=[soap]), done=set(), types=["electronics"]) == []
    assert [e["id"] for e in S.remaining_entries(catalog=_Cat(decor=[vase]), done=set(), types=["tabletop"])] == \
        ["vase1"]


# --------------------------------------------------------------------------
# The stages
# --------------------------------------------------------------------------

def test_a_decor_model_is_built_from_the_fits_own_record_at_its_own_size(rows):
    """fit.decor_model_asset is the fit's record (fit_decor_item's refactor kept every field and their order); the
    studio's asset of a model equals the fit's asset on an item of the model's own size."""
    e = _one(rows, "vase")
    w, d, h = e["bbox_m"]
    asset = S.studio_asset(e)
    assert asset["target"] == "within" and asset["fit_scale"] == [1.0, 1.0, 1.0]
    assert asset["bbox_m"] == [round(float(v), 4) for v in (w, d, h)] and asset["asset_id"] == e["id"]
    raw = {k: v for k, v in e.items() if k not in ("type", "catalog_type", "studio", "build_type")}
    raw["type"] = e["catalog_type"]
    fitted = F.fit_decor_item({"id": "x", "type": "vase", "size": [w, d, h], "host_id": "h"}, _Cat(decor=[raw]),
                              None, mode="relaxed")
    for key, value in asset.items():
        assert fitted[key] == value, key
    tv = _one(rows, "tv")
    assert S.studio_asset(tv) == F.library_first_asset(tv, "tv", F.library_first_scale(tv, "tv"))
    rug = S.studio_asset(_one(rows, "rug"))
    assert rug["target"] == "rug" and rug["bbox_m"][2] <= F.RUG_MAX_THICKNESS_M + 1e-9


def test_each_kind_gets_its_stage_and_the_builder_builds_it_there(rows):
    kinds = {}
    for e in rows:
        st = S.decor_stage(e)
        kinds.setdefault(st["kind"], (e, st))
        item = st["item"]
        kept, why = BF.floor_class_item(item, None)                    # never "a table piece on the floor" (UL151)
        assert why is None and kept.get("asset") is item["asset"], e["id"]
        level = {"id": "L0", "elevation": 0.0, "ceiling_height": st["ceiling_m"]}
        assert BF.decor_floor({"rooms": []}, level, item)[1] is item    # at its own height, as staged
    assert set(kinds) == {"plinth", "floor", "rug", "wall", "window", "pendant", "flush"}
    e, st = kinds["plinth"]
    plinth = st["props"][0]
    assert plinth["kind"] == "plinth" and st["item"]["center"][2] == plinth["max"][2] == S.STAGE["plinth_h_m"]
    side = plinth["max"][0] - plinth["min"][0]
    assert side >= max(S.STAGE["plinth_min_m"], max(st["item"]["asset"]["bbox_m"][:2])) - 1e-9
    e, st = kinds["wall"]
    box = st["item"]["asset"]["bbox_m"]
    footprint, mount = BF.wall_art_placement(st["item"], box, None, st["ceiling_m"])
    assert footprint is not None and mount["scale"] == 1.0 and footprint["center"][1] < 0       # in front of the wall
    assert st["props"][0]["kind"] == "backdrop" and st["props"][0]["min"][1] == 0.0
    e, st = kinds["window"]
    h = st["item"]["asset"]["bbox_m"][2]
    bottom = st["item"]["center"][2]
    assert abs(bottom + h - S.STAGE["textile_top_m"]) < 1e-3 or bottom == S.STAGE["textile_bottom_min_m"]
    assert st["item"]["center"][1] < -st["item"]["asset"]["bbox_m"][1] / 2                      # off the backdrop
    for kind in ("pendant", "flush"):
        e, st = kinds[kind]
        h = st["item"]["asset"]["bbox_m"][2]
        plan = BF.hang_plan(st["item"]["type"], st["item"]["center"][2], h, st["ceiling_m"])
        assert abs(plan["gap_left_m"]) < 1e-3                             # connected to the stage's ceiling
        assert (plan["cord_m"] > 0) == (kind == "pendant") and abs(plan["lift_m"]) < 1e-3
        assert st["props"][0]["kind"] == "panel" and st["props"][0]["min"][2] == st["ceiling_m"]
        assert st["props"][0]["shadow"] is False
    e, st = kinds["pendant"]
    assert BF.pendant_hang(st["item"]["center"][2], st["ceiling_m"])[1] is None
    assert kinds["rug"][1]["camera"]["elevation_deg"] > 45 and kinds["plinth"][1]["camera"] == {}
    e, st = kinds["floor"]
    assert len(st["item"]["center"]) == 2 and not st["props"]


def test_the_camera_of_a_stage_frames_the_box_from_its_angle():
    box = ([-0.3, -0.3, 1.2], [0.3, 0.3, 1.55])
    for kind, over in S.STAGE_CAMERAS.items():
        cam = S.camera(*box, dict(S.SETTINGS, **over))
        el = over.get("elevation_deg", S.SETTINGS["elevation_deg"])
        target = cam["target"]
        dz = cam["location"][2] - target[2]
        assert (dz > 0) == (el > 0), kind
        assert cam["distance"] > 0


# --------------------------------------------------------------------------
# The plan, the sheets and the index
# --------------------------------------------------------------------------

def test_the_plan_carries_the_stage_and_keeps_the_furniture_jobs_current(tmp_path, rows):
    assets, work = tmp_path / "assets", tmp_path / "work"
    e = copy.deepcopy(_one(rows, "pendant_light"))
    (assets / e["glb"]).parent.mkdir(parents=True, exist_ok=True)
    (assets / e["glb"]).write_bytes(b"x")
    doc = S.plan([e], assets, work)
    job = doc["jobs"][0]
    assert "piece" not in job and job["stage"] == S.decor_stage(e) and job["stage"]["kind"] == "pendant"
    assert S.job_sha(e, S.SETTINGS) != S.job_sha(dict(e, type="ceiling_light", build_type="ceiling_light"),
                                                  S.SETTINGS)
    # a furniture model's job (and so its current image) is the one of the committed batches
    sofa = S.rank_entries(("sofa",))[0]
    keys = ("glb", "gltf", "sha256_glb", "bbox_m", "unit_scale", "origin_offset", "front_axis", "up_axis",
            "bed_frame", "deck_height_m", "has_mattress", "has_bedding", "has_cushions", "material_slots")
    body = {"v": S.STUDIO_VERSION, "entry": {k: sofa.get(k) for k in keys}, "settings": S.SETTINGS}
    assert S.job_sha(sofa, S.SETTINGS) == hashlib.sha256(json.dumps(body, sort_keys=True, default=str)
                                                         .encode("utf-8")).hexdigest()
    assert S.STUDIO_VERSION == "ul217.1"


def test_new_sheets_go_by_type_and_never_take_a_committed_name(tmp_path, rows):
    sheets = S.sheet_plan(rows)
    taken = S.committed_sheets()
    assert "sofa-01" in taken and "ours-01" in taken
    S.check_sheet_names(sheets, taken)                                 # no clash
    assert {s["type"] for s in sheets} == {e["type"] for e in rows}
    assert all(re.fullmatch(r"[a-z_]+-\d{2}", s["sheet"]) for s in sheets)
    with pytest.raises(ValueError):
        S.check_sheet_names([{"sheet": "sofa-01"}], taken)
    # the batch's own index is no committed sheet of another batch (it is redone the same way)
    (tmp_path / "ranking_index.json").write_text(json.dumps({"models": {"a": {}}, "sheets": [{"sheet": "sofa-01"}]}))
    (tmp_path / "ranking_index_remaining.json").write_text(json.dumps({"models": {"b": {}},
                                                                       "sheets": [{"sheet": "vase-01"}]}))
    assert S.committed_ids(tmp_path) == {"a"} and S.committed_sheets(tmp_path) == {"sofa-01"}
    index = S.index_doc(rows, sheets)
    first = rows[0]
    assert index["models"][first["id"]]["type"] == first["type"]
    assert index["models"][first["id"]]["catalog_type"] == first["catalog_type"]
    assert index["types"][:3] == ["cushion", "throw", "rug"]


def test_the_cli_plans_one_group_of_the_batch(tmp_path):
    out = tmp_path / "out"
    code = S.main(["plan", "--batch", "remaining", "--types", "lights", "--assets", str(tmp_path / "a"), "--work",
                   str(tmp_path / "w"), "--out", str(out), "--limit", "2"])
    assert code == 0
    index = json.loads((out / "ranking_index_remaining.json").read_text())
    assert index["types"] == ["table_lamp", "pendant_light", "ceiling_light"]
    assert [s["sheet"] for s in index["sheets"]] == ["table_lamp-01", "pendant_light-01", "ceiling_light-01"]
    plan = json.loads((out / "studio_plan_remaining.json").read_text())
    assert len(plan["missing"]) == 6 and not (out / "ranking_index.json").exists()
    assert [e["type"] for e in S.batch_entries("", [])][:1] == ["bed_double"]      # the default batch as before
    with pytest.raises(ValueError):
        S.batch_entries("nope")


def test_the_job_script_and_the_blender_side_know_the_batch():
    job = (ROOT / "scripts" / "jobs" / "library_ranking.sh").read_text()
    assert 'RANK_BATCH="${RANK_BATCH:-}"' in job and 'ARGS+=(--batch "$RANK_BATCH")' in job
    assert 'studio_results_${RANK_BATCH}.json' in job and "S.batch_entries(sys.argv[2], types)" in job
    assert 'RANK_TYPES="bed_double,sofa,armchair"' in job                 # the default run as before
    src = (ROOT / "wenart" / "assets" / "audit" / "blender_studio.py").read_text()
    assert 'if job.get("stage"):' in src and '"ceiling_height": float(stage["ceiling_m"])' in src
    assert "ob.visible_shadow = False" in src and '"decor": [item]' in src


def test_merging_scores_reads_every_committed_index(tmp_path):
    a, b = tmp_path / "ranking_index.json", tmp_path / "ranking_index_remaining.json"
    a.write_text(json.dumps({"models": {"m1": {"type": "sofa", "sheet": "sofa-01", "letter": "A"}},
                             "sheets": [{"sheet": "sofa-01", "letters": {"A": "m1"}}]}))
    b.write_text(json.dumps({"models": {"v1": {"type": "vase", "sheet": "vase-01", "letter": "A"}},
                             "sheets": [{"sheet": "vase-01", "letters": {"A": "v1"}}]}))
    index = UR.load_indexes([a, b])
    doc = UR.merge(None, {"m1": 7, "v1": 2, "zz": 9}, index, "2026-10-31")
    assert set(doc["ranks"]) == {"m1", "v1"} and doc["ranks"]["v1"]["type"] == "vase"
    assert [s["sheet"] for s in index["sheets"]] == ["sofa-01", "vase-01"]


# --------------------------------------------------------------------------
# The page
# --------------------------------------------------------------------------

def _page_module():
    spec = importlib.util.spec_from_file_location("ranking_page", ROOT / "scripts" / "ranking_page.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _const(html_text: str, name: str):
    line = next(x for x in html_text.splitlines() if x.startswith(f"const {name} = "))
    return json.loads(line[len(f"const {name} = "):].split(";")[0])


def test_the_page_groups_the_tabs_with_readable_names(tmp_path):
    rk = tmp_path / "ranking"
    rk.mkdir()

    def index(models, sheets, types):
        return {"types": types, "sheets": sheets, "models": models}
    (rk / "ranking_index.json").write_text(json.dumps(index(
        {"s1": {"type": "sofa", "title": "Sofa"}}, [{"sheet": "sofa-01", "type": "sofa", "letters": {"A": "s1"}}],
        ["sofa"])))
    (rk / "ranking_index_ours.json").write_text(json.dumps(index(
        {"ours:toilet:p": {"type": "toilet", "group": "ours", "procedural": True}},
        [{"sheet": "ours-01", "type": "ours", "letters": {"A": "ours:toilet:p"}}], ["ours"])))
    (rk / "ranking_index_remaining.json").write_text(json.dumps(index(
        {"v1": {"type": "vase"}, "t1": {"type": "tv"}, "p1": {"type": "small_pump_bottle"}},
        [{"sheet": "vase-01", "type": "vase", "letters": {"A": "v1"}},
         {"sheet": "tv-01", "type": "tv", "letters": {"A": "t1"}},
         {"sheet": "small_pump_bottle-01", "type": "small_pump_bottle", "letters": {"A": "p1"}}],
        ["vase", "tv", "small_pump_bottle"])))
    mod = _page_module()
    out = tmp_path / "page" / "index.html"
    assert mod.main(["--ranking", str(rk), "--out", str(out)]) == 0
    text = out.read_text()
    groups = _const(text, "GROUPS")
    assert groups == [["Our builds", ["ours"]], ["Tabletop", ["vase"]], ["Electronics", ["tv"]],
                      ["Small items", ["small_pump_bottle"]], ["Furniture", ["sofa"]]]
    names = _const(text, "NAMES")
    assert names["vase"] == "Vases" and names["tv"] == "TVs" and names["small_pump_bottle"] == "Soap pumps"
    assert names["sofa"] == "Sofas" and mod.type_name("small_new_kind") == "New kind"
    assert 'id="groups"' in text and "renderGroups()" in text
    assert mod.main(["--ranking", str(rk), "--out", str(out), "--batch", "remaining"]) == 0
    text = out.read_text()
    assert _const(text, "TYPES") == ["vase", "tv", "small_pump_bottle"]
    assert {m["sheet"] for m in _const(text, "MODELS")} == {"vase-01", "tv-01", "small_pump_bottle-01"}
    for t in S.remaining_types():                                      # every sheet type has a readable name
        assert t in mod.TYPE_NAMES


# --------------------------------------------------------------------------
# The user's rank in the decor picks
# --------------------------------------------------------------------------

def test_the_normal_decor_pick_takes_the_users_best_ranked_models_first(ranks_file):
    vases = [_decor(f"v{i}") for i in range(3)]
    cat = _Cat(decor=vases)

    def pick(host):
        return F.fit_decor_item({"id": f"d_{host}", "type": "vase", "size": [0.3, 0.3, 0.4], "host_id": host}, cat,
                                None, mode="relaxed")
    hosts = [f"h{i}" for i in range(24)]
    plain = {h: pick(h)["asset_id"] for h in hosts}
    assert len(set(plain.values())) == 3 and all("user_rank" not in pick(h)["pick"] for h in hosts)
    ranks_file({"v1": 8})
    assert {pick(h)["asset_id"] for h in hosts} == {"v1"}              # the best-ranked one
    assert pick("h0")["pick"]["user_rank"] == {"rule": UR.RULE, "rank": 8, "kept": 1, "dropped": {"5": 2}}
    ranks_file({"v0": 3})                                              # below the unranked 5: never while 5s fit
    got = {h: pick(h)["asset_id"] for h in hosts}
    assert set(got.values()) == {"v1", "v2"} and got == {h: pick(h)["asset_id"] for h in hosts}   # deterministic
    ranks_file({"v0": 2, "v1": 3, "v2": 3})                            # 0-2: never used at all (catalog.usable)
    assert {pick(h)["asset_id"] for h in hosts} == {"v1", "v2"}
    ranks_file({"v0": 2, "v1": 2, "v2": 1})
    assert pick("h0") is None
    ranks_file({"v0": 9})                                              # a model that does not fit stays out
    big = dict(_decor("v0", bbox=(2.0, 0.1, 0.3)))                   # scaled to 0.3 m wide: 1.5 cm deep, refused
    asset = F.fit_decor_item({"id": "d", "type": "vase", "size": [0.3, 0.3, 0.4], "host_id": "h0"},
                             _Cat(decor=[big] + vases[1:]), None, mode="relaxed")
    assert asset["asset_id"] in ("v1", "v2")


def test_a_bedside_pendant_keeps_its_role_before_the_rank(ranks_file):
    slim = _decor("slim", "pendant_light", (0.15, 0.15, 0.6), title="slim drop pendant")
    wide = _decor("wide", "pendant_light", (0.6, 0.6, 0.4), title="wide dome pendant")
    ranks_file({"wide": 9})
    item = {"id": "p", "type": "pendant_light", "size": [0.7, 0.7, 1.0], "room_id": "r1", "fixture": "bedside"}
    asset = F.fit_decor_item(item, _Cat(decor=[slim, wide]), None, mode="relaxed")
    assert asset["asset_id"] == "slim"                                 # the role first, then the user's rank
    item = dict(item, fixture=None)
    assert F.fit_decor_item(item, _Cat(decor=[slim, wide]), None, mode="relaxed")["asset_id"] == "wide"


def test_the_textile_library_pick_reads_the_users_rank(ranks_file):
    def curtain(iid, quality=None):
        e = _decor(iid, "curtain", (2.2, 0.18, 2.6), styles=["modern"])
        if quality is not None:
            e["audit"]["vision_quality"] = quality
        return e
    item = {"id": "c", "type": "curtain", "size": [2.0, 0.08, 2.5], "center": [0.0, 0.0, 0.01]}
    cat = _Cat(decor=[curtain("unrated"), curtain("five", 5)])
    assert F.fit_decor_item(dict(item), cat, "modern", mode="relaxed")["asset_id"] == "five"
    ranks_file({"unrated": 7, "five": 4})                              # the user's eye before the vision quality
    assert F.fit_decor_item(dict(item), cat, "modern", mode="relaxed")["asset_id"] == "unrated"
    ranks_file({"unrated": 5, "five": 4})
    got = dict(item)
    assert F.fit_decor_item(got, cat, "modern", mode="relaxed") is None and "rates better" in got["library_gap"]["why"]


def test_the_page_has_one_score_filter_for_every_tab():
    """User (31 Oct 2026): "on the review page also put a filter general for the ranks slide 0 to 10 and for the ones
    which is not ranked yet": a two-handle 0-10 slider over the scored models, a not-ranked-yet switch, an all-types
    switch and a reset, applied by one ``matches`` rule to the grid."""
    import importlib.util
    from pathlib import Path

    spec = importlib.util.spec_from_file_location("ranking_page", Path(__file__).resolve().parents[1] / "scripts"
                                                  / "ranking_page.py")
    RP = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(RP)
    rows = [{"id": "a", "tab": "sofa", "type": "sofa", "sheet": "sofa-01", "letter": "A", "x": 0, "y": 0}]
    html = RP.page(rows, ["sofa"])
    for needle in ('id="f-lo" min="0" max="10"', 'id="f-hi" min="0" max="10"', 'id="f-unranked" checked',
                   'id="f-ranked" checked', 'id="f-all"', 'id="f-reset"', "function matches(m, f)",
                   '(f.all || m.tab === current) && matches(m, f)'):
        assert needle in html, needle
    assert 'id="unranked"' not in html            # the old "Unranked only" box is part of the filter now
