"""UL199 (30 Oct 2026): "Writing on the labels on the books are acceptable you can write things on them when needed" and
"Also wine vineger salt paper you can write them when you see needed": books carry printed titles on their spines (and
the top book of a stack on its cover), the kitchen's bottles and jars printed paper labels, from one committed
lettering atlas (``wenart.blender.print_labels``). Pure tests."""
from __future__ import annotations

from PIL import Image

from wenart.blender import book_parts as BK
from wenart.blender import kitchen_details as KD
from wenart.blender import parametric as P
from wenart.blender import print_labels as PL
from wenart.blender import small_parts as SM


def _prints(parts):
    return [p for p in parts if p.get("role") == PL.ROLE]


def _strip_of(part) -> int:
    """The strip a print film shows (its printed face's UVs inside one strip cell)."""
    us = [u for face in part["uvs"] for u, _v in face if (u, _v) != PL.CLEAR_UV]
    vs = [v for face in part["uvs"] for _u, v in face if (_u, v) != PL.CLEAR_UV]
    for k in range(PL.STRIPS):
        u0, v0, u1, v1 = PL.strip_cell(k)
        if min(us) >= u0 - 1e-9 and max(us) <= u1 + 1e-9 and min(vs) >= v0 - 1e-9 and max(vs) <= v1 + 1e-9:
            return k
    raise AssertionError("print outside every strip")


def _label_of(part) -> str:
    us = [u for face in part["uvs"] for u, _v in face if (u, _v) != PL.CLEAR_UV]
    vs = [v for face in part["uvs"] for _u, v in face if (_u, v) != PL.CLEAR_UV]
    for name in PL.LABEL_NAMES:
        u0, v0, u1, v1 = PL.label_cell(name)
        if min(us) >= u0 - 1e-9 and max(us) <= u1 + 1e-9 and min(vs) >= v0 - 1e-9 and max(vs) <= v1 + 1e-9:
            return name
    raise AssertionError("label outside every cell")


def test_the_atlas_is_committed_and_laid_out_as_the_module_says():
    img = Image.open(PL.ATLAS_PATH)
    assert img.size == (PL.ATLAS_PX, PL.ATLAS_PX) and img.mode == "RGBA"
    assert img.getpixel(PL.CLEAR_PX)[3] == 0                         # the corner unprinted faces sample
    for k in (0, PL.TONE_STRIPS - 1, PL.TONE_STRIPS, PL.STRIPS - 1):
        x0, y0, x1, y1 = PL.strip_box_px(k)
        alpha = img.crop((x0, y0, x1, y1)).getchannel("A")
        assert alpha.getextrema() == (0, 255)                         # letters on a transparent ground
    for name in PL.LABEL_NAMES:
        x0, y0, x1, y1 = PL.label_box_px(name)
        assert img.getpixel(((x0 + x1) // 2, y0 + 4))[3] == 255        # paper labels are opaque
    assert PL.LABEL_TOP + PL.LABEL_ROWS * PL.LABEL_PX[1] <= PL.ATLAS_PX
    assert len(set(PL.LABEL_NAMES)) == len(PL.LABEL_NAMES) <= PL.LABEL_COLS * PL.LABEL_ROWS
    texts = {PL.strip_text(k)["title"] + PL.strip_text(k)["author"] for k in range(PL.STRIPS)}
    assert len(texts) >= PL.STRIPS * 0.9                               # the strips differ


def test_a_spine_title_reads_down_the_spine_and_stays_on_it():
    t, w, h = 0.03, 0.17, 0.24
    titled = [sd for sd in range(60) if _prints(BK.book(t, w, h, seed=sd))]
    assert len(titled) >= 50                                         # almost every book has its title
    parts = BK.book(t, w, h, seed=titled[0])
    films = _prints(parts)
    assert len(films) == 1
    f = films[0]
    assert f["key"] == PL.LETTERING_KEY and PL.signed_volume(f) > 0.0
    xs, ys, zs = ([v[i] for v in f["verts"]] for i in range(3))
    assert -t / 2.0 <= min(xs) and max(xs) <= t / 2.0 and 0.0 < min(zs) and max(zs) < h
    assert max(ys) <= -w / 2.0 + 1e-9 and min(ys) >= -w / 2.0 - 0.001        # a film just in front of the spine
    printed = [i for i, uv in enumerate(f["uvs"]) if any(c != PL.CLEAR_UV for c in uv)]
    assert printed == [2]                                                     # the -Y face only
    face, uv = f["faces"][2], f["uvs"][2]
    top = max(range(4), key=lambda i: (f["verts"][face[i]][2], -f["verts"][face[i]][0]))
    u0, v0, u1, v1 = PL.strip_cell(_strip_of(f))
    assert abs(uv[top][0] - u0) < 1e-9 and abs(uv[top][1] - v0) < 1e-9     # the text starts at the book's top
    plus_x = max(range(4), key=lambda i: (f["verts"][face[i]][0], f["verts"][face[i]][2]))
    assert abs(uv[plus_x][1] - v1) < 1e-9                                     # the letters' tops to the front board
    assert PL.strip_text(_strip_of(f))["tone"] == PL.tone_for(next(p["key"] for p in parts if p["role"] == BK.ROLE))


def test_the_title_tone_follows_the_cover_colour():
    for colour in ("navy", "charcoal", "burgundy", "black", "terracotta", "rust"):
        assert PL.tone_for(BK.cover_key(colour)) == "light", colour         # gilt or cream on deep cloth
    for colour in ("cream", "off white", "sand", "greige", "camel", "sage"):
        assert PL.tone_for(BK.cover_key(colour)) == "dark", colour          # ink on light cloth
    assert PL.tone_for(BK.JACKET_KEY) == "light" and PL.tone_for("cloth:linen:no such colour") == "dark"
    for colour in set(BK.COVER_COLOURS):                                     # every shelf colour has a strip tone
        assert PL.tone_for(BK.cover_key(colour)) in ("light", "dark")


def test_a_row_shows_distinct_titles_and_is_deterministic():
    parts = BK.row(-0.4, 0.4, 0.0, 0.0, 0.2, 0.26, seed=7)
    films = _prints(parts)
    books = [p for p in parts if p["role"] == BK.PAGES_ROLE]
    assert len(films) >= len(books) * 0.8
    strips = [_strip_of(f) for f in films]
    assert len(strips) == len(set(strips))
    again = _prints(BK.row(-0.4, 0.4, 0.0, 0.0, 0.2, 0.26, seed=7))
    assert [f["uvs"] for f in again] == [f["uvs"] for f in films]
    other = [_strip_of(f) for f in _prints(BK.row(-0.4, 0.4, 0.0, 0.0, 0.2, 0.26, seed=8))]
    assert other != strips


def test_a_stack_lies_cover_up_with_a_title_on_its_top_cover():
    parts = BK.stack(0.0, 0.0, 0.0, 0.24, 0.17, 0.12, n=3, seed=2)
    films = _prints(parts)
    top = max(v[2] for p in parts if p["role"] != PL.ROLE for v in p["verts"])
    covers = [f for f in films if min(v[2] for v in f["verts"]) >= top - 0.001]
    assert len(covers) == 1                                                   # the top book's front cover
    spines = [f for f in films if f not in covers]
    assert spines and all(max(v[1] for v in f["verts"]) < -0.17 * 0.35 for f in spines)    # on the front spines


def test_kitchen_bottles_and_jars_carry_their_labels():
    oil = SM.oil_set(0.22, 0.12, 0.30)
    names = sorted(_label_of(p) for p in _prints(oil))
    assert names == ["olive_oil", "salt", "vinegar"]
    jars = KD.styling_parts("storage_jars", 0.30, 0.12, 0.24)
    assert sorted(_label_of(p) for p in _prints(jars)) == sorted(
        PL.JAR_WORDS[f] for f in ("rattan", "ceramic", "dark"))
    wine = SM.wine_bottle(0.0, 0.0, 0.0, label="wine_3")
    assert [_label_of(p) for p in _prints(wine)] == ["wine_3"]
    for p in _prints(oil) + _prints(jars) + _prints(wine):
        assert PL.signed_volume(p) > 0.0
        # the label's printed strips run left to right seen from the front (-Y): u grows with x
        faces = [(f, uv) for f, uv in zip(p["faces"], p["uvs"]) if any(c != PL.CLEAR_UV for c in uv)]
        mids = [(sum(p["verts"][i][0] for i in f) / len(f), sum(c[0] for c in uv) / len(uv)) for f, uv in faces]
        mids.sort()
        assert all(a[1] < b[1] for a, b in zip(mids, mids[1:]))
        assert all(sum(p["verts"][i][1] for i in f) / len(f) < 0.0 for f, _uv in faces)   # on the front


def test_the_lettering_key_resolves_and_its_uvs_follow_the_mesh():
    from wenart.blender import furniture as F

    assert PL.LETTERING_KEY in P.MATERIAL_KEYS and P.BEVEL_BY_ROLE[PL.ROLE] == 0.0
    keys, _ = F.style_material_keys({})
    assert PL.LETTERING_KEY in keys
    parts = BK.row(-0.2, 0.2, 0.0, 0.0, 0.2, 0.26, seed=1)
    verts, faces, _keys = P.world_mesh(parts, (1.0, 2.0), 30.0, 0.0)
    uvs = P.lettering_uvs(parts)
    assert len(uvs) == len(faces) and all(u is None or len(u) == len(f) for u, f in zip(uvs, faces))
    assert P.lettering_uvs([p for p in parts if p["role"] != PL.ROLE]) is None
    mirrored = P.mirror_parts_x(_prints(parts))
    for a, b in zip(_prints(parts), mirrored):
        assert b["uvs"] == [list(reversed(u)) for u in a["uvs"]] and PL.signed_volume(b) > 0.0
