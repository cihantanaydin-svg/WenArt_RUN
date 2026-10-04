"""``python -m wenart.furniture fit ...`` dispatches to ``wenart.furniture.fit`` (same arguments).

The layout step has its own entry (``python -m wenart.furniture.layout``).
"""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "fit":
        from wenart.furniture.fit import main as fit_main
        return fit_main(argv[1:])
    print("usage: python -m wenart.furniture fit <building.json> --out <building_fitted.json> "
          "[--catalog catalog.json] [--assets assets] [--style style.json]\n"
          "       python -m wenart.furniture.layout ... (AI layout for empty rooms)")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
