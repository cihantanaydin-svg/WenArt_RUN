"""3 Nov 2026 (real10 structure run 20261103-080610-full: the build stopped inside Blender after 17 s on "No module
named 'jsonschema'": the architect's door rule imports ``furniture.doorway`` -> ``placer`` -> ``furniture.schemas``,
which imported jsonschema at module level; Blender's own Python has numpy and the shapely the pod installs, not the CPU
venv's libraries). Every module the Blender build code imports (at module level or inside a function) must import
without them. CPU only: a subprocess with those libraries blocked."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = r'''
import sys, re, importlib
from pathlib import Path
for m in ("jsonschema", "yaml", "ezdxf", "cv2", "scipy", "PIL", "torch", "transformers", "openai"):
    sys.modules[m] = None              # not in Blender's bundled Python
targets = set()
pat1 = re.compile(r"^\s*from (wenart(?:\.\w+)*) import ([\w, ]+)", re.M)
pat2 = re.compile(r"^\s*import (wenart(?:\.\w+)+)", re.M)
for f in Path("wenart/blender").glob("*.py"):
    s = f.read_text(encoding="utf-8")
    targets.add("wenart.blender." + f.stem)
    for pkg, names in pat1.findall(s):
        for n in [x.strip() for x in names.split(",") if x.strip()]:
            targets.add(f"{pkg}.{n}" if Path(pkg.replace(".", "/"), n + ".py").exists() else pkg)
    targets.update(pat2.findall(s))
bad = []
for t in sorted(targets):
    try:
        importlib.import_module(t)
    except ModuleNotFoundError as e:
        if any(k in str(e) for k in ("bpy", "mathutils", "bmesh")):
            continue                   # Blender's own modules
        bad.append(f"{t}: {e}")
print("\n".join(bad))
sys.exit(1 if bad else 0)
'''


def test_the_blender_build_imports_only_what_blenders_python_has():
    res = subprocess.run([sys.executable, "-c", SCRIPT], cwd=str(ROOT), capture_output=True, text=True, timeout=600)
    assert res.returncode == 0, res.stdout + res.stderr[-2000:]
