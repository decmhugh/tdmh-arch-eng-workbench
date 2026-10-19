# Governance Content Packs — D3: Implementation Plan

> **Gate**: D3 — Tasks | **Status**: Draft | **D2 Approved**: TBD
> **Epic**: TBD · Board label `acp-product-team`

## Overview

Sequenced so the obligation field set is agreed first — it blocks the schema, the repo and every
downstream consumer. The existing CMRM YAML becomes the first pack file rather than a conversion
target (DD-1), so there is a working pack before any converter is written.

## Tasks

| Task | Description | Depends |
|------|-------------|---------|
| **T1** | Agree the **obligation field set** three ways (ACP / CMRM / GbD): id, domain, requirement, execution mode, prerequisites, accountable role, evidence expectation. Confirm CMRM's `ValidationPolicySpecifications_CMRM.yaml` can serve as the pack file unchanged, or record precisely what must change. (DD-1, DD-3, CP-Q5) | — |
| **T2** | Stand up the **content pack repository** `EDAEACP/acp-governance-content` with the pack layout, branch protection and content-owner review routing. (DD-8, CP-Q1, CP-Q2) | T1 |
| **T3** | Author the **four JSON Schemas** — questionnaire, band↔tier map, obligations, thresholds — with `domain` first-class on the obligation schema and privacy modelled as a second domain from day one. (DD-2, DD-3) | T1 |
| **T4** | Land the **first pack file**: CMRM's obligation YAML as `packs/obligations/mbct-genai-validation.yaml`, validating against the schema. (DD-1) | T2, T3 |
| **T5** | Build **CI validation**: JSON Schema plus semantic rules (prerequisite cycles, dangling references, band with no obligations, threshold with no metric), with author-readable errors naming file, entry and expectation. (DD-5) | T3 |
| **T6** | Convert the **GenAI Model Risk Classification Field Guide** (xlsx) into the questionnaire pack file, and author the **band ↔ Sun Life Model Risk tier** map. (DD-1) | T3 |
| **T7** | Convert the **GenAI Evaluation Metric Selection Guide** into the thresholds pack file, including **calibration metadata** so an uncalibrated LLM-as-judge is detectable. (D16, FR-11) | T3 |
| **T8** | Implement **pack release**: semver version, manifest with per-file checksums, published as a deployment-time artifact. (DD-2, DD-8) | T4, T5 |
| **T9** | Wire the **Luminate seed load** — packs consumed as seed configuration by the governance engines, with no pack content compiled into shared code. (FR-9) | T8 |
| **T10** | Add **`content_pack_version` to approvals, gate decisions and evidence records** so any past governance decision is reproducible. Coordinate the field with consortium Governance Mode (EACPP-915). (DD-7, FR-10) | T8 |
| **T11** | Build the **semantic diff** rendered on every pack change, so content owners approve meaning rather than a file diff. (DD-6) | T5 |
| **T12** | Define and implement the **pack upgrade policy** per content type — re-evaluate, grandfather or flag already-approved assets on a version bump. (FR-12, CP-Q4) | T10 |

## Definition of Done

- Obligation field set agreed three ways; CMRM's YAML is the pack file, with no translation step.
- Four schemas published; CI rejects an invalid pack with an error a risk specialist can act on.
- Questionnaire, band↔tier map, obligations and thresholds all released under one semver pack.
- Luminate loads the pack as seed configuration; nothing Sun Life-specific is in shared code.
- Every approval and evidence record cites the pack version it was judged against.

## References

- Spec: [D0](d0-discovery.md) · [D1](d1-requirements.md) · [D2](d2-design.md)
- Consuming spec: [`governance-intake`](../governance-intake/d0-discovery.md) (EACPP-877)
- Consortium: Governance Mode `EACPP-915` (obligation resolution, evidence contract)
- Decisions register: [D4, D5, D9, D10, D11, D16, D18](../governance-intake/artifacts/2026-08-12-decisions-and-actions.md)
