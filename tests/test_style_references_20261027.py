"""Style references (27 Oct 2026, lesson UL42; user: "find a way that ai have an idea what is a good room looks like
... take the good style photos from the internet"): reference sets from Openverse / Wikimedia Commons, the recipe
the vision model reads from them, the default recipes and the gaps of a room against its recipe."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from wenart.agent.model import MockModel
from wenart.style import recipe as RC
from wenart.style import recipe_read as RR
from wenart.style import references as RF


def test_spaces_and_queries():
    assert RF.space_of("living") == "living" and RF.space_of("bedroom", "child") == "child"
    assert RF.space_of(None, outdoor="VERANDA") == "veranda" and RF.space_of(None, outdoor="teras patio") == "terrace"
    assert RF.space_of("stair") is None
    q = RF.queries("living", "scandinavian")
    assert q[0] == "scandinavian living room interior" and "nordic living room interior" in q
    assert RF.queries("veranda", "mediterranean") == ["mediterranean covered veranda", "mediterranean porch"]
    assert RF.queries("kitchen", None) == ["kitchen interior design"]


def _openverse(n):
    return {"results": [{"id": f"a{i}", "url": f"https://img/{i}.jpg", "thumbnail": f"https://th/{i}", "title": f"t{i}",
                         "creator": "c", "license": "by", "license_version": "2.0",
                         "license_url": "https://creativecommons.org/licenses/by/2.0/",
                         "foreign_landing_url": f"https://page/{i}", "provider": "flickr",
                         "width": 1600 if i else 400, "height": 1000 if i else 300} for i in range(n)]}


def _commons():
    return {"query": {"pages": {"7": {"pageid": 7, "title": "File:Room.jpg", "imageinfo": [{
        "url": "https://upload/Room.jpg", "thumburl": "https://upload/1280px-Room.jpg", "width": 3000, "height": 2000,
        "descriptionurl": "https://commons/File:Room.jpg",
        "extmetadata": {"Artist": {"value": "<a href='x'>Ann</a>"}, "LicenseShortName": {"value": "CC BY-SA 4.0"},
                        "LicenseUrl": {"value": "https://creativecommons.org/licenses/by-sa/4.0"}}}]},
        "8": {"pageid": 8, "title": "File:Doc.pdf", "imageinfo": [{"url": "https://upload/Doc.pdf"}]}}}}


def test_the_searches_read_openverse_and_commons():
    calls = []

    def http(url):
        calls.append(url)
        return json.dumps(_openverse(3) if "openverse" in url else _commons()).encode()
    ov = RF.openverse_search("scandinavian living room interior", 20, http)
    assert [c["id"] for c in ov] == ["ov_a0", "ov_a1", "ov_a2"] and ov[1]["licence"] == "CC BY 2.0"
    assert "license_type=all-cc" in calls[0] and "category=photograph" in calls[0]
    wc = RF.commons_search("scandinavian living room interior", 20, http)
    assert len(wc) == 1 and wc[0]["creator"] == "Ann" and wc[0]["licence"] == "CC BY-SA 4.0"
    assert wc[0]["url"].endswith("1280px-Room.jpg")
    assert not RF.big_enough(ov[0]) and RF.big_enough(ov[1])


def test_select_keeps_the_space_best_first_without_duplicates():
    cands = [{"id": i, "url": i} for i in ("a", "b", "c", "d")]
    scores = {"a": {"space": 0.9, "negative": 0.1, "style": 0.5, "quality": 0.5, "vec": [1.0, 0.0]},
              "b": {"space": 0.8, "negative": 0.1, "style": 0.6, "quality": 0.6, "vec": [1.0, 0.01]},   # near a
              "c": {"space": 0.2, "negative": 0.7, "style": 0.9, "quality": 0.9, "vec": [0.0, 1.0]},    # a render
              "d": {"space": 0.7, "negative": 0.2, "style": 0.2, "quality": 0.3, "vec": [0.6, 0.8]}}
    kept = RF.select(cands, scores, k=5)
    assert [c["id"] for c in kept] == ["b", "d"] and "vec" not in kept[0]["scores"]


def test_fetch_set_downloads_scores_keeps_and_reuses(tmp_path):
    img = tmp_path / "x.jpg"
    Image.new("RGB", (8, 8), (200, 180, 160)).save(img)
    data = img.read_bytes()
    calls = []

    def http(url):
        calls.append(url)
        if "openverse" in url:
            return json.dumps(_openverse(4)).encode()
        if "commons.wikimedia" in url:
            return json.dumps({"query": {"pages": {}}}).encode()
        return data

    def scorer(paths, space, family):
        return {pid: {"space": 0.9, "negative": 0.1, "style": 0.5 + n / 10, "quality": 0.5, "vec": [1.0, n]}
                for n, pid in enumerate(sorted(paths))}
    man = RF.fetch_set("living", "scandinavian", tmp_path / "refs", http=http, scorer=scorer, k=2)
    folder = RF.set_dir(tmp_path / "refs", "living", "scandinavian")
    assert len(man["photos"]) == 2 and all((folder / p["file"]).is_file() for p in man["photos"])
    assert not (folder / "candidates").exists() and man["photos"][0]["sha256"]
    n = len(calls)
    assert RF.fetch_set("living", "scandinavian", tmp_path / "refs", http=http, scorer=scorer) == man
    assert len(calls) == n                                                      # cached on the volume
    lines = RF.attribution_lines([man])
    assert len(lines) == 2 and "CC BY 2.0" in lines[0] and "not rendered" in lines[0]


def _answer(rug=True, art=2, curtains=True, wall="warm_white", sig=("linen curtains",)):
    layers = {k: (0 if kind == "count" else False) for k, kind in RC.INTERIOR_LAYERS.items()}
    layers.update(rug=rug, wall_art=art, curtains=curtains, plants=1)
    return {"is_the_space": True, "layers": layers, "density": "layered", "signature": list(sig),
            "palette": {"wall_colour": wall, "floor": "light_wood", "wood_tone": "light", "metal": "black",
                        "textile_colours": ["beige", "sage"], "light_mood": "warm"}}


def test_aggregate_and_gaps():
    answers = [_answer(), _answer(art=3), _answer(rug=False, art=1, curtains=False, sig=("linen curtains", "x")),
               {"error": "no answer"}, dict(_answer(), is_the_space=False)]
    rec = RC.aggregate(answers, True)
    assert rec["n"] == 3 and rec["layers"]["rug"]["share"] == 0.667 and rec["layers"]["wall_art"]["median"] == 2
    assert {"rug", "curtains", "wall_art", "plants"} <= set(rec["must"]) and "mirror" not in rec["must"]
    assert rec["palette"]["wall_colour"] == {"value": "warm_white", "share": 1.0}
    assert rec["palette"]["textile_colours"] == ["beige", "sage"] and rec["signature"] == ["linen curtains"]
    gaps = RC.gaps(rec, {"rug": 1, "wall_art": 1})
    assert [g["layer"] for g in gaps] == ["plants", "curtains", "wall_art"] or \
        {g["layer"] for g in gaps} == {"plants", "curtains", "wall_art"}
    art = next(g for g in gaps if g["layer"] == "wall_art")
    assert art["wanted"] == 2 and art["have"] == 1
    schema = RC.photo_schema(True)
    assert set(schema["properties"]["layers"]["required"]) == set(RC.INTERIOR_LAYERS)
    assert "lounge_set" in RC.photo_schema(False)["properties"]["layers"]["properties"]


def test_default_recipes_and_their_text():
    rec = RC.default_recipe("veranda")
    assert rec["source"] == "default" and not rec["interior"] and "lounge_set" in rec["must"]
    assert rec["layers"]["planters"]["median"] == 3
    text = RC.recipe_text(RC.default_recipe("living"))
    assert text.startswith("What good rooms of this kind show (built-in designer defaults)") and "a rug" in text
    assert "framed art, prints or photos on the walls x2" in text


def test_recipe_for_reads_each_photo_once_and_caches(tmp_path):
    root = tmp_path / "refs"
    folder = RF.set_dir(root, "living", "scandinavian")
    folder.mkdir(parents=True)
    photos = []
    for i in range(3):
        Image.new("RGB", (16, 16), (120, 110, 100)).save(folder / f"p{i}.jpg")
        photos.append({"id": f"p{i}", "file": f"p{i}.jpg", "sha256": f"h{i}"})
    man = {"space": "living", "family": "scandinavian", "photos": photos}
    (folder / "manifest.json").write_text(json.dumps(man))
    model = MockModel(critic=[_answer(), _answer(), _answer(rug=False)])
    rec = RR.recipe_for(model, man, root)
    assert rec["n"] == 3 and rec["set_key"] == RR.set_key(man) and len(model.requests) == 3
    assert RR.recipe_for(MockModel(), man, root)["n"] == 3                     # cached by the photos' hashes
    recs = RR.recipes_for(["living", "veranda"], "scandinavian", root, None)
    assert recs["living"]["source"] == "photos" and recs["veranda"]["source"] == "default"
    b = {"rooms": [{"room_type": "living"}, {"room_type": "bedroom", "room_subtype": "child"}, {"room_type": "stair"}],
         "site": {"outdoor_spaces": [{"kind": "veranda"}]}}
    assert RR.project_spaces(b) == ["child", "facade", "garden", "living", "veranda"]


def test_the_decor_fills_the_recipes_must_layers_the_ai_left_out(tmp_path):
    """27 Oct 2026 (UL42): with a recipe, the stylist's question carries what good rooms of the kind show, and every
    must layer the agreed AI items miss is added by code in a free slot of its kind (method rule, the recipe as the
    reason); without a recipe nothing changes."""
    from test_decor_ai import STYLE, FakeClient, choose, living
    from wenart.furniture import decor_ai as DA

    b = living()
    recipe = RC.default_recipe("living")
    recipes = {"living": recipe}
    q = DA.room_questions(b, STYLE, recipes=recipes)[0]
    assert "What good rooms of this kind show" in q.prompts[1] and "What good rooms" not in \
        DA.room_questions(b, STYLE)[0].prompts[1]
    path = tmp_path / "answers.json"
    client = FakeClient(choose(("f_L0_002.centre", "vase", "terracotta")))
    DA.ask(b, STYLE, client, path, client.model, log=lambda *a: None, recipes=recipes)
    out, records = DA.apply(b, STYLE, DA.read_answers(path), recipes=recipes)
    items = [d for d in out["decor"] if d["room_id"] == q.room["id"]]
    have = DA.layer_counts(items)
    for layer in ("rug", "cushions", "throw", "wall_art", "pendant_or_ceiling_light"):
        assert have.get(layer), (layer, have)
    filled = [d for d in items if d["method"] == "rule" and str(d["reason"]).startswith("recipe:")]
    assert filled and "built-in designer defaults" in filled[0]["reason"]
    assert any(d["type"] == "vase" and d["method"] == "ai" for d in items)
    # no recipe: the AI's item and the minimum fill only
    path2 = tmp_path / "answers2.json"
    DA.ask(b, STYLE, FakeClient(choose(("f_L0_002.centre", "vase", "terracotta"))), path2, "fake", log=lambda *a: None)
    out2, _ = DA.apply(b, STYLE, DA.read_answers(path2))
    assert not [d for d in out2["decor"] if str(d.get("reason") or "").startswith("recipe:")]
    rec_path = tmp_path / "recipes.json"
    rec_path.write_text(json.dumps({"family": "scandinavian", "recipes": recipes}))
    assert DA.load_recipes(None, str(tmp_path / "style.json")) == recipes and DA.load_recipes("none", None) is None
    defaults = DA.load_recipes(None, None)                       # no recipes.json: the built-in recipes
    assert defaults["veranda"]["source"] == "default" and "lounge_set" in defaults["veranda"]["must"]


def test_the_judge_sees_a_reference_photo_of_the_space(tmp_path):
    """27 Oct 2026 (UL42): the judge gets the best reference photo of the view's space and style beside the render and
    names the layers the render lacks ('missing layer: ...')."""
    from wenart.agent import judge as JD

    root = tmp_path / "refs"
    folder = RF.set_dir(root, "living", "scandinavian")
    folder.mkdir(parents=True)
    Image.new("RGB", (16, 16), (200, 190, 180)).save(folder / "ov_1.jpg")
    (folder / "manifest.json").write_text(json.dumps({"space": "living", "family": "scandinavian",
                                                      "photos": [{"id": "ov_1", "file": "ov_1.jpg"}]}))
    b = {"project": {"style_family": "scandinavian"}, "rooms": [{"id": "r1", "room_type": "living", "label": "Salon"}],
         "furniture": [], "openings": [], "walls": []}
    view = {"name": "cam_r1_1", "room_id": "r1", "visible_furniture": []}
    ref = JD.reference_for(b, view, root)
    assert ref == folder / "ov_1.jpg"
    assert JD.reference_for(b, {"name": "ext_1"}, root) is None                # no facade set fetched
    render = tmp_path / "r.jpg"
    Image.new("RGB", (16, 16), (90, 90, 90)).save(render)
    model = MockModel(critic=[{"client_ready_score": 2, "tags": ["not_stylish"], "note": "bare",
                               "problems": [{"check": "D3", "severity": "major", "target": "r1",
                                             "message": "missing layer: rug"}]}])
    got = JD.judge_view(model, b, view, render, style="scandinavian", call_id="j1", reference=ref)
    assert got["row"]["reference"] == "ov_1.jpg" and got["findings"][0]["message"] == "missing layer: rug"
    content = model.requests[0]["messages"][1]["content"]
    assert sum(1 for c in content if c.get("type") == "image_url") == 2
    assert "Image 2 is a photo of a well-designed living" in content[-1]["text"]


def test_style_scores_compare_each_render_with_its_spaces_photos(tmp_path):
    root = tmp_path / "refs"
    folder = RF.set_dir(root, "living", "scandinavian")
    folder.mkdir(parents=True)
    for i in range(2):
        Image.new("RGB", (8, 8)).save(folder / f"p{i}.jpg")
    (folder / "manifest.json").write_text(json.dumps({"photos": [{"id": f"p{i}", "file": f"p{i}.jpg"}
                                                                 for i in range(2)]}))
    vecs = {"p0.jpg": [1.0, 0.0], "p1.jpg": [0.8, 0.6], "good.jpg": [0.95, 0.31], "bad.jpg": [0.0, 1.0]}

    def fake(paths):
        return [vecs[Path(p).name] for p in paths]
    views = [{"name": "cam_r_salon_1", "image": tmp_path / "good.jpg", "space": "living"},
             {"name": "cam_r_salon_2", "image": tmp_path / "bad.jpg", "space": "living"},
             {"name": "ext_1", "image": tmp_path / "x.jpg", "space": "facade"}]
    res = RF.style_scores(views, root, "scandinavian", embed_fn=fake)
    good, bad, ext = res["views"]
    assert good["similarity"] > 0.95 > bad["similarity"] and ext["reason"] == "no reference set"
    assert res["by_space"]["living"] == res["mean"]


def test_an_empty_set_is_fetched_again_and_searches_broaden(tmp_path):
    """Pod run 123917: every search failed (Openverse takes at most 20 results a page anonymously) and the empty sets
    were cached. Now a page asks for at most 20, an empty set is never reused, and too few photos broaden the query."""
    urls = []

    def dead(url):
        urls.append(url)
        raise RuntimeError("HTTP 401 Unauthorized")
    man = RF.fetch_set("living", "scandinavian", tmp_path, http=dead, scorer=lambda *a: {})
    assert man["photos"] == [] and "HTTP 401" in man["errors"][0]
    assert "page_size=20" in urls[0] and any("q=scandinavian+living+room&" in u for u in urls)  # broader query
    assert any("living+room" in u and "scandinavian" not in u for u in urls)
    n = len(urls)
    RF.fetch_set("living", "scandinavian", tmp_path, http=dead, scorer=lambda *a: {})
    assert len(urls) > n                                                     # not reused
    assert RF.broad_queries("veranda", "mediterranean") == ["mediterranean covered veranda", "covered veranda",
                                                            "porch"]


def test_pd12m_caption_search_and_candidate_sets(tmp_path):
    """27 Oct 2026 (user: "find the photos yourself and put it into the pod"): PD12M's captions name the space; paintings,
    drawings, maps and old photos are out; the family's words rank first; the candidates are downloaded, ranked and
    written as 512 px copies with a manifest for the session's choice."""
    rows = [{"id": 1, "url": "https://b/1.jpg", "caption": "A bright scandinavian living room with a grey sofa",
             "width": 2000, "height": 1300, "license": "https://cc0", "source": "x"},
            {"id": 2, "url": "https://b/2.jpg", "caption": "A modern living room with plants", "width": 1600,
             "height": 1000, "license": "https://cc0", "source": "x"},
            {"id": 3, "url": "https://b/3.jpg", "caption": "A painting of a living room", "width": 3000, "height": 2000},
            {"id": 4, "url": "https://b/4.jpg", "caption": "A small living room", "width": 600, "height": 400},
            {"id": 5, "url": "https://b/5.jpg", "caption": "A child's bedroom with a bunk bed", "width": 1500,
             "height": 1000},
            {"id": 6, "url": "https://b/6.jpg", "caption": "A covered porch with rocking chairs", "width": 1500,
             "height": 1000}]
    hits = RF.caption_hits(rows, "scandinavian")
    assert [r["id"] for r in hits["living"]] == [1, 2] and hits["living"][0]["style_hits"] >= 2
    assert [r["id"] for r in hits["child"]] == [5] and hits["bedroom"] == [] and [r["id"] for r in hits["veranda"]] == [6]
    acc = RF.merge_hits({}, hits, keep=1)
    assert [r["id"] for r in acc["living"]] == [1]
    img = tmp_path / "x.jpg"
    Image.new("RGB", (900, 600), (180, 170, 160)).save(img)
    data = img.read_bytes()

    def scorer(paths, space, family):
        return {pid: {"space": 0.9, "negative": 0.1, "style": 0.5, "quality": 0.5, "vec": [1.0, float(n)]}
                for n, pid in enumerate(sorted(paths))}
    counts = RF.candidate_sets("scandinavian", tmp_path / "root", tmp_path / "out", per_space=5,
                               http=lambda u: data, scorer=scorer, hits={"living": hits["living"]})
    assert counts == {"living": 2}
    man = json.loads((RF.set_dir(tmp_path / "out", "living", "scandinavian") / "manifest.json").read_text())
    assert man["source"] == "pd12m" and man["photos"][0]["licence"].startswith("public domain")
    out_img = Image.open(RF.set_dir(tmp_path / "out", "living", "scandinavian") / man["photos"][0]["file"])
    assert max(out_img.size) <= RF.EXPORT_SIDE_PX


def test_contact_sheet_numbers_the_photos_and_marks_the_picks(tmp_path):
    photos = []
    for i in range(7):
        Image.new("RGB", (400, 300), (30 * i, 100, 150)).save(tmp_path / f"p{i}.jpg")
        photos.append({"id": f"p{i}", "file": f"p{i}.jpg"})
    (tmp_path / "manifest.json").write_text(json.dumps({"photos": photos}))
    n = RF.contact_sheet(tmp_path, tmp_path / "sheet.jpg", cols=3, side=100, title="living", picked={"p1"})
    assert n == 7 and Image.open(tmp_path / "sheet.jpg").size == (300, 3 * 100 + 28)


def test_features_reads_the_transformers_5_output():
    class T:
        def norm(self, **kw):
            return 1.0

    class Out:
        pooler_output = T()
    t = T()
    assert RF._features(t) is t and RF._features(Out()) is Out.pooler_output
