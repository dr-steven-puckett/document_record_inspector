"""document_record_inspector.api.schemas — Pydantic request/response models."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    tool_id: str


# ---------------------------------------------------------------------------
# Counts sub-model
# ---------------------------------------------------------------------------


class InspectionCounts(BaseModel):
    files: int
    chunks: int
    embeddings: int
    summaries: int
    ingest_runs: int


# ---------------------------------------------------------------------------
# Row projections
# ---------------------------------------------------------------------------


class DocumentRow(BaseModel):
    document_id: str
    library_id: Optional[str] = None
    group_id: Optional[str] = None
    security_level: Optional[str] = None
    doc_type: Optional[str] = None
    original_filename: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    source_uri: Optional[str] = None
    ingested_at: Optional[str] = None
    ingest_version: Optional[str] = None
    content_sha256: Optional[str] = None
    size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
    status: Optional[str] = None


class DocumentFileRow(BaseModel):
    id: Optional[str] = None
    document_id: Optional[str] = None
    role: Optional[str] = None
    rel_path: Optional[str] = None
    file_ext: Optional[str] = None
    sha256: Optional[str] = None
    size_bytes: Optional[int] = None
    created_at: Optional[str] = None


class ChunkRow(BaseModel):
    id: Optional[str] = None
    document_id: Optional[str] = None
    chunk_index: Optional[int] = None
    chunk_id: Optional[str] = None
    # text is gated by include_text; null when suppressed
    text: Optional[str] = None
    token_count: Optional[int] = None
    char_count: Optional[int] = None
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    section_path: Optional[str] = None
    created_at: Optional[str] = None


class EmbeddingRow(BaseModel):
    id: Optional[str] = None
    chunk_id: Optional[str] = None
    chunk_index: Optional[int] = None
    embedding_model: Optional[str] = None
    embedding_dim: Optional[int] = None
    # vector is gated by include_vectors; null when suppressed
    vector: Optional[Any] = None
    created_at: Optional[str] = None


class SummaryRow(BaseModel):
    id: Optional[str] = None
    document_id: Optional[str] = None
    summary_prompt_id: Optional[str] = None
    output_type: Optional[str] = None
    model_used: Optional[str] = None
    provider: Optional[str] = None
    security_level: Optional[str] = None
    content: Optional[str] = None
    content_sha256: Optional[str] = None
    created_at: Optional[str] = None


class IngestRunRow(BaseModel):
    id: Optional[str] = None
    document_id: Optional[str] = None
    library_id: Optional[str] = None
    group_id: Optional[str] = None
    security_level: Optional[str] = None
    requested_by: Optional[str] = None
    status: Optional[str] = None
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    metrics_json: Optional[str] = None


# ---------------------------------------------------------------------------
# Top-level inspection response
# ---------------------------------------------------------------------------


class InspectionResponse(BaseModel):
    document: Optional[DocumentRow] = None
    files: list[DocumentFileRow] = Field(default_factory=list)
    chunks: list[ChunkRow] = Field(default_factory=list)
    embeddings: list[EmbeddingRow] = Field(default_factory=list)
    summaries: list[SummaryRow] = Field(default_factory=list)
    ingest_runs: list[IngestRunRow] = Field(default_factory=list)
    counts: InspectionCounts = Field(
        default_factory=lambda: InspectionCounts(
            files=0, chunks=0, embeddings=0, summaries=0, ingest_runs=0
        )
    )
