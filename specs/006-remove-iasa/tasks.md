# Tasks: Remove IASA corpus features and references

- [ ] T1 Remove IASA-specific test files that require missing IASA modules (AC1).
- [ ] T2 Remove IASA corpus requirements and acceptance criteria from [specs/002-ai-agent-core/spec.md](/C:/workspace/tdmh-arch-eng-workbench/specs/002-ai-agent-core/spec.md) while preserving non-IASA contracts (AC3, AC4).
- [ ] T3 Remove IASA infrastructure and tooling commitments from [specs/002-ai-agent-core/plan.md](/C:/workspace/tdmh-arch-eng-workbench/specs/002-ai-agent-core/plan.md) and [specs/002-ai-agent-core/tasks.md](/C:/workspace/tdmh-arch-eng-workbench/specs/002-ai-agent-core/tasks.md) (AC2, AC3).
- [ ] T4 [P] Run a repository sweep for `IASA` / `iasa` references and remove remaining active-scope references (AC2, AC3).
- [ ] T5 Run pytest and confirm the previous IASA module import failures are gone (AC1, AC4).
- [ ] T6 Confirm no Terraform apply/destroy or deployed AWS mutation was performed and summarize residual risks (AC5, AC6).
