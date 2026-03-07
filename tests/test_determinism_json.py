"""Tests for deterministic JSON output (byte-identical on repeated calls)."""
from __future__ import annotations

import json

from document_record_inspector.core import service
from document_record_inspector.core.determinism import canonical_json, canonical_json_bytes

DOC_ID = "aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff6666aaaa1111bbbb2222"


def _make_fixture() -> dict:
    return {
        "document": {"document_id": DOC_ID, "title": "Test", "status": "active"},
        "files": [
            {"id": "f2", "role": "primary", "rel_path": "z.pdf"},
            {"id": "f1", "role": "aux",     "rel_path": "a.txt"},
        ],
        "chunks": [
            {"id": "c2", "chunk_index": 1, "text": "second"},
            {"id": "c1", "chunk_index": 0, "text": "first"},
        ],
        "embeddings": [
            {"id": "e2", "chunk_index": 1, "embedding_model": "model-a", "vector": [0.1, 0.2]},
            {"id": "e1", "chunk_index": 0, "embedding_model": "model-a", "vector": [0.3, 0.4]},
        ],
        "summaries": [
            {"id": "s1", "output_type": "executive", "created_at": "2026-01-01"},
        ],
        "ingest_runs": [
            {"id": "r1", "started_at": "2026-01-01"},
        ],
    }


class TestCanonicalJson:
    def test_canonical_json_sort_keys(self):
        obj = {"z": 1, "a": 2, "m": 3}
        result = canonical_json(obj)
        parsed = json.loads(result)
        assert list(parsed.keys()) == sorted(parsed.keys())

    def test_canonical_json_trailing_newline(self):
        result = canonical_json({"k": "v"})
        assert result.endswith("\n")
        assert result.count("\n") == 1

    def test_canonical_json_bytes_utf8(self):
        obj = {"key": "valüe"}
        b = canonical_json_bytes(obj)
        assert isinstance(b, bytes)
        assert b.decode("utf-8")

    def test_canonical_json_byte_identical_on_repeat(self):
        obj = {"b": 2, "a": 1, "c": 3}
        r1 = canonical_json(obj)
        r2 = canonical_json(obj)
        assert r1 == r2


class TestServiceDeterminism:
    def test_inspect_byte_identical_on_repeat(self):
        fixture = _make_fixture()
        r1 = service.inspect_from_fixture(fixture, DOC_ID)
        r2 = service.inspect_from_fixture(fixture, DOC_ID)
        assert canonical_json(r1) == canonical_json(r2)

    def test_inspect_include_text_false_suppresses_text(self):
        fixture = _make_fixture()
        result = service.inspect_from_fixture(fixture, DOC_ID, include_text=False)
        for chunk in result["chunks"]:
            assert chunk["text"] is None

    def test_inspect_include_text_true_exposes_text(self):
        fixture = _make_fixture()
        result = service.inspect_from_fixture(fixture, DOC_ID, include_text=True)
        texts = [c["text"] for c in result["chunks"]]
        assert "first" in texts
        assert "second" in texts

    def test_inspect_include_vectors_false_suppresses_vector(self):
        fixture = _make_fixture()
        result = service.inspect_from_fixture(fixture, DOC_ID, include_vectors=False)
        for emb in result["embeddings"]:
            assert emb["vector"] is None

    def test_inspect_include_vectors_true_exposes_vector(self):
        fixture = _make_fixture()
        result = service.inspect_from_fixture(fixture, DOC_ID, include_vectors=True)
        vectors = [e["vector"] for e in result["embeddings"]]
        assert all(v is not None for v in vectors)

    def test_inspect_shuffled_input_same_output(self):
        import random
        fixture_a = _make_fixture()
        fixture_b = _make_fixture()
        for key in ("files", "chunks", "embeddings", "summaries", "ingest_runs"):
            random.shuffle(fixture_b[key])
        r_a = service.inspect_from_fixture(fixture_a, DOC_ID)
        r_b = service.inspect_from_fixture(fixture_b, DOC_ID)
        assert canonical_json(r_a) == canonical_json(r_b)

    def test_not_found_raises_value_error(self):
        fixture = _make_fixture()
        import pytest
        with pytest.raises(ValueError, match="not found"):
            service.inspect_from_fixture(fixture, "nonexistent-id")

    def test_empty_document_id_raises_value_error(self):
        fixture = _make_fixture()
        import pytest
        with pytest.raises(ValueError, match="non-empty"):
            service.inspect_from_fixture(fixture, "")

    def test_health_deterministic(self):
        r1 = service.health()
        r2 = service.health()
        assert canonical_json(r1) == canonical_json(r2)
        assert r1["tool_id"] == "document_record_inspector"
