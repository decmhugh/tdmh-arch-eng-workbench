---
parent: Decisions
nav_order: 16
title: ADR-0016 Jira Component Taxonomy
status: draft
date: 2026-04-27
decision-makers: [TBD - requires Jira admin]
---

# ADR-0016: Jira Component Taxonomy

## Status

**Draft** — Pending Jira admin to create components in EACPP project

## Context and Problem Statement

The EACPP Jira project currently has no components defined. We want to use Jira components to:
1. Categorize tickets by ACP system component
2. Enable component-based filtering and reporting
3. Align Jira structure with the 16 ACP spec components
4. Support future automation (auto-assign, notifications)

## Decision Drivers

* Alignment with spec-driven development (16 components defined in `specs/`)
* Need for better ticket organization and discoverability
* Support for component owners and domain experts
* Consistency between Jira and repository structure

## Considered Options

### Option 1: Mirror Spec Components

Create 16 components matching `specs/` directories:

| Component | Description |
|-----------|-------------|
| `acp-core` | Core ACP functionality |
| `agent-registry` | Agent registration and lifecycle |
| `ai-gateway` | AI model routing and gateway |
| `aws-adapter` | AWS infrastructure adapter |
| `deployment-infrastructure` | Deployment and infra |
| `evaluation-strategy` | Model evaluation |
| `governance-integration` | Governance and compliance |
| `inference-economics` | Cost and resource management |
| `kubernetes-adapter` | K8s adapter |
| `management-plane` | Management control plane |
| `mcp-registry` | MCP tool registry |
| `model-registry` | ML model registry |
| `snowflake-adapter` | Snowflake adapter |
| `storage-persistence` | Data storage layer |
| `ui-advanced-features` | Advanced UI features |
| `ui-management-console` | Management console UI |

### Option 2: Grouped Components

Create higher-level components grouping related specs:

| Component | Includes |
|-----------|----------|
| `core` | acp-core, management-plane, governance-integration |
| `adapters` | aws-adapter, kubernetes-adapter, snowflake-adapter |
| `registries` | agent-registry, model-registry, mcp-registry |
| `ui` | ui-management-console, ui-advanced-features |
| `ai` | ai-gateway, inference-economics, evaluation-strategy |
| `infrastructure` | deployment-infrastructure, storage-persistence |

### Option 3: Functional Components

Create components by function rather than system:

| Component | Purpose |
|-----------|---------|
| `docs` | Documentation work |
| `specs` | Spec authoring |
| `tooling` | CLI, scripts, automation |
| `process` | Process improvements |
| `infrastructure` | Deployment, CI/CD |

## Decision Outcome

**Chosen option: Option 1 (Mirror Spec Components)**

Rationale:
* 1:1 mapping simplifies automation and mental model
* Spec-driven development already defines these boundaries
* Can add grouped views via Jira filters/dashboards
* Future: component leads can be auto-assigned

### Consequences

**Good:**
* Clear ownership per component
* Easy to correlate Jira tickets with spec folders
* Supports automated workflows (component → assignee)

**Bad:**
* 16 components may seem like many initially
* Requires Jira admin to create components

**Neutral:**
* May add more components later as system grows

## Implementation

### Pre-requisites

1. Jira admin creates 16 components in EACPP project
2. Add component descriptions from spec `d0-discovery.md` summaries
3. Assign default leads (optional)

### MCP Tool Usage

Once components exist, use `nova_jira_update_issue` to set:

```json
{
  "components": ["agent-registry", "governance-integration"]
}
```

### Validation

The Jira skill (`.github/skills/jira/SKILL.md`) will validate component names against the defined taxonomy.

## More Information

* Related: ADR-0007 (Jira Issue Hierarchy)
* Specs: See `specs/*/spec.yaml` for component definitions
* Boards: Epic Board (23091), Stories Kanban (23490)
