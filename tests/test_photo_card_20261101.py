"""1 Nov 2026 (lesson UL237; user on real04 run 20261031-194116-full: "This is only a photo if that's the case don't use
this model ever again"): a library model that is only a photo card is found by code and never used.

The mesh check (``wenart.assets.audit.photocard.analyse`` / ``verdict``) on synthetic meshes and a synthetic GLB read
by ``glbmesh.textured_arrays``; the CPU rule (``cpu_rule``) on synthetic and committed audit measurements, with the
known examples of the ranking sheets (``results/library/ranking/ranking_index*.json``: sheet + letter -> model id);
the store (``results/library/photo_cards.json``, ``wenart.furniture.photo_cards``) through ``catalog.usable`` and
``catalog.unusable_reason``; the audit check and the model review. CPU only."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest

from wenart.assets.audit import checks as CK
from wenart.assets.audit import decide as DE
from wenart.assets.audit import glbmesh as GM
from wenart.assets.audit import photocard as P
from wenart.furniture import catalog as C
from wenart.furniture import photo_cards as PC

REPO = Path(__file__).resolve().parents[1]
RANKING = REPO / "results" / "library" / "ranking"
MEASURES = sorted((REPO / "results" / "library" / "audit").glob("*/measure.json"))


# --------------------------------------------------------------------------
# Synthetic meshes
# --------------------------------------------------------------------------

def box(x0, y0, z0, x1, y1, z1):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1),
         (x0, y1, z1)]
    t = [(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7), (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5), (2, 3, 7), (2, 7, 6),
         (3, 0, 4), (3, 4, 7)]
    return np.array(v, float), np.array(t)


def sheet(x0, x1, z0, z1, y=0.0):
    """A one-sided quad in the x-z plane (a SketchUp image: the photo mapped once, UV 0..1)."""
    v = np.array([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], float)
    t = np.array([(0, 1, 2), (0, 2, 3)])
    uv = np.array([[(0, 0), (1, 0), (1, 1)], [(0, 0), (1, 1), (0, 1)]], float)
    return v, t, uv


def once(t):
    return np.tile(np.array([[(0, 0), (1, 0), (1, 1)]], float), (len(t), 1, 1))


def tiled(t, span=2.0):
    return np.tile(np.array([[(0, 0), (span, 0), (span, span)]], float), (len(t), 1, 1))


def join(parts):
    vs, ts, tex, uvs, off = [], [], [], [], 0
    for v, t, textured, uv in parts:
        vs.append(v)
        ts.append(t + off)
        off += len(v)
        tex.append(np.full(len(t), textured))
        uvs.append(uv if uv is not None else np.full((len(t), 3, 2), np.nan))
    return np.concatenate(vs), np.concatenate(ts), np.concatenate(tex), np.concatenate(uvs)


def judge(parts, ftype="table_coffee", kind="furniture"):
    v, t, tex, uv = join(parts)
    stats = P.analyse(v, t, tex, uv)
    return P.verdict(stats, kind, ftype)[0], stats


def photo_board_with_stand():
    qv, qt, quv = sheet(-0.5, 0.5, 0.0, 0.7)
    sv, st = box(-0.05, 0.0, 0.0, 0.05, 0.25, 0.3)
    return [(qv, qt, True, quv), (sv, st, False, None)]


def table():
    top, tt = box(-0.6, -0.3, 0.42, 0.6, 0.3, 0.45)
    parts = [(top, tt, True, tiled(tt))]
    for x in (-0.55, 0.5):
        for y in (-0.25, 0.2):
            lv, lt = box(x, y, 0.0, x + 0.05, y + 0.05, 0.42)
            parts.append((lv, lt, True, tiled(lt)))
    return parts


def test_a_flat_textured_board_on_a_stand_is_a_photo_card():
    card, stats = judge(photo_board_with_stand())
    assert card and stats["ok"]
    p = stats["panels"][0]
    assert p["vertical"] and p["thin"] and p["once_mapped"] and p["size_m"] == [1.0, 0.7]
    assert p["textured_share"] > 0.9 and stats["share_one"] >= P.CARD_SHARE
    # a 1 cm board (a thin box) with the photo on it: the same
    bv, bt = box(-0.5, -0.005, 0.0, 0.5, 0.005, 0.7)
    sv, st = box(-0.05, 0.0, 0.0, 0.05, 0.25, 0.3)
    card, stats = judge([(bv, bt, True, once(bt)), (sv, st, False, None)])
    assert card and stats["panels"][0]["thickness_m"] == pytest.approx(0.01, abs=1e-4)
    # the reason names the numbers
    assert "1.00 x 0.70 m panel" in P.verdict(stats, "furniture", "table_coffee")[1]


def test_a_real_table_a_closed_box_a_bookshelf_and_a_thick_board_are_no_cards():
    assert not judge(table())[0]                                     # the top lies flat: no standing panel
    v, t = box(-0.9, -0.3, 0.0, 0.9, 0.3, 2.0)
    assert not judge([(v, t, True, tiled(t))], "wardrobe")[0]        # a closed box: front and side are one solid
    v, t = box(-1.0, -0.08, 0.0, 1.0, 0.08, 2.0)                     # a shallow closed box: its back backs the front
    card, stats = judge([(v, t, True, once(t))], "tall_cabinet")
    assert not card and stats["panels"][0]["backing_share"] >= P.BACKING_MAX
    parts = []
    bv, bt = box(-0.9, 0.34, 0.0, 0.9, 0.35, 2.0)
    parts.append((bv, bt, True, tiled(bt, 1.8)))
    for x in (-0.9, 0.88):
        sv, st = box(x, 0.0, 0.0, x + 0.02, 0.34, 2.0)
        parts.append((sv, st, True, tiled(st)))
    for z in (0.0, 0.4, 0.8, 1.2, 1.6, 1.98):
        hv, ht = box(-0.88, 0.0, z, 0.88, 0.34, z + 0.02)
        parts.append((hv, ht, True, tiled(ht)))
    card, stats = judge(parts, "bookshelf")
    assert not card and stats["share_one"] < P.CARD_SHARE           # the back shows, but the shelves hold the surface
    v, t = box(-0.5, -0.025, 0.0, 0.5, 0.025, 0.7)                   # a 5 cm board: the face of a solid
    assert not judge([(v, t, True, once(t))])[0]
    qv, qt, _ = sheet(-0.5, 0.5, 0.0, 0.7)                           # no image: no photo
    assert not judge([(qv, qt, False, None)])[0]


def test_flat_art_is_never_flagged_and_flat_structures_need_a_photo():
    wv, wt = box(-0.4, -0.01, 0.0, 0.4, 0.01, 0.6)
    art = [(wv, wt, True, once(wt))]
    assert judge(art, "table_coffee")[0]                             # the same board filed as a table: a card
    for ftype in ("wall_art", "decor_wall_art", "mirror", "decor_rug", "curtain", "blind", "clock", "tv"):
        card, stats = judge(art, ftype, "decor")
        assert not card and "flat by nature" in P.verdict(stats, "decor", ftype)[1]
    dv, dt = box(-0.45, -0.02, 0.0, 0.45, -0.005, 2.1)
    assert not judge([(dv, dt, True, tiled(dt, 3.0))], "door", "opening")[0]     # a wood door: tiled grain
    assert judge([(dv, dt, True, once(dt))], "door", "opening")[0]               # a photo of a door


def test_a_photo_panel_behind_a_lamp_and_crossed_cards():
    qv, qt, quv = sheet(-0.4, 0.4, 0.3, 1.1, y=0.2)
    lv, lt = box(-0.15, -0.1, 0.5, 0.15, 0.2, 0.8)
    cv, ct = box(-0.005, 0.0, 0.8, 0.005, 0.01, 1.3)
    card, stats = judge([(qv, qt, True, quv), (lv, lt, False, None), (cv, ct, False, None)], "pendant_light", "decor")
    assert card and stats["panels"][0]["extent_share"] >= P.EXTENT_MIN
    # a product photo in front of the real piece (the epoxy table): the front view and the image mapped once
    qv, qt, quv = sheet(-0.55, 0.55, 0.0, 0.62, y=-0.2)
    parts = [(qv, qt, True, quv)]
    tv_, tt = box(-0.5, -0.15, 0.40, 0.5, 0.2, 0.45)
    parts.append((tv_, tt, True, tiled(tt)))
    for x in (-0.45, 0.4):
        lv, lt = box(x, -0.1, 0.0, x + 0.05, 0.15, 0.40)
        parts.append((lv, lt, True, tiled(lt)))
    card, stats = judge(parts)
    assert card and stats["panels"][0]["front_share"] >= P.FRONT_SHARE
    # two crossed image cards (a billboard plant)
    a = sheet(-0.4, 0.4, 0.0, 1.2)
    bv = np.array([(0.0, -0.4, 0.0), (0.0, 0.4, 0.0), (0.0, 0.4, 1.2), (0.0, -0.4, 1.2)], float)
    card, stats = judge([(a[0], a[1], True, a[2]), (bv, a[1], True, a[2])], "potted_plant")
    assert card and stats["share_two"] >= stats["share_one"]
    # a ring lamp (no filled panel) is no card
    ring = []
    for k in range(16):
        ang = 2 * np.pi * k / 16
        x, z = 0.4 * np.cos(ang), 0.6 + 0.4 * np.sin(ang)
        rv, rt = box(x - 0.03, -0.01, z - 0.03, x + 0.03, 0.01, z + 0.03)
        ring.append((rv, rt, True, tiled(rt)))
    assert not judge(ring, "pendant_light", "decor")[0]


def test_the_mesh_check_loads_by_path_without_the_package():
    """``blender_audit.py`` loads photocard.py by path inside Blender (numpy only at the module level)."""
    spec = importlib.util.spec_from_file_location("audit_photocard_by_path", REPO / "wenart/assets/audit/photocard.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    v, t, tex, uv = join(photo_board_with_stand())
    assert mod.verdict(mod.analyse(v, t, tex, uv), "furniture", "table_coffee")[0]
    src = (REPO / "wenart/assets/audit/blender_audit.py").read_text(encoding="utf-8")
    assert 'HERE / "photocard.py"' in src and 'stats["photo_card"]' in src


# --------------------------------------------------------------------------
# GLB read and the pod scan
# --------------------------------------------------------------------------

def write_card_glb(path, transform=None):
    """A GLB with two primitives: a textured photo board (UV 0..1, optionally through KHR_texture_transform) and an
    untextured stand. glTF is Y-up: the board stands in x-y (the importer's x-z)."""
    board_pos = np.array([(-0.5, 0.0, 0.0), (0.5, 0.0, 0.0), (0.5, 0.7, 0.0), (-0.5, 0.7, 0.0)], np.float32)
    board_uv = np.array([(0, 0), (1, 0), (1, 1), (0, 1)], np.float32)
    if transform:                                   # stored UVs halved: the transform's scale 2 restores 0..1
        board_uv = board_uv * 0.5
    board_idx = np.array([0, 1, 2, 0, 2, 3], np.uint16)
    sv, st = box(-0.05, 0.0, 0.0, 0.05, 0.25, 0.3)
    stand_pos = np.stack([sv[:, 0], sv[:, 2], -sv[:, 1]], axis=1).astype(np.float32)     # Z-up -> glTF Y-up
    stand_idx = np.asarray(st, np.uint16).reshape(-1)
    chunks = [board_pos.tobytes(), board_uv.tobytes(), board_idx.tobytes(), stand_pos.tobytes(), stand_idx.tobytes()]
    views, blob = [], b""
    for c in chunks:
        blob += b"\0" * (-len(blob) % 4)
        views.append({"buffer": 0, "byteOffset": len(blob), "byteLength": len(c)})
        blob += c
    tex = {"index": 0}
    if transform:
        tex["extensions"] = {"KHR_texture_transform": {"scale": [2.0, 2.0]}}
    doc = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0, 1]}],
           "nodes": [{"mesh": 0}, {"mesh": 1}],
           "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "TEXCOORD_0": 1}, "indices": 2, "material": 0}]},
                      {"primitives": [{"attributes": {"POSITION": 3}, "indices": 4, "material": 1}]}],
           "materials": [{"pbrMetallicRoughness": {"baseColorTexture": tex}},
                         {"pbrMetallicRoughness": {"baseColorFactor": [0.8, 0.8, 0.8, 1.0]}}],
           "textures": [{"source": 0}], "images": [{"uri": "photo.png"}],
           "buffers": [{"byteLength": len(blob)}], "bufferViews": views,
           "accessors": [{"bufferView": 0, "componentType": 5126, "count": 4, "type": "VEC3",
                          "min": [-0.5, 0.0, 0.0], "max": [0.5, 0.7, 0.0]},
                         {"bufferView": 1, "componentType": 5126, "count": 4, "type": "VEC2"},
                         {"bufferView": 2, "componentType": 5123, "count": 6, "type": "SCALAR"},
                         {"bufferView": 3, "componentType": 5126, "count": 8, "type": "VEC3"},
                         {"bufferView": 4, "componentType": 5123, "count": 36, "type": "SCALAR"}]}
    if transform:
        doc["extensionsUsed"] = ["KHR_texture_transform"]
    from wenart.assets import warehouse as WH
    return WH.write_glb(path, doc, blob)


@pytest.mark.parametrize("transform", [False, True])
def test_a_card_glb_is_read_with_its_image_flags_and_uvs(tmp_path, transform):
    path = write_card_glb(tmp_path / "card.glb", transform)
    doc, buffers = GM.read(path)
    verts, tris, tex, uv = GM.textured_arrays(doc, buffers)
    v0, t0 = GM.mesh_arrays(doc, buffers)
    assert np.allclose(verts, v0) and np.array_equal(tris, t0)          # the same frame as mesh_arrays
    assert int(tex.sum()) == 2 and len(tex) == 14                       # the board's 2 triangles carry the image
    assert np.nanmax(uv[tex]) == pytest.approx(1.0) and np.nanmin(uv[tex]) == pytest.approx(0.0)
    assert np.isnan(uv[~tex]).all()
    assert np.allclose(verts[tris[tex]][:, :, 1], 0.0)                  # the board is the y = 0 sheet
    assert verts[:, 2].max() == pytest.approx(0.7)                       # standing (Z up)
    assert P.verdict(P.analyse(verts, tris, tex, uv), "furniture", "table_coffee")[0]


def test_the_scan_writes_records_resumes_and_merges(tmp_path):
    assets = tmp_path / "assets"
    write_card_glb(assets / "models" / "x" / "card.glb")
    v, t = box(-0.4, -0.4, 0.0, 0.4, 0.4, 0.45)
    items = [{"id": "x_card", "type": "table_coffee", "catalog_type": "table_coffee", "kind": "furniture",
              "title": "Coffee table", "glb": "models/x/card.glb", "sha256_glb": "aa"},
             {"id": "x_missing", "type": "chair", "kind": "furniture", "glb": "models/x/none.glb", "sha256_glb": "bb"}]
    out = tmp_path / "mesh.json"
    res = P.scan(items, assets, out, workers=1, log=lambda *_: None)
    assert res == {"records": 1, "cards": 1, "missing": 1, "left": 0}
    doc = json.loads(out.read_text())
    rec = doc["records"][0]
    assert rec["id"] == "x_card" and rec["card"] and rec["source"] == "mesh" and rec["sha256_glb"] == "aa"
    assert rec["reason"].startswith(P.REASON) and rec["metrics"]["panels"][0]["once_mapped"]
    assert doc["missing"] == ["x_missing"]
    calls = []
    P.scan(items, assets, out, workers=1, log=calls.append)              # resumable: nothing read again
    assert "0 to read" in calls[0]
    # merge: a mesh card is added, a CPU flag the mesh check clears is cleared, a scan of another file is skipped
    cpu = {"x_cpu": {"id": "x_cpu", "source": "cpu", "card": True, "rule": "full_face", "reason": "r",
                     "sha256_glb": "cc"},
           "x_old": {"id": "x_old", "source": "cpu", "card": True, "rule": "full_face", "reason": "r",
                     "sha256_glb": "dd"}}
    store = P.update_store(None, cpu=cpu, date="2026-11-01")
    mesh = [rec, {"id": "x_cpu", "card": False, "source": "mesh", "reason": "no panel", "sha256_glb": "cc"},
            {"id": "x_old", "card": False, "source": "mesh", "reason": "no panel", "sha256_glb": "zz"}]
    sha = {"x_card": "aa", "x_cpu": "cc", "x_old": "dd"}
    kept = P.update_store(store, mesh=mesh, current_sha=sha)        # default: a CPU card stays, the mesh numbers noted
    assert set(kept["cards"]) == {"x_card", "x_cpu", "x_old"} and not kept["cleared"]
    assert kept["cards"]["x_cpu"]["mesh_check"]["card"] is False and "mesh_check" not in kept["cards"]["x_old"]
    assert any("review: x_cpu" in line for line in P.summary(kept))
    merged = P.update_store(store, mesh=mesh, current_sha=sha, clear_cpu=True)
    assert set(merged["cards"]) == {"x_card", "x_old"} and set(merged["cleared"]) == {"x_cpu"}
    assert merged["cleared"]["x_cpu"]["was"] == "r"
    # a later CPU pass never overrides the mesh verdicts; a later scan clears an earlier mesh card it no longer finds
    again = P.update_store(merged, cpu=cpu)
    assert again["cards"]["x_card"]["source"] == "mesh" and "x_cpu" not in again["cards"]
    rescan = P.update_store(again, mesh=[dict(rec, card=False, reason="no panel")], current_sha=sha)
    assert "x_card" not in rescan["cards"] and "x_card" in rescan["cleared"]


# --------------------------------------------------------------------------
# CPU rule
# --------------------------------------------------------------------------

def measure(size, area, main, parts=2, outside=(), images=2):
    return {"ok": True, "size": list(size), "area_m2": area, "main_part_share": main, "parts": parts,
            "outside_parts": [{"share": 0.1, "sticks_out_m": 0.3, "sides": list(s)} for s in outside],
            "textures": {"images": images}}


def test_the_cpu_rule_full_face_and_thin_panel():
    # the epoxy table: a 1.73 x 0.97 m sheet spanning the box face, a 3D table behind it (+y only)
    m = measure((1.7297, 0.6321, 0.973), 3.6009, 0.4674, 8, [("+y",), ("+y",)], 3)
    got = P.cpu_rule(m, "furniture", "table_coffee")
    assert got and got["rule"] == "full_face" and "UL237" in got["reason"] and got["metrics"]["ratio"] == 1.0
    assert P.cpu_rule(dict(m, textures={"images": 0}), "furniture", "table_coffee") is None      # no image
    assert P.cpu_rule(measure((1.73, 0.63, 0.973), 3.6, 0.4674, 8, [("+y", "+z")]), "furniture",
                      "table_coffee") is None                            # a part above the sheet: the sheet is no card
    assert P.cpu_rule(m, "decor", "wall_art") is None and P.cpu_rule(m, "decor", "decor_mirror") is None
    assert P.cpu_rule(m, "opening", "door")["rule"] == "full_face"        # flat by build: the full-face sheet only
    # a thin box whose main part is a one-sided panel (a photo panel behind a linear lamp)
    thin = measure((0.933, 0.058, 0.452), 0.2481, 0.8217, 9, [("+x", "-y")], 4)
    assert P.cpu_rule(thin, "decor", "pendant_light")["rule"] == "thin_panel"
    assert P.cpu_rule(thin, "opening", "door") is None                    # a real door is a thin box
    # a real chair: the main part is not one sheet of the box
    assert P.cpu_rule(measure((0.5, 0.55, 0.9), 2.1, 0.45, 12, [("-z",), ("+x",)]), "furniture", "chair") is None


def ranking_ids(*keys):
    """Model ids of ``sheet:letter`` keys of the committed ranking indexes."""
    letters = {}
    for f in sorted(RANKING.glob("ranking_index*.json")):
        for s in json.loads(f.read_text(encoding="utf-8")).get("sheets") or []:
            letters.setdefault(s["sheet"], s["letters"])
    return [letters[k.split(":")[0]][k.split(":")[1]] for k in keys]


# verified on the sheets of 31 Oct 2026 (a product photo on a board, or a photo panel behind or instead of the piece)
KNOWN_CARDS = ("table_coffee-01:P", "pendant_light-01:H", "pendant_light-01:I", "pendant_light-02:F",
               "pendant_light-03:B", "pendant_light-03:G", "pendant_light-04:D", "pendant_light-05:K",
               "pendant_light-05:N", "pendant_light-05:P", "pendant_light-06:D", "pendant_light-07:M",
               "bar_stool-01:Q", "bench-01:M", "sideboard-01:I", "vase-02:F", "vase-02:I", "plant_large-01:G")
# real 3D models whose mesh numbers come close (a main part near one box face, a thin box, flat art)
KNOWN_REAL = ("chair-03:G", "pendant_light-02:B", "pendant_light-02:H", "pendant_light-05:E", "pendant_light-05:R",
              "pendant_light-06:L", "pendant_light-07:H", "bar_stool-04:C", "shoe_cabinet-01:H", "wardrobe-02:C",
              "side_table-02:B", "dresser-02:C", "dresser-02:A", "wall_art-04:T", "mirror-01:K", "cushion-07:H")
# photo panels behind the lamp whose panel does not span the box (the wire, the lamp beside it): the pod's mesh check
NEEDS_MESH = ("pendant_light-01:E", "pendant_light-01:O", "pendant_light-01:R", "pendant_light-08:C")


@pytest.mark.skipif(not MEASURES or not list(RANKING.glob("ranking_index*.json")),
                    reason="no committed audit measurements or ranking index")
def test_the_cpu_rule_on_the_known_examples_of_the_ranking_sheets():
    from wenart.assets.audit import items as IT
    items = {i["id"]: i for i in IT.load_items()}
    measures = P.load_measures(MEASURES)

    def flagged(iid):
        it = items[iid]
        return P.cpu_rule(measures[iid][0], it["kind"], it["type"]) is not None

    assert all(flagged(i) for i in ranking_ids(*KNOWN_CARDS))
    assert not any(flagged(i) for i in ranking_ids(*KNOWN_REAL))
    assert not any(flagged(i) for i in ranking_ids(*NEEDS_MESH))          # left to the mesh check (documented)
    # the user's coffee table (also on the user-rejected list)
    assert flagged("3dwh_4bb1b0bfa01eefe9079d94b0")


# --------------------------------------------------------------------------
# The store, catalog.usable and the audit
# --------------------------------------------------------------------------

def test_the_committed_store_is_what_the_cpu_rule_gives_and_cards_are_never_used():
    doc = json.loads(PC.PHOTO_CARDS_PATH.read_text(encoding="utf-8"))
    assert doc["kind"] == "photo_cards" and doc["lesson"] == "UL237" and doc["user"] == P.USER_WORDS
    cards = doc["cards"]
    if MEASURES:
        from wenart.assets.audit import items as IT
        cpu = P.cpu_cards(IT.load_items(), P.load_measures(P.default_measure_files()))
        # every card the CPU rule gives is in the store (labelled "mesh" once the mesh scan confirmed it), and every
        # card labelled "cpu" is one the rule gives
        assert set(cpu) - set(doc.get("cleared") or {}) <= set(cards)
        assert {k for k, v in cards.items() if v["source"] == "cpu"} <= set(cpu)
    assert all(r["card"] and r["reason"] and r["sha256_glb"] for r in cards.values())
    assert not any(P.flat_by_nature(r["type"]) for r in cards.values())
    cat = C.load()
    h = ranking_ids("pendant_light-01:H")[0]
    entry = cat.entry(h)
    assert entry is not None and h in cards
    for mode in C.LICENCE_MODES:
        assert not C.usable(entry, mode)
        assert "a photo card, not a 3D object (UL237)" in C.unusable_reason(entry, mode)
    assert not C.usable({"asset_id": h, "licence": "CC-BY-4.0", "licence_flag": "none"}, "relaxed")
    # a record of another file (a republished model) does not judge the new one
    assert PC.card(dict(entry, sha256_glb="0" * 64)) is None
    # a real model stays usable
    real = cat.entry(ranking_ids("chair-03:G")[0])
    assert PC.card(real) is None


def test_the_store_reader_and_its_reason(tmp_path):
    p = tmp_path / "cards.json"
    p.write_text(json.dumps({"cards": {"m1": {"card": True, "source": "mesh", "reason": "x", "sha256_glb": "s1"},
                                       "m2": {"card": False}}}))
    assert PC.card({"id": "m1", "sha256_glb": "s1"}, p) is not None and PC.card({"id": "m2"}, p) is None
    assert PC.card({"asset_id": "m1"}, p) is not None and PC.card({"id": "m1", "sha256_glb": "s2"}, p) is None
    why = PC.reason({"id": "m1"}, p)
    assert why.startswith("a photo card, not a 3D object (UL237)") and "mesh check" in why
    broken = tmp_path / "broken.json"
    broken.write_text("{")
    assert PC.cards(broken) == {}


def test_the_audit_check_removes_a_card_and_skips_flat_art():
    item = {"id": "t1", "type": "table_coffee", "catalog_type": "table_coffee", "kind": "furniture", "source": "3dwh",
            "licence": "CC-BY-4.0", "title": "Coffee table", "units_known": True, "bbox_m": [1.0, 0.25, 0.7]}
    v, t, tex, uv = join(photo_board_with_stand())
    m = {"ok": True, "photo_card": P.analyse(v, t, tex, uv)}
    r = CK.photo_card_check(item, {}, m)
    assert r["status"] == "remove" and r["reason"].startswith(P.REASON)
    assert CK.photo_card_check(dict(item, type="wall_art", catalog_type="decor_wall_art", kind="decor"), {},
                               m)["status"] == "skip"
    # the render's meshstats numbers alone: the CPU rule
    cpu_m = measure((1.7297, 0.6321, 0.973), 3.6009, 0.4674, 8, [("+y",)], 3)
    assert CK.photo_card_check(item, {}, cpu_m)["status"] == "remove"
    assert CK.photo_card_check(item, {}, None)["status"] == "skip"
    assert CK.photo_card_check(item, {}, measure((0.5, 0.55, 0.9), 2.1, 0.45, 12, [("-z",)]))["status"] == "ok"
    # in the audit's checks, and decide removes the model with the reason
    recs = CK.item_checks(item, {}, set(), m)
    pc = [c for c in recs if c["check"] == P.CHECK]
    assert len(pc) == 1 and pc[0]["status"] == "remove"
    dec = DE.decide(item, [pc[0]])
    assert DE.expected_status(dec) == "removed" and any("UL237" in x for x in dec["reasons"])


def test_the_model_review_names_a_card_built_in_a_run():
    from wenart.furniture import room_use as RU
    h = ranking_ids("pendant_light-01:H")[0]
    b = {"furniture": [], "decor": [{"id": "dec_L0_001", "type": "pendant_light", "room_id": "r1",
                                     "asset": {"asset_id": h, "licence": "CC-BY-4.0"}}]}
    found = RU.rejected_models(b)
    assert [f["metrics"]["rule"] for f in found] == ["photo_card"] and found[0]["metrics"]["lesson"] == "UL237"
    assert "photo card" in found[0]["message"]


def test_the_pod_job_is_a_valid_job_script():
    job = REPO / "scripts" / "jobs" / "library_photo_card.sh"
    text = job.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash") and "set -Eeuo pipefail" in text and "trap 'on_error" in text
    assert "wenart.assets.audit.photocard scan" in text and "merge --mesh" in text and 'LOGS=$WS/logs' in text
