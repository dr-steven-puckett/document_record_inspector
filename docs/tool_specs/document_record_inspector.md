# document_record_inspector

## Purpose

`document_record_inspector` is a deterministic TechVault inspection tool that returns a full record-level view of a single document and its related ingestion artifacts.

It is intended for debugging, validation, auditing, and operator inspection of one document at a time.

The tool provides a stable, read-only aggregation over the canonical ingestion tables for a single `document_id`.

## Scope

This tool inspects one document and returns:

- the `documents` row
- related `document_files`
- related `chunks`
- related `embeddings`
- related `summaries`
- related `ingest_runs`

This tool is read-only.

This tool does not perform ingestion, re-indexing, summarization, embedding generation, mutation, deletion, or repair.

## Why this tool exists

TechVault already exposes document listing and broader retrieval APIs, but a deterministic, full-fidelity single-document inspection view is needed for:

- ingestion debugging
- record integrity verification
- operator audits
- troubleshooting missing chunks / summaries / embeddings
- validating deterministic ingest outcomes
- CLI diagnostics
- future admin/operator UI detail panels

## Database tables accessed

Per database source of truth, this tool reads from:

- `documents`
- `document_files`
- `chunks`
- `embeddings`
- `summaries`
- `ingest_runs`

Relevant schema expectations include:

- `documents.document_id` is the canonical document key
- `document_files.document_id` links files to the document
- `chunks.document_id` links chunks to the document, with stable `chunk_index`
- `embeddings.chunk_id` links embeddings to `chunks.id`
- `summaries.document_id` links summaries to the document
- `ingest_runs.document_id` links ingest attempts to the document, but may be null for failed pre-hash runs

## Inputs

### Primary input

- `document_id: str`
  - required
  - expected to be a SHA-256 hex string matching the canonical TechVault document identifier

### Optional input flags

- `include_text: bool = false`
  - whether to include full chunk text in the response
  - defaults to `false` to keep payloads smaller and safer for routine inspection

- `include_vectors: bool = false`
  - whether to include embedding vector payloads
  - defaults to `false`
  - when `false`, embedding metadata is returned without vector contents

- `include_failed_runs_without_document_match: bool = false`
  - reserved minimal flag for future extension
  - initial implementation may omit this if not needed
  - default behavior should only include `ingest_runs` rows whose `document_id` equals the requested `document_id`

## Outputs

The tool returns one deterministic JSON object with the following top-level structure:

- `document`
- `files`
- `chunks`
- `embeddings`
- `summaries`
- `ingest_runs`
- `counts`

### Output contract

```json
{
  "document": {},
  "files": [],
  "chunks": [],
  "embeddings": [],
  "summaries": [],
  "ingest_runs": [],
  "counts": {
    "files": 0,
    "chunks": 0,
    "embeddings": 0,
    "summaries": 0,
    "ingest_runs": 0
  }
}
Deterministic guarantees

The tool must be strictly deterministic.

Requirements:

no LLM calls

no network calls

no nondeterministic timestamps in outputs

stable field ordering through canonical JSON serialization

stable ordering of arrays

explicit SQL ordering on every collection query

no reliance on DB default ordering

identical database state must produce byte-stable JSON output

Required stable ordering

files

order by role ASC, rel_path ASC, id ASC

chunks

order by chunk_index ASC, id ASC

embeddings

order by chunk position first, then embedding_model ASC, then id ASC

if implemented via join, sort by chunks.chunk_index ASC, embeddings.embedding_model ASC, embeddings.id ASC

summaries

order by output_type ASC, created_at ASC, id ASC

ingest_runs

order by started_at ASC, id ASC

API surface
HTTP endpoint

Expose a single read endpoint under the tool namespace:

GET /v1/tools/document_record_inspector/documents/{document_id}

Query parameters

include_text: bool = false

include_vectors: bool = false

Responses
200 OK

Returns the full inspection payload.

404 Not Found

Returned when the requested document_id does not exist in documents.

422 Validation Error

Returned for invalid input shape.

CLI interface

Provide a CLI entrypoint consistent with the template architecture.

Example interface:

techvault-tool-document-record-inspector inspect \
  --document-id <DOCUMENT_ID> \
  [--include-text] \
  [--include-vectors]
CLI behavior

prints canonical JSON to stdout

returns non-zero on validation or not-found errors

must not print non-deterministic decoration in JSON mode

human-readable stderr is allowed for failures

Agent/tool callable

Provide a callable wrapper suitable for TechVault tool registration that accepts the same logical arguments:

document_id

include_text

include_vectors

and returns the same deterministic response object as the API/service layer.

Minimal schema design

Create explicit response schemas for:

document row projection

file row projection

chunk row projection

embedding row projection

summary row projection

ingest run row projection

aggregate response

Prefer exact row-shaped response models rather than overly generic dictionaries.

Security and access expectations

This tool is inspection-oriented and read-only.

Initial implementation may assume trusted internal/operator usage consistent with existing tool patterns.

The tool must not broaden access beyond normal TechVault DB visibility. It should not invent new authorization abstractions.

Non-goals

This tool does not:

ingest documents

modify any TechVault row

repair corrupt records

regenerate embeddings

regenerate summaries

infer missing metadata

perform semantic search

perform RAG

inspect unrelated tables

expose audit log data in the initial version

introduce batch inspection in the initial version

Recommended implementation boundaries

Keep implementation minimal:

one-document inspection only

direct SQLAlchemy/db-session reads

compact deterministic response models

no pagination in initial version because scope is exactly one document and its directly linked child records

Suggested internal service functions

Examples only; follow template naming conventions:

get_document_record_inspection(...)

_get_document_or_404(...)

_list_document_files(...)

_list_document_chunks(...)

_list_document_embeddings(...)

_list_document_summaries(...)

_list_document_ingest_runs(...)

Testing requirements

Must include:

happy-path inspection test

not-found test

deterministic ordering tests for each returned collection

include_text=false hides chunk text as specified

include_vectors=false hides vector payloads as specified

OpenAPI snapshot test

CLI output test

canonical JSON stability test

Integration notes

Tool repository path:

backend/tools/document_record_inspector

Manifest:

tool.toml

Platform enablement follows standard TechVault conventions:

backend/platform/enabled_tools.toml

backend/platform/tool_manifests.py

backend/platform/tools_registry.py

backend/platform/tools_api_registry.py

Relationship to existing TechVault APIs

Current OpenAPI already includes:

GET /v1/documents for listing documents

ingest endpoints

search/RAG endpoints

It does not currently provide a full single-document inspection endpoint returning joined ingestion artifacts, so this tool fills a distinct operator/debugging role.

Final implementation rule

If any ambiguity remains during implementation, choose the smallest deterministic read-only implementation that returns a complete inspection for one document_id without inventing new platform abstractions.