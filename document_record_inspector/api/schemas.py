"""document_record_inspector.api.schemas — Pydantic response models.

All fields use str for UUIDs and ISO timestamps to guarantee byte-identical
serialization across platforms.  The embedding vector is intentionally omitted
because 2048-float arrays are too large for a diagnostic response.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Row models (one per TechVault table row)
# ---------------------------------------------------------------------------


class DocumentRow(BaseModel):
    """Single row from the documents table."""

    document_id: str
    library_id: str
    group_id: str
    security_level: str
    doc_type: str
    original_filename: str | None = None
    title: str | None = None
    author: str | None = None
    source_uri: str | None = None
    ingested_at: str
    ingest_version: str
    content_sha256: str
    size_bytes: int
    mime_type: str | None = None
    page_count: int | None = None
    language: str | None = None
    status: str


class DocumentFileRow(BaseModel):
    """Single row from the document_files table."""

    id: str
    document_id: str
    role: str
    rel_path: str
    file_ext: str
    sha256: str
    size_bytes: int
    created_at: str


class ChunkRow(BaseModel):
    """Single row from the chunks table."""

    id: str
    document_id: str
    chunk_index: int
    chunk_id: str
    text: str
    token_count: int | None = None
    char_count: int
    page_start: int | None = None
    page_end: int | None = None
    section_path: str | None = None
    created_at: str


class EmbeddingRow(BaseModel):
    """Single row from the embeddings table.

    The ``chunk_id`` field is the UUID primary key of the parent chunk
    (``chunks.id``), not the stable text ``chunk_id`` column.

    The embedding vector is intentionally omitted — 2048 floats would dwarf
    all other diagnostic data and are not needed for pipeline inspection.
    """

    id: str
    chunk_id: str  # chunks.id (UUID as text)
    embedding_model: str
    embedding_dim: int
    created_at: str


class SummaryRow(BaseModel):
    """Single row from the summaries table."""

    id: str
    document_id: str
    summary_prompt_id: str
    output_type: str
    model_used: str
    provider: str
    security_level: str
    content: str
    content_sha256: str
    created_at: str


class IngestRunRow(BaseModel):
    """Single row from the ingest_runs table.

    ``document_id`` is nullable in the schema (run may not yet be associated
    with a produced document).  ``metrics_json`` is stored as JSONB and
    returned as a dict.
    """

    id: str
    document_id: str | None = None
    library_id: str
    group_id: str
    security_level: str
    requested_by: str | None = None
    status: str
    error_message: str | None = None
    started_at: str
    ended_at: str | None = None
    metrics_json: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Composite / response models
# ---------------------------------------------------------------------------


class QueryInfo(BaseModel):
    """Echo of the lookup key used to produce this inspection record."""

    document_id: str


class DiagnosticsModel(BaseModel):
    """Deterministic rule-based inspection findings.

    All counts exactly match the lengths of the returned row collections.
    ``possible_issues`` is a stably sorted list of machine-friendly strings.
    """

    document_found: bool
    has_files: bool
    has_chunks: bool
    has_embeddings: bool
    has_summaries: bool
    ingest_run_count: int = Field(ge=0)
    chunk_count: int = Field(ge=0)
    embedding_count: int = Field(ge=0)
    summary_count: int = Field(ge=0)
    file_count: int = Field(ge=0)
    possible_issues: list[str]


class InspectionResponse(BaseModel):
    """Canonical forensic inspection record for one document.

    When the document does not exist in TechVault, ``document`` is ``null``
    and all collection fields are empty arrays.  The response is still valid
    and deterministic — ``diagnostics.possible_issues`` will contain
    ``"document_missing"``.

    Ordering rules (enforced by the service layer):
    - document_files: ascending by ``id``
    - chunks: ascending by ``chunk_index``, then ``id``
    - embeddings: ascending by ``chunk_id``, then ``id``
    - summaries: ascending by ``id``
    - ingest_runs: descending by ``started_at``, then ascending by ``id``
    """

    query: QueryInfo
    document: DocumentRow | None = None
    document_files: list[DocumentFileRow]
    chunks: list[ChunkRow]
    embeddings: list[EmbeddingRow]
    summaries: list[SummaryRow]
    ingest_runs: list[IngestRunRow]
    diagnostics: DiagnosticsModel

