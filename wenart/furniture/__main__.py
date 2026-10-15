"""``python -m wenart.furniture fit ...`` dispatches to ``wenart.furniture.fit`` (same arguments).

Milestone 13 (docs/milestone13.md §13.1, track T1): ``fit`` takes ``--licence-mode commercial|relaxed`` and
``--project <dir>`` (the brief: the licence mode and the ``furnished_rooms`` settings of the size snap; by default
the building's ``project.source_folder`` when that folder exists); ``licence-fields <catalog.json> ...`` writes the
licence fields (``licence_url``, ``licence_declared_by``, ``licence_flag``, ``commercial_safe``, ``attribution``) onto
the existing entries of the catalogue files by script (``wenart.furniture.catalog.write_licence_fields``), never by
hand, and prints the counts per flag.

The layout step has its own entry (``python -m wenart.furniture.layout``).

The refit (``wenart/run/stages.py`` ``refit``: ``python -m wenart.furniture.fit <building_decor.json> --source
building.json [--completion completion.json]``, the same ``fit`` entry) fits EVERY piece again
(``fit.fit_building``): a drawn piece the layout re-solved as part of its drawn group (Milestone 13 D5,
``solver._resolved_dict``: ``asset`` None, ``drawn_group``, ``adjusted_by_ai`` by the solver, the drawn values
kept) gets its model, module or parametric build like any other piece, never ``none``; the refit's locked check
(``fit.locked_check`` -> ``wenart.furniture.locked.check``) accepts such a member within
``groups.GROUP_MEMBER_MOVE_MAX_M`` (0.5 m) of its drawn centre and a real product size, and refuses more
(verified in ``tests/test_groups_edits.py``, round 2 of the build).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def licence_fields_main(argv: list[str]) -> int:
    from wenart.furniture import catalog as C

    paths = [Path(a) for a in argv if not a.startswith("-")]
    if not paths:
        paths = [C.CATALOG_PATH, C.library_path(C.CATALOG_PATH)]
    for path in paths:
        if not path.is_file():
            print(f"licence-fields: {path} is not a file", file=sys.stderr)
            return 2
        counts = C.write_licence_fields(path)
        print(json.dumps(counts, sort_keys=True))
    return 0


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "fit":
        from wenart.furniture.fit import main as fit_main
        return fit_main(argv[1:])
    if argv and argv[0] == "licence-fields":
        return licence_fields_main(argv[1:])
    print("usage: python -m wenart.furniture fit <building.json> --out <building_fitted.json> "
          "[--catalog catalog.json] [--assets assets] [--style style.json] [--licence-mode commercial|relaxed] "
          "[--project projects/<p>]\n"
          "       python -m wenart.furniture licence-fields [<catalog.json> <catalog_library.json>] "
          "(Milestone 13: write the licence fields of the existing entries)\n"
          "       python -m wenart.furniture.layout ... (AI layout for empty rooms)")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
