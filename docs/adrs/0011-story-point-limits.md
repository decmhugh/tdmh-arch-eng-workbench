---
parent: Decisions
nav_order: 11
title: ADR-0011 Story Point Limits
status: draft
date: 2026-04-27
---

# ADR-0011: Story Point Limits

## Status

**Draft** — from team-agreement.md

## Context and Problem Statement

How do we keep work items small enough to be predictable?

## Decision Outcome

**Chosen option**: Maximum 8 points per task; split 13s

| Points | Guidance |
|--------|----------|
| 1-3 | Small, well-understood work |
| 5 | Medium complexity |
| 8 | Maximum allowed — consider splitting |
| 13 | Must be split into smaller tasks |

## Rationale

- Smaller tasks = more predictable velocity
- Easier to parallelize work
- Faster feedback loops
- Reduces risk of scope creep

## Consequences

**Good:** Predictable sprints, smaller PRs
**Bad:** More overhead splitting large features

## More Information

See [team-agreement.md](../../docs/team-agreement.md)
