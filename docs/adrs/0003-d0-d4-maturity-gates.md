---
parent: Decisions
nav_order: 3
title: ADR-0003 D0-D4 Maturity Gate Model
status: draft
date: 2026-04-27
---

# ADR-0003: D0-D4 Maturity Gate Model

## Status

**Draft**

## Context and Problem Statement

How do we track component readiness and ensure quality at each stage?

## Decision Outcome

**Chosen option**: Five-gate maturity model

| Gate | Name | Deliverables |
|------|------|--------------|
| D0 | Discovery | Problem statement, stakeholders, constraints |
| D1 | Requirements | User stories, acceptance criteria, SLAs |
| D2 | Design | Architecture, data models, testing strategy |
| D3 | Tasks | Implementation breakdown, Jira tickets |
| D4 | Verification | Test results, security review, release checklist |

## Consequences

**Good:** Clear milestones, quality gates, documentation
**Bad:** Can feel heavyweight for small features

## More Information

See [d0-d4-overview.md](../../docs/process/d0-d4-overview.md)
