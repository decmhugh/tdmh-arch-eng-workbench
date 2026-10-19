# NOVA & ACP Integration - D0: Discovery

> **Gate**: D0 - Discovery | **Status**: Superseded in part | **Epic**: [EACPP-895](https://sunlife.atlassian.net/browse/EACPP-895) *(Nova-side counterpart: [CDSP-390](https://sunlife.atlassian.net/browse/CDSP-390))*

> **Amendment, 2026-09-04.** This D0 was written from a discovery conversation on 2026-08-10,
> before either system was inspected. Five of its framing assumptions do not survive contact
> with Nova and the plugin marketplace as they actually exist — most consequentially, Nova is
> **Backstage**, the integration direction is primarily **ACP → Nova via a catalogue provider**,
> and "IDP agent catalogue sync", listed here as out of scope, **is** the integration. The
> corrections are stated in full, with sources, in
> [D1 §0 — What changed since D0](d1-requirements.md#0-what-changed-since-d0).
>
> The problem statement, stakeholder map and risk register below remain useful and are not
> restated in D1. The **Scope** and **Open Questions** sections are superseded — read
> [D1](d1-requirements.md) instead. Two claims here are unevidenced and are not carried
> forward: cross-region agent discovery/failover, and the "1000 agents/day" load figure.

---

## Problem Statement

**What pain exists today?**

NOVA (internal development platform) has no standardized pathway to register agents with the Enterprise Agentic Control Plane (ACP). Currently:

- Developers building agents in NOVA cannot automatically register them into ACP's governance framework
- **Coding agents** (CLI/terminal-enabled agents) run in isolation within NOVA micro-VMs without centralized observability or audit trails
- **No unified agent catalogue** — ACP and NOVA maintain separate catalogues, creating friction for infrastructure and platform teams
- **Compliance blind spot** — Coding agents present elevated operational risk (broad tool access, no runtime guardrails) but lack centralized monitoring
- **Multiple portals** — Developers must navigate ACP UI separately to register agents, creating adoption friction
- **Cross-region deployment** is not supported for NOVA agents integrated with ACP

---

## Opportunity

**What becomes possible?**

Integrating NOVA with ACP enables:

- **Self-service agent registration** — NOVA developers can register agents directly from the NOVA UI without manual ACP access
- **Unified agent catalogue** — Single source of truth for all agents (coding, knowledge assistants, business logic agents) across both platforms
- **Governance at scale** — Compliance controls (authorization, audit, rate limiting, classification) applied uniformly at registration time
- **Improved observability** — All agent actions (MicroVM traffic, API calls, executions) logged and monitored through ACP audit framework
- **One-stop developer experience** — Infrastructure scaffolding and agent lifecycle management from one platform (NOVA)
- **Production-grade reliability** — IDP + ACP integration supporting global, cross-region agent deployment
- **Risk-based controls** — Differential governance for high-risk agents (CLI/write access) vs. read-only agents

---

## Stakeholders

**Who is impacted and their concerns?**

| Stakeholder | Role | Concern |
|-------------|------|---------|
| **NOVA Developers** | Build and register agents in NOVA | Simple, self-service registration workflow; no additional manual steps in ACP |
| **NOVA Platform Team** | Operate NOVA platform | Maintain agent catalogue; support IDP integration; ensure scalability and uptime |
| **ACP Product Lead** | Govern ACP roadmap | Define registration workflow; ensure compliance gates are enforced; maintain audit trail |
| **IDP Scrum Master** (Kristy Ashley) | Coordinate cross-platform integration | Sync agent catalogue between NOVA and IDP; define infrastructure provisioning contract |
| **Security & Compliance** | Audit and approve integrations | Oversight of coding agents; approval of security posture; audit trail requirements |
| **Platform Architecture** | Design system integration | Cross-region deployment; service mesh integration; latency and resilience |
| **Business Users** | Consume agents (via ACP) | Access unified catalogue of registered agents; discover and use agents with confidence |

---

## Scope

**What's in and out (explicit boundaries)?**

### **In Scope (MVP)**
- NOVA → ACP agent registration API integration
- Self-service registration UI flow in NOVA
- Classification of agent types (read-only vs. CLI/write access)
- Authorization workflow (team lead + security approval)
- Audit trail for agent registration events
- MicroVM observability integration with ACP monitoring
- Support for standard auth (MS EntraID / Okta)
- Initial deployment to production (single region)

### **Out of Scope (Backlog / Future)**
- IDP catalogue sync (backlog — Kristy Ashley to scope in D1)
- Cross-region failover and global DNS routing (D2 design)
- Non-standard auth environments (e.g., DentaQuest legacy) — evaluate post-MVP
- Runtime policy enforcement (e.g., blocking agents based on real-time signals) — future enhancement
- Agent update/rollback workflows — future enhancement
- Integration with external orchestration platforms (AgilePlace, Planview) — future enhancement

---

## Success Criteria

**Measurable outcomes:**

### **For NOVA Developers**
- Agents can be registered into ACP from NOVA UI without manual ACP access
- Self-service scaffolding for infrastructure setup (IDP integration)
- Simplified developer experience ("one portal" approach)
- Time to register an agent: < 5 minutes from NOVA UI

### **For ACP & Platform Teams**
- Comprehensive agent catalogue available to business and infrastructure teams
- All agent metadata and lifecycle events flow through ACP
- Compliance and governance controls applied at registration time (100% coverage)
- Zero manual ACP registrations for NOVA agents (automated pathway only)
- Cross-region availability (agents discoverable globally)

### **For Compliance & Security**
- 100% audit trail coverage for agent registration and execution
- MicroVM observability (traffic, API calls, resource usage) integrated with ACP monitoring
- Rate limiting and quota enforcement per agent
- Approved agents by team lead + security before production deployment

### **For Business**
- Adoption: 80% of NOVA developers use ACP registration within 3 months
- Time to value: agents operationalized (registered, approved, in catalogue) within 1 day

---

## Dependencies

**Blockers and prerequisites:**

| Dependency | Type | Status | Owner | Impact |
|------------|------|--------|-------|--------|
| **Okta API integration** | Technical | Backlog | Kristy Ashley | Primary auth mechanism for NOVA → ACP API calls; blocks D2 design |
| **ACP agent registration API** | Technical | In progress (ACP team) | ACP Product Lead | Define API contract (schema, error handling, rate limits); blocks D2 design |
| **MicroVM observability** | Technical | In progress (IDP team) | IDP Scrum Master | How to expose MicroVM traffic/logs to ACP; blocks D2 design |
| **IDP catalogue sync** | Technical | Backlog | Kristy Ashley | Future integration; out of scope for MVP but informs architecture |
| **Compliance approval** | Process | Pending | Security & Compliance | Approval of audit trail requirements and governance gates; blocks D1 requirements |
| **Non-EntraID auth strategy** | Technical | Backlog | Architecture | Special handling for clients like DentaQuest (non-standard auth); out of MVP scope |

---

## Risks

**Unknowns and mitigation ideas:**

| Risk | Likelihood | Severity | Mitigation |
|------|------------|----------|-----------|
| **Coding agent oversight gap** | High | High | Implement mandatory MicroVM observability + real-time audit trail before production |
| **API performance under scale** | Medium | High | Load test NOVA → ACP registration API with projected volume (e.g., 1000 agents/day); design caching strategy for agent discovery |
| **Cross-region latency** | Medium | Medium | Evaluate CDN / distributed cache for agent catalogue; define acceptable latency SLA (e.g., < 100ms for catalogue queries) |
| **Non-standard auth (DentaQuest)** | Low | Medium | Plan Okta federation strategy in D1; defer implementation to post-MVP phase |
| **IDP + ACP catalogue sync complexity** | Medium | Medium | Design sync protocol in D2 (webhooks vs. polling); assign owner and resource allocation in D1 |
| **Agent update/rollback failures** | Medium | High | Define version management and rollback strategy in D2; add compliance gates for agent updates |
| **Unauthorized agent registration** | High | High | Enforce approval workflow (team lead + security); implement rate limiting and quota per developer |

---

## Next Steps

- **Stakeholder Alignment**: Present D0 to NOVA platform team, ACP product lead, security, and architecture
- **D1 Requirements**: Define user stories, acceptance criteria, API contracts, and compliance gates
- **D2 Design**: Architecture diagrams, data models, integration patterns, and cross-region deployment strategy
- **D3 Tasks**: Sprint-ready implementation tasks with dependency mapping and effort estimates

---

## Compliance & Regulatory Requirements

### Model Risk Management
- **Risk Level**: Relatively low for most agents
- NOVA agents (especially coding assistants) present higher risk than traditional models

### Operational Risk — Coding Agents (Highest Concern)

**Issue**: Coding agents run in isolation without organizational oversight (analogy: GitHub Copilot for enterprises).

**Risk Factors**:
- **CLI/Terminal Access** — Agents with broad tool access to developer environments represent highest risk
- **Blind Spot** — Current NOVA architecture doesn't have centralized observability into agent actions
- **Unconstrained Execution** — No runtime guardrails or audit trail

### Observability & Audit Trail
- **MicroVM observability** — Each coding agent's traffic must be monitored and logged
- **ACP audit events** — Integration must emit governance events for all agent registrations and executions
- **Measurement & Alerting** — Set up monitoring for anomalous behavior (e.g., unusual data access patterns, excessive API calls)

### Governance Gates
- Agent registration must include:
  - Explicit authorization by team lead + security approval
  - Classification of agent type (read-only vs. CLI/write access)
  - Audit trail of all agent actions
  - Rate limiting and quota enforcement

---

## Stakeholders & Owners

| Role | Name | Responsibility |
|------|------|-----------------|
| **NOVA Platform Lead** | TBD | Define NOVA-side integration requirements, API contracts |
| **ACP Product Lead** | TBD | Define ACP registration workflow, compliance gates |
| **IDP Scrum Master** | Kristy Ashley | Coordinate IDP ↔ ACP catalogue sync (backlog) |
| **Security & Compliance** | TBD | Approve security posture, audit trail requirements |
| **Architecture** | TBD | Review cross-region deployment, service mesh integration |

---

## Known Constraints & Risks

| Constraint | Impact | Mitigation |
|------------|--------|-----------|
| Non-standard Auth (DentaQuest) | Not all clients use MS EntraID | Okta-based federation (in backlog) |
| Coding Agent Oversight | High operational risk | Implement MicroVM observability + audit trail |
| IDP Catalogue Integration | Backlog item | Define sync mechanism in D1 |
| Cross-region Latency | May impact real-time agent discovery | Evaluate CDN / caching strategy in D2 |

---

## Open Questions (For D1 Requirements)

1. What is the NOVA → ACP API contract for agent registration?
2. How should agent metadata (name, description, required permissions) be modeled in ACP?
3. What are the compliance gates for different agent types?
4. How will MicroVM observability integrate with ACP audit logging?
5. What is the timeline for IDP catalogue sync?
6. How will cross-region agent discovery and failover work?
7. What quotas/rate limits should apply to agent executions?

---

## Next Steps

- **D1 Requirements**: Define user stories, acceptance criteria, API contracts
- **D2 Design**: Architecture diagrams, data models, integration patterns
- **D3 Tasks**: Sprint-ready implementation tasks, dependency mapping
- **Stakeholder Alignment**: Present D0 to product, security, and architecture teams
