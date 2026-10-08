"""CPU tests of the type filter of the two surveys (``survey --types new|T1,T2``, Milestone 10 pod L1 follow-up).

The first library pod spent its two hours on downloads of the 24 older types, which the Milestone 9 library already
covers (models in ``<assets>/models/<source>/``, thumbnails, judge answers and ``accepted.json`` in the library folder).
A filtered survey lists and downloads only the listed types and keeps the records of every other type of the earlier
survey file as they are (their GLBs may be missing on the new pod); the later steps must still see the whole library.

Covered: the filter itself (``new`` = the 14 furniture and 12 decor types, names, errors), the Objaverse and the ABO
survey with it (other types kept, nothing of them read or downloaded, a kept uid never picked again, the exit code), the
thumbnails with a record whose GLB is gone (work folder kept, work folder lost, nothing kept at all, a run cut before
it), the way from a filtered survey to a catalogue with the older and the new models (stored answers reused, GLBs from
the assets folder), and the material slots of such models (GLB from the assets folder).
"""
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from test_objaverse import Mirror, box, fake_runner, quiet, run_judges, sofa_points
from wenart.assets import abo as A
from wenart.assets import objaverse as OV
from wenart.assets import recolour as RC

CFG = OV.load_config()
ACFG = A.load_config()
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "abo"
NEW_FURNITURE = ("sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib",
                 "bunk_bed", "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet")
NEW_DECOR = ("curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock", "sculpture", "plant_large",
             "pendant_light", "ceiling_light")


class CountingHub(OV.LocalHub):
    """The local mirror, remembering which files were asked for."""

    def __init__(self, root):
        super().__init__(root)
        self.asked: list[str] = []

    def path(self, filename):
        self.asked.append(filename)
        return super().path(filename)


# --------------------------------------------------------------------------
# The filter
# --------------------------------------------------------------------------

def test_new_is_the_14_furniture_and_12_decor_types_of_milestone_10():
    got = OV.parse_type_filter("new", CFG)
    assert got == list(NEW_FURNITURE + NEW_DECOR) and len(got) == 26 and OV.new_types(CFG) == got
    assert set(got) == set(A.new_types(ACFG))                     # the ABO config names the same types
    from wenart import building as B
    schema = B.load_schema()["$defs"]
    assert set(NEW_FURNITURE) <= set(schema["furniture"]["properties"]["type"]["enum"])
    assert set(NEW_DECOR) <= set(schema["decor"]["properties"]["type"]["enum"])


def test_the_filter_takes_names_new_all_or_nothing_and_refuses_unknown_names():
    assert OV.parse_type_filter(None, CFG) is None and OV.parse_type_filter("", CFG) is None
    assert OV.parse_type_filter("all", CFG) is None and OV.parse_type_filter("sofa,all", CFG) is None
    assert OV.parse_type_filter("sofa_corner,crib", CFG) == ["sofa_corner", "crib"]
    assert OV.parse_type_filter("crib crib, sofa", CFG) == ["crib", "sofa"]                 # repeats once
    assert OV.parse_type_filter(["sofa", "new"], CFG)[0] == "sofa" and len(OV.parse_type_filter("sofa,new", CFG)) == 27
    with pytest.raises(OV.UsageError, match="'sofaa' is no furniture or decor type"):
        OV.parse_type_filter("sofa,sofaa", CFG)
    with pytest.raises(OV.UsageError):
        OV.parse_type_filter("unknown", CFG)                                                  # not a library type


def test_a_wrong_type_name_is_a_usage_error_of_both_clis(tmp_path, capsys):
    out = tmp_path / "lib"
    assert OV.main(["survey", "--out", str(out), "--mirror", str(tmp_path), "--types", "sofaa"]) == OV.EXIT_SERVER
    assert "no furniture or decor type" in capsys.readouterr().err
    assert A.main(["survey", "--out", str(out), "--metadata", str(FIXTURE), "--no-download", "--types", "sofaa"]) \
        == A.EXIT_USAGE
    assert "no furniture or decor type" in capsys.readouterr().err
    assert not (out / OV.SURVEY_NAME).exists()


# --------------------------------------------------------------------------
# The Objaverse survey
# --------------------------------------------------------------------------

def old_and_new_mirror(tmp_path):
    """A mirror with two older types (a sofa, a dining table) and, added after the first survey, four of the new ones."""
    m = Mirror(tmp_path / "mirror")
    old = {"sofa": m.add("sofa", likes=9, name="Oak Sofa"), "table": m.add("dining_table", likes=8, name="Table")}
    return m, old


def add_new(m):
    return {"ottoman": m.add("ottoman", likes=5, name="Velvet Pouf"),
            "crib": m.add("crib", likes=4, name="White Crib", textured=False),
            "corner": m.add("sofa", likes=3, name="Big Sectional Couch"),
            "candle": m.add("candle", likes=1, name="Pillar candle", textured=False, faces=700)}


def test_a_filtered_objaverse_survey_lists_only_its_types_and_keeps_the_others(tmp_path):
    m, old = old_and_new_mirror(tmp_path)
    out = tmp_path / "lib"
    full = OV.survey(m.write(), out, CFG, log=quiet)
    assert {c["uid"] for c in full["candidates"]} == set(old.values()) and "types" not in full
    new = add_new(m)
    for uid in old.values():                                    # the new pod has no cache of the older models
        (m.root / "glbs" / "000-000" / f"{uid}.glb").unlink()
    m.write()
    hub = CountingHub(m.root)
    doc = OV.survey(hub, out, CFG, log=quiet, types=OV.parse_type_filter("new", CFG))
    by_uid = {c["uid"]: c for c in doc["candidates"]}
    assert set(by_uid) == set(old.values()) | {new["ottoman"], new["crib"], new["corner"], new["candle"]}
    assert doc["types"] == sorted(OV.new_types(CFG)) and doc["candidates_new"] == 4
    assert doc["carried"]["candidates"] == 2 and doc["carried"]["generated_utc"] == full["generated_utc"]
    for key in ("sofa", "table"):                               # kept exactly as the earlier survey has them
        assert by_uid[old[key]] == next(c for c in full["candidates"] if c["uid"] == old[key])
    assert by_uid[new["corner"]]["group"] == "sofa_corner" and by_uid[new["candle"]]["kind"] == "decor"
    assert not [f for f in hub.asked if any(u in f for u in old.values()) and f.endswith(".glb")]
    assert all(g in doc["counts"] for g in ("sofa", "table_dining")) and "ottoman" in doc["counts"]
    assert OV.read_json(out / OV.SURVEY_NAME)["candidates"] == doc["candidates"]
    assert OV.load_candidates(out)                                                   # the library steps read it


def test_a_filter_of_one_old_type_replaces_only_that_type(tmp_path):
    m, old = old_and_new_mirror(tmp_path)
    out = tmp_path / "lib"
    OV.survey(m.write(), out, CFG, log=quiet)
    extra = m.add("sofa", likes=2, name="Grey Sofa")
    doc = OV.survey(m.write(), out, CFG, log=quiet, types=["sofa"])
    got = {c["uid"]: c["group"] for c in doc["candidates"]}
    assert got == {old["sofa"]: "sofa", extra: "sofa", old["table"]: "table_dining"}
    assert doc["candidates_new"] == 2 and doc["carried"]["candidates"] == 1        # the table stays, the sofas are new


def test_a_uid_the_earlier_survey_keeps_is_not_picked_again_for_a_listed_type(tmp_path):
    """Milestone 9 surveyed a sectional couch as a sofa; the filtered survey of the corner sofas must not move it."""
    m = Mirror(tmp_path / "mirror")
    couch = m.add("sofa", likes=9, name="Big Sectional Couch")
    out = tmp_path / "lib"
    m9 = {k: v for k, v in CFG.items()}
    m9["categories"] = {k: v for k, v in CFG["categories"].items() if k != "sofa_corner"}
    first = OV.survey(m.write(), out, m9, log=quiet)
    assert first["candidates"][0]["group"] == "sofa"
    other = m.add("sofa", likes=1, name="Sectional Sofa")
    doc = OV.survey(m.write(), out, CFG, log=quiet, types=["sofa_corner"])
    got = {c["uid"]: c["group"] for c in doc["candidates"]}
    assert got == {couch: "sofa", other: "sofa_corner"} and doc["candidates_new"] == 1
    # the same filter again: nothing is new, the kept record is still there once
    again = OV.survey(m.write(), out, CFG, log=quiet, types=["sofa_corner"])
    assert [c["uid"] for c in again["candidates"]].count(couch) == 1 and len(again["candidates"]) == 2


def test_a_filtered_survey_without_an_earlier_one_lists_only_its_types_and_fails_without_news(tmp_path, capsys):
    m, old = old_and_new_mirror(tmp_path)
    new = add_new(m)
    out = tmp_path / "lib"
    doc = OV.survey(m.write(), out, CFG, log=quiet, types=["ottoman", "crib"])
    assert {c["uid"] for c in doc["candidates"]} == {new["ottoman"], new["crib"]} and doc["carried"]["candidates"] == 0
    rc = OV.main(["survey", "--mirror", str(m.root), "--out", str(out), "--types", "bench"])
    assert rc == OV.EXIT_FAIL                                  # nothing of the listed type: the earlier ones do not count
    assert "0 of the listed types, 2 kept from the earlier survey" in capsys.readouterr().out
    rc = OV.main(["survey", "--mirror", str(m.root), "--out", str(out), "--types", "ottoman"])
    assert rc == OV.EXIT_OK


# --------------------------------------------------------------------------
# The ABO survey
# --------------------------------------------------------------------------

def test_a_filtered_abo_survey_lists_only_its_types_and_keeps_the_others(tmp_path):
    out = tmp_path / "lib"
    meta = A.Metadata(ACFG, FIXTURE, tmp_path / "cache", download_missing=False)
    full = A.survey(meta, out, ACFG, download_glbs=False, log=quiet)
    by_type = {}
    for c in full["candidates"]:
        by_type.setdefault(c["group"], []).append(c["uid"])
    assert "sofa_corner" in by_type and "office_chair" in by_type and "sofa" in by_type and len(full["candidates"]) == 31
    doc = A.survey(meta, out, ACFG, download_glbs=False, log=quiet, types=["sofa_corner", "office_chair"])
    assert {c["group"] for c in doc["candidates"]} == set(by_type) and len(doc["candidates"]) == 31
    assert doc["types"] == ["office_chair", "sofa_corner"] and doc["candidates_new"] == 2
    assert doc["carried"]["candidates"] == 29 and doc["carried"]["generated_utc"] == full["generated_utc"]
    kept = {c["uid"]: c for c in doc["candidates"]}
    for c in full["candidates"]:
        assert kept[c["uid"]] == c
    assert set(doc["counts"]) == set(full["counts"]) and doc["rule_counts"] == full["rule_counts"]
    # only the listed types are mapped when there is no earlier survey
    fresh = A.survey(meta, tmp_path / "other", ACFG, download_glbs=False, log=quiet, types=["sofa_corner"])
    assert [c["group"] for c in fresh["candidates"]] == ["sofa_corner"] and set(fresh["counts"]) == {"sofa_corner"}
    assert fresh["carried"]["candidates"] == 0


def test_a_filtered_abo_survey_downloads_only_the_models_of_its_types(tmp_path):
    from test_objaverse import make_glb
    meta = A.Metadata(ACFG, FIXTURE, tmp_path / "cache", download_missing=False)
    fetched: list[str] = []

    def fetcher(url, dest, _max_bytes):
        fetched.append(url)
        make_glb(Path(dest))

    kw = dict(download_glbs=True, cache=tmp_path / "cache", fetcher=fetcher, log=quiet, workers=1)
    full = A.survey(meta, tmp_path / "all", ACFG, **kw)
    everything = len(fetched)
    assert everything == len(full["candidates"]) == 31
    fetched.clear()
    doc = A.survey(meta, tmp_path / "some", ACFG, types=["sofa_corner", "office_chair"], **kw)
    assert len(fetched) == 0 and doc["candidates_new"] == 2          # both are in the cache of the full survey already
    shutil.rmtree(tmp_path / "cache" / "original")
    doc = A.survey(meta, tmp_path / "some", ACFG, types=["sofa_corner", "office_chair"], **kw)
    assert len(fetched) == 2 and len(doc["candidates"]) == 2 and all("glb" in c for c in doc["candidates"])


def test_a_kept_abo_model_is_not_picked_again_and_the_cli_exit_code_counts_the_new_ones(tmp_path, capsys):
    out = tmp_path / "lib"
    args = ["survey", "--metadata", str(FIXTURE), "--no-download", "--out", str(out)]
    assert A.main(args) == A.EXIT_OK
    doc = OV.read_json(out / A.SURVEY_NAME)
    chair = next(c for c in doc["candidates"] if c["group"] == "office_chair")
    chair["group"], chair["types"] = "armchair", ["armchair"]                    # what Milestone 9 called it
    OV.write_json(out / A.SURVEY_NAME, doc)
    capsys.readouterr()
    assert A.main(args + ["--types", "office_chair"]) == A.EXIT_FAIL            # the fixture's only office chair is kept
    assert "0 of the listed types, 31 kept from the earlier survey" in capsys.readouterr().out
    again = OV.read_json(out / A.SURVEY_NAME)
    assert [c["uid"] for c in again["candidates"]].count(chair["uid"]) == 1 and len(again["candidates"]) == 31
    assert A.main(args + ["--types", "sofa_corner"]) == A.EXIT_OK


# --------------------------------------------------------------------------
# From a filtered survey to the catalogue
# --------------------------------------------------------------------------

def phase_one(tmp_path):
    """The Milestone 9 library: a sofa and a dining table surveyed, thumbnailed, judged, accepted, in the catalogue (the
    GLBs copied to the assets folder)."""
    m, old = old_and_new_mirror(tmp_path)
    out, assets, work = tmp_path / "lib", tmp_path / "assets", tmp_path / "work"
    OV.survey(m.write(), out, CFG, log=quiet)
    shapes = {old["sofa"]: (sofa_points(), []), old["table"]: (box(-0.8, -0.45, 0, 0.8, 0.45, 0.75), [])}
    doc, rc = OV.thumbnails(out, work, CFG, runner=fake_runner(shapes, []), log=quiet)
    assert rc == 0 and all(o["status"] == "ready" for o in doc["objects"].values())
    assert run_judges(SimpleNamespace(out=out, doc=doc))["qwen"] == 0
    acc = OV.accept(out, CFG)
    assert {d["uid"] for d in acc["accepted"]} == set(old.values())
    cat = OV.write_catalog(out, assets, CFG, log=quiet)
    assert {e["id"] for e in cat["entries"]} == {f"objaverse_{u}" for u in old.values()}
    return SimpleNamespace(m=m, old=old, out=out, assets=assets, work=work, shapes=shapes, cat=cat)


@pytest.mark.parametrize("keep_work", [True, False], ids=["work folder kept", "work folder lost"])
def test_the_catalogue_has_the_older_and_the_new_models_after_a_filtered_survey(tmp_path, keep_work):
    lib = phase_one(tmp_path)
    new = add_new(lib.m)
    for uid in lib.old.values():                                              # a new pod: no survey cache
        (lib.m.root / "glbs" / "000-000" / f"{uid}.glb").unlink()
    lib.m.write()
    hub = CountingHub(lib.m.root)
    doc = OV.survey(hub, lib.out, CFG, log=quiet, types=OV.parse_type_filter("new", CFG))
    assert doc["candidates_new"] == 4 and doc["carried"]["candidates"] == 2
    if not keep_work:
        shutil.rmtree(lib.work)
    shapes = {new["ottoman"]: (box(-0.4, -0.3, 0, 0.4, 0.3, 0.45), []), new["crib"]: (box(-0.35, -0.65, 0, 0.35, 0.65, 0.95), []),
              new["corner"]: (box(-1.4, -0.8, 0, 1.4, 0.8, 0.85) + box(-1.4, 0.3, 0.85, 1.4, 0.8, 1.0), []),
              new["candle"]: (box(-0.05, -0.05, 0, 0.05, 0.05, 0.2), [])}
    calls: list = []
    thumbs, rc = OV.thumbnails(lib.out, lib.work, CFG, runner=fake_runner(shapes, calls), log=quiet)
    assert rc == 0
    assert set(calls[0]) == set(new.values())                                # nothing of the older models is rendered
    objs = thumbs["objects"]
    assert all(objs[u]["status"] == "ready" for u in list(lib.old.values()) + list(new.values())), \
        {u: objs[u].get("code") for u in objs}
    assert thumbs["carried"] == (0 if keep_work else 2)
    assert all(bool(objs[u].get("carried")) == (not keep_work) for u in lib.old.values())
    # the stored answers of the older models are current: only the new ones are asked
    answered = OV.judge_requests(lib.out, CFG)
    assert len(answered["items"]) == 6
    asked: dict = {}
    rcs = run_judges(SimpleNamespace(out=lib.out, doc=thumbs),
                     clients={k: ask_like_the_geometry(thumbs, asked, k, crib=new["crib"]) for k in OV.MODEL_KEYS})
    assert rcs["qwen"] == 0 and rcs["glm"] == 0
    assert set(asked["qwen"]) == set(new.values()) and set(asked["glm"]) == set(new.values())
    acc = OV.accept(lib.out, CFG)
    assert {d["uid"] for d in acc["accepted"]} == set(lib.old.values()) | set(new.values()), acc["refused"]
    cat = OV.write_catalog(lib.out, lib.assets, CFG, log=quiet)
    assert cat["refused_at_write"] == []
    ids = {e["id"] for e in cat["entries"]}
    assert ids == {f"objaverse_{u}" for u in list(lib.old.values()) + [new["ottoman"], new["crib"], new["corner"]]}
    assert [e["decor_type"] for e in cat["decor"]] == ["candle"]
    for before in lib.cat["entries"]:                                           # the older entries are unchanged
        assert next(e for e in cat["entries"] if e["id"] == before["id"]) == before
    for uid in lib.old.values():
        assert (lib.assets / "models" / "objaverse" / f"{uid}.glb").is_file()
    assert "Oak Sofa" in OV.report(lib.out, CFG)
    # the material slots: the older models' GLBs come from the assets folder, the new ones from the survey cache
    ready = {m_["uid"]: m_ for m_ in RC.select_models(lib.out, lib.assets, scope="ready")}
    for uid in lib.old.values():
        assert ready[uid]["glb"] == str(lib.assets / "models" / "objaverse" / f"{uid}.glb")
    assert ready[new["ottoman"]]["glb"] == str(lib.m.root / "glbs" / "000-000" / f"{new['ottoman']}.glb")
    assert all(m_["glb"] for m_ in ready.values())


def ask_like_the_geometry(thumbs: dict, asked: dict, key: str, crib: str):
    """A judge that names the geometric front (the crib's front the judges agree on: view 0) and records its asks."""
    objs = thumbs["objects"]

    def fn(images, _prompt):
        from test_objaverse import answer
        from test_objaverse_m10 import decor_answer
        uid = Path(images[0]).stem
        asked.setdefault(key, []).append(uid)
        if objs[uid]["kind"] == "decor":
            return decor_answer(front=None)
        geo = objs[uid].get("geometric_front")
        front = OV.VIEW_SIDES.index(geo) if geo else (0 if uid == crib else None)
        return answer(front=front, styles=("modern", "scandinavian") if key == "qwen" else ("scandinavian", "neutral"))
    return fn


# --------------------------------------------------------------------------
# Thumbnails of records whose GLB is gone
# --------------------------------------------------------------------------

def test_a_record_without_glb_work_or_earlier_object_is_refused_glb_missing_not_a_failure(tmp_path):
    lib = phase_one(tmp_path)
    for uid in lib.old.values():
        (lib.m.root / "glbs" / "000-000" / f"{uid}.glb").unlink()
    shutil.rmtree(lib.work)
    (lib.out / OV.THUMBS_JSON).unlink()                                         # nothing earlier to keep
    calls: list = []
    doc, rc = OV.thumbnails(lib.out, lib.work, CFG, runner=fake_runner(lib.shapes, calls), log=quiet)
    assert rc == 0 and calls == []                                              # no Blender job, no failure
    assert {o["code"] for o in doc["objects"].values()} == {"glb_missing"} and doc["counts"] == {"glb_missing": 2}
    assert "survey again" in OV.reason_text("glb_missing")


def test_an_earlier_object_is_kept_only_when_it_still_fits(tmp_path):
    lib = phase_one(tmp_path)
    for uid in lib.old.values():
        (lib.m.root / "glbs" / "000-000" / f"{uid}.glb").unlink()
    shutil.rmtree(lib.work)
    sofa = lib.old["sofa"]
    cand = next(c for c in OV.load_candidates(lib.out) if c["uid"] == sofa)
    prev = OV.read_json(lib.out / OV.THUMBS_JSON)["objects"][sofa]
    assert OV.carried_object(prev, cand, lib.out)["carried"] is True
    assert OV.carried_object(dict(prev, glb_sha256="0" * 64), cand, lib.out) is None            # another GLB
    assert OV.carried_object(dict(prev, glb_sha256=cand["glb_sha256"]), cand, lib.out) is not None
    (lib.out / prev["thumb"]).unlink()
    assert OV.carried_object(prev, cand, lib.out) is None                                       # its thumbnail is gone
    assert OV.carried_object(None, cand, lib.out) is None
    for code in OV.TRANSIENT_CODES:                                  # a refusal of a step that did not finish
        assert OV.carried_object({"status": "refused", "code": code}, cand, lib.out) is None
    assert OV.carried_object({"status": "refused", "code": "unit_none", "detail": "x"}, cand, lib.out)["carried"]
    doc, rc = OV.thumbnails(lib.out, lib.work, CFG, runner=fake_runner(lib.shapes, []), log=quiet)
    assert rc == 0 and doc["objects"][sofa]["code"] == "glb_missing"             # its thumbnail is gone: nothing to keep
    assert doc["objects"][lib.old["table"]]["status"] == "ready" and doc["objects"][lib.old["table"]]["carried"]


def test_a_run_cut_before_a_model_keeps_what_the_earlier_run_made_of_it(tmp_path):
    lib = phase_one(tmp_path)
    shutil.rmtree(lib.work)                                   # the GLBs are here, the measurements are not

    def cut(_blender, jobs_path, _log, _timeout):                # Blender stopped before it measured anything
        return OV.EXIT_DEADLINE
    doc, rc = OV.thumbnails(lib.out, lib.work, CFG, runner=cut, log=quiet)
    assert rc == OV.EXIT_DEADLINE
    assert all(o["status"] == "ready" and o["carried"] for o in doc["objects"].values())
    assert doc["counts"] == {"ready": 2} and doc["carried"] == 2


# --------------------------------------------------------------------------
# The material slots of models whose GLB is only in the assets folder
# --------------------------------------------------------------------------

def test_recolour_takes_the_glb_from_the_assets_folder_when_the_survey_cache_lacks_it(tmp_path):
    lib = phase_one(tmp_path)
    for uid in lib.old.values():
        (lib.m.root / "glbs" / "000-000" / f"{uid}.glb").unlink()
    sofa, table = lib.old["sofa"], lib.old["table"]
    asset = lib.assets / "models" / "objaverse" / f"{sofa}.glb"
    for scope in ("ready", "accepted"):
        got = {m["uid"]: m for m in RC.select_models(lib.out, lib.assets, scope=scope)}
        assert got[sofa]["glb"] == str(asset) and got[table]["glb"]
        assert got[sofa]["glb_sha256"] == next(c for c in OV.load_candidates(lib.out) if c["uid"] == sofa)["glb_sha256"]
        # without the assets folder there is nothing to read; a copy with another sha256 is not taken
        assert {m["uid"]: m["glb"] for m in RC.select_models(lib.out, None, scope=scope)} == {sofa: None, table: None}
    asset.write_bytes(asset.read_bytes() + b"\0")
    got = {m["uid"]: m for m in RC.select_models(lib.out, lib.assets, scope="ready")}
    assert got[sofa]["glb"] is None and got[table]["glb"]
    # `slots` then lists the model with its status instead of failing
    doc, rc = RC.slots(lib.out, assets=lib.assets, work=tmp_path / "rw", scope="ready",
                       runner=lambda *a, **k: 0, blender="blender", log=quiet)
    assert {m["uid"]: m["status"] for m in doc["models"]}[sofa] == "no_glb"
