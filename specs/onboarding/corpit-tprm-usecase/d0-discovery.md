# Corp IT TPRM Use Case

> **Gate**: D0 — Discovery | **Status**: Draft | **Epic**: EACPP-1318

> **Amended by D1.** This D0 omits the presented architecture and contradicts the transcript on
> release phasing, human approvals and stakeholders. The corrections are in
> [D1 §0](d1-requirements.md#0-what-the-d0-left-out-or-got-wrong); read them before relying on this page.

## TPRM Business Overview

Third-Party Risk Management helps Corp IT assess and validate the risks associated with external vendors before and during their engagement with the organization. The process brings together vendor information, risk evidence, assessment activities, and validation decisions so that business and control teams can make informed choices about third-party relationships.

The TPRM application is intended to support this work through two initial agents: a **Risk Assessment Agent** and a **Validation Agent**. Together, they can reduce repetitive analysis, improve consistency, and help reviewers identify incomplete or higher-risk assessments while keeping accountable human review in the process.

### Business Value

- **Better risk decisions** — Give TPRM and control teams a more consistent view of vendor risk and supporting evidence.
- **Faster vendor assessment** — Reduce manual effort in the assessment and validation stages so reviews can progress more efficiently.
- **Improved control visibility** — Make assessment status, validation outcomes, and follow-up actions easier to track.
- **Stronger operational resilience** — Identify third-party risks earlier and support timely escalation before they affect business operations.
- **Clearer accountability** — Preserve human ownership of risk decisions while using agents to support analysis and validation.

### ACP Onboarding Value

ACP onboarding creates a governed path for the TPRM application to adopt platform controls after the initial application release.

- **Consistent risk assessment** — Support a repeatable TPRM assessment and validation workflow for the teams responsible for third-party risk.
- **Accountable AI use** — Govern model calls and retain the control evidence needed for operational and regulatory review.
- **Reduced delivery risk** — Reuse an existing ACP pattern instead of introducing a new integration design.

## Governance Need

The TPRM application requires ACP governance because it uses AI in an operational risk process and is intended for production use. The current assessment identifies a conditional approval posture and requires alignment with the applicable governance activities before release.

- **Regulatory context** — Operational risk requirements, including OSFI expectations, apply to the use case.
- **Conditional approval** — Production approval remains dependent on completing the required risk and architecture reviews.
- **Failure impact** — The impact of an agent failure must be assessed across clients, revenue, operations, and reputation before the production gate.
- **Release phasing** — The initial application release goes live without ACP or Agent Core; ACP onboarding and Agent Core incorporation are planned for the subsequent ACP-enabled MVP. The initial release is not blocked by ACP onboarding.
- **Platform direction** — The target onboarding platform is Luminate; the internal ACP MVP is not the ongoing onboarding target.

## Stakeholders

| Stakeholder | Role | Key Concern |
|-------------|------|-------------|
| Corp IT TPRM Team | Process owner | Production readiness and consistent risk assessment |
| Risk and Compliance Leads | Oversight | LVT confirmation, operational risk alignment, and conditional approval evidence |
| ACP Product Team | Platform owner | Reuse of the existing ACP onboarding pattern and incorporation into the ACP-enabled MVP |
| Grant Du | Architecture | Architecture review and confirmation that no new integration pattern is required |
| Kamal Boorghani | Architecture | Architecture review and confirmation that no new integration pattern is required |
| Sandra Lai | Model assignment owner | Model selection and assignment for the TPRM use case |

## Scope

### Initial Application Release

- **Two-agent application scope** — The initial application release includes the Risk Assessment Agent and Validation Agent.
- **Existing LLM integration pattern** — The application uses the established agent-calling-an-LLM pattern; no new integration pattern is required for the initial release.
- **Release boundary** — Record the initial application behavior and human review responsibilities; release sequencing follows the Governance Need decision above.

### ACP-Enabled MVP

- **TPRM workflow registration in ACP** — Register the use case and both operating agents in ACP.
- **Model usage governance** — Assign and govern the model used by the TPRM application through the approved ACP model pattern.
- **ACP and Agent Core onboarding** — Define and sequence incorporation of ACP and Agent Core into this MVP.
- **Governed model calls** — Route model calls through ACP and apply the controls agreed for the ACP-enabled MVP.
- **Auditability and observability** — Define the required audit trail, workflow usage, and cost visibility for the ACP-enabled path.
- **Review and escalation workflow** — Define how human review and exceptions are captured in the ACP-enabled path.

### Out of Scope

- **TPRM decision framework and risk methodology redesign** — This D0 does not redesign the firm's risk taxonomy, vendor risk scoring methodology, or underlying TPRM decision framework.
- **Full automation of every downstream approval step** — Phase 1 focuses on governed onboarding and workflow support, not end-to-end autonomous execution.
- **MCP onboarding** — No MCP integration is included in this first-wave assessment.
- **Additional agents or orchestration platforms** — The first wave is limited to the Risk Assessment Agent and Validation Agent.

## Onboarding Assessment

| Area | Assessment |
|---|---|
| Pattern | Existing agent-calling-an-LLM pattern; no new pattern required |
| Agents | Risk Assessment Agent and Validation Agent |
| Platform | Luminate; internal ACP MVP is not the ongoing onboarding target |
| Release phasing | Initial application release followed by ACP-enabled MVP; see Governance Need |
| LVT rating | LVT 4 (Obj: L4V4T4; Cap: L2V2T2) |

## Capability Requirements

The capability map identifies the following feasibility exposures for the ACP-enabled MVP. These are D0 findings, not claims that the capabilities are complete or available for the November 1 release.

| Capability | Status | Governance overlay | TPRM implication |
|---|---|---|---|
| [CAP-15](../../../capability-map.md#cap-15) — Risk tiering and materiality | 🟡 Partial | Mandatory | The TPRM risk band must drive proportionate controls, but the enforcement path is incomplete. |
| [CAP-11](../../../capability-map.md#cap-11) — Kill switch / emergency stop | 🟡 Partial | Mandatory | The ACP-enabled MVP needs an emergency-stop path; runtime denial is not complete. |
| [CAP-18](../../../capability-map.md#cap-18) — Audit trail | 🟡 Partial | Mandatory | Audit evidence is required, but the current external-producer limitation must be resolved for TPRM events. |
| [CAP-19](../../../capability-map.md#cap-19) — Regulatory reporting, evidence and attestation | 🟡 Partial | Mandatory | The required evidence and attestation package is not complete and must be addressed before ACP promotion. |
| [CAP-17](../../../capability-map.md#cap-17) — Evaluation, quality gating and assurance | 🟡 Partial — build in flight | Conditional — mandatory where the use case makes or influences a customer-affecting decision | Both TPRM agents influence vendor-risk decisions, so the conditional evaluation overlay applies to the ACP-enabled MVP. |

- **Agent onboarding** — Register the Risk Assessment Agent and Validation Agent through the established ACP onboarding pattern.
- **Model governance** — Confirm the model assignment with Sandra Lai and use the approved model path when ACP is incorporated in the ACP-enabled MVP.
- **Existing integration pattern** — Use the agent-calling-an-LLM pattern; no new pattern or MCP integration is identified for the first wave.
- **Evaluation capability** — Do not assume an existing evaluation pipeline is available. CAP-17 is partial and remains a P1 capability gap; any required pre-production evaluation depends on CAP-17 landing or an explicitly approved alternative.
- **Decision-impact determination** — The Risk Assessment Agent and Validation Agent both influence vendor-risk decisions, so CAP-17's conditional governance overlay applies to the ACP-enabled MVP.
- **Risk-aligned controls** — Use CAP-15 and the LVT assessment to determine the appropriate control depth during the later ACP onboarding work.

## Success Criteria

| Criterion | Measurement | Target | Measured at |
|-----------|-------------|--------|-------------|
| Initial application release is unblocked | Application release plan does not require ACP or Agent Core | November 1 go-live | Initial release |
| TPRM application scope is defined | Risk Assessment Agent and Validation Agent are documented as the initial application agents | Complete | This D0 |
| TPRM workflow is registered in ACP | Workflow appears in the registry with owner and status | 100% of pilot TPRM workflows registered | ACP-enabled MVP |
| AI assistance is governed | Model calls route through ACP with a reviewable audit record | 100% of model calls via ACP | ACP-enabled MVP |
| Vendor review evidence is traceable | Each review step can be linked to evidence and approver, subject to CAP-18 and CAP-19 availability | Audit trace for each case | ACP-enabled MVP |
| Human approvals are enforced | Approval steps are required for defined review states and model/tool access, subject to CAP-15 and CAP-17 controls | 100% for high-risk and exception reviews | ACP-enabled MVP |
| Review teams can onboard with minimal setup | New TPRM workflow can be registered without bespoke control design | < 1 business day for pilot onboarding | ACP-enabled MVP |
| Review process remains auditable | Approvals, detours, and escalations are logged and retrievable, subject to CAP-18 and CAP-19 gaps being addressed | 100% audit coverage | ACP-enabled MVP |

## Dependencies

| Dependency | Component/Team | Type | Risk |
|------------|---------------|------|------|
| Existing ACP onboarding pattern | ACP Product Team | High-level alignment | Medium |
| Model assignment and availability | ACP Product Team + Sandra Lai | Open | Medium |
| ACP and Agent Core incorporation | Corp IT TPRM + ACP Product Team | Future phase | Medium |
| CAP-17 evaluation, quality gating and assurance | ACP Product Team + Risk / Compliance | Partial; P1 gap and not assumed available | High |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Model selection or availability is unresolved | Medium | Medium | Confirm the use-case model assignment with Sandra Lai before ACP incorporation |
| ACP and Agent Core sequencing is not defined | Medium | Medium | Agree the ACP-enabled MVP onboarding path after the initial application release |
| Required evaluation is unavailable for agents influencing vendor-risk decisions | Medium | High | Treat CAP-17 as a dependency for the ACP-enabled MVP and define the D1 evaluation approach before ACP promotion |

## Open Questions

- [ ] What is the target release and scope for ACP and Agent Core onboarding in the ACP-enabled MVP?
- [ ] Who owns the ACP-enabled MVP onboarding plan and the transition from the initial application release?
- [ ] What is the confirmed impact assessment if either TPRM agent fails across clients, revenue, operations, and reputation?
- [ ] Is the LVT 4 assessment (Obj: L4V4T4; Cap: L2V2T2) final, and what controls are mandatory for that rating?
- [ ] What model is assigned to the TPRM use case, and has the assignment been approved?
- [ ] What CAP-17 evaluation and quality-gating approach will apply to the Risk Assessment Agent and Validation Agent before the ACP-enabled MVP is promoted?

## References

- Raw discovery transcript: [corp-it-tprm-acp-discovery-session.vtt](references/corp-it-tprm-acp-discovery-session.vtt)
- Readable discovery transcript: [corp-it-tprm-acp-discovery-session.txt](references/corp-it-tprm-acp-discovery-session.txt)
- ACP Capability Map: [docs/capability-map.md](../../../capability-map.md)
- Capability Gap Escalation: [docs/process/capability-gap-escalation.md](../../../process/capability-gap-escalation.md)
- Related governance patterns: [governance-intake](../../governance/governance-intake/d0-discovery.md)
- Related Corp IT onboarding examples: [aims-acp-integration](../aims-acp-integration/d0-discovery.md) and [orcc-acp-integration](../orcc-acp-integration/d0-discovery.md)
