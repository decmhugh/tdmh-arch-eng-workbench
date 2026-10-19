# Feature Build / Capability Requests

> **Gate**: D0 - Discovery | **Status**: Draft | **Epic**: EACPP-1386

## Purpose

Provide a central intake and delivery path for capability requests from ACP use-case owners. Requests may require a new ACP capability, an enhancement to an existing capability, or integration work needed to support a governed use case.

## How Ongoing Requests Are Managed

1. Capture each request in this Epic's capability-request register.
2. Record the requesting use case/team, business need, requested ACP capability, current capability-map status, dependencies, risks, priority, and target timing.
3. Refine accepted requests through D1 requirements and D2 design.
4. Decompose approved implementation work into `d3-tasks.md` during D3.
5. Create Jira Sub-tasks under this Epic from the D3 task rows.

Individual requests are not created as Jira tickets at D0 unless a separate decision requires an immediate investigation or risk record. The Epic and this register are the initial tracking mechanism.

## Initial Capability Requests

### Agent Registry Clearance Metadata

The Agent Registry should expose metadata describing what an agent is cleared to consume. The metadata should include ownership, description or intended purpose, and the data classifications or subclassifications the agent is permitted to read. Other services should be able to retrieve this information from the Agent Registry as the authoritative source.

Related capability: `CAP-01 - Agent Registry`.

Related capabilities:

- `CAP-13 - Attribute tagging and classification-driven control` for the curated, multi-valued governance attribute representing the data subclassifications an agent is cleared to read.
- `CAP-07 - RBAC and access policy` for policies that use governance attributes to restrict access between resources.
- `CAP-08 - Governed AI gateway` when the relevant agent-to-tool or agent-to-model traffic must pass through ACP for runtime enforcement.

The current capability direction is that the clearance attribute can be mandatory at agent registration, so registration is rejected when the required attribute is missing. Other services can retrieve the attribute and related metadata through the Agent Registry API. Runtime enforcement depends on the call traversing the governed ACP gateway.

Status: Discovery request. Detailed attribute schema, registration behavior, policy selectors, gateway boundary, ownership, and consuming services are not yet defined.

### Capability Relationship

This request should be tracked as a capability chain rather than as an Agent Registry-only change:

`CAP-01` stores and exposes the agent metadata -> `CAP-13` defines the governance attribute -> `CAP-07` applies access policy -> `CAP-08` carries runtime enforcement for gateway-routed traffic.

### On-Behalf-Of Authorization

ACP should support authorization when an agent acts on behalf of a human user or another agent. The model should preserve the relevant initiating identity, acting agent, delegation context, scopes, and policy decisions across the call chain without allowing the delegated actor to exceed the authority granted by the initiating identity.

Related capability: `CAP-24 - Delegated access and chain authorization`.

Status: Discovery request. Detailed token, trust, consent, chain, and enforcement requirements are not yet defined.

## Scope for This Epic

### In Scope

- Capability requests raised by ACP use-case owners.
- Capability-map assessment and status tracking.
- Requirements, design, dependency, risk, and ownership discovery.
- Capability-gap escalation where current Luminate support is insufficient.
- D3 decomposition into Jira Sub-tasks after requirements and design are approved.

### Out of Scope for This Placeholder

- Immediate implementation of the initial requests.
- Creating individual Jira tickets before requirements and design are sufficiently defined.
- Replacing the D0-D4 lifecycle for component delivery.
- Accepting a capability request as a commitment before feasibility, ownership, and priority are reviewed.

## Open Questions

- Who can submit, triage, accept, defer, or reject a capability request?
- What minimum information is required before a request enters D1?
- How are duplicate or related requests consolidated?
- How are capability priority, status, dependencies, and target timing reported?
- What criteria move a request from the register into D1, D2, and D3 work?
- Which requests require an immediate spike, risk, or capability-gap record?
- Who owns the request after it becomes a committed platform work item?
- Should the governance attribute be a mandatory agent-registration field, and what is its exact multi-valued schema?
- Which access-policy selectors consume the agent clearance attribute, and what happens when the attribute is absent or stale?
- Which Galileo/agent-to-tool or agent-to-model paths must traverse the ACP gateway for runtime enforcement?
- Which parts of this chain are already supported by Luminate and which require a capability gap or integration request?

## Dependencies

- ACP Capability Map and capability-gap escalation process.
- ACP Product Team triage and prioritization.
- Use-case owners requesting the capability.
- Architecture, security, risk, Finance, and operations stakeholders where applicable.
- Jira and repository workflows for D1-D3 progression.

## Success Criteria

| Criterion | Target | Measured at |
|---|---|---|
| Capability request register exists | Requests have a consistent intake record and status | This D0 |
| Initial requests are captured | Agent Registry clearance metadata and on-behalf-of authorization are recorded | This D0 |
| Related capability chain is visible | CAP-01, CAP-13, CAP-07, and CAP-08 relationships are recorded without prematurely creating implementation tickets | This D0 |
| Request triage is defined | Intake, ownership, prioritization, and acceptance criteria are documented | D1 |
| Accepted requests progress predictably | Requirements and design precede D3 Jira Sub-task creation | D2/D3 |
| Capability gaps are visible | Requests requiring Luminate changes or integrations are escalated through the standard process | D1/D2 |

## References

- ACP Capability Map: [docs/capability-map.md](../../../capability-map.md)
- Capability Gap Escalation: [docs/process/capability-gap-escalation.md](../../../process/capability-gap-escalation.md)
- D0-D4 process: [docs/process/d0-d4-overview.md](../../../process/d0-d4-overview.md)
- Team agreement: [docs/team-agreement.md](https://bitbucket.sunlifecorp.com/projects/EDAEACP/repos/acp-product-specs/browse/docs/team-agreement.md)
