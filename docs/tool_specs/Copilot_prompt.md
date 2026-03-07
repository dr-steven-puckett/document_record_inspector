
---

# SECTION 2 — COPILOT BUILD PROMPT

```md
You are building a new deterministic TechVault tool repository using the canonical tool factory template.

Tool name: document_record_inspector

Purpose:
A read-only deterministic inspection tool that returns the full record view for one document, including:
- documents row
- document_files
- chunks
- embeddings
- summaries
- ingest_runs

Repository target:
backend/tools/document_record_inspector

Template repository to inspect first:
/home/spuckett1/projects/tools/techvault_tool_template

Before writing code, inspect and follow the template repository architecture and prompt flow. You must align with the canonical deterministic tool pattern already used by the TechVault tool ecosystem.

Read these template files first:
- docs/TOOL_SPEC_TEMPLATE.md
- docs/TOOL_PROMPT_GENERATOR.md
- docs/TOOL_AUTOMATION_SCHEME.md
- docs/TOOL_FACTORY_PIPELINE.md
- docs/STANDARD_REPO_SKELETON.md
- docs/TOOL_TEMPLATE.md
- docs/TOOL_TEMPLATE_EXECUTION_PLAN.md
- docs/prompts/ (all relevant build-phase prompts)

Also inspect TechVault platform integration files and existing tool examples before implementation.

Authoritative tool requirements:
- deterministic outputs only
- no LLM calls
- no network calls
- offline operation only
- explicit ordering everywhere
- canonical JSON serialization
- stable OpenAPI snapshot
- stable CLI output
- no new platform abstractions unless absolutely required by the template
- do not modify core TechVault services beyond standard tool registration/integration points

Use the following tool behavior as the source of truth:

INPUTS
- document_id: required string
- include_text: optional bool default false
- include_vectors: optional bool default false

OUTPUT
A single deterministic JSON object with top-level keys:
- document
- files
- chunks
- embeddings
- summaries
- ingest_runs
- counts

DATABASE TABLES TO READ
- documents
- document_files
- chunks
- embeddings
- summaries
- ingest_runs

JOIN / RELATIONSHIP RULES
- documents is keyed by document_id
- document_files joins on document_id
- chunks joins on document_id
- embeddings joins to chunks via embeddings.chunk_id -> chunks.id
- summaries joins on document_id
- ingest_runs joins on document_id

REQUIRED SORTING
- files: role ASC, rel_path ASC, id ASC
- chunks: chunk_index ASC, id ASC
- embeddings: chunk_index ASC, embedding_model ASC, id ASC
- summaries: output_type ASC, created_at ASC, id ASC
- ingest_runs: started_at ASC, id ASC

API ENDPOINT
Implement:
GET /v1/tools/document_record_inspector/documents/{document_id}

Query params:
- include_text=false
- include_vectors=false

STATUS BEHAVIOR
- 200 for success
- 404 if document_id not found in documents
- 422 for validation failures

CLI
Create a CLI entrypoint consistent with the template, supporting a command equivalent to:
techvault-tool-document-record-inspector inspect --document-id <ID> [--include-text] [--include-vectors]

CLI must emit canonical JSON to stdout.

SCHEMA / MODEL GUIDANCE
Create explicit request/response models and row projections.
Do not use vague untyped dicts when a concrete schema is appropriate.
Keep models compact and deterministic.

IMPLEMENTATION BOUNDARIES
- read-only only
- one document at a time
- no pagination needed in initial version
- no audit_log support in initial version
- no repair/regeneration flows
- no batch mode
- no speculative features

TESTS REQUIRED
Build a complete pytest suite including:
- success path
- 404 path
- deterministic ordering tests
- include_text gating behavior
- include_vectors gating behavior
- CLI test
- OpenAPI snapshot test
- manifest validation / tool wiring tests if standard in template

OPENAPI / MANIFEST / REGISTRATION
Integrate using the template conventions for:
- tool.toml
- router.py
- service.py
- schemas.py
- CLI entrypoint
- agent tool callable
- README
- tests
- OpenAPI snapshot
- standard manifest wiring

Do not invent architecture outside the template.
Do not duplicate existing TechVault core document-list functionality.
This tool is a focused inspection/detail tool only.

Deliver a complete repo implementation that matches the template repository structure and deterministic standards.