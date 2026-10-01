"""CLI: ``python -m wenart.style <project_dir or building.json> --out style.json``.

Reads ``brief.yaml`` from a project folder, or ``project.brief`` from a
building JSON, and writes one ``style.json`` per style text (the second and
following go to ``style_2.json`` ...). Prints what was matched and assumed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from wenart.style.profile import profiles_from_brief, write_profiles


def load_brief(source: Path) -> dict | None:
    """The brief dict of a project folder (``brief.yaml``) or of a building JSON."""
    import yaml  # lazy: the package must import where PyYAML is missing (Blender)

    if source.is_dir():
        brief_path = source / "brief.yaml"
        if not brief_path.is_file():
            return None
        return yaml.safe_load(brief_path.read_text(encoding="utf-8")) or {}
    if source.suffix.lower() == ".json":
        building = json.loads(source.read_text(encoding="utf-8"))
        return building.get("project", {}).get("brief")
    if source.suffix.lower() in (".yaml", ".yml"):
        return yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    raise SystemExit(f"{source}: expected a project folder, a building.json or a brief.yaml")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Brief -> style profile (style.json)")
    parser.add_argument("source", help="project folder with brief.yaml, or a building.json")
    parser.add_argument("--out", default="style.json", help="output file (others: <stem>_2.json ...)")
    args = parser.parse_args(argv)

    brief = load_brief(Path(args.source))
    profiles = profiles_from_brief(brief)
    paths = write_profiles(profiles, Path(args.out))
    for profile, path in zip(profiles, paths):
        print(f"{path}: floor {profile['floor']['material']}, walls {profile['walls']['material']}, "
              f"light {profile['lighting']['mood']} ({profile['lighting']['hdri']})")
        print(f"  matched: {profile['matched_terms']}")
        if profile["unmatched_terms"]:
            print(f"  unmatched: {profile['unmatched_terms']}")
        for warning in profile["warnings"]:
            print(f"  note: {warning}")
    if len(profiles) > 1:
        print(f"{len(profiles)} styles in the brief: the render job renders {paths[0].name} and notes the others",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
