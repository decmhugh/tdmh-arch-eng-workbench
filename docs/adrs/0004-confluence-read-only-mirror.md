---
parent: Decisions
nav_order: 4
title: ADR-0004 Confluence as Read-Only Mirror
status: draft
date: 2026-04-27
---

# ADR-0004: Confluence as Read-Only Mirror

## Status

**Draft**

## Context and Problem Statement

Team members expect documentation in Confluence, but maintaining two sources of truth is error-prone.

## Decision Outcome

**Chosen option**: Git is source of truth; Confluence is auto-synced read-only mirror

- Specs authored in Git (markdown)
- Synced to Confluence via automation
- Confluence pages have "do not edit" disclaimer
- MCP tools are read-only for Confluence

## Consequences

**Good:** Single source of truth, version controlled, reviewable
**Bad:** Confluence edits are lost on next sync

## More Information

See [confluence-sync.md](../../docs/process/confluence-sync.md)
