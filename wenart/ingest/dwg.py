"""DWG -> DXF conversion with open-source converters.

Order: LibreDWG ``dwg2dxf`` (command line, flags from its man page:
``dwg2dxf -y -o OUT.dxf IN.dwg``), then the ``ezdwg`` Python package
(``ezdwg.to_dxf(dwg_path, dxf_path)``, PyPI 0.12.x). Every result is read
back with ``ezdxf.recover.readfile`` so the audit findings are reported with
the converter string. When no converter is installed the caller gets a
``ConverterNotFound`` error with a clear message; the pipeline turns that
into ``status: needs_review`` for the project.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from ezdxf import recover


class ConverterNotFound(RuntimeError):
    """No DWG converter (dwg2dxf, ezdwg) is available on this machine."""


class ConversionError(RuntimeError):
    """A converter ran but produced no readable DXF."""


def available_converters() -> list[str]:
    """Names of the converters that can be used here, in preference order."""
    found = []
    if shutil.which("dwg2dxf"):
        found.append("dwg2dxf")
    try:
        import ezdwg  # noqa: F401
        found.append("ezdwg")
    except ImportError:
        pass
    return found


def _dwg2dxf_version() -> str:
    try:
        out = subprocess.run(["dwg2dxf", "--version"], capture_output=True, text=True, timeout=30)
        first = (out.stdout or out.stderr).strip().splitlines()
        return first[0] if first else "dwg2dxf"
    except (OSError, subprocess.SubprocessError):
        return "dwg2dxf"


def _run_dwg2dxf(dwg_path: Path, dxf_path: Path) -> str:
    cmd = ["dwg2dxf", "-y", "-o", str(dxf_path), str(dwg_path)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if result.returncode != 0 or not dxf_path.is_file():
        raise ConversionError(f"dwg2dxf failed (exit {result.returncode}): {result.stderr.strip()[:500]}")
    return f"libredwg {_dwg2dxf_version()}"


def _run_ezdwg(dwg_path: Path, dxf_path: Path) -> str:
    import ezdwg

    ezdwg.to_dxf(str(dwg_path), str(dxf_path))
    if not dxf_path.is_file():
        raise ConversionError("ezdwg.to_dxf produced no file")
    version = getattr(ezdwg, "__version__", "unknown")
    return f"ezdwg {version}"


def dwg_to_dxf(path: str | Path, out_dir: Optional[str | Path] = None) -> tuple[Path, str]:
    """Convert ``path`` (a .dwg) to DXF next to it or into ``out_dir``.

    Returns ``(dxf_path, converter_string)``; the converter string also lists
    the ezdxf audit result (``"libredwg dwg2dxf 0.13.3; audit: 0 errors, 2 fixes"``).
    Raises ``ConverterNotFound`` or ``ConversionError``.
    """
    dwg_path = Path(path)
    if not dwg_path.is_file():
        raise FileNotFoundError(dwg_path)
    out_dir = Path(out_dir) if out_dir else dwg_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    dxf_path = out_dir / (dwg_path.stem + ".dxf")

    converters = available_converters()
    if not converters:
        raise ConverterNotFound(
            f"cannot convert {dwg_path.name}: no DWG converter found. Install LibreDWG (dwg2dxf on PATH) "
            "or the ezdwg Python package; on the pod this is done by scripts/pod_setup_recognition.sh")
    errors = []
    for name in converters:
        try:
            converter = _run_dwg2dxf(dwg_path, dxf_path) if name == "dwg2dxf" else _run_ezdwg(dwg_path, dxf_path)
            break
        except (ConversionError, subprocess.SubprocessError, OSError, Exception) as exc:  # noqa: BLE001
            errors.append(f"{name}: {exc}")
    else:
        raise ConversionError("; ".join(errors))

    try:
        _, auditor = recover.readfile(str(dxf_path))
    except Exception as exc:  # noqa: BLE001 - ezdxf raises several types
        raise ConversionError(f"{converter}: output is not readable by ezdxf: {exc}") from exc
    audit = f"audit: {len(auditor.errors)} errors, {len(auditor.fixes)} fixes"
    if auditor.has_errors:
        details = "; ".join(str(e.message) for e in auditor.errors[:5])
        audit += f" ({details})"
    return dxf_path, f"{converter}; {audit}"
