"""Tests for deterministic ordering invariants.

These tests run entirely in-memory against fixture data.
No database required.
"""
from __future__ import annotations

import random

import pytest

from document_record_inspector.core import service

DOC_ID = "aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff6666aaaa1111bbbb2222"

# ---------------------------------------------------------------------------
# Minimal fixture factory
# ---------------------------------------------------------------------------


def _make_fixture(
    files=None,
    chunks=None,
    embeddings=None,
    summaries=None,
    ingest_runs=None,
) -> dict:
    return {
        "document": {"document_id": DOC_ID, "title": "Test Doc", "status": "active"},
        "files": files or [],
        "chunks": chunks or [],
        "embeddings": embeddings or [],
        "summaries": summaries or [],
        "ingest_runs": ingest_runs or [],
    }


# ---------------------------------------------------------------------------
# Files ordering: role ASC, rel_path ASC, id ASC
# ---------------------------------------------------------------------------


class TestFilesOrdering:
    FILES_UNORDERED = [
        {"id": "f3", "role": "primary", "rel_path": "z.pdf"},
        {"id": "f1", "role": "aux",     "rel_path": "a.txt"},
        {"id": "f2", "role": "aux",     "rel_path": "b.txt"},
        {"id": "f4", "role": "primary", "rel_path": "a.pdf"},
    ]

    def test_files_sorted_role_then_rel_path(self):
        fixture = _make_fixture(files=self.FILES_UNORDERED)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        roles = [f["role"] for f in result["files"]]
        # aux comes before primary
        assert roles == ["aux", "aux", "primary", "primary"]

    def test_files_sorted_rel_path_within_role(self):
        fixture = _make_fixture(files=self.FILES_UNORDERED)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        aux_paths = [f["rel_path"] for f in result["files"] if f["role"] == "aux"]
        assert aux_paths == ["a.txt", "b.txt"]

    def test_files_id_tiebreaker(self):
        files = [
            {"id": "f2", "role": "primary", "rel_path": "same.pdf"},
            {"id": "f1", "role": "primary", "rel_path": "same.pdf"},
        ]
        fixture = _make_fixture(files=files)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        ids = [f["id"] for f in result["files"]]
        assert ids == ["f1", "f2"]

    def test_files_shuffle_independent(self):
        fixture_a = _make_fixture(files=list(self.FILES_UNORDERED))
        shuffled = list(self.FILES_UNORDERED)
        random.shuffle(shuffled)
        fixture_b = _make_fixture(files=shuffled)
        result_a = service.inspect_from_fixture(fixture_a, DOC_ID)
        result_b = service.inspect_from_fixture(fixture_b, DOC_ID)
        assert result_a["files"] == result_b["files"]


# ---------------------------------------------------------------------------
# Chunks ordering: chunk_index ASC, id ASC
# ---------------------------------------------------------------------------


class TestChunksOrdering:
    CHUNKS_UNORDERED = [
        {"id": "c3", "chunk_index": 2, "text": "chunk 2"},
        {"id": "c1", "chunk_index": 0, "text": "chunk 0"},
        {"id": "c2", "chunk_index": 1, "text": "chunk 1"},
    ]

    def test_chunks_sorted_by_chunk_index(self):
        fixture = _make_fixture(chunks=self.CHUNKS_UNORDERED)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        indexes = [c["chunk_index"] for c in result["chunks"]]
        assert indexes == [0, 1, 2]

    def test_chunks_id_tiebreaker(self):
        chunks = [
            {"id": "c2", "chunk_index": 0, "text": "text a"},
            {"id": "c1", "chunk_index": 0, "text": "text b"},
        ]
        fixture = _make_fixture(chunks=chunks)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        ids = [c["id"] for c in result["chunks"]]
        assert ids == ["c1", "c2"]

    def test_chunks_shuffle_independent(self):
        shuffled = list(self.CHUNKS_UNORDERED)
        random.shuffle(shuffled)
        r1 = service.inspect_from_fixture(_make_fixture(chunks=list(self.CHUNKS_UNORDERED)), DOC_ID)
        r2 = service.inspect_from_fixture(_make_fixture(chunks=shuffled), DOC_ID)
        assert r1["chunks"] == r2["chunks"]


# ---------------------------------------------------------------------------
# Embeddings ordering: chunk_index ASC, embedding_model ASC, id ASC
# ---------------------------------------------------------------------------


class TestEmbeddingsOrdering:
    EMBEDDINGS_UNORDERED = [
        {"id": "e3", "chunk_index": 1, "embedding_model": "model-b"},
        {"id": "e1", "chunk_index": 0, "embedding_model": "model-a"},
        {"id": "e4", "chunk_index": 1, "embedding_model": "model-a"},
        {"id": "e2", "chunk_index": 0, "embedding_model": "model-b"},
    ]

    def test_embeddings_sorted_chunk_index_then_model(self):
        fixture = _make_fixture(embeddings=self.EMBEDDINGS_UNORDERED)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        keys = [(e["chunk_index"], e["embedding_model"]) for e in result["embeddings"]]
        assert keys == [(0, "model-a"), (0, "model-b"), (1, "model-a"), (1, "model-b")]

    def test_embeddings_id_tiebreaker(self):
        embeddings = [
            {"id": "e2", "chunk_index": 0, "embedding_model": "model-a"},
            {"id": "e1", "chunk_index": 0, "embedding_model": "model-a"},
        ]
        fixture = _make_fixture(embeddings=embeddings)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        ids = [e["id"] for e in result["embeddings"]]
        assert ids == ["e1", "e2"]

    def test_embeddings_shuffle_independent(self):
        shuffled = list(self.EMBEDDINGS_UNORDERED)
        random.shuffle(shuffled)
        r1 = service.inspect_from_fixture(_make_fixture(embeddings=list(self.EMBEDDINGS_UNORDERED)), DOC_ID)
        r2 = service.inspect_from_fixture(_make_fixture(embeddings=shuffled), DOC_ID)
        assert r1["embeddings"] == r2["embeddings"]


# ---------------------------------------------------------------------------
# Summaries ordering: output_type ASC, created_at ASC, id ASC
# ---------------------------------------------------------------------------


class TestSummariesOrdering:
    SUMMARIES_UNORDERED = [
        {"id": "s3", "output_type": "general",   "created_at": "2026-01-01T10:00:00"},
        {"id": "s1", "output_type": "executive", "created_at": "2026-01-01T09:00:00"},
        {"id": "s2", "output_type": "executive", "created_at": "2026-01-01T10:00:00"},
    ]

    def test_summaries_sorted_output_type_then_created_at(self):
        fixture = _make_fixture(summaries=self.SUMMARIES_UNORDERED)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        keys = [(s["output_type"], s["created_at"]) for s in result["summaries"]]
        assert keys == [
            ("executive", "2026-01-01T09:00:00"),
            ("executive", "2026-01-01T10:00:00"),
            ("general",   "2026-01-01T10:00:00"),
        ]

    def test_summaries_id_tiebreaker(self):
        summaries = [
            {"id": "s2", "output_type": "general", "created_at": "2026-01-01T10:00:00"},
            {"id": "s1", "output_type": "general", "created_at": "2026-01-01T10:00:00"},
        ]
        fixture = _make_fixture(summaries=summaries)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        ids = [s["id"] for s in result["summaries"]]
        assert ids == ["s1", "s2"]


# ---------------------------------------------------------------------------
# Ingest runs ordering: started_at ASC, id ASC
# ---------------------------------------------------------------------------


class TestIngestRunsOrdering:
    RUNS_UNORDERED = [
        {"id": "r3", "started_at": "2026-01-03T00:00:00"},
        {"id": "r1", "started_at": "2026-01-01T00:00:00"},
        {"id": "r2", "started_at": "2026-01-02T00:00:00"},
    ]

    def test_runs_sorted_started_at(self):
        fixture = _make_fixture(ingest_runs=self.RUNS_UNORDERED)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        ids = [r["id"] for r in result["ingest_runs"]]
        assert ids == ["r1", "r2", "r3"]

    def test_runs_id_tiebreaker(self):
        runs = [
            {"id": "r2", "started_at": "2026-01-01T00:00:00"},
            {"id": "r1", "started_at": "2026-01-01T00:00:00"},
        ]
        fixture = _make_fixture(ingest_runs=runs)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        ids = [r["id"] for r in result["ingest_runs"]]
        assert ids == ["r1", "r2"]


# ---------------------------------------------------------------------------
# Counts
# ---------------------------------------------------------------------------


class TestCounts:
    def test_counts_match_collection_lengths(self):
        files = [{"id": "f1", "role": "primary", "rel_path": "a.pdf"}, {"id": "f2", "role": "aux", "rel_path": "b.txt"}]
        chunks = [{"id": "c1", "chunk_index": 0}, {"id": "c2", "chunk_index": 1}]
        embeddings = [{"id": "e1", "chunk_index": 0, "embedding_model": "m"}]
        summaries = [{"id": "s1", "output_type": "general", "created_at": "2026-01-01"}]
        runs = [{"id": "r1", "started_at": "2026-01-01"}]
        fixture = _make_fixture(files=files, chunks=chunks, embeddings=embeddings, summaries=summaries, ingest_runs=runs)
        result = service.inspect_from_fixture(fixture, DOC_ID)
        assert result["counts"]["files"] == 2
        assert result["counts"]["chunks"] == 2
        assert result["counts"]["embeddings"] == 1
        assert result["counts"]["summaries"] == 1
        assert result["counts"]["ingest_runs"] == 1
