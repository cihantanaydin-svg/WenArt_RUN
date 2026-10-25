"""A tasteful furniture selection (wenart/furniture/taste.py; user of 25 Oct 2026: "there is no taste in the
furniture selection"): a model's wood tone, metal finish and colours are read from its GLB, and the fit ranks the
models that fit the room's set (one wood tone and one contrast, one metal, the style's palette) first. CPU, pure."""
import json
import struct

import pytest

from wenart.furniture import fit as F
from wenart.furniture import taste as T


def _glb(path, materials, tris_per_material):
    """A GLB with one primitive (``n`` triangles of 1 x 1 m) per material."""
    positions, indices, prims, accessors, views = b"", b"", [], [], []
    for m, n in enumerate(tris_per_material):
        pos = []
        for k in range(n):
            pos += [(k * 2.0, 0.0, 0.0), (k * 2.0 + 1.0, 0.0, 0.0), (k * 2.0, 1.0, 0.0)]
        off = len(positions)
        positions += b"".join(struct.pack("<3f", *p) for p in pos)
        views.append({"buffer": 0, "byteOffset": off, "byteLength": len(pos) * 12})
        accessors.append({"bufferView": len(views) - 1, "componentType": 5126, "count": len(pos), "type": "VEC3",
                          "min": [0, 0, 0], "max": [n * 2.0, 1.0, 0.0]})
        prims.append({"attributes": {"POSITION": len(accessors) - 1}, "material": m})
    doc = {"asset": {"version": "2.0"}, "buffers": [{"byteLength": len(positions)}], "bufferViews": views,
           "accessors": accessors, "meshes": [{"primitives": prims}], "materials": materials}
    js = json.dumps(doc).encode()
    js += b" " * (-len(js) % 4)
    binary = positions + b"\0" * (-len(positions) % 4)
    body = struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(binary), 0x004E4942) + binary
    path.write_bytes(b"glTF" + struct.pack("<II", 2, 12 + len(body)) + body)
    return path


def _mat(name, rgb, metallic=0.0):
    return {"name": name, "pbrMetallicRoughness": {"baseColorFactor": list(rgb) + [1.0], "metallicFactor": metallic}}


def test_a_models_wood_tone_metal_and_colours_come_from_its_glb(tmp_path):
    walnut = _glb(tmp_path / "w.glb", [_mat("Walnut_top", (0.10, 0.05, 0.02)), _mat("legs", (0.02, 0.02, 0.02), 1.0)],
                  [8, 2])
    pal = T.glb_palette(walnut)
    assert [p["kind"] for p in pal] == ["wood", "metal"] and pal[0]["share"] == pytest.approx(0.8)
    a = T.attributes(pal)
    assert a["wood_tone"] == "dark" and a["metal"] == "black" and not a["loud"]
    oak = T.attributes(T.glb_palette(_glb(tmp_path / "o.glb", [_mat("oak", (0.72, 0.55, 0.36))], [4])))
    assert oak["wood_tone"] == "light"
    red = T.attributes(T.glb_palette(_glb(tmp_path / "r.glb", [_mat("Fabric", (0.75, 0.05, 0.05))], [4])))
    assert red["loud"] and "fabric" in red
    assert T.glb_palette(tmp_path / "missing.glb") is None


def test_the_rooms_set_one_wood_tone_one_contrast_one_metal_the_palette():
    target = {"wood_tone": "light", "metal": "black", "palette": [T.lab((0.8, 0.6, 0.2))]}   # a mustard accent
    room = {}
    assert T.steps({"wood_tone": "light", "metal": "black"}, room, target) == 0
    assert T.steps({"wood_tone": "medium"}, room, target) == 1             # the contrast tone: allowed once
    T.note(room, {"wood_tone": "light", "metal": "black"})
    T.note(room, {"wood_tone": "medium"})
    assert room == {"tones": ["light", "medium"], "metal": "black"}
    assert T.steps({"wood_tone": "medium"}, room, target) == 0             # the contrast repeats
    assert T.steps({"wood_tone": "dark"}, room, target) == 3               # a third tone, light-dark jump
    assert T.steps({"metal": "brass"}, room, target) == 2                  # a second metal in the room
    loud_red = {"loud": True, "main": T.lab((0.8, 0.05, 0.05))}
    loud_mustard = {"loud": True, "main": T.lab((0.85, 0.62, 0.15))}
    assert T.steps(loud_red, room, target) == 1 and T.steps(loud_mustard, room, target) == 0
    assert T.anchor_rank("sofa") < T.anchor_rank("side_table") < T.anchor_rank("rug")


def test_the_style_sets_the_target():
    style = {"furniture": {"wood": "wood_veneer_oak_light"}, "window_frame": {"material": "dark_bronze"},
             "floor": {"material": "wood_oak_light"}}
    t = T.targets(style)
    assert t["wood_tone"] in ("light", "medium") and t["metal"] == "black"
    assert T.targets({"floor": {"material": "wood_walnut"}})["wood_tone"] == "dark"
    assert T.targets(None) == {"palette": []}


class _Cache:
    def __init__(self, attrs):
        self.attrs = attrs

    def get(self, entry):
        return self.attrs.get(entry["id"], {})


def test_the_fit_ranks_the_matching_model_first():
    a = {"id": "dark_table", "bbox_m": [1.6, 0.9, 0.75], "units_known": True}
    b = {"id": "light_table", "bbox_m": [1.6, 0.9, 0.75], "units_known": True}
    plain = F.rank_candidates([a, b], 1.6, 0.9)
    assert [e["id"] for e in plain] == ["dark_table", "light_table"]           # by id when nothing else differs
    cache = _Cache({"dark_table": {"wood_tone": "dark"}, "light_table": {"wood_tone": "light"}})
    tasteful = F.rank_candidates([a, b], 1.6, 0.9, taste=(cache, {}, {"wood_tone": "light", "palette": []}))
    assert [e["id"] for e in tasteful] == ["light_table", "dark_table"]
