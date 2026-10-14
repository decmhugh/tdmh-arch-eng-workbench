# Plan: Business context, viewpoints, and ADR workflow

Spec: ./spec.md

## Design

This is a documentation and template change; no Lambda, API, or runtime behavior is required.

- Add project-authored Markdown templates under `templates/architecture/` for business context, the stakeholder/viewpoint matrix, three viewpoint types (business context, stakeholder concerns, and solution/deployment), and ADRs.
- Add `docs/architecture-workflow.md` describing intake, context review, viewpoint preparation, ADR review, and approval gates. Make clear that generated content remains proposed until a human records approval.
- Use stable IDs and cross-reference fields in templates. ADR states are `Proposed`, `Approved`, `Rejected`, or `Superseded`; approval records include approver and date, and rejected/superseded decisions retain rationale and applicable replacement references.
- Update the README with links to the templates and workflow so users can discover the new materials.
- Keep feature delivery artifacts in `specs/004-architecture-artifacts/`; do not conflate these with the architecture artefacts the templates describe.

## IAM (least privilege)

Not applicable. This change adds no AWS resources or permissions.

## Terraform changes

None.

## Validation

- Review all templates against AC1-AC6 and AC8-AC9.
- Review the workflow and README links against AC5-AC7 and AC10.
- No automated tests, Terraform validation, or deployment are expected for documentation-only changes.

## Constitution check

- [x] One Lambda per endpoint: no endpoint or Lambda is added.
- [x] Least-privilege IAM: no IAM resources or permissions are added.
- [x] No secrets in repo: templates prohibit secrets and unapproved sensitive material.
- [x] Log group with retention: not applicable; no runtime is added.
- [x] Spec-first and human review: implementation remains gated on approval of this spec, plan, and tasks.

## Risks / alternatives

- **Risk:** Templates could be mistaken for official BTABoK material. **Mitigation:** use project-authored structures only and link to approved source material without reproducing it.
- **Risk:** An agent-produced ADR could appear accepted without review. **Mitigation:** default ADR state to `Proposed`; require a human approver and date for `Approved`.
- **Alternative:** Store architecture templates alongside feature specs. Rejected because `specs/` is already the repository's feature-delivery workflow; `templates/architecture/` and `docs/` separate reusable architecture artefacts from feature specifications.
