---
has_children: true
nav_order: 100
title: Proposed ADRs
status: draft
---

# Proposed ADRs

These are draft ADRs for review as part of the CCoE Alignment Analysis.

## ADR Index

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-0001](0001-use-madr.md) | Use MADR 4.0.0 Format | Draft |
| [ADR-0002](0002-spec-driven-development.md) | Spec-Driven Development | Draft |
| [ADR-0003](0003-d0-d4-maturity-gates.md) | D0-D4 Maturity Gates | Draft |
| [ADR-0004](0004-confluence-read-only-mirror.md) | Confluence Read-Only Mirror | Draft |
| [ADR-0005](0005-git-source-of-truth.md) | Git as Source of Truth | Draft |
| [ADR-0006](0006-squash-merge-strategy.md) | Squash Merge Strategy | Draft |
| [ADR-0007](0007-jira-issue-hierarchy.md) | Jira Issue Hierarchy | Draft |
| [ADR-0008](0008-acceptance-criteria-format.md) | Acceptance Criteria Format | Draft |
| [ADR-0009](0009-diagram-format-standards.md) | Diagram Format Standards | Draft |
| [ADR-0010](0010-precommit-hook-enforcement.md) | Pre-commit Hook Enforcement | Draft |
| [ADR-0011](0011-story-point-limits.md) | Story Point Limits | Draft |
| [ADR-0012](0012-changelog-format.md) | Changelog Format | Draft |
| [ADR-0013](0013-pr-review-requirements.md) | PR Review Requirements | Draft |
| [ADR-0014](0014-cli-tooling-consolidation.md) | CLI Tooling Consolidation | Draft |
| [ADR-0015](0015-markdown-frontmatter-standards.md) | Markdown Frontmatter Standards | Draft |
| [ADR-0016](0016-jira-component-taxonomy.md) | Jira Component Taxonomy | Draft |
| [ADR-0017](0017-testing-strategy-standards.md) | Testing Strategy Standards | Draft |
| [ADR-0018](0018-frontend-technology-standards.md) | Frontend Technology Standards | Draft |
| [ADR-0019](0019-backend-technology-standards.md) | Backend Technology Standards | Draft |
| [ADR-0020](0020-open-source-evaluation-criteria.md) | Open Source Evaluation Criteria | Draft |
| [ADR-0021](0021-scalability-requirements.md) | Scalability Requirements | Draft |
| [ADR-0022](0022-performance-over-complexity.md) | Performance Over Developer Complexity for AI Infrastructure | Draft |
| [ADR-0023](0023-ai-human-work-separation.md) | AI vs Human Work Separation | Draft |
| [ADR-0024](0024-discuss-before-building.md) | Discuss Before Building Philosophy | Draft |
| [ADR-0025](0025-polyrepo-architecture.md) | Polyrepo Architecture | Draft |
| [ADR-0026](0026-namespace-strategy.md) | Kubernetes Namespace Strategy | Proposed |
| [ADR-0027](0027-release-promotion-cdd.md) | Release Promotion via CDD | Proposed |
| [ADR-0028](0028-git-branching-strategy.md) | Git Branching Strategy | Proposed |
| [ADR-0029](0029-provider-agnosticism.md) | LLM and Cloud Provider Agnosticism | Draft |
| [ADR-0030](0030-eval-langfuse-exposure.md) | Langfuse Public-API Exposure | Draft |
| [ADR-0031](0031-platform-vs-workload-environments.md) | Platform vs Workload Environments | Proposed |
| [ADR-0032](0032-gateway-account-placement.md) | Gateways in Their Environment's Account | Proposed |

## Categories

### Process (ADRs 0001-0013)
- 0001-0005: Core spec-driven development approach
- 0006-0013: Team agreements (from team-agreement.md)

### Technical Standards (ADRs 0014-0021)
- 0014-0015: Repository standards
- 0016: Jira configuration
- 0017: Testing strategy
- 0018-0019: Frontend/Backend tech stacks
- 0020-0021: Open source and scalability

### Strategic Principles (ADRs 0022-0025)
- 0022: Performance over complexity principle
- 0023: AI vs Human work separation
- 0024: Discuss before building philosophy
- 0025: Polyrepo architecture decision

### Deployment & Infrastructure (ADRs 0026+)
- 0026: Kubernetes namespace strategy
- 0027: Release promotion via CDD
- 0028: Git branching strategy
- 0030: Langfuse public-API exposure (evaluation runtime)
- 0031: Platform vs workload environments (which install owns workloads)
- 0032: Gateways in their environment's account (where the control plane's gateways run)

### Strategic Principles (continued)
- 0029: LLM and cloud provider agnosticism

## Review Process

1. Review each ADR individually
2. Comment in PR or Jira ticket
3. Mark as `accepted` after team approval
4. Move to `docs/adrs/` when finalized
