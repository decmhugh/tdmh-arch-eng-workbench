# Architecture artefact workflow

Use this workflow to create reviewable architecture artefacts from an agreed business need. The templates under [`../templates/architecture/`](../templates/architecture/) are project-authored structures, not reproductions of BTABoK content. They may reference approved source material by evidence ID.

## 1. Capture business context

Copy [`business-context.md`](../templates/architecture/business-context.md) to the architecture artefact location for the initiative. Assign a stable context ID and record objectives, scope, stakeholders, drivers, constraints, assumptions, risks, data sensitivity, evidence, and unresolved questions.

Use `[TBD]` for unknown information and identify an owner or resolution target where possible. Do not invent facts or put secrets or unapproved sensitive source material in the artefact. Keep the context proposed until its human review is recorded.

## 2. Review and confirm context

Have the appropriate business owner and stakeholders review the context, scope, constraints, assumptions, classification, and open questions. Record review state, reviewer, date, and notes in the artefact. Resolve important unknowns or explicitly carry them forward as risks before selecting viewpoints.

## 3. Select viewpoints and map concerns

Create a stakeholder/viewpoint matrix using [`stakeholder-viewpoint-matrix.md`](../templates/architecture/stakeholder-viewpoint-matrix.md). Assign stable stakeholder, concern, and viewpoint IDs. Select and complete the relevant templates:

- [`viewpoint-business-context.md`](../templates/architecture/viewpoint-business-context.md) for the business environment, boundaries, actors, and outcomes.
- [`viewpoint-stakeholder-concerns.md`](../templates/architecture/viewpoint-stakeholder-concerns.md) for concern coverage, responses, gaps, and trade-offs.
- [`viewpoint-solution-deployment.md`](../templates/architecture/viewpoint-solution-deployment.md) for proposed components, interfaces, deployment, and trust boundaries.

Link each concern to one or more viewpoints and record its coverage state. Keep uncovered concerns visible with an owner or follow-up action; do not treat blank entries as resolved.

## 4. Record decisions as proposals

Create one [`adr.md`](../templates/architecture/adr.md) per significant architecture decision. Assign a stable ADR ID and link the relevant requirements, concerns, viewpoints, and evidence. Record options, decision criteria, rationale, consequences, risks, and trade-offs. Use `Proposed` until a human review takes place.

Agent-generated or otherwise automated content is a proposal only. It cannot mark an ADR or architecture artefact approved or authorize implementation.

## 5. Obtain explicit human approval

The designated human reviewer records the review outcome, rationale, identity, and date. Set an ADR to `Approved` only when a human approver and approval date are present. Rejected decisions retain their rationale. Superseded decisions remain in the record, retain their rationale, and link to the replacing ADR.

Dependent implementation work is not authorized by a proposal. Treat it as authorized only after the relevant ADRs have been explicitly approved and the approved architecture baseline is identifiable. Any change to an approved decision requires a new review; preserve the previous decision and its history.

## 6. Preserve references and review evidence

Use stable IDs and repository-relative links so context, stakeholders, concerns, viewpoints, decisions, and evidence can be cross-referenced and later included in a traceability register. Before handoff, check links and IDs, document open gaps, and ensure no sensitive or unapproved material has been included.

This workflow creates version-controlled artefacts only. It does not publish JIRA items, push repository changes, modify AWS resources, or deploy systems.
