---
parent: Decisions
nav_order: 27
title: ADR-0027 Release Promotion via CDD
status: proposed
date: 2026-06-10
decision-makers: [TBD]
---

# ADR-0027: Release Promotion via Continuous Delivery Director

## Status

**Proposed**

## Context and Problem Statement

ACP deploys across five environments: dev-ca, sit-ca, stg-ca, prod-ca, and prod-us. We need a structured promotion pipeline that enforces quality gates, approval workflows, and audit trails as releases progress from development to production. Without a defined promotion model, deployments rely on ad-hoc manual processes with no traceability.

## Decision Drivers

* Audit trail -- regulatory and internal compliance require traceability of who approved what and when
* Quality gates -- each environment transition must verify different test levels passed
* Approval workflows -- production deployments require release manager sign-off and ServiceNow change requests
* Multi-region coordination -- prod-us deployment is a separate approval from prod-ca
* Integration with existing tooling -- Jenkins JTE is the deployment executor, ServiceNow is the change management system
* CDD is an enterprise-approved tool already available to the team

## Considered Options

* **Option A: CDD-orchestrated promotion** -- CDD manages phases, gates, and triggers Jenkins for deployment
* **Option B: Jenkins-only promotion** -- Jenkins pipelines handle promotion logic with manual approval steps
* **Option C: GitOps promotion** -- ArgoCD with PR-based promotion between branches/overlays

## Decision Outcome

**Option A: CDD-orchestrated promotion**, because it provides enterprise-grade audit trails, integrates with ServiceNow for change management, and separates promotion orchestration from deployment execution.

### Promotion Pipeline

```
dev-ca --> sit-ca --> stg-ca --> prod-ca --> prod-us
```

### Phase Gates

| Transition | Quality Gate | Approval | Change Management |
| - | - | - | - |
| dev-ca -> sit-ca | Unit tests + smoke tests pass | Automated | None |
| sit-ca -> stg-ca | Integration + regression tests pass | Manual approval in CDD | None |
| stg-ca -> prod-ca | Performance/soak tests pass | Release manager approval | ServiceNow CR required |
| prod-ca -> prod-us | Smoke validation in prod-ca | Explicit multi-region approval | ServiceNow CR required |

### Integration Model

```
CDD (orchestration)
  |
  +--> Jenkins (deployment execution)
  |      |
  |      +--> kubectl apply -k overlays/{env}-{region}
  |      +--> test execution + result reporting
  |
  +--> ServiceNow (change requests for stg/prod)
  |
  +--> Audit log (all transitions, approvers, timestamps, test results)
```

### Consequences

* Good, because CDD provides built-in audit trail for all phase transitions
* Good, because ServiceNow integration satisfies change management requirements
* Good, because Jenkins remains the deployment executor (no new deployment tooling)
* Good, because multi-region promotion is an explicit, separate phase (not automatic)
* Good, because test results are recorded at each gate for traceability
* Bad, because CDD adds a dependency -- if CDD is down, promotions are blocked
* Bad, because CDD configuration must be maintained alongside kustomize overlays
* Neutral, because team needs to learn CDD phase/gate configuration

### Confirmation

* CDD release pipeline configured with all five phases
* Successful promotion from dev-ca through prod-ca with all gates enforced
* ServiceNow CR created automatically for stg/prod deployments
* Audit log shows complete trail for a release

## Pros and Cons of the Options

### Option A: CDD-orchestrated promotion (chosen)

See Decision Outcome above.

### Option B: Jenkins-only promotion

Jenkins pipelines handle promotion with `input` steps for manual approval.

* Good, because no additional tool dependency (Jenkins already in use)
* Good, because pipeline-as-code keeps promotion logic in source control
* Bad, because Jenkins `input` steps are not a proper approval workflow (no delegation, no SLA)
* Bad, because audit trail is limited to Jenkins build logs (not enterprise-grade)
* Bad, because ServiceNow integration would need custom pipeline code
* Bad, because multi-region coordination is manual or requires custom orchestration

### Option C: GitOps promotion (ArgoCD)

ArgoCD watches overlay branches; promotion is a PR from one branch to another.

* Good, because promotion is a Git operation (full history, reviewable)
* Good, because ArgoCD provides drift detection and self-healing
* Bad, because ArgoCD is not yet approved for use (future consideration)
* Bad, because ArgoCD has no native ServiceNow integration or change management workflow
* Bad, because ArgoCD has no built-in approval gating process -- would require external tooling to enforce phase transitions
* Bad, because audit trail is limited to Git history (no enterprise approval/timestamp/approver metadata)
* Bad, because multi-region coordination would require custom tooling on top of ArgoCD

## More Information

* This decision is referenced by D1 FR-7 (Release Management via CDD) in the Deployment & Infrastructure spec (EACPP-212)
* Test strategy details (frameworks, coverage targets, test data) are defined separately in EACPP-265
* ArgoCD may be revisited when it receives enterprise approval (noted in D1 constraints)
