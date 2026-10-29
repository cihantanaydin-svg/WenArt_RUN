"""Code the Blender build runs works in Blender's own Python (29 Oct 2026: a local build of real06 stopped on "No module
named 'jsonschema'": the architect's walk-in rule read a room label through ``wenart.building``, which imports
jsonschema at the top; Blender's Python has shapely only, scripts/pod_setup.sh). The label folding is
``wenart.textfold`` now; these run the door and wardrobe label rules in a Python where jsonschema cannot be imported."""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

CODE = """
import sys
sys.modules["jsonschema"] = None          # as in Blender's Python: an import of it fails
from wenart.blender import door_states as D, wardrobe_fronts as W
room = {"id": "r1", "room_type": "storage", "label": "SOYUNMA ODASI"}
bed = {"id": "r2", "room_type": "bedroom", "label": "EBEVEYN YATAK ODASI"}
building = {"rooms": [room, bed], "furniture": [], "walls": [], "openings": []}
print(D.is_dressing(building, room), (W.master_bedroom([bed]) or {}).get("id"), W.walk_in(building, room) is not None)
"""


def test_the_door_and_wardrobe_label_rules_run_without_jsonschema():
    got = subprocess.run([sys.executable, "-c", CODE], capture_output=True, text=True, cwd=str(REPO))
    assert got.returncode == 0, got.stderr[-2000:]
    dressing, master, _walk_in = got.stdout.split()
    assert dressing == "True" and master == "r2"


def test_the_building_module_keeps_its_fold():
    from wenart import building as B
    from wenart import textfold as T

    assert B.fold_ascii is T.fold_ascii and B.fold_ascii("Şömine ODASI") == "somine odasi"
    assert B.slugify("Yatak Odası") == "yatak_odasi"
