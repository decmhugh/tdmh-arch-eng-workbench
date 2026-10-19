---
parent: Decisions
nav_order: 2
title: ADR-0002 Spec-Driven Development Approach
status: draft
date: 2026-04-27
---

# ADR-0002: Spec-Driven Development Approach

## Status

**Draft**

## Context and Problem Statement

How should we organize and track work for complex enterprise platform development?

## Decision Outcome

**Chosen option**: Spec-Driven Development with D0→D4 gates

- Each component has a spec folder (`specs/{spec_type}/{component}/`)
- Specs progress through maturity gates (D0→D4)
- Git is source of truth; Nova Build Hub (TechDocs) & Confluence is read-only mirror
- Jira tracks progress via epics and sub-tasks

## Consequences

**Good:** Clear documentation trail, reviewable milestones
**Bad:** More upfront documentation effort

## More Information

See [d0-d4-overview.md](../../docs/process/d0-d4-overview.md)
