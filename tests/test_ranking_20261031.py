"""31 Oct 2026, lesson UL217 (user: "Is it possible to do furniture ranking system? we render the furnitures and I
ranked them from 10 to 0 based purely on the look?", then "page with score buttons, start with beds sofas
armchairs"): the ranking studio (wenart.assets.audit.studio), the user's ranks (wenart.furniture.user_ranks) and the
fit's use of them (catalog.usable, fit.rank_key, the library-first decor). CPU only."""
import copy
import json
import math
import subprocess
from pathlib import Path

import pytest

from wenart.assets.audit import studio as S
from wenart.furniture import catalog as C
from wenart.furniture import fit as F
from wenart.furniture import user_ranks as UR

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def ranks_file(tmp_path, monkeypatch):
    """A user_ranks.json of our own (the committed one is not read)."""
    path = tmp_path / "user_ranks.json"

    def write(rows: dict) -> Path:
        path.write_text(json.dumps({"ranks": {k: {"rank": v, "date": "2026-10-31", "sheet": "sofa-01",
                                                  "letter": "A"} for k, v in rows.items()}}), encoding="utf-8")
        UR.reset()
        return path
    monkeypatch.setattr(UR, "USER_RANKS_PATH", path)
    write({})
    yield write
    UR.reset()


def _entries(ftype: str, n: int = 3) -> list[dict]:
    return [e for e in S.rank_entries((ftype,))][:n]


def test_the_ranked_models_are_the_ones_the_fit_may_use_in_type_order():
    rows = S.rank_entries(("sofa", "armchair"))
    types = [e["type"] for e in rows]
    assert types == sorted(types, key=("sofa", "armchair").index) and set(types) == {"sofa", "armchair"}
    assert all(C.usable(e, "relaxed") and F.bed_usable(e) for e in rows)
    ids = [e["id"] for e in rows if e["type"] == "sofa"]
    assert ids == sorted(ids)
    beds = S.rank_entries(("bed_double",))
    assert beds and all(F.bed_usable(e) for e in beds)                 # a bed without a mattress or deck: never


def test_the_studio_piece_carries_the_fits_own_asset_record():
    for ftype in S.RANK_TYPES:
        e = _entries(ftype, 1)[0]
        piece = S.studio_piece(e)
        w, d, h = (float(v) for v in e["bbox_m"])
        assert piece["type"] == ftype and piece["footprint"]["size"] == [round(w, 4), round(d, 4)]
        assert piece["footprint"]["center"] == [0.0, 0.0] and piece["footprint"]["rotation_deg"] == 0.0
        assert piece["asset"] == F.model_asset(e, ftype, w, d, [1.0, 1.0, 1.0])
        assert piece["asset"]["method"] == "library" and piece["asset"]["asset_id"] == e["id"]
    frame = next((e for e in S.rank_entries(("bed_double",)) if F.is_bed_frame(e) and not C.has_mattress(e)), None)
    if frame is not None:                                           # a bed frame comes with its bedding, as built
        assert S.studio_piece(frame)["asset"]["bedding"]["top_m"] > 0


def test_the_fit_and_the_studio_build_the_same_record():
    """fit.model_asset is the fit's own record (the refactor of 31 Oct 2026 kept every field)."""
    e = _entries("sofa", 1)[0]
    w, d, _ = e["bbox_m"]
    piece = {"id": "f1", "type": "sofa", "footprint": {"center": [0, 0], "size": [w, d], "rotation_deg": 0}}
    asset = F.fit_piece(piece, C.load())
    assert asset["method"] == "library"
    chosen = next(x for x in S.catalogue_entries() if x["id"] == asset["asset_id"])
    core = F.model_asset(chosen, "sofa", w, d, asset["fit_scale"])
    for key, value in core.items():
        assert asset[key] == value, key
    assert {"candidates", "ranking", "cap", "aspect_error", "depth_abs_m"} <= set(asset) - set(core)


def test_sheets_letter_twenty_models_each_per_type():
    rows = [{"id": f"s{i:03d}", "type": "sofa"} for i in range(45)] + [{"id": "a1", "type": "armchair"}]
    sheets = S.sheet_plan(rows)
    assert [s["sheet"] for s in sheets] == ["sofa-01", "sofa-02", "sofa-03", "armchair-01"]
    assert list(sheets[0]["letters"]) == list("ABCDEFGHIJKLMNOPQRST") and sheets[0]["of"] == 3
    assert sheets[2]["letters"] == {"A": "s040", "B": "s041", "C": "s042", "D": "s043", "E": "s044"}
    assert sheets[3]["letters"] == {"A": "a1"}


def test_the_camera_frames_every_corner_of_the_box():
    s = dict(S.SETTINGS)
    tan_half = (s["sensor_mm"] / 2) / s["lens_mm"]
    for box in (([-1.0, -1.1, 0.0], [1.0, 1.1, 1.1]), ([-0.4, -0.4, 0.0], [0.4, 0.4, 1.0]),
                ([-1.4, -0.5, 0.0], [1.4, 0.5, 0.85])):
        cam = S.camera(*box)
        fwd, right, up = S.view_basis(s["azimuth_deg"], s["elevation_deg"])
        worst = 0.0
        for x in (box[0][0], box[1][0]):
            for y in (box[0][1], box[1][1]):
                for z in (box[0][2], box[1][2]):
                    rel = [x - cam["location"][0], y - cam["location"][1], z - cam["location"][2]]
                    depth = sum(a * b for a, b in zip(rel, fwd))
                    assert depth > 0
                    u = abs(sum(a * b for a, b in zip(rel, right))) / depth
                    v = abs(sum(a * b for a, b in zip(rel, up))) / depth
                    worst = max(worst, u, v)
        assert worst <= tan_half / s["margin"] * 1.001                # inside the frame with the margin
        assert worst >= tan_half / s["margin"] * 0.999                # and tight: one corner on the margin
    assert abs(math.degrees(math.asin(-S.view_basis(35, 16)[0][2])) - 16) < 1e-9


def test_the_sheets_and_tiles_are_drawn(tmp_path):
    from PIL import Image
    work, out = tmp_path / "work", tmp_path / "out"
    rows = [{"id": f"m{i}", "type": "sofa", "bbox_m": [2.0, 0.9, 0.8], "title": "Sofa", "source": "abo"}
            for i in range(3)]
    for r in rows[:2]:
        p = S.image_path(work, r["id"])
        p.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (64, 64), (120, 100, 90)).save(p)
    index = S.index_doc(rows, S.sheet_plan(rows))
    assert index["types"] == ["sofa"] and index["models"]["m2"]["letter"] == "C"
    res = S.compose_sheets(index, work, out, {"sheet_tile_px": 64, "tile_px": 48})
    assert res == {"sheets": 1, "tiles": 2, "missing": ["m2"]}
    assert Image.open(out / "sheets" / "sofa-01.jpg").size == (5 * 64, 56 + 4 * 64)
    assert Image.open(out / "tiles" / "sofa" / "m0.jpg").size == (48, 48)


def test_the_plan_skips_a_current_image_and_lists_a_missing_file(tmp_path):
    from wenart.assets.audit import render as R
    assets, work = tmp_path / "assets", tmp_path / "work"
    e = copy.deepcopy(_entries("armchair", 1)[0])
    (assets / e["glb"] if e.get("glb") else assets / e["gltf"]).parent.mkdir(parents=True, exist_ok=True)
    (assets / (e.get("glb") or e["gltf"])).write_bytes(b"x")
    gone = dict(e, id="gone", glb="models/none/gone.glb")
    doc = S.plan([e, gone], assets, work)
    assert [j["id"] for j in doc["jobs"]] == [e["id"]] and doc["missing"][0]["id"] == "gone"
    job = doc["jobs"][0]
    R.measure_path(work, e["id"]).parent.mkdir(parents=True, exist_ok=True)
    R.measure_path(work, e["id"]).write_text(json.dumps({"id": e["id"], "job_sha": job["job_sha"], "ok": True}))
    S.image_path(work, e["id"]).parent.mkdir(parents=True, exist_ok=True)
    S.image_path(work, e["id"]).write_bytes(b"png")
    again = S.plan([e], assets, work)
    assert not again["jobs"] and again["skipped"] == [e["id"]]
    assert R.blender_command("b", Path("j.json"), S.STUDIO_SCRIPT)[6].endswith("blender_studio.py")


def test_user_ranks_rules(ranks_file):
    assert [UR.valid_rank(v) for v in (0, 10, 7.0, 11, -1, True, 6.5, "7")] == [0, 10, 7, None, None, None, None, None]
    ranks_file({"low": 2, "mid": 3, "top": 10})
    assert UR.out_reason({"id": "low"}) and "2/10" in UR.out_reason({"id": "low"})
    assert UR.out_reason({"id": "mid"}) is None and UR.out_reason({"id": "new"}) is None
    assert UR.rank_steps({"id": "top"}) == -10 and UR.rank_steps({"id": "mid"}) == 4 and UR.rank_steps({}) == 0
    assert UR.rank_of({"asset_id": "top"}) == 10                       # a fitted asset too
    assert UR.better_than_procedural({"id": "top"}) is True and UR.better_than_procedural({"id": "mid"}) is False
    assert UR.better_than_procedural({"id": "new"}) is None


def test_merge_keeps_valid_ranks_of_known_models():
    index = {"models": {"a": {"type": "sofa", "sheet": "sofa-01", "letter": "A", "title": "A sofa"},
                        "b": {"type": "sofa", "sheet": "sofa-01", "letter": "B", "title": "B sofa"}}}
    doc = UR.merge({"ranks": {"b": {"rank": 4}}}, {"a": 9, "b": 1, "zz": 5, "c": 12}, index, "2026-10-31")
    assert doc["kind"] == "user_ranks" and set(doc["ranks"]) == {"a", "b"}
    assert doc["ranks"]["a"]["rank"] == 9 and doc["ranks"]["b"]["rank"] == 1 and doc["ranks"]["a"]["letter"] == "A"


def test_a_low_rank_is_never_used_and_a_high_rank_comes_first(ranks_file):
    a, b = _entries("sofa", 2)
    assert C.usable(a, "relaxed") and C.usable(b, "relaxed")
    ranks_file({a["id"]: 1})
    assert not C.usable(a, "relaxed") and "ranked" in C.unusable_reason(a, "relaxed")
    w, d = (float(v) for v in a["bbox_m"][:2])
    ranks_file({a["id"]: 3, b["id"]: 9})
    order = F.rank_candidates([a, b], w, d)
    assert order[0]["id"] == b["id"]
    ka, kb = F.rank_key(a, w, d), F.rank_key(b, w, d)
    assert kb[2] < ka[2]                                               # the rank lives in the size steps
    ranks_file({})
    assert F.rank_key(a, w, d)[2] == ka[2] + UR.rank_steps({}) - 4 + F.soft_steps(a)


def test_the_users_rank_decides_library_first_decor(ranks_file):
    entry = {"id": "lap1", "type": "laptop", "glb": "x.glb", "bbox_m": [0.33, 0.24, 0.22], "real_product": True,
             "licence": "CC-BY-4.0", "source": "3dwh", "audit": {"status": "keep", "vision_quality": 3}}
    cat = type("Cat", (), {"extras": [entry]})()
    item = {"type": "laptop", "size": [0.35, 0.25]}
    assert F.library_first_item(dict(item), cat, None, "relaxed") is None        # vision quality 3 (< 4): procedural
    ranks_file({"lap1": 8})
    got = F.library_first_item(dict(item), cat, None, "relaxed")
    assert got is not None and got["asset_id"] == "lap1"
    ranks_file({"lap1": 5})
    assert F.library_first_item(dict(item), cat, None, "relaxed") is None        # ranked, but not better than ours


def test_the_job_script_and_the_stage_code_lists():
    job = ROOT / "scripts" / "jobs" / "library_ranking.sh"
    assert subprocess.run(["bash", "-n", str(job)], capture_output=True).returncode == 0
    text = job.read_text()
    assert "set -Eeuo pipefail" in text and "wenart.assets.audit.studio render" in text and "--limit 1" in text
    from wenart.run import stages as ST
    assert "results/library/user_ranks.json" in ST.FIT_CODE and "wenart/furniture/user_ranks.py" in ST.FIT_CODE
    assert "results/library/user_ranks.json" in ST.LEVELS_CODE
    build = (ROOT / "wenart" / "blender" / "build.py").read_text()
    assert '"wenart/furniture/user_ranks.py"' in build


def test_each_studio_model_gets_a_fresh_material_library():
    """Pod run 20261031-070545: the purge after each model removed the materials of a library kept for the whole run;
    52 of 520 models (48 beds with their bedding) failed on 'StructRNA of type Material has been removed'."""
    src = (ROOT / "wenart" / "assets" / "audit" / "blender_studio.py").read_text()
    assert "one(job, doc, scene, cam, new_library(job.get(\"style\")), keep)" in src and "orphans_purge" in src


@pytest.mark.user_ranks
def test_the_committed_ranks_are_valid():
    """The committed ranks (the user's scores from the ranking page) load, every rank is 0-10 and every ranked model
    is in the catalogue; a model ranked 0-2 is out of the fit."""
    UR.reset()
    rows = UR.ranks()
    data = json.loads(UR.USER_RANKS_PATH.read_text(encoding="utf-8"))
    assert len(rows) == len(data.get("ranks") or {})
    ids = {e["id"] for e in S.catalogue_entries()}
    assert set(rows) <= ids
    low = next((e for e in S.catalogue_entries() if e["id"] in rows and rows[e["id"]]["rank"] <= UR.OUT_AT_OR_BELOW),
               None)
    if low is not None:
        assert not C.usable(low, "relaxed")


def test_the_survey_text_is_read_back_against_the_sheets_the_rater_saw():
    index = {"sheets": [{"sheet": "sofa-01", "letters": {"A": "m1", "B": "m2", "T": "m20"}}]}
    name, got = UR.parse_text("Name: Ayse K\nsofa-01: A7 B0 T10 C5 Z9\nchair-09: A3\n", index)
    assert name == "Ayse K" and got == {"m1": 7, "m2": 0, "m20": 10}
    page = (ROOT / "scripts" / "ranking_page.py").read_text()
    assert "Copy my scores" in page and "ratings/{self}" in page and "--inline" in page


def test_our_builds_are_on_their_own_sheets_with_the_projects_styles():
    """31 Oct 2026 (the user: "yes start with 1 and 2"): every parametric and module builder, in each latest project's
    style, as "ours:<type>:<project>" on the "ours" sheets; a change of the builders' code changes the job."""
    styles = [("p1", {"family": "modern"}), ("p2", {"family": "scandinavian"})]
    es = S.procedural_entries(types=["toilet", "kitchen_counter"], styles=styles)
    assert [e["id"] for e in es] == ["ours:toilet:p1", "ours:toilet:p2", "ours:kitchen_counter:p1",
                                     "ours:kitchen_counter:p2"]
    assert {e["method"] for e in es if e["type"] == "kitchen_counter"} == {"module"}
    assert {e["method"] for e in es if e["type"] == "toilet"} == {"parametric"}
    sheets = S.sheet_plan(es)
    assert [s["sheet"] for s in sheets] == ["ours-01"] and len(sheets[0]["letters"]) == 4
    idx = S.index_doc(es, sheets)
    assert idx["models"]["ours:toilet:p1"]["procedural"] and idx["models"]["ours:toilet:p1"]["type"] == "toilet"
    piece = S.procedural_piece(es[0])
    assert piece["asset"]["method"] == "parametric" and S.procedural_piece(es[2])["asset"]["method"] == "module"
    a = S.job_sha(es[0], S.SETTINGS)
    assert a != S.job_sha(dict(es[0], code_sha="other"), S.SETTINGS)
    assert "stair" not in S.procedural_types() and "toilet" in S.procedural_types()
    job = (ROOT / "scripts" / "jobs" / "library_ranking.sh").read_text()
    assert "--procedural --proc-tag" in job and "studio_results_${RANK_PROC_TAG}.json" in job
