# Define ACP Financial Model

> **Gate**: D0 - Discovery | **Status**: Draft | **Epic**: EACPP-1376

## Purpose

Define the financial model for ACP inference so Bedrock usage can be centralized, attributed, and charged back to the appropriate client cost centres.

## Discovery Status

Discovery has not started. This placeholder records the questions to resolve and does not select an implementation, system of record, or ownership model.

## Initial Scope for Discovery

- Move Bedrock calls and associated spend into an EDAE workload account.
- Define how Bedrock charges will be attributed and charged back to clients.
- Assess whether existing Apptio pipelines can support the chargeback requirement or whether a new EDAE chargeback process is needed.
- Assess the impact if Apptio does not show clients their overall cloud spend by cost centre.
- Establish a valid source of truth for the chargeable cost centre before a client can be enabled with a model.
- Define ownership and controls for cost-centre number changes.
- Define reporting, reconciliation, exception handling, and audit requirements for chargeback.

## Out of Scope for This Placeholder

- Selecting Apptio or a new EDAE chargeback process before discovery is complete.
- Implementing workload-account migration or Bedrock routing.
- Changing enterprise finance policy or client cost-centre ownership rules.
- Defining model access policy or ACP runtime governance unrelated to financial attribution.

## Open Questions

- Which Bedrock calls and models move into the EDAE workload account, and what is the migration sequence?
- Will chargeback use existing Apptio pipelines, a new EDAE process, or an agreed combination?
- What happens when Apptio cannot show clients their complete cloud spend by cost centre?
- What system is the authoritative source for a valid chargeable cost centre?
- What validation is required before a client can be enabled with a model?
- Who approves, records, and communicates cost-centre number changes?
- How are historical usage, corrections, shared costs, and disputed charges reconciled?
- What reporting and audit evidence must be available to clients, Finance, Cloud FinOps, and ACP operators?

## Dependencies

- EDAE workload-account and Bedrock architecture owners.
- Finance and Cloud FinOps chargeback stakeholders.
- Apptio owners and existing cloud-cost reporting pipelines.
- Authoritative client and cost-centre data ownership.
- ACP model enablement and access-control process.

## References

- ACP Capability Map: [docs/capability-map.md](../../../capability-map.md)
- Capability Gap Escalation: [docs/process/capability-gap-escalation.md](../../../process/capability-gap-escalation.md)
