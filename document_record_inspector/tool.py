"""
Agent-mode stub for document_record_inspector.

Provides TOOL_SPEC and run() as required by the TechVault platform tool manifest
[agent_tool] contract.  Stub implementation for future agent-driven integration.
"""
from __future__ import annotations

from typing import Any

TOOL_SPEC: dict[str, Any] = {
    "name": "document_record_inspector",
    "description": (
        "Deterministic read-only inspection tool that returns the full record view "
        "for one TechVault document, including the documents row, document_files, "
        "chunks, embeddings, summaries, and ingest_runs. "
        "Use for debugging, validation, and operator inspection of a single document_id."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["health", "inspect"],
                "description": "The inspection action to perform.",
            },
            "args": {
                "type": "object",
                "description": "Action-specific arguments.",
                "properties": {
                    "document_id": {
                        "type": "string",
                        "description": "SHA-256 document_id to inspect (required for inspect).",
                    },
                    "include_text": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include chunk text in response.",
                    },
                    "include_vectors": {
                        "type": "boolean",
                        "default": False,
                        "description": "Include embedding vectors in response.",
                    },
                },
            },
        },
        "required": ["action"],
    },
}


def run(ctx: Any, args: dict[str, Any]) -> dict[str, Any]:
    """Agent callable entry point (stub — full implementation pending).

    In agent mode the platform calls this with a ToolContext and parsed args dict.
    The stub raises NotImplementedError so callers know it is not yet wired up
    rather than silently returning empty data.
    """
    raise NotImplementedError(
        "document_record_inspector agent-mode run() is not yet implemented. "
        "Use the HTTP API at /v1/tools/document_record_inspector/documents/{document_id} instead."
    )
