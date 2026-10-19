---
parent: Decisions
nav_order: 10
title: ADR-0010 Pre-commit Hook Enforcement
status: draft
date: 2026-04-27
---

# ADR-0010: Pre-commit Hook Enforcement

## Status

**Draft** — from team-agreement.md

## Context and Problem Statement

How do we ensure code quality checks run before commits?

## Decision Outcome

**Chosen option**: Pre-commit hooks are mandatory; `--no-verify` is prohibited

## Required Hooks

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/igorshubovych/markdownlint-cli
    rev: v0.39.0
    hooks:
      - id: markdownlint
```

## Enforcement

- CI checks that pre-commit hooks pass
- PRs failing pre-commit checks are blocked
- `git commit --no-verify` is not allowed

## Consequences

**Good:** Catches issues early, consistent formatting
**Bad:** Adds commit overhead

## More Information

See [team-agreement.md](../../docs/team-agreement.md)
Related: ADR-0017 (Testing Strategy)
