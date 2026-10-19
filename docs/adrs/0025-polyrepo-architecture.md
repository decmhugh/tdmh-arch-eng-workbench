---
parent: Decisions
nav_order: 25
title: ADR-0025 Polyrepo Architecture
status: draft
date: 2026-04-27
decision-makers: [TBD]
---

# ADR-0025: Polyrepo Architecture

## Status

**Draft**

## Context and Problem Statement

ACP consists of 20+ components. We need to decide on repository architecture:
- **Monorepo**: All code in one repository
- **Polyrepo**: Each component in its own repository

## Decision Drivers

* Team autonomy and independent deployment
* CI/CD pipeline complexity
* Code sharing and versioning
* Onboarding and discoverability
* Build time and test isolation

## Decision Outcome

**Polyrepo architecture with shared tooling repository (acp-devkit).**

### Repository Organization

```
t1k/acp/
├── acp-devkit/              # Shared tooling (this decision)
├── acp-specs/               # Specifications
├── acp-core/                # Shared domain models
├── acp-gateway/             # Gateway service
├── acp-agent-registry/      # Registry service
├── ...                      # Other services
└── agent-control-plane-ui/  # Frontend
```

### Why Polyrepo

| Factor | Polyrepo Advantage |
|--------|-------------------|
| **Independent Deployment** | Each service has its own CI/CD pipeline, can deploy independently |
| **Team Autonomy** | Teams can own repos, set their own pace |
| **Build Isolation** | Breaking change in one repo doesn't block others |
| **Clear Boundaries** | Forces explicit contracts between services |
| **Access Control** | Different teams can have different permissions |
| **Git History** | Clean, focused history per service |

### Mitigations for Polyrepo Challenges

| Challenge | Mitigation |
|-----------|------------|
| Discoverability | `acp-devkit/scripts/repos.yaml` manifest |
| Developer setup | `setup.ps1` script clones all repos |
| Cross-repo changes | Coordination via Jira epics |
| Shared code | `acp-core` as shared library |
| Consistent tooling | `acp-devkit` for shared workflows |
| IDE experience | VS Code multi-root workspace |

### Shared Tooling Repository (acp-devkit)

The `acp-devkit` repo addresses polyrepo friction:

```
acp-devkit/
├── .github/              # Reusable workflows
├── agents/               # Nova agents configs
├── scripts/
│   ├── repos.yaml        # Repository manifest
│   ├── bootstrap.ps1     # Clone/update all repos
│   └── pull-all.ps1      # Pull latest across all repos
└── vscode/
    └── acp-full.code-workspace
```

### Centralized Deployment Repository (acp-deploy)

Infrastructure and deployment manifests live in a centralized repo, separate from application code:

```
acp-deploy/
├── terraform/            # AWS infra (EKS, RDS, ElastiCache, IAM, VPC)
├── services/             # K8s manifests per service (Kustomize)
├── environments/         # Per-region overlays (dev, prod, multi-region)
├── docker-compose.yaml   # Local development stack
├── Jenkinsfile_infra     # Terraform apply pipeline
└── Jenkinsfile_deploy    # K8s deploy pipeline
```

**Rationale:**
- Single place to see "what runs where" across all services
- Environment-level changes (add a region, resize cluster) are atomic
- ArgoCD/GitOps-compatible (declarative manifests, no imperative scripts)
- Infrastructure team can review without navigating 15+ repos
- Application repos focus on code: `src/`, `tests/`, `Dockerfile`, `Jenkinsfile` (build only)

## Alternatives Considered

### Monorepo

**Pros:**
- Single checkout
- Atomic cross-service changes
- Unified CI/CD
- Easier refactoring

**Cons:**
- Long build times as codebase grows
- All-or-nothing access
- Merge conflicts across teams
- Single point of failure for CI
- Harder to enforce service boundaries

### Hybrid (Monorepo + Satellite Repos)

**Pros:**
- Core services together, specialized services separate
- Some flexibility

**Cons:**
- Complexity of both approaches
- Unclear rules for what goes where
- Inconsistent developer experience

## Consequences

**Good:**
- Clear service ownership
- Independent deployment pipelines
- Teams can move at their own pace
- Easier to open-source individual components
- Scales better with team growth

**Bad:**
- Initial setup requires multiple clones
- Cross-repo changes require coordination
- Dependency management more complex
- Need tooling to mitigate friction (acp-devkit)

**Mitigation:**
- `acp-devkit` provides consistent developer experience
- `repos.yaml` manifest keeps all repos discoverable
- VS Code workspace provides unified IDE view
- Regular sync meetings for cross-repo coordination

## More Information

* Related: ADR-0014 (CLI Tooling Consolidation)
* Tool: [acp-devkit](https://bitbucket.sunlifecorp.com/t1kacp/acp-devkit)
* Reference: [Monorepo vs Polyrepo](https://earthly.dev/blog/monorepo-vs-polyrepo/)
