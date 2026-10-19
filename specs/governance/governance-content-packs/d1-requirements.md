# Governance Content Packs — D1: Requirements

> **Gate**: D1 — Requirements | **Status**: Draft | **D0 Approved**: TBD

## Content types in a pack

| Type | Source | Authority | Consumed by |
|---|---|---|---|
| `questionnaire` | GenAI Model Risk Classification Field Guide (xlsx) | CMRM | risk-triage engine |
| `band-tier-map` | CMRM tier definitions + Sun Life naming | CMRM | intake → lifecycle outcome |
| `obligations` | MBCT GenAI Validation obligations (40 across 9 domains) | CMRM, extended per domain by GbD | obligation registry / gate engine |
| `thresholds` | GenAI Evaluation Metric Selection Guide | CMRM | harness SDK, eval engine, approval gate |

All four release together under one pack version (see CP-Q3).

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Define a **schema per content type** (questionnaire, band↔tier, obligations, thresholds), each versioned independently of the pack that contains them. | Must |
| FR-2 | The **obligation schema is domain-agnostic**: `domain` is a first-class required field, and privacy is modelled as a second domain from day one so the shape is not model-risk-only (D5). | Must |
| FR-3 | An obligation carries at minimum: id, domain, requirement text, **execution mode** (human / hybrid / automated), **prerequisites** (obligation ids), accountable role, and evidence expectation. Human-only obligations are marked such that automation can never satisfy them (D10). | Must |
| FR-4 | Terminology is **obligations**, not policies, throughout schema, field names and documentation. `policy` remains reserved for access/gateway enforcement policy (D4, A1). | Must |
| FR-5 | Provide a **conversion path** from each published source (xlsx / Confluence / existing CMRM YAML) into pack files, re-runnable when the source changes. | Must |
| FR-6 | **CI validates** every pack change against the schemas and fails with plain-language errors naming the file, the field and what is expected. | Must |
| FR-7 | A pack change produces a **semantic diff** — a readable summary of what changed in meaning (obligation added, threshold raised, band boundary moved) for the content owner to approve. | Must |
| FR-8 | Packs are released as a **semver-numbered artifact with a manifest** listing every content file and its checksum. | Must |
| FR-9 | Luminate loads a pack as **seed configuration**; no pack content is compiled into the shared engine (NFR-1 of `governance-intake`). | Must |
| FR-10 | Every **approval, gate decision and evidence record carries the pack version** it was judged against, so a past decision can be reproduced exactly. | Must |
| FR-11 | Threshold entries carry **calibration metadata** — what calibration is required for an LLM-as-judge metric and what proves the judge was tested (D16). | Should |
| FR-12 | Support a **pack upgrade policy** per CP-Q4: declare, per content type, whether a change re-evaluates, grandfathers or flags already-approved assets. | Should |
| FR-13 | Content owners can **propose a change without a git workflow** (review of the semantic diff is sufficient) if CP-Q1 resolves that way. | Could |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-1 | **No translation step.** If CMRM's existing YAML can be the pack, it is the pack. A second format that must be kept in sync is a permanent maintenance job and a permanent source of drift. | Must |
| NFR-2 | **Content authority stays with CMRM/GbD.** The pipeline never edits meaning; ACP Product owns format, validation and release only (D9). | Must |
| NFR-3 | **Reproducible** — a pack version plus an asset id is sufficient to re-derive the governance decision that was made. | Must |
| NFR-4 | **Sun Life-confidential** — pack content must not reach the consortium repository or any other member. | Must |
| NFR-5 | **Author-friendly failure** — validation errors are readable by a risk specialist, not only by an engineer. | Should |

## Constraints & Assumptions

- CMRM's obligation set is a **v0.1.0 draft** (40 obligations, 9 domains) and will move; the schema
  must tolerate additions without a breaking change.
- Ryan's granular per-obligation assessment criteria are **in flight** and land as content, not as
  schema (A6). Human execution mode ships first; automation is an upgrade (D10).
- Consortium engines consume packs but are specified separately (`EACPP-915`); this spec is blocked
  on the obligation schema being agreed three ways (D6).
- The Field Guide lives on SharePoint. Automated extraction may not be permitted; a manual export
  step is acceptable provided the converted output is validated.

## Open Questions

Carried from D0: CP-Q1 (contribution model), CP-Q2 (repo location), CP-Q3 (single vs per-type
version), CP-Q4 (upgrade policy), CP-Q5 (converge on CMRM's existing YAML).
