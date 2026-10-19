---
parent: Decisions
nav_order: 5
title: ADR-0005 Git as Source of Truth
status: draft
date: 2026-04-27
---

# ADR-0005: Git as Source of Truth

## Status

**Draft**

## Context and Problem Statement

Where should authoritative documentation live?

## Decision Outcome

**Chosen option**: Git repository is the single source of truth

- All specs, ADRs, process docs in Git
- Version controlled, auditable history
- PR-based review process
- External systems (Confluence, TechDocs) sync from Git

## Consequences

**Good:** Full version history, PR reviews, developer-friendly workflow
**Bad:** Non-technical stakeholders may prefer Confluence UI

## More Information

See [gitops-workflow.md](../../docs/process/gitops-workflow.md)
