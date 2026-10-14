# Plan: Remove IASA corpus features and references

Spec: ./spec.md

## Design

- Remove IASA-only test files from [tests/](/C:/workspace/tdmh-arch-eng-workbench/tests) that import non-existent IASA modules.
- Remove IASA-specific requirements and commitments from [specs/002-ai-agent-core/spec.md](/C:/workspace/tdmh-arch-eng-workbench/specs/002-ai-agent-core/spec.md), [specs/002-ai-agent-core/plan.md](/C:/workspace/tdmh-arch-eng-workbench/specs/002-ai-agent-core/plan.md), and [specs/002-ai-agent-core/tasks.md](/C:/workspace/tdmh-arch-eng-workbench/specs/002-ai-agent-core/tasks.md).
- Search the repository for remaining `IASA` / `iasa` corpus references and remove only those that imply active feature scope, infrastructure commitments, or test expectations.
- Preserve non-IASA endpoint behavior (`/agent/invoke`, `/agent/mcp`) and existing throttling/safety contracts.

## IAM (least privilege)

No new permissions are introduced. Any IASA-specific planned permission commitments are removed from documentation/spec artefacts only.

## Terraform changes

No Terraform resource creation, apply, or destroy is performed in this feature. Repository config and spec references are updated only.

## Constitution check

- [x] One Lambda per endpoint: no new endpoint is added.
- [x] Least-privilege IAM: no new IAM policy grants are introduced.
- [x] No secrets in repo: no secret handling changes.
- [x] Log group with retention: runtime logging resources are unchanged.
- [x] Infrastructure as code only: no manual AWS changes are performed.

## Validation

- Run pytest to verify removal of IASA import errors and that remaining tests collect/run for the current scope.
- Run targeted repository search for `IASA`/`iasa` to confirm no active IASA feature commitments remain.
- Skip Terraform apply/destroy; no deployment mutation occurs.

## Risks / alternatives

- **Risk:** Removing IASA lines from spec artefacts may unintentionally alter unrelated requirements.  
  **Mitigation:** limit edits to IASA-specific clauses and keep all non-IASA content intact.
- **Risk:** Hidden IASA references may remain in less obvious files.  
  **Mitigation:** perform a final repo-wide reference scan before completion.
