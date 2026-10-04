"""GPU test of the furniture library of every source (``pytest -m gpu tests/gpu/test_library.py``; docs/milestone7.md
§7, §9.2; docs/milestone8.md §2, §6, §7).

Run by the prep job after its ``library`` step (the ABO and Objaverse surveys, the generation on the L2 pod,
thumbnails on the GPU, both judging sessions, accept, write-catalog, report, ATTRIBUTION.md). ``WENART_LIBRARY`` =
the library folder (default ``$WENART_RESULTS/library``), ``WENART_ASSETS`` = the assets dir whose
``models/<source>/`` holds the accepted GLBs (default ``/workspace/assets``). Without a survey file there the tests
skip (other GPU jobs collect this folder too). No server is needed: the tests read the files the steps wrote.

- sources present: the ABO and Objaverse surveys found candidates (the generated survey is there when the L2 pod
  generated); ABO candidates are CC BY 4.0, units known, with the documented front and the credit line; Objaverse
  candidates carry every licence with its flag and a full credit; <= 24 per type and source;
- the thumbnails were rendered on the GPU; every candidate has a measurement or a reason; every bed has its deck
  measurement; every ready object its judging sheet and thumbnail;
- both judges answered every request (current and schema-valid);
- ``accepted.json`` follows from the stored answers by the rules (<= 12 per furniture type, <= 16 per decor type,
  <= 3 per type and style family);
- ``catalog_library.json`` validates and merges with ``catalog.json``; every GLB in the assets cache has the
  catalogue's sha256; the catalogue holds ABO models; licences and flags agree; bed frames have decks;
- attribution complete: every model's credit line is in ``ATTRIBUTION.md`` and the report, with the notices of
  the sources present.
"""
import math
import os
import warnings
from pathlib import Path

import pytest

from wenart.assets import abo as ABO
from wenart.assets import objaverse as OV
from wenart.furniture import catalog as C
from wenart.run import copy as CP

pytestmark = pytest.mark.gpu
RESULTS = Path(os.environ.get("WENART_RESULTS", "/tmp/wenart-results"))
LIBRARY = Path(os.environ.get("WENART_LIBRARY") or RESULTS / "library")
ASSETS = Path(os.environ.get("WENART_ASSETS", "/workspace/assets"))


def need(name: str) -> dict:
    doc = OV.read_json(LIBRARY / name)
    if doc is None:
        pytest.skip(f"{LIBRARY / name} not found (written by the prep job's library steps)")
    return doc


@pytest.fixture(scope="module")
def cfg():
    return OV.load_config()


@pytest.fixture(scope="module")
def surveys():
    docs = OV.load_surveys(LIBRARY)
    if not docs:
        pytest.skip(f"no survey file in {LIBRARY} (written by the prep job's library steps)")
    return docs


def test_both_real_sources_are_present(surveys):
    """docs/milestone8.md §1: ABO first, Objaverse; both surveys ran and downloaded candidates."""
    assert "abo" in surveys and "objaverse" in surveys, f"surveys present: {sorted(surveys)}"
    for source in ("abo", "objaverse"):
        assert surveys[source]["candidates"], f"the {source} survey found no candidate"
        assert surveys[source]["downloaded"] is True, source
    if "generated" not in surveys:
        warnings.warn("no survey_generated.json: no generation in this library (the L1 pod, or a failed L2 step)")


def test_objaverse_survey_found_lvis_categories_and_both_licence_spellings(cfg, surveys):
    surv = surveys.get("objaverse") or pytest.skip("no Objaverse survey")
    assert surv["lvis"]["found"], "no LVIS category of objaverse.yaml is in the file"
    if surv["lvis"]["missing"]:
        warnings.warn(f"LVIS categories not in the file (their types stay parametric): {surv['lvis']['missing']}; "
                      f"names sharing a word: {surv['lvis'].get('near_missing')}")
    seen = surv["licence_values"]
    for name, spellings in cfg["licences"]["accept"].items():
        assert any(OV.licence_value(s) in seen for s in spellings), (
            f"no {name} spelling of objaverse.yaml occurs; values seen: {list(seen)[:20]}")


def test_objaverse_candidates_are_credited_flagged_and_inside_the_prefilter(cfg, surveys):
    surv = surveys.get("objaverse") or pytest.skip("no Objaverse survey")
    pre = cfg["prefilter"]
    lo, hi = pre["face_count"]
    per_group: dict[str, int] = {}
    for c in surv["candidates"]:
        licence, flag, _ = OV.classify_licence(c["licence_raw"] if c["licence_raw"] != "(none)" else None, cfg)
        assert (c["licence"], c["licence_flag"]) == (licence, flag), c["uid"]
        assert C.licence_flag_of(c["licence"]) == c["licence_flag"], c["uid"]
        assert c["title"] and c["author"] and c["source_url"].startswith(("https://", "http://")), c["uid"]
        assert c["attribution"] == OV.attribution_line(c["title"], c["author"], c["source_url"], c["licence"], cfg)
        assert lo <= c["face_count"] <= hi, c["uid"]
        assert c["glb_bytes"] <= pre["max_glb_mb"] * 1024 * 1024, c["uid"]
        assert c["glb_info"]["textured"] or c["glb_info"]["vertex_colours"], c["uid"]
        per_group[c["group"]] = per_group.get(c["group"], 0) + 1
    for group, n in per_group.items():
        assert n <= pre["per_type_limit"] * len(group.split("|")), group


def test_abo_candidates_are_cc_by_with_known_units_and_the_documented_front(surveys):
    surv = surveys.get("abo") or pytest.skip("no ABO survey")
    acfg = ABO.load_config()
    assert surv["metadata"]["readme_checked"] is True, "3dmodels/README.md no longer states CC BY 4.0 / Amazon.com"
    per_type: dict[str, int] = {}
    for c in surv["candidates"]:
        assert c["uid"] == f"abo_{c['abo_3dmodel_id']}" and c["source"] == "abo", c["uid"]
        assert c["licence"] == C.CC_BY and c["licence_flag"] is None and c["author"] == "Amazon.com", c["uid"]
        assert c["attribution"] == ABO.attribution(c["title"], acfg), c["uid"]
        assert c["units_known"] is True and c["front_documented"] == "-Y", c["uid"]
        assert Path(c["glb"]).is_file() and c["glb_bytes"] <= acfg["survey"]["max_glb_mb"] * 1024 * 1024, c["uid"]
        assert c["glb_info"]["textured"] or c["glb_info"]["vertex_colours"], c["uid"]
        assert c["kind"] == ("decor" if c["group"] in C.DECOR_TYPES else "furniture"), c["uid"]
        per_type[c["group"]] = per_type.get(c["group"], 0) + 1
    assert all(n <= acfg["survey"]["per_type_limit"] for n in per_type.values()), per_type


def test_thumbnails_were_rendered_on_the_gpu_with_decks_for_beds(surveys):
    th = need(OV.THUMBS_JSON)
    assert th["device"] in ("OPTIX", "CUDA"), f"thumbnails rendered on {th['device']}"
    assert th["blender_exit"] == 0
    cands = OV.load_candidates(LIBRARY)
    assert set(th["objects"]) == {c["uid"] for c in cands if c.get("glb")}
    ready = 0
    for uid, rec in th["objects"].items():
        if rec["status"] != "ready":
            assert rec["code"] in OV.REASONS and rec["code"] != "not_rendered", (uid, rec.get("code"))
            continue
        ready += 1
        assert (LIBRARY / rec["sheet"]).is_file() and (LIBRARY / rec["thumb"]).is_file(), uid
        assert OV.pixels_sha256(LIBRARY / rec["sheet"]) == rec["sheet_pixels"], uid
        assert rec["unit"]["ok"], uid
        assert rec["type"] in C.FURNITURE_TYPES or rec["type"] in C.DECOR_TYPES, uid
        if rec["units_known"]:
            assert rec["unit"]["scale"] == 1.0 and rec["unit"].get("known"), uid
        if rec["type"] in C.BED_TYPES:
            assert "deck" in rec and len(rec["deck"]["hits_raw"]) == 5, uid
    assert ready, "no candidate is ready for judging"
    notice = (LIBRARY / OV.THUMBS_DIR / OV.NOTICE_NAME).read_text(encoding="utf-8")
    for text in OV.source_notices(sorted({o["source"] for o in th["objects"].values()}, key=OV.SOURCE_ORDER.index)):
        assert text in notice


def test_both_judges_answered_every_request():
    need(f"{OV.JUDGE_DIR}/{OV.REQUESTS_NAME}")
    status = OV.judge_status(LIBRARY)
    assert status["items"] > 0
    assert status["complete"], status["models"]


def test_accepted_follows_the_rules(cfg):
    acc = need(OV.ACCEPTED_NAME)
    th = need(OV.THUMBS_JSON)
    answers = OV.load_judgements(LIBRARY)
    assert acc["accepted"], "no library model accepted: see library_report.md"
    per_type: dict[tuple, int] = {}
    per_family: dict[tuple, int] = {}
    for dec in acc["accepted"]:
        again = OV.decide(th["objects"][dec["uid"]], answers[dec["uid"]], cfg)
        assert again["accepted"], (dec["uid"], again["failed"])
        assert (again["front_axis"], again["styles"]) == (dec["front_axis"], dec["styles"]), dec["uid"]
        per_type[(dec["kind"], dec["type"])] = per_type.get((dec["kind"], dec["type"]), 0) + 1
        for f in dec["styles"]:
            per_family[(dec["type"], f)] = per_family.get((dec["type"], f), 0) + 1
    for (kind, ftype), n in per_type.items():
        limit = cfg["accept"]["decor_per_type_max" if kind == "decor" else "per_type_max"]
        assert n <= limit, (ftype, n)
    for dec in acc["refused"]:
        if dec["code"] in ("over_type_limit", "over_style_limit"):
            continue
        again = OV.decide(th["objects"][dec["uid"]], answers.get(dec["uid"]) or {}, cfg)
        assert not again["accepted"] and again["code"] == dec["code"], dec["uid"]


def test_catalog_validates_merges_and_matches_the_cache(cfg):
    need(OV.ACCEPTED_NAME)
    cat = need(OV.CATALOG_NAME)
    C.validate(cat, complete=False)
    merged = C.Catalog(C.merge(OV.read_json(C.CATALOG_PATH), cat))
    assert merged.merged["models_added"] == len(cat["entries"])
    assert "abo" in cat["sources"], f"no ABO model in the catalogue (sources {cat['sources']})"
    if "objaverse" not in cat["sources"]:
        warnings.warn("no Objaverse model in the catalogue: see library_report.md")
    frontless = {t for t, spec in cfg["types"].items() if spec["front"] == OV.FRONTLESS_RULE}
    for e in cat["entries"] + cat.get("decor", []):
        glb = ASSETS / e["glb"]
        assert e["glb"] == f"models/{e['source']}/{e['uid']}.glb", e["id"]
        assert glb.is_file(), f"{glb} not in the assets cache"
        assert OV.sha256_file(glb) == e["sha256_glb"], e["id"]
        info = OV.glb_info(glb)
        assert info["textured"] or info["vertex_colours"], e["id"]
        assert e.get("licence_flag") == C.licence_flag_of(e["licence"]), e["id"]
        own = e.get("decor_type") or e["type"]
        assert e["front_axis_confidence"] == ("low" if own in frontless else "high"), e["id"]
        assert e["styles"] and isinstance(e["unit_scale"], (int, float)), e["id"]
        assert math.isfinite(e["unit_scale"]) and e["unit_scale"] > 0, e["id"]
        if e["source"] == "abo":
            assert e["unit_scale"] == 1.0 and e["units_known"] and e["licence"] == C.CC_BY, e["id"]
        elif e["unit_scale"] not in cfg["units"]:                     # units unknown: normalised by type (P2)
            assert e["unit_note"].startswith(OV.NORMALISED_NOTE), e["id"]
        if e["type"] in C.BED_TYPES:
            assert C.bed_usable(e), e["id"]


def test_bed_frames_have_decks(cfg):
    """docs/milestone8.md §2: a bed without a mattress is accepted only as a bed frame with a measured deck (at least
    min_hits of the 5 rays, inside the deck range); the builder puts the bedding on it."""
    cat = need(OV.CATALOG_NAME)
    th = need(OV.THUMBS_JSON)
    lo, hi = cfg["bed_frame"]["deck_range_m"]
    frames = [e for e in cat["entries"] if e.get("bed_frame")]
    for e in frames:
        assert e["has_mattress"] is False and lo <= e["deck_height_m"] <= hi, e["id"]
        deck = th["objects"][e["uid"]]["deck"]
        assert deck["hits"] >= cfg["bed_frame"]["min_hits"], e["id"]
        assert abs(th["objects"][e["uid"]]["deck_height_m"] - e["deck_height_m"]) < 1e-6, e["id"]
    for e in cat["entries"]:
        if e["type"] in C.BED_TYPES and not e.get("bed_frame"):
            assert e["has_mattress"] is True, e["id"]
    if not frames:
        warnings.warn("no bed frame in the catalogue")


def test_attribution_is_complete(cfg):
    """Every model's credit line (and licence flag) is in ATTRIBUTION.md and the report, with the notices of the
    sources present."""
    cat = need(OV.CATALOG_NAME)
    path = LIBRARY / CP.ATTRIBUTION
    assert path.is_file(), f"{path} not written"
    text = path.read_text(encoding="utf-8")
    report = (LIBRARY / OV.REPORT_NAME).read_text(encoding="utf-8")
    for notice in OV.source_notices(cat["sources"], cfg):
        assert notice in text and notice in report
    for e in cat["entries"] + cat.get("decor", []):
        assert e["attribution"] and e["attribution"] in text and e["attribution"] in report, e["id"]
        if e.get("licence_flag"):
            assert f"{e['attribution']} [licence flag: {e['licence_flag']}]" in text, e["id"]
        if e["source"] in ("objaverse", "abo") and e["licence"] != C.LICENCE:
            assert all(str(e.get(k) or "").strip() for k in C.CC_BY_FIELDS), e["id"]
