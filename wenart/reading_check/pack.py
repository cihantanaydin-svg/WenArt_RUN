"""The zip of a structure run (4 Nov 2026; user: "General rule always include into structure pod run zips these files"):
the pod's renders and the reading's comparison sheets together.

What: ``pack(out_dir, results, project, dest)`` writes ``dest`` (a .zip) with
- ``top_down/``: the pod's top-down plans (``renders/<project>/top_<level>_plan.jpg``),
- ``exterior/``: the exterior views (``final/<project>/ext_<n>_final_preview.jpg``, else the render previews),
- ``drawings/``: the reading check's comparison sheets drawn again with the pod's top-downs as panel 4 (panel 1 the
  source drawing without its grid and dimensions, ``sheets.is_grid_or_dimension``) and ``reading_check.md``.
How: ``out_dir`` is the local reading of the same commit (it holds the converted DXF the pod does not send back).
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path


def _renders(results: Path, project: str) -> tuple[list[Path], list[Path]]:
    tops = sorted((results / "renders" / project).glob("top_*_plan.jpg"))
    ext = sorted((results / "final" / project).glob("ext_*_final_preview.jpg"))
    if not ext:
        ext = sorted((results / "renders" / project).glob("ext_*_preview.jpg"))
    return tops, ext


def _ext_name(p: Path) -> str:
    m = re.match(r"(ext_\d+)", p.name)
    return f"{m.group(1)}.jpg" if m else p.name


def pack(out_dir, results, project: str, dest) -> Path:
    import wenart.reading_check as RC
    from wenart.reading_check import sheets as SH

    out_dir, results, dest = Path(out_dir), Path(results), Path(dest)
    res = RC.check(out_dir)
    RC.write(out_dir, res)
    tops, ext = _renders(results, project)
    sheets = SH.draw(out_dir, res, renders=str(results / "renders" / project) if tops else None)
    root = dest.stem
    dest.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
        for p in tops:
            z.write(p, f"{root}/top_down/{p.name}")
        for p in ext:
            z.write(p, f"{root}/exterior/{_ext_name(p)}")
        for p in sheets:
            z.write(p, f"{root}/drawings/{Path(p).name}")
        md = out_dir / "reading_check" / "reading_check.md"
        if md.is_file():
            z.write(md, f"{root}/drawings/reading_check.md")
    return dest
