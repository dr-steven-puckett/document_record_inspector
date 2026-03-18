from __future__ import annotations

import argparse
import json
import sys

from ..core.catalog_loader import load_catalog
from ..core.service import health_service


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tool-cli")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health")
    search = subparsers.add_parser("search")
    search.add_argument("--catalog-file", required=True)
    search.add_argument("--query", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "health":
        print(json.dumps(health_service(), sort_keys=True))
        return 0

    if args.command == "search":
        try:
            items = load_catalog(args.catalog_file)
            print(json.dumps({"items": items, "query": args.query}, sort_keys=True))
            return 0
        except Exception as exc:  # noqa: BLE001
            print(str(exc), file=sys.stderr)
            return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
