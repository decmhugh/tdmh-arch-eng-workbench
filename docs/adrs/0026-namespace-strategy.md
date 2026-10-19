---
parent: Decisions
nav_order: 26
title: ADR-0026 Kubernetes Namespace Strategy
status: proposed
date: 2026-06-10
decision-makers: [TBD]
---

# ADR-0026: Kubernetes Namespace Strategy

## Status

**Proposed**

## Context and Problem Statement

ACP deploys 15+ services to EKS. We need to decide how to organize services into Kubernetes namespaces. The choice affects secret isolation (VSO scoping), resource quota boundaries, network policy complexity, kustomize overlay structure, and operational overhead.

Cluster add-ons (Traefik, VSO, cert-manager) are managed by the Cloud Container Enablement (CCE) team in their own namespaces and are out of scope for this decision.

## Decision Drivers

* Secret isolation -- VSO `VaultStaticSecret` CRDs are namespace-scoped
* Resource governance -- quotas and LimitRanges apply per namespace
* Network policy boundaries -- default-deny is per namespace
* Operational simplicity -- fewer namespaces = fewer kustomize targets
* RBAC granularity -- namespace-level role bindings for team access
* Service discovery -- cross-namespace requires FQDN (`svc.ns.svc.cluster.local`)
* Blast radius -- failure in one namespace shouldn't impact others

## Considered Options

* **Option A: Single namespace** -- All ACP services in one `acp` namespace
* **Option B: Per-service namespaces** -- Each service gets its own namespace (8-10 namespaces)
* **Option C: Tier-based namespaces** -- Group by function (3-5 namespaces)

## Decision Outcome

**Option C: Tier-based namespaces**, because it balances isolation with operational simplicity.

### Namespace Layout

```
acp-ui/                          # Frontend (agent-control-plane-ui)
acp-gateway/                     # Ingress tier (acp-gateway, acp-agentgateway)
acp-control/                     # Control plane services
                                 #   acp-management-plane
                                 #   acp-agent-registry
                                 #   acp-mcp-registry
                                 #   acp-model-registry
                                 #   acp-policy-opa, acp-policy-cel
acp-data/                        # Data tier
                                 #   acp-store-postgres
                                 #   acp-observability
```

### Rationale

* **UI separated** because it has different scaling, security, and access patterns (static assets, CDN-friendly, no DB access)
* **Gateway separated** because it is the entry point and needs independent scaling/network policy (ingress-facing)
* **Control plane grouped** because these services share similar trust boundaries, all talk to the same backing stores, and are tightly coupled operationally
* **Data tier separated** because it has different resource profiles (connection pooling, disk I/O) and stricter access requirements

### Consequences

* Good, because VSO secrets scoped per tier (UI secrets separate from data tier secrets)
* Good, because resource quotas prevent one tier from starving another
* Good, because network policies are manageable (4 namespaces vs 10)
* Good, because kustomize overlays target 4 namespaces (reasonable complexity)
* Bad, because services within `acp-control` share a secret boundary (all control plane services can see each other's K8s Secrets)
* Bad, because adding a new service requires deciding which tier it belongs to
* Neutral, because cross-namespace service calls need FQDN, but only between tiers (within a tier, short names work)

### Confirmation

* All kustomize overlays in `acp-deploy` reference one of the four namespaces
* Network policies verified via `kubectl describe networkpolicy -n <ns>`
* Resource quotas confirmed per namespace per environment

## Pros and Cons of the Options

### Option A: Single namespace (`acp`)

All services in one namespace.

* Good, because simplest kustomize setup (one namespace target)
* Good, because service discovery uses short names everywhere
* Good, because minimal operational overhead
* Bad, because all secrets visible to all pods (no VSO isolation)
* Bad, because one misbehaving service can exhaust all resources
* Bad, because network policies cannot restrict intra-namespace traffic effectively
* Bad, because RBAC is all-or-nothing for the namespace

### Option B: Per-service namespaces

Each service gets its own namespace (8-10 namespaces).

* Good, because maximum secret isolation
* Good, because per-service resource quotas
* Good, because finest-grained network policies
* Bad, because kustomize must target 8-10 namespaces per overlay
* Bad, because cross-service calls all require FQDN
* Bad, because VSO CRDs duplicated per namespace
* Bad, because operational overhead scales with number of services
* Bad, because network policy rules multiply (N*N potential rules)

### Option C: Tier-based namespaces (chosen)

See Decision Outcome above.

## More Information

* This decision is referenced by D1 FR-8 (Namespace Strategy) in the Deployment & Infrastructure spec (EACPP-212)
* Cluster add-ons (Traefik, VSO, cert-manager) are in CCE-managed namespaces and not affected by this decision
* If secret isolation within `acp-control` becomes a concern, the tier can be split further without changing the overall model
