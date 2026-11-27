"""3 Nov 2026 (real10 structure run 20261103-080610-full: the build stopped inside Blender after 17 s on "No module
named 'jsonschema'": the architect's door rule imports ``furniture.doorway`` -> ``placer`` -> ``furniture.schemas``,
which imported jsonschema at module level; Blender's own Python has numpy and the shapely the pod installs, not the CPU
venv's libraries). Every module the Blender build code imports (at module level or inside a function) must import
without them. CPU only: a subprocess with those libraries blocked.

27 Nov 2026 (audit O1: ``shell.column_piece`` imported ``wenart.ingest.generic.layer_names``, which imported
``wenart.building`` -> jsonschema, and this test passed: its pattern read ``from X import layer_names as LN`` as one
name and imported only the package): the imports are read with ``ast`` (every ``import`` and ``from ... import``,
aliases and relative imports included, inside functions too), so every module a Blender file names is imported."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = r'''
import ast, sys, importlib
from pathlib import Path
for m in ("jsonschema", "yaml", "ezdxf", "cv2", "scipy", "PIL", "torch", "transformers", "openai"):
    sys.modules[m] = None              # not in Blender's bundled Python


def mod_path(name):
    p = Path(name.replace(".", "/"))
    if p.with_suffix(".py").exists():
        return p.with_suffix(".py")
    if (p / "__init__.py").exists():
        return p / "__init__.py"
    return None


def imports_of(path, pkg):
    """The wenart modules a file imports (``import a.b``, ``from a import b as c``, ``from . import b``), anywhere."""
    out = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            out.update(a.name for a in node.names if a.name.split(".")[0] == "wenart")
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                parts = pkg.split(".")
                parts = parts[: len(parts) - (node.level - 1)]
                base = ".".join(parts + ([base] if base else []))
            if base.split(".")[0] != "wenart":
                continue
            for a in node.names:
                sub = f"{base}.{a.name}"
                out.add(sub if mod_path(sub) else base)
    return out


targets = set()
for f in Path("wenart/blender").glob("*.py"):
    targets.add("wenart.blender." + f.stem)
    targets |= imports_of(f, "wenart.blender")
if len(sys.argv) > 1:
    print("\n".join(sorted(targets)))
    sys.exit(0)
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


def test_the_guard_follows_aliased_and_function_level_imports():
    """27 Nov 2026 (audit O1): the targets hold the modules ``shell.column_piece`` and the architect's
    ``act_cover_space`` import inside a function under an alias (``... import layer_names as LN``, ``... import outdoor
    as OD``)."""
    res = subprocess.run([sys.executable, "-c", SCRIPT, "list"], cwd=str(ROOT), capture_output=True, text=True,
                         timeout=600)
    names = set(res.stdout.split())
    assert "wenart.ingest.door_validity" in names           # shell.column_piece -> door_validity.column_piece
    assert "wenart.levels.outdoor" in names
    assert "wenart.textfold" in names


RUN = r'''
import sys
for m in ("jsonschema", "yaml", "ezdxf", "cv2", "scipy", "PIL", "torch", "transformers", "openai"):
    sys.modules[m] = None
from wenart.blender import shell
from wenart.ingest import door_validity as DV
col = {"id": "c", "start": [0, 0], "end": [0.5, 0], "thickness": 0.3, "evidence": [{"layer": "KOLON"}]}
host = {"id": "h", "start": [-2, -0.2], "end": [2, -0.2], "thickness": 0.1}
assert shell.column_piece(col, host) and DV.column_piece(col, host)
door = {"id": "d", "type": "door", "wall_id": "h", "center": [0.2, -0.2], "width": 0.9}
assert shell.foreign_cuts(col, {"h": host, "c": col}, [door]) == []
print("ok")
'''


def test_the_column_rule_runs_without_jsonschema():
    """27 Nov 2026 (audit O1): ``shell.foreign_cuts`` -> ``column_piece`` -> ``door_validity.column_piece`` -> the layer
    roles (``layer_names``, on ``wenart.textfold``) run in a Python without jsonschema (the path a module-level import
    check does not reach: the import sits inside a function)."""
    res = subprocess.run([sys.executable, "-c", RUN], cwd=str(ROOT), capture_output=True, text=True, timeout=600)
    assert res.returncode == 0 and res.stdout.strip() == "ok", res.stdout + res.stderr[-2000:]
