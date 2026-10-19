---
parent: Decisions
nav_order: 30
title: ADR-0030 Langfuse Public-API Exposure
status: draft
date: 2026-06-03
decision-makers: [TBD]
---

# ADR-0030: Langfuse Public-API Exposure

## Status

**Draft**

## Context and Problem Statement

The self-hosted Langfuse stack (server + ClickHouse + Redis + S3) is the runtime that backs
the evaluation score-producer pipeline (EACPP-210, D3). The Eval-Bridge worker polls
Langfuse `/api/public/scores`, the Eval-Scorer worker writes scores back to Langfuse, and
per-team projects issue Langfuse public/secret key (pk/sk) pairs for programmatic trace and
score submission. All of these callers run **inside** the cluster today.

A recurring question is whether Langfuse's public API (`/api/public/*`) should also be
**exposed externally** — i.e. north-south, reachable from outside the cluster — so that SaaS
webhooks (e.g. Openlayer) or business teams operating outside the ACP network boundary can
push traces and scores directly to Langfuse, rather than routing through an ACP-owned ingest
surface.

The question: **should ACP expose the Langfuse public API externally, or keep it
in-cluster only?** This ADR records the exposure decision and its rationale; the API
onboarding mechanics for any worker identities or external ingest surface are out of scope
here and are handled by T15/T16 (EACPP-446 / EACPP-447).

## Decision Drivers

* **Attack surface** — Langfuse's public API authenticates with long-lived pk/sk pairs and
  was not designed as an internet-facing, multi-tenant edge. Exposing it widens the attack
  surface (credential stuffing, key leakage, enumeration, abuse).
* **Tenant isolation** — Evaluation entities carry `tenant_id`; an external edge must not
  weaken the per-tenant isolation already enforced east-west.
* **Business need** — No external producer has an approved, funded requirement to push
  directly to Langfuse today. SaaS webhooks (Openlayer) are normalized by an ACP-owned
  adapter (`POST /ingest/webhooks/{provider}`), not by direct Langfuse access.
* **Least privilege** — Workers should hold only the scope they need; a public edge would
  require a distinct, rate-limited, WAF-fronted ingress with its own credential lifecycle.
* **Reversibility** — Keeping Langfuse in-cluster is the easily-reversible default; exposing
  it externally is hard to walk back once external integrations depend on it.
* **Governance** — External exposure of an enterprise data surface requires an approved API
  Design Review and security sign-off that have not been granted.

## Considered Options

1. **Internal-only (in-cluster) Langfuse** — Langfuse `/api/public/*` is reachable only from
   within the cluster (east-west). External producers, if any, go through the ACP-owned
   `evaluation-api` ingest surface (`evaluation.ingest.crud` scope) behind the gateway.
2. **Gateway-fronted external exposure** — Langfuse `/api/public/*` is fronted by the
   AgentGateway / API Platform with per-project pk/sk auth, rate limits, and WAF, exposed
   north-south for approved external producers.
3. **Direct external exposure** — Langfuse ingress published directly (e.g. via a public
   route/load balancer) with Langfuse's native pk/sk auth and no ACP edge in front.

## Decision Outcome

**Chosen option: Internal-only (in-cluster) Langfuse**, because no approved external
producer requirement exists, it keeps the attack surface minimal, and it is the
easily-reversible default. External exposure is **deferred** and gated behind explicit
approval.

Langfuse's public API is reachable only east-west (in-cluster). External SaaS webhooks and
business-team submissions are mediated by the ACP-owned `evaluation-api` ingest surface
(`POST /ingest/scores`, `POST /ingest/webhooks/{provider}`, scope `evaluation.ingest.crud`),
which is the single governed north-south entry point. Direct external access to Langfuse is
**not** published.

If an external producer requirement is later **approved** (API Design Review + security
sign-off), the chosen implementation is **Option 2 (gateway-fronted)**, never Option 3
(direct). The conditional design is recorded below so a future approval can be executed
without re-litigating the architecture.

### Conditional design — gateway-fronted external exposure (only if approved)

| Control | Requirement |
| - | - |
| Edge | AgentGateway / API Platform route in front of Langfuse `/api/public/*`; no direct Langfuse ingress |
| AuthN | Per-project Langfuse pk/sk, scoped to a single tenant project; keys resolved/rotated via Vault (VSO), never committed |
| Rate limiting | Per-project rate limits enforced at the gateway (north-south) |
| WAF | WAF in front of the external route (common rule set + abuse protection) |
| Scope | Maps to `evaluation.ingest.crud`; least-privilege, non-prod first |
| Tenant isolation | `tenant_id` derived from the project; cross-tenant writes rejected |
| Approval | Requires approved API Design Review and security sign-off before enablement |

### Applies To

| Component | Implication |
| - | - |
| Langfuse runtime (`acp-data`) | Public API reachable east-west only; no external route published by default |
| Eval-Bridge / Eval-Scorer workers | Continue calling Langfuse in-cluster; unaffected by this decision |
| `evaluation-api` ingest surface | Remains the single governed north-south entry point for external scores/webhooks |
| AgentGateway / API Platform | Hosts the conditional external route **only** after approval (Option 2) |
| Per-team Langfuse projects | pk/sk remain internal credentials unless/until external exposure is approved |

### Consequences

* Good, because the attack surface stays minimal — no internet-facing pk/sk edge.
* Good, because it is the easily-reversible default; external exposure can be added later
  without rework, using the recorded conditional design.
* Good, because external integrations have a single governed entry point (`evaluation-api`
  ingest) with consistent auth, rate limiting, and tenant isolation.
* Good, because it satisfies governance — no enterprise data surface is exposed without an
  approved API Design Review and security sign-off.
* Bad, because external producers cannot push directly to Langfuse; they must integrate via
  the ACP ingest adapter (extra hop / adapter work for new providers).
* Bad, because the conditional gateway design remains unimplemented until/unless approved,
  so an approved external need incurs follow-on work.

### Confirmation

* No external route/ingress targets Langfuse `/api/public/*` in dev manifests; Langfuse is
  reachable only within the cluster (verified in the deploy manifests / NetworkPolicy).
* External scores/webhooks flow through `evaluation-api` (`evaluation.ingest.crud`), not
  direct Langfuse access.
* If external exposure is later approved, the gateway route enforces per-project pk/sk auth,
  rate limits, and WAF per the conditional design table before enablement.

## More Information

* D3 plan: [Model & Agent Evaluation — D3 Implementation Plan](../../specs/evaluation-strategy/d3-tasks.md)
  (T12 — Langfuse public-API exposure; risk row "Exposing Langfuse widens attack surface").
* Related: T15 (EACPP-446) / T16 (EACPP-447) — `evaluation-api` onboarding (dev / prod),
  including the `evaluation.ingest.crud` scope referenced above. API onboarding mechanics are
  out of scope for this ADR.
* Related: [ADR-0026 Kubernetes Namespace Strategy](0026-namespace-strategy.md)
  (`acp-data` namespace placement for the Langfuse runtime).
* Revisit trigger: an approved, funded requirement for an external producer to push directly
  to Langfuse, accompanied by an approved API Design Review and security sign-off.
