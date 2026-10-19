---
parent: Decisions
nav_order: 8
title: ADR-0008 Acceptance Criteria Format
status: draft
date: 2026-04-27
---

# ADR-0008: Acceptance Criteria Format

## Status

**Draft** — from team-agreement.md

## Context and Problem Statement

How should acceptance criteria be written for consistency and testability?

## Decision Outcome

**Chosen option**: Gherkin format (Given/When/Then)

```gherkin
Given [precondition]
When [action is taken]
Then [expected outcome]
```

## Format in Jira

Use wiki markup or markdown:
```
*Given* the agent is in approved state
*When* transition to active is requested
*Then* the agent state changes to active
```

## Consequences

**Good:** Testable, consistent, maps to BDD test frameworks
**Bad:** Can be verbose for simple criteria

## More Information

See [team-agreement.md](../../docs/team-agreement.md)
See [jira-adf-formatting.md](../../docs/jira-adf-formatting.md)
