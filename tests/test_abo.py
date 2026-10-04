"""CPU tests of the ABO library source (docs/milestone8.md §2, §7: mapping table, dedup, style round robin, size
filter, record shape, credit line, no download).

The canned metadata in ``tests/fixtures/abo/`` are 38 real listings (trimmed) and their rows of
``3dmodels.csv.gz`` (one left out: ``no_model_row``), with the README's licence and attribution sections; no network.
"""
import copy
import gzip
import json
import shutil
from pathlib import Path

import pytest

from test_objaverse import Mirror, make_glb, quiet
from wenart.assets import abo as A
from wenart.assets import objaverse as OV
from wenart.furniture import catalog as C

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "abo"
CFG = A.load_config()
OCFG = OV.load_config()
INDEX = "https://amazon-berkeley-objects.s3.amazonaws.com/index.html"


def run_survey(tmp_path, cfg=None, download=False, fetcher=None, cache=None):
    meta = A.Metadata(cfg or CFG, FIXTURE, download_missing=False)
    return A.survey(meta, tmp_path / "lib", cfg or CFG, OCFG, download_glbs=download, cache=cache or tmp_path / "abo",
                    fetcher=fetcher, workers=2, log=quiet)


@pytest.fixture(scope="module")
def surveyed(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("abo")
    return run_survey(tmp)


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

def test_config_follows_the_spec():
    ds = CFG["dataset"]
    assert ds["base_url"] == "https://amazon-berkeley-objects.s3.amazonaws.com" and ds["index_url"] == INDEX
    assert ds["csv"] == "3dmodels/metadata/3dmodels.csv.gz" and ds["glb"] == "3dmodels/original/{path}"
    assert ds["listings"] == "listings/metadata/listings_{shard}.json.gz" and ds["shards"] == "0123456789abcdef"
    assert ds["licence"] == C.CC_BY and ds["credit_data"] == "Amazon.com" and ds["front_axis"] == "-Y"
    assert "Matthieu Guillaumin" in ds["credit_dataset"] and "Jitendra Malik" in ds["credit_dataset"]
    assert CFG["survey"]["per_type_limit"] == 24 and CFG["survey"]["max_glb_mb"] == 60
    assert len(A.metadata_names(CFG)) == 18                         # csv, README, 16 listings shards
    table, _ = OV.library_size_table(OCFG)
    heights = OV.heights_of(OCFG)
    for rule in CFG["rules"]:
        assert rule["product_types"] and rule["types"], rule["name"]
        for t in rule["types"]:
            for real in (OV.BED_TYPES if t == "bed" else [t]):
                assert real in table and real in heights, (rule["name"], real)
                assert real in C.FURNITURE_TYPES or real in C.DECOR_TYPES, real
    names = [r["name"] for r in CFG["rules"]]
    assert len(names) == len(set(names))
    # The ABO files never land in the repository (CLAUDE.md: caches on the container disk).
    assert A.DEFAULT_CACHE == Path("/opt/wenart/abo")


# --------------------------------------------------------------------------
# Mapping table: every row of docs/milestone8.md §2
# --------------------------------------------------------------------------

def mapped(ptype, name, dims):
    rule = A.match_rule(ptype, name, dims[2], CFG["rules"])
    if rule is None:
        return None
    table, tol = OV.library_size_table(OCFG)
    return A.resolve_type(rule, dims, OCFG, table, tol)[0]


@pytest.mark.parametrize("ptype, name, dims, expect", [
    ("TABLE", "Rivet Mid-Century Coffee Table, Walnut", [1.1, 0.55, 0.45], "table_coffee"),
    ("TABLE", "Bateman Rustic Bedside Table Nightstand", [0.6, 0.45, 0.6], "nightstand"),
    ("TABLE", "Modern Nightstands, Set", [0.5, 0.4, 0.55], "nightstand"),        # a plural is the same word
    ("TABLE", "Bristol Natural Edge Side Table", [0.48, 0.48, 0.49], "side_table"),
    ("TABLE", "Mid-Century End Table", [0.5, 0.45, 0.6], "side_table"),
    ("TABLE", "Round Accent Table", [0.45, 0.45, 0.55], "side_table"),
    ("TABLE", "Hayes Solid Wood Dining Table", [1.3, 0.9, 0.75], "table_dining"),
    ("TABLE", "Console Table", [1.2, 0.35, 0.8], None),                          # no rule
    ("CABINET", "Corona Wardrobe, 3 Door", [1.5, 0.57, 1.87], "wardrobe"),
    ("CABINET", "Tall Armoire", [1.0, 0.6, 1.9], "wardrobe"),
    ("CABINET", "2-Door TV Stand, White", [1.5, 0.41, 0.44], "tv_unit"),
    ("CABINET", "Media Cabinet", [1.6, 0.45, 0.6], "tv_unit"),
    ("CABINET", "File Cabinet", [0.55, 0.39, 0.6], None),
    ("LAMP", "Swing Arm Floor Lamp", [0.36, 0.36, 1.47], "floor_lamp"),
    ("LAMP", "Faux Wood Table Lamp", [0.21, 0.21, 0.46], None),                  # extent_z (height) < 1.2 m
    ("BED", "Tisbury Queen Bed", [1.71, 2.37, 1.44], "bed_double"),
    ("BED_FRAME", "Heavy Duty Bed Frame (Twin)", [1.02, 1.95, 0.66], "bed_single"),  # width <= 1.275 m
    ("BED", "Metal Twin Loft Bed", [1.39, 1.97, 1.29], None),                    # not_words
    ("SHELF", "Barrett 4-Shelf Bookcase", [1.02, 0.38, 1.88], "bookshelf"),
    ("SHELF", "Cube Storage Shelf", [0.8, 0.3, 0.8], None),                      # height < 1.0 m
    ("SHELF", "Floating Wall Shelf", [0.6, 0.2, 1.2], None),
    ("CHAIR", "Highland Wingback Accent Chair", [0.76, 0.95, 1.08], "armchair"),
    ("CHAIR", "Cameron Oversized Arm Chair", [0.77, 0.84, 0.94], "armchair"),
    ("CHAIR", "Leather Club Chair", [0.85, 0.85, 0.8], "armchair"),
    ("CHAIR", "Lounge Chair", [0.8, 0.85, 0.75], "armchair"),
    ("CHAIR", "Channel-Back Dining Chair", [0.48, 0.59, 0.9], "chair"),
    ("CHAIR", "Armless Accent Chair", [0.5, 0.6, 0.85], "chair"),               # armless: the chair rule
    ("CHAIR", "Emerly Living Room Chair", [1.04, 0.89, 0.86], "armchair"),       # chair rule, armchair by size
    ("CHAIR", "Velvet Swivel Office Chair", [0.6, 0.6, 1.0], None),
    ("CHAIR", "Lawson Angled Loveseat", [1.52, 0.8, 0.95], "sofa"),
    ("SOFA", "Revolve Upholstered Sofa", [1.98, 0.94, 0.92], "sofa"),
    ("SOFA", "L-Shape Sectional", [2.98, 1.94, 0.88], None),                     # outside the sofa range
    ("DESK", "Compact Desk", [0.70, 0.45, 0.76], None),                         # 0.70 m: below the desk width
    ("DESK", "Writing Desk", [1.2, 0.6, 0.76], "desk"),
    ("DRESSER", "6-Drawer Dresser", [1.54, 0.46, 0.81], "dresser"),
    ("DRESSER", "3-Drawer Chest", [0.6, 0.4, 0.6], "nightstand"),              # too small for a dresser
    ("RUG", "Modern Wool Area Rug, 4 x 6 Foot", [1.83, 1.21, 0.02], "rug"),
    ("WALL_ART", "Framed Print, 18 x 24", [0.46, 0.01, 0.61], "wall_art"),
    ("PILLOW", "Rustic Stripe Throw Pillow", [0.42, 0.17, 0.41], "cushion"),
    ("PILLOW", "Outdoor Patio Seat Cushion", [0.5, 0.5, 0.1], None),
    ("PLANTER", "Stoneware Planter", [0.22, 0.22, 0.2], "plant"),
    ("HOME", "Botanical Print in Gold Frame Wall Art", [0.45, 0.02, 0.55], "wall_art"),
    ("HOME", "Iron Decorative Hanging Mirror Wall Art", [0.77, 0.03, 0.98], None),
    ("OTTOMAN", "Round Ottoman", [1.0, 1.0, 0.45], None),
])
def test_mapping_table(ptype, name, dims, expect):
    if expect is None and A.match_rule(ptype, name, dims[2], CFG["rules"]) is not None:
        assert mapped(ptype, name, dims) is None             # a rule takes it, the size range refuses it
    else:
        assert mapped(ptype, name, dims) == expect


def test_listings_without_an_english_name_match_only_rules_without_words():
    assert A.match_rule("RUG", None, 0.02, CFG["rules"])["name"] == "rug"
    assert A.match_rule("TABLE", None, 0.5, CFG["rules"]) is None          # every TABLE rule needs a word
    assert A.english([{"language_tag": "de_DE", "value": "Tisch"}], ["en_US"]) == (None, None)
    assert A.english([{"language_tag": "de_DE", "value": "Tisch"}, {"language_tag": "en_GB", "value": " A  b "}],
                     ["en_US", "en_GB"]) == ("A b", "en_GB")
    assert A.any_value([{"language_tag": "nl_NL", "value": "Luchtbed"}]) == ("Luchtbed", "nl_NL")


def test_extents_are_turned_into_the_z_up_frame():
    """README convention 1: glTF +Y is up; the importer's Z-up box is (x, z, y) of the csv (checked on two GLBs)."""
    assert A.zup_extents([1.71, 1.44, 2.37]) == [1.71, 2.37, 1.44]


# --------------------------------------------------------------------------
# Survey on the canned metadata
# --------------------------------------------------------------------------

def test_survey_counts_dedup_and_refusals(surveyed):
    doc = surveyed
    assert doc["kind"] == "abo_survey" and doc["source"] == "abo" and doc["downloaded"] is False
    assert doc["metadata"]["readme_checked"] is True
    assert set(doc["metadata"]["files"]) == {Path(p).name for p in A.metadata_names(CFG).values()}
    assert all(len(f["sha256"]) == 64 for f in doc["metadata"]["files"].values())
    # 38 listings, 37 models: one model (a mouse pad) is listed twice and counted once.
    assert doc["listings"] == {"listings_with_model": 38, "models": 37, "listed_twice": 1, "no_english_name": 1}
    assert doc["unmapped_product_types"] == {"BED": 1, "CHAIR": 1, "LAMP": 1, "MOUSE_PAD": 1, "PILLOW": 1, "SHELF": 1}
    refused = {r["uid"]: r["code"] for r in doc["refused"]}
    assert refused == {"abo_B075X61WKJ": "no_model_row",              # the ottoman: its csv row is left out
                       "abo_B07BWK7JWZ": "size_range",                # an L-shape sectional, 2.98 x 1.94 m
                       "abo_B07DYJPF4G": "size_range"}                # the air bed without an English name
    counts = doc["counts"]
    assert counts["sofa"] == {"mapped": 3, "in_size": 2, "tried": 0, "candidates": 2, "not_selected": 0}
    assert counts["bed_double"]["candidates"] == 4 and counts["bed_single"]["candidates"] == 1
    assert counts["rug"]["candidates"] == 4 and len(doc["candidates"]) == 28
    types = {c["group"] for c in doc["candidates"]}
    assert types == {"armchair", "bed_double", "bed_single", "bookshelf", "chair", "cushion", "desk", "dresser",
                     "floor_lamp", "nightstand", "plant", "rug", "side_table", "sofa", "table_coffee",
                     "table_dining", "tv_unit", "wall_art", "wardrobe"}


def test_survey_records_have_the_shared_shape(surveyed, tmp_path):
    """The same record shape as Objaverse's survey.json candidates, plus the Milestone 8 fields."""
    m = Mirror(tmp_path / "mirror")
    m.add("sofa")
    objaverse = OV.survey(m.write(), tmp_path / "lib", OCFG, download=False, log=quiet)["candidates"][0]
    rec = next(c for c in surveyed["candidates"] if c["abo_3dmodel_id"] == "B07B4SCB6T")
    assert set(objaverse) <= set(rec)                       # every Objaverse field is there
    assert rec["uid"] == "abo_B07B4SCB6T" and rec["group"] == "bed_double" and rec["types"] == ["bed_double"]
    assert rec["categories"] == ["BED"] and rec["author"] == "Amazon.com" and rec["licence"] == C.CC_BY
    assert rec["source_url"] == f"{INDEX}#B07B4SCB6T" and rec["licence_url"] == CFG["dataset"]["licence_url"]
    assert rec["licence_flag"] is None and rec["source"] == "abo" and rec["kind"] == "furniture"
    assert rec["decor_type"] is None and rec["units_known"] is True and rec["style_hint"] == "beds"
    assert rec["extents_raw"] == [1.7128, 2.3722, 1.4429]  # csv x, z, y (metres)
    assert rec["csv_extents"] == pytest.approx([1.712752, 1.442861, 2.372174], abs=1e-6)
    assert rec["front_documented"] == "-Y" and "glTF +Z" in rec["front_note"]
    assert rec["object_path"] == "3dmodels/original/T/B07B4SCB6T.glb" and rec["abo_path"] == "T/B07B4SCB6T.glb"
    assert rec["face_count"] == 26122 and rec["texture_count"] == 3 and "glb" not in rec
    rug = next(c for c in surveyed["candidates"] if c["group"] == "rug")
    assert rug["kind"] == "decor" and rug["decor_type"] == "rug"
    for c in surveyed["candidates"]:
        assert c["uid"] == f"abo_{c['abo_3dmodel_id']}" and OV._UID_RE.fullmatch(c["uid"])
        assert OV.normalise_record(c, "abo") == c          # nothing to fill in
    # The shared steps read it like any source's.
    OV.write_json(tmp_path / "lib" / A.SURVEY_NAME, surveyed)
    assert {c["source"] for c in OV.load_candidates(tmp_path / "lib")} == {"objaverse", "abo"}


def test_credit_line_and_notice(surveyed):
    rec = next(c for c in surveyed["candidates"] if c["abo_3dmodel_id"] == "B07B4SCB6T")
    title = 'Stone & Beam Tisbury Nailhead Trim Queen Bed, 66"W, Spinnsol Cocoa'
    assert rec["title"] == title
    assert rec["attribution"] == (f'"{title}" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), {INDEX}; changes: '
                                  "scaled to the drawn footprint, re-oriented, rendered, AI-retouched")
    assert rec["attribution"].startswith(f'"{title}" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), {INDEX}')
    text = A.notice()
    for words in ("Amazon Berkeley Objects", "(c) Amazon.com", "CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/",
                  "Matthieu Guillaumin", "Jitendra Malik (UC Berkeley)", INDEX):
        assert words in text
    # A listing without an English name keeps its own name in the credit line (never an invented English one).
    assert A.any_value([{"language_tag": "nl_NL", "value": "Intex Luchtbed"}])[0] == "Intex Luchtbed"


def test_style_round_robin_then_texture_size_and_variants_last(tmp_path):
    """<= per_type_limit picks spread over the ABO style values: round robin (largest group first), colour variants
    of one product after the other products, larger textures first."""
    small = copy.deepcopy(CFG)
    small["survey"]["per_type_limit"] = 2
    doc = run_survey(tmp_path, small)
    rugs = [c["abo_3dmodel_id"] for c in doc["candidates"] if c["group"] == "rug"]
    # styles: Modern (Blooming Medallion, Ombre), none (Charcoal Medallion), Contemporary (Jute)
    assert rugs == ["B071777YN3", "B0719STLL8"]
    assert doc["counts"]["rug"]["not_selected"] == 2
    full = run_survey(tmp_path / "full")
    order = [(c["rank"], c["abo_3dmodel_id"]) for c in full["candidates"] if c["group"] == "rug"]
    assert [m for _r, m in order] == ["B071777YN3", "B0719STLL8", "B071SHLFLM", "B073F7GGK9"]
    beds = [c for c in full["candidates"] if c["group"] == "bed_double"]
    # Two Tisbury colour variants share the "beds" style: the second comes after every other product.
    assert [c["abo_3dmodel_id"] for c in beds][-1] in ("B07B4W5V3C", "B07B4SCB6T")
    assert [c["style_hint"] for c in beds] == ["beds", "18-inch", "Queen Bed", "beds"]


def test_pick_order_unit():
    def rec(mid, style, px, name, brand="B"):
        return {"abo_3dmodel_id": mid, "style_hint": style, "texture_px": px,
                "_vkey": A.variant_key(brand, name)}
    pool = [rec("a1", "Modern", 4, "Amazon Brand – Lamp X, Black"), rec("a2", "Modern", 16, "Lamp X, White"),
            rec("a3", "Modern", 1, "Lamp Y, Red"), rec("b1", "Rustic", 2, "Lamp Z"), rec("c1", None, 8, "Lamp Q")]
    order = [r["abo_3dmodel_id"] for r in A.pick_order(pool)]
    # groups: modern (3), then "" (none) and rustic by name; inside modern: a2 (16 px), a3 (another product), a1 last
    assert order == ["a2", "c1", "b1", "a3", "a1"]
    assert A.variant_key("Rivet", "Amazon Brand – Rivet Lawson Chair, 33\"W, Smoke") == \
        A.variant_key("rivet", "Rivet Lawson Chair, 33\"W, Dove")


def test_downloads_with_a_fake_fetcher(tmp_path):
    """Download in pick order until per_type_limit pass the file checks: too large, untextured and failed downloads
    are refused with their reason and the next pick is tried; the GLB sha256 is recorded; files already in the
    cache are not fetched again."""
    small = copy.deepcopy(CFG)
    small["survey"]["per_type_limit"] = 1
    small["survey"]["max_glb_mb"] = 0.001                 # ~1 KB: the padded GLB is too large
    calls = []

    def fetcher(url, dest, max_bytes):
        calls.append(url)
        mid = Path(dest).stem
        if mid == "B071777YN3":                            # the first rug: over the size limit
            raise A.TooLarge("over 0 MB")
        if mid == "B0719STLL8":                            # the second: untextured
            return make_glb(Path(dest), textured=False)
        if mid == "B07B4SCB6T":
            raise OSError("connection reset")
        return make_glb(Path(dest))
    doc = run_survey(tmp_path, small, download=True, fetcher=fetcher)
    rug = next(c for c in doc["candidates"] if c["group"] == "rug")
    assert rug["abo_3dmodel_id"] == "B071SHLFLM" and len(rug["glb_sha256"]) == 64
    assert Path(rug["glb"]) == tmp_path / "abo" / "original" / rug["abo_path"]
    assert rug["glb_info"]["textured"] and rug["glb_bytes"] == Path(rug["glb"]).stat().st_size
    codes = {r["abo_3dmodel_id"]: r["code"] for r in doc["refused"]}
    assert codes["B071777YN3"] == "glb_size" and codes["B0719STLL8"] == "untextured"
    assert codes["B07B4SCB6T"] == "download_failed"
    assert doc["counts"]["rug"]["tried"] == 3 and doc["counts"]["rug"]["not_selected"] == 1
    assert any(u.endswith("/3dmodels/original/T/B07B4SCB6T.glb") for u in calls)
    assert all(u.startswith("https://amazon-berkeley-objects.s3.amazonaws.com/3dmodels/original/") for u in calls)
    n = len(calls)
    run_survey(tmp_path, small, download=True, fetcher=fetcher)
    assert len(calls) - n == 2              # only the two that left no file (too large, failed) are fetched again


def test_metadata_is_downloaded_into_the_cache_once(tmp_path):
    got = []

    def fetcher(url, dest):
        got.append(url)
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FIXTURE / Path(url).name, dest)
        return dest
    meta = A.Metadata(CFG, cache=tmp_path / "cache", fetcher=fetcher)
    doc = A.survey(meta, tmp_path / "lib", CFG, OCFG, download_glbs=False, log=quiet)
    assert len(doc["candidates"]) == 28 and len(got) == 18
    assert f"{CFG['dataset']['base_url']}/3dmodels/metadata/3dmodels.csv.gz" in got
    assert (tmp_path / "cache" / "metadata" / "listings_f.json.gz").is_file()
    A.survey(A.Metadata(CFG, cache=tmp_path / "cache", fetcher=fetcher), tmp_path / "lib", CFG, OCFG,
             download_glbs=False, log=quiet)
    assert len(got) == 18                                  # cached: no second download


def test_no_download_needs_the_metadata(tmp_path, capsys):
    meta = A.Metadata(CFG, cache=tmp_path / "empty", download_missing=False)
    with pytest.raises(A.UsageError, match="metadata missing"):
        meta.path(CFG["dataset"]["csv"])
    assert A.main(["survey", "--out", str(tmp_path / "lib"), "--cache", str(tmp_path / "empty"),
                   "--no-download"]) == A.EXIT_USAGE
    assert "metadata missing" in capsys.readouterr().err
    out = tmp_path / "lib2"
    assert A.main(["survey", "--out", str(out), "--metadata", str(FIXTURE), "--no-download"]) == A.EXIT_OK
    doc = json.loads((out / "survey_abo.json").read_text())
    assert len(doc["candidates"]) == 28 and not any("glb" in c for c in doc["candidates"])


def test_a_broken_csv_row_and_a_readme_without_the_licence_are_recorded(tmp_path):
    meta_dir = tmp_path / "meta"
    shutil.copytree(FIXTURE, meta_dir)
    with gzip.open(FIXTURE / "3dmodels.csv.gz", "rt", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    head, rows = lines[0], lines[1:]
    bad = [r for r in rows if r.startswith("B07B4SCB6T,")][0].split(",")
    bad[-1] = "-1"                                         # a negative extent
    rows = [",".join(bad) if r.startswith("B07B4SCB6T,") else r for r in rows]
    with gzip.open(meta_dir / "3dmodels.csv.gz", "wt", encoding="utf-8") as fh:
        fh.write("\n".join([head] + rows) + "\n")
    (meta_dir / "README.md").write_text("# something else\n")
    warnings = []
    doc = A.survey(A.Metadata(CFG, meta_dir, download_missing=False), tmp_path / "lib", CFG, OCFG,
                   download_glbs=False, log=warnings.append)
    assert {r["uid"]: r["code"] for r in doc["refused"]}["abo_B07B4SCB6T"] == "bad_model_row"
    assert doc["metadata"]["readme_checked"] is False and any("WARNING" in w for w in warnings)
