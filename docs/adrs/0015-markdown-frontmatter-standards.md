---
parent: Decisions
nav_order: 15
title: ADR-0015 Markdown Frontmatter Standards
status: draft
date: 2026-04-27
---

# ADR-0015: Markdown Frontmatter Standards

## Status

**Draft**

## Context and Problem Statement

Inconsistent metadata across markdown files makes AI routing, search, and validation harder.

## Decision Outcome

**Chosen option**: Adopt frontmatter schema based on Cloud Doc Validator v2.1

## Required Fields

```yaml
---
title: "Document Title"              # 5-100 chars
description: "Brief summary"         # 20-300 chars
status: DRAFT | IN_REVIEW | PUBLISHED | ARCHIVED | DEPRECATED
---
```

## Recommended Fields

```yaml
---
owner:
  group: group:default/edae-acp      # Backstage entity
lastUpdated: 2026-04-27              # YYYY-MM-DD
routing:
  keywords: [keyword1, keyword2]     # 3-15 for AI/search
  capabilities: [documentation]       # Technical capabilities
  audience: [developer, architect]    # Target readers
---
```

## Spec-Specific Fields

```yaml
---
type: Spec
component: agent-registry
gate: D0
jira_epic: EACPP-123
---
```

## Benefits

- **AI Routing**: Copilot/RAG can use keywords
- **Search**: Indexed fields improve discoverability
- **Validation**: Schema enables automated checks
- **Backstage**: Owner ties to catalog entities

## Consequences

**Good:** Consistent metadata, better tooling support
**Bad:** Additional overhead when creating docs

## More Information

See Design Decision 5 in [design.md](../design.md)
