# Spec: Business context, viewpoints, and ADR workflow

Status: Approved

## Problem / Why

Architecture work needs a consistent, reviewable way to capture business context, connect stakeholder concerns to selected viewpoints, and record decisions before implementation begins. Without shared templates and explicit approval states, agent-produced architecture can omit concerns or be mistaken for an approved design.

## User stories

- As an architect, I want to capture business drivers, stakeholders, constraints, assumptions, and unknowns in a consistent format so that design work starts from an agreed context.
- As a stakeholder, I want my concerns linked to architecture viewpoints so that I can see how the design addresses them.
- As an architect, I want reusable viewpoint and ADR templates so that proposed designs and decisions can be compared and reviewed consistently.
- As an engineer, I want implementation work to rely only on approved architecture decisions so that proposals are not treated as authorization to build.

## API contract

Not applicable. This feature produces version-controlled architecture artefacts and review guidance; it does not add an API endpoint.

## Acceptance criteria

- AC1: A business-context artefact can record objectives, scope, stakeholders, drivers, constraints, assumptions, risks, data sensitivity, and unresolved questions; unknown information is clearly marked rather than invented.
- AC2: A stakeholder-and-viewpoint matrix links each stakeholder's concerns to one or more viewpoints and records any concerns not yet addressed.
- AC3: The repository provides reusable business-context, stakeholder-concerns, and solution/deployment viewpoint templates, each describing its purpose, relevant stakeholder concerns, and the information or model to be recorded.
- AC4: An ADR template records a stable identifier, context, linked requirements or concerns, options considered, decision criteria, decision, rationale, consequences, evidence, and status.
- AC5: Architecture artefacts and ADRs distinguish proposals from approved content. An ADR is not approved unless a human reviewer explicitly records the approval.
- AC6: Approval records identify the approver and approval date. Rejected and superseded decisions retain their rationale and references to replacement decisions where applicable.
- AC7: The documented workflow requires business-context review before viewpoint selection, and explicit ADR approval before dependent implementation work is treated as authorized.
- AC8: Templates use stable identifiers and links so that artefacts can be cross-referenced and later included in a traceability register.
- AC9: Templates and examples do not reproduce proprietary BTABoK corpus content; they provide project-authored structures that can reference approved source material.
- AC10: The templates and workflow are compatible with the existing repository and its spec-first, human-review conventions; they do not add a runtime service or external system write.

## Non-functional

- Artefacts are plain, version-controlled files that can be reviewed in Git.
- Templates make assumptions, evidence, and unresolved questions visible.
- Approval is auditable and cannot be inferred from agent output or generated status.
- Do not include secrets or unapproved sensitive source material in architecture artefacts.

## Out of scope

- Canonical machine-validated requirement schema or traceability validator.
- Automatic architecture approval or autonomous implementation authorization.
- JIRA publication, repository pushes, AWS changes, or deployment.
- Building the PDF-ingestion solution or generating its production code and Terraform.
- Reproducing or redistributing proprietary BTABoK material.

## Open questions

- None.
