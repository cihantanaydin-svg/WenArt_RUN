"""GPU test of the Objaverse library (``pytest -m gpu tests/gpu/test_library.py``; docs/milestone7.md §7, §9.2).

Run by the prep job after ``python -m wenart.assets.objaverse report`` (survey, thumbnails on the GPU, both judging
sessions, accept, write-catalog). ``WENART_LIBRARY`` = the library folder (default ``$WENART_RESULTS/library``),
``WENART_ASSETS`` = the assets dir whose ``models/objaverse/`` holds the accepted GLBs (default
``/workspace/assets``). Without a ``survey.json`` there the tests skip (other GPU jobs collect this folder too). No
server is needed: the tests read the files the steps wrote.

- the survey found LVIS categories and both accepted licence spellings occur (the names the session could not
  verify, docs/milestone7.md §7.1); a missing category is a warning, not a failure (its types stay parametric;
  the 3 Oct 2026 prep pod found no ``nightstand`` and no ``chest_of_drawers_(furniture)``);
- every candidate is CC0 / CC BY 4.0 with a full credit, inside the prefilter, <= 8 per type;
- the thumbnails were rendered on the GPU; every candidate has a measurement or a reason, every ready object its
  judging sheet and its thumbnail;
- both judges answered every request (current and schema-valid);
- ``accepted.json`` follows from the stored answers by the §7.2 rules, <= 6 per type;
- ``catalog_objaverse.json`` validates and merges with ``catalog.json``; every GLB in the assets cache has the
  catalogue's sha256; every entry carries its credit line; the file, the thumbnails and the report carry the
  ODC-By notice.
"""
import math
import os
import warnings
from pathlib import Path

import pytest

from wenart.assets import objaverse as OV
from wenart.furniture import catalog as C

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


def test_survey_found_lvis_categories_and_both_licence_spellings(cfg):
    surv = need(OV.SURVEY_NAME)
    assert surv["lvis"]["found"], "no LVIS category of objaverse.yaml is in the file"
    if surv["lvis"]["missing"]:
        warnings.warn(f"LVIS categories not in the file (their types stay parametric): {surv['lvis']['missing']}; "
                      f"names sharing a word: {surv['lvis'].get('near_missing')}")
    seen = surv["licence_values"]
    for name, spellings in cfg["licences"]["accept"].items():
        assert any(OV.licence_value(s) in seen for s in spellings), (
            f"no {name} spelling of objaverse.yaml occurs; values seen: {list(seen)[:20]}")
    assert surv["candidates"], "the survey found no candidate"
    assert surv["downloaded"] is True


def test_candidates_are_licensed_credited_and_inside_the_prefilter(cfg):
    surv = need(OV.SURVEY_NAME)
    pre = cfg["prefilter"]
    lo, hi = pre["face_count"]
    per_group: dict[str, int] = {}
    for c in surv["candidates"]:
        assert c["licence"] in (C.LICENCE, C.CC_BY), c["uid"]
        assert OV.classify_licence(c["licence_raw"], cfg)[0] == c["licence"], c["uid"]
        assert c["title"] and c["author"] and c["source_url"].startswith(("https://", "http://")), c["uid"]
        assert lo <= c["face_count"] <= hi, c["uid"]
        assert c["glb_bytes"] <= pre["max_glb_mb"] * 1024 * 1024, c["uid"]
        assert c["glb_info"]["textured"] or c["glb_info"]["vertex_colours"], c["uid"]
        per_group[c["group"]] = per_group.get(c["group"], 0) + 1
    for group, n in per_group.items():
        assert n <= pre["per_type_limit"] * len(group.split("|")), group


def test_thumbnails_were_rendered_on_the_gpu():
    surv = need(OV.SURVEY_NAME)
    th = need(OV.THUMBS_JSON)
    assert th["device"] in ("OPTIX", "CUDA"), f"thumbnails rendered on {th['device']}"
    assert th["blender_exit"] == 0
    assert set(th["objects"]) == {c["uid"] for c in surv["candidates"] if c.get("glb")}
    ready = 0
    for uid, rec in th["objects"].items():
        if rec["status"] != "ready":
            assert rec["code"] in OV.REASONS and rec["code"] != "not_rendered", (uid, rec.get("code"))
            continue
        ready += 1
        assert (LIBRARY / rec["sheet"]).is_file() and (LIBRARY / rec["thumb"]).is_file(), uid
        assert OV.pixels_sha256(LIBRARY / rec["sheet"]) == rec["sheet_pixels"], uid
        assert rec["unit"]["ok"] and rec["type"] in C.FURNITURE_TYPES, uid
    assert ready, "no candidate is ready for judging"
    notice = (LIBRARY / OV.THUMBS_DIR / OV.NOTICE_NAME).read_text(encoding="utf-8")
    assert "ODC Attribution License" in notice


def test_both_judges_answered_every_request():
    need(f"{OV.JUDGE_DIR}/{OV.REQUESTS_NAME}")
    status = OV.judge_status(LIBRARY)
    assert status["items"] > 0
    assert status["complete"], status["models"]


def test_accepted_follows_the_rules(cfg):
    acc = need(OV.ACCEPTED_NAME)
    th = need(OV.THUMBS_JSON)
    answers = OV.load_judgements(LIBRARY)
    assert acc["accepted"], "no Objaverse model accepted: see library_report.md"
    per_type: dict[str, int] = {}
    for dec in acc["accepted"]:
        again = OV.decide(th["objects"][dec["uid"]], answers[dec["uid"]], cfg)
        assert again["accepted"], (dec["uid"], again["failed"])
        assert (again["front_axis"], again["styles"]) == (dec["front_axis"], dec["styles"]), dec["uid"]
        per_type[dec["type"]] = per_type.get(dec["type"], 0) + 1
    assert all(n <= cfg["accept"]["per_type_max"] for n in per_type.values()), per_type
    for dec in acc["refused"]:
        if dec["code"] == "over_type_limit":
            continue
        again = OV.decide(th["objects"][dec["uid"]], answers.get(dec["uid"]) or {}, cfg)
        assert not again["accepted"] and again["code"] == dec["code"], dec["uid"]


def test_catalog_validates_merges_and_matches_the_cache(cfg):
    need(OV.ACCEPTED_NAME)
    cat = need(OV.CATALOG_NAME)
    C.validate(cat, complete=False)
    merged = C.Catalog(C.merge(OV.read_json(C.CATALOG_PATH), cat))
    assert merged.merged["models_added"] == len(cat["entries"])
    assert cat["notice"] == OV.odc_by_notice(cfg) and cat["file_licence"] == "ODC-By-1.0"
    frontless = {t for t, spec in cfg["types"].items() if spec["front"] == OV.FRONTLESS_RULE}
    per_type: dict[str, int] = {}
    for e in cat["entries"]:
        glb = ASSETS / e["glb"]
        assert glb.is_file(), f"{glb} not in the assets cache"
        assert OV.sha256_file(glb) == e["sha256_glb"], e["id"]
        info = OV.glb_info(glb)
        assert info["textured"] or info["vertex_colours"], e["id"]
        assert e["attribution"] == OV.attribution_line(e["title"], e["author"], e["source_url"], e["licence"], cfg)
        assert e["licence_url"] == cfg["licences"]["urls"][e["licence"]]
        assert e["front_axis_confidence"] == ("low" if e["type"] in frontless else "high"), e["id"]
        assert e["styles"] and isinstance(e["unit_scale"], (int, float)), e["id"]
        assert math.isfinite(e["unit_scale"]) and e["unit_scale"] > 0, e["id"]
        if e["unit_scale"] not in cfg["units"]:                        # units unknown: normalised by type (P2)
            assert e["unit_note"].startswith(OV.NORMALISED_NOTE), e["id"]
        if e["type"] in C.BED_TYPES:
            assert e["has_mattress"] is True, e["id"]
        per_type[e["type"]] = per_type.get(e["type"], 0) + 1
    assert all(n <= cfg["accept"]["per_type_max"] for n in per_type.values()), per_type


def test_report_carries_the_notice_and_every_credit(cfg):
    path = LIBRARY / OV.REPORT_NAME
    if not path.is_file():
        pytest.skip(f"{path} not found")
    text = path.read_text(encoding="utf-8")
    assert OV.odc_by_notice(cfg) in text
    cat = OV.read_json(LIBRARY / OV.CATALOG_NAME) or {"entries": []}
    for e in cat["entries"]:
        assert e["attribution"] in text, e["id"]
