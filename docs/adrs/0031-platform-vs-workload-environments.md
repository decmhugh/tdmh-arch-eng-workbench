---
parent: Decisions
nav_order: 31
title: ADR-0031 Platform vs Workload Environments
status: proposed
date: 2026-09-02
decision-makers: [Platform Architecture, ACP Product Team]
---

# ADR-0031: Platform vs Workload Environments

## Status

**Proposed** — requires acceptance by both Platform Architecture and the ACP Product Team.

## Context and Problem Statement

Two different things at Sun Life are both called an "environment", and the collision is the
single largest source of misreading in the Luminate rollout:

| Term | Meaning | Owner | Changes when |
|---|---|---|---|
| **Platform environment** | A whole install of Luminate — portal, database, IdP, gateway — on one EKS cluster in one AWS account. There are four: `dev`, `test`, `stage`, `prod`. | ACP platform team | Luminate itself is upgraded |
| **Workload environment** | An `Environment` row *inside* an install. A business team's DEV / SIT / STAGE / PROD. | Business teams, governed by the platform team | A workload is promoted |

These are orthogonal axes, but they share a vocabulary, so conversations silently substitute
one for the other. Today's dev install conflates them by default: it is simultaneously the
platform team's sandbox and a place business workloads run.

Until it is settled **which platform environment owns business-team workloads**, nothing
downstream can be specified — not the environment set, not gateway topology, not promotion,
not the governance posture, not the cross-environment matrix. Every requirement in the
Gateway & Environment Strategy assumes this decision.

The question: **does one Luminate install own all four workload environments, or does each
workload environment get its own install?**

## Decision Drivers

* **Audit traceability across promotion** — a workload promoted DEV → PROD must be
  recognisably the same workload, with an audit trail that joins across environments (FR-7).
* **Every environment primitive Luminate has is intra-install** — the `GatewayEnvironment`
  join, `Deployment(environment, gateway)`, `CrossEnvironmentRule` between two `Environment`
  rows, and `GovernanceStatus` keyed `(resource, environment)` all live inside one database.
* **One resource, one governance identity** — `GovernanceStatus` is already per resource per
  environment; the topology must not flatten or fragment that (FR-14).
* **The platform team needs a disposable sandbox** — somewhere it can start, stop, redeploy
  and reconfigure Luminate freely without interrupting a business team.
* **Terminology risk** — whichever option is chosen, the naming collision must be closed
  explicitly, or the decision will be misapplied regardless of its merit.
* **Reversibility** — splitting a catalogue later is a migration; joining two catalogues
  later is a rewrite.

## Considered Options

1. **One production control plane** — the `prod` install owns all four workload
   environments; non-production installs exist only to test Luminate itself.
2. **One install per workload environment** — the `dev` install *is* DEV, `test` *is* SIT,
   `stage` *is* STAGE, `prod` *is* PROD. This is the option the current setup drifts into by
   default.

## Decision Outcome

**Chosen option: One production control plane.** The `prod` Luminate install is the single
control plane for business workloads and owns all four workload environments — DEV, SIT,
STAGE and PROD — each served by its own gateway. The dev, test and stage installs are the
platform team's own SDLC for Luminate and, in steady state, hold no business workloads.

One transitional exception is deliberate. The four-environment topology is already built in
the prod install (see below), but a **pilot workload** may run in the **test** install so
that redeploying Luminate never interrupts it. Any workload sitting in a non-prod install is
transitional and has an explicit end: it migrates to the prod install, after which the dev,
test and stage installs hold no business workloads at all.

> **To confirm before acceptance:** whether the pilot workload is still in the test install
> or has already moved to the prod install. Either answer is consistent with this decision —
> it changes only how much migration remains — but the D2 roadmap still frames P1 as *pilot
> in test*, and that needs to agree with whatever is confirmed here.

Option 2 splits the catalogue, and a split catalogue means a "promoted" resource is a
*different* resource with no provable relationship to the one that was tested. That breaks
the audit story the platform exists to provide.

### This posture is already running

This is not a proposal to build something new. The chosen option is what is deployed today,
verified against `slf-eks-t1k-ca-prod` on 2026-09-01:

| Element | Observed state |
|---|---|
| `Environment` rows | Four — Dev, SIT, Stage, Prod — inside the one prod install |
| `Gateway` rows | Four, all in `ca-central-1` |
| `GatewayEnvironment` mappings | Four — one gateway per workload environment |
| Dedicated gateway namespaces | `luminate-gw-dev`, `luminate-gw-sit`, `luminate-gw-stage` — two replicas each, at `3/3` |
| PROD gateway | Carried in the `luminate-portal` release by design — `gateway.enabled: true` in `values/values-prod.yaml`, enabled 2026-08-26 — and published via `ingress.aiGateway.hostname` |
| DNS | `gw-dev`, `gw-sit` and `gw-stage` resolve to the Traefik NLB |
| Auth | `gw-sit` and `gateway` both return `401` on `/llm/v1/models` |

So **DD-3 is 4/4 by design** — three dedicated gateways plus the portal-borne PROD gateway —
and the ask on this ADR is to ratify an operating posture rather than to approve an untested
design.

Each install carries an explicit **role**, because the install names collide with the
workload environment names:

| Install | Cluster · AWS account | Role | Safe to redeploy at will? |
|---|---|---|---|
| **dev** | `slf-eks-t1k-ca-dev` · `360967146904` | **Sandbox** — ACP-team only. Start, stop, redeploy, reconfigure freely. | **Yes — this is the point** |
| **test** | `slf-eks-t1k-ca-uat` · `692797214700` | Platform verification, and the pilot workload plane | No while a pilot is live |
| **stage** | `slf-eks-t1k-ca-stage` · `775755739292` | Pre-production verification of Luminate itself | No |
| **prod** | `slf-eks-t1k-ca-prod` · `035722575935` | Business workloads, in four workload environments | No |

All four are in `ca-central-1`, one install per cluster per account.

The **test** install is this ADR's own counter-example. It answers to four names today:

| Where | Name |
|---|---|
| This ADR, and `values/values-test.yaml` in `luminate-sunlife-deploy` | `test` |
| The EKS cluster itself | `slf-eks-t1k-ca-uat` |
| [`specs/platform/sunlife-deployment/d3-tasks.md`](../../specs/platform/sunlife-deployment/d3-tasks.md) | TEST/UAT |
| `deploy-checklists/test-uat.md` in the deploy repo | `test-uat` |

Name the install explicitly; never infer it from a hostname, a values file or a checklist
filename. An ADR written to close a naming collision should not leave one of its own labels
unremarked — which is why the table above carries the cluster and account, so each install
is unambiguous regardless of the label anyone reaches for.

### Naming rule

**"dev install" means the sandbox. "DEV" means the workload environment inside the prod
install.** They are different things and the words are not interchangeable. Specs, runbooks,
tickets and user guides must qualify the term on first use in any document that mentions
both axes.

#### Worked example — the collision is in a live DNS record

```text
gateway.apps.slf-eks-t1k-ca-prod.aws.sunlifecorp.com
```

The `prod` in that hostname is the **platform** environment — the cluster and the AWS
account. The gateway it resolves to serves the **PROD workload** environment. The two axes
coincide here, which is exactly why the name reads as correct and nobody questions it.

Its sibling gets no such cover: `gw-sit.apps.slf-eks-t1k-ca-prod.aws.sunlifecorp.com` is the
SIT **workload** environment inside the **prod** install. To anyone who has not read this
ADR it reads as a misconfiguration. It is not — it is the model working as designed, and
reading it correctly requires holding both axes at once. That is the whole point of the
naming rule.

### Consequences

* Good, because a resource registered once carries **one governance identity** through all
  four environments, and the audit trail joins.
* Good, because promotion becomes a state change within one catalogue rather than a
  re-registration into a foreign one.
* Good, because the dev install becomes a genuine sandbox the platform team can redeploy at
  will, which it cannot be while a business team depends on it.
* Good, because `CrossEnvironmentRule` and `GovernanceStatus` operate on the axis they were
  modelled for.
* **Bad, because a team's DEV workload then runs on production infrastructure, in a
  production account, on a production cluster.** This is a real posture change and must be
  stated to every onboarding team rather than discovered.
* Bad, because blast radius concentrates: an incident in the prod install affects all four
  workload environments at once.
* Consequently, the isolation decisions are **not optional** — one gateway per environment
  (DD-3), default-deny cross-environment traffic (DD-6), per-tier quotas (DD-9) and
  telemetry data isolation (DD-10) are load-bearing for this ADR, not enhancements to it.

### Confirmation

* Both Platform Architecture and the ACP Product Team record acceptance; this ADR moves to
  **Accepted** and `DD-1`/`DD-2` in the D2 design are confirmed consistent with it.
* The install role table above is published, and the naming rule — with the
  `gateway.apps.slf-eks-t1k-ca-prod` worked example — is applied in `luminate-user-guides`
  when the SDLC path is written.
* No business workload exists in the dev, test or stage installs once migration completes —
  the dev install is a pure ACP-team sandbox.
* **No business workload is onboarded to the prod install until the isolation controls this
  decision leans on actually exist.** Per-environment gateways (DD-3) are in place. The
  `CrossEnvironmentRule` evaluator is not — the rule is a no-op in the request path until
  **T20** lands, so DD-6 today describes a boundary rather than holding one — and neither is
  collector-level redaction (DD-10a, **T29**). Until both land, onboarding is **by exception,
  with named platform-team approval** recorded against the workload. DD-2's *"synthetic /
  non-sensitive data only"* rule for DEV is likewise unevaluated, making it an onboarding
  condition rather than a control.

  The consequence this ADR accepts — a DEV workload in a production account — is not accepted
  until its mitigations are required rather than described.

## Pros and Cons of the Options

### One production control plane

* Good, because promotion, governance status and cross-environment rules all work as
  modelled — no primitive is asked to span a database boundary.
* Good, because there is one catalogue, one governance record and one audit trail.
* Good, because Luminate upgrades are proven in the non-prod installs before reaching any
  business workload.
* Neutral, because it concentrates operational attention on one install — a cost, but also a
  focus.
* Bad, because non-production workloads run on production infrastructure, requiring the
  isolation controls to be real rather than intended.

### One install per workload environment

* Good, because the blast radius of a DEV workload is a non-production account, with no
  isolation controls required to make that true.
* Good, because it matches the intuition most teams arrive with, so it needs no explanation.
* Bad, because a promoted resource is a new row in a different database with no provable
  relationship to its origin — FR-7 cannot be satisfied.
* Bad, because `CrossEnvironmentRule` becomes meaningless: it relates two `Environment` rows,
  and there would only ever be one per install.
* Bad, because `GovernanceStatus` per `(resource, environment)` fragments into four
  unrelated records, so "is this resource compliant?" has four answers that cannot be joined.
* Bad, because the platform team loses its disposable sandbox — the dev install becomes
  production-critical to whichever team is using it.
* Bad, because Luminate upgrades would have to be proven somewhere else entirely.

## More Information

* Spec: [D0](../../specs/platform/gateway-environment-strategy/d0-discovery.md) ·
  [D1](../../specs/platform/gateway-environment-strategy/d1-requirements.md) ·
  [D2 Topology](../../specs/platform/gateway-environment-strategy/d2-design/topology.md)
* Requirement: **FR-1** — record, as an ADR, which platform environment owns business-team
  workloads and what the remaining platform environments are for.
* Design decisions: **DD-1** (one production control plane), **DD-2** (four workload
  environments).
* Epic: EACPP-1089 · Task **T1**.
* Related: [ADR-0026](0026-namespace-strategy.md) (Kubernetes namespace strategy).
