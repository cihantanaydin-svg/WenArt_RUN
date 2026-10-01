"""CLI for the asset fetcher.

``python -m wenart.assets fetch --style style.json --assets assets [--size 2k] [--strict]``
    downloads every texture set and the HDRI of a style profile (idempotent);
    failures are printed and, with ``--strict``, make the exit code 1.
``python -m wenart.assets verify``
    lists the vocabulary ids against the APIs (no download).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from wenart.assets.fetch import fetch_for_style, verify_vocabulary


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="CC0 texture and HDRI fetcher")
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch", help="download the assets of a style profile")
    fetch.add_argument("--style", required=True, help="style.json from python -m wenart.style")
    fetch.add_argument("--assets", default="assets", help="assets folder (default: assets)")
    fetch.add_argument("--size", default="2k", help="texture resolution: 1k, 2k, 4k (default 2k)")
    fetch.add_argument("--hdri-size", default=None, help="HDRI resolution (default: same as --size)")
    fetch.add_argument("--strict", action="store_true", help="exit 1 when any asset failed")
    sub.add_parser("verify", help="check that every vocabulary id exists on the APIs")
    args = parser.parse_args(argv)

    if args.command == "verify":
        rows = verify_vocabulary()
        missing = 0
        for row in rows:
            flag = "ok" if row["exists"] else "MISSING"
            missing += not row["exists"]
            print(f"{row['kind']:<8} {row['slug']:<20} {row['source']:<10} {row['id']:<30} {str(row['size_m']):<16} {flag}")
        print(f"{len(rows)} ids, {missing} missing")
        return 1 if missing else 0

    style = json.loads(Path(args.style).read_text(encoding="utf-8"))
    result = fetch_for_style(style, Path(args.assets), size=args.size, hdri_size=args.hdri_size)
    print(f"{len(result['textures'])} texture sets, {len(result['hdris'])} HDRIs ready in {args.assets}; "
          f"{len(result['failed'])} failed")
    for asset_id, reason in result["failed"].items():
        print(f"  failed {asset_id}: {reason}")
    return 1 if (args.strict and result["failed"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
