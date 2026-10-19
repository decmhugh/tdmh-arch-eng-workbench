---
parent: Decisions
nav_order: 7
title: ADR-0007 Jira Issue Type Hierarchy
status: draft
date: 2026-04-27
---

# ADR-0007: Jira Issue Type Hierarchy

## Status

**Draft** — from team-agreement.md

## Context and Problem Statement

What Jira issue types should we use for ACP work?

## Decision Outcome

**Chosen option**: Epics + Sub-tasks only

| Type | Purpose |
|------|---------|
| Epic | Represents a D0→D4 spec component |
| Sub-task | Individual work items under epics |

No Stories or Tasks at the project level.

## Consequences

**Good:** Simple hierarchy, clear epic→work relationship
**Bad:** May not fit all team workflows

## More Information

See [team-agreement.md](../../docs/team-agreement.md)
Related: ADR-0016 (Jira Components)
