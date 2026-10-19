---
parent: Decisions
nav_order: 32
title: ADR-0032 Gateways in Their Environment's Account
status: proposed
date: 2026-10-06
decision-makers: [Platform Architecture, ACP Product Team]
---

# ADR-0032: Gateways in Their Environment's Account

## Status

**Proposed** — agreed in the *Luminate Gateway Environment Deployment Model* session on
2026-10-06; submitted with the ATG and ISRA for the topology. Refines
[ADR-0031](0031-platform-vs-workload-environments.md), which it does not change: one production
control plane still owns all four workload environments.

## Context and Problem Statement

ADR-0031 placed every business workload in the production Luminate install, in four workload
environments, each with its own gateway. Built as written, all eight gateways — four environments in
two regions — ran in the **production AWS account**.

Section 2.3 of the Infrastructure, Platform and Network Security Directive prohibits new workload
communication between environments (Production, Stage, Non-production, Lab) without authorized access
and inspection layers. With every gateway in the production account, every DEV, SIT and STAGE
workload talked to a production-account gateway, and those gateways called back into non-production
backends.

The question: **where do the gateways of the one production control plane run?**

## Decision Drivers

* **One governance record** — ADR-0031's reason for one control plane still holds.
* **Environment segregation** — non-production and stage traffic, Bedrock use, capacity and operator
  access should sit in the account Sun Life classifies for that environment.
* **Minimal cross-environment communication** — whatever remains must be enumerable, authenticated,
  content-free and inspectable.
* **Transparent to business teams** — a gateway move must not re-credential or reconfigure a workload.

## Considered Options

1. **All gateways in the production account** — the built state.
2. **One Luminate install per environment** — removes cross-environment communication and the single
   governance record with it.
3. **Each environment's gateways in that environment's account, one production control plane.**

## Decision Outcome

**Chosen option 3.** The DEV, SIT, STAGE and PROD gateways run in the dev, test, stage and prod
workload accounts respectively, in each serving region, and call Bedrock in their own
account. Today the serving regions are `ca-central-1` and `us-east-1`; they are an open list, and a
further region adds one gateway per environment in the same accounts, by procedure (DD-19).
The production control plane governs all of them. The only communication between a lower
account and the production account is each gateway's outbound, authenticated, content-free control
link to the control plane.

The lower Luminate installs remain, used only by the ACP platform team to test Luminate releases.

### Consequences

* Good: each environment's traffic, Bedrock spend and blast radius sit in its own account.
* Good: operator access to production becomes an entitlement on the production account only.
* Good: the control link is one enumerable flow per gateway, which can be inspected and approved.
* Good: gateways keep their identity across the move; agents see only a hostname change, and
  friendly hostnames make later moves invisible.
* Bad: the control link is still communication between environments and needs ATG and ISRA approval,
  and possibly a Security Exception.
* Bad: gateways outside the production account must be trusted only as themselves and must reach the
  identity provider's signing keys from any cluster — two Luminate changes.
* Good: adding a region is a repeatable procedure, not a redesign or a second install.
* Bad: the test and stage accounts need `us-east-1` clusters.

## More Information

Design: `specs/platform/gateway-environment-strategy` — D2 DD-3, DD-13 to DD-19, and the Assurance page.
