---
parent: Decisions
nav_order: 6
title: ADR-0006 Squash Merge Strategy
status: draft
date: 2026-04-27
---

# ADR-0006: Squash Merge Strategy

## Status

**Draft** — from team-agreement.md

## Context and Problem Statement

How should PRs be merged to maintain clean history?

## Decision Outcome

**Chosen option**: Squash merge with one commit per PR

- All PRs use squash merge
- Commit message follows conventional commits
- Feature branch history condensed to single commit
- Main branch has linear, readable history

## Consequences

**Good:** Clean history, easy bisect, clear audit trail
**Bad:** Loses granular commit history from feature branch

## More Information

See [team-agreement.md](../../docs/team-agreement.md)
