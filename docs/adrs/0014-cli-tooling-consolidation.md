---
parent: Decisions
nav_order: 14
title: ADR-0014 CLI Tooling Consolidation
status: draft
date: 2026-04-27
---

# ADR-0014: CLI Tooling Consolidation

## Status

**Draft**

## Context and Problem Statement

Multiple standalone Python scripts exist with inconsistent interfaces. How do we consolidate them?

## Decision Outcome

**Chosen option**: Unified CLI with Poetry + Typer

## Proposed Structure

```
pyproject.toml
src/acp_cli/
├── __init__.py
├── main.py           # acp
├── validate.py       # acp validate
├── sync.py           # acp sync
├── generate.py       # acp generate-index
└── seed.py           # acp seed
```

## Commands

| Command | Purpose |
|---------|---------|
| `acp validate [PATH]` | Validate specs, ADRs, frontmatter |
| `acp sync [PATH]` | Sync to Confluence |
| `acp generate-index` | Generate spec index |
| `acp seed <component>` | Scaffold new spec |

## Why Typer?

- Auto-generated `--help`
- Type hints for parameters
- Rich output (colors, tables)
- Clean subcommand structure

## Consequences

**Good:** Single entry point, consistent interface
**Bad:** Migration effort from existing scripts

## More Information

See Design Decision 6 in [design.md](../design.md)
