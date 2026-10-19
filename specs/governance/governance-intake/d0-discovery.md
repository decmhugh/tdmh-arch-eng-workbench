# Governance Intake & Risk Classification (Sun Life) — D0: Discovery

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: TBD
> **Owner**: Governance-by-Design (Duncan Wyllie) + ACP Product (Seth Chalmers) + CMRM (Ryan Bolick)
> **Scope**: Sun Life **product** spec — the SLF instance of governance intake on **Luminate**.
> The **reusable engines** (risk triage, evaluation, compliance registry) are consortium
> contributions; this spec configures and consumes them with Sun Life content.

## Problem Statement

Sun Life is standing up the consortium **Luminate** platform as the go-forward runtime, but
the **governance intake process** that gates agents/models — GenAI Risk Triage, validation
requirements, PIA/ISRA/ATG, Archer/GRC — is not yet wired to it. Today intake is manual forms
and ad-hoc ISRAs that do not scale to the volume of agents being created, and the **risk
classification, validation policies, and evaluation requirements live in separate CMRM
artifacts** (the GenAI Model Risk Classification Field Guide, the policies list, and an
emerging per-policy YAML) that no system ingests end-to-end.

Since the Consortium came online we also lost momentum integrating our streams (ACP, Model
Risk/CMRM, Governance-by-Design). We need **one intake** that: runs a **shared, reusable risk
classification**, drives the **Luminate registry lifecycle and gated deployments**, sets the
**required evaluations and validations** per risk band, and produces **audit-ready evidence**.

## Background & Drivers

- **Luminate is the runtime.** The internal MVP proved the intake→lifecycle→evaluation→audit
  chain; the go-forward instance must run on Luminate and consume the **consortium engines**,
  not a Sun Life fork.
- **CMRM owns the content.** The **questionnaire** (Field Guide), the **validation-requirement
  policies**, and the WIP **per-policy YAML** are the authoritative inputs — Sun Life should
  configure/seed the reusable engines with them, not re-encode them.
- **GbD owns the process + GRC.** Archer is the GRC system-of-record; ServiceNow is the
  workflow engine; PIA/ISRA/ATG are Sun Life gate names.
- **Separation of concerns.** Generic mechanism → consortium (`governance-risk-triage`,
  `model-agent-evaluation`, `regulatory-reporting`); Sun Life content + integration → this
  product spec.

## Opportunity

A single AI-assisted intake (Amazon Quick as the UX layer) that: (1) runs the **reusable
risk-triage engine** seeded with the CMRM Field Guide; (2) maps the **risk band → Sun Life
Model Risk tier**; (3) binds **validation requirements** and **required evaluations** per
band; (4) routes **PIA/ISRA/ATG** to ServiceNow and syncs **Archer**; and (5) drives the
**Luminate registry lifecycle + gated deployment** — all auditable end-to-end.

## Scope

### In Scope

| # | Capability | Description |
|---|-----------|-------------|
| 1 | Intake UX on Luminate | Amazon Quick form (UX only) calling Luminate/ACP APIs behind the scenes |
| 2 | Reusable risk classification | Adopt consortium `governance-risk-triage` engine, **seeded with the CMRM Field Guide** questionnaire/matrix |
| 3 | Band ↔ Model Risk tier | Sun Life mapping of the engine's risk band to CMRM tiers (config) |
| 4 | Validation requirements per band | Bind the CMRM **policies list** as gates (validations / PIA / ISRA / ATG / MRM review) with 1LoD/2LoD/3LoD sign-off |
| 5 | Required evaluations per band | Sun Life **evaluation metric guide** — which eval suites/scorers/thresholds run per band (config over `model-agent-evaluation`) |
| 6 | Policy-as-YAML ingestion | Ingest CMRM's **per-policy YAML** into the compliance/policy registry (`regulatory-reporting` seed schema) |
| 7 | Registry lifecycle + gated deploy | Risk band drives Luminate Agent/Model/MCP lifecycle: auto-approve below band, review/escalate above |
| 8 | Archer bi-directional sync | Archer risk record ↔ ACP risk tier / lifecycle status (GRC system-of-record) |
| 9 | ServiceNow routing | PIA/ISRA/ATG work items created from intake output |
| 10 | Audit-ready evidence | All intake artifacts + decisions retrievable per agent; evidence packages (`regulatory-reporting`) |

### Out of Scope

- The **generic engines** themselves (owned by the consortium specs) — this spec configures them.
- Amazon Quick platform production rollout (owned by the Quick platform team).
- Collibra lineage publishing; Data Control Plane convergence (future).
- Enterprise-Architecture template standardization.

## Stakeholders

| Stakeholder | Role | Key Concern |
|-------------|------|-------------|
| Duncan Wyllie | GbD Lead / process owner | Intake workflow, gate names, compliance |
| Ryan Bolick | CMRM / Model Risk | Questionnaire (Field Guide), validation policies, per-policy YAML |
| Kalyan / Lalit | Governance-by-Design | Framework alignment, reusable module adoption |
| Seth Chalmers | ACP Product / implementer | Luminate API integration, lifecycle enforcement |
| Eric Robson | US Architecture / Security | US/NIST regional alignment |
| Risk & Compliance | Governance consumers | Risk thresholds, action determination, sign-off |
| AI4Ops / Consumer Teams | Consumers | Frictionless onboarding, clear requirements |

## References

- CMRM policies list (Confluence): <https://sunlife.atlassian.net/wiki/x/BYHFVBo>
- CMRM per-policy YAML, WIP (Confluence): <https://sunlife.atlassian.net/wiki/x/UALAVBo>
- CMRM GenAI Model Risk Classification Field Guide: <https://sunlifefinancial.sharepoint.com/sites/RiskMgmt/CMRM/RefMat_Public/RiskClass/GenAI_ModelRiskClassification_FieldGuide.xlsx>
- Consortium engines (generic): `governance-risk-triage` (EACPP-648), `model-agent-evaluation`
  (EACPP-647), `regulatory-reporting` (EACPP-649), `agent-registry` (EACPP-646),
  `model-registry` (EACPP-650) — `EDAEACP/acp-consortium-specs`
- Legacy internal intake: `governance-integration` (EACPP-21/215), `T1KACP/acp-specs`
- Luminate deployment: `sunlife-deployment` (EACPP-596)
