"""document_record_inspector.cli.main — argparse CLI for the document_record_inspector tool.

Canonical invocation: python -m document_record_inspector.cli.main <command> [options]

Commands
--------
health  [--catalog-file <path>]
inspect --document-id <ID>
        [--catalog-file <path>]
        [--include-text]
        [--include-vectors]

stdout: JSON only (canonical: sort_keys, compact, one trailing newline)
stderr: error messages only, no tracebacks
exit 0 on success, exit 1 on error
"""
from __future__ import annotations

import argparse
import json
import sys


def _emit(obj: dict) -> None:
    """Write canonical JSON to stdout."""
    sys.stdout.write(
        json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    )


def _die(message: str) -> None:
    """Write error message to stderr and exit 1."""
    sys.stderr.write(f"error: {message}\n")
    sys.exit(1)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------


def _cmd_health(_args: argparse.Namespace) -> None:
    from document_record_inspector.core import service  # noqa: PLC0415

    try:
        result = service.health()
    except (ValueError, PermissionError) as exc:
        _die(str(exc))
        return
    _emit(result)


def _cmd_inspect(args: argparse.Namespace) -> None:
    from document_record_inspector.core import service  # noqa: PLC0415

    try:
        if args.catalog_file:
            from document_record_inspector.core.catalog_loader import load_fixture  # noqa: PLC0415
            fixture = load_fixture(args.catalog_file)
            result = service.inspect_from_fixture(
                fixture,
                args.document_id,
                include_text=args.include_text,
                include_vectors=args.include_vectors,
            )
        else:
            import os  # noqa: PLC0415
            from sqlalchemy import create_engine  # noqa: PLC0415
            from sqlalchemy.orm import sessionmaker  # noqa: PLC0415

            url = os.environ.get("DATABASE_URL")
            if not url:
                _die(
                    "DATABASE_URL is not set. "
                    "Use --catalog-file for standalone mode, or export DATABASE_URL."
                )
                return
            engine = create_engine(url, pool_pre_ping=True)
            Session = sessionmaker(bind=engine, expire_on_commit=False)
            db = Session()
            try:
                result = service.inspect_from_db(
                    db,
                    args.document_id,
                    include_text=args.include_text,
                    include_vectors=args.include_vectors,
                )
            finally:
                db.close()

    except (ValueError, PermissionError) as exc:
        _die(str(exc))
        return
    _emit(result)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m document_record_inspector.cli.main",
        description="document_record_inspector tool CLI",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ── health ──────────────────────────────────────────────────────────────
    health_p = subparsers.add_parser("health", help="Return tool health status")
    health_p.add_argument(
        "--catalog-file",
        dest="catalog_file",
        default="",
        metavar="PATH",
        help="(accepted for contract compliance; not used by health)",
    )

    # ── inspect ──────────────────────────────────────────────────────────────
    inspect_p = subparsers.add_parser(
        "inspect",
        help="Return full record view for one document",
    )
    inspect_p.add_argument(
        "--document-id",
        dest="document_id",
        required=True,
        metavar="ID",
        help="The document_id (SHA-256 hex) to inspect",
    )
    inspect_p.add_argument(
        "--catalog-file",
        dest="catalog_file",
        default="",
        metavar="PATH",
        help="Relative path to a fixture JSON file (standalone / test mode)",
    )
    inspect_p.add_argument(
        "--include-text",
        dest="include_text",
        action="store_true",
        default=False,
        help="Include chunk text in output (default: false)",
    )
    inspect_p.add_argument(
        "--include-vectors",
        dest="include_vectors",
        action="store_true",
        default=False,
        help="Include embedding vectors in output (default: false)",
    )

    return parser


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "health":
        _cmd_health(args)
    elif args.command == "inspect":
        _cmd_inspect(args)
    else:
        _die(f"Unknown command: {args.command!r}")


if __name__ == "__main__":
    main()
