"""document_record_inspector.cli.main — CLI for document pipeline inspection.

Canonical invocation::

    python -m document_record_inspector.cli inspect --document-id <id>
    python -m document_record_inspector.cli health

stdout  : canonical JSON only (sort_keys, compact, one trailing newline)
stderr  : error messages only, no tracebacks
exit 0  : success
exit 1  : input / service error
exit 2  : unrecognised command (argparse)

DB connectivity
---------------
In standalone mode (no ``DATABASE_URL`` set, or no DB reachable) ``inspect``
returns a valid empty response with ``document: null``.  To get real data,
set ``DATABASE_URL`` to a PostgreSQL DSN and ensure the TechVault schema is
present.  The platform integration path (FastAPI + adapter) is the primary
production path; the CLI is provided for scripted forensic use.
"""
from __future__ import annotations

import argparse
import sys

from ..core.determinism import canonical_json
from ..core.service import health_service, inspect_document


def _emit(obj: object) -> None:
    """Write canonical JSON to stdout with a trailing newline."""
    sys.stdout.write(canonical_json(obj) + "\n")


def _die(message: str, code: int = 1) -> None:
    """Write an error message to stderr and exit."""
    sys.stderr.write(f"error: {message}\n")
    sys.exit(code)


def _get_db():
    """Return a SQLAlchemy Session from DATABASE_URL, or None if unavailable.

    This is the CLI-specific DB factory.  It tries to import the TechVault
    session factory from ``backend.techvault.app.db.session``; if that module
    is not on the path (standalone mode) or ``DATABASE_URL`` is not set, it
    falls back to ``None`` so the service returns an empty deterministic result.
    """
    import os  # noqa: PLC0415

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return None

    try:
        from sqlalchemy import create_engine  # noqa: PLC0415
        from sqlalchemy.orm import sessionmaker  # noqa: PLC0415

        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        return Session()
    except Exception:  # noqa: BLE001
        return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m document_record_inspector.cli",
        description="document_record_inspector — forensic inspection CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Return tool health status as JSON.")

    inspect_cmd = subparsers.add_parser(
        "inspect",
        help="Inspect a single document across all pipeline stages.",
    )
    inspect_cmd.add_argument(
        "--document-id",
        required=True,
        metavar="DOCUMENT_ID",
        help="The document_id to inspect (exact match).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "health":
        _emit(health_service())
        return 0

    if args.command == "inspect":
        db = _get_db()
        session_opened = db is not None
        try:
            result = inspect_document(args.document_id, db)
            _emit(result.model_dump())
            return 0
        except ValueError as exc:
            _die(str(exc))
        finally:
            if session_opened and db is not None:
                db.close()

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

