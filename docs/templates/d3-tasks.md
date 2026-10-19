# {Component Name} — D3: Implementation Plan

> **Gate**: D3 — Tasks | **Status**: Draft | **Epic**: {EPIC-KEY}

## Task Summary

| # | Task | Type | Points | Sprint | Depends On | Jira |
|---|------|------|--------|--------|------------|------|
| 1 | {Task title} | Story | 2 | S1 | — | |
| 2 | {Task title} | Story | 3 | S1 | T1 | |
| 3 | {Task title} | Spike | 1 | S1 | — | |
| 4 | {Task title} | Story | 2 | S2 | T2, T3 | |

## Luminate Support Checks

> Optional, and only meaningful for a task that leans on a capability the
> [ACP Capability Map](../capability-map.md) does not mark ✅ Available. Delete this section if
> every task rests on shipping capability.

Any task table carrying a **Luminate support** column makes `create_jira_from_spec.py` render a
warning panel at the top of that task's Jira ticket, telling whoever picks it up to re-verify
before building. Capability verdicts are snapshots — a gap may have closed, and a ✅ may have
regressed off the enforcement path — so the check belongs at pick-up time, not authoring time.

| Task | Luminate support | What to re-verify at pick-up |
|------|------------------|------------------------------|
| T{n} | {CAP-XX · G{n}} | {The specific thing to confirm against `origin/main`, and what changes if the answer moved} |

Leave a task out of this table, or write `—`, when it needs no check.

## Dependency Graph

```mermaid
graph LR
    T1[T1: {short name}]
    T2[T2: {short name}]
    T3[T3: {short name}]
    T4[T4: {short name}]
    
    T1 --> T2
    T1 --> T3
    T2 --> T4
    T3 --> T4
```

## Sprint Allocation

### Sprint 1: {Theme}

| Task | Points | Assignee | Definition of Done |
|------|--------|----------|-------------------|
| T1: {title} | 2 | TBD | {What "done" looks like} |
| T2: {title} | 3 | TBD | {What "done" looks like} |
| T3: {title} | 1 | TBD | {What "done" looks like} |

### Sprint 2: {Theme}

| Task | Points | Assignee | Definition of Done |
|------|--------|----------|-------------------|
| T4: {title} | 2 | TBD | {What "done" looks like} |

## Task Details

### T1: {Task Title}

**Type**: Story | **Points**: 2 | **Sprint**: S1

**Description**:
{What needs to be built, referencing D2 design components.}

**Acceptance Criteria**:
- [ ] {Specific, testable criterion}
- [ ] {Another criterion}
- [ ] Unit tests pass with ≥ 90% coverage
- [ ] Pre-commit hooks pass

**D2 Reference**: {Which design section this implements}

---

### T2: {Task Title}

**Type**: Story | **Points**: 3 | **Sprint**: S1 | **Depends on**: T1

**Description**:
{What needs to be built.}

**Acceptance Criteria**:
- [ ] {Criterion}
- [ ] {Criterion}

---

## Risk Mitigation

| Risk (from D0) | Mitigation Task | Sprint |
|-----------------|----------------|--------|
| {Risk} | T3: {spike/POC task} | S1 |

## Jira Ticket Map

> Filled after ticket creation. Maps task numbers to Jira keys.

| Task | Jira Key | Status |
|------|----------|--------|
| T1 | | |
| T2 | | |

## Notes

- {Any implementation notes, conventions, or constraints}
- {Team agreements on approach}
