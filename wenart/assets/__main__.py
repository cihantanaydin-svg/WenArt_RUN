"""CLI for the asset fetcher.

``python -m wenart.assets fetch --style style.json --assets assets [--size 2k] [--strict]``
    downloads every texture set and the HDRI of a style profile (idempotent);
    failures are printed and, with ``--strict``, make the exit code 1.
``python -m wenart.assets verify``
    lists the vocabulary ids against the APIs (no download).
``python -m wenart.assets models fetch --assets assets [--ids id ...] [--size 1k]``
    downloads the furniture catalogue's CC0 Poly Haven models (glTF + textures)
    into ``assets/models/`` and records them in the manifest with measured boxes.
``python -m wenart.assets models verify``
    lists the catalogue ids against the Poly Haven model listing (no download).
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
    models = sub.add_parser("models", help="CC0 furniture models of the catalogue (Milestone 4)")
    models.add_argument("action", choices=["fetch", "verify"])
    models.add_argument("--assets", default="assets", help="assets folder (default: assets)")
    models.add_argument("--ids", nargs="*", default=None, help="model ids (default: every catalogue id)")
    models.add_argument("--size", default="1k", help="glTF texture resolution: 1k, 2k, 4k (default 1k)")
    models.add_argument("--catalog", default=None, help="catalog.json (default: wenart/furniture/catalog.json)")
    models.add_argument("--strict", action="store_true", help="exit 1 when any model failed")
    args = parser.parse_args(argv)

    if args.command == "models":
        return _models(args)

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


def _models(args) -> int:
    from wenart.assets import models as M
    from wenart.assets import fetch as F
    from wenart.assets import web
    from wenart.furniture import catalog as C

    catalog = C.load(Path(args.catalog)) if args.catalog else C.load()
    ids = args.ids or catalog.ids()
    if args.action == "verify":
        rows = M.verify_catalog(ids)
        missing = 0
        for row in rows:
            flag = "ok" if row["exists"] else "MISSING"
            missing += not row["exists"]
            dims = row["dimensions_api_mm"]
            dims_s = " x ".join(f"{d / 1000:.3f}" for d in dims) + " m" if dims else "-"
            print(f"{row['id']:<28} {str(row['category']):<48} {dims_s:<26} {flag}")
        print(f"{len(rows)} ids, {missing} missing")
        return 1 if missing else 0
    failed = {}
    for asset_id in ids:
        try:
            entry = M.fetch_model(asset_id, Path(args.assets), size=args.size)
            print(M.summarise(entry))
        except (web.NetworkError, web.HTTPStatusError, F.AssetNotFound, F.LicenceError, KeyError, RuntimeError) as exc:
            failed[asset_id] = f"{type(exc).__name__}: {exc}"
            print(f"{asset_id:<28} FAILED: {exc}")
    total = M.total_size_bytes(Path(args.assets), ids)
    print(f"{len(ids) - len(failed)} models ready in {args.assets}/{M.MODELS_DIR} ({total / 1e6:.1f} MB); {len(failed)} failed")
    return 1 if (args.strict and failed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
