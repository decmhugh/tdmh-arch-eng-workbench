# Governance Intake & Risk Classification (Sun Life) — D3: Implementation Plan

> **Gate**: D3 — Tasks | **Status**: Draft | **D2 Approved**: TBD
> **Epic**: [EACPP-877](https://sunlife.atlassian.net/browse/EACPP-877) · Board label `acp-product-team`
> **Amended** 9 September 2026 — T15 to T21 carry the
> [Luminate integration review](artifacts/2026-09-09-luminate-band-integration-review.md).
> **Amended again** 14 September 2026 — T22 to T28 carry the Archer × ACP × GbD working session.
> The picture is in [Architecture Overview](d2-architecture-overview.md).
> **Amended again** 15 September 2026 — T29 to T36 carry the
> [risk classification module workshop](references/2026-09-15-risk-classification-module-workshop.docx).
> T29 is a correction to what is already built, not new scope.

## Overview

Sun Life integration + configuration over the consortium engines. Sequenced so the intake
contract + risk seeding land first, then policy/eval config, then lifecycle drive and GRC.

## Tasks

| Task | Description | Depends |
|------|-------------|---------|
| **T1** | Define the **intake API contract** (frontend-agnostic). The **UX surface** that consumes it moved to [`governance-intake-ui`](../../onboarding/governance-intake-ui/d0-discovery.md) — this task now ends at the contract. (DD-1) | — |
| **T2** | Seed the consortium **risk-triage engine** with the **CMRM Field Guide** (questions/scoring/matrix) and configure the **band ↔ Model Risk tier** map. (DD-2) | T1 |
| **T3** | Ingest the **CMRM policies list + per-policy YAML** as **policy packs** into the `regulatory-reporting` registry. (DD-3) | — |
| **T4** | Configure **per-band validation gates** (validations/PIA/ISRA/ATG/MRM + 1LoD/2LoD/3LoD) and the **evaluation metric guide** (required evals/thresholds per band). (DD-4) | T2, T3 |
| **T5** | Wire **risk band → Luminate registry lifecycle + gated deployment** (auto-approve / review / escalate). (DD-5) | T2 |
| **T6** | Build the **Archer** bi-directional sync and **ServiceNow** PIA/ISRA/ATG routing adapters (config-driven field maps, circuit-breaker). (DD-6) | T4 |
| **T7** | Emit **audit events** + wire **evidence packages**; add **discovered-agent auto-triage**. (DD-7) | T5 |
| **T8** | Rename **policies → obligations** across this spec, the intake API surface and the governance data model; reserve *policy* for access/gateway enforcement. Make `domain` first-class so privacy and other risk domains use the same shape. (DD-11, D4, D5) | — |
| **T9** | Write down the **report scope boundary** — OSFI **E-23** from ACP per agent/model, broader OSFI **technology-risk** from GbD per application/use case — and agree it with Kathryn before either report is built. (DD-8, D7) | — |
| **T10** | Publish the **governance data product**: a documented, versioned read interface over ACP governance data for GbD to aggregate against. (DD-8, D8) | T9 |
| **T11** | Implement the **three evaluation layers**: aggregate registration and scheduled evaluations into the governance record; make a **single inference retrievable end-to-end** on demand without aggregating it. (DD-9, D14) | T5 |
| **T12** | Implement the **reference-by-default evidence strategy** — artifacts from external evidence producers are referenced, not copied; only what a report or Archer record must physically hold is duplicated. Settle the boundary in the Seth/Kalyan session first. (DD-10, Q3) | T7 |
| **T13** | Pin the **governance content pack version** onto every approval, gate decision and evidence record, so a decision remains reproducible after obligations or thresholds change. (FR-16) | T4 |
| **T14** | **Book and run the GbD × ACP intake-UI alignment session** — settle whether the Governance-by-Design UI remains the front door or users move into ACP/Luminate, agree the target personas and end-to-end journey, and confirm what changes are needed to the AI-assisted triage form. Attendees: Duncan, Kathryn, Seth. Output is an **ADR** recorded in [`governance-intake-ui`](../../onboarding/governance-intake-ui/d0-discovery.md), which is blocked until this lands. | T1 |
| **T15** | **Seed the `risk-band` attribute** in each Luminate deployment — definition marked governance-authoritative with `max_per_entity = 1`, applicability for `agent`/`model`/`mcp_server`/`deployment`, and one curated value per band. Nothing seeds it today, so this is the prerequisite for every other Luminate-facing task. (DD-13, FR-18) | — |
| **T16** | **Publish the band** from ACP to `(entity_type, entity_id)` over the attributes API, under a dedicated principal scoped to the `risk-band` dimension. Confirm Luminate republishes `GovernanceStatus` on write and that `resolve_obligations` stops raising `BandNotResolvable`. (DD-13, FR-17, FR-22) | T15, T2 |
| **T17** | **Decide and implement how the content pack revision reaches Luminate**, so an audit there can name what the band was judged against without calling ACP. Take the decision at the review — second attribute now, or a platform change later. (DD-15, FR-19, LB-Q2) | T16, T13 |
| **T18** | **Extend the intake contract to collect the agentic attributes** Luminate does not model — data reach, autonomy, regulatory scope, credential scope, and for MCP servers the data classification and PII/PCI/government-data flags — and classify agents and MCP servers on them alongside the model-risk questionnaire. (FR-20) | T1, T2 |
| **T19** | **Implement the classification trigger**: intake pushes on submission, and a scheduled reconciliation sweep catches resources registered outside the intake flow. Luminate emits no events, so absent this a resource registered directly is never classified. (DD-17, FR-21) | T16 |
| **T20** | **Raise the machine-producer defect with the consortium** — a `ServicePrincipal` cannot register as an `EvidenceProducer`, and an unregistered submission is accepted, uncounted and returned `201`. Ask for producer onboarding and for rejection rather than silent degradation. Track the ACP evidence path as blocked on it. (DD-16, LB-Q1) | — |
| **T21** | **Onboard the risk-classification API to the Sun Life API Platform.** Register it as its own API Platform app — own Okta authorization server, audience and ingress base path — following the pattern the other ACP APIs already use, and publish the OpenAPI to SwaggerHub alongside them. Two things make this more than paperwork. The service authenticates on **static bearer tokens from configuration** today, so it must move to Okta JWT verification before it can be published. And its **tenant is taken from the credential**, not from the request, so the API Platform must provision a tenant claim — otherwise every caller resolves to one tenant and the isolation is lost. Settle the scope names against the existing convention (`acp-model-registry.models.r`, `acp-mcp-registry.servers.crud`). Distinct from FR-22, which is the credential ACP uses to *call* Luminate. (FR-23) | T1 |
| **T22** | **Separate inherent risk from controls in every pack.** Split the agentic and MCP-server signal sets so the band is produced from what a resource could do — data reach, autonomy, destructive capability, external exposure, regulatory scope, model tier — and registration, ownership, inbound authentication and credential posture move to a control section carried beside it. Today they are one weighted score, so being registered and owned lowers the band, which credits a control into an inherent rating. Settle the split with Model Risk (RC-Q2) before rebalancing weights. (DD-21, FR-28) | T2 |
| **T23** | **Model the AI use case on the Luminate project.** Carry the use-case band, the APM id and the GbD / GCP id at project level, and give a resource a way to name the use case it belongs to. Resolve RC-Q3 first — a project is a valid attribute target so the band can be stored, but it is not swept and not band-covered, so nothing enforces it. (DD-18, FR-24) | T15 |
| **T24** | **Implement the containment check.** Compare each resource band against its use case's ceiling and publish the result. Not an aggregation — the use-case band is set independently by GbD and the resource is checked against it. Decide RC-Q4 (a use case whose band is lowered) and RC-Q5 (per-environment or not) as part of this. (DD-19, FR-25) | T23, T16 |
| **T25** | **Emit a divergence finding** when a resource classifies above its use case's ceiling, and expose it where GbD can consume it. The check runs continuously, because the case that matters is the agent that grew after intake. ACP raises; GbD decides. (DD-20, FR-26, FR-27) | T24 |
| **T26** | **Carry the environment on a band** so DEV and SIT observe while STAGE and PROD enforce, and the promotion gate is where intake, approval and obligations bind. (FR-29) | T16 |
| **T27** | **Run an end-to-end simulation** before the containment check is built — walk one use case from intake through lower-environment registration, promotion and a deliberate divergence, without needing the systems built. A bad answer changes the design, and finding that out afterwards is the expensive outcome. | T23 |
| **T28** | **Build the use-case classification pack export** and wire it into the governance intake form so intake is pre-populated rather than blank. Settle RC-Q7 first — which fields the pack can answer from observation and which remain a business judgement — because that split decides how much of the form is left. (DD-23, FR-30) | T23, T24 |
| **T29** | **Correct the instrument-to-resource mapping.** The model-risk questionnaire assesses an *application of a model* and must apply at the use-case level only; a model's own band is ingested from the model-risk process rather than computed. Fix `applies_to` on the pack, fix the narrative, and make ingestion of an approved model classification an explicit supported path. Small change, but it is currently wrong. (DD-24, FR-31) | — |
| **T30** | **Retain per-domain results and carry disagreement.** Restructure a classification so each contributing domain's inputs, instrument and result survive independently and can be recomputed without unpicking the composite, and so a conflict between domains is represented rather than flattened by taking the higher. Blocked on RC-Q10 and RC-Q11 — how a composite is derived across non-corresponding scales, and who arbitrates. (DD-26, FR-31, FR-32) | T22 |
| **T31** | **Expose the risk profile for continuous retrieval and portfolio aggregation** — current and historical, per resource and per use case, plus an aggregate view against risk appetite. Publishing at the promotion gate serves the gate and starves the monitoring layer, which reads across the whole lifecycle. (DD-27, FR-33) | T23, T26 |
| **T32** | **Admit evaluation results as answers to the accuracy and error-rate questions**, so measured error moves the inherent level instead of a remembered estimate, and carry those metrics in the export pack as evidence. This is the largest single reduction in what a human has to answer, and it narrows RC-Q7 directly. (FR-34, FR-35) | T28 |
| **T33** | **Make the export pack sufficient for risk acceptance** — state the band *and* the obligations it will cause to be enforced, so the accountable owner signs off a known enforcement posture rather than a score. Extends T28 rather than duplicating it. (DD-28, FR-35) | T28 |
| **T34** | **Support conditional questions and hard triggers in a pack.** Activation conditions on questions and sections, with unasked questions recorded as not applicable rather than missing — the distinction matters because a missing signal currently scores zero. Needed before the enterprise tiering instrument, with its conditional agentic branch, can run on this engine. (FR-38, RC-Q8) | — |
| **T35** | **Define the observe-only eligibility criteria.** State what qualifies a resource for the non-enforcing path, what is assumed rather than verified, and how a self-contained experiment differs from resources inside a real use case. Include the case where a lower environment exposes production data, which breaks the assumption the path rests on. (FR-37, RC-Q14) | — |
| **T36** | **Carry external governance identifiers on the use case** so the GRC platform retains observability while the inventory sits in the control plane and no sync exists. Cheap now, and the difference between reconciliation and re-keying later. (FR-36) | T23 |

> **UI split.** The intake **surface** — front door, personas, API handoff, form specification,
> auto-population and AI assistance — moved to [`governance-intake-ui`](../../onboarding/governance-intake-ui/d0-discovery.md)
> after the GbD × ACP session concluded that the UI flow and API handoff require a dedicated design
> and implementation discussion. This spec keeps the **contract and the engine**; the UI spec owns
> the surface. T14 books the session that unblocks it.

> **Scope note.** T6 covers the **ServiceNow** PIA/ISRA/ATG routing adapter. The Archer half —
> synthetic Archer, evidence publication, bidirectional sync and APM pass-through — moved to its own
> spec, [`archer-grc-sync`](../../integration/archer-grc-sync/d3-tasks.md), after the 12 August session established
> that Archer must stay off the critical path (D2). Obligation, questionnaire and threshold content
> moved to [`governance-content-packs`](../governance-content-packs/d3-tasks.md); T3 and T4 configure
> what those packs deliver rather than authoring it here.

## Definition of Done

- Intake contract published; risk engine seeded with the Field Guide; band↔tier configured.
- Front-door decision taken at the T14 session and recorded as an ADR in `governance-intake-ui`.
- Obligations/YAML ingested; per-band validation + eval gates enforced pre-APPROVED/ACTIVE.
- Risk band drives the Luminate lifecycle + gated deploy; ServiceNow wired; evidence produced.
- Report scope boundary agreed in writing; GbD consumes a documented governance data product.
- Registration and scheduled evaluations aggregated; a single inference retrievable end-to-end.
- Every approval cites the content pack version it was judged against.
- The `risk-band` attribute is seeded, ACP publishes the band, and Luminate's obligation
  resolution no longer raises `BandNotResolvable` for a governed resource.
- A resource registered outside the intake flow is still classified, by the reconciliation sweep.
- Agents and MCP servers are classified on agentic attributes, not only the model-risk questionnaire.
- The risk-classification API is published on the Sun Life API Platform, verifying Okta JWTs and
  resolving tenancy from a token claim.
- A band is produced from inherent risk alone; controls are carried beside it as mitigations.
- An AI use case carries a band, and every agent, model and MCP server inside it is checked against
  that ceiling continuously.
- A resource that classifies above its use case raises a finding Governance by Design can act on.
- At the promotion gate, the governance intake form is pre-populated from a use-case classification
  pack the platform exports, not filled in from memory.

## References

- Spec: [D0](d0-discovery.md) · [D1](d1-requirements.md) · [D2](d2-design.md)
- CMRM: policies <https://sunlife.atlassian.net/wiki/x/BYHFVBo> · per-policy YAML
  <https://sunlife.atlassian.net/wiki/x/UALAVBo> · Field Guide
  <https://sunlifefinancial.sharepoint.com/sites/RiskMgmt/CMRM/RefMat_Public/RiskClass/GenAI_ModelRiskClassification_FieldGuide.xlsx>
- Consortium engines: `governance-risk-triage` (EACPP-648), `model-agent-evaluation`
  (EACPP-647), `regulatory-reporting` (EACPP-649), Governance Mode (EACPP-915) ·
  depends on `sunlife-deployment` (EACPP-596)
- Alignment session: [decisions & actions](artifacts/2026-08-12-decisions-and-actions.md) ·
  [roadmap & work split](artifacts/2026-08-12-governance-alignment-roadmap.md) ·
  [follow-up verification](artifacts/2026-08-12-followup-verification.md)
- Workshop transcript, 15 September 2026:
  [risk classification module](references/2026-09-15-risk-classification-module-workshop.docx) —
  the source for T29 to T36 and for the DD-24 correction
