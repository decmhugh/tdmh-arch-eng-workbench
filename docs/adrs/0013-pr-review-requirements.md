---
parent: Decisions
nav_order: 13
title: ADR-0013 PR Review Requirements
status: draft
date: 2026-04-27
---

# ADR-0013: PR Review Requirements

## Status

**Draft** — from team-agreement.md

## Context and Problem Statement

What are the review requirements for pull requests?

## Decision Outcome

**Chosen option**: Human approval required; 2 reviewers for AI-generated PRs

| PR Type | Reviewers |
|---------|-----------|
| Human-authored | 1 approving review |
| AI-generated (Copilot) | 2 approving reviews |
| Documentation-only | same rules from previous 2 |
| Security-related | 2 approving reviews + security team |

## AI-Generated PR Guidelines

PRs created or substantially modified by AI must:
- Be clearly labeled (`ai-generated` label)
- Have commit messages indicating AI authorship
- Undergo extra scrutiny for:
  - Security vulnerabilities
  - License compliance
  - Test coverage
  - Edge cases

## Consequences

**Good:** Quality assurance, knowledge sharing
**Bad:** Can slow velocity if reviewers unavailable

## More Information

See [team-agreement.md](../../docs/team-agreement.md)
