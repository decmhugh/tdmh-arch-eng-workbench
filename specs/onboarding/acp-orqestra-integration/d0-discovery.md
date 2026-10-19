# ACP & orQEstra Integration

> **Gate**: D0 - Discovery | **Status**: Draft | **Epic**: EACPP-1377

## Business Overview

orQEstra is an orchestration/application platform that the team wants to integrate with ACP so its model interactions can use governed ACP services rather than an isolated integration path.

The discovery discussion covers two orQEstra-related use cases, including a POC use case and a broader orQEstra production direction. The initial POC is expected to run in development, while the team is targeting both use cases for production by the end of Q4, subject to governance approval.

## Business Value

- **Governed orchestration** — Connect orQEstra to ACP so model and application interactions can use the enterprise control plane.
- **Provider flexibility** — Preserve the ability to use Bedrock initially while keeping the integration path adaptable to other model providers.
- **Reusable integration** — Establish a repeatable application-to-ACP pattern that can support orQEstra use cases and future ACP consumers.
- **Operational visibility** — Create a path toward policy, credentials, monitoring, and production support for the integrated application.
- **User-level cost attribution** — Investigate how model and token consumption can be attributed to individual users or consuming teams, including the chargeback issues seen with comparable developer tools.

## Cost and Chargeback Context

The transcript distinguishes between ACP platform/service charges and the consuming team's token and LLM costs. The consuming business unit is expected to pay for its use of ACP services, while model and token consumption must be attributed through the backend. User-level attribution is a desired outcome, but the chargeback mechanism and reporting path are not yet decided.

- **Platform/service cost** — Establish how ACP onboarding and ongoing operational costs are represented and charged.
- **Model/token cost** — Attribute Bedrock or other model consumption to the account owner, user, or consuming team as appropriate.
- **Chargeback design** — Confirm whether the existing account-based model is sufficient or whether a user-level allocation mechanism is required.

## Governance Need

The orQEstra integration needs ACP to provide governed model access, application registration, policy management, and controlled gateway routing. The integration must distinguish between what orQEstra owns as an application and what ACP owns as the governed platform path.

- **Application registration** — Register the orQEstra application and establish the relevant relationships to models and ACP services.
- **Gateway access** — Route orQEstra model calls through an ACP-governed gateway using managed credentials and access policies.
- **Model and provider governance** — Confirm whether the initial integration uses Bedrock models through ACP, orQEstra's own Bedrock account, or another supported provider path.
- **Policy control** — Define who creates and administers policies for the application, models, and any future governed services.
- **Production readiness** — Identify the additional controls, monitoring, support, and operating requirements required before orQEstra is considered production-ready.
- **Governance approval** — Production progression depends on the required governance approvals, including ATG and ISRA.
- **Production terminology** — The first use case is already used by people in a production-like manner, while the ACP production state additionally requires monitoring, assessments, and governance approval. The POC remains a development activity.

## Scope

### In Scope

- orQEstra application registration and ACP integration discovery.
- Model and provider path assessment, with Bedrock as the initial candidate.
- Gateway routing, credential management, and policy configuration.
- Application, model, and governed-service relationships required for the first use cases.
- POC-to-production readiness assessment.
- Monitoring, support, and operational requirements discovery.
- User-level usage and cost attribution discovery.

### Out of Scope for D0

- Final orQEstra architecture or deployment design.
- Selecting a single chargeback mechanism before Finance and platform stakeholders confirm the options.
- Final production approval and detailed readiness criteria.
- Building new ACP platform capabilities before capability gaps are identified.
- Detailed implementation tasks and acceptance criteria, which belong in later gates.

## Onboarding Assessment

| Area | Assessment |
|---|---|
| Integration subject | orQEstra application/orchestration platform |
| Use cases | Two use cases discussed, including a POC and a broader production direction; exact scope to be confirmed |
| Initial provider candidate | Bedrock through ACP; account/topology arrangement remains open |
| ACP path | Application registration, governed gateway, policies, credentials, and model relationships |
| Production intent | Initial POC in development; first use case already used by users in a production-like manner; both use cases targeted for production by end of Q4 subject to governance approval |
| LVT | Not yet determined in discovery |
| Milestones | End-of-Q4 production target discussed; detailed milestones remain open |
| Cost model | User-level attribution and chargeback require further design |

## Capability Requirements

At D0, the relevant capability areas are identified without claiming final availability or design:

- **Application and identity registration** — Register orQEstra and establish the identity used for governed calls.
- **Governed gateway routing** — Route model calls through the ACP gateway.
- **Model/provider registry** — Select and govern the initial model/provider path.
- **Policy and credentials** — Define access-policy ownership and managed credential behavior.
- **Observability and cost accounting** — Capture usage data needed for monitoring and user-level attribution.
- **Lifecycle and production governance** — Define the gates for moving from POC through production readiness.
- **Evaluation and metrics** — Identify the evaluation framework, metrics, and SDK path needed for the use cases; do not assume an evaluation pipeline is available at D0.

### Capability Map Exposure

| Capability | D0 relevance | Status / decision |
|---|---|---|
| [CAP-05](../../../capability-map.md#cap-05) — SSO and human identity | Application and user identity for governed access | Confirm identity and authorization path |
| [CAP-08](../../../capability-map.md#cap-08) — Governed AI gateway | Route orQEstra model calls through ACP | Required integration path |
| [CAP-14](../../../capability-map.md#cap-14) — Lifecycle governance and approvals | Production readiness and governance gates | Confirm obligations before production |
| [CAP-17](../../../capability-map.md#cap-17) — Evaluation, quality gating and assurance | Evaluation and metrics discussed, but pipeline availability is not established | To be confirmed; do not assume available |
| [CAP-20](../../../capability-map.md#cap-20) — Observability and cost accounting | Monitoring, token usage, and chargeback attribution | Required for production and financial reporting |

## Dependencies and Open Questions

- What are the exact two orQEstra use cases and which one is the initial POC?
- What is the current orQEstra architecture, and which calls must be routed through ACP?
- Will orQEstra use Bedrock through ACP, an orQEstra-owned Bedrock account, or another provider path?
- Which gateway, application, model, and policy objects must be registered for the first use case?
- Who owns policy creation, credential management, and application administration?
- What monitoring, incident response, and production support model applies?
- What evaluation framework, metrics, and SDK path will be used, and is CAP-17 available for the intended timing?
- What is the user-to-cost attribution model for tokens and model consumption?
- What chargeback mechanism and reporting path will Finance support?
- What detailed milestones and production readiness criteria are required for the end-of-Q4 target?
- What LVT rating applies to each orQEstra use case?

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| orQEstra architecture and use-case boundaries are unclear | Integration scope and effort cannot be estimated | Confirm the application boundary and two use cases in D1 |
| Provider or Bedrock account topology is unresolved | Gateway and credential design may be reworked | Decide the initial provider/account path before D2 |
| Production requirements are not defined | POC may be mistaken for production readiness | Define monitoring, support, incident, and governance gates before production approval |
| User-level cost attribution is unavailable | Chargeback and financial reporting remain incomplete | Define usage identifiers and attribution ownership with Finance and platform teams |
| Detailed milestones are not agreed | Dependencies and delivery sequencing remain unclear | Establish a D1 discovery plan and decision register against the end-of-Q4 target |
| Evaluation capability is assumed before it is available | Production assurance may be incomplete | Confirm CAP-17 status and define an approved interim evaluation approach if needed |

## Success Criteria

| Criterion | Target | Measured at |
|---|---|---|
| orQEstra scope is defined | Two use cases and the initial POC are documented | D1 |
| ACP integration boundary is agreed | Application, gateway, model, policy, and credential responsibilities are documented | D1/D2 |
| Provider path is selected | Initial Bedrock/provider and account topology are recorded | D1/D2 |
| Production readiness is defined | Monitoring, support, incident, governance, and approval criteria are documented | D1/D2, before ACP production promotion |
| Cost attribution direction is agreed | Platform/service charges, model/token usage, user identifiers, and chargeback options are documented | D1 |
| Evaluation direction is agreed | Evaluation framework, metrics, SDK path, and CAP-17 dependency are documented | D1 |

## References

- Raw discovery transcript: [orqestra-acp-discovery-session.vtt](references/orqestra-acp-discovery-session.vtt)
- Readable discovery transcript: [orqestra-acp-discovery-session.txt](references/orqestra-acp-discovery-session.txt)
- ACP Capability Map: [docs/capability-map.md](../../../capability-map.md)
- Capability Gap Escalation: [docs/process/capability-gap-escalation.md](../../../process/capability-gap-escalation.md)
