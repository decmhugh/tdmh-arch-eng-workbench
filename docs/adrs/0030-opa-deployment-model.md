---
parent: Decisions
nav_order: 30
sidebar_position: 30
title: ADR-0030 — OPA Policy Engine Deployment Model
status: proposed
date: 2026-05-27
decision-makers: [Matt Clark, Seth Chalmers]
consulted: [Central OPA / DevOps team (TBD)]
informed: [ACP engineering team]
---
<!-- markdownlint-disable-next-line MD025 -->
# OPA Policy Engine — Sidecar vs Central Instance

## Context and Problem Statement

ACP uses OPA as a fallback policy engine for complex authorization decisions that CEL cannot handle (graph traversals, recursive policy chains, advanced Rego rules). It is currently deployed as a dedicated container within the `acp-control` namespace, communicating via HTTP on port 8181.

The enterprise already operates a **central OPA instance** managed by the CTO's DevOps team for infrastructure governance-as-code (self-serve workflows, compliance checks, CTO-level policy enforcement). This raises the question: should ACP maintain a separate OPA deployment or integrate with the central instance? And regardless of where enforcement runs, should ACP policy bundles be consumable by other systems?

## Decision Drivers

* Domain isolation — ACP Rego rules are agent-specific (access control, cross-border, model risk)
* Independent release cycle — ACP team ships policy updates on their own cadence
* Latency — CEL handles 95% of decisions in-process (~50us); OPA is the fallback for complex rules
* Enterprise visibility — CTO governance-as-code platform needs consolidated policy view
* Bundle consumability — other teams/gateways may want to consume ACP policy bundles
* Operational overhead — running a separate OPA instance vs leveraging an existing one
* OSFI E-23 — may require consolidated policy audit trail across the enterprise

## Considered Options

* **Option A: Dedicated sidecar (current state)**
* **Option B: Central OPA integration**
* **Option C: Hybrid — local OPA + bundle publishing to central**

## Decision Outcome

**Status: OPEN** — No decision made yet. Current implementation (Option A) continues to unblock active development. Decision deadline: Sprint 14 (July 2026).

The key open question is whether ACP policy bundles should be consumable by other systems (central OPA, other teams' gateways). If yes, that favors Options B or C regardless of where enforcement runs.

### Action Items

- [ ] Meet with central OPA team to discuss bundle namespace compatibility (`data.acp.*`)
- [ ] Benchmark latency: dedicated OPA vs central OPA for ACP policy evaluations
- [ ] Document bundle format requirements for cross-team publishing
- [ ] Determine if OSFI E-23 requires consolidated policy visibility (audit requirement)

## Pros and Cons of the Options

### Option A: Dedicated Sidecar (current)

OPA runs as a container in `acp-control` namespace, co-located with management-plane.

* Good, because domain isolation — no risk of interference with other policies
* Good, because independent release cycle — ACP ships Rego updates without coordination
* Good, because low latency — localhost HTTP call (~5ms vs network hop)
* Good, because no cross-team dependency — ACP team owns the full stack
* Bad, because operational overhead of maintaining a separate OPA instance
* Bad, because Rego rules exist in isolation — no enterprise visibility
* Bad, because duplicated operational patterns (monitoring, upgrades, security patches)

### Option B: Central OPA Integration

ACP pushes its Rego policies to the CTO's central OPA instance and queries it remotely.

* Good, because single OPA fleet — shared operational expertise
* Good, because enterprise visibility — CTO governance-as-code sees all policies
* Good, because reduced operational overhead for ACP team
* Bad, because coupling to central team's change cycle and availability
* Bad, because latency — network hop to central OPA vs localhost
* Bad, because risk of policy interference if namespacing isn't strict
* Bad, because ACP rules must conform to central namespace conventions

### Option C: Hybrid — Local OPA + Bundle Publishing

ACP keeps its dedicated OPA for real-time enforcement but publishes compiled bundles to the central OPA for visibility and consumption by other systems.

* Good, because best of both — fast local evaluation + enterprise visibility
* Good, because other teams can consume ACP bundles without affecting enforcement
* Good, because central OPA has read-only view of ACP policies for audit
* Bad, because additional integration work (bundle format compatibility)
* Bad, because versioning complexity — two places to keep in sync
* Neutral, because bundle publishing aligns with ACP's existing propagation system (CEL/Cedar/Rego bundles)

## More Information

* ACP already has a propagation system that compiles policy bundles (CEL, Cedar, Rego formats)
* The management-plane publishes bundles to gateways — same mechanism could publish to central OPA
* Central OPA uses `data.*` namespace hierarchy — ACP would register under `data.acp.*`
* Related: ADR-0029 (provider agnosticism) — keeping OPA as a swappable backend aligns with this principle
