"""27 Oct 2026 (review: two places only suited one style family, the Scandinavian test house; user rule: "Every fix is
general: a rule of the pipeline for every project"):

- the reference photos' caption filter and ranking (``wenart.style.references``): each style family has its own look
  words, period words and house words (``FAMILY_CAPTION``), so a classic, rustic or mediterranean room keeps its
  "antique" photos and a classic facade is a traditional house, while a Scandinavian set ranks as before;
- the decor minimums (``decor_ai.ROOM_MIN``, ``architect_details.DECOR_MIN``) scale with the style's decor density
  (``wenart.style.density``: the recipe's measured density, else the family's), never under a lived-in room.
"""
from __future__ import annotations

import re

from wenart.blender import architect_details as AD
from wenart.furniture import decor_ai as DA
from wenart.furniture import tabletop as TT
from wenart.style import density as DN
from wenart.style import recipe as RC
from wenart.style import references as RF
from wenart.style import vocabulary as V

from test_decor_ai import STYLE, FakeClient, choose, living

FAMILIES = [name for name, _ in V.STYLE_FAMILIES]


def _row(i, caption):
    return {"id": i, "url": f"https://b/{i}.jpg", "caption": caption, "width": 2000, "height": 1300,
            "license": "https://cc0", "source": "x"}


def test_every_family_of_the_registry_has_its_caption_words_and_density():
    assert set(RF.FAMILY_WORDS) == set(FAMILIES) == set(RF.FAMILY_CAPTION) == set(V.FAMILY_DENSITY)
    for fam, voc in RF.FAMILY_CAPTION.items():
        assert set(voc) == {"look", "house", "buildings", "period"}, fam
        assert set(voc["period"]) <= set(RF.PERIOD_WORDS), fam
        assert voc["look"] and voc["house"], fam
    assert set(V.FAMILY_DENSITY.values()) <= set(RC.DENSITY) and set(DN.DENSITY_FACTOR) == set(RC.DENSITY)
    # the light families keep every period word out; the period families let them in
    for fam in ("scandinavian", "japandi", "modern", "modern minimal", "minimal"):
        assert not RF.FAMILY_CAPTION[fam]["period"], fam
    for fam in ("classic", "rustic", "mediterranean"):
        assert {"vintage", "antique", "historic"} <= set(RF.FAMILY_CAPTION[fam]["period"]), fam


def test_a_scandinavian_set_ranks_as_before():
    """Every word the old one-look ranking scored still scores for Scandinavian, the family's own words first; with
    no family the filters are the old ones."""
    old_words = ("modern", "contemporary", "cozy", "bright", "stylish", "elegant", "minimalist", "wooden", "light",
                 "white walls", "plants", "natural light", "spacious")
    scored = set(RF.FAMILY_CAPTION["scandinavian"]["look"]) | set(RF.QUALITY_WORDS)
    assert set(old_words) <= scored
    assert RF.facade_pattern(None) == \
        r"\b(modern|contemporary|white|two\-story|single\-story) (house|home|villa)\b|\b(house|villa) exterior\b"
    for word in ("vintage", "antique", "historic", "painting", "museum"):
        assert re.search(RF.CAPTION_EXCLUDE, f"a {word} living room") and \
            re.search(RF.caption_exclude("scandinavian"), f"a {word} living room"), word
    pts = RF.caption_points("scandinavian")
    named = pts("a scandinavian living room")
    assert named == RF.FAMILY_WORD_POINTS and named > pts("a modern minimalist living room")
    # whole words: "light" is not in "bright", "plant" is in "plants"
    assert RF.caption_points(None)("a bright room") == 1 and pts("a bright room") == 1
    assert pts("a room with plants") == 1


def test_a_classic_or_rustic_family_keeps_its_period_rooms_and_ranks_them_first():
    rows = [_row(1, "An elegant traditional living room with antique furniture and a chandelier"),
            _row(2, "A modern minimalist living room with white walls and light wood"),
            _row(3, "A vintage farmhouse living room with exposed beams and a stone fireplace"),
            _row(4, "A painting of an antique living room"),
            _row(5, "A museum period room, living room of a palace")]
    classic = RF.caption_hits(rows, "classic")["living"]
    assert [r["id"] for r in classic] == [1, 2, 3]                       # paintings and museums out for every family
    best = max(classic, key=lambda r: r["style_hits"])
    assert best["id"] == 1 and {r["id"]: r["style_hits"] for r in classic}[2] <= 1   # "modern" is no bonus here
    rustic = sorted(RF.caption_hits(rows, "rustic")["living"], key=lambda r: -r["style_hits"])
    assert rustic[0]["id"] == 3
    # a light family drops the period rooms (as before) and ranks the modern one first
    assert [r["id"] for r in RF.caption_hits(rows, "scandinavian")["living"]] == [2]
    assert [r["id"] for r in RF.caption_hits(rows, "minimal")["living"]] == [2]
    # industrial: vintage pieces belong to the look, antiques do not
    assert re.search(RF.caption_exclude("industrial"), "an antique room") and \
        not re.search(RF.caption_exclude("industrial"), "a vintage loft")


def test_the_facade_takes_the_family_house_words():
    rows = [_row(1, "A modern white house with a flat roof"), _row(2, "A traditional brick house with a porch"),
            _row(3, "An old stone farmhouse in the hills"), _row(4, "A whitewashed villa by the sea"),
            _row(5, "Farmhouse exterior at dusk"), _row(6, "A georgian house in the city")]

    def facades(fam):
        return [r["id"] for r in RF.caption_hits(rows, fam, spaces=["facade"])["facade"]]
    assert facades(None) == [1]                                                   # the old rule
    assert facades("scandinavian") == [1]
    assert facades("classic") == [2, 6]
    assert facades("rustic") == [3, 5]
    assert facades("mediterranean") == [1, 4]


def test_pexels_rows_rank_by_the_family_words():
    from test_style_references_20261027 import _pexels_rec

    rows = [RF.pexels_row(r) for r in (
        _pexels_rec(1, "Modern Living Room", "interior, living room, modern, minimalist", "A living room with a rug."),
        _pexels_rec(2, "Antique Living Room", "interior, living room, classic, antique",
                    "A traditional living room with a rug, a chandelier and framed artwork."))]
    classic = {r["id"]: r["style_hits"] for r in RF.pexels_hits(rows, "classic")["living"]}
    assert classic[2] > classic[1]
    assert [r["id"] for r in RF.pexels_hits(rows, "scandinavian")["living"]] == [1]       # antique: out for it


def test_the_decor_minimum_scales_with_the_density_never_under_a_lived_in_room():
    for t, base in DA.ROOM_MIN.items():
        assert DN.decor_minimum(t, base, "balanced") == base, t
        assert DN.LIVED_IN_MIN.get(t, DN.LIVED_IN_MIN["other"]) <= DN.decor_minimum(t, base, "sparse") <= base, t
        assert DN.decor_minimum(t, base, "layered") >= base, t
    assert [DN.decor_minimum("living", 9, d) for d in ("sparse", "balanced", "layered")] == [6, 9, 12]
    assert DN.decor_minimum("bedroom", 7, "sparse") == 5 and DN.decor_minimum("dining", 4, "sparse") == 3
    assert DN.decor_minimum("kitchen", 2, "sparse") == 2 and DN.decor_minimum("wc", 1, "sparse") == 1
    # the recipe's measured density first, then the family's, then balanced
    measured = dict(RC.default_recipe("living"), source="photos", n=8, density={"value": "layered", "share": 0.6})
    assert DN.decor_density(measured, "japandi")[0] == "layered" and "8 reference photos" in \
        DN.decor_density(measured, "japandi")[1]
    assert DN.decor_density(RC.default_recipe("living"), "japandi")[0] == "sparse"        # built-in: not measured
    assert DN.decor_density(None, "Classic")[0] == "layered"
    assert DN.decor_density(None, None)[0] == "balanced" and DN.decor_density(None, "bohemian")[0] == "balanced"


def test_the_decor_stage_fills_a_room_to_its_style_and_the_architect_checks_the_same_number(tmp_path):
    b = living()
    path = tmp_path / "answers.json"
    client = FakeClient(choose(("f_L0_002.centre", "vase", "terracotta")))
    DA.ask(b, STYLE, client, path, client.model, log=lambda *a: None)
    answers = DA.read_answers(path)
    counts, kept, styled = {}, {}, {}
    for fam in ("japandi", "scandinavian", "classic"):
        out, records = DA.apply(b, STYLE, answers, style={"family": fam})
        rid = records[0].room_id
        # 28 Oct 2026: the styled tops (tabletop.dress_tops, by the style's density) come after the minimum
        styled[fam] = len([d for d in out["decor"] if d["room_id"] == rid and TT.REASON_TAG in str(d.get("reason"))])
        counts[fam] = len([d for d in out["decor"] if d["room_id"] == rid   # 28 Oct 2026: not the lighting rule's
                           and d.get("rule") != "decor.ceiling_lights"]) - styled[fam]
        kept[fam] = out["decor_minimum"][rid]
        fill = [d for d in out["decor"] if str(d.get("reason", "")).startswith("styling")]
        assert fill and f"the {fam} family" in fill[0]["reason"]
        # the architect reads the decor stage's number: the room is styled for its own style
        s3 = AD.styled_rooms(out, fam)[1]
        assert s3["status"] == "ok" and f"a styled living {kept[fam]['min']}" in s3["answers"][0]["found"]
    assert [kept[f]["min"] for f in ("japandi", "scandinavian", "classic")] == [6, 9, 12]
    assert counts["japandi"] == 6 < counts["scandinavian"] == 9 < counts["classic"]
    total = {f: counts[f] + styled[f] for f in counts}                           # a sparse style, smaller groups
    assert styled["japandi"] > 0 and total["japandi"] < total["scandinavian"] <= total["classic"], (counts, styled)
    # no style: a balanced room, as before
    out, _ = DA.apply(b, STYLE, answers)
    assert out["decor_minimum"][records[0].room_id]["min"] == DA.ROOM_MIN["living"]
    # without the decor stage's record the architect scales DECOR_MIN by the family: seven items are a styled
    # japandi living room, too few for a scandinavian (9) or a classic one (12)
    room = {"id": "r", "level_id": "L0", "room_type": "living", "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]]}
    bare = {"rooms": [room], "furniture": [{"id": "s", "type": "sofa", "room_id": "r"}],
            "decor": [{"id": f"d{i}", "type": "vase", "room_id": "r"} for i in range(7)]}
    assert AD.styled_rooms(bare, "japandi")[1]["status"] == "ok"
    for fam, want in (("scandinavian", 9), (None, 9), ("classic", 12)):
        s3 = AD.styled_rooms(bare, fam)[1]
        assert s3["status"] == "open" and f"a styled living {want}" in s3["answers"][0]["found"], fam
    assert AD.decor_goal(bare, dict(room, room_type="wc"), "classic") is None             # S3 does not check a wc
