# Define ACP Operating Model

> **Gate**: D0 - Discovery | **Status**: Draft | **Epic**: EACPP-1375

## Purpose

Define the operating model required to run ACP as an enterprise platform. The initial placeholder covers service-level expectations, incident management, escalation, change management, ownership, and communications.

## Discovery Status

Discovery has not started. No discovery calls, stakeholder decisions, service levels, support commitments, or operating procedures are recorded yet.

## Initial Scope for Discovery

- Service catalogue and supported ACP capabilities.
- Service-level objectives and response expectations by environment and severity.
- Incident classification, triage, ownership, escalation, communications, and post-incident review.
- Operational support responsibilities across ACP Product, platform, infrastructure, security, risk, and consuming teams.
- Change management for ACP platform changes, gateway policies, models, guardrails, access policies, and onboarding patterns.
- Release, maintenance, emergency-change, rollback, and notification procedures.
- Runbooks, operational documentation, support contacts, and hand-off requirements.
- Governance evidence, auditability, and reporting responsibilities.

## Out of Scope for This Placeholder

- Implementing individual use cases.
- Building new ACP platform capabilities.
- Defining the detailed architecture of a specific integration.
- Replacing existing enterprise incident or change-management systems.

## Open Questions

- Who owns the ACP service and each operational support tier?
- Which environments and ACP capabilities require defined service levels?
- What severity model, response targets, resolution targets, and escalation paths apply?
- Which system is the authoritative record for incidents and changes?
- How are standard, normal, emergency, and rollback changes approved and communicated?
- What operational readiness evidence is required before a use case moves toward production?
- Which existing enterprise support, incident, and change-management processes must ACP integrate with?

## Dependencies

- ACP Product Team ownership and service definition.
- Enterprise incident and change-management process owners.
- Platform, infrastructure, security, risk, and consuming use-case teams.
- Existing service-management tooling and reporting requirements.

## References

- ACP D0-D4 process: [docs/process/d0-d4-overview.md](../../../process/d0-d4-overview.md)
- Design review guide: [docs/process/design-review-guide.md](../../../process/design-review-guide.md)
