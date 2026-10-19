---
parent: Decisions
nav_order: 9
title: ADR-0009 Diagram Format Standards
status: draft
date: 2026-04-27
---

# ADR-0009: Diagram Format Standards

## Status

**Draft** — from team-agreement.md

## Context and Problem Statement

How should diagrams be created and stored in documentation?

## Decision Outcome

**Chosen option**: Mermaid as default, PlantUML acceptable

| Format | Use Case |
|--------|----------|
| Mermaid | Default — flowcharts, sequence, ER diagrams |
| PlantUML | Complex diagrams, C4 model |
| PNG/SVG | External tools (Excalidraw) with source in repo |

## Benefits of Text-Based Diagrams

- Version controlled with code
- Diff-able in PRs
- Renders in GitHub/GitLab/Confluence
- No external tool required to edit

## Consequences

**Good:** Version controlled, editable in any text editor
**Bad:** Less visual fidelity than dedicated tools

## More Information

See [team-agreement.md](../../docs/team-agreement.md)
