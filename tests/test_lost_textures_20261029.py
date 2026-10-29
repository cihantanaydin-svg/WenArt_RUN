"""Argus P12: a finish built flat because its texture set never reached the assets (29 Oct 2026: real04 run
20261029-201533-full rendered 41 herringbone floors flat, "asset WoodFloor034 not in the assets manifest")."""
from wenart.audit import process as P
from wenart.audit.inputs import Inputs


def test_a_finish_built_flat_without_its_set_is_found_with_its_objects():
    inp = Inputs(project="p", layout="pod", root=None)
    inp.manifest = {
        "materials": {
            "wood_herringbone_mid": {"slug": "wood_herringbone_mid", "textured": False,
                                     "reason": "asset WoodFloor034 not in the assets manifest"},
            "tiles_light": {"slug": "tiles_light", "textured": False,
                            "reason": "style names no asset for this material; procedural tiles grid"},
            "wood_oak_light__WoodFloor051": {"slug": "wood_oak_light", "textured": True, "reason": "textured"}},
        "objects": [{"material": "wood_herringbone_mid"}] * 4 + [{"material": "tiles_light"}]}
    got = P.lost_textures(inp)
    assert [(f["check"], f["severity"], f["kind"], f["target"], f["evidence"]["objects"]) for f in got] == \
        [("P12", "major", "lost", "wood_herringbone_mid", 4)]
    assert "P12" in {f["check"] for f in P.audit(inp)["findings"]}
