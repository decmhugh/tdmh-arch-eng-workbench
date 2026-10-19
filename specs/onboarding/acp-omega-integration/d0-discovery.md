# ACP & Omega Integration

> **Gate**: D0 - Discovery | **Status**: Draft | **Epic**: EACPP-1379

## Business Overview

Omega is an application/use case the team wants to integrate with ACP for governed model access and a managed application-to-ACP integration path. The first discovery boundary is to clarify Omega's application and agent architecture, the model/provider path, the gateway and credential flow, and the requirements for moving from development or demonstration toward production readiness.

## Business Value

- **Governed Omega integration** - Establish a standard ACP path for Omega model interactions.
- **Controlled model access** - Route applicable model calls through ACP-managed models, policies, and credentials.
- **Reusable integration pattern** - Capture an onboarding path that can be reused for similar applications and use cases.
- **Operational readiness** - Define the monitoring, governance, support, and production-readiness requirements for Omega.
- **Cost and usage visibility** - Establish the usage information needed to understand model consumption and financial treatment.

## Governance Need

Omega requires a clear integration boundary between application-owned behavior and ACP-owned governance. The D0 work must establish how Omega applications or agents are registered, how calls reach models and governed tools, and who owns identity, policy, credentials, monitoring, and production support.

- **Application and agent boundary** - Confirm which Omega components are applications, agents, orchestration services, or tools.
- **Gateway routing** - Define which calls route through the ACP gateway and how credentials are managed.
- **Model and provider governance** - Confirm the initial model/provider path and account topology.
- **Policy and identity** - Define access policies, identity providers, authorization, and administrative ownership.
- **Production readiness** - Define the monitoring, evaluation, governance, support, and approval criteria required before production use.

## Scope

### In Scope for D0

- Omega application and agent integration discovery.
- Model/provider and gateway integration assessment.
- Application, agent, model, policy, credential, and tool relationships.
- Identity, authorization, monitoring, and operational support questions.
- Development/POC to production-readiness transition questions.
- Usage, cost, and chargeback discovery where model consumption is involved.

### Not Decided in D0

- Final Omega architecture or deployment design.
- Final model/provider and account arrangement.
- Final application, agent, policy, credential, and support ownership.
- Final production date or approval decision.
- Detailed implementation tasks and acceptance criteria.

## Onboarding Assessment

| Area | Assessment |
|---|---|
| Integration subject | Omega application/use case and associated agent or orchestration components |
| Current state | Architecture and component boundary require confirmation |
| ACP path | Application/agent registration, governed gateway, policies, credentials, and model relationships |
| Provider path | Model/provider and account topology remain open |
| Production intent | Production-readiness path is required; date and approval criteria remain open |
| Monitoring/evaluation | Requirements need to be defined before production promotion |
| Cost model | Usage and financial treatment require discovery |

## Capability Requirements

At D0, the relevant capability areas are identified without claiming final availability or design:

- **Application and identity registration** - Register Omega and establish identities for governed calls.
- **Governed gateway routing** - Route applicable Omega model and tool calls through ACP.
- **Model/provider registry** - Select and govern the initial model/provider path.
- **Policy and credentials** - Define authorization, policy ownership, and managed credential behavior.
- **Observability and cost accounting** - Capture usage, monitoring, and cost data.
- **Evaluation and production governance** - Define evaluation, incident, support, approval, and production-readiness requirements.

### Luminate Capability Exposure

These are the relevant Luminate capabilities for Omega's D0 integration boundary. The table identifies current platform support; it does not assume every capability is required until the Omega architecture and use-case boundary are confirmed.

| Capability | Status | Governance overlay | Omega implication |
|---|---|---|---|
| [CAP-01](../../../capability-map.md#cap-01) - Agent Registry | Available | Mandatory | Register Omega agents and ownership where agents are governed directly. |
| [CAP-02](../../../capability-map.md#cap-02) - Model Registry | Available | Mandatory | Register and select the approved model/provider path. |
| [CAP-03](../../../capability-map.md#cap-03) - MCP Tool Registry | Available | Conditional - mandatory if Omega calls MCP tools | Apply if the confirmed Omega architecture uses registered MCP servers or tools. |
| [CAP-05](../../../capability-map.md#cap-05) - SSO and human identity | Available | Mandatory | Establish attributable human access and identity federation. |
| [CAP-06](../../../capability-map.md#cap-06) - Machine identity and programmatic access | Available; hardening in flight upstream | Mandatory | Define service identity for Omega application or agent calls. |
| [CAP-07](../../../capability-map.md#cap-07) - RBAC and access policy | Available | Mandatory | Govern Omega application, agent, model, and tool relationships. |
| [CAP-08](../../../capability-map.md#cap-08) - Governed AI gateway | Available | Mandatory | Route applicable Omega model and tool calls through ACP. |
| [CAP-14](../../../capability-map.md#cap-14) - Lifecycle governance and approvals | Partial | Mandatory | Define assessment, approval, promotion, suspension, and production-readiness gates. |
| [CAP-17](../../../capability-map.md#cap-17) - Evaluation, quality gating and assurance | Partial - build in flight | Conditional - mandatory where the use case makes or influences a customer-affecting decision | Confirm evaluation and quality-gating requirements before production promotion. |
| [CAP-20](../../../capability-map.md#cap-20) - Observability and cost accounting | Available | Mandatory | Capture monitoring, usage, token-cost, and attribution data. |

## Accountable Participants

| Participant | Context |
|---|---|
| Andy Zhu | Omega/use-case participant |
| Mahmoud Khalil | Omega/use-case participant |
| Seth Chalmers | ACP technical participant |
| Lalit Summan | ACP onboarding/delivery participant |
| Robert Chin | Platform/finance-routing participant |

## Open Questions

- What is Omega's current architecture, and which components are applications, agents, tools, or orchestration services?
- Which Omega calls must route through ACP, and which remain application-local?
- Which models and providers are required initially, and what account topology is expected?
- Which ACP objects must be registered for the first Omega use case?
- Who owns identity, policy administration, credential lifecycle, monitoring, and production support?
- What evaluation, monitoring, and production-readiness evidence is required before promotion?
- What LVT rating or risk classification applies to each Omega use case?
- What usage identifiers and reporting are needed for cost and chargeback decisions?
- What is the target production date and what approval gates must be completed first?

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Omega architecture and integration boundary are unclear | Scope and effort cannot be estimated | Confirm the application, agent, tool, and provider boundaries in D1 |
| Provider, account, or gateway topology is unresolved | Integration design may be reworked | Decide the initial provider/account path before D2 |
| Identity, policy, and credential ownership is unclear | Access and onboarding may be blocked | Assign ownership before implementation |
| Production requirements are undefined | Demonstration or POC may be mistaken for production readiness | Define monitoring, evaluation, governance, support, and approval gates |
| Cost and usage attribution is unresolved | Financial reporting may be incomplete | Define usage identifiers and accounting ownership with Finance/platform teams |

## Success Criteria

| Criterion | Target | Measured at |
|---|---|---|
| Omega scope is defined | Application, agents, tools, models, and initial use case documented | D1 |
| ACP integration boundary is agreed | Registration, gateway, identity, policy, credential, and ownership responsibilities documented | D1/D2 |
| Provider path is selected | Initial model/provider and account topology recorded | D1/D2 |
| Production readiness is defined | Monitoring, evaluation, support, governance, and approval criteria documented | D1/D2, before production promotion |
| Cost direction is agreed | Usage identifiers and cost/chargeback reporting options documented | D1 |

## References

- Raw discovery transcript: [omega-acp-discovery-session.vtt](references/omega-acp-discovery-session.vtt)
- Readable discovery transcript: [omega-acp-discovery-session.txt](references/omega-acp-discovery-session.txt)
- ACP Capability Map: [docs/capability-map.md](../../../capability-map.md)
- Capability Gap Escalation: [docs/process/capability-gap-escalation.md](../../../process/capability-gap-escalation.md)
