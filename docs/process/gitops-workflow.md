# GitOps Workflow for Spec-Driven Development

## Overview

Specs are managed through a GitOps workflow where **pull requests are the review mechanism**
and **`main` branch is the source of truth**. Each gate advancement is a PR.

## Branch Strategy

```
main (protected — requires PR approval)
├── spec/acp-core/d0          # D0 Discovery draft
├── spec/acp-core/d1          # D1 Requirements draft
├── spec/agent-registry/d0    # Different component, same pattern
└── spec/agent-registry/d1
```

### Branch Naming

```
spec/{component-name}/d{gate-number}
```

Examples:
- `spec/agent-registry/d0` — Agent Registry discovery
- `spec/acp-core/d1` — acp-core requirements
- `spec/ai-gateway/d2` — AI Gateway design
- `spec/ui-management-console/d2-v2` — Second design iteration

### Commit Messages

```
spec({component}): {description}
```

Examples:
```
spec(agent-registry): draft D0 discovery
spec(agent-registry): add API contract sketches to D1
spec(acp-core): revise D2 event schema design after review feedback
spec(ai-gateway): generate D3 tasks from D2 design
```

## Workflow Steps

### 1. Start a New Spec Gate

```bash
# Ensure you're on latest main
git checkout main && git pull

# Create spec branch
git checkout -b spec/agent-registry/d1

# Copy template if starting fresh
cp docs/templates/d1-requirements.md specs/platform/agent-registry/d1-requirements.md

# Edit the spec
# ... write requirements ...

# Update spec.yaml metadata
# ... set current_gate: D1, status: draft ...
```

### 2. Submit for Review

```bash
# Commit and push
git add specs/platform/agent-registry/
git commit -m "spec(agent-registry): draft D1 requirements with API contracts"
git push origin spec/agent-registry/d1

# Open PR in Bitbucket
# - Title: "spec(agent-registry): D1 Requirements"
# - Description: Summary of what's covered, link to D0
# - Reviewers: Engineering team (for D1)
```

### 3. Review Process

- Reviewers use the [Design Review Guide](design-review-guide.md) checklists
- All comments must be resolved before merge
- Minimum 2 approvals for D1 and D2 gates
- 1 approval sufficient for D0, D3, D4

### 4. Merge and Advance

```bash
# After approval, squash merge to main
# This advances the component to the next gate

# Update spec.yaml on main
git checkout main && git pull
# spec.yaml should show: current_gate: D1, status: approved
```

### 5. Sync to Confluence (Post-Merge)

```bash
# After merge, sync the updated spec to Confluence
set -a && source .github/.env && set +a
python3 scripts/sync_to_confluence.py specs/platform/agent-registry/
```

## Protection Rules

### Main Branch

- **Require PR**: Direct pushes to `main` are prohibited
- **Require approval**: At least 1 approval (2 for D1, D2 gates)
- **Require passing checks**: Spec validation must pass
- **Squash merge**: One commit per gate advancement

### Spec Validation (CI Check)

The `validate_specs.py` script runs on every PR:
- `spec.yaml` is valid YAML with required fields
- Referenced files exist
- Mermaid diagrams render without errors
- Gate order is respected (can't have D2 without D1 merged)

## Handling Updates to Merged Specs

Sometimes a merged spec needs revision (e.g., D2 design changes after implementation feedback):

```bash
# Create an update branch
git checkout -b spec/agent-registry/d2-update-1

# Edit the existing D2
# ... make changes ...

git commit -m "spec(agent-registry): update D2 — revise error handling after impl feedback"
git push origin spec/agent-registry/d2-update-1

# PR with explanation of why the spec changed
```

## Parallel Specs

Multiple components can be at different gates simultaneously:

```
specs/platform/acp-core/          → D2 (design approved)
specs/platform/agent-registry/    → D1 (requirements in review)
specs/platform/model-registry/    → D0 (discovery just merged)
specs/platform/ai-gateway/        → D0 (discovery in draft)
```

This is normal and expected. Components progress independently unless they have
dependencies (documented in D0).
