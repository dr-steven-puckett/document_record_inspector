"""document_record_inspector.core.catalog_loader — safe fixture loading for standalone / test mode.

This loader reads a JSON fixture file that contains the pre-fetched inspection
data for a single document.  It is used by the CLI standalone mode and tests.

Fixture format (all fields match the DB column names):

{
  "document": { ... documents row ... },
  "files":    [ ... document_files rows ... ],
  "chunks":   [ ... chunks rows ... ],
  "embeddings": [
    { ... embeddings row ..., "chunk_index": <int from join> }
  ],
  "summaries":   [ ... summaries rows ... ],
  "ingest_runs": [ ... ingest_runs rows ... ]
}

Path safety rules (same as template standard):
  - reject absolute paths
  - reject path traversal (any component is "..")
  - reject null bytes in path
  - reject non-UTF-8 filenames or content
"""
from __future__ import annotations

import json
import os


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------


def _check_path_safety(raw_path: str) -> None:
    """Raise ValueError if *raw_path* is unsafe."""
    from pathlib import PurePosixPath  # local import keeps namespace clean

    if "\x00" in raw_path:
        raise ValueError(f"Catalog path contains null bytes: {raw_path!r}")

    try:
        raw_path.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(
            f"Catalog path is not valid UTF-8 (contains surrogates): {raw_path!r}"
        ) from exc

    if os.path.isabs(raw_path):
        raise ValueError(f"Catalog path must not be absolute: {raw_path!r}")

    for part in PurePosixPath(raw_path.replace("\\", "/")).parts:
        if part == "..":
            raise ValueError(
                f"Catalog path contains path traversal component: {raw_path!r}"
            )


# ---------------------------------------------------------------------------
# Fixture validation
# ---------------------------------------------------------------------------

_REQUIRED_TOP_LEVEL_KEYS = frozenset(
    {"document", "files", "chunks", "embeddings", "summaries", "ingest_runs"}
)


def _validate_fixture(data: object) -> dict:
    """Validate the top-level structure of a fixture file.

    Returns the validated dict on success.
    """
    if not isinstance(data, dict):
        raise ValueError(
            f"Fixture root must be a JSON object, got {type(data).__name__}"
        )

    missing = _REQUIRED_TOP_LEVEL_KEYS - set(data.keys())
    if missing:
        raise ValueError(
            f"Fixture is missing required top-level keys: {sorted(missing)}"
        )

    # document must be a dict or null
    if data["document"] is not None and not isinstance(data["document"], dict):
        raise ValueError(
            f"Fixture 'document' must be a JSON object or null, "
            f"got {type(data['document']).__name__}"
        )

    # collections must be arrays
    for key in ("files", "chunks", "embeddings", "summaries", "ingest_runs"):
        if not isinstance(data[key], list):
            raise ValueError(
                f"Fixture '{key}' must be a JSON array, "
                f"got {type(data[key]).__name__}"
            )

    return data  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Public loader
# ---------------------------------------------------------------------------


def load_fixture(catalog_file: str) -> dict:
    """Load and validate a document inspection fixture from *catalog_file*.

    Parameters
    ----------
    catalog_file:
        Relative path to a UTF-8 JSON file containing a single-document
        inspection fixture.

    Returns
    -------
    dict
        Validated fixture dict with keys: document, files, chunks,
        embeddings, summaries, ingest_runs.

    Raises
    ------
    ValueError
        On any path safety violation, parse error, or validation failure.
    """
    _check_path_safety(catalog_file)

    try:
        with open(catalog_file, encoding="utf-8") as fh:
            raw = json.load(fh)
    except FileNotFoundError:
        raise ValueError(f"Fixture file not found: {catalog_file!r}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Fixture file is not valid JSON: {catalog_file!r}: {exc}")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Fixture file is not valid UTF-8: {catalog_file!r}: {exc}")

    return _validate_fixture(raw)
