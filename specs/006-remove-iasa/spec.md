# Spec: Remove IASA corpus features and references

Status: Approved

## Problem / Why

The repository currently includes IASA-specific tests and planning artefacts, while corresponding runtime modules are absent. This causes failing test collection and leaves repository intent inconsistent. The project needs IASA-specific code/tests/infrastructure references removed so the codebase reflects the current non-IASA scope and validates cleanly.

## User stories

- As an engineer, I want the test suite to run without missing IASA-module import errors so that CI results reflect supported features.
- As an operator, I want Terraform and repository artefacts to avoid IASA-specific resources or commitments so that planned infrastructure matches current scope.
- As a reviewer, I want repository specs and docs to remove IASA-only requirements so that future work is not driven by obsolete corpus assumptions.

## API contract

| Method | Path | Request | Success | Errors |
| ------ | ---- | ------- | ------- | ------ |
| POST | /agent/invoke | Existing JSON request contract remains unchanged | Existing response contract remains unchanged, excluding any requirement to answer from an IASA corpus | Existing error contracts remain unchanged |
| POST | /agent/mcp | Existing MCP request contract remains unchanged | Existing MCP response contract remains unchanged, excluding any IASA-knowledge tool requirement | Existing MCP error contracts remain unchanged |

No new endpoints are added. No endpoint authentication or throttling behavior is changed by this feature.

## Acceptance criteria

- AC1: Repository tests that are specifically for IASA ingestion and IASA knowledge retrieval are removed, and pytest no longer fails due to missing `agent.ingest_iasa` or `agent.knowledge` modules.
- AC2: Repository source and infrastructure files contain no active IASA-specific feature code, resource references, or configuration commitments.
- AC3: Specs/plans/tasks in the repository no longer require IASA corpus upload, indexing, retrieval, or IASA-specific tooling.
- AC4: Existing non-IASA API behavior for `/agent/invoke` and `/agent/mcp` remains unchanged.
- AC5: No Terraform apply or destroy is executed as part of this removal.
- AC6: Deployed AWS resources are not modified by this change; removal is limited to repository content and configuration.

## Non-functional

- Keep changes surgical and limited to IASA-related scope removal.
- Preserve least-privilege IAM and existing observability behavior for remaining features.
- Maintain passing validation workflows for the remaining repository scope.

## Out of scope

- Deleting or mutating already-deployed AWS resources.
- Adding new replacement corpus/retrieval features.
- Broad redesign of agent behavior unrelated to IASA removal.

## Open questions

- None.
